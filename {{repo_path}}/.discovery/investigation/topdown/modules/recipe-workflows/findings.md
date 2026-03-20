# Synthesis: Recipe Workflow Patterns

**Module:** Recipe Workflow Patterns (amplifier/recipes/ + dot-graph-bundle/recipes/)  
**Source perspectives:** Direct source examination of 16 recipe YAML files  
**Missing perspectives:** code-tracer, behavior-observer, integration-mapper (all dispatched; none produced artifacts)  
**Cross-reference:** recipe-orchestration synthesis (sibling module covering the execution engine)  
**Fidelity tier:** standard  
**Synthesis date:** 2026-03-19

---

## Executive Summary

Sixteen recipe YAML files across two repositories (6 amplifier, 10 dot-graph-bundle) totaling 11,345 lines represent the most complex declarative orchestration artifacts in this ecosystem. Direct source examination reveals five dominant structural patterns: orchestrator/worker pairs, foreach fan-out, staged approval pipelines, sub-recipe composition, and conditional execution. The amplifier recipes are an order of magnitude larger (avg 1,578 lines) than dot-graph recipes (avg 188 lines), reflecting different maturity stages and domain complexity. **No triplicate agents produced artifacts for this module**, so all findings derive from direct examination cross-referenced with the recipe-orchestration engine synthesis. Three significant patterns warrant further investigation: the model tier cost strategy (copy-pasted rather than centralized), the MODULES.md bypass (3 independent fetch mechanisms), and the rate-limiting tier asymmetry between structurally similar orchestrator recipes.

---

## Agent Artifact Status

| Agent | Artifacts Produced | Notes |
|-------|--------------------|-------|
| code-tracer | **None** | Directory exists, empty |
| behavior-observer | **None** | Directory exists, empty |
| integration-mapper | **None** | Directory exists, empty |

**Impact:** Without triplicate agent perspectives, this synthesis cannot provide multi-agent consensus or track inter-agent discrepancies. All findings are marked as direct-source examination with confidence levels based on evidence strength rather than agent convergence. Cross-references to the recipe-orchestration synthesis (which DID have agent input) provide partial multi-perspective validation.

---

## Findings

### F-01: Two Distinct Recipe Populations (HIGH confidence)

The repository contains two structurally distinct recipe populations:

| Property | Amplifier Recipes (6) | Dot-Graph Recipes (10) |
|----------|----------------------|----------------------|
| Total lines | 9,467 | 1,878 |
| Avg lines/recipe | 1,578 | 188 |
| Range | 590–3,021 | 112–380 |
| Domain | Ecosystem operations (audit, activity, document gen) | Codebase discovery (prescan, investigate, synthesize) |
| Execution style | Mixed flat + staged | Primarily staged |
| Maturity | v1.2–v8.1 (many iterations) | v1.0 (first generation) |

**Evidence:** `wc -l` on all recipe files; version fields in YAML headers; changelog comments.

### F-02: Orchestrator/Worker Pair — Dominant Composition Pattern (HIGH confidence)

Three orchestrator/worker pairs emerge across both repositories:

1. **Audit pair** (amplifier): `amplifier-ecosystem-audit.yaml` (590 lines, staged) → `repo-audit.yaml` (903 lines, flat) via foreach
2. **Activity pair** (amplifier): `ecosystem-activity-report.yaml` (1,487 lines, flat) → `repo-activity-analysis.yaml` (1,189 lines, flat) via foreach
3. **Discovery pipeline** (dot-graph): `discovery-pipeline.yaml` (176 lines, staged) → `strategy-topdown.yaml`/`strategy-bottomup.yaml` (377/380 lines, staged) → `discovery-investigate-topic.yaml`/`discovery-synthesize-module.yaml` (118/166 lines) via foreach

The pattern is: orchestrator handles discovery/enumeration + fan-out + aggregation; worker handles per-item processing. Context passing flows parent→child via the `context:` block. Output flows child→parent via output delta trimming (confirmed by recipe-orchestration synthesis C-02).

**Cross-reference:** Recipe-orchestration synthesis F-06, C-02, C-14.

### F-03: Foreach Fan-Out — Three Distinct Usage Modes (HIGH confidence)

