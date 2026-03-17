"""Hierarchical DOT Assembly.

Takes per-module DOT files and a manifest, merges them into subsystem DOT files
with subgraph clusters and a bounded overview.dot.

Public API: assemble_hierarchy(manifest, output_dir, render_png=False) -> dict
"""

from __future__ import annotations

import contextlib
import io
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pydot

from amplifier_module_tool_dot_graph import render as _render

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

_MAX_OVERVIEW_LINES: int = 250
_MAX_OVERVIEW_NODES: int = 80

# pydot pseudo-node names injected by default style declarations.
_PSEUDO_NODES: frozenset[str] = frozenset({"node", "edge", "graph"})


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def assemble_hierarchy(
    manifest: dict,
    output_dir: str,
    render_png: bool = False,
) -> dict:
    """Assemble hierarchical DOT files from per-module DOT files.

    Args:
        manifest: Dict with 'modules' and 'subsystems' keys describing the structure.
            modules: {mod_name: {dot_path: str, subsystem: str}}
            subsystems: {ss_name: {modules: [mod_name]}}
            invalidated_modules: [str]  (optional)
        output_dir: Directory to write output DOT files.
        render_png: If True, render each output DOT file to PNG via graphviz.
            Render failures are non-fatal and recorded in 'warnings'.
            Default: False.

    Returns:
        On success:
            {
                success: True,
                outputs: {overview: str, subsystems: {name: path}},
                stats: {total_nodes, total_edges, subsystems, modules},
                warnings: [str],
                regenerated: [str],
                skipped: [str],
            }
        On failure:
            {success: False, error: str}
    """
    # --- Validate manifest ---
    if not manifest or not isinstance(manifest, dict):
        return _error("Manifest must be a non-empty dict")

    if "modules" not in manifest:
        return _error("Manifest is missing required 'modules' key")

    if "subsystems" not in manifest:
        return _error("Manifest is missing required 'subsystems' key")

    modules_def: dict = manifest["modules"]
    subsystems_def: dict = manifest["subsystems"]
    invalidated: list[str] = manifest.get("invalidated_modules", [])

    # --- Parse all module DOT files ---
    warnings: list[str] = []
    parsed_modules: dict[str, pydot.Dot] = {}

    for mod_name, mod_info in modules_def.items():
        dot_path = mod_info.get("dot_path", "")
        graph = _parse_dot_file(dot_path)
        if graph is None:
            warnings.append(
                f"Module '{mod_name}': could not parse DOT file '{dot_path}' — skipped"
            )
        else:
            parsed_modules[mod_name] = graph

    # --- Count nodes and edges across all parsed modules ---
    total_nodes = 0
    total_edges = 0
    for graph in parsed_modules.values():
        n, e = _count_graph_elements(graph)
        total_nodes += n
        total_edges += e

    # --- Determine which subsystems to regenerate ---
    if invalidated:
        # Build set of subsystems whose modules are invalidated
        invalidated_set = set(invalidated)
        subsystems_to_regenerate: set[str] = set()
        for ss_name, ss_info in subsystems_def.items():
            ss_modules = ss_info.get("modules", [])
            if any(m in invalidated_set for m in ss_modules):
                subsystems_to_regenerate.add(ss_name)
    else:
        # Regenerate all subsystems
        subsystems_to_regenerate = set(subsystems_def.keys())

    # --- Ensure output directory exists (and subsystems/ subdir) ---
    os.makedirs(output_dir, exist_ok=True)
    subsystems_dir = str(Path(output_dir) / "subsystems")
    os.makedirs(subsystems_dir, exist_ok=True)

    # --- Generate subsystem DOT files ---
    subsystem_paths: dict[str, str] = {}
    regenerated: list[str] = []
    skipped: list[str] = []

    for ss_name, ss_info in subsystems_def.items():
        if ss_name not in subsystems_to_regenerate:
            skipped.append(ss_name)
            # If the file already exists (from a prior run), still record its path
            ss_path = str(Path(subsystems_dir) / f"{ss_name}.dot")
            if Path(ss_path).exists():
                subsystem_paths[ss_name] = ss_path
            continue

        ss_modules = ss_info.get("modules", [])
        ss_graph = _build_subsystem_dot(ss_name, ss_modules, parsed_modules)
        _add_legend(ss_graph, f"Subsystem: {ss_name}")

        ss_path = str(Path(subsystems_dir) / f"{ss_name}.dot")
        Path(ss_path).write_text(ss_graph.to_string())
        subsystem_paths[ss_name] = ss_path
        regenerated.append(ss_name)

    # --- Generate overview DOT ---
    overview_graph = _build_overview_dot(subsystems_def, parsed_modules)
    _add_legend(overview_graph, "Overview")

    overview_path = str(Path(output_dir) / "overview.dot")
    Path(overview_path).write_text(overview_graph.to_string())

    # --- Optionally render all output DOT files to PNG ---
    if render_png:
        png_paths: list[str] = []
        all_dot_paths = [overview_path] + list(subsystem_paths.values())
        for dot_path in all_dot_paths:
            png_path = dot_path.replace(".dot", ".png")
            try:
                dot_content = Path(dot_path).read_text()
                render_result = _render.render_dot(dot_content, "png", "dot", png_path)
                if render_result.get("success"):
                    png_paths.append(png_path)
                else:
                    warnings.append(
                        f"PNG render failed for '{dot_path}': "
                        f"{render_result.get('error', 'unknown error')}"
                    )
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"PNG render error for '{dot_path}': {exc}")
                logger.debug("PNG render exception for %s", dot_path, exc_info=True)

    stats = {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "subsystems": len(subsystems_def),
        "modules": len(modules_def),
    }

    return {
        "success": True,
        "outputs": {
            "overview": overview_path,
            "subsystems": subsystem_paths,
        },
        "stats": stats,
        "warnings": warnings,
        "regenerated": regenerated,
        "skipped": skipped,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_dot_file(dot_path: str) -> pydot.Dot | None:
    """Parse a DOT file to a pydot.Dot graph.

    Args:
        dot_path: Path to the DOT file.

    Returns:
        pydot.Dot on success, None on any failure (missing file, parse error).
    """
    if not dot_path:
        return None

    try:
        content = Path(dot_path).read_text()
    except OSError:
        return None

    if not content.strip():
        return None

    captured = io.StringIO()
    graphs: list[pydot.Dot] | None = None
    with contextlib.redirect_stdout(captured):
        try:
            graphs = pydot.graph_from_dot_data(content)
        except Exception:  # noqa: BLE001
            return None

    if not graphs:
        return None

    return graphs[0]


def _count_graph_elements(graph: pydot.Dot) -> tuple[int, int]:
    """Count real nodes and edges in a pydot graph, excluding pseudo-nodes.

    Recursively includes nodes and edges from subgraphs.

    Args:
        graph: A pydot.Dot or pydot.Subgraph.

    Returns:
        (node_count, edge_count) tuple.
    """
    nodes: set[str] = set()
    edges: int = 0

    def _collect(g: pydot.Graph) -> None:
        nonlocal edges
        for node in g.get_node_list():
            name = node.get_name().strip('"')
            if name not in _PSEUDO_NODES:
                nodes.add(name)
        edges += len(g.get_edge_list())
        for sg in g.get_subgraph_list():
            _collect(sg)

    _collect(graph)

    # Also count nodes that appear only in edges (implicit nodes)
    def _collect_edge_nodes(g: pydot.Graph) -> None:
        for edge in g.get_edge_list():
            src = str(edge.get_source()).strip('"')
            dst = str(edge.get_destination()).strip('"')
            if src not in _PSEUDO_NODES:
                nodes.add(src)
            if dst not in _PSEUDO_NODES:
                nodes.add(dst)
        for sg in g.get_subgraph_list():
            _collect_edge_nodes(sg)

    _collect_edge_nodes(graph)

    return len(nodes), edges


def _copy_module_elements_to_cluster(
    mod_graph: pydot.Dot,
    cluster: pydot.Subgraph,
) -> None:
    """Copy nodes (excluding pseudo-nodes) and edges from a module graph into a cluster.

    Args:
        mod_graph: Parsed pydot.Dot graph for a single module.
        cluster: Target pydot.Subgraph cluster to receive the elements.
    """
    for node in mod_graph.get_node_list():
        name = node.get_name().strip('"')
        if name in _PSEUDO_NODES:
            continue
        new_node = pydot.Node(node.get_name())
        new_node.obj_dict = node.obj_dict.copy()
        cluster.add_node(new_node)

    for edge in mod_graph.get_edge_list():
        new_edge = pydot.Edge(edge.get_source(), edge.get_destination())
        new_edge.obj_dict = edge.obj_dict.copy()
        cluster.add_edge(new_edge)


def _build_subsystem_dot(
    subsystem_name: str,
    module_names: list[str],
    parsed_modules: dict[str, pydot.Dot],
) -> pydot.Dot:
    """Build a subsystem DOT graph with each module as a cluster subgraph.

    Args:
        subsystem_name: Name of the subsystem.
        module_names: List of module names in this subsystem.
        parsed_modules: Map from module name to parsed pydot.Dot graph.

    Returns:
        pydot.Dot graph representing the subsystem.
    """
    ss_graph = pydot.Dot(
        graph_name=f'"{subsystem_name}"',
        graph_type="digraph",
    )
    ss_graph.set("label", f'"{subsystem_name}"')

    for mod_name in module_names:
        if mod_name not in parsed_modules:
            continue

        mod_graph = parsed_modules[mod_name]
        cluster = pydot.Subgraph(f"cluster_{mod_name}")
        cluster.set("label", f'"{mod_name}"')

        _copy_module_elements_to_cluster(mod_graph, cluster)
        ss_graph.add_subgraph(cluster)

    return ss_graph


def _build_overview_dot(
    subsystems_def: dict,
    parsed_modules: dict[str, pydot.Dot],
) -> pydot.Dot:
    """Build an overview DOT graph with subsystems as cluster subgraphs.

    Auto-collapses if the overview would exceed _MAX_OVERVIEW_NODES nodes or
    _MAX_OVERVIEW_LINES lines.

    Args:
        subsystems_def: {ss_name: {modules: [mod_name]}} manifest fragment.
        parsed_modules: Map from module name to parsed pydot.Dot graph.

    Returns:
        pydot.Dot graph for the overview.
    """
    # Try full overview first, then check size limits
    full_graph = _build_full_overview(subsystems_def, parsed_modules)
    full_dot = full_graph.to_string()

    total_nodes = sum(
        _count_graph_elements(parsed_modules[m])[0]
        for ss_info in subsystems_def.values()
        for m in ss_info.get("modules", [])
        if m in parsed_modules
    )
    line_count = len(full_dot.splitlines())

    if total_nodes > _MAX_OVERVIEW_NODES or line_count > _MAX_OVERVIEW_LINES:
        return _build_collapsed_overview(subsystems_def, parsed_modules)

    return full_graph


def _build_full_overview(
    subsystems_def: dict,
    parsed_modules: dict[str, pydot.Dot],
) -> pydot.Dot:
    """Build a full (uncollapsed) overview DOT graph.

    Each subsystem becomes a cluster, containing each module as a nested cluster.

    Args:
        subsystems_def: Subsystem definitions from manifest.
        parsed_modules: Parsed module graphs.

    Returns:
        pydot.Dot overview graph.
    """
    overview = pydot.Dot(graph_name='"overview"', graph_type="digraph")
    overview.set("label", '"Overview"')

    for ss_name, ss_info in subsystems_def.items():
        ss_cluster = pydot.Subgraph(f"cluster_{ss_name}")
        ss_cluster.set("label", f'"{ss_name}"')

        for mod_name in ss_info.get("modules", []):
            if mod_name not in parsed_modules:
                continue

            mod_graph = parsed_modules[mod_name]
            mod_cluster = pydot.Subgraph(f"cluster_{mod_name}")
            mod_cluster.set("label", f'"{mod_name}"')

            _copy_module_elements_to_cluster(mod_graph, mod_cluster)
            ss_cluster.add_subgraph(mod_cluster)

        overview.add_subgraph(ss_cluster)

    return overview


def _build_collapsed_overview(
    subsystems_def: dict,
    parsed_modules: dict[str, pydot.Dot],
) -> pydot.Dot:
    """Build a collapsed overview where each module is a single representative node.

    Used when the full overview would exceed size limits.

    Args:
        subsystems_def: Subsystem definitions from manifest.
        parsed_modules: Parsed module graphs.

    Returns:
        Collapsed pydot.Dot overview graph.
    """
    overview = pydot.Dot(graph_name='"overview"', graph_type="digraph")
    overview.set("label", '"Overview (collapsed)"')

    for ss_name, ss_info in subsystems_def.items():
        ss_cluster = pydot.Subgraph(f"cluster_{ss_name}")
        ss_cluster.set("label", f'"{ss_name}"')

        for mod_name in ss_info.get("modules", []):
            # Each module becomes a single representative node
            node = pydot.Node(f'"{mod_name}"', shape="box", style="filled")
            ss_cluster.add_node(node)

        overview.add_subgraph(ss_cluster)

    return overview


def _add_legend(graph: pydot.Dot, title: str) -> None:
    """Add a legend subgraph with timestamp and title to the graph.

    Mutates graph in-place.

    Args:
        graph: The pydot.Dot graph to annotate.
        title: Human-readable title for the legend.
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    legend_label = f'"{title}\\nGenerated: {timestamp}"'

    legend = pydot.Subgraph("cluster_legend")
    legend.set("label", legend_label)
    legend.set("style", '"dashed"')
    legend.set("color", '"gray"')

    # Add a single invisible node to anchor the cluster
    anchor = pydot.Node(
        '"_legend_anchor"',
        style='"invis"',
        shape='"point"',
        width="0",
    )
    legend.add_node(anchor)

    graph.add_subgraph(legend)


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _error(message: str) -> dict:
    """Build a standardized error response dict."""
    return {"success": False, "error": message}
