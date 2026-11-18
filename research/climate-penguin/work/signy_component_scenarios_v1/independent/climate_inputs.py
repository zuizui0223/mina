#!/usr/bin/env python3
"""Independently audit Signy GOPT climatic inputs; never fit or predict diet.

Run from any working directory, with Python 3.9+ and no third-party packages:
    python research/climate-penguin/work/signy_component_scenarios_v1/independent/climate_inputs.py

--root points to the climate-penguin project root, and --out overrides the output
folder. All inputs are tracked local CSV/JSON extracts. No network is used and
no helper from the original analyses is imported. Annual SIC is the arithmetic
mean of four monthly values, followed by equal weights over 20 complete years.
This deliberately reproduces diet_niche_scenarios_v1, whose averaging differs
from the calendar-day-weighted CMIP6 seasonal_climatologies table. That table is
used only to cross-check site/member/grid provenance and the weighting note.
"""
from __future__ import annotations

import argparse
import calendar
import csv
from datetime import date, timedelta
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import fmean, stdev

MONTHS = (8, 9, 10, 11)
SUPPORT = (21.90128214834321, 66.68284803598858)
PERIODS = {
    "historical": ((1995, 2014),),
    "ssp245": ((2041, 2060), (2081, 2100)),
    "ssp585": ((2041, 2060), (2081, 2100)),
}
EXPECTED_MODELS = (("ACCESS-CM2", "r1i1p1f1"),
                   ("BCC-CSM2-MR", "r1i1p1f1"),
                   ("CESM2", "r4i1p1f1"))
