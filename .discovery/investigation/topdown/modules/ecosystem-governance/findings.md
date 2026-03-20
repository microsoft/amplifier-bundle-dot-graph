# Module Synthesis: Ecosystem Governance Model

**Module**: Ecosystem Governance Model
**Scope**: Governance rules (REPOSITORY_RULES.md, awareness hierarchy), knowledge delivery pipeline (docs/ → context/ → behaviors/ → agents/ → @-mention protocol), module loading & coordination (amplifier-core kernel, amplifier-foundation policy), enforcement mechanisms (recipes/), circular content lifecycle
**Investigation sources synthesized**: 7
  1. Code-tracer (bundle-composition) — HOW: execution paths through module loading, activation, and coordination
  2. Documentation-governance module synthesis — 7 bottom-up + top-down sources on governance artifacts and enforcement
  3. Expert-agent-knowledge module synthesis — 8 investigation streams on knowledge hierarchy and agent routing
  4. Agent-behavior-architecture module synthesis — 8 sources on agent definition patterns and behavior composition
  5. Recipe-orchestration module synthesis — 5 perspectives on recipe engine, enforcement recipes, and coordination
  6. Top-down subsystem synthesis — Cross-module data flows, coupling assessment, emergent patterns
  7. Bottom-up context/ level synthesis — Context injection triad analysis
**Fidelity**: standard
**Date**: 2026-03-20

---

## Executive Summary

The Ecosystem Governance Model is a convention-dominated system where sophisticated code infrastructure supports a fragile policy layer. Seven independent investigation streams converge on a central paradox: the module loading system (kernel) is well-engineered with strict separation of concerns, polyglot support, and parallel activation — yet the governance system built on top operates entirely through advisory convention with zero mechanical enforcement of its most important principle (the "Golden Rule" / dependency-based awareness). Two independent silent degradation mechanisms compound: module loading continues on non-fatal failures with only `logger.warning`, and @-mention content delivery returns `None` on missing content without errors. Together these create a diagnostic blindspot where governance knowledge can vanish from agent sessions without any signal at any stage. Seven discrepancies remain open, the most impactful being whether directory-level @-mentions eagerly or lazily load content — a question identified independently by four module syntheses that determines whether each session pays ~20KB or ~200KB in governance token cost.

---

## Consensus Findings

| ID | Finding | Sources Confirming | Confidence |
|----|---------|-------------------|------------|
| C-01 | Convention-Over-Code Architecture | all 7 sources | HIGH |
| C-02 | Strict Kernel/Policy Separation | code-tracer, top-down subsystem | HIGH |
| C-03 | @-mention Protocol as Sole Knowledge Delivery | expert-knowledge, doc-governance, agent-behavior, bundle-composition, top-down subsystem | HIGH |
| C-04 | Compounding Silent Degradation Chain | code-tracer, doc-governance, expert-knowledge, agent-behavior, top-down subsystem | HIGH |
| C-05 | Awareness Hierarchy Has Zero Mechanical Enforcement | doc-governance, recipe-orchestration, top-down subsystem | HIGH |
| C-06 | MODULES.md as Single Point of Failure | doc-governance, recipe-orchestration, top-down subsystem | HIGH |
| C-07 | Hub-and-Spoke Navigation Pattern | doc-governance, expert-knowledge, agent-behavior | HIGH |
| C-08 | 5-Tier Knowledge Hierarchy | expert-knowledge, agent-behavior, top-down subsystem | HIGH |
| C-09 | Module Loading Error Asymmetry | code-tracer, bundle-composition | MEDIUM |
| C-10 | Thin Bundle Behavior Pattern | expert-knowledge, agent-behavior, doc-governance, top-down subsystem | HIGH |
| C-11 | Circular Content Lifecycle | top-down subsystem, doc-governance, recipe-orchestration | HIGH |
| C-12 | Module Type System Excludes Agents | code-tracer, agent-behavior, top-down subsystem | HIGH |
| C-13 | Recipe Engine as Widest Boundary-Crossing Module | recipe-orchestration (code-tracer + integration-mapper), top-down subsystem | HIGH |

