# DOT Quality Standards

Quality gates, shape vocabulary, color semantics, and anti-patterns for DOT diagrams.
Used by the `diagram-reviewer` agent and the `dot_validate` tool during automated validation.

---

## Line Count Targets

| Diagram Type | Target (lines) | Warn Above | Rationale |
|---|---|---|---|
| overview | 100–200 | 250 | High-level; too much detail defeats the purpose |
| detail | 150–300 | 400 | Full system view; use clusters to manage scale |
| inline | 10–40 | 60 | Embedded in docs; must stay scannable |
| quick sketch | any | 100 | Exploratory; no minimum, brevity encouraged |

---

## Node Count Guidelines

| Node Count | Assessment | Guidance |
|---|---|---|
| 1–10 | Fine | No special handling needed |
| 11–25 | Good | Add clusters to group related nodes |
| 26–40 | Approaching limit | Mandatory clusters; consider splitting into overview + detail |
| 41+ | Too many | Split diagram; one diagram cannot serve multiple purposes |

---

## Required Elements

### Always Required

| Element | Attribute | Example |
|---|---|---|
| Graph label | `label="..."` | `label="System Overview"` |
| Font name | `fontname="..."` | `fontname="Helvetica"` |
| Layout direction | `rankdir=...` | `rankdir=LR` |

### Required for >20 Nodes

| Element | Reason |
|---|---|
| Legend (`cluster_legend`) | Readers can't memorize shape/color semantics at scale |
| Clusters for logical groups | Prevents visual noise; establishes hierarchy |
| Consistent node ID prefix per cluster | `svc_`, `db_`, `ext_` — supports automated validation |

---

## General-Purpose Shape Vocabulary

| Shape | Meaning | Suggested Fill | When to Use |
|---|---|---|---|
| `box` (default) | Service / process | `#dae8fc` (blue) | Generic compute unit, agent, microservice |
| `ellipse` | Start / end marker | `#d5e8d4` (green) | Entry/exit points, terminal states |
| `diamond` | Decision / router | `#fff2cc` (yellow) | Conditional branching, pure routing (no LLM) |
| `cylinder` | Data store | `#f8cecc` (red-tint) | Database, cache, file system, queue |
| `hexagon` | Human gate | `#e1d5e7` (purple) | Approval required, human-in-the-loop |
| `component` | Fan-out (parallel) | `#dae8fc` (blue) | Dispatch to concurrent branches |
| `tripleoctagon` | Fan-in (collect) | `#dae8fc` (blue) | Gather parallel results |
| `parallelogram` | Tool / shell exec | `#fff2cc` (yellow) | Direct command execution, no LLM |
| `house` | Supervisor loop | `#ffe6cc` (orange) | Iterative retry or manager pattern |
| `folder` | Sub-pipeline | `#f5f5f5` (gray) | Nested workflow invocation |
| `note` | Annotation | `#ffffc0` (light yellow) | Collapsed cluster summary, inline comment |
| `point` | Invisible anchor | none | Initial state dot in state machines |

---

## Color Semantics

| Color | Hex | Meaning | Usage |
|---|---|---|---|
| Blue (default) | `#dae8fc` | Neutral / process | Standard service or agent node |
| Green | `#d5e8d4` | Success / healthy | Passing state, completed step, OK path |
| Red | `#f8cecc` | Error / failure | Failed step, error path, critical problem |
| Yellow | `#fff2cc` | Warning / decision | Branch point, caution, conditional logic |
| Orange | `#ffe6cc` | Data / transformation | Data flow node, ETL step, transformer |
| Purple | `#e1d5e7` | External / third-party | Outside system boundary, human actor |
| Gray | `#f5f5f5` | Inactive / placeholder | Disabled node, future work, legend entry |

---

## Edge Style Semantics

| Style | DOT Attribute | Meaning | When to Use |
|---|---|---|---|
| Solid | `style=solid` (default) | Synchronous call | Standard control flow, sync request |
| Dashed | `style=dashed` | Asynchronous / event | Async message, event-driven, fire-and-forget |
| Dotted | `style=dotted` | Weak dependency | Optional link, soft reference, can-reach |
| Bold | `style=bold` | Critical path | Hot path, must-not-fail, main data flow |
| Red arrow | `color=red` | Error / failure path | Exception route, dead-letter, fallback |

