# Phase 3: Graph Intelligence Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Implement `analyze.py` with 8 NetworkX-backed graph intelligence operations and wire them into the existing `DotGraphTool` routing in `__init__.py`.

**Architecture:** DOT string → pydot parse → `nx.drawing.nx_pydot.from_pydot()` → NetworkX `MultiDiGraph` → run graph algorithms → return structured dict. Each analysis operation is an internal function (`_stats`, `_reachability`, etc.) dispatched by a public `analyze_dot()` entry point. Operations that find issues (unreachable nodes, cycles) also return an `annotated_dot` field with findings highlighted in the DOT source.

**Tech Stack:** Python 3.11+, pydot ≥3.0 (DOT parsing), networkx ≥3.0 (graph algorithms), pytest + pytest-asyncio (testing)

---

## Working Directory

All file paths are relative to the workspace root: `/home/bkrabach/dev/dot-graph-bundle`

**Run module tests:**
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

**Run bundle tests:**
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/ -v --tb=short
```

## Important Technical Context

- `nx.drawing.nx_pydot.from_pydot()` returns a **`MultiDiGraph`** (not `DiGraph`). This means edges are keyed: `G.edges` returns `(src, dst, key)` tuples. Use `G.number_of_edges()` not `len(G.edges)` for edge count. Most `nx` algorithms work on MultiDiGraph, but some (like `nx.density`) need the node/edge counts directly.
- pydot parsing uses `pydot.graph_from_dot_data(dot_content)` which returns a list — take `[0]`.
- pydot strips quotes from node names — use `.strip('"')` on `get_name()`.
- The existing `validate.py` has `_ENTRY_HINTS` and `_PSEUDO_NODES` frozensets. `analyze.py` needs its own copy of `_PSEUDO_NODES` (or import from validate) to filter out pydot pseudo-nodes (`"node"`, `"edge"`, `"graph"`) from NetworkX graph results.
- `amplifier_core.ToolResult` is the return type from `execute()` in `__init__.py`. The analyze module itself returns plain dicts.

---

### Task 1: `analyze.py` — Core DOT→NetworkX parsing + `stats` operation

**Files:**
- Create: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py`
- Create: `modules/tool-dot-graph/tests/test_analyze.py`

This task establishes the DOT→pydot→NetworkX pipeline that all 8 operations depend on, plus the first operation (`stats`) to prove it works end-to-end.

**Step 1: Write the failing tests**

Create `modules/tool-dot-graph/tests/test_analyze.py` with:

```python
"""Tests for analyze.py — graph intelligence operations backed by NetworkX.

Tests are organized by operation: stats, reachability, unreachable, cycles,
paths, critical_path, subgraph_extract, diff.
"""

import pytest


# ---------------------------------------------------------------------------
# DOT fixtures (plain strings, no files)
# ---------------------------------------------------------------------------

SIMPLE_DAG = "digraph G { a -> b; b -> c; c -> d }"
DIAMOND_DAG = "digraph G { a -> b; a -> c; b -> d; c -> d }"
CYCLIC_GRAPH = "digraph G { a -> b; b -> c; c -> a }"
DISCONNECTED = "digraph G { a -> b; c -> d }"
SINGLE_NODE = "digraph G { a }"
EMPTY_GRAPH = "digraph G {}"
UNDIRECTED = "graph G { a -- b; b -- c }"
COMPLEX_DAG = """digraph G {
    start -> parse; start -> validate;
    parse -> transform; validate -> transform;
    transform -> render; transform -> cache;
    render -> output; cache -> output;
}"""


# ---------------------------------------------------------------------------
# Core parsing tests
# ---------------------------------------------------------------------------


def test_analyze_dot_invalid_content_returns_error():
    """analyze_dot() with unparseable DOT returns success=False with error message."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot("this is not valid DOT !!!###", {"analysis": "stats"})

    assert result["success"] is False, "Invalid DOT must return success=False"
    assert "error" in result, "Error result must have 'error' key"


def test_analyze_dot_empty_content_returns_error():
    """analyze_dot() with empty string returns success=False."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot("", {"analysis": "stats"})

    assert result["success"] is False, "Empty DOT must return success=False"


def test_analyze_dot_unknown_analysis_returns_error():
    """analyze_dot() with unknown analysis type returns error listing valid types."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "frobnicate"})

    assert result["success"] is False
    assert "error" in result
    assert "frobnicate" in result["error"], "Error must mention the unknown analysis name"


def test_analyze_dot_missing_analysis_key_returns_error():
    """analyze_dot() with no 'analysis' key in options returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {})

    assert result["success"] is False
    assert "error" in result


# ---------------------------------------------------------------------------
# stats operation tests
# ---------------------------------------------------------------------------


def test_stats_simple_dag():
    """stats on simple linear DAG returns correct node/edge counts."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "stats"})

    assert result["success"] is True
    assert result["operation"] == "stats"
    stats = result["stats"]
    assert stats["node_count"] == 4, f"Expected 4 nodes (a,b,c,d), got {stats['node_count']}"
    assert stats["edge_count"] == 3, f"Expected 3 edges, got {stats['edge_count']}"
    assert stats["is_directed"] is True
    assert stats["is_dag"] is True


def test_stats_diamond_dag():
    """stats on diamond DAG returns correct counts and density."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(DIAMOND_DAG, {"analysis": "stats"})

    assert result["success"] is True
    stats = result["stats"]
    assert stats["node_count"] == 4
    assert stats["edge_count"] == 4
    assert stats["is_dag"] is True
    assert isinstance(stats["density"], float)
    assert 0 < stats["density"] <= 1


def test_stats_cyclic_graph():
    """stats on cyclic graph correctly reports is_dag=False."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "stats"})

    assert result["success"] is True
    stats = result["stats"]
    assert stats["is_dag"] is False


def test_stats_disconnected_graph():
    """stats on disconnected graph reports multiple components."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(DISCONNECTED, {"analysis": "stats"})

    assert result["success"] is True
    stats = result["stats"]
    assert stats["weakly_connected_components"] == 2, (
        f"Expected 2 components, got {stats['weakly_connected_components']}"
    )


def test_stats_single_node():
    """stats on single-node graph returns correct counts."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SINGLE_NODE, {"analysis": "stats"})

    assert result["success"] is True
    stats = result["stats"]
    assert stats["node_count"] == 1
    assert stats["edge_count"] == 0


def test_stats_result_has_all_fields():
    """stats result contains all expected fields."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "stats"})

    assert result["success"] is True
    stats = result["stats"]
    required_fields = [
        "node_count", "edge_count", "density", "is_directed", "is_dag",
        "weakly_connected_components", "nodes", "self_loops",
    ]
    for field in required_fields:
        assert field in stats, f"stats must include '{field}' field"
```

