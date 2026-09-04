"""
Lint: every shipped recipe that references an agent must declare schema_version 2.

Why this test exists
--------------------
A schema v1 (legacy) recipe borrows its agent catalog from whatever session
invokes it. That makes an `agent:` reference silently caller-dependent: the
recipe works from a bundle that happens to carry `dot-graph:*` agents and fails
-- or resolves a *different* agent -- from one that does not.

Schema v2 fixes this by making the recipe a self-contained dependency root: it
declares a `dependencies:` closure, and `agent:` references resolve ONLY from
that closure (recipe-dependency-manifest.v1 Core 3, Core 11 -- the engine never
infers a source from an agent's namespace prefix).

So the invariant is: agent reference => schema_version 2 + a dependencies entry
that supplies it.

Validates:
- Every recipes/**/*.yaml parses as YAML (1 test)
- Every recipe with an `agent:` reference declares schema_version: 2 (1 test)
- Every such recipe declares a non-empty `dependencies:` list (1 test)
- Every dependency entry has a `source` and a `kind` of bundle|behavior (1 test)
- Every `agent:` reference is covered by some dependency's required_agents,
  or by a top-level `agents:` alias resolving to one (1 test)
- Dependency entries carry no keys beyond source/kind/required_agents (1 test)
- The known-legacy exemption list is accurate -- listed files really do lack
  agent references (1 test)
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPES_DIR = REPO_ROOT / "recipes"

# ---------------------------------------------------------------------------
# Exemptions
#
# A file listed here is allowed to reference an agent while staying schema v1.
# Each entry needs a real reason -- the only currently-known legitimate one is
# `agent: self`, which cannot be expressed as a closed-world dependency (a
# recipe cannot declare a source for the caller's own session agent). See the
# bundle-recipes tracker item recipes-80q.
#
# This map is deliberately empty: no recipe in this bundle uses `agent: self`.
# It exists so a future exemption has a documented home instead of an
# unexplained edit to the assertion below.
# ---------------------------------------------------------------------------
EXEMPT: dict[str, str] = {}

# Dependency entries accept exactly these keys (manifest.v1 Core 2). Anything
# else -- including `aliases` -- is a parse error in the v2 runner.
ALLOWED_DEPENDENCY_KEYS = {"source", "kind", "required_agents"}
ALLOWED_DEPENDENCY_KINDS = {"bundle", "behavior"}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _recipe_paths() -> list[Path]:
    """Every shipped recipe YAML, sorted for stable test output."""
    return sorted(RECIPES_DIR.rglob("*.yaml"))


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _iter_steps(data: dict):
    """Yield every step, from flat `steps:` and from staged `stages:` alike."""
    yield from data.get("steps") or []
    for stage in data.get("stages") or []:
        if isinstance(stage, dict):
            yield from stage.get("steps") or []


def _agent_refs(data: dict) -> set[str]:
    """Every `agent:` reference in the recipe."""
    refs = set()
    for step in _iter_steps(data):
        if isinstance(step, dict) and step.get("agent"):
            refs.add(step["agent"])
    return refs


def _recipes_with_agents() -> list[tuple[Path, dict]]:
    out = []
    for path in _recipe_paths():
        if _rel(path) in EXEMPT:
            continue
        data = _load(path)
        if _agent_refs(data):
            out.append((path, data))
    return out


AGENT_RECIPES = _recipes_with_agents()
AGENT_RECIPE_IDS = [_rel(p) for p, _ in AGENT_RECIPES]


# ---------------------------------------------------------------------------
# Sanity: the corpus this lint runs over is non-empty and parseable
# ---------------------------------------------------------------------------


def test_every_recipe_parses_as_yaml():
    """Every recipes/**/*.yaml must parse as a YAML mapping."""
    paths = _recipe_paths()
    assert paths, f"No recipe YAML files found under {RECIPES_DIR}"
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{_rel(path)}: recipe must be a YAML mapping"


def test_lint_corpus_is_non_empty():
    """Guard: this lint is meaningless if it matches zero files."""
    assert AGENT_RECIPES, (
        "No recipe with an `agent:` reference was found. Either the recipes "
        "moved, the step shape changed, or EXEMPT swallowed everything -- in "
        "any case this lint is no longer checking anything."
    )


# ---------------------------------------------------------------------------
# The invariant
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("path", "data"), AGENT_RECIPES, ids=AGENT_RECIPE_IDS)
def test_agent_recipe_declares_schema_version_2(path: Path, data: dict):
    """A recipe that references an agent must declare schema_version: 2."""
    assert data.get("schema_version") == 2, (
        f"{_rel(path)} references agent(s) {sorted(_agent_refs(data))} but "
        f"declares schema_version={data.get('schema_version')!r}. A legacy (v1) "
        f"recipe borrows the calling session's agent map, so it only runs from "
        f"a bundle that already carries those agents. Add `schema_version: 2` "
        f"and a `dependencies:` block naming the bundle that ships them -- or "
        f"add this file to EXEMPT with a reason."
    )


@pytest.mark.parametrize(("path", "data"), AGENT_RECIPES, ids=AGENT_RECIPE_IDS)
def test_agent_recipe_declares_dependencies(path: Path, data: dict):
    """schema_version 2 requires a non-empty dependencies list (Core 1)."""
    deps = data.get("dependencies")
    assert isinstance(deps, list) and deps, (
        f"{_rel(path)}: schema_version 2 requires a non-empty `dependencies:` "
        f"list, got {deps!r}"
    )


@pytest.mark.parametrize(("path", "data"), AGENT_RECIPES, ids=AGENT_RECIPE_IDS)
def test_dependency_entries_are_well_formed(path: Path, data: dict):
    """Each dependency needs a source and a kind of bundle|behavior (Core 2)."""
    for i, dep in enumerate(data.get("dependencies") or []):
        where = f"{_rel(path)} dependencies[{i}]"
        assert isinstance(dep, dict), f"{where}: must be a mapping, got {dep!r}"

        source = dep.get("source")
        assert isinstance(source, str) and source.strip(), (
            f"{where}: `source` is required and must be a non-empty string"
        )

        kind = dep.get("kind")
        assert kind in ALLOWED_DEPENDENCY_KINDS, (
            f"{where}: `kind` must be one of "
            f"{sorted(ALLOWED_DEPENDENCY_KINDS)}, got {kind!r}"
        )


@pytest.mark.parametrize(("path", "data"), AGENT_RECIPES, ids=AGENT_RECIPE_IDS)
def test_dependency_entries_have_no_unknown_keys(path: Path, data: dict):
    """A dependency entry accepts only source/kind/required_agents (Core 2)."""
    for i, dep in enumerate(data.get("dependencies") or []):
        if not isinstance(dep, dict):
            continue
        unknown = set(dep) - ALLOWED_DEPENDENCY_KEYS
        assert not unknown, (
            f"{_rel(path)} dependencies[{i}]: unknown key(s) {sorted(unknown)}. "
            f"A dependency entry accepts only "
            f"{sorted(ALLOWED_DEPENDENCY_KEYS)} -- anything else is a v2 parse "
            f"error, not a silent no-op."
        )


@pytest.mark.parametrize(("path", "data"), AGENT_RECIPES, ids=AGENT_RECIPE_IDS)
def test_every_agent_reference_is_declared(path: Path, data: dict):
    """Every `agent:` reference must be supplied by the declared closure.

    Undeclared is unresolved (Core 6): referencing an agent no dependency
    supplies is a preflight failure, not a runtime surprise.
    """
    supplied: set[str] = set()
    for dep in data.get("dependencies") or []:
        if isinstance(dep, dict):
            supplied.update(dep.get("required_agents") or [])

    aliases = data.get("agents") or {}

    for ref in sorted(_agent_refs(data)):
        # A reference is either a canonical namespace:name, or a bare alias
        # declared in the top-level `agents:` map (Core 3).
        canonical = aliases.get(ref, ref) if isinstance(aliases, dict) else ref
        assert canonical in supplied, (
            f"{_rel(path)}: step references agent {ref!r} (resolving to "
            f"{canonical!r}) but no dependency declares it in "
            f"`required_agents`. Declared: {sorted(supplied) or 'none'}. "
            f"The engine never infers a dependency from a namespace prefix "
            f"(Core 11) -- declare it explicitly."
        )


# ---------------------------------------------------------------------------
# The exemption list must stay honest
# ---------------------------------------------------------------------------


def test_exempt_entries_exist_and_are_justified():
    """Every EXEMPT entry must name a real file and carry a reason."""
    for rel, reason in EXEMPT.items():
        assert (REPO_ROOT / rel).exists(), (
            f"EXEMPT names {rel!r}, which does not exist. Remove the stale entry."
        )
        assert reason.strip(), f"EXEMPT entry {rel!r} has an empty reason."


def test_exempt_entries_still_need_exempting():
    """An exempt file that no longer references an agent should be un-exempted."""
    for rel in EXEMPT:
        data = _load(REPO_ROOT / rel)
        assert _agent_refs(data), (
            f"EXEMPT names {rel!r}, but it references no agent -- the lint "
            f"would not flag it anyway. Remove the exemption."
        )
