# Module Synthesis: Ecosystem Governance & Awareness Hierarchy

**Module**: Ecosystem Governance & Awareness Hierarchy
**Scope**: Governance rules (REPOSITORY_RULES.md, awareness hierarchy), knowledge delivery pipeline (docs/ → context/ → behaviors/ → agents/ → @-mention protocol), module loading & coordination (amplifier-core kernel, amplifier-foundation policy), enforcement mechanisms (recipes/)
**Investigation perspectives synthesized**: 4
  1. Code-tracer (module-ecosystem) — HOW: execution paths through module loading, activation, and coordination
  2. Documentation-governance module synthesis — 7 bottom-up + top-down sources on governance artifacts and enforcement
  3. Expert-agent-knowledge module synthesis — 4 investigation streams on knowledge hierarchy and agent routing
  4. Top-down subsystem synthesis — Cross-module data flows and coupling assessment
**Fidelity**: standard
**Date**: 2026-03-19

---

## Executive Summary

The Ecosystem Governance & Awareness Hierarchy is a convention-dominated system where sophisticated code infrastructure supports a fragile policy layer. The code-tracer reveals a well-engineered module loading system with strict kernel/policy separation, polyglot support, and parallel activation — yet the governance system built on top operates entirely through advisory convention with zero mechanical enforcement of its most important principle (the "Golden Rule" / dependency-based awareness). All four investigation perspectives independently converge on this infrastructure-vs-policy asymmetry as the defining characteristic. Two independent silent degradation mechanisms compound: module loading continues on non-fatal failures with only logger.warning, and @-mention content delivery returns None on missing content without errors. Together these create a chain where governance knowledge can vanish from agent sessions without any diagnostic at any stage. Six discrepancies remain open, the most impactful being whether directory-level @-mentions eagerly or lazily load content — a question that determines whether each session pays ~20KB or ~200KB in governance token cost.

---

## Consensus Findings

| ID | Finding | Sources | Confidence |
|----|---------|---------|------------|
| C-01 | Convention-Over-Code Architecture | code-tracer, doc-governance XC-01, expert-knowledge C-03, subsystem | HIGH |
| C-02 | Strict Kernel/Policy Separation | code-tracer, subsystem | HIGH |
| C-03 | @-mention Protocol as Sole Knowledge Delivery | expert-knowledge C-05, doc-governance C-05, subsystem Flow 2 | HIGH |
| C-04 | Compounding Silent Degradation Chain | code-tracer, doc-governance XC-02, expert-knowledge C-07, subsystem | HIGH |
| C-05 | Awareness Hierarchy Has Zero Mechanical Enforcement | doc-governance C-07, subsystem Flow 5, expert-knowledge X-01 | HIGH |
| C-06 | MODULES.md as Single Point of Failure | doc-governance C-02, subsystem Flow 4 | HIGH |
| C-07 | Hub-and-Spoke Navigation Pattern | doc-governance C-06, expert-knowledge C-02 | HIGH |
| C-08 | 5-Tier Knowledge Hierarchy | expert-knowledge C-01, subsystem Flow 2 | HIGH |
| C-09 | Module Loading Error Asymmetry | code-tracer | MEDIUM |
| C-10 | Thin Bundle Behavior Pattern | expert-knowledge C-04, doc-governance C-03, subsystem | HIGH |
| C-11 | Circular Content Lifecycle | subsystem, doc-governance C-04 + C-07 | MEDIUM |

### C-01: Convention-Over-Code Architecture

Every layer of the ecosystem governance system relies on convention rather than code enforcement. The code-tracer shows only two code-enforced mechanisms across the entire module ecosystem: the @-mention resolver and ContentDeduplicator. The documentation-governance synthesis (XC-01) independently catalogs conventions at every governance layer: knowledge hierarchy tier priority (natural language instruction), governance rules (prose principles), expert routing (convention in agent descriptions), model tier strategy (copy-pasted YAML), and thin/heavy behavior split (YAML pattern). The expert-agent-knowledge synthesis (C-03) confirms this as independently identified by all investigation streams.

