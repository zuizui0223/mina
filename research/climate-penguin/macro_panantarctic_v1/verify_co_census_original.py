#!/usr/bin/env python3
"""Independent audit of 3-pair original co-census ecological niche comparisons.

Does NOT fit a new model or select results. Recomputes true original count
ratios, exact-year original 25km ice, unique-site means and broad-region
centered Pearson correlations from two source files, without importing any
estimation function from co_census_three_pair_niche.py.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"cocensus_niche_outputs"
PAIRS=[("ADPE","GEPE"),("ADPE","CHPE"),("CHPE","GEPE")]

def read(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def average(values):
    return sum(values)/len(values)
def pearson(a,b):
    if len(a)<4 or len(a)!=len(b):
        return None
    x=average(a);y=average(b)
    p=sum((v-x)*(w-y) for v,w in zip(a,b))
    s=sum((v-x)**2 for v in a);t=sum((w-y)**2 for w in b)
    if min(s,t)<1e-18:return None
    return p/math.sqrt(s*t)
def approx(a,b):
    return a is not None and b is not None and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-10)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--full-ice-csv",type=Path,required=True)
    ap.add_argument("--full-ice-summary",type=Path,required=True)
    arg=ap.parse_args()
    original=read(ROOT/"outputs/observed_multi_species_same_year_303.csv")
    archive=read(arg.full_ice_csv)
    data=read(OUT/"original_cocensused_3species_pairs_1991_2020.csv")
    sites=read(OUT/"original_pair_site_mean_environment_and_nest_ratio.csv")
    result=json.loads((OUT/"three_species_cocensus_niche_summary.json").read_text())
    receipt=json.loads(arg.full_ice_summary.read_text())
    if len(original)!=303 or len(data)!=357 or len(sites)!=82 or len(archive)!=71400 or receipt["n_original_source_netCDF_files"]!=120:
        raise ValueError("Source or pair observation number has changed")
    annual=defaultdict(dict)
    for row in archive:
        idx=(row["site_id"],int(row["year"]))
        month=int(row["month"])
        if month in annual[idx]:raise ValueError("Duplicate original marine source month")
        if row["source_full_595_site_monthly_support"]!="OK":
            raise ValueError("A recorded co-census year is missing OSI monthly input")
        annual[idx][month]=float(row["source_25km_buffer_mean_SIC_pct"])
    if len(annual)!=595*30 or any(len(a)!=4 for a in annual.values()):
        raise ValueError("Full original marine date source drift")
    original_map={(z["site_id"],int(z["census_season"])):z for z in original}
    if len(original_map)!=303:raise ValueError("Duplicate original same-site/year census")
    bypair=defaultdict(list)
    duplicate=set()
    for z in data:
        pair=z["species_pair"]
        if pair not in [a+"__"+b for a,b in PAIRS]:
            raise ValueError("Unplanned focal species contrast")
        key=(z["site_id"],int(z["census_season"]))
        if (pair,*key) in duplicate:
            raise ValueError("Duplicated observed source pair-year")
        duplicate.add((pair,*key))
        orig=original_map[key]
        a,b=pair.split("__")
        x=orig[a+"_observed_nests"]
        y=orig[b+"_observed_nests"]
        if x=="" or y=="":
            raise ValueError("Missing species turned into false observed absence")
        expected_ratio=math.log1p(float(x))-math.log1p(float(y))
        if not approx(float(z["log1p_first_minus_log1p_second"]),expected_ratio):
            raise ValueError("Published species-count ratio differs from source")
        source_sic=average([annual[key][month] for month in (8,9,10,11)])
        if not approx(float(z["same_year_AugNov_original_SIC_pct"]),source_sic):
            raise ValueError("Species comparison year not matched to actual original annual ice")
        bypair[pair].append(z)
    site_map={(r["species_pair"],r["site_id"]):r for r in sites}
    if len(site_map)!=82:raise ValueError("Source site-only records not unique")
    checked={}
    for first,second in PAIRS:
        pair=first+"__"+second
        orig_rows=bypair[pair]
        bysite=defaultdict(list)
        for z in orig_rows:bysite[z["site_id"]].append(z)
        mean=[]
        for site,group in sorted(bysite.items()):
            m=site_map[pair,site]
            avx=average([float(z["same_year_AugNov_original_SIC_pct"]) for z in group])
            avy=average([float(z["log1p_first_minus_log1p_second"]) for z in group])
            if not approx(avx,float(m["mean_SIC_pct"])) or not approx(avy,float(m["mean_log_nest_ratio"])):
                raise ValueError("Site equal mean is not from original repeated count/ice records")
            if len(group)!=int(m["n_co_census_years"]):
                raise ValueError("Original source repeated years mismatch")
            mean.append({"site":site,"reg":m["source_region"],"x":avx,"y":avy})
        expected=result["pairs_fixed_before_statistical_outcome"][pair]
        if len(mean)!=expected["unique_original_colony_sites"] or len(orig_rows)!=expected["source_same_year_co_census_observations"]:
            raise ValueError("Published region/site pair counts mismatch")
        x=[z["x"] for z in mean];y=[z["y"] for z in mean]
        pool=pearson([float(z["same_year_AugNov_original_SIC_pct"]) for z in orig_rows],
                     [float(z["log1p_first_minus_log1p_second"]) for z in orig_rows])
        siteequal=pearson(x,y)
        regions=defaultdict(list)
        for z in mean:regions[z["reg"]].append(z)
        centered_x=[];centered_y=[]
        for z in mean:
            centered_x.append(z["x"]-average([v["x"] for v in regions[z["reg"]]]))
            centered_y.append(z["y"]-average([v["y"] for v in regions[z["reg"]]]))
        residual=pearson(centered_x,centered_y)
        for calculated,field in ((pool,"pooled_siteyear_r_naive_not_inferential"),
                                 (siteequal,"site_equal_mean_r_geographic"),
                                 (residual,"site_equal_region_demeaned_r")):
            if not approx(calculated,expected[field]):
                raise ValueError("Original independent species-pair geographic correlation mismatch")
        bootstrap=expected["region_demeaned_250km_block_interval"]
        interval=bootstrap.get("95pct_interval")
        if bootstrap["status"]=="DESCRIPTIVE_SPATIAL_BLOCK_INTERVAL_ONLY" and (interval is None or not interval[0]<=0<=interval[1]):
            raise ValueError("Previously published spatial CI inference boundary changed")
        checked[pair]={"n_years":len(orig_rows),"n_sites":len(mean),
                      "pooled_r":pool,"site_equal_r":siteequal,
                      "region_demeaned_r":residual,
                      "block_95pct_interval":interval}
    output={"status":"INDEPENDENT_ORIGINAL_CO_CENSUS_MERGE_AND_RATIOS_VERIFIED",
            "n_source_count_colony_sites":595,"n_original_source_census_siteyears":303,
            "n_original_three_species_pair_observations":len(data),
            "n_original_species_pair_sites":len(sites),
            "n_original_full_30yr_seaice_site_months":len(archive),
            "fixed_all_three_pairs":checked,
            "no_unknown_species_imputed_as_zero":True,
            "caveat":"Second implementation on same underlying sources; spatial-block intervals are still descriptive and not independently biologically replicated."}
    (OUT/"independent_original_source_pair_validation.json").write_text(
        json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("INDEPENDENT_PENGUIN_COCENSUS_ORIGINAL_VALIDATION="+json.dumps(output,ensure_ascii=False))
if __name__=="__main__":
    main()
