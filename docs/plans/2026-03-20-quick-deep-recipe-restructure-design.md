# Quick/Deep Discovery Pipeline Restructure Design

## Goal

Restructure the dot-graph bundle's discovery recipes into two tiers — a lightweight "quick" pipeline (~30-60 min) and the full "deep" Parallax Discovery pipeline (~3+ hours) — both producing the same polished output structure but at different depths.

## Background

The discovery pipeline has gone through two generations:

- **v1** (commit 6381791): A monolithic 3-recipe pipeline with a single top-down investigation pass. Fast but shallow.
- **v2** (current): A 10-recipe Parallax Discovery pipeline running multiple strategies (top-down, bottom-up, sequential) with consensus synthesis. Thorough but slow (~3+ hours).

Users frequently need a quick architectural scan — enough to understand a repo's structure and decide whether deeper investigation is warranted. The v1 pipeline served this purpose but was replaced wholesale by v2. Restoring v1 as a "quick" tier alongside the "deep" v2 gives users the right tool for each situation.

Both pipelines already share two core sub-recipes (`investigate-topic` and `synthesize-module`), making the two-tier structure a natural fit rather than a duplication problem.

## Approach

Restore the v1 pipeline from git history as the quick tier, enhance both pipelines with polished output steps (overview.md, flat output directory), and reorganize the recipe directory so shared building blocks stay at the root while pipeline-specific recipes live in `quick/` and `deep/` subdirectories.

## Architecture

### Directory Structure

```
recipes/
  # Shared building blocks (used by both quick and deep)
  discovery-investigate-topic.yaml    # Per-topic: dispatch agents
  discovery-synthesize-module.yaml    # Per-module: consensus + quality gate

  # Quick pipeline (~30-60 min, single top-down pass)
  quick/
    discovery-pipeline.yaml           # Scan → investigate → synthesize → polish

  # Deep pipeline (~3+ hours, multi-strategy Parallax)
  deep/
    discovery-pipeline.yaml           # Scan → strategies → combine
    strategy-topdown.yaml
    strategy-bottomup.yaml
    strategy-sequential.yaml
    discovery-combine.yaml
    synthesize-level.yaml             # Bottom-up specific
    synthesize-subsystem.yaml
    synthesize-overview.yaml
```

### Cross-Reference Paths

- Shared recipes keep their current paths: `@dot-graph:recipes/discovery-investigate-topic.yaml`
- Deep recipes update to: `@dot-graph:recipes/deep/strategy-topdown.yaml`, etc.
- Quick pipeline entry point: `@dot-graph:recipes/quick/discovery-pipeline.yaml`

Deep-only sub-recipes (`synthesize-level`, `synthesize-subsystem`, `synthesize-overview`) move into `deep/` because they are exclusively used by the bottom-up and assembly stages of the deep pipeline.

## Components

### Quick Pipeline

The quick pipeline is the restored v1, enhanced with finishing steps that produce the same polished output structure as the deep pipeline.

**Stage 1: Scan** (same as v1)

- `structural-scan` — prescan the repo, write prescan-result.json
- `topic-select` — agent picks 3-5 investigation topics
- Approval gate — user reviews topics before agent dispatch

**Stage 2: Investigate** (same as v1)

- `prepare-topics` — create per-topic directories
- `investigate-topics` — foreach topic, call shared `discovery-investigate-topic.yaml` (dispatches code-tracer + integration-mapper at standard fidelity)

**Stage 3: Synthesize** (v1 + enhancements)

- `reconcile-modules` — foreach topic, call shared `discovery-synthesize-module.yaml` (consensus DOT + quality gate)
- `assemble` — run the existing `assemble.py` plumbing to merge per-module DOTs into overview
- `validate` — validate all produced DOTs
- **NEW:** `hoist-outputs` — bash step that copies each `modules/{slug}/diagram.dot` and `modules/{slug}/findings.md` to the output root, plus the overview DOT. Creates a flat `output/` directory.
- **NEW:** `summarize` — agent step that reads all `findings.md` files and produces `overview.md`. Uses the `writing` model role for quality prose.
- `update-metadata` — write `last-run.json`

The v1 pipeline at commit 6381791 includes a `change-detect` step that checks `last-run.json` and computes git diff for incremental runs. The quick pipeline preserves this optimization.

### Deep Pipeline

The deep pipeline (current v2) needs minimal structural changes — it already works. The restructuring is primarily about moving files into `deep/` and updating cross-references.

**What moves into `deep/`:**

- `discovery-pipeline.yaml`
- `strategy-topdown.yaml`
- `strategy-bottomup.yaml`
- `strategy-sequential.yaml`
- `discovery-combine.yaml`
- `synthesize-level.yaml`
- `synthesize-subsystem.yaml`
- `synthesize-overview.yaml`

**What stays at the root (shared):**

- `discovery-investigate-topic.yaml`
- `discovery-synthesize-module.yaml`

**Deep pipeline enhancements (matching quick):**

- Add `node_target` parameter (default 25) to overview synthesis
- Add `overview.md` generation step using the `discovery-architecture-writer` agent
- Add `hoist-outputs` step to create the flat `output/` directory

Both pipelines produce the same polished output structure. The deep version has richer content from running multiple strategies.