**Evidence**: code-tracer §Key Architectural Observations §1 ("Strict kernel/policy separation" — mechanism-only contracts with all policy in app layer); doc-governance XC-01 ("Only two mechanisms are code-enforced"); expert-knowledge C-03 ("Every investigation stream independently identifies that the knowledge architecture relies on conventions").

### C-02: Strict Kernel/Policy Separation

The code-tracer reveals a clean architectural boundary: `amplifier-core` (kernel) defines only mechanisms — `ModuleLoader`, `ModuleCoordinator`, `_session_init.py`, protocol interfaces. All policy — where to find modules, how to install them, how to resolve sources — lives in `amplifier-foundation` (app layer): `SimpleSourceResolver`, `ModuleActivator`, `BundleModuleResolver`, `Bundle.prepare()`. The top-down subsystem synthesis confirms this at the cross-module level: the kernel bridge (`to_mount_plan()`) is the sole serialization boundary between foundation and kernel, using a plain dict interface.

**Evidence**: code-tracer §Summary ("kernel defines mechanisms-only contracts; all policy lives in the app layer"); code-tracer §Key Architectural Observations §2 ("Late binding via mount point injection — loader checks with contextlib.suppress"); subsystem Flow 9 ("Sole kernel bridge, plain dict interface").

### C-03: @-mention Protocol as Sole Knowledge Delivery

All investigation streams converge: the @-mention protocol (`parse_mentions()` → `BaseMentionResolver` → `ContentDeduplicator`) is the sole mechanism by which governance knowledge reaches AI agents. The expert-knowledge synthesis states it is "the sole delivery mechanism for ALL governance rules and ALL expert knowledge." The documentation-governance synthesis confirms this as C-05. The code-tracer shows the underlying mechanism: `coordinator.mount("module-source-resolver", resolver)` enables the resolution chain, and the `source_base_paths` namespace map is produced by `Bundle.compose()`.

**Evidence**: expert-knowledge C-05; doc-governance C-05; subsystem Flow 2 ("@-mention Delivery Chain"); code-tracer §Execution Path 3 Step 7 ("session.coordinator.mount('module-source-resolver', self.resolver)").

### C-04: Compounding Silent Degradation Chain

Two independent silent degradation mechanisms exist and compound:

1. **Module loading level** (code-tracer): Providers, tools, and hooks log `logger.warning` on failure but do not abort session initialization. A session can start with no tools if they all fail to load. Only orchestrator and context manager failures are fatal (`RuntimeError`).

2. **Content delivery level** (doc-governance, expert-knowledge, subsystem): Missing namespaces in `source_base_paths` → @-mention returns None → governance tier silently absent → expert operates with reduced knowledge → enforcement has no reference standard.

The compound effect: if the module-source-resolver fails to mount (warning only), then ALL @-mention resolution fails, meaning ALL governance content vanishes from ALL sessions — with no error, no warning, no fallback at the content delivery layer.

**Evidence**: code-tracer §Error Handling Paths ("Non-fatal: logger.warning(...) only"); doc-governance XC-02 (full degradation chain); expert-knowledge C-07 ("no fallback messaging or error handling"); subsystem §Emergent Patterns §3 ("Silent Degradation Chain").

### C-05: Awareness Hierarchy Has Zero Mechanical Enforcement

The "Golden Rule" (dependency-based awareness) — the most important governance principle defined in REPOSITORY_RULES.md — has zero automated checking anywhere in the system. Enforcement recipes (repo-audit, ecosystem-audit) check only boilerplate compliance (README sections, MODULES.md listing), not awareness-hierarchy compliance. All enforcement is advisory (expert agent provides guidance), periodic (recipes run manually), and narrow (test_doc_sweep.sh checks 3 files for model names only).

