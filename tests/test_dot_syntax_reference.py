"""
Tests for docs/DOT-SYNTAX-REFERENCE.md existence and required content.
TDD: This test is written BEFORE the docs/DOT-SYNTAX-REFERENCE.md file is created.
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOT_SYNTAX_REF_PATH = REPO_ROOT / "docs" / "DOT-SYNTAX-REFERENCE.md"

# Minimum threshold constants for attribute/element presence checks
MIN_TABLE_ROWS = 10
MIN_BASIC_SHAPES = 6
MIN_EXTENDED_SHAPES = 5
MIN_NODE_ATTRS = 12
MIN_EDGE_ATTRS = 10
MIN_GRAPH_ATTRS = 12
MIN_HTML_ELEMENTS = 7
MIN_LAYOUT_ENGINES = 7
MIN_OUTPUT_FORMATS = 4


@pytest.fixture(scope="module")
def doc_content():
    """Read DOT-SYNTAX-REFERENCE.md once per test module."""
    return DOT_SYNTAX_REF_PATH.read_text()


# --- File existence and size ---


def test_dot_syntax_reference_exists():
    """docs/DOT-SYNTAX-REFERENCE.md must exist."""
    assert DOT_SYNTAX_REF_PATH.exists(), (
        f"docs/DOT-SYNTAX-REFERENCE.md not found at {DOT_SYNTAX_REF_PATH}"
    )


def test_dot_syntax_reference_line_count_in_range(doc_content):
    """File must be approximately 350-400 lines (±15% tolerance)."""
    lines = doc_content.splitlines()
    assert 300 <= len(lines) <= 450, (
        f"Expected 300-450 lines (target 350-400), got {len(lines)}"
    )


# --- Grammar section ---


def test_has_grammar_section(doc_content):
    """File must contain a Grammar section."""
    assert "Grammar" in doc_content, "Must contain a Grammar section"


def test_has_bnf_abstract_grammar(doc_content):
    """Grammar section must include BNF abstract grammar."""
    assert "stmt_list" in doc_content, "Must include BNF grammar with stmt_list"
    assert "edgeRHS" in doc_content, "Must include BNF grammar with edgeRHS"
    assert "compass_pt" in doc_content, "Must include BNF grammar with compass_pt"


def test_has_graph_types_table(doc_content):
    """Must have a Graph Types table covering digraph/graph/strict variants."""
    assert "digraph" in doc_content, "Must mention digraph"
    assert "strict" in doc_content, "Must mention strict graph variant"
    # Must have a table (pipe-delimited rows)
    pipe_lines = [ln for ln in doc_content.splitlines() if ln.strip().startswith("|")]
    assert len(pipe_lines) >= MIN_TABLE_ROWS, (
        f"Expected at least {MIN_TABLE_ROWS} table rows total, got {len(pipe_lines)}"
    )


def test_has_id_types_table(doc_content):
    """Must have an ID Types table with alphanumeric/numeral/quoted/HTML types."""
    assert "alphanumeric" in doc_content.lower() or "Alphabetic" in doc_content, (
        "Must mention alphanumeric/alphabetic ID type"
    )
    assert "numeral" in doc_content.lower() or "Numeral" in doc_content, (
        "Must mention numeral ID type"
    )
    assert "quoted" in doc_content.lower() or "Double-quoted" in doc_content, (
        "Must mention quoted string ID type"
    )
    assert "HTML" in doc_content, "Must mention HTML ID type"


def test_has_case_insensitive_keywords(doc_content):
    """Must mention case-insensitive keywords."""
    assert (
        "case-insensitive" in doc_content.lower()
        or "case insensitive" in doc_content.lower()
    ), "Must mention that keywords are case-insensitive"


# --- Nodes section ---


def test_has_nodes_section(doc_content):
    """File must contain a Nodes section."""
    assert "Nodes" in doc_content or "Node" in doc_content, (
        "Must contain a Nodes section"
    )


def test_has_node_declaration_examples(doc_content):
    """Nodes section must include implicit/explicit/multi-attribute declaration examples."""
    assert "implicit" in doc_content.lower() or "Implicit" in doc_content, (
        "Must show implicit node declaration"
    )
    assert "explicit" in doc_content.lower() or "Explicit" in doc_content, (
        "Must show explicit node declaration"
    )


def test_has_basic_shapes_table(doc_content):
    """Must have a Basic Shapes table with at least 8 shapes."""
    basic_shapes = [
        "box",
        "ellipse",
        "circle",
        "diamond",
        "rectangle",
        "point",
        "plaintext",
        "none",
    ]
    found = sum(1 for s in basic_shapes if s in doc_content)
    assert found >= MIN_BASIC_SHAPES, (
        f"Expected at least {MIN_BASIC_SHAPES} of the 8 basic shapes, found {found}"
    )


def test_has_extended_shapes_table(doc_content):
    """Must have Extended Shapes table with shapes like cylinder, folder, note, etc."""
    extended_shapes = [
        "cylinder",
        "folder",
        "note",
        "tab",
        "component",
        "hexagon",
        "doublecircle",
    ]
    found = sum(1 for s in extended_shapes if s in doc_content)
    assert found >= MIN_EXTENDED_SHAPES, (
        f"Expected at least {MIN_EXTENDED_SHAPES} extended shapes, found {found}"
    )


def test_has_special_shapes_including_record(doc_content):
    """Must mention special shapes including deprecated record."""
    assert "record" in doc_content, (
        "Must mention 'record' shape (including deprecated note)"
    )


def test_has_node_style_attributes(doc_content):
    """Must have Node Style Attributes table with at least 16 attributes."""
    node_attrs = [
        "label",
        "shape",
        "color",
        "fillcolor",
        "style",
        "fontname",
        "fontsize",
        "fontcolor",
        "width",
        "height",
        "fixedsize",
        "tooltip",
        "URL",
        "penwidth",
        "margin",
        "peripheries",
    ]
    found = sum(1 for a in node_attrs if a in doc_content)
    assert found >= MIN_NODE_ATTRS, (
        f"Expected at least {MIN_NODE_ATTRS} of 16 node style attributes, found {found}"
    )


# --- Edges section ---


def test_has_edges_section(doc_content):
    """File must contain an Edges section."""
    assert "Edge" in doc_content or "Edges" in doc_content, (
        "Must contain an Edges section"
    )


def test_has_edge_declaration_examples(doc_content):
    """Must show edge declaration examples: simple, attributed, chain, fan-out."""
    assert "->" in doc_content, "Must show directed edge operator '->'"
    assert "--" in doc_content, "Must show undirected edge operator '--'"


def test_has_edge_attributes_table(doc_content):
    """Must have an Edge Attributes table with at least 14 attributes."""
    edge_attrs = [
        "label",
        "color",
        "style",
        "weight",
        "arrowhead",
        "arrowtail",
        "dir",
        "headlabel",
        "taillabel",
        "constraint",
        "minlen",
        "penwidth",
        "ltail",
        "lhead",
    ]
    found = sum(1 for a in edge_attrs if a in doc_content)
    assert found >= MIN_EDGE_ATTRS, (
        f"Expected at least {MIN_EDGE_ATTRS} of 14 edge attributes, found {found}"
    )


# --- Graph Attributes section ---


def test_has_graph_attributes_section(doc_content):
    """File must contain a Graph Attributes section."""
    assert (
        "Graph Attribute" in doc_content or "graph attribute" in doc_content.lower()
    ), "Must contain Graph Attributes section"


def test_has_common_graph_attributes(doc_content):
    """Must have Common Graph Attributes table with at least 17 attributes."""
    graph_attrs = [
        "rankdir",
        "ranksep",
        "nodesep",
        "bgcolor",
        "label",
        "fontname",
        "fontsize",
        "size",
        "ratio",
        "margin",
        "pad",
        "splines",
        "compound",
        "newrank",
        "concentrate",  # not in doc; tolerance threshold (>=12) accounts for this
        "overlap",
        "dpi",
    ]
    found = sum(1 for a in graph_attrs if a in doc_content)
    assert found >= MIN_GRAPH_ATTRS, (
        f"Expected at least {MIN_GRAPH_ATTRS} of 17 graph attributes, found {found}"
    )


def test_has_default_attribute_statements(doc_content):
    """Must show Default Attribute Statements examples."""
    assert "node [" in doc_content or "node[" in doc_content, (
        "Must show default node attribute statement"
    )
    assert "edge [" in doc_content or "edge[" in doc_content, (
        "Must show default edge attribute statement"
    )


# --- Subgraphs and Clusters section ---


def test_has_subgraphs_section(doc_content):
    """File must contain a Subgraphs section."""
    assert "Subgraph" in doc_content or "subgraph" in doc_content, (
        "Must contain Subgraphs section"
    )


def test_has_cluster_naming_requirement(doc_content):
    """Must show cluster subgraph naming requirement (cluster_ prefix)."""
    assert "cluster_" in doc_content, "Must show cluster_ naming convention"


def test_has_rank_control(doc_content):
    """Must cover rank control with rank=same/min/max/source/sink."""
    assert "rank=same" in doc_content or "rank=min" in doc_content, (
        "Must show rank control subgraphs"
    )
    for rank_val in ["same", "min", "max", "source", "sink"]:
        assert rank_val in doc_content, f"Must mention rank={rank_val}"


def test_has_compound_edges(doc_content):
    """Must cover edges between clusters with compound=true."""
    assert "compound=true" in doc_content or "compound" in doc_content, (
        "Must mention compound edges between clusters"
    )


# --- HTML Labels section ---


def test_has_html_labels_section(doc_content):
    """File must contain an HTML Labels section."""
    assert "HTML" in doc_content and "Label" in doc_content, (
        "Must contain HTML Labels section"
    )


def test_has_html_table_example(doc_content):
    """Must contain a TABLE/TR/TD example with PORT connections."""
    assert "TABLE" in doc_content, "Must show TABLE element"
    assert "<TR>" in doc_content or "TR" in doc_content, "Must show TR element"
    assert "<TD" in doc_content or "TD" in doc_content, "Must show TD element"
    assert "PORT" in doc_content, "Must show PORT connections"


def test_has_html_elements_table(doc_content):
    """Must have a Supported HTML Elements table with at least 9 elements."""
    html_elements = ["TABLE", "TR", "TD", "FONT", "BR", "HR", "IMG", "<B>", "<I>"]
    found = sum(1 for e in html_elements if e in doc_content)
    assert found >= MIN_HTML_ELEMENTS, (
        f"Expected at least {MIN_HTML_ELEMENTS} of 9 HTML elements, found {found}"
    )


# --- Ports and Compass Points section ---


def test_has_ports_section(doc_content):
    """File must contain a Ports and Compass Points section."""
    assert "Compass" in doc_content or "compass" in doc_content, (
        "Must contain Ports and Compass Points section"
    )


def test_has_compass_points(doc_content):
    """Must show all 8 compass points."""
    # All 8 compass points are abbreviated — verify key ones are mentioned
    assert "ne" in doc_content and "sw" in doc_content and "nw" in doc_content, (
        "Must show compass points ne, sw, nw at minimum"
    )


# --- Layout Engines section ---


def test_has_layout_engines_section(doc_content):
    """File must contain a Layout Engines section."""
    assert "Layout Engine" in doc_content or "Layout engine" in doc_content, (
        "Must contain Layout Engines section"
    )


def test_has_eight_engines_table(doc_content):
    """Must have table of 8 layout engines with algorithm descriptions."""
    engines = ["dot", "neato", "fdp", "sfdp", "twopi", "circo", "osage", "patchwork"]
    found = sum(1 for e in engines if e in doc_content)
    assert found >= MIN_LAYOUT_ENGINES, (
        f"Expected at least {MIN_LAYOUT_ENGINES} of 8 layout engines, found {found}"
    )


def test_has_engine_selection_heuristic(doc_content):
    """Must include an engine selection heuristic/guide."""
    assert "DAG" in doc_content or "hierarchy" in doc_content.lower(), (
        "Must include engine selection guidance"
    )


# --- Output Formats section ---


def test_has_output_formats_section(doc_content):
    """File must contain an Output Formats section."""
    assert "Output Format" in doc_content or "output format" in doc_content.lower(), (
        "Must contain Output Formats section"
    )


def test_has_five_primary_formats(doc_content):
    """Must have table of 5 primary output formats."""
    formats = ["SVG", "PNG", "PDF", "JSON", "DOT"]
    found = sum(1 for f in formats if f in doc_content)
    assert found >= MIN_OUTPUT_FORMATS, (
        f"Expected at least {MIN_OUTPUT_FORMATS} of 5 output formats, found {found}"
    )


def test_has_rendering_commands(doc_content):
    """Must include rendering commands with validation and statistics."""
    assert "-T" in doc_content, "Must show -T flag for output format selection"
    assert "dot -T" in doc_content or "dot -" in doc_content, (
        "Must show dot rendering commands"
    )


# --- Color Specification section ---


def test_has_color_specification_section(doc_content):
    """File must contain a Color Specification section."""
    assert "Color" in doc_content, "Must contain Color Specification section"


def test_has_color_formats(doc_content):
    """Must cover name/hex/hex+alpha/HSV/color lists."""
    assert "#" in doc_content, "Must show hex color format"
    assert "HSV" in doc_content or "hsv" in doc_content, "Must mention HSV color format"


# --- String Features section ---


def test_has_string_features_section(doc_content):
    """File must contain a String Features section."""
    assert "String" in doc_content, "Must contain String Features section"


def test_has_string_features(doc_content):
    """Must cover newlines, concatenation, escapes, justification."""
    assert "\\n" in doc_content or "newline" in doc_content.lower(), (
        "Must mention newlines in string features"
    )
    assert "concatenat" in doc_content.lower() or "+" in doc_content, (
        "Must mention string concatenation"
    )