### C-01: Convention-Over-Code Architecture

Every layer of the ecosystem governance system relies on convention rather than code enforcement. This is the single most broadly confirmed finding — independently identified by all seven investigation sources. The code-tracer shows only two code-enforced mechanisms across the entire module ecosystem: the @-mention resolver and `ContentDeduplicator`. The documentation-governance synthesis (XC-01) catalogs conventions at every governance layer. The expert-agent-knowledge synthesis (C-03) confirms this independently. The recipe-orchestration synthesis (C-11) adds that recipe-level conventions (model tiering, `_precomputed` optimization, file-based data passing, rate limiting) constitute an additional uncodified framework layer.

The agent-behavior-architecture synthesis adds cross-bundle evidence: the dual-layer agent definition format (YAML frontmatter + Markdown body) is followed consistently across all 7 agents in the dot-graph bundle and the 1 agent in the amplifier bundle, yet no schema enforces this pattern.

**Evidence**: code-tracer §Key Architectural Observations §1; doc-governance XC-01; expert-knowledge C-03; agent-behavior C-04; recipe-orchestration C-11 + Insight 1 ("Shadow Framework"); top-down subsystem §Emergent Patterns §2.

### C-02: Strict Kernel/Policy Separation

The code-tracer reveals a clean architectural boundary: `amplifier-core` (kernel) defines only mechanisms — `ModuleLoader`, `ModuleCoordinator`, `_session_init.py`, protocol interfaces. All policy — where to find modules, how to install them, how to resolve sources — lives in `amplifier-foundation` (app layer): `SimpleSourceResolver`, `ModuleActivator`, `BundleModuleResolver`, `Bundle.prepare()`. The bundle-composition code-tracer (CI-04) independently confirms: "The pipeline crosses an architectural boundary between amplifier-foundation (bundle management) and amplifier-core (module loading). The bridge is the `module-source-resolver` coordinator mount point." The top-down subsystem synthesis confirms this at the cross-module level: the kernel bridge (`to_mount_plan()`) is the sole serialization boundary using a plain dict interface.

**Evidence**: code-tracer §Summary; bundle-composition CI-04; top-down subsystem Flow 10 (cleanest boundary in the subsystem).

### C-03: @-mention Protocol as Sole Knowledge Delivery

Five investigation sources converge: the @-mention protocol (`parse_mentions()` → `BaseMentionResolver` → `ContentDeduplicator`) is the sole mechanism by which governance knowledge reaches AI agents. The expert-knowledge synthesis states it is "the sole delivery mechanism for ALL governance rules and ALL expert knowledge." The documentation-governance synthesis confirms this as C-05. The agent-behavior-architecture synthesis (C-07) confirms all cross-boundary references use namespace-mediated composition. The bundle-composition code-tracer traces the underlying mechanism: `Bundle.compose()` produces `source_base_paths` → resolver resolves `@namespace:path` → system prompt factory assembles per-request.

**Evidence**: expert-knowledge C-05; doc-governance C-05; agent-behavior C-07; bundle-composition F-09; top-down subsystem Flow 3.

### C-04: Compounding Silent Degradation Chain

Two independent silent degradation mechanisms exist and compound. This is the second most broadly confirmed finding — independently identified by five investigation sources:

1. **Module loading level** (code-tracer, bundle-composition): Providers, tools, and hooks log `logger.warning` on failure but do not abort session initialization. Only orchestrator and context manager failures are fatal (`RuntimeError`). A session can start with no tools if they all fail to load.

2. **Content delivery level** (doc-governance, expert-knowledge, agent-behavior, top-down): Missing namespaces in `source_base_paths` → @-mention returns `None` → governance tier silently absent → expert operates with reduced knowledge → enforcement has no reference standard.

