# Level Synthesis: `outlines/`

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/outlines`
**Fidelity:** standard
**Child subdirectories:** none (leaf directory)
**Files at this level:** 1

---

## Files and Symbols at This Level

| File | Size | Type | Role |
|------|------|------|------|
| `development-hygiene_outline.json` | 15,999 bytes | JSON | Document synthesis specification |

This is a **leaf directory** containing a single artifact: a structured JSON outline that serves as a machine-readable specification for generating a synthesized documentation file.

### Structural Decomposition of `development-hygiene_outline.json`

The file has two top-level keys:

**`_meta`** — Generation configuration:
- `document_type: "synthesized"` — marks this as a spec for automated generation
- `model: "claude-sonnet-4-20250514"`, `temperature: 0.2`, `max_response_tokens: 8000`
- `target_path: "context/development-hygiene.md"` — the output document this spec will generate
- `source_repo: "amplifier"` — the home repository
- `allowed_source_repos` — 37 Amplifier ecosystem repositories that may contribute source material (includes core, foundation, all app/bundle/module repos)
- `consumers_excluded: []` — no files excluded from consumer tracking
- `regeneration_notes` — prose instructions explaining how and when to regenerate

**`document`** — Section tree specification:
- `title`: "Amplifier CLI Installation Architecture & Development Hygiene"
- `output`: "context/development-hygiene.md"
- `sections`: hierarchical array of sections, each with `heading`, `level`, `prompt`, `sources`, `sections[]`

### Section Hierarchy

```
§1  Amplifier CLI Installation Architecture & Development Hygiene  (root, level 1)
    §1.1  How Amplifier is Installed                               (level 2)
          §1.1.1  Installation Flow                                (level 3)
          §1.1.2  Runtime Behavior                                 (level 3)
          §1.1.3  Directory Structure                              (level 3)
    §1.2  CRITICAL: Never Delete the Cache Directly               (level 2)
          §1.2.1  The Right Way: `amplifier reset`                 (level 3)
    §1.3  Development Patterns                                     (level 2)
          §1.3.1  Don't Modify ~/.amplifier/cache/ for Development (level 3)
          §1.3.2  Project-Local Source Overrides                   (level 3)
          §1.3.3  Settings Scope Hierarchy                         (level 3)
          §1.3.4  Shadow Environments (Recommended for Testing)    (level 3)
          §1.3.5  Project-Local Virtual Environments               (level 3)
    §1.4  Summary: Where Things Belong                            (level 2)
```
Total: 5 top-level sections (including root), 9 subsections, 14 total nodes.

### Source References Within the Outline

Each section's `sources` array references files with `file_path`, `contribution`, and `relevance` fields:

| Source File | Relevance Tier | Section Count |
|---|---|---|
| `docs/LOCAL_DEVELOPMENT.md` | high (most refs) | 12 individual section references |
| `docs/USER_ONBOARDING.md` | medium | 4 individual section references |

`LOCAL_DEVELOPMENT.md` is the dominant grounding document, supplying content for all major sections. `USER_ONBOARDING.md` contributes primarily to the settings scope hierarchy and summary sections.

---

## Cross-Child Connections

**None** — this is a leaf directory with no child subdirectories. The cross-level connections at this node are entirely *upward*: the generated output (`context/development-hygiene.md`) and the source references (`docs/LOCAL_DEVELOPMENT.md`, `docs/USER_ONBOARDING.md`) live outside this directory. The `outlines/` directory itself only contains specifications; it depends on sibling or parent directories for inputs and outputs.

---

## Boundary Patterns

### Pattern: Document Synthesis Specification

The single file in this directory represents the **Document Synthesis Specification** pattern:

- A JSON file encodes *what* to write (section prompts), *where* to look (source file references), *who* is allowed to contribute (allowed_source_repos), and *where* to write it (target_path).
- An external generation process reads this spec and calls an LLM with the prompts + grounded sources to produce the target markdown file.
- This separates **specification** (this directory) from **content** (`context/`) and **sources** (`docs/`).

This is a **content pipeline input node**: the `outlines/` directory acts as a schema/spec store that feeds a documentation generation pipeline. The outline file references two upstream source documents and one downstream target, making this directory a pure specification layer with no logic of its own.

### Pattern: LLM-Grounded Section Scaffolding

Each section in the outline carries:
1. A **prompt** — the instruction sent to the LLM for that section
2. **Sources** — files that ground the generation (cited by path + contribution + relevance)

This is a structured prompt-engineering pattern for documentation synthesis: rather than a free-form prompt, every section has its own scoped instruction and explicit source citations, enabling reproducible, auditable document generation.

---

## Relationship to Parent Directories

The `outlines/` directory sits within `amplifier/` and is a sibling to directories like `context/`, `docs/`, `recipes/`, etc. (presumed — not directly visible here).

Key cross-boundary relationships visible from this outline:
- **Reads from** `amplifier/docs/LOCAL_DEVELOPMENT.md` and `amplifier/docs/USER_ONBOARDING.md`
- **Writes to** `amplifier/context/development-hygiene.md`
- **Scoped to** 37 repositories across the Amplifier monorepo ecosystem via `allowed_source_repos`

---

## Uncertainties for the Next Level Up

1. **Are there more outline files?** This directory currently holds one file. Is this a growing collection, or a one-off? The `outlines/` directory name implies a pattern — do other outline specs exist (e.g., `installation_outline.json`, `architecture_outline.json`)?

2. **What runs the generation pipeline?** The outline spec references a model and target, but there is no generation runner in this directory. Where does the generation script/recipe live that reads these outlines and produces the context files?

3. **Is `context/development-hygiene.md` up to date?** The outline has `regeneration_notes` suggesting this file must be re-run periodically. Is there CI or a recipe that tracks freshness?

4. **How does `allowed_source_repos` act as a scope gate?** The field lists 37 repos, but the enforcement mechanism is not visible from the outline alone. What in the generation pipeline enforces that only these repos are used?

5. **How is the outline itself maintained?** Since the outline's prompts reference specific line numbers (e.g., "lines 614-620") in source files, it can become stale. Is there a process for keeping outline source references current?