### New Agent: `discovery-architecture-writer`

- **Model role:** `writing`
- **Shared by:** both quick and deep pipelines
- **Inputs:** per-module `findings.md` files, `topics.json`, `overview.dot`
- **Output:** `overview.md`

### Output Naming Convention

Top-level output files use the `overview.*` naming convention:

- `overview.dot` + `overview.md` — consistent stem pair
- "Overview" is content-agnostic (describes abstraction level, not repo content)
- Predictable: a developer who sees `overview.dot` will guess `overview.md` exists
- Avoids path redundancy (`.discovery/output/discovery.md` would repeat "discovery")
- No UPPERCASE — that's a repo-root convention (`README.md`), not for nested directories

## Data Flow

### Output Structure (both pipelines)

```
.discovery/
  output/
    overview.md              # Polished narrative entry point with links to module details
    overview.dot             # Hoisted from assembly
    overview.svg             # Rendered
    {slug}.dot               # Hoisted per-module consensus DOTs
    {slug}.svg               # Rendered
  modules/                   # Raw investigation artifacts (preserved)
    {slug}/
      diagram.dot
      findings.md
      agents/code-tracer/...
      agents/integration-mapper/...
  topics.json
  scan_result.json
  last-run.json
```

### overview.md Contents

- Executive summary (2-3 sentences on what was discovered)
- Repo overview (what this codebase is — derived from investigation, not assumed)
- For each module: a paragraph summary with a relative link to the detailed `findings.md`
- Key patterns and cross-cutting insights
- Open questions

Links use relative paths to `../modules/{slug}/findings.md` for per-module detail.

## Overview DOT — Node Target with Value-Driven Allocation

The overview DOT receives a configurable `node_target` context variable (default: 25). The synthesizer agent should:

- **Strive to reach** the target — don't produce a 5-node overview when 25 would be richer
- **Strive to stay near** the target — don't produce 60 nodes when 25 was asked for
- **Not treat it as a hard limit** — a simple repo might naturally be 12 nodes and that's fine; a complex one might justify 30

### Value-Driven Allocation

The agent decides how to spend its node budget based on architectural significance, not even distribution. A concept that's most complex or most interesting gets more depth. A concept that's genuinely simple stays simple.

### Adaptive Graph Structure Based on Repo Character

- **Focused repo** (single main idea): One graph with more internal depth. Most nodes go toward depth of that single idea. The overview essentially IS the detailed view.
- **Medium repo** (3-5 main ideas): Subgraph clusters per idea with internal structure proportional to significance — not size.
- **Broad repo** (many ideas): More clusters, less depth per cluster, but still mini-graphs not single boxes.

### Key Rule

Every top-level concept should be represented by enough structure to understand what it does when scanning across many repos. A single unlabeled box is never enough. But "enough" varies — for a trivial utility it might be 2 nodes, for a complex subsystem it might be 8.

### Example — Right Level

```dot
subgraph cluster_auth {
  label="Authentication"
  oauth [label="OAuth2 Provider"]
  tokens [label="Token Manager"]
  sessions [label="Session Store"]
  oauth -> tokens -> sessions
}

subgraph cluster_api {
  label="API Layer"
  router [label="Request Router"]
  middleware [label="Auth Middleware"]
  handlers [label="Endpoint Handlers"]
  router -> middleware -> handlers
}

auth_sessions -> api_middleware [label="validates"]
```

### Implementation

This is a prompt instruction to the overview synthesizer agent. The `node_target` is passed as a context variable from the pipeline (default 25, configurable via CLI context).

## Error Handling

Both pipelines inherit existing error handling from v1/v2:

- Quality gates on synthesized DOTs (validation step rejects malformed output)
- Approval gates before expensive agent dispatch (user reviews selected topics)
- `last-run.json` metadata enables incremental re-runs if a pipeline fails partway through
- The `change-detect` step (quick pipeline) skips re-investigation of unchanged modules

## Testing Strategy

- **Quick pipeline smoke test:** Run against a small known repo, verify the output structure is produced with all expected files (`overview.md`, `overview.dot`, per-module DOTs, `last-run.json`)
- **Deep pipeline regression:** Verify the deep pipeline still produces correct output after the file moves and cross-reference updates
- **Shared sub-recipe isolation:** Confirm `discovery-investigate-topic.yaml` and `discovery-synthesize-module.yaml` work when called from both `quick/` and `deep/` parent recipes
- **Node target validation:** Run the overview synthesizer with different `node_target` values (10, 25, 40) and verify the output scales appropriately
- **Output structure parity:** Confirm both pipelines produce the same `output/` directory structure (same file names, same layout) — only content depth differs

## Open Questions

1. **CLI node_target override:** Should the quick pipeline support a `node_target` override from the CLI context? (Proposed: yes, default 25)
2. **Deep combine overview.md:** Should the deep pipeline's combine step also produce an `overview.md`, or only the individual strategy outputs? (Proposed: yes, the combine step produces the final `overview.md`)
3. **Incremental change-detect:** The v1 pipeline at commit 6381791 has a `change-detect` step that checks `last-run.json` and computes git diff for incremental runs. Should the quick pipeline preserve this? (Proposed: yes, it's a useful optimization)
