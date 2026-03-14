# DOT/Graphviz Infrastructure

You have access to DOT/Graphviz graph authoring, analysis, and intelligence capabilities.

## When to Use DOT

| Value Proposition | Why It Matters |
|-------------------|----------------|
| Dense representation | Encode complex structures in compact, parseable text |
| Reconciliation forcing function | Making relationships explicit surfaces contradictions |
| Multi-scale navigation | Same graph renders meaningfully at detail or overview level |
| Analysis substrate | Machines can query, transform, and reason over graph structure |
| Multi-modal bridge | Renders as images, text, or data — works across tools |
| Workflow visualization | Maps processes, pipelines, and state machines clearly |
| Investigation artifact | Captures findings in persistent, shareable, diffable form |

## Quick Shape Vocabulary

| Shape | Meaning | Use Case |
|-------|---------|----------|
| box | Process / component | Services, modules, steps |
| ellipse | Data / state | Nodes, data stores, states |
| diamond | Decision | Branch points, conditions |
| cylinder | Storage | Databases, file systems |
| folder | Group / namespace | Clusters, packages |
| circle / doublecircle | Start / terminal | FSM states |
| note | Annotation | Labels, callouts, caveats |

## Available Capabilities

**Agents**: `dot-author` (graph creation and editing), `diagram-reviewer` (quality review)
**Tools**: `dot_validate`, `dot_render`, `dot_setup`, `dot_analyze`
**Skills**: `dot-syntax`, `dot-patterns`, `dot-as-analysis`, `dot-quality`, `dot-graph-intelligence`

## Delegation

- **DOT authoring** (create, edit, refine diagrams): ALWAYS delegate to `dot-author`. It has authoritative knowledge of DOT syntax, layout algorithms, and graph intelligence patterns.
- **DOT quality review** (evaluate, audit, validate diagrams): ALWAYS delegate to `diagram-reviewer`. It provides independent, objective PASS/WARN/FAIL verdicts. Do NOT rely on `dot-author` to review its own output.
