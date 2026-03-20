# Synthesis: Recipe Orchestration Engine

**Module:** Recipe Orchestration Engine (`amplifier_module_tool_recipes/`)  
**Source perspectives:** code-tracer (top-down), integration-mapper (top-down), bottom-up recipe analysis, subsystem-level synthesis  
**Missing perspective:** behavior-observer (no artifacts produced in any investigation pass)  
**Fidelity tier:** standard  
**Synthesis date:** 2026-03-19

---

## Executive Summary

The Recipe Orchestration Engine is a 2,750+ line async workflow executor implemented as an Amplifier tool module across six source files (`__init__.py`, `executor.py`, `models.py`, `session.py`, `expression_evaluator.py`, `validator.py`). Multiple investigation perspectives independently confirm it integrates with amplifier-core through a single formal agent-execution capability (`session.spawn`) while accessing 9+ coordinator surfaces via duck-typed attribute lookups. The engine implements flat sequential, staged (with approval gates), foreach (sequential/parallel), while-loop, bash, and recursive sub-recipe execution paths. Its most architecturally significant property — confirmed across all perspectives — is that it is the **widest boundary-crossing module** in the ecosystem, touching provider routing, session persistence, cancellation, hooks, bundle resolution, and template evaluation simultaneously. The bottom-up analysis of 6 real recipe YAML files reveals two orchestrator/worker recipe pairs, a model-tier cost optimization convention, and tight coupling to MODULES.md via three independent fetch mechanisms that bypass the @-mention protocol. Three high-impact open questions remain: the data loss surface during checkpoint-trimmed resume, the undefined runtime behavior of parallel foreach with approval gates, and whether the three independent rate-limiting tiers interact correctly.

---

## Convergence Table