**Evidence**: doc-governance C-07; subsystem Flow 5 ("Sole enforcement mechanism; Golden Rule NOT enforced"); expert-knowledge X-01 ("the only guard against context poisoning is a philosophy document about context poisoning").

### C-06: MODULES.md as Single Point of Failure

MODULES.md (25KB, 323 lines) is consumed by 3 enforcement recipes through 3 independent fetch mechanisms that bypass the @-mention namespace resolution entirely: `curl -sL` from GitHub raw URL (repo-audit), `curl` + URL extraction (ecosystem-audit), and `gh api` + `base64 -d` (ecosystem-activity-report). The @-mention protocol exists precisely to abstract content delivery, yet the most critical shared dependency bypasses it entirely.

**Evidence**: doc-governance C-02 (detailed three-mechanism analysis); subsystem Flow 4 ("MODULES.md Bypass — TIGHT — 3 hardcoded fetch mechanisms").

### C-07: Hub-and-Spoke Navigation Pattern

Two independent investigation streams identified hub-and-spoke as the dominant navigation pattern across different layers:
- **Documentation**: README.md functions as multi-audience hub routing to user tier, developer trilogy, and ecosystem docs
- **Agent architecture**: amplifier-expert.md functions as gateway agent routing to spoke experts (core-expert, foundation-expert, recipe-author)

This parallel structure across documentation and agent layers suggests hub-and-spoke is a deliberate cross-layer design pattern.

**Evidence**: doc-governance C-06; expert-knowledge C-02; bottom-up context/ §Boundary Pattern ("Specialist Delegation Registry").

### C-08: 5-Tier Knowledge Hierarchy

The amplifier-expert agent defines a 5-tier @-mention knowledge hierarchy:

| Tier | Namespace | Domain |
|------|-----------|--------|
| 0 | `@core:docs/` | Kernel internals |
| 1 | `@amplifier:docs/` | Entry-point documentation |
| 2 | `@foundation:docs/` | Foundation library |
| 3 | `@foundation:context/` | Core philosophy |
| 4 | `@recipes:docs/` | Workflow recipes |

Priority ordering is natural language instruction only — no runtime enforcement of tier precedence.

**Evidence**: expert-knowledge C-01 (tier table with 3-source confirmation); subsystem Flow 2.

### C-09: Module Loading Error Asymmetry (MEDIUM confidence)

The code-tracer reveals a critical asymmetry in `_session_init.py`:
- **Fatal** (abort session): Orchestrator failure (`RuntimeError`, line 69-72), Context manager failure (same pattern, line 97-99)
- **Non-fatal** (continue degraded): Provider/tool/hook failures (`logger.warning`, line 179-183)

This asymmetry means a session can start with no tools, no hooks, and missing providers — which would silently remove capabilities that governance enforcement depends on.

**Evidence**: code-tracer §Error Handling Paths (full analysis with line citations). Single-source finding for code detail, but degradation behavior confirmed independently by governance investigations.

### C-10: Thin Bundle Behavior Pattern

The behavior layer implements two distinct thin-bundle patterns: `amplifier-expert-behavior` (active — injects both agent and context), and `amplifier-dev-behavior` (passive — injects context only). These are composable thin bundles that reference existing capabilities rather than define new ones. The `recipes-usage.md` context was deliberately demoted to a soft reference (commented out in YAML), demonstrating conscious token budget management.

**Evidence**: expert-knowledge C-04; subsystem Flow 1 ("The behavior layer acts as a context gate").

### C-11: Circular Content Lifecycle (MEDIUM confidence)

The top-down subsystem synthesis identifies a defining subsystem pattern: Documentation Governance → Expert Agent Knowledge → Bundle Composition → Recipe Orchestration → (generates new documentation) → cycle repeats. This cycle is visible only at the subsystem level; no single module sees the full loop. The documentation-governance synthesis confirms both endpoints: C-04 (document generation pipeline) and C-07 (enforcement recipes that close the loop).

