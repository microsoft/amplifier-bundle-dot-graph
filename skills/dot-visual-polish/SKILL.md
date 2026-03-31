---
name: dot-visual-polish
description: Use when producing a polished OmniGraffle-style PNG from a DOT file — applies visual refinement after structural diagrams are complete and correct. Requires GOOGLE_API_KEY for nano-banana image generation.
---

# DOT Visual Polish Protocol

## Purpose

Transform a structurally correct DOT diagram into a visually polished, presentation-ready PNG with an OmniGraffle aesthetic. This protocol uses Graphviz for structural layout and nano-banana pro for visual refinement.

**When to use:** After a diagram passes `dot-quality` standards and you want a polished visual for presentations, documentation, or stakeholder communication.

**Prerequisites:**
- The DOT file is structurally complete and renders cleanly with Graphviz
- `GOOGLE_API_KEY` is set (nano-banana image generation required)

---

## The Protocol

### Step 0 — Load Anti-Slop Gate

Load the `no-ai-slop` skill and complete its pre-generation checklist before proceeding to Step 3. This is not optional.

```
load_skill("no-ai-slop")
```

### Step 1 — Render Structural Reference at 300 DPI

Produce a high-resolution PNG using Graphviz. This becomes the layout reference for nano-banana — it preserves the exact node positions, edge routing, and spatial relationships from the DOT source.

```bash
dot -Tpng -Gdpi=300 input.dot -o input_graphviz.png
```

Save to the same directory as the source file with a `_graphviz` suffix (e.g., `diagram_graphviz.png`). 300 DPI ensures nano-banana has enough detail to read all labels.

**Verify:** The file exists and is >100KB (a 300 DPI diagram should be substantial).

### Step 2 — Check Label Legibility

Use nano-banana `analyze` on the Graphviz render to identify any labels that won't survive the visual polish step.

```
nano-banana(
  operation="analyze",
  image_path="input_graphviz.png",
  prompt="List every text label visible in this diagram. Flag any that are:
  - Truncated or cut off
  - Overlapping with other text or elements
  - Smaller than ~8pt equivalent
  - Containing special characters that may render incorrectly (arrows, unicode, etc.)
  - Otherwise illegible or ambiguous
  
  For each flagged label, provide: (1) the label text as best you can read it, and (2) what's wrong."
)
```

Collect the list of illegible labels — these need explicit callout in the generation prompt so nano-banana reproduces them correctly.

### Step 3 — Parse DOT Structure for Prompt

Before generating, extract the complete graph structure from the DOT source to include in the generation prompt. This ensures nano-banana reproduces the exact topology, not an approximation.

Extract and list:
- All node names and their labels (verbatim)
- All edges with their labels (verbatim)
- All subgraph/cluster names and their labels
- The `rankdir` (layout direction)
- Any legend or title text

This parsed structure goes into the generation prompt as explicit text — do NOT rely on nano-banana reading the structure from the reference image alone.

### Step 4 — Generate Polished PNG

Write a generation prompt that includes ALL of:
1. The Graphviz render as `reference_image_path` (layout structure)
2. The complete parsed graph structure from Step 3 (every node, edge, label)
3. Any illegible labels from Step 2, with their correct text explicitly stated
4. The OmniGraffle Aesthetic Guide (below)

```
nano-banana(
  operation="generate",
  prompt="<the full prompt below>",
  reference_image_path="input_graphviz.png",
  output_path="input.png"
)
```

**Generation prompt template:**

