"""
Tests for context/discovery-prescan-instructions.md existence and required content.
Covers the Topic Selection Methodology for the prescan agent.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PRESCAN_INSTRUCTIONS_PATH = REPO_ROOT / "context" / "discovery-prescan-instructions.md"


def test_prescan_instructions_exists():
    """context/discovery-prescan-instructions.md must exist."""
    assert PRESCAN_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-prescan-instructions.md not found at {PRESCAN_INSTRUCTIONS_PATH}"
    )


def test_prescan_instructions_line_count():
    """File must be between 60 and 150 lines (spec: 60-150 lines)."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 60 <= len(lines) <= 150, f"Expected 60-150 lines, got {len(lines)}"


def test_prescan_instructions_has_heading():
    """File must contain a heading about prescan/topic selection."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in ["prescan", "Prescan", "Topic Selection", "topic selection"]
    ), "Must contain a heading about prescan or topic selection"


def test_prescan_instructions_has_topic_selection_criteria():
    """File must contain a topic selection criteria table with required signals."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    # Must mention the required signals from the spec
    required_signals = [
        "entry point",
        "config",
        "test",
    ]
    for signal in required_signals:
        assert signal.lower() in content.lower(), (
            f"Must contain topic selection signal: '{signal}'"
        )
    # Must also mention the 'What Is NOT a Good Topic' section
    assert any(
        phrase in content.lower()
        for phrase in ["not a good topic", "not good topic", "what is not", "avoid"]
    ), "Must contain 'What Is NOT a Good Topic' guidance"


def test_prescan_instructions_has_fidelity_guidance():
    """File must contain fidelity tier guidance table."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert "fidelity" in content.lower(), "Must mention fidelity tiers"
    # Must mention both standard and deep tiers
    assert "standard" in content.lower(), "Must mention standard fidelity tier"
    assert "deep" in content.lower(), "Must mention deep fidelity tier"


def test_prescan_instructions_has_json_output_format():
    """File must contain JSON output format with flat array schema fields."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert "json" in content.lower(), "Must contain JSON output format"
    # Must contain required schema fields (flat array format)
    required_fields = ["name", "slug", "description"]
    for field in required_fields:
        assert field in content, f"JSON schema must include field: '{field}'"


def test_prescan_instructions_documents_flat_array_format():
    """File must document flat JSON array format (not nested {topics: [...]} wrapper)."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    # Must NOT present the nested topics wrapper as the output format
    # (it should document a flat array)
    # Check that there's a JSON code block starting with '[' (flat array)
    json_blocks = re.findall(r"```json\s*(.*?)```", content, re.DOTALL)
    assert json_blocks, "Must contain at least one JSON code block"
    flat_array_blocks = [b for b in json_blocks if b.strip().startswith("[")]
    assert flat_array_blocks, (
        "JSON code block must show flat array format starting with '[', not nested object"
    )


def test_prescan_instructions_documents_slug_field():
    """File must document the 'slug' field as an explicit JSON field in the output schema."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    # slug must appear as a JSON field (in quotes) or explicitly named as a field
    # "slug" as a word in descriptions is not enough — it must be documented as an output field
    assert '"slug"' in content or "**slug**" in content or "`slug`" in content, (
        "Must document 'slug' as an explicit field in the output format "
        "(e.g. in a JSON example block or field description)"
    )


def test_prescan_instructions_explains_slug_is_kebab_case():
    """File must explain that slug is kebab-case."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert "kebab" in content.lower() or "kebab-case" in content.lower(), (
        "Must explain that slug is kebab-case"
    )


def test_prescan_instructions_explains_slug_drives_directories():
    """File must explain that slug is used for directory path construction (output/modules/{slug}/)."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    # Must mention specific directory path pattern using slug
    assert any(
        phrase in content for phrase in ["output/modules/", "modules/{slug}", "{slug}"]
    ), (
        "Must explain that slug drives directory path construction, "
        "e.g. referencing 'output/modules/{slug}/' pattern"
    )


def test_prescan_instructions_mentions_structural_inventory():
    """File must reference 'structural inventory' as input."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert "structural inventory" in content.lower(), (
        "Must reference 'structural inventory' as input"
    )


def test_prescan_instructions_has_topic_count_range():
    """File must specify 3-7 topic range."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert any(phrase in content for phrase in ["3-7", "3–7", "3 to 7", "3 and 7"]), (
        "Must specify '3-7' or '3–7' topic range"
    )