**Step 2: Run tests to verify they fail**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short
```

Expected: All tests FAIL with `ModuleNotFoundError: No module named 'amplifier_module_tool_dot_graph.analyze'`

**Step 3: Write the implementation**

Create `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py` with:

```python
"""NetworkX-backed graph intelligence for DOT content.

Parses DOT → pydot → NetworkX MultiDiGraph, then runs graph algorithms.
Each operation is a separate internal function dispatched by analyze_dot().

Operations: stats, reachability, unreachable, cycles, paths, critical_path,
subgraph_extract, diff.
"""

from __future__ import annotations

import contextlib
import io

import networkx as nx
import pydot

# pydot pseudo-node names injected by default style declarations.
_PSEUDO_NODES: frozenset[str] = frozenset({"node", "edge", "graph"})

# Valid analysis operation names.
_KNOWN_ANALYSES: frozenset[str] = frozenset(
    {
        "stats",
        "reachability",
        "unreachable",
        "cycles",
        "paths",
        "critical_path",
        "subgraph_extract",
        "diff",
    }
)

# Entry-point node names exempt from "unreachable" warnings.
_ENTRY_HINTS: frozenset[str] = frozenset(
    {"start", "entry", "root", "begin", "init", "source"}
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_dot(dot_content: str, options: dict) -> dict:
    """Run a graph analysis operation on DOT content.

    Args:
        dot_content: Raw DOT graph string.
        options: Must contain 'analysis' key naming the operation.
                 Operation-specific keys (e.g. 'source_node') also live here.

    Returns:
        On success: {success: True, operation: str, ...operation-specific results}
        On failure: {success: False, error: str}
    """
    analysis = options.get("analysis")
    if not analysis:
        return {
            "success": False,
            "error": (
                "Missing 'analysis' key in options. "
                f"Valid analyses: {sorted(_KNOWN_ANALYSES)}"
            ),
        }

    if analysis not in _KNOWN_ANALYSES:
        return {
            "success": False,
            "error": (
                f"Unknown analysis '{analysis}'. "
                f"Valid analyses: {sorted(_KNOWN_ANALYSES)}"
            ),
        }

    # --- Parse DOT → pydot → NetworkX ---
    # Special case: diff needs two DOT strings, parsed separately.
    if analysis == "diff":
        return _diff(dot_content, options)

    # Special case: subgraph_extract works on pydot graph, not NetworkX.
    if analysis == "subgraph_extract":
        pydot_graph = _parse_dot(dot_content)
        if pydot_graph is None:
            return _parse_error(dot_content)
        return _subgraph_extract(pydot_graph, dot_content, options)

    # All other operations need a NetworkX graph.
    pydot_graph = _parse_dot(dot_content)
    if pydot_graph is None:
        return _parse_error(dot_content)

    nxgraph = _pydot_to_networkx(pydot_graph)

    # Dispatch to operation handler.
    dispatch = {
        "stats": lambda: _stats(nxgraph),
        "reachability": lambda: _reachability(nxgraph, options),
        "unreachable": lambda: _unreachable(nxgraph, dot_content),
        "cycles": lambda: _cycles(nxgraph, dot_content),
        "paths": lambda: _paths(nxgraph, options),
        "critical_path": lambda: _critical_path(nxgraph),
    }

    return dispatch[analysis]()


# ---------------------------------------------------------------------------
# DOT → NetworkX parsing
# ---------------------------------------------------------------------------


def _parse_dot(dot_content: str) -> pydot.Dot | None:
    """Parse DOT string into a pydot graph. Returns None on failure."""
    if not dot_content or not dot_content.strip():
        return None

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        try:
            graphs = pydot.graph_from_dot_data(dot_content)
        except Exception:  # noqa: BLE001
            return None

    if not graphs:
        return None
    return graphs[0]


def _pydot_to_networkx(pydot_graph: pydot.Dot) -> nx.MultiDiGraph:
    """Convert pydot graph to NetworkX MultiDiGraph, filtering pseudo-nodes."""
    nxgraph = nx.drawing.nx_pydot.from_pydot(pydot_graph)
    # Remove pydot pseudo-nodes that leak through.
    for pseudo in _PSEUDO_NODES:
        if pseudo in nxgraph:
            nxgraph.remove_node(pseudo)
    return nxgraph


def _parse_error(dot_content: str) -> dict:
    """Standard error dict for unparseable DOT content."""
    return {
        "success": False,
        "error": "Failed to parse DOT content. Check syntax with the validate operation.",
    }


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------


def _stats(graph: nx.MultiDiGraph) -> dict:
    """Compute graph statistics."""
    n = graph.number_of_nodes()
    e = graph.number_of_edges()

    # Density: for a directed graph without self-loops, max edges = n*(n-1).
    density = nx.density(graph) if n > 1 else 0.0

    is_dag = nx.is_directed_acyclic_graph(graph)

    # Weakly connected components (treats edges as undirected for connectivity).
    components = list(nx.weakly_connected_components(graph))

    # Self-loops count.
    self_loops = nx.number_of_selfloops(graph)

    return {
        "success": True,
        "operation": "stats",
        "stats": {
            "node_count": n,
            "edge_count": e,
            "density": round(density, 4),
            "is_directed": graph.is_directed(),
            "is_dag": is_dag,
            "weakly_connected_components": len(components),
            "self_loops": self_loops,
            "nodes": sorted(graph.nodes()),
        },
    }
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short
```

Expected: All 11 tests PASS

**Step 5: Run full module test suite**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: All existing tests still pass (66 + 11 new = 77 total)

**Step 6: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py modules/tool-dot-graph/tests/test_analyze.py && git commit -m "feat: add analyze.py with DOT→NetworkX parsing and stats operation"
```

---

### Task 2: `analyze.py` — reachability + unreachable + cycles operations

**Files:**
- Modify: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py`
- Modify: `modules/tool-dot-graph/tests/test_analyze.py`

**Step 1: Add failing tests**

Append to `modules/tool-dot-graph/tests/test_analyze.py`:

```python
# ---------------------------------------------------------------------------
# reachability operation tests
# ---------------------------------------------------------------------------


def test_reachability_from_source():
    """reachability from 'a' in a->b->c->d returns {b, c, d}."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability", "source_node": "a"})

    assert result["success"] is True
    assert result["operation"] == "reachability"
    assert set(result["reachable"]) == {"b", "c", "d"}


def test_reachability_from_leaf():
    """reachability from leaf node 'd' returns empty set."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability", "source_node": "d"})

    assert result["success"] is True
    assert result["reachable"] == []