The compound effect: if the `module-source-resolver` fails to mount (warning only), ALL @-mention resolution fails, meaning ALL governance content vanishes from ALL sessions — with no error, no warning, no fallback at the content delivery layer.

The agent-behavior-architecture synthesis (X-06) independently confirms: "At no point in the chain — from missing files to absent tiers to reduced knowledge — does any mechanism surface an error, warning, or degradation notice."

**Evidence**: code-tracer §Error Handling Paths; doc-governance XC-02; expert-knowledge C-07; agent-behavior X-06; top-down subsystem §Emergent Patterns §5.

### C-05: Awareness Hierarchy Has Zero Mechanical Enforcement

The "Golden Rule" (dependency-based awareness) — the most important governance principle defined in REPOSITORY_RULES.md — has zero automated checking anywhere in the system. Enforcement recipes (repo-audit, ecosystem-audit) check only boilerplate compliance (README sections, MODULES.md listing), not awareness-hierarchy compliance. The recipe-orchestration synthesis (F-14) adds a new dimension: the recipe engine's observability gaps mean that even recipe-level enforcement failures go undetected — "NO events are emitted for: variable substitution failures, checkpoint trimming, rate limiter state changes."

All enforcement is: advisory (expert agent provides guidance), periodic (recipes run manually), and narrow (test_doc_sweep.sh checks 3 files for model names only).

**Evidence**: doc-governance C-07; recipe-orchestration F-14; top-down subsystem Flow 6.

### C-06: MODULES.md as Single Point of Failure

MODULES.md (25KB, 323 lines) is consumed by 4 of 6 recipes through 3 independent fetch mechanisms that bypass the @-mention namespace resolution entirely: `curl -sL` from GitHub raw URL (repo-audit), `curl` + URL extraction (ecosystem-audit), `gh api` + `base64 -d` (ecosystem-activity-report), and local file read (outline-generation). The recipe-orchestration synthesis (F-04 + F-05) independently confirms filesystem as the primary coordination medium and template→bash as the most fragile integration point.

**Evidence**: doc-governance C-02; recipe-orchestration F-04, F-05; top-down subsystem Flow 5 (TIGHT coupling).

### C-07: Hub-and-Spoke Navigation Pattern

Three independent investigation streams identified hub-and-spoke as the dominant navigation pattern across different layers:
- **Documentation**: README.md routes to audience-tiered docs (doc-governance)
- **Agent architecture**: amplifier-expert.md routes to spoke experts (expert-knowledge)
- **Context layer**: ecosystem-overview.md is the hub referencing both other context files (agent-behavior)

The agent-behavior-architecture synthesis (X-03) explicitly notes: "This triple hub-and-spoke suggests a deliberate cross-layer design pattern, not coincidence. Every layer has a single gateway that routes to specialized children."

**Evidence**: doc-governance C-06; expert-knowledge C-02; agent-behavior X-03.

### C-08: 5-Tier Knowledge Hierarchy

The amplifier-expert agent defines a 5-tier @-mention knowledge hierarchy:

| Tier | Namespace | Domain |
|------|-----------|--------|
| 0 | `@core:docs/` | Kernel internals |
| 1 | `@amplifier:docs/` | Entry-point documentation |
| 2 | `@foundation:docs/` | Foundation library |
| 3 | `@foundation:context/` | Core philosophy |
| 4 | `@recipes:docs/` | Workflow recipes |

The expert-knowledge synthesis verified **28 @-mentions total** (10 directory-level, 18 file-level) in the agent file — more than the "5 tiers" framing suggests. Priority ordering is natural language instruction only — no runtime enforcement of tier precedence.

**Evidence**: expert-knowledge C-01 (verified counts); agent-behavior C-05; top-down subsystem Flow 3.

### C-09: Module Loading Error Asymmetry (MEDIUM confidence)

The code-tracer reveals a critical asymmetry in `_session_init.py`:
- **Fatal** (abort session): Orchestrator failure (`RuntimeError`, line 69-72), Context manager failure (same pattern, line 97-99)
- **Non-fatal** (continue degraded): Provider/tool/hook failures (`logger.warning`, line 179-183)

