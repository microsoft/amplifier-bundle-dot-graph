---
name: dot-patterns
description: Use when you need copy-paste DOT templates for common diagram types — start from a working pattern rather than blank canvas
---

# DOT Pattern Templates

## Overview

Ready-to-use DOT templates for the most common diagram types. Each template is complete, renders correctly, and demonstrates the right shape vocabulary and layout choices. Copy, rename nodes, adjust labels.

**Core principle:** Start from a working pattern. Blank canvas invites bad defaults. Templates encode proven shape vocabulary, layout direction, and structural choices.

## Pattern Selection

How to choose the right template:

```dot
digraph pattern_selection {
    rankdir=TB
    node [shape=diamond style="rounded,filled" fillcolor="#FFF9C4" fontname="Helvetica"]
    edge [fontname="Helvetica" fontsize=10]

    Q1 [label="Has states\nwith transitions?"]
    Q2 [label="Hierarchical\nlayers/tiers?"]
    Q3 [label="Parallel\nbranches?"]
    Q4 [label="Step-by-step\nflow?"]

    node [shape=box style="rounded,filled" fillcolor="#E8F0FE"]
    SM   [label="State Machine"]
    LA   [label="Layered Architecture"]
    FOFI [label="Fan-Out / Fan-In"]
    DAG  [label="DAG / Workflow"]
    LEG  [label="Add a Legend"]

    Q1 -> SM   [label="yes"]
    Q1 -> Q2   [label="no"]
    Q2 -> LA   [label="yes"]
    Q2 -> Q3   [label="no"]
    Q3 -> FOFI [label="yes"]
    Q3 -> Q4   [label="no"]
    Q4 -> DAG

    node [shape=note style="filled" fillcolor="#F0F4C3"]
    NOTE [label="Using color?\nAdd a Legend"]
    DAG  -> NOTE [style=dashed]
    LA   -> NOTE [style=dashed]
}
```

---

## Template 1: DAG / Workflow

Use for pipelines, CI/CD flows, processing steps, data pipelines.

```dot
digraph workflow {
    label="Workflow Title"
    labelloc=t
    rankdir=LR
    node [shape=box style="rounded,filled" fillcolor="#E8F0FE" fontname="Helvetica"]
    edge [fontname="Helvetica" fontsize=10 color="#666666"]

    Start  [label="Start" shape=ellipse fillcolor="#C8E6C9"]
    StepA  [label="Step A"]
    StepB  [label="Step B"]
    StepC  [label="Step C"]
    Done   [label="Done" shape=ellipse fillcolor="#FFCDD2"]

    Start -> StepA
    StepA -> StepB [label="on success"]
    StepA -> StepC [label="on failure" style=dashed color="#E57373"]
    StepB -> Done
    StepC -> Done
}
```

---

## Template 2: State Machine

Use for lifecycle states, order status, connection states, document workflows.

```dot
digraph state_machine {
    label="State Machine Title"
    labelloc=t
    rankdir=LR
    node [shape=box style="rounded,filled" fillcolor="#E8F0FE" fontname="Helvetica"]
    edge [fontname="Helvetica" fontsize=10]

    // Initial state marker
    _start [shape=point width=0.2 fillcolor=black]

    // States
    Idle      [label="Idle"]
    Active    [label="Active"]
    Paused    [label="Paused"]
    Terminal  [label="Terminal" shape=doublecircle fillcolor="#FFCDD2"]

    // Transitions
    _start -> Idle
    Idle   -> Active  [label="start"]
    Active -> Paused  [label="pause"]
    Active -> Terminal [label="complete"]
    Paused -> Active  [label="resume"]
    Paused -> Terminal [label="cancel"]
}
```

---

## Template 3: Layered Architecture

Use for system architecture, n-tier applications, domain boundaries.

