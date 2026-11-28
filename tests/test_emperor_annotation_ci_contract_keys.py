"""Stop GitHub Actions from referencing nonexistent source-audit receipt keys.

Previous CI runs passed the scientific source table and focused tests but
failed only because the workflow called obsolete keys. This test reads code
and a frozen JSON receipt; it does not open the satellite XLSX or fit biology.
"""
import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/emperor-colony-evidence-v1.yml"
SCRIPT = ROOT / "scripts/audit_larue_2024_annotation_ice_bird_state_v1.py"
FROZEN = ROOT / "results/EMPEROR_LARUE_AUTHOR_NO_IMAGE_ICE_BIRD_ANNOTATIONS_V1.json"
STAGE = "      - name: Audit all literal No image states with author notes, ice vs bird nondetection"


def source_return_keys():
    tree = ast.parse(SCRIPT.read_text(encoding="utf8"))
    audit = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "audit")
    return_values = [x.value for x in ast.walk(audit)
                     if isinstance(x, ast.Return) and isinstance(x.value, ast.Dict)]
    assert len(return_values) == 1
    return {
        k.value for k in return_values[0].keys
        if isinstance(k, ast.Constant) and isinstance(k.value, str)
    }


def workflow_expectations():
    txt = WORKFLOW.read_text(encoding="utf8")
    assert txt.count(STAGE) == 1
    segment = txt.split(STAGE, 1)[1].split(
        "      - uses: actions/upload-artifact", 1
    )[0]
    return {
        "actual": set(re.findall(r"\bactual\[['\"]([^'\"]+)['\"]\]", segment)),
        "frozen": set(re.findall(r"\bfrozen\[['\"]([^'\"]+)['\"]\]", segment)),
    }


def test_annotation_action_receipt_key_contract():
    referenced = workflow_expectations()
    actual_keys = source_return_keys()
    frozen_keys = set(json.loads(FROZEN.read_text(encoding="utf8")))
    assert referenced["actual"] <= actual_keys, (
        "Workflow uses nonexistent actual output keys: "
        + ", ".join(sorted(referenced["actual"] - actual_keys))
    )
    assert referenced["frozen"] <= frozen_keys, (
        "Workflow uses nonexistent frozen result keys: "
        + ", ".join(sorted(referenced["frozen"] - frozen_keys))
    )
    assert len(referenced["actual"]) >= 10
    assert len(referenced["frozen"]) >= 6
