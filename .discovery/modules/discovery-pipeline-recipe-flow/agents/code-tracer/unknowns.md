# Code-Tracer Unknowns: Discovery Pipeline Recipe Flow

1. **@dot-graph:recipes/* resolution** — How does the recipe engine resolve `@dot-graph:` bundle references for sub-recipes? Requires registered bundle — not tested in Phase E integration.

2. **foreach + recipe parallelism** — Does `foreach` run recipe invocations sequentially or in parallel? The models.py shows `parallel:` option — is it applied here?

3. **Approval gate persistence** — If the session ends between Stage 1 and Stage 2, can the pipeline resume from the approval gate checkpoint?

4. **Context propagation across stages** — How does `change_result` (set in Stage 1) reach Stage 3 (references `{{change_result.output_dir}}`)?

5. **Topic count validation** — If prescan agent returns fewer than 3 topics, does the pipeline still proceed? No guard found in recipe code.
