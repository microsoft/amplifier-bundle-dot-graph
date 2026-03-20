# Code Tracer Findings: Entry Point Bundle Composition

**Topic:** Entry Point Bundle Composition  
**Repo:** `/home/bkrabach/dev/dot-graph-bundle`  
**Key Repos:** `amplifier/`, `amplifier-foundation/`, `amplifier-core/`

---

## Summary

The Entry Point Bundle Composition mechanism is a multi-stage pipeline: parse → resolve → compose → activate → session-init. It spans two repositories (`amplifier-foundation` for bundle management, `amplifier-core` for module loading) and involves five key classes: `BundleRegistry`, `Bundle`, `SimpleSourceResolver`, `ModuleActivator`, and `ModuleLoader`.

---

## 1. Entry Point: The Bundle File

The user-facing entry point is `amplifier/bundle.md` — a markdown file with YAML frontmatter.

**`amplifier/bundle.md:1-10`** — Frontmatter declares `bundle:` metadata and `includes:` list:
```yaml
bundle:
  name: amplifier
  version: 1.0.0
  description: Amplifier ecosystem entry point
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: amplifier:behaviors/amplifier-expert
```

The `includes:` list drives recursive bundle composition. Each entry is either a full URI (`git+https://`) or a namespace-qualified path (`namespace:subpath`).

---

## 2. Bundle Loading: `BundleRegistry._load_single()`

**`amplifier-foundation/amplifier_foundation/registry.py:1267-1301`** — Top-level convenience function `load_bundle(source)` creates a `BundleRegistry` and calls `_load_single()`.

**`registry.py:348-573`** — `_load_single(name_or_uri, ...)`:

1. **Cache check** (`registry.py:387-388`): Returns cached `Bundle` if already loaded via `self._loaded_bundles[uri]`.
2. **Circular dependency guard** (`registry.py:390-394`): Uses a `frozenset` loading chain; raises `BundleDependencyError` if same URI appears in chain.
3. **Diamond deduplication** (`registry.py:396-398`): If another `asyncio.Task` is already loading this URI, awaits its `Future` instead of re-fetching.
4. **URI → local path**: `self._source_resolver.resolve(uri)` → `ResolvedSource.active_path` (`registry.py:414-418`).
5. **File parsing** (`registry.py:420-421`): `self._load_from_path(local_path)`.
6. **Nested bundle detection** (`registry.py:427-493`): Walks up directory tree to find root `bundle.md`; sets `source_base_paths[namespace] = source_root` for namespace resolution.
7. **Include composition** (`registry.py:551-554`): `self._compose_includes(bundle, ...)` if `bundle.includes` is non-empty.

---

## 3. URI Resolution: `SimpleSourceResolver`

**`amplifier-foundation/amplifier_foundation/sources/resolver.py:19-81`** — Dispatches to type-specific handlers:

- `FileSourceHandler` — `file://` and local paths
- `GitSourceHandler` — `git+https://` URIs (clones into `~/.amplifier/cache/`)
- `ZipSourceHandler` — `zip+https://`, `zip+file://`
- `HttpSourceHandler` — `https://`, `http://`

First matching handler wins (`resolver.py:77-79`). Handlers return a `ResolvedSource` with `active_path` (the actual local path to load from) and `source_root` (the root of the git clone or directory, used as stop boundary for nested bundle detection).

`#subdirectory=` fragments on git URIs (e.g., `git+https://...@main#subdirectory=behaviors/foo.yaml`) cause the resolver to clone the repo and return the subdirectory path as `active_path`.

---

## 4. File Parsing: `_load_from_path()` and `Bundle.from_dict()`

**`registry.py:574-620`** — `_load_from_path(path)`:
- Directory → looks for `bundle.md` or `bundle.yaml`
- File `.md` → `_load_markdown_bundle(path)` (`registry.py:604-612`)
- File `.yaml/.yml` → `_load_yaml_bundle(path)` (`registry.py:614-620`)

