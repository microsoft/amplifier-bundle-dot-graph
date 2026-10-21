"""Execute production bash steps in the real runner, without model calls."""

import asyncio
import copy
import json
from pathlib import Path

import pytest
import yaml
from amplifier_recipe_runner.engine import StepEngine, parse_program

ROOT = Path(__file__).resolve().parents[1]
TOPIC = [{"name": "Core", "slug": "core", "description": "Central implementation"}]


def step(file, id):
    data = yaml.safe_load((ROOT / "recipes" / file).read_text())

    def find(value):
        if isinstance(value, dict):
            if value.get("id") == id:
                return copy.deepcopy(value)
            for child in value.values():
                found = find(child)
                if found:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = find(child)
                if found:
                    return found
        return None

    result = find(data)
    assert result
    return result


def run(file, id, context, cwd):
    engine = StepEngine(
        parse_program({"steps": [step(file, id)]}),
        invoke_agent=None,
        workspace=cwd,
        run_id="security-regression",
    )
    return asyncio.run(engine.execute(context))


@pytest.mark.parametrize("existing", [None, "NOT DOT " * 10])
def test_overview_plain_response_and_invalid_existing(tmp_path, existing):
    out = tmp_path / "output"
    out.mkdir()
    file = out / "overview.dot"
    if existing:
        file.write_text(existing)
    dot = 'digraph "system spine" { subgraph cluster_a { a [label="}"]; } a -> b; }'
    ctx = {
        "change_result": {"output_dir": str(tmp_path), "repo_path": str(tmp_path)},
        "overview_dot_result": "Here is the diagram:\n```dot\n" + dot + "\n```",
    }
    result = run("quick/discovery-pipeline.yaml", "verify-overview-dot", ctx, tmp_path)
    if existing:
        assert result.status != "succeeded"
        assert file.read_text() == existing
    else:
        assert result.status == "succeeded", result
        assert ctx["overview_dot_verify_result"]["status"] == "recovered"
        assert file.read_text() == dot


@pytest.mark.parametrize("file", ["quick/discovery-pipeline.yaml", "deep/strategy-topdown.yaml"])
def test_topic_file_symlink_does_not_overwrite_outside(tmp_path, file):
    outside = tmp_path / "outside"
    outside.write_text("KEEP")
    out = tmp_path / "out"
    out.mkdir()
    (out / "topics.json").symlink_to(outside)
    ctx = {
        "topics": TOPIC,
        "change_result": {"output_dir": str(out)},
        "ctx": {"output_dir": str(out)},
        "parent_topics_available": "false",
    }
    id = "prepare-topics" if file.startswith("quick") else "save-topics-from-scan"
    result = run(file, id, ctx, tmp_path)
    assert result.status != "succeeded"
    assert outside.read_text() == "KEEP"


@pytest.mark.parametrize("file,id,output", [
    ("quick/discovery-pipeline.yaml", "structural-scan", "scan_result"),
    ("deep/discovery-pipeline.yaml", "structural-scan", "scan_result"),
    ("deep/strategy-topdown.yaml", "structural-scan", "scan_result"),
    ("deep/strategy-bottomup.yaml", "prescan", "prescan_result"),
])
def test_prescan_imports_installed_module_not_workspace(tmp_path, monkeypatch, file, id, output):
    target = tmp_path / "target"
    target.mkdir()
    (target / "main.py").write_text("print('hello')\n")
    marker = tmp_path / "IMPORTED"
    for parent in [tmp_path, tmp_path / "modules/tool-dot-graph"]:
        fake = parent / "amplifier_module_tool_dot_graph"
        fake.mkdir(parents=True)
        (fake / "__init__.py").write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).touch()\nraise RuntimeError('UNTRUSTED')\n"
        )
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    out = tmp_path / "out"
    ctx = {"ctx": {"repo_path": str(target), "output_dir": str(out)},
           "change_result": {"repo_path": str(target), "output_dir": str(out), "tier": "full"},
           "parent_topics_available": "false"}
    result = run(file, id, ctx, tmp_path)
    assert not marker.exists()
    assert result.status == "succeeded", result
    scan = ctx[output]
    structure = scan.get("structure", scan)
    assert structure["success"]
    assert structure["total_files"] == 1


def test_overview_missing_and_invalid_response_fail(tmp_path):
    for text in ["no graph produced", "digraph broken { a -> }"]:
        ctx = {"change_result": {"repo_path": str(tmp_path), "output_dir": str(tmp_path)},
               "overview_dot_result": text}
        result = run("quick/discovery-pipeline.yaml", "verify-overview-dot", ctx, tmp_path)
        assert result.status != "succeeded"
        assert not (tmp_path / "output/overview.dot").exists()


