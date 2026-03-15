"""Tests for analyze.py — DOT→NetworkX parsing pipeline and stats operation.

11 tests covering:
- Error handling: invalid content, empty content, unknown analysis, missing analysis key
- Stats operation: simple DAG, diamond DAG, cyclic graph, disconnected graph,
  single node, undirected graph, result field coverage

DOT fixtures defined as module-level constants.
"""


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


# ---------------------------------------------------------------------------
# Error handling tests
# ---------------------------------------------------------------------------


def test_analyze_dot_invalid_content_returns_error():
    """Invalid DOT content returns success=False with descriptive error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot("this is not dot content !!!###", {"analysis": "stats"})

    assert result["success"] is False, "Invalid DOT must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"
    assert len(result["error"]) > 0, "'error' must be a non-empty string"


def test_analyze_dot_empty_content_returns_error():
    """Empty DOT content returns success=False with descriptive error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot("", {"analysis": "stats"})

    assert result["success"] is False, "Empty DOT must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"
    assert len(result["error"]) > 0, "'error' must be non-empty"


def test_analyze_dot_unknown_analysis_returns_error():
    """Unknown analysis type returns success=False with descriptive error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(SIMPLE_DAG, {"analysis": "unknown_operation_xyz"})

    assert result["success"] is False, "Unknown analysis must return success=False"
    assert "error" in result, "Error result must have 'error' key"
    assert isinstance(result["error"], str), "'error' must be a string"


def test_analyze_dot_missing_analysis_key_returns_error():
    """Options dict missing 'analysis' key returns success=False with descriptive error."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

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
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

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
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

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
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(CYCLIC_GRAPH, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on CYCLIC_GRAPH must succeed, got: {result}"
    )
    assert result["is_dag"] is False, (
        f"CYCLIC_GRAPH must NOT be a DAG, got is_dag={result['is_dag']}"
    )


def test_stats_disconnected_graph():
    """Stats on a disconnected graph reports 2 weakly connected components."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(DISCONNECTED, {"analysis": "stats"})

    assert result["success"] is True, (
        f"Stats on DISCONNECTED must succeed, got: {result}"
    )
    assert result["weakly_connected_components"] == 2, (
        f"DISCONNECTED must have 2 WCCs, got: {result['weakly_connected_components']}"
    )


def test_stats_single_node():
    """Stats on a single-node graph returns 1 node, 0 edges, 1 component."""
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

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
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

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
    from amplifier_module_tool_dot_graph.analyze import analyze_dot

    result = analyze_dot(UNDIRECTED, {"analysis": "stats"})

    assert result["success"] is True, f"Stats on UNDIRECTED must succeed, got: {result}"
    assert result["is_directed"] is False, (
        f"UNDIRECTED must have is_directed=False, got: {result['is_directed']}"
    )
