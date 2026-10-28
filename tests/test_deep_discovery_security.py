"""Regression tests for deep discovery recipe bash security boundaries."""

import asyncio
import copy
import json
import os
import subprocess
from pathlib import Path

import yaml
from amplifier_recipe_runner.engine import StepEngine
from amplifier_recipe_runner.engine import parse_program
from amplifier_recipe_runner.engine import substitute_variables


REPO_ROOT = Path(__file__).parent.parent
DEEP_PIPELINE = REPO_ROOT / "recipes" / "deep" / "discovery-pipeline.yaml"
TOPDOWN = REPO_ROOT / "recipes" / "deep" / "strategy-topdown.yaml"


def _step(recipe_path: Path, stage_name: str, step_id: str) -> dict:
    recipe = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
    for stage in recipe["stages"]:
        if stage["name"] == stage_name:
            for step in stage["steps"]:
                if step["id"] == step_id:
                    return step
    raise AssertionError(f"{step_id} not found in {recipe_path}")


def _run_bash_step(
    step: dict, context: dict[str, object], *, cwd: Path
) -> subprocess.CompletedProcess[str]:
    """Execute a bash step after the real runner renders command and env."""
    command = substitute_variables(step["command"], context)
    env = os.environ.copy()
    env.update(
        {
            name: substitute_variables(value, context)
            for name, value in step.get("env", {}).items()
        }
    )
    return subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _bash_commands() -> list[tuple[Path, str, str]]:
    """Return every declared bash command, including nested loop bodies."""
    commands = []
    for recipe_path in REPO_ROOT.joinpath("recipes").rglob("*.yaml"):
        recipe = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))

        def walk(value: object) -> None:
            if isinstance(value, dict):
                if value.get("type") == "bash":
                    command = value.get("command")
                    assert isinstance(command, str), (
                        f"{recipe_path}: bash step {value.get('id')!r} has no command"
                    )
                    commands.append((recipe_path, str(value.get("id")), command))
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(recipe)
    return commands


def _newline_injection(prefix: str, sentinel: Path) -> str:
    """Make a comment-breaking payload that would execute as Python source."""
    return (
        f"{prefix}\n"
        "__import__('pathlib').Path("
        f"{str(sentinel)!r}"
        ").touch()\n#"
    )


def test_deep_resolve_context_treats_newline_injected_repo_path_as_env_data(
    tmp_path: Path,
) -> None:
    """A malicious path cannot escape an interpolated comment into Python."""
    step = _step(DEEP_PIPELINE, "scan", "resolve-context")
    sentinel = tmp_path / "executed"
    valid_repo = tmp_path / "repo"
    valid_repo.mkdir()
    payload = _newline_injection(str(valid_repo), sentinel)

    result = _run_bash_step(
        step,
        {"repo_path": payload, "output_dir": ""},
        cwd=REPO_ROOT,
    )

    assert result.returncode != 0
    assert "repo_path must name an existing directory" in result.stderr
    assert not sentinel.exists()


