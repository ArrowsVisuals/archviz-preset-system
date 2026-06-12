"""
ArchViz Preset System v5.1 — (AV) Scene
=======================================

Locked-project batch rendering with controlled variation, layered data,
and model-aware compilation. One node, three core widgets.

DATA LAYERS (each piece of text lives exactly once):
  presets/   style vocabulary  — shared with the (AV) Matrix ({preset:...})
  pools/     entourage lines   — global, one line = one option ({pool} slots)
  templates/ typology rules    — SYSTEM/CORE skeletons with {field:...} holes
  projects/  per-project file  — fills fields, picks pools, tiny

All four live under  ComfyUI/user/archviz_scenes/  after first run
(bundled examples auto-copy there; user edits survive package updates).

FILE FORMAT (plain text, section-based):
  === SYSTEM ===            section body until next header
  === CORE @flux2_pro ===   optional per-model variant of any section
  === FIELDS ===            one-line fields:  key: value
  === FIELD name ===        multiline field
  === SHOTS ===             shot lines:  front: people_street, cars_luxury
  === POOL name extends === project-local lines appended to a global pool
  Pool files may start with:  @guard: text appended to every line

REFERENCES inside any body text:
  {field:material_legend}   filled from the project file
  {preset:lighting/golden_hour}  pulled from the Matrix preset library
                                 (model-aware: per-preset overrides apply)

MODEL AWARENESS:
  - The Scene node has a target_model dropdown (same profiles as the Matrix).
  - Untagged SYSTEM/CORE sections are the default dialect (Nano Banana edit).
  - Add  === CORE @flux2_pro ===  variants where a model needs different
    phrasing. If a variant is missing, the default text is used verbatim and
    a warning is emitted (never silently rewritten — geometry-lock language
    is too important to mangle automatically).
  - model_profiles.json may define per-profile  "scene_system":
    "separate" (default) | "merge" (prepend system into prompt, for models
    without a system field) | "drop".

VARIATION MATH:
  variation + seed deterministically pick one line from each pool.
  Enumeration is exhaustive and collision-free: variations 0..N-1 cover
  every pool combination exactly once (mixed-radix decode), in a
  seed-shuffled order (affine bijection). Same (shot, variation, seed)
  always reproduces the same prompt.

License: MIT
"""

import re
from math import gcd
from pathlib import Path

NODE_DIR = Path(__file__).resolve().parent
COMFYUI_ROOT = NODE_DIR.parent.parent
BUNDLED_SCENES = NODE_DIR / "scene_data"
USER_SCENES = COMFYUI_ROOT / "user" / "archviz_scenes"

_SUBDIRS = ("templates", "pools", "projects")

_HEADER_RE = re.compile(r"^===\s*(.+?)\s*===\s*$")
_REF_RE = re.compile(r"\{(field|preset|pool):([^}]+)\}")


# ---------------------------------------------------------------------------
# First-run setup
# ---------------------------------------------------------------------------
# Files shipped by pre-release 5.2.x builds under old names. They were
# bundled content (not user-authored), so removing stale user-dir copies
# is safe and prevents duplicate entries in the shot dropdown.
_LEGACY_BUNDLED = [
    "projects/example_townhouses.txt",
    "projects/example_school.txt",
    "projects/example_perspective_villa.txt",
] + [f"projects/starter_{n}.txt" for n in (
    "villa", "townhouses", "tower", "apartments", "school",
    "mosque", "retail", "perspective", "interior", "renovation",
)]


def _ensure_user_scenes():
    """Copy bundled scene_data tree to user dir on first run, and remove
    stale copies of renamed bundled files from earlier 5.2.x builds."""
    import shutil
    if USER_SCENES.exists():
        removed = 0
        for rel in _LEGACY_BUNDLED:
            stale = USER_SCENES / rel
            if stale.exists():
                stale.unlink()
                removed += 1
        if removed:
            print(f"[ArchViz] Removed {removed} legacy bundled file(s) "
                  f"from {USER_SCENES} (renamed in 5.2.2)")
        return
    if not BUNDLED_SCENES.exists():
        return
    shutil.copytree(BUNDLED_SCENES, USER_SCENES)
    print(f"[ArchViz] First run — copied scene examples to {USER_SCENES}")


