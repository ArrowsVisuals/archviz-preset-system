"""
ArchViz Preset System v5.0 for ComfyUI
=====================================

Self-contained ComfyUI custom node package for high-end architectural
visualization prompt construction — now model-aware. One preset library,
compiled into the native prompt dialect of your target model:
Nano Banana (edit + generate), Flux 2 Pro, Flux 2 Dev/Flex (structured),
GPT Image 2 (brief), Ideogram 4 (JSON caption).

Pick the model in the (AV) Matrix `target_model` dropdown. The default
("nano_banana_edit") is byte-identical to v4 output — existing workflows
are unaffected. Dialects live in presets/model_profiles.json (user-editable).

INSTALLATION:
  Drop this entire folder into ComfyUI/custom_nodes/ and restart ComfyUI.
  Default presets auto-copy to ComfyUI/user/archviz_presets.json on first run.
  Your edits there survive future package updates.

THREE NODES (under "ArchViz" category):
  (AV) Preset    — single-category dropdown
  (AV) Matrix    — all 10 categories in one node (recommended default)
  (AV) Assembler — manual fragment concatenator (flexibility)

License: MIT
Repo: https://github.com/<your-org>/archviz-preset-system
"""

import json
import shutil
from pathlib import Path

from .compilers import compile_prompt, profile_names
from .scene import ArchVizScene

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
NODE_DIR = Path(__file__).resolve().parent
COMFYUI_ROOT = NODE_DIR.parent.parent
DEFAULT_PRESETS_PATH = NODE_DIR / "presets" / "default_presets.json"
USER_PRESETS_PATH = COMFYUI_ROOT / "user" / "archviz_presets.json"

# Matrix node category order (also defines what shows up in INPUT_TYPES)
MATRIX_CATEGORIES = [
    "preservation",
    "camera",
    "lighting",
    "atmosphere",
    "style",
    "materials",
    "people",
    "population_density",
    "hero_style",
    "scale_life",
    "cars",
    "surroundings",
    "enhancement",
]


# ---------------------------------------------------------------------------
# First-run setup: copy bundled defaults to user/ if missing
# ---------------------------------------------------------------------------
def _ensure_user_presets():
    """Copy bundled defaults to user dir on first run. Never overwrites."""
    if USER_PRESETS_PATH.exists():
        return False
    if not DEFAULT_PRESETS_PATH.exists():
        print(f"[ArchViz] WARNING: bundled defaults not found at {DEFAULT_PRESETS_PATH}")
        return False
    USER_PRESETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DEFAULT_PRESETS_PATH, USER_PRESETS_PATH)
    print(f"[ArchViz] First run — copied default presets to {USER_PRESETS_PATH}")
    print(f"[ArchViz] Edit that file to customize. Updates won't overwrite your changes.")
    return True


_ensure_user_presets()


# ---------------------------------------------------------------------------
# Preset loading
# ---------------------------------------------------------------------------
_DEFAULT_FALLBACK = {cat: {"_placeholder": "edit archviz_presets.json"} for cat in MATRIX_CATEGORIES}


def _load_presets() -> dict:
    """Read user/archviz_presets.json. Falls back to bundled defaults, then placeholders."""
    for path in (USER_PRESETS_PATH, DEFAULT_PRESETS_PATH):
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                continue
            cleaned = {}
            for cat, presets in data.items():
                if cat.startswith("_"):
                    continue
                if isinstance(presets, dict) and presets:
                    cleaned[cat] = presets
            if cleaned:
                return cleaned
        except (json.JSONDecodeError, OSError) as e:
            print(f"[ArchViz] Error reading {path}: {e}")
    return _DEFAULT_FALLBACK


def _category_options(category: str) -> list:
    """Return preset names for one category, with '(none)' first."""
    presets = _load_presets()
    cat = presets.get(category, {})
    return ["(none)"] + sorted(k for k in cat.keys() if not k.startswith("_"))


def _resolve(category: str, name: str, model: str = "") -> str:
    """Look up preset text. Returns empty string if 'none' or not found.

    v5: a preset value may be a plain string (used for all models) or an
    object of per-model overrides, e.g.
        {"default": "…", "flux2_pro": "…", "ideogram4_json": "…"}
    """
    if not name or name == "(none)" or name.startswith("_"):
        return ""
    presets = _load_presets()
    value = presets.get(category, {}).get(name, "")
    if isinstance(value, dict):
        if model and model in value:
            return value[model]
        return value.get("default", "")
    return value


def _join_fragments(parts: list, separator: str = ". ") -> str:
    """Join non-empty fragments with the separator, append a trailing period."""
    cleaned = [p.strip().rstrip(" .,;") for p in parts if p and p.strip()]
    if not cleaned:
        return ""
    return separator.join(cleaned) + "."


