"""
Tests for skills/parallax-investigation/SKILL.md existence and required content.
TDD: Tests written BEFORE the skill file is created.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "parallax-investigation" / "SKILL.md"


def test_parallax_investigation_skill_exists():
    """skills/parallax-investigation/SKILL.md must exist."""
    assert SKILL_PATH.exists(), f"SKILL.md not found at {SKILL_PATH}"


def test_parallax_investigation_skill_is_not_empty():
    """SKILL.md must be at least 500 characters."""
    content = SKILL_PATH.read_text()
    assert len(content) >= 500, (
        f"SKILL.md must be at least 500 characters, got {len(content)}"
    )


def test_parallax_investigation_skill_has_yaml_frontmatter():
    """SKILL.md must start with YAML frontmatter (---)."""
    content = SKILL_PATH.read_text()
    assert content.startswith("---"), (
        "SKILL.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "SKILL.md must have closing --- for frontmatter"
    )


def test_parallax_investigation_skill_documents_three_perspectives():
    """SKILL.md must document the three-perspective model: HOW, WHAT, WHERE, code-tracer, behavior-observer."""
    content = SKILL_PATH.read_text()
    assert "HOW" in content, "Must mention HOW perspective"
    assert "WHAT" in content, "Must mention WHAT perspective"
    assert "WHERE" in content, "Must mention WHERE perspective"
    assert "code-tracer" in content, "Must mention code-tracer agent"
    assert "behavior-observer" in content, "Must mention behavior-observer agent"


def test_parallax_investigation_skill_documents_no_fiat_rule():
    """SKILL.md must document the no-fiat rule (keywords: no-fiat, no fiat, reconcil, discrepanc)."""
    content = SKILL_PATH.read_text().lower()
    has_no_fiat = "no-fiat" in content or "no fiat" in content
    has_reconcil = "reconcil" in content
    has_discrepanc = "discrepanc" in content
    assert has_no_fiat or has_reconcil or has_discrepanc, (
        "Must document the no-fiat rule (keywords: no-fiat, no fiat, reconcil, discrepanc)"
    )


def test_parallax_investigation_skill_documents_wave_structure():
    """SKILL.md must document wave structure (keywords: wave, verification, adversarial)."""
    content = SKILL_PATH.read_text().lower()
    assert "wave" in content, "Must mention wave structure"
    assert "verification" in content, "Must mention verification wave"
    assert "adversarial" in content, "Must mention adversarial wave"


def test_parallax_investigation_skill_documents_fidelity_tiers():
    """SKILL.md must document fidelity tiers (keywords: quick, deep, fidelit)."""
    content = SKILL_PATH.read_text().lower()
    assert "quick" in content, "Must mention quick fidelity tier"
    assert "deep" in content, "Must mention deep fidelity tier"
    assert "fidelit" in content, "Must mention fidelity tiers"
