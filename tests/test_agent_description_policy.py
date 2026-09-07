"""Repo-wide guard: every agent description stays out of the always-on catalog budget.

Every ``agents/*.md`` frontmatter ``meta.description`` in this bundle is
concatenated into the ``delegate`` tool's own description, which is injected
into the head of EVERY session on EVERY turn -- whether or not the agent is
ever delegated to. A tutorial in a catalog entry is therefore paid for by every
session that never invokes the capability.

Policy source (canonical, not restated here):
``foundation:context/shared/description-authoring-principles.md`` V3 and the
"Example policy" section -- zero ``<example>`` blocks, zero ``<commentary>``
tags, in any description surface.

Per-agent test modules assert the same thing for the agent they own. This
module is the one that also covers an agent added LATER, which is how the
policy escaped this repo in the first place: nothing here ever looked at
``agents/*.md`` as a set.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

# Always-on catalog budget for meta.description (chars).
DESCRIPTION_CHAR_BUDGET = 600

AGENT_FILES = sorted(AGENTS_DIR.glob("*.md"))


def _description(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---"), f"{path.name}: missing YAML frontmatter"
    end = content.index("\n---", 3)
    frontmatter = yaml.safe_load(content[3:end])
    meta = frontmatter.get("meta") or {}
    description = meta.get("description")
    assert description, f"{path.name}: meta.description missing or empty"
    return description


def test_agents_directory_is_not_empty():
    """A vacuous pass on an empty glob is the failure mode this guard must not have."""
    assert AGENT_FILES, f"no agent files found under {AGENTS_DIR}"


@pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.stem)
def test_agent_description_has_no_example_blocks(agent_path: Path):
    description = _description(agent_path)
    assert description.count("<example>") == 0, (
        f"{agent_path.name}: meta.description must contain ZERO <example> blocks, "
        f"found {description.count('<example>')}"
    )
    assert description.count("<commentary>") == 0, (
        f"{agent_path.name}: meta.description must contain ZERO <commentary> tags, "
        f"found {description.count('<commentary>')}"
    )


@pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.stem)
def test_agent_description_within_catalog_budget(agent_path: Path):
    description = _description(agent_path)
    assert len(description) <= DESCRIPTION_CHAR_BUDGET, (
        f"{agent_path.name}: meta.description is {len(description)} chars, over the "
        f"{DESCRIPTION_CHAR_BUDGET}-char always-on catalog budget"
    )


@pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.stem)
def test_agent_description_states_when_not_to_use(agent_path: Path):
    """Trigger-first descriptions need the negative boundary, not just the positive one.

    A catalog entry that only says when to reach for an agent gives the router
    no way to rule it out, which is how sibling agents in the same pipeline get
    confused for one another.
    """
    description = _description(agent_path)
    assert "DO NOT USE WHEN" in description, (
        f"{agent_path.name}: meta.description must carry an explicit "
        f"'DO NOT USE WHEN' clause"
    )
