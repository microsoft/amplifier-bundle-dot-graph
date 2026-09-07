# cb58 — skills catalog reduction: measurements

Work item `model_performance-cb58`. Branch `lane/cb58-dot-graph-catalog-reduction`,
branch point `8f50273`. Spend authority **$0**; every number below is a local
measurement, no model calls.

---

## 1. The repo has 7 skills, not 8 — `bundle-to-dot` is not here

Verified first, as the task required, rather than taken from the program's list.

```
$ find skills -type f -name SKILL.md   # at branch point 8f50273
skills/architecture-overview-diagram/SKILL.md
skills/dot-as-analysis/SKILL.md
skills/dot-graph-intelligence/SKILL.md
skills/dot-patterns/SKILL.md
skills/dot-quality/SKILL.md
skills/dot-syntax/SKILL.md
skills/parallax-investigation/SKILL.md
```

`bundle-to-dot` ships from **amplifier-foundation**
(`~/.amplifier/cache/amplifier-foundation-*/skills/bundle-to-dot`), not from this
repository. The lane charter forbids touching other repos, so folding it is
recorded **NOT-POSSIBLE (out of scope for this lane)**. It remains a valid
follow-up against amplifier-foundation.

Consequence for the grouping: `dot-authoring` absorbs **three** topics
(dot-syntax, dot-patterns, dot-quality) rather than the four the program assumed.
`dot-analysis` absorbs all four it was assigned.

## 2. Re-measured load counts — 6 of 7 have zero loads in 30 days

Method: every `skill:loaded` event is emitted by `tool-skills` on **every**
successful `load_skill(skill_name=...)` (`amplifier_module_tool_skills/__init__.py`,
the emit at the end of the load path), so it is an exact marker, not a proxy.