def test_reachability_missing_source_node():
    """reachability without source_node returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability"})

    assert result["success"] is False
    assert "source_node" in result["error"]


def test_reachability_nonexistent_node():
    """reachability with node not in graph returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability", "source_node": "zzz"})

    assert result["success"] is False
    assert "zzz" in result["error"]


def test_reachability_in_cyclic_graph():
    """reachability in cyclic graph a->b->c->a from 'a' returns {b, c}."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "reachability", "source_node": "a"})

    assert result["success"] is True
    assert set(result["reachable"]) == {"b", "c"}


# ---------------------------------------------------------------------------
# unreachable operation tests
# ---------------------------------------------------------------------------


def test_unreachable_in_disconnected_graph():
    """unreachable in 'a->b; c->d' finds nodes with no incoming edges (excluding entry hints)."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(DISCONNECTED, {"analysis": "unreachable"})

    assert result["success"] is True
    assert result["operation"] == "unreachable"
    # 'a' and 'c' have no incoming edges and aren't entry hint names
    assert set(result["unreachable_nodes"]) == {"a", "c"}


def test_unreachable_entry_hints_excluded():
    """Entry-hint node names (start, entry, etc.) are not flagged as unreachable."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    dot = "digraph G { start -> a; a -> b; orphan -> c }"
    result = analyze_dot(dot, {"analysis": "unreachable"})

    assert result["success"] is True
    # 'start' has no incoming but is an entry hint — excluded.
    # 'orphan' has no incoming and is NOT an entry hint — included.
    assert "start" not in result["unreachable_nodes"]
    assert "orphan" in result["unreachable_nodes"]


def test_unreachable_fully_connected():
    """Fully connected DAG with a single root 'start' has no unreachable nodes."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    dot = "digraph G { start -> a; a -> b; b -> c }"
    result = analyze_dot(dot, {"analysis": "unreachable"})

    assert result["success"] is True
    assert result["unreachable_nodes"] == []


def test_unreachable_returns_annotated_dot():
    """unreachable result includes annotated_dot with unreachable nodes colored red."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(DISCONNECTED, {"analysis": "unreachable"})

    assert result["success"] is True
    assert "annotated_dot" in result
    # Annotated DOT should contain color=red for unreachable nodes
    assert "red" in result["annotated_dot"]


# ---------------------------------------------------------------------------
# cycles operation tests
# ---------------------------------------------------------------------------


def test_cycles_in_cyclic_graph():
    """cycles detects the cycle in a->b->c->a."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "cycles"})

    assert result["success"] is True
    assert result["operation"] == "cycles"
    assert result["has_cycles"] is True
    assert len(result["cycles"]) >= 1
    # The cycle should contain all three nodes
    cycle_nodes = set()
    for cycle in result["cycles"]:
        cycle_nodes.update(cycle)
    assert {"a", "b", "c"} <= cycle_nodes


def test_cycles_in_dag():
    """cycles in a DAG returns has_cycles=False, empty cycles list."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "cycles"})

    assert result["success"] is True
    assert result["has_cycles"] is False
    assert result["cycles"] == []


def test_cycles_returns_annotated_dot():
    """cycles result includes annotated_dot with cycle edges highlighted when cycles exist."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "cycles"})

    assert result["success"] is True
    assert result["has_cycles"] is True
    assert "annotated_dot" in result
    assert "red" in result["annotated_dot"]
```

**Step 2: Run tests to verify the new tests fail**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short -k "reachability or unreachable or cycles"
```

Expected: All new tests FAIL (functions not yet implemented)

**Step 3: Implement the three operations**

Add to `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py`, after the `_stats` function:

```python
# ---------------------------------------------------------------------------
# reachability
# ---------------------------------------------------------------------------


def _reachability(graph: nx.MultiDiGraph, options: dict) -> dict:
    """Find all nodes reachable from a source node via directed edges."""
    source = options.get("source_node")
    if not source:
        return {
            "success": False,
            "error": "Missing 'source_node' in options for reachability analysis.",
        }
    if source not in graph:
        return {
            "success": False,
            "error": f"Node '{source}' not found in graph. Available nodes: {sorted(graph.nodes())}",
        }

    reachable = sorted(nx.descendants(graph, source))
    return {
        "success": True,
        "operation": "reachability",
        "source_node": source,
        "reachable": reachable,
        "reachable_count": len(reachable),
    }


# ---------------------------------------------------------------------------
# unreachable
# ---------------------------------------------------------------------------


def _unreachable(graph: nx.MultiDiGraph, dot_content: str) -> dict:
    """Find nodes with no incoming edges (excluding entry-hint names)."""
    unreachable = []
    for node in sorted(graph.nodes()):
        if graph.in_degree(node) == 0 and node.lower() not in _ENTRY_HINTS:
            unreachable.append(node)

    annotated_dot = _annotate_nodes(dot_content, unreachable, color="red", style="bold")

    return {
        "success": True,
        "operation": "unreachable",
        "unreachable_nodes": unreachable,
        "unreachable_count": len(unreachable),
        "annotated_dot": annotated_dot,
    }


# ---------------------------------------------------------------------------
# cycles
# ---------------------------------------------------------------------------


def _cycles(graph: nx.MultiDiGraph, dot_content: str) -> dict:
    """Detect all simple cycles in the graph."""
    cycles = [sorted(c) for c in nx.simple_cycles(graph)]

    # Build set of edges involved in cycles for annotation.
    cycle_edges: set[tuple[str, str]] = set()
    for cycle in nx.simple_cycles(graph):
        cycle_list = list(cycle)
        for i in range(len(cycle_list)):
            src = cycle_list[i]
            dst = cycle_list[(i + 1) % len(cycle_list)]
            cycle_edges.add((src, dst))

    annotated_dot = _annotate_edges(dot_content, cycle_edges, color="red", style="bold")

    return {
        "success": True,
        "operation": "cycles",
        "has_cycles": len(cycles) > 0,
        "cycles": cycles,
        "cycle_count": len(cycles),
        "annotated_dot": annotated_dot if cycles else None,
    }


# ---------------------------------------------------------------------------
# Annotation helpers
# ---------------------------------------------------------------------------


def _annotate_nodes(
    dot_content: str, nodes: list[str], color: str = "red", style: str = "bold"
) -> str:
    """Insert attribute declarations for highlighted nodes into DOT content.

    Adds lines like: node_name [color=red, style=bold];
    right after the opening brace of the graph.
    """
    if not nodes:
        return dot_content

    annotations = []
    for node in nodes:
        # Quote node names that contain special chars; always safe to quote.
        annotations.append(f'    "{node}" [color={color}, style={style}];')

    annotation_block = "\n".join(annotations)

    # Insert after the first '{' line.
    lines = dot_content.split("\n")
    for i, line in enumerate(lines):
        if "{" in line:
            lines.insert(i + 1, annotation_block)
            break

    return "\n".join(lines)


def _annotate_edges(
    dot_content: str,
    edges: set[tuple[str, str]],
    color: str = "red",
    style: str = "bold",
) -> str:
    """Insert attribute declarations for highlighted edges into DOT content.

    Adds lines like: "src" -> "dst" [color=red, style=bold];
    right after the opening brace of the graph.
    """
    if not edges:
        return dot_content

    annotations = []
    for src, dst in sorted(edges):
        annotations.append(f'    "{src}" -> "{dst}" [color={color}, style={style}];')

    annotation_block = "\n".join(annotations)

    lines = dot_content.split("\n")
    for i, line in enumerate(lines):
        if "{" in line:
            lines.insert(i + 1, annotation_block)
            break

    return "\n".join(lines)
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short
```

Expected: All tests pass (11 from Task 1 + 14 new = 25 total in test_analyze.py)

**Step 5: Run full module test suite**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: All pass (66 existing + 14 new = 80 total)

**Step 6: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py modules/tool-dot-graph/tests/test_analyze.py && git commit -m "feat: add reachability, unreachable, and cycles analysis operations"
```

---

### Task 3: `analyze.py` — paths + critical_path operations

**Files:**
- Modify: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py`
- Modify: `modules/tool-dot-graph/tests/test_analyze.py`

**Step 1: Add failing tests**

Append to `modules/tool-dot-graph/tests/test_analyze.py`:

```python
# ---------------------------------------------------------------------------
# paths operation tests
# ---------------------------------------------------------------------------


def test_paths_simple():
    """paths from 'a' to 'd' in linear DAG returns single path [a,b,c,d]."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "paths", "source_node": "a", "target_node": "d"}
    )

    assert result["success"] is True
    assert result["operation"] == "paths"
    assert len(result["paths"]) == 1
    assert result["paths"][0] == ["a", "b", "c", "d"]


def test_paths_diamond():
    """paths from 'a' to 'd' in diamond DAG returns 2 paths."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        DIAMOND_DAG, {"analysis": "paths", "source_node": "a", "target_node": "d"}
    )

    assert result["success"] is True
    assert len(result["paths"]) == 2


def test_paths_no_path_exists():
    """paths between disconnected nodes returns empty paths list."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        DISCONNECTED, {"analysis": "paths", "source_node": "a", "target_node": "d"}
    )

    assert result["success"] is True
    assert result["paths"] == []
    assert result["path_count"] == 0


def test_paths_missing_source():
    """paths without source_node returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "paths", "target_node": "d"}
    )

    assert result["success"] is False
    assert "source_node" in result["error"]


def test_paths_missing_target():
    """paths without target_node returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "paths", "source_node": "a"}
    )

    assert result["success"] is False
    assert "target_node" in result["error"]


def test_paths_nonexistent_source():
    """paths with nonexistent source returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "paths", "source_node": "zzz", "target_node": "d"}
    )

    assert result["success"] is False
    assert "zzz" in result["error"]


# ---------------------------------------------------------------------------
# critical_path operation tests
# ---------------------------------------------------------------------------


def test_critical_path_linear_dag():
    """critical_path on linear DAG a->b->c->d returns [a,b,c,d]."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "critical_path"})

    assert result["success"] is True
    assert result["operation"] == "critical_path"
    assert result["critical_path"] == ["a", "b", "c", "d"]
    assert result["length"] == 4


def test_critical_path_diamond_dag():
    """critical_path on diamond DAG returns one of the two longest paths (length 3)."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(DIAMOND_DAG, {"analysis": "critical_path"})

    assert result["success"] is True
    assert result["length"] == 3  # a->b->d or a->c->d
    assert result["critical_path"][0] == "a"
    assert result["critical_path"][-1] == "d"


def test_critical_path_complex_dag():
    """critical_path on complex DAG finds the true longest path."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(COMPLEX_DAG, {"analysis": "critical_path"})

    assert result["success"] is True
    assert result["length"] >= 4  # start->parse/validate->transform->render/cache->output


def test_critical_path_on_cyclic_graph():
    """critical_path on cyclic graph returns error (only works on DAGs)."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "critical_path"})

    assert result["success"] is False
    assert "cycle" in result["error"].lower() or "dag" in result["error"].lower()


def test_critical_path_single_node():
    """critical_path on single-node graph returns that node."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SINGLE_NODE, {"analysis": "critical_path"})

    assert result["success"] is True
    assert result["critical_path"] == ["a"]
    assert result["length"] == 1
```

