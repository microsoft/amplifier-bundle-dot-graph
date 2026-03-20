# Level Findings: assets/branding/icons

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/assets/branding/icons`
**Level slug:** `assets-branding-icons`
**Fidelity tier:** standard
**Children synthesized:** 0 (leaf directory — no subdirectories)

---

## Files and Symbols at This Level

This is a pure asset leaf directory. All 14 files are binary assets (no source code). No children exist.

| File | Format | Size | Purpose |
|------|--------|------|---------|
| `Amplifier.icns` | macOS icon bundle | 1.75 MB | Multi-resolution icon for macOS apps |
| `amplifier-windows.ico` | Windows icon | 969 B | Multi-resolution icon for Windows |
| `MenuBarIcon.png` | PNG | 522 B | macOS menu bar icon — standard resolution |
| `MenuBarIcon@2x.png` | PNG | 1.3 KB | macOS menu bar icon — retina (@2x) |
| `amplifier-icon-16.png` | PNG | 947 B | 16×16 app icon |
| `amplifier-icon-22.png` | PNG | 1.5 KB | 22×22 (Linux system tray standard) |
| `amplifier-icon-32.png` | PNG | 2.7 KB | 32×32 app icon |
| `amplifier-icon-44.png` | PNG | 4.5 KB | 44×44 (Windows taskbar / HiDPI) |
| `amplifier-icon-48.png` | PNG | 5.1 KB | 48×48 (Linux/Android standard) |
| `amplifier-icon-64.png` | PNG | 8.0 KB | 64×64 app icon |
| `amplifier-icon-128.png` | PNG | 22.6 KB | 128×128 app icon |
| `amplifier-icon-256.png` | PNG | 66 KB | 256×256 app icon |
| `amplifier-icon-512.png` | PNG | 228 KB | 512×512 app icon |
| `amplifier-icon-1024.png` | PNG | 842 KB | 1024×1024 master / App Store |

---

## Cross-Child Connections

**None** — this is a leaf directory with no subdirectories. All cross-cutting structure is internal to this level.

---

## Boundary Patterns

### 1. Multi-Platform Icon Distribution Pattern

The icon set is organized around a **three-platform distribution strategy**:

- **macOS** → `Amplifier.icns` (self-contained multi-resolution bundle; the OS renders the appropriate size at runtime)
- **Windows** → `amplifier-windows.ico` (multi-resolution container understood by the Win32 shell)
- **Linux / cross-platform** → individual `.png` files consumed directly by the desktop environment

The PNG files are the *canonical source set* from which both `.icns` and `.ico` bundles are derived (or could be regenerated). The 1024px PNG (`842 KB`) is the master/source—its large size and resolution make it the highest-fidelity original.

### 2. Menu Bar Specialty Pair

`MenuBarIcon.png` and `MenuBarIcon@2x.png` form a **retina-aware asset pair**. These are separate from the main application icon series—likely a simplified or adapted design optimized for small-size display in the macOS menu bar (where the full-detail application icon would not read well). The 1x/2x naming follows Apple's standard asset catalog convention.

### 3. Multi-Resolution PNG Series (10 sizes)

The PNG files span **16 px to 1024 px** covering three distinct size tiers:

| Tier | Sizes | Purpose |
|------|-------|---------|
| Standard power-of-2 | 16, 32, 64, 128, 256, 512, 1024 | macOS, Windows, general UI |
| Linux/Android-specific | 22, 48 | Linux system tray (22 px), freedesktop.org / Android (48 px) |
| Windows HiDPI | 44 | Windows taskbar at 150–200% DPI scaling |

The non-power-of-2 sizes (22, 44, 48) are the signal of intentional cross-platform targeting beyond macOS/Windows.

### 4. File Size Scaling Consistency

File sizes scale approximately with pixel area (as expected for PNG at consistent visual complexity):
- 16→32px (4× area): 947 B → 2.7 KB (≈ 2.8×) ✓
- 32→64px (4× area): 2.7 KB → 8.0 KB (≈ 3.0×) ✓
- 256→512px (4× area): 66 KB → 228 KB (≈ 3.5×) ✓
- 512→1024px (4× area): 228 KB → 842 KB (≈ 3.7×) ✓

This consistency suggests the same artwork is rendered at each size (no custom per-size artwork beyond the menu bar specialty icons).

---

## Uncertainties for Next Level Up

The following questions cannot be answered from within this directory alone and should be investigated by the parent level (`assets/branding` or the build system):

1. **How are these icons referenced in the build?** Which build config files (e.g., `tauri.conf.json`, `Info.plist`, `electron-builder.yml`, or similar) reference `Amplifier.icns`, `amplifier-windows.ico`, or specific PNG sizes? The icon files exist here but the wiring to the packager is upstream.

2. **Is the 1024px PNG truly the master?** Or is there a vector source (`.svg`, `.ai`, `.sketch`, `.figma`) elsewhere in the repository from which all rasters are generated? If so, the PNG files are *derived* artifacts — understanding the generation toolchain matters for maintainability.

3. **Are menu bar icons derived from the main series?** The `MenuBarIcon.png` files appear to be a separate design. Where does that design live? Is it regenerated from a source alongside the main icon?

4. **Are any sizes unused?** Sizes like 22, 44, and 48 are platform-specific. If the app does not ship on Linux or certain Windows configurations, those files may be dead assets. The build config would clarify.

5. **Is `.icns` generated from these PNGs automatically?** If `Amplifier.icns` is checked into source control rather than generated during CI, there is a risk of drift between the `.icns` bundle contents and the individual PNGs in this directory.
