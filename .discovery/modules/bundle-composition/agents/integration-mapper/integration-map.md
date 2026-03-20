# Integration Map: Bundle Composition

## Overview

Bundle Composition is the central orchestration mechanism in Amplifier's foundation layer. It sits at the intersection of 7 major subsystems, acting as the primary configuration pipeline that transforms declarative YAML/Markdown specifications into executable `AmplifierSession` instances. Every other mechanism in the system either feeds into or consumes the output of bundle composition.

**Key insight**: Bundle Composition is not a standalone feature — it is the *integration fabric* itself. The boundaries mapped below are not optional touchpoints; they are the critical data transformation seams that determine what an agent session can do.

---

## Boundary 1: Bundle Composition <-> Source Resolution

**Direction**: Composition -> Source Resolution (downstream dependency)
**What crosses**: URI strings (git+https://, file://, namespace:path)
**What returns**: `ResolvedSource` objects with `active_path` and `source_root`

### Integration Points

| Caller | Callee | Data Flow |
|--------|--------|-----------|
| `BundleRegistry._load_single()` | `SimpleSourceResolver.resolve(uri)` | URI string -> local Path |
| `BundleRegistry._resolve_include_source()` | `BundleRegistry._find_resource_path()` | namespace:path -> file:// or git+#subdirectory= URI |
| `ModuleActivator.activate()` | `SimpleSourceResolver.resolve(uri)` | Module source URI -> local Path |

### Boundary Characteristics

- **Protocol mismatch**: The `includes:` section in bundle YAML accepts 3 different formats (plain name, URI string, `{bundle: URI}` dict), all of which must be normalized to a URI before source resolution can proceed. This normalization happens in `_parse_include()`.
- **Namespace resolution gap**: When `includes` uses `namespace:path` syntax (e.g., `foundation:behaviors/streaming-ui`), the registry must first load the namespace bundle to discover its `local_path`, then construct a full `git+...#subdirectory=` URI. This creates a **two-phase load dependency** — namespace bundles must load before their nested sub-bundles.
- **Caching boundary**: `SimpleSourceResolver` delegates to protocol-specific handlers (`GitSourceHandler`, `FileSourceHandler`, `HttpSourceHandler`, `ZipSourceHandler`). The cache lives at `~/.amplifier/cache/`. Composition is unaware of cache freshness — it trusts whatever the resolver returns.

### Emergent Behavior

- **Circular dependency detection** uses a `frozenset` loading chain that tracks URIs across the recursive include tree. Subdirectory bundles get special treatment — they're allowed to reference their root bundle's namespace without triggering the cycle detector.
- **Diamond dependency deduplication** uses `asyncio.Future`-based deduplication in `_pending_loads`. If two includes reference the same URI concurrently, only one load executes and the other awaits the same Future.

---

## Boundary 2: Bundle Composition <-> Deep Merge System

**Direction**: Composition -> Deep Merge (internal mechanism)
**What crosses**: Two `Bundle` dataclass instances (parent + child)
**What returns**: One merged `Bundle` instance

### Integration Points

| Caller | Callee | Data Flow |
|--------|--------|-----------|
| `Bundle.compose()` | `deep_merge()` | session dicts, spawn dicts |
| `Bundle.compose()` | `merge_module_lists()` | providers, tools, hooks lists |
| `BundleRegistry._compose_includes()` | `Bundle.compose()` | Chain of included bundles |

### Boundary Characteristics

- **Section-specific merge strategies**: Bundle composition does NOT use a uniform merge. Each section has its own strategy:
  - `session`, `spawn` -> `deep_merge()` (recursive dict merge, child wins for scalars, lists concatenate with dedup)
  - `providers`, `tools`, `hooks` -> `merge_module_lists()` (merge by `module` or `id` key, deep merge configs for matching IDs)
  - `agents` -> simple `dict.update()` (later wins entirely by agent name)
  - `context` -> accumulate with namespace prefix (no collision, additive)
  - `instruction` -> later replaces earlier (last writer wins)
  - `name`, `version` -> later wins

- **List merge deduplication**: `deep_merge()` uses type-namespaced dedup keys (`(type, value)`) and `json.dumps(sort_keys=True)` for dicts. This prevents the string `"{'a': 1}"` from colliding with the dict `{'a': 1}`.

### Emergent Behavior

- **Silent list replacement impossible**: There is no mechanism for a child bundle to replace a parent's list entirely. If two behaviors declare the same tool module with list-typed config (e.g., `config.skills`), the lists always concatenate. This is documented as a known limitation — users must restructure data or avoid sharing module declarations.
- **Module config deep merge by ID**: When parent and child both declare `tool-skills` with different `config` sections, `merge_module_lists()` finds them by matching `module` key and deep-merges their configs. This is the mechanism that allows behaviors to layer config onto shared tools.

---

## Boundary 3: Bundle Composition <-> @Mention Resolution System

**Direction**: Bidirectional — Composition provides namespace registry -> Mention system resolves file paths
**What crosses (outward)**: `source_base_paths` dict (namespace -> Path), `Bundle` instances per namespace
**What crosses (inward)**: Resolved file Paths, loaded content for system prompt

### Integration Points

| Caller | Callee | Data Flow |
|--------|--------|-----------|
| `PreparedBundle._build_bundles_for_resolver()` | Creates `BaseMentionResolver` | source_base_paths -> bundles dict for resolver |
| `PreparedBundle._create_system_prompt_factory()` | `load_mentions()`, `format_context_block()` | instruction text -> resolved @mention content |
| `Bundle.resolve_pending_context()` | Uses `source_base_paths` | namespace:path refs -> resolved Paths |

### Boundary Characteristics

- **Two-phase context resolution**: Context references with namespace prefixes (e.g., `foundation:context/file.md`) cannot be resolved at parse time because `source_base_paths` isn't populated yet. They're stored in `_pending_context` and resolved later after composition, when all namespace paths are known. This is the **deferred resolution pattern**.
- **Dynamic system prompt factory**: The system prompt is NOT statically built at session creation. Instead, a factory function is registered that re-reads all @mentioned files on EVERY `get_messages_for_request()` call. This enables mid-session changes to files like `AGENTS.md` to take effect immediately.
- **ContentDeduplicator at boundary**: When both bundle context files and @mentions in the instruction reference the same file, `ContentDeduplicator` prevents duplicate content in the system prompt. A fresh deduplicator is created on each factory call.

### Emergent Behavior

- **Namespace collision risk**: `source_base_paths` is populated with the first-seen path for each namespace. If two included bundles register the same namespace with different paths, only the first one survives. The `compose()` method uses `if ns not in result.source_base_paths` — first writer wins.
- **Fallback for older context managers**: If the context manager doesn't support `set_system_prompt_factory()`, the system falls back to pre-resolving all @mentions once at session creation and injecting as a static system message. This means files modified mid-session won't be picked up — a silent behavioral degradation.

---

## Boundary 4: Bundle Composition <-> Session Lifecycle (Kernel)

**Direction**: Composition -> Kernel (downstream consumer of mount plans)
**What crosses**: Mount plan dict (`{session, providers, tools, hooks, agents, spawn}`)
**What returns**: Initialized `AmplifierSession` with mounted modules

### Integration Points

| Caller | Callee | Data Flow |
|--------|--------|-----------|
| `Bundle.to_mount_plan()` | Returns plain dict | Bundle fields -> mount plan dict |
| `PreparedBundle.create_session()` | `AmplifierSession(mount_plan)` | mount plan -> kernel session |
| `PreparedBundle.create_session()` | `session.coordinator.mount("module-source-resolver", resolver)` | BundleModuleResolver -> kernel |
| `PreparedBundle.create_session()` | `session.coordinator.register_capability(...)` | working_dir, bundle_package_paths, mention_resolver |
| `PreparedBundle.create_session()` | `session.initialize()` | Triggers module loading |

### Boundary Characteristics

- **Foundation-to-kernel contract**: The `to_mount_plan()` method is the **sole serialization boundary** between foundation's rich Bundle model and the kernel's plain dict configuration. The kernel knows nothing about bundles, @mentions, or composition — it receives a flat dict and loads modules from it.
- **Capability registration**: Foundation injects several capabilities into the kernel's coordinator:
  - `"module-source-resolver"` — the `BundleModuleResolver` that maps module IDs to paths
  - `"session.working_dir"` — resolved working directory for tools
  - `"bundle_package_paths"` — sys.path entries for bundle packages
  - `"mention_resolver"` and `"mention_deduplicator"` — for tools that need @mention resolution
- **Spawn policy is app-layer**: The `create_session()` method explicitly documents that spawn capability registration is NOT its responsibility. The app layer (CLI, API server) must register its own spawn capability.

### Emergent Behavior

- **Module pre-activation for agents**: `Bundle.prepare()` walks the `agents` section of the mount plan and pre-activates all modules declared in agent configs. Without this, spawned agent sessions would fail silently when their orchestrator/provider/tool modules aren't in the resolver's paths. This is a **composition-time side effect** that exists solely because of the spawn boundary.
- **Orchestrator config merge at spawn time**: When `PreparedBundle.spawn()` receives `orchestrator_config`, it modifies the child mount plan directly (`child_mount_plan["orchestrator"]["config"].update(orchestrator_config)`). This happens AFTER `to_mount_plan()` — the mount plan is a mutable intermediate, not a frozen contract.

---

## Boundary 5: Bundle Composition <-> Agent Spawning (Delegation)

**Direction**: Bidirectional — Composition provides spawn mechanism, spawning re-invokes composition
**What crosses (outward)**: Parent `PreparedBundle` + child `Bundle` -> spawned child session
**What crosses (inward)**: `{output, session_id, status, turn_count, metadata}` result dict

### Integration Points

| Caller | Callee | Data Flow |
|--------|--------|-----------|
| `PreparedBundle.spawn()` | `self.bundle.compose(child_bundle)` | Parent + child bundles -> composed bundle |
| `PreparedBundle.spawn()` | `apply_provider_preferences_with_resolution()` | Provider preferences -> modified mount plan |
| `PreparedBundle.spawn()` | `AmplifierSession(child_mount_plan)` | New session creation |
| `PreparedBundle.spawn()` | `child_context.set_messages(parent_messages)` | Context inheritance |
| Agent file loading | `_load_agent_file_metadata()` | .md frontmatter -> agent config with tools/providers/hooks |

### Boundary Characteristics

- **Re-composition on spawn**: When `compose=True` (default), spawning re-invokes `self.bundle.compose(child_bundle)`. The parent bundle provides the base (tools, providers, hooks), and the child bundle's config layers on top. This means spawn is NOT a fresh bundle load — it's a composition of the already-composed parent with the agent's overlay.
- **Agent metadata loading**: `_load_agent_file_metadata()` extracts not just `meta:` section (name, description) but also top-level `tools`, `providers`, `hooks`, `session`, and `provider_preferences` from agent .md frontmatter. Agents ARE bundles at the file format level.
- **Provider preference chain**: Spawning supports an ordered list of `ProviderPreference` objects with glob model patterns (e.g., `claude-haiku-*`). Resolution queries the parent session's coordinator to resolve patterns against available models.
- **Working directory inheritance**: Child sessions inherit `session.working_dir` from the parent coordinator, falling back to `session_cwd` or `bundle.base_path`.

### Emergent Behavior

- **Lazy module activation**: The `BundleModuleResolver` supports `async_resolve()` which activates modules on-demand during spawning if they weren't pre-activated by the parent bundle. This uses an `asyncio.Lock` for thread-safety, with double-check locking.
- **Self-delegation depth tracking**: Spawn registers `self_delegation_depth` as a coordinator capability so tool-delegate can read it via `get_capability()` for depth limiting. This is a composition -> coordinator -> tool cross-cutting concern.
- **Hook-based completion capture**: Spawn registers a temporary hook on `orchestrator:complete` (priority 999) to capture structured metadata from the child session's execution. This is unregistered in a `finally` block. The hook mechanism crosses the composition -> hooks -> orchestrator boundary.

---

## Boundary 6: Bundle Composition <-> Module Activation

**Direction**: Composition -> Activation (downstream)
**What crosses**: List of module specs (`{module, source}` dicts)
**What returns**: `dict[str, Path]` mapping module IDs to local paths

### Integration Points

| Caller | Callee | Data Flow |
|--------|--------|-----------|
| `Bundle.prepare()` | `ModuleActivator(base_path=self.base_path)` | Bundle's base_path -> activator |
| `Bundle.prepare()` | `activator.activate_bundle_package()` | Bundle paths -> package installation |
| `Bundle.prepare()` | `activator.activate_all(modules)` | Module specs -> activated paths |
| `Bundle.prepare()` | `BundleModuleResolver(module_paths, activator)` | Paths + activator -> resolver |

### Boundary Characteristics

- **Bundle package installation before module activation**: `prepare()` installs bundle packages (via `pyproject.toml`) BEFORE activating individual modules. This ordering is critical because modules may import from their parent bundle's package (e.g., `from amplifier_bundle_shadow import ShadowManager`).
- **Source resolver callback**: `prepare()` accepts an optional `source_resolver` callback that the app layer can provide for settings-based overrides. This allows the app to redirect module sources without foundation knowing about settings — a clean policy/mechanism separation.
- **Relative path resolution at parse time**: `_validate_module_list()` resolves relative source paths (`./modules/foo`) to absolute paths at parse time, before composition can change `base_path`. This fixes issue #190 where relative paths resolved against the wrong directory after composition.

### Emergent Behavior

- **sys.path pollution**: `ModuleActivator` adds module paths and bundle `src/` and `lib/` directories to `sys.path`. These paths accumulate across activations and are tracked in `_bundle_package_paths` for inheritance by child sessions. There's no cleanup mechanism — once on sys.path, always on sys.path.
- **Install state fingerprinting**: `InstallStateManager` tracks installed modules by fingerprint to skip redundant installations. But this fingerprint check doesn't account for source changes between git commits — if the cache path hasn't changed, the module won't be reinstalled even if the source code has changed.

---

## Boundary 7: Bundle Composition <-> Registry Persistence

**Direction**: Bidirectional — Composition drives registry state, registry provides load history
**What crosses (outward)**: Bundle names, URIs, versions, include relationships, load timestamps
**What crosses (inward)**: Previously registered bundle URIs, cached local paths

### Integration Points

| Caller | Callee | Data Flow |
|--------|--------|-----------|
| `BundleRegistry._load_single()` | `self._registry[name]` | Bundle state tracking |
| `BundleRegistry._compose_includes()` | `_record_include_relationships()` | Parent-child include graph |
| `BundleRegistry.save()` | `registry.json` | State -> disk |
| `BundleRegistry._validate_cached_paths()` | Startup cleanup | Stale path detection |

### Boundary Characteristics

- **Root vs nested bundle distinction**: The registry tracks whether each bundle is a `root` (at repo top level) or `nested` (loaded via `#subdirectory=`). Nested bundles preserve their root bundle's registry entry — a subdirectory load won't overwrite the root URI.
- **Include relationship graph**: The registry maintains bidirectional `includes`/`included_by` lists. When unregistering a bundle, these relationships are cleaned up in both directions.

### Emergent Behavior

- **Implicit root bundle registration**: When loading a nested bundle, the registry automatically registers the containing root bundle if not already registered. This ensures root bundles are tracked for version updates even when only accessed transitively through nested includes.

---

## Cross-Cutting Concerns

### 1. Namespace Resolution (spans all boundaries)
The `source_base_paths` dict is THE namespace registry. It's populated during composition, consumed by @mention resolution, used by agent path resolution, and critical for context file loading. A single namespace collision propagates errors across all consumers.

### 2. Path Resolution Strategy (spans Source Resolution, Module Activation, Mentions)
Three independent path resolution mechanisms coexist:
- `SimpleSourceResolver` for bundle/module URI -> local path
- `BaseMentionResolver` for @mention -> file path
- `construct_context_path` for context name -> file path

Each has slightly different fallback behavior and extension point conventions.

### 3. Ordering Sensitivity (spans Composition, Deep Merge, Includes)
Bundle composition is order-dependent: includes are composed left-to-right, then the declaring bundle layers on top. The `_compose_includes` method implements `included[0].compose(included[1]).compose(...).compose(declaring_bundle)`. This means the declaring bundle always wins, and later includes override earlier ones.

### 4. Install-time vs Runtime Separation
Bundle composition straddles two phases: install-time (downloading, activating, caching) and runtime (session creation, @mention resolution, agent spawning). The `PreparedBundle` is the bridge artifact — it captures install-time results and provides runtime entry points.
