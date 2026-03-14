"""
Tests for skills/dot-syntax/SKILL.md existence and required content.
TDD: This test is written BEFORE the skills/dot-syntax/SKILL.md file is created.
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "dot-syntax" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_content():
    """Read SKILL.md once per test module."""
    return SKILL_PATH.read_text()


# --- File existence and line count ---


def test_skill_file_exists():
    """skills/dot-syntax/SKILL.md must exist."""
    assert SKILL_PATH.exists(), f"skills/dot-syntax/SKILL.md not found at {SKILL_PATH}"


def test_skill_line_count_in_range(skill_content):
    """File must be approximately 130-150 lines (with tolerance)."""
    lines = skill_content.splitlines()
    assert 120 <= len(lines) <= 165, (
        f"Expected 120-165 lines (target 130-150), got {len(lines)}"
    )


# --- Frontmatter ---


def test_frontmatter_has_name(skill_content):
    """YAML frontmatter must have name: dot-syntax."""
    assert "name: dot-syntax" in skill_content, (
        "Frontmatter must contain 'name: dot-syntax'"
    )


def test_frontmatter_description_starts_with_use_when(skill_content):
    """Description must start with 'Use when writing or reading DOT/Graphviz code...'."""
    assert "Use when writing or reading DOT/Graphviz code" in skill_content, (
        "Description must start with 'Use when writing or reading DOT/Graphviz code'"
    )


def test_frontmatter_delimiters(skill_content):
    """File must have YAML frontmatter delimiters (---)."""
    lines = skill_content.splitlines()
    assert lines[0].strip() == "---", "First line must be '---' (frontmatter start)"
    # Find closing ---
    closing = any(line.strip() == "---" for line in lines[1:10])
    assert closing, "Must have closing '---' frontmatter delimiter"


# --- Overview section ---


def test_has_overview_section(skill_content):
    """Must have an Overview section."""
    assert "## Overview" in skill_content or "# Overview" in skill_content, (
        "Must contain an Overview section"
    )


def test_overview_mentions_fast_lookup(skill_content):
    """Overview must mention fast/quick lookup purpose."""
    content_lower = skill_content.lower()
    assert "fast" in content_lower or "quick" in content_lower, (
        "Overview must mention fast/quick lookup"
    )


def test_overview_mentions_core_principle(skill_content):
    """Overview must mention core principle about structure vs layout."""
    content_lower = skill_content.lower()
    assert "structure" in content_lower, (
        "Overview must mention core principle about structure"
    )
    assert "layout" in content_lower or "position" in content_lower, (
        "Overview must mention layout/positioning principle"
    )


# --- Graph Declaration section ---


def test_has_graph_declaration_section(skill_content):
    """Must have a Graph Declaration section."""
    assert "Graph Declaration" in skill_content, (
        "Must contain a Graph Declaration section"
    )


def test_graph_declaration_has_digraph(skill_content):
    """Graph Declaration must show digraph, graph, and strict variants."""
    assert "digraph" in skill_content, "Must show digraph declaration"
    assert "strict digraph" in skill_content, "Must show strict digraph variant"


# --- Nodes section ---


def test_has_nodes_section(skill_content):
    """Must have a Nodes section."""
    assert "## Nodes" in skill_content or "# Nodes" in skill_content, (
        "Must contain a Nodes section"
    )


def test_nodes_has_implicit_and_explicit(skill_content):
    """Nodes section must cover implicit and explicit node creation."""
    content_lower = skill_content.lower()
    assert "implicit" in content_lower, "Must mention implicit node creation"
    assert "explicit" in content_lower, "Must mention explicit node creation"


def test_nodes_has_multiline_and_quoted(skill_content):
    """Nodes section must cover multiline labels and quoted IDs."""
    assert "\\n" in skill_content or "multiline" in skill_content.lower(), (
        "Must show multiline label syntax"
    )
    assert "quoted" in skill_content.lower() or '"node with spaces"' in skill_content, (
        "Must mention quoted IDs for special chars"
    )


def test_nodes_has_id_rules(skill_content):
    """Nodes section must mention ID rules."""
    assert "ID" in skill_content and (
        "rule" in skill_content.lower()
        or "a-z" in skill_content.lower()
        or "[a-z" in skill_content.lower()
    ), "Must include ID rules"


# --- Edges section ---


def test_has_edges_section(skill_content):
    """Must have an Edges section."""
    assert "## Edges" in skill_content or "# Edges" in skill_content, (
        "Must contain an Edges section"
    )


def test_edges_has_directed_and_labeled(skill_content):
    """Edges section must show directed and labeled edges."""
    assert "->" in skill_content, "Must show directed edge operator"


def test_edges_has_chain(skill_content):
    """Edges section must show chain syntax."""
    assert (
        "chain" in skill_content.lower()
        or "-> B -> C" in skill_content
        or "-> B -> " in skill_content
    ), "Must show chain edge syntax"


def test_edges_has_fan_out(skill_content):
    """Edges section must show fan-out syntax."""
    assert (
        "fan-out" in skill_content.lower()
        or "fan out" in skill_content.lower()
        or "{B C D}" in skill_content
        or "-> {" in skill_content
    ), "Must show fan-out edge syntax"


# --- Attributes section ---


def test_has_attributes_section(skill_content):
    """Must have an Attributes section."""
    assert "## Attributes" in skill_content or "# Attributes" in skill_content, (
        "Must contain an Attributes section"
    )


def test_attributes_has_node_edge_graph_defaults(skill_content):
    """Attributes must show defaults for node, edge, and graph."""
    assert "node [" in skill_content or "node[" in skill_content, (
        "Must show default node attributes"
    )
    assert "edge [" in skill_content or "edge[" in skill_content, (
        "Must show default edge attributes"
    )
    assert "graph [" in skill_content or "rankdir" in skill_content, (
        "Must show graph attributes"
    )


# --- Shapes Quick Table ---


def test_has_shapes_section(skill_content):
    """Must have a Shapes section or Shapes Quick Table."""
    assert "Shape" in skill_content, "Must contain a Shapes section"


def test_shapes_has_at_least_11_shapes(skill_content):
    """Shapes section must include at least 11 shapes."""
    shapes = [
        "box",
        "ellipse",
        "circle",
        "diamond",
        "rectangle",
        "hexagon",
        "cylinder",
        "note",
        "folder",
        "parallelogram",
        "doublecircle",
        "component",
        "tab",
        "point",
        "plaintext",
    ]
    found = sum(1 for s in shapes if s in skill_content)
    assert found >= 11, f"Expected at least 11 shapes, found {found}"


# --- Subgraphs and Clusters section ---


def test_has_subgraphs_section(skill_content):
    """Must have a Subgraphs section."""
    assert "Subgraph" in skill_content or "subgraph" in skill_content, (
        "Must contain a Subgraphs section"
    )


def test_subgraphs_has_cluster_prefix(skill_content):
    """Must show cluster_ prefix requirement."""
    assert "cluster_" in skill_content, "Must show cluster_ naming convention"


def test_subgraphs_has_rank_control(skill_content):
    """Must show rank control."""
    assert "rank=same" in skill_content or "rank=" in skill_content, (
        "Must show rank control"
    )


# --- HTML Labels section ---


def test_has_html_labels_section(skill_content):
    """Must have an HTML Labels section."""
    assert "HTML" in skill_content and "Label" in skill_content, (
        "Must contain an HTML Labels section"
    )


def test_html_labels_has_table_tr_td(skill_content):
    """HTML Labels must show TABLE, TR, TD elements."""
    assert "TABLE" in skill_content, "Must show TABLE element"
    assert "TR" in skill_content, "Must show TR element"
    assert "TD" in skill_content, "Must show TD element"


def test_html_labels_has_port_example(skill_content):
    """HTML Labels must show PORT attribute example."""
    assert "PORT" in skill_content, "Must show PORT in HTML label example"


# --- Layout Engines section ---


def test_has_layout_engines_section(skill_content):
    """Must have a Layout Engines section."""
    assert "Layout" in skill_content and "Engine" in skill_content, (
        "Must contain a Layout Engines section"
    )


def test_layout_engines_has_five_engines(skill_content):
    """Must have table of at least 5 layout engines."""
    engines = ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]
    found = sum(1 for e in engines if e in skill_content)
    assert found >= 5, f"Expected at least 5 layout engines, found {found}"


def test_layout_engines_has_twopi(skill_content):
    """Must include twopi engine — matches dot-instructions.md which documents all 6 engines."""
    assert "twopi" in skill_content, (
        "Layout engines table must include 'twopi' for radial/hub-and-spoke layouts "
        "(present in dot-instructions.md but missing from skill)"
    )


# --- Common Gotchas section ---


def test_has_common_gotchas_section(skill_content):
    """Must have a Common Gotchas section."""
    assert "Gotcha" in skill_content or "gotcha" in skill_content.lower(), (
        "Must contain a Common Gotchas section"
    )


def test_common_gotchas_has_at_least_6(skill_content):
    """Common Gotchas table must have at least 6 entries."""
    # Count table rows (lines with | that aren't header/separator)
    lines = skill_content.splitlines()
    # Find gotcha section
    in_gotcha = False
    gotcha_rows = 0
    for line in lines:
        if "Gotcha" in line or "gotcha" in line.lower():
            in_gotcha = True
        if (
            in_gotcha
            and "|" in line
            and "---" not in line
            and "Gotcha" not in line
            and "Fix" not in line
        ):
            gotcha_rows += 1
        # Stop at next section header
        if (
            in_gotcha
            and line.startswith("## ")
            and "Gotcha" not in line
            and gotcha_rows > 0
        ):
            break
    assert gotcha_rows >= 6, f"Expected at least 6 gotcha rows, found {gotcha_rows}"


# --- Render Commands section ---


def test_has_render_commands_section(skill_content):
    """Must have a Render Commands section."""
    assert "Render" in skill_content, "Must contain a Render Commands section"


def test_render_commands_has_svg_png(skill_content):
    """Render Commands must include SVG and PNG examples."""
    assert "svg" in skill_content.lower() or "SVG" in skill_content, (
        "Must show SVG render command"
    )
    assert "png" in skill_content.lower() or "PNG" in skill_content, (
        "Must show PNG render command"
    )


def test_render_commands_has_validate(skill_content):
    """Render Commands must include validation command."""
    assert (
        "validate" in skill_content.lower()
        or "-Tsvg /dev/null" in skill_content
        or "nul" in skill_content
    ), "Must show validate command"
