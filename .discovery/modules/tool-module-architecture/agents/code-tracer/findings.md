# Code-Tracer Findings: Tool Module Architecture

## Module Location
`modules/tool-dot-graph/amplifier_module_tool_dot_graph/`

## Key Finding 1: Router Pattern (dispatch via if-chain)
**File:** `__init__.py:175-257`

`DotGraphTool.execute()` is the single entry point. It receives `input_data: dict[str, Any]`
and dispatches based on `operation` string:

```
"validate"  → validate.validate_dot(dot_content, layers=layers)
"render"    → render.render_dot(dot_content, output_format, engine, output_path)
"setup"     → setup_helper.check_environment()
"analyze"   → analyze.analyze_dot(dot_content, options)
"prescan"   → prescan.prescan_repo(repo_path)
"assemble"  → assemble.assemble_hierarchy(manifest, output_dir)
```

No registry or plugin system — plain if/elif chain. `options` dict carries operation-specific params.

## Key Finding 2: Mount Contract
**File:** `__init__.py:260-286`

`async def mount(coordinator, config)` is the Amplifier module contract:
1. Instantiates `DotGraphTool()`
2. Calls `await coordinator.mount("tools", tool, name=tool.name)`
3. Returns metadata: `{name, version, provides}`

The tool is registered as `"dot_graph"` — single tool, 6 operations.

## Key Finding 3: prescan — Pure Python Walker
**File:** `prescan.py:93-157`

`prescan_repo(repo_path: str) -> dict`
- Uses `os.walk` with `_SKIP_DIRS` pruning
- Detects modules via indicator files (`__init__.py`, `Cargo.toml`, etc.)
- Returns: `{success, repo_path, languages, total_files, modules, build_manifests, entry_points, directory_tree}`
- No external dependencies — pure Python

## Key Finding 4: assemble — pydot Required
**File:** `assemble.py:17-18`

`import pydot` at module level. `assemble_hierarchy(manifest, output_dir)` requires:
```
manifest = {
    "modules": {name: {"dot_path": str, "subsystem": str}},
    "subsystems": {name: {"modules": [str]}}
}
```
Builds subsystem clusters with `pydot.Subgraph(f"cluster_{name}")` and overview graph.
Auto-collapses overview if >80 nodes or >250 lines.

## Key Finding 5: validate — 3-Layer
**File:** `validate.py` (not fully read, but from __init__.py routing)

Called with `validate_dot(dot_content, layers=layers)` where layers can be
`["syntax", "structural", "render"]`. Returns `{valid: bool, issues: [...]}`.

## Call Chain Evidence
```
amplifier coordinator
  → coordinator.mount("tools", DotGraphTool())
    → DotGraphTool.execute({"operation": "prescan", "options": {"repo_path": "..."}})
      → prescan.prescan_repo(repo_path)
        → _collect_all_files(repo)
          → os.walk with _SKIP_DIRS pruning
        → _detect_modules(repo, all_files)
        → _build_directory_tree(repo, max_depth=4)
```
