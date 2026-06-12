"""
(AV) Scene validation:
1. Determinism — same (shot, variation, seed) twice -> identical output
2. Exhaustive uniqueness — variations 0..215 produce 216 distinct pick-combos
3. Model awareness — system separate vs merged per profile; {preset:} refs resolve
4. Guard clause auto-append on the gardens pool
5. Output matches the user's original hand-written methodology
Run from package root:  python3 tests/demo_scene.py
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
alias = ROOT.parent / "avps_pkg"
if not alias.exists():
    alias.symlink_to(ROOT)
sys.path.insert(0, str(ROOT.parent))
import avps_pkg as av
from avps_pkg.scene import build_scene, list_shots, _load_project, _files, _load_pool_file, _variation_indices

shots = list_shots()
print("shots discovered:", shots)
assert "townhouses/front_marketing" in shots and "townhouses/back_garden" in shots

# 1) determinism
a = build_scene("townhouses/front_marketing", 7, 42, "nano_banana_edit")
b = build_scene("townhouses/front_marketing", 7, 42, "nano_banana_edit")
assert a == b, "determinism failed"
print("[PASS] deterministic: same inputs -> identical (system, prompt, tag, debug)")

# 2) exhaustive uniqueness across all 6*6*6 = 216 combos
sizes = [6, 6, 6]
seen = set()
for v in range(216):
    seen.add(tuple(_variation_indices(sizes, v, seed=42)))
assert len(seen) == 216, f"collision! only {len(seen)} unique of 216"
# and a different seed gives a different ordering
order_a = [tuple(_variation_indices(sizes, v, 42)) for v in range(5)]
order_b = [tuple(_variation_indices(sizes, v, 99)) for v in range(5)]
assert order_a != order_b
print("[PASS] variations 0..215 cover all 216 combinations exactly once; seed shuffles order")

# 3) model awareness
sys_nb, prompt_nb, tag_nb, dbg_nb = build_scene("townhouses/front_marketing", 0, 42, "nano_banana_edit")
sys_fx, prompt_fx, tag_fx, dbg_fx = build_scene("townhouses/front_marketing", 0, 42, "flux2_pro")
assert sys_nb and "photorealistic architectural visualization engine" in sys_nb
assert sys_fx == "", "flux2_pro should have no separate system output"
assert "faithfully reproducing the reference" in prompt_fx, "flux2_pro should use its generation-dialect template variant"
assert "RETEXTURING a locked design" not in prompt_fx, "edit-dialect system must not leak into flux prompt"
print("[PASS] nano_banana_edit -> separate edit system; flux2_pro -> dedicated generation-dialect variant, no edit leakage")

# 4) guard clause auto-append on back/gardens
_, prompt_back, tag_back, dbg_back = build_scene("townhouses/back_garden", 3, 42, "nano_banana_edit")
assert "Strictly no outdoor furniture" in prompt_back
assert "PARKED CARS" not in prompt_back  # back shot has no car pool
print("[PASS] guard clause appended to garden line; back shot uses only its own pool")

# 5) fidelity to original methodology
assert "boundary wall" in prompt_nb and "TRAVERTINE" in prompt_nb
assert "FOREGROUND:" in prompt_nb and "PARKED CARS:" in prompt_nb and "VEGETATION:" in prompt_nb
assert prompt_nb.count("\n\n") >= 3  # core + 3 slots joined by blank lines
print("[PASS] front prompt = CORE + people + cars + vegetation, blank-line joined (original methodology)")

print("\nfilename tags:", tag_nb, "|", tag_back)
print("\n----- debug output sample -----")
print(dbg_nb)
print("\n[ALL PASS]")
