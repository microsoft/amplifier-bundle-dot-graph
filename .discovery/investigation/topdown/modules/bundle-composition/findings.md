# Synthesis: Entry Point Bundle Composition

**Module:** Entry Point Bundle Composition
**Investigation:** Top-Down Discovery
**Fidelity:** Standard
**Date:** 2026-03-20
**Agents contributing:** code-tracer (1 of 1)

---

## Executive Summary

The bundle composition system is a multi-phase pipeline spanning two repositories (amplifier-foundation for bundle management, amplifier-core for module loading) with five key stages: URI resolution, file parsing, recursive include composition, module activation, and session creation. All findings originate from a single agent (code-tracer) and are classified as MEDIUM confidence. No inter-agent discrepancies exist, but 10 open unknowns from the code-tracer warrant further investigation — particularly around Rust engine availability, git cache invalidation, dependency re-installation semantics, and spawn tool inheritance.

---

## Convergence Table

Since only one agent (code-tracer) produced artifacts, all findings are single-source. No multi-agent convergence is possible. Every finding below carries MEDIUM confidence.

| Finding | Agents Confirming | Confidence |
|---------|-------------------|------------|
| Two public entry points funnel into `_load_single()` | code-tracer | MEDIUM |
| URI resolution via `SimpleSourceResolver` with 4 handler types | code-tracer | MEDIUM |
| Two-phase include loading (sequential namespaces, then parallel recursive) | code-tracer | MEDIUM |
| Left-to-right composition with declaring bundle applied last (wins) | code-tracer | MEDIUM |
| `deep_merge()` for session/spawn dicts; `merge_module_lists()` by module ID | code-tracer | MEDIUM |
| Cycle detection via `frozenset` loading chain per call tree | code-tracer | MEDIUM |
| Diamond deduplication via `_pending_loads` Future coalescing | code-tracer | MEDIUM |
| Deferred context resolution via `_pending_context` + `resolve_pending_context()` | code-tracer | MEDIUM |
| Sequential bundle package install before parallel module activation | code-tracer | MEDIUM |
| `BundleModuleResolver` with `asyncio.Lock` for lazy activation | code-tracer | MEDIUM |
| System prompt factory re-reads context files on every request | code-tracer | MEDIUM |
| Spawn composes parent+child, shares parent's `BundleModuleResolver` | code-tracer | MEDIUM |
| Module loading order: orchestrator > context > providers > tools > hooks | code-tracer | MEDIUM |
| Transport dispatch: Python (default), WASM, gRPC via `_engine.resolve_module()` | code-tracer | MEDIUM |

---

## Single-Source Findings

All findings below are `[single-source: code-tracer]`. They represent a code-level trace through the bundle composition pipeline with file:line evidence.

### F-01: Entry Point Architecture [single-source: code-tracer]

Two public entry points converge into one internal loader:
- `load_bundle(source)` at `registry.py:1267` — convenience function creating a `BundleRegistry`
- `BundleRegistry._load_single(uri)` at `registry.py:348` — the core loader with cache check, cycle guard, diamond dedup, source resolution, parsing, nested detection, and include composition

**Evidence:** `registry.py:1267-1301` (load_bundle), `registry.py:348-573` (_load_single)

### F-02: URI Resolution Pipeline [single-source: code-tracer]

`SimpleSourceResolver.resolve(uri)` (`sources/resolver.py:63`) dispatches via first-match to four handlers:
- `FileSourceHandler` — `file://` and local paths
- `GitSourceHandler` — `git+https://` URIs (shallow clones to `~/.amplifier/cache/`)
- `ZipSourceHandler` — `zip+https://`, `zip+file://`
- `HttpSourceHandler` — `https://`, `http://`

Git URIs support `#subdirectory=` fragments for nested bundle access within a single clone.

**Evidence:** `sources/resolver.py:19-81`

### F-03: Bundle File Parsing [single-source: code-tracer]

`_load_from_path()` (`registry.py:574`) detects format by extension:
- `.md` -> `_load_markdown_bundle()` -> `parse_frontmatter()` + `Bundle.from_dict()`
- `.yaml/.yml` -> `_load_yaml_bundle()` -> `Bundle.from_dict()`

`Bundle.from_dict()` (`bundle.py:531-579`) parses all sections (`bundle:`, `includes:`, `session:`, `providers:`, `tools:`, `hooks:`, `agents:`, `context:`), validates module lists, and resolves relative source paths against `base_path` at parse time.

