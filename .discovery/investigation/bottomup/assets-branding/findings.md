# Level Synthesis: assets/branding

**Directory:** `/amplifier/assets/branding`  
**Fidelity tier:** standard  
**Entry count:** 4 (1 file + 3 subdirectories, 19 total files)

---

## Files and Symbols at This Level

| File | Size | Role |
|------|------|------|
| `README.md` | 3,439 bytes | Master documentation for ALL branding assets — covers all three child directories, includes HTML favicon snippets, PWA manifest JSON, icon-generation Python script, and co-author attribution line |

The README.md is architecturally significant at this level: it is the **only file that spans all three subdirectories** and provides the canonical usage contract for consumers of this branding system.

---

## Child Directory Summary

| Directory | File Count | Purpose |
|-----------|-----------|---------|
| `icons/` | 14 | Native app icons — multiple PNG sizes (16px–1024px), macOS `.icns`, Windows `.ico`, macOS menu bar templates |
| `favicons/` | 3 | Web browser favicons — `favicon.ico`, `favicon-32.png`, `apple-touch-icon.png` |
| `pwa/` | 2 | Progressive Web App icons — `pwa-192.png`, `pwa-512.png` |

---

## Cross-Child Connections

### Connection 1: `icons/amplifier-icon-32.png` ≡ `favicons/favicon-32.png`
- **Source child:** `icons/`
- **Target child:** `favicons/`
- **Evidence:** Both files are exactly **2,772 bytes**
- **Interpretation:** These are identical files (same pixel data, same encoding). The `favicon-32.png` is a direct copy of the 32px app icon. There is **no separate derivation step** — the icon IS the favicon at 32px.

### Connection 2: `icons/amplifier-icon-512.png` ≡ `pwa/pwa-512.png`
- **Source child:** `icons/`
- **Target child:** `pwa/`
- **Evidence:** Both files are exactly **233,792 bytes**
- **Interpretation:** These are identical files. The PWA splash screen icon is a direct copy of the 512px app icon. The `pwa/` directory at the 512px tier adds no unique content — it is a re-distribution of the same binary.

### Connection 3: `icons/amplifier-icon-1024.png` → all subdirectories
- **Source child:** `icons/`
- **Target children:** `favicons/`, `pwa/`
- **Mechanism:** Documented in README.md — the 1024px master is the generative root. The README explicitly references it in the Python code snippet for generating new sizes.
- **Derived cross-child assets:**
  - `favicons/apple-touch-icon.png` (180×180) — resized from master
  - `favicons/favicon.ico` (16+32+48 multi-resolution composite) — derived from master
  - `pwa/pwa-192.png` (192×192) — resized from master

---

## Boundary Pattern

### Pattern: **Master Icon Distribution (Single-Source Fan-Out)**

The dominant structural pattern at this level is a **single canonical source cascading to platform-specific variant directories**:

```
GitHub Avatar (460px)
    └── AI upscale
        └── amplifier-icon-1024.png  [MASTER — in icons/]
            ├── icons/        ← native app + desktop OS
            ├── favicons/     ← web browser
            └── pwa/          ← Progressive Web App
```

Key properties of this pattern:
1. **Single master, multiple contexts** — all three subdirectories serve the same brand identity but for different platform runtimes (desktop OS, browser, mobile/PWA).
2. **Cross-boundary file identity** — two files exist in two different platform directories with identical bytes (icon-32 = favicon-32; icon-512 = pwa-512). These are not independently derived; they are the same file placed in two locations for semantic clarity.
3. **README as the distribution contract** — the top-level `README.md` encodes exactly which file goes where and provides copy-paste usage snippets for each platform (HTML `<link>` tags, JSON PWA manifest, Python resize script). This makes README.md the integration documentation for all three child directories simultaneously.

---

## Potential Concerns / Uncertainties for Next Level Up

1. **Duplication risk:** `icons/amplifier-icon-32.png` and `favicons/favicon-32.png` are identical binaries. If the icon is ever updated, both files must be updated in sync. There is no symlink or reference — the duplication is physical. The same applies to the 512px pair. Any tooling that regenerates icons must update both locations.

2. **Master source location:** The generative master (`amplifier-icon-1024.png`) lives inside `icons/`, which is a child directory rather than at the branding root. From a distribution standpoint, the master is embedded inside one of the consumers. A parent-level consumer who needs only the master must know to look inside `icons/`.

3. **No version or provenance metadata in filenames:** The files carry no version indicator. If the brand changes, there is no mechanism to distinguish old from new assets at the filesystem level.

4. **Questions for parent level (assets/):**
   - Are there other branding directories alongside `branding/` (e.g., logos, screenshots)?
   - Is the `branding/` directory consumed by any build system, or is it purely static reference material?
   - Does any CI/CD pipeline verify that the paired identical files (32px, 512px) stay in sync across `icons/` and `favicons/`/`pwa/`?

---

## Summary

The `assets/branding` directory implements a **Master Icon Distribution pattern**: one GitHub-sourced 1024px master in `icons/` drives 19 total image files across three platform-scoped subdirectories. The most architecturally significant cross-child fact is that **two pairs of files are byte-for-byte identical across child boundaries** (`icons/icon-32 = favicons/favicon-32` and `icons/icon-512 = pwa/pwa-512`), making the subdirectory separation a semantic/contextual organization rather than a derivation boundary. The top-level `README.md` serves as the sole integration document spanning all three children.
