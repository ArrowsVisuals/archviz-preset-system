"""
ArchViz Preset System v5 — Model Dialect Compilers
==================================================

Takes the category-keyed prompt fragments resolved by the Matrix node and
compiles them into the native prompt dialect of the selected target model.

Why this exists
---------------
The v4 presets were written in Nano Banana's edit-instruction dialect
("change X, preserve Y, keep the input image identical"). Other models
speak different languages:

  - Flux 2 Pro wants one cohesive natural-prose creative brief
    (subject -> environment -> style -> technical), positive phrasing only.
  - Flux 2 Dev/Flex respond best to semi-structured / labeled prompts.
  - GPT Image 2 wants a concrete photographer's brief in labeled slots,
    with hype adjectives stripped and hard "must not drift" constraints.
  - Ideogram 4 was trained on structured JSON captions.
  - Nano Banana generate-mode wants creative-director narrative prose
    (no edit instructions, since there is nothing to edit).

Profiles are data, not code: see presets/model_profiles.json. Users can add
or tune a model dialect without touching Python.

Backward compatibility
----------------------
The "nano_banana_edit" profile uses format "v4_join", which reproduces the
v4 Matrix output byte-for-byte. It is the default. Existing workflows do
not change behavior.

License: MIT
"""

import json
import re
from pathlib import Path

NODE_DIR = Path(__file__).resolve().parent
PROFILES_PATH = NODE_DIR / "presets" / "model_profiles.json"

# Sentences containing these markers are edit-instructions that confuse
# pure text-to-image / scene-description models. Matched case-insensitively.
_EDIT_MARKERS = (
    "input image",
    "do not",
    "must remain",
    "preserve the exact",
    "remain identical",
    "minimal change",
    "only modification",
    "re-render",
    "via compositing",
    "identically",
    "as described below",
    "only surface-level",
    "shown in the input",
    "every other pixel",
)

# Conservative hype-word strip list (GPT Image 2 treats these as noise).
_HYPE_WORDS = (
    "stunning",
    "breathtaking",
    "masterpiece",
    "award-winning",
    "ultra-detailed",
    "ultra detailed",
)

_FALLBACK_PROFILES = {
    "nano_banana_edit": {
        "label": "Nano Banana (edit) — v4 default",
        "format": "v4_join",
    }
}


def load_profiles() -> dict:
    """Read model_profiles.json. Order of keys = dropdown order."""
    try:
        with PROFILES_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        profiles = {k: v for k, v in data.items() if not k.startswith("_")}
        if profiles:
            return profiles
    except (json.JSONDecodeError, OSError) as e:
        print(f"[ArchViz] Error reading model profiles: {e}")
    return dict(_FALLBACK_PROFILES)


def profile_names() -> list:
    return list(load_profiles().keys())


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------
def _sentences(text: str) -> list:
    """Split a fragment into rough sentences, keeping content intact."""
    parts = re.split(r"(?<=[.;])\s+", text.strip())
    return [p.strip().rstrip(".;").strip() for p in parts if p.strip()]


def _strip_edit_sentences(text: str) -> str:
    """Remove sentences that are edit-instructions rather than descriptions."""
    kept = []
    for s in _sentences(text):
        low = s.lower()
        if any(marker in low for marker in _EDIT_MARKERS):
            continue
        kept.append(s)
    return ". ".join(kept)


