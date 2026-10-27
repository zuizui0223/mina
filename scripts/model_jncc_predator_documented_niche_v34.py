#!/usr/bin/env python3
"""V34 actual original Stanbury predator source-label niches; not occupancy SDMs.

No JNCC seabird count, share, concentration or other response is downloaded/read.
Predicts whether first-party source *labels* (1/2) are present versus mixed
"assumed or known absent" 0. These are NOT calibrated true predator probabilities.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import audit_jncc_predator_island_source_v33 as v33

TAXA = (
    "American mink",
    "Brown rat",
    "House mouse",
    "European hedgehog",
    "Stoat",
)
MIN_ISLAND_AREA_HA = 10.0
BINS = ((10.0, 50.0, "(10,50] ha"), (50.0, 500.0, "(50,500] ha"),
        (500.0, float("inf"), ">500 ha"))
FEATURE_NAMES = ("log1p_area", "latitude", "longitude", "log1p_resident_population")
MIN_TEST_POS = 3
MIN_TEST_REF = 3
SPATIAL_CELL_DEGREES = 1
N_FOLDS = 5


def area_bin(area: float) -> str:
    for low, high, label in BINS:
        if low < area <= high:
            return label
    raise ValueError("SOURCE_COHORT_GATE source area outside >10ha primary cohort")


def source_cohort(island_meta: dict[int, dict], status_rows: list[dict]) -> list[dict]:
    lookup = {}
    for record in status_rows:
        lowid = record["lowid"]
        if lowid in lookup:
            raise ValueError("SOURCE_ID_GATE duplicate ESM5 lowid")
        lookup[lowid] = record
    if set(lookup) != set(island_meta):
        raise ValueError("SOURCE_ID_GATE exact full original RSPB 9688 <> Stanbury ESM5")
    selected = []
    for lowid in sorted(lookup):
        meta = island_meta[lowid]
        value = meta.get("low_tide_area_h")
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            continue
        if not value > MIN_ISLAND_AREA_HA:
            continue
        selected.append({"lowid": lowid, "meta": meta,
                         "status": lookup[lowid]["status_codes"]})
    return selected


def finite_float(value) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) else None


def cohort_descriptives(cohort: list[dict], taxon: str) -> dict:
    out = {}
    for group_name, eligible in (
        *((label, [r for r in cohort if area_bin(r["meta"]["low_tide_area_h"]) == label])
          for _, _, label in BINS),
        ("population_zero", [r for r in cohort if finite_float(r["meta"].get("human_population")) == 0]),
        ("population_positive", [r for r in cohort if (finite_float(r["meta"].get("human_population")) or 0) > 0]),
        ("population_missing", [r for r in cohort if (
            finite_float(r["meta"].get("human_population")) is None or
            finite_float(r["meta"].get("human_population")) < 0
        )]),
    ):
        codes = Counter(r["status"].get(taxon, "<MISSING>") for r in eligible)
        out[group_name] = {
            "islands_n": len(eligible),
            "source_code_counts": dict(sorted(codes.items())),
            "documented_confirmed_or_probable_n": codes["1"] + codes["2"],
            "source_positive_per_all_islands": (
                (codes["1"] + codes["2"]) / len(eligible) if eligible else None
            ),
            "unknown_possible_code3_n": codes["3"],
            "reference_zero_includes_assumed_absence_n": codes["0"],
        }
    return out


def make_model_arrays(cohort: list[dict], taxon: str):
    records = []
    removal = Counter()
    for record in cohort:
        status = str(record["status"].get(taxon, "")).strip()
        if status not in {"0", "1", "2"}:
            removal["source_status_possible3_or_unresolved"] += 1
            continue
        m = record["meta"]
        area = finite_float(m.get("low_tide_area_h"))
        lat = finite_float(m.get("latitude"))
        lon = finite_float(m.get("longitude"))
        population = finite_float(m.get("human_population"))
        if any(v is None for v in (area, lat, lon, population)):
            removal["incomplete_original_predictor"] += 1
            continue
        if area <= MIN_ISLAND_AREA_HA or population < 0 or not (48 <= lat <= 63.5) or not (-13.5 <= lon <= 3.5):
            removal["source_predictor_outside_defined_geography"] += 1
            continue
        records.append({
            "lowid": record["lowid"],
            "y": int(status in {"1", "2"}),
            "status": status,
            "x": [math.log1p(area), lat, lon, math.log1p(population)],
            "group": f"{math.floor(lat)}:{math.floor(lon)}",
            "population": population,
        })
    return records, removal


def evaluate_spatial_label_model(records: list[dict]) -> dict:
    if not records:
        return {"status": "STOP_NO_SOURCE_LABEL_AND_COMPLETE_COVARIATE_ROWS"}
    y = np.array([r["y"] for r in records], dtype=int)
    x = np.array([r["x"] for r in records], dtype=float)
    groups = np.array([r["group"] for r in records])
    profile = {
        "source_complete_case_islands": len(records),
        "source_positive_confirmed_or_probable": int(y.sum()),
        "reference_mixed_assumed_or_known_absence": int(len(y)-y.sum()),
        "original_distinct_1degree_geographic_cells": len(set(groups)),
        "original_coordinate_spatial_holdout_degree": SPATIAL_CELL_DEGREES,
        "group_kfold": N_FOLDS,
    }
    if len(set(groups)) < N_FOLDS or y.sum() < N_FOLDS*MIN_TEST_POS or (len(y)-y.sum()) < N_FOLDS*MIN_TEST_REF:
        return {"status": "STOP_SPATIAL_LABEL_SUPPORT", **profile}
    splits = list(GroupKFold(n_splits=N_FOLDS).split(x, y, groups=groups))
    for train_ix, test_ix in splits:
        test_y = y[test_ix]
        train_y = y[train_ix]
        if (
            test_y.sum() < MIN_TEST_POS
            or len(test_y) - test_y.sum() < MIN_TEST_REF
            or len(set(train_y)) < 2
        ):
            return {
                "status": "STOP_SPATIAL_TEST_FOLD_CLASS_IMBALANCE",
                **profile,
                "per_fold_test_label_support": [
                    {"fold": i, "test_n": len(s[1]), "source_positives": int(y[s[1]].sum())}
                    for i, s in enumerate(splits)
                ],
            }
    preds = {"prevalence_null": np.zeros(len(y)), "G": np.zeros(len(y)),
             "GH": np.zeros(len(y))}
    per_fold = []
    for fold, (train_ix, test_ix) in enumerate(splits):
        train_y = y[train_ix]
        rate = float(train_y.mean())
        preds["prevalence_null"][test_ix] = rate
        for key, cols in (("G", slice(0,3)), ("GH", slice(0,4))):
            model = make_pipeline(
                StandardScaler(),
                LogisticRegression(max_iter=1000, C=1, solver="lbfgs"),
            )
            model.fit(x[train_ix, cols], train_y)
            preds[key][test_ix] = model.predict_proba(x[test_ix, cols])[:,1]
        per_fold.append({
            "fold": fold,
            "islands_n": len(test_ix),
            "source_positive_n": int(y[test_ix].sum()),
            "reference_n": int(len(test_ix) - y[test_ix].sum()),
            "group_cells": len(set(groups[test_ix])),
            "brier_prevalence": float(brier_score_loss(y[test_ix],preds["prevalence_null"][test_ix])),
            "brier_G": float(brier_score_loss(y[test_ix],preds["G"][test_ix])),
            "brier_GH": float(brier_score_loss(y[test_ix],preds["GH"][test_ix])),
        })
    scores = {}
    for key, pred in preds.items():
        scores[key] = {
            "heldout_brier":float(brier_score_loss(y,pred)),
            "heldout_log_loss":float(log_loss(y,pred,labels=[0,1])),
            "heldout_auc":float(roc_auc_score(y,pred)),
            "heldout_average_precision":float(average_precision_score(y,pred)),
        }
    full = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000,C=1,solver="lbfgs")
    )
    full.fit(x,y)
    return {
        "status":"GEOGRAPHICALLY_CROSSVALIDATED_ORIGINAL_SOURCE_LABEL_PREDICTION_ONLY",
        **profile,
        "scores":scores,
        "brier_gain_G_vs_prevalence":scores["prevalence_null"]["heldout_brier"]-scores["G"]["heldout_brier"],
        "brier_gain_GH_vs_G":scores["G"]["heldout_brier"]-scores["GH"]["heldout_brier"],
        "source_label_GH_standardized_coefficients_not_causal":dict(zip(FEATURE_NAMES,map(float,full[-1].coef_[0]))),
        "source_label_GH_full_sample_intercept":float(full[-1].intercept_[0]),
        "per_fold":per_fold,
        "original_source_rank0_is_mixed_assumed_or_known_absence":True,
        "not_an_occupancy_probability_niche_model":True,
        "not_a_penguin_or_seabird_population_effect":True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path,required=True)
    args=ap.parse_args()
    report={
        "status":"SOURCE_ONLY_PREDATOR_NICHE_AUDIT_IN_PROGRESS",
        "source_interpretation":"SOURCE_RECORDED_POSITIVE_VS_ASSUMED_OR_KNOWN_ABSENT_NOT_TRUE_OCCUPANCY",
        "stanbury_ESM5_exact_sha256":"3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5",
        "taxa":list(TAXA),
        "low_tide_primary_area_ha":">10",
        "JNCC_breeding_outcome_records_opened":0,
        "JNCC_predator_ecological_effect_fitted":False,
    }
    try:
        island_ids, islands, meta=v33.fetch_rpsb_islands()
        original=v33.bounded_get(v33.SUPPLEMENTS["ESM5"],v33.MAX_SUPP_BYTES)
        if hashlib.sha256(original).hexdigest()!=report["stanbury_ESM5_exact_sha256"]:
            raise ValueError("SOURCE_SHA_GATE Stanbury original ESM5 changed")
        extracted=[]
        workbook,sheets=v33.sheet_rows(original,islands,extracted)
        if not len(islands)==len(extracted)==len(island_ids)==9688:
            raise ValueError("SOURCE_COHORT_GATE incomplete original RSPB/Stanbury lowid join")
        cohort=source_cohort(islands,extracted)
        if len(cohort)!=506:
            raise ValueError("SOURCE_COHORT_GATE >10ha low-tide reference changed")
        report["source_RSPB_island_point_n"]=len(islands)
        report["source_ESM5_matched_island_n"]=len(extracted)
        report["source_low_tide_area_gt10ha_eligible_island_n"]=len(cohort)
        taxa={}
        for taxon in TAXA:
            description=cohort_descriptives(cohort,taxon)
            rows,drop=make_model_arrays(cohort,taxon)
            niche=evaluate_spatial_label_model(rows)
            taxa[taxon]={
                "source_status_distribution_by_fixed_environment":description,
                "complete_case_removed_by_rule":dict(drop),
                "geographically_heldout_original_source_label_model":niche,
            }
        report["predator_taxa_source_profiles"]=taxa
        report["status"]="V34_ORIGINAL_PREDATOR_SOURCE_LABEL_NICHE_PROFILE_COMPLETED"
        report["scientific_conclusion_ceiling"]="SOURCE-DOCUMENTED DISTRIBUTION AND EXPLORATORY LABEL MODEL ONLY; NO CALIBRATED TRUE OCCUPANCY OR SEABIRD CAUSATION"
    except Exception as exc:
        report["status"]="V34_SOURCE_OR_SCHEMA_HOLD_NOT_AN_ECOLOGICAL_NULL"
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)[:500]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # Log compact numerical summary rather than all raw source rows.
    print(json.dumps({
        "status":report["status"],
        "source_eligible_islands":report.get("source_low_tide_area_gt10ha_eligible_island_n"),
        "results":{
            taxon: {
                "status":item["geographically_heldout_original_source_label_model"]["status"],
                "source_positive":item["source_status_distribution_by_fixed_environment"]["(10,50] ha"]["documented_confirmed_or_probable_n"]
                    +item["source_status_distribution_by_fixed_environment"]["(50,500] ha"]["documented_confirmed_or_probable_n"]
                    +item["source_status_distribution_by_fixed_environment"][">500 ha"]["documented_confirmed_or_probable_n"],
                "brier_G_gain_vs_prevalence":item["geographically_heldout_original_source_label_model"].get("brier_gain_G_vs_prevalence"),
                "brier_GH_gain_vs_G":item["geographically_heldout_original_source_label_model"].get("brier_gain_GH_vs_G")
            } for taxon,item in report.get("predator_taxa_source_profiles",{}).items()
        },
        "error":report.get("error"),
    },ensure_ascii=False))
    if report["status"]=="V34_SOURCE_OR_SCHEMA_HOLD_NOT_AN_ECOLOGICAL_NULL":
        raise SystemExit(2)


if __name__=="__main__":
    main()
