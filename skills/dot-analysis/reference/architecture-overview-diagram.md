---
name: architecture-overview-diagram
description: >
  Generate a README-level architecture overview DOT diagram for a repository
  through code-first investigation, iterative design, and antagonistic review.
  Use when the user says "create an architecture diagram", "make a README
  diagram", "top-level overview diagram", or wants a single diagram that
  gives a non-technical reader the "I get it" understanding of a system.
  Produces a .dot source, .svg, and .png — reviewed to PASS quality.
  Also surfaces doc/code discrepancies and optionally generates detail diagrams.
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

# Architecture Overview Diagram

Generate a single, README-level architecture overview diagram for a repository.
The diagram should give a non-technical reader an instant "I get it" understanding
of what the system does, how it works, and what value it provides — from the
diagram alone, without reading any docs.

The process is code-first: read the actual source code, not documentation, to
determine what the system really does. Then iterate the diagram design with user
feedback and antagonistic review until it passes quality gates.

This skill commonly surfaces doc/code discrepancies, dead code, and stale
artifacts as a side effect of the investigation. Those findings should be
presented to the user for cleanup alongside the diagram work.

## Inputs

- `<repo_path>`: Path to the repository to diagram.
- `<reference_diagram>`: (Optional) Path to a gold-standard diagram to use as a
  style/structure reference. If this repo is part of an ecosystem with sibling
  repos that already have overview diagrams, use those as implicit references
  for visual consistency — even if the user doesn't explicitly provide one.

## Steps

### 1. Deep Code Investigation

Launch parallel agents to read the actual source code and build a ground-truth
understanding of the system architecture. Do NOT read documentation first — code
is the source of truth.

**Execution**: Delegate to `foundation:explorer` (2-3 parallel instances with
different scopes) and `python-dev:code-intel` or `rust-dev:code-intel` for
semantic call-graph tracing.

