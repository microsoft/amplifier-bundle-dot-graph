# Unknowns: Module Ecosystem Code Tracer

**Topic:** Module Ecosystem  
**Status:** Questions requiring further investigation

---

## U-01: Rust `_engine` Module Internals

**Question:** What exactly does `_engine.resolve_module()` read from the module directory? What is the `amplifier.toml` manifest schema for WASM/gRPC modules?

**Evidence of gap:**
- `loader.py:267-269` — calls `resolve_module(str(module_path))` and reads `manifest.get("transport", "python")`
- `loader.py:692-696` — reads `amplifier.toml` via `tomli` for gRPC config, but the schema is not visible
- `amplifier_core/_engine.pyi` exists but wasn't read — contains the PyO3 bindings signatures

**What to investigate:** Read `amplifier-core/crates/amplifier-core/src/transport.rs` and `module_resolver.rs`, plus `_engine.pyi` for the full polyglot manifest schema.

---

## U-02: How `coordinator.mount()` Works in Python (PyO3 Bridge)

**Question:** The Python `coordinator.mount("tools", tool, name="foo")` call routes through PyO3 to Rust. How does the Python `Tool` protocol object get marshalled into Rust `Arc<dyn Tool>`?

**Evidence of gap:**
- `coordinator.py:8` re-exports `RustCoordinator as ModuleCoordinator` — the entire coordinator is Rust
- Python modules register Python objects via `coordinator.mount(...)` — how Rust holds a Python object as `Arc<dyn Tool>` requires PyO3 bridge understanding
- The `bindings/` directory in `amplifier-core` was not explored

**What to investigate:** `amplifier-core/bindings/` and the PyO3 bridge code that wraps Python callables as Rust traits.

---

## U-03: `_install_dependencies()` Full Implementation

**Question:** Exactly how does `ModuleActivator._install_dependencies()` install modules — specifically which `uv pip` flags are used, how are target directories structured, and what happens if `uv` is not available?

**Evidence of gap:**
- `activator.py:104` calls `self._install_dependencies(module_path, module_name)` 
- Only lines 100-165 were read; `_install_dependencies` body was not fully traced
- The comment at line 111 mentions "installed via `uv pip install --target`" but the actual subprocess call wasn't captured

**What to investigate:** Read `activator.py:249-487` for the full `_install_dependencies` implementation.

---

## U-04: `BundleModuleResolver` Integration with App-CLI Source Overrides

**Question:** How does `amplifier-app-cli` register module source overrides (settings-based overrides) to override the bundle's declared `source:` for a module?

**Evidence of gap:**
- `bundle.py:264-266` mentions a `source_resolver` callback parameter for `prepare()` that allows app-layer source override
- `bundle.py:285-287` shows the callback pattern: `def resolve_with_overrides(module_id, source) -> str`
- The actual implementation in `amplifier-app-cli` was not traced

**What to investigate:** Explore `amplifier-app-cli` (not locally present) to understand the settings-based override implementation.

---

## U-05: Hook Module Registration Path

**Question:** How exactly do hooks register themselves with `coordinator.hooks`? The `hooks.register()` call was referenced but the full `HookRegistry` implementation and registration parameters were not traced.

**Evidence of gap:**
- `_session_init.py:207-227` — loads hook via `loader.load()` → calls `hook_mount(coordinator)`
- `coordinator.rs:82` — `hooks: Arc<HookRegistry>` exists in coordinator
- The hook module `mount()` was not traced through to see the actual `hooks.register()` call chain
- `amplifier-core/crates/amplifier-core/src/hooks.rs` was not read

**What to investigate:** Read `hooks.rs` in Rust core and look at a hooks module (e.g., `amplifier-foundation/modules/hooks-session-naming/`) to see the full registration pattern.

---

## U-06: `context-simple` Module's `set_system_prompt_factory()` Implementation

**Question:** `bundle.py:1157-1160` checks `hasattr(context_manager, "set_system_prompt_factory")` before registering the dynamic system prompt factory. Is this a protocol method or an optional extension? Which context modules support it?

**Evidence of gap:**
- `interfaces.py` does NOT include `set_system_prompt_factory` in the `ContextManager` protocol — it's an optional extension
- `bundle.py:1162-1169` provides a fallback path for context managers that don't support it (pre-resolve and inject as system message)
- The actual `context-simple` and `context-persistent` module implementations were not read

**What to investigate:** Read the context module implementations to understand which support the factory pattern and how it integrates with `get_messages_for_request()`.

---

## U-07: Module Validation Implementation Details

**Question:** What exactly do the `ProviderValidator`, `ToolValidator`, etc. validate? Are they structural (import + introspect) or behavioral (call the function)?

**Evidence of gap:**
- `loader.py:542-587` — `_validate_module()` selects validator class and calls `validator.validate(package_path, config)`
- The `validation/` directory structure was seen but no validator file was read
- `validation/behavioral/` and `validation/structural/` subdirectories suggest two levels

**What to investigate:** Read `validation/tool.py` and `validation/provider.py` to understand what constitutes a passing validation.

---

## U-08: `resolver.py` in Foundation — Relationship to `SimpleSourceResolver`

**Question:** `amplifier-foundation/amplifier_foundation/sources/resolver.py` implements `SimpleSourceResolver`. Is there also a more advanced `StandardModuleSourceResolver` mentioned in `bundle.py:888`? What does it add?

**Evidence of gap:**
- `BundleModuleResolver.get_module_source()` at `bundle.py:887-900` notes "compatibility with StandardModuleSourceResolver's interface"
- This implies another resolver exists somewhere
- Only `SimpleSourceResolver` was traced

**What to investigate:** Search for `StandardModuleSourceResolver` in the codebase to understand its additional capabilities vs. `SimpleSourceResolver`.

---

## U-09: WASM Module Lifecycle

**Question:** After `load_and_mount_wasm()` is called, how does the WASM module register its tools/providers into the coordinator? Does it use the same `mount()` contract as Python modules?

**Evidence of gap:**
- `loader.py:653-658` — `wasm_mount()` calls `load_and_mount_wasm(coord, str(module_path))` and logs result, but returns `None` (no cleanup)
- The comment says "Calls Rust `load_and_mount_wasm()` binding which... mounts the loaded module directly into the coordinator's `mount_points` dict"
- The Rust implementation in `wasm_engine.rs` was not read

**What to investigate:** Read `amplifier-core/crates/amplifier-core/src/wasm_engine.rs` to understand the full WASM mounting contract.

---

## U-10: `coordinator.get("module-source-resolver")` — Mount Point Mechanism

**Question:** The Python coordinator calls `coordinator.get("module-source-resolver")` to retrieve the resolver. But the Rust coordinator only has typed fields for orchestrator/context/providers/tools. How do Python objects get stored in non-standard mount points like `"module-source-resolver"`?

**Evidence of gap:**
- `coordinator.py:8` — entire coordinator is `RustCoordinator`
- `loader.py:221` calls `coordinator.get("module-source-resolver")` via Python
- Rust coordinator doesn't have a generic string→object store visible in `coordinator.rs`
- The PyO3 bridge must implement a Python-side dictionary or use the capabilities map

**What to investigate:** The PyO3 bindings in `amplifier-core/bindings/` to understand how Python-side `get()/mount()` for arbitrary keys is implemented.