def test_deep_prepare_topics_treats_newline_injected_topic_as_data(
    tmp_path: Path,
) -> None:
    """Unused topic context cannot escape a command comment into Python."""
    step = _step(TOPDOWN, "investigate", "prepare-topics")
    output = tmp_path / "discovery"
    output.mkdir()
    (output / "topics.json").write_text(
        json.dumps(
            [
                {
                    "name": "Valid Topic",
                    "slug": "valid-topic",
                    "description": "A valid topic loaded from the persisted file.",
                }
            ]
        ),
        encoding="utf-8",
    )
    sentinel = tmp_path / "executed"
    payload = _newline_injection("valid-topic", sentinel)

    result = _run_bash_step(
        step,
        {"ctx": {"output_dir": str(output)}, "topics": payload},
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert not sentinel.exists()


def test_no_bash_command_contains_recipe_template_markers() -> None:
    """Bash commands must receive untrusted values through env, never templates."""
    violations = [
        f"{recipe_path.relative_to(REPO_ROOT)}:{step_id}"
        for recipe_path, step_id, command in _bash_commands()
        if "{{" in command
    ]

    assert not violations, (
        "recipe template markers in bash commands can interpolate into comments "
        "or source code: " + ", ".join(violations)
    )


def test_deep_prescan_fails_closed_when_prescan_is_unavailable(tmp_path: Path) -> None:
    """Deep discovery must not silently substitute an incomplete directory listing."""
    step = _step(DEEP_PIPELINE, "scan", "structural-scan")
    target = tmp_path / "target"
    target.mkdir()
    output = tmp_path / "output"

    # Run outside the bundle so the recipe's relative module import is absent.
    result = _run_bash_step(
        step,
        {"ctx": {"repo_path": str(target), "output_dir": str(output)}},
        cwd=tmp_path,
    )

    assert result.returncode != 0
    assert "prescan failed:" in result.stderr
    assert not (output / "prescan-result.json").exists()


def test_deep_topic_prepare_rejects_traversal_slug_before_creating_directories(
    tmp_path: Path,
) -> None:
    """A malicious topic slug cannot escape the top-down modules directory."""
    step = _step(TOPDOWN, "investigate", "prepare-topics")
    output = tmp_path / "discovery"
    output.mkdir()
    (output / "topics.json").write_text(
        json.dumps(
            [
                {
                    "name": "Escape",
                    "slug": "../outside",
                    "description": "Try to escape the output tree",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = _run_bash_step(
        step,
        {"ctx": {"output_dir": str(output)}, "topics": []},
        cwd=REPO_ROOT,
    )

    assert result.returncode != 0
    assert "slug must contain lowercase letters" in result.stderr
    assert not (tmp_path / "outside").exists()


def test_topdown_downstream_foreach_uses_normalized_prepared_topics(tmp_path: Path) -> None:
    """The real runner dispatches normalized slugs, never raw topic-select output."""
    output_dir = tmp_path / "discovery"
    output_dir.mkdir()
    raw_topics = [
        {
            "name": "Core ",
            "slug": "core ",
            "description": "The central implementation. ",
        }
    ]
    (output_dir / "topics.json").write_text(json.dumps(raw_topics), encoding="utf-8")

    prepare_context = {"ctx": {"output_dir": str(output_dir)}}
    prepare = StepEngine(
        parse_program({"steps": [_step(TOPDOWN, "investigate", "prepare-topics")]}),
        invoke_agent=None,  # type: ignore[arg-type] - this test runs only bash and recipe steps
        workspace=REPO_ROOT,
        run_id="prepare-normalized-topics",
    )
    prepare_outcome = asyncio.run(prepare.execute(prepare_context))
    assert prepare_outcome.status == "succeeded"
    assert prepare_context["prep_result"]["topics"][0]["slug"] == "core"

    # The two production foreach steps use @mentions, which require the host
    # resolver. Replace only that transport detail with an existing local child
    # and keep each real foreach expression and context mapping intact.
    child_recipe = tmp_path / "child.yaml"
    child_recipe.write_text("steps: []\n", encoding="utf-8")
    for stage_name, step_id, expected_key, expected_value in (
        ("investigate", "investigate-topics", "topic_slug", "core"),
        ("synthesize", "reconcile-modules", "module_dir", f"{output_dir}/modules/core"),
    ):
        dispatched_contexts: list[dict[str, object]] = []

        async def capture_sub_recipe(_path, context, _step_spec, _recursion):
            dispatched_contexts.append(context)
            return {}

        downstream = copy.deepcopy(_step(TOPDOWN, stage_name, step_id))
        downstream["recipe"] = "child.yaml"
        runner_context = {
            "topics": raw_topics,
            "prep_result": prepare_context["prep_result"],
            "ctx": {"repo_path": str(tmp_path), "output_dir": str(output_dir)},
            "fidelity": "standard",
            "lens": "architecture",
        }
        engine = StepEngine(
            parse_program({"steps": [downstream]}),
            invoke_agent=None,  # type: ignore[arg-type] - sub-recipes are captured below
            workspace=tmp_path,
            recipe_path=tmp_path / "parent.yaml",
            run_id=f"normalized-{step_id}",
            sub_recipe_runner=capture_sub_recipe,
        )

        outcome = asyncio.run(engine.execute(runner_context))

        assert outcome.status == "succeeded"
        assert len(dispatched_contexts) == 1
        assert dispatched_contexts[0][expected_key] == expected_value