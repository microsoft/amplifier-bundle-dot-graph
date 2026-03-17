# Discovery Pipeline v2 Phase A: Four New Agents — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Create 4 new discovery agents and their context instruction files for the v2 redesign — all markdown, no Python code.

**Architecture:** Each agent gets a context instruction file (`context/<name>-instructions.md`) containing the full methodology, and an agent file (`agents/<name>.md`) with YAML frontmatter and a markdown body that `@mention`s the instructions file. `behaviors/dot-discovery.yaml` is updated to declare all 4 new agents. Two existing test files are updated to cover the expanded file set.

**Tech Stack:** Markdown, YAML frontmatter (agent files), pytest (Python test files)

---

## Pre-flight

Confirm the test suite is green before starting:

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ -v --tb=short 2>&1 | tail -5
```

Expected: `797 passed`

---

### Task 1: Context instructions for `discovery-level-synthesizer`

**Files:**
- Create: `context/discovery-level-synthesizer-instructions.md`
- Create: `tests/test_discovery_level_synthesizer_instructions.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_level_synthesizer_instructions.py` with this exact content:

```python
"""
Tests for context/discovery-level-synthesizer-instructions.md existence and required content.
Covers the Bottom-Up Level Synthesis Methodology for the level-synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LEVEL_SYNTH_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-level-synthesizer-instructions.md"
)


def test_level_synthesizer_instructions_exists():
    """context/discovery-level-synthesizer-instructions.md must exist."""
    assert LEVEL_SYNTH_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-level-synthesizer-instructions.md not found at "
        f"{LEVEL_SYNTH_INSTRUCTIONS_PATH}"
    )


def test_level_synthesizer_instructions_line_count():
    """File must be between 80 and 180 lines."""
    content = LEVEL_SYNTH_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_level_synthesizer_instructions_has_heading():
    """File must contain a heading about level synthesis or bottom-up."""
    content = LEVEL_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Level Synthesizer",
            "level synthesizer",
            "Level Synthesis",
            "Bottom-Up",
            "bottom-up",
        ]
    ), "Must contain a heading about level synthesis or bottom-up"


def test_level_synthesizer_instructions_mentions_fresh_context():
    """File must mention fresh context / clean slate mandate."""
    content = LEVEL_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["fresh context", "clean slate", "zero prior", "fresh"]
    ), "Must mention fresh context or clean slate mandate"


def test_level_synthesizer_instructions_mentions_cross_child():
    """File must mention cross-child connections."""
    content = LEVEL_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "cross-child",
            "cross child",
            "between children",
            "spanning children",
            "span multiple child",
        ]
    ), "Must mention cross-child connections"


def test_level_synthesizer_instructions_mentions_shape_vocabulary():
    """File must mention at least 2 semantic shapes from the vocabulary."""
    content = LEVEL_SYNTH_INSTRUCTIONS_PATH.read_text()
    shapes = ["note", "box", "cylinder", "component", "diamond", "hexagon"]
    found = [s for s in shapes if s in content]
    assert len(found) >= 2, f"Must mention at least 2 semantic shapes, found: {found}"


def test_level_synthesizer_instructions_mentions_diagram_dot():
    """File must mention diagram.dot as a required output."""
    content = LEVEL_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content, "Must mention diagram.dot as a required output"


def test_level_synthesizer_instructions_mentions_findings_md():
    """File must mention findings.md as a required output."""
    content = LEVEL_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must mention findings.md as a required output"
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_level_synthesizer_instructions.py -v
```

Expected: `FAILED` — `test_level_synthesizer_instructions_exists` fails with "file not found"

---

**Step 3: Write the implementation**

Create `context/discovery-level-synthesizer-instructions.md` with this exact content:

```markdown
# Discovery Level Synthesizer: Bottom-Up Level Synthesis Methodology

You are the **level-synthesizer** agent in the bottom-up discovery strategy. Your role is to
synthesize what lives at one directory level of a codebase — reading what's directly present
plus what child directories have already discovered — and produce a graph representing this
level's structure and its cross-child connections.

## Core Principle

**Build upward from evidence, not downward from assumptions.**

Do not reason about what a directory "should" contain. Read what is actually there: the source
files at this level, and the synthesis DOTs produced by each immediate child directory. Let
that evidence drive your synthesis.

## Fresh Context Mandate

Start with a clean slate. You have no memory of previous directory levels. Each directory level
is a fresh investigation. Do not carry assumptions from sibling directories or parent directories —
what you find here may be completely different.

## What to Look For

### Cross-Child Connections

Your highest-value finding is connections that span multiple child directories. These are
connections only visible at this level — not inside any single child.

Look specifically for:
- Imports that pull from two or more child directories at this level
- Shared types or interfaces that flow between children
- Orchestration code that coordinates multiple children
- Error handling that aggregates results from multiple children

### Boundary Patterns

What does this level reveal that the children couldn't see from inside? Common patterns:
- A registry or factory that instantiates classes from multiple children
- A pipeline that chains components from different children in order
- A configuration layer that controls child behavior uniformly
- A public API that abstracts over multiple child implementations

### What Does NOT Belong Here

Do not re-describe child internals visible in the children's DOTs. The children have already
documented their own structure. Your job is the seam between them, not their contents.

## Shape Vocabulary

Use these standard shapes for semantic clarity:

| Shape | Use for |
|-------|---------|
| `note` | Source files (`.py`, `.rs`, `.go`, etc.) |
| `box` | Classes, functions, key symbols |
| `cylinder` | Data stores, caches, databases |
| `component` | Modules, packages, sub-directories |
| `diamond` | Decision points, conditional branches |
| `hexagon` | Interfaces, protocols, abstract types |

Use `fillcolor` to distinguish origin: blue (`#ddeeff`) for this level's content, gray
(`#eeeeee`) for child content referenced from this level.

## Required Artifacts

Produce both files in your assigned directory before signaling completion:

### diagram.dot

A DOT digraph representing this directory level. Validate with the dot-graph tool before writing.

Requirements:
- `digraph` (directed graph)
- Cluster subgraphs for each child directory referenced
- This level's files and key symbols outside or above the child clusters
- Edges showing cross-child connections as the primary finding
- Legend cluster
- 50–150 lines

### findings.md

A level summary covering:
- Files and key symbols directly at this level (not in children)
- Cross-child connections found (these are the primary finding)
- Boundary patterns visible from this level that no single child could see
- What remains uncertain or requires investigation at the next level up

Format: structured markdown, concise. This is input to the parent level-synthesizer.

## Final Response Contract

Signal completion only after both artifacts are written to the assigned directory. Your final
message must state:
- Which directory level was synthesized
- How many cross-child connections were found
- The single most significant boundary pattern discovered
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_level_synthesizer_instructions.py -v
```

Expected: All 8 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add context/discovery-level-synthesizer-instructions.md tests/test_discovery_level_synthesizer_instructions.py && git commit -m "feat: add discovery-level-synthesizer context instructions (Phase A v2)"
```

---

### Task 2: Context instructions for `discovery-subsystem-synthesizer`

**Files:**
- Create: `context/discovery-subsystem-synthesizer-instructions.md`
- Create: `tests/test_discovery_subsystem_synthesizer_instructions.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_subsystem_synthesizer_instructions.py` with this exact content:

```python
"""
Tests for context/discovery-subsystem-synthesizer-instructions.md existence and required content.
Covers the Subsystem Synthesis Methodology for the subsystem-synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-subsystem-synthesizer-instructions.md"
)


def test_subsystem_synthesizer_instructions_exists():
    """context/discovery-subsystem-synthesizer-instructions.md must exist."""
    assert SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-subsystem-synthesizer-instructions.md not found at "
        f"{SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH}"
    )


def test_subsystem_synthesizer_instructions_line_count():
    """File must be between 80 and 180 lines."""
    content = SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_subsystem_synthesizer_instructions_has_heading():
    """File must contain a heading about subsystem synthesis."""
    content = SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Subsystem Synthesizer",
            "subsystem synthesizer",
            "Subsystem Synthesis",
            "Seam",
            "seam",
        ]
    ), "Must contain a heading about subsystem synthesis or seam-finding"


