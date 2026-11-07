"""Climate-only year-to-year SIC covariance under CMIP6 at fixed 39 Adélie source sites.

Original pinned model monthly CSV.gz, no reanalysis or re-retrieval. This is a 20y
within-period projection of MODEL environmental cofluctuation only. Biological
insurance, demography and future mortality are not estimated.

python research/climate-penguin/work/seaice_future_covariance_v1/build.py --check-receipt
"""
from __future__ import annotations
import argparse
import calendar
import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[2]
IN = ROOT / "outputs"
OUT = IN / "seaice_future_covariance_v1"

# Every original data file is a fixed Git blob (compressed bytes, not decompressed CSV).
PINNED = {
    "history": ("historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv", "db58938630e80d22ba445600ce1ad3f554c452e2"),
    "counts": ("comparison_audit/mapppd_unambiguous_site_seasons.csv", "fc134e364cf38699fa7611d7dee5fbbbcb370c0a"),
    "locations": ("climate_penguin/daily_ice_locations.csv", "1c5214ab355d3d2e19bc33e5de4693fa21f38731"),
    "observed": ("climate_penguin/macro_monthly_seaice_1991_2020.csv", "4fcea71c2d8b1069b6ad143f6522061ed434daf5"),
    "climatology": ("cmip6_projection_v1/seasonal_climatologies.csv", "2a794a27fbd6460f7efc78cf09d5d3e98d38fd45"),
    "metadata": ("cmip6_projection_v1/source_metadata.json", "22797d76a0e9515904d9ac6bfd98f8cadab32e94"),
}
MODELS = {
    "ACCESS-CM2": {"member": "r1i1p1f1", "calendar": "proleptic_gregorian"},
    "BCC-CSM2-MR": {"member": "r1i1p1f1", "calendar": "noleap"},
    "CESM2": {"member": "r4i1p1f1", "calendar": "noleap"},
}
for model, entry in MODELS.items():
    for experiment, sha in {
        "ACCESS-CM2": {"historical": "ebf6639f8d45dc832b8542c352594ac191bef3d2", "ssp245": "7b0d584498d71dfe9dd291654fc90d69ce282063", "ssp585": "11e519af8ff2dde864a8d5439a96bd48b2c5ab6e"},
        "BCC-CSM2-MR": {"historical": "549dc1ddc9b709d3c1c79ddc5d313fb344186274", "ssp245": "6226616be2908683b2467c8f39f6f3ff7b96ab3c", "ssp585": "f1cd2afc13f49a273ed9f2a7fd6056f03931464a"},
        "CESM2": {"historical": "f6a048e2c04996997b44f8287079442f390160fc", "ssp245": "efe09a7c558301cdbe9d6aa91f9b52af7a00f61c", "ssp585": "b2e3344662ed7b3fc87dda7d719387f7277ff2b2"}
    }[model].items():
        PINNED[model + "_" + experiment] = (
            f"cmip6_projection_v1/monthly_{model}_{entry['member']}_siconc_{experiment}.csv.gz",
            sha,
        )

