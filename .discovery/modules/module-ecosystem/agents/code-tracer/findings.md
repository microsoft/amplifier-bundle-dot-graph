# Code Tracer Findings: Module Ecosystem

**Topic:** Module Ecosystem  
**Repository:** `/home/bkrabach/dev/dot-graph-bundle/amplifier`  
**Investigator role:** HOW agent — execution paths with file:line evidence

---

## Summary

The Module Ecosystem is a layered, protocol-driven system for dynamically loading, validating, and mounting Python (and polyglot) capabilities into a session coordinator. The kernel (`amplifier-core`) defines mechanisms-only contracts; all policy (where to find modules, how to install them) lives in the app layer (`amplifier-foundation`).

---

## Entry Points

### Session Initialization Triggers Module Loading

`amplifier-core/python/amplifier_core/_session_init.py:22-248` — `initialize_session()` is the orchestration entry point. Called by the Rust session wrapper after `AmplifierSession` is created. It:

1. Creates or retrieves a `ModuleLoader` from `coordinator.loader` (lines 40–45)
2. Loads orchestrator (REQUIRED — fatal failure) (lines 47–72)
3. Loads context manager (REQUIRED — fatal failure) (lines 74–99)
4. Validates multi-instance provider specs (lines 101–119)
5. Loads providers (NON-FATAL — warning on failure) (lines 121–183)
6. Loads tools (NON-FATAL — warning on failure) (lines 185–205)
7. Loads hooks (NON-FATAL — warning on failure) (lines 207–227)
8. Emits `session:fork` event if child session (lines 229–246)

**Critical asymmetry**: orchestrator and context manager raise `RuntimeError` on failure; providers, tools, and hooks only log `logger.warning`. A session can start with no tools if they all fail to load.

---

## Execution Path 1: Module Loading via `ModuleLoader.load()`

`amplifier-core/python/amplifier_core/loader.py:176-338`

### Step 1: Cache check
`loader.py:202-211` — If `module_id` already in `_loaded_modules`, return cached raw function wrapped in a fresh closure with the provided `config`.

### Step 2: Source resolver lookup
`loader.py:216-234` — Attempts `coordinator.get("module-source-resolver")`. If no resolver mounted, falls back to `_load_direct()` (entry points + filesystem discovery).

### Step 3: Resolution (if resolver present)
`loader.py:237-248` — Calls `source_resolver.async_resolve(module_id, source_hint=...)` (or sync `resolve()` for older resolvers), then `source.resolve()` to get a filesystem `Path`.

### Step 4: sys.path injection BEFORE validation
`loader.py:253-260` — `sys.path.insert(0, str(module_path))` — must happen before validation so the module's dependencies (installed via `uv pip install --target`) are importable.

### Step 5: Polyglot transport dispatch
`loader.py:262-289` — If `coordinator` is provided, calls `_engine.resolve_module(str(module_path))` (Rust). Reads manifest `transport` field:
- `"wasm"` → `_make_wasm_mount()` → `_engine.load_and_mount_wasm()`
- `"grpc"` → `_make_grpc_mount()` → reads `amplifier.toml`, delegates to `loader_grpc.load_grpc_module()`
- `"python"` or absent → falls through to Python path

### Step 6: Module validation (Python only)
`loader.py:292` — `_validate_module(module_id, module_path, config)` — runs type-appropriate validator (`ProviderValidator`, `ToolValidator`, etc.) from `validation/` package.

### Step 7: Entry point loading
`loader.py:308-318` — `importlib.metadata.entry_points(group="amplifier.modules")` — searches for matching entry point by name.

### Step 8: Filesystem import fallback
`loader.py:320-330` — `importlib.import_module(f"amplifier_module_{module_id.replace('-','_')}")` — checks for `module.mount` attribute.

### Step 9: Mount closure wrapping
`loader.py:313-317` — Returns:
```python
async def mount_with_config(coordinator: ModuleCoordinator, fn=raw_fn):
    return await fn(coordinator, config or {})
```

---

## Execution Path 2: Module Source Resolution (App-Layer)

`amplifier-foundation/amplifier_foundation/sources/resolver.py:19-81`

`SimpleSourceResolver.resolve(uri)`:
1. `parse_uri(uri)` → `ParsedURI`
2. Iterates handlers in priority order: `FileSourceHandler` → `GitSourceHandler` → `ZipSourceHandler` → `HttpSourceHandler`
3. First handler where `can_handle(parsed)` returns `True` wins
4. Returns `ResolvedSource(active_path, source_root)`

