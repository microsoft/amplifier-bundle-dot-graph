# Subsystem Synthesis: amplifier bundle (bottomup-discovery)

**Subsystem:** `amplifier/` — the Amplifier ecosystem entry-point bundle
**Modules analyzed:** agents, behaviors, context, docs, outlines, recipes, tests, assets
**Fidelity tier:** standard
**Date:** 2026-03-20

---

## Cross-Module Data Flows

### Flow 1: behaviors -> context (context injection)

- **Source module:** `behaviors/`
- **Target module:** `context/`
- **Mechanism:** YAML `context.include` directives
- **Evidence:**
  - `amplifier-dev.yaml` includes `amplifier:context/development-hygiene.md`
  - `amplifier-expert.yaml` includes `amplifier:context/ecosystem-overview.md`
- **Coupling:** **Clean** — mediated by the `amplifier:` namespace resolver; behaviors reference context files by stable path, not by internal structure
- **Direction:** behaviors declare which context files to inject; context files are passive targets

### Flow 2: behaviors -> agents (agent inclusion)

- **Source module:** `behaviors/`
- **Target module:** `agents/`
- **Mechanism:** YAML `agents.include` directive
- **Evidence:**
  - `amplifier-expert.yaml` includes `amplifier:amplifier-expert` (the agent defined in `agents/amplifier-expert.md`)
- **Coupling:** **Clean** — mediated by the `amplifier:` namespace; the behavior references the agent by name, not by file path internals
- **Direction:** one-way; the behavior pulls the agent definition into a session

### Flow 3: agents -> docs (knowledge tier references)

- **Source module:** `agents/`
- **Target module:** `docs/`
- **Mechanism:** `@amplifier:docs/` @-mention references in agent instructions
- **Evidence:**
  - `amplifier-expert.md` Tier 1 knowledge references: `docs/USER_GUIDE.md`, `docs/USER_ONBOARDING.md`, `docs/DEVELOPER.md`, `docs/MODULES.md`, `docs/REPOSITORY_RULES.md`
- **Coupling:** **Clean** — @-mention is a lazy read mechanism; agent reads docs at query time, no compile-time binding
- **Direction:** one-way; agent reads docs on demand

### Flow 4: agents -> context (knowledge tier + soft references)

- **Source module:** `agents/`
- **Target module:** `context/`
- **Mechanism:** @-mention references and soft reference to `recipes-usage.md`
- **Evidence:**
  - `amplifier-expert.md` references context files through knowledge tiers
  - `amplifier-expert.yaml` behavior originally included `recipes-usage.md` but demoted to soft reference for token budget management
  - Uses `@foundation:context/shared/common-agent-base.md` as @-include base (external bundle dependency)
- **Coupling:** **Clean** — @-mention lazy loading

### Flow 5: outlines -> context (synthesis pipeline — TIGHT)

- **Source module:** `outlines/`
- **Target module:** `context/`
- **Mechanism:** Document synthesis pipeline — outline spec produces context document
- **Evidence:**
  - `development-hygiene_outline.json` has `target_path: context/development-hygiene.md`
  - The outline specifies structure and sources; LLM synthesis produces the context file
- **Coupling:** **Tight** — the outline's `target_path` directly names a file in `context/`. Changes to outline structure directly change the generated context document. This is an explicit production dependency.
- **Direction:** one-way; outlines produce context files

### Flow 6: outlines -> docs (source extraction)

- **Source module:** `outlines/`
- **Target module:** `docs/`
- **Mechanism:** Source file references in outline sections
- **Evidence:**
  - `development-hygiene_outline.json` cites `docs/LOCAL_DEVELOPMENT.md` (12 section references, high relevance) and `docs/USER_ONBOARDING.md` (4 references)
- **Coupling:** **Clean** — docs are read-only sources; outline references them by path but doesn't modify them
- **Direction:** one-way; outlines read from docs to produce context

### Flow 7: context -> docs (shared registry dependency)

