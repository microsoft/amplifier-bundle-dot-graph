# cb58 — DONE NOTE

**LANDING STAGE: this lane is done at the draft PR.** The lane may not merge.
Fail-before / pass-after is demonstrated below; the merge is the manager's next
stage.

Work item: `model_performance-cb58`
Branch: `lane/cb58-dot-graph-catalog-reduction` from `origin/main` @ `8f50273`
Spend: **$0.00** of a $0.00 authority. No model calls. Local reads, byte counts,
real `load_skill` probes, and the repo test suite only.

---

## Deliverables

| Deliverable | State |
|---|---|
| Exactly 2 always-visible `dot-*` skills, each naming its absorbed L3 topics | **DONE** — `dot-authoring`, `dot-analysis`; model-visible dot entries 7 → 2 |
| Every folded name resolves per the stated alias/stub decision | **DONE** — all 7 resolve; mechanism = redirect stub; verified in-process and end-to-end through the CLI |
| Before/after visibility-block render on the owner's real app list | **DONE** — both counts quoted; `settings.yaml` md5 `028a195c52bb1a0c81be88c5ed9253f5` unchanged |
| Nothing deleted — every original body survives as an L3 file | **DONE** — 7 git-detected 100% renames into `skills/<hub>/reference/` |
| Anything already compliant left unedited and named | **DONE** — see MEASUREMENTS.md §6 |
| Fold `bundle-to-dot` | **NOT-POSSIBLE** — it is not in this repository; it ships from amplifier-foundation, and the lane may not touch other repos |

## Fail-before / pass-after

`tests/test_skills_catalog.py` is the new pin on the consolidated catalog.

- **Before** — the file was copied into a clean worktree at branch point
  `8f50273` and run there: **34 failed, 1 passed**. The headline failure:

  ```
  test_exactly_two_model_visible_skills
  AssertionError: Expected exactly ['dot-analysis', 'dot-authoring'] model-visible
  skills, got ['architecture-overview-diagram', 'dot-as-analysis',
  'dot-graph-intelligence', 'dot-patterns', 'dot-quality', 'dot-syntax',
  'parallax-investigation']
  ```

  (The single pre-existing pass is `test_reference_files_are_not_rediscovered_as_skills`,
  vacuous before the `reference/` directories exist.)
- **After**: **35 passed, 0 failed** in that file — old-name resolution for all 7,
  L3-body survival for all 7, and untruncated rendering of both hub descriptions.

Full suite: **1300 passed / 11 failed** at the branch point → **1343 passed / 11
failed** now. The same 11 pre-existing failures, unrelated to this lane
(`test_bundle_md` version, `test_dot_core_behavior` and
`test_dot_discovery_behavior` context keys, `test_gitignore` `ai_working/tmp`).
**Zero new failures.**

## Headline numbers

- Load counts, trailing 30 days, 1,746 event files carrying the `skill:loaded`
  marker out of 313 GB scanned: **6 of the 7 skills in this repo have ZERO loads**;
  `parallax-investigation` has 1. Adding foundation's `bundle-to-dot` (also 0),
  the program's "6 of 8" is really **7 of 8**.
- Visibility block: model-visible entries **69 → 64**; dot-* model-visible
  **7 → 2**; block **11,658 → 12,188 chars** (**+530, +4.5%**) because the
  user-invoked section that now carries the 7 stubs is not token-budgeted.
- The removal variant measures **11,655 chars** (3 below baseline) but breaks four
  cross-bundle references and the `/architecture-overview-diagram` command. The
  recommendation and the one-commit path to switch are in MEASUREMENTS.md §4.

## For the reviewer

The one judgement call worth a second opinion: **stubs vs outright removal.** I
shipped stubs and disclosed their +530-char always-on cost. See MEASUREMENTS.md §4
for the numbers on both, and for exactly what to delete if you want the floor.

**Merge-order note for the manager.** A sibling lane, `lane/kp79-catalog-dot-graph`,
has a worktree on this same repository. It was not inspected and nothing here
touches it, but if it also edits `skills/`, `tests/test_final_verification.py`, or
`context/dot-awareness.md`, these two branches will conflict — sequence them rather
than merging in parallel.
