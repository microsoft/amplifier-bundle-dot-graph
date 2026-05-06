"""Tests for analyze.py — DOT→NetworkX parsing pipeline and stats operation.

11 tests covering:
- Error handling: invalid content, empty content, unknown analysis, missing analysis key
- Stats operation: simple DAG, diamond DAG, cyclic graph, disconnected graph,
  single node, undirected graph, result field coverage
- Subgraph extract: existing cluster, nonexistent cluster, missing option, label preservation
- Diff: added nodes, removed edges, added edges, identical graphs, missing option, invalid content

DOT fixtures defined as module-level constants.
"""

import pydot

from amplifier_module_tool_dot_graph.analyze import analyze_dot


# ---------------------------------------------------------------------------
# DOT Fixtures (module-level constants)
# ---------------------------------------------------------------------------

# 4 nodes, 3 edges — linear chain, is_dag=True
SIMPLE_DAG = "digraph G { a -> b; b -> c; c -> d }"

# 4 nodes, 4 edges — diamond shape, is_dag=True, density is float
DIAMOND_DAG = "digraph G { a -> b; a -> c; b -> d; c -> d }"

# 3 nodes, 3 edges — cycle: a->b->c->a, is_dag=False
CYCLIC_GRAPH = "digraph G { a -> b; b -> c; c -> a }"

# 4 nodes, 2 edges — two disconnected components: a->b and c->d
DISCONNECTED = "digraph G { a -> b; c -> d }"

# 1 node, 0 edges
SINGLE_NODE = "digraph G { a }"

# Empty digraph (no nodes or edges)
EMPTY_GRAPH = "digraph G {}"

# Undirected graph — is_directed=False
UNDIRECTED = "graph G { a -- b -- c }"

# 6 nodes, 6 edges — complex DAG with multiple branches
COMPLEX_DAG = "digraph G { a -> b; a -> c; b -> d; c -> d; d -> e; d -> f }"

# Two-layer fan-out: a -> {b0..b10} -> {c0..c9} -> z gives 11*10 = 110 simple paths.
# Used to verify the 100-path cap triggers truncated=True.
PATHS_OVER_CAP = (
    "digraph G { "
    + " ".join(f"a -> b{i};" for i in range(11))
    + " ".join(f"b{i} -> c{j};" for i in range(11) for j in range(10))
    + " ".join(f"c{j} -> z;" for j in range(10))
    + " }"
)

# Digraph with two clusters: cluster_core (x→y→z, label="Core") and
# cluster_util (u→v, label="Util"), plus cross-cluster edges x→u and z→v.
CLUSTERED_DOT = """digraph G {
    subgraph cluster_core {
        label = "Core";
        x -> y;
        y -> z;
    }
    subgraph cluster_util {
        label = "Util";
        u -> v;
    }
    x -> u;
    z -> v;
}"""

# Linear chain: a→b→c→d
DOT_V1 = "digraph G { a -> b; b -> c; c -> d }"

# Modified version: a→b→c→e and d→e (c→d removed, c→e and d→e added, 'e' is new node)
DOT_V2 = "digraph G { a -> b; b -> c; c -> e; d -> e }"


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


def test_analyze_dot_invalid_content_returns_error():
    """Invalid DOT content returns success=False with descriptive error."""
    result = analyze_dot("this is not dot content !!!###", {"analysis": "stats"})

    assert result["success"] is False, "Invalid DOT must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"
    assert len(result["error"]) > 0, "'error' must be a non-empty string"


def test_analyze_dot_empty_content_returns_error():
    """Empty DOT content returns success=False with descriptive error."""
    result = analyze_dot("", {"analysis": "stats"})

    assert result["success"] is False, "Empty DOT must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"
    assert len(result["error"]) > 0, "'error' must be non-empty"


def test_analyze_dot_unknown_analysis_returns_error():
    """Unknown analysis type returns success=False with descriptive error."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "unknown_operation_xyz"})

    assert result["success"] is False, "Unknown analysis must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"


def test_analyze_dot_missing_analysis_key_returns_error():
    """Options dict missing 'analysis' key returns success=False with descriptive error."""
    # Options provided but without 'analysis' key
    result = analyze_dot(SIMPLE_DAG, {"some_other_key": "value"})

    assert result["success"] is False, "Missing analysis key must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"


# ---------------------------------------------------------------------------
# Stats operation tests
# ---------------------------------------------------------------------------


def test_stats_simple_dag():
    """Stats on a simple 4-node, 3-edge DAG returns correct counts and is_dag=True."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "stats"})

    assert result["success"] is True, f"Stats on valid DAG must succeed, got: {result}"
    assert result["node_count"] == 4, (
        f"SIMPLE_DAG must have 4 nodes, got: {result['node_count']}"
    )
    assert result["edge_count"] == 3, (
        f"SIMPLE_DAG must have 3 edges, got: {result['edge_count']}"
    )
    assert result["is_dag"] is True, (
        f"SIMPLE_DAG must be a DAG, got is_dag={result['is_dag']}"
    )
    assert result["is_directed"] is True, (
        f"SIMPLE_DAG must be directed, got is_directed={result['is_directed']}"
    )


