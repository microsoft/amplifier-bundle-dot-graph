# Code-Tracer Unknowns: Agent Constellation

1. **Agent capability differences at runtime** — All agents specify model_role:reasoning but the actual model dispatched depends on the session's routing matrix. How do discovery agents behave with non-reasoning models?

2. **discovery-prescan-instructions.md** — Referenced as @dot-graph:context/discovery-prescan-instructions.md but this file was not found in the repo during the scan. Is it missing or in a different location?

3. **Agent memory / cross-step context** — How much context from the structural scan does each investigation agent receive? The recipe passes `repo_path` and `output_dir` but not the full scan result.

4. **Synthesizer retry semantics** — When the quality gate retries, the synthesizer receives `_validation_errors`. Does it create a new diagram.dot or amend the existing one? What if the file system state is inconsistent?