ABS_TOL = 1e-10


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    check(bool(rows), f"No output rows: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    check(b"\r" not in path.read_bytes(), f"Non-LF line ending: {path.name}")


def support_class(value):
    if value < SUPPORT[0]:
        return "below"
    if value > SUPPORT[1]:
        return "above"
    return "within"


def annual_means(rows, value_key, expected_years, label):
    expected_keys = {(year, month) for year in expected_years for month in MONTHS}
    values = {}
    for row in rows:
        key = (int(row["year"]), int(row["month"]))
        check(key not in values, f"Duplicate year/month: {label} {key}")
        value = float(row[value_key])
        check(math.isfinite(value) and 0 <= value <= 100,
              f"Invalid raw SIC: {label} {key} {value}")
        values[key] = value
    check(set(values) == expected_keys, f"Incomplete/extra year-month coverage: {label}")
    return {year: fmean(values[year, month] for month in MONTHS)
            for year in sorted(expected_years)}


def wgs84_distance_km(lat1, lon1, lat2, lon2):
    """Vincenty inverse on WGS84; independent of extraction's pyproj helper."""
    major = 6378137.0
    flattening = 1 / 298.257223563
    minor = (1 - flattening) * major
    u1 = math.atan((1 - flattening) * math.tan(math.radians(lat1)))
    u2 = math.atan((1 - flattening) * math.tan(math.radians(lat2)))
    su1, cu1, su2, cu2 = math.sin(u1), math.cos(u1), math.sin(u2), math.cos(u2)
    longitude = math.radians(lon2 - lon1)
    lam = longitude
    for _ in range(100):
        sl, cl = math.sin(lam), math.cos(lam)
        sin_sigma = math.hypot(cu2 * sl, cu1 * su2 - su1 * cu2 * cl)
        if sin_sigma == 0:
            return 0.0
        cos_sigma = su1 * su2 + cu1 * cu2 * cl
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cu1 * cu2 * sl / sin_sigma
        cos2_alpha = 1 - sin_alpha * sin_alpha
        cos2_sigma_mid = (cos_sigma - 2 * su1 * su2 / cos2_alpha) if cos2_alpha else 0.0
        c = flattening / 16 * cos2_alpha * (4 + flattening * (4 - 3 * cos2_alpha))
        previous = lam
        lam = longitude + (1 - c) * flattening * sin_alpha * (
            sigma + c * sin_sigma * (cos2_sigma_mid + c * cos_sigma *
                                    (-1 + 2 * cos2_sigma_mid ** 2)))
        if abs(lam - previous) < 1e-13:
            break
    else:
        raise ValueError("WGS84 inverse did not converge")
    u2_coeff = cos2_alpha * (major * major - minor * minor) / (minor * minor)
    a = 1 + u2_coeff / 16384 * (4096 + u2_coeff * (-768 + u2_coeff * (320 - 175 * u2_coeff)))
    b = u2_coeff / 1024 * (256 + u2_coeff * (-128 + u2_coeff * (74 - 47 * u2_coeff)))
    correction = b * sin_sigma * (cos2_sigma_mid + b / 4 * (
        cos_sigma * (-1 + 2 * cos2_sigma_mid ** 2) - b / 6 * cos2_sigma_mid *
        (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_mid ** 2)))
    return minor * a * (sigma - correction) / 1000


def main(root, out):
    inputs = {}

    def source(relative_path):
        path = root / relative_path
        check(path.is_file(), f"Missing required input: {relative_path}")
        inputs.setdefault(relative_path, {}).update(
            {"file": relative_path, "sha256": sha256(path), "bytes": path.stat().st_size})
        return path

    legacy_manifest = json.loads(source("outputs/diet_niche_scenarios_v1/source_manifest.json").read_text())
    for entry in legacy_manifest:
        relative_path = entry["file"].replace("\\", "/")
        check(not Path(relative_path).is_absolute() and ".." not in Path(relative_path).parts,
              "Unsafe path in original source manifest")
        path = source(relative_path)
        check(sha256(path) == entry["sha256"], f"Original source hash mismatch: {relative_path}")
        inputs[relative_path]["original_manifest_sha256"] = entry["sha256"]
        inputs[relative_path]["original_manifest_hash_match"] = True
    check(len(legacy_manifest) == 11, "Expected 11 original source-manifest entries")

    # Only the predictor/support columns are used from the legacy diet table.
    dietary_support = read_csv(source("outputs/niche_multiscale_v1/annual_distances.csv"))
    dietary_support = [r for r in dietary_support if r["variant"] == "full"
                       and r["pair"] == "Gentoo-vs-others" and r["metric"] == "fish"]
    xs = [float(r["sic_aug_nov"]) for r in dietary_support]
    check(len(xs) == 9 and min(xs) == SUPPORT[0] and max(xs) == SUPPORT[1],
          "Diet SIC support/cohort changed")
    original = read_csv(source("outputs/diet_niche_scenarios_v1/conditional_scenarios.csv"))
    original_by_key = {(r["model"], r["member"], r["scenario"], r["period"]): r for r in original}
    check(len(original) == len(original_by_key) == 12, "Legacy scenario keys not unique/complete")

    sites_path = source("outputs/climate_penguin/daily_ice_locations.csv")
    sites = [r for r in read_csv(sites_path) if r["site_id"] == "GOPT"]
    check(len(sites) == 1, "GOPT site is not unique")
    site = sites[0]
    location = site["location_id"]
    check(location == "loc020", "GOPT location mapping changed")
    observed = read_csv(source("outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"))
    observed = [r for r in observed if r["site_id"] == "GOPT" and float(r["inner_km"]) == 0
                and 1995 <= int(r["year"]) <= 2014]
    for r in observed:
        expected_days = calendar.monthrange(int(r["year"]), int(r["month"]))[1]
        check(r["location_id"] == location and r["complete_month"].lower() == "true"
              and all(int(r[k]) == expected_days for k in ("days", "supported_days", "expected_days")),
              f"Observed completeness failure in {r['year']}-{r['month']}")
    observed_annual = annual_means(observed, "sic_mean", range(1995, 2015), "observed")
    baseline = fmean(float(r["sic_mean"]) for r in observed)
    check(abs(baseline - fmean(observed_annual.values())) <= ABS_TOL,
          "Observed pooled-month and equal-year reference mismatch")

    # Audit the recorded observational acquisition/version; no raw files fetched.
    daily_entries = []
    for name in ("daily_concentration_1991_2010_manifest.json", "daily_concentration_manifest.json"):
        records = json.loads(source(f"outputs/climate_penguin/{name}").read_text())
        daily_entries.extend(r for r in records if "1995-01-01" <= r["date"] < "2015-01-01")
    expected_dates = {str(date(year, 8, 1) + timedelta(days=i))
                      for year in range(1995, 2015) for i in range(122)}
    check(len(daily_entries) == len(expected_dates) == 2440
          and {r["date"] for r in daily_entries} == expected_dates,
          "Observed daily acquisition-manifest coverage is incomplete")
    check(all(r["ok"] and "conc_450a1_files" in r["url"]
              and "cdr-v3p1" in r["url"] and re.fullmatch(r"[0-9a-f]{64}", r["sha256"])
              for r in daily_entries), "Observed source acquisition/version not confirmed")

    cmip_manifest = json.loads(source("outputs/cmip6_projection_v1/manifest.json").read_text())
    metadata = json.loads(source("outputs/cmip6_projection_v1/source_metadata.json").read_text())
    metadata = [r for r in metadata if r["variable_id"] == "siconc"]
    meta_by_key = {(r["source_id"], r["member_id"], r["experiment_id"]): r for r in metadata}
    stores = [r for r in read_csv(source("outputs/cmip6_projection_v1/selected_stores.csv"))
              if r["variable_id"] == "siconc"]
    stores_by_key = {(r["source_id"], r["member_id"], r["experiment_id"]): r for r in stores}
    published_stores = read_csv(source("outputs/diet_niche_manuscript_v1/CMIP6_SOURCE_STORES.csv"))
    check({tuple(sorted(r.items())) for r in stores} == {tuple(sorted(r.items())) for r in published_stores},
          "Source-store manuscript export disagrees with selected stores")
    check(len(stores) == len(stores_by_key) == len(meta_by_key) == 9, "Expected nine unique siconc stores")
    check(sorted((r["source_id"], r["member_id"]) for r in cmip_manifest["selected_models"])
          == list(EXPECTED_MODELS), "Availability-selected model/member set changed")
    extraction_hash = sha256(source("work/cmip6_projection_v1/extract.py"))
    check(extraction_hash == cmip_manifest["extraction_code_sha256"], "CMIP extraction-code identity mismatch")
    check(sha256(sites_path) == cmip_manifest["site_input_sha256"], "CMIP site identity mismatch")
    for name in ("work/diet_niche_scenarios_v1/analyze.py",
                 "work/climate_penguin/monthly_seaice_for_counts.py",
                 "work/climate_penguin/extract_daily_concentration.py",
                 "outputs/climate_penguin/macro_monthly_seaice_1991_2020_checks.json"):
        source(name)
    seasonal = [r for r in read_csv(source("outputs/cmip6_projection_v1/seasonal_climatologies.csv"))
                if r["site_id"] == "GOPT" and r["variable_id"] == "siconc"]
    check(len(seasonal) == 15, "Expected 15 GOPT siconc climatology provenance rows")

    scenario_rows, annual_rows, support_rows, source_rows = [], [], [], []
    model_caveats = []
    max_comparison_error = 0.0
    physical_violations = []
    for model, member in EXPECTED_MODELS:
        support_file = f"outputs/cmip6_projection_v1/support_{model}_{member}_siconc.csv"
        grid_rows = [r for r in read_csv(source(support_file)) if r["site_id"] == "GOPT"]
        check(len(grid_rows) == 1, f"GOPT support not unique: {model}")
        grid = grid_rows[0]
        check((grid["source_id"], grid["member_id"], grid["location_id"], grid["variable_id"])
              == (model, member, location, "siconc"), f"Grid model/member/location mismatch: {model}")
        check(all(float(grid[k]) == float(site[k]) for k in ("latitude", "longitude")),
              f"Site-coordinate mismatch: {model}")
        distance = float(grid["distance_km"])
        independent_distance = wgs84_distance_km(float(grid["latitude"]), float(grid["longitude"]),
                                               float(grid["grid_lat"]), float(grid["grid_lon"]))
        check(abs(independent_distance - distance) < 1e-6, f"WGS84 grid distance mismatch: {model}")
        related_seasonal = [r for r in seasonal if r["source_id"] == model]
        check(len(related_seasonal) == 5 and all(r["member_id"] == member
              and r["location_id"] == location and r["grid_cell_id"] == grid["grid_cell_id"]
              and abs(float(r["distance_km"]) - distance) <= ABS_TOL
              for r in related_seasonal), f"Seasonal provenance mismatch: {model}")
        annual_by_experiment = {}
        reference_meta = meta_by_key[model, member, "historical"]
        for experiment, spans in PERIODS.items():
            key = (model, member, experiment)
            meta, store = meta_by_key[key], stores_by_key[key]
            check(meta["zstore"] == store["zstore"] == meta["cache_identity"]["zstore"]
                  and f"/v{store['version']}/" in store["zstore"]
                  and store["table_id"] == "SImon" and store["grid_label"] == grid["grid_label"],
                  f"Source version/grid mismatch: {key}")
            check(meta["source_units"] == "%" and meta["output_units"] == "percent",
                  f"Wrong SIC units: {key}")
            check(meta["grid_unchanged_vs_historical"] is True
                  and all(meta["cache_identity"][k] == reference_meta["cache_identity"][k]
                          for k in ("grid_sha256", "support_sha256")),
                  f"Historical/future grid-support identity mismatch: {key}")
            check(meta["cache_identity"]["code_sha256"] == extraction_hash
                  and meta["cache_identity"]["site_file_sha256"] == sha256(sites_path)
                  and meta["cache_identity"]["months"] == list(MONTHS)
                  and meta["cache_identity"]["periods"] == [list(span) for span in spans],
                  f"Cached extraction provenance mismatch: {key}")
            if experiment != "historical":
                check((meta["parent_source_id"], meta["parent_experiment_id"], meta["parent_variant_label"])
                      == (model, "historical", member), f"Historical parent/member mismatch: {key}")
            relative_path = f"outputs/cmip6_projection_v1/monthly_{model}_{member}_siconc_{experiment}.csv.gz"
            all_rows = read_csv(source(relative_path))
            check(len(all_rows) == meta["monthly_values"], f"Monthly file row-count mismatch: {key}")
            monthly = [r for r in all_rows if r["location_id"] == location]
            check(all((r["source_id"], r["member_id"], r["experiment_id"], r["variable_id"], r["units"])
                      == (model, member, experiment, "siconc", "percent") for r in monthly),
                  f"Monthly file identity/unit mismatch: {key}")
            expected_years = [year for low, high in spans for year in range(low, high + 1)]
            check(len(monthly) == meta["requested_months"] == 4 * len(expected_years),
                  f"Monthly count mismatch: {key}")
            annual_by_experiment[experiment] = annual_means(monthly, "value", expected_years, str(key))
            source_rows.append(dict(model=model, member=member, scenario=experiment,
                location_id=location, site_id="GOPT", grid_label=grid["grid_label"],
                grid_cell_id=grid["grid_cell_id"], site_latitude=float(grid["latitude"]),
                site_longitude=float(grid["longitude"]), grid_latitude=float(grid["grid_lat"]),
                grid_longitude=float(grid["grid_lon"]), distance_km=distance,
                independently_recomputed_wgs84_distance_km=independent_distance,
                distance_absolute_difference_km=abs(distance-independent_distance),
                locations_sharing_cell=int(grid["locations_sharing_cell"]),
                mask_strategy=grid["mask_strategy"], source_units=meta["source_units"],
                normalized_units=meta["output_units"], calendar=meta["calendar"],
                version=store["version"], zstore=store["zstore"],
                requested_months=len(monthly), complete_years=len(expected_years),
                months="8;9;10;11", every_year_four_complete_months=True,
                raw_monthly_sic_min=min(float(r["value"]) for r in monthly),
                raw_monthly_sic_max=max(float(r["value"]) for r in monthly),
                source_file=relative_path, sha256=inputs[relative_path]["sha256"],
                original_manifest_hash_match=inputs[relative_path]["original_manifest_hash_match"]))

        historical = fmean(annual_by_experiment["historical"].values())
        offset = baseline - historical
        model_caveats.append(dict(model=model, member=member,
            raw_historical_mean_sic=historical, observed_reference_sic=baseline,
            additive_correction_pp=offset, historical_model_bias_pp=-offset,
            raw_zero_implies_adjusted_sic=offset,
            minimum_possible_delta_given_raw_sic_ge_zero_pp=-historical,
            warning=("BCC raw reference is near zero; subsequent nonnegative SIC can decline by at most "
                     f"{historical:.12g} pp. Additive correction relocates the raw zero floor to "
                     f"{offset:.12g}%. Within-support future years do not validate climatic fidelity."
                     if model == "BCC-CSM2-MR" else
                     "Additive mean correction does not correct variability, distribution, coastal representation, or bounds.")))
        for experiment, spans in PERIODS.items():
            for low, high in spans:
                period = f"{low}-{high}"
                values = {year: annual_by_experiment[experiment][year] for year in range(low, high + 1)}
                check(len(values) == 20, f"Not 20 annual values: {model} {experiment} {period}")
                raw_mean = fmean(values.values())
                corrected = {year: value + offset for year, value in values.items()}
                corrected_mean = fmean(corrected.values())
                mean_delta = raw_mean - historical
                adjusted_future_mean = baseline + mean_delta
                check(abs(corrected_mean - adjusted_future_mean) <= ABS_TOL,
                      f"Annual and mean correction disagree: {model} {experiment} {period}")
                for year, value in values.items():
                    adjusted = corrected[year]
                    row = dict(model=model, member=member, scenario=experiment, period=period,
                        location_id=location, site_id="GOPT", year=year, n_months=4,
                        raw_annual_sic=value, observed_reference_sic=baseline,
                        model_historical_sic=historical, additive_correction_pp=offset,
                        adjusted_annual_sic=adjusted, support_min=SUPPORT[0], support_max=SUPPORT[1],
                        support_class=support_class(adjusted),
                        within_diet_sic_support=support_class(adjusted) == "within",
                        within_physical_percent_range=0 <= adjusted <= 100,
                        raw_annual_at_zero=value == 0, model_cell_distance_km=distance)
                    annual_rows.append(row)
                    if not row["within_physical_percent_range"]:
                        physical_violations.append(row)
                classes = [support_class(value) for value in corrected.values()]
                support_rows.append(dict(model=model, member=member, scenario=experiment, period=period,
                    location_id=location, n_years=20, n_monthly_values=80,
                    raw_mean_sic=raw_mean, raw_annual_sd=stdev(values.values()),
                    additive_correction_pp=offset, adjusted_mean_sic=corrected_mean,
                    adjusted_annual_sd=stdev(corrected.values()),
                    adjusted_annual_min=min(corrected.values()), adjusted_annual_max=max(corrected.values()),
                    support_min=SUPPORT[0], support_max=SUPPORT[1],
                    n_years_within_support=classes.count("within"), n_years_below_support=classes.count("below"),
                    n_years_above_support=classes.count("above"),
                    all_years_within_support=classes.count("within") == 20,
                    mean_within_support=support_class(corrected_mean) == "within",
                    n_years_below_physical_zero=sum(v < 0 for v in corrected.values()),
                    n_years_above_physical_100=sum(v > 100 for v in corrected.values()),
                    n_raw_annual_zero=sum(v == 0 for v in values.values()),
                    years_below_support=";".join(str(y) for y,v in corrected.items() if support_class(v)=="below"),
                    years_above_support=";".join(str(y) for y,v in corrected.items() if support_class(v)=="above")))
                if experiment == "historical":
                    continue
                old = original_by_key[model, member, experiment, period]
                reconstructed = dict(observed_reference_sic=baseline, model_historical_sic=historical,
                    historical_model_bias_pp=-offset, model_future_sic=raw_mean, model_delta_sic_pp=mean_delta,
                    delta_adjusted_sic=adjusted_future_mean, model_cell_distance_km=distance,
                    observed_diet_sic_min=SUPPORT[0], observed_diet_sic_max=SUPPORT[1])
                errors = {field: abs(value - float(old[field])) for field, value in reconstructed.items()}
                row_error = max(errors.values())
                max_comparison_error = max(max_comparison_error, row_error)
                check(row_error <= ABS_TOL and old["location_id"] == location,
                      f"Legacy climate input mismatch: {model} {experiment} {period}")
                within = support_class(adjusted_future_mean) == "within"
                check(within == (old["within_observed_diet_sic_range"].lower() == "true"),
                      f"Legacy mean-support mismatch: {model} {experiment} {period}")
                scenario_rows.append(dict(model=model, member=member, scenario=experiment, period=period,
                    location_id=location, **reconstructed, within_observed_diet_sic_range=within,
                    annual_n_within_support=classes.count("within"), annual_n_below_support=classes.count("below"),
                    annual_n_above_support=classes.count("above"),
                    legacy_delta_adjusted_sic=float(old["delta_adjusted_sic"]),
                    legacy_max_absolute_numeric_difference=row_error, legacy_climatic_fields_match=True))

    check(len(scenario_rows) == 12 and len(annual_rows) == 300 and len(support_rows) == 15,
          "Unexpected output dimensionality")
    observed_rows = [dict(site_id="GOPT", location_id=location, year=year, n_months=4,
                         observed_annual_sic=value, support_min=SUPPORT[0], support_max=SUPPORT[1],
                         support_class=support_class(value)) for year,value in observed_annual.items()]
    out.mkdir(parents=True, exist_ok=True)
    output_tables = {
        "climate_inputs_scenarios.csv": scenario_rows,
        "climate_inputs_annual.csv": annual_rows,
        "climate_inputs_support.csv": support_rows,
        "climate_inputs_observed_annual.csv": observed_rows,
        "climate_inputs_sources.csv": source_rows,
    }
    for name, rows in output_tables.items():
        write_csv(out / name, rows)
    verification = dict(
        status="passed", purpose="Independent climate-input reconstruction and annual predictor-support audit only",
        source_snapshot_git_commit="fcf369b6aaf1e3824e1ae48e6009e6c3b591e7a5",
        implementation="Python standard-library csv/gzip/math/statistics; no original analysis helpers imported",
        script_sha256=sha256(Path(__file__)), comparison_absolute_tolerance_pp=ABS_TOL,
        support_comparison="Closed interval, inclusive; no clipping, no annual exclusions, no extrapolated diet output",
        units="SIC percent; differences and additive correction in percentage points",
        annual_definition="Equal arithmetic weights across August, September, October, November in each complete year",
        reference_definition="Equal arithmetic mean across 80 observed monthly values, equivalently 20 complete annual means, 1995-2014",
        correction="adjusted_annual_sic = raw_annual_sic + observed_reference_mean - model_historical_mean",
        scenario_mean="observed_reference_mean + model_future_mean - model_historical_mean",
        averaging_caveat="CMIP6 seasonal_climatologies.csv uses calendar-day weights. Existing diet_niche_scenarios_v1 uses equal monthly weights; this independent audit reproduces the latter, including its observed reference.",
        site=dict(site_id="GOPT", location_id=location, latitude=float(site["latitude"]), longitude=float(site["longitude"]),
                  observed_spatial_window_km=[0,100], model_support="single native ocean grid cell per model",
                  distance_definition="WGS84 site-to-model-cell displacement, not measured coastline distance"),
        observed_source=dict(product="OSI SAF OSI-450-a1", filename_version="cdr-v3p1",
            unit_evidence="Tracked extraction code explicitly checks ice_conc units == '%' and monthly code averages sic_percent_mean",
            reference_months=80, reference_years=20, reference_complete_supported_days=2440,
            acquisition_manifest_dates_verified=2440, raw_daily_files_reopened=False,
            limitation="Daily acquisition success/hashes and version are checked in retained manifests; original netCDF content is not re-read in this audit"),
        observed_reference_sic=baseline, diet_support=list(SUPPORT),
        observed_reference_annual=dict(n_years=20,n_within_support=sum(r["support_class"]=="within" for r in observed_rows),
            n_below_support=sum(r["support_class"]=="below" for r in observed_rows),
            n_above_support=sum(r["support_class"]=="above" for r in observed_rows),
            annual_min=min(observed_annual.values()),annual_max=max(observed_annual.values()),
            years_above_support=[r["year"] for r in observed_rows if r["support_class"]=="above"]),
        checks=dict(original_manifest_hashes_matched=11,selected_model_members=3,source_versions_units_verified=9,
            complete_four_month_years_model=300,complete_twenty_year_model_periods=15,scenario_climate_inputs_matched=12,
            scenario_climate_max_absolute_difference_pp=max_comparison_error,
            supported_scenario_means=sum(r["within_observed_diet_sic_range"] for r in scenario_rows),
            future_periods_with_all_annual_values_supported=sum(r["all_years_within_support"] for r in support_rows if r["scenario"]!="historical"),
            model_cell_distances_independently_recomputed_wgs84=3,all_output_csv_lf=True),
        model_bias_and_floor_caveats=model_caveats,
        additive_correction_physical_range_violations=physical_violations,
        limitations=[
            "Predictor support is a gate for the observed SIC association; it does not establish future ecological or climatic validity.",
            "Annual within-support counts are labeled scenario/model diagnostics, not probabilities; simulated years are not paired observed years.",
            "All three availability-selected models and their designated members are retained without response-dependent exclusion or ensemble probabilities.",
            "The constant correction changes the mean only; it leaves model variability and raw-zero floors intact and can exceed physical bounds.",
            "Observed 0-100 km regional exposure and a native model grid cell have different spatial support; distance does not correct coastal representation.",
            "Historical/future version, grid, member and unit provenance is verified against retained files and metadata, without a new remote source validation.",
            "No new annual or future-mean diet response is calculated by this script.",
        ],
        input_hashes=[inputs[name] for name in sorted(inputs)],
        output_csv_hashes=[dict(file=name,rows=len(rows),sha256=sha256(out/name)) for name,rows in output_tables.items()],
    )
    with (out/"climate_inputs_verification.json").open("w",encoding="utf-8",newline="\n") as handle:
        json.dump(verification,handle,indent=2,ensure_ascii=False,allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status":verification["status"],"observed_reference_sic":baseline,**verification["checks"]},indent=2))
    print("model,scenario,period,n_within,n_below,n_above,adjusted_mean")
    for r in support_rows:
        print(f"{r['model']},{r['scenario']},{r['period']},{r['n_years_within_support']},"
              f"{r['n_years_below_support']},{r['n_years_above_support']},{r['adjusted_mean_sic']:.12g}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument("--out",type=Path)
    args = parser.parse_args()
    project_root = args.root.resolve()
    output = args.out or project_root/"outputs/signy_component_scenarios_v1/independent"
    main(project_root,output.resolve())
