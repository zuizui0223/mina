"""Independent source-to-result validation of Signy diet components.

Primary analysis helpers and generated numeric outputs are never imported.
CSV ingestion uses row loops; OLS/HC3 uses statsmodels; exact permutations
use SciPy with one common exposure permutation for all response columns.
"""

from __future__ import annotations

import argparse
import calendar
import csv
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy import stats
import statsmodels
import statsmodels.api as sm

import palmer_reference


YEARS = tuple(range(2001, 2010))
OUTPUT_PATH = Path("research/climate-penguin/outputs/signy_diet_components_v1")
EXPECTED_HASHES = {
    "Adelie_diet_summary.csv": "ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
    "Gentoo_diet_summary.csv": "6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902",
    "macro_monthly_seaice_1991_2020.csv": "b21b10743f3a56281d0cf62f55988823f55b645b6d3fbb1bf7c2d366dff1b3ae",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def average(values):
    values = list(values)
    return math.fsum(values) / len(values)


def numeric(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def portable_path(path, repo_root):
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def pinned_source(path, repo_root):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = EXPECTED_HASHES[path.name]
    if actual != expected:
        raise ValueError(f"source hash mismatch: {path.name}")
    return {"file": portable_path(path, repo_root), "sha256": actual}


def source_components(source_directory):
    annual = []
    audits = []
    for species in ("Adelie", "Gentoo"):
        seen = set()
        valid_by_year = {year: [] for year in YEARS}
        n_source = 0
        excluded = []
        for row in read_csv(source_directory / f"{species}_diet_summary.csv"):
            key = row["DATE"], row["RECORD_ID"]
            if key in seen:
                raise ValueError(f"duplicate stomach source key: {key}")
            seen.add(key)
            sampled = date.fromisoformat(row["DATE"])
            if sampled.month not in (1, 2, 3, 4, 11, 12):
                raise ValueError(f"unexpected sampling month: {key}")
            year = sampled.year - int(sampled.month <= 4)
            if year not in valid_by_year:
                continue
            n_source += 1
            fish = numeric(row["FISH_MASS_g"])
            crust = numeric(row["CRUSTACEAN_MASS_g"])
            ceph = numeric(row["CEPHALOPOD_MASS_g"])
            other = numeric(row["OTHER_FOOD_MASS_g"])
            total = numeric(row["TOTAL_MASS_g"])
            krill = numeric(row["EUPHAUSIA_SUPERBA_MASS_g"])
            food = fish + crust + ceph + other
            checks = {
                "finite_food_components_and_total": all(map(math.isfinite, (fish, crust, ceph, other, total))),
                "fish_nonnegative": fish >= 0,
                "crustacean_nonnegative": crust >= 0,
                "cephalopod_nonnegative": ceph >= 0,
                "other_food_nonnegative": other >= 0,
                "total_positive": total > 0,
                "fish_plus_crustacean_positive": fish + crust > 0,
                "fish_plus_crustacean_not_excessive": fish + crust <= 1.05 * total + 0.05,
                "krill_within_crustacean": math.isnan(krill) or krill <= 1.05 * crust + 0.05,
                "food_positive": food > 0,
                "food_not_excessive": food <= 1.05 * total + 0.05,
            }
            if not all(checks.values()):
                excluded.append({"DATE": key[0], "RECORD_ID": key[1],
                                 "failed_checks": [k for k, v in checks.items() if not v]})
                continue
            valid_by_year[year].append({"fish": fish, "crust": crust,
                                        "food": food, "q": fish / food})
        for year, samples in valid_by_year.items():
            if not samples:
                raise ValueError(f"no valid stomachs: {species} {year}")
            positives = [row for row in samples if row["fish"] > 0]
            p = len(positives) / len(samples)
            c = average(row["q"] for row in positives) if positives else None
            m = average(row["q"] for row in samples)
            if c is not None and not math.isclose(p * c, m, rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError(f"m = p*c identity failed: {species} {year}")
            if not positives and m != 0:
                raise ValueError("zero-positive season has nonzero mean fish fraction")
            annual.append({
                "species": species, "year": year, "n_stomachs": len(samples),
                "n_positive_fish_mass": len(positives), "positive_mass_frequency": p,
                "conditional_fish_fraction": c, "mean_fish_fraction": m,
                "mean_fish_mass_g": average(row["fish"] for row in samples),
                "mean_crustacean_mass_g": average(row["crust"] for row in samples),
                "mean_food_mass_g": average(row["food"] for row in samples),
            })
        audits.append({"species": species, "n_source": n_source,
                       "n_valid": sum(len(v) for v in valid_by_year.values()),
                       "n_excluded": len(excluded), "excluded_keys": excluded})
    return annual, audits


def annual_exposure(source):
    months = {year: {} for year in YEARS}
    for row in read_csv(source):
        year, month = int(row["year"]), int(row["month"])
        if row["site_id"] != "GOPT" or year not in months or float(row["inner_km"]) != 0 or month not in (8, 9, 10, 11):
            continue
        if month in months[year]:
            raise ValueError(f"duplicate sea-ice key: {year} {month}")
        expected = calendar.monthrange(year, month)[1]
        if row["complete_month"].lower() != "true":
            raise ValueError(f"incomplete month: {year} {month}")
        if any(int(row[key]) != expected for key in ("days", "supported_days", "expected_days")):
            raise ValueError(f"monthly day support mismatch: {year} {month}")
        sic = numeric(row["sic_mean"])
        if not math.isfinite(sic) or not 0 <= sic <= 100:
            raise ValueError("invalid SIC")
        months[year][month] = sic
    result = {}
    for year, values in months.items():
        if set(values) != {8, 9, 10, 11}:
            raise ValueError(f"missing antecedent month: {year}")
        result[year] = average(values[month] for month in (8, 9, 10, 11))
    return result, {"n_selected_months": sum(len(v) for v in months.values()),
                    "all_months_complete": True, "all_days_match_calendar": True,
                    "unique_selected_keys": True, "months_equally_weighted": True}


def joint_permutations(x, response_columns):
    """Enumerate common x permutations using SciPy's independent implementation."""
    names = tuple(response_columns)
    xc = x - x.mean()
    centered = {key: np.asarray(response_columns[key]) - np.mean(response_columns[key]) for key in names}
    norms = {key: math.sqrt(float(xc @ xc) * float(yc @ yc)) for key, yc in centered.items()}
    if any(norm <= 0 for norm in norms.values()):
        raise ValueError("primary correlation is undefined for a constant series")

    def statistic(permuted_x, axis=-1):
        # SciPy places the permutation batch on axis 0 and concatenates there.
        # Keep response columns on the final axis for both scalar and batches.
        return np.stack([np.sum(permuted_x * centered[key], axis=axis) / norms[key]
                         for key in names], axis=-1)

    permutation = stats.permutation_test(
        (xc,), statistic, permutation_type="pairings", vectorized=True,
        n_resamples=np.inf, batch=4096, alternative="greater",
    )
    distribution = permutation.null_distribution
    expected = math.factorial(len(x))
    if distribution.shape != (expected, len(names)):
        raise ValueError(f"unexpected exact null shape: {distribution.shape}")
    observed = statistic(xc)
    primary_indices = [names.index("frequency"), names.index("composition")]
    null_maximum = np.max(np.abs(distribution[:, primary_indices]), axis=1)
    results = {}
    for i, key in enumerate(names):
        count = int(np.count_nonzero(np.abs(distribution[:, i]) >= abs(observed[i]) - 1e-12))
        result = {"status": "estimable", "r": float(observed[i]),
                  "extreme_count": count, "p_exact": count / expected}
        if key in ("frequency", "composition"):
            adjusted = int(np.count_nonzero(null_maximum >= abs(observed[i]) - 1e-12))
            result.update({"max2_extreme_count": adjusted, "p_max2": adjusted / expected})
        results[key] = result
    family = {"n_permutations": expected, "n_prespecified_components": 2,
              "n_variable_components": 2,
              "components": {key: results[key] for key in ("frequency", "composition")}}
    return family, results


def describe(x, y, years, exact_result):
    design = sm.add_constant(x / 10.0)
    fitted = sm.OLS(y, design).fit(cov_type="HC3", use_t=True)
    ci = fitted.conf_int(alpha=0.05)
    r = float(stats.pearsonr(x, y).statistic)
    loo = {str(year): float(stats.pearsonr(np.delete(x, i), np.delete(y, i)).statistic)
           for i, year in enumerate(years)}
    time = np.array(years, dtype=float)
    trend = sm.add_constant(time - time.mean())
    residual_x = sm.OLS(x, trend).fit().resid
    residual_y = sm.OLS(y, trend).fit().resid
    shifted = [float(stats.pearsonr(x, np.roll(y, i)).statistic) for i in range(len(y))]
    result = {
        "status": "estimable", "n_seasons": len(y), "years": years,
        "mean_value": average(y), "min_value": float(min(y)), "max_value": float(max(y)),
        "sic_min": float(min(x)), "sic_max": float(max(x)), "pearson_r": r,
        "slope_per_10pp": float(fitted.params[1]), "intercept": float(fitted.params[0]),
        "hc3_slope_95_low": float(ci[1, 0]), "hc3_slope_95_high": float(ci[1, 1]),
        "hc3_slope_se": float(fitted.bse[1]), "hc3_t_df": int(fitted.df_resid),
        "leave_one_season_r_min": min(loo.values()), "leave_one_season_r_max": max(loo.values()),
        "leave_one_season_r": loo,
        "detrended_r": float(stats.pearsonr(residual_x, residual_y).statistic),
        "first_difference_r": float(stats.pearsonr(np.diff(x), np.diff(y)).statistic),
        "circular_extreme_count": sum(abs(v) >= abs(r) - 1e-12 for v in shifted),
        "circular_denominator": len(y), "circular_shift_r": shifted,
        "n_permutations": math.factorial(len(y)), **exact_result,
    }
    return result


def slope(x, y):
    return float(stats.linregress(x / 10.0, y).slope)


def account(x, p, c, years):
    P, C = average(p), average(c)
    frequency = C * (p - P)
    composition = P * (c - C)
    covariation = (p - P) * (c - C)
    mean_response = p * c
    terms = {"frequency": frequency, "composition": composition, "covariation": covariation}
    term_slopes = {key: slope(x, values) for key, values in terms.items()}
    mean_slope = slope(x, mean_response)
    reconstruction_errors = [abs(float(f + z + v + P * C - m))
                             for f, z, v, m in zip(frequency, composition, covariation, mean_response)]
    if max(reconstruction_errors) > 1e-12:
        raise ValueError("accounting value identity failed")
    if not math.isclose(math.fsum(term_slopes.values()), mean_slope, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("accounting slope identity failed")
    summary = {
        "mean_frequency": P, "mean_conditional_fraction": C,
        "constant_product_of_means": P * C, "mean_fish_fraction": average(mean_response),
        "covariation_mean": average(covariation), "component_slopes_per_10pp": term_slopes,
        "sum_component_slopes_per_10pp": math.fsum(term_slopes.values()),
        "mean_response_slope_per_10pp": mean_slope,
        "signed_slope_fraction": {key: value / mean_slope for key, value in term_slopes.items()}
                                 if abs(mean_slope) > 1e-12 else None,
        "max_value_identity_error": max(reconstruction_errors),
        "slope_identity_error": math.fsum(term_slopes.values()) - mean_slope,
    }
    rows = [{"year": year, **{key: float(terms[key][i]) for key in terms},
             "mean_fish_fraction": float(mean_response[i]), "sic_aug_nov": float(x[i])}
            for i, year in enumerate(years)]
    return rows, summary


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(repo_root, source_directory, out):
    ice_path = repo_root / "research/climate-penguin/outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"
    manifest = [pinned_source(source_directory / f"{species}_diet_summary.csv", repo_root)
                for species in ("Adelie", "Gentoo")]
    manifest.append(pinned_source(ice_path, repo_root))
    annual, audits = source_components(source_directory)
    exposure, ice_audit = annual_exposure(ice_path)
    annual = [{**row, "sic_aug_nov": exposure[row["year"]]} for row in annual]
    gentoo = [row for row in annual if row["species"] == "Gentoo"]
    if [row["year"] for row in gentoo] != list(YEARS) or sum(row["n_stomachs"] for row in gentoo) != 73:
        raise ValueError("specified Gentoo cohort changed")
    if any(row["n_positive_fish_mass"] < 1 or row["conditional_fish_fraction"] is None for row in gentoo):
        raise ValueError("conditional fraction unavailable in the fixed nine seasons")
    x = np.array([row["sic_aug_nov"] for row in gentoo])
    p = np.array([row["positive_mass_frequency"] for row in gentoo])
    c = np.array([row["conditional_fish_fraction"] for row in gentoo])
    m = np.array([row["mean_fish_fraction"] for row in gentoo])
    if not all(np.isfinite(z).all() for z in (x, p, c, m)):
        raise ValueError("nonfinite primary quantity")
    if not all(((z >= 0) & (z <= 1)).all() for z in (p, c, m)):
        raise ValueError("fraction outside 0..1")
    family, exact = joint_permutations(x, {"frequency": p, "composition": c, "mean_response": m})
    associations = {key: describe(x, values, list(YEARS), exact[key])
                    for key, values in (("frequency", p), ("composition", c))}
    mean_association = describe(x, m, list(YEARS), exact["mean_response"])
    terms, accounting = account(x, p, c, list(YEARS))
    leave_out = []
    for i, year in enumerate(YEARS):
        keep_years = [kept for kept in YEARS if kept != year]
        _, value = account(np.delete(x, i), np.delete(p, i), np.delete(c, i), keep_years)
        leave_out.append({"omitted_year": year, **value["component_slopes_per_10pp"],
                          "mean_response": value["mean_response_slope_per_10pp"]})
    masses = {}
    for column in ("mean_fish_mass_g", "mean_crustacean_mass_g", "mean_food_mass_g"):
        values = np.array([row[column] for row in gentoo])
        masses[column] = {"mean_g": average(values), "min_g": float(min(values)), "max_g": float(max(values)),
                          "pearson_r": float(stats.pearsonr(x, values).statistic),
                          "slope_g_per_10pp": slope(x, values)}
    result = {
        "status": "independent_recalculation_complete", "analysis_date": "2026-11-06",
        "independence": "Raw CSV loops, SciPy common exposure permutations, statsmodels HC3; no primary analysis helpers or numeric outputs used.",
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
        "primary_species": "Gentoo", "n_seasons": len(gentoo),
        "n_stomachs": sum(row["n_stomachs"] for row in gentoo),
        "source_manifest": manifest, "source_audit": audits, "ice_source_audit": ice_audit,
        "species_season_components": annual, "gentoo_primary_nine_seasons": gentoo,
        "component_associations": associations, "mean_response_association": mean_association,
        "permutation_family": family, "slope_accounting": accounting,
        "annual_accounting_terms": terms, "leave_one_season_accounting": leave_out,
        "recovered_mass_descriptives": masses,
        "support_checks": {
            "all_nine_seasons_have_positive_fish_mass": True,
            "positive_counts_by_year": {str(row["year"]): row["n_positive_fish_mass"] for row in gentoo},
            "zero_positive_gentoo_seasons": [],
            "max_direct_mean_minus_product_absolute_error": float(np.max(np.abs(m - p * c))),
            "both_prespecified_components_vary": bool(np.ptp(p) > 0 and np.ptp(c) > 0),
            "mass_means_include_zero_fish_stomachs": True,
            "loo_accounting_recentres_P_and_C_in_each_subset": True,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "independent_results.json").write_text(
        json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    for filename, rows in (("species_season_components.csv", annual),
                           ("gentoo_primary_nine_seasons.csv", gentoo),
                           ("annual_accounting_terms.csv", terms),
                           ("leave_one_season_accounting.csv", leave_out)):
        write_csv(out / filename, rows)
    palmer_reference.run(repo_root, out)
    print(json.dumps({"component_associations": associations, "slope_accounting": accounting,
                      "recovered_mass_descriptives": masses, "support_checks": result["support_checks"]},
                     ensure_ascii=False, allow_nan=False, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5])
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output = args.out.resolve() if args.out else repo_root / OUTPUT_PATH / "independent"
    run(repo_root, args.source_dir.resolve(), output)
