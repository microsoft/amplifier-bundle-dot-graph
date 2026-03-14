# Phase 2: Validation, Rendering & Setup Tools — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Replace the placeholder `DotGraphTool` with a real tool that routes to three implementation modules: `setup_helper.py` (environment detection), `validate.py` (three-layer DOT validation), and `render.py` (graphviz CLI wrapper).

**Architecture:** Single `dot_graph` tool with an `operation` parameter that routes to the appropriate module. `setup_helper` is a shared utility imported by both `validate` and `render` for graphviz detection and graceful degradation. All operations return structured JSON inside `ToolResult.output`. The `analyze` operation stays as a Phase 3 placeholder.

**Tech Stack:** Python ≥3.11, pydot ≥3.0 (DOT parsing), graphviz CLI (optional — graceful degradation), pytest + pytest-asyncio (testing), amplifier-core (ToolResult)

**Design doc:** `docs/plans/2026-03-13-dot-graph-bundle-design.md` (Tier 2 section)

---

## Verified Codebase Facts

These were confirmed by reading actual files and running code — not guessed:

- **pydot v4.0.1** — `pydot.graph_from_dot_data(s)` returns `None` (not exception) on invalid DOT. Parse error messages print to **stdout** (not stderr). Returns `list[pydot.Dot]` on success.
- **pydot node gotcha** — Nodes declared inside subgraphs do NOT appear in the top-level `get_node_list()`. Must recurse through `get_subgraph_list()`. Default style entries (`node`, `edge`, `graph`) appear as pseudo-nodes — filter them out.
- **graphviz v2.43.0** installed at `/usr/bin/dot`. All engines available: dot, neato, fdp, sfdp, twopi, circo.
- **networkx v3.6.1** installed.
- **ToolResult** — `from amplifier_core import ToolResult`. Constructor: `ToolResult(success=bool, output=str)`.
- **Existing tests** — 15 tests in `modules/tool-dot-graph/tests/test_mount_stub.py`, all passing. Uses `pytest-asyncio` with `asyncio_mode = "auto"`.
- **Test runner** — `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short`

---

## File Map

| Action | Path |
|--------|------|
| Create | `modules/tool-dot-graph/amplifier_module_tool_dot_graph/setup_helper.py` |
| Create | `modules/tool-dot-graph/amplifier_module_tool_dot_graph/validate.py` |
| Create | `modules/tool-dot-graph/amplifier_module_tool_dot_graph/render.py` |
| Modify | `modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py` |
| Create | `modules/tool-dot-graph/tests/test_setup_helper.py` |
| Create | `modules/tool-dot-graph/tests/test_validate.py` |
| Create | `modules/tool-dot-graph/tests/test_render.py` |
| Create | `modules/tool-dot-graph/tests/test_tool_integration.py` |
| Rename | `modules/tool-dot-graph/tests/test_mount_stub.py` → `tests/test_mount.py` |

---

## Task 1: Environment Detection (`setup_helper.py`)

**Files:**
- Create: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/setup_helper.py`
- Test: `modules/tool-dot-graph/tests/test_setup_helper.py`

### Step 1: Write the failing tests

Create `modules/tool-dot-graph/tests/test_setup_helper.py`:

```python
"""Tests for setup_helper — environment detection for DOT graph tools."""

from unittest.mock import patch


def test_check_environment_returns_dict():
    """check_environment() returns a dict with all required top-level keys."""
    from amplifier_module_tool_dot_graph import setup_helper

    result = setup_helper.check_environment()
    assert isinstance(result, dict)
    assert "graphviz" in result
    assert "pydot" in result
    assert "networkx" in result


def test_graphviz_status_has_installed_key():
    """graphviz status always includes 'installed' as a bool."""
    from amplifier_module_tool_dot_graph import setup_helper

    gv = setup_helper.check_environment()["graphviz"]
    assert "installed" in gv
    assert isinstance(gv["installed"], bool)


def test_graphviz_installed_includes_version_and_engines():
    """When graphviz IS installed, version and engines are populated."""
    from amplifier_module_tool_dot_graph import setup_helper

    gv = setup_helper.check_environment()["graphviz"]
    if gv["installed"]:
        assert "version" in gv
        assert "engines" in gv
        assert isinstance(gv["engines"], list)
        assert len(gv["engines"]) > 0
        assert "dot" in gv["engines"]


def test_graphviz_not_installed_returns_hint():
    """When graphviz is NOT on PATH, returns install_hint and empty engines."""
    from amplifier_module_tool_dot_graph import setup_helper

    with patch("shutil.which", return_value=None):
        gv = setup_helper._check_graphviz()
    assert gv["installed"] is False
    assert gv["version"] is None
    assert gv["engines"] == []
    assert "install_hint" in gv
    assert isinstance(gv["install_hint"], str)
    assert len(gv["install_hint"]) > 0


def test_pydot_detected():
    """pydot is a declared dependency — must always be detected."""
    from amplifier_module_tool_dot_graph import setup_helper

    result = setup_helper.check_environment()
    assert result["pydot"]["installed"] is True
    assert result["pydot"]["version"] is not None


def test_networkx_detected():
    """networkx is a declared dependency — must always be detected."""
    from amplifier_module_tool_dot_graph import setup_helper

    result = setup_helper.check_environment()
    assert result["networkx"]["installed"] is True
    assert result["networkx"]["version"] is not None


def test_install_hint_is_nonempty_string():
    """_install_hint() always returns a useful string."""
    from amplifier_module_tool_dot_graph import setup_helper

    hint = setup_helper._install_hint()
    assert isinstance(hint, str)
    assert len(hint) > 0
```

### Step 2: Run tests to verify they fail

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_setup_helper.py -v --tb=short
```