**`registry.py:604-612`** — `_load_markdown_bundle(path)`:
```python
content = path.read_text(encoding="utf-8")
frontmatter, body = parse_frontmatter(content)    # splits YAML from markdown
bundle = Bundle.from_dict(frontmatter, base_path=path.parent)
bundle.instruction = body.strip() if body.strip() else None
```

**`amplifier-foundation/amplifier_foundation/bundle.py:531-579`** — `Bundle.from_dict(data, base_path)`:
- Reads `bundle:`, `includes:`, `session:`, `providers:`, `tools:`, `hooks:`, `agents:`, `context:`
- Validates module lists via `_validate_module_list()` — raises `BundleValidationError` for malformed items
- Resolves relative module source paths against `base_path` at parse time (`bundle.py:750-764`)
- Context parsing: `_parse_context()` (`bundle.py:667-707`) splits into `resolved` (immediate) and `pending` (namespaced, deferred)
- Returns a `Bundle` dataclass

---

## 5. Include Composition: `_compose_includes()`

**`registry.py:622-735`** — `_compose_includes(bundle, parent_name, _loading_chain)`:

**Phase 0 — Preload namespace bundles** (`registry.py:640`):
`_preload_namespace_bundles(includes)` loads any `namespace:path` dependencies first so `local_path` is populated before path resolution.

**Phase 1 — Parse and resolve sources** (`registry.py:643-678`):
```python
for include in bundle.includes:
    include_source = self._parse_include(include)   # handles str or dict
    resolved_source = self._resolve_include_source(include_source)
    include_sources.append(resolved_source)
```

**`registry.py:840-939`** — `_resolve_include_source(source)`:
- Priority 1: `git+`, `http://`, `https://`, `file://` → returned as-is
- Priority 2: `namespace:path` syntax → constructs `git+https://...#subdirectory=path` URI by looking up namespace in registry
- Priority 3: Plain names → returned as-is for registry lookup

**Phase 2 — Parallel loading** (`registry.py:680-690`):
```python
tasks = [self._load_single(source, ..., _loading_chain=_loading_chain)
         for source in include_sources]
results = await asyncio.gather(*tasks, return_exceptions=True)
```
All includes are fetched/cloned concurrently. Failures (except `BundleDependencyError` for circular deps) are logged and skipped (non-fatal unless `strict=True`).

**Phase 3 — Composition** (`registry.py:730-735`):
```python
result = included_bundles[0]
for included in included_bundles[1:]:
    result = result.compose(included)
return result.compose(bundle)    # current bundle overrides includes
```
This gives later-wins semantics: the loading bundle's own config overrides its includes.

---

## 6. Bundle.compose(): Merge Strategy

**`bundle.py:98-213`** — `Bundle.compose(*others)` produces a new `Bundle` with merged configuration:

| Section | Merge Strategy |
|---------|---------------|
| `session`, `spawn` | `deep_merge()` — nested dicts merged, later wins for scalars |
| `providers`, `tools`, `hooks` | `merge_module_lists()` — merge by module ID (later overrides same module) |
| `agents` | `dict.update()` — later overrides earlier by agent name |
| `context` | Accumulate with `namespace:` prefix to avoid collisions |
| `instruction` | Last non-None replaces earlier |
| `source_base_paths` | Accumulates all namespace→path mappings (first-wins for each namespace) |
| `base_path` | Uses the composed-in bundle's `base_path` (ensures paths resolve locally) |

The `source_base_paths` dict (`bundle.py:114-119`) is critical: it maps each bundle namespace (e.g., `"foundation"`, `"amplifier"`) to the filesystem root of that bundle's clone, enabling `@namespace:path` mentions to resolve correctly in system prompts.

---

## 7. Module Activation: `Bundle.prepare()`

**`bundle.py:245-393`** — `Bundle.prepare(install_deps, source_resolver, progress_callback)`:

1. **Bundle package installation** (`bundle.py:302-314`): Installs the bundle's own Python package (if `pyproject.toml` exists) AND all included bundles' packages via `activator.activate_bundle_package(bundle_path)`. This ensures bundle-local imports work before modules load.

2. **Collect modules** (`bundle.py:316-371`): Iterates all module specs (orchestrator, context, providers, tools, hooks, and agent-level modules) applying optional `source_resolver` callback for app-layer overrides.

