# Integration-Mapper Unknowns: Discovery Pipeline Recipe Flow

1. **Sub-recipe session isolation** — When the outer recipe dispatches a sub-recipe per topic (foreach), do all topic sub-recipes share a session or each get a fresh session? If shared, context pollution between topics is a risk.

2. **Context variable injection into Python** — `{{topics}}` is substituted as a raw Python literal into the bash script. If a topic slug contains `'` or `"`, this breaks the Python syntax. No escaping observed.

3. **approval_gate persistence** — If the session is closed after Stage 1 approval, can a new session resume from the approval checkpoint? The recipe framework supports session resumability via checkpointing, but this was not tested.

4. **Sub-recipe bundle resolution** — `@dot-graph:recipes/discovery-investigate-topic.yaml` requires the recipe engine to know the bundle root path. If the bundle isn't registered, this fails silently or errors. Not tested.
