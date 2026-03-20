# Unknowns: Entry Point Bundle Composition

**Topic:** Entry Point Bundle Composition  
**Status:** Open questions requiring further investigation

---

## U-01: `amplifier_core._engine` Rust Binary Availability

**Location:** `loader.py:267`
```python
from amplifier_core._engine import resolve_module
manifest = resolve_module(str(module_path))
```

**Question:** The transport dispatch (Python / WASM / gRPC) depends on `amplifier_core._engine` — a Rust extension module. The code has an `ImportError` fallback that silently falls through to Python loading (`loader.py:281-284`). It is unknown:
- When is the Rust engine present vs absent in production deployments?
- Does the `.wasm` and gRPC transport path ever activate in this bundle's use case?
- What does `amplifier.toml` look like for a WASM or gRPC module?

**Impact:** If the Rust engine is always present, transport dispatch is deterministic. If it is absent in some deployments, all modules silently fall back to Python — which may hide misconfigured WASM/gRPC modules.

---

## U-02: `GitSourceHandler` Caching and Invalidation

**Location:** `sources/resolver.py:46-51` → `sources/git.py`

**Question:** Git bundles are cloned into `~/.amplifier/cache/`. The cache check logic in `_load_single()` (`registry.py:387-388`) uses an in-memory `_loaded_bundles` dict keyed by URI. It is unknown:
- How does the `GitSourceHandler` determine if a cached clone is stale?
- Does the `@main` branch pin actually re-fetch on new commits, or is it frozen once cached?
- What is the on-disk cache structure (bare clone vs working tree)?

**Impact:** Outdated cached bundles could silently serve stale behavior without any user warning.

---

## U-03: `InstallStateManager` and Dependency Re-Installation

**Location:** `modules/activator.py` → `modules/install_state.py`

**Question:** `activator.finalize()` (`bundle.py:379`) saves install state to disk. The `ModuleActivator` skips re-activation for `cache_key in self._activated` within a session, but on the next session start:
- How does `InstallStateManager` decide whether to re-run `uv pip install`?
- Is there a hash or timestamp check, or is it purely presence-based?
- What happens when a module's `requirements.txt` changes but the cached directory still exists?

**Impact:** Stale module dependencies could cause silent runtime failures that are hard to diagnose.

---

## U-04: `_resolve_include_source()` with No `local_path`

**Location:** `registry.py:910-916`

**Question:** When a namespace bundle's URI is `git+https://` but `local_path` is `None` (bundle is currently being loaded), the code constructs a URI directly without verification:
```python
return f"{base_uri}#subdirectory={rel_path}"
```
This is a "construct and hope" path. It is unknown:
- Does this ever fire in practice for the `amplifier` entry bundle?
- Could this cause a race condition in concurrent include loading where two tasks both construct unverified URIs?

**Impact:** Could produce subtle include failures for self-referencing bundles with no local cache.

---

## U-05: System Prompt Factory Re-read Behavior

**Location:** `bundle.py:985-1041`

**Question:** The system prompt factory is registered to re-read all context files and re-resolve `@mentions` on every `get_messages_for_request()` call. It is unknown:
- How frequently is `get_messages_for_request()` called in the streaming orchestrator?
- Is there any caching within the factory, or does it re-read every file every turn?
- For large bundles (e.g., `foundation` with 40+ includes), what is the performance impact?

**Impact:** Could cause I/O-bound latency on every turn for bundles with many context files.

---

## U-06: `_pending_context` Resolution Timing

**Location:** `bundle.py:467-499`, `bundle.py:1118`

**Question:** Namespaced context references (e.g., `foundation:context/file.md`) are stored as `_pending_context` during parsing because `source_base_paths` isn't available yet. `resolve_pending_context()` is called in `PreparedBundle.create_session()` after `session.initialize()`.

- Is `_pending_context` ever accessed between `Bundle.from_dict()` and `create_session()`?
- What happens if `resolve_pending_context()` fails silently for a namespace that was never loaded (unregistered bundle)?

**Impact:** Silently missing context files would result in the system prompt lacking expected context without any error.

---

## U-07: Spawn Composition and Tool Inheritance

**Location:** `bundle.py:1255-1258`

**Question:** When `PreparedBundle.spawn(child_bundle, ..., compose=True)`, it calls `self.bundle.compose(child_bundle)`. The comment in `bundle.py:1059` says "tool_inheritance / hook_inheritance filtering is app-layer policy." It is unknown:
- Where exactly does the app layer apply tool inheritance filtering?
- How does the `spawn` config section (`bundle.py:65-67`) interact with the merge?
- Is the `exclude_tools` field in `spawn` config enforced here or at a different layer?

**Impact:** Understanding tool inheritance is critical for understanding what capabilities child agents actually receive.

---

## U-08: `BundleModuleResolver` vs `ModuleLoader.discover()`

**Location:** `loader.py:80-101`

**Question:** `ModuleLoader` has a `discover()` method that scans entry points and filesystem. When a `module-source-resolver` is mounted, this path is bypassed entirely (`loader.py:225-232`). It is unknown:
- Is `discover()` ever called in the foundation-based flow?
- Is it used only for standalone usage without `BundleRegistry`?

**Impact:** Understanding when `discover()` activates helps clarify the boundary between kernel-native and foundation-mediated module loading.

---

## U-09: Multi-Provider Instance Remapping Edge Case

**Location:** `_session_init.py:133-175`

**Question:** For multi-instance providers, the code takes a "snapshot" of the current provider at the default name before loading, then remounts the previous occupant after remapping. This logic is complex:
```python
existing_at_default = _snap_dict.get(_default_name)
# ... load new instance ...
# if instance_id != default_name AND existing_at_default:
#     restore existing_at_default to default_name
```
- What is the intended behavior when three+ instances of the same provider module are loaded?
- Is there a test covering the three-instance case?

**Impact:** Incorrect provider remapping could silently shadow a provider, causing the wrong model to be used.

---

## U-10: App-Layer Entry Points Not Traced

**Question:** This investigation traced the foundation library layer. The actual CLI entry points that call `load_bundle()` and `bundle.prepare()` were not located in this workspace. The `amplifier-foundation/amplifier_foundation/` package provides the library, but the app-layer code (CLI, API server) that:
- Reads user configuration
- Decides which bundle to load
- Calls `create_session()` and `session.execute()`

...was not found in the `amplifier-foundation` or `amplifier-core` repos. The actual session runner (e.g., `amplifier-app-cli`) is referenced in comments (`bundle.py:1199`) but was not available in this workspace.

**Impact:** The full end-to-end flow from user invocation to session execution cannot be traced without the app-layer code.