**Evidence**: subsystem §Emergent Patterns §1 ("Circular Content Lifecycle — subsystem-defining pattern"); doc-governance C-04 (two-stage generation pipeline) + C-07 (enforcement closing the loop).

---

## Cross-Cutting Insights

### X-01: Infrastructure Robustness vs. Policy Fragility

The code-tracer reveals a well-engineered module loading system: strict kernel/policy separation, polyglot support (WASM, gRPC, Python), parallel activation via `asyncio.gather()`, SHA256-based cache management, proper fallback chains. Yet the governance system built on top of this infrastructure is entirely advisory — convention-based rules, no continuous enforcement, no automated compliance checking. The infrastructure supports robust policy enforcement, but no policy enforcement exists.

This asymmetry is the most significant cross-cutting finding: the code layer has **the mechanisms** to enforce governance (module validation, protocol checking, mount point gating), but the governance layer uses **none of them**. The `_validate_module()` function validates module structure but no equivalent validates governance compliance.

**Sources**: code-tracer §Execution Path 6 (module validation); code-tracer §Key Architectural Observations (7 sophisticated design features); doc-governance C-07 (advisory-only enforcement); expert-knowledge X-01 (documentation-as-architecture risk).

### X-02: Two-Layer Silent Degradation Creates Diagnostic Blindspot

The code-level silent degradation (C-09: non-fatal module loading) and the content-level silent degradation (C-04: @-mention returns None) operate at different layers but share the same consequence: no diagnostic exists. The code-tracer shows `logger.warning` as the only signal when modules fail to load; the governance investigations show no signal at all when content fails to resolve. These two layers compound into a diagnostic blindspot where the absence of governance from a session is literally undetectable from within that session.

The missing diagnostic infrastructure spans: (1) no health check for whether governance content resolved, (2) no token budget measurement, (3) no fallback content on missing tiers, (4) no session-startup governance validation.

**Sources**: code-tracer §Error Handling Paths; doc-governance XC-02 (full degradation chain); expert-knowledge §Agent Coverage Assessment ("Missing: No investigation stream performed runtime verification").

### X-03: Module Type System Excludes Agents

The code-tracer explicitly identifies: "Agents are not a module type" (`loader.py:514` — "agents are config data, not modules"). The `TYPE_TO_MOUNT_POINT` map includes orchestrator, provider, tool, hook, context, and resolver — but not agent. This means the entire governance knowledge delivery system (agents → behaviors → context) operates **outside** the module type system that the code-tracer traced. Governance awareness is delivered through a mechanism (bundle configuration) that the module loading infrastructure explicitly does not manage.

This creates an architectural gap: the module ecosystem has validation (`_validate_module()`), caching (`_loaded_modules`), cleanup (`_added_paths`), and type checking (protocol interfaces) — none of which apply to the agent/behavior/context layer that carries governance knowledge.

**Sources**: code-tracer §Module Type → Mount Point Mapping; code-tracer §Key Architectural Observations §7 ("Agents are not a module type"); expert-knowledge C-04 (thin bundle pattern operates at YAML/configuration level).

### X-04: Kernel/Policy Separation Mirrors Governance/Enforcement Separation

The code architecture's kernel/policy separation (C-02) mirrors the governance system's rules/enforcement separation. Both share the same philosophical approach: define abstract contracts in one place, implement policy elsewhere. But the consequences differ sharply:
- **In code**: The separation works well — kernel defines protocols, foundation implements policy, contracts are enforced at mount time
- **In governance**: The separation means enforcement is entirely optional — rules are defined in REPOSITORY_RULES.md, enforcement recipes exist but run manually and check only surface-level compliance

The pattern that enables robust code infrastructure produces fragile governance when applied to human-readable rules rather than machine-checkable contracts.

**Sources**: code-tracer §Summary; subsystem §Coupling Assessment (clean vs. tight coupling split).

---

## Discrepancy Register

