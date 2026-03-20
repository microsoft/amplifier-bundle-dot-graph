# Level Synthesis: outlines/

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/outlines`
**Fidelity:** standard
**Child count:** 0 (leaf directory — no subdirectories)

---

## Files and Symbols at This Level

This directory contains a single file:

| File | Type | Size |
|------|------|------|
| `development-hygiene_outline.json` | JSON document-generation spec | 15,999 bytes |

### `development-hygiene_outline.json` — Structure

This is a **structured document synthesis specification** consumed by an AI-driven document
generation pipeline. It encodes everything needed to produce one output document.

**`_meta` block — generation parameters:**

| Key | Value |
|-----|-------|
| `document_type` | `"synthesized"` — marks this as a machine-generated output spec |
| `model` | `claude-sonnet-4-20250514` — target AI model |
| `max_response_tokens` | `8000` |
| `temperature` | `0.2` |
| `source_repo` | `"amplifier"` — primary repository context |
| `target_path` | `context/development-hygiene.md` — output file destination |
| `allowed_source_repos` | 50+ repositories across the Amplifier ecosystem |
| `consumers_excluded` | `[]` — no consumers excluded from grounding |
| `regeneration_notes` | Human-readable guidance for future regeneration runs |

The `allowed_source_repos` list spans the full Amplifier ecosystem: `amplifier`,
`amplifier-core`, `amplifier-foundation`, all CLI apps, all bundles (recipes,
design-intelligence, lsp, python-dev, rust-dev, shadow, typescript-dev, etc.), and
all module types (providers, tools, hooks, context, loop modules).

**`document` block — hierarchical section tree:**

```
# Amplifier CLI Installation Architecture & Development Hygiene
  ## How Amplifier is Installed
    ### Installation Flow
    ### Runtime Behavior
    ### Directory Structure
  ## CRITICAL: Never Delete the Cache Directly
    ### The Right Way: `amplifier reset`
  ## Development Patterns
    ### Don't Modify ~/.amplifier/cache/ for Development
    ### Project-Local Source Overrides
    ### Settings Scope Hierarchy
    ### Shadow Environments (Recommended for Testing)
    ### Project-Local Virtual Environments
  ## Summary: Where Things Belong
```

Each section carries: `heading`, `level` (1–3), `prompt` (AI generation instruction),
and `sources` (grounding file references with contribution description and relevance rating).

**Source files referenced across all sections:**

| Source File | Relevance | Sections |
|-------------|-----------|---------|
| `docs/LOCAL_DEVELOPMENT.md` | high | Installation Flow, Runtime Behavior, Directory Structure, Cache Warning, `amplifier reset`, Anti-patterns, Source Overrides, Settings Hierarchy, Shadow Envs, Venvs, Summary |
| `docs/USER_ONBOARDING.md` | medium/high | Settings Scope Hierarchy, Summary |
| `README.md` | high | Installation Flow |

`docs/LOCAL_DEVELOPMENT.md` is the **primary grounding source** — referenced by every
top-level section. `README.md` and `docs/USER_ONBOARDING.md` serve as supplementary
sources for specific subsections.

---

## Cross-Child Connections

**None.** This is a leaf directory with no subdirectories. There are no cross-child
connections to report.

---

## Boundary Patterns

### Pattern: AI Document Generation Spec (single-file, per-document)

The `outlines/` directory implements a **document synthesis specification layer**. Each
JSON file encodes everything a generation pipeline needs to produce one markdown document:

1. **Model configuration** — AI model selection, token budget, temperature constraints
2. **Source grounding** — specific files with relevance ranking and contribution descriptions
3. **Section scaffolding** — hierarchical prompt structure decomposing the document into
   independently-generatable sections
4. **Ecosystem scope declaration** — explicit `allowed_source_repos` list making this a
   cross-repo synthesis point (50+ repositories)

This pattern separates document **structure and intent** (the outline spec) from document
**content** (the generated `.md` at `target_path`). The `outlines/` directory is the
specification layer; `context/` is the output layer.

### Pattern: 1:1 Spec-to-Output Mapping

File naming follows a direct convention:
```
outlines/<name>_outline.json  →  context/<name>.md
```
The `target_path` field in `_meta` makes this mapping explicit and machine-readable.

### Pattern: Prompt-as-Structured-Contract

Each section's `prompt` field is not freeform text — it encodes a precise contract:
numbered steps, required content elements, specific fields to cite, and format
instructions (tables, ASCII trees, code blocks). This turns the outline into a
repeatable, deterministic document generation contract rather than open-ended guidance.

---

## Uncertainties for the Next Level Up

1. **How many outline specs exist at the bundle level?** This directory contains one file.
   Are there other outline spec files in sibling directories or other locations within the
   bundle? The `outlines/` pattern may be applied consistently across modules.

2. **What pipeline consumes these outlines?** The `_meta.consumers_excluded: []` field
   implies a pipeline that tracks consumers. What tool, recipe, or script reads these JSON
   specs and triggers document generation? This connection is invisible at this level.

3. **`context/` sibling relationship:** The `target_path` points to
   `context/development-hygiene.md`. How does the generation pipeline bridge
   `outlines/*.json` → `context/*.md`? Is there a recipe, Makefile, or script
   orchestrating this at the parent level?

4. **`allowed_source_repos` currency:** The 50+ repo list was written at a point in time.
   Is there a mechanism keeping it synchronized with the evolving Amplifier ecosystem?
   The `regeneration_notes` field hints at manual regeneration rather than automated
   synchronization.

5. **Single-file vs. multi-file outlines:** Is `development-hygiene_outline.json` the
   only outline, or was the directory designed to hold many? The parent level can confirm
   whether `outlines/` is a collection point or a singleton holder.