def test_stats_diamond_dag():
    """Stats on a 4-node diamond DAG returns correct counts and float density."""
    result = analyze_dot(DIAMOND_DAG, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on DIAMOND_DAG must succeed, got: {result}"
    )
    assert result["node_count"] == 4, (
        f"DIAMOND_DAG must have 4 nodes, got: {result['node_count']}"
    )
    assert result["edge_count"] == 4, (
        f"DIAMOND_DAG must have 4 edges, got: {result['edge_count']}"
    )
    assert isinstance(result["density"], float), (
        f"density must be a float, got: {type(result['density'])}"
    )
    assert result["density"] > 0.0, (
        f"DIAMOND_DAG density must be > 0, got: {result['density']}"
    )
    assert result["is_dag"] is True, "DIAMOND_DAG must be a DAG (no cycles)"


def test_stats_cyclic_graph():
    """Stats on a cyclic graph returns is_dag=False."""
    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on CYCLIC_GRAPH must succeed, got: {result}"
    )
    assert result["is_dag"] is False, (
        f"CYCLIC_GRAPH must NOT be a DAG, got is_dag={result['is_dag']}"
    )


def test_stats_disconnected_graph():
    """Stats on a disconnected graph reports 2 weakly connected components."""
    result = analyze_dot(DISCONNECTED, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on DISCONNECTED must succeed, got: {result}"
    )
    assert result["weakly_connected_components"] == 2, (
        f"DISCONNECTED must have 2 WCCs, got: {result['weakly_connected_components']}"
    )


def test_stats_single_node():
    """Stats on a single-node graph returns 1 node, 0 edges, 1 component."""
    result = analyze_dot(SINGLE_NODE, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on SINGLE_NODE must succeed, got: {result}"
    )
    assert result["node_count"] == 1, (
        f"SINGLE_NODE must have 1 node, got: {result['node_count']}"
    )
    assert result["edge_count"] == 0, (
        f"SINGLE_NODE must have 0 edges, got: {result['edge_count']}"
    )


def test_stats_result_has_all_fields():
    """Stats result includes all required fields: node_count, edge_count, density,
    is_directed, is_dag, weakly_connected_components, self_loops, nodes, operation, success."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "stats"})

    assert result["success"] is True, f"Stats must succeed, got: {result}"

    required_fields = [
        "success",
        "operation",
        "node_count",
        "edge_count",
        "density",
        "is_directed",
        "is_dag",
        "weakly_connected_components",
        "self_loops",
        "nodes",
    ]
    for field in required_fields:
        assert field in result, (
            f"Stats result must include '{field}', got keys: {list(result.keys())}"
        )

    assert result["operation"] == "stats", (
        f"operation must be 'stats', got: {result['operation']}"
    )
    assert isinstance(result["nodes"], list), (
        f"'nodes' must be a list, got: {type(result['nodes'])}"
    )
    assert len(result["nodes"]) == result["node_count"], (
        f"len(nodes) must equal node_count: {len(result['nodes'])} != {result['node_count']}"
    )


def test_stats_undirected_graph():
    """Stats on an undirected graph returns is_directed=False."""
    result = analyze_dot(UNDIRECTED, {"analysis": "stats"})

    assert result["success"] is True, f"Stats on UNDIRECTED must succeed, got: {result}"
    assert result["is_directed"] is False, (
        f"UNDIRECTED must have is_directed=False, got: {result['is_directed']}"
    )


# ---------------------------------------------------------------------------
# DOT fixtures for reachability / unreachable / cycles tests
# ---------------------------------------------------------------------------

# Graph with an entry hint node ('start') and an orphan ('orphan')
ENTRY_HINT_GRAPH = "digraph G { start -> a; orphan -> b }"


# ---------------------------------------------------------------------------
# Reachability operation tests
# ---------------------------------------------------------------------------


def test_reachability_from_source():
    """Reachability from 'a' in a linear chain a→b→c→d returns [b, c, d]."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability", "source_node": "a"})

    assert result["success"] is True, f"Reachability must succeed, got: {result}"
    assert result["reachable"] == ["b", "c", "d"], (
        f"From 'a' in SIMPLE_DAG must reach [b,c,d], got: {result['reachable']}"
    )


def test_reachability_from_leaf():
    """Reachability from the leaf node 'd' in a linear chain returns []."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability", "source_node": "d"})

    assert result["success"] is True, (
        f"Reachability from leaf must succeed, got: {result}"
    )
    assert result["reachable"] == [], (
        f"Leaf node 'd' can reach nobody, got: {result['reachable']}"
    )


def test_reachability_missing_source_node():
    """Missing 'source_node' option returns error mentioning 'source_node'."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability"})

    assert result["success"] is False, "Missing source_node must return success=False"
    assert "source_node" in result["error"], (
        f"Error must mention 'source_node', got: {result['error']}"
    )