Foreach loops appear across both repositories with three distinct usage modes:

1. **Over entities** (repos, topics): `ecosystem-activity-report.yaml:800` iterates over `{{active_repos.repos}}`; `strategy-topdown.yaml:263` iterates over `{{topics}}`
2. **Over data chunks**: `repo-activity-analysis.yaml:435` iterates over `{{commits_data.chunks}}` with `max_iterations: 100`
3. **Over pipeline stages**: `strategy-topdown.yaml:288` iterates over topics again for synthesis, after investigation

Mode 1 and 2 use `type: recipe` (sub-recipe) or direct agent steps. Mode 3 chains multiple foreach loops sequentially over the same collection for different processing phases.

**Evidence:** grep for `foreach:` across all recipe files.

### F-04: Staged Approval Pipelines — Two Complexity Tiers (HIGH confidence)

Staged recipes use approval gates at two distinct scales:

- **Single-gate**: `amplifier-ecosystem-audit.yaml` (1 gate after discovery, before audit fan-out); `discovery-pipeline.yaml` (1 gate after scan, before strategies)
- **Multi-gate pipeline**: `document-generation.yaml` (5 gates: after generation, structural validation, content validation, quality validation, finalization)

The multi-gate pattern in `document-generation.yaml` implements a structured BFS validation pipeline: `v0 → [structural] → v1 → [content checks parallel] → v2 → [quality checks parallel] → v3 → final`. Each gate allows human review before the next validation phase.

**Evidence:** grep for `approval:` in all recipe files; stage structure in document-generation.yaml.

### F-05: Model Tier Strategy — Copy-Pasted Convention (HIGH confidence)

Three amplifier recipes implement per-step model tiering for cost optimization:

| Tier | Model Pattern | Used For |
|------|---------------|----------|
| Fast | `claude-haiku-*` / `gpt-5-mini` | Parsing, classification, date handling |
| Standard | `claude-sonnet-*` / `gpt-5.4` | Analysis, synthesis, validation |
| Premium | `claude-opus-4-*` / `gpt-5.4` | Document generation (doc-gen only) |

Each recipe independently encodes this strategy with `provider_preferences` lists. There is no shared `model-tiers.yaml` or common include mechanism. Dot-graph recipes use NO model tier configuration — they rely on bundle-level defaults.

**Cross-reference:** Recipe-orchestration synthesis F-12.  
**Evidence:** grep for `model:` and `provider:` across recipe files.

### F-06: Conditional Execution — Widespread Branch Logic (HIGH confidence)

Conditions appear in 4 of 6 amplifier recipes (20+ condition expressions total). Common patterns:

- **Feature flags**: `condition: "{{include_community}} == 'true'"` (ecosystem-audit)
- **Data guards**: `condition: "{{commits_data.has_commits}} == 'true'"` (repo-activity)
- **Pass/fail gates**: `condition: "{{structural_issues.passed}} == false"` (document-generation)
- **Optimization branches**: `condition: "{{scope_check.needs_llm}} == 'true'"` (ecosystem-activity)

String equality (`== 'true'`/`== 'false'`) dominates over boolean conditions, reflecting the expression evaluator's custom truthiness rules (confirmed by recipe-orchestration C-10).

### F-07: File-Based Data Passing — Workaround Convention (HIGH confidence)

`document-generation.yaml` explicitly documents the pattern: "FILE-BASED DATA: Complex JSON passed via files, not template variables" and "AGENT-WRITES-FILE: Agents write document content directly to files." The recipe-orchestration synthesis identified this as a workaround for template-to-bash escaping fragility (F-10).

Amplifier recipes heavily use `working_dir` directories (`./ai_working/ecosystem-audit`, `./ai_working/analyses/`) for intermediate artifacts. Dot-graph recipes use `output_dir` patterns writing to `.discovery/` subdirectories.

### F-08: Changelog-Driven Development — In-File Version History (HIGH confidence)

Amplifier recipes embed extensive changelogs as YAML comments:

| Recipe | Versions Documented | Notable Pattern |
|--------|-------------------|-----------------|
| ecosystem-activity-report | 15+ versions (v1.4–v1.15.2) | Rate limiting evolved across 4 versions |
| document-generation | 8+ versions (v1–v8.1) | Added Design Intelligence feedback loop |
| repo-activity-analysis | 5+ versions (v1.7–v3.1) | Token-based chunking replaced truncation |
| outline-generation-from-doc | 6+ versions (v1.5–v1.6.1) | Classification logic refined 3 times |

Dot-graph recipes have no changelogs (v1.0 first generation). This asymmetry marks the maturity boundary between the two populations.

### F-09: Sub-Recipe Resolution — Two Path Styles (HIGH confidence)

Sub-recipes are referenced via two distinct styles:

1. **Relative path**: `recipe: "./repo-activity-analysis.yaml"` (amplifier recipes)
2. **@bundle:path**: `recipe: "@dot-graph:recipes/discovery-investigate-topic.yaml"` (dot-graph recipes)

The @bundle resolution uses the mention_resolver capability (confirmed by recipe-orchestration synthesis). Amplifier recipes do NOT use @bundle resolution despite being inside a bundle directory. Dot-graph recipes consistently use @bundle paths.

### F-10: Deep Nesting — Discovery Pipeline Reaches 4 Levels (MEDIUM confidence)

The dot-graph discovery pipeline achieves the deepest recipe nesting observed:

```
discovery-pipeline.yaml (orchestrator)
  → strategy-topdown.yaml (strategy, foreach topics)
    → discovery-investigate-topic.yaml (per-topic, dispatches agents)
    → discovery-synthesize-module.yaml (per-module synthesis)
      → [validation steps]
  → strategy-bottomup.yaml (strategy, foreach directories)
    → synthesize-level.yaml (per-level)
  → discovery-combine.yaml (merge top-down + bottom-up)
```

`recursion.max_depth: 4` and `max_total_steps: 500` in amplifier-ecosystem-audit.yaml confirms the engine supports this depth. The dot-graph pipeline's `max_depth: 3` is more conservative.

---

## Cross-Cutting Insights

### Insight 1: Recipe Complexity Correlates with Domain Interaction Width

Amplifier recipes interacting with external services (GitHub API, LLM providers, filesystem) are vastly more complex than dot-graph recipes that primarily dispatch agents. The `ecosystem-activity-report.yaml` (1,487 lines) handles pagination, rate limiting, date parsing, timezone detection, and file I/O — concerns absent from `discovery-investigate-topic.yaml` (118 lines) which delegates entirely to agent capabilities. This suggests recipe complexity is driven by imperative workarounds for external service interaction, not by the recipe orchestration model itself.

### Insight 2: Pattern Replication Without Abstraction

The model tier strategy (F-05), rate limiting configuration, retry patterns, and MODULES.md fetch mechanisms are all independently implemented per recipe. There is no shared include, template, or configuration inheritance mechanism. This creates a copy-paste maintenance burden: when the ecosystem-activity-report evolved its rate limiting through 4 versions (v1.10–v1.14), the ecosystem-audit recipe did not receive equivalent evolution. The recipe system's YAML format provides no import or mixin capability.

### Insight 3: Approval Gates Serve Fundamentally Different Purposes

Single-gate patterns (ecosystem-audit, discovery-pipeline) use approval as a "confirm scope before expensive work" checkpoint. Multi-gate patterns (document-generation) use approval as incremental quality gates in a validation pipeline. These are architecturally different: the first is a cost-control mechanism, the second is a quality-control workflow. Both use the same `ApprovalGatePausedError` mechanism (recipe-orchestration C-03), but the design intent diverges.

### Insight 4: Two Generations of Recipe Design

The amplifier recipes represent a first generation of recipe design: large monolithic files, extensive bash steps, in-file changelogs, relative path resolution, workaround accumulation. The dot-graph recipes represent a second generation: smaller focused files, deep composition via @bundle paths, minimal bash, no changelogs needed (first version). The boundary between generations aligns with the transition from "recipes as scripts" to "recipes as composable units."

---

## Discrepancy Register