# ---------------------------------------------------------------------------
# Node 1: (AV) Preset — single-category dropdown
# ---------------------------------------------------------------------------
class ArchVizPresetLoader:
    """Loads a single preset prompt fragment from one category."""

    @classmethod
    def INPUT_TYPES(cls):
        presets = _load_presets()
        all_named = []
        for cat in sorted(presets.keys()):
            for name in presets[cat]:
                all_named.append(f"{cat}/{name}")
        if not all_named:
            all_named = ["preservation/_placeholder"]

        return {
            "required": {
                "preset": (sorted(all_named),),
            },
            "optional": {
                "passthrough": ("STRING", {"forceInput": True, "default": ""}),
                "separator":   ("STRING", {"default": ", "}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "load_preset"
    CATEGORY = "ArchViz"

    def load_preset(self, preset, passthrough="", separator=", "):
        if "/" not in preset:
            return (passthrough,)
        category, name = preset.split("/", 1)
        text = _resolve(category, name)
        if not text:
            return (passthrough,)
        return (f"{passthrough}{separator}{text}" if passthrough else text,)


# ---------------------------------------------------------------------------
# Node 2: (AV) Matrix — all 10 categories in one node
# ---------------------------------------------------------------------------
class ArchVizPresetMatrix:
    """One-stop node: dropdowns for all categories, single assembled output.

    Fragment order (highest to lowest weight in final prompt):
      1. preservation  (anchors geometry — most important)
      2. camera        (composition)
      3. lighting
      4. atmosphere
      5. style         (photographic equipment + aesthetic)
      6. materials     (firm signature options included)
      7. people        (with ethnicity refinement)
      8. scale_life    (occupancy + activity)
      9. cars          (hero vehicle options)
      10. surroundings (context preservation/refinement)
      11. override     (free-form additions, optional)
    """

    @classmethod
    def INPUT_TYPES(cls):
        # target_model is appended AFTER the categories so that saved v4
        # workflows (whose widget values are positional) still map their 13
        # category selections correctly. A v4 workflow's trailing separator
        # value lands in target_model as an unknown profile, which safely
        # falls back to byte-identical v4 output.
        required = {cat: (_category_options(cat),) for cat in MATRIX_CATEGORIES}
        required["target_model"] = (profile_names(),)
        return {
            "required": required,
            "optional": {
                "override":  ("STRING", {"forceInput": True, "default": ""}),
                "separator": ("STRING", {"default": ". "}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "filename_tag")
    FUNCTION = "assemble"
    CATEGORY = "ArchViz"

    def assemble(self, target_model="nano_banana_edit", override="", separator=". ", **selections):
        # Resolve each category with model-aware overrides
        fragments = {
            cat: _resolve(cat, selections.get(cat, "(none)"), model=target_model)
            for cat in MATRIX_CATEGORIES
        }

        prompt = compile_prompt(
            fragments=fragments,
            profile_name=target_model,
            category_order=MATRIX_CATEGORIES,
            override=override,
            separator=separator,
        )

        # Filename tag: prioritize enhancement preset, then descriptive selections
        tag_parts = []
        if target_model and target_model != "nano_banana_edit":
            tag_parts.append(target_model.replace("_", "")[:10])
        # If enhancement is active, lead with that
        enh = selections.get("enhancement", "(none)")
        if enh and enh != "(none)":
            tag_parts.append(enh.replace("_", "")[:12])
        # Then add other distinctive selections
        for cat in ("lighting", "hero_style", "style", "people", "cars"):
            value = selections.get(cat, "(none)")
            if value and value != "(none)":
                tag_parts.append(value.replace("_", "")[:12])
        if not tag_parts:
            tag_parts = ["render"]
        filename_tag = "_".join(tag_parts[:3])

        return (prompt, filename_tag)


# ---------------------------------------------------------------------------
# Node 3: (AV) Assembler — manual concatenator (kept for advanced wiring)
# ---------------------------------------------------------------------------
class ArchVizPromptAssembler:
    """Manual concatenator — 6 fragment slots, skips empty inputs."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"separator": ("STRING", {"default": ". "})},
            "optional": {
                f"fragment_{i}": ("STRING", {"forceInput": True, "default": ""})
                for i in range(1, 7)
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "assemble"
    CATEGORY = "ArchViz"

    def assemble(self, separator=". ", **kwargs):
        parts = [kwargs.get(f"fragment_{i}", "") for i in range(1, 7)]
        return (_join_fragments(parts, separator=separator),)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "ArchVizPresetLoader":    ArchVizPresetLoader,
    "ArchVizPresetMatrix":    ArchVizPresetMatrix,
    "ArchVizPromptAssembler": ArchVizPromptAssembler,
    "ArchVizScene":           ArchVizScene,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArchVizPresetLoader":    "(AV) Preset",
    "ArchVizPresetMatrix":    "(AV) Matrix",
    "ArchVizPromptAssembler": "(AV) Assembler",
    "ArchVizScene":           "(AV) Scene",
}

WEB_DIRECTORY = "./web"

print(f"[ArchViz] v5.2.0 loaded — 4 nodes, {len(profile_names())} target models, 13 categories + Scene projects")
print(f"[ArchViz] Presets file: {USER_PRESETS_PATH}")