**Git source resolution** (`sources/git.py:144-229`):
- `_get_cache_path()`: SHA256(`"{git_url}@{ref}"`)[:16] + repo name — `git.py:48`
- If cache exists and `_verify_clone_integrity()` passes → return cached — `git.py:162-172`
- Otherwise: `git clone --depth 1 [--branch ref] git_url cache_path` — `git.py:185-195`
- Verifies clone: checks for `.git` + `pyproject.toml`/`setup.py`/`bundle.md` — `git.py:107-142`
- Saves cache metadata JSON (`cached_at`, `ref`, `commit`) — `git.py:207-217`

---

## Execution Path 3: Bundle Preparation (Foundation Layer)

`amplifier-foundation/amplifier_foundation/bundle.py:245-393` — `Bundle.prepare()`

### Step 1: Generate mount plan
`bundle.py:292` — `self.to_mount_plan()` extracts session/providers/tools/hooks/agents into a dict

### Step 2: Create `ModuleActivator`
`bundle.py:296` — `ModuleActivator(install_deps=True, base_path=self.base_path)`

### Step 3: Install bundle packages FIRST (critical ordering)
`bundle.py:302-314` — `activator.activate_bundle_package()` for each bundle in `source_base_paths`. **CRITICAL**: bundle packages (e.g., `amplifier_bundle_python_dev`) must be on sys.path before their own modules try to import from them.

### Step 4: Collect all modules to activate
`bundle.py:317-371` — Sweeps: orchestrator, context, providers, tools, hooks. **Also sweeps agent configs** to pre-activate modules needed by child sessions.

### Step 5: Parallel activation
`bundle.py:374-376` — `activator.activate_all(modules_to_activate)` → `asyncio.gather()` for concurrent download+install

### Step 6: Create `BundleModuleResolver`
`bundle.py:383` — Maps module IDs → local paths. Holds `activator` reference for **lazy activation** of agent-specific modules not pre-activated.

### Step 7: Session creation
`bundle.py:1095` — `session.coordinator.mount("module-source-resolver", self.resolver)` mounts resolver BEFORE `session.initialize()` at line 1115.

---

## Execution Path 4: Module Activation (`ModuleActivator.activate()`)

`amplifier-foundation/amplifier_foundation/modules/activator.py:68-114`

1. **Cache check**: `cache_key = "{module_name}:{source_uri}"` — line 90
2. **Source download**: `self._resolver.resolve(source_uri)` → `ResolvedSource` — line 99
3. **Dependency install**: `await self._install_dependencies(module_path, ...)` — line 104 (uses `uv pip install --target`)
4. **sys.path injection**: `sys.path.insert(0, str(module_path))` — line 111
5. **Track activation**: `self._activated.add(cache_key)` — line 113

**Parallel activation** (`activator.py:125-165`): `activate_all()` uses `asyncio.gather(*tasks)`, catching individual exceptions without aborting the batch.

---

## Execution Path 5: Module `mount()` Contract

`modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py:274-301`

Every module exposes an async `mount(coordinator, config)` function. From `tool-dot-graph`:

```python
async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    tool = DotGraphTool()
    await coordinator.mount("tools", tool, name=tool.name)
    return {"name": "tool-dot-graph", "version": "0.4.0", "provides": ["dot_graph"]}
```

`_session_init.py:67-68`: If the return value is callable, registers it as cleanup: `coordinator.register_cleanup(cleanup)`.

---

## Execution Path 6: Coordinator (Rust Implementation)

`amplifier-core/crates/amplifier-core/src/coordinator.rs:74-101`

The `Coordinator` Rust struct (exposed via PyO3 as `RustCoordinator`, re-exported as `ModuleCoordinator`):

```rust
pub struct Coordinator {
    orchestrator: Mutex<Option<Arc<dyn Orchestrator>>>,   // single slot
    context: Mutex<Option<Arc<dyn ContextManager>>>,       // single slot
    providers: Mutex<HashMap<String, Arc<dyn Provider>>>,  // named map
    tools: Mutex<HashMap<String, Arc<dyn Tool>>>,           // named map
    capabilities: Mutex<HashMap<String, Value>>,            // generic registry
    channels: Mutex<HashMap<String, Vec<ContributorEntry>>>,// contribution channels
    cleanup_functions: Mutex<Vec<CleanupFn>>,
    hooks: Arc<HookRegistry>,
    cancellation: CancellationToken,
    ...
}
```