Expected: **FAIL** — `ModuleNotFoundError` or `ImportError` because `setup_helper` does not exist yet.

### Step 3: Write the implementation

Create `modules/tool-dot-graph/amplifier_module_tool_dot_graph/setup_helper.py`:

```python
"""Environment detection for DOT graph tools.

Detects availability of graphviz CLI, pydot, and networkx.
Returns structured status dicts for use by validate.py and render.py.
"""

import platform
import shutil
import subprocess


def check_environment() -> dict:
    """Check all DOT graph tool dependencies.

    Returns:
        Dict with keys: graphviz, pydot, networkx — each containing
        availability status and version info.
    """
    return {
        "graphviz": _check_graphviz(),
        "pydot": _check_pydot(),
        "networkx": _check_networkx(),
    }


def _check_graphviz() -> dict:
    """Detect graphviz CLI installation, version, and available engines."""
    dot_path = shutil.which("dot")
    if not dot_path:
        return {
            "installed": False,
            "version": None,
            "engines": [],
            "install_hint": _install_hint(),
        }

    version = None
    try:
        result = subprocess.run(
            ["dot", "-V"], capture_output=True, text=True, timeout=5
        )
        # dot -V prints version to stderr
        version_text = result.stderr.strip() or result.stdout.strip()
        if version_text:
            version = version_text
    except (subprocess.TimeoutExpired, OSError):
        pass

    engines = []
    for name in ("dot", "neato", "fdp", "sfdp", "twopi", "circo"):
        if shutil.which(name):
            engines.append(name)

    return {
        "installed": True,
        "version": version,
        "engines": engines,
    }


def _check_pydot() -> dict:
    """Detect pydot Python package."""
    try:
        import pydot

        return {"installed": True, "version": pydot.__version__}
    except ImportError:
        return {"installed": False, "version": None}


def _check_networkx() -> dict:
    """Detect networkx Python package."""
    try:
        import networkx

        return {"installed": True, "version": networkx.__version__}
    except ImportError:
        return {"installed": False, "version": None}


def _install_hint() -> str:
    """Return platform-appropriate install guidance for Graphviz."""
    system = platform.system()
    if system == "Darwin":
        return "brew install graphviz"
    elif system == "Linux":
        return "sudo apt-get install graphviz  # or: sudo dnf install graphviz"
    elif system == "Windows":
        return "winget install graphviz  # or: choco install graphviz"
    return "Install Graphviz from https://graphviz.org/download/"
```

### Step 4: Run tests to verify they pass

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_setup_helper.py -v --tb=short
```

Expected: **7 passed**

### Step 5: Run full existing test suite to check nothing broke

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: **22 passed** (15 existing + 7 new)

### Step 6: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/setup_helper.py modules/tool-dot-graph/tests/test_setup_helper.py && git commit -m "feat: add setup_helper for environment detection (graphviz, pydot, networkx)"
```

---

## Task 2: Three-Layer DOT Validation (`validate.py`)

**Files:**
- Create: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/validate.py`
- Test: `modules/tool-dot-graph/tests/test_validate.py`

**Depends on:** Task 1 (imports `setup_helper` for Layer 3 graphviz detection)

### Step 1: Write the failing tests

Create `modules/tool-dot-graph/tests/test_validate.py`:

```python
"""Tests for validate — three-layer DOT validation."""

import shutil
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Layer 1: Syntax (pydot parse)
# ---------------------------------------------------------------------------


def test_valid_dot_returns_valid():
    """Valid DOT content parses successfully."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("digraph G { a -> b; }")
    assert result["valid"] is True
    assert not any(i["severity"] == "error" for i in result["issues"])


def test_invalid_dot_fails_syntax():
    """Invalid DOT content fails at the syntax layer."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("not valid dot at all")
    assert result["valid"] is False
    syntax_errors = [i for i in result["issues"] if i["layer"] == "syntax"]
    assert len(syntax_errors) > 0
    assert syntax_errors[0]["severity"] == "error"


def test_empty_string_fails_syntax():
    """Empty string fails at the syntax layer."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("")
    assert result["valid"] is False


def test_whitespace_only_fails_syntax():
    """Whitespace-only string fails at the syntax layer."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("   \n  ")
    assert result["valid"] is False


def test_undirected_graph_parses():
    """Undirected graphs (graph, not digraph) parse correctly."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("graph G { a -- b; }")
    assert result["valid"] is True


# ---------------------------------------------------------------------------
# Layer 2: Structural
# ---------------------------------------------------------------------------


def test_empty_graph_structural_error():
    """A graph with no nodes or edges gets a structural error."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("digraph G { }", layers=["syntax", "structural"])
    structural = [i for i in result["issues"] if i["layer"] == "structural"]
    assert any(i["severity"] == "error" for i in structural)


def test_unreachable_node_warning():
    """Nodes with no incoming edges (not entry points) get a warning."""
    from amplifier_module_tool_dot_graph import validate

    # 'a' and 'c' are roots (no incoming), 'b' and 'd' have incoming
    dot = "digraph G { a -> b; c -> d; }"
    result = validate.validate_dot(dot, layers=["syntax", "structural"])
    unreachable = [
        i
        for i in result["issues"]
        if i["layer"] == "structural" and "no incoming" in i["message"]
    ]
    assert len(unreachable) > 0


def test_entry_point_names_not_flagged():
    """Nodes named 'start', 'entry', 'root' are NOT flagged as unreachable."""
    from amplifier_module_tool_dot_graph import validate

    dot = "digraph G { start -> a; a -> b; }"
    result = validate.validate_dot(dot, layers=["syntax", "structural"])
    structural_warns = [
        i
        for i in result["issues"]
        if i["layer"] == "structural" and i["severity"] == "warn"
    ]
    assert len(structural_warns) == 0


