# Integration-Mapper Unknowns: Tool Module Architecture

1. **amplifier_core ToolResult contract** — What fields does ToolResult carry?
   What does `success=False` mean for the coordinator? Does it surface as an error to the agent?

2. **Module config parameter** — `mount(coordinator, config=None)` accepts config
   but the implementation ignores it. What configuration could be passed?

3. **Tool naming collision** — If two modules both register as "dot_graph", what happens?
   Is there a registration guard?

4. **pydot import-time failure** — `assemble.py` has `import pydot` at line 17 (module level).
   If pydot is missing, the entire module fails to import. Does this cause mount() to fail?
   Or is the import lazy?

5. **graphviz version compatibility** — Which graphviz CLI version does render.py require?
   Is there a minimum version check in setup_helper.py?
