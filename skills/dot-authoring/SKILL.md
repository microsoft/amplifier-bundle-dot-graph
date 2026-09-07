---
name: dot-authoring
description: Use when writing, fixing or reviewing a DOT/Graphviz diagram — absorbs dot-syntax, dot-patterns and dot-quality (syntax lookup, templates, the title/legend law, quality gate).
---

# DOT Authoring

One entry point for writing DOT/Graphviz by hand. Three reference files sit beside
this one; load only the one the task needs.

**Core principle:** DOT describes structure (what connects to what). Layout engines
handle positioning — you never specify coordinates.

## Pick the reference

| You need | Read | Absorbed from |
|----------|------|---------------|
| Syntax lookup — nodes, edges, attributes, clusters, HTML labels, layout engines, gotchas, render commands | `reference/syntax.md` | `dot-syntax` |
| A working starting template — DAG/workflow, state machine, layered architecture, fan-out/fan-in, legend | `reference/patterns.md` | `dot-patterns` |
| Quality enforcement before sharing or committing — checklist, line-count targets, anti-patterns, shape vocabulary, the 7-step gate | `reference/quality.md` | `dot-quality` |

Load with `read_file(skill_directory + "/reference/<file>.md")` — `skill_directory`
is returned by `load_skill`.

## The rules that apply to every diagram

> **NO DIAGRAM WITHOUT A TITLE, NO COLOR WITHOUT A LEGEND**

- Set `label=` and `labelloc=t` on the graph. An untitled diagram cannot be referenced.
- Any `fillcolor`/`color` in use means a `cluster_legend` subgraph must exist.
- Set `rankdir` explicitly. Do not rely on defaults.
- Shapes carry meaning: `box` = service/process, `cylinder` = data store,
  `diamond` = decision, `ellipse` = start/terminal, `parallelogram` = external,
  `note` = annotation, `folder` = group. Full table in `reference/quality.md`.
- Every node needs at least one edge. A floating node is a forgotten node.
- Draw the error paths, not just the happy path.
- Verify it renders: `dot -Tsvg diagram.dot > /dev/null`.

## Workflow

1. Choose a template from `reference/patterns.md` rather than starting blank.
2. Look up anything unfamiliar in `reference/syntax.md`.
3. Run the 7-step gate in `reference/quality.md` before sharing or committing.
4. For an independent PASS/WARN/FAIL verdict, delegate to `dot-graph:diagram-reviewer`
   — do not let the author review its own output.

## Related

- Structural questions about an existing graph (cycles, reachability, diffs) and
  diagram-driven investigation: `load_skill(skill_name="dot-analysis")`.
- Creation and editing at scale: delegate to `dot-graph:dot-author`.
