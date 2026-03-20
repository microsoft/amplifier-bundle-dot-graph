# Level Synthesis: amplifier/tests/

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/tests`
**Fidelity tier:** standard
**Child subdirectories:** none
**Cross-child connections:** 0 (flat directory — no subdirectories)

---

## Files and Symbols at This Level

### `test_doc_sweep.sh` (81 lines)

A self-contained bash acceptance test script for **task-15: Main Repo Documentation Sweep**. It verifies that GPT model name references across the repo were correctly migrated.

**Internal symbols:**

| Symbol | Type | Role |
|--------|------|------|
| `check()` | bash function | Local test helper — takes a description, expectation (`empty`/`nonempty`), and a command to run; increments `PASS` or `FAIL` counter |
| `PASS` / `FAIL` | integer variables | Running counters; final exit code is 1 if `FAIL > 0` |

**External targets probed (grep-based verification):**

| Target file | Checks | What is verified |
|------------|--------|-----------------|
| `README.md` | 3 | No `gpt-5.1` refs, no `gpt-5.2` refs, has `gpt-5.4` refs |
| `docs/USER_GUIDE.md` | 2 | No `gpt-5.1` refs, has `gpt-5.4` refs |
| `recipes/document-generation.yaml` | 4 | No `gpt-4o` refs, has `gpt-5.4` refs, has `gpt-5-mini` refs, does NOT have `gpt-5.4-mini` (guards against wrong substitution order) |

The script changes directory to the repo root (`cd "$(dirname "$0")/.."`), so all path references are relative to the repo root, not to `tests/`.

---

## Cross-Child Connections

**None.** This directory has no subdirectories, so there are no cross-child connections to report.

---

## Boundary Patterns

### Pattern: Task-Scoped Acceptance Test

`test_doc_sweep.sh` is a **task-specific acceptance test** — it verifies the completion of a single named task (task-15) rather than providing ongoing regression coverage. Key characteristics:

- **Temporal artifact**: The test validates a one-time migration (GPT model name upgrade from `gpt-4o` / `gpt-5.1` / `gpt-5.2` to `gpt-5.4` / `gpt-5-mini`). It is not designed to evolve with the codebase.
- **Cross-cutting scope**: The test touches three distinct top-level directories (`README.md`, `docs/`, `recipes/`) in a single run, acting as a cross-cutting integration check for documentation consistency.
- **No test framework**: The test uses a hand-rolled `check()` helper rather than a formal test framework (pytest, bats, etc.), suggesting this is a lightweight ad-hoc verification written alongside the task.
- **Exit-code contract**: Exits 0 on full pass, 1 on any failure — compatible with CI pipeline integration.

### Pattern: Flat Single-File Test Layer

The `tests/` directory contains exactly one file and no subdirectories. This is a **minimal test layer** — not a structured test suite. There is no `conftest.py`, no `__init__.py`, no test runner configuration, and no fixture library.

---

## Uncertainties for Next Level Up

1. **Is there a broader test suite elsewhere?** Only one test exists here. Are there additional tests co-located with source code (e.g., in `context/`, `recipes/`, or `agents/` subdirectories)? The parent level (`amplifier/`) should check for test files outside `tests/`.

2. **Is task-15 complete?** The test verifies a migration. Has it been run and passed? The presence of the test without a recorded result file suggests it may never have been executed, or results are not persisted.

3. **CI integration?** There is no Makefile, `justfile`, or `.github/workflows` visible at this level. How is `test_doc_sweep.sh` invoked in CI? This is a question for the `amplifier/` parent level or the repo root.

4. **Why bash and not bats or pytest?** The test is shell-based despite the repo otherwise using Python tooling. Is this a conscious choice or ad-hoc? Parent level analysis may reveal a pattern.

5. **Is `gpt-5.4` a real model name?** The test validates against model names (`gpt-5.4`, `gpt-5-mini`) that do not correspond to known OpenAI model names at time of writing. This may indicate speculative/placeholder names used in the project, or internal naming conventions — worth flagging for the parent level.
