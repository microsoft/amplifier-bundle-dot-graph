"""
Shared test helpers for the dot-graph bundle test suite.
"""

import sys
import venv
from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="session")
def recipe_python(tmp_path_factory):
    """Explicit trusted install path; never import a target workspace's module."""
    env = tmp_path_factory.mktemp("recipe-python")
    venv.EnvBuilder(system_site_packages=True, symlinks=True).create(env)
    python = env / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    site = next(env.glob("lib/python*/site-packages"))
    module = Path(__file__).resolve().parents[1] / "modules/tool-dot-graph"
    (site / "trusted-dot-graph.pth").write_text(str(module) + "\n")
    return python


@pytest.fixture(autouse=True)
def select_recipe_python(monkeypatch, recipe_python):
    monkeypatch.setenv("AMPLIFIER_PYTHON", str(recipe_python))


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body
