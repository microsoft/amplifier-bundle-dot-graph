"""Three-layer DOT graph validation.

Layer 1 — Syntax:   Parse via pydot; capture stdout parse errors.
Layer 2 — Structural: Inspect parsed graph for structural issues.
Layer 3 — Render:   Test render via graphviz CLI (dot -Tcanon).
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import tempfile

import pydot

from amplifier_module_tool_dot_graph import setup_helper

# Entry-point node names that are exempt from "no incoming edges" warnings.
_ENTRY_HINTS: frozenset[str] = frozenset(
    {"start", "entry", "root", "begin", "init", "source"}
)

# pydot pseudo-node names injected by default style declarations.
_PSEUDO_NODES: frozenset[str] = frozenset({"node", "edge", "graph"})

# Valid layer names accepted by validate_dot().
_KNOWN_LAYERS: frozenset[str] = frozenset({"syntax", "structural", "render"})


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_dot(
    dot_content: str,
    layers: list[str] | None = None,
) -> dict:
    """Validate DOT content through up to three layers.

    Args:
        dot_content: Raw DOT graph string.
        layers: Which layers to run. Defaults to ['syntax', 'structural', 'render'].

    Returns:
        {
            valid: bool,           # True when no error-severity issues present
            issues: list[dict],    # Each: {layer, severity, message}
            stats:  dict,          # {nodes, edges, clusters, lines}
        }
    """
    if layers is None:
        layers = ["syntax", "structural", "render"]

    unknown = set(layers) - _KNOWN_LAYERS
    if unknown:
        raise ValueError(
            f"Unknown layer(s): {sorted(unknown)}. "
            f"Valid layers are: {sorted(_KNOWN_LAYERS)}"
        )

    all_issues: list[dict] = []
    stats: dict = {"nodes": 0, "edges": 0, "clusters": 0, "lines": 0}

    # Always count source lines (regardless of which layers run).
    if dot_content:
        stats["lines"] = len(dot_content.splitlines())

    graph: pydot.Dot | None = None

    # --- Layer 1: Syntax ---
    if "syntax" in layers:
        graph, syntax_issues = _check_syntax(dot_content)
        all_issues.extend(syntax_issues)

    # --- Layer 2: Structural ---
    if "structural" in layers and graph is not None:
        struct_issues, struct_stats = _check_structural(graph)
        all_issues.extend(struct_issues)
        stats.update(struct_stats)

    # --- Layer 3: Render quality ---
    if "render" in layers:
        render_issues = _check_render_quality(dot_content)
        all_issues.extend(render_issues)

    has_errors = any(i["severity"] == "error" for i in all_issues)
    return {
        "valid": not has_errors,
        "issues": all_issues,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# Layer 1 — Syntax
# ---------------------------------------------------------------------------


def _check_syntax(dot_content: str) -> tuple[pydot.Dot | None, list[dict]]:
    """Parse DOT content via pydot.

    Returns:
        (graph_or_None, issues_list)
        graph_or_None is None when parsing fails.
    """
    if not dot_content or not dot_content.strip():
        return None, [_issue("syntax", "error", "Empty DOT content")]

    # pydot prints parse errors to stdout — capture them.
    captured = io.StringIO()
    graphs: list[pydot.Dot] | None = None
    with contextlib.redirect_stdout(captured):
        try:
            graphs = pydot.graph_from_dot_data(dot_content)
        except Exception as exc:  # noqa: BLE001
            return None, [_issue("syntax", "error", str(exc))]

    if not graphs:
        # Parse failure — extract first line of captured output as message.
        output = captured.getvalue().strip()
        first_line = output.splitlines()[0] if output else "Parse error (unknown)"
        return None, [_issue("syntax", "error", first_line)]

    return graphs[0], []


# ---------------------------------------------------------------------------
# Layer 2 — Structural
# ---------------------------------------------------------------------------


def _check_structural(graph: pydot.Dot) -> tuple[list[dict], dict]:
    """Inspect parsed graph for structural issues.

    Returns:
        (issues, stats)  — stats dict does NOT include 'lines'.
    """
    issues: list[dict] = []

    all_nodes = _collect_all_nodes(graph)
    all_edges = _collect_all_edges(graph)
    clusters = _collect_clusters(graph)

    stats = {
        "nodes": len(all_nodes),
        "edges": len(all_edges),
        "clusters": len(clusters),
    }

    # (a) Empty graph
    if not all_nodes and not all_edges:
        issues.append(
            _issue("structural", "error", "Graph is empty (no nodes or edges)")
        )
        return issues, stats

    # Build adjacency info for directed graphs.
    is_digraph = graph.get_type() == "digraph"

    outgoing: dict[str, set[str]] = {n: set() for n in all_nodes}
    incoming: dict[str, set[str]] = {n: set() for n in all_nodes}
    node_has_edge: dict[str, bool] = {n: False for n in all_nodes}

    for src, dst in all_edges:
        node_has_edge[src] = True
        node_has_edge[dst] = True
        outgoing.setdefault(src, set()).add(dst)
        incoming.setdefault(dst, set()).add(src)

    # (b) Unreachable nodes — digraph only.
    if is_digraph:
        for node in all_nodes:
            has_out = bool(outgoing.get(node))
            has_in = bool(incoming.get(node))
            if has_out and not has_in and node.lower() not in _ENTRY_HINTS:
                issues.append(
                    _issue(
                        "structural",
                        "warn",
                        f"Node '{node}' has no incoming edges",
                    )
                )

    # (c) Isolated nodes — zero edges of any kind.
    for node in all_nodes:
        if not node_has_edge.get(node, False):
            issues.append(_issue("structural", "warn", f"Node '{node}' is isolated"))

    # (d) Orphan clusters — no edges connecting cluster nodes to outside nodes.
    outside_nodes = all_nodes - {
        n for cluster_nodes in clusters.values() for n in cluster_nodes
    }

    for cluster_name, cluster_nodes in clusters.items():
        connected_to_outside = any(
            (src in cluster_nodes and dst in outside_nodes)
            or (dst in cluster_nodes and src in outside_nodes)
            for src, dst in all_edges
        )
        if not connected_to_outside:
            issues.append(
                _issue(
                    "structural",
                    "warn",
                    f"Cluster '{cluster_name}' has no edges connecting to outside nodes",
                )
            )

    # (e) Missing legend — 10+ nodes, no legend cluster.
    if len(all_nodes) >= 10 and not any(
        name.lower().startswith("cluster_legend") or name.lower() == "legend"
        for name in clusters
    ):
        issues.append(
            _issue(
                "structural",
                "info",
                "Graph has 10+ nodes but no 'legend' cluster — consider adding a legend",
            )
        )

    return issues, stats


# ---------------------------------------------------------------------------
# Layer 3 — Render quality
# ---------------------------------------------------------------------------


def _check_render_quality(dot_content: str) -> list[dict]:
    """Test-render DOT via graphviz CLI (dot -Tcanon).

    Returns:
        List of render-layer issues.
    """
    env = setup_helper.check_environment()
    graphviz_info = env.get("graphviz", {})

    if not graphviz_info.get("installed", False):
        hint = graphviz_info.get(
            "install_hint", "Install Graphviz from https://graphviz.org/"
        )
        return [
            _issue(
                "render",
                "info",
                f"Skipped render quality check (Graphviz not installed). {hint}",
            )
        ]

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dot", delete=False
        ) as tmp_file:
            tmp_file.write(dot_content)
            tmp_path = tmp_file.name

        result = subprocess.run(
            ["dot", "-Tcanon", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            stderr_msg = result.stderr.strip() or "Render failed (unknown error)"
            return [_issue("render", "error", stderr_msg)]

        if result.stderr.strip():
            return [_issue("render", "warn", result.stderr.strip())]

        return []

    except subprocess.TimeoutExpired:
        return [_issue("render", "error", "Render timed out after 30 seconds")]
    except OSError as exc:
        return [_issue("render", "error", str(exc))]
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Structural helpers
# ---------------------------------------------------------------------------


def _collect_all_nodes(graph: pydot.Dot) -> set[str]:
    """Recursively collect real node names, filtering pydot pseudo-nodes.

    Gathers from both explicit node declarations AND edge endpoints because
    pydot only populates get_node_list() for explicitly-declared nodes.
    """
    names: set[str] = set()
    _recurse_nodes(graph, names)
    # Also collect nodes referenced only in edges (implicit node definitions).
    _collect_edge_endpoint_names(graph, names)
    # Remove pseudo-nodes that might have slipped in from edge endpoints.
    names -= _PSEUDO_NODES
    return names


def _recurse_nodes(subgraph: pydot.Dot | pydot.Subgraph, names: set[str]) -> None:
    for node in subgraph.get_node_list():
        raw = str(node.get_name()).strip('"')
        if raw and raw not in _PSEUDO_NODES:
            names.add(raw)
    for sg in subgraph.get_subgraph_list():
        _recurse_nodes(sg, names)


def _collect_all_edges(graph: pydot.Dot) -> list[tuple[str, str]]:
    """Recursively collect all edges from graph and subgraphs."""
    edges: list[tuple[str, str]] = []
    _recurse_edges(graph, edges)
    return edges


def _recurse_edges(
    subgraph: pydot.Dot | pydot.Subgraph,
    edges: list[tuple[str, str]],
) -> None:
    for edge in subgraph.get_edge_list():
        src = str(edge.get_source()).strip('"')
        dst = str(edge.get_destination()).strip('"')
        edges.append((src, dst))
    for sg in subgraph.get_subgraph_list():
        _recurse_edges(sg, edges)


def _collect_clusters(graph: pydot.Dot) -> dict[str, set[str]]:
    """Collect cluster subgraphs (name starts with 'cluster') and their node sets.

    Note: only top-level subgraphs are examined for cluster membership.
    Nested clusters (clusters within clusters) are not tracked — this is
    intentional given DOT's rare usage of nested clusters and the absence
    of a spec requirement for deeper recursion.
    """
    clusters: dict[str, set[str]] = {}
    for sg in graph.get_subgraph_list():
        raw_name = sg.get_name()
        if raw_name is None:
            continue  # anonymous subgraph — cannot be a named cluster, skip
        name = str(raw_name).strip('"')
        if name.lower().startswith("cluster"):
            node_set: set[str] = set()
            # Collect nodes declared inside this cluster.
            _recurse_nodes(sg, node_set)
            # Also collect node names referenced by edges inside the cluster.
            edge_nodes: set[str] = set()
            _collect_edge_endpoint_names(sg, edge_nodes)
            node_set |= edge_nodes
            clusters[name] = node_set
    return clusters


def _collect_edge_endpoint_names(
    subgraph: pydot.Dot | pydot.Subgraph,
    names: set[str],
) -> None:
    """Collect all node names that appear as edge endpoints in subgraph (recursive)."""
    for edge in subgraph.get_edge_list():
        names.add(str(edge.get_source()).strip('"'))
        names.add(str(edge.get_destination()).strip('"'))
    for sg in subgraph.get_subgraph_list():
        _collect_edge_endpoint_names(sg, names)


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------


def _issue(layer: str, severity: str, message: str) -> dict:
    """Build a standardised issue dict."""
    return {"layer": layer, "severity": severity, "message": message}
