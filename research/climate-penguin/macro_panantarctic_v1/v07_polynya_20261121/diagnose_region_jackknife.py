#!/usr/bin/env python3
"""Bounded uncertainty audit of the unchanged polynya 439/358 models.

Only the eight previously identified informative source regions are used.
No outcome, radius, lag, covariate, or subset is searched. All leave-region-out
fits rebuild colony and region-by-season fixed effects by explicit QR.

The declared fallback to unavailable R/clubSandwich is CV3 delete-one-cluster
jackknife covariance centred at the full-sample estimate:
    (G-1)/G * sum_g (beta_minus_g - beta)(beta_minus_g - beta)'.
Intervals use t(G-1), not a Satterthwaite approximation. This does not solve
exploratory selection or guarantee correct finite-cluster coverage.

 Run with the same numpy/pandas/scipy environment as the frozen verifier:
 python diagnose_region_jackknife.py --root PATH --out OUTPUT.json
 If installed beside the manuscript, --root may be omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(args):
    root = args.manuscript_dir.resolve()
    verifier = root / "verify_frozen_polynya_results.py"
    spec = importlib.util.spec_from_file_location("frozen_verifier", verifier)
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    iso, physical, author_y, temporal, *_ = v.read_sources(
        root / "frozen_archives", root / "verification_inputs/matched_temporal358.csv"
    )
    main_data = iso.merge(physical[v.KEYS + [v.POLYNYA]], on=v.KEYS,
                          validate="one_to_one")
    main_data = main_data.loc[main_data[v.POLYNYA].notna()].reset_index(drop=True)
    main_data = main_data.merge(author_y[v.KEYS + [v.Y_AUTHOR]], on=v.KEYS,
                                validate="one_to_one")
    temporal = temporal.merge(author_y[v.KEYS + [v.Y_AUTHOR]], on=v.KEYS,
                              validate="one_to_one")
    reference = json.loads((root / "reproduction_receipt.json").read_text())
    informative = reference["main439_observation_support"]["informative_regions"]
    assert informative == reference["temporal358_observation_support"]["informative_regions"]
    assert len(informative) == 8
    existing_loo = pd.read_csv(root / "source_inputs/main439_leave_region_out.csv")
    checks = []

    def close(label, actual, expected, tolerance=1e-8):
        err = float(np.max(np.abs(np.asarray(actual)-np.asarray(expected))))
        assert err <= tolerance, (label, err)
        checks.append({"label": label, "max_abs_difference": err,
                       "tolerance": tolerance, "passed": True})

    def fit(data, features, response):
        projection = v.FixedEffectProjection(data)
        x = projection.remove(data[features].to_numpy(float))
        y = projection.remove(data[response].to_numpy(float))
        assert np.linalg.matrix_rank(x) == len(features)
        inverse = np.linalg.pinv(x)
        beta = inverse @ y
        return beta, inverse, projection.rank

    models = {}
    for response, response_label in [(v.Y_OLD, "original"),
                                      (v.Y_AUTHOR, "author_R1000_mean")]:
        for name, full, features, contrast in [
            ("M_P", main_data, v.MODEL_FEATURES["M_P"], [0,0,0,0,.1]),
            ("M_SP", main_data, v.MODEL_FEATURES["M_SP"], [0,0,0,0,0,.1]),
            ("P0_minus_P1", temporal, v.TEMPORAL_FEATURES, [0,0,0,0,0,.1,-.1]),
        ]:
            key = f"{response_label}_{name}"
            data = full.loc[full[v.REGION].isin(informative)].reset_index(drop=True)
            beta, inverse, rank = fit(data, features, response)
            c = np.asarray(contrast)
            estimate = float(c @ beta)
            beta_full, _, _ = fit(full, features, response)
            close(key + " informative support leaves all slopes unchanged", beta, beta_full)
            if name in ("M_P", "M_SP"):
                ref_key = "original_single_PLSR" if response == v.Y_OLD else "author_R1000_mean_Y"
                ref = reference["new_20261121_main425_informative8_support_sensitivity"][ref_key][name]["polynya_per_10pp"]
            else:
                ref_key = "temporal347_informative8_original_single_plsr_joint" if response == v.Y_OLD else "author_R1000_mean_Y_informative8_joint"
                ref = reference[ref_key]["P0_minus_P1_per_10pp"]
            close(key + " frozen coefficient", estimate, ref["estimate"])
            leaveout = []
            coefficients = []
            for omitted in informative:
                sample = data.loc[data[v.REGION].ne(omitted)].reset_index(drop=True)
                b_minus, _, r_minus = fit(sample, features, response)
                coefficients.append(b_minus)
                loo_estimate = float(c @ b_minus)
                if response == v.Y_OLD and name in ("M_P", "M_SP"):
                    archived = existing_loo.loc[(existing_loo.model == name) &
                                (existing_loo.omitted_original_region == omitted), "polynya_beta"]
                    assert len(archived) == 1
                    close(key + " archived omission " + omitted, loo_estimate, float(archived.iloc[0])*.1)
                leaveout.append({"omitted_region": omitted, "n":len(sample),
                                  "sites":int(sample.site_id.nunique()),
                                  "fixed_effect_rank":r_minus,
                                  "contrast_per_10pp":loo_estimate,
                                  "coefficients_native_units":dict(zip(features, map(float,b_minus)))})
            delta = np.vstack(coefficients) - beta
            g = len(informative)
            covariance = (g-1)/g * (delta.T @ delta)
            se = float(np.sqrt(c @ covariance @ c))
            critical = float(stats.t.ppf(.975, g-1))
            # Independently calculate the scalar contrast jackknife identity.
            scalar_se = float(np.sqrt((g-1)/g * sum((z["contrast_per_10pp"]-estimate)**2 for z in leaveout)))
            close(key + " covariance agrees with scalar contrast", se, scalar_se, 1e-12)
            weights = c @ inverse
            shares = [float(np.sum(weights[data[v.REGION].eq(region)]**2)) for region in informative]
            shares = np.asarray(shares) / sum(shares)
            models[key] = {
                "response":response, "original_n":len(full), "informative_n":len(data),
                "informative_sites":int(data.site_id.nunique()), "clusters":g,
                "fixed_effect_rank":rank, "features":features, "contrast":contrast,
                "estimate_per_10pp":estimate,
                "archived_informative8_cr1":ref,
                "CV3_delete_one_region_t7":{
                    "se":se, "df":g-1, "ci95":[estimate-critical*se,estimate+critical*se],
                    "p_two_sided":float(2*stats.t.sf(abs(estimate/se),g-1)),
                    "covariance_native_units":covariance.tolist(),
                    "centre":"full-sample coefficient vector; not mean of leave-out estimates",
                },
                "coefficients_native_units_CV3":{
                    feature:{"estimate":float(beta[j]),
                             "se":float(np.sqrt(covariance[j,j])),
                             "ci95":[float(beta[j]-critical*np.sqrt(covariance[j,j])),
                                     float(beta[j]+critical*np.sqrt(covariance[j,j]))]}
                    for j,feature in enumerate(features)
                },
                "focal_coefficients_per_10pp_CV3":{
                    feature:{"estimate":float(.1*beta[j]),
                             "se":float(.1*np.sqrt(covariance[j,j])),
                             "ci95":[float(.1*(beta[j]-critical*np.sqrt(covariance[j,j]))),
                                     float(.1*(beta[j]+critical*np.sqrt(covariance[j,j])))]}
                    for j,feature in enumerate(features)
                    if feature in [v.POLYNYA, "P0", "P1"]
                },
                "all_omission_contrasts_negative":all(z["contrast_per_10pp"] < 0 for z in leaveout),
                "leave_one_informative_region_out":leaveout,
                "design_only_cluster_information_shares":dict(zip(informative, map(float,shares))),
                "design_only_inverse_herfindahl":float(1 / sum(shares**2)),
                "concentration_index_is_not_inferential_degrees_of_freedom":True,
            }
    out = {
        "status":"PASS_BOUNDED_FROZEN_DESIGN_REGION_JACKKNIFE_SENSITIVITY",
        "audit_date":"2026-11-21",
        "method":"CV3 delete-one-informative-region covariance, centred at full estimate, t(7)",
        "method_selected_before_observing_new_intervals":True,
        "preferred_method_not_run":"R/Rscript and clubSandwich are absent; no CR2 or Satterthwaite result is claimed.",
        "fixed_effects":"Site and region-by-season dummies reconstructed and QR-absorbed in every full and leave-out fit.",
        "original_or_new":"New uncertainty audit on frozen data and model definitions; not a new hypothesis or independent data replication.",
        "source_reference":"MacKinnon JG, Nielsen MO, Webb MD (2023). Fast and reliable jackknife and bootstrap methods for cluster-robust inference. Journal of Applied Econometrics 38:671-694, DOI 10.1002/jae.2969, Eq. 18; t(G-1) and cluster fixed effects discussed in Section 3.",
        "script_sha256":sha256(Path(__file__)),
        "frozen_verifier_sha256":sha256(verifier),
        "frozen_receipt_sha256":sha256(root / "reproduction_receipt.json"),
        "runtime":{"python":platform.python_version(),"numpy":np.__version__,"pandas":pd.__version__},
        "informative_regions":informative,
        "models":models,"checks":checks,
        "limitations":[
            "CV3+t(7) is a sensitivity, not guaranteed exact coverage with eight heterogeneous clusters.",
            "No correction for exploratory selection, model-history multiplicity, calibration bias, or inter-region error correlation is supplied.",
            "The design-only concentration index describes information imbalance and is not the df used in the t interval.",
            "Calibration ensemble sensitivity reuses the same pixels and laboratory set.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":out["status"], "checks_passed":len(checks),
        "results":{k:{"estimate":r["estimate_per_10pp"],"CV3":{i:j for i,j in r["CV3_delete_one_region_t7"].items() if i != "covariance_native_units"},"information_concentration":r["design_only_inverse_herfindahl"]} for k,r in models.items()}},indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", "--manuscript-dir", dest="manuscript_dir",type=Path,
                        default=Path(__file__).resolve().parent)
    parser.add_argument("--out",type=Path,required=True)
    main(parser.parse_args())
