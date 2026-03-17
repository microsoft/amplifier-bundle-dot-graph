# Code-Tracer Findings: Agent Constellation

## Agents Traced (7 total, all in agents/)

### Discovery Pipeline Agents (5)
1. **discovery-prescan.md** — Topic selector. One-shot agent, outputs JSON array of topics.
   Reads structural inventory, applies selection criteria. model_role: reasoning.
   Uses context: @dot-graph:context/discovery-prescan-instructions.md

2. **discovery-code-tracer.md** — HOW agent. Uses LSP + filesystem tools. Produces:
   findings.md, diagram.dot, unknowns.md. model_role: reasoning.
   "Cite every finding with file:line evidence." "Follow call chains through multiple files."

3. **discovery-behavior-observer.md** — WHAT agent. Examines 10+ instances.
   Deep fidelity only. Produces: findings.md, catalog.md, patterns.md, diagram.dot, unknowns.md.

4. **discovery-integration-mapper.md** — WHERE/WHY agent. Maps cross-boundary effects.
   "The most architecturally significant insights live at BOUNDARIES."
   Produces: integration-map.md, diagram.dot, unknowns.md.

5. **discovery-synthesizer.md** — Synthesis agent. Reads all 2-3 agent outputs per module.
   CARDINAL RULE: "Never reconcile discrepancies by fiat." Produces: diagram.dot, findings.md.
   Called repeatedly (up to 3×) by quality gate loop if DOT validation fails.

### General DOT Agents (2)
6. **dot-author.md** — General-purpose DOT diagram author. Creates diagrams from scratch.
   Applies dot-patterns, dot-syntax, dot-quality skills.

7. **diagram-reviewer.md** — Reviews existing DOT diagrams for quality/accuracy.
   Checks against dot-quality standards.

## Agent Roles in Triplicate Investigation Pattern
```
Topic X investigation (standard fidelity):
  code-tracer     → HOW things work (code paths)
  integration-mapper → WHERE/WHY things connect (boundaries)
  
Topic X investigation (deep fidelity):
  code-tracer
  behavior-observer → WHAT patterns exist (10+ instances)
  integration-mapper
  
Synthesis:
  discovery-synthesizer reads all agent outputs → consensus diagram
```

## model_role Distribution
- Most discovery agents: `model_role: reasoning` (complex analysis)
- dot-author, diagram-reviewer: (model_role unspecified, defaults to general)
