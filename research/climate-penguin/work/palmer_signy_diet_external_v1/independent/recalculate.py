"""Independent numeric audit of the Palmer–Signy dietary comparison.

No function or generated numeric output from the primary analysis is imported.
Input ingestion uses csv/ElementTree; inference uses SciPy and statsmodels.
Run with Python plus NumPy, SciPy and statsmodels, supplying --source-dir for
the two hash-pinned Signy CSVs. Palmer inputs and output defaults are repo-relative.
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
import xml.etree.ElementTree as ET

import numpy as np
import scipy
from scipy import stats
import statsmodels
import statsmodels.api as sm


SIGNY_YEARS = tuple(range(2001, 2010))
PALMER_YEARS = tuple(range(2009, 2015))
SOURCE_HASHES = {
    "Adelie_diet_summary.csv": "ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
    "Gentoo_diet_summary.csv": "6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902",
    "macro_monthly_seaice_1991_2020.csv": "b21b10743f3a56281d0cf62f55988823f55b645b6d3fbb1bf7c2d366dff1b3ae",
    "pickett2018_europepmc.xml": "7d074d865cb6cf187f4aad56f7535179a8de9832c54b46783d6013dad7efd97d",
}
ANALYSIS_PATH = Path("research/climate-penguin/work/palmer_signy_diet_external_v1")
OUTPUT_PATH = Path("research/climate-penguin/outputs/palmer_signy_diet_external_v1")


def portable_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.name


def rows_from_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def hash_source(path: Path, repo_root: Path) -> dict:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = SOURCE_HASHES.get(path.name)
    if expected is not None and expected != actual:
        raise ValueError(f"source hash mismatch: {path.name}")
    return {"file": portable_path(path, repo_root), "sha256": actual, "expected_sha256": expected}


def number(value: str) -> float:
    return float(value) if value.strip() else math.nan


def mean(values) -> float:
    values = list(values)
    return math.fsum(values) / len(values)


def signy_species(raw_directory: Path):
    annual = []
    audits = []
    for species in ("Adelie", "Gentoo"):
        records = rows_from_csv(raw_directory / f"{species}_diet_summary.csv")
        observed_keys = set()
        per_year = {year: [] for year in SIGNY_YEARS}
        source_counts = {year: 0 for year in SIGNY_YEARS}
        excluded = []
        closure_anomalies = []
        n_legacy = 0
        nonfood_positive = 0
        for row in records:
            key = row["DATE"], row["RECORD_ID"]
            if key in observed_keys:
                raise ValueError(f"duplicate raw stomach: {key}")
            observed_keys.add(key)
            sampled = date.fromisoformat(row["DATE"])
            if sampled.month not in (1, 2, 3, 4, 11, 12):
                raise ValueError(f"unexpected sampling month: {key}")
            year = sampled.year - int(sampled.month <= 4)
            if year not in source_counts:
                continue
            source_counts[year] += 1
            fish = number(row["FISH_MASS_g"])
            crustacean = number(row["CRUSTACEAN_MASS_g"])
            cephalopod = number(row["CEPHALOPOD_MASS_g"])
            other_food = number(row["OTHER_FOOD_MASS_g"])
            total = number(row["TOTAL_MASS_g"])
            krill = number(row["EUPHAUSIA_SUPERBA_MASS_g"])
            nonfood = number(row["NON_FOOD_MASS_g"])
            nonfood_positive += int(nonfood > 0)
            food = fish + crustacean + cephalopod + other_food
            pair_mass = fish + crustacean
            legacy_checks = {
                "finite_fish_crustacean_total": all(map(math.isfinite, (fish, crustacean, total))),
                "fish_nonnegative": fish >= 0,
                "crustacean_nonnegative": crustacean >= 0,
                "total_positive": total > 0,
                "fish_plus_crustacean_positive": pair_mass > 0,
                "fish_plus_crustacean_not_excessive": pair_mass <= 1.05 * total + 0.05,
                "krill_within_crustacean": math.isnan(krill) or krill <= 1.05 * crustacean + 0.05,
            }
            legacy_good = all(legacy_checks.values())
            n_legacy += int(legacy_good)
            primary_checks = {
                **legacy_checks,
                "cephalopod_finite_nonnegative": math.isfinite(cephalopod) and cephalopod >= 0,
                "other_food_finite_nonnegative": math.isfinite(other_food) and other_food >= 0,
                "food_positive": food > 0,
                "food_not_excessive": food <= 1.05 * total + 0.05,
            }
            primary_good = all(primary_checks.values())
            if all(map(math.isfinite, (food, total, nonfood))) and abs(total - nonfood - food) > 0.5:
                closure_anomalies.append({
                    "DATE": key[0], "RECORD_ID": key[1], "year": year,
                    "total_g": total, "nonfood_g": nonfood, "food_sum_g": food,
                    "total_minus_nonfood_minus_food_g": total - nonfood - food,
                    "passes_primary_qc": primary_good,
                })
            if not primary_good:
                excluded.append({"DATE": key[0], "RECORD_ID": key[1],
                                 "failed_checks": [k for k, v in primary_checks.items() if not v]})
                continue
            per_year[year].append({
                "fish_food": fish / food,
                "fish_total": fish / total,
                "legacy_fish_crustacean": fish / pair_mass,
            })
        for year, samples in per_year.items():
            if not samples:
                raise ValueError(f"empty species-season: {species} {year}")
            annual.append({
                "region": "Signy", "species": species, "year": year,
                "n_source_stomachs": source_counts[year], "n_stomachs": len(samples),
                **{f"{metric}_mean": mean(s[metric] for s in samples)
                   for metric in ("fish_food", "fish_total", "legacy_fish_crustacean")},
            })
        audits.append({
            "species": species, "n_source": sum(source_counts.values()),
            "n_valid": sum(len(v) for v in per_year.values()), "legacy_n_valid": n_legacy,
            "n_excluded": len(excluded), "excluded_keys": excluded,
            "nonfood_positive_source_rows": nonfood_positive,
            "closure_anomalies_gt_0_5g": closure_anomalies,
        })
    return annual, audits


def palmer_from_xml(xml_path: Path, csv_path: Path):
    root = ET.parse(xml_path).getroot()
    table = root.find(".//table-wrap[@id='ece34445-tbl-0001']/table/tbody")
    if table is None:
        raise ValueError("Table 1 absent from saved primary XML")
    fish_rows = []
    category = None
    for tr in table.findall("tr"):
        cells = ["".join(td.itertext()).strip() for td in tr.findall("td")]
        if len(cells) == 8:
            category = cells.pop(0)
        if len(cells) != 7:
            raise ValueError("unexpected Table 1 cell layout")
        if category != "Unidentified fish (%)":
            continue
        year = int(cells[0])
        for species, value_pos, n_pos in (("Adelie", 1, 2), ("Gentoo", 3, 4)):
            fish_mean = float(cells[value_pos].split("±")[0].strip())
            fish_rows.append({
                "region": "Palmer", "species": species, "year": year,
                "fish_mean_pct": fish_mean, "fish_food_mean": fish_mean / 100.0,
                "sample_n": int(cells[n_pos]),
            })
    lookup = {(r["species"], r["year"]): r for r in fish_rows}
    if set(lookup) != {(s, y) for s in ("Adelie", "Gentoo") for y in PALMER_YEARS}:
        raise ValueError("Palmer table keys incomplete")
    extraction = rows_from_csv(csv_path)
    if len(extraction) != len(lookup):
        raise ValueError("Palmer CSV row count mismatch")
    compared = set()
    for row in extraction:
        key = row["species"], int(row["season_start_year"])
        if key in compared:
            raise ValueError("duplicate key in Palmer extracted CSV")
        compared.add(key)
        original = lookup[key]
        if number(row["fish_mean_pct"]) != original["fish_mean_pct"]:
            raise ValueError(f"Palmer fish mean transcription mismatch: {key}")
        if int(row["sample_n"]) != original["sample_n"]:
            raise ValueError(f"Palmer sample n transcription mismatch: {key}")
        if int(row["season_end_year"]) != key[1] + 1:
            raise ValueError(f"Palmer season end mismatch: {key}")
    return fish_rows, {
        "independently_read_primary_xml": True,
        "fish_means_compared_to_derived_csv": len(extraction),
        "fish_sample_sizes_compared_to_derived_csv": len(extraction),
        "table_sample_n_totals": {
            s: sum(r["sample_n"] for r in fish_rows if r["species"] == s)
            for s in ("Adelie", "Gentoo")
        },
        "methods_sample_n_totals": {"Adelie": 136, "Gentoo": 128},
        "unresolved_source_issue": "Gentoo Table 1 sum 129 versus methods 128; no correction or individual reconstruction",
    }


def sea_ice(ice_path: Path):
    needed = {(site, year): {} for site, years in
              (("GOPT", SIGNY_YEARS), ("BISC", PALMER_YEARS), ("LITC", PALMER_YEARS))
              for year in years}
    selected_rows = 0
    for row in rows_from_csv(ice_path):
        key = row["site_id"], int(row["year"])
        month = int(row["month"])
        if key not in needed or float(row["inner_km"]) != 0 or month not in (8, 9, 10, 11):
            continue
        if month in needed[key]:
            raise ValueError(f"duplicate monthly exposure key: {key} {month}")
        expected = calendar.monthrange(key[1], month)[1]
        if row["complete_month"].lower() != "true":
            raise ValueError(f"month marked incomplete: {key} {month}")
        if any(int(row[col]) != expected for col in ("days", "supported_days", "expected_days")):
            raise ValueError(f"daily coverage does not match calendar: {key} {month}")
        concentration = number(row["sic_mean"])
        if not math.isfinite(concentration) or not 0 <= concentration <= 100:
            raise ValueError(f"invalid SIC: {key} {month}")
        needed[key][month] = concentration
        selected_rows += 1
    annual = {}
    proxy_rows = []
    for key, values in needed.items():
        if set(values) != {8, 9, 10, 11}:
            raise ValueError(f"not all four antecedent months: {key}")
        annual[key] = mean(values[m] for m in (8, 9, 10, 11))
        proxy_rows.append({"site_id": key[0], "year": key[1], "sic_aug_nov": annual[key]})
    region = {
        "Signy": {year: annual[("GOPT", year)] for year in SIGNY_YEARS},
        "Palmer": {year: mean(annual[(site, year)] for site in ("BISC", "LITC"))
                   for year in PALMER_YEARS},
    }
    return region, annual, proxy_rows, {
        "unique_monthly_rows": selected_rows,
        "expected_monthly_rows": 4 * (len(SIGNY_YEARS) + 2 * len(PALMER_YEARS)),
        "all_four_months_present": True,
        "all_daily_counts_equal_calendar_days": True,
        "all_complete_month_flags_true": True,
        "no_duplicate_selected_keys": True,
        "equal_month_then_equal_proxy_weighting": True,
    }


def make_pairs(species_rows, ice_by_year, metric="fish_food_mean"):
    by_year = {}
    for row in species_rows:
        by_year.setdefault(row["year"], {})[row["species"]] = row
    result = []
    for year, species in sorted(by_year.items()):
        if set(species) != {"Adelie", "Gentoo"}:
            raise ValueError(f"incomplete species pairing in {year}")
        a, g = species["Adelie"][metric], species["Gentoo"][metric]
        result.append({"region": species["Adelie"]["region"], "year": year,
                       "Adelie": a, "Gentoo": g, "signed_gap": g - a,
                       "distance": abs(g - a), "sic_aug_nov": ice_by_year[year]})
    if set(by_year) != set(ice_by_year):
        raise ValueError("year support differs between diet and ice")
    return result


def exact_absolute_pearson(x, y):
    """SciPy enumerates response permutations; calculate an absolute-tail p.

    SciPy's returned pvalue uses a different two-sided convention and is not used.
    Enumeration includes permutations with tied outcomes in their correct counts.
    """
    xc = x - x.mean()
    yc = y - y.mean()
    norm = np.sqrt(np.dot(xc, xc) * np.dot(yc, yc))

    def statistic(permuted_y, axis=-1):
        return np.sum(permuted_y * xc, axis=axis) / norm

    enumeration = stats.permutation_test(
        (yc,), statistic, permutation_type="pairings", vectorized=True,
        n_resamples=np.inf, batch=4096, alternative="greater",
    )
    distribution = enumeration.null_distribution
    expected = math.factorial(len(y))
    if len(distribution) != expected:
        raise ValueError("permutation enumeration incomplete")
    observed = float(statistic(yc))
    count = int(np.count_nonzero(np.abs(distribution) >= abs(observed) - 1e-12))
    return {"n_permutations": expected, "extreme_count": count, "p_exact": count / expected}


def summarize(pairs):
    years = np.array([r["year"] for r in pairs], dtype=float)
    x = np.array([r["sic_aug_nov"] for r in pairs])
    y = np.array([r["distance"] for r in pairs])
    design = sm.add_constant(x / 10.0)
    model = sm.OLS(y, design).fit(cov_type="HC3", use_t=True)
    ci = model.conf_int(alpha=0.05)
    observed = float(stats.pearsonr(x, y).statistic)
    leave_one = {str(int(years[k])): float(stats.pearsonr(np.delete(x, k), np.delete(y, k)).statistic)
                 for k in range(len(y))}
    time_design = sm.add_constant(years - years.mean())
    x_residual = sm.OLS(x, time_design).fit().resid
    y_residual = sm.OLS(y, time_design).fit().resid
    shifts = [float(stats.pearsonr(x, np.roll(y, i)).statistic) for i in range(len(y))]
    return {
        "n_seasons": len(y), "years": [int(z) for z in years],
        "mean_distance": mean(y), "min_distance": float(min(y)), "max_distance": float(max(y)),
        "sic_min": float(min(x)), "sic_max": float(max(x)), "pearson_r": observed,
        "slope_per_10pp": float(model.params[1]), "intercept": float(model.params[0]),
        "hc3_slope_95_low": float(ci[1, 0]), "hc3_slope_95_high": float(ci[1, 1]),
        "hc3_slope_se": float(model.bse[1]), "hc3_t_df": int(model.df_resid),
        "leave_one_season_r_min": min(leave_one.values()), "leave_one_season_r_max": max(leave_one.values()),
        "leave_one_season_r": leave_one,
        "detrended_r": float(stats.pearsonr(x_residual, y_residual).statistic),
        "first_difference_r": float(stats.pearsonr(np.diff(x), np.diff(y)).statistic),
        "circular_extreme_count": sum(abs(z) >= abs(observed) - 1e-12 for z in shifts),
        "circular_denominator": len(y), "circular_shift_r": shifts,
        **exact_absolute_pearson(x, y),
    }


def external_prediction(source, target):
    x = np.array([r["sic_aug_nov"] for r in source])
    y = np.array([r["distance"] for r in source])
    fit = stats.linregress(x, y)
    baseline = mean(y)
    predictions = []
    for row in target:
        predicted = float(fit.intercept + fit.slope * row["sic_aug_nov"])
        predictions.append({
            **row, "predicted_distance": predicted, "training_mean_prediction": baseline,
            "in_training_ice_range": bool(x.min() <= row["sic_aug_nov"] <= x.max()),
            "prediction_in_response_range": 0 <= predicted <= 1,
            "model_absolute_error": abs(predicted - row["distance"]),
            "training_mean_absolute_error": abs(baseline - row["distance"]),
        })
    scores = {}
    for label, subset in (("all_target_seasons", predictions),
                          ("within_training_ice_range", [r for r in predictions if r["in_training_ice_range"]])):
        scores[label] = {
            "n": len(subset), "model_mae": mean(r["model_absolute_error"] for r in subset),
            "training_mean_mae": mean(r["training_mean_absolute_error"] for r in subset),
            "model_rmse": math.sqrt(mean((r["predicted_distance"] - r["distance"]) ** 2 for r in subset)),
            "training_mean_rmse": math.sqrt(mean((baseline - r["distance"]) ** 2 for r in subset)),
        }
    scores["training_intercept"] = float(fit.intercept)
    scores["training_slope_per_10pp"] = float(fit.slope * 10.0)
    return predictions, scores


def write_csv(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def run(repo_root: Path, raw_directory: Path, output: Path):
    palmer_directory = repo_root / ANALYSIS_PATH / "sources"
    ice_path = repo_root / "research/climate-penguin/outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"
    xml_path = palmer_directory / "pickett2018_europepmc.xml"
    csv_path = palmer_directory / "pickett2018_palmer_diet_species_season.csv"
    source_paths = [raw_directory / f"{s}_diet_summary.csv" for s in ("Adelie", "Gentoo")]
    source_paths += [ice_path, xml_path, csv_path]
    hashes = [hash_source(path, repo_root) for path in source_paths]
    signy, source_audit = signy_species(raw_directory)
    palmer, palmer_audit = palmer_from_xml(xml_path, csv_path)
    regional_ice, proxy_ice, proxy_rows, ice_audit = sea_ice(ice_path)
    signy_pairs = make_pairs(signy, regional_ice["Signy"])
    palmer_pairs = make_pairs(palmer, regional_ice["Palmer"])
    regions = {"Signy": summarize(signy_pairs), "Palmer": summarize(palmer_pairs)}
    sensitivity = []
    for proxy in ("BISC", "LITC"):
        alternative = make_pairs(palmer, {year: proxy_ice[(proxy, year)] for year in PALMER_YEARS})
        sensitivity.append({"scope": "Palmer_proxy", "variant": proxy, **summarize(alternative)})
    for metric in ("fish_total_mean", "legacy_fish_crustacean_mean"):
        alternative = make_pairs(signy, regional_ice["Signy"], metric)
        sensitivity.append({"scope": "Signy_denominator", "variant": metric, **summarize(alternative)})
    predicted, prediction_scores = external_prediction(signy_pairs, palmer_pairs)
    output.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "independent_recalculation_complete",
        "independence": "No primary analysis helper or numeric output used; raw CSV row loops, primary XML extraction, SciPy permutations and statsmodels HC3.",
        "analysis_date": "2026-11-06", "source_manifest": hashes,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
        "estimand": "Absolute Gentoo–Adelie difference in equal-stomach mean fish fraction of recovered food",
        "primary_qc": "Existing F+C mass mask plus complete nonnegative edible components and food <= 1.05 * total + 0.05 g",
        "signy_species_seasons": signy, "palmer_species_seasons": palmer,
        "annual_pair_comparison": signy_pairs + palmer_pairs,
        "annual_ice_proxies": proxy_rows,
        "regions": regions, "transport": prediction_scores, "predictions": predicted,
        "source_audit": source_audit, "palmer_source_audit": palmer_audit,
        "ice_source_audit": ice_audit, "sensitivity": sensitivity,
        "inference_limit": "Region-specific descriptive results; exact p assumes exchangeable years; HC3 does not correct serial dependence; retrospective geographically external comparison.",
    }
    (output / "independent_results.json").write_text(
        json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8")
    write_csv(output / "annual_pair_comparison.csv", result["annual_pair_comparison"])
    write_csv(output / "signy_species_seasons.csv", signy)
    write_csv(output / "signy_to_palmer_transport.csv", predicted)
    print(json.dumps({"regions": regions, "transport": prediction_scores,
                      "ice_source_audit": ice_audit, "output": str(output)},
                     ensure_ascii=False, allow_nan=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[5],
                        help="Repository root; defaults to the checkout containing this script")
    parser.add_argument("--source-dir", type=Path, required=True,
                        help="Directory containing Adelie_diet_summary.csv and Gentoo_diet_summary.csv")
    parser.add_argument("--out", type=Path,
                        help="Output directory; defaults to the analysis output's independent/ directory")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    output = args.out.resolve() if args.out else repo_root / OUTPUT_PATH / "independent"
    run(repo_root, args.source_dir.resolve(), output)
