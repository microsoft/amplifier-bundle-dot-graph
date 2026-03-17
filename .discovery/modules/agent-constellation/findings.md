# Synthesized Findings: Agent Constellation

## Consensus Findings

### 1. Triplicate Investigation Design
The 3 investigation agents are explicitly designed with complementary blind spots:
- code-tracer (HOW): misses emergent patterns and boundary effects
- behavior-observer (WHAT): misses causation, only runs at deep fidelity
- integration-mapper (WHERE/WHY): misses implementation detail
discovery-synthesizer triangulates from all 3 perspectives.
**Confidence: HIGH** — agent definitions confirm this explicitly.

### 2. File System as the ONLY Cross-Agent Coordination Mechanism
Agents communicate ONLY through the file system. No direct calls, no shared memory.
Code-tracer writes to `agents/code-tracer/`, integration-mapper to `agents/integration-mapper/`.
Synthesizer reads ALL files in `agents/*/`.
This design choice provides isolation but creates implicit path coupling.
**Confidence: HIGH** — traced all I/O paths in recipe.

### 3. No Fiat Reconciliation — Cardinal Rule
The discovery-synthesizer has an explicit cardinal rule: "Never reconcile discrepancies by fiat."
If agents disagree, the discrepancy is documented in findings.md under "Open Discrepancies."
This is a quality property enforced at the agent definition level, not the recipe level.
**Confidence: HIGH** — directly stated in agent prompt.

### 4. 7 Agents, 2 Distinct Groups
General DOT agents (dot-author, diagram-reviewer) are for ad-hoc tasks, NOT in the discovery pipeline.
Discovery pipeline agents (prescan + 3 investigation + synthesizer) form a separate group.
**Confidence: HIGH** — behavior YAML files (dot-core vs dot-discovery) confirm separation.

### 5. Synthesizer Runs in a Quality Gate Loop
The synthesizer is special: it runs up to 3 times per module with validation feedback.
After Phase E fix, this is properly implemented as a while loop with `max_while_iterations: 3`.
Other investigation agents run exactly once.
**Confidence: HIGH** — verified from recipe structure.

## Open Discrepancies

### Discrepancy A: Synthesizer file read scope
Code-tracer: prompt says "read all agent artifacts"
Integration-mapper: unclear if ALL files or just specific filenames (findings.md, diagram.dot)
**Unresolved:** The synthesizer's actual file reading scope depends on runtime behavior.

### Discrepancy B: General agents' relationship to discovery agents
Integration-mapper noted dot-author and diagram-reviewer could polish discovery outputs.
Code-tracer found no formal handoff mechanism between them.
**Unresolved:** Whether these agents are meant to be used post-discovery is not specified in the pipeline.
