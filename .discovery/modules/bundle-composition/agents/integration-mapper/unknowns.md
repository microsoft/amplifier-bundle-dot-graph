# Unknowns: Bundle Composition Integration Boundaries

## Unresolved Boundary Questions

### U-01: App-Layer Spawn Capability Registration (High Priority)

**Boundary**: Bundle Composition <-> Agent Spawning <-> App Layer
**Question**: How does the app layer (CLI, API server) register its spawn capability, and what exact contract does it implement?

`PreparedBundle.create_session()` explicitly states: "Session spawning capability registration is APP-LAYER policy. Apps should register their own spawn capability." However, this investigation was scoped to the foundation and core repositories. The actual spawn capability implementation lives in the app layer (e.g., `amplifier-app-cli/session_spawner.py` referenced in comments), which was not examined.

**Why it matters**: The spawn capability is the bridge between the `task` tool (which the LLM invokes) and `PreparedBundle.spawn()` (which foundation provides). The app layer translates between them, handling:
- Resolving agent names to Bundle objects
- tool_inheritance / hook_inheritance filtering policy
- Agent config lookup from coordinator

Without examining this boundary, we cannot confirm whether the app layer's contract matches foundation's expectations.

### U-02: Context Manager `set_system_prompt_factory()` Contract (Medium Priority)

**Boundary**: Bundle Composition <-> @Mention Resolution <-> Context Manager Module
**Question**: Which context manager modules support `set_system_prompt_factory()`, and what is the behavioral difference for those that don't?

The code has a two-path branch:
1. If `context_manager` has `set_system_prompt_factory` -> register dynamic factory (files re-read each turn)
2. Else -> pre-resolve @mentions once and inject as static system message

This creates a **silent behavioral split** where the same bundle configuration produces different runtime behavior depending on which context manager module is mounted. We did not examine the context manager modules to determine which path is taken in practice.

**Why it matters**: Users composing bundles with different context managers may get unexpectedly stale @mention content without any warning or error.

### U-03: Event System Integration During Composition (Medium Priority)

**Boundary**: Bundle Composition <-> Event System (Kernel)
**Question**: Does bundle composition emit events during the loading/composition process, and how do hooks observe composition-time behavior?

The investigation found that `spawn()` registers a temporary hook on `orchestrator:complete` to capture completion data. However, we did not trace whether the composition process itself (loading, merging, preparing) emits events. The kernel's event system was not deeply examined.

**Why it matters**: If composition is silent (no events), then observability tools cannot track what happened during bundle loading — which includes resolved, which failed, which were skipped due to circular dependencies. The `logger.warning()` calls in the registry are the only observability mechanism found.

### U-04: Include Source Resolver Callback Chain (Low Priority)

**Boundary**: Bundle Composition <-> Registry <-> App Layer
**Question**: What callbacks does the app layer register via `set_include_source_resolver()`, and how do they interact with the default resolution logic?

The `BundleRegistry` accepts an `include_source_resolver` callback that takes priority over default resolution. This is an extension point that allows the app layer to override how include URIs are resolved. We did not examine what callbacks are registered in practice.

**Why it matters**: This callback can completely redirect where bundles are loaded from, potentially overriding git sources with local paths or vice versa. Understanding this is necessary to map the full resolution chain.

### U-05: Validator Integration (Low Priority)

**Boundary**: Bundle Composition <-> Validation
**Question**: Where and when does `validator.py` participate in the composition pipeline?

The foundation includes an `amplifier_foundation/validator.py` module that was not read during this investigation. It's unclear whether validation runs during composition (before merging), after composition (before prepare), or only on explicit request.

**Why it matters**: If validation happens after composition, errors from invalid bundle configs may be attributed to the composed result rather than the source bundle. If it happens before, individual bundles are validated but the composed result may violate constraints that only emerge from the interaction.

### U-06: Session Fork and Composition (Low Priority)

**Boundary**: Bundle Composition <-> Session Fork
**Question**: When a session is forked, does the forked session retain the original bundle composition, or can it be re-composed?

`session/fork.py` implements file-based and in-memory session forking with turn-aware slicing. The forked session preserves `bundle` and `model` from parent metadata. But it's unclear whether the forked session retains the full composed bundle (including source_base_paths, agent configs, etc.) or only the mount plan snapshot.

**Why it matters**: If forked sessions lose composition context, they may not be able to spawn agents or resolve @mentions correctly. This would be a hidden degradation at the fork boundary.

---

## Missing Connections

### M-01: Recipe System <-> Bundle Composition

Recipes (declarative YAML workflows) delegate steps to agents, which are spawned via bundle composition. However, the recipe system's interaction with composition was not traced. Specifically: how do recipes specify `orchestrator_config` overrides, and how does the `foreach` loop pattern interact with bundle re-composition for parallel agent spawns?

### M-02: Settings/Configuration <-> Bundle Composition

The `source_resolver` callback parameter in `Bundle.prepare()` is documented as enabling "settings-based overrides" at the app layer. But we did not examine how the settings system (if any) feeds into this callback, or how user-level configuration (e.g., preferred models, API keys) interacts with the composition pipeline.

### M-03: Discovery System <-> Bundle Composition

The `amplifier_foundation/discovery/` package exists but was not examined. It may provide bundle discovery mechanisms (finding bundles in directories, scanning for behaviors) that feed into the registry before composition begins.

### M-04: Kernel Module Loading <-> Bundle Module Resolver

The kernel's `loader.py` and `_session_init.py` were not examined. The `BundleModuleResolver` implements the kernel's `ModuleSourceResolver` protocol, but the exact contract (especially around `async_resolve` vs sync `resolve`) was not verified against the kernel's expectations.

---

## Boundary Risks Identified

### R-01: Namespace First-Writer-Wins Could Cause Silent Errors

`source_base_paths` uses first-writer-wins for namespace registration. If two included bundles register the same namespace with different paths (e.g., due to version mismatch or local overrides), the second registration is silently ignored. This could cause @mention resolution to point to unexpected files.

### R-02: sys.path Accumulation Has No Cleanup

Module activation adds paths to `sys.path` globally and permanently. Over a long session with many agent spawns, this list grows monotonically. While unlikely to cause functional issues, it creates import ambiguity risk if two bundles provide packages with the same name.

### R-03: Install State Fingerprint May Miss Source Changes

The `InstallStateManager` skips reinstallation when the fingerprint matches, but if the cached path hasn't changed (same git repo, same commit hash in cache), source changes from a new git push won't be detected until the cache is explicitly cleared.
