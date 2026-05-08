# Contributing to ArchViz Preset System

Thanks for your interest in improving this package.

## Most useful contributions

The single most valuable thing you can contribute is **new preset entries** in `presets/default_presets.json`. The package is essentially a curated prompt library — better prompts make it more useful for everyone.

When adding a preset, please:

1. **Use positive-constraint phrasing.** "Preserve the X" works better than "do not change the X" with Nano Banana Pro / Gemini 3 Pro Image. See existing presets for tone.
2. **Be specific.** "Honed travertine with warm creamy beige tones and subtle horizontal grain" beats "stone material."
3. **Test before submitting.** Run a few generations with the new preset selected and confirm it produces the intended look.
4. **Match the existing voice.** Phrases should be sentence fragments that read naturally when concatenated with other fragments using `. ` separator.
5. **Avoid lighting/style/camera language inside other categories.** Each category should stay in its own lane so users can mix freely.

## Adding a new category

If you need a new category (e.g., `time_period` or `weather_extremes`), edit:

1. `presets/default_presets.json` — add the category and presets
2. `__init__.py` — add the category name to `MATRIX_CATEGORIES` list
3. `CHANGELOG.md` — document the addition

After this, the `(AV) Matrix` node will automatically show the new dropdown after restart.

## Code changes

The package is intentionally minimal — three nodes, no dependencies outside the Python standard library. Please keep it that way unless there's a strong reason to add complexity.

## Reporting issues

When reporting a bug, include:
- ComfyUI version
- Output of the `[ArchViz] v3 loaded` console line on startup
- The full error traceback
- Your `archviz_presets.json` (or confirmation it's the default)
- A workflow file that reproduces the issue if possible

## Pull requests

Fork → branch → commit with descriptive message → PR. Small focused PRs merge faster than large ones.