**Step 2: Run tests to verify the new tests fail**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short -k "paths or critical_path"
```

Expected: All new tests FAIL

**Step 3: Implement the two operations**

Add to `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py`, after the `_cycles` function (before the annotation helpers):

```python
# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------


def _paths(graph: nx.MultiDiGraph, options: dict) -> dict:
    """Find all simple paths between source and target nodes."""
    source = options.get("source_node")
    target = options.get("target_node")

    if not source:
        return {
            "success": False,
            "error": "Missing 'source_node' in options for paths analysis.",
        }
    if not target:
        return {
            "success": False,
            "error": "Missing 'target_node' in options for paths analysis.",
        }
    if source not in graph:
        return {
            "success": False,
            "error": f"Source node '{source}' not found in graph. Available: {sorted(graph.nodes())}",
        }
    if target not in graph:
        return {
            "success": False,
            "error": f"Target node '{target}' not found in graph. Available: {sorted(graph.nodes())}",
        }

    # Cap at 100 paths to avoid combinatorial explosion on dense graphs.
    all_paths = []
    for path in nx.all_simple_paths(graph, source, target):
        all_paths.append(path)
        if len(all_paths) >= 100:
            break

    return {
        "success": True,
        "operation": "paths",
        "source_node": source,
        "target_node": target,
        "paths": all_paths,
        "path_count": len(all_paths),
        "truncated": len(all_paths) >= 100,
    }


# ---------------------------------------------------------------------------
# critical_path
# ---------------------------------------------------------------------------


def _critical_path(graph: nx.MultiDiGraph) -> dict:
    """Find the longest path in a DAG (critical path).

    Only works on directed acyclic graphs. Returns error for cyclic graphs.
    """
    if not nx.is_directed_acyclic_graph(graph):
        return {
            "success": False,
            "error": (
                "critical_path requires a DAG (directed acyclic graph). "
                "This graph contains cycles. Use the 'cycles' analysis to find them."
            ),
        }

    path = nx.dag_longest_path(graph)

    return {
        "success": True,
        "operation": "critical_path",
        "critical_path": path,
        "length": len(path),
    }
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short
```

Expected: All 36 tests pass (25 + 11 new)

**Step 5: Run full module test suite**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: All pass (66 existing + 25 new = 91 total)

**Step 6: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py modules/tool-dot-graph/tests/test_analyze.py && git commit -m "feat: add paths and critical_path analysis operations"
```

---

### Task 4: `analyze.py` — subgraph_extract + diff operations

**Files:**
- Modify: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py`
- Modify: `modules/tool-dot-graph/tests/test_analyze.py`

**Step 1: Add failing tests**

Append to `modules/tool-dot-graph/tests/test_analyze.py`:

```python
# ---------------------------------------------------------------------------
# subgraph_extract operation tests
# ---------------------------------------------------------------------------

CLUSTERED_DOT = """digraph G {
    outside_a -> outside_b;
    subgraph cluster_core {
        label="Core";
        x -> y;
        y -> z;
    }
    subgraph cluster_util {
        label="Utilities";
        u -> v;
    }
    outside_a -> x;
    z -> outside_b;
}"""


def test_subgraph_extract_existing_cluster():
    """subgraph_extract extracts 'cluster_core' as standalone DOT."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        CLUSTERED_DOT, {"analysis": "subgraph_extract", "cluster_name": "cluster_core"}
    )

    assert result["success"] is True
    assert result["operation"] == "subgraph_extract"
    extracted = result["extracted_dot"]
    assert "x" in extracted
    assert "y" in extracted
    assert "z" in extracted
    # Should be valid DOT (parseable)
    import pydot
    graphs = pydot.graph_from_dot_data(extracted)
    assert graphs and len(graphs) > 0, "Extracted DOT must be parseable"


def test_subgraph_extract_nonexistent_cluster():
    """subgraph_extract with nonexistent cluster returns error with available clusters."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        CLUSTERED_DOT, {"analysis": "subgraph_extract", "cluster_name": "cluster_nonexistent"}
    )

    assert result["success"] is False
    assert "cluster_nonexistent" in result["error"]
    assert "available" in result["error"].lower()


def test_subgraph_extract_missing_cluster_name():
    """subgraph_extract without cluster_name returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(CLUSTERED_DOT, {"analysis": "subgraph_extract"})

    assert result["success"] is False
    assert "cluster_name" in result["error"]


def test_subgraph_extract_preserves_label():
    """Extracted subgraph preserves the cluster label."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        CLUSTERED_DOT, {"analysis": "subgraph_extract", "cluster_name": "cluster_core"}
    )

    assert result["success"] is True
    assert "Core" in result["extracted_dot"]


# ---------------------------------------------------------------------------
# diff operation tests
# ---------------------------------------------------------------------------

DOT_V1 = "digraph G { a -> b; b -> c; c -> d }"
DOT_V2 = "digraph G { a -> b; b -> c; c -> e; d -> e }"


def test_diff_detects_added_nodes():
    """diff between v1 and v2 detects node 'e' was added."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        DOT_V1, {"analysis": "diff", "dot_content_b": DOT_V2}
    )

    assert result["success"] is True
    assert result["operation"] == "diff"
    assert "e" in result["added_nodes"]


def test_diff_detects_removed_edges():
    """diff between v1 and v2 detects edge c->d was removed."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        DOT_V1, {"analysis": "diff", "dot_content_b": DOT_V2}
    )

    assert result["success"] is True
    # c->d exists in v1 but not v2
    removed_edge_strs = [f"{s}->{t}" for s, t in result["removed_edges"]]
    assert "c->d" in removed_edge_strs


