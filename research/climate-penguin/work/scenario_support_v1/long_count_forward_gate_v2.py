"""Exploratory 301-interval Adelie nest-count rolling hindcast (2005–2018).

Model comparison is post-outcome exploratory and frozen here for reproducibility:
no growth, ridge(site+time), and six fixed variants using near/offshore sea ice.
Start-season SIC is available before the next count; end-season SIC and annual
change are conditional hindsight diagnostics, NOT prospective forecasts.
Source record is never overwritten. Only Python stdlib is required.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "research/climate-penguin/outputs/long_count_seaice_v1/intervals.csv"
OUT = ROOT / "research/climate-penguin/outputs/long_count_forward_gate_v2"
EXPECTED = OUT / "expected_receipt.json"
TEST_YEARS = tuple(range(2005, 2019))
SPEC = {
    "site": (),
    "near": ("near",),
    "far": ("far",),
    "both": ("near", "far"),
    "end": ("near_end",),
    "delta": ("delta",)
}
LAMBDA_YEAR = 3.0
LAMBDA_SITE = 3.0
LAMBDA_CLIMATE = 8.0


def rows_from_source(path=SOURCE):
    with open(path, newline="", encoding="utf-8") as fh:
        raw = list(csv.DictReader(fh))
    rows = []
    for z in raw:
        if z["species_id"] != "ADPE" or z["same_known_method"] != "True":
            raise ValueError("non-ADPE or mismatched survey method")
        start, end, gap = (int(z[k]) for k in ("start", "end", "gap"))
        n0, n1 = (float(z[k]) for k in ("n_start", "n_end"))
        if gap != 1 or end != start + 1 or n0 <= 0 or n1 <= 0:
            raise ValueError("unexpected censuses or nonpositive abundance")
        rate = float(z["log_growth"])
        near, end_ice, far = (float(z[k]) for k in ("near_start", "near_end", "offshore_start"))
        if not all(map(math.isfinite, (rate, near, end_ice, far))):
            raise ValueError("missing environmental exposure")
        if not math.isclose(rate, math.log(n1 / n0), abs_tol=1e-10):
            raise ValueError("count growth source mismatch")
        if not math.isclose(float(z["near_change10"]), (end_ice-near)/10.0, abs_tol=1e-10):
            raise ValueError("SIC source change mismatch")
        rows.append({
            "id": z["site_id"], "region": z["region"],
            "start": start, "end": end, "y": rate,
            "n_start": n0, "n_end": n1,
            "near": near, "near_end": end_ice, "far": far,
            "timing": z["both_all_after_september"] == "True"
        })
    rows.sort(key=lambda z: (z["start"], z["id"]))
    return rows


def solve(gram, rhs):
    n = len(rhs)
    work = [list(row) + [rhs[i]] for i, row in enumerate(gram)]
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(work[i][k]))
        if abs(work[p][k]) < 1e-12:
            raise ValueError("singular ridge system")
        work[k], work[p] = work[p], work[k]
        v = work[k][k]
        for j in range(k, n+1):
            work[k][j] /= v
        for i in range(n):
            if i == k:
                continue
            v = work[i][k]
            for j in range(k, n+1):
                work[i][j] -= v * work[k][j]
    return [r[n] for r in work]


def fit(train, variables, climate_penalty=LAMBDA_CLIMATE):
    sites = sorted({r["id"] for r in train})
    def raw_value(r, v):
        return r["near_end"] - r["near"] if v == "delta" else r[v]
    stats = []
    for v in variables:
        mean = sum(raw_value(r, v) for r in train) / len(train)
        sd = math.sqrt(sum((raw_value(r, v) - mean)**2 for r in train) / len(train)) or 1.0
        stats.append((v, mean, sd))
    def features(r):
        return ([1.0, (r["start"] - 2000.0) / 10.0]
                + [float(r["id"] == s) for s in sites]
                + [(raw_value(r, v) - mu) / sd for v, mu, sd in stats])
    n = 2 + len(sites) + len(variables)
    A = [[0.0] * n for _ in range(n)]
    b = [0.0] * n
    for r in train:
        x = features(r)
        for i in range(n):
            b[i] += x[i] * r["y"]
            for j in range(n):
                A[i][j] += x[i]*x[j]
    for i in range(1, n):
        A[i][i] += LAMBDA_YEAR if i == 1 else (LAMBDA_SITE if i < 2 + len(sites) else climate_penalty)
    beta = solve(A, b)
    def predict(r):
        return sum(x * c for x, c in zip(features(r), beta))
    return predict


def metrics(rows):
    result = {
        "n": len(rows), "sites": len({r["site_id"] for r in rows}),
        "regions": len({r["region"] for r in rows}),
        "years": len({r["test_start"] for r in rows})
    }
    if not rows:
        return result
    for model in ("zero", *SPEC):
        errs = [r[model] - r["observed_log_growth"] for r in rows]
        result[model+"_mae"] = sum(abs(v) for v in errs) / len(errs)
        result[model+"_rmse"] = math.sqrt(sum(v*v for v in errs)/len(errs))
    return result


def analyze(source, climate_penalty=LAMBDA_CLIMATE):
    out, folds = [], []
    for year in TEST_YEARS:
        train = [z for z in source if z["start"] < year]
        seen = {r["id"] for r in train}
        test = [z for z in source if z["start"] == year and z["id"] in seen]
        if len(train) < 100 or not test:
            raise ValueError("historical sample support changed")
        fns = {model: fit(train, variables, climate_penalty)
               for model, variables in SPEC.items()}
        for r in test:
            pred = {
                "site_id": r["id"], "region": r["region"],
                "test_start": r["start"], "test_end": r["end"],
                "observed_log_growth": r["y"],
                "base_nests": r["n_start"], "observed_end_nests": r["n_end"],
                "timing_supported": r["timing"],
                "zero": 0.0, "train_rows": len(train)
            }
            for k, fn in fns.items():
                pred[k] = fn(r)
            out.append(pred)
        folds.append({
            "year": year, "train_rows": len(train),
            "test_rows": len(test), "test_sites": len({r["id"] for r in test}),
            "timing_rows": sum(r["timing"] for r in test),
            "mae": {k: sum(abs(fn(r) - r["y"]) for r in test)/len(test)
                    for k, fn in {"zero": lambda r: 0.0, **fns}.items()}
        })
    subsets = {
        "all": metrics(out),
        "timing": metrics([r for r in out if r["timing_supported"]]),
        "nonVictoria": metrics([r for r in out if r["region"] != "Victoria Land"]),
        "timingNonVictoria": metrics([r for r in out
                                     if r["timing_supported"] and r["region"] != "Victoria Land"])
    }
    eq = {
        k: sum(f["mae"][k] for f in folds)/len(folds)
        for k in ("zero", *SPEC)
    }
    return {"source_rows": len(source), "source_sites": len({r["id"] for r in source}),
            "source_regions": len({r["region"] for r in source}),
            "subsets": subsets, "equal_year_mae": eq,
            "folds": folds, "predictions": out}


def verify(result, reference):
    if (result["source_rows"], result["source_sites"], result["source_regions"]) != (301, 33, 6):
        raise ValueError("source row/site/region support mismatch")
    for cohort, expected in reference["subsets"].items():
        got = result["subsets"][cohort]
        for key, value in expected.items():
            if isinstance(value, int):
                if got[key] != value:
                    raise ValueError(f"count changed {cohort}.{key}: {got[key]} vs {value}")
            elif not math.isclose(got[key], value, rel_tol=1e-9, abs_tol=1e-9):
                raise ValueError(f"metric changed {cohort}.{key}: {got[key]} vs {value}")
    for k, v in reference["equal_year_mae"].items():
        if not math.isclose(result["equal_year_mae"][k], v, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(f"year-weighted metric mismatch {k}")
    if [z["test_rows"] for z in result["folds"]] != reference["test_per_year"]:
        raise ValueError("test roster changed")
    if [z["train_rows"] for z in result["folds"]] != reference["train_per_year"]:
        raise ValueError("train history changed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=SOURCE)
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--check-receipt", action="store_true")
    args = ap.parse_args()
    rows = rows_from_source(args.source)
    output = analyze(rows)
    if args.check_receipt:
        frozen = json.loads(EXPECTED.read_text(encoding="utf-8"))
        verify(output, frozen)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/"predictions.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output["predictions"][0]))
        writer.writeheader()
        writer.writerows(output["predictions"])
    receipt = {k: v for k, v in output.items() if k != "predictions"}
    receipt["source_sha256"] = hashlib.sha256(args.source.read_bytes()).hexdigest()
    receipt["status"] = ("Post-result descriptive rolling hindcast, not climate causality "
                         "or calibrated future abundance projection.")
    (args.output/"result.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"source": len(rows), "tested": output["subsets"]["all"]["n"],
                      "timing": output["subsets"]["timing"]["n"],
                      "all_mae": {k: output["subsets"]["all"][k+"_mae"]
                                  for k in ("zero", "site", "near", "far", "both", "end", "delta")},
                      "receipt_verified": bool(args.check_receipt)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
