"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 35 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files (total 35).
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent

# The 35 expected bundle files (21 original + 3 Phase A + 3 Phase D recipes + 8 Phase A v2)
EXPECTED_FILES = [
    ".gitignore",
    "bundle.md",
    "behaviors/dot-graph.yaml",
    "agents/dot-author.md",
    "agents/diagram-reviewer.md",
    "context/dot-awareness.md",
    "context/dot-instructions.md",
    "docs/DOT-SYNTAX-REFERENCE.md",
    "docs/DOT-PATTERNS.md",
    "docs/DOT-QUALITY-STANDARDS.md",
    "docs/GRAPHVIZ-SETUP.md",
    "docs/GRAPH-ANALYSIS-GUIDE.md",
    "modules/tool-dot-graph/pyproject.toml",
    "modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py",
    "scripts/dot-validate.sh",
    "scripts/dot-render.sh",
    "skills/dot-syntax/SKILL.md",
    "skills/dot-patterns/SKILL.md",
    "skills/dot-as-analysis/SKILL.md",
    "skills/dot-quality/SKILL.md",
    "skills/dot-graph-intelligence/SKILL.md",
    # Phase A: discovery architecture
    "behaviors/dot-core.yaml",
    "behaviors/dot-discovery.yaml",
    "context/discovery-awareness.md",
    # Phase D: discovery pipeline recipes
    "recipes/discovery-pipeline.yaml",
    "recipes/discovery-investigate-topic.yaml",
    "recipes/discovery-synthesize-module.yaml",
    # Phase A v2: new discovery agent and context files
    "agents/discovery-level-synthesizer.md",
    "agents/discovery-subsystem-synthesizer.md",
    "agents/discovery-overview-synthesizer.md",
    "agents/discovery-combiner.md",
    "context/discovery-level-synthesizer-instructions.md",
    "context/discovery-subsystem-synthesizer-instructions.md",
    "context/discovery-overview-synthesizer-instructions.md",
    "context/discovery-combiner-instructions.md",
]

SKILL_FILES = [
    "skills/dot-syntax/SKILL.md",
    "skills/dot-patterns/SKILL.md",
    "skills/dot-as-analysis/SKILL.md",
    "skills/dot-quality/SKILL.md",
    "skills/dot-graph-intelligence/SKILL.md",
]


# --- Step 1: Complete file tree (35 files) ---


@pytest.mark.parametrize("rel_path", EXPECTED_FILES)
def test_bundle_file_exists(rel_path):
    """Step 1: Each of the 35 expected bundle files exists."""
    path = REPO_ROOT / rel_path
    assert path.exists(), f"Bundle file missing: {rel_path}"
    assert path.is_file(), f"Expected file but found directory: {rel_path}"


def test_total_file_count():
    """Step 6: Total bundle file count is exactly 35 (27 prior + 8 Phase A v2)."""
    present = [f for f in EXPECTED_FILES if (REPO_ROOT / f).exists()]
    assert len(present) == 35, (
        f"Expected 35 bundle files, found {len(present)}. "
        f"Missing: {[f for f in EXPECTED_FILES if f not in present]}"
    )


# --- Step 2: Tool module imports ---


def test_tool_module_import():
    """Step 2: amplifier_module_tool_dot_graph can be imported and mount is callable."""
    module_path = str(REPO_ROOT / "modules" / "tool-dot-graph")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from amplifier_module_tool_dot_graph import mount; print('OK')",
        ],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PYTHONPATH": module_path,
        },
    )
    assert result.returncode == 0, f"Module import failed:\n{result.stderr}"
    assert result.stdout.strip() == "OK", f"Unexpected output: {result.stdout!r}"


# --- Step 3: Scripts are executable ---


def test_dot_validate_sh_is_executable():
    """Step 3a: scripts/dot-validate.sh is executable."""
    script = REPO_ROOT / "scripts" / "dot-validate.sh"
    assert script.is_file(), "dot-validate.sh not found"
    assert os.access(script, os.X_OK), "dot-validate.sh is not executable"


def test_dot_render_sh_is_executable():
    """Step 3b: scripts/dot-render.sh is executable."""
    script = REPO_ROOT / "scripts" / "dot-render.sh"
    assert script.is_file(), "dot-render.sh not found"
    assert os.access(script, os.X_OK), "dot-render.sh is not executable"


def test_scripts_respond_to_help():
    """Step 3c: Both scripts respond to --help without error."""
    for script_name in ["dot-validate.sh", "dot-render.sh"]:
        script = REPO_ROOT / "scripts" / script_name
        result = subprocess.run(
            [str(script), "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"{script_name} --help failed (rc={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --- Step 4: Behavior YAML is valid ---


def test_behavior_yaml_valid():
    """Step 4: behaviors/dot-graph.yaml is valid YAML."""
    yaml_path = REPO_ROOT / "behaviors" / "dot-graph.yaml"
    assert yaml_path.exists(), "behaviors/dot-graph.yaml not found"
    with yaml_path.open() as f:
        data = yaml.safe_load(f)
    assert data is not None, "behaviors/dot-graph.yaml parsed as empty/None"


# --- Step 5: Skill frontmatter has 'Use when...' descriptions ---


@pytest.mark.parametrize("skill_rel_path", SKILL_FILES)
def test_skill_has_use_when_description(skill_rel_path):
    """Step 5: Each skill's SKILL.md has a 'description: Use when...' frontmatter line."""
    skill_path = REPO_ROOT / skill_rel_path
    assert skill_path.exists(), f"Skill file not found: {skill_rel_path}"

    content = skill_path.read_text()
    lines = content.splitlines()

    # Find description line in first 10 lines (frontmatter area)
    desc_line = None
    for line in lines[:10]:
        if line.strip().startswith("description:"):
            desc_line = line.strip()
            break

    assert desc_line is not None, (
        f"{skill_rel_path}: No 'description:' found in first 10 lines"
    )
    assert "Use when" in desc_line, (
        f"{skill_rel_path}: description does not start with 'Use when...': {desc_line!r}"
    )