def test_subsystem_synthesizer_instructions_investigates_between_modules():
    """File must emphasize investigating the spaces between modules."""
    content = SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "between modules",
            "spaces between",
            "seam",
            "between",
        ]
    ), "Must emphasize investigating the spaces between modules"


def test_subsystem_synthesizer_instructions_mentions_cross_module():
    """File must mention cross-module data flows or connections."""
    content = SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "cross-module",
            "cross module",
            "between modules",
            "module boundary",
            "module boundaries",
        ]
    ), "Must mention cross-module connections or data flows"


def test_subsystem_synthesizer_instructions_mentions_interface_or_boundary():
    """File must mention interface, boundary, or hexagon shapes."""
    content = SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["interface", "boundary", "hexagon", "shared interface"]
    ), "Must mention interfaces, boundaries, or hexagon shapes"


def test_subsystem_synthesizer_instructions_mentions_diagram_dot():
    """File must mention diagram.dot as a required output."""
    content = SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content, "Must mention diagram.dot as a required output"


def test_subsystem_synthesizer_instructions_mentions_findings_md():
    """File must mention findings.md as a required output."""
    content = SUBSYSTEM_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must mention findings.md as a required output"
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_subsystem_synthesizer_instructions.py -v
```

Expected: `FAILED` — `test_subsystem_synthesizer_instructions_exists` fails with "file not found"

---

**Step 3: Write the implementation**

Create `context/discovery-subsystem-synthesizer-instructions.md` with this exact content:

```markdown
# Discovery Subsystem Synthesizer: Seam-Finder Methodology

You are the **subsystem-synthesizer** agent. Your role is to investigate the spaces **between**
modules within a subsystem — finding cross-module data flows, shared interfaces, and emergent
patterns that no single module's DOT can capture.

## Core Principle

> **You investigate the spaces BETWEEN modules, not their internals.**

You receive per-module consensus DOTs plus source files at the subsystem boundary. Your job is
not to summarize each module — the module DOTs already do that. Your job is what emerges when
you look at how modules relate to each other.

## What to Look For

### Cross-Module Data Flows

Trace data as it crosses module boundaries:
- What types flow from module A into module B?
- Where are those types defined — in a shared module, or is one module importing from another?
- Are there transformation points at the boundary (type conversions, validation, serialization)?

### Shared Interfaces

Look for interfaces that span multiple modules:
- Abstract types, protocols, or base classes that two or more modules implement
- Shared configuration or context objects that flow through multiple modules
- Event types or message formats that decouple modules from each other

### Coupling vs. Separation

Assess the quality of module boundaries:
- **Tight coupling**: Module A directly imports from module B's internals (not its public API)
- **Clean separation**: Modules communicate only through well-defined interfaces
- **Hidden coupling**: Two modules share state through a third (database, cache, global)

Note: document what you find, do not editorialize. Tight coupling is a finding, not a failure.

### What Does NOT Belong Here

Do not describe module internals. The per-module DOTs captured those. Your diagram shows
what NO single module's DOT captured — the seam, the boundary, the interoperation.

## Visual Conventions

Use these conventions to make subsystem-level structure immediately readable:

| Element | Visual | Meaning |
|---------|--------|---------|
| Interfaces / protocols | `shape=hexagon` | Shared contract between modules |
| Module clusters | `subgraph cluster_<name>` | Each module as a cluster |
| Cross-module calls | `style=dashed` | Calls that cross module boundaries |
| Shared types | `shape=note, style=filled, fillcolor="#ffe0b2"` | Types flowing between modules |
| Tight coupling | `color=red` edge | Direct internal import (noteworthy) |

## Required Artifacts

Produce both files in your assigned directory before signaling completion:

### diagram.dot

A DOT digraph representing the subsystem's inter-module structure. Validate before writing.

Requirements:
- Each module as a `subgraph cluster_<name>`
- Cross-module edges as the primary content
- Shared interfaces as hexagon nodes
- Legend cluster
- 50–150 lines

### findings.md

A subsystem-level analysis covering:
- Cross-module data flows found
- Shared interfaces identified
- Coupling assessment (tight coupling hotspots, clean separations)
- Emergent subsystem-level patterns not visible inside any single module
- Recommended investigation for any coupling concerns

## Final Response Contract

Signal completion only after both artifacts are written. Your final message must state:
- Which subsystem was analyzed
- How many cross-module flows were identified
- Whether any tight coupling was found, and where
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_subsystem_synthesizer_instructions.py -v
```

Expected: All 8 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add context/discovery-subsystem-synthesizer-instructions.md tests/test_discovery_subsystem_synthesizer_instructions.py && git commit -m "feat: add discovery-subsystem-synthesizer context instructions (Phase A v2)"
```

---

### Task 3: Context instructions for `discovery-overview-synthesizer`

**Files:**
- Create: `context/discovery-overview-synthesizer-instructions.md`
- Create: `tests/test_discovery_overview_synthesizer_instructions.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_overview_synthesizer_instructions.py` with this exact content:

```python
"""
Tests for context/discovery-overview-synthesizer-instructions.md existence and required content.
Covers the Overview Synthesis Methodology for the overview-synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OVERVIEW_SYNTH_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-overview-synthesizer-instructions.md"
)


def test_overview_synthesizer_instructions_exists():
    """context/discovery-overview-synthesizer-instructions.md must exist."""
    assert OVERVIEW_SYNTH_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-overview-synthesizer-instructions.md not found at "
        f"{OVERVIEW_SYNTH_INSTRUCTIONS_PATH}"
    )


def test_overview_synthesizer_instructions_line_count():
    """File must be between 80 and 180 lines."""
    content = OVERVIEW_SYNTH_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_overview_synthesizer_instructions_has_heading():
    """File must contain a heading about overview synthesis."""
    content = OVERVIEW_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Overview Synthesizer",
            "overview synthesizer",
            "Overview Synthesis",
            "System-Level",
            "system-level",
        ]
    ), "Must contain a heading about overview synthesis"


def test_overview_synthesizer_instructions_every_node_is_subsystem():
    """File must state that every node represents an entire subsystem."""
    content = OVERVIEW_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "every node represents",
            "each node represents",
            "node represents a subsystem",
            "node is a subsystem",
            "nodes are subsystems",
        ]
    ), "Must state that every node represents an entire subsystem"


def test_overview_synthesizer_instructions_mentions_quality_gate():
    """File must mention the quality gate (80 nodes or 250 lines)."""
    content = OVERVIEW_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert "80" in content or "250" in content, (
        "Must mention quality gate: >80 nodes means too detailed, or 250-line limit"
    )


def test_overview_synthesizer_instructions_mentions_dot_quality():
    """File must reference dot-quality skill or quality standards."""
    content = OVERVIEW_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["dot-quality", "dot quality", "quality skill", "quality standard"]
    ), "Must reference dot-quality skill or quality standards"


def test_overview_synthesizer_instructions_mentions_diagram_dot():
    """File must mention diagram.dot as a required output."""
    content = OVERVIEW_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content, "Must mention diagram.dot as a required output"


def test_overview_synthesizer_instructions_mentions_findings_md():
    """File must mention findings.md as a required output."""
    content = OVERVIEW_SYNTH_INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must mention findings.md as a required output"
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_overview_synthesizer_instructions.py -v
```

Expected: `FAILED` — `test_overview_synthesizer_instructions_exists` fails with "file not found"

---

**Step 3: Write the implementation**

Create `context/discovery-overview-synthesizer-instructions.md` with this exact content:

```markdown
# Discovery Overview Synthesizer: System-Level Pattern Finder Methodology

You are the **overview-synthesizer** agent. Your role is to produce the governing-level view of
a repository — a bounded overview showing how subsystems relate to each other, what the
end-to-end architectural flow looks like, and what you would explain to a newcomer in 5 minutes.

## Core Principle

> **Every node in your diagram represents an entire subsystem — not a file, not a class.**

You receive all subsystem DOTs plus source files at the repo root. You are operating at the
highest level of abstraction in the discovery pipeline. Collapse everything that is subsystem-
internal into a single node. Your diagram shows the architecture, not the implementation.

## Quality Gate

**If your diagram has more than 80 nodes, it is too detailed.** Stop and collapse further.

Common collapse strategies:
- Merge closely related subsystems into a single cluster node
- Represent all utility/helper subsystems as one `[Utilities]` node
- If a subsystem has no cross-subsystem connections, it may not need a node

This is a hard rule. A 90-node diagram is not a slightly-detailed overview — it is a failure
to synthesize. Re-collapse until you are at or below 80 nodes.

Your `diagram.dot` must also stay within **150–250 lines**. Reference the dot-quality skill
(`@dot-graph:skills/dot-quality/SKILL.md`) if you are uncertain about quality standards.

## What to Show

### Cross-Subsystem Dependencies

Trace how subsystems depend on each other:
- Which subsystems are upstream (others depend on them)?
- Which are downstream (they depend on others)?
- Are there circular dependencies?
- What is the "spine" — the critical path that most flows pass through?

### End-to-End Flow

Identify the primary flows that a user action or external input takes through the system:
- Entry point (CLI, API endpoint, event) → which subsystem handles it first?
- How does it move through subsystems to produce output?
- Where are the major boundaries (network calls, DB writes, external API calls)?

### Architectural Patterns

What governing pattern does the architecture follow?
- Pipeline? (stages in sequence)
- Hub-and-spoke? (one central coordinator)
- Event-driven? (publish/subscribe across subsystems)
- Layered? (presentation → business logic → data)

Name the pattern explicitly. If the architecture doesn't fit a clean pattern, that is also
a finding — name what makes it complex or hybrid.

## Output Bounds

- **≤80 nodes** — hard limit; collapse if exceeded
- **150–250 lines** — diagram.dot target range
- **3–5 sentences** — the architectural spine summary in findings.md

## Required Artifacts

Produce both files in your assigned directory before signaling completion:

### diagram.dot

A bounded DOT digraph representing the full system architecture. Validate before writing.

Requirements:
- Each subsystem as a node or minimal cluster
- Cross-subsystem dependency edges as the primary content
- Architectural spine highlighted (e.g., bold edges or a distinct color)
- Legend cluster
- 150–250 lines, ≤80 nodes

### findings.md

A system-level narrative covering:
- The governing architectural pattern (named)
- The architectural spine (primary end-to-end flow, 3–5 sentences)
- Notable cross-subsystem dependency findings
- Any circular dependencies or unexpected coupling
- What this codebase would look like explained to a newcomer

## Final Response Contract

Signal completion only after both artifacts are written. Your final message must state:
- How many subsystems were synthesized into the overview
- The named architectural pattern
- The single most important cross-subsystem dependency
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_overview_synthesizer_instructions.py -v
```

Expected: All 8 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add context/discovery-overview-synthesizer-instructions.md tests/test_discovery_overview_synthesizer_instructions.py && git commit -m "feat: add discovery-overview-synthesizer context instructions (Phase A v2)"
```

---

### Task 4: Context instructions for `discovery-combiner`

**Files:**
- Create: `context/discovery-combiner-instructions.md`
- Create: `tests/test_discovery_combiner_instructions.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_combiner_instructions.py` with this exact content:

```python
"""
Tests for context/discovery-combiner-instructions.md existence and required content.
Covers the Convergence/Divergence Analysis Methodology for the combiner agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
COMBINER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-combiner-instructions.md"
)


def test_combiner_instructions_exists():
    """context/discovery-combiner-instructions.md must exist."""
    assert COMBINER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-combiner-instructions.md not found at "
        f"{COMBINER_INSTRUCTIONS_PATH}"
    )


def test_combiner_instructions_line_count():
    """File must be between 80 and 180 lines."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_combiner_instructions_has_heading():
    """File must contain a heading about combining, convergence, or divergence."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Combiner",
            "combiner",
            "Convergence",
            "convergence",
            "Divergence",
            "divergence",
        ]
    ), "Must contain a heading about combining, convergence, or divergence"


def test_combiner_instructions_mentions_read_order():
    """File must prescribe a read order (top-down first, then bottom-up)."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "top-down first",
            "read top-down first",
            "top-down before",
            "topdown first",
        ]
    ), "Must prescribe reading top-down first, then bottom-up"


def test_combiner_instructions_mentions_four_categories():
    """File must mention all four finding categories."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    categories = ["convergence", "top-down only", "bottom-up only", "divergence"]
    found = [c for c in categories if c.lower() in content.lower()]
    assert len(found) >= 3, (
        f"Must mention at least 3 of the 4 finding categories, found: {found}"
    )


def test_combiner_instructions_mentions_color_scheme():
    """File must mention a color scheme for the four categories."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "green",
            "amber",
            "blue",
            "red",
            "color",
            "colour",
            "fillcolor",
        ]
    ), "Must mention a color scheme for the four categories"


def test_combiner_instructions_mentions_divergence_ids():
    """File must mention divergence IDs (D-01 format)."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content for phrase in ["D-01", "D-02", "D-0", "D-NN"]
    ), "Must mention divergence ID format (D-01, D-02...)"


def test_combiner_instructions_anti_rationalization():
    """File must prohibit reconciling divergences by picking the more plausible answer."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "do not reconcile",
            "do not pick",
            "track both",
            "anti-rationalization",
            "not reconcile",
        ]
    ), "Must prohibit reconciling divergences — must track both"