def _strip_hype(text: str) -> str:
    for w in _HYPE_WORDS:
        text = re.sub(rf"\b{re.escape(w)}\b,?\s*", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip(" ,")


def _word_count(text: str) -> int:
    return len(text.split())


def _join_prose(parts: list) -> str:
    cleaned = [p.strip().rstrip(" .,;") for p in parts if p and p.strip()]
    if not cleaned:
        return ""
    out = ". ".join(cleaned) + "."
    # Sentence-case each joined fragment start for readable prose.
    return re.sub(
        r"(^|\. )([a-z])", lambda m: m.group(1) + m.group(2).upper(), out
    )


# v4-exact join (must stay byte-identical to __init__._join_fragments)
def v4_join(parts: list, separator: str = ". ") -> str:
    cleaned = [p.strip().rstrip(" .,;") for p in parts if p and p.strip()]
    if not cleaned:
        return ""
    return separator.join(cleaned) + "."


# ---------------------------------------------------------------------------
# Compiler core
# ---------------------------------------------------------------------------
def compile_prompt(
    fragments: dict,
    profile_name: str,
    category_order: list,
    override: str = "",
    separator: str = ". ",
) -> str:
    """
    fragments       : {category: resolved_text} (empty strings allowed)
    profile_name    : key in model_profiles.json
    category_order  : canonical v4 category order (used by v4_join)
    override        : free-form user additions, appended last
    separator       : v4_join separator passthrough (ignored by other formats)
    """
    profiles = load_profiles()
    profile = profiles.get(profile_name) or _FALLBACK_PROFILES["nano_banana_edit"]
    fmt = profile.get("format", "v4_join")

    # ---- v4 byte-identical path -------------------------------------------
    if fmt == "v4_join":
        parts = [fragments.get(cat, "") for cat in category_order]
        if override and override.strip():
            parts.append(override.strip())
        return v4_join(parts, separator=separator)

    # ---- shared preprocessing for all v5 dialects -------------------------
    drop = set(profile.get("drop_categories", []))
    frag = {
        cat: text
        for cat, text in fragments.items()
        if text and text.strip() and cat not in drop
    }

    if profile.get("strip_edit_sentences"):
        frag = {c: _strip_edit_sentences(t) for c, t in frag.items()}
        frag = {c: t for c, t in frag.items() if t}

    if profile.get("strip_hype"):
        frag = {c: _strip_hype(t) for c, t in frag.items()}
        frag = {c: t for c, t in frag.items() if t}

    order = [c for c in profile.get("order", category_order) if c in frag]
    # Any resolved category the profile forgot to order goes at the end,
    # so user-added custom categories are never silently lost.
    order += [c for c in frag if c not in order]

    # ---- prose (Flux 2 Pro, Nano Banana generate) --------------------------
    if fmt == "prose":
        parts = []
        opener = profile.get("opener", "").strip()
        if opener:
            parts.append(opener)
        parts += [frag[c] for c in order]
        if override and override.strip():
            parts.append(override.strip())
        text = _join_prose(parts)

        budget = profile.get("word_budget")
        if budget:
            trim_order = [
                c for c in profile.get("trim_priority", []) if c in frag
            ]
            while _word_count(text) > budget and trim_order:
                victim = trim_order.pop(0)
                frag.pop(victim, None)
                kept = [opener] if opener else []
                kept += [frag[c] for c in order if c in frag]
                if override and override.strip():
                    kept.append(override.strip())
                text = _join_prose(kept)
        return text

    # ---- labeled slots (Flux 2 Dev structured, GPT Image 2 brief) ----------
    if fmt == "labeled":
        lines = []
        opener = profile.get("opener", "").strip()
        if opener:
            lines.append(opener)
        used = set()
        for slot_label, slot_cats in profile.get("slots", {}).items():
            texts = [frag[c] for c in slot_cats if c in frag]
            used.update(c for c in slot_cats if c in frag)
            if texts:
                lines.append(f"{slot_label}: {'; '.join(texts)}")
        leftovers = [frag[c] for c in order if c not in used]
        if leftovers:
            lines.append(f"Details: {'; '.join(leftovers)}")
        if override and override.strip():
            lines.append(f"Additional: {override.strip()}")
        return "\n".join(lines)

    # ---- JSON caption (Ideogram 4, Flux 2 Dev JSON) ------------------------
    if fmt == "json":
        obj = {}
        opener = profile.get("opener", "").strip()
        if opener:
            obj["scene"] = opener
        used = set()
        for key, slot_cats in profile.get("slots", {}).items():
            texts = [frag[c] for c in slot_cats if c in frag]
            used.update(c for c in slot_cats if c in frag)
            if texts:
                if key == "scene" and "scene" in obj:
                    obj["scene"] = obj["scene"] + " " + " ".join(texts)
                else:
                    obj[key] = "; ".join(texts)
        leftovers = [frag[c] for c in order if c not in used]
        if leftovers:
            obj["details"] = "; ".join(leftovers)
        if override and override.strip():
            obj["additional"] = override.strip()
        return json.dumps(obj, ensure_ascii=False, indent=2)

    # Unknown format — fail safe to v4 behavior.
    parts = [fragments.get(cat, "") for cat in category_order]
    if override and override.strip():
        parts.append(override.strip())
    return v4_join(parts, separator=separator)