3. **Parallel activation** (`bundle.py:373-376`): `activator.activate_all(modules_to_activate)` — downloads and installs all modules concurrently.

4. **Resolver creation** (`bundle.py:383`): `BundleModuleResolver(module_paths, activator=activator)` — maps module IDs to local paths. The `activator` is retained for lazy activation of modules not in the initial activation set (agent-specific modules).

5. Returns `PreparedBundle(mount_plan, resolver, bundle, bundle_package_paths)`.

---

## 8. Session Creation: `PreparedBundle.create_session()`

**`bundle.py:1043-1171`** — `create_session(session_id, parent_id, ...)`:

1. **Create session** (`bundle.py:1085-1092`): `AmplifierSession(self.mount_plan, ...)` — validates `session.orchestrator` and `session.context` are present.
2. **Mount resolver** (`bundle.py:1095`): `await session.coordinator.mount("module-source-resolver", self.resolver)` — critical: makes modules findable.
3. **Register capabilities** (`bundle.py:1100-1112`): `bundle_package_paths` and `session.working_dir` registered as coordinator capabilities.
4. **Initialize session** (`bundle.py:1115`): `await session.initialize()` — triggers module loading.
5. **Resolve pending context** (`bundle.py:1118`): `self.bundle.resolve_pending_context()` — resolves namespaced context refs now that `source_base_paths` is populated.
6. **System prompt factory** (`bundle.py:1125-1169`): If bundle has instruction or context, creates a factory function that:
   - Re-reads all context files on every call (dynamic — picks up file changes)
   - Resolves `@namespace:path` mentions via `BaseMentionResolver`
   - Injects into context manager via `set_system_prompt_factory()`, or pre-resolves as fallback.

---

## 9. Module Loading: `initialize_session()` and `ModuleLoader.load()`

**`amplifier-core/python/amplifier_core/_session_init.py:22-248`** — `initialize_session(config, coordinator, session_id, parent_id)`:

Loads modules in strict order:
1. **Orchestrator** (required — raises `RuntimeError` if missing) — `_session_init.py:47-72`
2. **Context manager** (required — raises `RuntimeError` if missing) — `_session_init.py:74-99`
3. **Providers** (optional, failures logged/skipped) — `_session_init.py:122-183`
4. **Tools** (optional, failures logged/skipped) — `_session_init.py:185-205`
5. **Hooks** (optional, failures logged/skipped) — `_session_init.py:207-227`

Multi-instance provider support (`_session_init.py:101-119`): validates at most one provider entry per module may omit `instance_id`.

Each module: `mount_fn = await loader.load(module_id, config, source_hint, coordinator)` → `cleanup = await mount_fn(coordinator)`.

**`amplifier-core/python/amplifier_core/loader.py:176-338`** — `ModuleLoader.load(module_id, config, source_hint, coordinator)`:

1. **Cache check** (`loader.py:202-211`): Returns cached closure if module already loaded.
2. **Source resolver lookup** (`loader.py:217-224`): Gets `module-source-resolver` from coordinator (the `BundleModuleResolver` mounted at `create_session()`).
3. **Async resolution** (`loader.py:240-248`): `source_resolver.async_resolve(module_id, source_hint)` — fast path if already activated; lazy activation if not.
4. **sys.path injection** (`loader.py:254-260`): Adds `module_path` to `sys.path[0]` for import.
5. **Transport dispatch** (`loader.py:262-289`): Calls `amplifier_core._engine.resolve_module(path)` to read manifest:
   - `transport == "wasm"` → `_make_wasm_mount()` (`loader.py:627-658`)
   - `transport == "grpc"` → `_make_grpc_mount()` (`loader.py:660-697`)
   - Python (default) → falls through
6. **Validation** (`loader.py:292`): `_validate_module(module_id, module_path, config)` runs type-specific protocol validation.
7. **Entry point resolution** (`loader.py:309-318`): `importlib.metadata.entry_points(group="amplifier.modules")` — finds installed Python packages.
8. **Filesystem resolution** (`loader.py:321-330`): `importlib.import_module(f"amplifier_module_{id}")` — imports from `sys.path`.
9. **Returns** a closure `mount_with_config_*` binding `coordinator` and `config`.

