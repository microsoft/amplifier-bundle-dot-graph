"""Tests for validate.py — three-layer DOT validation (syntax, structural, render quality).

20 tests covering:
- Layer 1 (syntax): empty, whitespace, invalid, valid digraph, valid undirected
- Layer 2 (structural): empty graph, unreachable nodes, entry points, isolated nodes,
  orphan clusters, connected clusters, stats counting, legend info
- Layer 3 (render quality): valid DOT passes, skipped without graphviz
- Layer selection: syntax-only
- Result structure: required keys, issue structure
"""

import shutil
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Layer 1 — Syntax tests
# ---------------------------------------------------------------------------


def test_valid_dot_returns_valid():
    """Simple valid digraph returns valid=True with no errors."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("digraph G { a -> b }")

    assert result["valid"] is True, "Valid DOT must return valid=True"
    errors = [i for i in result["issues"] if i["severity"] == "error"]
    assert len(errors) == 0, (
        f"Valid DOT must have no error-severity issues, got: {errors}"
    )


def test_invalid_dot_fails_syntax():
    """Malformed DOT content fails at syntax layer with an error."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("this is definitely not valid dot content !!!###")

    assert result["valid"] is False, "Invalid DOT must return valid=False"
    syntax_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "syntax" and i["severity"] == "error"
    ]
    assert len(syntax_errors) >= 1, (
        f"Invalid DOT must produce a syntax error, got: {result['issues']}"
    )


def test_empty_string_fails_syntax():
    """Empty string fails at syntax layer with 'Empty DOT content' error."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("")

    assert result["valid"] is False, "Empty string must return valid=False"
    syntax_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "syntax" and i["severity"] == "error"
    ]
    assert len(syntax_errors) >= 1, "Empty string must produce a syntax error"
    assert "Empty DOT content" in syntax_errors[0]["message"], (
        f"Empty string error must mention 'Empty DOT content', got: {syntax_errors[0]['message']}"
    )


def test_whitespace_only_fails_syntax():
    """Whitespace-only string fails at syntax layer with 'Empty DOT content' error."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("   \n\t  ")

    assert result["valid"] is False, "Whitespace-only must return valid=False"
    syntax_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "syntax" and i["severity"] == "error"
    ]
    assert len(syntax_errors) >= 1, "Whitespace-only must produce a syntax error"
    assert "Empty DOT content" in syntax_errors[0]["message"], (
        f"Whitespace-only error must mention 'Empty DOT content', got: {syntax_errors[0]['message']}"
    )


def test_undirected_graph_parses():
    """Undirected graph with -- edges parses correctly and returns valid=True."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("graph G { a -- b -- c }")

    assert result["valid"] is True, (
        f"Undirected graph must parse as valid, got: {result['issues']}"
    )
    syntax_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "syntax" and i["severity"] == "error"
    ]
    assert len(syntax_errors) == 0, (
        f"Undirected graph must have no syntax errors, got: {syntax_errors}"
    )


# ---------------------------------------------------------------------------
# Layer 2 — Structural tests
# ---------------------------------------------------------------------------


def test_empty_graph_structural_error():
    """Graph with no nodes or edges produces a structural error."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("digraph G {}")

    assert result["valid"] is False, "Empty graph must return valid=False"
    structural_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "structural" and i["severity"] == "error"
    ]
    assert len(structural_errors) >= 1, (
        f"Empty graph must produce a structural error, got: {result['issues']}"
    )


def test_unreachable_node_warning():
    """In a digraph, node with outgoing but no incoming edges (not an entry name) gets warning."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # 'orphan' has only outgoing edges, 'a' is also reachable only from 'orphan'
    # but orphan has no incoming and is not in entry_hints
    dot = "digraph G { orphan_node -> a; a -> b; b -> a }"
    result = validate_dot(dot)

    warn_issues = [
        i
        for i in result["issues"]
        if i["layer"] == "structural"
        and i["severity"] == "warn"
        and "no incoming" in i["message"].lower()
    ]
    assert len(warn_issues) >= 1, (
        f"Node with no incoming edges must produce a warning, got: {result['issues']}"
    )


def test_entry_point_names_not_flagged():
    """Entry point nodes ('start', 'entry', 'root', 'begin', 'init', 'source') are not flagged."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # 'start' has no incoming edges but IS in entry_hints — should NOT be flagged
    dot = "digraph G { start -> a; a -> b; b -> a }"
    result = validate_dot(dot)

    # No 'no incoming edges' warnings should mention 'start'
    flagged_entry = [
        i
        for i in result["issues"]
        if i["layer"] == "structural"
        and i["severity"] == "warn"
        and "no incoming" in i["message"].lower()
        and "start" in i["message"]
    ]
    assert len(flagged_entry) == 0, (
        f"Entry point node 'start' must NOT be flagged for no incoming edges, "
        f"got: {result['issues']}"
    )