def test_diff_detects_added_edges():
    """diff between v1 and v2 detects new edges c->e and d->e."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        DOT_V1, {"analysis": "diff", "dot_content_b": DOT_V2}
    )

    assert result["success"] is True
    added_edge_strs = [f"{s}->{t}" for s, t in result["added_edges"]]
    assert "c->e" in added_edge_strs
    assert "d->e" in added_edge_strs


def test_diff_identical_graphs():
    """diff between identical graphs shows no changes."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "diff", "dot_content_b": SIMPLE_DAG}
    )

    assert result["success"] is True
    assert result["added_nodes"] == []
    assert result["removed_nodes"] == []
    assert result["added_edges"] == []
    assert result["removed_edges"] == []


def test_diff_missing_dot_content_b():
    """diff without dot_content_b returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "diff"})

    assert result["success"] is False
    assert "dot_content_b" in result["error"]


def test_diff_invalid_dot_content_b():
    """diff with invalid dot_content_b returns error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "diff", "dot_content_b": "not valid dot!!!"}
    )

    assert result["success"] is False
```

**Step 2: Run tests to verify the new tests fail**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short -k "subgraph_extract or diff"
```

Expected: All new tests FAIL

**Step 3: Implement the two operations**

Add the `_subgraph_extract` function to `modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py`, after `_critical_path` (before the annotation helpers):

```python
# ---------------------------------------------------------------------------
# subgraph_extract
# ---------------------------------------------------------------------------


def _subgraph_extract(
    pydot_graph: pydot.Dot, dot_content: str, options: dict
) -> dict:
    """Extract a named cluster subgraph as standalone DOT.

    Works on the pydot graph object (not NetworkX) because pydot preserves
    the cluster structure, labels, and attributes that NetworkX discards.
    """
    cluster_name = options.get("cluster_name")
    if not cluster_name:
        return {
            "success": False,
            "error": "Missing 'cluster_name' in options for subgraph_extract analysis.",
        }

    # Find the named cluster.
    available_clusters = []
    target_subgraph: pydot.Subgraph | None = None

    for sg in pydot_graph.get_subgraph_list():
        raw_name = sg.get_name()
        if raw_name is None:
            continue
        name = str(raw_name).strip('"')
        if name.lower().startswith("cluster"):
            available_clusters.append(name)
        if name == cluster_name:
            target_subgraph = sg

    if target_subgraph is None:
        return {
            "success": False,
            "error": (
                f"Cluster '{cluster_name}' not found. "
                f"Available clusters: {available_clusters}"
            ),
        }

    # Build a standalone digraph from the cluster's contents.
    graph_type = pydot_graph.get_type()
    standalone = pydot.Dot(graph_type=graph_type)
    standalone.set_name(cluster_name)

    # Copy the cluster's label if present.
    label = target_subgraph.get_label()
    if label:
        standalone.set_label(label)

    # Copy nodes.
    for node in target_subgraph.get_node_list():
        standalone.add_node(pydot.Node(node.get_name(), obj_dict=node.obj_dict.copy()))

    # Copy edges.
    for edge in target_subgraph.get_edge_list():
        standalone.add_edge(
            pydot.Edge(
                edge.get_source(),
                edge.get_destination(),
                obj_dict=edge.obj_dict.copy(),
            )
        )

    extracted_dot = standalone.to_string()

    return {
        "success": True,
        "operation": "subgraph_extract",
        "cluster_name": cluster_name,
        "extracted_dot": extracted_dot,
        "node_count": len(target_subgraph.get_node_list()),
        "edge_count": len(target_subgraph.get_edge_list()),
    }


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------


def _diff(dot_content_a: str, options: dict) -> dict:
    """Structural diff between two DOT graphs.

    Compares nodes and edges. Reports added/removed for each.
    """
    dot_content_b = options.get("dot_content_b")
    if not dot_content_b:
        return {
            "success": False,
            "error": "Missing 'dot_content_b' in options for diff analysis.",
        }

    graph_a_pydot = _parse_dot(dot_content_a)
    graph_b_pydot = _parse_dot(dot_content_b)

    if graph_a_pydot is None:
        return {"success": False, "error": "Failed to parse first DOT content (dot_content)."}
    if graph_b_pydot is None:
        return {"success": False, "error": "Failed to parse second DOT content (dot_content_b)."}

    nx_a = _pydot_to_networkx(graph_a_pydot)
    nx_b = _pydot_to_networkx(graph_b_pydot)

    nodes_a = set(nx_a.nodes())
    nodes_b = set(nx_b.nodes())

    # For edge comparison, ignore the MultiDiGraph key (third element).
    edges_a = {(u, v) for u, v, _ in nx_a.edges}
    edges_b = {(u, v) for u, v, _ in nx_b.edges}

    added_nodes = sorted(nodes_b - nodes_a)
    removed_nodes = sorted(nodes_a - nodes_b)
    added_edges = sorted(edges_b - edges_a)
    removed_edges = sorted(edges_a - edges_b)

    return {
        "success": True,
        "operation": "diff",
        "added_nodes": added_nodes,
        "removed_nodes": removed_nodes,
        "added_edges": [list(e) for e in added_edges],
        "removed_edges": [list(e) for e in removed_edges],
        "summary": {
            "nodes_added": len(added_nodes),
            "nodes_removed": len(removed_nodes),
            "edges_added": len(added_edges),
            "edges_removed": len(removed_edges),
            "unchanged_nodes": len(nodes_a & nodes_b),
            "unchanged_edges": len(edges_a & edges_b),
        },
    }
```

**Step 4: Run tests to verify they pass**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_analyze.py -v --tb=short
```

Expected: All 46 tests pass (36 + 10 new)

**Step 5: Run full module test suite**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: All pass (66 existing + 35 new = 101 total)

**Step 6: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/analyze.py modules/tool-dot-graph/tests/test_analyze.py && git commit -m "feat: add subgraph_extract and diff analysis operations"
```

