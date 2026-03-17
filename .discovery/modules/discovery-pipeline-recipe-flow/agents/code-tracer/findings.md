# Code-Tracer Findings: Discovery Pipeline Recipe Flow

## Recipes Traced
- `recipes/discovery-pipeline.yaml` (outer orchestrator, 442 lines)
- `recipes/discovery-investigate-topic.yaml` (per-topic sub-recipe, 116 lines)
- `recipes/discovery-synthesize-module.yaml` (synthesis quality gate, 152 lines)

## Key Finding 1: 3-Stage Outer Pipeline with Approval Gate
`discovery-pipeline.yaml` has 3 stages:
1. **scan** (3 steps: change-detect + structural-scan + topic-select)
   - `topic-select` dispatches `dot-graph:discovery-prescan` agent
   - Ends with `approval_gate: required: true` — human must approve topics
2. **investigate** (2 steps: prepare-topics + investigate-topics)
   - `investigate-topics` uses `foreach: "{{topics}}"` + `type: "recipe"` pointing to sub-recipe
   - `@dot-graph:recipes/discovery-investigate-topic.yaml`
3. **synthesize** (4 steps: reconcile-modules + assemble + final-validate + update-metadata)
   - `reconcile-modules` is another foreach recipe loop over topics

## Key Finding 2: Incremental Run Detection (change-detect step)
Steps compare `current_commit` (git HEAD) vs `last_commit` (stored in `last-run.json`).
- If same: tier = "skip" (entire pipeline skips via conditions)
- If diff: tier = "incremental" (only changed files scope)
- If no prior run: tier = "full"
Conditions: `condition: "{{change_result.tier}} != 'skip'"` gates structural-scan and topic-select.

## Key Finding 3: Sub-Recipe foreach Loop
```yaml
- id: "investigate-topics"
  type: "recipe"
  foreach: "{{topics}}"
  as: "topic"
  recipe: "@dot-graph:recipes/discovery-investigate-topic.yaml"
```
Each topic dispatches an independent sub-recipe execution.
At standard fidelity: 2 agents per topic (code-tracer + integration-mapper).

## Key Finding 4: Quality Gate Loop (synthesize-module.yaml)
Fixed structure (after Phase E bugs fixed):
```yaml
- id: "quality-gate"
  type: "bash"
  command: "true"         # no-op; while_steps runs instead
  while_condition: "true"
  break_when: "{{quality_check.quality_passed}} == true"
  max_while_iterations: 3
  update_context:
    _validation_errors: "{{quality_check.validation_errors}}"
  steps:
    - id: synthesize    # agent
    - id: validate      # bash
    - id: check-quality # bash
```
Max 3 synthesis+validate iterations per module.

## Key Finding 5: Bugs Found During Phase E
**Bug 1:** `prescan(repo_path=repo_path)` — module not callable, fixed to `prescan.prescan_repo(repo_path)`
**Bug 2:** `assemble(output_dir, topics)` — module not callable + wrong API, fixed to `assemble.assemble_hierarchy(manifest, output_dir)` with proper manifest
**Bug 3:** discovery-investigate-topic.yaml default `topic: {}` caused validation errors — fixed to typed defaults
**Bug 4:** `loop_back_to: "synthesize"` — invalid Step field, recipe failed to load — fixed by restructuring as while loop
**Bug 5:** `max_iterations: 3` — wrong field name, should be `max_while_iterations: 3`
**Issue 6:** Agent bundle references (`dot-graph:...`) not found via recipe framework — requires full Amplifier session with bundle configured
