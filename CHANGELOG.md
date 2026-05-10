# Changelog

All notable changes to the ArchViz Preset System are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.0] — 2026-05-10

### Added
- **3 aerial camera presets** for masterplan and elevated work:
  - `aerial_oblique_45` — classic 45° oblique drone view, the standard real-estate hero
  - `aerial_high_overview` — high-altitude near-orthographic for masterplan and site-context shots
  - `aerial_low_drone` — low-altitude tracking shot for cinematic project hero views
- **2 aerial atmosphere presets** to control depth and clarity:
  - `aerial_perspective_strong` — progressive haze fading distant elements (depth and scale)
  - `clear_aerial_sharp` — exceptionally clear high-altitude air for technical masterplan shots
- **4 surroundings presets** for project-context variety:
  - `mixed_use_neighborhood` — ground-floor retail with residential/office above, animated street life
  - `urban_dense_aerial_context` — surrounding city fabric for masterplan aerials
  - `coastal_aerial_context` — waterfront context for shoreline projects and resort masterplans
  - `desert_aerial_context` — sandy/dune surroundings with site infrastructure visible

### Recommended aerial workflow
- `camera` → `aerial_oblique_45` (most projects) or `aerial_high_overview` (masterplans)
- `atmosphere` → `aerial_perspective_strong` for hero shots, `clear_aerial_sharp` for technical
- `surroundings` → match to project context (urban / coastal / desert)
- `lighting` → `golden_hour` or `morning_soft` work especially well from the air
- `population_density` → typically `(none)` since figures are too small to read at aerial scale

### Stats
13 categories, 118 presets total (was 109 in v4.0.1)

## [4.0.1] — 2026-05-10

### Fixed
- **Gulf Arab ethnicity presets no longer force both genders to be present.** The v4.0.0 presets said "men in X, women in Y" which the model interpreted as a presence statement — combining `single_hero` + `emirati` (or other Gulf ethnicities) was producing multiple figures instead of one. Rewrote `emirati`, `saudi`, `qatari`, `omani`, and `gulf_mixed` to use "Traditional [X] attire when figures are present: men wear..., women wear..." which is conditional reference rather than presence requirement. Now `single_hero` + Gulf ethnicity correctly produces one figure.

### Added
- **`preservation/people_only_minimal_change`** — a new preservation preset for the "add people to an existing finished render" workflow. Uses aggressive compositing-style language ("treat the input as a finished photograph that you are adding people to via compositing") to minimize the model's tendency to re-render and soften the rest of the image. Use this with descriptive categories (lighting, atmosphere, style, materials, surroundings) all set to `(none)` for best results — the model will then focus only on adding the specified figures while leaving the rest pixel-identical.

### Recommended workflow for adding people to existing renders
For minimum quality loss when populating a finished render with figures:
- `preservation` → `people_only_minimal_change`
- `people` → ethnicity of choice
- `population_density` → `single_hero` or `hero_with_supporting`
- `hero_style` → archetype of choice
- All other categories → `(none)`
- Optionally add to USER OVERRIDE: "Only modification: add the specified human figure to the scene. Treat as compositing, not re-rendering."

## [4.0.0] — 2026-05-10

⚠️ **Breaking changes** — saved workflows from v3.x will need preset re-selection because category structure and preset names have changed. See migration notes at the bottom of this entry.

### Critical fixes
- **Watermark issue resolved.** Removed all branded/named real-world references that were triggering Gemini 3 Pro Image's training-data recall behavior. Specifically removed: city names (Dubai, Emirates Hills, Palm Jumeirah, Al Barari), car brands (Mercedes-Benz, BMW, Bentley, Rolls-Royce, Maybach, Porsche, McLaren), camera brands (Hasselblad, Arri Alexa, Kodak Portra), publication names (Dwell, Architectural Digest), and photographer names (Iwan Baan, Hélène Binet, Julius Schulman, DBOX). All replaced with descriptive equivalents that produce the same visual style without triggering watermark reproduction.
- **Motion blur prompt rewritten.** The previous `motion_blur_figures` preset was producing duplicate-figure failures (sharp character + transparent ghost overlay). The new prompt explicitly negates these failure modes: "do NOT produce double exposure, do NOT produce a sharp figure with a transparent copy next to it, do NOT produce ghostly transparent overlays" and describes the correct long-exposure photographic effect concretely.

### Restructured: people category split into three independent axes
The single `people` category bundled ethnicity, count, and styling. Now split into three composable axes:
- **`people`** — ethnicity only (no count language). 11 ethnicity options.
- **`population_density`** — how many people and where placed. 4 options: single_hero, hero_with_supporting, multiple_active, crowded_public.
- **`hero_style`** — what the hero figure is wearing/doing. 6 options: elegant_woman_flowing_dress, elegant_man_tailored, contemplative_figure_from_behind, fashion_editorial_woman, couple_arrival_lifestyle, active_resident_lifestyle.