# Every production bash file-write destination and directory-creation boundary.
# Run the same step with a safe destination first, so a missing context variable
# or import failure cannot give a false-positive security result.
WRITES = [
    ("quick/discovery-pipeline.yaml", "prepare-topics", "topics.json"),
    ("quick/discovery-pipeline.yaml", "prepare-topics", "modules/core/agents"),
    ("quick/discovery-pipeline.yaml", "prepare-topics", "output/modules"),
    ("quick/discovery-pipeline.yaml", "assemble", "manifest.json"),
    ("quick/discovery-pipeline.yaml", "assemble", "output"),
    ("quick/discovery-pipeline.yaml", "verify-overview-dot", "output/overview.dot"),
    ("quick/discovery-pipeline.yaml", "verify-overview-dot", "output"),
    ("quick/discovery-pipeline.yaml", "update-metadata", "last-run.json"),
    ("deep/discovery-pipeline.yaml", "structural-scan", "prescan-result.json"),
    ("deep/strategy-topdown.yaml", "structural-scan", "prescan-result.json"),
    ("deep/strategy-topdown.yaml", "save-topics-from-scan", "topics.json"),
    ("deep/strategy-topdown.yaml", "save-topics-from-file", "topics.json"),
    ("deep/strategy-topdown.yaml", "prepare-topics", "modules/core/agents"),
    ("deep/strategy-topdown.yaml", "update-metadata", "last-run.json"),
    ("deep/strategy-bottomup.yaml", "prescan", "prescan-result.json"),
    ("deep/strategy-bottomup.yaml", "compute-traversal", "traversal-plan.json"),
    ("deep/strategy-bottomup.yaml", "update-traversal-plan", "traversal-plan.json"),
    ("deep/strategy-bottomup.yaml", "identify-subsystems", "subsystems"),
    ("deep/strategy-bottomup.yaml", "update-metadata", "last-run.json"),
    ("deep/discovery-combine.yaml", "render", "combined.png"),
    ("deep/discovery-combine.yaml", "hoist-outputs", "overview.dot"),
    ("deep/discovery-combine.yaml", "update-metadata", "last-run.json"),
]


def write_context(root):
    target, out = root / "target", root / "out"
    target.mkdir(parents=True)
    out.mkdir()
    (target / "main.py").write_text("print('hello')\n")
    (target / ".discovery").mkdir()
    (target / ".discovery/topics.json").write_text(json.dumps(TOPIC))
    (out / "topics.json").write_text(json.dumps(TOPIC))
    (out / "traversal-plan.json").write_text(json.dumps({"post_order": [], "completed": []}))
    (out / "combined.dot").write_text("digraph combined { a -> b; }")
    paths = {"repo_path": str(target), "output_dir": str(out)}
    return {
        **paths, "ctx": paths.copy(), "change_result": {**paths, "tier": "full", "current_commit": ""},
        "prescan_result": paths.copy(), "traversal_plan": paths.copy(), "topics": TOPIC,
        "parent_topics_available": "false", "fidelity": "standard", "render_png": "true",
        "overview_dot_result": "digraph recovered { a -> b; }",
        "validation_result": {"valid_count": 1, "error_count": 0},
    }, out


@pytest.mark.parametrize("file,id,destination", WRITES)
def test_all_bash_writes_reject_preexisting_output_symlinks(tmp_path, file, id, destination):
    for attack in (False, True):
        ctx, out = write_context(tmp_path / str(attack))
        if id == "save-topics-from-file":
            ctx["parent_topics_available"] = "true"
        path = out / destination
        outside = tmp_path / ("outside-" + str(attack))
        is_file = path.suffix in (".json", ".dot", ".png")
        if is_file:
            outside.write_text("KEEP")
        else:
            outside.mkdir()
        if attack:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.is_file():
                path.unlink()
            path.symlink_to(outside, target_is_directory=not is_file)
        result = run(file, id, ctx, tmp_path)
        if attack:
            assert result.status != "succeeded", (file, id, result)
            assert "unsafe" in str(result) or "escapes" in str(result), result
            if is_file:
                assert outside.read_text() == "KEEP"
            else:
                assert list(outside.iterdir()) == []
        else:
            assert result.status == "succeeded", (file, id, result)
            assert path.exists(), (file, id, destination)


@pytest.mark.parametrize("response", [
    'digraph "quoted graph" { subgraph cluster_a { a [label="}"]; } a -> b; }',
    'Here is a graph in prose:\nstrict digraph G { subgraph cluster_a { a; } a -> b; }\nDone.',
    'graph "undirected graph" { a -- b; }',
])
def test_plain_agent_response_recovers_complete_graph(tmp_path, response):
    ctx, out = write_context(tmp_path)
    ctx["overview_dot_result"] = response
    result = run("quick/discovery-pipeline.yaml", "verify-overview-dot", ctx, tmp_path)
    assert result.status == "succeeded", result
    assert ctx["overview_dot_verify_result"]["status"] == "recovered"
    assert (out / "output/overview.dot").read_text().endswith("}")


def test_existing_valid_dot_is_parsed_and_preserved(tmp_path):
    ctx, out = write_context(tmp_path)
    path = out / "output/overview.dot"
    path.parent.mkdir()
    path.write_text("digraph G { a -> b; }")
    result = run("quick/discovery-pipeline.yaml", "verify-overview-dot", ctx, tmp_path)
    assert result.status == "succeeded", result
    assert ctx["overview_dot_verify_result"]["status"] == "ok"
    assert path.read_text() == "digraph G { a -> b; }"