# ---------------------------------------------------------------------------
# File discovery (user dir wins over bundled by filename)
# ---------------------------------------------------------------------------
def _files(kind: str) -> dict:
    """{stem: Path} for one subdir, user files overriding bundled ones."""
    out = {}
    for root in (BUNDLED_SCENES, USER_SCENES):
        d = root / kind
        if d.is_dir():
            for p in sorted(d.glob("*.txt")):
                out[p.stem] = p
    return out


# ---------------------------------------------------------------------------
# Section parser
# ---------------------------------------------------------------------------
def _parse_sections(text: str) -> tuple:
    """Returns (preamble_lines, [(header, body_text), ...])."""
    preamble, sections = [], []
    current_header, current_body = None, []
    for line in text.splitlines():
        m = _HEADER_RE.match(line)
        if m:
            if current_header is not None:
                sections.append((current_header, "\n".join(current_body).strip()))
            current_header, current_body = m.group(1), []
        elif current_header is None:
            preamble.append(line)
        else:
            current_body.append(line)
    if current_header is not None:
        sections.append((current_header, "\n".join(current_body).strip()))
    return preamble, sections


def _split_model_tag(name: str) -> tuple:
    """'CORE @a, b' -> ('CORE', ['a', 'b']);  'CORE' -> ('CORE', [None])"""
    if "@" in name:
        base, _, tag = name.partition("@")
        tags = [t.strip() for t in tag.split(",") if t.strip()]
        return base.strip(), tags or [None]
    return name.strip(), [None]


# ---------------------------------------------------------------------------
# Pool loading
# ---------------------------------------------------------------------------
def _load_pool_file(path: Path) -> tuple:
    """Returns (guard, [lines]). '#' comments and blanks ignored."""
    guard, lines = "", []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("@guard:"):
            guard = line[len("@guard:"):].strip()
            continue
        lines.append(line)
    return guard, lines


# ---------------------------------------------------------------------------
# Template / project loading
# ---------------------------------------------------------------------------
def _load_template(name: str) -> dict:
    """{ (SECTION, model_tag_or_None): body }"""
    paths = _files("templates")
    if name not in paths:
        raise ValueError(
            f"[ArchViz Scene] template '{name}' not found. "
            f"Available: {', '.join(sorted(paths)) or '(none)'}"
        )
    _, sections = _parse_sections(paths[name].read_text(encoding="utf-8"))
    out = {}
    for header, body in sections:
        base, tags = _split_model_tag(header)
        for tag in tags:
            out[(base.upper(), tag)] = body
    return out


def _load_project(name: str) -> dict:
    """Parse a project file into a structured dict."""
    paths = _files("projects")
    if name not in paths:
        raise ValueError(f"[ArchViz Scene] project '{name}' not found")
    text = paths[name].read_text(encoding="utf-8")
    preamble, sections = _parse_sections(text)

    proj = {
        "name": name,
        "template": None,
        "fields": {},          # {(key, model_tag): value}
        "shots": {},           # {shot: [pool names]}
        "pool_extends": {},    # {pool: [extra lines]}
        "pool_replace": {},    # {pool: [lines]}
        "sections": {},        # project-level SYSTEM/CORE overrides
    }

    for line in preamble:
        line = line.strip()
        if line.lower().startswith("template:"):
            proj["template"] = line.split(":", 1)[1].strip()

    for header, body in sections:
        base, tags = _split_model_tag(header)
        parts = base.split()
        kind = parts[0].upper()
        for tag in tags:
            if kind == "FIELDS":
                for fl in body.splitlines():
                    if ":" in fl:
                        k, _, v = fl.partition(":")
                        proj["fields"][(k.strip(), tag)] = v.strip()
            elif kind == "FIELD" and len(parts) >= 2:
                proj["fields"][(parts[1], tag)] = body
            elif kind == "SHOTS":
                for sl in body.splitlines():
                    if ":" in sl:
                        shot, _, pools = sl.partition(":")
                        proj["shots"][shot.strip()] = [
                            p.strip() for p in pools.split(",") if p.strip()
                        ]
            elif kind == "POOL" and len(parts) >= 2:
                pool_name = parts[1]
                lines = [
                    l.strip() for l in body.splitlines()
                    if l.strip() and not l.strip().startswith("#")
                ]
                if "extends" in (p.lower() for p in parts[2:]):
                    proj["pool_extends"][pool_name] = lines
                else:
                    proj["pool_replace"][pool_name] = lines
            elif kind in ("SYSTEM", "CORE"):
                proj["sections"][(kind, tag)] = body

    if not proj["template"]:
        raise ValueError(
            f"[ArchViz Scene] project '{name}' has no 'template:' line"
        )
    return proj