This gives 11 × 4 × 6 = 264 combinations from 21 preset values, vs. ~17 hard-coded combinations before.

### New: hero_style category with 6 archetypes
Based on Schulman's Stahl House photography tradition and modern high-end residential render conventions:
- `elegant_woman_flowing_dress` — light dress or abaya in motion (the iconic luxury-residential archetype)
- `elegant_man_tailored` — tailored suit or thobe, contemplating space
- `contemplative_figure_from_behind` — anonymous, atmospheric, lets viewer project in
- `fashion_editorial_woman` — theatrical magazine-style with dress dramatically caught in motion
- `couple_arrival_lifestyle` — couple walking together, residential aspirational
- `active_resident_lifestyle` — candid lifestyle moment, less posed

The `elegant_woman_flowing_dress` and `elegant_man_tailored` presets explicitly support both Western dress and Gulf traditional attire (abaya/thobe) when combined with appropriate ethnicity.

### Renamed for clarity
| v3.x | v4.0.0 |
|---|---|
| `preservation/strict_anchor` | `preservation/preserve_exactly` |
| `preservation/standard_anchor` | `preservation/preserve_design` |
| `preservation/refinement_allowed` | `preservation/preserve_with_polish` |
| `preservation/restraint` | `preservation/restrained_realism` |
| `preservation/no_clutter` | `preservation/clean_minimal` |
| `preservation/competition_grade` | `preservation/competition_polished` |
| `lighting/blue_hour_dubai` | `lighting/blue_hour_warm` |
| `lighting/night_warm_glow` | `lighting/night_with_glow` |
| `atmosphere/clear_pristine` | `atmosphere/clear_air` |
| `atmosphere/warm_dust_gulf` | `atmosphere/warm_dust_haze` |
| `atmosphere/humid_coastal` | `atmosphere/humid_coastal_air` |
| `atmosphere/neutral_studio` | `atmosphere/neutral_clean` |
| `style/film_portra` | `style/film_warm_grain` |
| `style/hasselblad_clean` | `style/digital_clean` |
| `style/cinematic_arri` | `style/cinematic_anamorphic` |
| `style/magazine_dwell` | `style/magazine_residential` |
| `style/competition_render` | `style/competition_dramatic` |
| `style/watercolor_traditional` | `style/watercolor_painted` |
| `style/loose_concept_sketch` | `style/concept_sketch_loose` |
| `materials/travertine_signature` | `materials/travertine_full_palette` |
| `materials/travertine_mashrabiya` | `materials/travertine_with_screens` |
| `materials/premium_natural` | `materials/premium_natural_mix` |
| `materials/industrial_refined` | `materials/industrial_concrete_steel` |
| `materials/warm_residential` | `materials/warm_residential_oak` |
| `materials/mediterranean_warm` | `materials/mediterranean_limestone` |
| `materials/high_tech_precision` | `materials/precision_anodized_aluminum` |
| `cars/hero_silver_mercedes` | `cars/hero_luxury_sedan_silver` |
| `cars/hero_dark_luxury` | `cars/hero_luxury_sedan_dark` |
| `cars/passing_motion_blur` | `cars/passing_blur` |
| `cars/two_luxury_parked` | `cars/two_sedans_parked` |
| `cars/supercar_hero` | `cars/hero_sports_coupe` |
| `surroundings/dubai_residential_district` | `surroundings/gulf_residential_district` |
| `surroundings/coastal_view` | `surroundings/coastal_distant_view` |
| `people/few_*` (e.g. few_emirati) | `people/*` (e.g. emirati) — count moved to population_density |

### Added
- New `cars/hero_electric_modern` — modern electric luxury sedan archetype (without naming Tesla or other brands)
- Deep skin/cloth/fabric photography vocabulary added to `enhance_people_full`. Includes: subsurface scattering, anisotropic specular highlights for hair, material-specific fabric terminology (linen slubs, silk satin sheen, cashmere fiber halo, denim diagonal twill, wool matte fiber), realistic skin chromatic variation, joint articulation accuracy.

### Removed
- All v3.x preset keys with branded references (Mercedes, Hasselblad, Arri, Portra, Dwell, Iwan Baan, etc.)
- `few_*` ethnicity presets (split into ethnicity-only `people` + new `population_density`)

### Migration from v3.x
**Recommended path:**
1. Close ComfyUI completely
2. Delete `ComfyUI/user/archviz_presets.json` (back up first if you have customizations)
3. Restart ComfyUI — first-run logic copies the new v4.0.0 defaults
4. Open any saved workflows and re-select preset combinations in the (AV) Matrix node — v3.x preset keys won't be found, dropdowns will fall back to `(none)`

