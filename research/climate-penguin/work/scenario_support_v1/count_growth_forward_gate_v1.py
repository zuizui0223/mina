"""Strict forward-year exploratory audit of Adelie nest growth versus September ice.

No future observed counts enter training. A fixed, intentionally simple ridge
specification compares no-change, site+time, and site+time+ice forecasts.
The annual count change has not been causally calibrated to climate. The
three-environment intersection is checked for support only, never fitted.
Pure Python stdlib; no external calls. Results retain all source rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "research/climate-penguin/outputs/climate_penguin/count_environment_annual_intervals.csv"
DEST = ROOT / "research/climate-penguin/outputs/count_growth_forward_gate_v1"
EXPECTED = DEST / "expected_receipt.json"
YEARS = (2015, 2016, 2017, 2018)
LAMBDA_SITE = 3.0
LAMBDA_YEAR = 3.0
LAMBDA_ICE = 8.0


def load_rows(path=SOURCE):
    with open(path, encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    out = []
    for r in records:
        if r["species_id"] != "ADPE" or r["same_known_method"] != "True":
            raise ValueError("unexpected species or count-method record")
        if int(r["gap"]) != 1 or int(r["end"]) != int(r["start"]) + 1:
            raise ValueError("unexpected observation interval")
        n0, n1 = float(r["n_start"]), float(r["n_end"])
        if n0 <= 0 or n1 <= 0:
            raise ValueError("zero or negative count in log-growth cohort")
        y = float(r["log_growth"])
        if abs(y - math.log(n1 / n0)) > 1e-10:
            raise ValueError("growth and original counts disagree")
        ice = float(r["start_near_sic"])
        if not math.isfinite(ice):
            raise ValueError("missing primary sea-ice exposure")
        out.append(dict(
            site_id=r["site_id"], region=r["region"], start=int(r["start"]),
            end=int(r["end"]), y=y, ice=ice, timing=r["timing_supported"] == "True",
            full=all(r[k] != "" and math.isfinite(float(r[k])) for k in
                     ("start_near_sic", "start_surface_salinity",
                      "start_surface_potential_temperature_c"))
        ))
    return sorted(out, key=lambda z: (z["start"], z["site_id"], z["end"]))


def linear_solve(a, b):
    """Gaussian elimination with partial pivoting for a small ridge system."""
    n = len(b)
    m = [list(a[i]) + [b[i]] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda j: abs(m[j][k]))
        if abs(m[pivot][k]) < 1e-13:
            raise ValueError("singular ridge normal equations")
        m[k], m[pivot] = m[pivot], m[k]
        z = m[k][k]
        for j in range(k, n + 1):
            m[k][j] /= z
        for i in range(n):
            if i == k:
                continue
            z = m[i][k]
            for j in range(k, n + 1):
                m[i][j] -= z * m[k][j]
    return [r[n] for r in m]


def fit(train, with_ice, lambda_ice=LAMBDA_ICE):
    """Train with strictly earlier start years and training-only scaling."""
    sites = sorted({r["site_id"] for r in train})
    mu = sum(r["ice"] for r in train) / len(train)
    sd = math.sqrt(sum((r["ice"] - mu)**2 for r in train) / len(train)) or 1.0

    def design(r):
        return ([1.0, (r["start"] - 2013.0) / 3.0]
                + [float(r["site_id"] == site) for site in sites]
                + ([(r["ice"] - mu) / sd] if with_ice else []))

    n = 2 + len(sites) + int(with_ice)
    gram = [[0.0] * n for _ in range(n)]
    rhs = [0.0] * n
    for r in train:
        x = design(r)
        for i in range(n):
            rhs[i] += x[i] * r["y"]
            for j in range(n):
                gram[i][j] += x[i] * x[j]
    penalties = [0.0, LAMBDA_YEAR] + [LAMBDA_SITE] * len(sites)
    if with_ice:
        penalties.append(lambda_ice)
    for i in range(n):
        gram[i][i] += penalties[i]
    beta = linear_solve(gram, rhs)

    def predict(r):
        return sum(x * b for x, b in zip(design(r), beta))
    return predict


def metrics(preds):
    if not preds:
        return dict(n=0, sites=0)
    fields = ("nochange", "siteyear", "siteyear_ice")
    output = dict(n=len(preds), sites=len({p["site_id"] for p in preds}))
    for field in fields:
        errors = [p[field] - p["observed_log_growth"] for p in preds]
        output["mae_" + field] = sum(map(abs, errors)) / len(errors)
        output["rmse_" + field] = math.sqrt(sum(e * e for e in errors) / len(errors))
    return output


def run(rows, ice_penalty=LAMBDA_ICE):
    predictions, folds, full_folds = [], [], []
    for year in YEARS:
        train = [r for r in rows if r["start"] < year]
        sites = {r["site_id"] for r in train}
        test = [r for r in rows if r["start"] == year and r["site_id"] in sites]
        if len(train) < 30:
            raise ValueError("support for fixed fold unexpectedly changed")
        pred_base = fit(train, with_ice=False)
        pred_ice = fit(train, with_ice=True, lambda_ice=ice_penalty)
        for r in test:
            predictions.append(dict(
                test_start_year=year, test_end_year=r["end"],
                site_id=r["site_id"], region=r["region"],
                source_count_timing_supported=r["timing"],
                observed_log_growth=r["y"],
                nochange=0.0, siteyear=pred_base(r),
                siteyear_ice=pred_ice(r), training_rows=len(train)
            ))
        folds.append(dict(year=year, training_rows=len(train),
                          training_sites=len(sites), test_seen_rows=len(test),
                          test_timing_rows=sum(r["timing"] for r in test),
                          metrics=metrics([p for p in predictions if p["test_start_year"] == year])))
        full_train = [r for r in train if r["full"]]
        full_test = [r for r in rows if r["start"] == year and r["full"]]
        full_sites = {r["site_id"] for r in full_train}
        full_seen = [r for r in full_test if r["site_id"] in full_sites]
        full_folds.append(dict(year=year, training_complete=len(full_train),
                               training_sites=len(full_sites),
                               training_regions=len({r["region"] for r in full_train}),
                               test_complete=len(full_test),
                               test_seen=len(full_seen),
                               test_seen_timing=sum(r["timing"] for r in full_seen)))
    all_metrics = metrics(predictions)
    strict_metrics = metrics([p for p in predictions if p["source_count_timing_supported"]])
    full = [r for r in rows if r["full"]]
    return dict(
        source_rows=len(rows), source_sites=len({r["site_id"] for r in rows}),
        source_regions=len({r["region"] for r in rows}),
        full_rows=len(full), full_sites=len({r["site_id"] for r in full}),
        full_timing_rows=sum(r["timing"] for r in full),
        full_timing_sites=len({r["site_id"] for r in full if r["timing"]}),
        all_metrics=all_metrics, strict_metrics=strict_metrics,
        folds=folds, full_folds=full_folds, predictions=predictions
    )


def check_receipt(result, expected):
    support = expected["full_support"]
    checks = dict(all_intervals=result["source_rows"],
                  interval_sites=result["source_sites"],
                  interval_regions=result["source_regions"],
                  three_environment_complete=result["full_rows"],
                  three_environment_sites=result["full_sites"],
                  complete_timing_supported=result["full_timing_rows"],
                  complete_timing_sites=result["full_timing_sites"],
                  three_env_seen_forward_test=sum(x["test_seen"] for x in result["full_folds"]),
                  three_env_seen_forward_timing=sum(x["test_seen_timing"] for x in result["full_folds"]))
    for k, v in support.items():
        if checks[k] != v:
            raise ValueError(f"full-support receipt mismatch: {k}: {checks[k]} vs {v}")
    fwd = expected["forward_support"]
    actual = dict(test_intervals=result["all_metrics"]["n"],
                  test_sites=result["all_metrics"]["sites"],
                  strict_test_intervals=result["strict_metrics"]["n"],
                  strict_test_sites=result["strict_metrics"]["sites"],
                  fold_train_rows=[x["training_rows"] for x in result["folds"]],
                  fold_test_seen=[x["test_seen_rows"] for x in result["folds"]])
    for k, v in fwd.items():
        if actual[k] != v:
            raise ValueError(f"forward-support receipt mismatch: {k}")
    for k, prefix in (("all", "all_metrics"), ("timing", "strict_metrics")):
        for field, v in expected["metrics"][k].items():
            source_key = field.replace("nochange", "nochange").replace("siteyear_ice", "siteyear_ice")
            if field == "n":
                got = result[prefix]["n"]
            else:
                got = result[prefix][source_key]
            if not math.isclose(got, v, abs_tol=1e-9, rel_tol=1e-9):
                raise ValueError(f"metric mismatch {k}/{field}: {got} != {v}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=DEST)
    parser.add_argument("--check-receipt", action="store_true")
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    rows = load_rows(args.source)
    res = run(rows)
    if args.check_receipt:
        frozen = json.loads(EXPECTED.read_text(encoding="utf-8"))
        check_receipt(res, frozen)
        for lam, expected_mae in frozen["ice_penalty_sensitivity_mae"].items():
            sensitivity = run(rows, float(lam))["all_metrics"]["mae_siteyear_ice"]
            if not math.isclose(sensitivity, expected_mae, abs_tol=1e-9, rel_tol=1e-9):
                raise ValueError("penalty sensitivity mismatch: " + lam)
    args.output.mkdir(parents=True, exist_ok=True)
    with open(args.output / "forward_predictions.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(res["predictions"][0]))
        writer.writeheader()
        writer.writerows(res["predictions"])
    result = {k: v for k, v in res.items() if k != "predictions"}
    result["source_sha256"] = hashlib.sha256(source_bytes).hexdigest()
    result["head_note"] = ("Exploratory fixed-ridge rolling same-site diagnostic; "
                           "ice at interval start, no future counts in training; "
                           "no significance, no validated nesting forecast.")
    with open(args.output / "result.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"all": res["all_metrics"], "timing": res["strict_metrics"],
                      "complete_env": res["full_rows"],
                      "complete_env_seen_forward": sum(x["test_seen"] for x in res["full_folds"]),
                      "receipt_checked": bool(args.check_receipt)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
