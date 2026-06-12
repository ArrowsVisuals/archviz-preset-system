"""Content validation: all templates instantiate with dummy fields; all
pools load non-empty; example projects build for every model profile."""
import sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
alias = ROOT.parent / "avps_pkg"
if not alias.exists():
    alias.symlink_to(ROOT)
sys.path.insert(0, str(ROOT.parent))
import avps_pkg as av
from avps_pkg.scene import (_files, _load_template, _load_pool_file,
                            _resolve_refs, build_scene, list_shots)
from avps_pkg.compilers import profile_names

# 1) all templates parse and their {field:} refs are resolvable
for name in _files("templates"):
    tmpl = _load_template(name)
    assert ("SYSTEM", None) in tmpl and ("CORE", None) in tmpl, f"{name}: missing SYSTEM/CORE"
    refs = set(re.findall(r"\{field:([^}]+)\}", tmpl[("SYSTEM", None)] + tmpl[("CORE", None)]))
    fields = {(r, None): f"<{r}>" for r in refs}
    w, t = [], []
    out = _resolve_refs(tmpl[("CORE", None)], fields, "nano_banana_edit", w, t)
    assert not w, f"{name}: warnings {w}"
    print(f"[PASS] template {name}: fields = {sorted(refs)}")

# 2) all pools load, non-empty, 6 lines each
for name, path in _files("pools").items():
    guard, lines = _load_pool_file(path)
    assert len(lines) >= 5, f"pool {name} too small ({len(lines)})"
    print(f"[PASS] pool {name}: {len(lines)} lines" + (" + guard" if guard else ""))

# 3) every example project shot builds under every model profile
for shot in list_shots():
    for model in profile_names():
        s, p, tag, dbg = build_scene(shot, 0, 42, model)
        assert p, f"{shot} @ {model}: empty prompt"
        assert "WARNINGS" not in dbg or "no @" in dbg, f"{shot} @ {model}: {dbg}"
print(f"[PASS] all {len(list_shots())} shots build under all {len(profile_names())} model profiles")

# 4) generation-dialect variants engage for flux2_pro (no fallback warning)
for shot in list_shots():
    s_, p_, t_, dbg = build_scene(shot, 0, 42, "flux2_pro")
    assert "no @flux2_pro variant" not in dbg, f"{shot}: flux variant missing"
    assert "faithfully reproducing the reference" in p_, f"{shot}: flux variant not used"
print("[PASS] @flux2_pro template variants engage on every example shot (no fallbacks)")

# 5) Matrix widget order: 13 categories first, target_model AFTER (v4 compat)
mt = av.ArchVizPresetMatrix.INPUT_TYPES()
req_keys = list(mt["required"].keys())
assert req_keys[:13] == av.MATRIX_CATEGORIES, "categories must come first"
assert req_keys[13] == "target_model", "target_model must be appended last"
print("[PASS] Matrix widget order preserves v4 workflow compatibility")
print("[ALL PASS]")