Investigation targets:
- Entry points (CLI, API, main)
- Core data flows (what goes in, what comes out)
- Component boundaries (what are the major subsystems)
- External dependencies (what does it call out to)
- User-facing interaction patterns (how do humans interact)
- Safety/enforcement mechanisms
- Plugin/extension points
- Awareness boundaries (what should this repo know about, what shouldn't it?)

**Success criteria**: A complete mental model of what the system does, its
components, data flows, external dependencies, and user-facing behaviors —
all derived from source code with file:line citations.

### 2. Catalog Existing Documentation

In parallel with Step 1, catalog all existing docs and diagrams in the repo.

**Execution**: Delegate to `foundation:explorer` (separate instance,
`context_depth="none"`).

Find:
- All `.dot`, `.svg`, `.png` diagram files
- All architecture/design docs
- README claims about system structure
- Any discrepancies between docs and code (note these for later)
- Stale artifacts, dead code, duplicate files, awareness boundary violations

**Artifacts**: Compile a cleanup backlog of doc/code discrepancies, stale
references, and other issues found. Present this to the user alongside the
diagram work — the investigation commonly surfaces significant cleanup needs.

**Success criteria**: Complete inventory of existing documentation with
accuracy assessment against code findings from Step 1, plus a cleanup
backlog for the user to review.

### 3. Analyze Reference Diagram (if provided or available)

If a gold-standard reference diagram was provided, OR if sibling repos in the
same ecosystem already have overview diagrams, analyze their design principles
to guide our diagram's style and structure.

**Execution**: Delegate to `design-intelligence:design-system-architect`
with the reference diagram.

Extract:
- Node count, edge density, cluster strategy
- Color system and shape vocabulary
- Information hierarchy (how it guides the eye)
- Text density per node and edge
- What makes it work as an "I get it" overview
- Concrete design principles to follow

**Rules**: When working within an ecosystem of repos, visual consistency
matters. If sibling repos use specific color palettes, shape vocabularies,
or cluster patterns, match them — the diagrams should look like a family.
If the system has an underlying DSL with defined shape semantics (e.g. a
pipeline DSL where hexagon=human gate), the overview diagrams should use
those same shapes — don't introduce conflicting meanings at different
documentation layers.

**Success criteria**: A numbered list of design principles extracted from the
reference, ready to apply to our diagram.

### 4. Design the Value Story

Before creating any DOT, define what story the diagram tells. This is the most
important step — a diagram without a clear story is just boxes and arrows.

Answer these questions:
- What is the one-sentence value proposition? ("You provide X, the system does Y,
  you get Z")
- What are the INPUTS from the user's perspective?
- What is the PROCESSING at the right abstraction level?
- What are the OUTPUTS the user cares about?
- What external dependencies need to be shown?
- What should be EXCLUDED (too detailed for this level)?
- What is the distinctive feature that makes this system different?

Present the story to the user for feedback before proceeding.

**Rules**:
- Do NOT name specific plugin implementations — show the plugin concept generically
- Do NOT name specific frontend applications — show the interface concept generically
- DO name real ecosystem dependencies that all users will encounter
- DO show safety/enforcement mechanisms if they exist
- DO show bidirectional interactions (human-in-the-loop, feedback channels)
- Respect awareness boundaries — the repo should only reference its direct deps

**Success criteria**: User confirms the story and scope before diagram creation.

**Human checkpoint**: Present the story framing and get explicit approval.

### 5. Create Initial DOT Diagram

Generate the DOT source following these hard constraints:

- **≤20 nodes** (target 12-17 for overview)
- **Edge-to-node ratio ≤ 1.5:1**
- **Maximum cluster nesting depth = 2**
- **Pure DAG** (top-to-bottom flow, feedback loops use `constraint=false`)
- **≤3 node shapes** plus special shapes for gates/safety (note=data,
  rounded-box=process, folder=external, hexagon=human-gate, octagon=safety).
  If the system has an underlying DSL with its own shape vocabulary (e.g. the
  attractor pipeline DSL), align overview shapes with that vocabulary — don't
  introduce shape meanings in the overview that conflict with the DSL layer.
- **≤6 semantic fill colors**, all pastel (~90% lightness)
- **Cluster border color matches node fill family**
- **Node labels: ≤3 lines**, name what it IS not what it DOES
- **Edge labels: verb phrases, ≤3 words**
- **Dashed = external/swappable/planned, solid = core/implemented**
- **All edges labeled** with verb phrases

**Execution**: Delegate to `dot-graph:dot-author` with the complete design
specification from Step 4 and the design principles from Step 3.

Render to `.svg` and `.png` alongside the `.dot` source.

**Success criteria**: A valid, rendered DOT diagram that follows all constraints.

### 6. Present to User for Feedback

Show the rendered diagram to the user. Ask for specific feedback:
- Does the story come through?
- Is anything missing that's important?
- Is anything shown that's too detailed?
- Do the labels make sense?

Iterate Steps 5-6 as needed based on feedback. Expect 2-4 iterations.

**Success criteria**: User says the direction is right.

**Human checkpoint**: User reviews and provides feedback each iteration.

### 7. Hunt for Missing Mechanisms

Before the antagonistic review, proactively search for important mechanisms
that the diagram does NOT yet show. Send fresh agents to read the code with
the specific question: "what user-facing capabilities exist that aren't in
this diagram?"

**Execution**: Delegate to `foundation:explorer` (fresh, `context_depth="none"`)
and `resolve:resolve-expert` or domain-appropriate expert agents. Give them
the current diagram's node list and ask them to find what's missing.

Rate each finding: CRITICAL (users need to know), IMPORTANT (valuable but
detail-level), or IMPLEMENTATION (skip for overview).

Present the findings to the user for decision on what to add.

**Success criteria**: User confirms which missing mechanisms to add (if any).

**Human checkpoint**: Present missing mechanism candidates and get approval.

### 8. Antagonistic Review

Launch parallel antagonistic reviews from three different perspectives:

**8a. Fresh code audit** — Delegate to `foundation:explorer` with
`context_depth="none"` and `model_role="critique"`. Give it the diagram's
claims and ask it to verify each against the actual source code. For each
claim: ACCURATE, INACCURATE, or PARTIALLY ACCURATE with file:line evidence.

**8b. Diagram quality review** — Delegate to `dot-graph:diagram-reviewer`.
Get a structured PASS/WARN/FAIL verdict covering syntax, structure, color
consistency, edge labels, readability, and comparison to reference.

**8c. Design critique** — Delegate to `design-intelligence:design-system-architect`
with `model_role="critique"`. Ask it to compare against the reference diagram
and find problems in story clarity, balance, missing/excess information, edge
label quality, and feedback loop clarity.

**Success criteria**: All three reviews complete. All factual claims verified
as ACCURATE. Diagram reviewer returns PASS or WARN (no FAIL). Design critique
identifies only minor issues.

### 9. Incorporate Review Findings

Fix any issues found in Step 8:
- Factual inaccuracies → fix the diagram to match code reality
- Missing mechanisms identified by code audit → add if README-level important
- Quality warnings → fix per reviewer guidance
- Design issues → fix per critique guidance

Re-render the diagram after fixes.

**Success criteria**: All review findings addressed. Diagram re-rendered.

### 10. Final Review

Run one more `dot-graph:diagram-reviewer` pass on the final version to
confirm PASS (or acceptable WARN).

**Success criteria**: Diagram reviewer returns PASS or WARN with no blocking
issues.

### 11. Place and Commit

1. Copy the `.dot`, `.svg`, and `.png` to the target repo's `docs/` directory
2. Add an `![Architecture](docs/<name>.svg)` reference to the repo's README.md
   (near the top, after the title and description, before prerequisites)
3. Commit and push

**Success criteria**: Diagram is committed, pushed, and visible in the
repo's README on GitHub.

**Human checkpoint**: Confirm the placement and commit message before pushing.

### 12. Detail Diagrams (Optional)

After the overview is placed, assess whether detail-level diagrams would add
value. Good candidates are:
- The system's most architecturally distinctive feature
- Core data flows that are non-obvious from the overview
- Plugin/extension lifecycle if the system is extensible
- State machines if the system has a rich lifecycle

Look at sibling repos for patterns — if the backend has 7 detail diagrams
covering different angles, the frontend likely benefits from 2-3 covering
its distinctive perspectives.

**Execution**: Delegate to `dot-graph:dot-author` with specific angle and
code-level findings from Step 1. Use the same visual conventions as the
overview. Save to `docs/diagrams/` subdirectory.

**Success criteria**: Detail diagrams committed and pushed.

**Human checkpoint**: Confirm which detail diagrams to create.
