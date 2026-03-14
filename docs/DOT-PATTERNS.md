# DOT Pattern Catalog

> Copy-paste patterns for common graph structures. Each pattern includes complete,
> runnable DOT code and "Use when" guidance.
>
> Render any example: `dot -Tsvg pattern.dot -o pattern.svg`

---

## Pattern 1: Simple DAG / Workflow

**Use when:** You need a left-to-right sequential pipeline — CI/CD stages, data
processing steps, or any workflow with a clear start and end.

```dot
digraph simple_workflow {
  rankdir=LR
  node [fontname="Helvetica", fontsize=12]

  start  [shape=ellipse, label="Start", style=filled, fillcolor=lightgreen]
  step1  [shape=box,     label="Fetch Data"]
  step2  [shape=box,     label="Process"]
  step3  [shape=box,     label="Validate"]
  done   [shape=ellipse, label="Done",  style=filled, fillcolor=lightblue]

  start -> step1 -> step2 -> step3 -> done
}
```

---

## Pattern 2: Conditional Branching

**Use when:** A decision point splits flow into two or more paths. Use a diamond
node as a pure router — it labels the question, edges label the answers.

```dot
digraph conditional_branch {
  rankdir=LR
  node [fontname="Helvetica", fontsize=12]

  input   [shape=box,     label="Input"]
  decide  [shape=diamond, label="Valid?"]
  process [shape=box,     label="Process"]
  reject  [shape=box,     label="Reject\n& Log"]
  done    [shape=ellipse, label="Done"]

  input   -> decide
  decide  -> process [label="Yes"]
  decide  -> reject  [label="No"]
  process -> done
  reject  -> done
}
```

---

## Pattern 3: Fan-Out / Fan-In Parallel

**Use when:** Work can be dispatched to independent workers concurrently, then
results collected. Use `component` shape to signal parallel dispatch and collect.

```dot
digraph fan_out_fan_in {
  rankdir=LR
  node [fontname="Helvetica", fontsize=12]

  dispatch [shape=component, label="Dispatch"]
  worker1  [shape=box,       label="Worker A"]
  worker2  [shape=box,       label="Worker B"]
  worker3  [shape=box,       label="Worker C"]
  collect  [shape=component, label="Fan-In\nCollect"]
  done     [shape=ellipse,   label="Done"]

  dispatch -> worker1
  dispatch -> worker2
  dispatch -> worker3
  worker1  -> collect
  worker2  -> collect
  worker3  -> collect
  collect  -> done
}
```

---

## Pattern 4: Layered Architecture

**Use when:** A system has clearly separated horizontal layers (presentation,
API, domain, data). Clusters visually enforce layer boundaries.

```dot
digraph layered_architecture {
  rankdir=TB
  compound=true
  node [fontname="Helvetica", fontsize=12]

  subgraph cluster_presentation {
    label="Presentation Layer"; style=filled; fillcolor=lightyellow
    web_ui [shape=box, label="Web UI"]
    mobile [shape=box, label="Mobile App"]
  }

  subgraph cluster_api {
    label="API Layer"; style=filled; fillcolor=lightcyan
    gateway [shape=box, label="API Gateway"]
    auth    [shape=box, label="Auth Service"]
  }

  subgraph cluster_domain {
    label="Domain Layer"; style=filled; fillcolor=lavender
    orders [shape=box, label="Order Service"]
    users  [shape=box, label="User Service"]
  }

  subgraph cluster_data {
    label="Data Layer"; style=filled; fillcolor=mistyrose
    db    [shape=cylinder, label="Primary DB"]
    cache [shape=cylinder, label="Cache"]
  }

  web_ui  -> gateway
  mobile  -> gateway
  gateway -> auth
  gateway -> orders
  gateway -> users
  orders  -> db
  users   -> db
  orders  -> cache
}
```

---

## Pattern 5: State Machine

**Use when:** A system has discrete states with named transitions. Use `point`
for the initial pseudo-state, `circle` for states, `doublecircle` for terminal.

```dot
digraph state_machine {
  node [fontname="Helvetica", fontsize=12]

  __init__ [shape=point]
  idle     [shape=circle,       label="Idle"]
  running  [shape=circle,       label="Running"]
  paused   [shape=circle,       label="Paused"]
  done     [shape=doublecircle, label="Done"]

  __init__ -> idle
  idle     -> running [label="start"]
  running  -> paused  [label="pause"]
  paused   -> running [label="resume"]
  running  -> done    [label="complete"]
  running  -> idle    [label="reset"]
}
```

---

## Pattern 6: Dependency Graph

**Use when:** Showing which components depend on which others, rendered so
lower-level foundations appear at the bottom and dependents rise above them.

