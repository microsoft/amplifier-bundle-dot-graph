# Synthesis: Recipe Orchestration Patterns

**Module:** Recipe Orchestration Engine (`amplifier_module_tool_recipes/` + `amplifier/recipes/`)  
**Perspectives synthesized:**
- Top-down code-tracer (executor engine mechanics)
- Top-down integration-mapper (boundary analysis + changelog archaeology)
- Bottom-up level-synthesis (6 real recipe YAML files, behavioral patterns)
- Discovery-pipeline investigation (concrete 3-recipe pipeline, bugs found during testing)
- Subsystem-level cross-module analysis (recipe-orchestration's role in ecosystem)

**Behavior-observer status:** No dedicated behavior-observer ran; bottom-up level-synthesis partially fills this gap with real recipe analysis.  
**Fidelity tier:** standard  
**Synthesis date:** 2026-03-20

---

## Executive Summary

The Recipe Orchestration Engine is a 2,750+ line async workflow executor implemented across five source files, driving 6 production recipes (22KB–126KB, 386KB total). Four independent perspectives converge on the same meta-finding: the engine is a shadow framework — a Turing-complete orchestration layer behind a declarative YAML surface. It implements flat/staged routing, five step types (agent, bash, recipe, foreach, while), approval gates, three-tier rate limiting, provider tiering, and quality-gate loops — all accessed through a single formal kernel capability (`session.spawn`) but 9+ informal coordinator surfaces via duck-typed `getattr()`. The most significant cross-cutting insight is that recipe-level conventions (model tiering, `_precomputed` optimization, file-based data passing, rate limiting) constitute an uncodified framework layer where most production bugs and workarounds concentrate.

---

## Convergence Table

| # | Claim | Perspectives Confirming | Confidence |
|---|-------|------------------------|------------|
| C-01 | Single formal kernel capability (`session.spawn` at executor.py:1559) but 9+ informal coordinator surfaces | code-tracer, integration-mapper, subsystem | HIGH |
| C-02 | Orchestrator/Worker recipe pattern is the dominant composition model | bottom-up (2 pairs), integration-mapper, discovery-pipeline | HIGH |
| C-03 | Five step types: agent, bash, recipe, foreach, while | code-tracer, discovery-pipeline (uses all 5) | HIGH |
| C-04 | Model tier strategy (haiku/sonnet/opus) is a recipe-level convention with no central definition | integration-mapper (F-12), bottom-up (Pattern 5) | HIGH |
| C-05 | Filesystem is the primary cross-agent coordination mechanism | integration-mapper, bottom-up (Connection 3), discovery-pipeline (Finding 4) | HIGH |
| C-06 | Template→bash boundary is the most fragile integration point | integration-mapper (changelogs), discovery-pipeline (injection surface) | HIGH |
| C-07 | Approval gates are control-flow mechanisms, not failure modes | code-tracer (C-03), bottom-up (Pattern 3), discovery-pipeline | HIGH |
| C-08 | Context dict is overloaded: execution state + data bus + template store + checkpoint | code-tracer, integration-mapper, discovery-pipeline (cross-stage threading) | HIGH |
| C-09 | Checkpoint trimming (>100KB → placeholder) creates data loss risk on resume | code-tracer, integration-mapper | HIGH |
| C-10 | Parallel foreach + approval gates is explicitly undefined behavior | code-tracer, integration-mapper | HIGH |
| C-11 | Convention-over-code architecture dominates recipe patterns | bottom-up (8 convention examples), subsystem (Emergent Pattern 2) | HIGH |
| C-12 | Recipe engine is the widest boundary-crossing module in the ecosystem | integration-mapper, subsystem (Flow 14, Pattern 7) | HIGH |
| C-13 | Quality-gate loops are an emergent cross-recipe pattern | discovery-pipeline (while loop max 3×), bottom-up (doc-gen 6 stages) | HIGH |
| C-14 | Safe expression evaluator uses recursive descent parsing (no `eval()`) | code-tracer, integration-mapper | HIGH |
| C-15 | Sub-recipe output delta trimming returns only new keys to parent | code-tracer, integration-mapper | HIGH |

---

## Consensus Findings

### F-01: Architecture — Five-File Engine Driving Six Production Recipes (HIGH)

The code-tracer traced five source files: `__init__.py` (tool shell), `executor.py` (execution engine), `models.py` (YAML data model), `session.py` (persistence), and `expression_evaluator.py` (condition parser). The bottom-up analysis independently cataloged the 6 real recipes this engine drives:

| Recipe | Version | Structure | Size |
|--------|---------|-----------|------|
| `amplifier-ecosystem-audit.yaml` | 1.2.0 | staged + approval | 22KB |
| `repo-audit.yaml` | 1.2.0 | flat | 35KB |
| `ecosystem-activity-report.yaml` | 1.15.2 | flat | 63KB |
| `repo-activity-analysis.yaml` | 3.1.0 | flat | 49KB |
| `document-generation.yaml` | 8.1.0 | multi-stage + approval | 126KB |
| `outline-generation-from-doc.yaml` | 1.6.1 | flat | 91KB |

**Source:** code-tracer §Entry Points; bottom-up level-synthesis §Files table

### F-02: Orchestrator/Worker — The Dominant Composition Pattern (HIGH)

Three independent perspectives confirm orchestrator/worker as the primary recipe composition model:
- **Bottom-up** identified 2 explicit pairs: audit (ecosystem-audit → repo-audit) and activity (ecosystem-activity-report → repo-activity-analysis)
- **Integration-mapper** traced the sub-recipe execution mechanics: `foreach` + `type: recipe` with context variable passing
- **Discovery-pipeline** is itself an orchestrator (3 stages) dispatching worker sub-recipes per topic

Both bottom-up pairs share the same structure: orchestrator discovers entities → optional approval gate → fans out via foreach → collects results. Rate limiting is owned by the orchestrator; workers don't define it.

**Source:** bottom-up §Patterns 1–2; integration-mapper §Boundary 6–7; discovery-pipeline code-tracer §Finding 3

### F-03: Model Tier Strategy — Uncodified Cost Optimization (HIGH)

The integration-mapper identified per-step model selection as a recipe-level cost optimization (F-12). The bottom-up analysis independently cataloged the same pattern across 3 recipes: haiku for parsing/classification, sonnet for analysis/synthesis, opus for generation. Critically, the bottom-up analysis adds: "no central definition — each recipe encodes it locally." This is copy-pasted YAML, not a framework feature.

**Source:** integration-mapper §F-12; bottom-up §Pattern 5

### F-04: Filesystem as Coordination Medium — Three Variants (HIGH)

Three perspectives identify filesystem coordination, each revealing a different variant:
1. **Explicit sub-recipe invocation** (bottom-up Connection 1–2): context passed via recipe engine
2. **Manual pipeline** (bottom-up Connection 3): outline-gen → document-gen connected by `outline.json` on disk, user must wire explicitly
3. **Shadow data bus** (integration-mapper F-11): `_precomputed` convention + `./ai_working/` shared namespace

The discovery-pipeline analysis confirms: "the file system is the ONLY coordination mechanism between agents."

**Source:** bottom-up §Connections 1–3; integration-mapper §F-11; discovery-pipeline §Finding 4

### F-05: Template→Bash Fragility — Confirmed from Two Angles (HIGH)

The integration-mapper found systematic template→bash escaping failures from changelogs (v1.7.0 large JSON breaks bash; v6.1.1 Python boolean mismatch). The discovery-pipeline investigation independently found the same pattern: `{{topics}}` substituted directly as a Python literal into bash heredoc scripts — "potential injection surface if topics contain special characters."

The integration-mapper documented the evolved workaround: `printf '%s\\n'` replaced `echo` and heredocs, and file-based data passing emerged as a structural workaround.

**Source:** integration-mapper §F-09; discovery-pipeline integration-mapper §Boundary 3

### F-06: Three-Layer Memory Safety with Known Corruption Surface (HIGH)

Both code-tracer and integration-mapper confirm three layers of defense:
1. Sub-recipe output delta trimming (executor.py:2509-2514) — returns only new keys
2. Checkpoint trimming (executor.py:1455-1495) — replaces values >100KB with placeholders
3. Tool-result truncation at 10KB
4. `gc.collect()` after every agent spawn (evidence of past PyO3/Rust reference cycle problems)

The checkpoint trimming creates a known corruption surface: on resume, `substitute_variables()` silently injects placeholder strings into prompts. Neither perspective has verified whether this occurs in production.

**Source:** code-tracer §Critical Observations #2, #4; integration-mapper §Cross-Cutting Concern 2

### F-07: Quality-Gate Loop — Emergent Cross-Recipe Pattern (HIGH)

The discovery-pipeline investigation revealed a concrete quality-gate implementation: `while_condition: "true"` + `break_when: "{{quality_check.quality_passed}} == true"` + `max_while_iterations: 3`. This pattern synthesize→validate→retry enables iterative improvement.

The bottom-up analysis found `document-generation.yaml` (v8.1.0, 126KB, 6 stages) uses multi-stage approval gates for quality control — a different implementation of the same concept. Together these reveal quality gating as an emergent pattern implemented differently in each recipe, with no shared abstraction.

**Source:** discovery-pipeline code-tracer §Finding 4; bottom-up §Pattern 3

### F-08: Rate Limiting — Three Independent Tiers (HIGH)

The integration-mapper identified three rate-limiting tiers:
1. Recipe-level `rate_limiting.max_concurrent_llm` + `min_delay_ms`
2. Orchestrator-level `orchestrator.config.min_delay_between_calls_ms`
3. Bash-level `api_delay_seconds` (GitHub API pacing)

The bottom-up analysis confirms and adds a nuance: both GitHub-facing orchestrators define `rate_limiting`, but only `ecosystem-activity-report` adds orchestrator-level pacing. This asymmetry may indicate different reliability requirements or an incomplete port.

**Source:** integration-mapper §F-10; bottom-up §Pattern 4

### F-09: Cancellation — Two-Source State Machine Without Child Propagation (HIGH)

Both code-tracer and integration-mapper confirm: cancellation comes from `coordinator.cancellation` (SIGINT) and `session_manager.request_cancellation()` (external call), with a four-state machine (NONE → REQUESTED → IMMEDIATE → CANCELLED). The integration-mapper adds: spawned agent sessions are **unaware** of recipe cancellation — no propagation into child sessions.

**Source:** code-tracer §Cancellation System; integration-mapper §Cross-Cutting Concern 3

### F-10: Provider Resolution — Five-Tier Priority with Inline Fallback (HIGH)

Both agents traced the five-tier cascade: step `provider_preferences` → step `model_role` → legacy `provider`+`model` → agent-level `provider_preferences` → agent `model_role`. An inline fallback at executor.py:1706-1746 re-implements `amplifier_hooks_routing.resolver` logic due to cross-venv dependency, with unknown behavioral drift.

**Source:** code-tracer §execute_step(); integration-mapper §Boundary 10

---

## Single-Source Findings

### F-11: `depends_on` is Validation-Only Metadata [code-tracer] (MEDIUM)

`depends_on` (models.py:262) is validated at build time (referenced step IDs must exist and appear earlier) but has no runtime enforcement. Steps always execute sequentially in order.

**Source:** code-tracer unknowns §U-08

### F-12: Bash Steps Exempt from Recursion Limits [code-tracer] (MEDIUM)

Bash steps do NOT count against the recursion `total_steps` limit (executor.py:2655-2752). A recipe hitting its limit could add more bash steps without restriction.

**Source:** code-tracer findings §Bash Step

### F-13: Checkpoint-Approval Two-Phase Commit Risk [integration-mapper] (MEDIUM)

When a staged recipe hits an approval gate, two sequential operations write to the same JSON file: (1) save state with next-stage pointer, (2) add approval fields. A crash between them advances the stage pointer without recording the pending approval.

**Source:** integration-mapper §Emergent Composition Effect 3

### F-14: Observability Gaps at Error-Prone Boundaries [integration-mapper] (MEDIUM)

Six recipe lifecycle events are registered, but NO events are emitted for: variable substitution failures, checkpoint trimming, rate limiter state changes, sub-recipe entry/exit, or condition evaluation. These missing events cover the most common bug sources per changelogs.

**Source:** integration-mapper unknowns §IU-10

### F-15: Naming Variance in Orchestrator/Worker Contracts [bottom-up] (MEDIUM)

The bottom-up analysis found naming inconsistencies across paired recipes:
- `create_fix_prs` (orchestrator) → `create_fix_pr` (worker) — plural/singular mismatch
- Different `working_dir` defaults per recipe
- No schema validation between orchestrator and worker context contracts

**Source:** bottom-up §Naming Inconsistencies table

### F-16: `foundation:zen-architect` is Universal — Used by ALL 6 Recipes [bottom-up] (MEDIUM)

All 6 recipes use `foundation:zen-architect` for analysis, synthesis, and generation. `foundation:explorer` is used by 4 of 6. This concentration means a single agent regression affects all recipe workflows.

**Source:** bottom-up §Shared Agent Usage table

### F-17: document-generation.yaml is an Outlier (v8.1.0, 126KB) [bottom-up] (MEDIUM)

At 126KB and version 8.1.0 with in-file changelog spanning 7+ major versions, document-generation has a separate development cadence from all other recipes. It's the only recipe using design-intelligence agents and the only one with opus-tier model selection.

**Source:** bottom-up §Uncertainty 5

### F-18: Bundle Resolution Requires Full Amplifier Session [discovery-pipeline] (HIGH)

The discovery-pipeline investigation found that `@dot-graph:recipes/*` bundle-relative paths failed during Phase E integration testing because the bundle wasn't registered. Recipe execution failed at Stage 1 — this is not a graceful degradation but a hard failure.

**Source:** discovery-pipeline code-tracer §Finding 5; §Bug 6

### F-19: Incremental Detection Blind Spot [discovery-pipeline] (MEDIUM)

The discovery pipeline's change-detect step uses `git rev-parse HEAD` for incremental detection. If prompts or agent descriptions change but code files don't, the pipeline won't re-investigate. This applies to any recipe implementing git-based skip logic.

**Source:** discovery-pipeline integration-mapper §Composition Effects

---

## Cross-Cutting Insights

### Insight 1: The Recipe Layer is a Shadow Framework

Combining the top-down engine analysis, bottom-up real recipe patterns, and subsystem-level cross-module view reveals: recipe YAML conventions constitute an uncodified framework layer. Model tiering, `_precomputed` optimization, file-based data passing, rate limiting configuration, quality-gate loops, orchestrator/worker patterns, and naming conventions are all framework-level patterns encoded entirely in copied YAML. The engine provides primitives (steps, loops, conditions); the framework emerges from convention. This is where most production bugs and version churn concentrate — document-generation at v8.1.0 is evidence.

### Insight 2: Context Dict is a Universal (Overloaded) Integration Medium

The code-tracer traced internal mechanics. The integration-mapper identified architectural implications. The discovery-pipeline showed cross-stage context threading. Together: the context dict simultaneously serves as execution state, data bus, template variable store, checkpoint payload, and cross-recipe interface. Every boundary in the system passes through context, making it the single most important and fragile data structure. Checkpoint trimming, template escaping, and naming variance all attack this single surface.

### Insight 3: Duck Typing Creates an Invisible Dependency Graph

The code-tracer found specific `getattr()` calls. The integration-mapper counted 9+ coordinator surfaces. The subsystem analysis elevated this to the "widest boundary module" pattern. Together: the recipe module's actual dependency surface is far wider than any manifest declares. It functionally depends on coordinator, session, hooks, cancellation, display, bundle resolution, and provider routing — all through untyped attribute lookups that silently degrade to fallback values when surfaces are absent.

### Insight 4: Workarounds Mark Boundary Impedance Mismatches

The integration-mapper's changelog archaeology and the code-tracer's mechanism tracing converge on the same workaround set: `gc.collect()` for PyO3 memory cycles, `printf '%s\\n'` for template→bash escaping, output delta trimming for context accumulation, inline routing fallback for cross-venv dependency, file-based data passing for large JSON. Each workaround marks a boundary where the declarative YAML surface conceals an impedance mismatch with imperative execution. The discovery-pipeline's `{{topics}}` injection surface suggests more workarounds are needed.

---

## Discrepancy Register

| ID | Description | Perspectives | Impact | Status |
|----|-------------|-------------|--------|--------|
| D-01 | "Single integration point" vs. "widest module" characterization | code-tracer, integration-mapper | LOW | RESOLVED |
| D-02 | Missing full behavioral quantification of engine feature usage | all | MEDIUM | PARTIALLY RESOLVED |
| D-03 | foreach parallelism default behavior and context isolation | code-tracer, discovery-pipeline, bottom-up | MEDIUM | OPEN |
| D-04 | Approval gate persistence across session boundaries | discovery-pipeline (both agents) | HIGH | OPEN |
| D-05 | Bundle resolution path — traced in theory, failed in practice | top-down, discovery-pipeline | HIGH | OPEN |

### D-01: Kernel Coupling Characterization — RESOLVED

**Code-tracer claims:** "The entire recipe engine touches amplifier-core through exactly one capability: `coordinator.get_capability('session.spawn')` at executor.py:1559."

**Integration-mapper claims:** "The recipe executor accesses 9+ coordinator capabilities" and is "the widest module in the ecosystem."

**Resolution:** These are compatible at different scopes. One formal `get_capability` call for agent execution; 9+ informal `getattr()` access surfaces total. Both are factually correct.

### D-02: Missing Behavioral Quantification — PARTIALLY RESOLVED

**Top-down** flagged: behavior-observer produced no artifacts. Missing: feature usage frequency, anti-pattern catalog, documented vs. actual patterns.

**Bottom-up provides partial fill:** Catalogs all 6 recipes with structure types, version depths, sizes, agent usage, and connection patterns. Confirms 2 of 6 are staged, 4 are flat; 2 use foreach sub-recipes; 1 uses manual pipeline. Identifies model tier strategy across 3 recipes.

**Still missing:** Per-feature engine usage statistics (how many recipes use while loops? condition evaluation? parallel foreach?), anti-pattern catalog, comparison of documented patterns vs. actual usage.

### D-03: foreach Parallelism Behavior — OPEN

**Code-tracer claims:** Sequential loops share context by reference; parallel loops get isolated copies per iteration (C-05).

**Discovery-pipeline notes:** foreach in the pipeline recipe doesn't specify `parallel: true`, so runs sequentially. Asks: "Does foreach run recipe invocations sequentially or in parallel?"

**Bottom-up shows:** audit pair uses `parallel: 2`, activity pair uses `parallel: {{parallel_analysis}}` (default: 1).

**Unresolved:** The isolation mechanism for parallel copies is traced in code (code-tracer) but never tested with real recipes containing approval gates (C-10). The actual behavior of `asyncio.gather()` + `ApprovalGatePausedError` + `return_exceptions=False` is undetermined.

**Resolution needed:** Execution-based test with parallel foreach over sub-recipes containing approval gates.

### D-04: Approval Gate Persistence Across Sessions — OPEN

**Discovery-pipeline code-tracer unknowns §3:** "If the session ends between Stage 1 and Stage 2, can the pipeline resume from the approval gate checkpoint?"

**Discovery-pipeline integration-mapper unknowns §3:** "If the session is closed after Stage 1 approval, can a new session resume from the approval checkpoint? Not tested."

**Top-down (F-13):** Identified a two-phase commit risk — crash between checkpoint write and approval field write could skip the gate.

**Unresolved:** No execution-based verification. The checkpoint persistence mechanism is traced in code, but cross-session resumability through approval gates is not tested.

### D-05: Bundle Resolution — Theory vs. Practice Gap — OPEN

**Top-down integration-mapper:** Traced `@bundle:path` resolution via `mention_resolver` capability.

**Discovery-pipeline (Bug 6):** "Agent bundle references (`dot-graph:...`) not found via recipe framework — requires full Amplifier session with bundle configured." Recipe execution **failed at Stage 1** during Phase E testing.

**Unresolved:** The resolution path exists in theory (mention_resolver → source_base_paths → file lookup) but when the bundle wasn't registered, the failure was hard, not graceful. This contradicts the silent degradation pattern seen elsewhere.

---

## Open Questions

### OQ-01: Who registers `session.spawn` and when? (HIGH)
Both top-down agents flagged this. `executor.py:1559` consumes it, nobody in the recipe module registers it. Likely in the app layer. A boot-ordering bug could silently disable all agent steps.

### OQ-02: What is the actual data loss surface during checkpoint-trimmed resume? (HIGH)
When >100KB values are trimmed to placeholders and the recipe resumes, `substitute_variables()` silently injects placeholders. Not verified in production.

### OQ-03: What happens when parallel foreach + approval gates interact? (HIGH)
`asyncio.gather()` with `return_exceptions=False` would raise on first `ApprovalGatePausedError` and cancel remaining tasks. Not verified.

### OQ-04: Can recipes resume across session boundaries through approval gates? (HIGH)
Identified by both discovery-pipeline agents. Not tested. The two-phase commit risk (F-13) makes this particularly important.

### OQ-05: How do the three rate-limiting tiers interact? (MEDIUM)
Do they stack? Does sub-recipe inheritance override or merge?

### OQ-06: Does the inline routing fallback drift from canonical implementation? (MEDIUM)
The inline fallback at executor.py:1706-1746 may differ from `amplifier_hooks_routing.resolver`.

### OQ-07: Is the `_precomputed` convention documented? (LOW)
No documentation or schema validation found for this optimization contract.

### OQ-08: Why does only `ecosystem-activity-report` use `orchestrator.config` pacing? (LOW)
The audit recipe doesn't include within-agent pacing despite similar multi-repo API exposure.

---

## Recommended Next Steps

1. **Execution-based verification of OQ-02** (HIGH) — Test checkpoint trimming + resume with large step outputs. This resolves the highest-severity unverified claim.

2. **Execution-based verification of OQ-03** (HIGH) — Test parallel foreach + approval gate interaction. Both top-down agents flagged this as undefined behavior.

3. **Execution-based verification of OQ-04** (HIGH) — Test cross-session approval gate resumability. Discovery-pipeline agents independently identified this gap.

4. **Run full behavior-observer pass** (MEDIUM) — Read all 6 production recipes to quantify: which engine features are actually used (while loops, conditions, parallel foreach, sub-recipes) and which are unused. The bottom-up synthesis partially fills this but doesn't map features back to engine capabilities.

5. **Trace `session.spawn` registration** (HIGH) — Follow OQ-01 to map boot-time capability registration. A single missing registration silently disables all agent steps.

6. **Abstract MODULES.md access** (MEDIUM) — The subsystem synthesis identified 3 independent fetch mechanisms across 4 recipes as the most significant tight coupling. An `@amplifier:docs/MODULES.md` mention would align with existing patterns.

7. **Formalize recipe-coordinator contract** (MEDIUM) — The 9+ duck-typed `getattr()` surfaces should be evaluated for formal capability registration.