```
Create a visually polished version of this architecture diagram using the reference image for exact layout and topology.

GRAPH STRUCTURE (reproduce exactly):
<paste the full parsed structure from Step 3 — every node, edge, cluster, and label>

ILLEGIBLE LABELS TO FIX (if any from Step 2):
<list each label with its correct text>

VISUAL STYLE — OmniGraffle Aesthetic:
- Background: Clean white (#FFFFFF) or very light warm gray (#F9F8F6)
- Node shapes: Rounded rectangles (corner radius ~8-12pt); ovals only for terminal/start nodes
- Node fill: Flat soft colors — light blues (#D6E8FA), soft greens (#D4EDDA), warm ambers (#FFF3CD), cool grays (#F0F0F0); subtle 1-2% gradient top-to-bottom acceptable
- Node border: Thin (1pt), medium-gray (#AAAAAA or #999999); no harsh black outlines
- Node shadow: Subtle drop shadow offset (1pt, 2pt), blur 4pt, opacity 15-20%
- Typography: Clean sans-serif (Helvetica Neue, SF Pro, or similar); title 28pt+ bold; cluster titles 18pt+ medium; node labels 16pt+; edge labels 11pt+ gray — never smaller
- Connectors: Smooth curved or orthogonal lines, 1.5pt stroke, medium gray (#888888); filled arrowheads, not hollow
- Spacing: Generous — minimum 24-32pt clearance between nodes; nodes should NOT be crowded
- Clusters: Light fill with rounded rectangle enclosure, dashed or thin border, semi-transparent fill
- Layout direction: Match the reference image exactly (top-down, left-right, etc.)
- Overall feel: Professional, airy, polished — NOT mechanical or boxy

CRITICAL RULES:
- Preserve EVERY node and EVERY edge from the reference — do not omit any
- Preserve EVERY label exactly as specified — do not abbreviate, rephrase, or truncate
- Preserve the spatial layout from the reference image — same relative positions
- Special characters (@, arrows, unicode) must be rendered large and unambiguous
- If a label has multiple lines, preserve the line breaks
```

### Step 5 — Verify Output

After generation:
1. Use nano-banana `compare` to check the polished output against the Graphviz render — verify no nodes or edges were dropped
2. Verify all labels from the DOT source are present and legible in the output
3. If any nodes/edges are missing or labels are wrong, regenerate with corrections

Save the final polished PNG to the same directory as the source DOT, using the base name without suffix (e.g., `diagram.dot` → `diagram.png`, overwriting the Graphviz render). Keep the `_graphviz` version as the structural reference.

---

## OmniGraffle Aesthetic Reference

For quick reference during prompt construction:

| Attribute | Specification |
|-----------|--------------|
| **Background** | White `#FFFFFF` or light warm gray `#F9F8F6` |
| **Node shapes** | Rounded rectangles (radius ~8-12pt); ovals sparingly for terminals |
| **Node fill** | Flat soft colors: blues `#D6E8FA`, greens `#D4EDDA`, ambers `#FFF3CD` |
| **Node border** | Thin `1pt`, medium-gray `#AAAAAA` — no harsh black |
| **Node shadow** | Subtle: offset `(1,2)pt`, blur `4pt`, opacity `15-20%` |
| **Title** | `28pt+` bold sans-serif |
| **Cluster titles** | `18pt+` medium sans-serif |
| **Node labels** | `16pt+` regular sans-serif |
| **Edge labels** | `11pt+` gray sans-serif |
| **Connectors** | `1.5pt` stroke, medium gray `#888888`, filled arrowheads |
| **Spacing** | Minimum `24-32pt` node clearance |
| **Clusters** | Light fill, rounded enclosure, dashed/thin border |

## What to Avoid

- No harsh black node borders (`#000000` outlines)
- No cramped layouts — generous whitespace always
- No default Graphviz color schemes (dark blue headers, saturated fills)
- No neon or overly saturated colors
- No thick connector lines (>2pt)
- No uniform large border-radius on everything — vary slightly between element types
- No shadow on every single element — reserve for nodes only, not connectors or labels
- No gradient backgrounds — white or near-white only

## Output Files

After completing the protocol, the directory should contain:

| File | Purpose |
|------|---------|
| `diagram.dot` | Original DOT source (unchanged) |
| `diagram_graphviz.png` | Structural reference render (300 DPI, Graphviz output) |
| `diagram.png` | Polished OmniGraffle-style output (nano-banana generated) |
