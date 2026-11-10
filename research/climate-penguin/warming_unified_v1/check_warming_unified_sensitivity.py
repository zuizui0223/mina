#!/usr/bin/env python3
"""Post-result sensitivity audit for the climate-first penguin manuscript.

Descriptive sensitivity only; neither a new confirmatory climate test nor a
future biological forecast. Runs solely on the three frozen unified tables.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent

def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def require(condition, why):
    if not condition:
        raise ValueError("WARMING_SOURCE_SENSITIVITY: " + why)

def corr(a, b):
    require(len(a) == len(b) and len(a) >= 3, "paired year count")
    x, y = mean(a), mean(b)
    da, db = [v-x for v in a], [v-y for v in b]
    d = math.sqrt(sum(v*v for v in da)*sum(v*v for v in db))
    require(d > 0, "constant variable")
    return sum(v*w for v, w in zip(da, db))/d

def rank(a):
    order = sorted(range(len(a)), key=lambda j: a[j])
    r = [0.0]*len(a)
    i = 0
    while i < len(a):
        j = i+1
        while j < len(a) and a[order[j]] == a[order[i]]:
            j += 1
        for k in range(i, j):
            r[order[k]] = (i+1+j)/2
        i = j
    return r

def detrend(a, years):
    x0, y0 = mean(years), mean(a)
    b = sum((x-x0)*(y-y0) for x, y in zip(years, a))/sum((x-x0)**2 for x in years)
    return [y-y0-b*(x-x0) for x, y in zip(years, a)]

def sensitivity(sic, biological, years):
    n = len(years)
    r = corr(sic, biological)
    shifts = [corr(sic[-k:]+sic[:-k] if k else sic, biological) for k in range(n)]
    z = math.atanh(r)
    return {
        "pearson_r": r,
        "spearman_r_tie_aware": corr(rank(sic), rank(biological)),
        "linear_year_detrended_r": corr(detrend(sic, years), detrend(biological, years)),
        "post_2003_r": corr(sic[2:], biological[2:]),
        "fisher_95_interval_iid_years_only": [
            math.tanh(z-sign*1.96/math.sqrt(n-3)) for sign in (1, -1)],
        "circular_shift_abs_alignment_rank": sum(abs(x) >= abs(r)-1e-12 for x in shifts),
        "circular_shift_total_alignments": n,
        "circular_shift_correlations": shifts,
    }

def main(data_dir, output_dir):
    nine = read_csv(data_dir/"signy_same_year_diet_phenology.csv")
    future = read_csv(data_dir/"six_site_future_physical.csv")
    years = [int(q["year"]) for q in nine]
    require(years == list(range(2001,2010)), "9 common seasons changed")
    require({q["site_id"] for q in nine} == {"SIGNY::GOPT"}, "island changed")
    require(sum(int(q["n_stomachs_adelie"])+int(q["n_stomachs_gentoo"])
                for q in nine) == 422, "stomach cohort changed")
    require([q["adelie_hatching_source_colony"] for q in nine]
            == ["A41"]*2+["A39"]*7, "phenology colony provenance changed")
    sic = [float(q["sic_aug_nov_pct"]) for q in nine]
    fish = [float(q["diet_gap_fish_fraction"]) for q in nine]
    gap = [float(q["hatching_gap_days"]) for q in nine]
    require(abs(corr(sic, fish)-0.7814247513630724)<1e-10, "fish r source changed")
    require(abs(corr(sic, gap)+0.06607505241266795)<1e-10, "hatch r source changed")
    groups = defaultdict(list)
    for q in future:
        groups[(q["experiment"],q["period"])].append(q)
    require(set(groups) == {
        ("ssp245","2041-2060"), ("ssp245","2081-2100"),
        ("ssp585","2041-2060"), ("ssp585","2081-2100")}, "4 future scenarios changed")
    scenarios = []
    for (scenario, period), six in sorted(groups.items()):
        require(len(six)==6 and len({q["site_id"] for q in six})==6, "six source sites")
        marine = [q for q in six if q["source_verified_marine"]=="1"]
        require(len(marine)==4 and {q["site_id"] for q in marine}
                == {"ARDL","BISC","LION","LLAN"}, "marine support")
        require(all(q["SIC_pp_change_mean"]=="" and q["sos_change_native"]==""
                    for q in six if q not in marine), "unverified marine value")
        pixels = defaultdict(list)
        for q in marine:
            pixels[q["marine_fingerprint"]].append(float(q["SIC_pp_change_mean"]))
        require({k:len(v) for k,v in pixels.items()}=={"F018":1,"F030":3},
                "original two repeated ocean cells")
        require(all(max(v)-min(v)<1e-12 for v in pixels.values()),
                "inconsistent values within one original ocean fingerprint")
        site_equal = mean([float(q["SIC_pp_change_mean"]) for q in marine])
        pixel_equal = mean([mean(v) for v in pixels.values()])
        scenarios.append({
            "ssp":scenario, "period":period, "tas_6site_equal_C":mean(
                [float(q["tas_C_change_mean"]) for q in six]),
            "sic_4site_equal_pp":site_equal, "sic_2pixel_equal_pp":pixel_equal,
            "pixel_minus_site_pp":pixel_equal-site_equal,
            "n_original_marine_sites":4, "n_distinct_marine_fingerprints":2,
        })
    result = {
        "status":"POST_RESULT_DESCRIPTIVE_ONLY_NO_FUTURE_BIOLOGICAL_FORECAST",
        "island_climate_years":9, "original_stomachs_not_climate_replicates":422,
        "diet_gentoo_minus_adelie":sensitivity(sic, fish, years),
        "hatching_chinstrap_minus_adelie":sensitivity(sic, gap, years),
        "marine_physical_scenario_weighting":scenarios,
        "warnings":[
            "Different species pairs for diet and hatching, not a within-individual multi-axis test.",
            "With only nine climate years the Fisher interval assumes iid years and is not proof of unchanged hatching gap.",
            "Circular shifts are a coarse alignment sensitivity, not a valid exact p-value for nonstationary climate.",
            "Four sites share only two actual marine grid fingerprints.",
            "No causal warming attribution or future breeding-number forecast."
        ]
    }
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/"WARMING_SENSITIVITY_DIAGNOSTICS_20261107.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=HERE/"data")
    parser.add_argument("--out-dir", type=Path, default=HERE/"outputs")
    args=parser.parse_args()
    result=main(args.data_dir,args.out_dir)
    print(json.dumps({
        "status":result["status"],
        "detrended_diet_ice_r":result["diet_gentoo_minus_adelie"]["linear_year_detrended_r"],
        "ssp585_late_two_grid_sic_pp":result["marine_physical_scenario_weighting"][-1]["sic_2pixel_equal_pp"],
    }))