def test_combine_imports_ignore_workspace_packages_and_pythonpath(tmp_path, monkeypatch):
    ctx, out = write_context(tmp_path)
    marker = tmp_path / "IMPORTED"
    for parent in [tmp_path, tmp_path / "modules/tool-dot-graph"]:
        fake = parent / "amplifier_module_tool_dot_graph"
        fake.mkdir(parents=True)
        (fake / "__init__.py").write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).touch()\nraise RuntimeError('UNTRUSTED')\n"
        )
    for name in ["json", "pydot"]:
        (tmp_path / f"{name}.py").write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).touch()\nraise RuntimeError('UNTRUSTED')\n"
        )
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    for id in ["validate", "render"]:
        result = run("deep/discovery-combine.yaml", id, ctx, tmp_path)
        assert result.status == "succeeded", result
        assert not marker.exists()
    assert (out / "combined.png").read_bytes().startswith(b"\x89PNG")


def test_quick_bash_pipeline_preserves_literal_paths_and_topic_data(tmp_path):
    target = tmp_path / "repo '\" $(touch EXECUTED)\nEOF\n"
    target.mkdir()
    (target / "main.py").write_text("print('hello')\n")
    out = tmp_path / "output '\" $(touch EXECUTED)\nEOF\n"
    ctx = {"repo_path": str(target), "output_dir": str(out), "fidelity": "standard"}
    file = "quick/discovery-pipeline.yaml"
    for id in ("change-detect", "structural-scan"):
        result = run(file, id, ctx, tmp_path)
        assert result.status == "succeeded", result
    ctx["topics"] = [{**TOPIC[0], "description": "'\" $(touch EXECUTED)\nEOF\nliteral"}]
    assert run(file, "prepare-topics", ctx, tmp_path).status == "succeeded"
    module = out / "output/modules/core/diagram.dot"
    module.write_text("digraph core { a -> b; }")
    assert run(file, "assemble", ctx, tmp_path).status == "succeeded"
    assert not ctx["assemble_result"].get("error"), ctx["assemble_result"]
    assert run(file, "validate", ctx, tmp_path).status == "succeeded"
    ctx["overview_dot_result"] = "digraph G { subgraph cluster_a { a; } a -> b; }"
    assert run(file, "verify-overview-dot", ctx, tmp_path).status == "succeeded"
    assert run(file, "update-metadata", ctx, tmp_path).status == "succeeded"
    assert json.loads((out / "topics.json").read_text()) == ctx["topics"]
    assert (out / "last-run.json").exists()
    assert not (tmp_path / "EXECUTED").exists()


def test_deep_bash_flows_preserve_explicit_output_boundary(tmp_path):
    """Exercise real sequential context flow; seed only model-produced artifacts."""
    target = tmp_path / "target '\" $(touch EXECUTED)\nEOF\n"
    target.mkdir()
    (target / "main.py").write_text("print('hello')\n")
    output = tmp_path / "explicit-output"
    parent = {"repo_path": str(target), "output_dir": str(output)}
    for id in ["resolve-context", "structural-scan"]:
        result = run("deep/discovery-pipeline.yaml", id, parent, tmp_path)
        assert result.status == "succeeded", result
    assert (output / "prescan-result.json").exists()

    topdown, bottomup = output / "topdown", output / "bottomup"
    ctx = {"repo_path": str(target), "output_dir": str(topdown),
           "parent_topics_available": "false", "fidelity": "standard"}
    for id in ["resolve-context", "structural-scan"]:
        result = run("deep/strategy-topdown.yaml", id, ctx, tmp_path)
        assert result.status == "succeeded", result
    ctx["topics"] = TOPIC
    for id in ["save-topics-from-scan", "prepare-topics", "update-metadata"]:
        result = run("deep/strategy-topdown.yaml", id, ctx, tmp_path)
        assert result.status == "succeeded", result
    assert (topdown / "last-run.json").exists()

    ctx = {"repo_path": str(target), "output_dir": str(bottomup), "fidelity": "standard"}
    for id in ["resolve-context", "prescan", "compute-traversal",
               "update-traversal-plan", "identify-subsystems", "update-metadata"]:
        result = run("deep/strategy-bottomup.yaml", id, ctx, tmp_path)
        assert result.status == "succeeded", result
    assert (bottomup / "last-run.json").exists()

    combined = output / "combined"
    combined.mkdir()
    (combined / "combined.dot").write_text("digraph combined { a -> b; }")
    ctx = {"repo_path": str(target), "topdown_dir": str(topdown),
           "bottomup_dir": str(bottomup), "output_dir": str(combined), "render_png": "true"}
    for id in ["resolve-context", "validate", "render", "hoist-outputs", "update-metadata"]:
        result = run("deep/discovery-combine.yaml", id, ctx, tmp_path)
        assert result.status == "succeeded", result
    assert (combined / "overview.dot").exists()
    assert (combined / "combined.png").read_bytes().startswith(b"\x89PNG")
    assert (combined / "last-run.json").exists()
    assert not (target / ".discovery").exists()
    assert not (tmp_path / "EXECUTED").exists()