def test_isolated_node_warning():
    """A node with zero edges gets an isolated-node warning."""
    from amplifier_module_tool_dot_graph import validate

    dot = "digraph G { a -> b; c; }"
    result = validate.validate_dot(dot, layers=["syntax", "structural"])
    isolated = [
        i
        for i in result["issues"]
        if i["layer"] == "structural" and "isolated" in i["message"]
    ]
    assert len(isolated) > 0


def test_orphan_cluster_warning():
    """A cluster with no edges to outside nodes gets a warning."""
    from amplifier_module_tool_dot_graph import validate

    dot = """digraph G {
        subgraph cluster_orphan { x; y; x -> y; }
        a -> b;
    }"""
    result = validate.validate_dot(dot, layers=["syntax", "structural"])
    orphan = [
        i
        for i in result["issues"]
        if i["layer"] == "structural" and "no edges connecting" in i["message"]
    ]
    assert len(orphan) > 0


def test_connected_cluster_no_orphan_warning():
    """A cluster with edges to outside nodes does NOT get an orphan warning."""
    from amplifier_module_tool_dot_graph import validate

    dot = """digraph G {
        subgraph cluster_0 { x; y; x -> y; }
        a -> x;
    }"""
    result = validate.validate_dot(dot, layers=["syntax", "structural"])
    orphan = [
        i
        for i in result["issues"]
        if i["layer"] == "structural" and "no edges connecting" in i["message"]
    ]
    assert len(orphan) == 0


def test_stats_counting():
    """Stats correctly count nodes, edges, clusters, and lines."""
    from amplifier_module_tool_dot_graph import validate

    dot = """digraph G {
        subgraph cluster_0 { a; b; }
        a -> b;
        b -> c;
    }"""
    result = validate.validate_dot(dot, layers=["syntax", "structural"])
    assert result["stats"]["nodes"] >= 3
    assert result["stats"]["edges"] >= 2
    assert result["stats"]["clusters"] >= 1
    assert result["stats"]["lines"] >= 4


def test_legend_info_for_large_graphs():
    """Graphs with 10+ nodes and no legend get an info-level message."""
    from amplifier_module_tool_dot_graph import validate

    nodes = "; ".join(f"n{i}" for i in range(12))
    edges = "; ".join(f"n{i} -> n{i+1}" for i in range(11))
    dot = f"digraph G {{ {nodes}; {edges}; }}"
    result = validate.validate_dot(dot, layers=["syntax", "structural"])
    legend_info = [
        i
        for i in result["issues"]
        if i["layer"] == "structural" and "legend" in i["message"].lower()
    ]
    assert len(legend_info) > 0
    assert legend_info[0]["severity"] == "info"


# ---------------------------------------------------------------------------
# Layer 3: Render quality
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("dot"), reason="Graphviz not installed")
def test_render_quality_valid_dot():
    """Valid DOT passes render quality check when graphviz is available."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("digraph G { a -> b; }", layers=["render"])
    render_errors = [
        i
        for i in result["issues"]
        if i["layer"] == "render" and i["severity"] == "error"
    ]
    assert len(render_errors) == 0


def test_render_quality_skipped_without_graphviz():
    """When graphviz is absent, Layer 3 skips gracefully with info message."""
    from amplifier_module_tool_dot_graph import validate

    with patch(
        "amplifier_module_tool_dot_graph.setup_helper.check_environment",
        return_value={
            "graphviz": {
                "installed": False,
                "install_hint": "brew install graphviz",
            },
            "pydot": {"installed": True, "version": "4.0"},
            "networkx": {"installed": True, "version": "3.0"},
        },
    ):
        result = validate.validate_dot("digraph G { a -> b; }", layers=["render"])
    render_info = [
        i
        for i in result["issues"]
        if i["layer"] == "render" and i["severity"] == "info"
    ]
    assert len(render_info) > 0
    assert "not installed" in render_info[0]["message"].lower()


# ---------------------------------------------------------------------------
# Layer selection
# ---------------------------------------------------------------------------


def test_syntax_only_layer():
    """When layers=['syntax'], only syntax issues appear."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("digraph G { a -> b; }", layers=["syntax"])
    for issue in result["issues"]:
        assert issue["layer"] == "syntax"


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------


def test_result_has_required_keys():
    """Every result has valid, issues, and stats."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("digraph G { a -> b; }")
    assert "valid" in result
    assert "issues" in result
    assert "stats" in result
    assert isinstance(result["valid"], bool)
    assert isinstance(result["issues"], list)
    assert isinstance(result["stats"], dict)


def test_issue_structure():
    """Each issue has layer, severity, and message keys."""
    from amplifier_module_tool_dot_graph import validate

    result = validate.validate_dot("not valid")
    assert len(result["issues"]) > 0
    for issue in result["issues"]:
        assert "layer" in issue
        assert "severity" in issue
        assert "message" in issue
```

### Step 2: Run tests to verify they fail

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_validate.py -v --tb=short
```

Expected: **FAIL** — `ImportError` because `validate` module does not exist yet.

### Step 3: Write the implementation

Create `modules/tool-dot-graph/amplifier_module_tool_dot_graph/validate.py`:

```python
"""Three-layer DOT validation.

Layer 1 (Syntax): Parse via pydot. No graphviz required.
Layer 2 (Structural): Inspect parsed graph for issues. No graphviz required.
Layer 3 (Render quality): Test render via graphviz CLI. Requires graphviz.
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import tempfile

import pydot

from . import setup_helper