def test_reachability_nonexistent_node():
    """Non-existent source node returns error mentioning the node name."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability", "source_node": "z"})

    assert result["success"] is False, "Non-existent node must return success=False"
    assert "z" in result["error"], (
        f"Error must mention the node name 'z', got: {result['error']}"
    )


def test_reachability_in_cyclic_graph():
    """Reachability from 'a' in a→b→c→a cycle returns [b, c] (not 'a' itself)."""
    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "reachability", "source_node": "a"})

    assert result["success"] is True, (
        f"Reachability in cyclic graph must succeed, got: {result}"
    )
    assert set(result["reachable"]) == {"b", "c"}, (
        f"From 'a' in CYCLIC_GRAPH must reach {{b,c}}, got: {result['reachable']}"
    )


def test_reachability_result_has_all_fields():
    """Reachability result includes required fields: success, operation, source_node,
    reachable, reachable_count."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "reachability", "source_node": "a"})

    assert result["success"] is True, f"Reachability must succeed, got: {result}"

    required_fields = [
        "success",
        "operation",
        "source_node",
        "reachable",
        "reachable_count",
    ]
    for field in required_fields:
        assert field in result, (
            f"Reachability result must include '{field}', got keys: {list(result.keys())}"
        )

    assert result["operation"] == "reachability", (
        f"operation must be 'reachability', got: {result['operation']}"
    )
    assert result["source_node"] == "a", (
        f"source_node must echo the input 'a', got: {result['source_node']}"
    )
    assert result["reachable_count"] == len(result["reachable"]), (
        f"reachable_count must equal len(reachable): "
        f"{result['reachable_count']} != {len(result['reachable'])}"
    )


# ---------------------------------------------------------------------------
# Unreachable operation tests
# ---------------------------------------------------------------------------


def test_unreachable_in_disconnected_graph():
    """Disconnected graph with a→b and c→d: nodes 'a' and 'c' have no in-edges → unreachable."""
    result = analyze_dot(DISCONNECTED, {"analysis": "unreachable"})

    assert result["success"] is True, f"Unreachable must succeed, got: {result}"
    unreachable = result["unreachable"]
    assert "a" in unreachable, f"'a' must be unreachable, got: {unreachable}"
    assert "c" in unreachable, f"'c' must be unreachable, got: {unreachable}"
    assert "b" not in unreachable, (
        f"'b' has in-edges and must not be unreachable, got: {unreachable}"
    )
    assert "d" not in unreachable, (
        f"'d' has in-edges and must not be unreachable, got: {unreachable}"
    )


def test_unreachable_entry_hints_excluded():
    """Entry hint nodes (e.g. 'start') are excluded from unreachable; orphan nodes are included."""
    result = analyze_dot(ENTRY_HINT_GRAPH, {"analysis": "unreachable"})

    assert result["success"] is True, (
        f"Unreachable on ENTRY_HINT_GRAPH must succeed, got: {result}"
    )
    unreachable = result["unreachable"]
    assert "start" not in unreachable, (
        f"'start' is an entry hint and must be excluded, got: {unreachable}"
    )
    assert "orphan" in unreachable, (
        f"'orphan' has no in-edges and is not a hint, must be unreachable, got: {unreachable}"
    )


def test_unreachable_fully_connected():
    """Cyclic graph (all nodes have in-degree >= 1) returns empty unreachable list."""
    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "unreachable"})

    assert result["success"] is True, (
        f"Unreachable on CYCLIC_GRAPH must succeed, got: {result}"
    )
    assert result["unreachable"] == [], (
        f"All nodes in CYCLIC_GRAPH have in-edges; unreachable must be [], got: {result['unreachable']}"
    )


def test_unreachable_returns_annotated_dot():
    """Unreachable analysis returns annotated_dot with unreachable nodes colored red."""
    result = analyze_dot(DISCONNECTED, {"analysis": "unreachable"})

    assert result["success"] is True, f"Unreachable must succeed, got: {result}"
    assert "annotated_dot" in result, "Result must include 'annotated_dot'"
    assert isinstance(result["annotated_dot"], str), "annotated_dot must be a string"
    assert "red" in result["annotated_dot"], (
        f"annotated_dot must contain 'red' for unreachable nodes, got:\n{result['annotated_dot']}"
    )


# ---------------------------------------------------------------------------
# Cycles operation tests
# ---------------------------------------------------------------------------


def test_cycles_in_cyclic_graph():
    """Cycle detection in a→b→c→a returns has_cycles=True with the cycle nodes a,b,c."""
    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "cycles"})

    assert result["success"] is True, f"Cycles must succeed, got: {result}"
    assert result["has_cycles"] is True, "CYCLIC_GRAPH must have cycles"
    assert result["cycle_count"] >= 1, "cycle_count must be at least 1"
    # Each cycle is sorted; check a,b,c appear in the cycles
    all_cycle_nodes: set[str] = set()
    for cycle in result["cycles"]:
        all_cycle_nodes.update(cycle)
    assert {"a", "b", "c"}.issubset(all_cycle_nodes), (
        f"Cycle must contain a, b, c; got cycles: {result['cycles']}"
    )