Mount methods:
- `coordinator.rs:131` — `set_orchestrator()` — single slot, overwrites
- `coordinator.rs:155` — `mount_provider(name, Arc<dyn Provider>)` — named map
- `coordinator.rs:180` — `mount_tool(name, Arc<dyn Tool>)` — named map

**Capability registry** (`coordinator.rs:348-358`): JSON values, used for app-layer → module communication without direct imports. Key capabilities registered by foundation:
- `"session.spawn"` — registered by `amplifier-app-cli` (`_register_session_spawning()`)
- `"bundle_package_paths"` — list of src/ directories needed by child sessions — `bundle.py:1101-1103`
- `"session.working_dir"` — working directory for tools — `bundle.py:1110-1112`
- `"mention_resolver"`, `"mention_deduplicator"` — for @-mention resolution — `bundle.py:1145-1150`
- `"self_delegation_depth"` — depth limiter for recursive delegation — `bundle.py:1327-1329`

---

## Module Type → Mount Point Mapping

`amplifier-core/python/amplifier_core/loader.py:31-38`

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

Type determination priority (`loader.py:425-523`):
1. **Primary**: `__amplifier_module_type__` module-level attribute — `loader.py:461`
2. **Fallback**: naming convention substring match — `loader.py:506-521`
3. **Default**: `"tool"` if no match — `loader.py:522-523`

---

## Module Interfaces (Protocol Definitions)

`amplifier-core/python/amplifier_core/interfaces.py`

Five `@runtime_checkable` protocols:
- `Orchestrator` (line 34): `execute(prompt, context, providers, tools, hooks, **kwargs) -> str`
- `Provider` (line 68): `name`, `get_info()`, `list_models()`, `complete(request) -> ChatResponse`, `parse_tool_calls(response)`
- `Tool` (line 135): `name`, `description`, `execute(input: dict) -> ToolResult`
- `ContextManager` (line 162): `add_message()`, `get_messages_for_request()`, `get_messages()`, `set_messages()`, `clear()`
- `HookHandler` (line 212): `__call__(event: str, data: dict) -> HookResult`

---

## Error Handling Paths

### Fatal (abort session init)
`_session_init.py:69-72` — Orchestrator failure:
```python
raise RuntimeError(f"Cannot initialize without orchestrator: {str(e)}")
```
`_session_init.py:97-99` — Context manager failure (same pattern)

### Non-fatal (continue with degraded session)
`_session_init.py:179-183` — Provider/tool/hook failures: `logger.warning(...)` only

### Source resolution fallback
`loader.py:296-306` — If source resolver raises `ModuleNotFoundError`, falls back to direct entry-point discovery before propagating the error.

---

## Multi-Instance Provider Support

`_session_init.py:101-178` — When a provider config includes `instance_id`:
1. Snapshot existing provider at default mount name before loading (lines 133-143)
2. Load provider (self-mounts to default name, e.g., `"anthropic"`)
3. Remap: `coordinator.mount("providers", new_instance, name=instance_id)` (line 165)
4. Restore previous default if overwritten (lines 167-175)

---

## Key Architectural Observations

1. **Strict kernel/policy separation**: `loader.py` and `module_sources.py` define only protocols. `SimpleSourceResolver`, `GitSourceHandler`, `ModuleActivator` provide all policy.

2. **Late binding via mount point injection**: The `"module-source-resolver"` mount point is optional — loader checks with `contextlib.suppress(ValueError)` and falls back gracefully. Kernel works in minimal deployments.

3. **Polyglot support is transparent**: WASM and gRPC modules dispatched before Python loading, using same `mount()` contract surface. Transport determined by `amplifier.toml` in module directory.

4. **Lazy activation for agent modules**: `BundleModuleResolver.async_resolve()` activates agent-specific modules on-demand with `asyncio.Lock` for thread safety (`bundle.py:869-884`).

5. **sys.path tracking for cleanup**: `loader.py:719-728` — `cleanup()` removes all paths added by this loader instance from `_added_paths: list[str]`.

6. **Bundle package install ordering is critical**: `bundle.py:298-314` — Bundle packages installed before modules activated. Modules may import from the bundle's own package (e.g., `amplifier_bundle_shadow`).

7. **Agents are not a module type**: `loader.py:514` comment — `# Note: No "agent" - agents are config data, not modules`. Agents are bundles loaded as configuration, not runtime modules.
