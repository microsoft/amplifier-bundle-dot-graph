# Integration-Mapper: Tool Module Architecture

## Cross-Boundary Integration Points

### Boundary 1: Amplifier Coordinator ↔ Tool Module
- **Contract:** `mount(coordinator, config)` async function
- **Registration:** `coordinator.mount("tools", tool, name="dot_graph")`
- **Mechanism:** Tool is registered as a named tool; coordinator dispatches calls to `execute()`
- **Effect:** The 6 operations become available as `dot_graph` tool in any agent session

### Boundary 2: Tool Module ↔ Python Dependencies
- **pydot:** Required by `validate.py`, `assemble.py`. Import at module level in assemble.py —
  if pydot unavailable, module import fails silently or raises ImportError.
- **networkx:** Required by `analyze.py`. Not at module level in `__init__.py` but via analyze.
- **graphviz CLI:** External binary — `render.py` and `setup_helper.py` shell out to it.
  Render fails gracefully if graphviz not installed.

### Boundary 3: prescan ↔ Discovery Pipeline Recipe
- **Caller:** `discovery-pipeline.yaml` structural-scan bash step
- **Protocol mismatch (BUG):** Recipe called `prescan(repo_path=...)` treating the MODULE
  as callable. Correct call: `prescan.prescan_repo(repo_path)`.
- **Fallback path:** Recipe had a fallback for this failure — basic dir listing.

### Boundary 4: assemble ↔ Discovery Pipeline Recipe  
- **Caller:** `discovery-pipeline.yaml` assemble bash step
- **Protocol mismatch (BUG):** Recipe called `assemble(output_dir, topics)` — wrong module+signature.
  Correct: `assemble.assemble_hierarchy(manifest, output_dir)` with manifest dict.
- **Fix applied:** Builds proper manifest from topics before calling assemble_hierarchy.

### Boundary 5: Tool Module ↔ File System
- `prescan.py` reads directory structure (read-only os.walk)
- `assemble.py` writes `.dot` files to `output_dir/`
- `render.py` may write to temp dir or specified output_path

## Composition Effects

**Discovery pipeline integration:** The prescan+assemble pair forms a pipeline bookend:
- prescan at start → produces inventory
- assemble at end → produces output DOTs from investigation results
These two modules are never called in the same agent turn — they bridge different pipeline phases.

**pydot as shared dependency:** validate, assemble both depend on pydot. This creates
an implicit coupling: if pydot breaks, both validation AND assembly fail.
