"""
Tests for the consolidated skills catalog (model_performance-cb58).

The bundle ships exactly TWO model-visible skills -- dot-authoring and
dot-analysis. The seven previously-standalone skills survive as L3 reference
files plus old-name redirect stubs marked ``disable-model-invocation: true``,
so ``load_skill(skill_name=<old name>)`` still resolves and cross-bundle
references to the old names do not break.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

HUBS = ("dot-authoring", "dot-analysis")

# old skill name -> (hub that absorbed it, its L3 reference file)
FOLDED = {
    "dot-syntax": ("dot-authoring", "syntax.md"),
    "dot-patterns": ("dot-authoring", "patterns.md"),
    "dot-quality": ("dot-authoring", "quality.md"),
    "dot-graph-intelligence": ("dot-analysis", "graph-intelligence.md"),
    "dot-as-analysis": ("dot-analysis", "reconciliation.md"),
    "parallax-investigation": ("dot-analysis", "parallax-investigation.md"),
    "architecture-overview-diagram": (
        "dot-analysis",
        "architecture-overview-diagram.md",
    ),
}


def _frontmatter(path: Path) -> dict:
    """Parse the YAML frontmatter of a SKILL.md file."""
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---"), f"{path} must start with YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, f"{path} has incomplete frontmatter"
    return yaml.safe_load(parts[1]) or {}


def _all_skill_frontmatter() -> dict[str, dict]:
    """Map skill name -> frontmatter for every SKILL.md under skills/."""
    out = {}
    for skill_file in sorted(SKILLS_DIR.rglob("SKILL.md")):
        fm = _frontmatter(skill_file)
        out[fm["name"]] = fm
    return out


# --- Catalog shape ---


def test_exactly_two_model_visible_skills():
    """Only dot-authoring and dot-analysis appear in the model-facing index."""
    visible = sorted(
        name
        for name, fm in _all_skill_frontmatter().items()
        if not fm.get("disable-model-invocation", False)
    )
    assert visible == sorted(HUBS), (
        f"Expected exactly {sorted(HUBS)} model-visible skills, got {visible}"
    )


@pytest.mark.parametrize("hub", HUBS)
def test_hub_skill_exists(hub):
    assert (SKILLS_DIR / hub / "SKILL.md").exists(), f"skills/{hub}/SKILL.md missing"


@pytest.mark.parametrize("old,expected", sorted(FOLDED.items()))
def test_hub_description_names_absorbed_topic(old, expected):
    """Each hub description names every L3 topic it absorbed."""
    hub, _ref = expected
    fm = _frontmatter(SKILLS_DIR / hub / "SKILL.md")
    assert old in fm["description"], (
        f"{hub} description must name absorbed topic '{old}'"
    )


# hooks-skills-visibility (amplifier-bundle-skills) truncates every rendered
# catalog line at DEFAULT_LINE_CHAR_CAP characters. A description longer than
# that renders with a trailing ellipsis, which silently drops the absorbed-topic
# names the test above just checked for.
VISIBILITY_LINE_CHAR_CAP = 180


@pytest.mark.parametrize("hub", HUBS)
def test_hub_description_renders_untruncated(hub):
    fm = _frontmatter(SKILLS_DIR / hub / "SKILL.md")
    description = " ".join(fm["description"].split())
    assert len(description) <= VISIBILITY_LINE_CHAR_CAP, (
        f"{hub} description is {len(description)} chars; the visibility hook "
        f"truncates at {VISIBILITY_LINE_CHAR_CAP}, so the absorbed-topic names "
        f"would not reach the model"
    )


# --- Nothing deleted: every original body survives as an L3 file ---


@pytest.mark.parametrize("old,expected", sorted(FOLDED.items()))
def test_original_body_survives_as_l3_reference(old, expected):
    hub, ref = expected
    path = SKILLS_DIR / hub / "reference" / ref
    assert path.exists(), f"L3 reference for '{old}' missing at {path}"
    assert len(path.read_text(encoding="utf-8")) >= 500, (
        f"L3 reference {path} is suspiciously small -- body may have been truncated"
    )


def test_reference_files_are_not_rediscovered_as_skills():
    """L3 files must not be named SKILL.md -- discovery walks recursively."""
    for hub in HUBS:
        for path in (SKILLS_DIR / hub / "reference").iterdir():
            assert path.name != "SKILL.md", (
                f"{path} would be re-discovered as a standalone skill"
            )


# --- Old names still resolve (the alias/stub decision) ---


@pytest.mark.parametrize("old", sorted(FOLDED))
def test_old_name_still_resolves_via_stub(old):
    """A redirect stub keeps load_skill(skill_name=<old name>) working."""
    stub = SKILLS_DIR / old / "SKILL.md"
    assert stub.exists(), f"redirect stub missing at {stub}"
    fm = _frontmatter(stub)
    assert fm["name"] == old, f"{stub} must declare name: {old}"
    assert fm.get("disable-model-invocation") is True, (
        f"{stub} must set disable-model-invocation: true to stay out of the "
        f"model-facing index"
    )


@pytest.mark.parametrize("old,expected", sorted(FOLDED.items()))
def test_stub_points_at_its_reference_file(old, expected):
    hub, ref = expected
    body = (SKILLS_DIR / old / "SKILL.md").read_text(encoding="utf-8")
    assert hub in body, f"{old} stub must name the {hub} skill"
    assert ref in body, f"{old} stub must name its reference file {ref}"


def test_architecture_overview_diagram_stays_user_invocable():
    """/architecture-overview-diagram must survive the fold."""
    fm = _frontmatter(SKILLS_DIR / "architecture-overview-diagram" / "SKILL.md")
    assert fm.get("user-invocable") is True, (
        "architecture-overview-diagram must keep user-invocable: true so the "
        "slash command still resolves"
    )