- **Source module:** `context/`
- **Target module:** `docs/`
- **Mechanism:** References to `docs/MODULES.md` as canonical ecosystem repo registry
- **Evidence:**
  - `context/ecosystem-overview.md` references `docs/MODULES.md` for ecosystem repo listings
  - `context/recipes-usage.md` provides `grep`/`jq` commands to extract repo URLs from `docs/MODULES.md`
- **Coupling:** **Clean** — read-only references via @-mention
- **Direction:** one-way; context files read from docs

### Flow 8: recipes -> docs (HIDDEN runtime dependency)

- **Source module:** `recipes/`
- **Target module:** `docs/`
- **Mechanism:** Runtime fetch of `docs/MODULES.md` bypassing the `amplifier:` namespace
- **Evidence:**
  - `amplifier-ecosystem-audit.yaml`: `curl -sL ... "https://raw.githubusercontent.com/microsoft/amplifier/main/docs/MODULES.md"` (HTTP fetch for community repo discovery)
  - `repo-audit.yaml`: `curl -sL ... "https://raw.githubusercontent.com/microsoft/amplifier/main/docs/MODULES.md"` (HTTP fetch for MODULES.md listing check)
  - `ecosystem-activity-report.yaml`: `gh api repos/microsoft/amplifier/contents/docs/MODULES.md` (GitHub API fetch for all-repo discovery)
  - `outline-generation-from-doc.yaml`: `modules_file="{{landing_repo_path}}/docs/MODULES.md"` (local file read for repo scope gating)
- **Coupling:** **Hidden** — all recipe workflow pairs depend on MODULES.md's format and location. The HTTP/API fetches are invisible to bundle namespace resolution. The local file read in outline-generation depends on the landing repo having MODULES.md at the expected path.
- **Direction:** one-way; recipes consume docs as data source

### Flow 9: tests -> docs + recipes (verification targets — TIGHT)

- **Source module:** `tests/`
- **Target modules:** `docs/`, `recipes/`
- **Mechanism:** grep-based assertion checks against files in other modules
- **Evidence:**
  - `test_doc_sweep.sh` asserts against `README.md` (root), `docs/USER_GUIDE.md`, and `recipes/document-generation.yaml`
- **Coupling:** **Tight** — the test script hardcodes relative paths to files in `docs/` and `recipes/`. Renaming or moving those files silently breaks the test.
- **Direction:** one-way; tests read from docs and recipes

### Flow 10: recipes <-> outlines (pipeline artifact format)

- **Source module:** `recipes/`
- **Target module:** `outlines/`
- **Mechanism:** Shared `outline.json` artifact format
- **Evidence:**
  - `outline-generation-from-doc.yaml` produces structured outline JSON
  - `document-generation.yaml` consumes `outline_path` as input context variable
  - `outlines/development-hygiene_outline.json` is the same format used by both recipes
- **Coupling:** **Clean** — the outline JSON format acts as a typed data contract between recipes and the outlines module
- **Direction:** bidirectional; recipes produce and consume the format; outlines/ stores instances

### Flow 11: bundle.md -> behaviors + context + docs (root wiring)

- **Source:** `bundle.md` (root bundle definition)
- **Target modules:** `behaviors/`, `context/`, `docs/`
- **Mechanism:** Bundle includes and @-mention references
- **Evidence:**
  - `includes: - bundle: amplifier:behaviors/amplifier-expert` (pulls behavior)
  - `@amplifier:context/ecosystem-overview.md` (inlines context)
  - `@amplifier:docs/` (references docs directory)
  - `includes: - bundle: git+https://github.com/microsoft/amplifier-foundation@main` (external)
- **Coupling:** **Clean** — uses the standard bundle inclusion protocol
- **Direction:** root fans out to modules; modules do not reference bundle.md

---

## Shared Interfaces

### Interface 1: Bundle Declaration Protocol

