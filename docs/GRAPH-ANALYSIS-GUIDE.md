# Graph Analysis Guide

> **Phase 3 Preview** — graph intelligence via code algorithms, zero LLM tokens required
> Informed by: BOOTSTRAP-SYNTHESIS.md (Tier 3), DOT-ECOSYSTEM-RESEARCH.md Section 5

---

## The Core Idea

A DOT file is not just a picture. It is a formal graph structure — nodes, edges, and
attributes — that graph algorithms can interrogate directly. Once you have a `.dot` file,
a Python program can answer structural questions in milliseconds without involving an LLM.

**Five questions your graphs can answer without an LLM:**

1. "If I change node X, what nodes are affected?" → **Reachability analysis**
2. "Are there any nodes nothing can reach?" → **Unreachable node detection**
3. "Is there a circular dependency in this pipeline?" → **Cycle detection**
4. "How does data flow from A to B?" → **Path finding**
5. "What is the longest execution path through the system?" → **Critical path analysis**

**Zero LLM token cost.** These analyses run as pure graph algorithms — O(V+E) traversals,
not language model calls. Fast, deterministic, and free at any scale.

---

## Analysis Operations

The following eight operations form the Phase 3 `dot_analyze` tool contract.
Each operation maps to one or more NetworkX algorithms via `pydot` → `networkx` parsing.
All results are returned as structured data (lists, dicts) suitable for downstream use
in annotations, reports, or LLM context injection.

### 1. Reachability

**Question:** Which nodes can be reached from a given starting node?
**Use case:** Impact analysis — "what does changing this node affect downstream?"
**How it works:** Depth-first traversal from the source node following directed edges.
**Interpretation:** Any reachable node is a potential downstream dependency of the source.

### 2. Unreachable Nodes

**Question:** Which nodes can never be reached from any entry point?
**Use case:** Dead code / dead node detection — finding orphaned pipeline steps.
**How it works:** Compute reachable set from all zero-in-degree nodes; subtract from all nodes.
**Interpretation:** Unreachable nodes are candidates for removal or reconnection.

### 3. Cycle Detection

**Question:** Does this graph contain any cycles?
**Use case:** Circular dependency discovery — validating that pipelines are true DAGs.
**How it works:** `nx.simple_cycles(G)` returns all elementary cycles in the graph.
**Interpretation:** Any cycle is a potential infinite loop or execution ordering violation.

### 4. Path Finding

**Question:** Is there a path between node A and node B? What are all paths?
**Use case:** Connection understanding — "can data flow from this input to that output?"
**How it works:** `nx.has_path(G, A, B)` and `nx.all_simple_paths(G, A, B)`.
**Interpretation:** Multiple paths indicate redundancy; no path indicates disconnection.

### 5. Critical Path

**Question:** What is the longest path through the graph?
**Use case:** Bottleneck identification — finding the performance-limiting execution sequence.
**How it works:** Topological sort combined with dynamic programming longest-path algorithm.
**Interpretation:** The critical path sets the theoretical minimum total execution time.

### 6. Subgraph Extraction

**Question:** What does the N-hop neighborhood of node X look like?
**Use case:** Zoom-in navigation — isolating one subsystem from a large complex diagram.
**How it works:** Collect N-hop neighbors via BFS; induce subgraph on that node set.
**Interpretation:** Extracted subgraph can be rendered and reviewed in isolation.

### 7. Structural Diff

**Question:** What changed between two versions of this graph?
**Use case:** Change tracking — reviewing pipeline and architecture evolution across commits.
**How it works:** Compare node sets, edge sets, and attribute dicts between two parsed graphs.
**Interpretation:** Output details — added nodes, removed nodes, added edges, removed edges,
and changed attributes. Each change class is reported separately for precision.

### 8. Graph Statistics

**Question:** What are the key structural properties of this graph?
**Use case:** Quick health check — detecting unusually large, dense, or fragmented graphs.
**How it works:** Compute six metrics directly from the NetworkX graph object in one pass.
**Interpretation:** Six reported metrics: node count, edge count, average degree,
max in-degree (busiest consumer node), max out-degree (busiest producer node), and
number of weakly connected components (isolated subgraph count).

---

## The Analysis-to-Artifact Loop

Graph analysis delivers maximum value when findings feed back into the DOT artifact:

```
DOT → analyze → annotate → render → act → update → DOT (next version)
```

1. **analyze** — run operations above; identify structural problems and anomalies
2. **annotate** — write findings back into DOT as comments or highlight attributes
3. **render** — generate SVG with issues visually marked for human review
4. **act** — fix the pipeline, restructure the architecture, remove dead nodes
5. **update** — commit the revised DOT; analysis baseline resets for the next cycle

This loop makes graphs self-documenting: structural problems surface automatically
on every commit, without waiting for a human reviewer to notice them manually.
The analysis outputs can also be injected as structured context into LLM prompts,
giving agents precise graph facts rather than forcing them to infer structure visually.

---

## When to Use Code vs LLM

| Task | Prefer | Rule of Thumb |
|------|--------|---------------|
| Validate graph is a DAG (no cycles) | **Code** | Deterministic; LLM cannot count edges reliably |
| Find all nodes reachable from X | **Code** | Graph traversal is O(V+E), not a language task |
| List nodes with no incoming edges | **Code** | Set arithmetic; zero ambiguity in the answer |
| Explain what this pipeline does | **LLM** | Requires semantic understanding of node labels |
| Suggest a better graph structure | **LLM** | Design judgment, not graph theory |
| Author a DOT file for a new use case | **LLM** | Generating from intent requires language reasoning |

**Rule of thumb:** If the question has a mathematically correct answer derivable from
graph structure alone, use code. If the question requires understanding intent, context,
or the semantics of labels, use the LLM. When in doubt: structure is code territory;
meaning is LLM territory.