def validate_dot(
    dot_content: str,
    layers: list[str] | None = None,
) -> dict:
    """Validate DOT content through up to three layers.

    Args:
        dot_content: DOT format string to validate.
        layers: Which layers to run. Default: all available.
                Options: "syntax", "structural", "render".

    Returns:
        {
            "valid": bool,       # True if no errors (warnings/info OK)
            "issues": [{"layer": str, "severity": str, "message": str}, ...],
            "stats": {"nodes": int, "edges": int, "clusters": int, "lines": int}
        }
    """
    if layers is None:
        layers = ["syntax", "structural", "render"]

    issues: list[dict] = []
    line_count = dot_content.count("\n") + 1 if dot_content.strip() else 0
    stats = {"nodes": 0, "edges": 0, "clusters": 0, "lines": line_count}
    graph = None

    # Layer 1: Syntax
    if "syntax" in layers:
        graph, syntax_issues = _check_syntax(dot_content)
        issues.extend(syntax_issues)

    # Layer 2: Structural (only if syntax passed)
    if "structural" in layers and graph is not None:
        structural_issues, structural_stats = _check_structural(graph)
        issues.extend(structural_issues)
        stats.update(structural_stats)
        # lines is preserved because structural_stats doesn't include it

    # Layer 3: Render quality (only if syntax passed)
    if "render" in layers and graph is not None:
        render_issues = _check_render_quality(dot_content)
        issues.extend(render_issues)

    has_errors = any(i["severity"] == "error" for i in issues)

    return {
        "valid": not has_errors,
        "issues": issues,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# Layer 1: Syntax
# ---------------------------------------------------------------------------


def _check_syntax(dot_content: str) -> tuple[pydot.Dot | None, list[dict]]:
    """Parse DOT with pydot, capturing any error output."""
    issues: list[dict] = []

    if not dot_content or not dot_content.strip():
        issues.append({
            "layer": "syntax",
            "severity": "error",
            "message": "Empty DOT content",
        })
        return None, issues

    # pydot prints parse errors to stdout (via pyparsing) — capture them
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        result = pydot.graph_from_dot_data(dot_content)

    error_output = capture.getvalue().strip()

    if result is None or (isinstance(result, list) and len(result) == 0):
        msg = "DOT syntax parse failed"
        if error_output:
            # Keep only the first line of error for conciseness
            first_line = error_output.split("\n")[0].strip()
            if first_line:
                msg += f": {first_line}"
        issues.append({
            "layer": "syntax",
            "severity": "error",
            "message": msg,
        })
        return None, issues

    return result[0], issues


# ---------------------------------------------------------------------------
# Layer 2: Structural
# ---------------------------------------------------------------------------


def _collect_all_nodes(graph: pydot.Dot | pydot.Subgraph) -> set[str]:
    """Recursively collect all real node names from graph and subgraphs.

    Filters out pydot pseudo-nodes ('node', 'edge', 'graph') which represent
    default attribute statements, not actual graph nodes.
    """
    nodes: set[str] = set()
    for n in graph.get_node_list():
        name = n.get_name().strip('"')
        # 'node', 'edge', 'graph' are default style entries, not real nodes
        if name not in ("node", "edge", "graph"):
            nodes.add(name)
    for s in graph.get_subgraph_list():
        nodes.update(_collect_all_nodes(s))
    return nodes


def _collect_all_edges(
    graph: pydot.Dot | pydot.Subgraph,
) -> set[tuple[str, str]]:
    """Recursively collect all edges from graph and subgraphs."""
    edges: set[tuple[str, str]] = set()
    for e in graph.get_edge_list():
        src = e.get_source().strip('"')
        dst = e.get_destination().strip('"')
        edges.add((src, dst))
    for s in graph.get_subgraph_list():
        edges.update(_collect_all_edges(s))
    return edges


def _collect_clusters(
    graph: pydot.Dot | pydot.Subgraph,
) -> list[tuple[str, set[str]]]:
    """Collect cluster subgraphs and their node sets (recursive)."""
    clusters: list[tuple[str, set[str]]] = []
    for s in graph.get_subgraph_list():
        name = s.get_name().strip('"')
        if name.startswith("cluster"):
            cluster_nodes = _collect_all_nodes(s)
            clusters.append((name, cluster_nodes))
        # Recurse into nested subgraphs for nested clusters
        clusters.extend(_collect_clusters(s))
    return clusters


def _check_structural(graph: pydot.Dot) -> tuple[list[dict], dict]:
    """Layer 2: Structural analysis of the parsed pydot graph."""
    issues: list[dict] = []

    all_nodes = _collect_all_nodes(graph)
    all_edges = _collect_all_edges(graph)
    clusters = _collect_clusters(graph)

    stats = {
        "nodes": len(all_nodes),
        "edges": len(all_edges),
        "clusters": len(clusters),
    }

    # Check: empty graph
    if not all_nodes and not all_edges:
        issues.append({
            "layer": "structural",
            "severity": "error",
            "message": "Graph is empty (no nodes or edges)",
        })
        return issues, stats

    # Check: unreachable nodes (digraph only — concept doesn't apply to undirected)
    if graph.get_type() == "digraph":
        destinations = {dst for _, dst in all_edges}
        sources = {src for src, _ in all_edges}
        entry_hints = {"start", "entry", "root", "begin", "init", "source"}

        for node in sorted(all_nodes):
            if node in destinations:
                continue  # Has incoming edges — reachable
            if node in sources:
                # Has outgoing but no incoming — entry point or unreachable
                if node.lower() not in entry_hints:
                    issues.append({
                        "layer": "structural",
                        "severity": "warn",
                        "message": (
                            f"Node '{node}' has no incoming edges"
                            " (unreachable or entry point)"
                        ),
                    })
            else:
                # No edges at all — isolated
                issues.append({
                    "layer": "structural",
                    "severity": "warn",
                    "message": f"Node '{node}' is isolated (no edges)",
                })

    # Check: orphan clusters (no edges connecting to outside)
    for cluster_name, cluster_nodes in clusters:
        if not cluster_nodes:
            continue
        has_external_edge = False
        for src, dst in all_edges:
            src_in = src in cluster_nodes
            dst_in = dst in cluster_nodes
            if src_in != dst_in:  # One inside, one outside
                has_external_edge = True
                break
        if not has_external_edge:
            issues.append({
                "layer": "structural",
                "severity": "warn",
                "message": (
                    f"Cluster '{cluster_name}' has no edges connecting"
                    " to nodes outside it"
                ),
            })

    # Check: missing legend (info-level, only for graphs with 10+ nodes)
    if len(all_nodes) >= 10:
        has_legend = any("legend" in name.lower() for name, _ in clusters)
        if not has_legend:
            issues.append({
                "layer": "structural",
                "severity": "info",
                "message": (
                    "No legend subgraph found"
                    " (recommended for graphs with 10+ nodes)"
                ),
            })

    return issues, stats


# ---------------------------------------------------------------------------
# Layer 3: Render quality
# ---------------------------------------------------------------------------


def _check_render_quality(dot_content: str) -> list[dict]:
    """Layer 3: Verify the DOT actually renders via graphviz CLI."""
    issues: list[dict] = []

    env_status = setup_helper.check_environment()
    if not env_status["graphviz"]["installed"]:
        hint = env_status["graphviz"].get(
            "install_hint", "Install Graphviz from https://graphviz.org/download/"
        )
        issues.append({
            "layer": "render",
            "severity": "info",
            "message": (
                f"Skipped render quality check (Graphviz not installed). {hint}"
            ),
        })
        return issues

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dot", delete=False
        ) as f:
            f.write(dot_content)
            tmp_path = f.name

        result = subprocess.run(
            ["dot", "-Tcanon", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            msg = "Graphviz render check failed"
            if result.stderr.strip():
                msg += f": {result.stderr.strip()}"
            issues.append({
                "layer": "render",
                "severity": "error",
                "message": msg,
            })
        elif result.stderr.strip():
            # Rendered OK but graphviz emitted warnings
            issues.append({
                "layer": "render",
                "severity": "warn",
                "message": f"Graphviz warnings: {result.stderr.strip()}",
            })
    except subprocess.TimeoutExpired:
        issues.append({
            "layer": "render",
            "severity": "error",
            "message": "Graphviz render check timed out (>30s)",
        })
    except OSError as e:
        issues.append({
            "layer": "render",
            "severity": "error",
            "message": f"Failed to run graphviz: {e}",
        })
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return issues
```

### Step 4: Run tests to verify they pass

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_validate.py -v --tb=short
```

Expected: **20 passed** (or 19 passed + 1 skipped if graphviz absent in CI)

### Step 5: Run full test suite

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: All tests pass (existing 15 + 7 setup_helper + 20 validate)

### Step 6: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/validate.py modules/tool-dot-graph/tests/test_validate.py && git commit -m "feat: add three-layer DOT validation (syntax, structural, render quality)"
```

---

## Task 3: Graphviz CLI Rendering (`render.py`)

**Files:**
- Create: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/render.py`
- Test: `modules/tool-dot-graph/tests/test_render.py`

**Depends on:** Task 1 (imports `setup_helper` for graphviz detection)

### Step 1: Write the failing tests

Create `modules/tool-dot-graph/tests/test_render.py`:

```python
"""Tests for render — Graphviz CLI rendering wrapper."""

import os
import shutil
from unittest.mock import patch

import pytest

SIMPLE_DOT = "digraph G { a -> b; }"

HAS_GRAPHVIZ = shutil.which("dot") is not None
HAS_NEATO = shutil.which("neato") is not None


# ---------------------------------------------------------------------------
# Successful rendering (requires graphviz)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_GRAPHVIZ, reason="Graphviz not installed")
def test_render_svg_default():
    """Default render produces an SVG file."""
    from amplifier_module_tool_dot_graph import render

    result = render.render_dot(SIMPLE_DOT)
    assert result["success"] is True
    assert result["output_path"].endswith(".svg")
    assert result["format"] == "svg"
    assert result["engine"] == "dot"
    assert os.path.exists(result["output_path"])
    assert result["size_bytes"] > 0
    os.unlink(result["output_path"])


@pytest.mark.skipif(not HAS_GRAPHVIZ, reason="Graphviz not installed")
def test_render_png():
    """Render to PNG format."""
    from amplifier_module_tool_dot_graph import render

    result = render.render_dot(SIMPLE_DOT, output_format="png")
    assert result["success"] is True
    assert result["output_path"].endswith(".png")
    assert result["format"] == "png"
    os.unlink(result["output_path"])


@pytest.mark.skipif(not HAS_NEATO, reason="neato not installed")
def test_render_with_neato_engine():
    """Render using the neato layout engine."""
    from amplifier_module_tool_dot_graph import render

    result = render.render_dot(SIMPLE_DOT, engine="neato")
    assert result["success"] is True
    assert result["engine"] == "neato"
    os.unlink(result["output_path"])


@pytest.mark.skipif(not HAS_GRAPHVIZ, reason="Graphviz not installed")
def test_render_custom_output_path(tmp_path):
    """Render to a caller-specified output path."""
    from amplifier_module_tool_dot_graph import render

    out = str(tmp_path / "test_output.svg")
    result = render.render_dot(SIMPLE_DOT, output_path=out)
    assert result["success"] is True
    assert result["output_path"] == out
    assert os.path.exists(out)


# ---------------------------------------------------------------------------
# Input validation (no graphviz needed)
# ---------------------------------------------------------------------------


def test_unsupported_format_returns_error():
    """Unsupported output format returns error without calling graphviz."""
    from amplifier_module_tool_dot_graph import render

    result = render.render_dot(SIMPLE_DOT, output_format="bmp")
    assert result["success"] is False
    assert "Unsupported format" in result["error"]


def test_unsupported_engine_returns_error():
    """Unsupported engine name returns error without calling graphviz."""
    from amplifier_module_tool_dot_graph import render

    result = render.render_dot(SIMPLE_DOT, engine="invalid_engine")
    assert result["success"] is False
    assert "Unsupported engine" in result["error"]


# ---------------------------------------------------------------------------
# Graceful degradation
# ---------------------------------------------------------------------------


def test_no_graphviz_returns_install_hint():
    """When graphviz is absent, returns error with install guidance."""
    from amplifier_module_tool_dot_graph import render

    with patch(
        "amplifier_module_tool_dot_graph.setup_helper.check_environment",
        return_value={
            "graphviz": {
                "installed": False,
                "version": None,
                "engines": [],
                "install_hint": "brew install graphviz",
            },
            "pydot": {"installed": True, "version": "4.0"},
            "networkx": {"installed": True, "version": "3.0"},
        },
    ):
        result = render.render_dot(SIMPLE_DOT)
    assert result["success"] is False
    assert "not installed" in result["error"].lower()


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_GRAPHVIZ, reason="Graphviz not installed")
def test_success_result_has_required_keys():
    """Successful render result contains all expected keys."""
    from amplifier_module_tool_dot_graph import render

    result = render.render_dot(SIMPLE_DOT)
    assert "success" in result
    assert "output_path" in result
    assert "format" in result
    assert "engine" in result
    assert "size_bytes" in result
    os.unlink(result["output_path"])


def test_error_result_has_required_keys():
    """Error render result contains success=False and error message."""
    from amplifier_module_tool_dot_graph import render

    result = render.render_dot(SIMPLE_DOT, output_format="bmp")
    assert result["success"] is False
    assert "error" in result
    assert isinstance(result["error"], str)
```

### Step 2: Run tests to verify they fail

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_render.py -v --tb=short
```

Expected: **FAIL** — `ImportError` because `render` module does not exist yet.

### Step 3: Write the implementation

Create `modules/tool-dot-graph/amplifier_module_tool_dot_graph/render.py`:

```python
"""Graphviz CLI rendering wrapper.

Renders DOT content to SVG, PNG, PDF, or JSON via graphviz subprocess.
Uses setup_helper for environment detection and graceful degradation.
"""

from __future__ import annotations

import os
import subprocess
import tempfile

from . import setup_helper

SUPPORTED_FORMATS = ("svg", "png", "pdf", "json", "ps", "eps")
SUPPORTED_ENGINES = ("dot", "neato", "fdp", "sfdp", "twopi", "circo")


def render_dot(
    dot_content: str,
    output_format: str = "svg",
    engine: str = "dot",
    output_path: str | None = None,
) -> dict:
    """Render DOT content to an output format via graphviz CLI.

    Args:
        dot_content: DOT format string to render.
        output_format: Output format — svg, png, pdf, json, ps, eps.
        engine: Layout engine — dot, neato, fdp, sfdp, twopi, circo.
        output_path: Where to write output. Auto-generated temp file if None.

    Returns:
        On success: {"success": True, "output_path": str, "format": str,
                      "engine": str, "size_bytes": int}
        On failure: {"success": False, "error": str}
    """
    # Validate format
    if output_format not in SUPPORTED_FORMATS:
        return {
            "success": False,
            "error": (
                f"Unsupported format '{output_format}'."
                f" Supported: {', '.join(SUPPORTED_FORMATS)}"
            ),
        }

    # Validate engine
    if engine not in SUPPORTED_ENGINES:
        return {
            "success": False,
            "error": (
                f"Unsupported engine '{engine}'."
                f" Supported: {', '.join(SUPPORTED_ENGINES)}"
            ),
        }

    # Check graphviz availability
    env_status = setup_helper.check_environment()
    if not env_status["graphviz"]["installed"]:
        hint = env_status["graphviz"].get(
            "install_hint", "Install Graphviz from https://graphviz.org/download/"
        )
        return {
            "success": False,
            "error": f"Graphviz not installed. {hint}",
        }

    if engine not in env_status["graphviz"]["engines"]:
        available = ", ".join(env_status["graphviz"]["engines"])
        return {
            "success": False,
            "error": (
                f"Engine '{engine}' not found on PATH."
                f" Available: {available}"
            ),
        }

    # Write DOT to temp file, render, clean up
    tmp_dot = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dot", delete=False
        ) as f:
            f.write(dot_content)
            tmp_dot = f.name

        # Generate output path if not provided
        if output_path is None:
            output_path = tempfile.mktemp(suffix=f".{output_format}")

        result = subprocess.run(
            [engine, f"-T{output_format}", tmp_dot, "-o", output_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or "Unknown render error"
            return {"success": False, "error": f"Render failed: {error_msg}"}

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {"success": False, "error": "Render produced empty output"}

        return {
            "success": True,
            "output_path": output_path,
            "format": output_format,
            "engine": engine,
            "size_bytes": os.path.getsize(output_path),
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Render timed out (>30s)"}
    except OSError as e:
        return {"success": False, "error": f"Failed to run graphviz: {e}"}
    finally:
        if tmp_dot and os.path.exists(tmp_dot):
            os.unlink(tmp_dot)
```

### Step 4: Run tests to verify they pass

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_render.py -v --tb=short
```

Expected: **10 passed** (or some skipped if graphviz absent in CI)

### Step 5: Run full test suite

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: All tests pass.

### Step 6: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/render.py modules/tool-dot-graph/tests/test_render.py && git commit -m "feat: add graphviz CLI rendering wrapper (SVG/PNG/PDF, engine selection)"
```

---

## Task 4: Wire Up the Real Tool (`__init__.py` Rewrite)

**Files:**
- Modify: `modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py`
- Create: `modules/tool-dot-graph/tests/test_tool_integration.py`
- Rename: `modules/tool-dot-graph/tests/test_mount_stub.py` → `test_mount.py`

**Depends on:** Tasks 1, 2, 3 (imports all three modules)

### Step 1: Write the failing integration tests

Create `modules/tool-dot-graph/tests/test_tool_integration.py`:

```python
"""Integration tests for DotGraphTool operation routing.

Verifies that the tool correctly routes each operation to the right module
and returns structured JSON in ToolResult.output.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Operation routing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_operation_routes_correctly():
    """operation='validate' routes to validate module and returns structured result."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({
        "operation": "validate",
        "dot_content": "digraph G { a -> b; }",
    })
    assert result.success is True
    data = json.loads(result.output)
    assert "valid" in data
    assert "issues" in data
    assert "stats" in data
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_validate_invalid_dot_returns_failure():
    """operation='validate' with bad DOT returns success=False."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({
        "operation": "validate",
        "dot_content": "not valid dot",
    })
    assert result.success is False
    data = json.loads(result.output)
    assert data["valid"] is False


@pytest.mark.asyncio
async def test_validate_with_layer_option():
    """operation='validate' accepts layers option."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({
        "operation": "validate",
        "dot_content": "digraph G { a -> b; }",
        "options": {"layers": ["syntax"]},
    })
    data = json.loads(result.output)
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_setup_operation_returns_environment():
    """operation='setup' returns environment status."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "setup"})
    assert result.success is True
    data = json.loads(result.output)
    assert "graphviz" in data
    assert "pydot" in data
    assert "networkx" in data


@pytest.mark.asyncio
async def test_analyze_operation_returns_phase3_pending():
    """operation='analyze' returns Phase 3 pending message."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({
        "operation": "analyze",
        "dot_content": "digraph G { a -> b; }",
    })
    assert result.success is False
    data = json.loads(result.output)
    assert "Phase 3" in data.get("error", "")


