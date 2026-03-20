# Level Synthesis: assets/branding/favicons

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/assets/branding/favicons`
**Level slug:** `assets-branding-favicons`
**Fidelity tier:** standard
**Children synthesized:** 0 (leaf directory)

---

## Files and Symbols at This Level

This is a **leaf directory** containing three static binary favicon assets. There are no subdirectories and no source code.

| File | Type | Size | Purpose |
|------|------|------|---------|
| `apple-touch-icon.png` | PNG image | 38,612 bytes | iOS/Apple home-screen icon (typically 180×180 px) |
| `favicon-32.png` | PNG image | 2,772 bytes | Standard browser favicon at 32×32 px |
| `favicon.ico` | ICO format | 969 bytes | Legacy multi-resolution favicon for older browsers |

**Size observations:**
- `apple-touch-icon.png` is ~14× larger than `favicon-32.png`, consistent with a higher-resolution icon (180×180 vs 32×32).
- `favicon.ico` at 969 bytes is unusually small, likely containing only a 16×16 embedded image rather than a multi-size ICO bundle.

---

## Cross-Child Connections

**None.** This is a leaf directory with no children. There are no cross-child edges.

---

## Boundary Patterns

### Static Asset Bundle Pattern
The three files collectively satisfy the standard web favicon coverage triangle:
- **ICO fallback** (`favicon.ico`) — consumed by legacy browsers and many feed readers via root-relative `/favicon.ico` convention.
- **PNG favicon** (`favicon-32.png`) — referenced explicitly by modern HTML `<link rel="icon">` tags.
- **Apple touch icon** (`apple-touch-icon.png`) — consumed by iOS Safari when a user saves the site to their home screen, referenced via `<link rel="apple-touch-icon">`.

Together they form a **complete favicon set** that targets all major consumption paths: browser tab, bookmark, iOS home screen.

---

## Relationship to Parent Level

This directory sits at `assets/branding/favicons`, implying:
- A `branding/` parent likely contains other brand assets (logos, color references, etc.).
- An `assets/` grandparent likely groups all static, non-code resources for the application.
- Nothing in this directory references or is referenced by source code directly — consumption is via HTML `<link>` tags and browser convention.

---

## Uncertainties for Next Level Up

1. **Are these favicons referenced in HTML templates?** The parent synthesis should locate the `<link>` tags that reference these files and confirm the file names match (e.g., whether `favicon-32.png` is the actual name used in `<link rel="icon" sizes="32x32">`).
2. **Is `favicon.ico` served from the root?** Many web servers require `favicon.ico` at the web root (`/favicon.ico`). If this file lives at `assets/branding/favicons/favicon.ico`, a redirect, copy step, or build process may be needed — the parent level should confirm this.
3. **Is an SVG favicon absent?** Modern browsers prefer SVG favicons for resolution independence. The absence of an `.svg` file here may be intentional (brand constraint) or an oversight.
4. **Are there multiple icon sizes beyond 32px?** Only one PNG size is present. A comprehensive favicon set often includes 16, 48, 96, 192, and 512 px variants for PWA manifests.

---

## Summary

A minimal, well-formed **leaf asset directory** containing the three files needed for cross-browser favicon coverage. No code, no imports, no cross-child connections. The primary signal for the parent level is whether the HTML templates correctly reference these files and whether `favicon.ico` is reachable at the web root.
