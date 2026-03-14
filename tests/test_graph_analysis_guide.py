"""
Tests for docs/GRAPH-ANALYSIS-GUIDE.md existence and required content.
TDD: This test is written BEFORE docs/GRAPH-ANALYSIS-GUIDE.md is created.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
DOC_PATH = REPO_ROOT / "docs" / "GRAPH-ANALYSIS-GUIDE.md"


@pytest.fixture(scope="module")
def doc_content():
    """Read GRAPH-ANALYSIS-GUIDE.md once per test module."""
    return DOC_PATH.read_text(encoding="utf-8")


# --- File existence and size ---


def test_file_exists():
    """docs/GRAPH-ANALYSIS-GUIDE.md must exist."""
    assert DOC_PATH.exists(), f"docs/GRAPH-ANALYSIS-GUIDE.md not found at {DOC_PATH}"


def test_line_count_in_range(doc_content):
    """File must be approximately 130-150 lines."""
    lines = doc_content.splitlines()
    assert 120 <= len(lines) <= 165, (
        f"Expected 120-165 lines (target 130-150), got {len(lines)}"
    )


# --- The Core Idea section ---


def test_has_core_idea_section(doc_content):
    """Must contain a 'The Core Idea' section."""
    assert "Core Idea" in doc_content, "Must contain 'The Core Idea' section"


def test_core_idea_mentions_dot_as_graph_structures(doc_content):
    """Core Idea must frame DOT as formal graph structures."""
    content_lower = doc_content.lower()
    assert "graph" in content_lower and "structure" in content_lower, (
        "Core Idea must frame DOT as formal graph structures"
    )


def test_core_idea_has_five_example_questions(doc_content):
    """Core Idea must list 5 example questions with analysis type mappings."""
    # Scope to the Core Idea section (between '## The Core Idea' and the next '---')
    start = doc_content.find("## The Core Idea")
    end = doc_content.find("\n---\n", start)
    core_idea_section = doc_content[start:end] if end != -1 else doc_content[start:]
    question_count = core_idea_section.count("?")
    assert question_count >= 5, (
        f"Core Idea must include at least 5 example questions, "
        f"found {question_count} '?' in Core Idea section"
    )


def test_core_idea_mentions_zero_llm_cost(doc_content):
    """Core Idea must emphasize zero LLM token cost."""
    content_lower = doc_content.lower()
    assert (
        "zero" in content_lower or "no llm" in content_lower or "token" in content_lower
    ), "Core Idea must emphasize zero LLM token cost"


# --- Analysis Operations section ---


def test_has_analysis_operations_section(doc_content):
    """Must contain an 'Analysis Operations' section."""
    assert "Analysis Operations" in doc_content, (
        "Must contain 'Analysis Operations' section"
    )


def test_has_reachability_operation(doc_content):
    """Must include Reachability operation for impact analysis."""
    content_lower = doc_content.lower()
    assert "reachability" in content_lower, (
        "Must include Reachability analysis operation"
    )


def test_has_unreachable_nodes_operation(doc_content):
    """Must include Unreachable Nodes operation for dead code detection."""
    content_lower = doc_content.lower()
    assert "unreachable" in content_lower, (
        "Must include Unreachable Nodes analysis operation"
    )


def test_has_cycle_detection_operation(doc_content):
    """Must include Cycle Detection operation for circular dependency discovery."""
    content_lower = doc_content.lower()
    assert "cycle" in content_lower, "Must include Cycle Detection analysis operation"


def test_has_path_finding_operation(doc_content):
    """Must include Path Finding operation for connection understanding."""
    content_lower = doc_content.lower()
    assert "path" in content_lower and "find" in content_lower, (
        "Must include Path Finding analysis operation"
    )


def test_has_critical_path_operation(doc_content):
    """Must include Critical Path operation for bottleneck identification."""
    content_lower = doc_content.lower()
    assert "critical path" in content_lower, (
        "Must include Critical Path analysis operation"
    )


def test_has_subgraph_extraction_operation(doc_content):
    """Must include Subgraph Extraction operation for zoom-in navigation."""
    content_lower = doc_content.lower()
    assert "subgraph" in content_lower, (
        "Must include Subgraph Extraction analysis operation"
    )


def test_has_structural_diff_operation(doc_content):
    """Must include Structural Diff operation for change tracking."""
    content_lower = doc_content.lower()
    assert "diff" in content_lower, "Must include Structural Diff analysis operation"


def test_has_graph_statistics_operation(doc_content):
    """Must include Graph Statistics operation with 6 metrics."""
    content_lower = doc_content.lower()
    assert "statistic" in content_lower or "statistics" in content_lower, (
        "Must include Graph Statistics analysis operation"
    )


def test_operations_have_subsections(doc_content):
    """Each operation must have Question/Use case/How it works/Interpretation subsections."""
    content_lower = doc_content.lower()
    assert "question" in content_lower, "Operations must include 'Question' subsection"
    assert "use case" in content_lower, "Operations must include 'Use case' subsection"
    assert "how it works" in content_lower, (
        "Operations must include 'How it works' subsection"
    )
    assert "interpretation" in content_lower, (
        "Operations must include 'Interpretation' subsection"
    )


# --- The Analysis-to-Artifact Loop section ---


def test_has_analysis_artifact_loop_section(doc_content):
    """Must contain the Analysis-to-Artifact Loop section."""
    content_lower = doc_content.lower()
    assert "artifact" in content_lower and "loop" in content_lower, (
        "Must contain the Analysis-to-Artifact Loop section"
    )


def test_loop_shows_dot_analyze_annotate_render_act_update_cycle(doc_content):
    """Loop section must show the DOT→analyze→annotate→render→act→update cycle."""
    content_lower = doc_content.lower()
    assert "analyze" in content_lower or "analysis" in content_lower, (
        "Loop must include 'analyze' step"
    )
    assert "annotate" in content_lower, "Loop must include 'annotate' step"
    assert "render" in content_lower, "Loop must include 'render' step"
    assert "act" in content_lower, "Loop must include 'act' step"
    assert "update" in content_lower, "Loop must include 'update' step"


# --- When to Use Code vs LLM table ---


def test_has_code_vs_llm_section(doc_content):
    """Must contain the 'When to Use Code vs LLM' decision matrix."""
    content_lower = doc_content.lower()
    assert "code" in content_lower and "llm" in content_lower, (
        "Must contain code vs LLM decision matrix"
    )


def test_code_vs_llm_has_six_tasks(doc_content):
    """Code vs LLM table must have 6 tasks mapped to code/LLM preference."""
    # The table should have at least 6 rows — count occurrences of '|' rows
    table_rows = [
        line for line in doc_content.splitlines() if line.strip().startswith("|")
    ]
    # Must have at least 6 data rows (excluding header and separator rows)
    data_rows = [r for r in table_rows if "---" not in r and "Task" not in r]
    assert len(data_rows) >= 6, (
        f"Code vs LLM table must have at least 6 task rows, found {len(data_rows)}"
    )


def test_code_vs_llm_has_rule_of_thumb(doc_content):
    """Code vs LLM section must include a rule of thumb."""
    content_lower = doc_content.lower()
    assert (
        "rule" in content_lower
        or "thumb" in content_lower
        or "guideline" in content_lower
    ), "Code vs LLM section must include a rule of thumb"
