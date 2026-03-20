# Level Synthesis: `amplifier/recipes/`

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/recipes`
**Fidelity tier:** standard
**Synthesized:** 2026-03-20

---

## Files and Symbols at This Level

This directory is flat — all 6 entries are YAML recipe files with no subdirectories. There is no `__init__.py`, registry module, or index file at this level. Each recipe is a standalone workflow definition loadable directly by the Amplifier recipe engine.

| File | Name (internal) | Version | Size | Lines | Role |
|------|----------------|---------|------|-------|------|
| `amplifier-ecosystem-audit.yaml` | `amplifier-ecosystem-audit` | 1.2.0 | 21.8 KB | 590 | Orchestrator: audits all amplifier repos in MS org |
| `repo-audit.yaml` | `repo-audit` | 1.2.0 | 34.9 KB | 903 | Leaf: audits a single repo for compliance |
| `ecosystem-activity-report.yaml` | `ecosystem-activity-report` | 1.15.2 | 63.0 KB | 1487 | Orchestrator: reports activity across ecosystem |
| `repo-activity-analysis.yaml` | `repo-activity-analysis` | 3.1.0 | 49.5 KB | 1189 | Leaf: analyzes git activity in a single repo |
| `outline-generation-from-doc.yaml` | `outline-generation-from-document` | 1.6.1 | 91.7 KB | 2277 | Producer: generates structured outlines from docs |
| `document-generation.yaml` | `document-generation` | 8.1.0 | 126.4 KB | 3021 | Consumer: generates documents from outlines |

---

## Cross-File Connections

### Connection 1: `amplifier-ecosystem-audit` → `repo-audit` (direct sub-recipe invocation)

**Type:** `type: "recipe"` step in a foreach loop  
**Location:** `amplifier-ecosystem-audit.yaml` lines 351–352  
**Mechanism:** After discovering all Amplifier repositories in the Microsoft GitHub org, the orchestrator fans out to `repo-audit.yaml` once per repo via:

```yaml
type: "recipe"
recipe: "amplifier/recipes/repo-audit.yaml"
```

**Context passed:** `repo_owner`, `repo_name`, `create_fix_pr`, `dry_run`, `working_dir`  
**Pattern:** The orchestrator handles discovery, rate limiting (`max_concurrent_llm: 3`, `min_delay_ms: 500`), and final report synthesis. The leaf handles all single-repo compliance checks.

---

### Connection 2: `ecosystem-activity-report` → `repo-activity-analysis` (direct sub-recipe invocation)

**Type:** `type: "recipe"` step in a foreach loop  
**Location:** `ecosystem-activity-report.yaml` lines 804–805  
**Mechanism:**

```yaml
type: "recipe"
recipe: "./repo-activity-analysis.yaml"
```

**Context passed:** `repo_url`, `date_range`, `date_start`, `date_end`, `github_user`, `working_dir`  
**Optimization note:** The orchestrator explicitly pre-computes `date_start`, `date_end`, and `github_user` and passes them to the sub-recipe to skip redundant LLM calls inside `repo-activity-analysis` (comment: "eliminates 12 redundant LLM calls"). This is a deliberate performance contract between these two recipes.  
**Rate limiting:** `max_concurrent_llm: 1`, `min_delay_ms: 3000` (v1.13.0 reduced to sequential for reliability).

---

### Connection 3: `outline-generation-from-doc` → `document-generation` (file-based data pipeline)

**Type:** File handoff (not a direct recipe invocation)  
**Mechanism:** `outline-generation-from-doc` writes structured outline files to `output_dir: "./outlines"` as both YAML and JSON. `document-generation` consumes them via `outline_path=./outline.json`.  
**Evidence:** `document-generation.yaml` changelog (line 216): *"Improvements from outline-generation recipe patterns (v6.0.1)"* — the two were developed together and share design lineage.  
**Directionality:** outline-generation is upstream; document-generation is downstream. The caller must execute outline-generation first, then pass its output path to document-generation.

---

### Connection 4: Shared agent vocabulary (cross-recipe)

All agent invocations across the 6 recipes:

| Agent | Used In |
|-------|---------|
| `foundation:zen-architect` | repo-audit, ecosystem-activity-report, document-generation, outline-generation-from-doc |
| `foundation:explorer` | ecosystem-activity-report, document-generation, outline-generation-from-doc |
| `foundation:modular-builder` | repo-audit |
| `foundation:file-ops` | ecosystem-activity-report |
| `design-intelligence:voice-strategist` | document-generation |
| `design-intelligence:layout-architect` | document-generation |

`foundation:zen-architect` is the universal synthesis agent — it appears in 4 of 6 recipes for reasoning-heavy steps (report generation, analysis, doc writing). `foundation:explorer` appears in 3 recipes for content discovery steps.

---

### Connection 5: Shared GitHub CLI dependency cluster

4 of 6 recipes share a hard dependency on the `gh` CLI and a common interaction pattern with the GitHub API:

- `amplifier-ecosystem-audit.yaml` — GitHub Search API + repo discovery
- `repo-audit.yaml` — `gh repo view`, `gh api`, file fetching via `gh`
- `ecosystem-activity-report.yaml` — `gh api` for commits/PRs
- `repo-activity-analysis.yaml` — `gh api` for commits/PRs with pagination

`document-generation.yaml` and `outline-generation-from-doc.yaml` are entirely GitHub-independent (they work on local files and cloned repos via git).

---

### Connection 6: Shared infrastructure conventions

Across all 6 recipes:

| Convention | Recipes Using It |
|------------|-----------------|
| `working_dir` context variable (intermediate file staging) | All 6 |
| `recursion` block with `max_depth` / `max_total_steps` | All 6 (implied or explicit) |
| `retry` with exponential backoff | repo-audit, repo-activity-analysis, amplifier-ecosystem-audit, ecosystem-activity-report, document-generation |
| `rate_limiting` block (LLM concurrency + delay) | amplifier-ecosystem-audit, ecosystem-activity-report |
| Model tiering (haiku → sonnet → opus by task complexity) | repo-activity-analysis, ecosystem-activity-report, document-generation |
| `parse_json: true` on bash steps | amplifier-ecosystem-audit, ecosystem-activity-report |
| `on_error: "continue"` vs `"fail"` distinction | repo-audit, ecosystem-activity-report, repo-activity-analysis |
| `ai_working/` as conventional output sub-directory | All 4 GitHub recipes |

---

## Boundary Patterns

### Pattern 1: Orchestrator–Leaf Pair (two instances)

The dominant structural pattern in this directory. Two complete pairs:

```
amplifier-ecosystem-audit (orchestrator)
    → discovers repos
    → foreach: invokes repo-audit per repo (type: "recipe")
    → synthesizes final report