| ID | Description | Sources Involved | Status | Impact |
|----|-------------|-----------------|--------|--------|
| D-01 | Eager vs. lazy @-mention directory loading | doc-governance D-03, expert-knowledge D-01 | OPEN | HIGH |
| D-02 | Governance scope: centralized vs. distributed | doc-governance D-01, subsystem | OPEN | MEDIUM |
| D-03 | Content budget: deliberate strategy vs. ad hoc sizing | doc-governance D-02, expert-knowledge X-02 | OPEN | MEDIUM |
| D-04 | recipes-usage.md inclusion mechanism | expert-knowledge D-02 | OPEN | LOW-MEDIUM |
| D-05 | PyO3 coordinator bridge mechanism | code-tracer | OPEN | MEDIUM |
| D-06 | common-agent-base.md content unknown | expert-knowledge D-03 | OPEN | LOW |

### D-01: Eager vs. Lazy @-mention Directory Loading

**Claim A (subsystem, expert-knowledge)**: Directory-level @-mentions like `@core:docs/` may eagerly load all files in that directory. If eager, every session pays full governance token cost (~90K+ characters from docs/ alone). "Whether directory @-mentions are eagerly or lazily loaded" is flagged as the highest-impact unresolved question by both the top-down subsystem and the expert-knowledge synthesis.

**Claim B (no direct evidence)**: No investigation source has traced the resolver code to determine actual behavior. The code-tracer traced the module loader but NOT the @-mention resolver (which lives in `amplifier-foundation/amplifier_foundation/mentions/resolver.py`).

**Impact**: HIGH — determines whether governance content costs ~20KB or ~200KB per session.

**Resolution needed**: Read `_resolve_mention()` in the mentions resolver for directory path arguments. Determine if `os.listdir()` or equivalent is called.

### D-02: Governance Scope — Centralized or Distributed?

**Claim A (bottom-up docs/)**: REPOSITORY_RULES.md describes rules for the entire amplifier ecosystem but is located in a single repo's `docs/`. This centralization is noted as anomalous.

**Claim B (subsystem)**: Three governance documents operate independently across the ecosystem: REPOSITORY_RULES.md (amplifier repo), CONTEXT_POISONING.md (amplifier-foundation), DOCUMENTATION_LINKING.md (amplifier-core). No cross-reference connects them. Governance is actually distributed with no coordination mechanism.

**Impact**: MEDIUM — determines whether governance drift between repos is a design flaw or expected.

**Resolution needed**: Survey all Amplifier ecosystem repos for governance-related documents. Determine if REPOSITORY_RULES.md is canonical source or each repo independently defines governance.

### D-03: Content Budget — Deliberate or Ad Hoc?

**Claim A (bottom-up context/, bottom-up behaviors/)**: File sizes are "nearly identical (~6300–6700 bytes each), suggesting deliberate design: these files are balanced, peer-level context documents." The behavior YAML deliberately demotes `recipes-usage.md` from `context.include` to a comment, "showing conscious token management."

**Claim B (subsystem)**: "No token budget enforcement — full 5-tier resolution could exhaust context window." Recommends "Measure the full token budget."

**Impact**: MEDIUM — if deliberate, the ~6.5KB sizing is a design constraint to preserve; if ad hoc, the system may silently degrade as content grows.

**Resolution needed**: (1) Search for documented context budget policy. (2) Measure actual token cost of full governance content resolution. (3) Check commit history for the `recipes-usage.md` demotion rationale.

### D-04: recipes-usage.md Inclusion Status

**Claim A (bottom-up behaviors/)**: YAML comment says "demoted to soft reference (load on demand)."

**Claim B (primary source)**: Agent instructions say "see amplifier:context/recipes-usage.md (load on demand)" suggesting the agent tells users to request it manually.

**Impact**: LOW-MEDIUM — unclear whether "soft reference" means (a) never injected, (b) injected via different path, or (c) loaded only when agent references it.