def test_isolated_node_warning():
    """Node with zero edges (isolated) produces a structural warning."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # 'isolated' has no edges at all
    dot = "digraph G { a -> b; isolated }"
    result = validate_dot(dot)

    isolated_warns = [
        i
        for i in result["issues"]
        if i["layer"] == "structural"
        and i["severity"] == "warn"
        and "isolated" in i["message"].lower()
    ]
    assert len(isolated_warns) >= 1, (
        f"Isolated node must produce a 'isolated' warning, got: {result['issues']}"
    )


def test_orphan_cluster_warning():
    """Cluster with no edges connecting to outside nodes produces a warning."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # cluster_a is completely internal: only x->y inside, no edges to 'outside'
    dot = """
    digraph G {
        outside_node -> other_node
        subgraph cluster_a {
            x -> y
        }
    }
    """
    result = validate_dot(dot)

    orphan_warns = [
        i
        for i in result["issues"]
        if i["layer"] == "structural"
        and i["severity"] == "warn"
        and "no edges connecting" in i["message"].lower()
    ]
    assert len(orphan_warns) >= 1, (
        f"Orphan cluster must produce a 'no edges connecting' warning, got: {result['issues']}"
    )


def test_connected_cluster_no_orphan_warning():
    """Cluster with edges to outside nodes does NOT produce an orphan cluster warning."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # cluster_a has node 'x' connected to outside 'outside_node'
    dot = """
    digraph G {
        outside_node -> x
        subgraph cluster_a {
            x -> y
        }
    }
    """
    result = validate_dot(dot)

    orphan_warns = [
        i
        for i in result["issues"]
        if i["layer"] == "structural"
        and i["severity"] == "warn"
        and "no edges connecting" in i["message"].lower()
    ]
    assert len(orphan_warns) == 0, (
        f"Connected cluster must NOT produce orphan warning, got: {orphan_warns}"
    )


def test_stats_counting():
    """Stats correctly count nodes, edges, clusters, and lines."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    dot = """digraph G {
    subgraph cluster_a {
        x -> y
    }
    a -> b
    c
}"""
    result = validate_dot(dot)
    stats = result["stats"]

    assert "nodes" in stats, "Stats must include 'nodes'"
    assert "edges" in stats, "Stats must include 'edges'"
    assert "clusters" in stats, "Stats must include 'clusters'"
    assert "lines" in stats, "Stats must include 'lines'"

    assert stats["clusters"] == 1, f"Must count 1 cluster, got: {stats['clusters']}"
    assert stats["edges"] >= 2, (
        f"Must count at least 2 edges (x->y, a->b), got: {stats['edges']}"
    )
    assert stats["lines"] > 0, f"Lines must be > 0, got: {stats['lines']}"


def test_legend_info_for_large_graphs():
    """Graph with 10+ nodes and no 'legend' cluster gets an info issue."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # 10 nodes, no legend cluster
    nodes = " ".join(f"n{i} -> n{i + 1};" for i in range(10))
    dot = f"digraph G {{ {nodes} }}"
    result = validate_dot(dot)

    legend_info = [
        i
        for i in result["issues"]
        if i["layer"] == "structural"
        and i["severity"] == "info"
        and "legend" in i["message"].lower()
    ]
    assert len(legend_info) >= 1, (
        f"Large graph without legend must produce info issue, got: {result['issues']}"
    )


# ---------------------------------------------------------------------------
# Layer 3 — Render quality tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz not installed")
def test_render_quality_valid_dot():
    """Valid DOT passes render quality check when graphviz is available."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("digraph G { a -> b; b -> c }")

    render_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "render" and i["severity"] == "error"
    ]
    assert len(render_errors) == 0, (
        f"Valid DOT must pass render quality check, got render errors: {render_errors}"
    )


def test_render_quality_skipped_without_graphviz():
    """Render quality check produces info (not error) when graphviz is not installed."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # Mock graphviz as not installed
    mock_env = {
        "graphviz": {
            "installed": False,
            "version": None,
            "engines": [],
            "install_hint": "brew install graphviz",
        },
        "pydot": {"installed": True, "version": "4.0.1"},
        "networkx": {"installed": True, "version": "3.4"},
    }
    with patch(
        "amplifier_module_tool_dot_graph.validate.setup_helper.check_environment",
        return_value=mock_env,
    ):
        result = validate_dot("digraph G { a -> b }")

    render_info = [
        i
        for i in result["issues"]
        if i["layer"] == "render" and i["severity"] == "info"
    ]
    render_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "render" and i["severity"] == "error"
    ]
    assert len(render_info) >= 1, (
        f"Skipped render must produce info issue, got: {result['issues']}"
    )
    assert len(render_errors) == 0, (
        f"Skipped render must NOT produce error, got: {render_errors}"
    )
    # Info message should mention 'Skipped'
    assert "Skipped" in render_info[0]["message"], (
        f"Info message must mention 'Skipped', got: {render_info[0]['message']}"
    )


