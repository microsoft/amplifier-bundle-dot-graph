# DONE-NOTE — lane `j1e6-ci-dot-graph`

**Item:** `model_performance-j1e6` — *CI for the 19 repos that have NO `.github/workflows` at all — red-then-green proven, one PR per repo*
**Repo slice:** `microsoft/amplifier-bundle-dot-graph`
**Branch:** `lane/j1e6-ci-dot-graph` · **PR:** [#9](https://github.com/microsoft/amplifier-bundle-dot-graph/pull/9)
**Base:** `main` @ `d38a74a`
**Date:** 2026-09-07

---

## Outcome

**Every deliverable DONE.** No deliverable was recorded NOT-POSSIBLE; the cap did not bind
(it authorized $0 for a deliverable that buys no API calls — see *Spend* below).

This repo had **no `.github/workflows/` at all**. It now has a four-job workflow, proven red
before proven green, shipped as a PR ready for the manager to land.

---

## Deliverables

| deliverable | state | evidence |
|---|---|---|
| `.github/workflows/ci.yml` running the real suite, ruff pinned, `push:main` + `pull_request`, no path filters / `continue-on-error` / `\|\| true` | **DONE** | commit `df50f19` |
| BOTH run URLs quoted in the PR body; RED run's job log shows the suite executing with a genuine **test** failure | **DONE** | RED [34150232761](https://github.com/microsoft/amplifier-bundle-dot-graph/actions/runs/34150232761) · GREEN [34150486730](https://github.com/microsoft/amplifier-bundle-dot-graph/actions/runs/34150486730) |
| Scratch PR CLOSED and branch DELETED — verified, not assumed | **DONE** | PR #8 `state: CLOSED`; `git ls-remote --heads origin scratch/j1e6-ci-red-proof` returns empty |
| Statement of what the suite actually covers | **DONE** | 1350 root tests + 193 module tests = **1543**. Not an import smoke |
| Clean main red → report + fix as separate named commits, never by weakening the workflow | **DONE** | 11 test failures + 1 ruff finding found; 4 named fix commits `0929d61`, `3cd7a49`, `c8149cf`, `1ae7b11` |
| DRAFT PR, marked ready when GREEN is in; DO NOT MERGE | **DONE** | opened `--draft`, marked ready after the green run. Not merged |

---

## The red-then-green gate

**RED** — scratch branch `scratch/j1e6-ci-red-proof`, scratch PR #8, run
[34150232761](https://github.com/microsoft/amplifier-bundle-dot-graph/actions/runs/34150232761).
All **6 of 6** jobs failed, each for its intended reason:

| job | deliberate defect | observed in the job log |
|---|---|---|
| `Lint` | `deliberately_undefined_name` in `scripts/zz_ci_red_proof.py` | `F821 Undefined name` … `Found 1 error.` |
| `Tests — root (3.11)` | `assert 1 == 2` | **`1 failed, 1350 passed in 6.25s`** |
| `Tests — root (3.12)` | same | **`1 failed, 1350 passed in 6.74s`** |
| `Tests — root (3.13)` | same | **`1 failed, 1350 passed in 5.65s`** |
| `Tests — tool-dot-graph` | `assert 1 == 2` | **`1 failed, 193 passed in 2.74s`** |
| `Bundle structure (YAML)` | malformed `behaviors/zz-ci-red-proof.yaml` | `OK bundle.md` … `is not valid YAML: mapping values are not allowed here` |

The load-bearing part is that the test jobs failed **on a test assertion with the rest of the
suite passing**, not on setup or lint. That is the difference between a CI proven to execute the
suite and one that merely proved it can exit non-zero.

**Cleanup, verified rather than assumed:**

```
$ gh pr view 8 --json state,closed   -> {"closed":true,"state":"CLOSED"}
$ git ls-remote --heads origin scratch/j1e6-ci-red-proof   -> (empty)
```

**GREEN** — PR #9, run
[34150486730](https://github.com/microsoft/amplifier-bundle-dot-graph/actions/runs/34150486730).
All 6 jobs `success`: `1350 passed` on 3.11/3.12/3.13, `193 passed` for the module,
`All checks passed!` for ruff, and 3 behaviors + `bundle.md` parsed cleanly.

---

## Finding 1 — clean main did not pass its own suite (11 failures + 1 ruff finding)

`main` @ `d38a74a` — the state every catalog and patch PR in this batch merged into — fails
**11 of 1351** root tests, and carries one ruff finding. This was invisible because nothing in
the repo ever ran the suite: PR #7 (the 14,615 → 6,484 char delegate-catalog reduction, the
largest in the sweep) merged with **only `license/cla` green**, and the
`tests/test_agent_description_policy.py` it added has never been executed by any automation.

None of the 11 is a product defect. All are **tests asserting a past state** that the source
deliberately moved on from. Fixed as four separate named commits — no `continue-on-error`, no
narrowed lint selection:

**`0929d61` — ruff `F401`.** `modules/tool-dot-graph/tests/test_mount_stub.py:9` imports
`unittest.mock.call` and never uses it. The only lint finding in the repo at the chosen pin.

**`3cd7a49` — three exact-literal version assertions, never updated across bumps.**

| file | test expected | ships |
|---|---|---|
| `bundle.md` | `0.2.0` | `0.3.1` |
| `behaviors/dot-core.yaml` | `0.2.0` | `0.3.0` |
| `behaviors/dot-discovery.yaml` | `0.1.0` | `0.2.0` |

Re-pinned to the shipped values — the smallest change that makes the suite honest. **Recorded
as a known treadmill**: an exact-literal version assertion fails on every legitimate bump and
protects nothing a consumer depends on. Asserting "present and semver-shaped" would end the
cycle, but that is a design call for the repo owner, not one a CI-wiring PR should take
unilaterally. Raised as a follow-up in the PR body instead.

**`c8149cf` — seven tests asserting a `context` key that was deliberately removed.**
`behaviors/dot-core.yaml` and `behaviors/dot-discovery.yaml` each carry an in-file NOTE saying
their awareness content was moved to an `@`-mention in its agent sink to keep ~540 and ~462
tokens out of always-on context, citing `BUNDLE_GUIDE.md §"Behavior context.include Policy"`.
The tests still asserted `context.include`.

*Verified before changing anything* — `agents/dot-author.md:119` and `:121` do carry
`@dot-graph:context/dot-awareness.md` and `@dot-graph:context/discovery-awareness.md`, so the
content genuinely reaches a model at its new location. **The tests were stale, not catching a
regression.** Rewritten to assert the same invariant at its new home: the doc exists; at least
one agent `@`-mentions it (fails loud if orphaned); and the behavior declares **no** `context`
key — which pins the token-reduction decision so always-on context cannot creep back silently.

**`1ae7b11` — `.gitignore` assertion narrower than the rule in place.**
`test_gitignore_has_amplifier_specific_section` asserted the literal `ai_working/tmp`;
`.gitignore:69` ignores `ai_working/`, which subsumes it. Fixed test-side, because adding
`ai_working/tmp` to `.gitignore` would be a redundant line added purely to satisfy a stale
string match.

After all four: **1350 passed, 0 failed**, ruff clean.

## Finding 2 — ruff's default rule set moved materially between 0.15.x and 0.16.x

Measured on this repo, same `--isolated` invocation, same source at `d38a74a`:

| ruff | default-set findings |
|---|---|
| `0.15.5` (local dev) | 1 |
| `0.15.11` (family lock) | **1** |
| `0.16.6` (used by the sibling notify lane) | **28** — `I001` ×11, `PLW1510` ×9, `RUF059` ×4, `SIM102` ×2, `F401` ×1, `RUF100` ×1 |

This is why the sibling `nxxf`/notify lane had to narrow its selection to `E4,E7,E9,F`.
Pinning to **0.15.11** — the version `amplifier-bundle-context-intelligence/uv.lock` locks —
made a *narrowing unnecessary*: the **full default rule set** is clean at that pin after the one
`F401` fix. Pinned tool + `--isolated` + full default set means the gate cannot drift red
without an edit to `ci.yml`.

**Consequence for whoever bumps ruff here later:** a bump to 0.16.x is not a no-op; it is 28
findings of opinion-tier work. That is a deliberate, visible decision rather than a surprise.

## Finding 3 — `graphviz` is a real dependency of this suite, and its absence is silent

`tests/test_dot_render_sh.py` guards five render assertions behind `shutil.which("dot")` and
**skips them without a marker** when the binary is absent. A CI that did not install graphviz
would show the same "1350 passed" and quietly exercise none of the render path. Both test jobs
install it via apt.

## Finding 4 (reported, not fixed) — `ruff format` is not wired, on purpose

At `d38a74a`, `ruff format --check` reports **6 files would be reformatted** (including
`tests/test_discovery_investigate_topic_recipe.py`, `tests/test_discovery_pipeline_recipe.py`,
`tests/test_discovery_synthesize_module_recipe.py`,
`tests/test_quick_discovery_pipeline_recipe.py`). Not wired, and **labelled as not wired in the
PR body** rather than quietly omitted. The repo declares no `[tool.ruff]` config at all, so
wiring the formatter would be *asserting* ruff-format as this repo's standard — an owner
decision, not a CI-wiring decision. Reformatting 6 files inside a workflow PR would also bury
the workflow in churn.

## Finding 5 (reported, not fixed) — the root declares no way to install its own test deps

The root `pyproject.toml` has no `[dependency-groups] dev` and no extras, so the 1350-test suite
has no declared install path. The workflow names `pytest pyyaml pydot networkx` explicitly, with
a comment saying why. Raised as follow-up #1 in the PR body; not taken here, because a packaging
change does not belong in a workflow PR.

---

## Goal defect — the claim could not be taken, by construction

`work_claim(project="model_performance", item_id="model_performance-j1e6")` was called first, per
Procedure 1, and was **refused**:

```
claim model_performance-j1e6 as 'agent-spark-1-1101453' failed:
  Error claiming model_performance-j1e6: issue already claimed by agent-spark-1-1101253
```

The holder (`pid 1101253`, elapsed 44 s at that moment) is a **live sibling lane started ~200 PIDs
before this one** — i.e. the concurrent batch this lane is part of, not a stale hold.

This is not a blocker; it is a **conflict between the goal's Procedure 1 and the item's own
design**, and the item is the authoritative spec (GOAL.md §Procedure 1 says so explicitly). The
item description opens with:

> FILED AS ONE ITEM WITH MANY LANES, not one item per repo. […] Same here: one lane per repo,
> one PR per repo, all against this item.

A work-tracker claim is a mutex over **one** item. Nineteen lanes cannot each hold it. Procedure 1's
"if the claim is refused, write BLOCKED.md and stop" would therefore BLOCK **18 of the 19 repo
lanes at second zero** and deliver CI for exactly one repo — the precise opposite of the owner
directive the item quotes ("*let's add CI to the ones that are missing them*").

**Choice made, recorded here per SCOPE-OUTS ("No waiting on any human decision: choose, record the
choice, continue"):** the work was done. The deliverable for this repo is fully reachable, costs
$0, and is what the owner asked for. What could not be done is the *bookkeeping verb* —
`work_resolve` requires holding the item.

**Recommended fix to the goal template** (for the manager, not for this lane): a multi-lane item
needs either (a) a per-repo child item each lane can claim, or (b) an explicit Procedure-1 clause
saying "a refused claim on a known multi-lane item is expected — proceed and report", so the
refusal is not miscoded as OUTCOME branch C. Option (a) is better: it also makes per-repo progress
visible in `work_status`, which one shared item cannot show.

---

## Spend

**$0.00 API / DTU / container.** GitHub Actions minutes only: 2 workflow runs × 6 short
`ubuntu-latest` jobs.

**Cap arithmetic, checked on first read as the authoring rule requires.** The goal states
`0 runs x 0 arms x $0 / 1.00 = $0.00`, slack `$0.00`. The arithmetic **closes**: this deliverable
buys no measurement runs, so its run-count term is genuinely zero and no per-run price needs to be
quoted. No residue, because there is nothing to spend on. This is *not* the 1ru failure mode (a
run-buying deliverable funded at a price quoted for a smaller run count) — there is no purchase to
size.

**No infrastructure created**, so nothing was registered in the infra ledger and nothing needed
teardown. `infra_ledger.sh ... sweep` was never run.

---

## Deviations

1. **The PR is not workflow-only.** It carries `ci.yml` plus four named test/lint fix commits plus
   this note. Mandated, not chosen: clean main is red, and the goal's deliverable line says
   "*fix them as separate named commits — never by weakening the workflow*" (the `b4xs`
   precedent). The workflow itself is one commit, `df50f19`, reviewable in isolation.
2. **This note is committed inside the repo**, at `docs/lanes/j1e6-ci-dot-graph/DONE-NOTE.md`, per
   artifact-path/v1 — alongside the prior lane's `docs/lanes/kp79-catalog-dot-graph/`. The repo-root
   `DONE-NOTE.md` was never created or touched (item kez).
3. **Item not resolved** — see *Goal defect* above. The lane holds no item to resolve.
