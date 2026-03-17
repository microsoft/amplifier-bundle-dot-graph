# Code-Tracer Unknowns: Tool Module Architecture

## Unresolved Questions

1. **validate.py internals** — The 3-layer validation implementation was not fully traced.
   Known: takes `dot_content` string and optional `layers` list.
   Unknown: how does "render" layer validation work (does it shell out to graphviz CLI?).

2. **analyze.py internals** — 8 analysis operations listed in input_schema but
   implementation was not traced. Likely uses networkx DiGraph.

3. **render.py** — How does it handle the path when graphviz is not installed?
   Fallback behavior not confirmed.

4. **Error propagation** — DotGraphTool.execute() returns ToolResult.
   Unknown: what happens when `pydot` is not installed at mount time?
   `assemble.py` imports pydot at module level — this could fail at import.

5. **ToolResult contract** — `from amplifier_core import ToolResult` imported but
   amplifier_core is a submodule/dependency. The full ToolResult contract
   (fields, success semantics) not traced from source.