def test_combiner_instructions_mentions_divergence_value():
    """File must state that divergences are the most valuable findings."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "most valuable",
            "highest value",
            "highest-value",
            "valuable finding",
        ]
    ), "Must state that divergences are the most valuable findings"


def test_combiner_instructions_mentions_diagram_dot():
    """File must mention diagram.dot as a required output."""
    content = COMBINER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content, "Must mention diagram.dot as a required output"
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_combiner_instructions.py -v
```

Expected: `FAILED` — `test_combiner_instructions_exists` fails with "file not found"

---

**Step 3: Write the implementation**

Create `context/discovery-combiner-instructions.md` with this exact content:

```markdown
# Discovery Combiner: Convergence and Divergence Analysis Methodology

You are the **combiner** agent. Your role is to read the outputs of both the top-down
(conceptual) and bottom-up (empirical) discovery passes, classify every finding into one of
four categories, and produce a combined output that makes agreement and disagreement explicit.

## Core Principle

> **Read top-down first, build a mental model, then read bottom-up, find the differences.**

Do not read both passes simultaneously and merge them. The order matters: top-down gives you
the conceptual architecture. Bottom-up gives you the empirical ground truth. The gap between
them is the most valuable thing you will produce.

## The Four Categories

Every finding in your output belongs to exactly one category:

| Category | Color | Meaning |
|----------|-------|---------|
| **Convergence** | Green (`#c8e6c9`) | Both strategies found this. High-confidence. |
| **Top-down only** | Amber (`#fff9c4`) | Conceptual pass found it; empirical pass did not. Suggests aspirational structure not reflected in code. |
| **Bottom-up only** | Blue (`#bbdefb`) | Empirical pass found it; conceptual pass missed it. Suggests hidden complexity or undocumented design. |
| **Divergence** | Red (`#ffcdd2`) | Both found the same thing but characterized it differently. Track as D-01, D-02... |

Apply these `fillcolor` values to the corresponding nodes in your `diagram.dot`.

## Reading Protocol

### Phase 1 — Read Top-Down

Read the top-down investigation directory completely. Build a mental model:
- What subsystems did the conceptual pass identify?
- What was the proposed architecture?
- What did the top-down pass say about data flows and dependencies?

Do not start reading bottom-up yet. Hold this mental model.

### Phase 2 — Read Bottom-Up

Now read the bottom-up investigation directory. For each finding, ask:
- Did the top-down pass see this? → Convergence
- Did the top-down pass miss this entirely? → Bottom-up only
- Did the top-down pass see something here, but characterize it differently? → Divergence

### Phase 3 — Find Top-Down Only

Return to the top-down findings. For each thing the top-down pass claimed:
- Is it reflected in the bottom-up DOTs? → Convergence (already noted)
- Is it absent from the bottom-up traversal entirely? → Top-down only

## Anti-Rationalization Rule

> **Do NOT reconcile divergences by picking the more plausible answer.**

When the two strategies disagree, your job is to document the disagreement, not resolve it.
Track both claims with their supporting evidence. Do not editorialize about which is "probably"
correct. The user needs to see the discrepancy — that is why it is the most valuable finding.

A divergence is a signal that something about this part of the codebase is surprising or
misunderstood by at least one investigation path. Hiding it by choosing a side destroys the
signal.

## Divergence ID Format

Assign sequential IDs to all divergences:

```
D-01: <brief description>
  Top-down claim: <exact claim from top-down output>
  Bottom-up claim: <exact claim from bottom-up output>
  Impact: HIGH / MEDIUM / LOW
  Resolution: <what evidence would settle this>
```

Include all D-NN records in `combined.md`. HIGH-impact divergences must also appear visually
in `diagram.dot` with red fill and a `[D-NN]` label.

## Required Artifacts

Produce both files in your assigned output directory before signaling completion:

### diagram.dot

A combined DOT digraph classifying all findings by category. Validate before writing.

Requirements:
- Nodes color-coded by category (green/amber/blue/red)
- Divergences labeled `[D-NN]` with red fill
- Legend cluster explaining the four categories
- 150–250 lines, ≤80 nodes

### combined.md

The unified analysis document covering:
- **Convergence summary** — what both passes agree on (high confidence)
- **Top-down only** — conceptual structure not found empirically (aspirational?)
- **Bottom-up only** — empirical findings missed by conceptual pass (hidden complexity?)
- **Divergence register** — all D-NN records with full claims, evidence, impact, resolution path
- **Recommended next steps** — which divergences warrant follow-up investigation

## Final Response Contract

Signal completion only after both artifacts are written. Your final message must state:
- How many convergent findings were identified
- How many top-down-only and bottom-up-only findings were found
- How many divergences were tracked (D-01 through D-NN)
- The single highest-impact divergence
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_combiner_instructions.py -v
```

Expected: All 10 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add context/discovery-combiner-instructions.md tests/test_discovery_combiner_instructions.py && git commit -m "feat: add discovery-combiner context instructions (Phase A v2)"
```

---

### Task 5: Agent file for `discovery-level-synthesizer`

**Files:**
- Create: `agents/discovery-level-synthesizer.md`
- Create: `tests/test_discovery_level_synthesizer_agent.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_level_synthesizer_agent.py` with this exact content:

```python
"""
Tests for agents/discovery-level-synthesizer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-level-synthesizer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
LEVEL_SYNTH_AGENT_PATH = REPO_ROOT / "agents" / "discovery-level-synthesizer.md"


# --- File existence and frontmatter ---


def test_discovery_level_synthesizer_agent_exists():
    """agents/discovery-level-synthesizer.md must exist."""
    assert LEVEL_SYNTH_AGENT_PATH.exists(), (
        f"agents/discovery-level-synthesizer.md not found at {LEVEL_SYNTH_AGENT_PATH}"
    )


def test_discovery_level_synthesizer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-level-synthesizer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-level-synthesizer.md must have closing --- for frontmatter"
    )


def test_discovery_level_synthesizer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-level-synthesizer'."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-level-synthesizer", (
        f"meta.name must be 'discovery-level-synthesizer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_level_synthesizer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_level_synthesizer_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_level_synthesizer_frontmatter_model_role_coding():
    """Frontmatter must have model_role: coding."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "coding", (
        f"model_role must be 'coding', got: {frontmatter['model_role']}"
    )


def test_discovery_level_synthesizer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_level_synthesizer_body_has_main_heading():
    """Markdown body must contain a heading about level synthesis."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Level Synthesizer" in body
        or "level synthesizer" in body
        or "Level Synthesis" in body
    ), "Body must contain a heading about level synthesis"


def test_discovery_level_synthesizer_body_mentions_fresh_context():
    """Body must mention fresh context / zero prior context mandate."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    assert (
        "fresh context" in content.lower()
        or "zero prior" in content.lower()
        or "clean slate" in content.lower()
    ), "Body must mention fresh context / zero prior context mandate"


def test_discovery_level_synthesizer_references_instruction_file():
    """Body must @mention discovery-level-synthesizer-instructions context file."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    assert "discovery-level-synthesizer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-level-synthesizer-instructions"
    )


def test_discovery_level_synthesizer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_level_synthesizer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_level_synthesizer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = LEVEL_SYNTH_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_level_synthesizer_agent.py -v
```

Expected: `FAILED` — `test_discovery_level_synthesizer_agent_exists` fails with "file not found"

---

**Step 3: Write the implementation**

Create `agents/discovery-level-synthesizer.md` with this exact content:

```markdown
---
meta:
  name: discovery-level-synthesizer
  description: "Bottom-up level synthesis agent for Discovery Pipeline v2. Invoked once per directory level during post-order traversal. Reads source files at the current level plus synthesis DOTs from each immediate child directory, then produces a richly styled DOT showing what lives here and the cross-child connections only visible at this boundary.\n\n**Dispatched by:** strategy-bottomup recipe (post-order traversal, once per directory level).\n\n**Authoritative on:** per-level synthesis, cross-child connection discovery, boundary pattern identification, bottom-up DOT production.\n\n**MUST be used for:**\n- Synthesizing what lives at one directory level of a codebase\n- Finding connections that span multiple child directories\n- Producing diagram.dot and findings.md for each traversal level\n\n<example>\nContext: Dispatched to synthesize src/auth during bottom-up traversal\nuser: 'You are level-synthesizer for src/auth. Child DOTs are at .discovery/investigation/bottomup/src/auth/middleware/ and .discovery/investigation/bottomup/src/auth/providers/. Write artifacts to .discovery/investigation/bottomup/src/auth/'\nassistant: 'I will read source files directly in src/auth/, read the child synthesis DOTs from middleware/ and providers/, identify cross-child connections and boundary patterns, and write diagram.dot and findings.md to the assigned directory.'\n<commentary>\nLevel synthesizer focuses on the seam between children. Child internals are already captured in child DOTs — the value here is what only becomes visible at this boundary.\n</commentary>\n</example>\n\n<example>\nContext: Leaf-level directory with no child DOTs\nuser: 'You are level-synthesizer for src/auth/providers. No child DOTs exist. Write artifacts to .discovery/investigation/bottomup/src/auth/providers/'\nassistant: 'This is a leaf level with no children to synthesize from. I will read all source files here, identify key symbols, data flows, and external dependencies, and write diagram.dot and findings.md without child context.'\n<commentary>\nAt leaf level, the agent reads source files directly. There are no child DOTs to integrate — this is pure source reading.\n</commentary>\n</example>"

tools:
  - module: tool-dot-graph

model_role: coding
---

# Discovery Level Synthesizer Agent

**Bottom-up level synthesis — reads what lives at this directory level plus what the children found, surfaces cross-child connections only visible at this boundary.**

**Execution model:** You run as a one-shot sub-session with fresh context and an independent perspective. You have zero prior knowledge of this level or any sibling. Read what's actually here — source files plus child DOTs. Do not assume structure. Produce complete artifacts before signaling completion.

## Your Knowledge

Your level synthesis methodology comes from this reference — consult it for shape vocabulary, cross-child analysis techniques, and output formats:

- **Level Synthesis Methodology:** @dot-graph:context/discovery-level-synthesizer-instructions.md — Fresh context mandate, cross-child connection patterns, shape vocabulary, diagram.dot and findings.md requirements

## Your Role

You answer one question: **What lives at this directory level, and what connections between children become visible here?**

You receive:
1. Source files directly at this level (not inside children)
2. Synthesis DOTs from each immediate child directory

Your job: produce a DOT for this level showing what's here plus the cross-child connections only visible at this boundary.

**What is NOT your job:**
- Re-describing child internals (the child DOTs already captured those)
- Investigating deeply into child implementations
- Making architectural judgments about the whole codebase