def test_cycles_in_dag():
    """Cycle detection in a DAG returns has_cycles=False and empty cycles list."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "cycles"})

    assert result["success"] is True, f"Cycles on DAG must succeed, got: {result}"
    assert result["has_cycles"] is False, "SIMPLE_DAG has no cycles"
    assert result["cycles"] == [], (
        f"SIMPLE_DAG cycles must be [], got: {result['cycles']}"
    )


def test_cycles_returns_annotated_dot():
    """Cycle detection in a cyclic graph returns annotated_dot with cycle edges colored red."""
    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "cycles"})

    assert result["success"] is True, f"Cycles must succeed, got: {result}"
    assert "annotated_dot" in result, "Result must include 'annotated_dot'"
    assert result["annotated_dot"] is not None, (
        "annotated_dot must not be None for cyclic graph"
    )
    assert "red" in result["annotated_dot"], (
        f"annotated_dot must contain 'red' for cycle edges, got:\n{result['annotated_dot']}"
    )


def test_cycles_dag_annotated_dot_is_none():
    """Cycle detection in a DAG returns annotated_dot=None (no cycles to highlight)."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "cycles"})

    assert result["success"] is True, f"Cycles on DAG must succeed, got: {result}"
    assert result["annotated_dot"] is None, (
        f"DAG has no cycles so annotated_dot must be None, got: {result['annotated_dot']}"
    )


# ---------------------------------------------------------------------------
# Paths operation tests
# ---------------------------------------------------------------------------


def test_paths_simple():
    """Paths from 'a' to 'd' in linear DAG a->b->c->d returns single path [a,b,c,d]."""
    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "paths", "source_node": "a", "target_node": "d"}
    )

    assert result["success"] is True, f"Paths must succeed, got: {result}"
    assert result["path_count"] == 1, (
        f"Linear DAG must have exactly 1 path, got: {result['path_count']}"
    )
    assert result["paths"] == [["a", "b", "c", "d"]], (
        f"Single path must be [a,b,c,d], got: {result['paths']}"
    )
    assert result["truncated"] is False, "Single-path result must not be truncated"


def test_paths_diamond():
    """Paths from 'a' to 'd' in diamond DAG returns 2 paths."""
    result = analyze_dot(
        DIAMOND_DAG, {"analysis": "paths", "source_node": "a", "target_node": "d"}
    )

    assert result["success"] is True, f"Paths must succeed, got: {result}"
    assert result["path_count"] == 2, (
        f"Diamond DAG must have 2 paths, got: {result['path_count']}"
    )
    assert len(result["paths"]) == 2, (
        f"paths list must have 2 entries, got: {len(result['paths'])}"
    )
    for path in result["paths"]:
        assert path[0] == "a", f"Each path must start at 'a', got: {path}"
        assert path[-1] == "d", f"Each path must end at 'd', got: {path}"
    assert result["truncated"] is False


def test_paths_no_path_exists():
    """Disconnected graph: paths from 'a' to 'd' (different component) returns empty, path_count=0."""
    result = analyze_dot(
        DISCONNECTED, {"analysis": "paths", "source_node": "a", "target_node": "d"}
    )

    assert result["success"] is True, (
        f"Paths must succeed even when no path exists, got: {result}"
    )
    assert result["path_count"] == 0, (
        f"No path between components, got: {result['path_count']}"
    )
    assert result["paths"] == [], (
        f"No-path result must be empty list, got: {result['paths']}"
    )


def test_paths_missing_source():
    """Missing 'source_node' option returns error mentioning 'source_node'."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "paths", "target_node": "d"})

    assert result["success"] is False, "Missing source_node must return success=False"
    assert "source_node" in result["error"], (
        f"Error must mention 'source_node', got: {result['error']}"
    )


def test_paths_missing_target():
    """Missing 'target_node' option returns error mentioning 'target_node'."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "paths", "source_node": "a"})

    assert result["success"] is False, "Missing target_node must return success=False"
    assert "target_node" in result["error"], (
        f"Error must mention 'target_node', got: {result['error']}"
    )


def test_paths_nonexistent_source():
    """Non-existent source node returns error mentioning the node name."""
    result = analyze_dot(
        SIMPLE_DAG, {"analysis": "paths", "source_node": "z", "target_node": "d"}
    )

    assert result["success"] is False, (
        "Non-existent source node must return success=False"
    )
    assert "z" in result["error"], (
        f"Error must mention the node name 'z', got: {result['error']}"
    )


def test_paths_truncation():
    """More than 100 simple paths triggers truncation: path_count=100, truncated=True."""
    result = analyze_dot(
        PATHS_OVER_CAP, {"analysis": "paths", "source_node": "a", "target_node": "z"}
    )

    assert result["success"] is True, f"Paths must succeed, got: {result}"
    assert result["path_count"] == 100, (
        f"Truncated result must contain exactly 100 paths, got: {result['path_count']}"
    )
    assert result["truncated"] is True, "Graph with 110 paths must set truncated=True"


# ---------------------------------------------------------------------------
# Critical path operation tests
# ---------------------------------------------------------------------------