Context parsing (`_parse_context()` at `bundle.py:667-707`) splits into `resolved` (immediate local paths) and `_pending_context` (namespaced refs deferred until `source_base_paths` is populated).

**Evidence:** `registry.py:574-620`, `bundle.py:531-579`, `bundle.py:667-707`

### F-04: Root Bundle Detection [single-source: code-tracer]

After parsing, `_load_single()` walks UP the directory tree (`registry.py:427-493`) from the loaded bundle to a `source_root` stop boundary, looking for a root `bundle.md`. Found root bundles register their namespace in `source_base_paths`, enabling `@namespace:path` context mentions across composed bundles.

**Evidence:** `registry.py:427-493`

### F-05: Two-Phase Include Composition [single-source: code-tracer]

`_compose_includes()` (`registry.py:622-735`) orchestrates:

1. **Phase 0 — Sequential namespace pre-loading** (`registry.py:640`): `_preload_namespace_bundles()` loads namespace bundles first so `local_path` is populated
2. **Phase 1 — Parse and resolve** (`registry.py:643-678`): Each include parsed via `_parse_include()` and resolved via `_resolve_include_source()`
3. **Phase 2 — Parallel recursive loading** (`registry.py:680-690`): `asyncio.gather()` loads all includes concurrently, each recursing through `_load_single()`
4. **Phase 3 — Composition** (`registry.py:730-735`): Included bundles merged left-to-right via `Bundle.compose()`, declaring bundle applied LAST (wins)

**Evidence:** `registry.py:622-735`, `registry.py:773`, `registry.py:840-939`

### F-06: Composition Merge Semantics [single-source: code-tracer]

`Bundle.compose(*others)` (`bundle.py:98-213`) applies distinct strategies per section:

| Section | Strategy |
|---------|----------|
| `session`, `spawn` | `deep_merge()` — nested dicts merged recursively, later wins for scalars |
| `providers`, `tools`, `hooks` | `merge_module_lists()` — merge by module ID, later overrides same module |
| `agents` | `dict.update()` — later overrides earlier by agent name |
| `context` | Accumulate with `namespace:` prefix |
| `instruction` | Last non-None replaces earlier |
| `source_base_paths` | Accumulate; first registration wins for each namespace |

**Evidence:** `bundle.py:98-213`, `bundle.py:114-119`

### F-07: Cycle Detection and Deduplication [single-source: code-tracer]

- **Cycle detection** (`registry.py:390-394`): `_loading_chain: frozenset[str]` tracks URIs per call tree; raises `BundleDependencyError` on repeat
- **Diamond deduplication** (`registry.py:396-398`): If another `asyncio.Task` is already loading a URI, awaits its `Future` instead of re-fetching
- **`#subdirectory=` exemption**: Nested bundle URIs with subdirectory fragments are treated as distinct URIs for cycle detection purposes

**Evidence:** `registry.py:387-398`

### F-08: Module Activation Pipeline [single-source: code-tracer]

`Bundle.prepare()` (`bundle.py:245-393`):
1. **Sequential** bundle package installation (`bundle.py:302-314`) — installs `pyproject.toml` packages for all namespaces
2. **Parallel** module activation via `ModuleActivator.activate_all()` (`bundle.py:373-376`)
3. Build `BundleModuleResolver(module_paths, activator)` (`bundle.py:383`) — retains activator for lazy activation
4. Return `PreparedBundle(mount_plan, resolver, bundle, bundle_package_paths)`

**Evidence:** `bundle.py:245-393`

### F-09: Session Creation [single-source: code-tracer]

`PreparedBundle.create_session()` (`bundle.py:1043-1171`):
1. Create `AmplifierSession(mount_plan)` — validates orchestrator and context present
2. Mount `BundleModuleResolver` as `module-source-resolver` on coordinator
3. Call `session.initialize()` -> `initialize_session()` which loads modules in strict order: orchestrator > context > providers > tools > hooks
4. Resolve pending context via `resolve_pending_context()`
5. Register system prompt factory that re-reads context files on every `get_messages_for_request()` call

**Evidence:** `bundle.py:1043-1171`, `_session_init.py:22-248`

### F-10: Module Loading in amplifier-core [single-source: code-tracer]

`ModuleLoader.load()` (`loader.py:176-338`):
1. Cache check -> source resolver lookup -> `async_resolve()` (fast path or lazy activation)
2. `sys.path.insert(0, module_path)` for import
3. Transport dispatch via `_engine.resolve_module()`: WASM -> `_make_wasm_mount()`, gRPC -> `_make_grpc_mount()`, Python -> falls through
4. Validation via `_validate_module()`, then entry point or filesystem resolution
5. Returns closure `mount_with_config_*` binding coordinator and config