ecosystem-activity-report (orchestrator)
    → discovers repos from MODULES.md
    → foreach: invokes repo-activity-analysis per repo (type: "recipe")  
    → synthesizes final report
```

Both orchestrators:
- Perform discovery and filtering
- Manage rate limiting (GitHub API + LLM concurrency)
- Pass precomputed values to leaves to avoid redundant work
- Aggregate leaf outputs into a final ecosystem-level report

Both leaves:
- Accept a single repo as input
- Are independently executable (can be run directly)
- Produce structured JSON output for the orchestrator to aggregate

This is the "fan-out aggregation" recipe pattern.

---

### Pattern 2: Document Generation Pipeline (loose coupling)

```
outline-generation-from-doc
    → analyzes existing document
    → identifies sources and classifies directionality
    → produces ./outlines/*.yaml + ./outlines/*.json

document-generation (separate execution, reads outline_path)
    → BFS section generation
    → parallel validation (structural → content → quality)
    → produces final document
```

These two recipes form a two-stage documentation pipeline. The coupling is loose (file handoff, not recipe invocation), meaning they can be used independently or together. The shared conceptual lineage is visible in their changelogs.

---

### Pattern 3: GitHub Ecosystem Analysis Subsystem

4 of 6 recipes form a coherent "GitHub ecosystem analysis" subsystem: two orchestrator–leaf pairs that together support:
- **Compliance auditing**: Does each repo have required files, labels, README sections?
- **Activity reporting**: What commits and PRs happened across the ecosystem?

Both subsystems share:
- `gh` CLI as the data access layer
- `ai_working/` directory convention
- Rate limiting against GitHub API and LLM providers
- `foundation:zen-architect` for synthesis steps

---

## Uncertainties for Next Level Up

1. **Are these recipes registered anywhere?** No manifest, index file, or registry exists in this directory. The parent level (`amplifier/`) or the bundle root may contain a recipe catalog or bundle.md that declares which recipes are public API.

2. **Is `outline-generation-from-doc` → `document-generation` a deliberate pipeline?** The changelog reference suggests it is, but there is no explicit invocation chain in any recipe file. A parent-level bundle definition may formalize this as a named workflow.

3. **Version alignment:** `repo-audit` and `amplifier-ecosystem-audit` share version `1.2.0` exactly. `repo-activity-analysis` (v3.1.0) and `ecosystem-activity-report` (v1.15.2) do not match. The ecosystem-audit pair appears to be co-versioned; the activity pair is not. Parent-level tooling may enforce or ignore this.

4. **Who discovers and loads these recipes?** The Amplifier recipe engine presumably discovers them by path, but the mechanism for bundle-level recipe discovery is not visible at this level.

5. **`document-generation.yaml` is by far the largest recipe (3021 lines, v8.1.0).** Its size suggests it may have diverged into a standalone product. Whether it belongs in this recipes directory or should be in its own bundle is a question for the parent level.
