# Level Findings: assets/branding/pwa

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/assets/branding/pwa`
**Level slug:** `assets-branding-pwa`
**Fidelity tier:** standard
**Children analyzed:** none (leaf directory)

---

## Files and Symbols at This Level

This is a **leaf directory** containing exactly two static PNG image assets:

| File | Size | Purpose |
|------|------|---------|
| `pwa-192.png` | 42,655 bytes (~42 KB) | PWA icon — 192×192 px (required by Web App Manifest for homescreen/launcher use) |
| `pwa-512.png` | 233,792 bytes (~228 KB) | PWA icon — 512×512 px (required by Web App Manifest for splash screens and stores) |

These are the two mandatory icon sizes specified in the [W3C Web App Manifest specification](https://www.w3.org/TR/appmanifest/#icons-member). Both sizes are commonly referenced in a `manifest.json` or `manifest.webmanifest` file via their `src` paths.

---

## Cross-Child Connections

**None.** This is a leaf directory with no subdirectories. There are no cross-child connections to report.

---

## Boundary Patterns

### Static Asset Bundle — PWA Icon Pair

The two files together form the **canonical PWA icon pair**: a 192 px icon for Android homescreen shortcuts and a 512 px icon for splash screens and maskable icon generation. This pair is not incidental — it is the minimum viable icon set required by the Web App Manifest specification for PWA installability.

**Pattern type:** Static asset pair following the W3C Web App Manifest icon size convention.

**Consumers (expected upstream):**
- A `manifest.json` / `manifest.webmanifest` file referencing these paths (likely in `assets/branding/` or a web output directory)
- A build pipeline step that copies or hashes these files into a public/dist directory
- Any PWA audit tool (e.g., Lighthouse) that checks for compliant icon sizes

---

## Uncertainties for Next Level Up

1. **Where is the manifest file?** The parent `assets/branding/` or a higher-level directory should contain a `manifest.json` or similar file that references these icon paths — this connection is not visible from within this directory.
2. **Are there additional icon sizes?** Some PWA setups include 48, 72, 96, 144, 180 px icons or a dedicated `favicon.ico`. The presence of only 192 and 512 may be intentional minimalism or may indicate other sizes live elsewhere.
3. **Build pipeline integration:** It is unclear whether these files are copied verbatim to a dist/public directory or processed (e.g., hashed for cache-busting). The parent level should reveal the build configuration.
4. **Maskable icon variant:** The 512 px icon may or may not be marked as `purpose: maskable` in the manifest. This cannot be determined from the file alone.

---

## Summary

A minimal, spec-compliant PWA icon asset directory containing the two required icon sizes (192 px and 512 px). No internal complexity — architectural significance lies entirely in its relationship to an upstream `manifest.json` and build pipeline.