---

### Task 5: `__init__.py` — Wire analyze route + update schema and description

**Files:**
- Modify: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py`
- Modify: `modules/tool-dot-graph/tests/test_tool_integration.py`

This task replaces the "Phase 3 pending" placeholder with real routing to `analyze.analyze_dot()`, updates the tool description and schema to document all analyze options, and bumps the version to 0.3.0.

**Step 1: Update the integration test for analyze**

In `modules/tool-dot-graph/tests/test_tool_integration.py`, **replace** the existing `test_analyze_operation_returns_phase3_pending` test with these new tests:

Find and replace this block (lines 140-156):

```python
@pytest.mark.asyncio
async def test_analyze_operation_returns_phase3_pending():
    """analyze operation returns success=False with Phase 3 pending message."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "analyze", "dot_content": SIMPLE_DOT})

    assert result.success is False, (
        "analyze must return success=False (Phase 3 pending)"
    )
    data = _parse_output(result)
    assert "error" in data, "analyze response must have 'error' key"
    error_msg = data["error"]
    assert "Phase 3" in error_msg or "not yet implemented" in error_msg, (
        f"analyze error must mention Phase 3 or 'not yet implemented', got: {error_msg!r}"
    )
```

Replace with:

```python
@pytest.mark.asyncio
async def test_analyze_stats_routes_correctly():
    """analyze operation with analysis='stats' calls analyze.analyze_dot and returns stats."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "analyze", "dot_content": SIMPLE_DOT, "options": {"analysis": "stats"}}
    )

    assert result.success is True, "analyze stats must return success=True"
    data = _parse_output(result)
    assert data["operation"] == "stats"
    assert "stats" in data
    assert data["stats"]["node_count"] == 2  # a, b


@pytest.mark.asyncio
async def test_analyze_missing_analysis_returns_error():
    """analyze operation without 'analysis' in options returns error."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "analyze", "dot_content": SIMPLE_DOT, "options": {}}
    )

    assert result.success is False
    data = _parse_output(result)
    assert "error" in data


@pytest.mark.asyncio
async def test_analyze_cycles_routes_correctly():
    """analyze operation with analysis='cycles' on a DAG returns has_cycles=False."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "analyze", "dot_content": SIMPLE_DOT, "options": {"analysis": "cycles"}}
    )

    assert result.success is True
    data = _parse_output(result)
    assert data["operation"] == "cycles"
    assert data["has_cycles"] is False


@pytest.mark.asyncio
async def test_analyze_invalid_dot_returns_error():
    """analyze operation with invalid DOT returns success=False."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "analyze", "dot_content": INVALID_DOT, "options": {"analysis": "stats"}}
    )

    assert result.success is False
    data = _parse_output(result)
    assert "error" in data
```

Also add a test for the updated schema and version:

```python
def test_input_schema_documents_analyze_options():
    """input_schema options property includes analyze-specific sub-properties."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema
    option_props = schema["properties"]["options"]["properties"]

    assert "analysis" in option_props, "options.properties must include 'analysis'"
    assert "source_node" in option_props, "options.properties must include 'source_node'"
    assert "target_node" in option_props, "options.properties must include 'target_node'"
    assert "cluster_name" in option_props, "options.properties must include 'cluster_name'"
    assert "dot_content_b" in option_props, "options.properties must include 'dot_content_b'"


@pytest.mark.asyncio
async def test_mount_returns_version_030():
    """mount() returns version 0.3.0, indicating Phase 3 implementation."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    result = await mount(coordinator)

    assert result["version"] == "0.3.0", (
        f"Expected version 0.3.0 (Phase 3), got: {result['version']!r}"
    )
```

**Step 2: Run tests to verify the new/changed tests fail**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_tool_integration.py -v --tb=short
```

Expected: New analyze tests FAIL (still hitting Phase 3 pending placeholder), schema test FAILS (missing analyze options), version test FAILS (still 0.2.0)

**Step 3: Update `__init__.py`**

Make these changes to `modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py`:

**Change 1:** Update the module docstring (line 1-9). Replace:

```python
"""
DOT graph tool module for Amplifier.

Provides tools for generating, validating, and analyzing DOT-format graphs
using pydot and networkx.

Phase 2: Routes tool calls to validate, render, and setup_helper modules.
Phase 3 (pending): Will add analyze operations backed by networkx.
"""
```

With:

```python
"""
DOT graph tool module for Amplifier.

Provides tools for validating, rendering, and analyzing DOT-format graphs
using pydot and networkx.

Routes tool calls to validate, render, setup_helper, and analyze modules.
"""
```

**Change 2:** Add analyze import (line 17). Replace:

```python
from amplifier_module_tool_dot_graph import render, setup_helper, validate
```

With:

```python
from amplifier_module_tool_dot_graph import analyze, render, setup_helper, validate
```

**Change 3:** Update class docstring (lines 23-31). Replace:

```python
    """DOT graph tool routing validate, render, setup, and analyze operations.

    Phase 2 implementation provides:
    - Validation: three-layer syntax, structural, and render-quality checks via pydot
    - Rendering: graphviz CLI wrapper for SVG/PNG/PDF output
    - Setup: environment check for graphviz, pydot, and networkx availability

    Phase 3 (pending): analyze — reachability, cycle detection, critical path,
    and structural diff via networkx.
    """
```

With:

```python
    """DOT graph tool routing validate, render, setup, and analyze operations.

    - Validation: three-layer syntax, structural, and render-quality checks via pydot
    - Rendering: graphviz CLI wrapper for SVG/PNG/PDF output
    - Setup: environment check for graphviz, pydot, and networkx availability
    - Analyze: graph intelligence via networkx — stats, reachability, unreachable,
      cycles, paths, critical_path, subgraph_extract, diff
    """
```

**Change 4:** Update description property (lines 39-51). Replace:

```python
    @property
    def description(self) -> str:
        return """DOT graph tool — validate, render, and analyze DOT-format graphs.

