# Level Findings: `docs/`

**Directory**: `/home/bkrabach/dev/dot-graph-bundle/amplifier/docs`  
**Level slug**: `docs`  
**Fidelity tier**: standard  
**Date**: 2026-03-20

---

## Files and Symbols at This Level

This is a flat documentation directory with **10 Markdown files** and no subdirectories synthesized at this pass. All files are at this level.

| File | Role | Audience | Frontmatter |
|------|------|----------|-------------|
| `README.md` | Audience-routing hub, documentation index | all | none |
| `MODULES.md` | Ecosystem component catalog (infrastructure, apps, libraries, bundles, modules, community) | all | none |
| `USER_ONBOARDING.md` | Getting-started guide: installation → first run | user | `audience: user, status: stable, last_updated: 2025-11-18` |
| `USER_GUIDE.md` | Complete user reference: configuration, sessions, providers, bundles | user | `audience: user, status: stable, last_updated: 2025-11-18` |
| `DEVELOPER.md` | AI-assisted module development guide ("use Amplifier to build Amplifier") | developer | none |
| `MODULE_DEVELOPMENT.md` | Module creation and testing workflows, override strategies | developer | `audience: developer, status: stable, last_updated: 2025-10-16` |
| `LOCAL_DEVELOPMENT.md` | Monorepo/multi-module development environment setup | developer | `audience: developer, status: stable, last_updated: 2025-10-16` |
| `TESTING_GUIDE.md` | Testing philosophy, test organization, patterns by module type | developer | `audience: developer, status: stable, last_updated: 2025-10-16` |
| `REPOSITORY_RULES.md` | Awareness hierarchy, dependency-based referencing, where content belongs | contributors / ecosystem | none |
| `ADR_TEMPLATE.md` | Template for Architecture Decision Records | contributors | none |

### Shared Concepts Across Multiple Files

These concepts appear in 3+ files, forming the invisible connective tissue of this doc set:

- **`amplifier-core` kernel contract** — appears in `DEVELOPER.md`, `MODULE_DEVELOPMENT.md`, `TESTING_GUIDE.md`. The `mount(coordinator, config)` entry-point protocol is the common anchor.
- **Module resolution 6-layer system** — described in both `LOCAL_DEVELOPMENT.md` and `MODULE_DEVELOPMENT.md`. Same content in both; potential drift risk.
- **`uv` as the package manager** — installation commands in `USER_ONBOARDING.md`, `LOCAL_DEVELOPMENT.md`, `MODULE_DEVELOPMENT.md`, `TESTING_GUIDE.md`.
- **Bundle configuration** — `USER_GUIDE.md`, `USER_ONBOARDING.md`, `MODULES.md` all describe bundles from different angles.
- **YAML frontmatter metadata** — 5 of 10 files have structured frontmatter (`audience`, `status`, `last_updated`); the other 5 do not. No enforcement mechanism is visible at this level.

---

## Cross-File Connections

These are explicit references (links) from one file to another within this directory. Files without subdirectories = files are the primary units of analysis.

| # | From | To | What Is Shared / Why |
|---|------|----|----------------------|
| 1 | `README.md` | `USER_ONBOARDING.md` | Routes new users: "Start here!" |
| 2 | `README.md` | `LOCAL_DEVELOPMENT.md` | Routes module developers to dev environment setup |
| 3 | `README.md` | `MODULE_DEVELOPMENT.md` | Routes module developers to module creation guide |
| 4 | `README.md` | `TESTING_GUIDE.md` | Routes module developers to test guide |
| 5 | `README.md` | `REPOSITORY_RULES.md` | (implicit — part of contributor path) |
| 6 | `USER_GUIDE.md` | `USER_ONBOARDING.md` | Sends users to config reference & clean-reinstall recovery |
| 7 | `USER_GUIDE.md` | `MODULES.md` | "See available modules" |
| 8 | `USER_GUIDE.md` | `DEVELOPER.md` | "Build your own" |
| 9 | `DEVELOPER.md` | `MODULES.md` | Add community module: "Add to MODULES.md" |
| 10 | `TESTING_GUIDE.md` | `MODULE_DEVELOPMENT.md` | Related docs: module development guide |
| 11 | `TESTING_GUIDE.md` | `LOCAL_DEVELOPMENT.md` | Related docs: environment setup |
| 12 | `MODULE_DEVELOPMENT.md` | `LOCAL_DEVELOPMENT.md` | Setup prerequisite, scenario examples reference it |
| 13 | `USER_ONBOARDING.md` | `USER_GUIDE.md` | References config reference / session management sections |

**Total cross-file connections: 13**

---

## Boundary Patterns

### Pattern 1: Audience-Discriminating Router (README.md)

**The most significant pattern at this level.** `README.md` acts as a single entry-point that routes readers into one of three distinct documentation paths based on audience:

- 🚀 **New Users** → `USER_ONBOARDING.md`, `USER_GUIDE.md`
- 👨‍💻 **Module Developers** → `LOCAL_DEVELOPMENT.md`, `MODULE_DEVELOPMENT.md`, `TESTING_GUIDE.md`
- 🏗️ **Contributors & Architects** → `REPOSITORY_RULES.md`, `ADR_TEMPLATE.md`, philosophy docs (in `context/` subdirectory not in this inventory)

This is not a simple index — `README.md` actively categorizes and discriminates by audience role, making it the only file in the directory that bridges all three audiences.

**Components**: `README.md` → `{USER_ONBOARDING, USER_GUIDE}` ∪ `{LOCAL_DEVELOPMENT, MODULE_DEVELOPMENT, TESTING_GUIDE}` ∪ `{REPOSITORY_RULES, ADR_TEMPLATE}`

---

### Pattern 2: Developer Workflow Triad

`LOCAL_DEVELOPMENT.md`, `MODULE_DEVELOPMENT.md`, and `TESTING_GUIDE.md` form a tightly coupled, complementary triad. Evidence:

- **Identical frontmatter**: All three share `audience: developer`, `status: stable`, `last_updated: 2025-10-16`
- **Explicit cross-linking**: `TESTING_GUIDE.md` links both siblings in its Related Documentation section; `MODULE_DEVELOPMENT.md` links `LOCAL_DEVELOPMENT.md` as a prerequisite
- **Sequential workflow coverage**: environment setup (LOCAL) → module creation (MODULE) → verification (TESTING)

These three documents could reasonably be tagged as a single curriculum unit.

---

### Pattern 3: User Journey Duality

`USER_ONBOARDING.md` and `USER_GUIDE.md` form a structured user progression:
- `USER_ONBOARDING.md` — first-time experience: installation, `amplifier init`, first run, environment variables
- `USER_GUIDE.md` — complete reference: configuration dimensions, session management, advanced usage

`USER_GUIDE.md` explicitly sends users *back* to `USER_ONBOARDING.md` for the clean-reinstall recovery procedure, creating a bidirectional relationship between these two.

---

### Pattern 4: Ecosystem Catalog as Registry (MODULES.md)

`MODULES.md` functions as a **central registry** for the entire Amplifier component ecosystem. Multiple audience paths converge on it:
- Users arrive via `USER_GUIDE.md` → "See available modules"
- Developers arrive via `DEVELOPER.md` → "Add your module to the community modules section"
- `README.md` references it implicitly via audience routing

It is the only file in this directory that catalogs external repositories (30+ bundles, 40+ modules, community contributions). No other file attempts to duplicate this scope.

---

### Pattern 5: Governance Layer (REPOSITORY_RULES.md + ADR_TEMPLATE.md)

`REPOSITORY_RULES.md` defines a **cross-ecosystem documentation contract** — the awareness hierarchy and dependency-based referencing rules that govern not just this directory, but all repositories in the Amplifier ecosystem. `ADR_TEMPLATE.md` provides the scaffold for recording architectural decisions following those rules.

These two files have a fundamentally different scope than all other files in this directory: they govern the ecosystem, not just document it.

---

## Uncertainties for Next Level Up

1. **Missing files referenced by README.md** — `README.md` links to `SCENARIO_TOOLS_GUIDE.md`, `TROUBLESHOOTING.md`, `MENTION_PROCESSING.md`, `CONTEXT_LOADING.md`, `REQUEST_ENVELOPE_MODELS.md`, `AMPLIFIER_AS_LINUX_KERNEL.md`, `AMPLIFIER_CONTEXT_GUIDE.md`. None of these were in the directory inventory. They likely live in subdirectories (`context/`, etc.) or are forthcoming. The parent level should check for a `context/` subdirectory.

2. **Frontmatter inconsistency** — 5 of 10 files have structured YAML frontmatter; 5 do not. `DEVELOPER.md` includes a note that its contents are "aspirational as of 10/17/2025." No enforcement or validation mechanism is visible. Is there a linter or CI check?

3. **Module resolution 6-layer system duplication** — Both `LOCAL_DEVELOPMENT.md` and `MODULE_DEVELOPMENT.md` describe the same 6-layer module resolution order with nearly identical prose. This is a drift risk. Which file owns the canonical version?

4. **REPOSITORY_RULES.md scope vs. location** — This governance document applies to the entire Amplifier ecosystem, but it lives in the `docs/` subdirectory of what appears to be the entry-point repository. Does the parent level (the root) have its own governance context, or does it defer entirely to this file?

5. **ADR usage** — `ADR_TEMPLATE.md` references a `decisions/` directory (`see the decisions directory`). This directory was not in the inventory. The parent level should look for a `decisions/` sibling directory.

6. **USER_GUIDE.md references `../README.md`** — `USER_GUIDE.md` links to `../README.md#quick-start` which is the parent directory's README, not this directory's README. This cross-boundary reference should be tracked at the parent level.