The bundle-composition code-tracer (F-10) independently confirms: "Module loading order: orchestrator > context > providers > tools > hooks" with the first two required and the rest optional.

**Evidence**: code-tracer §Error Handling Paths; bundle-composition F-10. MEDIUM confidence — code-level detail from single-repo traces confirmed by independent composition analysis.

### C-10: Thin Bundle Behavior Pattern

Four investigation streams independently confirm the behavior layer implements two distinct thin-bundle patterns: `amplifier-expert-behavior` (active — injects both agent and context), and `amplifier-dev-behavior` (passive — injects context only). The agent-behavior-architecture synthesis (C-02) provides the strongest confirmation: "All four investigation streams independently identify these as composable thin bundles."

The `recipes-usage.md` context was deliberately demoted to a soft reference (commented out in YAML), demonstrating conscious token budget management.

**Evidence**: expert-knowledge C-04; agent-behavior C-02; doc-governance C-03; top-down subsystem Flow 2.

### C-11: Circular Content Lifecycle

Three investigation sources identify the defining subsystem pattern: Documentation Governance → Agent & Behavior Architecture → Expert Agent Knowledge → Bundle Composition → Recipe Orchestration → (generates new documentation) → cycle repeats. This cycle is visible only at the subsystem level; no single module sees the full loop.

The recipe-orchestration synthesis adds quantitative evidence for the cycle's difficulty: `document-generation.yaml` at v8.1.0 (126KB, 3,033 lines with in-file changelog spanning 7+ major versions) demonstrates that mechanically encoding governance into executable pipelines requires extensive iteration.

**Evidence**: top-down subsystem §Emergent Patterns §1; doc-governance C-04 + C-07; recipe-orchestration F-17.

### C-12: Module Type System Excludes Agents

The code-tracer explicitly identifies: "Agents are not a module type" (`loader.py:514` — "agents are config data, not modules"). The `TYPE_TO_MOUNT_POINT` map includes orchestrator, provider, tool, hook, context, and resolver — but not agent. The agent-behavior-architecture synthesis (X-02) independently identifies this as "Documentation-as-Architecture Fragility" — the entire agent/behavior/context layer operates outside the module type system.

This creates an architectural gap: the module ecosystem has validation (`_validate_module()`), caching (`_loaded_modules`), cleanup (`_added_paths`), and type checking (protocol interfaces) — none of which apply to the agent/behavior/context layer that carries governance knowledge.

**Evidence**: code-tracer §Module Type → Mount Point Mapping; agent-behavior X-02; top-down subsystem Flow 11 (ARCHITECTURAL GAP).

### C-13: Recipe Engine as Widest Boundary-Crossing Module

The recipe-orchestration synthesis confirms from two independent perspectives (code-tracer + integration-mapper): the recipe executor engine accesses 9+ coordinator surfaces via duck-typed `getattr()` with fallback, making it the widest boundary-crossing module in the ecosystem. This creates an invisible dependency graph: the module declares one formal capability (`session.spawn`) but functionally depends on coordinator, session, hooks, cancellation, display, bundle resolution, and provider routing — all accessed through untyped attribute lookups.

**Evidence**: recipe-orchestration C-01, C-12, Insight 3; top-down subsystem Flow 14.

---

## Cross-Cutting Insights

### X-01: Infrastructure Robustness vs. Policy Fragility

The code-tracer reveals a well-engineered module loading system: strict kernel/policy separation, polyglot support (WASM, gRPC, Python), parallel activation via `asyncio.gather()`, SHA256-based cache management, proper fallback chains, three-layer cache and deduplication (bundle-composition CI-03). Yet the governance system built on top of this infrastructure is entirely advisory — convention-based rules, no continuous enforcement, no automated compliance checking.