| # | Claim | Perspectives Confirming | Confidence |
|---|-------|------------------------|------------|
| C-01 | Single kernel integration point for agent execution via `coordinator.get_capability("session.spawn")` at executor.py:1559 | code-tracer, integration-mapper | HIGH |
| C-02 | Sub-recipe output delta trimming (executor.py:2509-2514) returns only new keys to parent, preventing memory accumulation | code-tracer, integration-mapper | HIGH |
| C-03 | `ApprovalGatePausedError` is a control-flow mechanism (not a failure) for human-in-the-loop pauses | code-tracer, integration-mapper, source code verification | HIGH |
| C-04 | Explicit `gc.collect()` after every agent spawn and sub-recipe execution to break PyO3/Rust reference cycles | code-tracer, integration-mapper | HIGH |
| C-05 | Sequential loops share context by reference; parallel loops get isolated copies per iteration | code-tracer, integration-mapper | HIGH |
| C-06 | Checkpoint trimming (>100KB -> placeholder) creates silent data corruption risk on resume | code-tracer, integration-mapper | HIGH |
| C-07 | Parallel foreach + approval gates is explicitly "undefined behavior" (validator warns but doesn't prevent) | code-tracer, integration-mapper | HIGH |
| C-08 | Provider resolution has inline fallback re-implementing `amplifier_hooks_routing.resolver` logic due to cross-venv dependency | code-tracer, integration-mapper | HIGH |
| C-09 | Two independent cancellation sources (coordinator CancellationToken + SessionManager state machine) must stay synchronized | code-tracer, integration-mapper, source code verification | HIGH |
| C-10 | Safe expression evaluator uses recursive descent parsing (no `eval()`) with custom truthiness rules | code-tracer, integration-mapper | HIGH |
| C-11 | Duck-typed coordinator access via `getattr()` with fallback creates invisible coupling to 9+ surfaces | code-tracer, integration-mapper | HIGH |
| C-12 | Recipe engine is the widest module in the ecosystem — touches more boundaries than any other | code-tracer, integration-mapper, subsystem synthesis | HIGH |
| C-13 | `foundation:zen-architect` is the universal agent used by all 6 real recipes | bottom-up recipe analysis | HIGH |
| C-14 | Two orchestrator/worker recipe pairs follow identical structural pattern (ecosystem-audit/repo-audit, ecosystem-activity/repo-activity) | bottom-up recipe analysis, subsystem synthesis | HIGH |
| C-15 | Three independent MODULES.md fetch mechanisms bypass the @-mention namespace protocol — the tightest coupling in the subsystem | bottom-up recipe analysis, subsystem synthesis | HIGH |

---

## Consensus Findings

### F-01: Architecture — Six-File Module with Single Formal Kernel Entry Point (HIGH)

Both top-down agents confirm the module comprises six source files: `__init__.py` (tool shell + mount, 986 lines), `executor.py` (execution engine, 2752 lines), `models.py` (YAML data model), `session.py` (persistence, 577 lines), `expression_evaluator.py` (condition parser), and `validator.py` (recipe validation). Source code verification confirms the import structure: `__init__.py` imports from `executor`, `models`, `session`, and `validator`. The engine integrates with amplifier-core through exactly one formal capability for agent execution (`session.spawn`), but the integration-mapper identified 9+ informal coordinator surfaces accessed via `getattr()`.

**Source:** code-tracer findings §Entry Points; integration-mapper findings §Cross-Cutting Concern 1; source code `__init__.py:1-17`

### F-02: Execution Model — Flat/Staged Routing with Five Step Types (HIGH)

The code-tracer traced the complete execution flow: `execute_recipe()` at executor.py:435 routes to either flat loop (executor.py:626) or `_execute_staged_recipe()` (executor.py:848) based on `recipe.is_staged`. Five step types are dispatched: agent (via `execute_step_with_retry`), bash (via `_execute_bash_step`), recipe (via `_execute_recipe_step`), foreach loop, and while loop. The integration-mapper's boundary analysis confirms each type crosses different boundaries. Bottom-up recipe analysis validates this with real usage: all 6 recipes use agent steps, 4 use bash, 2 use sub-recipe invocation, 2 use foreach loops, and 2 use staged execution with approval gates.

**Source:** code-tracer findings §Execution Paths; integration-mapper integration-map §Boundaries; bottom-up recipes findings §Boundary Patterns

### F-03: Memory Safety — Three-Layer Defense Against Context Accumulation (HIGH)

Both agents independently identified the context accumulation problem and its three-layer mitigation:
1. **Sub-recipe output delta trimming** (executor.py:2509-2514) — returns only new keys
2. **Checkpoint trimming** (executor.py `_CHECKPOINT_TRIM_THRESHOLD_BYTES = 100_000`) — replaces values >100KB with placeholders
3. **Tool-result truncation** at 10KB (`MAX_OUTPUT_SIZE_BYTES = 10_000` in `__init__.py:23`)

Source code verification confirms both thresholds. The `gc.collect()` calls are evidence of past memory problems with PyO3/Rust reference cycles.

**Source:** code-tracer findings §Critical Observations; integration-mapper findings §Cross-Cutting Concern 2; source code `__init__.py:23`, `executor.py:42`

### F-04: Approval Gate Propagation Through Nested Recipes (HIGH)

Both agents confirm the approval mechanism: `ApprovalGatePausedError` (executor.py:60-79) propagates up the call stack, the tool layer catches it and returns `status: "paused_for_approval"`, and on resume the saved state is loaded and execution continues. The integration-mapper additionally identified compound stage name bubbling (`parent_stage/child_stage`) as an emergent composition effect. Source code verification confirms the exception carries `session_id`, `stage_name`, `approval_prompt`, and `resume_session_id`.

**Source:** code-tracer findings §Staged Recipe; integration-mapper findings §Emergent Composition Effects; source code `executor.py:60-79`

### F-05: Cancellation — Two-Source Four-State Machine (HIGH)

Both agents confirm cancellation comes from two sources: `coordinator.cancellation` (SIGINT/Ctrl+C propagation) and `session_manager.request_cancellation()` (external tool call). Source code verification confirms the four-state enum: `NONE -> REQUESTED -> IMMEDIATE -> CANCELLED` (session.py:24-36). The integration-mapper identified that spawned agent sessions are **unaware** of recipe cancellation — there is no cancellation propagation into child agent sessions.

**Source:** code-tracer findings §Cancellation System; integration-mapper findings §Cross-Cutting Concern 3; source code `session.py:24-36`

### F-06: Orchestrator/Worker Recipe Pairs — Dominant Real-World Pattern (HIGH)

Bottom-up recipe analysis independently discovered the same structural pattern the subsystem synthesis identified: two recipe pairs follow identical orchestrator/worker design:
- **Audit pair**: `amplifier-ecosystem-audit.yaml` (orchestrator, staged + approval) -> `repo-audit.yaml` (worker, flat)
- **Activity pair**: `ecosystem-activity-report.yaml` (orchestrator) -> `repo-activity-analysis.yaml` (worker)

Both use `foreach` with `type: recipe` to fan out work. Both orchestrators own rate-limiting configuration. Workers do not define rate limiting.

**Source:** bottom-up recipes findings §Boundary Patterns; subsystem synthesis §Flow 4-5

### F-07: MODULES.md Bypass — Tightest Coupling in the Subsystem (HIGH)

The subsystem synthesis identified 3 independent fetch mechanisms for MODULES.md that bypass the @-mention protocol:
1. `repo-audit` + `ecosystem-audit`: `curl -sL` from GitHub raw URL
2. `ecosystem-activity-report`: `gh api` + `base64 -d`
3. `outline-generation-from-doc`: local file read

The bottom-up recipe analysis confirms 4 of 6 recipes depend on MODULES.md. The @-mention protocol (`amplifier:docs/MODULES.md`) exists specifically to abstract content delivery, yet recipes bypass it entirely for their most critical shared dependency.

**Source:** subsystem synthesis §Flow 5; bottom-up recipes findings §Connection 1-2

---

## Single-Source Findings

### F-08: `depends_on` is Validation-Only Metadata [code-tracer] (MEDIUM)

The code-tracer found that `depends_on` (models.py) is validated at build time (validator.py checks that referenced step IDs exist and appear earlier) but found no evidence of runtime enforcement in executor.py. Steps execute sequentially in definition order, making `depends_on` a documentation/validation mechanism, not a runtime scheduling constraint.

**Source:** code-tracer unknowns §U-08

### F-09: Bash Steps Exempt from Recursion Limits [code-tracer] (MEDIUM)

Bash steps do NOT count against the recursion `total_steps` limit (executor.py:2655-2752). A recipe hitting its step limit could theoretically add more bash steps without restriction. This is likely intentional but creates an asymmetry.

**Source:** code-tracer findings §Step Type: Bash Step

### F-10: Template-to-Bash Boundary is the Most Fragile Integration Point [integration-mapper] (MEDIUM)

Changelog analysis revealed a systematic pattern of template-to-bash escaping failures: large JSON breaking bash (v1.7.0), Python boolean `True`/`False` vs JSON `true`/`false` mismatch (v6.1.1), and evolved `printf '%s\\n'` workarounds. This fragility drove the emergence of file-based data passing as a workaround convention.

**Source:** integration-mapper unknowns §IU-08

### F-11: Three-Tier Rate Limiting Across Independent Boundaries [integration-mapper] (MEDIUM)

Three independent rate-limiting tiers exist:
1. Recipe-level: `rate_limiting.max_concurrent_llm` + `min_delay_ms`
2. Orchestrator-level: `orchestrator.config.min_delay_between_calls_ms`
3. Bash-level: `api_delay_seconds` (GitHub API pacing)

Bottom-up recipe analysis confirms both GitHub-facing orchestrators define `rate_limiting` blocks, but only `ecosystem-activity-report` uses `orchestrator.config` — the asymmetry is unexplained.

**Source:** integration-mapper unknowns §IU-02; bottom-up recipes findings §Pattern 4

### F-12: Model Tier Strategy as Copy-Pasted Convention [integration-mapper, bottom-up] (MEDIUM)

Both perspectives independently identified per-step model tiering (haiku for parsing, sonnet for analysis, opus for generation) as a cost optimization pattern. The bottom-up analysis confirms 3 of 6 recipes use this pattern. There is no central `model-tiers.yaml` or common include — each recipe encodes the strategy independently, creating drift risk.

**Source:** integration-mapper integration-map §Boundary 3; bottom-up recipes findings §Pattern 5

### F-13: `_precomputed` Convention for Sub-Recipe Optimization [integration-mapper] (MEDIUM)

Parent recipes pass pre-calculated values to sub-recipes using underscore-prefixed `_precomputed` keys to skip expensive LLM calls. The bottom-up analysis confirmed this in `ecosystem-activity-report -> repo-activity-analysis` data passing. This is an implicit contract with no schema or compatibility checking.

**Source:** integration-mapper integration-map §Boundary 7; bottom-up recipes findings §Connection 2

### F-14: Checkpoint-Approval Two-Phase Commit Risk [integration-mapper] (MEDIUM)

When a staged recipe hits an approval gate, two sequential operations write to the same JSON file: (1) save state with next-stage pointer, (2) add approval fields. A crash between steps 1 and 2 would advance the stage pointer without recording the pending approval, causing the approval gate to be skipped on resume.

**Source:** integration-mapper findings §Emergent Composition Effect 3

### F-15: Observability Blind Spots at Error-Prone Boundaries [integration-mapper] (MEDIUM)

Six recipe lifecycle events are registered (`recipe:start`, `recipe:step`, `recipe:complete`, `recipe:approval`, `recipe:loop_iteration`, `recipe:loop_complete`), but NO events are emitted for: variable substitution failures, checkpoint trimming, rate limiter state changes, sub-recipe entry/exit, or condition evaluation. These missing events cover the most common sources of bugs per changelogs.

**Source:** integration-mapper unknowns §IU-10

### F-16: Naming Inconsistencies Across Paired Recipes [bottom-up] (LOW)

Bottom-up recipe analysis found naming variances between orchestrator and worker recipes: `create_fix_prs` (plural) vs `create_fix_pr` (singular), differing `working_dir` defaults. These are translation points in the orchestrator's `context:` block when invoking the worker.

**Source:** bottom-up recipes findings §Naming Inconsistencies

---

## Cross-Cutting Insights

### Insight 1: Context Dict is the Universal (Overloaded) Integration Medium

All perspectives surface different facets of the same underlying issue: the `context` dict simultaneously serves as execution state, data bus, template variable store, and checkpoint payload. The code-tracer traced how values flow in (step outputs, loop variables) and out (template substitution, sub-recipe parameters). The integration-mapper identified this overloading as the root cause of checkpoint trimming corruption, template escaping bugs, and memory accumulation. The bottom-up analysis revealed the `_precomputed` convention and `working_dir` defaults as further evidence of context-as-data-bus patterns. Every boundary in the system passes through context, making it the single most important data structure and the single most fragile.

### Insight 2: Declarative-Imperative Gap is the Meta-Tension

The integration-mapper explicitly named this as "Architectural Tension 2": recipe YAML is declarative, but the executor implements mutable state, conditionals, loops, recursion, rate limiting, error handling, and approval gates — a Turing-complete orchestration engine. The code-tracer's detailed mechanism tracing implicitly confirms this by revealing the depth of imperative machinery behind each YAML keyword. The bottom-up recipe analysis corroborates: `document-generation.yaml` alone is 126KB with 8+ major versions, indicating iterative complexity growth. This gap is where most recipe bugs live.

### Insight 3: Workarounds Reveal Boundary Tensions

The integration-mapper's changelog analysis and the code-tracer's mechanism tracing converge on the same set of workarounds: `gc.collect()` for memory (PyO3 cycles), file-based data passing for template-to-bash fragility, output delta trimming for context accumulation, inline routing fallback for cross-venv dependency. The bottom-up analysis adds: the `_precomputed` convention (workaround for redundant LLM calls) and naming translation points (workaround for no shared schema between orchestrator and worker). Each workaround marks a boundary where the declarative YAML surface conceals an impedance mismatch with the imperative execution reality.

### Insight 4: Silent Degradation Chain Spans the Module

The subsystem synthesis identified a two-layer silent degradation chain: module loading continues on non-fatal failures, and @-mention returns None on missing content. The recipe engine is the primary consumer of this chain — if MODULES.md fetch fails, if agent spawning silently degrades, if checkpoint trimming silently corrupts values, the recipe continues executing with degraded state. The six observability events (F-15) do not cover the most common failure modes, creating a module where failures propagate silently through context corruption rather than surfacing as errors.

---

## Discrepancy Register

| ID | Description | Perspectives | Impact | Status |
|----|-------------|-------------|--------|--------|
| D-01 | Characterization of kernel coupling scope | code-tracer, integration-mapper | LOW | RESOLVED |
| D-02 | Missing behavioral quantification (usage patterns across real recipes) | N/A (behavior-observer absent) | MEDIUM | OPEN |
| D-03 | Rate-limiting tier asymmetry between orchestrator recipes | integration-mapper, bottom-up | LOW | OPEN |

### D-01: Characterization of Kernel Coupling — RESOLVED

**Code-tracer claims:** "The entire recipe engine touches amplifier-core through exactly one capability: `coordinator.get_capability('session.spawn')` at executor.py:1559. All other behavior is self-contained."

**Integration-mapper claims:** "The recipe executor accesses 9+ coordinator capabilities" and is "the widest module in the ecosystem."

**Resolution:** These claims are compatible, not contradictory. The code-tracer scoped its claim specifically to formal agent execution capability (one `get_capability` call). The integration-mapper counted ALL coordinator access surfaces including `getattr()` lookups, config reads, hooks emission, and mount registration. Both are factually correct at their stated scope. The synthesized view: one formal capability for agent execution, but 9+ informal access surfaces total.

### D-02: Missing Behavioral Quantification — OPEN

**What is missing:** The behavior-observer produced no artifacts in any investigation pass. We lack:
- Quantitative feature usage statistics across real recipes (which features are production-critical vs. rarely-used)
- Anti-pattern catalog from real-world recipe authoring
- Comparison of documented patterns vs. actual patterns in the wild

The bottom-up recipe analysis partially fills this gap (it cataloged 6 real recipes) but focused on structural connections, not behavioral usage patterns.

**Impact:** MEDIUM — without usage frequency data, we cannot confidently rank which execution paths most need hardening.

**Resolution needed:** A behavior-observer pass reading 10+ recipe YAML files across the ecosystem to catalog actual feature usage patterns.

### D-03: Rate-Limiting Tier Asymmetry — OPEN

**Integration-mapper claims:** Three independent rate-limiting tiers exist and their interaction is unknown.

**Bottom-up analysis observes:** Only `ecosystem-activity-report` uses `orchestrator.config.min_delay_between_calls_ms`; `amplifier-ecosystem-audit` does not, despite similar multi-repo API exposure.

Neither perspective explains why. Possible explanations: different reliability requirements, different API call volumes, or an incomplete port of the pattern. Without execution-based testing, this asymmetry cannot be resolved.

---

## Open Questions

### OQ-01: Who registers `session.spawn` and when? (HIGH)
Both top-down agents flagged this. `executor.py:1559` consumes it, nobody in the recipe module registers it. Likely registered by the app layer (`amplifier-foundation` CLI startup). A startup dependency ordering bug could silently disable all agent steps.
**Resolution:** Search `register_capability.*session.spawn` across the full ecosystem.

### OQ-02: What is the actual data loss surface during checkpoint-trimmed resume? (HIGH)
Both agents identified the risk (C-06). Source code confirms `_CHECKPOINT_TRIM_THRESHOLD_BYTES = 100_000` (executor.py:42). When a >100KB value is trimmed to a placeholder and the recipe is later resumed, `substitute_variables()` silently injects the placeholder into prompts. No verification exists of whether this occurs in production.
**Resolution:** Write a test that creates a recipe with a >100KB step output, saves a checkpoint, resumes, and verifies what downstream steps receive.

### OQ-03: What happens when parallel foreach tasks hit approval gates? (HIGH)
Both agents flagged this as "undefined behavior" (C-07). `asyncio.gather()` with `return_exceptions=False` would raise on first `ApprovalGatePausedError` and cancel remaining tasks. No execution-based verification exists.
**Resolution:** Execution-based test with a parallel foreach over 2+ sub-recipes each containing an approval gate.

### OQ-04: How do the three rate-limiting tiers interact? (MEDIUM)
Integration-mapper identified three independent tiers (F-11). Bottom-up analysis confirmed the asymmetry (D-03). Do they stack multiplicatively? Does sub-recipe inheritance override or merge?
**Resolution:** Trace rate limiter initialization in `execute_recipe()` and verify behavior when both recipe-level and orchestrator-level configs are present.

### OQ-05: Does the inline routing fallback drift from the canonical implementation? (MEDIUM)
Both agents identified the dual-path provider resolution (C-08). The inline fallback at executor.py:1706-1746 does "flexible provider name matching" that may differ from `amplifier_hooks_routing.resolver`.
**Resolution:** Diff the inline implementation against the canonical resolver for behavioral equivalence.

### OQ-06: Is the `_precomputed` convention documented anywhere? (LOW)
Integration-mapper and bottom-up analysis both identified this as an optimization convention (F-13). No documentation or schema validation found.
**Resolution:** Search documentation and recipe guides for `_precomputed` references.

### OQ-07: Does the checkpoint-approval two-phase write actually cause gate skipping? (MEDIUM)
Integration-mapper identified the theoretical risk (F-14). No crash testing or atomicity verification has been performed.
**Resolution:** Instrument the approval gate write path and test with simulated crash between the two writes.

---

## Recommended Next Steps

1. **Run behavior-observer pass** (HIGH priority) — Read 10+ real recipe YAML files across the ecosystem to quantify feature usage and identify anti-patterns. This fills the missing third perspective (D-02).

2. **Execution-based verification of OQ-02** (HIGH priority) — Test checkpoint trimming + resume with large step outputs to determine if data corruption is theoretical or practical.

3. **Execution-based verification of OQ-03** (HIGH priority) — Test parallel foreach + approval gate interaction to determine actual runtime behavior.

4. **Trace `session.spawn` registration** (HIGH priority) — Follow OQ-01 to map the boot-time capability registration sequence.

5. **Abstract MODULES.md access** (MEDIUM priority) — The 3 independent fetch mechanisms (F-07) are the tightest coupling in the subsystem. An `amplifier:docs/MODULES.md` @-mention would align with existing patterns.

6. **Audit observability coverage** (MEDIUM priority) — Compare the 6 emitted event types against the integration-mapper's list of error-prone boundaries to quantify the observability gap (F-15).