Module type -> mount point mapping is kernel-defined (`TYPE_TO_MOUNT_POINT` at `loader.py:31-38`), not declared by modules.

**Evidence:** `loader.py:176-338`, `loader.py:31-38`

### F-11: Spawn Composition [single-source: code-tracer]

`PreparedBundle.spawn()` (`bundle.py:1173-1390`):
- When `compose=True` (default): `effective_bundle = self.bundle.compose(child_bundle)` — child overrides parent
- Child receives parent's `BundleModuleResolver` — pre-activated modules immediately available
- `provider_preferences` applied before session creation by rewriting provider section

**Evidence:** `bundle.py:1173-1390`, `bundle.py:1303`

---

## Cross-Cutting Insights

### CI-01: Sequential-then-Parallel as Recurring Architecture

The bundle composition system applies a **sequential-then-parallel** pattern at three distinct levels:
- **Include loading:** Sequential namespace pre-load -> parallel recursive loads
- **Module activation:** Sequential bundle package install -> parallel module activation
- **Session init:** Strictly ordered module loading (orchestrator first, hooks last)

This reflects a deliberate dependency ordering — later parallel phases depend on state populated by earlier sequential phases. This is an architectural pattern, not an optimization gap.

### CI-02: `source_base_paths` as Critical Cross-Cutting State

The `source_base_paths` dict on `Bundle` bridges composition and resolution. It is:
- **Populated** during root bundle detection (F-04) and composition merge (F-06)
- **Consumed** during pending context resolution (F-09), agent lookup, and bundle package installation (F-08)
- **Shared** across spawn boundaries (F-11) via parent resolver reuse

This dict is the single most important piece of cross-cutting state. Its "first registration wins" merge semantics make it sensitive to load ordering in diamond dependency scenarios.

### CI-03: Three-Layer Cache and Deduplication

Three distinct layers prevent redundant work, composed implicitly (no explicit orchestration):
1. `_loaded_bundles` — already-loaded bundles by URI (memory cache)
2. `_pending_loads` — in-flight Future deduplication (concurrent coalescing)
3. Git clone cache — deterministic `sha256` key on disk

The implicit composition means cache invalidation behavior may be non-obvious, particularly for the interaction between git clone cache staleness and in-memory bundle cache.

### CI-04: Two-Repo Boundary at Module Loading

The pipeline crosses an architectural boundary between amplifier-foundation (bundle management: registry, sources, composition) and amplifier-core (module loading: `ModuleLoader`, `initialize_session`). The bridge is the `module-source-resolver` coordinator mount point — foundation provides the resolver, core consumes it. This is a clean separation of concerns, with the coordinator acting as the integration point.

---

## Discrepancy Register

No inter-agent discrepancies exist because only one agent (code-tracer) produced artifacts.

| ID | Description | Agents | Status |
|----|-------------|--------|--------|
| -- | No discrepancies (single-agent investigation) | -- | N/A |

---

## Unknowns and Open Questions

These originate directly from the code-tracer's unknowns file (U-01 through U-10). They are promoted verbatim; none are invented or reinterpreted.

### OQ-01: Rust Engine Availability (from code-tracer U-01) — MEDIUM

**Question:** `amplifier_core._engine` (Rust extension) controls transport dispatch. The `ImportError` fallback silently falls through to Python loading. When is the Rust engine present vs absent? Could this hide misconfigured WASM/gRPC modules?

**Evidence:** `loader.py:267-284`
**Resolution needed:** Check deployment configurations for `_engine` availability; test WASM module with and without Rust engine.

### OQ-02: Git Cache Invalidation (from code-tracer U-02) — MEDIUM

**Question:** Git bundles cloned to `~/.amplifier/cache/`. How does `GitSourceHandler` determine if a cached clone is stale? Does `@main` re-fetch on new commits or freeze once cached?

**Evidence:** `sources/resolver.py:46-51`, `registry.py:387-388`
**Resolution needed:** Read `sources/git.py` to trace cache check logic and invalidation triggers.

### OQ-03: Dependency Re-Installation (from code-tracer U-03) — MEDIUM

**Question:** `InstallStateManager` saves state to disk. How does it decide whether to re-run `uv pip install`? Is there a hash/timestamp check or purely presence-based?

**Evidence:** `modules/activator.py`, `modules/install_state.py`
**Resolution needed:** Trace `InstallStateManager` logic for cache key computation and staleness detection.