This asymmetry is the most significant cross-cutting finding: the code layer has **the mechanisms** to enforce governance (module validation, protocol checking, mount point gating), but the governance layer uses **none of them**. The recipe-orchestration synthesis adds: the recipe engine has evolved extensive workaround patterns (gc.collect() for PyO3 memory, printf for template→bash escaping, output delta trimming) — evidence that even the execution infrastructure builds defensive mechanisms that governance does not.

**Sources**: code-tracer §Key Architectural Observations; bundle-composition CI-01, CI-03; doc-governance C-07; recipe-orchestration Insight 4.

### X-02: Two-Layer Silent Degradation Creates Diagnostic Blindspot

The code-level silent degradation (C-09: non-fatal module loading) and the content-level silent degradation (C-04: @-mention returns None) operate at different layers but share the same consequence: no diagnostic exists. The code-tracer shows `logger.warning` as the only signal when modules fail to load; the governance investigations show no signal at all when content fails to resolve. The recipe-orchestration synthesis (F-14) reveals a third layer: even the recipe engine lacks observability events for variable substitution failures, checkpoint trimming, and condition evaluation — meaning enforcement recipe failures also go undetected.

The missing diagnostic infrastructure spans: (1) no health check for whether governance content resolved, (2) no token budget measurement, (3) no fallback content on missing tiers, (4) no session-startup governance validation, (5) no recipe-level event emission for enforcement failures.

**Sources**: code-tracer §Error Handling Paths; doc-governance XC-02; expert-knowledge §Agent Coverage Assessment; recipe-orchestration F-14.

### X-03: Kernel/Policy Separation Mirrors Governance/Enforcement Separation

The code architecture's kernel/policy separation (C-02) mirrors the governance system's rules/enforcement separation. Both share the same philosophical approach: define abstract contracts in one place, implement policy elsewhere. But the consequences differ:
- **In code**: The separation works — kernel defines protocols, foundation implements policy, contracts are enforced at mount time
- **In governance**: The separation means enforcement is optional — rules are in REPOSITORY_RULES.md, enforcement recipes run manually and check only surface-level compliance
- **In recipes**: The separation creates a shadow framework (recipe-orchestration Insight 1) — the engine provides primitives, but the conventions encoded in YAML are where production bugs concentrate

The pattern that enables robust code infrastructure produces fragile governance when applied to human-readable rules rather than machine-checkable contracts.

**Sources**: code-tracer §Summary; recipe-orchestration Insight 1; top-down subsystem §Coupling Assessment.

### X-04: Single-Agent Knowledge Monopoly Amplifies Fragility

The entire agents/ directory contains exactly one file (`amplifier-expert.md`, 15.1 KB). This single document carries all ecosystem knowledge routing: 5-tier hierarchy, 3-mode persona dispatch, 3 spoke expert routing rules, 7 philosophy principles, 6 anti-patterns, and decision frameworks. The expert-knowledge synthesis (X-03) calls it a "Knowledge Monopoly." The agent-behavior-architecture synthesis (X-01) adds cross-bundle contrast: the dot-graph bundle defines 7 agents with complementary roles, showing that single-agent design is a *choice* for the amplifier bundle, not an ecosystem constraint.

This monopoly amplifies every other fragility: if `amplifier-expert.md` is absent, stale, or malformed, ALL ecosystem knowledge routing fails with no fallback. The top-down subsystem synthesis identifies five sequential SPOFs spanning four modules: MODULES.md → @-mention resolver → module-source-resolver mount → system prompt factory → LLM tier reasoning.

**Sources**: agent-behavior X-01; expert-knowledge X-03; top-down subsystem §Emergent Patterns §6.

### X-05: Context Dict as Universal (Overloaded) Integration Medium

The recipe-orchestration synthesis reveals that the context dict simultaneously serves as execution state, data bus, template variable store, checkpoint payload, and cross-recipe interface. Every boundary in the recipe system passes through context, making it the single most important and fragile data structure. Checkpoint trimming (>100KB → placeholder), template escaping, and naming variance all attack this single surface.