---

## 10. Module Type → Mount Point Mapping

**`loader.py:31-38`** — Kernel-defined stable mapping:

```python
TYPE_TO_MOUNT_POINT = {
    "orchestrator": "orchestrator",
    "provider": "providers",
    "tool": "tools",
    "hook": "hooks",
    "context": "context",
    "resolver": "module-source-resolver",
}
```

Module type is declared by `__amplifier_module_type__` attribute (`loader.py:461-475`) or inferred from naming convention (`loader.py:489-523`). Mount point is derived from type by kernel, not declared by module.

---

## 11. Lazy Activation: `BundleModuleResolver.async_resolve()`

**`bundle.py:833-885`** — For modules not in the initial activation set (e.g., agent-specific tools):

```python
async with self._activation_lock:
    if module_id in self._paths:
        return BundleModuleSource(self._paths[module_id])
    module_path = await self._activator.activate(module_id, hint)
    self._paths[module_id] = module_path
```

Uses an `asyncio.Lock` for thread-safe activation; double-checks after acquiring lock (double-checked locking pattern).

---

## 12. Spawn: Bundle Composition for Sub-Sessions

**`bundle.py:1173-1390`** — `PreparedBundle.spawn(child_bundle, instruction, ...)`:

When `compose=True` (default): `effective_bundle = self.bundle.compose(child_bundle)` — merges parent bundle with child bundle, giving child overrides over parent.

Child gets parent's `BundleModuleResolver` (`bundle.py:1303`): `await child_session.coordinator.mount("module-source-resolver", self.resolver)` — modules pre-activated in parent are immediately available.

`provider_preferences` handled before session creation (`bundle.py:1276-1282`): applies provider/model preferences by rewriting the mount plan's provider section.

---

## Key Execution Path (Top-Down)

```
load_bundle("amplifier/bundle.md")                  registry.py:1267
  BundleRegistry._load_single(uri)                  registry.py:348
    SimpleSourceResolver.resolve(uri)               sources/resolver.py:63
      GitSourceHandler.resolve(...)                 sources/git.py
    _load_from_path(local_path)                     registry.py:574
      _load_markdown_bundle(path)                   registry.py:604
        parse_frontmatter(content)                  io/frontmatter.py
        Bundle.from_dict(frontmatter, base_path)    bundle.py:531
    _compose_includes(bundle)                       registry.py:622
      _preload_namespace_bundles(includes)          registry.py:773
      _parse_include(include)                       registry.py:963
      _resolve_include_source(source)               registry.py:840
      asyncio.gather(*[_load_single(...)])           registry.py:690  ← PARALLEL
      Bundle.compose(*included_bundles)             bundle.py:98

bundle.prepare()                                    bundle.py:245
  ModuleActivator.activate_bundle_package(...)      modules/activator.py
  ModuleActivator.activate_all(modules)             modules/activator.py
  BundleModuleResolver(module_paths, activator)     bundle.py:383

PreparedBundle.create_session()                     bundle.py:1043
  AmplifierSession(mount_plan)                      session.py:30
  coordinator.mount("module-source-resolver", ...)  bundle.py:1095
  session.initialize()                              session.py:110
    initialize_session(config, coordinator, ...)    _session_init.py:22
      ModuleLoader.load(orchestrator_id, ...)       loader.py:176
        BundleModuleResolver.async_resolve(...)     bundle.py:833
        sys.path.insert(0, module_path)             loader.py:256
        _engine.resolve_module(path) [transport]    loader.py:267
        _validate_module(...)                       loader.py:292
        mount_fn(coordinator)                       _session_init.py:66
      ModuleLoader.load(context_id, ...)
      ModuleLoader.load(provider_id, ...)  ← each provider, tool, hook
  bundle.resolve_pending_context()                  bundle.py:1118
  context_manager.set_system_prompt_factory(...)    bundle.py:1161
```