**Resolution needed**: Instrument a session with `amplifier-expert-behavior` loaded and observe whether `recipes-usage.md` content appears in the system prompt.

### D-05: PyO3 Coordinator Bridge Mechanism

**Claim A (code-tracer)**: The Python `coordinator.mount("tools", tool, name="foo")` routes through PyO3 to Rust. How a Python `Tool` protocol object gets marshalled into Rust `Arc<dyn Tool>` is untraced. The code-tracer also flags that `coordinator.get("module-source-resolver")` retrieves a resolver, but the Rust coordinator doesn't have a generic string→object store visible in `coordinator.rs`.

**Claim B**: No other investigation source addresses this mechanism.

**Impact**: MEDIUM — the PyO3 bridge is the mechanism that enables governance content delivery (it's how the module-source-resolver gets mounted), yet its implementation is a blind spot. If the bridge has failure modes, they would compound the silent degradation chain.

**Resolution needed**: Read the PyO3 bindings in `amplifier-core/bindings/` to understand Python-side `get()/mount()` for arbitrary keys.

### D-06: common-agent-base.md Content Unknown

**Claim A (expert-knowledge D-03)**: Bottom-up agents/ analysis flags that `@foundation:context/shared/common-agent-base.md` is appended to the expert agent's instructions. "Its content could impose additional operating constraints not apparent from this file alone."

**Claim B**: No investigation source examined the file's content.

**Impact**: LOW — likely adds standard operating constraints, but could modify the expert's effective behavior in governance-relevant ways.

**Resolution needed**: Read the file. This is a simple file read, no code tracing required.

---

## Open Questions

1. **Is the governance enforcement gap deliberate or unsolved?** The 8-version evolution of document-generation suggests mechanical enforcement is hard, not impossible. Is advisory governance sufficient, or is the absence of Golden Rule enforcement an engineering debt?

2. **What is the actual token cost of full governance tier resolution?** No measurement exists. Directory-level @-mentions could expand to 200KB+ of content. This is the most impactful unmeasured quantity in the system.

3. **How do child sessions inherit governance?** The boundary between `delegate tool` and `PreparedBundle.spawn()` — mediated by `session_spawner.py` in `amplifier-app-cli` — is a blind spot across all investigations. Whether child sessions get the same governance content as parent sessions is unverified.

4. **Does the module validation system (`_validate_module()`) have an analog for governance content?** The code infrastructure validates module structure (ProviderValidator, ToolValidator, etc.) but no equivalent validates governance content integrity, completeness, or freshness.

5. **How many governance-like documents exist across the full ecosystem?** Only three repos have been identified (amplifier, amplifier-foundation, amplifier-core). The 37-repo `allowed_source_repos` field in outline specs suggests many repos could contain governance-relevant content.

6. **Is `amplifier-dev-behavior` ever loaded?** The root `bundle.md` only includes `amplifier:behaviors/amplifier-expert`. The dev behavior exists but no investigation found a reference that loads it. It may be orphaned.

---

## Recommended Next Steps

1. **Resolve D-01 (eager vs. lazy loading)** — Trace the @-mention resolver implementation in `amplifier-foundation`. This is the highest-impact open question, determining the governance system's practical token cost per session.

2. **Measure full governance token budget** — Instrument the system prompt factory to log token counts when all 5 tiers resolve. No measurement currently exists.

3. **Trace the PyO3 bridge (D-05)** — Read `amplifier-core/bindings/` to understand how the module-source-resolver mount works across the Python/Rust boundary. This is the mechanism that enables all governance content delivery.

4. **Survey parallel governance systems (D-02)** — Catalog governance-related documents across all Amplifier ecosystem repos. Determine coordination mechanism (or lack thereof).

5. **Read common-agent-base.md (D-06)** — Simple file read to close the lowest-effort discrepancy.

6. **Prototype governance validation** — Explore whether the existing module validation infrastructure (`_validate_module()`) could be extended to validate governance content integrity at session startup.
