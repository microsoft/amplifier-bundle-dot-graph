"""
Tests for bundle.md root file existence and required content.
TDD: This test is written BEFORE the bundle.md file is created.
"""

from pathlib import Path

import yaml

# Root of the repository (two levels up from this test file)
REPO_ROOT = Path(__file__).parent.parent
BUNDLE_MD_PATH = REPO_ROOT / "bundle.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


def test_bundle_md_exists():
    """bundle.md must exist at the repo root."""
    assert BUNDLE_MD_PATH.exists(), f"bundle.md not found at {BUNDLE_MD_PATH}"


def test_bundle_md_has_valid_yaml_frontmatter():
    """bundle.md must have valid YAML frontmatter delimited by ---."""
    content = BUNDLE_MD_PATH.read_text()
    assert content.startswith("---"), "bundle.md must start with YAML frontmatter (---)"
    assert content.count("---") >= 2, "bundle.md must have closing --- for frontmatter"
    frontmatter, _ = _parse_frontmatter(content)
    assert isinstance(frontmatter, dict), "YAML frontmatter must parse to a dict"


def test_bundle_md_frontmatter_has_bundle_name():
    """Frontmatter must contain bundle.name = 'dot-graph'."""
    content = BUNDLE_MD_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "bundle" in frontmatter, "Frontmatter must have 'bundle' key"
    assert frontmatter["bundle"]["name"] == "dot-graph", (
        f"bundle.name must be 'dot-graph', got: {frontmatter['bundle'].get('name')}"
    )


def test_bundle_md_frontmatter_has_version():
    """Frontmatter must contain bundle.version = '0.1.0'."""
    content = BUNDLE_MD_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert frontmatter["bundle"]["version"] == "0.1.0", (
        f"bundle.version must be '0.1.0', got: {frontmatter['bundle'].get('version')}"
    )


def test_bundle_md_frontmatter_has_description():
    """Frontmatter must contain the expected description."""
    expected = "General-purpose DOT/Graphviz infrastructure \u2014 knowledge, tools, and graph intelligence"
    content = BUNDLE_MD_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert frontmatter["bundle"]["description"] == expected, (
        f"bundle.description mismatch.\nExpected: {expected!r}\nGot: {frontmatter['bundle'].get('description')!r}"
    )


def test_bundle_md_frontmatter_has_includes():
    """Frontmatter must contain includes list referencing 'dot-graph:behaviors/dot-graph'."""
    content = BUNDLE_MD_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "includes" in frontmatter, "Frontmatter must have 'includes' key"
    includes = frontmatter["includes"]
    assert isinstance(includes, list), "'includes' must be a list"
    bundle_refs = [item.get("bundle") for item in includes if isinstance(item, dict)]
    assert "dot-graph:behaviors/dot-graph" in bundle_refs, (
        f"includes must contain 'dot-graph:behaviors/dot-graph', got: {bundle_refs}"
    )


def test_bundle_md_body_has_heading():
    """Markdown body must contain heading '# DOT/Graphviz Infrastructure'."""
    content = BUNDLE_MD_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# DOT/Graphviz Infrastructure" in body, (
        "Markdown body must contain '# DOT/Graphviz Infrastructure'"
    )


def test_bundle_md_body_has_dot_awareness_mention():
    """Markdown body must contain @mention for dot-graph:context/dot-awareness.md."""
    content = BUNDLE_MD_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "@dot-graph:context/dot-awareness.md" in body, (
        "Markdown body must contain '@dot-graph:context/dot-awareness.md'"
    )
