# Integration-Mapper: Discovery Pipeline Recipe Flow

## Cross-Boundary Integration Points

### Boundary 1: Outer Recipe ↔ Recipe Framework Engine
- **Context threading:** `change_result` set in Stage 1 is referenced in Stage 3 via `{{change_result.output_dir}}` and `{{change_result.current_commit}}`. The recipe engine must propagate context across stages.
- **Approval gate:** Pauses execution between Stage 1 and Stage 2. The recipe engine must persist the `topics` context for the approval callback to resume.
- **foreach + recipe:** `type: "recipe"` with `foreach: "{{topics}}"` creates one session per topic. Each sub-session gets `topic`, `fidelity`, `repo_path`, `output_dir` from the outer context.

### Boundary 2: Outer Recipe ↔ Sub-Recipes
Two sub-recipe boundaries:
- `@dot-graph:recipes/discovery-investigate-topic.yaml` — invoked per topic
- `@dot-graph:recipes/discovery-synthesize-module.yaml` — invoked per topic
Both use `@dot-graph:` bundle-relative paths, requiring the bundle to be registered.

### Boundary 3: Recipe ↔ Bash Steps (Python embedded scripts)
All bash steps use embedded `python3 - <<'EOF'` heredocs with Jinja2 variable substitution.
- `{{topics}}` in the assemble step embeds the Python list literal directly into Python code. This is a potential injection surface if topics contain special characters.
- `{{change_result.output_dir}}` embeds a path string — also risk if path contains quotes.

### Boundary 4: Recipe ↔ File System (output_dir contract)
The pipeline writes to `.discovery/` under `repo_path`:
- `modules/{slug}/agents/{agent-name}/` — investigation outputs  
- `modules/{slug}/diagram.dot` — synthesis output
- `overview.dot`, `manifest.json`, `last-run.json` — final outputs
This file-based handoff is the coordination mechanism between sub-recipe outputs and the outer pipeline.

### Boundary 5: Recipe ↔ Git (incremental detection)
The change-detect step uses `git rev-parse HEAD` and `git diff --name-only` for commit-based incremental detection. Failure is graceful (falls back to "full" tier). No network calls — purely local git operations.

## Composition Effects

**Full pipeline composition:** The outer recipe is a meta-orchestrator. It doesn't run agents itself (except topic-select). It coordinates 3 types of delegations:
1. Agent step (discovery-prescan) for scoping
2. Recipe loop (investigate-topic) for parallel investigation  
3. Recipe loop (synthesize-module) for quality-gated synthesis
This creates a 3-level hierarchy: outer pipeline → sub-recipes → individual agents.

**Incremental correctness issue:** The incremental detection skips investigation if files haven't changed, but there's no check on agent model changes or prompt changes. If prompts change but code doesn't, the pipeline won't re-investigate.