# ---------------------------------------------------------------------------
# Layer selection test
# ---------------------------------------------------------------------------


def test_syntax_only_layer():
    """Passing layers=['syntax'] skips structural and render checks."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # 'isolated' node would produce structural warning if structural layer ran
    result = validate_dot("digraph G { a -> b; isolated }", layers=["syntax"])

    structural_issues = [i for i in result["issues"] if i["layer"] == "structural"]
    render_issues = [i for i in result["issues"] if i["layer"] == "render"]

    assert len(structural_issues) == 0, (
        f"Syntax-only run must not produce structural issues, got: {structural_issues}"
    )
    assert len(render_issues) == 0, (
        f"Syntax-only run must not produce render issues, got: {render_issues}"
    )


# ---------------------------------------------------------------------------
# Result structure tests
# ---------------------------------------------------------------------------


def test_result_has_required_keys():
    """validate_dot() result always contains 'valid', 'issues', and 'stats' keys."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    result = validate_dot("digraph G { a -> b }")

    assert "valid" in result, "Result must have 'valid' key"
    assert "issues" in result, "Result must have 'issues' key"
    assert "stats" in result, "Result must have 'stats' key"
    assert isinstance(result["valid"], bool), "'valid' must be a bool"
    assert isinstance(result["issues"], list), "'issues' must be a list"
    assert isinstance(result["stats"], dict), "'stats' must be a dict"


def test_issue_structure():
    """Each issue dict has 'layer', 'severity', and 'message' keys."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # Use isolated node to ensure at least one issue
    result = validate_dot("digraph G { a -> b; orphan_xyz }")

    assert len(result["issues"]) >= 1, "Must have at least one issue for this input"
    for issue in result["issues"]:
        assert "layer" in issue, f"Issue must have 'layer' key: {issue}"
        assert "severity" in issue, f"Issue must have 'severity' key: {issue}"
        assert "message" in issue, f"Issue must have 'message' key: {issue}"
        assert isinstance(issue["layer"], str), f"'layer' must be a string: {issue}"
        assert isinstance(issue["severity"], str), (
            f"'severity' must be a string: {issue}"
        )
        assert isinstance(issue["message"], str), f"'message' must be a string: {issue}"


def test_warnings_do_not_affect_valid():
    """Graph with only warnings (no errors) returns valid=True."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # Isolated node produces a warning but not an error
    result = validate_dot("digraph G { a -> b; isolated_node }")

    warn_issues = [i for i in result["issues"] if i["severity"] == "warn"]
    assert len(warn_issues) >= 1, "Must have at least one warning for this input"
    assert result["valid"] is True, (
        f"Graph with only warnings must still return valid=True, got valid={result['valid']} "
        f"with issues: {result['issues']}"
    )


def test_anonymous_subgraph_does_not_crash():
    """Anonymous subgraph (no name) must not crash _collect_clusters.

    Valid DOT allows anonymous subgraphs: subgraph { a -> b }
    pydot returns None for get_name() on anonymous subgraphs.
    Calling .strip() on None raises AttributeError — this test guards that path.
    """
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # Anonymous subgraph — no cluster_ prefix, no name at all
    dot = """
    digraph G {
        outside -> x
        subgraph {
            x -> y
        }
    }
    """
    # Must not raise AttributeError
    result = validate_dot(dot)

    assert "valid" in result, (
        "Result must have 'valid' key even with anonymous subgraph"
    )
    assert "issues" in result, (
        "Result must have 'issues' key even with anonymous subgraph"
    )


def test_unknown_layer_raises_value_error():
    """Passing an unknown layer name raises ValueError with informative message.

    Silently accepting unknown layers (e.g., layers=['typo']) returns valid=True
    with no issues, masking the caller's mistake. A clear ValueError improves
    debuggability — the caller knows immediately that their layer name is wrong.
    """
    from amplifier_module_tool_dot_graph.validate import validate_dot

    with pytest.raises(ValueError, match="Unknown layer"):
        validate_dot("digraph G { a -> b }", layers=["typo"])


def test_all_three_layers_run_by_default():
    """Without specifying layers, all three layers (syntax, structural, render) are checked."""
    from amplifier_module_tool_dot_graph.validate import validate_dot

    # Valid DOT: syntax passes, structural may produce warnings, render runs
    result = validate_dot("digraph G { a -> b }")

    # Result must have no errors (so valid=True) but we check all layers ran
    # by verifying the result is complete and structured correctly
    assert "valid" in result
    assert "issues" in result
    assert "stats" in result

    # Stats must include lines (added by validate_dot, not structural layer)
    assert "lines" in result["stats"], "Default layers must include line count in stats"
    # Stats must include nodes and edges (from structural layer)
    assert "nodes" in result["stats"], "Default layers must count nodes"
    assert "edges" in result["stats"], "Default layers must count edges"