If you had custom presets you added in v3.x, copy them from your backup file into the new `archviz_presets.json` after step 3.

## [3.1.1] — 2026-05-10

### Changed
- People-enhancement presets reframed from anatomy-focused to holistic. Enhancing a person now means improving anatomy AND skin micro-texture AND hair detail AND clothing fabric AND posture together — because that's what produces a person who reads as natural rather than just a "fixed" person.
- Renamed `fix_anatomy_full` → `enhance_people_full`. The new preset addresses faces (eyes, skin, expression), hair (strand detail, natural fall), skin (micro-texture, color variation), clothing (fabric weave, drape, material weight), posture (relaxed unposed body language), AND anatomy (correct hands, proportions, facial features) — all in one comprehensive pass.

### Added
- New `enhance_people_polish` preset: refines surface quality (skin, hair, clothing fabric) WITHOUT modifying anatomy or pose. Use this when the figures are already correctly posed and you just want them to look more detailed and natural.

### Kept
- `fix_hands_only` and `fix_faces_only` remain for surgical single-element fixes
- `motion_blur_figures` remains as the pro architectural photography option that sidesteps anatomy entirely

## [3.1.0] — 2026-05-08

### Added
- New `enhancement` category with 10 presets for refinement and upscaling workflows:
  - `upscale_4k_full` — standard upscale to higher resolution with full preservation
  - `enhance_architecture_only` — building details, materials, edges focus
  - `enhance_vegetation_strict` — refine plants without adding new ones
  - `enhance_vegetation_creative` — refine plants with creative additions allowed
  - `fix_anatomy_full` — comprehensive people fix (faces + hands + legs + proportions)
  - `fix_hands_only` — surgical hands-only pass
  - `fix_faces_only` — surgical faces-only pass
  - `enhance_materials_textures` — surfaces and texture detail
  - `motion_blur_figures` — convert rough figures to elegant motion-blur ghosts (pro architectural photography technique)
  - `subtle_cleanup` — minimal artifact removal, no transformation
- Filename tag generation now prioritizes the enhancement selection when active

### Changed
- Matrix node now has 11 categories (was 10) — `enhancement` added at the end
- Updated load banner to show v3.1 and category count

## [3.0.1] — 2026-05-08

### Fixed
- Validation script no longer rejects empty preset values (the `scale_life/none` preset is intentionally empty)

## [3.0.0] — 2026-05-08

### Added
- New `cars` category with 7 presets (silver Mercedes hero, dark luxury, motion blur, etc.)
- New `surroundings` category with 8 presets (preserve_input default, Dubai district, coastal view, etc.)
- New `travertine_signature`, `travertine_white_plaster`, `travertine_mashrabiya`, `travertine_warm_timber`, `white_plaster_timber_screens` material presets — calibrated to firm visual identity
- Refined Arab ethnicity presets: `few_emirati`, `few_saudi`, `few_qatari`, `few_omani`, `few_gulf_mixed`, `few_levantine_arab`
- New `few_afro_diaspora` and `few_afro_american` presets (replacing generic `few_african`)
- New Dubai-specific atmosphere presets: `warm_dust_gulf`, `humid_coastal`, `blue_hour_dubai`
- First-run logic: bundled defaults auto-copy to `ComfyUI/user/archviz_presets.json` so package updates don't overwrite user customizations
- Self-contained package structure ready for GitHub distribution and ComfyUI Manager
- `pyproject.toml` for ComfyUI Manager registry compatibility

### Changed
- 10 categories total (was 8 in v2): added `cars` and `surroundings`
- Generic `few_african` replaced with two diaspora-focused presets per firm preference
- `(AV) Matrix` node now exposes 10 dropdowns
- Filename tag generation includes car selection when present

### Removed
- Generic `few_african` preset (replaced with diaspora presets)

## [2.0.0] — 2026-05-07

### Added
- `(AV) Matrix` node consolidating all 8 categories in one node
- `(AV)` prefix on all node display names for visual identification
- New `preservation` category with 6 positive-constraint presets
- New `materials` category with 8 palette presets
- New `people` category with 12 ethnicity options
- New `scale_life` category with 9 occupancy options
- Photographer/equipment vocabulary in style presets (Iwan Baan, Hasselblad, Portra 400)

### Changed
- Workflow simplified from 37 nodes to 15 nodes per the consolidated Matrix node
- Style presets rewritten with specific photographer references

## [1.0.0] — 2026-05-07

### Added
- Initial release with `ArchVizPresetLoader` and `ArchVizPromptAssembler` nodes
- 4 categories: lighting, atmosphere, style, camera
- 31 starter presets
- 4-branch parallel Render Variations workflow