- Window: files under `~/.amplifier/projects/**` named `events.jsonl` or
  `root_events.jsonl`, `-mtime -30`, **excluding** `context-intelligence/`
  duplicates (per the program's own de-duplication rule).
- Corpus: **25,977** event files in window → **11,352** after de-duplication →
  **313.0 GB** → **1,746** files actually carrying the `skill:loaded` marker.
- Totals in window: **3,350** load events across **85** distinct skills.

| Skill | Loads (30d) | Distinct sessions |
|---|---|---|
| dot-syntax | **0** | 0 |
| dot-patterns | **0** | 0 |
| dot-quality | **0** | 0 |
| dot-graph-intelligence | **0** | 0 |
| dot-as-analysis | **0** | 0 |
| architecture-overview-diagram | **0** | 0 |
| parallax-investigation | 1 | 1 |
| *bundle-to-dot (foundation, out of scope)* | **0** | 0 |

For scale, the busiest skills in the same window: `restless-old-brian` 1255,
`context-intelligence-graph-query` 198, `intent-keeper` 149, `user-advocate` 145,
`cranky-old-sam` 115.

**Verdict on the program's claim.** The program said "6 of 8 have zero loads."
Measured on this branch: **6 of the 7 skills in this repo** are zero-load, and the
8th name it counted (`bundle-to-dot`, in another repo) is *also* zero-load — so
across the program's own 8, the true figure is **7 of 8 zero-load**, one more than
assumed. The single non-zero skill, `parallax-investigation` (1 load), was already
assigned to `dot-analysis`. **The measured zero-load set does not change the
grouping**, so the program's grouping is kept, minus `bundle-to-dot`.

## 3. Alias/stub decision — VERIFIED, not assumed

### What the loader actually supports

Read from the shipped `tool-skills` module, then tested:

- Skill identity is the **frontmatter `name`**, not the directory name. A
  directory-name mismatch is a warning, not a rejection (`discovery.py`).
- Discovery is a **recursive** `os.walk` for files literally named `SKILL.md`.
  L3 reference files must therefore *not* be named `SKILL.md` — pinned by
  `tests/test_skills_catalog.py::test_reference_files_are_not_rediscovered_as_skills`.
- There is **no alias field** and **no "hidden" flag**. `shortcut:` only aliases a
  slash command. Every discovered skill renders in the visibility block; the only
  control is *which section*: `disable-model-invocation: true` moves a skill out of
  the model-facing "Available skills" index into "User-invoked skills"
  (`hooks.py::_format_skills_list`).

So the only mechanism that keeps an old name resolving is a **real SKILL.md stub at
the old path carrying the old `name`**. That is what shipped.

### Mechanism chosen

**Alias/stub — all 7 old names still resolve.** Each original directory keeps a
`SKILL.md` with its original `name`, `disable-model-invocation: true`, and a body
that points at the L3 file. `architecture-overview-diagram` additionally keeps
`user-invocable: true`, plus its `allowed-tools` and `model_role`, so the
`/architecture-overview-diagram` command survives.

Why not remove outright: the names are referenced **outside this repo**.
`amplifier-bundle-skills`' own `amplifier-tool-leverage-patterns` skill cites
`dot-patterns` / `dot-syntax` by name, and two `amplifier-bundle-attractor` design
docs cite `dot-syntax`/`dot-patterns`/`dot-quality`/`dot-graph-intelligence`.

### Test results, quoted

**(a) In-process, real `SkillsTool`, against this branch's `skills/`:**

```
dot-syntax                       success=True  | # dot-syntax (folded) ...
dot-patterns                     success=True  | # dot-patterns (folded) ...
dot-quality                      success=True  | # dot-quality (folded) ...
dot-graph-intelligence           success=True  | # dot-graph-intelligence (folded) ...
dot-as-analysis                  success=True  | # dot-as-analysis (folded) ...
parallax-investigation           success=True  | # parallax-investigation (folded) ...
architecture-overview-diagram    success=True  | # Architecture Overview Diagram (folded) ...
dot-authoring                    success=True  | # DOT Authoring ...
dot-analysis                     success=True  | # DOT Analysis ...
```

Negative control:

```
NEGATIVE CONTROL success: False
error: {'message': "Skill 'dot-nonexistent-control' not found. Available:
 architecture-overview-diagram, dot-analysis, dot-as-analysis, dot-authoring,
 dot-graph-intelligence, dot-patterns, dot-quality, dot-syntax,
 parallax-investigation"}
```

**(b) End-to-end through the real CLI**, with this branch's `skills/` staged into
the mounted bundle cache and restored immediately afterwards
(cache verified back to its original 7 directories; owner `settings.yaml`
untouched):

```
$ amplifier tool invoke load_skill skill_name=dot-syntax
Result from load_skill:
  {'content': '# dot-syntax\n\n# dot-syntax (folded)\n\n`dot-syntax` is now a
   reference file inside the **dot-authoring** skill. ...',
   'skill_name': 'dot-syntax',
   'skill_directory': '.../skills/dot-syntax',
   'loaded_from': '.../amplifier-bundle-dot-graph-43d42df775a679a7/skills'}

$ amplifier tool invoke load_skill skill_name=dot-authoring
Result from load_skill:
  {'content': '# dot-authoring\n\n# DOT Authoring\n\nOne entry point for writing
   DOT/Graphviz by hand. ...'}

$ amplifier tool invoke load_skill list=true
after_catalog_count = 86      (before: 84)
```

## 4. Before/after `hooks-skills-visibility` render

Owner's real app list, owner's `settings.yaml` **untouched** — md5
`028a195c52bb1a0c81be88c5ed9253f5` at the start of the lane and again after every
probe.

Method: the catalog *names* come from a scratch session
(`amplifier tool invoke load_skill list=true`, run in `/tmp`, no LLM call);
metadata for those names is recovered by running the shipped `discover_skills`
over every mounted skills root; the block itself is produced by the shipped
`SkillsVisibilityHook._format_skills_list`. No renderer was reimplemented.

| | skills | **model-visible entries** | user-invoked entries | block chars | est. tokens | dot-* model-visible |
|---|---|---|---|---|---|---|
| **before** | 80 | **69** | 11 | 11,658 | 2,914 | 7 |
| **after (shipped — stubs)** | 82 | **64** | 18 | 12,188 | 3,047 | **2** |
| after (variant — removal) | 75 | 64 | 11 | 11,655 | 2,913 | 2 |

Rendered dot lines, after:

```
Available skills (use load_skill tool):
- **dot-analysis**: Use when a diagram is the analysis instrument, not the output — absorbs dot-graph-intelligence, dot-as-analysis, parallax-investigation, architecture-overview-diagram.
- **dot-authoring**: Use when writing, fixing or reviewing a DOT/Graphviz diagram — absorbs dot-syntax, dot-patterns and dot-quality (syntax lookup, templates, the title/legend law, quality gate).

User-invoked skills (available via /command):
- **architecture-overview-diagram**: Folded into dot-analysis — still runnable as /architecture-overview-diagram.
- **dot-as-analysis**: Folded into dot-analysis — load that instead.
- **dot-graph-intelligence**: Folded into dot-analysis — load that instead.
- **dot-patterns**: Folded into dot-authoring — load that instead.
- **dot-quality**: Folded into dot-authoring — load that instead.
- **dot-syntax**: Folded into dot-authoring — load that instead.
- **parallax-investigation**: Folded into dot-analysis — load that instead.
```

Both hub lines render **untruncated** — pinned by
`test_hub_description_renders_untruncated`, because the hook clips every line at
180 characters and a longer description would silently drop the absorbed-topic
names the catalog exists to advertise.

### The honest finding: this does not shrink the block

The "Available skills" section is **token-budgeted** (default 2,500 est. tokens,
`hooks.py`). Dropping the model-visible count 69 → 64 does **not** shrink it — the
freed budget is redistributed as more detail for the skills that remain. What the
fold actually buys is a **model-facing dot-* catalog of 2 entries instead of 7**,
and five slots of budget returned to other skills.

The "User-invoked skills" section is **not** budgeted — only the per-line character
cap bounds it. So the 7 stubs **add 530 chars (~133 est. tokens, +4.5%)** to the
always-on block. That cost is real and is disclosed rather than buried.

It is small in practice because the index is rendered at
`visibility.placement="prefix"` — it rides the cached system prefix and is
re-billed only when the catalog changes, not per request.

**Recommendation (mine, for review):** keep the stubs. The 530 chars sit in a
cached prefix; against that, removal would silently break four cross-bundle
references and the `/architecture-overview-diagram` command, and would turn a
redirect that *teaches the new name* into a bare "not found". If the reviewer
prefers the absolute floor, the removal variant is one commit — delete the six
non-user-invocable stub directories and drop the corresponding rows from `FOLDED`
in `tests/test_skills_catalog.py`; the measured block then lands at 11,655 chars,
3 chars **below** baseline.

### Known limitation of this measurement

4 of the 84 names the scratch session reported (`amplifier-config`, `goal-batch`,
`goalify`, `ten-lane-highway`) could not be located on disk by the reconstruction,
so the rendered block covers 80 of 84 skills. The gap is identical in the before
and after columns, so every delta above is unaffected.

## 5. Test suite

Baseline at branch point `8f50273`: **1300 passed, 11 failed**. The 11 are
pre-existing and unrelated (`test_bundle_md` version, `test_dot_core_behavior` /
`test_dot_discovery_behavior` context keys, `test_gitignore` `ai_working/tmp`).

After this change: **1343 passed, 11 failed** — the same 11, **zero new
failures**, +43 passing tests.

## 6. Already compliant, left unedited

- `context/discovery-overview-synthesizer-instructions.md` — references the
  `dot-quality` standard by name; that name still resolves via its stub, so the
  file is correct as written and was not touched.
- `agents/`, `recipes/`, `README.md` — carry no `skills/` paths and no skill-name
  references; unchanged.
- `behaviors/dot-core.yaml` — points `tool-skills` at the repo's `skills/`
  directory as a whole; the new layout needs no config change, so it is unchanged.