This mirrors the @-mention resolver's role in governance delivery: a single mechanism (context dict for recipes, @-mention for knowledge) carries all cross-boundary communication. Both create single points of failure with silent degradation on corruption.

**Sources**: recipe-orchestration C-08, Insight 2; bundle-composition CI-02 (`source_base_paths` as critical cross-cutting state).

---

## Discrepancy Register

| ID | Description | Sources Involved | Status | Impact |
|----|-------------|-----------------|--------|--------|
| D-01 | Eager vs. lazy @-mention directory loading | doc-governance, expert-knowledge, agent-behavior, ecosystem-governance | OPEN | HIGH |
| D-02 | Governance scope: centralized vs. distributed | doc-governance, ecosystem-governance, top-down subsystem | OPEN | MEDIUM |
| D-03 | Content budget: deliberate strategy vs. ad hoc sizing | doc-governance, agent-behavior, expert-knowledge | OPEN | MEDIUM |
| D-04 | recipes-usage.md inclusion mechanism | expert-knowledge, agent-behavior | OPEN | LOW-MEDIUM |
| D-05 | PyO3 coordinator bridge mechanism | code-tracer, bundle-composition | OPEN | MEDIUM |
| D-06 | common-agent-base.md and common-system-base.md content unknown | expert-knowledge, agent-behavior | OPEN | MEDIUM |
| D-07 | amplifier-dev-behavior: loaded or orphaned? | doc-governance, expert-knowledge, agent-behavior | OPEN | MEDIUM |

### D-01: Eager vs. Lazy @-mention Directory Loading

**Claim A (top-down subsystem, expert-knowledge, agent-behavior)**: Directory-level @-mentions like `@core:docs/` may eagerly load all files in that directory. If eager, every session pays full governance token cost. Expert-knowledge counted 28 @-mentions (10 directory + 18 file-level) — far more than the "5 tiers" framing suggests. Agent-behavior independently calls this "the highest-priority discrepancy — it determines the expert's actual token footprint."

**Claim B (no direct evidence)**: No investigation source has traced the resolver code to determine actual behavior. The code-tracer traced the module loader but NOT the @-mention resolver (which lives in `amplifier-foundation/amplifier_foundation/mentions/resolver.py`).

**Cross-source confirmation**: This discrepancy was independently identified by FOUR module syntheses (doc-governance D-03, expert-knowledge D-01, agent-behavior D-04, ecosystem-governance), making it the most widely flagged open question in the entire investigation.

**Impact**: HIGH — determines whether governance content costs ~20KB or ~200KB per session (10x difference).

**Resolution needed**: Read `_resolve_mention()` in the mentions resolver for directory path arguments. Determine if `os.listdir()` or equivalent is called. Alternatively, instrument a session and measure actual system prompt size.

### D-02: Governance Scope — Centralized or Distributed?

**Claim A (bottom-up docs/)**: REPOSITORY_RULES.md describes rules for the entire amplifier ecosystem but is located in a single repo's `docs/`. This centralization is noted as anomalous.

**Claim B (top-down subsystem)**: Three governance documents operate independently across the ecosystem: REPOSITORY_RULES.md (amplifier repo), CONTEXT_POISONING.md (amplifier-foundation), DOCUMENTATION_LINKING.md (amplifier-core). No cross-reference connects them. Governance is actually distributed with no coordination mechanism.

**Impact**: MEDIUM — determines whether governance drift between repos is a design flaw or expected.

**Resolution needed**: Survey all Amplifier ecosystem repos for governance-related documents. Determine if REPOSITORY_RULES.md is canonical source or each repo independently defines governance.

### D-03: Content Budget — Deliberate or Ad Hoc?

**Claim A (bottom-up context/, bottom-up behaviors/)**: File sizes are "nearly identical (~6300–6700 bytes each), suggesting deliberate design." The behavior YAML deliberately demotes `recipes-usage.md`, "showing conscious token management."

