# Changelog

All notable changes to the ArchViz Preset System are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