- **Type:** Structural YAML schema (`bundle` -> `context` -> optional `agents`)
- **Modules implementing it:** `behaviors/` (both YAML files), `bundle.md` (root)
- **Description:** The shared contract that allows the Amplifier runtime to discover and load bundle components. Both behavior YAML files and the root bundle.md follow the same `bundle:` / `context:` / `agents:` / `includes:` schema.
- **Role:** Primary composition mechanism — the protocol enabling all inter-module wiring.

### Interface 2: @-mention Namespace Resolution

- **Type:** Runtime path resolution protocol (`amplifier:path/to/resource`)
- **Modules using it:** `agents/` (knowledge tier refs), `behaviors/` (context.include, agents.include), `bundle.md` (@-mention inlines), `context/` (references to external bundles)
- **Description:** The `amplifier:` namespace prefix resolves to the root of this bundle at runtime. All cross-module references within this bundle use this protocol, making them location-independent as long as relative paths within the bundle are preserved.
- **Role:** Decoupling mechanism — modules reference each other by namespace path, not by absolute filesystem paths.

### Interface 3: MODULES.md Registry Format

- **Type:** Shared data format (Markdown registry with structured sections)
- **Modules consuming it:** `recipes/` (4 recipes parse it at runtime), `docs/` (defines it), `context/` (2 context files reference it), `agents/` (references it in knowledge tiers)
- **Description:** `docs/MODULES.md` serves as the living ecosystem catalog. Four modules depend on its structure and content. There is no schema enforcement — it is a hand-maintained Markdown file consumed by LLM-based parsing in recipe steps.
- **Role:** Implicit shared contract — changes to MODULES.md format could break recipe parsing without warning.

### Interface 4: Outline Spec Format

- **Type:** JSON schema for document synthesis (`_meta` + `sections[]` + source mappings)
- **Modules using it:** `outlines/` (stores specs), `recipes/` (outline-generation and document-generation recipes operate on the same format)
- **Description:** The outline JSON format is the artifact contract between the outline-generation recipe and the document-generation recipe, and between the outlines/ module and the context/ module.
- **Role:** Pipeline interface — the only typed data contract in this subsystem.

---

## Coupling Assessment

| Source Module | Target Module | Coupling Type | Evidence |
|---|---|---|---|
| behaviors -> context | context/ | **Clean** | Namespace-mediated `context.include` |
| behaviors -> agents | agents/ | **Clean** | Namespace-mediated `agents.include` |
| agents -> docs | docs/ | **Clean** | @-mention lazy read |
| agents -> context | context/ | **Clean** | @-mention lazy read / soft ref |
| context -> docs | docs/ | **Clean** | @-mention references to MODULES.md |
| outlines -> context | context/ | **Tight** | Direct `target_path` production dependency |
| outlines -> docs | docs/ | **Clean** | Read-only source references |
| recipes -> docs | docs/ | **Hidden** | 4 recipe files fetch MODULES.md at runtime (curl/gh api/local read); bypasses namespace |
| recipes <-> outlines | outlines/ | **Clean** | Shared outline.json format as typed contract |
| tests -> docs + recipes | docs/, recipes/ | **Tight** | Hardcoded relative file paths in grep assertions |
| bundle.md -> all | behaviors, context, docs | **Clean** | Standard bundle include protocol |