Phase 2 implementation provides:
- Validation: three-layer syntax, structural, and render-quality checks via pydot
- Rendering: graphviz CLI wrapper for SVG/PNG/PDF output
- Setup: environment check for graphviz, pydot, and networkx availability

Operations:
- validate: Parse and validate DOT content through up to three layers (syntax, structural, render)
- render: Render DOT content to SVG, PNG, PDF, or other formats via graphviz CLI
- setup: Check environment for graphviz, pydot, and networkx availability
- analyze: Structural graph analysis (Phase 3 pending)"""
```

With:

```python
    @property
    def description(self) -> str:
        return """DOT graph tool — validate, render, and analyze DOT-format graphs.

Operations:
- validate: Parse and validate DOT content through up to three layers (syntax, structural, render)
- render: Render DOT content to SVG, PNG, PDF, or other formats via graphviz CLI
- setup: Check environment for graphviz, pydot, and networkx availability
- analyze: Graph intelligence via networkx. Set options.analysis to one of:
    stats, reachability, unreachable, cycles, paths, critical_path, subgraph_extract, diff"""
```

**Change 5:** Update input_schema to add analyze-specific options (lines 54-104). Replace the entire `input_schema` property:

```python
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["validate", "render", "setup", "analyze"],
                    "description": "Operation to perform on the DOT graph",
                },
                "dot_content": {
                    "type": "string",
                    "description": "DOT graph content as a string",
                },
                "options": {
                    "type": "object",
                    "description": "Operation-specific options (format, layout engine, etc.)",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": (
                                "Output format for render operation "
                                "(svg, png, pdf, json, ps, eps)"
                            ),
                        },
                        "engine": {
                            "type": "string",
                            "description": (
                                "Layout engine for render operation "
                                "(dot, neato, fdp, sfdp, twopi, circo)"
                            ),
                        },
                        "output_path": {
                            "type": "string",
                            "description": (
                                "Output file path for render operation "
                                "(auto-generated in temp dir if not provided)"
                            ),
                        },
                        "layers": {
                            "type": "array",
                            "description": (
                                "Validation layers to run "
                                "(syntax, structural, render). Defaults to all three."
                            ),
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["operation"],
        }
```

With:

```python
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["validate", "render", "setup", "analyze"],
                    "description": "Operation to perform on the DOT graph",
                },
                "dot_content": {
                    "type": "string",
                    "description": "DOT graph content as a string",
                },
                "options": {
                    "type": "object",
                    "description": "Operation-specific options",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": (
                                "Output format for render operation "
                                "(svg, png, pdf, json, ps, eps)"
                            ),
                        },
                        "engine": {
                            "type": "string",
                            "description": (
                                "Layout engine for render operation "
                                "(dot, neato, fdp, sfdp, twopi, circo)"
                            ),
                        },
                        "output_path": {
                            "type": "string",
                            "description": (
                                "Output file path for render operation "
                                "(auto-generated in temp dir if not provided)"
                            ),
                        },
                        "layers": {
                            "type": "array",
                            "description": (
                                "Validation layers to run "
                                "(syntax, structural, render). Defaults to all three."
                            ),
                            "items": {"type": "string"},
                        },
                        "analysis": {
                            "type": "string",
                            "enum": [
                                "stats", "reachability", "unreachable", "cycles",
                                "paths", "critical_path", "subgraph_extract", "diff",
                            ],
                            "description": (
                                "Analysis type for analyze operation"
                            ),
                        },
                        "source_node": {
                            "type": "string",
                            "description": (
                                "Source node for reachability and paths analyses"
                            ),
                        },
                        "target_node": {
                            "type": "string",
                            "description": (
                                "Target node for paths analysis"
                            ),
                        },
                        "cluster_name": {
                            "type": "string",
                            "description": (
                                "Cluster name for subgraph_extract analysis"
                            ),
                        },
                        "dot_content_b": {
                            "type": "string",
                            "description": (
                                "Second DOT content for diff analysis"
                            ),
                        },
                    },
                },
            },
            "required": ["operation"],
        }
```

**Change 6:** Replace the analyze placeholder block (lines 145-153). Replace:

```python
        if operation == "analyze":
            result = {
                "error": "analyze operation is not yet implemented (Phase 3 pending)",
                "hint": (
                    "Phase 3 will provide reachability, cycle detection, critical path, "
                    "and structural diff via networkx."
                ),
            }
            return ToolResult(success=False, output=json.dumps(result))
```

With:

```python
        if operation == "analyze":
            result = analyze.analyze_dot(dot_content, options)
            return ToolResult(success=result["success"], output=json.dumps(result))
```

**Change 7:** Update mount() log message and version (lines 181-190). Replace:

```python
    logger.info(
        "tool-dot-graph mounted: registered 'dot_graph' tool "
        "with validate/render/setup routing (Phase 2)"
    )

    return {
        "name": "tool-dot-graph",
        "version": "0.2.0",
        "provides": ["dot_graph"],
    }
```

With:

```python
    logger.info(
        "tool-dot-graph mounted: registered 'dot_graph' tool "
        "with validate/render/setup/analyze routing"
    )

    return {
        "name": "tool-dot-graph",
        "version": "0.3.0",
        "provides": ["dot_graph"],
    }
```

**Step 4: Run the integration tests**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/test_tool_integration.py -v --tb=short
```

Expected: All integration tests pass. Note: the old `test_mount_registers_real_tool` test checks for version `0.2.0` — either update it to `0.3.0` or remove it since the new `test_mount_returns_version_030` covers this. If it fails, update `test_mount_registers_real_tool` to expect `0.3.0`.

**Step 5: Run full module test suite**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: All pass

**Step 6: Run bundle tests**

Run:
```bash
cd /home/bkrabach/dev/dot-graph-bundle && python -m pytest tests/ -v --tb=short
```

Expected: All 502+ bundle tests still pass

**Step 7: Commit**

```bash
cd /home/bkrabach/dev/dot-graph-bundle && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py modules/tool-dot-graph/tests/test_tool_integration.py && git commit -m "feat: wire analyze operations into DotGraphTool, bump version to 0.3.0"
```
