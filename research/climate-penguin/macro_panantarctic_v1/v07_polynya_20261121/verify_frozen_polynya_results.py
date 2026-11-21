#!/usr/bin/env python3
"""Independently reproduce existing frozen 439/358 polynya results offline.

This verifier reads SHA256-pinned observed inputs. It does not import any of the
original regression implementations, select new models, refit laboratory PLSR,
or infer new biological/causal confirmation. Fixed effects are removed using an
explicit categorical dummy matrix and pivoted-QR orthogonal projection, rather
than the alternating demeaning in the original fitting scripts.

An explicitly requested 2026-11-21 support sensitivity additionally excludes the
14 main-panel rows in three single-site regions whose covariates are absorbed
by the fixed effects. The four otherwise unchanged M_P/M_SP fits use 425 rows,
eight informative groups and t(7). This new covariance-support disclosure is
separately labeled; it is not represented as an original frozen 11-group result.

The source CR1 convention is reproduced exactly: G/(G-1)*(n-1)/(n-k), with k
the number of retained slope columns after fixed-effect absorption, followed by
t(G-1) intervals. This is a convention-specific reproduction, not a claim of
finite-sample coverage or an endorsement of every possible degrees-of-freedom
choice. The P0-P1 interval uses their joint covariance.

Example:
  python verify_frozen_polynya_results.py --inputs-dir source_artifacts \
    --temporal-csv matched_analysis.csv --out reproduction_receipt.json

Required ZIPs: isotope860.zip, polynya_physical.zip, polynya_main439.zip,
author_R1000.zip. The temporal CSV is the unmodified pinned repository file
polynya_temporal_20261120/matched_analysis.csv. No network is used.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy import linalg, stats


PINNED_COMMIT = "a1cf988df3501794e9add243a8c2be8ecbb7b43a"
SOURCE_HASHES = {
    "isotope860.zip": "dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205",
    "polynya_physical.zip": "702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96",
    "polynya_main439.zip": "e413eab31b101c4a9a11c6dc7656d58906527a2146e6ccef442bb677ede6b233",
    "author_R1000.zip": "be0234fef11a11b5b19129c8a84db0ab90dbe80b7cd6a71a3e733e36eaa1e342",
}
TEMPORAL_SHA256 = "7876e7ef687964a3e8c9d29c566b3627c8a210adfa094b65c22d72f8764375db"
TEMPORAL_GIT_BLOB_SHA1 = "875d374cc3b91df613908cfe6e20d67d3e076c3e"
ISO_MEMBER = "matched_860_original_isotope_ocean_ice_site_seasons.csv"
PHY_MEMBER = "source_original_860_site_seasons_true_DEEPAA100km_no_optical_Y.csv"
MAIN_RESULT = "DEEPAA100km_FROZEN_DIRECT_COASTAL_POLYNYA_OPTICAL_ISOTOPE_VERDICT.json"
AUTHOR_PREFIX = "old439_358_new_Y_method_sensitivity/"
AUTHOR_Y_MEMBER = AUTHOR_PREFIX + "original_860_same_source_old_single_vs_author_R1000_PLSR_optical_Y.csv"
AUTHOR_RESULT = AUTHOR_PREFIX + "AUTHOR_R1000_PLSR_ORIGINAL439_358_FIXED_MEASUREMENT_VERDICT.json"
KEYS = ["site_id", "season"]
REGION = "source_region"
Y_OLD = "predicted_d15N_season_day_equal"
Y_AUTHOR = "author_R1000_delta15N_season_day_equal"
POLYNYA = "direct_DEEPAA_coastal_polynya_fraction"
SALINITY = "GLORYS_NovFeb_salinity"
BASE = ["mean_doy_centered", "mean_doy_sq", "GLORYS_NovFeb_thetao_C",
        "author_SIC_150km_NovFeb_center_approx_fraction"]
MODEL_FEATURES = {"M0": BASE, "M_S": BASE + [SALINITY],
                  "M_P": BASE + [POLYNYA], "M_SP": BASE + [SALINITY, POLYNYA]}
TEMPORAL_FEATURES = BASE + [SALINITY, "P0", "P1"]
COEFFICIENT_ABS_TOLERANCE = 1e-8
SSE_ABS_TOLERANCE = 1e-6
INFORMATION_SS_THRESHOLD = 1e-16


def require(condition, message):
    if not bool(condition):
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def compare(label, actual, expected, checks, atol=COEFFICIENT_ABS_TOLERANCE):
    a = np.asarray(actual, dtype=float)
    e = np.asarray(expected, dtype=float)
    require(a.shape == e.shape, f"{label}: reference shape changed")
    error = float(np.max(np.abs(a-e)))
    require(np.isfinite(a).all() and error <= atol,
            f"{label}: abs error {error:.12g} exceeds {atol:.12g}")
    checks.append({"check": label, "max_abs_difference": error,
                   "absolute_tolerance": atol, "passed": True})


def read_sources(inputs, temporal_path):
    raw_members, receipts = {}, {}
    wanted = {
        "isotope860.zip": [ISO_MEMBER],
        "polynya_physical.zip": [PHY_MEMBER, "DEEPAA_ACTUAL_860_SOURCE_GEO_TIME_GATE.json"],
        "polynya_main439.zip": [MAIN_RESULT],
        "author_R1000.zip": [AUTHOR_Y_MEMBER, AUTHOR_RESULT],
    }
    for filename, expected_hash in SOURCE_HASHES.items():
        path = inputs / filename
        raw = path.read_bytes()
        require(digest(raw) == expected_hash, f"SHA256 mismatch: {filename}")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            require(archive.testzip() is None, f"ZIP CRC failure: {filename}")
            members = {}
            for member in wanted[filename]:
                value = archive.read(member)
                raw_members[member] = value
                members[member] = {"sha256": digest(value), "bytes": len(value)}
        receipts[filename] = {"sha256": expected_hash, "bytes": len(raw),
                              "zip_crc": "PASS", "used_members": members}
    raw = temporal_path.read_bytes()
    require(digest(raw) == TEMPORAL_SHA256, "Frozen temporal CSV SHA256 mismatch")
    blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    require(blob == TEMPORAL_GIT_BLOB_SHA1, "Frozen temporal CSV Git blob mismatch")
    receipts["matched_analysis.csv"] = {
        "sha256": digest(raw), "git_blob_sha1": blob, "bytes": len(raw),
        "pinned_commit": PINNED_COMMIT,
        "repository_path": "research/climate-penguin/macro_panantarctic_v1/polynya_temporal_20261120/matched_analysis.csv",
    }
    def csv(member):
        return pd.read_csv(io.BytesIO(raw_members[member]), dtype={"site_id": str})
    return (csv(ISO_MEMBER), csv(PHY_MEMBER), csv(AUTHOR_Y_MEMBER),
            pd.read_csv(io.BytesIO(raw), dtype={"site_id": str}),
            json.loads(raw_members[MAIN_RESULT]),
            json.loads(raw_members[AUTHOR_RESULT]),
            json.loads(raw_members["DEEPAA_ACTUAL_860_SOURCE_GEO_TIME_GATE.json"]),
            receipts)


def canonical_hash(data, columns):
    """Hash the ordered actual design/outcome values, separately from raw files."""
    raw = data.sort_values(KEYS)[columns].to_csv(
        index=False, lineterminator="\n", float_format="%.17g").encode()
    return digest(raw)


class FixedEffectProjection:
    """Orthogonal projection onto the complement of explicit dummy columns."""

    def __init__(self, data):
        site = pd.get_dummies(data.site_id.astype(str), dtype=float).to_numpy()
        labels = data[REGION].astype(str) + "__" + data.season.astype(str)
        region_season = pd.get_dummies(labels, dtype=float).to_numpy()
        self.dummies = np.column_stack([site, region_season])
        q, r, _ = linalg.qr(self.dummies, mode="economic", pivoting=True)
        diagonal = np.abs(np.diag(r))
        tolerance = np.finfo(float).eps * max(self.dummies.shape) * diagonal.max()
        self.rank = int(np.sum(diagonal > tolerance))
        self.q = q[:, :self.rank]
        self.maximum_dummy_crossproduct = 0.0

    def remove(self, values):
        a = np.asarray(values, dtype=float)
        require(np.isfinite(a).all(), "Non-finite source model input")
        result = a - self.q @ (self.q.T @ a)
        error = float(np.max(np.abs(self.dummies.T @ result)))
        self.maximum_dummy_crossproduct = max(self.maximum_dummy_crossproduct, error)
        require(error < 1e-7, f"Explicit FE projection orthogonality failed: {error}")
        return result


def fit_frozen(data, features, response, projection):
    x = projection.remove(data[features].to_numpy(float))
    y = projection.remove(data[response].to_numpy(float))
    n, k = x.shape
    require(np.linalg.matrix_rank(x) == k, "Frozen slope design is rank deficient")
    inverse = np.linalg.pinv(x)
    beta = inverse @ y
    residual = y - x @ beta
    groups = sorted(data[REGION].unique())
    g = len(groups)
    # Block influence vectors directly produce the cluster sandwich without
    # importing statsmodels or forming the less stable inverse of X'X.
    influence = np.vstack([
        inverse[:, data[REGION].eq(group).to_numpy()] @
        residual[data[REGION].eq(group).to_numpy()] for group in groups
    ])
    correction = g / (g-1) * (n-1) / (n-k)
    covariance = correction * (influence.T @ influence)
    require(np.isfinite(covariance).all(), "Invalid cluster covariance")
    critical = float(stats.t.ppf(.975, g-1))
    result = {"n": n, "sites": int(data.site_id.nunique()), "reporting_regions": g,
              "seasons": sorted(map(int, data.season.unique())),
              "fixed_effect_design_rank": projection.rank,
              "retained_slopes_k": k, "cr1_correction": float(correction),
              "interval_t_df": g-1, "sse": float(residual @ residual),
              "response": response, "features": list(features)}

    def contrast(vector):
        v = np.asarray(vector, dtype=float)
        estimate = float(v @ beta)
        se = float(np.sqrt(v @ covariance @ v))
        return {"estimate": estimate, "se": se,
                "ci95": [estimate-critical*se, estimate+critical*se]}

    result["coefficients_native_units"] = {
        name: contrast(np.eye(k)[index]) for index, name in enumerate(features)
    }
    if POLYNYA in features:
        result["polynya_per_10pp"] = contrast(np.eye(k)[features.index(POLYNYA)] * .1)
    if "P0" in features and "P1" in features:
        p0 = np.eye(k)[features.index("P0")] * .1
        p1 = np.eye(k)[features.index("P1")] * .1
        result["P0_per_10pp"] = contrast(p0)
        result["P1_per_10pp"] = contrast(p1)
        result["P0_minus_P1_per_10pp"] = contrast(p0-p1)
        result["P0_P1_covariance_per_10pp_squared"] = float(p0 @ covariance @ p1)
        result["contrast_uses_joint_covariance"] = True
    return result


def information_support(data, exposures, projection):
    residual = projection.remove(data[exposures].to_numpy(float))
    rows = []
    for region in sorted(data[REGION].unique()):
        mask = data[REGION].eq(region).to_numpy()
        ss = np.sum(residual[mask]**2, axis=0)
        rows.append({"region": region, "rows": int(mask.sum()),
                     "sites": int(data.loc[mask, "site_id"].nunique()),
                     "exposure_residual_ss": dict(zip(exposures, map(float, ss))),
                     "informative_for_all_listed_exposures": bool(np.all(ss > INFORMATION_SS_THRESHOLD))})
    informative = [x["region"] for x in rows if x["informative_for_all_listed_exposures"]]
    return {"criterion": "Each listed exposure has sum of squared site + region-season FE residuals > 1e-16",
            "threshold": INFORMATION_SS_THRESHOLD, "reporting_regions": len(rows),
            "informative_regions": informative, "informative_region_count": len(informative),
            "zero_information_regions": [x["region"] for x in rows if not x["informative_for_all_listed_exposures"]],
            "informative_rows": int(data[REGION].isin(informative).sum()), "by_region": rows}


def values(coefficient):
    return [coefficient["estimate"], *coefficient["ci95"]]


def main(args):
    (iso, physical, author_y, temporal, original_main, original_author,
     physical_gate, source_receipts) = read_sources(args.inputs_dir, args.temporal_csv)
    checks = []
    for name, frame in [("isotope", iso), ("physical", physical), ("author Y", author_y)]:
        require((len(frame), frame.site_id.nunique(), frame[REGION].nunique()) == (860, 88, 13),
                f"{name}: source 860/88/13 denominator drift")
        require(not frame.duplicated(KEYS).any(), f"{name}: duplicate site-season")
    require(physical_gate["status"] == "PASS_DIRECT_POLYNYA_MACRO_SUPPORT_SOURCE_ONLY_NO_Y_FIT",
            "Existing physical source gate did not pass")
    require(all(physical_gate["frozen_gate_checks"].values()), "Existing physical gates incomplete")
    author_comparison = iso[KEYS + [REGION, "n_source_pixels", "n_observed_days", Y_OLD]].merge(
        author_y, on=KEYS, suffixes=("_iso", "_author"), validate="one_to_one")
    require(len(author_comparison) == 860, "Author Y comparison lost source keys")
    for column in [REGION, "n_source_pixels", "n_observed_days"]:
        require(author_comparison[column+"_iso"].eq(author_comparison[column+"_author"]).all(),
                f"Author reconstruction changed observed support: {column}")
    compare("Original Y identical before author mean replacement",
            author_comparison[Y_OLD+"_iso"], author_comparison[Y_OLD+"_author"], checks, 1e-12)
    iso = iso.merge(author_y[KEYS + [Y_AUTHOR]], on=KEYS, validate="one_to_one")
    joined = iso.merge(physical[KEYS + [REGION, POLYNYA]], on=KEYS,
                       suffixes=("", "_physical"), validate="one_to_one")
    require(len(joined) == 860 and joined[REGION].eq(joined[REGION+"_physical"]).all(),
            "Physical and optical source geography mismatch")
    main_data = joined.loc[joined[POLYNYA].notna()].copy().reset_index(drop=True)
    require((len(main_data), main_data.site_id.nunique(), main_data[REGION].nunique()) == (439, 85, 11),
            "Frozen main 439/85/11 denominator drift")
    require(sorted(main_data.season.unique()) == list(range(2004, 2011)), "Main dates changed")
    require(not temporal.duplicated(KEYS).any(), "Temporal duplicate site-season")
    require((len(temporal), temporal.site_id.nunique(), temporal[REGION].nunique()) == (358, 85, 11),
            "Frozen temporal 358/85/11 denominator drift")
    require(sorted(temporal.season.unique()) == list(range(2004, 2010)), "Temporal dates changed")
    shared = temporal.merge(main_data[KEYS + BASE + [SALINITY, Y_OLD, POLYNYA]],
                            on=KEYS, suffixes=("", "_439"), validate="one_to_one")
    require(len(shared) == 358, "Temporal sample is not nested within original 439")
    for column in BASE + [SALINITY, Y_OLD]:
        compare("358 preserves original439 " + column,
                shared[column], shared[column+"_439"], checks, 1e-12)
    compare("358 P0 preserves original physical exposure", shared.P0, shared[POLYNYA], checks, 1e-12)
    temporal = temporal.merge(author_y[KEYS + [Y_AUTHOR]], on=KEYS, validate="one_to_one")

    project439 = FixedEffectProjection(main_data)
    project358 = FixedEffectProjection(temporal)
    old_main = {name: fit_frozen(main_data, features, Y_OLD, project439)
                for name, features in MODEL_FEATURES.items()}
    for name, fit in old_main.items():
        reference = original_main["models"][name]["region"]
        compare(name+" original439 SSE", fit["sse"], reference["sse"], checks, SSE_ABS_TOLERANCE)
        for source_coefficient in reference["coefficients"]:
            coefficient = fit["coefficients_native_units"][source_coefficient["feature"]]
            compare(name+" original439 "+source_coefficient["feature"],
                    [coefficient["estimate"], coefficient["se"], *coefficient["ci95"]],
                    [source_coefficient["native_beta"], source_coefficient["se"], *source_coefficient["t95ci"]],
                    checks)
    partial = {name: 1-fit["sse"]/old_main["M0"]["sse"] for name, fit in old_main.items()}
    partial["M_SP_vs_M_S"] = 1-old_main["M_SP"]["sse"]/old_main["M_S"]["sse"]
    for name in MODEL_FEATURES:
        compare(name+" residual SSE reduction", partial[name],
                original_main["models"][name]["additional_M0_residual_fraction"], checks)
    compare("M_SP incremental reduction vs M_S", partial["M_SP_vs_M_S"],
            original_main["M_SP_incremental_residual_fraction_vs_M_S"], checks)
    ps = project439.remove(main_data[[POLYNYA, SALINITY]].to_numpy(float))
    ps_correlation = float(np.corrcoef(ps.T)[0, 1])
    compare("FE-only P-S correlation, rounded source report", ps_correlation, -.08043, checks, 5e-6)
    info439 = information_support(main_data, [POLYNYA], project439)
    info358 = information_support(temporal, ["P0", "P1"], project358)
    require(info358["informative_region_count"] == 8 and info358["informative_rows"] == 347,
            "Previously fixed informative temporal support changed")
    reduced = temporal.loc[temporal[REGION].isin(info358["informative_regions"])].copy().reset_index(drop=True)
    project347 = FixedEffectProjection(reduced)
    old_time = fit_frozen(temporal, TEMPORAL_FEATURES, Y_OLD, project358)
    old_info = fit_frozen(reduced, TEMPORAL_FEATURES, Y_OLD, project347)
    new_main = {name: fit_frozen(main_data, MODEL_FEATURES[name], Y_AUTHOR, project439)
                for name in ["M_P", "M_SP"]}
    new_time = fit_frozen(temporal, TEMPORAL_FEATURES, Y_AUTHOR, project358)
    new_info = fit_frozen(reduced, TEMPORAL_FEATURES, Y_AUTHOR, project347)
    # Requested one-time support audit, not a search for a preferred result:
    # the subset is determined only by the existing FE design and exposure.
    main_reduced = main_data.loc[main_data[REGION].isin(info439["informative_regions"])].copy().reset_index(drop=True)
    require((len(main_reduced), main_reduced[REGION].nunique()) == (425, 8),
            "Main-panel informative support is not the disclosed 425 rows / 8 groups")
    project425 = FixedEffectProjection(main_reduced)
    main425_original = {name: fit_frozen(main_reduced, MODEL_FEATURES[name], Y_OLD, project425)
                        for name in ["M_P", "M_SP"]}
    main425_author = {name: fit_frozen(main_reduced, MODEL_FEATURES[name], Y_AUTHOR, project425)
                      for name in ["M_P", "M_SP"]}
    for response_label, reduced_models, full_models in [
        ("original single PLSR", main425_original, old_main),
        ("author R1000 mean", main425_author, new_main),
    ]:
        for name, subset_fit in reduced_models.items():
            full_fit = full_models[name]
            compare("New support sensitivity preserves SSE: "+response_label+" "+name,
                    subset_fit["sse"], full_fit["sse"], checks, SSE_ABS_TOLERANCE)
            compare("New support sensitivity preserves all slopes: "+response_label+" "+name,
                    [subset_fit["coefficients_native_units"][feature]["estimate"] for feature in MODEL_FEATURES[name]],
                    [full_fit["coefficients_native_units"][feature]["estimate"] for feature in MODEL_FEATURES[name]], checks)
    comparisons = [
        ("439 M_P", old_main["M_P"]["polynya_per_10pp"], new_main["M_P"]["polynya_per_10pp"], "original439_M_P"),
        ("439 M_SP", old_main["M_SP"]["polynya_per_10pp"], new_main["M_SP"]["polynya_per_10pp"], "original439_M_SP"),
        ("358 joint P0", old_time["P0_per_10pp"], new_time["P0_per_10pp"], "original358_P0_joint"),
        ("358 joint P1", old_time["P1_per_10pp"], new_time["P1_per_10pp"], "original358_P1_joint"),
        ("358 covariance-correct difference", old_time["P0_minus_P1_per_10pp"], new_time["P0_minus_P1_per_10pp"], "original358_P0_minus_P1"),
        ("347 informative8 difference", old_info["P0_minus_P1_per_10pp"], new_info["P0_minus_P1_per_10pp"], "original358_informative_8region_P0_minus_P1"),
    ]
    for name, old, new, key in comparisons:
        reference = original_author[key]
        compare(name+" old Y", values(old),
                [reference["old_single_PLSR_beta_per_10pp"], *reference["old_region_cluster_t95"]], checks)
        compare(name+" author R1000 mean Y", values(new),
                [reference["author_R1000_PLSR_beta_per_10pp"], *reference["author_region_cluster_t95"]], checks)

    receipt = {
        "status": "PASS_INDEPENDENT_REPRODUCTION_OF_EXISTING_FROZEN_POLYNYA_RESULTS",
        "source_commit": PINNED_COMMIT,
        "verifier_source_sha256": digest(Path(__file__).read_bytes()),
        "verification_scope": "Independent reproduction of existing fixed models, plus separately disclosed requested 2026-11-21 main425 informative-group covariance sensitivity; no model search or new ecological hypothesis",
        "independent_numerical_method": {
            "fixed_effects": "Explicit site and region-by-season dummy matrix; pivoted QR orthogonal projection",
            "regression": "NumPy pseudoinverse OLS on projected columns",
            "covariance": "Sum of source-region block influence outer products times CR1",
            "source_cr1": "G/(G-1)*(n-1)/(n-k); k counts retained slope columns, not absorbed FE rank",
            "intervals": "Student t(G-1); P0-P1 uses the full joint covariance",
            "does_not_import_original_fit_implementation": True,
            "does_not_refit_laboratory_PLSR": True,
            "main439_zero_information_subset_refitted": True,
        },
        "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                    "pandas": pd.__version__, "scipy": scipy.__version__},
        "source_files": source_receipts,
        "observed_design_hashes_sha256": {
            "main439": canonical_hash(main_data, KEYS+[REGION]+BASE+[SALINITY, POLYNYA, Y_OLD, Y_AUTHOR]),
            "temporal358": canonical_hash(temporal, KEYS+[REGION]+TEMPORAL_FEATURES+[Y_OLD, Y_AUTHOR]),
        },
        "main439_original_single_plsr": old_main,
        "main439_residual_sse_reductions_fraction": partial,
        "main439_P_S_correlation_after_site_and_region_season_FE_only": ps_correlation,
        "main439_observation_support": info439,
        "new_20261121_main425_informative8_support_sensitivity": {
            "status": "PASS_COEFFICIENTS_AND_SSE_UNCHANGED_NEW_COVARIANCE_SUPPORT_DISCLOSURE",
            "performed_utc_date": "2026-11-21",
            "is_original_frozen_11_region_result": False,
            "explicitly_requested_followup": True,
            "new_ecological_hypothesis_or_model_search": False,
            "subset_rule": info439["criterion"],
            "excluded_regions": info439["zero_information_regions"],
            "excluded_rows": len(main_data)-len(main_reduced),
            "n": len(main_reduced), "sites": int(main_reduced.site_id.nunique()),
            "informative_regions": int(main_reduced[REGION].nunique()),
            "interval_t_df": 7,
            "source_cr1_convention_unchanged": True,
            "observed_design_sha256": canonical_hash(main_reduced, KEYS+[REGION]+BASE+[SALINITY, POLYNYA, Y_OLD, Y_AUTHOR]),
            "original_single_PLSR": main425_original,
            "author_R1000_mean_Y": main425_author,
            "interpretation": "Dropping FE-absorbed single-site regions leaves coefficients and SSE unchanged, while the source CR1 correction and t reference use eight contributing groups. This is a post-result support sensitivity, not independent replication or proof of causal identification.",
        },
        "temporal358_original_single_plsr_joint": old_time,
        "temporal358_observation_support": info358,
        "temporal347_informative8_original_single_plsr_joint": old_info,
        "author_R1000_mean_Y_same439_sensitivity": new_main,
        "author_R1000_mean_Y_same358_joint": new_time,
        "author_R1000_mean_Y_informative8_joint": new_info,
        "explicit_projection_max_abs_dummy_crossproduct": {
            "main439": project439.maximum_dummy_crossproduct,
            "temporal358": project358.maximum_dummy_crossproduct,
            "informative347": project347.maximum_dummy_crossproduct,
            "main425_new_support_sensitivity": project425.maximum_dummy_crossproduct,
        },
        "checks": checks,
        "limitations": [
            "Reproduction uses the original already-selected historical optical pixels and frozen derived physical exposure; native satellite extraction is not repeated.",
            "The mean outcome of the original-author 1000 calibration fits is reused; laboratory calibrations and their distribution are not refitted or independently validated here.",
            "The nominal region-cluster intervals follow the original source convention and do not adjust for the prior exploratory search or guarantee small-cluster coverage.",
            "Numerical agreement is not an independent biological replication, causal confirmation, new-era validation, direct diet measurement, or population forecast.",
            "The temporal informative8 sensitivity was already frozen. The main425 informative8 covariance sensitivity is newly requested on 2026-11-21 and explicitly separated from original frozen 11-region intervals.",
        ],
        "new_causal_confirmation": False,
        "new_model_or_outcome_selection": False,
        "new_post2013_ecological_replication": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"], "checks_passed": len(checks),
        "original439_M_P": old_main["M_P"]["polynya_per_10pp"],
        "original439_M_SP": old_main["M_SP"]["polynya_per_10pp"],
        "original358_difference": old_time["P0_minus_P1_per_10pp"],
        "informative8_difference": old_info["P0_minus_P1_per_10pp"],
        "main439_informative_regions": info439["informative_region_count"],
        "main439_informative_rows": info439["informative_rows"],
        "main439_FE_only_P_S_correlation": ps_correlation,
        "main439_partial_reductions": partial,
        "author439_M_P": new_main["M_P"]["polynya_per_10pp"],
        "author439_M_SP": new_main["M_SP"]["polynya_per_10pp"],
        "author358_difference": new_time["P0_minus_P1_per_10pp"],
        "new_main425_original_M_P": main425_original["M_P"]["polynya_per_10pp"],
        "new_main425_original_M_SP": main425_original["M_SP"]["polynya_per_10pp"],
        "new_main425_author_M_P": main425_author["M_P"]["polynya_per_10pp"],
        "new_main425_author_M_SP": main425_author["M_SP"]["polynya_per_10pp"],
        "receipt": str(args.out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs-dir", required=True, type=Path)
    parser.add_argument("--temporal-csv", type=Path,
                        help="Pinned matched_analysis.csv; defaults to inputs-dir/matched_analysis.csv")
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).with_name("reproduction_receipt.json"))
    options = parser.parse_args()
    if options.temporal_csv is None:
        options.temporal_csv = options.inputs_dir / "matched_analysis.csv"
    main(options)