**Tight coupling locations (2):**
1. **outlines/ -> context/**: `development-hygiene_outline.json` targets `context/development-hygiene.md` by explicit path. Changes to the outline directly change the context document.
2. **tests/ -> docs/ + recipes/**: `test_doc_sweep.sh` hardcodes paths `docs/USER_GUIDE.md` and `recipes/document-generation.yaml`. File renames silently break the test.

**Hidden coupling (1):**
1. **recipes/ -> docs/**: Four recipe files depend on `docs/MODULES.md` at runtime — two via HTTP/GitHub API fetch (`curl`/`gh api`), one via local file read (`{{landing_repo_path}}/docs/MODULES.md`), and one via `curl` for listing checks. All bypass the `amplifier:` namespace resolution, making the dependency invisible to bundle tooling.

---

## Emergent Patterns

### Pattern 1: Three-Layer Context Pipeline

Content flows through a three-layer refinement pipeline that spans four modules:

```
docs/ (authoritative long-form documentation)
  | sourced by
outlines/ (synthesis specifications with section-level prompts)
  | produces
context/ (agent-optimized ~6.5KB summaries)
  | injected by
behaviors/ (session activation declarations)
  | consumed by
agents/ (runtime knowledge base)
```

This pipeline transforms dense developer documentation into token-efficient context files. The `outlines/` module is the transformation bridge. This is the dominant architectural pattern in the subsystem — it explains WHY most cross-module edges exist.

### Pattern 2: Hub-and-Spoke Bundle Architecture

`bundle.md` sits at the center and fans out to three operational spokes:
- **Knowledge spoke:** `agents/` + `context/` + `docs/` — defines what the bundle knows
- **Capability spoke:** `behaviors/` — defines what sessions can do
- **Automation spoke:** `recipes/` — defines repeatable multi-step workflows

Each spoke is self-contained but connects through the `amplifier:` namespace protocol.

### Pattern 3: Dual-Lifecycle Documentation (Human vs. Agent)

The subsystem maintains two parallel documentation surfaces:
- **`docs/`** — human-facing, audience-tiered (user / developer / contributor), 10 files, ~125KB total
- **`context/`** — agent-facing, balanced ~6.5KB each, 3 files, ~20KB total

These are NOT duplicates. They have different consumers, different granularity, and different update cycles. The `outlines/` module is the bridge that synthesizes agent context from human docs.

### Pattern 4: Recipe Orchestrator-Worker Topology

The `recipes/` module internally implements two orchestrator-worker pairs and one pipeline pair:
- **Audit:** `ecosystem-audit` -> `repo-audit` (foreach parallel:2)
- **Activity:** `activity-report` -> `repo-analysis` (foreach + _precomputed interface)
- **DocGen:** `outline-gen` -> `document-gen` (file-based handoff via outline.json)

All three pairs consume `docs/MODULES.md` as their shared registry, creating a runtime dependency from the automation spoke back to the knowledge spoke.

### Pattern 5: Static Asset Island

The `assets/` module is structurally isolated — zero cross-module data flows. No other module references files in `assets/`. It exists as a pure static resource repository consumed only by external tooling outside this bundle's scope.

---

## Recommended Investigation

1. **MODULES.md format stability:** All recipe workflow pairs depend on parsing MODULES.md at runtime (via `curl`, `gh api`, or local file read). What happens when MODULES.md format changes? The tests/ module does NOT test MODULES.md parsing — there is zero regression coverage for this hidden coupling.

2. **Outline pipeline completeness:** Only one outline spec exists (`development-hygiene_outline.json`). Are there outline specs for the other two context files (`ecosystem-overview.md`, `recipes-usage.md`)? If not, how are those maintained — manually or via a different mechanism?

3. **Behavior activation mechanism:** The `bundle.md` only includes `amplifier:behaviors/amplifier-expert`. Is `amplifier-dev` ever loaded? The findings don't reveal WHETHER `amplifier-dev.yaml` is auto-discovered or explicitly referenced elsewhere.

4. **Test coverage gap:** The single test script covers only model name migration (8 grep assertions across 3 files). No tests verify cross-module contracts (namespace resolution, MODULES.md parsing, outline-to-context production). The subsystem has zero structural regression testing.

5. **assets/ consumer identification:** No module in this bundle references `assets/`. The next level up should identify external consumers (build systems, HTML templates, packaging pipelines).

6. **Shared agent vocabulary across recipes:** `foundation:zen-architect` appears in 4 of 6 recipes; `foundation:explorer` in 3 of 6. This shared dependency on external foundation agents creates an implicit coupling between the recipes module and the foundation bundle's agent roster. Changes to those agents affect multiple recipes simultaneously.

7. **Outline source freshness:** The outline `development-hygiene_outline.json` references specific line numbers in source docs (e.g., "lines 614-620"). These references become stale as source documents evolve. No mechanism for validating outline-to-source alignment is visible.