def test_critical_path_linear_dag():
    """Critical path in linear DAG a->b->c->d returns [a,b,c,d] with length 4."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "critical_path"})

    assert result["success"] is True, f"Critical path must succeed, got: {result}"
    assert result["critical_path"] == ["a", "b", "c", "d"], (
        f"Critical path must be [a,b,c,d], got: {result['critical_path']}"
    )
    assert result["length"] == 4, f"Length must be 4, got: {result['length']}"


def test_critical_path_diamond_dag():
    """Critical path in diamond DAG has length 3, starts with 'a', ends with 'd'."""
    result = analyze_dot(DIAMOND_DAG, {"analysis": "critical_path"})

    assert result["success"] is True, f"Critical path must succeed, got: {result}"
    assert result["length"] == 3, (
        f"Diamond critical path length must be 3, got: {result['length']}"
    )
    assert result["critical_path"][0] == "a", (
        f"Critical path must start with 'a', got: {result['critical_path']}"
    )
    assert result["critical_path"][-1] == "d", (
        f"Critical path must end with 'd', got: {result['critical_path']}"
    )


def test_critical_path_complex_dag():
    """Critical path in complex DAG (a->b->d->e and similar) has length >= 4."""
    result = analyze_dot(COMPLEX_DAG, {"analysis": "critical_path"})

    assert result["success"] is True, f"Critical path must succeed, got: {result}"
    assert result["length"] >= 4, (
        f"Complex DAG critical path length must be >= 4, got: {result['length']}"
    )
    assert isinstance(result["critical_path"], list), "critical_path must be a list"
    assert len(result["critical_path"]) == result["length"], (
        f"len(critical_path) must equal length: "
        f"{len(result['critical_path'])} != {result['length']}"
    )


def test_critical_path_on_cyclic_graph():
    """Critical path on a cyclic graph returns success=False with error mentioning cycle or dag."""
    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "critical_path"})

    assert result["success"] is False, (
        "Critical path on cyclic graph must return success=False"
    )
    error_lower = result["error"].lower()
    assert "cycle" in error_lower or "dag" in error_lower, (
        f"Error must mention 'cycle' or 'dag', got: {result['error']}"
    )


def test_critical_path_single_node():
    """Critical path on a single-node graph returns [a] with length 1."""
    result = analyze_dot(SINGLE_NODE, {"analysis": "critical_path"})

    assert result["success"] is True, (
        f"Critical path on single node must succeed, got: {result}"
    )
    assert result["critical_path"] == ["a"], (
        f"Single node critical path must be ['a'], got: {result['critical_path']}"
    )
    assert result["length"] == 1, (
        f"Single node length must be 1, got: {result['length']}"
    )


# ---------------------------------------------------------------------------
# Subgraph extract operation tests
# ---------------------------------------------------------------------------


def test_subgraph_extract_existing_cluster():
    """Extracting cluster_core from CLUSTERED_DOT returns 3 nodes (x,y,z) and parseable DOT."""
    result = analyze_dot(
        CLUSTERED_DOT,
        {"analysis": "subgraph_extract", "cluster_name": "cluster_core"},
    )

    assert result["success"] is True, f"Subgraph extract must succeed, got: {result}"
    assert result["node_count"] == 3, (
        f"cluster_core has 3 nodes (x, y, z), got: {result['node_count']}"
    )
    assert "extracted_dot" in result, "Result must include 'extracted_dot'"
    # Result must be parseable DOT
    parsed = pydot.graph_from_dot_data(result["extracted_dot"])
    assert parsed is not None and len(parsed) > 0, (
        f"extracted_dot must be parseable DOT, got:\n{result.get('extracted_dot')}"
    )


def test_subgraph_extract_nonexistent_cluster():
    """Extracting a nonexistent cluster returns error mentioning the name and 'available'."""
    result = analyze_dot(
        CLUSTERED_DOT,
        {"analysis": "subgraph_extract", "cluster_name": "cluster_nonexistent"},
    )

    assert result["success"] is False, "Nonexistent cluster must return success=False"
    assert "cluster_nonexistent" in result["error"], (
        f"Error must mention the cluster name, got: {result['error']}"
    )
    assert "available" in result["error"].lower(), (
        f"Error must mention 'available', got: {result['error']}"
    )


def test_subgraph_extract_missing_cluster_name():
    """Missing 'cluster_name' option returns error mentioning 'cluster_name'."""
    result = analyze_dot(CLUSTERED_DOT, {"analysis": "subgraph_extract"})

    assert result["success"] is False, "Missing cluster_name must return success=False"
    assert "cluster_name" in result["error"], (
        f"Error must mention 'cluster_name', got: {result['error']}"
    )


def test_subgraph_extract_preserves_label():
    """Extracted cluster DOT preserves the label attribute ('Core' for cluster_core)."""
    result = analyze_dot(
        CLUSTERED_DOT,
        {"analysis": "subgraph_extract", "cluster_name": "cluster_core"},
    )

    assert result["success"] is True, f"Subgraph extract must succeed, got: {result}"
    assert "Core" in result["extracted_dot"], (
        f"Extracted DOT must preserve label 'Core', got:\n{result['extracted_dot']}"
    )


# ---------------------------------------------------------------------------
# Diff operation tests
# ---------------------------------------------------------------------------


def test_diff_detects_added_nodes():
    """Diff V1→V2 detects 'e' as an added node."""
    result = analyze_dot(DOT_V1, {"analysis": "diff", "dot_content_b": DOT_V2})

    assert result["success"] is True, f"Diff must succeed, got: {result}"
    assert "e" in result["added_nodes"], (
        f"Node 'e' must be in added_nodes, got: {result['added_nodes']}"
    )


def test_diff_detects_removed_edges():
    """Diff V1→V2 detects c→d as a removed edge."""
    result = analyze_dot(DOT_V1, {"analysis": "diff", "dot_content_b": DOT_V2})

    assert result["success"] is True, f"Diff must succeed, got: {result}"
    removed = [tuple(e) for e in result["removed_edges"]]
    assert ("c", "d") in removed, (
        f"Edge (c, d) must be in removed_edges, got: {result['removed_edges']}"
    )


def test_diff_detects_added_edges():
    """Diff V1→V2 detects c→e and d→e as added edges."""
    result = analyze_dot(DOT_V1, {"analysis": "diff", "dot_content_b": DOT_V2})

    assert result["success"] is True, f"Diff must succeed, got: {result}"
    added = [tuple(e) for e in result["added_edges"]]
    assert ("c", "e") in added, (
        f"Edge (c, e) must be in added_edges, got: {result['added_edges']}"
    )
    assert ("d", "e") in added, (
        f"Edge (d, e) must be in added_edges, got: {result['added_edges']}"
    )


def test_diff_identical_graphs():
    """Diff of a graph against itself returns all empty lists."""
    result = analyze_dot(DOT_V1, {"analysis": "diff", "dot_content_b": DOT_V1})

    assert result["success"] is True, f"Diff must succeed, got: {result}"
    assert result["added_nodes"] == [], f"No nodes added, got: {result['added_nodes']}"
    assert result["removed_nodes"] == [], (
        f"No nodes removed, got: {result['removed_nodes']}"
    )
    assert result["added_edges"] == [], f"No edges added, got: {result['added_edges']}"
    assert result["removed_edges"] == [], (
        f"No edges removed, got: {result['removed_edges']}"
    )


def test_diff_missing_dot_content_b():
    """Missing 'dot_content_b' option returns error mentioning 'dot_content_b'."""
    result = analyze_dot(DOT_V1, {"analysis": "diff"})

    assert result["success"] is False, "Missing dot_content_b must return success=False"
    assert "dot_content_b" in result["error"], (
        f"Error must mention 'dot_content_b', got: {result['error']}"
    )


def test_diff_invalid_dot_content_b():
    """Invalid DOT in dot_content_b returns success=False."""
    result = analyze_dot(
        DOT_V1, {"analysis": "diff", "dot_content_b": "this is not dot !!!###"}
    )

    assert result["success"] is False, "Invalid dot_content_b must return success=False"


# ---------------------------------------------------------------------------
# Subgraph cluster recursion tests (Improvement 2)
# ---------------------------------------------------------------------------

# DOT where ALL nodes live inside subgraph clusters — no top-level edges.
# A flat pydot walk returns 0 nodes; the recursive fix returns all 5.
ALL_IN_CLUSTERS_DOT = """digraph G {
    subgraph cluster_a {
        a -> b;
        b -> c;
    }
    subgraph cluster_b {
        x -> y;
    }
}"""

# DOT with deeply-nested clusters (cluster inside cluster).
NESTED_CLUSTERS_DOT = """digraph G {
    subgraph cluster_outer {
        subgraph cluster_inner {
            p -> q;
            q -> r;
        }
        r -> s;
    }
}"""


def test_stats_all_nodes_in_clusters_returns_correct_count():
    """Stats on a DOT where every node is inside subgraph clusters returns
    the correct node/edge count (not 0).

    Without the recursive subgraph walk, from_pydot sees no top-level nodes
    or edges and returns node_count=0.  With the fix, all 5 nodes are found.
    """
    result = analyze_dot(ALL_IN_CLUSTERS_DOT, {"analysis": "stats"})

    assert result["success"] is True, f"Stats must succeed, got: {result}"
    assert result["node_count"] == 5, (
        f"ALL_IN_CLUSTERS_DOT has 5 nodes (a,b,c,x,y), got: {result['node_count']} — "
        "subgraph recursion may be missing"
    )
    assert result["edge_count"] == 3, (
        f"ALL_IN_CLUSTERS_DOT has 3 edges, got: {result['edge_count']}"
    )


def test_stats_deeply_nested_clusters_returns_correct_count():
    """Stats on a DOT with clusters nested two levels deep returns correct counts."""
    result = analyze_dot(NESTED_CLUSTERS_DOT, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on nested clusters must succeed, got: {result}"
    )
    assert result["node_count"] == 4, (
        f"NESTED_CLUSTERS_DOT has 4 nodes (p,q,r,s), got: {result['node_count']}"
    )
    assert result["edge_count"] == 3, (
        f"NESTED_CLUSTERS_DOT has 3 edges, got: {result['edge_count']}"
    )


def test_stats_clustered_dot_includes_cross_cluster_nodes():
    """Stats on CLUSTERED_DOT (cross-cluster edges at top level) counts all nodes
    from both clusters and top-level edges."""
    result = analyze_dot(CLUSTERED_DOT, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on CLUSTERED_DOT must succeed, got: {result}"
    )
    # cluster_core: x->y->z (3 nodes), cluster_util: u->v (2 nodes)
    # Top-level: x->u, z->v (no new nodes; x,u,z,v already in clusters)
    assert result["node_count"] == 5, (
        f"CLUSTERED_DOT has 5 nodes (x,y,z,u,v), got: {result['node_count']}"
    )
    assert result["edge_count"] == 5, (
        f"CLUSTERED_DOT has 5 edges (x->y, y->z, u->v, x->u, z->v), "
        f"got: {result['edge_count']}"
    )


def test_stats_simple_dag_unaffected_by_subgraph_fix():
    """Stats on a flat (no-cluster) DAG still works correctly after the fix."""
    result = analyze_dot(SIMPLE_DAG, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on SIMPLE_DAG must still succeed, got: {result}"
    )
    assert result["node_count"] == 4, (
        f"SIMPLE_DAG still has 4 nodes, got: {result['node_count']}"
    )
    assert result["edge_count"] == 3, (
        f"SIMPLE_DAG still has 3 edges, got: {result['edge_count']}"
    )


# ---------------------------------------------------------------------------
# Producer/consumer operation fixtures
# ---------------------------------------------------------------------------

# Pipeline with proper producer/consumer declarations — all condition keys match
PIPELINE_WITH_PRODUCERS = '''digraph pipeline {
    Start [shape=ellipse]
    Eval [shape=parallelogram tool_outputs="verdict,confidence" parse_json=true]
    Approve [shape=box]
    Retry [shape=box]
    Start -> Eval
    Eval -> Approve [condition="verdict=approved"]
    Eval -> Retry [condition="verdict=rejected"]
}'''

# Pipeline where a condition references a key no producer declares
PIPELINE_UNMATCHED = '''digraph pipeline {
    Start [shape=ellipse]
    Eval [shape=parallelogram tool_outputs="verdict" parse_json=true]
    Route [shape=diamond]
    End [shape=ellipse]
    Start -> Eval
    Eval -> Route
    Route -> End [condition="nonexistent_key=yes"]
}'''

# Pipeline with no condition edges — valid graph, nothing to analyse
PIPELINE_NO_CONDITIONS = '''digraph pipeline {
    A [shape=box]
    B [shape=box]
    A -> B
}'''

# Pipeline with conditions but no tool_outputs declarations — all keys unmatched
PIPELINE_NO_PRODUCERS = '''digraph pipeline {
    A [shape=box]
    B [shape=box]
    A -> B [condition="status=done"]
}'''

# Pipeline where the producer is DOWNSTREAM of the condition edge (not an ancestor)
PIPELINE_DOWNSTREAM_PRODUCER = '''digraph pipeline {
    Start [shape=ellipse]
    Router [shape=diamond]
    Worker [shape=parallelogram tool_outputs="result" parse_json=true]
    End [shape=ellipse]
    Start -> Router
    Router -> Worker
    Router -> End [condition="result=ok"]
    Worker -> End
}'''

# Pipeline with the producer node inside a subgraph cluster
PIPELINE_CLUSTERED_PRODUCER = '''digraph pipeline {
    subgraph cluster_eval {
        Eval [shape=parallelogram tool_outputs="verdict" parse_json=true]
    }
    Start -> Eval
    Eval -> End [condition="verdict=approved"]
}'''

# Pipeline testing all condition formats: key=value, key!=value, key=
PIPELINE_CONDITION_FORMATS = '''digraph pipeline {
    A [shape=parallelogram tool_outputs="status,flag,mode" parse_json=true]
    A -> B [condition="status=ok"]
    A -> C [condition="flag!=yes"]
    A -> D [condition="mode="]
}'''


# ---------------------------------------------------------------------------
# Producer/consumer operation tests
# ---------------------------------------------------------------------------


def test_producer_consumer_all_matched():
    """All condition keys have upstream producers: unmatched_keys is empty."""
    result = analyze_dot(PIPELINE_WITH_PRODUCERS, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    assert result["unmatched_keys"] == [], (
        f"All keys should be matched; unmatched_keys must be [], "
        f"got: {result['unmatched_keys']}"
    )
    matched_key_names = [m["key"] for m in result["matched_keys"]]
    assert "verdict" in matched_key_names, (
        f"'verdict' must be in matched_keys, got: {matched_key_names}"
    )


def test_producer_consumer_unmatched_key():
    """Condition referencing a key no producer declares appears in unmatched_keys."""
    result = analyze_dot(PIPELINE_UNMATCHED, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    unmatched_key_names = [u["key"] for u in result["unmatched_keys"]]
    assert "nonexistent_key" in unmatched_key_names, (
        f"'nonexistent_key' must be in unmatched_keys, got: {unmatched_key_names}"
    )


def test_producer_consumer_no_conditions():
    """Graph with no condition edges returns success with empty matched/unmatched lists."""
    result = analyze_dot(PIPELINE_NO_CONDITIONS, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    assert result["matched_keys"] == [], (
        f"No condition edges: matched_keys must be [], got: {result['matched_keys']}"
    )
    assert result["unmatched_keys"] == [], (
        f"No condition edges: unmatched_keys must be [], got: {result['unmatched_keys']}"
    )
    assert result["total_condition_edges"] == 0, (
        f"No condition edges: total must be 0, got: {result['total_condition_edges']}"
    )


def test_producer_consumer_no_producers():
    """Conditions exist but no tool_outputs declared: all condition keys are unmatched."""
    result = analyze_dot(PIPELINE_NO_PRODUCERS, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    assert result["total_producers"] == 0, (
        f"No tool_outputs: total_producers must be 0, got: {result['total_producers']}"
    )
    unmatched_key_names = [u["key"] for u in result["unmatched_keys"]]
    assert "status" in unmatched_key_names, (
        f"'status' must be in unmatched_keys when no producers, got: {unmatched_key_names}"
    )
    assert result["matched_keys"] == [], (
        f"No producers: matched_keys must be [], got: {result['matched_keys']}"
    )


def test_producer_consumer_undirected_error():
    """Undirected graph returns success=False with a descriptive error."""
    result = analyze_dot(UNDIRECTED, {"analysis": "producer_consumer"})

    assert result["success"] is False, (
        "producer_consumer on an undirected graph must return success=False"
    )
    assert "error" in result, "Error result must have 'error' key"
    assert "directed" in result["error"].lower(), (
        f"Error must mention 'directed', got: {result['error']}"
    )


def test_producer_consumer_result_fields():
    """Result includes all expected top-level fields with correct types."""
    result = analyze_dot(PIPELINE_WITH_PRODUCERS, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"

    required_fields = [
        "success",
        "operation",
        "total_condition_edges",
        "total_condition_keys",
        "total_producers",
        "matched_keys",
        "unmatched_keys",
        "producers",
        "annotated_dot",
    ]
    for field in required_fields:
        assert field in result, (
            f"Result must include '{field}', got keys: {list(result.keys())}"
        )

    assert result["operation"] == "producer_consumer", (
        f"operation must be 'producer_consumer', got: {result['operation']}"
    )
    assert isinstance(result["matched_keys"], list), "'matched_keys' must be a list"
    assert isinstance(result["unmatched_keys"], list), "'unmatched_keys' must be a list"
    assert isinstance(result["producers"], dict), "'producers' must be a dict"
    assert isinstance(result["annotated_dot"], str), "'annotated_dot' must be a string"
    assert isinstance(result["total_condition_edges"], int), (
        "'total_condition_edges' must be an int"
    )
    assert isinstance(result["total_condition_keys"], int), (
        "'total_condition_keys' must be an int"
    )
    assert isinstance(result["total_producers"], int), "'total_producers' must be an int"


def test_producer_consumer_upstream_reachability():
    """A producer that is DOWNSTREAM of the condition edge source is not counted upstream.

    In PIPELINE_DOWNSTREAM_PRODUCER:
      Router -> End [condition="result=ok"]
    Worker (which declares tool_outputs="result") is a child of Router, not an ancestor.
    Therefore 'result' must appear in unmatched_keys even though a producer exists.
    """
    result = analyze_dot(PIPELINE_DOWNSTREAM_PRODUCER, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    unmatched_key_names = [u["key"] for u in result["unmatched_keys"]]
    assert "result" in unmatched_key_names, (
        f"'result' must be unmatched (Worker is downstream of Router, not upstream); "
        f"got unmatched: {unmatched_key_names}"
    )


def test_producer_consumer_condition_parsing():
    """All three condition formats are parsed to correct keys.

    PIPELINE_CONDITION_FORMATS has A -> B [condition="status=ok"],
    A -> C [condition="flag!=yes"], A -> D [condition="mode="].
    Node A produces status, flag, mode — all edges should be matched.
    """
    result = analyze_dot(PIPELINE_CONDITION_FORMATS, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    assert result["unmatched_keys"] == [], (
        f"All condition formats should parse and match producers; "
        f"unmatched_keys must be [], got: {result['unmatched_keys']}"
    )
    matched_key_names = [m["key"] for m in result["matched_keys"]]
    assert "status" in matched_key_names, (
        f"'status' (from key=value) must be matched, got: {matched_key_names}"
    )
    assert "flag" in matched_key_names, (
        f"'flag' (from key!=value) must be matched, got: {matched_key_names}"
    )
    assert "mode" in matched_key_names, (
        f"'mode' (from key=) must be matched, got: {matched_key_names}"
    )
    assert result["total_condition_edges"] == 3, (
        f"3 condition edges, got: {result['total_condition_edges']}"
    )
    assert result["total_condition_keys"] == 3, (
        f"3 unique condition keys, got: {result['total_condition_keys']}"
    )


def test_producer_consumer_clustered_nodes():
    """Producer nodes declared inside subgraph clusters are found via recursive walk."""
    result = analyze_dot(PIPELINE_CLUSTERED_PRODUCER, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    # Eval is inside cluster_eval but must still be registered as a producer.
    assert "Eval" in result["producers"], (
        f"Eval (inside cluster) must appear in producers dict, got: {result['producers']}"
    )
    assert result["unmatched_keys"] == [], (
        f"'verdict' should be matched via clustered Eval; unmatched_keys must be [], "
        f"got: {result['unmatched_keys']}"
    )


def test_producer_consumer_annotated_dot():
    """Unmatched condition edges are highlighted red in annotated_dot."""
    result = analyze_dot(PIPELINE_UNMATCHED, {"analysis": "producer_consumer"})

    assert result["success"] is True, f"producer_consumer must succeed, got: {result}"
    assert "annotated_dot" in result, "Result must include 'annotated_dot'"
    assert isinstance(result["annotated_dot"], str), "'annotated_dot' must be a string"
    assert "red" in result["annotated_dot"], (
        f"annotated_dot must contain 'red' for unmatched edges, "
        f"got:\n{result['annotated_dot']}"
    )