**Claim B (top-down subsystem, expert-knowledge)**: "No token budget enforcement — full 5-tier resolution could exhaust context window." Expert-knowledge X-02 identifies "Token Budget as Unmonitored Architectural Constraint."

**Neither source resolves**: Evidence of deliberate management exists (demotion, balanced sizes), but no measurement or enforcement mechanism exists. Both claims could be simultaneously true — informal budget with no enforcement.

**Impact**: MEDIUM — if deliberate, the ~6.5KB sizing is a design constraint to preserve; if ad hoc, the system may silently degrade as content grows.

**Resolution needed**: (1) Search for documented context budget policy. (2) Measure actual token cost of full governance content resolution. (3) Check commit history for the `recipes-usage.md` demotion rationale.

### D-04: recipes-usage.md Inclusion Status

**Claim A (bottom-up behaviors/)**: YAML comment says "demoted to soft reference (load on demand)."

**Claim B (primary source)**: Agent instructions say "see amplifier:context/recipes-usage.md (load on demand)" suggesting the agent tells users to request it manually. Bundle.md line 86 also references it as `@amplifier:context/recipes-usage.md`.

**Impact**: LOW-MEDIUM — unclear whether "soft reference" means (a) never injected, (b) injected via different path, or (c) loaded only when agent references it.

**Resolution needed**: Instrument a session with `amplifier-expert-behavior` loaded and observe whether `recipes-usage.md` content appears in the system prompt.

### D-05: PyO3 Coordinator Bridge Mechanism

**Claim A (code-tracer)**: The Python `coordinator.mount("tools", tool, name="foo")` routes through PyO3 to Rust. How a Python `Tool` protocol object gets marshalled into Rust `Arc<dyn Tool>` is untraced. The code-tracer also flags that `coordinator.get("module-source-resolver")` retrieves a resolver, but the Rust coordinator doesn't have a generic string→object store visible in `coordinator.rs`.

**Claim B (bundle-composition code-tracer)**: Confirms the two-repo boundary and the mount mechanism, but also does not trace into the PyO3 bindings. Notes `gc.collect()` workaround after every agent spawn as evidence of past PyO3/Rust reference cycle problems.

**Impact**: MEDIUM — the PyO3 bridge enables all governance content delivery via the module-source-resolver mount, yet its implementation is a blind spot. The `gc.collect()` workaround suggests known stability concerns.

**Resolution needed**: Read the PyO3 bindings in `amplifier-core/bindings/` to understand Python-side `get()/mount()` for arbitrary keys.

### D-06: common-agent-base.md and common-system-base.md Content Unknown

**Claim A (expert-knowledge D-03)**: Bottom-up agents/ analysis flags that `@foundation:context/shared/common-agent-base.md` is appended to the expert agent's instructions. "Its content could impose additional operating constraints."

**Claim B (agent-behavior C-10, expert-knowledge C-10)**: TWO distinct common-base files exist — `common-system-base.md` included by `bundle.md` at the bundle composition level, and `common-agent-base.md` included by `amplifier-expert.md` at the agent level. Neither file's content was examined by any investigation stream.

**Impact**: MEDIUM (elevated from LOW) — two files at two different composition levels could modify effective governance behavior. The bundle-level file affects ALL sessions, not just the expert agent.

**Resolution needed**: Simple file reads of both files in `amplifier-foundation/context/shared/`. No code tracing required.

### D-07: amplifier-dev-behavior — Loaded or Orphaned?

**Claim A (doc-governance D-04, expert-knowledge D-04, agent-behavior D-01)**: Three independent module syntheses flag this as unresolved. `bundle.md` only includes `amplifier:behaviors/amplifier-expert`. No reference to `amplifier-dev` was found.

**Claim B (bottom-up behaviors/)**: The file exists as a structurally valid behavior bundle (202 bytes) that injects `development-hygiene.md` — which contains critical operational safety knowledge including "NEVER: rm -rf ~/.amplifier/cache/".

**Cross-source confirmation**: Independently flagged by THREE module syntheses, making it the second-most widely identified discrepancy after D-01.

