# ArchViz Preset System

[![Validate](https://github.com/ArrowsVisuals/archviz-preset-system/actions/workflows/validate.yml/badge.svg)](https://github.com/ArrowsVisuals/archviz-preset-system/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A ComfyUI custom node package for high-end architectural visualization prompt construction with **Nano Banana Pro / Gemini 3 Pro Image**.

Designed specifically for image-to-image workflows where preserving input geometry is critical — the typical "screenshot or basic render → high-end render" workflow used by architecture firms.

## What it does

- **Curated preset library** for prompt construction across 10 categories
- **One Matrix node** consolidates all preset selection (no canvas clutter)
- **Positive-constraint phrasing** throughout (more reliable than negative prompts)
- **Photographer/equipment vocabulary** in style presets (Hasselblad, Portra 400, tilt-shift, etc.)
- **Gulf Arab ethnicity refinement** — Saudi, Emirati, Qatari, Omani specifics with appropriate dress
- **Firm-signature material presets** — travertine + white textured plaster + mashrabiya combinations
- **Hero car options** for luxury residential renders
- **Surroundings preservation** with optional refinement levels

## Quick start

### Installation

**Option A: ComfyUI Manager** (once published to registry)

Search for "ArchViz Preset System" in ComfyUI Manager.

**Option B: Manual git clone**

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/ArrowsVisuals/archviz-preset-system.git
```

**Option C: Manual download**

Download the latest release zip from [Releases](https://github.com/ArrowsVisuals/archviz-preset-system/releases), extract into `ComfyUI/custom_nodes/`.

### First run

Restart ComfyUI. On first launch, the bundled `presets/default_presets.json` is automatically copied to `ComfyUI/user/archviz_presets.json`. Your edits there survive future package updates.

You should see this in the console:

```
[ArchViz] First run — copied default presets to /path/to/ComfyUI/user/archviz_presets.json
[ArchViz] v3 loaded — 3 nodes ((AV) Preset / Matrix / Assembler)
```

### Try the example workflow

Open `workflows/render_variations_v3.json` in ComfyUI. Drop a basic render or screenshot into the input image node and hit Queue. You'll get 4 distinct high-end variations in parallel.

## The three nodes

All grouped under the **ArchViz** category in the right-click menu.

| Node | Use |
|------|-----|
| `(AV) Preset` | Single-category dropdown — for advanced/manual wiring |
| `(AV) Matrix` | All 10 categories in one node — recommended default |
| `(AV) Assembler` | Manual 6-fragment concatenator — flexibility |

## The 10 categories

| Category | Purpose |
|----------|---------|
| `preservation` | Anchors geometry — most important slot |
| `camera` | Composition, viewpoint, framing |
| `lighting` | Time of day, light quality |
| `atmosphere` | Weather, haze, conditions |
| `style` | Photographic equipment + aesthetic |
| `materials` | Material palette including firm signatures |
| `people` | Figure presence with ethnicity options |
| `scale_life` | Activity level + occupancy |
| `cars` | Hero vehicles for luxury residential |
| `surroundings` | Context preservation with refinement options |
| `enhancement` | Upscale, refine, or fix specific elements |

Pick `(none)` on any axis you don't want active. The Matrix node skips empty fragments.

## Enhancement workflows

The `enhancement` category covers a different mode of operation than the descriptive categories. Use it when you have an existing render that needs refinement rather than transformation:

- **Upscaling 1K → 4K:** Use `upscale_4k_full` and set most other categories to `(none)`. Set the Nano Banana resolution to 4K.
- **Vegetation refinement:** Use `enhance_vegetation_strict` for fidelity, or `enhance_vegetation_creative` if you want richer planting.
- **Fixing people:** Use `fix_anatomy_full` for comprehensive fixes, or `fix_hands_only` / `fix_faces_only` for surgical passes.
- **Avoiding face/anatomy issues entirely:** Use `motion_blur_figures` — a professional architectural photography technique that turns rough figures into elegant motion-blurred ghosts.

For enhancement runs, set most descriptive categories (lighting, atmosphere, style, etc.) to `(none)` so the prompt focuses on the refinement instruction. Stacking multiple enhancements in one pass can produce over-sharpened results — one clean pass beats three aggressive ones.

## Editing the preset library

Edit `ComfyUI/user/archviz_presets.json` in any text editor.

```json
{
  "category_name": {
    "preset_name": "the prompt text fragment"
  }
}
```

Rules:
- Editing existing preset **text**: changes apply on next workflow run, no restart
- Adding new preset **names**: restart ComfyUI to refresh dropdowns
- Adding new categories: requires editing `MATRIX_CATEGORIES` in `__init__.py`

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidance on writing good preset prompts.

## Why image-to-image preservation matters

Nano Banana Pro / Gemini 3 Pro Image works best when the prompt describes only what's *missing* from the input — not the geometry, composition, and design that's already shown. This package is built around that principle:

- The `preservation` category anchors the architecture so the model treats it as fixed
- The `system_prompt` in the example workflow tells the model to render rather than redesign
- Material/lighting/style fragments add the polish layer on top of the existing design

## Compatibility

- ComfyUI 0.20+ (subgraph support recommended for the example workflow)
- WAS Node Suite (for the `Image Save` node in the example workflow)
- ComfyUI's official Gemini Image node, OR any compatible Nano Banana / Gemini 3 Pro Image node

The custom nodes themselves have **no dependencies** outside the Python standard library.

## Roadmap

- LLM enhancer node integration (Gemini Flash) for user-intent rewriting
- Per-axis blueprint subgraphs for advanced multi-pass workflows
- Additional regional preset packs (Levant, Maghreb, South Asia specifics)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The most valuable contributions are well-written preset entries.

## License

MIT — see [LICENSE](LICENSE).