---

## Anti-Patterns

### Structural

| Anti-Pattern | Severity | Problem | Fix |
|---|---|---|---|
| Orphan node | ERROR | Disconnected node adds noise | Connect or remove |
| Undirected cycle | WARN | Ambiguous feedback loop | Add `constraint=false` or use dashed back-edge |
| Cluster with one node | WARN | Cluster overhead for no grouping benefit | Remove cluster or add nodes |
| Flat graph >25 nodes | ERROR | Unreadable without hierarchy | Add `subgraph cluster_` groupings |
| Cross-cluster edges without `ltail/lhead` | WARN | Edge routing ignores logical boundary | Add `ltail` / `lhead` attributes |
| Missing start/exit node | ERROR | Diagram has no clear entry or exit | Add `shape=ellipse` start and exit nodes |

### Style

| Anti-Pattern | Severity | Problem | Fix |
|---|---|---|---|
| Inconsistent fontname | WARN | Mixed fonts render badly across viewers | Set global `fontname` on graph |
| Hardcoded pixel sizes | WARN | Breaks layout engine hinting | Remove `width`/`height` unless required |
| RGB hex in label text | WARN | HTML-like color in plain label | Use `fontcolor` attribute instead |
| Too many fill colors (>7) | WARN | Color loses semantic meaning | Restrict to this document's color palette |
| Missing `style=filled` on colored node | ERROR | `fillcolor` has no effect without it | Add `style=filled` to all colored nodes |
| Bold font without semantic reason | INFO | Visual hierarchy misleading | Reserve bold for critical-path nodes only |
| shape=box on legend item for non-service | INFO | Legend shape mismatch confuses readers | Match legend shape to actual shape used |

### Naming

| Anti-Pattern | Severity | Problem | Fix |
|---|---|---|---|
| Generic IDs (`n1`, `a`, `node2`) | WARN | Unreadable diff and non-searchable | Use descriptive snake_case IDs |
| Inconsistent ID casing | WARN | `myService` vs `my_service` in same graph | Standardise on `snake_case` |
| Label duplicates ID exactly | INFO | Redundant; label should add human context | Either remove label or make it more descriptive |
| Cluster name missing `cluster_` prefix | ERROR | Graphviz silently ignores the subgraph box | Rename to `subgraph cluster_<name>` |

---

## Quality Gate Thresholds

| Check | PASS | WARN | FAIL |
|---|---|---|---|
| Line count vs type target | Within target | Up to warn threshold | Exceeds warn threshold |
| Node count | ≤25 | 26–40 | >40 |
| Required attributes present | All 3 present | 2 of 3 | Missing `fontname` or `rankdir` |
| Orphan nodes | 0 | — | ≥1 |
| Cluster usage (if >20 nodes) | Clusters present | — | No clusters |
| Legend present (if >20 nodes) | `cluster_legend` found | — | Missing |
| Color palette compliance | All fills in palette | 1–2 extras | >2 outside palette |
| Naming convention | All IDs snake_case | ≤3 violations | >3 violations |

---

## The Reconciliation Principle

DOT diagrams in the Amplifier ecosystem are **reconciliation artifacts** — they are not documentation added after the fact but the primary medium through which system understanding is verified and communicated.

A diagram reconciles three things simultaneously:

1. **Intent** — what the designer believed the system does
2. **Implementation** — what the code actually does
3. **Audience** — what the reader needs to understand to act

When a DOT diagram and the code diverge, that divergence is a signal: either the code drifted from intent, or the diagram was never grounded in reality. The quality standards in this document exist to make diagrams trustworthy enough to serve as that reconciliation surface.

**Implication for validation:** Automated quality checks (line counts, node counts, required attributes) catch *form* violations. Human or agent review is required to catch *semantic* violations — diagrams that are syntactically perfect but factually wrong about the system they describe.
