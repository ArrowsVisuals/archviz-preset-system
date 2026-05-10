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

## The 13 categories

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
| `population_density` | How many people and where placed |
| `hero_style` | The compositional anchor figure's style |
| `cars` | Hero vehicles for luxury residential (brand-free) |
| `surroundings` | Context preservation with refinement options |
| `enhancement` | Upscale, refine, or fix specific elements |

Pick `(none)` on any axis you don't want active. The Matrix node skips empty fragments.

## The three-axis people system (v4.0+)

Scene population is split across three independent axes that combine to produce 11 × 4 × 6 = 264 figure variations:

**`people` (ethnicity, no count)** — emirati, saudi, qatari, omani, gulf_mixed, levantine_arab, european, afro_diaspora, east_asian, south_asian, mixed_diverse

**`population_density` (count + placement)** — single_hero (one foreground figure), hero_with_supporting (foreground hero + few background), multiple_active (several figures, no central hero), crowded_public (many figures)

**`hero_style` (what the hero is wearing/doing)** — elegant_woman_flowing_dress, elegant_man_tailored, contemplative_figure_from_behind, fashion_editorial_woman, couple_arrival_lifestyle, active_resident_lifestyle

The hero archetypes are based on the photographic tradition of Julius Schulman's iconic luxury residential photography (Stahl House, etc.) and modern high-end residential render conventions. The `elegant_woman_flowing_dress` and `elegant_man_tailored` archetypes work with any ethnicity — Western dress for Western ethnicities, abaya/thobe for Gulf ethnicities.

## Recommended workflows for common use cases

### Adding people to an existing finished render

When your input is already a high-quality render and you only want to add figures, use the minimal-change configuration to prevent softening of the rest of the image:

- `preservation` → `people_only_minimal_change`
- `people` → ethnicity of choice
- `population_density` → `single_hero`, `hero_with_supporting`, or `multiple_active`
- `hero_style` → archetype of choice (or `(none)` for non-hero figures)
- All other categories → `(none)`

The `people_only_minimal_change` preservation preset uses compositing-style language that tells the model to add only the specified figures while leaving every other pixel of the input identical.

### Generating variations of a render

When you want to explore different lighting, atmosphere, or style on the same building, use the standard preservation + descriptive categories:

- `preservation` → `preserve_design` or `preserve_with_polish`
- `lighting`, `atmosphere`, `style`, etc. → variations per branch

This is what the example workflow `render_variations_v3.json` demonstrates.

### Transforming a screenshot or draft into a polished render

When the input is a SketchUp/Revit screenshot or rough render needing significant uplift:

- `preservation` → `preserve_design`
- `style` → `photoreal_editorial` or similar finished-look preset
- `materials`, `lighting`, `atmosphere` → as desired

The model can do substantial transformation here because the input doesn't have fidelity to lose.

## Enhancement workflows

The `enhancement` category covers a different mode of operation than the descriptive categories. Use it when you have an existing render that needs refinement rather than transformation:

- **Upscaling 1K → 4K:** Use `upscale_4k_full` and set most other categories to `(none)`. Set the Nano Banana resolution to 4K.
- **Vegetation refinement:** Use `enhance_vegetation_strict` for fidelity, or `enhance_vegetation_creative` if you want richer planting.
- **Enhancing people holistically:** Use `enhance_people_full` — refines anatomy, skin micro-texture, hair detail, clothing fabric, and posture together. This is what makes people look genuinely natural rather than just "fixed."
- **Polishing already-correct figures:** Use `enhance_people_polish` — refines skin/hair/clothing surface quality without modifying anatomy or pose.
- **Surgical single-element fixes:** Use `fix_hands_only` or `fix_faces_only` when only one part is broken.
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