| ID | Description | Source | Impact | Status |
|----|-------------|--------|--------|--------|
| D-01 | Rate limiting asymmetry between orchestrator recipes | Direct examination + recipe-orchestration D-03 | MEDIUM | OPEN |
| D-02 | Sub-recipe path resolution style divergence | Direct examination | LOW | OPEN |
| D-03 | Missing triplicate agent perspectives | Process gap | HIGH | OPEN |

### D-01: Rate-Limiting Tier Asymmetry — OPEN

**Observation:** `ecosystem-activity-report.yaml` uses BOTH recipe-level rate limiting AND `orchestrator.config.min_delay_between_calls_ms: 500`. `amplifier-ecosystem-audit.yaml` uses ONLY recipe-level rate limiting despite similar multi-repo API exposure.

**Possible explanations:** (1) Different API call volumes; (2) activity-report evolved through more rate-limiting issues (changelog shows v1.10–v1.14 rate-limiting evolution); (3) incomplete pattern port.

**Resolution needed:** Execution-based comparison of API call patterns between the two orchestrators. Or review of activity-report changelog to determine if orchestrator-level rate limiting addresses a specific failure mode absent in ecosystem-audit.

**Cross-reference:** Recipe-orchestration synthesis D-03.

### D-02: Sub-Recipe Path Resolution Divergence — OPEN

**Observation:** Amplifier recipes use relative paths (`./repo-activity-analysis.yaml`). Dot-graph recipes use @bundle paths (`@dot-graph:recipes/discovery-investigate-topic.yaml`). Both are valid but create different coupling characteristics: relative paths couple to filesystem layout; @bundle paths couple to bundle registration.

**Impact:** LOW — both work correctly. The divergence may reflect different authoring eras or intentional design choices.

**Resolution needed:** Clarification of whether @bundle paths are the recommended convention going forward.

### D-03: Missing Triplicate Agent Perspectives — OPEN

**Observation:** All three agent directories (code-tracer, behavior-observer, integration-mapper) exist but contain no artifacts. This synthesis is based entirely on direct source examination, not multi-perspective reconciliation.

**Impact:** HIGH — this synthesis lacks:
- Code-tracer perspective on execution paths through recipe YAML parsing
- Behavior-observer quantification of feature usage patterns across 16 recipes
- Integration-mapper analysis of cross-recipe data flow and boundary tensions

**Resolution needed:** Re-dispatch triplicate agents for this module, or accept this single-perspective synthesis with reduced confidence.

---

## Open Questions

### OQ-01: Why do amplifier recipes not use @bundle path resolution? (MEDIUM)
The amplifier bundle contains 6 recipes, yet sub-recipe references use relative paths. Is this intentional (recipes should be self-contained) or historical (written before @bundle resolution existed)?

### OQ-02: What is the actual cost differential of the model tier strategy? (MEDIUM)
`ecosystem-activity-report` claims "~10x cost reduction on simple parsing steps" (v1.15.0 changelog). No verification exists across the 3 recipes that implement this pattern. Is the savings actually realized?

### OQ-03: What prevents the pattern-replication problem from growing? (HIGH)
With no import/mixin mechanism in recipe YAML, every shared pattern (model tiers, rate limiting, retry config) is copied per recipe. As the recipe count grows, how does the ecosystem prevent configuration drift?

### OQ-04: Are dot-graph recipes inheriting rate limiting from somewhere? (LOW)
Dot-graph recipes contain NO rate limiting, retry, or model tier configuration. Are they relying on bundle-level or engine-level defaults? If so, what are those defaults?

---

## Recommended Next Steps

1. **Re-dispatch triplicate agents** (HIGH priority) — The empty agent directories represent a process failure. Code-tracer should trace YAML parsing paths, behavior-observer should catalog feature usage across all 16 recipes, and integration-mapper should map cross-recipe data flows.

2. **Investigate recipe abstraction mechanisms** (HIGH priority) — OQ-03 identifies the most significant architectural tension: pattern replication without abstraction. Determine if recipe includes, templates, or shared config blocks are feasible.

3. **Verify model tier cost claims** (MEDIUM priority) — OQ-02 could validate or refute a significant optimization pattern. Compare actual provider costs with and without tiering.

4. **Standardize sub-recipe path convention** (LOW priority) — D-02 identifies a style divergence that could be resolved with a documented convention.