from __future__ import annotations

import importlib.util
from pathlib import Path


def load_guard_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "guard_ross_resight_outcome_access.py"
    spec = importlib.util.spec_from_file_location("ross_guard", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
