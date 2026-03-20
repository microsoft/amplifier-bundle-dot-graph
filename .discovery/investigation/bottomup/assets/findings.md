# Level Synthesis: `assets/`

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/assets`
**Fidelity tier:** standard
**Child directories analyzed:** `branding/`

---

## Files and Symbols at This Level

There are **no files directly in `assets/`**. The directory exists purely as a namespace
container. All content lives inside the single child subdirectory `branding/`.

---

## Cross-Child Connections

**Count: 0**

There is only one child directory (`branding/`), so cross-child connections are
structurally impossible at this level. No imports, shared types, or orchestration
code span multiple children here.

---

## Boundary Patterns

### Pattern: Static Asset Repository with Single Master Source

`branding/` organizes all Amplifier visual identity assets. The dominant structural
pattern within this subtree is a **derivation hierarchy**: a single master source
file (`icons/amplifier-icon-1024.png`, 1024×1024 px, AI-upscaled from the official
GitHub avatar at `github.com/microsoft-amplifier`) is the root from which all other
sizes and formats are generated.

Three deployment-target buckets organize the derived assets:

| Directory   | File count | Deployment target |
|-------------|-----------|-------------------|
| `icons/`    | 14 files  | Desktop/native apps (macOS `.icns`, Windows `.ico`, PNG 16–1024px, menu bar templates) |
| `favicons/` | 3 files   | Web browsers (`.ico` multi-res, PNG 32px, Apple touch icon 180px) |
| `pwa/`      | 2 files   | Progressive Web App manifests (192px, 512px) |

`branding/README.md` acts as the single authoritative inventory and usage guide for
the entire branding subtree — documenting the derivation source, all file sizes and
purposes, and code snippets for HTML favicon setup, PWA manifest, and GitHub README
embedding.

### Pattern: Template vs. Full-Color Asset Split

Within `icons/`, the assets split into two semantic categories:
- **Full-color** icons (`amplifier-icon-*.png`) — for app icons, documentation, marketing
- **Template images** (`MenuBarIcon.png`, `MenuBarIcon@2x.png`) — black + alpha, tinted
  automatically by macOS for light/dark mode; used for system tray / menu bar contexts

### Notable: Cross-Bucket File Identity

The `branding/README.md` reveals that some files across deployment buckets are
**identical copies** (not separate renders):
- `icons/amplifier-icon-512.png` is the same file as `pwa/pwa-512.png`
- `icons/amplifier-icon-32.png` is the same file as `favicons/favicon-32.png`

This means the directory bucketing is organizational/semantic — buckets communicate
deployment target, not independent generation. The PWA and favicon buckets are
thin convenience aliases over the canonical icons.

---

## Uncertainties for Next Level Up

1. **Who consumes these assets?** The README documents usage snippets for web HTML,
   PWA manifests, and GitHub READMEs, but it is not clear which build scripts,
   packaging pipelines, or documentation systems in the broader repository actually
   reference `assets/branding/` paths. The parent level should look for references
   to `assets/branding` in build configs, CI workflows, and packaging manifests.

2. **Are the derived sizes generated programmatically?** The README includes a Python
   snippet using `Pillow` to generate new sizes from the 1024px master, but there is
   no build script or `Makefile` in this directory. Are the current derived files
   pre-generated artifacts committed to the repo, or is there a generation step
   elsewhere?

3. **Platform packaging integration?** The presence of `Amplifier.icns` (macOS) and
   `amplifier-windows.ico` (Windows) suggests a native desktop application is packaged
   somewhere. The parent level should identify which packaging configuration consumes
   these platform-specific bundles.