@pytest.mark.asyncio
async def test_unknown_operation_returns_error():
    """Unknown operation returns structured error."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "nonexistent"})
    assert result.success is False
    data = json.loads(result.output)
    assert "error" in data
    assert "nonexistent" in data["error"]


# ---------------------------------------------------------------------------
# Input schema
# ---------------------------------------------------------------------------


def test_input_schema_includes_setup_operation():
    """input_schema enum includes all four operations."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    ops = tool.input_schema["properties"]["operation"]["enum"]
    assert "validate" in ops
    assert "render" in ops
    assert "analyze" in ops
    assert "setup" in ops


def test_input_schema_documents_options():
    """input_schema options property has sub-properties for format, engine, layers."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    options = tool.input_schema["properties"]["options"]
    assert "properties" in options
    assert "format" in options["properties"]
    assert "engine" in options["properties"]
    assert "layers" in options["properties"]


# ---------------------------------------------------------------------------
# mount() contract (must still work)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mount_registers_real_tool():
    """mount() registers the real (non-placeholder) tool."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    metadata = await mount(coordinator)

    assert coordinator.mount.called
    args, kwargs = coordinator.mount.call_args
    assert args[0] == "tools"
    assert kwargs["name"] == "dot_graph"
    assert metadata["name"] == "tool-dot-graph"
    assert metadata["provides"] == ["dot_graph"]


