# dot-graph Bundle Improvement Plan

## Goal

Evolve `amplifier-bundle-dot-graph` from a working investigation toolkit into a robust, user-facing product with reliable pipelines, optimized agents, and first-class investigation framing.

**Success criteria:**
- A user can type "investigate this codebase" and the bundle handles the rest — no recipe path knowledge required
- The quick pipeline always produces `overview.dot` as the primary navigation artifact
- Discovery runs complete without OOM kills on any reasonable hardware
- Investigation framing is a first-class feature users can choose deliberately
- All existing tests still pass (baseline: 1,347); new tests added for each change

**Out of scope (next cycle):** staleness detection / incremental re-runs, discovery→issues integration, cost estimation UI.

---

## Approach

All 12 improvements designed together, shipped as three parallel PRs. Workstream A is the dependency gate — B3 and B5 assume A2 is stable; B1, B2, B4 are fully independent. Workstream C begins after A and B merge.

| Workstream | Items | Est. effort |
|---|---|---|
| A: Reliability | 5 items — template bugs, overview.dot, subprocess wiring, double-injection, prescan schema | ~1 day |
| B: Quick wins | 5 items — model roles, diagram quality standards, orchestrator agent, methodology skill, entry point recipe | ~1–2 days |
| C: New capabilities | 1 item — lens/framing system | ~1 week |

---

## Workstream A: Reliability Fixes

### A1 — Resolver Step Pattern

**Files:** `recipes/deep/discovery-pipeline.yaml`, `recipes/deep/strategy-topdown.yaml`, `recipes/deep/strategy-bottomup.yaml`, `recipes/deep/discovery-combine.yaml`

Every pipeline/strategy gets a `resolve-context` Step 0 (bash, ~12 lines) that derives all paths in Python and outputs `{{ctx.output_dir}}` and `{{ctx.repo_path}}`. All downstream steps reference `{{ctx.*}}` instead of raw `{{var}}` defaults. The quick pipeline already does this via `change-detect` — normalize the pattern name and apply it everywhere.

**Rule for recipe authors:** Context defaults must be literal values. If a value depends on another context variable, resolve it in a bash step.

### A2 — `overview.dot` in Quick Pipeline Output

The quick pipeline's `summarize` step calls the architecture-writer agent to produce `overview.md` but emits no DOT. Add a follow-up step (or extend summarize) that runs the dot-author agent to produce a 10–15 node "system spine" diagram alongside `overview.md`. This is the "start here" artifact users expect.

Currently missing — verified absent from output directory.

### A3 — Subprocess Isolation Wiring

Add `spawn_mode: subprocess` to every agent step in:
- `discovery-investigate-topic.yaml`
- `discovery-synthesize-module.yaml`
- The deep pipeline's synthesize recipes

Bash steps stay in-process. ~8 lines changed total.

### A4 — Bundle Composition Cleanup

Remove the `@dot-graph:context/dot-awareness.md` line from `bundle.md`'s markdown body — it is already injected via `dot-core.yaml`'s `context.include`. Remove the `dot-core` include from `dot-discovery.yaml` (it is included by the `dot-graph.yaml` umbrella) and add the explanatory comment:

```yaml
# Requires dot-core — see dot-graph.yaml umbrella behavior
```

### A5 — Prescan Schema Alignment

Update `agents/discovery-prescan.md` (and its instructions file) to document the `[{name, slug, description}]` format that recipes actually consume. The `slug` field is load-bearing — it drives all directory creation — and is currently undocumented in the agent's contract.

---

## Workstream B: Quick Wins

### B1 — Model Role Corrections

Change the following agents from `model_role: coding` to `model_role: reasoning`:

| Agent | Current | Correct |
|---|---|---|
| `discovery-synthesizer` | `coding` | `reasoning` |
| `discovery-combiner` | `coding` | `reasoning` |
| `discovery-level-synthesizer` | `coding` | `reasoning` |
| `discovery-subsystem-synthesizer` | `coding` | `reasoning` |
| `discovery-overview-synthesizer` | `coding` | `reasoning` |

These agents do not generate code — they read multiple investigation artifacts and produce analytical synthesis. Also verify `diagram-reviewer` is `model_role: critique`.

### B2 — Diagram Quality Standards in Agent Instructions

Add two requirements to the shared diagram quality context file that all diagram-producing agents load:

1. *"If you use more than one edge style, your legend MUST include a row for each with its semantic meaning (e.g. `dashed = optional delegation`, `dotted = read-only access`)."*
2. *"Define your shape vocabulary in a comment block before assigning shapes to nodes. Do not reuse a shape for a different semantic role within the same diagram."*

### B3 — `discovery-orchestrator` Agent

New `fast`-model agent that translates "investigate this codebase" into the correct recipe invocation with resolved parameters. Responsibilities:

- Knows both recipe paths (quick vs deep) and when to use each
- Resolves `repo_path` from context or asks the user
- Invokes the `recipes` tool with correct context variables
- Does **not** coordinate agents directly — delegates entirely to the recipe

Added **first** in `dot-discovery.yaml`. The `discovery-awareness.md` delegation target changes from "the recipe" to "this agent."

### B4 — `parallax-methodology` Skill in the Bundle

Move/copy from workspace `.amplifier/skills/` into `skills/parallax-investigation/SKILL.md`. The bundle becomes self-contained — the methodology explaining why the investigation is structured the way it is travels with the bundle wherever it is composed.

### B5 — `recipes/discover.yaml` Entry Point

A thin top-level recipe with `mode: auto | quick | deep` that selects the appropriate sub-recipe. Auto-mode inspects repo size (file count from prescan) and routes to quick or deep. Removes the decision point for new users. ~30–40 lines.

`discover.yaml` exposes `lens` as a top-level context variable with `architecture` as default (prerequisite for Workstream C).

---

## Workstream C: New Capabilities

### C1 — Investigation Lens System

A `lens` context variable (default: `architecture`) that injects investigation framing into every agent prompt. Existing users see no behavior change — the default lens matches the current implicit framing.

**Built-in lenses:**

| Lens | Emphasis |
|---|---|
| `architecture` | Component organization, patterns, design (current implicit default) |
| `security` | Trust boundaries, input validation, credential handling, attack surfaces |
| `quality` | Tech debt, inconsistency, maintenance risk, anti-patterns |
| `onboarding` | Happy path, key abstractions, where to find things for newcomers |
| `debugging` | Observability, error handling, how to trace problems to root cause |

**Implementation:**

- `context/lenses/` directory with one `.md` file per lens (~3–5 sentences each)
- Each recipe that dispatches investigation agents includes a `{{lens_guidance}}` variable, populated from the lens file at pipeline start by a small bash resolver step
- Agent prompts get a leading `## Investigation Framing` block if `lens_guidance` is non-empty
- Users can pass free-text `lens` to define a custom framing (the resolver falls back to treating the value as inline guidance)

The `discover.yaml` entry point (B5) exposes `lens` as a top-level context variable — wired as part of B5 delivery.

**Failure behavior:** The pipeline always fails hard on agent failure. Partial recovery is explicitly out of scope. The current fail-fast behavior is correct and intentional.

---

## Testing Strategy

**Existing baseline:** 1,347 tests. All must pass before and after every workstream.

### Workstream A Tests

| Test | What it catches |
|---|---|
| Assert quick pipeline output directory never contains a literal `{{` character in any path | Resolver step regressions |
| Assert `overview.dot` exists in quick pipeline output after every run | A2 regression |
| Assert each agent step in `discovery-investigate-topic.yaml` declares `spawn_mode: subprocess` | A3 regression |
| Assert `dot-awareness.md` appears exactly once in the composed bundle system prompt | A4 double-injection regression |
| Assert `discovery-prescan` response JSON contains `slug` field on every topic object | A5 contract regression |

### Workstream B Tests

| Test | What it catches |
|---|---|
| Assert `model_role` for each of the 5 corrected agents equals `reasoning` | B1 regression |
| Assert `discovery-orchestrator` agent exists in `dot-discovery.yaml` agent list, listed first | B3 regression |
| Assert `skills/parallax-investigation/SKILL.md` exists and loads without error | B4 regression |
| Assert `recipes/discover.yaml` exists and is valid recipe YAML | B5 existence |
| Assert `discover.yaml` routes to quick recipe when `mode: quick` and deep when `mode: deep` | B5 routing logic |

### Workstream C Tests

| Test | What it catches |
|---|---|
| Assert `lens: architecture` (default) produces identical output to current behavior | C1 regression for existing users |
| Assert each built-in lens name resolves to a non-empty guidance string | C1 missing lens files |
| Assert lens context variable is present in agent prompt when a non-default lens is set | C1 injection logic |

---

## Execution Plan

Three PRs, one per workstream, opened in parallel for review.

**Dependency note:**

- B3 (orchestrator) assumes A2 is complete — the orchestrator links to `overview.dot` as the primary artifact
- B5 (`discover.yaml`) assumes the resolver pattern from A1 is stable and can be referenced
- B1, B2, B4 are fully independent of Workstream A and can ship first
- **Workstream C does not start until A and B are merged**

```
PR A (Reliability)  ──────────────────────────────────┐
PR B (Quick Wins)   ── B1, B2, B4 now / B3, B5 after A ┤── merge ──► PR C (Lens System)
```

Any workstream can be reviewed independently. No shared state between PRs outside the noted dependency gate.