**Impact**: MEDIUM — if orphaned, operational safety knowledge may never reach agent sessions, and `development-hygiene.md` is injected only as a generation pipeline output, not as agent context.

**Resolution needed**: (1) Search all bundle YAML files for references to `amplifier-dev-behavior`. (2) Trace `BundleRegistry._load_single()` to determine if it scans directories for all YAML files or only loads explicitly included bundles.

---

## Open Questions

1. **Is the governance enforcement gap deliberate or unsolved?** The 8-version evolution of document-generation suggests mechanical enforcement is hard, not impossible. Is advisory governance sufficient, or is the absence of Golden Rule enforcement an engineering debt?

2. **What is the actual token cost of full governance tier resolution?** No measurement exists. Given 28 @-mentions (10 directory + 18 file-level), the actual cost could be dramatically different from the ~20KB suggested by context files alone. This is the most impactful unmeasured quantity in the system.

3. **How do child sessions inherit governance?** The boundary between `delegate tool` and `PreparedBundle.spawn()` — mediated by `session_spawner.py` in `amplifier-app-cli` — is a blind spot across all investigations. The bundle-composition code-tracer (F-11) confirms children get parent's `BundleModuleResolver`, but whether governance content is fully propagated is unverified.

4. **Does the module validation system have an analog for governance content?** The code infrastructure validates module structure (ProviderValidator, ToolValidator, etc.) but no equivalent validates governance content integrity, completeness, or freshness.

5. **How many governance-like documents exist across the full ecosystem?** Only three repos have been identified (amplifier, amplifier-foundation, amplifier-core). The 37-repo `allowed_source_repos` field in outline specs suggests many repos could contain governance-relevant content.

6. **What is the actual data loss surface during checkpoint-trimmed resume?** The recipe-orchestration synthesis (OQ-02) identifies that >100KB values are trimmed to placeholders during checkpoint, and `substitute_variables()` silently injects these placeholders on resume. This could affect governance enforcement recipe outputs.

7. **Does the recipe engine's inline routing fallback drift from the canonical implementation?** The fallback at executor.py:1706-1746 re-implements `amplifier_hooks_routing.resolver` logic — if it drifts, governance recipes may route to wrong model tiers.

---

## Recommended Next Steps

1. **Resolve D-01 (eager vs. lazy loading)** — Trace the @-mention resolver implementation in `amplifier-foundation`. This is the highest-impact open question, independently flagged by four module syntheses, determining the governance system's practical token cost per session.

2. **Resolve D-07 (amplifier-dev-behavior activation)** — Search all bundle manifests for references. If orphaned, either wire it into the composition or remove the dead behavior file. Independently flagged by three module syntheses.

3. **Measure full governance token budget** — Instrument the system prompt factory to log token counts when all 5 tiers resolve. No measurement currently exists.

4. **Read common-base files (D-06)** — Simple file reads of `common-system-base.md` and `common-agent-base.md` in `amplifier-foundation/context/shared/`. Low effort, resolves a medium-impact blind spot at two composition levels.

5. **Trace the PyO3 bridge (D-05)** — Read `amplifier-core/bindings/` to understand how the module-source-resolver mount works across the Python/Rust boundary. The `gc.collect()` workaround suggests known instability.

6. **Abstract MODULES.md access** — The 3 independent fetch mechanisms across 4 recipes are the most significant tight coupling. An `@amplifier:docs/MODULES.md` @-mention would align with existing patterns.

7. **Survey parallel governance systems (D-02)** — Catalog governance-related documents across all Amplifier ecosystem repos. Determine coordination mechanism (or lack thereof).

8. **Prototype governance validation** — Explore whether the existing module validation infrastructure (`_validate_module()`) could be extended to validate governance content integrity at session startup.

9. **Formalize recipe-coordinator contract** — The 9+ duck-typed `getattr()` surfaces (C-13) should be evaluated for formal capability registration, reducing the invisible dependency graph.
