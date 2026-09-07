---
name: architecture-overview-diagram
description: Folded into dot-analysis — still runnable as /architecture-overview-diagram.
disable-model-invocation: true
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit_file
  - bash
  - glob
  - grep
  - delegate
  - dot_graph
  - load_skill
model_role: reasoning
---

# Architecture Overview Diagram (folded)

The full 12-step workflow is preserved verbatim as a reference file inside the
**dot-analysis** skill. Nothing was deleted.

**Do this first, then follow what you read:**

`read_file("<this skill_directory>/../dot-analysis/reference/architecture-overview-diagram.md")`

`skill_directory` is returned by `load_skill`. Repository path:
`skills/dot-analysis/reference/architecture-overview-diagram.md`

If that path does not resolve, run `load_skill(skill_name="dot-analysis")` and read
`reference/architecture-overview-diagram.md` from the `skill_directory` it returns.

Execute the workflow exactly as written there — including its human checkpoints.