```dot
digraph layered_arch {
    label="System Architecture"
    labelloc=t
    rankdir=TB
    compound=true
    node [fontname="Helvetica" style="rounded,filled"]
    edge [fontname="Helvetica" fontsize=10]

    subgraph cluster_presentation {
        label="Presentation Layer"
        style=filled fillcolor="#E3F2FD"
        node [fillcolor="#BBDEFB"]
        WebUI  [label="Web UI"]
        MobileUI [label="Mobile UI"]
    }

    subgraph cluster_api {
        label="API Layer"
        style=filled fillcolor="#E8F5E9"
        node [fillcolor="#C8E6C9"]
        Gateway [label="API Gateway"]
        Auth    [label="Auth Service"]
    }

    subgraph cluster_domain {
        label="Domain Layer"
        style=filled fillcolor="#FFF9C4"
        node [fillcolor="#FFF59D"]
        CoreSvc [label="Core Service"]
        Events  [label="Event Bus"]
    }

    subgraph cluster_data {
        label="Data Layer"
        style=filled fillcolor="#FCE4EC"
        node [fillcolor="#F8BBD9"]
        DB    [label="Database" shape=cylinder]
        Cache [label="Cache" shape=cylinder]
    }

    WebUI    -> Gateway [lhead=cluster_api]
    MobileUI -> Gateway [lhead=cluster_api]
    Gateway  -> CoreSvc [lhead=cluster_domain]
    Auth     -> CoreSvc [lhead=cluster_domain]
    CoreSvc  -> DB      [lhead=cluster_data]
    CoreSvc  -> Cache   [lhead=cluster_data]
}
```

---

## Template 4: Fan-Out / Fan-In

Use for parallel processing, scatter-gather, map-reduce, worker pools.

```dot
digraph fan_out_fan_in {
    label="Parallel Processing"
    labelloc=t
    rankdir=LR
    node [shape=box style="rounded,filled" fillcolor="#E8F0FE" fontname="Helvetica"]
    edge [fontname="Helvetica" fontsize=10 color="#666666"]

    Input    [label="Input"]
    Dispatch [label="Dispatch" shape=component fillcolor="#C8E6C9"]

    subgraph { rank=same; WorkerA; WorkerB; WorkerC }
    WorkerA [label="Worker A"]
    WorkerB [label="Worker B"]
    WorkerC [label="Worker C"]

    Collect  [label="Collect" shape=component fillcolor="#FFCDD2"]
    Output   [label="Output"]

    Input    -> Dispatch
    Dispatch -> WorkerA
    Dispatch -> WorkerB
    Dispatch -> WorkerC
    WorkerA  -> Collect
    WorkerB  -> Collect
    WorkerC  -> Collect
    Collect  -> Output
}
```

---

## Template 5: Legend

Add to any diagram that uses color or non-obvious shapes.

```dot
digraph with_legend {
    label="Diagram With Legend"
    labelloc=t
    rankdir=LR
    node [shape=box style="rounded,filled" fontname="Helvetica"]
    edge [fontname="Helvetica" fontsize=10]

    // Main diagram nodes
    SvcA [label="Service A" fillcolor="#E8F0FE"]
    SvcB [label="Service B" fillcolor="#E8F0FE"]
    DB   [label="Database"  shape=cylinder fillcolor="#FCE4EC"]
    Ext  [label="External"  shape=parallelogram fillcolor="#FFF9C4"]

    SvcA -> SvcB
    SvcB -> DB
    Ext  -> SvcA

    // Legend cluster
    subgraph cluster_legend {
        label="Legend"
        style=filled fillcolor="#F5F5F5"
        node [width=1.5]

        L_svc [label="Service"   shape=box         fillcolor="#E8F0FE"]
        L_db  [label="Data Store" shape=cylinder    fillcolor="#FCE4EC"]
        L_ext [label="External"  shape=parallelogram fillcolor="#FFF9C4"]

        L_svc -> L_db  [style=invis]
        L_db  -> L_ext [style=invis]
    }
}
```

---

## Template Checklist

Before submitting a diagram created from a template:

- [ ] Title set via `label=` and `labelloc=t` on the graph
- [ ] All node IDs replaced with meaningful names
- [ ] All `label=` values updated to real content
- [ ] Shape vocabulary matches what the node actually is (service, store, decision, etc.)
- [ ] Color is consistent and a legend is included if color carries meaning
- [ ] Diagram renders without errors: `dot -Tsvg diagram.dot > /dev/null`
