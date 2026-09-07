---
name: dot-analysis
description: Use when a diagram is the analysis instrument rather than the output — absorbs dot-graph-intelligence (cycles, reachability, diffs), dot-as-analysis (belief vs reality), parallax-investigation and architecture-overview-diagram.
---

# DOT Analysis

Diagrams as instruments: draw what you believe, verify it against the code, and let
the delta be the finding. Four reference files sit beside this one; load only the one
the task needs.

**Core principle:** completeness pressure is the mechanism. You cannot leave a box
disconnected without asking why, and you cannot draw a flow without tracing where it
actually goes.

## Pick the reference

| You need | Read | Absorbed from |
|----------|------|---------------|
| Programmatic structure answers — reachability, unreachable nodes, cycles, paths, critical path, subgraph extract, diff, stats | `reference/graph-intelligence.md` | `dot-graph-intelligence` |
| The belief-vs-reality reconciliation workflow — introspect, represent, reconcile, surface, plus the anti-rationalization table | `reference/reconciliation.md` | `dot-as-analysis` |
| Multi-agent, multi-pass investigation — triplicate teams, the no-fiat rule, wave structure, fidelity tiers, artifact layout | `reference/parallax-investigation.md` | `parallax-investigation` |
| The full README-level architecture overview workflow — 12 steps, hard diagram constraints, antagonistic review | `reference/architecture-overview-diagram.md` | `architecture-overview-diagram` |

Load with `read_file(skill_directory + "/reference/<file>.md")` — `skill_directory`
is returned by `load_skill`. The architecture-overview workflow also stays reachable
as the `/architecture-overview-diagram` command.

## Code answers structure; the LLM interprets it

Structural questions are code problems. Run them with the `dot_graph` tool's
`analyze` operation, then reason about what the answer means.

| Question | Operation |
|----------|-----------|
| Is B reachable from A? | `reachability` |
| Which nodes are stranded? | `unreachable` |
| Are there circular dependencies? | `cycles` |
| What is the bottleneck path? | `critical_path` |
| What changed between two versions? | `diff` |
| How large and dense is this? | `stats` |

Interpretation cues: cycles in a dependency graph are a design problem; unreachable
nodes are dead paths, orphans, or forgotten placeholders; edges far outnumbering nodes
means everything talks to everything.

## The reconciliation loop

1. **Introspect** — write down what you believe the system does, before reading code.
2. **Represent** — draw that belief in DOT. Floating nodes are the forcing function.
3. **Reconcile** — read the code, and mark each element believed / actual / status.
4. **Surface** — redraw to match reality. The delta is the finding report.

Do not resolve a disagreement by picking the more plausible answer. Record both
claims, give it an ID, and mark it OPEN — that is the no-fiat rule, and the
discrepancy is the investigation's most valuable output.

## Related

- Writing or fixing the DOT itself: `load_skill(skill_name="dot-authoring")`.
- A full codebase investigation run: delegate to `dot-graph:discovery-orchestrator`.
