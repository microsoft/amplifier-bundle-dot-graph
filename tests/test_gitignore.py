"""
Tests for .gitignore file existence and required content.
TDD: This test is written BEFORE the .gitignore file is created.
"""

from pathlib import Path

# Root of the repository (two levels up from this test file)
REPO_ROOT = Path(__file__).parent.parent
GITIGNORE_PATH = REPO_ROOT / ".gitignore"


def test_gitignore_exists():
    """The .gitignore file must exist at the repo root."""
    assert GITIGNORE_PATH.exists(), f".gitignore not found at {GITIGNORE_PATH}"


def test_gitignore_has_private_settings_section():
    """Must include private settings section with .env and *.local patterns."""
    content = GITIGNORE_PATH.read_text()
    assert "# Private settings" in content
    assert ".env" in content
    assert "*.local" in content


def test_gitignore_has_os_files_section():
    """Must include OS files section (.DS_Store, Thumbs.db)."""
    content = GITIGNORE_PATH.read_text()
    assert "# OS files" in content
    assert ".DS_Store" in content
    assert "Thumbs.db" in content


def test_gitignore_has_dependencies_build_test_section():
    """Must include dependencies/build/test section."""
    content = GITIGNORE_PATH.read_text()
    assert "node_modules" in content
    assert ".venv" in content
    assert "__pycache__" in content
    assert "*.egg-info" in content
    assert "dist/" in content
    assert "build/" in content


def test_gitignore_has_logs_section():
    """Must include logs section."""
    content = GITIGNORE_PATH.read_text()
    assert "# Logs" in content
    assert "*.log" in content


def test_gitignore_has_azd_section():
    """Must include azd files section."""
    content = GITIGNORE_PATH.read_text()
    assert "#azd files" in content or "# azd files" in content
    assert ".azure" in content


def test_gitignore_has_databases_section():
    """Must include databases section."""
    content = GITIGNORE_PATH.read_text()
    assert "# Databases" in content
    assert "*.db" in content
    assert "*.sqlite" in content


def test_gitignore_has_amplifier_specific_section():
    """Must include Amplifier-specific ignores section."""
    content = GITIGNORE_PATH.read_text()
    assert "# Amplifier specific ignores" in content
    assert "ai_working/tmp" in content


def test_gitignore_has_dot_output_ignores():
    """Must include DOT rendered output ignores for svg, png, pdf."""
    content = GITIGNORE_PATH.read_text()
    assert "*.svg" in content
    assert "*.png" in content
    assert "*.pdf" in content


def test_gitignore_dot_output_exceptions_for_docs():
    """Must include exceptions allowing docs/**/*.svg and docs/**/*.png."""
    content = GITIGNORE_PATH.read_text()
    assert "!docs/**/*.svg" in content
    assert "!docs/**/*.png" in content


def test_gitignore_first_line_is_comment():
    """First line should be a comment (standard .gitignore header)."""
    lines = GITIGNORE_PATH.read_text().splitlines()
    assert len(lines) >= 5, "File must have at least 5 lines"
    # First line should be a comment indicating the private settings section
    assert lines[0].startswith("#"), f"First line should be a comment, got: {lines[0]}"