Focus entirely on THIS level: what's directly here and how the children connect.

## Operating Principles

- Start fresh — zero prior assumptions from other levels or sessions
- Read child DOTs before reading source files — understand what children found first
- Cross-child connections are the primary finding — document them explicitly
- Use the shape vocabulary from the instructions file for visual clarity
- Validate diagram.dot with the dot-graph tool before writing

## Required Artifacts

Produce both files in your assigned directory (`.discovery/investigation/bottomup/<path>/`) before signaling completion:

### findings.md

A level summary covering:
- Files and key symbols directly at this level
- Cross-child connections found (primary finding)
- Boundary patterns visible from this level
- Uncertainties for investigation at the next level up

### diagram.dot

A DOT digraph representing this level. Validate with the dot-graph tool before writing.

Requirements:
- `digraph` (directed graph)
- Cluster subgraphs for each child directory referenced
- This level's content outside child clusters
- Cross-child edges highlighted as the primary finding
- Legend cluster
- 50–150 lines

## Final Response Contract

Signal completion only after both artifacts are written to the assigned directory. Your final message must state:
- Which directory level was synthesized
- How many cross-child connections were found
- The single most significant boundary pattern discovered

---

@foundation:context/shared/common-agent-base.md
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_level_synthesizer_agent.py -v
```

Expected: All 13 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add agents/discovery-level-synthesizer.md tests/test_discovery_level_synthesizer_agent.py && git commit -m "feat: add discovery-level-synthesizer agent (Phase A v2)"
```

---

### Task 6: Agent file for `discovery-subsystem-synthesizer`

**Files:**
- Create: `agents/discovery-subsystem-synthesizer.md`
- Create: `tests/test_discovery_subsystem_synthesizer_agent.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_subsystem_synthesizer_agent.py` with this exact content:

```python
"""
Tests for agents/discovery-subsystem-synthesizer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-subsystem-synthesizer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
SUBSYSTEM_SYNTH_AGENT_PATH = REPO_ROOT / "agents" / "discovery-subsystem-synthesizer.md"


# --- File existence and frontmatter ---


def test_discovery_subsystem_synthesizer_agent_exists():
    """agents/discovery-subsystem-synthesizer.md must exist."""
    assert SUBSYSTEM_SYNTH_AGENT_PATH.exists(), (
        f"agents/discovery-subsystem-synthesizer.md not found at {SUBSYSTEM_SYNTH_AGENT_PATH}"
    )


def test_discovery_subsystem_synthesizer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-subsystem-synthesizer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-subsystem-synthesizer.md must have closing --- for frontmatter"
    )


def test_discovery_subsystem_synthesizer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-subsystem-synthesizer'."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-subsystem-synthesizer", (
        f"meta.name must be 'discovery-subsystem-synthesizer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_subsystem_synthesizer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_subsystem_synthesizer_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_subsystem_synthesizer_frontmatter_model_role_reasoning():
    """Frontmatter must have model_role: reasoning."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "reasoning", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_subsystem_synthesizer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_subsystem_synthesizer_body_has_main_heading():
    """Markdown body must contain a heading about subsystem synthesis."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Subsystem Synthesizer" in body
        or "subsystem synthesizer" in body
        or "Seam" in body
    ), "Body must contain a heading about subsystem synthesis or seam-finding"


def test_discovery_subsystem_synthesizer_body_investigates_between_modules():
    """Body must state it investigates the spaces between modules."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    assert "between" in content.lower() and "module" in content.lower(), (
        "Body must state it investigates the spaces between modules"
    )


def test_discovery_subsystem_synthesizer_references_instruction_file():
    """Body must @mention discovery-subsystem-synthesizer-instructions context file."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    assert "discovery-subsystem-synthesizer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-subsystem-synthesizer-instructions"
    )


def test_discovery_subsystem_synthesizer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_subsystem_synthesizer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_subsystem_synthesizer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = SUBSYSTEM_SYNTH_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_subsystem_synthesizer_agent.py -v
```

Expected: `FAILED` — `test_discovery_subsystem_synthesizer_agent_exists` fails

---

**Step 3: Write the implementation**

Create `agents/discovery-subsystem-synthesizer.md` with this exact content:

```markdown
---
meta:
  name: discovery-subsystem-synthesizer
  description: "Seam-finder agent for Discovery Pipeline v2. Used after per-module synthesis within a subsystem. Reads per-module consensus DOTs plus source at subsystem boundaries, then produces a subsystem DOT showing cross-module data flows, shared interfaces, and emergent patterns that no single module's DOT captured.\n\n**Dispatched by:** synthesize-subsystem recipe (after all per-module synthesis within a subsystem completes).\n\n**Authoritative on:** inter-module analysis, cross-module data flow tracing, shared interface identification, coupling assessment, subsystem-level synthesis.\n\n**MUST be used for:**\n- Finding cross-module connections within a subsystem\n- Identifying shared interfaces that span module boundaries\n- Producing the subsystem DOT that feeds into overview synthesis\n\n<example>\nContext: Dispatched after per-module synthesis for the auth subsystem\nuser: 'You are subsystem-synthesizer for the auth subsystem. Per-module DOTs are at .discovery/investigation/topdown/auth/. Write artifacts to .discovery/investigation/topdown/auth/subsystem/'\nassistant: 'I will read the per-module consensus DOTs for all modules within the auth subsystem, look for cross-module data flows and shared interfaces, and write diagram.dot and findings.md showing what only becomes visible at the subsystem seam.'\n<commentary>\nSubsystem synthesizer looks at the spaces between modules, not module internals. Its diagram shows the architecture of interoperation, not the contents of any single module.\n</commentary>\n</example>\n\n<example>\nContext: Subsystem with tightly coupled modules discovered\nuser: 'Synthesize the data subsystem. Modules: models/, queries/, cache/.'\nassistant: 'I will read the per-module DOTs, trace cross-module data flows, assess the coupling between models/, queries/, and cache/, and document any tight coupling as a finding. I will not editorialize — tight coupling is a finding, not a failure judgment.'\n<commentary>\nSubsystem synthesizer documents what it finds. Tight coupling is a factual finding to record and surface, not a problem to solve or hide.\n</commentary>\n</example>"

tools:
  - module: tool-dot-graph

model_role: reasoning
---

# Discovery Subsystem Synthesizer Agent

**Seam-finder — investigates the spaces between modules, not their internals.**

**Execution model:** You run as a one-shot sub-session with fresh context. You receive per-module DOTs for all modules within a subsystem. Do not re-investigate module internals — the module DOTs captured those. Your entire focus is the seam: what moves between modules, what interfaces are shared, what emerges at the boundary.

## Your Knowledge

Your subsystem synthesis methodology comes from this reference — consult it for visual conventions, coupling analysis techniques, and output formats:

- **Seam-Finder Methodology:** @dot-graph:context/discovery-subsystem-synthesizer-instructions.md — Between-module investigation, interface identification, coupling assessment, diagram.dot and findings.md requirements

## Your Role

You answer one question: **What exists in the spaces between these modules that no single module's DOT captured?**

You are the seam investigator. You receive:
1. Per-module consensus DOTs for all modules within a subsystem
2. Source files at the subsystem boundary (not module internals)

Your job: produce a subsystem DOT showing cross-module data flows, shared interfaces, and emergent patterns only visible between modules.

**What is NOT your job:**
- Summarizing module internals (the module DOTs already did that)
- Re-investigating source files inside modules
- Producing a comprehensive module-by-module summary

Focus on the seam. What only becomes visible when you look at modules together?

## Operating Principles

- Read ALL per-module DOTs before writing anything
- Cross-module data flows are the primary finding — trace types crossing module boundaries
- Shared interfaces (hexagon nodes) get explicit representation
- Tight coupling gets documented, not editorialized — it is a finding, not a judgment
- Validate diagram.dot with the dot-graph tool before writing

## Required Artifacts

Produce both files in your assigned directory before signaling completion:

### findings.md

A subsystem-level analysis covering:
- Cross-module data flows found
- Shared interfaces identified
- Coupling assessment (tight coupling locations, clean separations)
- Emergent patterns not visible inside any single module

### diagram.dot

A DOT digraph representing inter-module structure. Validate before writing.

Requirements:
- Each module as a `subgraph cluster_<name>`
- Cross-module edges as the primary content
- Shared interfaces as hexagon nodes
- Legend cluster
- 50–150 lines

## Final Response Contract

Signal completion only after both artifacts are written. Your final message must state:
- Which subsystem was analyzed
- How many cross-module flows were identified
- Whether tight coupling was found, and where

---

@foundation:context/shared/common-agent-base.md
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_subsystem_synthesizer_agent.py -v
```