@pytest.mark.asyncio
async def test_mounted_tool_can_validate():
    """The tool registered by mount() can execute validate operations."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]

    result = await tool.execute({
        "operation": "validate",
        "dot_content": "digraph G { a -> b; }",
    })
    data = json.loads(result.output)
    assert data["valid"] is True
```

### Step 2: Run new integration tests to verify they fail

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/test_tool_integration.py -v --tb=short
```

Expected: **FAIL** — The current placeholder `execute()` doesn't return JSON or route to modules.

### Step 3: Rename the old test file

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git mv modules/tool-dot-graph/tests/test_mount_stub.py modules/tool-dot-graph/tests/test_mount.py
```

### Step 4: Replace `__init__.py` with the real implementation

Replace the **entire contents** of `modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py` with:

```python
"""DOT graph tool module for Amplifier.

Provides tools for validating, rendering, and analyzing DOT-format graphs
using pydot and graphviz CLI.

Phase 2: Real tool routing to validate, render, and setup modules.
"""

import json
import logging
from typing import Any

from amplifier_core import ToolResult

from . import render
from . import setup_helper
from . import validate

logger = logging.getLogger(__name__)


class DotGraphTool:
    """DOT graph operations tool.

    Routes to validate, render, setup, or analyze based on 'operation' parameter.
    """

    @property
    def name(self) -> str:
        return "dot_graph"

    @property
    def description(self) -> str:
        return (
            "DOT graph tool \u2014 validate, render, and analyze DOT-format graphs.\n"
            "\n"
            "Operations:\n"
            "- validate: Three-layer DOT validation (syntax via pydot, structural"
            " analysis, render quality via graphviz)\n"
            "- render: Render DOT to SVG/PNG/PDF via graphviz CLI\n"
            "- setup: Check environment (graphviz, pydot, networkx availability)\n"
            "- analyze: Graph intelligence via networkx (Phase 3 \u2014 not yet"
            " implemented)"
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["validate", "render", "analyze", "setup"],
                    "description": "Operation to perform on the DOT graph",
                },
                "dot_content": {
                    "type": "string",
                    "description": "DOT graph content as a string",
                },
                "options": {
                    "type": "object",
                    "description": (
                        "Operation-specific options (format, layout engine, etc.)"
                    ),
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["svg", "png", "pdf", "json", "ps", "eps"],
                            "description": (
                                "Output format for render operation (default: svg)"
                            ),
                        },
                        "engine": {
                            "type": "string",
                            "enum": [
                                "dot", "neato", "fdp", "sfdp", "twopi", "circo",
                            ],
                            "description": (
                                "Layout engine for render operation (default: dot)"
                            ),
                        },
                        "output_path": {
                            "type": "string",
                            "description": (
                                "Output file path for render operation"
                                " (auto-generated if omitted)"
                            ),
                        },
                        "layers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["syntax", "structural", "render"],
                            },
                            "description": (
                                "Which validation layers to run (default: all)"
                            ),
                        },
                    },
                },
            },
            "required": ["operation"],
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute a DOT graph operation.

        Args:
            input_data: Must contain 'operation'. May contain 'dot_content'
                        and 'options' depending on the operation.

        Returns:
            ToolResult with structured JSON in the output field.
        """
        operation = input_data.get("operation", "unknown")
        dot_content = input_data.get("dot_content", "")
        options = input_data.get("options") or {}

        if operation == "validate":
            result = validate.validate_dot(
                dot_content=dot_content,
                layers=options.get("layers"),
            )
            return ToolResult(
                success=result["valid"],
                output=json.dumps(result),
            )

        elif operation == "render":
            result = render.render_dot(
                dot_content=dot_content,
                output_format=options.get("format", "svg"),
                engine=options.get("engine", "dot"),
                output_path=options.get("output_path"),
            )
            return ToolResult(
                success=result["success"],
                output=json.dumps(result),
            )

        elif operation == "setup":
            result = setup_helper.check_environment()
            return ToolResult(success=True, output=json.dumps(result))

        elif operation == "analyze":
            return ToolResult(
                success=False,
                output=json.dumps({
                    "error": (
                        "analyze operation is not yet implemented"
                        " (Phase 3 pending)"
                    ),
                    "hint": (
                        "Use the dot-graph-intelligence skill for guidance"
                        " on manual analysis"
                    ),
                }),
            )

        else:
            return ToolResult(
                success=False,
                output=json.dumps({
                    "error": f"Unknown operation '{operation}'",
                    "supported": ["validate", "render", "setup", "analyze"],
                }),
            )