### OQ-04: `_resolve_include_source` with No `local_path` (from code-tracer U-04) — MEDIUM

**Question:** When a namespace bundle's URI is `git+https://` but `local_path` is `None`, the code constructs a URI without verification. Could this race with concurrent include loading?

**Evidence:** `registry.py:910-916`
**Resolution needed:** Execution test with concurrent namespace-referencing includes.

### OQ-05: System Prompt Factory Performance (from code-tracer U-05) — MEDIUM

**Question:** The system prompt factory re-reads all context files and re-resolves `@mentions` on every `get_messages_for_request()` call. For large bundles (40+ includes), what is the I/O impact?

**Evidence:** `bundle.py:985-1041`
**Resolution needed:** Profile system prompt factory with a large bundle composition.

### OQ-06: `_pending_context` Resolution Timing (from code-tracer U-06) — MEDIUM

**Question:** Namespaced context references stored as `_pending_context` during parsing. Is it ever accessed before `resolve_pending_context()`? What happens if resolution fails silently for an unregistered namespace?

**Evidence:** `bundle.py:467-499`, `bundle.py:1118`
**Resolution needed:** Check for early access to pending context; test with intentionally unregistered namespace.

### OQ-07: Spawn Tool Inheritance (from code-tracer U-07) — HIGH

**Question:** When `spawn(compose=True)`, where exactly does the app layer apply tool inheritance filtering? How does the `spawn` config section interact with `compose()`? Where is `exclude_tools` enforced?

**Evidence:** `bundle.py:1255-1258`, `bundle.py:1059` (comment referencing app-layer policy)
**Resolution needed:** Trace spawn config and tool filtering in amplifier-app-cli.

### OQ-08: `BundleModuleResolver` vs `ModuleLoader.discover()` (from code-tracer U-08) — LOW

**Question:** `ModuleLoader.discover()` scans entry points and filesystem but is bypassed when `module-source-resolver` is mounted. Is `discover()` ever used in the foundation-based flow?

**Evidence:** `loader.py:80-101`, `loader.py:225-232`
**Resolution needed:** `grep -rn "discover" amplifier-core/` to locate call sites.

### OQ-09: Multi-Provider Instance Remapping (from code-tracer U-09) — MEDIUM

**Question:** The multi-instance provider logic snapshots existing provider at default name, loads new instance, then restores. What happens with 3+ instances of the same provider module?

**Evidence:** `_session_init.py:133-175`
**Resolution needed:** Test with 3+ provider instances; review test suite for multi-instance coverage.

### OQ-10: App-Layer Entry Points Not Traced (from code-tracer U-10) — HIGH

**Question:** The CLI entry points that call `load_bundle()` and `bundle.prepare()` were not found in this workspace. The full end-to-end flow from user invocation to session execution cannot be traced.

**Evidence:** `bundle.py:1199` (comment referencing app-layer code)
**Resolution needed:** Include `amplifier-app-cli` repository in workspace for complete pipeline trace.

---

## Recommended Next Steps

1. **Behavior-observer pass** — Catalog 10+ real bundle compositions across the ecosystem to validate merge semantics and identify common patterns vs edge cases. Priority: OQ-05 (performance), OQ-07 (tool inheritance).
2. **Integration-mapper pass** — Map the two-repo boundary between amplifier-foundation and amplifier-core, particularly the `module-source-resolver` mount point contract and spawn resolver sharing. Priority: CI-04.
3. **Trace git cache handler** — Read `sources/git.py` to resolve OQ-02 (cache invalidation). This is achievable by code reading alone.
4. **Include app-layer code** — Add `amplifier-app-cli` to workspace to trace the full pipeline (OQ-10) and locate tool inheritance filtering (OQ-07).
5. **Execution-based verification** — Run adversarial tests for diamond dependency ordering (CI-02/`source_base_paths`) and multi-provider remapping (OQ-09), which cannot be resolved by code reading alone.

---

## Investigation Metadata

- **Single-agent limitation:** All findings are MEDIUM confidence. A second agent perspective (behavior-observer or integration-mapper) would elevate confirmed findings to HIGH.
- **Scope boundary:** Code-tracer traced amplifier-foundation registry/bundle code and amplifier-core session/loader code. App-layer CLI code is out of scope.
- **Artifacts consumed:** `agents/code-tracer/findings.md` (295 lines), `agents/code-tracer/unknowns.md` (145 lines), `agents/code-tracer/diagram.dot` (202 lines)
