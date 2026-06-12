"""
v5 validation: (1) default profile output is byte-identical to v4 logic,
(2) side-by-side compilation of one preset stack into every model dialect.
Run from package root:  python3 tests/demo_compile.py
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Import the package under an importable alias (folder name has a hyphen).
import importlib.util
alias = ROOT.parent / "avps_pkg"
if not alias.exists():
    alias.symlink_to(ROOT)
sys.path.insert(0, str(ROOT.parent))
import avps_pkg as av

# --- A realistic stack: golden-hour hero exterior with an Emirati family ---
SELECTIONS = {
    "preservation": "preserve_exactly",
    "camera": "low_hero_angle",
    "lighting": None,            # filled below with a golden-hour-ish preset
    "atmosphere": None,
    "style": None,
    "materials": None,
    "people": "emirati",
    "population_density": None,
    "hero_style": None,
    "scale_life": None,
    "cars": None,
    "surroundings": None,
    "enhancement": "(none)",
}

presets = av._load_presets()

def pick(cat, *prefer):
    names = sorted(k for k in presets.get(cat, {}) if not k.startswith("_"))
    for p in prefer:
        for n in names:
            if p in n:
                return n
    return names[0] if names else "(none)"

SELECTIONS["lighting"] = pick("lighting", "golden")
SELECTIONS["atmosphere"] = pick("atmosphere", "clear", "warm")
SELECTIONS["style"] = pick("style", "editorial", "marketing")
SELECTIONS["materials"] = pick("materials", "travertine", "stone")
SELECTIONS["population_density"] = pick("population_density", "few", "sparse")
SELECTIONS["hero_style"] = pick("hero_style", "family")
SELECTIONS["scale_life"] = "(none)"
SELECTIONS["cars"] = "(none)"
SELECTIONS["surroundings"] = pick("surroundings", "desert", "preserve")

print("STACK:", json.dumps(SELECTIONS, indent=2))
print("=" * 78)

matrix = av.ArchVizPresetMatrix()

# --- 1) byte-identical v4 check -------------------------------------------
frags_v4 = [av._resolve(c, SELECTIONS.get(c) or "(none)") for c in av.MATRIX_CATEGORIES]
expected_v4 = av._join_fragments(frags_v4, ". ")
got_default, tag_default = matrix.assemble(target_model="nano_banana_edit",
                                           **{c: (SELECTIONS.get(c) or "(none)") for c in av.MATRIX_CATEGORIES})
assert got_default == expected_v4, "BYTE-COMPAT FAILED"
print(f"[PASS] nano_banana_edit output is byte-identical to v4 join "
      f"({len(got_default)} chars), tag={tag_default}")
print("=" * 78)

# --- 2) all dialects side by side -----------------------------------------
from avps_pkg.compilers import profile_names
for model in profile_names():
    prompt, tag = matrix.assemble(target_model=model,
                                  **{c: (SELECTIONS.get(c) or "(none)") for c in av.MATRIX_CATEGORIES})
    words = len(prompt.split())
    print(f"\n########## {model}  ({words} words, {len(prompt)} chars, tag={tag}) ##########")
    print(prompt)

print("\n[ALL PASS]")