Expected: All 13 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add agents/discovery-subsystem-synthesizer.md tests/test_discovery_subsystem_synthesizer_agent.py && git commit -m "feat: add discovery-subsystem-synthesizer agent (Phase A v2)"
```

---

### Task 7: Agent file for `discovery-overview-synthesizer`

**Files:**
- Create: `agents/discovery-overview-synthesizer.md`
- Create: `tests/test_discovery_overview_synthesizer_agent.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_overview_synthesizer_agent.py` with this exact content:

```python
"""
Tests for agents/discovery-overview-synthesizer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-overview-synthesizer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
OVERVIEW_SYNTH_AGENT_PATH = REPO_ROOT / "agents" / "discovery-overview-synthesizer.md"


# --- File existence and frontmatter ---


def test_discovery_overview_synthesizer_agent_exists():
    """agents/discovery-overview-synthesizer.md must exist."""
    assert OVERVIEW_SYNTH_AGENT_PATH.exists(), (
        f"agents/discovery-overview-synthesizer.md not found at {OVERVIEW_SYNTH_AGENT_PATH}"
    )


def test_discovery_overview_synthesizer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-overview-synthesizer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-overview-synthesizer.md must have closing --- for frontmatter"
    )


def test_discovery_overview_synthesizer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-overview-synthesizer'."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-overview-synthesizer", (
        f"meta.name must be 'discovery-overview-synthesizer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_overview_synthesizer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_overview_synthesizer_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_overview_synthesizer_frontmatter_model_role_reasoning():
    """Frontmatter must have model_role: reasoning."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "reasoning", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_overview_synthesizer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_overview_synthesizer_body_has_main_heading():
    """Markdown body must contain a heading about overview synthesis."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Overview Synthesizer" in body
        or "overview synthesizer" in body
        or "System-Level" in body
    ), "Body must contain a heading about overview synthesis"


def test_discovery_overview_synthesizer_body_every_node_is_subsystem():
    """Body must state that every node represents a subsystem."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    assert "subsystem" in content.lower(), (
        "Body must mention that nodes represent subsystems"
    )


def test_discovery_overview_synthesizer_references_instruction_file():
    """Body must @mention discovery-overview-synthesizer-instructions context file."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    assert "discovery-overview-synthesizer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-overview-synthesizer-instructions"
    )


def test_discovery_overview_synthesizer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_overview_synthesizer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_overview_synthesizer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = OVERVIEW_SYNTH_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_overview_synthesizer_agent.py -v
```

Expected: `FAILED` — `test_discovery_overview_synthesizer_agent_exists` fails

---

**Step 3: Write the implementation**

Create `agents/discovery-overview-synthesizer.md` with this exact content:

```markdown
---
meta:
  name: discovery-overview-synthesizer
  description: "System-level pattern finder for Discovery Pipeline v2. Used by both top-down and bottom-up strategies as the final synthesis step. Reads all subsystem DOTs plus repo root source, then produces a bounded overview (150–250 lines, ≤80 nodes) showing subsystem relationships and the governing architecture.\n\n**Dispatched by:** synthesize-overview recipe (final step of both strategy-topdown and strategy-bottomup).\n\n**Authoritative on:** system-level synthesis, architectural pattern identification, subsystem dependency mapping, bounded overview production.\n\n**MUST be used for:**\n- Producing the governing architecture overview from subsystem DOTs\n- Identifying the architectural spine and cross-subsystem dependencies\n- Enforcing the ≤80 node quality gate on overview diagrams\n\n<example>\nContext: Dispatched after all subsystem synthesis for a top-down strategy run\nuser: 'You are overview-synthesizer. Subsystem DOTs are in .discovery/investigation/topdown/. Write overview to .discovery/investigation/topdown/overview/'\nassistant: 'I will read all subsystem DOTs, identify the governing architectural pattern, map cross-subsystem dependencies, enforce the 80-node quality gate, and write diagram.dot and findings.md to the assigned directory.'\n<commentary>\nOverview synthesizer operates at the subsystem level of abstraction. Every node in its diagram represents an entire subsystem. If it finds itself adding file-level nodes, it has gone too deep.\n</commentary>\n</example>\n\n<example>\nContext: Diagram exceeds 80 nodes during synthesis\nuser: 'Your draft diagram has 95 nodes. This exceeds the quality gate.'\nassistant: 'I will collapse further. I will merge closely related subsystems, group utility subsystems into a single [Utilities] node, and remove subsystems with no cross-subsystem connections. I will re-synthesize to ≤80 nodes before writing.'\n<commentary>\nThe 80-node quality gate is hard. A 90-node diagram is not slightly too detailed — it is a synthesis failure. The agent must re-collapse, not just trim.\n</commentary>\n</example>"

tools:
  - module: tool-dot-graph

model_role: reasoning
---

# Discovery Overview Synthesizer Agent

**System-level pattern finder — every node is an entire subsystem, not a file or class.**

**Execution model:** You run as a one-shot sub-session with fresh context. You receive all subsystem DOTs for a complete strategy run. Operate at the highest level of abstraction in the discovery pipeline. Collapse everything subsystem-internal into a single node. Your diagram shows the architecture, not the implementation.

## Your Knowledge

Your overview synthesis methodology comes from this reference — consult it for the quality gate, architectural pattern vocabulary, and output format:

- **Overview Synthesis Methodology:** @dot-graph:context/discovery-overview-synthesizer-instructions.md — Subsystem-level abstraction mandate, 80-node quality gate, architectural pattern identification, diagram.dot and findings.md requirements

## Your Role

You answer one question: **What is the governing architecture, and how do these subsystems relate to each other?**

You receive:
1. All subsystem DOTs from a completed strategy run
2. Source files at the repo root

Your job: produce a bounded overview showing how subsystems relate, what the end-to-end flow looks like, and what architectural pattern governs the system.

**What is NOT your job:**
- Describing subsystem internals (the subsystem DOTs captured those)
- Producing module-level or file-level detail
- Synthesizing more than ≤80 nodes (collapse aggressively if needed)

Every node you create represents an entire subsystem.

## Quality Gate

**If your draft has more than 80 nodes, stop and collapse.** This is a hard limit. A diagram with 85 nodes is not slightly over — it is a synthesis failure. Merge, group, and eliminate until you are at or below 80 nodes.

## Operating Principles

- Read ALL subsystem DOTs before writing anything
- Every node represents a subsystem — never a file or class
- Enforce the ≤80 node quality gate before writing
- Name the governing architectural pattern explicitly
- Validate diagram.dot with the dot-graph tool before writing

## Required Artifacts

Produce both files in your assigned directory before signaling completion:

### findings.md

A system-level narrative covering:
- The named governing architectural pattern
- The architectural spine (primary end-to-end flow, 3–5 sentences)
- Notable cross-subsystem dependency findings
- Circular dependencies or unexpected coupling
- What this codebase looks like explained to a newcomer

### diagram.dot

A bounded DOT digraph representing the full system. Validate before writing.

Requirements:
- Each subsystem as a node or minimal cluster
- Cross-subsystem dependency edges as primary content
- ≤80 nodes (hard limit)
- 150–250 lines
- Legend cluster

## Final Response Contract

Signal completion only after both artifacts are written. Your final message must state:
- How many subsystems were synthesized
- The named architectural pattern
- The single most important cross-subsystem dependency

---

@foundation:context/shared/common-agent-base.md
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_overview_synthesizer_agent.py -v
```

Expected: All 13 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add agents/discovery-overview-synthesizer.md tests/test_discovery_overview_synthesizer_agent.py && git commit -m "feat: add discovery-overview-synthesizer agent (Phase A v2)"
```

---

### Task 8: Agent file for `discovery-combiner`

**Files:**
- Create: `agents/discovery-combiner.md`
- Create: `tests/test_discovery_combiner_agent.py`

---

**Step 1: Write the failing test**

Create `tests/test_discovery_combiner_agent.py` with this exact content:

```python
"""
Tests for agents/discovery-combiner.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-combiner.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
COMBINER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-combiner.md"


