"""DOT→NetworkX parsing pipeline and graph analysis operations.

Provides analyze_dot() which validates options, parses DOT via pydot,
converts to NetworkX, and dispatches to operation handlers.

Operations: stats, reachability, unreachable, cycles, paths,
            critical_path, subgraph_extract, diff.
"""

from __future__ import annotations

import contextlib
import io
from typing import cast

import networkx as nx
import pydot


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

# pydot pseudo-node names injected by default style declarations.
_PSEUDO_NODES: frozenset[str] = frozenset({"node", "edge", "graph"})

# All known analysis operations.
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

# Entry-point node names exempt from "no incoming edges" warnings.
_ENTRY_HINTS: frozenset[str] = frozenset(
    {"start", "entry", "root", "begin", "init", "source"}
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_dot(dot_content: str, options: dict | None = None) -> dict:
    """Analyze a DOT graph using the specified operation.

    Args:
        dot_content: Raw DOT graph string.
        options: Dict containing 'analysis' key specifying which operation to run,
                 plus any operation-specific parameters.

    Returns:
        {success: True, operation: str, ...result fields} on success,
        or {success: False, error: str} on failure.
    """
    # Validate options and extract analysis type.
    if not options or "analysis" not in options:
        return _parse_error("Missing required 'analysis' key in options")

    analysis = options["analysis"]
    if analysis not in _KNOWN_ANALYSES:
        return _parse_error(
            f"Unknown analysis '{analysis}'. "
            f"Valid analyses are: {sorted(_KNOWN_ANALYSES)}"
        )

    # Special routing: diff and subgraph_extract are dispatched before NetworkX conversion.
    if analysis == "diff":
        return _dispatch_diff(dot_content, options)
    if analysis == "subgraph_extract":
        return _dispatch_subgraph_extract(dot_content, options)

    # Parse DOT → pydot.
    graph = _parse_dot(dot_content)
    if graph is None:
        return _parse_error("Failed to parse DOT content (syntax error or empty input)")

    # Convert pydot → NetworkX.
    G = _pydot_to_networkx(graph)

    # Dispatch to operation handler.
    if analysis == "stats":
        return _stats(G)

    # Remaining operations not yet implemented in this task.
    return _parse_error(f"Analysis '{analysis}' is not yet implemented")


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_dot(dot_content: str) -> pydot.Dot | None:
    """Parse DOT string into a pydot graph.

    Args:
        dot_content: Raw DOT graph string.

    Returns:
        pydot.Dot on success, None on failure (syntax error or empty input).
    """
    if not dot_content or not dot_content.strip():
        return None

    # pydot prints parse errors to stdout — capture them to keep output clean.
    captured = io.StringIO()
    graphs: list[pydot.Dot] | None = None
    with contextlib.redirect_stdout(captured):
        try:
            graphs = pydot.graph_from_dot_data(dot_content)
        except Exception:  # noqa: BLE001
            return None

    if not graphs:
        return None

    return graphs[0]


def _pydot_to_networkx(graph: pydot.Dot) -> nx.Graph:
    """Convert a pydot graph to a NetworkX graph, filtering pseudo-nodes.

    Uses nx.drawing.nx_pydot.from_pydot() which produces:
    - MultiDiGraph for digraph pydot graphs
    - MultiGraph for undirected pydot graphs

    Filters out pydot pseudo-nodes ('node', 'edge', 'graph') that are
    injected by default style declarations.

    Args:
        graph: Parsed pydot graph.

    Returns:
        NetworkX MultiDiGraph or MultiGraph with pseudo-nodes removed.
    """
    G = nx.drawing.nx_pydot.from_pydot(graph)

    # Remove pseudo-nodes that pydot injects for global style declarations.
    pseudo_nodes = [n for n in G.nodes() if str(n).strip('"') in _PSEUDO_NODES]
    G.remove_nodes_from(pseudo_nodes)

    return G


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _parse_error(message: str) -> dict:
    """Build a standardized error response dict.

    Args:
        message: Human-readable description of the error.

    Returns:
        {success: False, error: message}
    """
    return {"success": False, "error": message}


# ---------------------------------------------------------------------------
# Stats operation
# ---------------------------------------------------------------------------


def _stats(G: nx.Graph) -> dict:
    """Compute structural statistics for a NetworkX graph.

    Args:
        G: NetworkX graph (MultiDiGraph or MultiGraph).

    Returns:
        {
            success: True,
            operation: "stats",
            node_count: int,
            edge_count: int,
            density: float,
            is_directed: bool,
            is_dag: bool,
            weakly_connected_components: int,
            self_loops: int,
            nodes: list[str],
        }
    """
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    density = nx.density(G)
    is_directed = G.is_directed()

    # is_dag is a directed-graph concept; undirected graphs return False.
    if is_directed:
        is_dag = nx.is_directed_acyclic_graph(G)
    else:
        is_dag = False

    # Weakly connected components for directed graphs; connected for undirected.
    # cast() is needed because pyright cannot narrow the type from the is_directed check.
    if is_directed:
        wcc_count = nx.number_weakly_connected_components(cast(nx.DiGraph, G))
    else:
        wcc_count = nx.number_connected_components(G)

    self_loops = nx.number_of_selfloops(G)
    nodes = sorted(str(n) for n in G.nodes())

    return {
        "success": True,
        "operation": "stats",
        "node_count": node_count,
        "edge_count": edge_count,
        "density": density,
        "is_directed": is_directed,
        "is_dag": is_dag,
        "weakly_connected_components": wcc_count,
        "self_loops": self_loops,
        "nodes": nodes,
    }


# ---------------------------------------------------------------------------
# Placeholder handlers for special-routed operations
# ---------------------------------------------------------------------------


def _dispatch_diff(dot_content: str, options: dict) -> dict:
    """Dispatch diff operation (routed before NetworkX conversion).

    Compares two DOT graphs for structural differences.
    Not yet implemented — placeholder for future task.
    """
    return _parse_error("Analysis 'diff' is not yet implemented")


def _dispatch_subgraph_extract(dot_content: str, options: dict) -> dict:
    """Dispatch subgraph_extract operation (routed before NetworkX conversion).

    Extracts a subgraph around specified nodes.
    Not yet implemented — placeholder for future task.
    """
    return _parse_error("Analysis 'subgraph_extract' is not yet implemented")