# ---------------------------------------------------------------------------
# Model-aware section / field selection
# ---------------------------------------------------------------------------
DEFAULT_DIALECT = "nano_banana_edit"


def _pick(d: dict, key: str, model: str, warnings: list, what: str,
          warn_on_fallback: bool = False) -> str:
    """Model-tagged value wins; fall back to untagged.

    warn_on_fallback: sections (SYSTEM/CORE) warn whenever a non-default
    dialect falls back to default text — whether or not other model
    variants exist — because edit-dialect geometry language silently fed
    to a generation model is exactly the failure v5 exists to prevent.
    Fields never warn (untagged fields are the norm).
    """
    if (key, model) in d:
        return d[(key, model)]
    if (key, None) in d:
        if warn_on_fallback and model and model != DEFAULT_DIALECT:
            warnings.append(
                f"{what} '{key}' has no @{model} variant — using default "
                f"(edit-dialect) text"
            )
        return d[(key, None)]
    return ""


# ---------------------------------------------------------------------------
# Reference resolution
# ---------------------------------------------------------------------------
def _resolve_refs(text: str, fields: dict, model: str,
                  warnings: list, trace: list, depth: int = 0) -> str:
    if depth > 4:
        warnings.append("reference nesting deeper than 4 — stopped")
        return text

    def sub(m):
        kind, arg = m.group(1), m.group(2).strip()
        if kind == "field":
            val = _pick(fields, arg, model, warnings, "field")
            if not val:
                warnings.append(f"field '{arg}' is empty or missing")
            trace.append(f"[field:{arg}]")
            return _resolve_refs(val, fields, model, warnings, trace, depth + 1)
        if kind == "preset":
            # Lazy import to avoid a circular import at package load time.
            from . import _resolve as resolve_preset
            if "/" not in arg:
                warnings.append(f"bad preset ref '{arg}' (need category/name)")
                return ""
            cat, _, name = arg.partition("/")
            val = resolve_preset(cat, name, model=model)
            if not val:
                warnings.append(f"preset '{arg}' not found in library")
            trace.append(f"[preset:{arg}]")
            return val
        if kind == "pool":
            warnings.append(
                f"{{pool:{arg}}} found in body text — pools are attached via "
                f"the SHOTS section, not inline. Ignored."
            )
            return ""
        return m.group(0)

    return _REF_RE.sub(sub, text)


# ---------------------------------------------------------------------------
# Deterministic variation: exhaustive, collision-free, seed-shuffled
# ---------------------------------------------------------------------------
def _variation_indices(pool_sizes: list, variation: int, seed: int) -> list:
    """Map (variation, seed) -> one index per pool.

    Variations 0..total-1 cover every combination exactly once, in an order
    shuffled by the seed (affine bijection: pos = (a*v + b) mod total).
    """
    total = 1
    for n in pool_sizes:
        total *= max(n, 1)
    if total <= 1:
        return [0] * len(pool_sizes)

    v = variation % total
    a = (seed * 2654435761 + 1) % total
    a = a or 1
    while gcd(a, total) != 1:
        a += 1
    b = (seed * 40503 + 12345) % total
    pos = (a * v + b) % total

    indices = []
    for n in pool_sizes:
        n = max(n, 1)
        indices.append(pos % n)
        pos //= n
    return indices


