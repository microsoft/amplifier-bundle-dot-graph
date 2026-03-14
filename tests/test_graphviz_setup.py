"""
Tests for docs/GRAPHVIZ-SETUP.md existence and required content.
TDD: This test is written BEFORE the docs/GRAPHVIZ-SETUP.md file is created.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
DOC_PATH = REPO_ROOT / "docs" / "GRAPHVIZ-SETUP.md"


@pytest.fixture(scope="module")
def doc_content():
    """Read GRAPHVIZ-SETUP.md once per test module."""
    return DOC_PATH.read_text(encoding="utf-8")


# --- File existence and size ---


def test_file_exists():
    """docs/GRAPHVIZ-SETUP.md must exist."""
    assert DOC_PATH.exists(), f"docs/GRAPHVIZ-SETUP.md not found at {DOC_PATH}"


def test_line_count_in_range(doc_content):
    """File must be approximately 140-160 lines."""
    lines = doc_content.splitlines()
    assert 130 <= len(lines) <= 175, (
        f"Expected 130-175 lines (target 140-160), got {len(lines)}"
    )


# --- Optional note ---


def test_graphviz_is_optional(doc_content):
    """File must note that Graphviz is OPTIONAL."""
    assert "optional" in doc_content.lower(), "Must state that Graphviz is optional"


def test_works_without_graphviz(doc_content):
    """Must explain what works without Graphviz (DOT authoring, syntax validation, graph analysis)."""
    content_lower = doc_content.lower()
    assert "pydot" in content_lower, "Must mention pydot works without Graphviz"
    assert "networkx" in content_lower, "Must mention networkx works without Graphviz"
    assert "render" in content_lower, "Must mention rendering requires Graphviz"


# --- Quick Check section ---


def test_has_quick_check_section(doc_content):
    """Must contain a Quick Check section."""
    assert "Quick Check" in doc_content or "quick check" in doc_content.lower(), (
        "Must contain a Quick Check section"
    )


def test_quick_check_has_dot_version_command(doc_content):
    """Quick Check must show 'dot -V' command."""
    assert "dot -V" in doc_content, "Quick Check must show 'dot -V' command"


def test_quick_check_has_expected_output(doc_content):
    """Quick Check must show expected output format."""
    # The expected output typically includes "graphviz version"
    assert "graphviz version" in doc_content.lower(), (
        "Quick Check must show expected output from dot -V"
    )


# --- Installation by Platform section ---


def test_has_installation_section(doc_content):
    """Must contain an Installation section."""
    assert "Installation" in doc_content or "installation" in doc_content.lower(), (
        "Must contain an Installation section"
    )


def test_has_macos_brew_instructions(doc_content):
    """Must contain macOS/Homebrew installation instructions."""
    assert "brew" in doc_content.lower() or "homebrew" in doc_content.lower(), (
        "Must include macOS Homebrew installation"
    )
    assert "macos" in doc_content.lower() or "macOS" in doc_content, (
        "Must include macOS section"
    )


def test_has_ubuntu_debian_instructions(doc_content):
    """Must contain Ubuntu/Debian apt installation instructions."""
    assert "apt" in doc_content.lower(), "Must include Ubuntu/Debian apt installation"
    assert "ubuntu" in doc_content.lower() or "Ubuntu" in doc_content, (
        "Must include Ubuntu section"
    )
    assert "debian" in doc_content.lower() or "Debian" in doc_content, (
        "Must include Debian section"
    )


def test_has_fedora_rhel_instructions(doc_content):
    """Must contain Fedora/RHEL/CentOS dnf installation instructions."""
    assert "dnf" in doc_content.lower(), "Must include Fedora/RHEL dnf installation"
    assert "fedora" in doc_content.lower() or "Fedora" in doc_content, (
        "Must include Fedora section"
    )


def test_has_windows_instructions(doc_content):
    """Must contain Windows installation instructions."""
    assert "windows" in doc_content.lower() or "Windows" in doc_content, (
        "Must include Windows section"
    )
    # Should have choco or winget or download instructions
    has_windows_method = (
        "choco" in doc_content.lower()
        or "winget" in doc_content.lower()
        or "download" in doc_content.lower()
    )
    assert has_windows_method, (
        "Windows instructions must include choco, winget, or download method"
    )


def test_has_conda_instructions(doc_content):
    """Must contain Conda cross-platform installation instructions."""
    assert "conda" in doc_content.lower() or "Conda" in doc_content, (
        "Must include Conda cross-platform installation"
    )


def test_has_docker_instructions(doc_content):
    """Must contain Docker installation instructions."""
    assert "docker" in doc_content.lower() or "Docker" in doc_content, (
        "Must include Docker installation"
    )


def test_docker_has_alpine_example(doc_content):
    """Docker section must include Alpine Dockerfile example."""
    assert "alpine" in doc_content.lower() or "Alpine" in doc_content, (
        "Docker section must include Alpine example"
    )


def test_docker_has_ubuntu_example(doc_content):
    """Docker section must include Ubuntu Dockerfile example."""
    # Docker Ubuntu example
    assert "ubuntu" in doc_content.lower(), (
        "Docker section must include Ubuntu Dockerfile example"
    )


def test_has_six_platform_indicators(doc_content):
    """Must have installation instructions for at least 6 platform indicators (macOS/brew,
    Ubuntu/Debian/apt, Fedora/RHEL/dnf, Windows, Conda, Docker Alpine). Docker Ubuntu is
    verified separately by test_docker_has_ubuntu_example."""
    platform_indicators = [
        "brew",  # macOS
        "apt",  # Ubuntu/Debian
        "dnf",  # Fedora/RHEL
        "windows",  # Windows
        "conda",  # Conda
        "alpine",  # Docker Alpine
    ]
    found = sum(1 for p in platform_indicators if p in doc_content.lower())
    assert found >= 6, f"Expected all 6 platform indicators, found {found}"


# --- Python Dependencies section ---


def test_has_python_dependencies_section(doc_content):
    """Must contain a Python Dependencies section."""
    assert "Python" in doc_content and (
        "Dependencies" in doc_content or "dependencies" in doc_content.lower()
    ), "Must contain a Python Dependencies section"


def test_python_deps_has_pip_install(doc_content):
    """Python Dependencies must show pip install commands."""
    assert "pip install" in doc_content, (
        "Python Dependencies must show 'pip install' commands"
    )
    assert "pydot" in doc_content, "Must show pip install pydot"
    assert "networkx" in doc_content, "Must show pip install networkx"


def test_python_deps_has_verify_commands(doc_content):
    """Python Dependencies must show verification commands."""
    # Should have import statements for verification
    assert "import pydot" in doc_content or "import networkx" in doc_content, (
        "Must show Python import verification commands"
    )


def test_python_deps_has_table_mapping(doc_content):
    """Must have a table mapping packages to purpose and Graphviz requirement."""
    # Check for a table (pipe-delimited rows)
    pipe_lines = [ln for ln in doc_content.splitlines() if ln.strip().startswith("|")]
    assert len(pipe_lines) >= 3, (
        f"Must have a table with at least 3 rows, found {len(pipe_lines)} pipe-delimited rows"
    )


def test_python_deps_table_has_graphviz_column(doc_content):
    """Package table must indicate which packages require Graphviz."""
    # Should mention "required" in context of Graphviz for rendering
    content_lower = doc_content.lower()
    assert "required" in content_lower or "optional" in content_lower, (
        "Package table must indicate Graphviz requirement status"
    )


# --- Verification section ---


def test_has_verification_section(doc_content):
    """Must contain a Verification section."""
    assert "Verification" in doc_content or "verification" in doc_content.lower(), (
        "Must contain a Verification section"
    )


def test_verification_has_bash_script(doc_content):
    """Verification section must contain a bash script."""
    assert (
        "```bash" in doc_content
        or "#!/bin/bash" in doc_content
        or "bash" in doc_content.lower()
    ), "Verification section must include a bash script"


def test_verification_checks_graphviz_cli(doc_content):
    """Verification script must check Graphviz CLI."""
    assert (
        "dot -V" in doc_content
        or "command -v dot" in doc_content
        or "which dot" in doc_content
    ), "Verification script must check for dot command"


def test_verification_checks_layout_engines(doc_content):
    """Verification script must check layout engines."""
    # Check for multiple engines (neato, fdp, sfdp, etc.)
    engines = ["neato", "fdp", "sfdp", "circo", "twopi"]
    found = sum(1 for e in engines if e in doc_content)
    assert found >= 2, (
        f"Verification script must check layout engines, found {found} engine references"
    )


def test_verification_checks_python_packages(doc_content):
    """Verification script must check Python packages."""
    assert "pydot" in doc_content and "networkx" in doc_content, (
        "Verification script must check pydot and networkx"
    )


def test_verification_has_render_test(doc_content):
    """Verification script must include a render test scoped within the Verification section."""
    lines = doc_content.splitlines()
    # Find the Verification section header
    verif_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("## Verification"):
            verif_start = i
            break
    assert verif_start is not None, "No '## Verification' section found"
    # Only inspect content from that section onward
    verif_content = "\n".join(lines[verif_start:])
    assert (
        "digraph" in verif_content.lower() or "render test" in verif_content.lower()
    ), (
        "Verification section must include a render test (digraph or 'render test' marker)"
    )


# --- Troubleshooting section ---


def test_has_troubleshooting_section(doc_content):
    """Must contain a Troubleshooting section."""
    assert (
        "Troubleshooting" in doc_content or "troubleshooting" in doc_content.lower()
    ), "Must contain a Troubleshooting section"


def test_troubleshooting_has_dot_not_found(doc_content):
    """Troubleshooting must cover 'dot: command not found' issue."""
    assert "command not found" in doc_content or "not found" in doc_content.lower(), (
        "Troubleshooting must cover 'dot: command not found'"
    )


def test_troubleshooting_has_font_errors(doc_content):
    """Troubleshooting must cover font errors."""
    assert "font" in doc_content.lower(), "Troubleshooting must cover font errors"


def test_troubleshooting_has_pydot_invocation_exception(doc_content):
    """Troubleshooting must cover pydot InvocationException."""
    assert (
        "InvocationException" in doc_content or "invocation" in doc_content.lower()
    ), "Troubleshooting must cover pydot InvocationException"


def test_troubleshooting_has_svg_font_issue(doc_content):
    """Troubleshooting must cover SVG wrong font issue."""
    assert "svg" in doc_content.lower() and "font" in doc_content.lower(), (
        "Troubleshooting must cover SVG font issues"
    )


def test_troubleshooting_has_large_graph_performance(doc_content):
    """Troubleshooting must cover large graph rendering performance."""
    content_lower = doc_content.lower()
    assert "large" in content_lower and (
        "slow" in content_lower or "performance" in content_lower
    ), "Troubleshooting must cover large graph rendering performance"


def test_troubleshooting_has_five_items(doc_content):
    """Troubleshooting section must have at least 5 distinct issues."""
    # Count issue headers (### in troubleshooting context)
    lines = doc_content.splitlines()
    # Find troubleshooting section start
    trouble_start = None
    for i, line in enumerate(lines):
        if "troubleshooting" in line.lower():
            trouble_start = i
            break

    if trouble_start is None:
        pytest.fail("No troubleshooting section found")

    # Count subsection headers after troubleshooting
    subsections = [ln for ln in lines[trouble_start:] if ln.strip().startswith("###")]
    assert len(subsections) >= 5, (
        f"Troubleshooting must have at least 5 issues, found {len(subsections)}"
    )


def test_troubleshooting_items_have_diagnosis_and_fix(doc_content):
    """Troubleshooting items must provide diagnosis and fix guidance."""
    content_lower = doc_content.lower()
    assert (
        "diagnos" in content_lower
        or "cause" in content_lower
        or "check" in content_lower
    ), "Troubleshooting must include diagnosis guidance"
    assert (
        "fix" in content_lower
        or "solution" in content_lower
        or "install" in content_lower
    ), "Troubleshooting must include fix guidance"
