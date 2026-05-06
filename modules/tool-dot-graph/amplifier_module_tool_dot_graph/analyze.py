"""DOT→NetworkX parsing pipeline and graph analysis operations.

Provides analyze_dot() which validates options, parses DOT via pydot,
converts to NetworkX, and dispatches to operation handlers.

Operations: stats, reachability, unreachable, cycles, paths,
            critical_path, subgraph_extract, diff, producer_consumer.
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
        "producer_consumer",
    }
)

# Entry-point node names exempt from "no incoming edges" warnings.
# Consumed by the 'unreachable' operation when reporting unreachable-node warnings.
_ENTRY_HINTS: frozenset[str] = frozenset(
    {"start", "entry", "root", "begin", "init", "source"}
)

# Maximum number of simple paths returned by the 'paths' operation before
# truncation.  Capped to avoid combinatorial explosion on dense graphs.
_PATH_CAP: int = 100


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
        return _diff(dot_content, options)
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
    if analysis == "reachability":
        return _reachability(G, options)
    if analysis == "unreachable":
        return _unreachable(G, dot_content)
    if analysis == "cycles":
        return _cycles(G, dot_content)
    if analysis == "paths":
        return _paths(G, options)
    if analysis == "critical_path":
        return _critical_path(G)
    if analysis == "producer_consumer":
        return _producer_consumer(G, dot_content)

    # Should be unreachable: all _KNOWN_ANALYSES operations are dispatched above.
    raise AssertionError(f"Unhandled analysis type in dispatcher: {analysis!r}")


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
    # pydot currently prints errors to stdout only, not stderr; redirect_stdout
    # is therefore sufficient. If a future pydot version shifts to stderr,
    # this guard would need to be extended with redirect_stderr as well.
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


def _collect_all_nodes_and_edges(
    pydot_graph: pydot.Graph,
) -> tuple[list[pydot.Node], list[pydot.Edge]]:
    """Recursively collect nodes and edges from a graph and all its subgraphs.

    pydot only exposes top-level nodes/edges via get_nodes()/get_edges().
    Assembled DOT files wrap every real node inside ``subgraph cluster_*``
    blocks, so a flat walk returns 0 nodes.  This helper recurses into every
    subgraph so that nothing is missed.

    Args:
        pydot_graph: A pydot Graph, Dot, or Subgraph to walk.

    Returns:
        (nodes, edges) — flat lists accumulated across all nesting levels.
    """
    nodes: list[pydot.Node] = list(pydot_graph.get_nodes())
    edges: list[pydot.Edge] = list(pydot_graph.get_edges())
    for subgraph in pydot_graph.get_subgraphs():
        sub_nodes, sub_edges = _collect_all_nodes_and_edges(subgraph)
        nodes.extend(sub_nodes)
        edges.extend(sub_edges)
    return nodes, edges


def _pydot_to_networkx(graph: pydot.Dot) -> nx.Graph:
    """Convert a pydot graph to a NetworkX graph, filtering pseudo-nodes.

    Recursively walks all ``subgraph cluster_*`` wrappers so that nodes
    declared inside clusters are included.  A plain ``from_pydot`` call only
    sees top-level nodes and edges; assembled DOT files place everything
    inside clusters, yielding 0 nodes without the recursive walk.

    Produces:
    - MultiDiGraph for digraph pydot graphs
    - MultiGraph for undirected pydot graphs

    Filters out pydot pseudo-nodes ('node', 'edge', 'graph') that are
    injected by default style declarations.

    Args:
        graph: Parsed pydot graph.

    Returns:
        NetworkX MultiDiGraph or MultiGraph with pseudo-nodes removed.
    """
    graph_type = graph.get_type()
    G: nx.Graph
    if graph_type == "digraph":
        G = nx.MultiDiGraph()
    else:
        G = nx.MultiGraph()

    # Collect nodes and edges from the full graph tree (including clusters).
    all_nodes, all_edges = _collect_all_nodes_and_edges(graph)

    # Add explicit nodes, skipping pydot style-declaration pseudo-nodes.
    for node in all_nodes:
        name = node.get_name()
        if str(name).strip('"') not in _PSEUDO_NODES:
            G.add_node(name)

    # Add edges; implicitly-declared endpoint nodes are created by networkx.
    for edge in all_edges:
        src = edge.get_source()
        dst = edge.get_destination()
        if (
            str(src).strip('"') not in _PSEUDO_NODES
            and str(dst).strip('"') not in _PSEUDO_NODES
        ):
            G.add_edge(src, dst)

    # Final sweep: remove any pseudo-nodes that slipped in via edge endpoints.
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
# Reachability operation
# ---------------------------------------------------------------------------


def _reachability(G: nx.Graph, options: dict) -> dict:
    """Find all nodes reachable from a source node via directed edges.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        options: Must contain 'source_node' key with the name of the start node.

    Returns:
        {
            success: True,
            operation: "reachability",
            source_node: str,
            reachable: list[str],   # sorted, excludes source itself
            reachable_count: int,
        }
        or {success: False, error: str} on invalid input.
    """
    if "source_node" not in options:
        return _parse_error("Missing required 'source_node' in options")

    source = options["source_node"]

    if source not in G:
        return _parse_error(f"Node '{source}' not found in graph")

    reachable = nx.descendants(G, source)
    reachable_list = sorted(str(n) for n in reachable)

    return {
        "success": True,
        "operation": "reachability",
        "source_node": source,
        "reachable": reachable_list,
        "reachable_count": len(reachable_list),
    }


# ---------------------------------------------------------------------------
# Unreachable operation
# ---------------------------------------------------------------------------


def _unreachable(G: nx.Graph, dot_content: str) -> dict:
    """Identify nodes with no incoming edges, excluding well-known entry points.

    Nodes whose lower-cased name appears in _ENTRY_HINTS (start, entry, root,
    begin, init, source) are excluded from the result even if they have
    in-degree 0.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        dot_content: Original DOT source, used to produce annotated output.

    Returns:
        {
            success: True,
            operation: "unreachable",
            unreachable: list[str],    # sorted
            unreachable_count: int,
            annotated_dot: str,        # nodes colored red in DOT source
        }
    """
    DG = cast(nx.DiGraph, G)
    unreachable_nodes = sorted(
        str(n)
        for n in DG.nodes()
        if DG.in_degree(n) == 0 and str(n).strip('"').lower() not in _ENTRY_HINTS
    )

    annotated = _annotate_nodes(dot_content, unreachable_nodes, "red", "filled")

    return {
        "success": True,
        "operation": "unreachable",
        "unreachable": unreachable_nodes,
        "unreachable_count": len(unreachable_nodes),
        "annotated_dot": annotated,
    }


# ---------------------------------------------------------------------------
# Cycles operation
# ---------------------------------------------------------------------------


def _cycles(G: nx.Graph, dot_content: str) -> dict:
    """Detect all simple cycles in a directed graph.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        dot_content: Original DOT source, used to produce annotated output.

    Returns:
        {
            success: True,
            operation: "cycles",
            has_cycles: bool,
            cycles: list[list[str]],  # each cycle is a sorted list of node names
            cycle_count: int,
            annotated_dot: str | None,  # cycle edges colored red; None if no cycles
        }
    """
    if not G.is_directed():
        return _parse_error("Cycle detection requires a directed graph")

    raw_cycles = list(nx.simple_cycles(G))

    if not raw_cycles:
        return {
            "success": True,
            "operation": "cycles",
            "has_cycles": False,
            "cycles": [],
            "cycle_count": 0,
            "annotated_dot": None,
        }

    # Sort each cycle's node list for deterministic output.
    sorted_cycles = [sorted(str(n) for n in cycle) for cycle in raw_cycles]

    # Collect every edge that participates in at least one cycle.
    cycle_edges: set[tuple[str, str]] = set()
    for cycle in raw_cycles:
        for i in range(len(cycle)):
            src = str(cycle[i])
            dst = str(cycle[(i + 1) % len(cycle)])
            cycle_edges.add((src, dst))

    annotated = _annotate_edges(dot_content, list(cycle_edges), "red", "bold")

    return {
        "success": True,
        "operation": "cycles",
        "has_cycles": True,
        "cycles": sorted_cycles,
        "cycle_count": len(raw_cycles),
        "annotated_dot": annotated,
    }


# ---------------------------------------------------------------------------
# Paths operation
# ---------------------------------------------------------------------------


def _paths(G: nx.Graph, options: dict) -> dict:
    """Find all simple paths between two nodes, capped at 100 to avoid combinatorial explosion.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        options: Must contain 'source_node' and 'target_node' keys.

    Returns:
        {
            success: True,
            operation: "paths",
            source_node: str,
            target_node: str,
            paths: list[list[str]],  # each path is a list of node names
            path_count: int,
            truncated: bool,         # True if more than 100 paths exist
        }
        or {success: False, error: str} on invalid input.
    """
    if "source_node" not in options:
        return _parse_error("Missing required 'source_node' in options")
    if "target_node" not in options:
        return _parse_error("Missing required 'target_node' in options")

    source = options["source_node"]
    target = options["target_node"]

    if source not in G:
        return _parse_error(f"Node '{source}' not found in graph")
    if target not in G:
        return _parse_error(f"Node '{target}' not found in graph")

    raw_paths: list[list[str]] = []
    truncated = False

    path_gen = nx.all_simple_paths(G, source=source, target=target)
    for path in path_gen:
        raw_paths.append([str(n) for n in path])
        if len(raw_paths) == _PATH_CAP:
            # Peek from the same generator to check whether a 101st path exists.
            try:
                next(path_gen)
                truncated = True  # a path beyond the cap was found
            except StopIteration:
                pass  # exactly _PATH_CAP paths — no truncation
            break

    return {
        "success": True,
        "operation": "paths",
        "source_node": source,
        "target_node": target,
        "paths": raw_paths,
        "path_count": len(raw_paths),
        "truncated": truncated,
    }


# ---------------------------------------------------------------------------
# Critical path operation
# ---------------------------------------------------------------------------


def _critical_path(G: nx.Graph) -> dict:
    """Find the longest path in a DAG (critical path).

    Args:
        G: NetworkX graph (MultiDiGraph expected). Must be a DAG.

    Returns:
        {
            success: True,
            operation: "critical_path",
            critical_path: list[str],  # ordered list of node names on the longest path
            length: int,               # number of nodes in the critical path
        }
        or {success: False, error: str} if the graph contains cycles.
    """
    if not G.is_directed() or not nx.is_directed_acyclic_graph(G):
        return _parse_error(
            "Critical path requires a directed acyclic graph (DAG). "
            "The graph contains a cycle or is not directed."
        )

    longest = nx.dag_longest_path(cast(nx.DiGraph, G))
    path = [str(n) for n in longest]

    return {
        "success": True,
        "operation": "critical_path",
        "critical_path": path,
        "length": len(path),
    }


# ---------------------------------------------------------------------------
# DOT annotation helpers
# ---------------------------------------------------------------------------


def _annotate_nodes(dot_content: str, nodes: list[str], color: str, style: str) -> str:
    """Insert per-node attribute declarations into a DOT string.

    Declarations are inserted on new lines immediately after the first line
    that contains '{', so they take precedence over any global defaults.

    Args:
        dot_content: Raw DOT graph string.
        nodes: Node names to annotate (must already exist in the graph).
        color: DOT color value (e.g. "red").
        style: DOT style value (e.g. "filled").

    Returns:
        Modified DOT string with attribute lines injected, or the original
        string unchanged if no nodes are provided or no '{' is found.
    """
    if not nodes:
        return dot_content

    lines = dot_content.split("\n")
    insert_idx: int | None = None
    for i, line in enumerate(lines):
        if "{" in line:
            insert_idx = i + 1
            break

    if insert_idx is None:
        return dot_content

    new_lines = [f'  {node} [color="{color}", style="{style}"];' for node in nodes]
    return "\n".join(lines[:insert_idx] + new_lines + lines[insert_idx:])


def _annotate_edges(
    dot_content: str, edges: list[tuple[str, str]], color: str, style: str
) -> str:
    """Insert per-edge attribute declarations into a DOT string.

    Declarations are inserted on new lines immediately after the first line
    that contains '{'.

    Args:
        dot_content: Raw DOT graph string.
        edges: (src, dst) pairs to annotate.
        color: DOT color value (e.g. "red").
        style: DOT style value (e.g. "bold").

    Returns:
        Modified DOT string with attribute lines injected, or the original
        string unchanged if no edges are provided or no '{' is found.
    """
    if not edges:
        return dot_content

    lines = dot_content.split("\n")
    insert_idx: int | None = None
    for i, line in enumerate(lines):
        if "{" in line:
            insert_idx = i + 1
            break

    if insert_idx is None:
        return dot_content

    new_lines = [
        f'  {src} -> {dst} [color="{color}", style="{style}"];' for src, dst in edges
    ]
    return "\n".join(lines[:insert_idx] + new_lines + lines[insert_idx:])


# ---------------------------------------------------------------------------
# Subgraph extract operation
# ---------------------------------------------------------------------------


def _dispatch_subgraph_extract(dot_content: str, options: dict) -> dict:
    """Dispatch subgraph_extract operation (routed before NetworkX conversion).

    Parses DOT to pydot to preserve cluster structure, then delegates to
    _subgraph_extract which works directly on the pydot graph.
    """
    graph = _parse_dot(dot_content)
    if graph is None:
        return _parse_error("Failed to parse DOT content (syntax error or empty input)")
    return _subgraph_extract(graph, dot_content, options)


def _subgraph_extract(pydot_graph: pydot.Dot, _dot_content: str, options: dict) -> dict:
    """Extract a named cluster subgraph into a standalone DOT graph.

    Works on the pydot graph (not NetworkX) to preserve cluster
    structure, labels, and attributes.

    Args:
        pydot_graph: Parsed pydot graph containing clusters.
        _dot_content: Original DOT source (intentionally unused; kept for API symmetry).
        options: Must contain 'cluster_name' key with the name of the target cluster.

    Returns:
        {
            success: True,
            operation: "subgraph_extract",
            cluster_name: str,
            extracted_dot: str,   # standalone DOT string for the cluster
            node_count: int,
            edge_count: int,
        }
        or {success: False, error: str} on failure.
    """
    if "cluster_name" not in options:
        return _parse_error("Missing required 'cluster_name' in options")

    cluster_name = options["cluster_name"]

    # Search direct subgraph children, stripping any surrounding quotes from names.
    target_cluster: pydot.Subgraph | None = None
    available: list[str] = []
    for sg in pydot_graph.get_subgraph_list():
        sg_name = (sg.get_name() or "").strip('"')
        available.append(sg_name)
        if sg_name == cluster_name:
            target_cluster = sg
            break

    if target_cluster is None:
        return _parse_error(
            f"Cluster '{cluster_name}' not found in graph. "
            f"Available clusters: {available}"
        )

    # Build a standalone pydot.Dot from the cluster contents.
    new_graph = pydot.Dot(graph_type="digraph")

    # Copy all cluster-level attributes (e.g. label) to the new graph.
    for attr_key, attr_val in target_cluster.get_attributes().items():
        new_graph.set(attr_key, attr_val)

    # Copy nodes with obj_dict to preserve all attributes.
    for node in target_cluster.get_node_list():
        new_node = pydot.Node(node.get_name())
        new_node.obj_dict = node.obj_dict.copy()
        new_graph.add_node(new_node)

    # Copy edges with obj_dict to preserve all attributes.
    for edge in target_cluster.get_edge_list():
        new_edge = pydot.Edge(edge.get_source(), edge.get_destination())
        new_edge.obj_dict = edge.obj_dict.copy()
        new_graph.add_edge(new_edge)

    extracted_dot = new_graph.to_string()

    # Derive node/edge counts via NetworkX (handles implicitly-defined nodes).
    G = _pydot_to_networkx(new_graph)
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()

    return {
        "success": True,
        "operation": "subgraph_extract",
        "cluster_name": cluster_name,
        "extracted_dot": extracted_dot,
        "node_count": node_count,
        "edge_count": edge_count,
    }


# ---------------------------------------------------------------------------
# Diff operation
# ---------------------------------------------------------------------------


def _diff(dot_content_a: str, options: dict) -> dict:
    """Compute structural differences between two DOT graphs.

    Parses both DOT strings independently, converts to NetworkX, then
    compares node sets and edge sets.  MultiDiGraph parallel-edge keys
    are ignored so only (u, v) pairs are compared.

    Args:
        dot_content_a: First (baseline) DOT graph string.
        options: Must contain 'dot_content_b' key with the second DOT string.

    Returns:
        {
            success: True,
            operation: "diff",
            added_nodes: list[str],           # in B but not A, sorted
            removed_nodes: list[str],         # in A but not B, sorted
            added_edges: list[list[str]],     # [u, v] pairs in B but not A, sorted
            removed_edges: list[list[str]],   # [u, v] pairs in A but not B, sorted
            summary: {
                added_nodes_count: int,
                removed_nodes_count: int,
                added_edges_count: int,
                removed_edges_count: int,
                unchanged_nodes: int,
                unchanged_edges: int,
            },
        }
        or {success: False, error: str} on failure.
    """
    if "dot_content_b" not in options:
        return _parse_error("Missing required 'dot_content_b' in options")

    dot_content_b: str = options["dot_content_b"]

    # Parse both DOT strings independently.
    graph_a = _parse_dot(dot_content_a)
    if graph_a is None:
        return _parse_error("Failed to parse DOT content (syntax error or empty input)")

    graph_b = _parse_dot(dot_content_b)
    if graph_b is None:
        return _parse_error(
            "Failed to parse 'dot_content_b' (syntax error or empty input)"
        )

    # Convert both to NetworkX graphs.
    G_a = _pydot_to_networkx(graph_a)
    G_b = _pydot_to_networkx(graph_b)

    # Compare node sets.
    nodes_a: set[str] = {str(n) for n in G_a.nodes()}
    nodes_b: set[str] = {str(n) for n in G_b.nodes()}

    added_nodes = sorted(nodes_b - nodes_a)
    removed_nodes = sorted(nodes_a - nodes_b)

    # Compare edge sets, ignoring MultiDiGraph parallel-edge keys.
    # Cast to MultiDiGraph so pyright knows edges(keys=True) yields (u, v, key) triples.
    MDG_a = cast(nx.MultiDiGraph, G_a)
    MDG_b = cast(nx.MultiDiGraph, G_b)
    edges_a: set[tuple[str, str]] = {
        (str(u), str(v)) for u, v, _ in MDG_a.edges(keys=True)
    }
    edges_b: set[tuple[str, str]] = {
        (str(u), str(v)) for u, v, _ in MDG_b.edges(keys=True)
    }

    added_edges = sorted([list(e) for e in edges_b - edges_a])
    removed_edges = sorted([list(e) for e in edges_a - edges_b])

    summary = {
        "added_nodes_count": len(added_nodes),
        "removed_nodes_count": len(removed_nodes),
        "added_edges_count": len(added_edges),
        "removed_edges_count": len(removed_edges),
        "unchanged_nodes": len(nodes_a & nodes_b),
        "unchanged_edges": len(edges_a & edges_b),
    }

    return {
        "success": True,
        "operation": "diff",
        "added_nodes": added_nodes,
        "removed_nodes": removed_nodes,
        "added_edges": added_edges,
        "removed_edges": removed_edges,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Producer/consumer operation
# ---------------------------------------------------------------------------


def _parse_condition_key(condition: str) -> str:
    """Extract the context key from a DOT condition attribute value.

    Handles all three attractor condition formats (quotes already stripped
    by the caller):

        key=value    ->  'key'
        key!=value   ->  'key'
        key=         ->  'key'   (empty-value / missing-key check)

    Args:
        condition: Stripped condition string with surrounding quotes removed.

    Returns:
        The key portion of the condition string.
    """
    if "!=" in condition:
        return condition.split("!=")[0].strip()
    if "=" in condition:
        return condition.split("=")[0].strip()
    return condition.strip()


def _producer_consumer(G: nx.Graph, dot_content: str) -> dict:
    """Detect condition keys on edges that have no upstream producer node.

    Performs static analysis of DOT pipeline graphs.  In the attractor
    pipeline engine a condition like ``condition="verdict=approved"`` on an
    edge checks a context key called ``verdict``.  If no upstream node
    declares that it produces ``verdict`` (via ``tool_outputs="verdict,..."``),
    the pipeline will silently route incorrectly.  This analyser catches that
    at authoring time.

    Nodes declare produced context keys via the ``tool_outputs`` attribute::

        Eval [shape=parallelogram tool_outputs="verdict,confidence" parse_json=true]

    Args:
        G: NetworkX graph (MultiDiGraph expected — directed graphs only).
        dot_content: Original DOT source, used to access node/edge attributes
                     via pydot and to produce annotated output.

    Returns:
        {
            success: True,
            operation: "producer_consumer",
            total_condition_edges: int,    # edges carrying condition= attributes
            total_condition_keys: int,     # unique keys referenced by conditions
            total_producers: int,          # nodes with tool_outputs declared
            matched_keys: list[dict],      # keys satisfied by an upstream producer
            unmatched_keys: list[dict],    # THE ERRORS — keys with no upstream producer
            producers: dict,               # node -> [key, ...] map
            annotated_dot: str,            # unmatched edges highlighted red
        }
        or {success: False, error: str} if the graph is undirected.
    """
    if not G.is_directed():
        return _parse_error("producer_consumer requires a directed graph")

    DG = cast(nx.DiGraph, G)

    # Re-parse DOT to access node/edge attributes.  The NetworkX graph carries
    # topology only; pydot is the authoritative source for custom attributes.
    pydot_graph = _parse_dot(dot_content)
    if pydot_graph is None:
        return _parse_error("Failed to parse DOT content (syntax error or empty input)")

    # Recursively collect nodes and edges (handles subgraph cluster nesting).
    all_nodes, all_edges = _collect_all_nodes_and_edges(pydot_graph)

    # ------------------------------------------------------------------
    # 1. Build producers map: clean_node_name -> [key, ...]
    #    Nodes declare what context keys they produce via
    #    tool_outputs="k1,k2,...".
    # ------------------------------------------------------------------
    producers: dict[str, list[str]] = {}
    for node in all_nodes:
        raw_name = node.get_name()
        clean_name = str(raw_name).strip('"')
        if clean_name in _PSEUDO_NODES:
            continue
        attrs = node.get_attributes() or {}
        if "tool_outputs" in attrs:
            raw_val = str(attrs["tool_outputs"]).strip('"')
            keys = [k.strip() for k in raw_val.split(",") if k.strip()]
            if keys:
                producers[clean_name] = keys

    # ------------------------------------------------------------------
    # 2. Reverse map: context_key -> [producer_node_names]
    # ------------------------------------------------------------------
    key_to_producers: dict[str, list[str]] = {}
    for node_name, keys in producers.items():
        for key in keys:
            key_to_producers.setdefault(key, []).append(node_name)

    # ------------------------------------------------------------------
    # 3. Collect condition edges: (raw_src, raw_dst, condition_str)
    #    Skips pseudo-nodes and edges without a condition= attribute.
    # ------------------------------------------------------------------
    condition_edges: list[tuple[str, str, str]] = []
    for edge in all_edges:
        src = edge.get_source()
        dst = edge.get_destination()
        if str(src).strip('"') in _PSEUDO_NODES or str(dst).strip('"') in _PSEUDO_NODES:
            continue
        attrs = edge.get_attributes() or {}
        if "condition" in attrs:
            cond_str = str(attrs["condition"]).strip('"')
            condition_edges.append((src, dst, cond_str))

    # ------------------------------------------------------------------
    # 4. Classify each condition edge as matched or unmatched.
    #    A key is matched for an edge when at least one node in the
    #    upstream set (nx.ancestors(DG, src) ∪ {src}) declares that key
    #    in its tool_outputs.
    # ------------------------------------------------------------------
    matched: dict[str, dict] = {}  # key -> {key, producers, consumers}
    unmatched: dict[str, dict] = {}  # key -> {key, consumers, reachable_producers}

    for src, dst, cond_str in condition_edges:
        key = _parse_condition_key(cond_str)
        src_clean = str(src).strip('"')
        dst_clean = str(dst).strip('"')
        edge_info = {"from": src_clean, "to": dst_clean, "condition": cond_str}

        # Resolve the edge source to the node name actually stored in DG.
        # pydot may return quoted names; try raw first, then stripped.
        src_in_dg: str = src if src in DG else src_clean

        # Build upstream set: all ancestors of the edge source + source itself.
        if src_in_dg in DG:
            ancestor_nodes = nx.ancestors(DG, src_in_dg)
            upstream: set[str] = {str(n).strip('"') for n in ancestor_nodes} | {
                src_clean
            }
        else:
            upstream = {src_clean}

        # Producers of this key that are upstream of the current edge.
        all_producers_for_key = key_to_producers.get(key, [])
        reachable = [p for p in all_producers_for_key if p in upstream]

        if reachable:
            if key not in matched:
                matched[key] = {
                    "key": key,
                    "producers": all_producers_for_key,
                    "consumers": [],
                }
            matched[key]["consumers"].append(edge_info)
        else:
            if key not in unmatched:
                unmatched[key] = {
                    "key": key,
                    "consumers": [],
                    "reachable_producers": [],
                }
            unmatched[key]["consumers"].append(edge_info)

    # ------------------------------------------------------------------
    # 5. Annotate unmatched edges in the DOT source (red highlight).
    # ------------------------------------------------------------------
    unmatched_pairs: list[tuple[str, str]] = list(
        {
            (str(src).strip('"'), str(dst).strip('"'))
            for src, dst, cond_str in condition_edges
            if _parse_condition_key(cond_str) in unmatched
        }
    )
    annotated = _annotate_edges(dot_content, unmatched_pairs, "red", "bold")

    # ------------------------------------------------------------------
    # 6. Summary counts.
    # ------------------------------------------------------------------
    all_condition_keys: set[str] = {
        _parse_condition_key(c) for _, _, c in condition_edges
    }

    return {
        "success": True,
        "operation": "producer_consumer",
        "total_condition_edges": len(condition_edges),
        "total_condition_keys": len(all_condition_keys),
        "total_producers": len(producers),
        "matched_keys": list(matched.values()),
        "unmatched_keys": list(unmatched.values()),
        "producers": producers,
        "annotated_dot": annotated,
    }