# ---------------------------------------------------------------------------
# Shot list for the dropdown
# ---------------------------------------------------------------------------
def list_shots() -> list:
    shots = []
    for proj_name in _files("projects"):
        try:
            proj = _load_project(proj_name)
            for shot in proj["shots"]:
                shots.append(f"{proj_name}/{shot}")
        except Exception as e:
            print(f"[ArchViz Scene] skipping project '{proj_name}': {e}")
    return shots or ["(no projects found)"]


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------
def build_scene(shot_ref: str, variation: int, seed: int, model: str,
                style_override: str = "") -> tuple:
    """Returns (system_prompt, prompt, filename_tag, debug_report)."""
    if "/" not in shot_ref:
        raise ValueError(f"[ArchViz Scene] invalid shot '{shot_ref}'")
    proj_name, _, shot = shot_ref.partition("/")

    warnings, trace = [], []
    proj = _load_project(proj_name)
    tmpl = _load_template(proj["template"])
    trace.append(f"[template:{proj['template']}]")

    if shot not in proj["shots"]:
        raise ValueError(
            f"[ArchViz Scene] shot '{shot}' not in project '{proj_name}'. "
            f"Available: {', '.join(proj['shots'])}"
        )

    # Sections: project override beats template; model tag beats untagged.
    sections = dict(tmpl)
    sections.update(proj["sections"])
    system_raw = _pick(sections, "SYSTEM", model, warnings, "section",
                       warn_on_fallback=True)
    core_raw = _pick(sections, "CORE", model, warnings, "section",
                     warn_on_fallback=True)

    system_txt = _resolve_refs(system_raw, proj["fields"], model, warnings, trace)
    core_txt = _resolve_refs(core_raw, proj["fields"], model, warnings, trace)

    # Pools for this shot (project replace/extends cascade).
    pool_files = _files("pools")
    pool_names = proj["shots"][shot]
    pools, guards = [], []
    for pn in pool_names:
        if pn in proj["pool_replace"]:
            guard, lines = "", proj["pool_replace"][pn]
        elif pn in pool_files:
            guard, lines = _load_pool_file(pool_files[pn])
            lines = lines + proj["pool_extends"].get(pn, [])
        else:
            raise ValueError(
                f"[ArchViz Scene] pool '{pn}' (shot '{shot}') not found. "
                f"Available: {', '.join(sorted(pool_files)) or '(none)'}"
            )
        if not lines:
            raise ValueError(f"[ArchViz Scene] pool '{pn}' is empty")
        pools.append(lines)
        guards.append(guard)

    # Deterministic picks.
    sizes = [len(p) for p in pools]
    idx = _variation_indices(sizes, variation, seed)
    slot_lines = []
    for i, (lines, guard) in enumerate(zip(pools, guards)):
        line = _resolve_refs(lines[idx[i]], proj["fields"], model, warnings, trace)
        if guard:
            line = f"{line} {guard}"
        slot_lines.append(line)
        trace.append(f"[pool:{pool_names[i]}#{idx[i] + 1}/{sizes[i]}]")

    # Assemble prompt: core + slots (+ optional Matrix style bridge).
    parts = [core_txt] + slot_lines
    if style_override and style_override.strip():
        parts.append(style_override.strip())
        trace.append("[style_override]")
    prompt = "\n\n".join(p for p in parts if p)

    # Per-profile system handling for models without a system field.
    from .compilers import load_profiles
    profile = load_profiles().get(model, {})
    scene_system = profile.get("scene_system", "separate")
    if scene_system == "merge" and system_txt:
        prompt = f"{system_txt}\n\n{prompt}"
        system_txt = ""
        trace.append("[system merged into prompt]")
    elif scene_system == "drop":
        system_txt = ""
        trace.append("[system dropped per profile]")

    total = 1
    for n in sizes:
        total *= n
    tag = f"{proj_name[:10]}_{shot[:8]}_v{variation % max(total, 1):03d}_s{seed}"

    report_lines = [
        f"shot: {shot_ref}   model: {model}",
        f"variation {variation} of {total} unique combinations   seed {seed}",
        f"picks: " + ", ".join(
            f"{pool_names[i]} line {idx[i] + 1}" for i in range(len(pools))
        ),
        "sources: " + " ".join(trace),
    ]
    if warnings:
        report_lines.append("WARNINGS:")
        report_lines += [f"  - {w}" for w in warnings]
        for w in warnings:
            print(f"[ArchViz Scene] WARNING: {w}")
    debug = "\n".join(report_lines)

    return system_txt, prompt, tag, debug


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------
class ArchVizScene:
    """Locked-project batch renders with controlled, reproducible variation."""

    @classmethod
    def INPUT_TYPES(cls):
        from .compilers import profile_names
        return {
            "required": {
                "shot": (list_shots(),),
                "variation": ("INT", {"default": 0, "min": 0, "max": 999999,
                                      "control_after_generate": True}),
                "seed": ("INT", {"default": 42, "min": 0, "max": 2**31 - 1}),
                "target_model": (profile_names(),),
            },
            "optional": {
                "style_override": ("STRING", {"forceInput": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "system_prompt", "filename_tag", "debug")
    FUNCTION = "build"
    CATEGORY = "ArchViz"

    def build(self, shot, variation, seed, target_model, style_override=""):
        # Output order mirrors the Nano Banana / Gemini node's input order
        # (prompt above system_prompt) so connections run parallel.
        system_prompt, prompt, tag, debug = build_scene(
            shot, variation, seed, target_model, style_override)
        return (prompt, system_prompt, tag, debug)


_ensure_user_scenes()
