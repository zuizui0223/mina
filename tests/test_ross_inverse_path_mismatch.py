from pathlib import Path
import importlib.util
import math

SCRIPT = Path("scripts/analyze_ross_inverse_path_mismatch.py")
spec = importlib.util.spec_from_file_location("ross_inverse", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_loss_gain_vectors_and_effect_size():
    x = mod.read(Path("external/ross_island_v2_frozen_counts.csv"))
    loss = [x[1999][u]-x[2001][u] for u in mod.UNITS]
    gain = [x[2002][u]-x[2001][u] for u in mod.UNITS]
    L, G = sum(loss), sum(gain)
    expected = [G*z/L for z in loss]
    residual = [g-e for g,e in zip(gain,expected)]
    mismatch = 0.5*sum(abs(z) for z in residual)
    cosine = mod.dot(loss,gain)/(mod.norm(loss)*mod.norm(gain))
    assert L == 112613
    assert G == 109198
    assert math.isclose(mismatch/G, 0.09405445040386184, rel_tol=1e-12)
    assert math.isclose(cosine, 0.9969470572957101, rel_tol=1e-12)
    positive = [u for u,z in zip(mod.UNITS,residual) if z>0]
    assert positive == ["Cape Crozier West"]