async def mount(
    coordinator: Any, config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Mount the dot_graph tool into the coordinator.

    Registers the DotGraphTool which routes operations to validate,
    render, and setup modules.

    Args:
        coordinator: The Amplifier coordinator instance.
        config: Optional module configuration.

    Returns:
        Module metadata dict.
    """
    tool = DotGraphTool()

    await coordinator.mount("tools", tool, name=tool.name)

    logger.info("tool-dot-graph mounted: registered 'dot_graph' tool")

    return {
        "name": "tool-dot-graph",
        "version": "0.2.0",
        "provides": ["dot_graph"],
    }
```

### Step 5: Run ALL module tests to verify everything passes

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short
```

Expected: **All tests pass.** This includes:
- `test_mount.py` — 15 existing mount/protocol tests (the renamed file)
- `test_setup_helper.py` — 7 environment detection tests
- `test_validate.py` — 20 validation tests
- `test_render.py` — 10 render tests
- `test_tool_integration.py` — 11 integration/routing tests

Total: **~63 tests passing** (some render tests may be skipped if graphviz absent)

### Step 6: Run the root bundle tests to check nothing broke

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ -v --tb=short
```

Expected: All existing bundle tests still pass.

### Step 7: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py modules/tool-dot-graph/tests/test_tool_integration.py modules/tool-dot-graph/tests/test_mount.py && git add -u && git commit -m "feat: replace placeholder DotGraphTool with real validate/render/setup routing"
```

---

## Post-Implementation Verification

After all 4 tasks are complete, run these final checks:

### Full test suite

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest modules/tool-dot-graph/tests/ -v --tb=short && python -m pytest tests/ -v --tb=short
```

### Smoke test the tool end-to-end

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -c "
import asyncio, json
from unittest.mock import AsyncMock, MagicMock
from amplifier_module_tool_dot_graph import mount

async def smoke():
    coord = MagicMock()
    coord.mount = AsyncMock()
    await mount(coord)
    tool = coord.mount.call_args[0][1]

    # Validate
    r = await tool.execute({'operation': 'validate', 'dot_content': 'digraph G { a -> b; }'})
    print('Validate:', json.loads(r.output)['valid'])

    # Setup
    r = await tool.execute({'operation': 'setup'})
    env = json.loads(r.output)
    print('Graphviz:', env['graphviz']['installed'])
    print('pydot:', env['pydot']['version'])

    # Render
    r = await tool.execute({'operation': 'render', 'dot_content': 'digraph G { a -> b; }', 'options': {'format': 'svg'}})
    print('Render:', json.loads(r.output)['success'])

    # Analyze (Phase 3 pending)
    r = await tool.execute({'operation': 'analyze', 'dot_content': 'digraph G { a -> b; }'})
    print('Analyze:', json.loads(r.output)['error'])

asyncio.run(smoke())
"
```

Expected output:
```
Validate: True
Graphviz: True
pydot: 4.0.1
Render: True
Analyze: analyze operation is not yet implemented (Phase 3 pending)
```

### Push

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git push
```