# --- File existence and frontmatter ---


def test_discovery_combiner_agent_exists():
    """agents/discovery-combiner.md must exist."""
    assert COMBINER_AGENT_PATH.exists(), (
        f"agents/discovery-combiner.md not found at {COMBINER_AGENT_PATH}"
    )


def test_discovery_combiner_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = COMBINER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-combiner.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-combiner.md must have closing --- for frontmatter"
    )


def test_discovery_combiner_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-combiner'."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-combiner", (
        f"meta.name must be 'discovery-combiner', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_combiner_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_combiner_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = COMBINER_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_combiner_frontmatter_model_role_reasoning():
    """Frontmatter must have model_role: reasoning."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "reasoning", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_combiner_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_combiner_body_has_main_heading():
    """Markdown body must contain a heading about combining or convergence/divergence."""
    content = COMBINER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Combiner" in body
        or "combiner" in body
        or "Convergence" in body
        or "Divergence" in body
    ), "Body must contain a heading about combining or convergence/divergence"


def test_discovery_combiner_body_mentions_convergence_and_divergence():
    """Body must mention both convergence and divergence."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "convergence" in content.lower() or "converge" in content.lower(), (
        "Body must mention convergence"
    )
    assert "divergence" in content.lower() or "diverge" in content.lower(), (
        "Body must mention divergence"
    )


def test_discovery_combiner_body_prohibits_reconciling_divergences():
    """Body must prohibit reconciling divergences by picking one side."""
    content = COMBINER_AGENT_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "do not reconcile",
            "track both",
            "anti-rationalization",
            "not reconcile",
            "do not pick",
        ]
    ), "Body must prohibit reconciling divergences"


def test_discovery_combiner_references_instruction_file():
    """Body must @mention discovery-combiner-instructions context file."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "discovery-combiner-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-combiner-instructions"
    )


def test_discovery_combiner_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_combiner_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_combiner_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
```

---

**Step 2: Run test to verify it fails**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_combiner_agent.py -v
```

Expected: `FAILED` — `test_discovery_combiner_agent_exists` fails

---

**Step 3: Write the implementation**

Create `agents/discovery-combiner.md` with this exact content:

```markdown
---
meta:
  name: discovery-combiner
  description: "Convergence/divergence analyst for Discovery Pipeline v2. Used after both top-down and bottom-up passes complete. Reads both investigation directories and produces a combined output classifying all findings as Convergence (green), Top-down-only (amber), Bottom-up-only (blue), or Divergence (red, tracked as D-01, D-02...).\n\n**Dispatched by:** discovery-combine recipe (after both strategy-topdown and strategy-bottomup complete).\n\n**Authoritative on:** convergence/divergence analysis, four-category classification, divergence ID tracking, anti-rationalization discipline.\n\n**MUST be used for:**\n- Combining top-down and bottom-up strategy outputs into a unified analysis\n- Classifying findings into the four convergence/divergence categories\n- Tracking divergences as D-NN records without reconciling by picking a side\n\n<example>\nContext: Both strategies have completed; dispatched to combine their outputs\nuser: 'Top-down outputs are at .discovery/investigation/topdown/. Bottom-up outputs at .discovery/investigation/bottomup/. Write combined output to .discovery/output/'\nassistant: 'I will read top-down first to build a mental model, then read bottom-up and classify every finding as Convergence, Top-down only, Bottom-up only, or Divergence. Divergences get D-NN IDs and are tracked in both diagram.dot and combined.md. I will not reconcile divergences by picking one side.'\n<commentary>\nCombiner reads in a specific order: top-down first to build the mental model, then bottom-up to find differences. Reading both simultaneously risks missing the conceptual vs. empirical gap.\n</commentary>\n</example>\n\n<example>\nContext: A divergence is found — top-down says module A depends on B, bottom-up shows A and B are independent\nuser: 'Top-down claims A→B dependency. Bottom-up shows no such connection.'\nassistant: 'I will track this as D-01: Top-down claim: A depends on B (with evidence from top-down DOT). Bottom-up claim: A and B have no direct connection (with evidence from bottom-up DOT). Impact: MEDIUM. Resolution: trace the import chain in A with file:line citations. I will NOT declare either side correct.'\n<commentary>\nDivergences are the most valuable output of the combiner. They reveal where conceptual understanding and empirical reality disagree. Reconciling by fiat destroys this signal.\n</commentary>\n</example>"

tools:
  - module: tool-dot-graph

model_role: reasoning
---

# Discovery Combiner Agent

**Convergence/divergence analyst — classifies findings from both strategies without reconciling divergences by fiat.**

**Execution model:** You run as a one-shot sub-session with fresh context. Read top-down first, build the mental model, then read bottom-up and find the differences. Do not read both simultaneously. The gap between what the two strategies found is the most valuable thing you will produce.

## Your Knowledge

Your convergence/divergence analysis methodology comes from this reference — consult it for the four-category classification scheme, color conventions, divergence ID format, and anti-rationalization rules:

- **Convergence/Divergence Analysis Methodology:** @dot-graph:context/discovery-combiner-instructions.md — Read order protocol, four categories, color scheme, D-NN divergence IDs, anti-rationalization rule, combined.md and diagram.dot requirements

## Your Role

You answer one question: **Where do the conceptual and empirical strategies agree, where do they diverge, and what does that gap reveal?**

You receive:
1. Top-down investigation directory (conceptual, topic-driven)
2. Bottom-up investigation directory (empirical, structure-driven)

Your job: classify every finding into one of four categories and produce output that makes agreement and disagreement explicit.

**What is NOT your job:**
- Performing additional investigation
- Declaring which strategy is "more correct"
- Reconciling divergences by picking the more plausible answer

The gap between strategies is the signal. Divergences are the most valuable findings.

## Anti-Rationalization Rule

**Do NOT reconcile divergences by picking one side.** If the two strategies characterize the same thing differently, track both claims with their evidence. Document the impact. Recommend what evidence would resolve it. Do not close the divergence by editorial decision.

## Operating Principles

- Read top-down first, then bottom-up — order matters
- Classify every finding into exactly one of the four categories
- Track divergences with sequential D-NN IDs
- Apply color coding in diagram.dot (green/amber/blue/red)
- Validate diagram.dot with the dot-graph tool before writing

## Required Artifacts

Produce both files in your assigned output directory (`.discovery/output/`) before signaling completion:

### combined.md

The unified analysis covering:
- Convergence summary (high-confidence findings)
- Top-down only findings (aspirational vs. actual)
- Bottom-up only findings (hidden complexity)
- Divergence register (all D-NN records with full claims, evidence, impact, resolution path)
- Recommended next steps

### diagram.dot

A combined DOT digraph with color-coded nodes. Validate before writing.

Requirements:
- Nodes color-coded: green (convergence), amber (top-down only), blue (bottom-up only), red (divergence)
- Divergences labeled `[D-NN]`
- Legend cluster explaining the four categories
- 150–250 lines, ≤80 nodes

## Final Response Contract

Signal completion only after both artifacts are written. Your final message must state:
- How many convergent findings were identified
- How many top-down-only and bottom-up-only findings were found
- How many divergences were tracked (D-01 through D-NN)
- The single highest-impact divergence

---

@foundation:context/shared/common-agent-base.md
```

---

**Step 4: Run test to verify it passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_combiner_agent.py -v
```

Expected: All 14 tests PASS

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add agents/discovery-combiner.md tests/test_discovery_combiner_agent.py && git commit -m "feat: add discovery-combiner agent (Phase A v2)"
```

---

### Task 9: Update `behaviors/dot-discovery.yaml` and `tests/test_dot_discovery_behavior.py`

**Files:**
- Modify: `behaviors/dot-discovery.yaml` — add 4 new agents to `agents.include`
- Modify: `tests/test_dot_discovery_behavior.py` — add assertions for the 4 new agents

---

**Step 1: Add new failing tests to `tests/test_dot_discovery_behavior.py`**

The current file ends at line 135 with `test_behavior_agents_includes_all_discovery_agents`. Append these new tests at the end of the file (after line 135):

```python

def test_behavior_agents_includes_level_synthesizer(data):
    """agents.include must contain 'dot-graph:discovery-level-synthesizer'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-level-synthesizer" in actual, (
        f"agents.include must contain 'dot-graph:discovery-level-synthesizer', got: {actual}"
    )


