# Integration-Mapper: Agent Constellation

## Cross-Boundary Integration Points

### Boundary 1: Agent ↔ Recipe (dispatch protocol)
All 5 discovery agents are dispatched by the recipe engine via agent steps:
- `agent: "dot-graph:discovery-prescan"` — requires bundle namespace resolution
- Recipe passes context via `prompt:` Jinja2 template substitution
- Agent receives: topic.name, topic.slug, repo_path, output_dir
- Agent produces: files written to output_dir path

**Critical:** Agents are NOT called programmatically. The recipe's prompt IS the API contract. There is no function signature — only a natural language spec.

### Boundary 2: Agent ↔ Agent (indirect via file system)
Agents don't call each other directly. They communicate through files:
- discovery-code-tracer writes to `agents/code-tracer/`
- discovery-integration-mapper writes to `agents/integration-mapper/`  
- discovery-synthesizer READS from `agents/*/` → writes consensus to `modules/{slug}/`
This file-system-mediated handoff is the only cross-agent coordination.

### Boundary 3: Investigation Agents ↔ Quality Gate
The discovery-synthesizer is unique: it runs in a while loop (max 3 iterations).
Between iterations, `_validation_errors` are injected into its prompt.
The synthesizer doesn't know it's being retried — it reads `_validation_errors` and acts on it.

### Boundary 4: dot-author / diagram-reviewer ↔ Core Agents
`dot-author` and `diagram-reviewer` are general-purpose agents, not in the discovery pipeline.
They serve ad-hoc diagram creation and review tasks.
Overlap with discovery agents: discovery-synthesizer also produces DOT diagrams.
No formal handoff — they are parallel workflows with no coordination mechanism.

### Boundary 5: Agent ↔ Skills (knowledge injection)
Agents access skills via `@dot-graph:skills/` references in their prompts or via the `tool-skills` module. The skills are NOT embedded in agent prompts — they're referenced and loaded at runtime. This creates a dependency:
- Agent quality depends on skill availability at session time
- If a skill changes, agent behavior changes even without agent update

## Composition Effects

**Triplicate coverage design:** The 3 investigation agents are explicitly designed to have blind spots that others cover:
- code-tracer HOW: misses patterns and boundaries
- behavior-observer WHAT: misses causation and code detail
- integration-mapper WHERE/WHY: misses implementation detail
The synthesizer's value comes entirely from this designed incompleteness — it triangulates.

**Standard vs Deep fidelity impact:** At standard fidelity, behavior-observer is skipped. The synthesizer only sees 2 perspectives instead of 3. The findings.md "Open Discrepancies" section may be larger because the pattern-level evidence is missing.