def csv_read(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def csv_write(path, records):
    if not records:
        raise RuntimeError("Empty source result " + str(path))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

def close(actual, wanted, label, tol=1e-8):
    if not math.isfinite(actual) or abs(actual - wanted) > tol:
        raise ValueError(f"Source validation failure {label}: observed {actual}, expected {wanted}")

def weighted_average(series, weights):
    return sum(x * w for x, w in zip(series, weights)) / sum(weights)

def sample_std(values):
    return stdev(values) if len(values) > 1 else 0.0

def detrended(values):
    n = len(values)
    mx = (n - 1) / 2.0
    my = mean(values)
    slope = sum((i - mx) * (v - my) for i, v in enumerate(values)) / sum((i - mx)**2 for i in range(n))
    return [values[i] - (my + slope * (i - mx)) for i in range(n)]

def get_stats(site_annual, sites, region_weights, grid_for_site, min_sd, mode, detrend):
    # The same site set is used within a paired historic/future comparison.
    if not sites:
        return None
    if mode == "equal_sites":
        weights = {s: 1.0 for s in sites}
    elif mode == "latest_counts":
        weights = {s: SITE[s]["latest_count"] for s in sites}
    elif mode == "same_method_counts":
        weights = {s: SITE[s]["same_method_count"] for s in sites}
    elif mode == "region_fixed_total":
        nby = {r: sum(SITE[s]["region"] == r for s in sites) for r in set(SITE[s]["region"] for s in sites)}
        weights = {s: region_weights[SITE[s]["region"]]/nby[SITE[s]["region"]] for s in sites}
    elif mode == "exclude_crozier":
        selected = [s for s in sites if s not in {"CRZE","CRZW"}]
        weights = {s: SITE[s]["latest_count"] for s in selected}
    elif mode == "equal_native_model_cells":
        group = defaultdict(list)
        for s in sites:
            group[grid_for_site[s]].append(s)
        weights = {s: 1.0/len(group[grid_for_site[s]]) for s in sites}
    else:
        raise ValueError("Bad weights mode")
    working = sorted(weights)
    if len(working) < 3:
        return None
    common_years = len(next(iter(site_annual.values())))
    raw = [weighted_average([site_annual[s][t] for s in working], [weights[s] for s in working])
           for t in range(common_years)]
    norm, detrend_excluded = {}, []
    for s in working:
        v = site_annual[s]
        if detrend:
            v = detrended(v)
        sigma = sample_std(v)
        if sigma <= 1e-8:
            detrend_excluded.append(s)
            continue
        norm[s] = [(x - mean(v)) / sigma for x in v]
    active = sorted(norm)
    if len(active) < 3:
        return None
    z = [weighted_average([norm[s][t] for s in active], [weights[s] for s in active])
         for t in range(common_years)]
    original_weight_sum = sum(SITE[x]["latest_count"] for x in SITE)
    represented = sum(SITE[s]["latest_count"] for s in working) / original_weight_sum * 100
    model_cell_weights = defaultdict(float)
    for s in working:
        model_cell_weights[grid_for_site[s]] += weights[s]
    denom = sum(model_cell_weights.values())
    effective_cells = denom**2 / sum(x*x for x in model_cell_weights.values())
    return {
        "n_sites_used": len(working),
        "n_model_cells_used": len(model_cell_weights),
        "effective_weighted_native_model_cells": effective_cells,
        "original_latest_count_weight_coverage_pct": represented,
        "standardized_valid_sites": len(active),
        "detrended_zero_variation_excluded": ";".join(detrend_excluded),
        "annual_mean_raw_sic_pct": mean(raw),
        "raw_weighted_mean_SIC_annual_SD_pp": sample_std(raw),
        "site_standardized_common_anomaly_SD": sample_std(z),
        "n_years": common_years,
        "annual_raw_SIC": raw,
        "annual_z": z,
    }

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    expected_path = OUT / "expected_receipt.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    source_bytes = {}
    for key, (rel, target) in PINNED.items():
        path = IN / rel
        content = path.read_bytes()
        sha = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if sha != target or expected["input_git_blobs"][key] != sha:
            raise ValueError(f"Original Git content changed {key}: {sha}")
        source_bytes[key] = content
    history = csv_read(IN / PINNED["history"][0])
    counts = csv_read(IN / PINNED["counts"][0])
    locations = csv_read(IN / PINNED["locations"][0])
    clim = csv_read(IN / PINNED["climatology"][0])
    metadata = json.loads(source_bytes["metadata"])
    observed = csv_read(IN / PINNED["observed"][0])
    if len(history) != 39 or len(counts) != 2999 or len(observed) != 9600 or len(clim) != 4770:
        raise ValueError("Original source cohort sizes changed")
    source_ids = {x["site_id"] for x in history}
    geo = {x["site_id"]:x for x in history}
    coords = {x["site_id"]:x for x in locations if x["cohort"] == "macro_40" and x["site_id"] in source_ids}
    if len(coords) != 39 or len(source_ids) != 39:
        raise ValueError("39 source breeding sites not recovered")
    by_counts = defaultdict(list)
    for x in counts:
        if x["site_id"] not in source_ids or x["species_id"] != "ADPE":
            continue
        if not x["count"] or not math.isfinite(float(x["count"])) or float(x["count"]) < 0:
            continue
        by_counts[x["site_id"]].append(x)
    global SITE
    SITE = {}
    for site in source_ids:
        ordered = sorted(by_counts[site], key=lambda z: int(z["season"]), reverse=True)
        if not ordered:
            raise ValueError("Missing source count " + site)
        matched = next((x for x in ordered if x["method"] == geo[site]["method"]), None)
        if matched is None:
            raise ValueError("Missing same-method source count " + site)
        SITE[site] = {
            "region":geo[site]["region"],
            "location_id":coords[site]["location_id"],
            "latest_count":float(ordered[0]["count"]),
            "same_method_count":float(matched["count"]),
        }
    source_weight = sum(x["latest_count"] for x in SITE.values())
    if source_weight != 1074279 or len(SITE) != 39:
        raise ValueError("Source count denominator drift")
    region_weight = defaultdict(float)
    for s in SITE:
        region_weight[SITE[s]["region"]] += SITE[s]["latest_count"]
    meta = {(m["source_id"],m["experiment_id"]):m for m in metadata if m["variable_id"]=="siconc"}
    check = {(x["source_id"],x["experiment_id"],x["period"],x["location_id"]):x for x in clim
        if x["variable_id"] == "siconc" and x["cohort"] == "macro_40" and x["site_id"] in source_ids}
    source_years = {("historical","1995-2014"):range(1995,2015)}
    for exp in ("ssp245","ssp585"):
        source_years[(exp,"2041-2060")] = range(2041,2061)
        source_years[(exp,"2081-2100")] = range(2081,2101)
    mapped_model = {}
    seasonal_site = []
    annual_output = []
    max_clim_mean_err = 0.0
    max_clim_sd_err = 0.0
    for model in MODELS:
        for exp in ("historical","ssp245","ssp585"):
            m = meta.get((model,exp))
            if not m or m["calendar"] != MODELS[model]["calendar"] or m["output_units"] != "percent":
                raise ValueError("CMIP6 calendar/unit metadata changed")
            raw = source_bytes[model+"_"+exp]
            read = list(csv.DictReader(gzip.decompress(raw).decode("utf-8").splitlines()))
            by_id = defaultdict(lambda:defaultdict(dict))
            target_loc = {x["location_id"] for x in SITE.values()}
            for x in read:
                if x["location_id"] not in target_loc:
                    continue
                if x["source_id"]!=model or x["experiment_id"]!=exp or x["units"]!="percent" or x["variable_id"]!="siconc":
                    raise ValueError("Monthly original source labels changed")
                year, month = int(x["year"]),int(x["month"])
                if month not in (8,9,10,11) or not 0 <= float(x["value"]) <= 100:
                    raise ValueError("Original month or physical SIC out of bounds")
                if month in by_id[x["location_id"]][year]:
                    raise ValueError("Duplicate monthly source site/year/month")
                by_id[x["location_id"]][year][month] = float(x["value"])
            for (period_exp,period),years in source_years.items():
                if period_exp!=exp:
                    continue
                by_site = {}
                cells = {}
                for s in sorted(SITE):
                    loc = SITE[s]["location_id"]
                    seasonal = []
                    for year in years:
                        x = by_id[loc].get(year)
                        if not x or sorted(x) != [8,9,10,11]:
                            raise ValueError(f"Missing seasonal original site/month {model}/{exp}/{s}/{year}")
                        days = {mo:calendar.monthrange(year,mo)[1] for mo in (8,9,10,11)}
                        sic = sum(x[mo]*days[mo] for mo in days)/sum(days.values())
                        seasonal.append(sic)
                        annual_output.append({"source_id":model,"experiment_id":exp,"period":period,
                            "year":year,"site_id":s,"location_id":loc,"native_model_siconc_pct":sic,
                            "region":SITE[s]["region"],"latest_recorded_count":SITE[s]["latest_count"]})
                    entry = check.get((model,exp,period,loc))
                    if entry is None or int(entry["complete_years"])!=20:
                        raise ValueError("Missing original source seasonal-climatology receipt")
                    meanerr = abs(mean(seasonal)-float(entry["seasonal_mean"]))
                    sderr = abs(sample_std(seasonal)-float(entry["annual_sd"]))
                    max_clim_mean_err = max(max_clim_mean_err,meanerr)
                    max_clim_sd_err = max(max_clim_sd_err,sderr)
                    close(meanerr,0.0,"original seasonal mean",tol=1e-8)
                    close(sderr,0.0,"original seasonal SD",tol=1e-8)
                    by_site[s]=seasonal
                    cells[s]=entry["grid_cell_id"]
                    seasonal_site.append({"source_id":model,"experiment_id":exp,"period":period,"site_id":s,
                        "observed_region":SITE[s]["region"],
                        "latest_recorded_count":SITE[s]["latest_count"],
                        "original_source_model_cell":cells[s],
                        "model_cell_distance_km":float(entry["distance_km"]),
                        "mean_model_SIC_pct":mean(seasonal),
                        "annual_SD_model_SIC_pp":sample_std(seasonal),
                        "annual_detrended_residual_SD_pp":sample_std(detrended(seasonal))})
                mapped_model[(model,exp,period)]={"annual":by_site,"cells":cells}
    if len(annual_output)!=3*5*39*20 or len(seasonal_site)!=3*5*39:
        raise ValueError("Original monthly source joined output count unexpected")
    observedYear=defaultdict(lambda:defaultdict(dict))
    for x in observed:
        if x["site_id"] not in SITE or x["inner_km"]!="0" or x["complete_month"]!="True":
            continue
        year, month=int(x["year"]),int(x["month"])
        if year in range(1995,2015) and month in (8,9,10,11):
            observedYear[x["site_id"]][year][month]=float(x["sic_mean"])
    observedSIC={}
    for s in SITE:
        v=[]
        for year in range(1995,2015):
            months=observedYear[s][year]
            if sorted(months)!=[8,9,10,11]:
                raise ValueError("Missing original satellite observed seasonal record")
            v.append(mean(list(months.values()))) # original observed source arithmetic 4-month mean.
        observedSIC[s]=v
    MODE = ("equal_sites","latest_counts","same_method_counts","region_fixed_total","exclude_crozier","equal_native_model_cells")
    thresholds = [0.1,0.5,1.0]
    paired = []
    timeSeries = []
    observedSummary=[]
    for mode in ("equal_sites","latest_counts","region_fixed_total","exclude_crozier"):
        dummyCells={x:x for x in SITE}
        observedStat=get_stats(observedSIC,sorted(SITE),region_weight,dummyCells,0.0,mode,False)
        observedSummary.append({
            "source":"OSI_SAF_satellite","period":"1995-2014","season":"Aug-Nov",
            "mode":mode,"n_sites":observedStat["n_sites_used"],
            "raw_annual_SIC_SD_pp":observedStat["raw_weighted_mean_SIC_annual_SD_pp"],
            "standardized_common_anomaly_SD":observedStat["site_standardized_common_anomaly_SD"],
        })
    for model in MODELS:
        h=mapped_model[(model,"historical","1995-2014")]
        for exp in ("ssp245","ssp585"):
            for period in ("2041-2060","2081-2100"):
                f=mapped_model[(model,exp,period)]
                if h["cells"]!=f["cells"]:
                    raise ValueError("Climate model source marine cell changed across time")
                for threshold in thresholds:
                    included=[s for s in sorted(SITE) if
                        sample_std(h["annual"][s])>=threshold and sample_std(f["annual"][s])>=threshold]
                    if not included:
                        raise ValueError("No paired original biological sites with non-constant climate")
                    for mode in MODE:
                        for detrend in (False,True):
                            old=get_stats(h["annual"],included,region_weight,h["cells"],threshold,mode,detrend)
                            new=get_stats(f["annual"],included,region_weight,f["cells"],threshold,mode,detrend)
                            if old is None or new is None:
                                continue
                            if old["n_sites_used"]!=new["n_sites_used"]:
                                raise ValueError("Inconsistent spatial support paired model periods")
                            paired.append({
                                "model":model,"scenario":exp,"future_period":period,
                                "historical_period":"1995-2014","min_both_periods_native_annual_SIC_SD_pp":threshold,
                                "weight_mode":mode,"remove_period_linear_trend":detrend,
                                "paired_original_sites":old["n_sites_used"],
                                "paired_distinct_native_model_cells":old["n_model_cells_used"],
                                "source_census_mass_coverage_pct":old["original_latest_count_weight_coverage_pct"],
                                "effective_native_model_cells_by_weights":old["effective_weighted_native_model_cells"],
                                "history_mean_SIC_pct":old["annual_mean_raw_sic_pct"],
                                "future_mean_SIC_pct":new["annual_mean_raw_sic_pct"],
                                "model_mean_SIC_change_pp":new["annual_mean_raw_sic_pct"]-old["annual_mean_raw_sic_pct"],
                                "historic_portfolio_annual_raw_SIC_SD_pp":old["raw_weighted_mean_SIC_annual_SD_pp"],
                                "future_portfolio_annual_raw_SIC_SD_pp":new["raw_weighted_mean_SIC_annual_SD_pp"],
                                "future_minus_historic_raw_annual_SD_pp":new["raw_weighted_mean_SIC_annual_SD_pp"]-old["raw_weighted_mean_SIC_annual_SD_pp"],
                                "historic_standardized_common_SIC_anomaly_SD":old["site_standardized_common_anomaly_SD"],
                                "future_standardized_common_SIC_anomaly_SD":new["site_standardized_common_anomaly_SD"],
                                "future_minus_historic_standardized_common_anomaly_SD":new["site_standardized_common_anomaly_SD"]-old["site_standardized_common_anomaly_SD"],
                                "history_valid_standardized_sites":old["standardized_valid_sites"],
                                "future_valid_standardized_sites":new["standardized_valid_sites"],
                                "history_detrended_zero_variation_sites":old["detrended_zero_variation_excluded"],
                                "future_detrended_zero_variation_sites":new["detrended_zero_variation_excluded"],
                                "environment_not_demographic_forecast":True,
                            })
                            if threshold==0.5 and mode in ("equal_sites","latest_counts") and not detrend:
                                for label,result,years in (
                                    ("historical",old,list(range(1995,2015))),
                                    ("future",new,list(range(int(period[:4]),int(period[-4:])+1)))
                                ):
                                    for i,year in enumerate(years):
                                        timeSeries.append({"model":model,"scenario":exp,"period":period,
                                            "time_type":label,"year":year,"weight_mode":mode,
                                            "paired_support_sites":old["n_sites_used"],
                                            "portfolio_SIC_pct":result["annual_raw_SIC"][i],
                                            "portfolio_standardized_anomaly":result["annual_z"][i]})
    # Prevent a misleading model comparison from using *different* sets of source breeding codes.
    # This is a second comparison: intersect all three models' paired historical/future
    # non-constant SIC support, and optionally restrict each model's nearest marine cell
    # distance and historical absolute model-versus-satellite SIC mismatch.
    common_three_model_matched_site_cohort = []
    common_three_model_portfolio = []
    common_masks = [
        ("all_model_var", None, None),
        ("all_model_var_and_50km", 50.0, None),
        ("all_model_var_50km_bias15pp", 50.0, 15.0),
    ]
    for experiment in ("ssp245","ssp585"):
        for period in ("2041-2060","2081-2100"):
            for minSD in thresholds:
                for name,max_distance,max_bias in common_masks:
                    shared=[]
                    for site in sorted(SITE):
                        compatible=True
                        for model in MODELS:
                            old=mapped_model[(model,"historical","1995-2014")]
                            future=mapped_model[(model,experiment,period)]
                            if sample_std(old["annual"][site])<minSD or sample_std(future["annual"][site])<minSD:
                                compatible=False
                                break
                            record=check[(model,"historical","1995-2014",SITE[site]["location_id"])]
                            if max_distance is not None and float(record["distance_km"])>max_distance:
                                compatible=False
                                break
                            historical_observed_bias=abs(float(record["seasonal_mean"])-mean(observedSIC[site]))
                            if max_bias is not None and historical_observed_bias>max_bias:
                                compatible=False
                                break
                        if compatible:
                            shared.append(site)
                    supported_count=sum(SITE[s]["latest_count"] for s in shared)
                    common_three_model_matched_site_cohort.append({
                        "scenario":experiment,"future_period":period,"minimum_paired_annual_site_SIC_SD_pp":minSD,
                        "support_mask":name,"n_common_breeding_site_codes":len(shared),
                        "original_latest_count_weight_coverage_pct":100*supported_count/source_weight,
                        "source_site_codes":";".join(shared),
                        "minimum_source_breeding_sites_for_covariance":3,
                        "no_demographic_forecast":True,
                    })
                    if len(shared)<3:
                        continue
                    for model in MODELS:
                        old=mapped_model[(model,"historical","1995-2014")]
                        future=mapped_model[(model,experiment,period)]
                        for mode in ("equal_sites","latest_counts","region_fixed_total",
                                     "exclude_crozier","equal_native_model_cells"):
                            for detrend in (False,True):
                                a=get_stats(old["annual"],shared,region_weight,old["cells"],minSD,mode,detrend)
                                b=get_stats(future["annual"],shared,region_weight,future["cells"],minSD,mode,detrend)
                                if a is None or b is None:
                                    continue
                                if a["n_sites_used"]!=b["n_sites_used"]:
                                    raise ValueError("Inconsistent identical three-model source cohort within periods")
                                common_three_model_portfolio.append({
                                    "scenario":experiment,"future_period":period,
                                    "minimum_paired_site_SIC_annual_SD_pp":minSD,
                                    "source_support_mask":name,"model":model,"weight_mode":mode,
                                    "linear_detrending":detrend,
                                    "three_model_common_site_cohort_size":len(shared),
                                    "paired_sites_after_weight_mode":a["n_sites_used"],
                                    "original_census_mass_coverage_pct":a["original_latest_count_weight_coverage_pct"],
                                    "native_model_cells":a["n_model_cells_used"],
                                    "effective_weighted_native_model_cells":a["effective_weighted_native_model_cells"],
                                    "historical_raw_annual_SD_pp":a["raw_weighted_mean_SIC_annual_SD_pp"],
                                    "future_raw_annual_SD_pp":b["raw_weighted_mean_SIC_annual_SD_pp"],
                                    "historical_common_standardized_anomaly_SD":a["site_standardized_common_anomaly_SD"],
                                    "future_common_standardized_anomaly_SD":b["site_standardized_common_anomaly_SD"],
                                    "future_minus_historical_standardized_SD":
                                      b["site_standardized_common_anomaly_SD"]-a["site_standardized_common_anomaly_SD"],
                                    "environment_not_demographic_future":True,
                                })
    csv_write(OUT/"common_three_model_matched_breeding_site_support.csv",
              common_three_model_matched_site_cohort)
    csv_write(OUT/"common_three_model_source_cohort_future_covariance.csv",
              common_three_model_portfolio)

    if len(paired)<180 or len(timeSeries)==0:
        raise ValueError("Missing sufficient original climate ensemble source support")
    numericalFacts={
        "original_historical_sites":len(SITE),"models":len(MODELS),
        "historical_future_source_site_years":len(annual_output),
        "original_annual_site_periods":len(seasonal_site),
        "max_recomputed_seasonal_source_climatology_error":max_clim_mean_err,
        "max_recomputed_seasonal_source_annualSD_error":max_clim_sd_err,
        "paired_model_future_weight_mode_comparisons":len(paired),
        "observed_same_year_20y_site_count":len(observedSIC),
    }
    if args.check_receipt:
        for key,want in expected["structural_facts"].items():
            close(float(numericalFacts[key]),float(want),key)
    for r in paired:
        if r["historic_standardized_common_SIC_anomaly_SD"]>1.00000001 or r["future_standardized_common_SIC_anomaly_SD"]>1.00000001:
            raise ValueError("Standardized annual covariance exceeds mathematical bound")
    csv_write(OUT/"model_native_20yr_annual_SIC_by_site.csv",annual_output)
    csv_write(OUT/"model_original_site_annual_sic_variability.csv",seasonal_site)
    csv_write(OUT/"historic_vs_future_SIC_covariance_by_weights.csv",paired)
    csv_write(OUT/"original_observed_satellite_1995_2014_portfolios.csv",observedSummary)
    csv_write(OUT/"paired_annual_model_portfolio_series.csv",timeSeries)
    focal=[x for x in paired if x["min_both_periods_native_annual_SIC_SD_pp"]==0.5 and not x["remove_period_linear_trend"]]
    trend=[x for x in paired if x["min_both_periods_native_annual_SIC_SD_pp"]==0.5 and x["remove_period_linear_trend"]]
    def brief(row):
        return {
            "model":row["model"],"scenario":row["scenario"],"future_period":row["future_period"],
            "weight_mode":row["weight_mode"],
            "paired_sites":row["paired_original_sites"],
            "paired_cells":row["paired_distinct_native_model_cells"],
            "count_weight_coverage_pct":row["source_census_mass_coverage_pct"],
            "old_raw_SD":row["historic_portfolio_annual_raw_SIC_SD_pp"],
            "future_raw_SD":row["future_portfolio_annual_raw_SIC_SD_pp"],
            "old_z_SD":row["historic_standardized_common_SIC_anomaly_SD"],
            "future_z_SD":row["future_standardized_common_SIC_anomaly_SD"],
            "delta_z_SD":row["future_minus_historic_standardized_common_anomaly_SD"],
        }
    result={
       "version":1,"status":"original_CMIP6_monthly_future_annual_environment_coherence_not_penguin_demographic_prediction",
       "input_git_blobs":expected["input_git_blobs"],
       "source_recalculation":numericalFacts,
       "observed_20yr_same_site_satellite_baseline":observedSummary,
       "main_model_results":list(map(brief,focal)),
       "detrended_sensitivity":list(map(brief,trend)),
       "common_three_model_matched_source_sites":common_three_model_matched_site_cohort,
       "common_three_model_future_covariance":common_three_model_portfolio,

       "boundary":"CMIP6 3 models, one member each, 20 years per period; source sites are repeated over native model marine cells; standardization drops sites with small model variability and pairs support within each model; changed future covariance is not future nesting synchrony or risk probability."
    }
    (OUT/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"validation.json").write_text(json.dumps({"original_git_blobs_checked":True,
         "original_model_summary_mean_and_SD_crosscheck":True,
         "record_counts":numericalFacts,
         "strict_structure_receipt_verified":args.check_receipt,
         "does_not_estimate_population_synchrony":True},indent=2)+"\n",encoding="utf-8")
    print("PENGUIN FUTURE MODEL SIC COVARIANCE "+json.dumps({
        "structural":numericalFacts,
        "observed":observedSummary,
        "scenario_results":[x for x in map(brief,focal) if x["scenario"]=="ssp585" and x["future_period"]=="2081-2100"],
        "detrended":[x for x in map(brief,trend) if x["scenario"]=="ssp585" and x["future_period"]=="2081-2100" and x["weight_mode"] in ("equal_sites","latest_counts")],
        "selected_threshold_variation":[brief(x) for x in paired if x["scenario"]=="ssp585" and x["future_period"]=="2081-2100" and x["weight_mode"]=="latest_counts" and not x["remove_period_linear_trend"]],
        "common_allmodels_SSP585_late_0_5": [x for x in common_three_model_portfolio if
            x["scenario"]=="ssp585" and x["future_period"]=="2081-2100"
            and x["minimum_paired_site_SIC_annual_SD_pp"]==0.5 and
            x["source_support_mask"]=="all_model_var" and not x["linear_detrending"]
            and x["weight_mode"] in ("equal_sites","latest_counts","exclude_crozier")],
        "common_support_SSP585_late_0_5":[x for x in common_three_model_matched_site_cohort if
            x["scenario"]=="ssp585" and x["future_period"]=="2081-2100"
            and x["minimum_paired_annual_site_SIC_SD_pp"]==0.5],
        "common_climate_sensitivity":[x for x in common_three_model_portfolio if
            x["scenario"]=="ssp585" and x["future_period"]=="2081-2100"
            and x["weight_mode"]=="latest_counts"
            and x["source_support_mask"] in ("all_model_var","all_model_var_50km_bias15pp")
            and x["minimum_paired_site_SIC_annual_SD_pp"] in (0.1,0.5,1.0)],
        "verified":args.check_receipt
     },ensure_ascii=False),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check-receipt",action="store_true")
    main_args=parser.parse_args()
    args=main_args
    main()
