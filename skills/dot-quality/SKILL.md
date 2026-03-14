---
name: dot-quality
description: Use when enforcing quality standards on DOT diagrams — checking completeness, structure, and visual clarity before sharing or committing
---

# DOT Quality Standards

## Overview

Every DOT diagram makes structural claims. Those claims must be verifiable, complete, and unambiguous. Quality enforcement ensures diagrams communicate correctly — not just render correctly.

**Core principle:** A diagram that renders without errors can still be wrong. Structural claims require titles, color requires legends, and shapes must match their semantic meaning.

---

## The Iron Law

> **NO DIAGRAM WITHOUT A TITLE, NO COLOR WITHOUT A LEGEND**

These are not suggestions. A diagram without a title is anonymous — reviewers cannot reference it. A diagram with unexplained color is ambiguous — different readers draw different conclusions.

---

## Quality Checklist

### Must Have — FAIL if missing

- [ ] Graph has a `label=` attribute set to a meaningful title
- [ ] `labelloc=t` is set (title appears at top, not bottom)
- [ ] Every node has either a meaningful ID or an explicit `label=`
- [ ] All edges convey accurate relationships (not aspirational or assumed)

### Should Have — WARN if missing

- [ ] `rankdir` is set explicitly (LR, TB, BT, or RL) — don't rely on defaults
- [ ] Default node and edge attributes are declared at the top with `node [...]` and `edge [...]`
- [ ] Shape vocabulary is consistent with the shape-meaning table below
- [ ] If any color is used, a `cluster_legend` subgraph documents all colors used
- [ ] Error and exception paths are drawn (not just the happy path)
- [ ] External dependencies are shown, even if simplified

### Nice to Have — INFO

- [ ] `fontname` is set consistently (Helvetica or similar sans-serif)
- [ ] `nodesep` and `ranksep` are tuned for readability
- [ ] Cluster fill colors are distinct from node fill colors
- [ ] A `// comment` explains any non-obvious structural choice

---

## Line Count Targets

| Diagram Type | Target | WARN at | FAIL at |
|-------------|--------|---------|---------|
| Overview / context | 30–80 | 120 | 200 |
| Architecture (detail) | 80–150 | 250 | 400 |
| Inline (single concept) | 10–30 | 50 | 80 |
| Quick sketch | 5–20 | 35 | 60 |

Diagrams that exceed WARN thresholds should be split into overview + detail files.

---

## Anti-Pattern Red Flags

| Flag | Problem | Fix |
|------|---------|-----|
| Floating node | Node with no edges — forgotten or placeholder | Connect it or remove it |
| Mystery color | Color used without legend entry | Add to legend or remove color |
| `label=""` | Empty label — invisible node | Set a meaningful label |
| Duplicate node IDs | Same ID used for different concepts | Rename to make IDs unique |
| All nodes same shape | Shape vocabulary not being used | Apply shape-meaning table |
| Edges without direction meaning | Arrow direction doesn't match data/control flow | Reverse or relabel edges |
| No title | Anonymous diagram — cannot be referenced | Add `label=` and `labelloc=t` |

---

## Shape Vocabulary Compliance

Shapes carry semantic meaning. Using the wrong shape creates ambiguity:

| Shape | Meaning | Misuse to Avoid |
|-------|---------|-----------------|
| `box` / `rectangle` | Service, process, component | Don't use for data stores |
| `cylinder` | Database, file store, queue | Don't use for services |
| `diamond` | Decision point, branch | Don't use for processes |
| `ellipse` | Start / end state, terminal | Don't use for services |
| `doublecircle` | Final/accepted state (FSM) | Reserve for state machines |
| `parallelogram` | External system, I/O | Don't use for internal services |
| `note` | Annotation, documentation node | Don't use for primary components |
| `component` | Fan-out / fan-in coordinator | Don't use for simple steps |
| `point` | Initial state marker (FSM) | Reserve for state machines only |
| `folder` | File group, repository | Don't use for services |

---

## The Quality Gate

Run this 7-step check before every diagram is shared, committed, or embedded in documentation:

1. **Render check** — `dot -Tsvg diagram.dot > /dev/null` — zero errors
2. **Title check** — `grep 'label=' diagram.dot` shows a non-empty title
3. **Color check** — if any `fillcolor` or `color` attribute is set, `cluster_legend` exists
4. **Shape check** — review each node shape against the Shape Vocabulary table
5. **Float check** — every node has at least one edge (incoming or outgoing)
6. **Path check** — error/failure paths are present, not just the happy path
7. **Size check** — line count is within target range for the diagram type