```dot
digraph dependency_graph {
  rankdir=BT
  node [fontname="Helvetica", fontsize=12, shape=box]

  app       [label="Application"]
  service_a [label="Service A"]
  service_b [label="Service B"]
  lib_x     [label="Library X"]
  lib_y     [label="Library Y"]
  runtime   [label="Runtime"]

  service_a -> app
  service_b -> app
  lib_x     -> service_a
  lib_y     -> service_a
  lib_y     -> service_b
  runtime   -> lib_x
  runtime   -> lib_y
}
```

---

## Pattern 7: Legend

**Use when:** A diagram uses multiple shapes or edge styles that need explanation.
Place the legend in a `cluster_legend` subgraph so it renders as a boxed key.

```dot
digraph with_legend {
  rankdir=LR
  node [fontname="Helvetica", fontsize=12]

  // Main diagram
  api      [shape=box,      label="API Service"]
  store    [shape=cylinder, label="Data Store"]
  external [shape=ellipse,  label="External"]
  decision [shape=diamond,  label="Gate"]

  api -> store
  api -> external [style=dashed, label="async"]
  api -> decision

  // Legend — must be named cluster_legend for convention
  subgraph cluster_legend {
    label="Legend"; style=solid
    node [style=filled]
    l_svc  [shape=box,       label="Service",   fillcolor=white]
    l_db   [shape=cylinder,  label="Data Store", fillcolor=lightblue]
    l_ext  [shape=ellipse,   label="External",  fillcolor=lightyellow]
    l_dec  [shape=diamond,   label="Decision",  fillcolor=lightyellow]
    l_sync [shape=plaintext, label="——  sync"]
    l_asyn [shape=plaintext, label="- -  async"]
  }
}
```

---

## Pattern 8: Retry Loop

**Use when:** An operation may fail and should be retried a fixed number of times
before giving up. Use a dashed back-edge (with `constraint=false`) for the retry arc.

```dot
digraph retry_loop {
  rankdir=LR
  node [fontname="Helvetica", fontsize=12]

  start        [shape=ellipse,  label="Start"]
  attempt      [shape=box,      label="Attempt\nOperation"]
  success_gate [shape=diamond,  label="Success?"]
  retries_gate [shape=diamond,  label="Retries\nLeft?"]
  done         [shape=ellipse,  label="Done"]
  failed       [shape=ellipse,  label="Failed",
                style=filled,   fillcolor=lightcoral]

  start        -> attempt
  attempt      -> success_gate
  success_gate -> done          [label="yes"]
  success_gate -> retries_gate  [label="no"]
  retries_gate -> attempt       [label="yes", style=dashed, constraint=false]
  retries_gate -> failed        [label="no"]
}
```

---

## Pattern 9: Data Flow

**Use when:** Data moves through ingestion, validation, transformation, storage,
and reporting stages. Shapes communicate the role of each node at a glance.

```dot
digraph data_flow {
  rankdir=LR
  node [fontname="Helvetica", fontsize=12]

  src_db  [shape=cylinder, label="Source DB"]
  src_api [shape=cylinder, label="External API"]
  ingest  [shape=box,      label="Ingest"]
  valid   [shape=diamond,  label="Valid?"]
  xform   [shape=box,      label="Transform"]
  rejects [shape=box,      label="Reject Log"]
  storage [shape=cylinder, label="Data Store"]
  report  [shape=tab,      label="Report"]

  src_db  -> ingest
  src_api -> ingest
  ingest  -> valid
  valid   -> xform   [label="yes"]
  valid   -> rejects [label="no"]
  xform   -> storage
  storage -> report
}
```

---

## Pattern 10: Progressive Disclosure

**Use when:** A system is too large for one diagram. Create a concise `overview.dot`
using `note` shapes to summarize each subsystem, with pointers to per-subsystem
detail files (`subsystem-a.dot`, `subsystem-b.dot`, etc.).

**File naming convention:**
- `overview.dot` — system map, 150–250 lines, loads fast as agent context
- `<subsystem>.dot` — full detail for one bounded area, loaded on demand
- `.investigation/<topic>.dot` — raw investigative artifacts, load only when needed

```dot
// overview.dot — top-level orientation (load first)
// Detail files: frontend.dot  backend.dot  data.dot
digraph system_overview {
  rankdir=TB
  node [fontname="Helvetica", fontsize=12, style=filled]

  frontend  [shape=note,    label="Frontend\n[→ frontend.dot]",
             fillcolor=lightyellow]
  backend   [shape=note,    label="Backend\n[→ backend.dot]",
             fillcolor=lightcyan]
  data_tier [shape=note,    label="Data Tier\n[→ data.dot]",
             fillcolor=lavender]
  external  [shape=ellipse, label="External\nServices",
             fillcolor=white]

  frontend  -> backend
  backend   -> data_tier
  backend   -> external [style=dashed]
}
```