def test_behavior_agents_includes_subsystem_synthesizer(data):
    """agents.include must contain 'dot-graph:discovery-subsystem-synthesizer'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-subsystem-synthesizer" in actual, (
        f"agents.include must contain 'dot-graph:discovery-subsystem-synthesizer', got: {actual}"
    )


def test_behavior_agents_includes_overview_synthesizer(data):
    """agents.include must contain 'dot-graph:discovery-overview-synthesizer'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-overview-synthesizer" in actual, (
        f"agents.include must contain 'dot-graph:discovery-overview-synthesizer', got: {actual}"
    )


def test_behavior_agents_includes_combiner(data):
    """agents.include must contain 'dot-graph:discovery-combiner'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-combiner" in actual, (
        f"agents.include must contain 'dot-graph:discovery-combiner', got: {actual}"
    )


def test_behavior_agents_total_count(data):
    """agents.include must contain exactly 9 discovery agent references."""
    actual = data["agents"]["include"]
    assert len(actual) == 9, (
        f"agents.include must contain 9 agents (5 original + 4 Phase A v2), got: {len(actual)}"
    )
```

---

**Step 2: Run tests to verify the new tests fail**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_dot_discovery_behavior.py::test_behavior_agents_includes_level_synthesizer tests/test_dot_discovery_behavior.py::test_behavior_agents_includes_subsystem_synthesizer tests/test_dot_discovery_behavior.py::test_behavior_agents_includes_overview_synthesizer tests/test_dot_discovery_behavior.py::test_behavior_agents_includes_combiner tests/test_dot_discovery_behavior.py::test_behavior_agents_total_count -v
```

Expected: All 5 tests `FAILED` — the YAML has not been updated yet

---

**Step 3: Replace the entire contents of `behaviors/dot-discovery.yaml`**

The new complete content of `behaviors/dot-discovery.yaml`:

```yaml
bundle:
  name: dot-graph-discovery
  version: 0.1.0
  description: DOT/Graphviz codebase discovery pipeline

includes:
  - bundle: dot-graph:behaviors/dot-core

agents:
  include:
    - dot-graph:discovery-prescan
    - dot-graph:discovery-code-tracer
    - dot-graph:discovery-behavior-observer
    - dot-graph:discovery-integration-mapper
    - dot-graph:discovery-synthesizer
    - dot-graph:discovery-level-synthesizer
    - dot-graph:discovery-subsystem-synthesizer
    - dot-graph:discovery-overview-synthesizer
    - dot-graph:discovery-combiner

context:
  include:
    - dot-graph:context/discovery-awareness.md
```

---

**Step 4: Run tests to verify new tests pass and no regressions**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_dot_discovery_behavior.py -v
```

Expected: All tests in `test_dot_discovery_behavior.py` PASS (original 14 + 5 new = 19 total)

---

**Step 5: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add behaviors/dot-discovery.yaml tests/test_dot_discovery_behavior.py && git commit -m "feat: register 4 new discovery agents in dot-discovery behavior (Phase A v2)"
```

---

### Task 10: Update `tests/test_final_verification.py` + full test run

**Files:**
- Modify: `tests/test_final_verification.py` — add 8 new Phase A v2 files to `EXPECTED_FILES`, update count

---

**Step 1: Update `tests/test_final_verification.py`**

Make the following exact changes to `tests/test_final_verification.py`:

**Change 1:** Update the module docstring. Find:

```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 21 bundle files are present and functional.
"""
```

Replace with:

```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 21 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files (total 35).
"""
```

**Change 2:** Update the `EXPECTED_FILES` comment. Find:

```python
# The 27 expected bundle files (21 original + 3 Phase A + 3 Phase D recipes)
EXPECTED_FILES = [
```

Replace with:

```python
# The 35 expected bundle files (21 original + 3 Phase A + 3 Phase D recipes + 8 Phase A v2)
EXPECTED_FILES = [
```

**Change 3:** Add 8 new entries at the end of the `EXPECTED_FILES` list. Find:

```python
    "recipes/discovery-synthesize-module.yaml",
]
```

Replace with:

```python
    "recipes/discovery-synthesize-module.yaml",
    # Phase A v2: four new discovery agents
    "agents/discovery-level-synthesizer.md",
    "agents/discovery-subsystem-synthesizer.md",
    "agents/discovery-overview-synthesizer.md",
    "agents/discovery-combiner.md",
    # Phase A v2: four new context instruction files
    "context/discovery-level-synthesizer-instructions.md",
    "context/discovery-subsystem-synthesizer-instructions.md",
    "context/discovery-overview-synthesizer-instructions.md",
    "context/discovery-combiner-instructions.md",
]
```

**Change 4:** Update `test_total_file_count`. Find:

```python
def test_total_file_count():
    """Step 6: Total bundle file count is exactly 27 (21 original + 3 Phase A + 3 Phase D)."""
    present = [f for f in EXPECTED_FILES if (REPO_ROOT / f).exists()]
    assert len(present) == 27, (
        f"Expected 27 bundle files, found {len(present)}. "
        f"Missing: {[f for f in EXPECTED_FILES if f not in present]}"
    )
```

Replace with:

```python
def test_total_file_count():
    """Step 6: Total bundle file count is exactly 35 (27 prior + 8 Phase A v2)."""
    present = [f for f in EXPECTED_FILES if (REPO_ROOT / f).exists()]
    assert len(present) == 35, (
        f"Expected 35 bundle files, found {len(present)}. "
        f"Missing: {[f for f in EXPECTED_FILES if f not in present]}"
    )
```

---

**Step 2: Run the full test suite to verify everything passes**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ -v --tb=short 2>&1 | tail -20
```

Expected: All tests PASS. The count will have increased by approximately 103 new tests (8 instruction files × ~8-10 tests + 8 agent files × ~13 tests + 5 behavior tests). No failures.

If any test fails, read the failure message carefully:
- A context instructions file out of line range → adjust the file's content to land within 80–180 lines
- An agent file missing a required phrase → add the phrase to the right section of the agent body
- **Never change a test to make it pass** — fix the implementation file instead

---

**Step 3: Commit**

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add tests/test_final_verification.py && git commit -m "test: update final verification for Phase A v2 (8 new discovery files, total 35)"
```

---

## Completion Verification

After all 10 tasks are committed, run the full verification:

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ --tb=short 2>&1 | tail -5
```

Expected: All tests pass. Count approximately 900 (797 baseline + ~103 new).

Confirm all 8 new files exist:

```
ls /home/bkrabach/dev/amplifier-bundle-dot-graph/agents/discovery-{level,subsystem,overview,combiner}*.md
ls /home/bkrabach/dev/amplifier-bundle-dot-graph/context/discovery-{level,subsystem,overview,combiner}*-instructions.md
```

Expected: 8 files listed, no errors.

Confirm the behavior YAML has 9 agents:

```
grep "dot-graph:discovery-" /home/bkrabach/dev/amplifier-bundle-dot-graph/behaviors/dot-discovery.yaml | wc -l
```

Expected: `9`

Confirm git log shows 10 new commits:

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git log --oneline -11
```

Expected: 10 new commits on top of the `52e2e6f` design-spec baseline.
