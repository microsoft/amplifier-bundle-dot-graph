---
name: dot-syntax
description: Use when writing or reading DOT/Graphviz code and needing quick syntax reference — node declarations, edge syntax, attributes, subgraphs, HTML labels, and common gotchas
---

# DOT Syntax Quick Reference

## Overview

Fast lookup for DOT graph description language syntax. Covers the constructs you'll use 90% of the time.

**Core principle:** DOT describes structure (what connects to what). Layout engines handle positioning. You never specify coordinates.

## Graph Declaration

```dot
digraph name { }          // directed graph (use ->)
graph name { }            // undirected graph (use --)
strict digraph name { }   // no multi-edges allowed
```

## Nodes

```dot
my_node                                    // implicit creation
my_node [label="Display Name" shape=box]   // explicit with attributes
my_node [label="Line 1\nLine 2"]           // multiline label
"node with spaces"                         // quoted ID for special chars
```

**ID rules:** `[a-zA-Z_][a-zA-Z_0-9]*` unquoted. Use quotes for spaces/special chars.

## Edges

```dot
A -> B                          // directed edge
A -> B [label="calls"]          // labeled edge
A -> B -> C                     // chain
A -> {B C D}                    // fan-out (A connects to B, C, and D)
A -> B [style=dashed color=red] // styled edge
```

## Attributes

```dot
// Defaults (apply to all subsequent nodes/edges)
node [shape=box style="rounded,filled" fillcolor="#E8F0FE" fontname="Helvetica"]
edge [color="#666666" fontsize=10]
graph [rankdir=TB nodesep=0.5]

// Per-element (override defaults)
my_node [shape=diamond fillcolor="#FFF9C4"]
A -> B [color=blue penwidth=2]
```

## Shapes Quick Table

| Shape | Description |
|-------|-------------|
| `box` / `rectangle` | Rectangle (default-ish) |
| `ellipse` | Oval (true default) |
| `circle` | Equal width/height ellipse |
| `diamond` | Decision / branch |
| `hexagon` | Process step |
| `cylinder` | Database / storage |
| `note` | Document with folded corner |
| `folder` | Folder tab shape |
| `parallelogram` | Skewed rectangle |
| `doublecircle` | Final state (state machines) |
| `plaintext` | No border (label only) |

## Subgraphs and Clusters

```dot
// Cluster — name MUST start with cluster_
subgraph cluster_group {
    label="Group Name"
    style=filled
    fillcolor="#F0F0F0"
    A; B; C
}

// Rank control — force nodes to same level
subgraph { rank=same; A; B; C }
// rank values: same | min | max | source | sink

// Edges between clusters (needs compound=true on graph)
digraph G {
    compound=true
    subgraph cluster_a { A }
    subgraph cluster_b { B }
    A -> B [ltail=cluster_a lhead=cluster_b]
}
```

## HTML Labels

Use `<...>` instead of `"..."` for the label value:

```dot
node [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
    <TR>
        <TD PORT="left">Left</TD>
        <TD PORT="right">Right</TD>
    </TR>
</TABLE>>]
```

Connect to ports: `A:left -> B:right`

Supported elements: `TABLE`, `TR`, `TD`, `FONT`, `BR`, `HR`, `IMG`, `<B>`, `<I>`, `<U>`

## Layout Engines

| Engine | Best for |
|--------|----------|
| `dot` | Hierarchical DAGs, flowcharts (default) |
| `neato` | Small undirected graphs, spring layout |
| `fdp` | Larger undirected graphs, force-directed |
| `sfdp` | Very large undirected graphs |
| `circo` | Circular layouts, ring topologies |
| `twopi` | Radial/hub-and-spoke layouts |

Use `dot` for most diagrams. Switch to `neato`/`fdp` when hierarchy doesn't matter.

## Common Gotchas

| Gotcha | Fix |
|--------|-----|
| Cluster not visible | Name must start with `cluster_` |
| Edges go wrong direction | Use `rankdir=LR` or `rankdir=TB` on graph |
| Node IDs with spaces fail | Quote the ID: `"my node"` |
| HTML label not rendering | Use `<...>` not `"..."` for label value |
| Undirected edge in digraph | Use `->` in digraph, `--` in graph only |
| Subgraph edge not crossing clusters | Set `compound=true` on outer graph |

## Render Commands

```bash
# SVG (best for docs — scalable, text-searchable)
dot -Tsvg input.dot -o output.svg

# PNG (for embedding in Markdown/presentations)
dot -Tpng input.dot -o output.png

# Validate syntax only (no output file)
dot -Tsvg input.dot > /dev/null

# Specify layout engine
neato -Tsvg input.dot -o output.svg
fdp -Tpng input.dot -o output.png
```
