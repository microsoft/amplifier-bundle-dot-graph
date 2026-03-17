# Synthesized Findings: Discovery Pipeline Recipe Flow

## Consensus Findings

### 1. 3-Stage Pipeline with Approval Gate
The outer pipeline has distinct stages with a human approval gate between Stage 1 and Stage 2.
Stage 1 produces topics; Stage 2 investigates; Stage 3 synthesizes.
The approval gate is mandatory (`required: true`) — the pipeline cannot proceed automatically.
**Confidence: HIGH** — directly verified from YAML structure.

### 2. Incremental Run Detection
Change detection uses git commit hashing (current HEAD vs stored last-run.json).
Three tiers: skip / incremental / full. Skip bypasses all investigation steps via conditions.
This is a sophisticated mechanism for large repos but has a blind spot:
prompt/agent changes don't trigger re-investigation.
**Confidence: HIGH** — code-tracer traced the git commands.

### 3. Quality Gate Loop (Fixed Architecture)
The synthesize-module sub-recipe uses a while loop with max 3 iterations.
The synthesizer receives validation errors as feedback and revises the diagram.
Before Phase E fix: `loop_back_to` field was invalid → recipe failed to load entirely.
After fix: `while_condition: "true"` + `break_when` + `max_while_iterations: 3`.
**Confidence: HIGH** — directly validated via recipe framework.

### 4. File-System as Cross-Agent Coordination
The pipeline uses the file system as the only coordination mechanism between agents.
Each stage reads from what the previous stage wrote. No in-memory passing between sub-recipes.
This is intentional (isolation) but means all agents need consistent path agreements.
**Confidence: HIGH** — traced all I/O paths.

### 5. Bundle Agent Resolution Requires Full Configuration
The recipe references agents as `dot-graph:discovery-prescan`, etc.
This requires the bundle to be registered in the Amplifier session configuration.
During Phase E integration test, this was NOT configured → recipe execution failed at Stage 1.
**Confidence: HIGH** — observed directly during execution attempt.

## Open Discrepancies

### Discrepancy A: Context injection safety
Code-tracer noted `{{topics}}` is substituted directly as a Python literal.
Integration-mapper noted this is an injection risk if slugs contain special characters.
**Unresolved:** No escaping/quoting observed. Risk level depends on topic slug validation.

### Discrepancy B: foreach parallelism
Code-tracer noted `foreach: "{{topics}}"` dispatches one sub-recipe per topic.
Integration-mapper asked if they run in parallel.
The recipe doesn't specify `parallel: true`, so they run sequentially.
**Semi-resolved:** Sequential by default. Parallel is possible but not used here.
