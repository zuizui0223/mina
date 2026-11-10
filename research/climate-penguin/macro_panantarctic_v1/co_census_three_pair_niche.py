#!/usr/bin/env python3
"""Three co-censused species pairs: site vs within-site SIC/nest ratios.

Post-result descriptive macro analysis; no pseudoabsences or hidden p-tests.
The full Antarctic original dataset (595 sites) is a biological source frame,
but actual co-censused 2-species rows occupy only a geographic subpanel.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE/"outputs"
OUT=HERE/"cocensus_niche_outputs"
OUT.mkdir(exist_ok=True,parents=True)
PAIRS=(("ADPE","GEPE"),("ADPE","CHPE"),("CHPE","GEPE"))
EXPECTED={("ADPE","GEPE"):(100,25),("ADPE","CHPE"):(89,24),
          ("CHPE","GEPE"):(168,33)}
BOOTSTRAP=2000
SEED=20261110

def read(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def write(path,rows,columns=None):
    if not rows and columns is None:raise ValueError("Empty study output")
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns or list(rows[0]))
        w.writeheader()
        w.writerows(rows)
def corr(x,y):
    a=np.asarray(x,dtype=float)
    b=np.asarray(y,dtype=float)
    if len(a)<4 or np.std(a)<1e-10 or np.std(b)<1e-10:
        return None
    return float(np.corrcoef(a,b)[0,1])
def slope(years,x,y):
    a=np.array(x,dtype=float);b=np.array(y,dtype=float)
    if len(a)<3 or np.ptp(years)<5 or np.std(a)<1e-10:return None
    return float(np.dot(a-a.mean(),b-b.mean())/np.dot(a-a.mean(),a-a.mean()))
def region_corr(sites):
    regions=defaultdict(list)
    for i,z in enumerate(sites):regions[z["region"]].append(i)
    x=np.array([z["mean_SIC_pct"] for z in sites])
    y=np.array([z["mean_log_nest_ratio"] for z in sites])
    for ind in regions.values():
        x[ind]-=x[ind].mean()
        y[ind]-=y[ind].mean()
    return corr(x,y)
def block_boot(sites,pairindex):
    keys=sorted({r["polar_250km_block"] for r in sites})
    if len(keys)<5:
        return {"status":"REGIONAL_BIOLOGICAL_INFERENCE_UNDERPOWERED",
                "n_spatial_blocks":len(keys),"n_valid_reps":0,"95pct_interval":None}
    by=defaultdict(list)
    for r in sites:by[r["polar_250km_block"]].append(r)
    rng=np.random.default_rng(SEED+pairindex)
    allr=[]
    for _ in range(BOOTSTRAP):
        trial=[z for block in rng.choice(keys,size=len(keys),replace=True)
               for z in by[block]]
        r=region_corr(trial)
        if r is not None:allr.append(r)
    valid=len(allr)
    if valid<.75*BOOTSTRAP:
        return {"status":"REGIONAL_BIOLOGICAL_INFERENCE_UNDERPOWERED",
                "n_spatial_blocks":len(keys),"n_valid_reps":valid,
                "95pct_interval":None}
    return {"status":"DESCRIPTIVE_SPATIAL_BLOCK_INTERVAL_ONLY",
            "n_spatial_blocks":len(keys),"n_valid_reps":valid,
            "95pct_interval":[float(np.quantile(allr,.025)),
                              float(np.quantile(allr,.975))]}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--full-ice-csv",required=True,type=Path)
    ap.add_argument("--full-ice-summary",required=True,type=Path)
    args=ap.parse_args()
    macro=json.loads((BASE/"macro_original_coverage.json").read_text())
    if macro["status"]!="PAN_ANTARCTIC_FULL_SOURCE_MACRO_PANEL_SUCCESS":
        raise ValueError("Unverified original full Antarctic survey source")
    sites={z["site_id"]:z for z in read(BASE/"panantarctic_595_site_inventory.csv")}
    cosurvey=read(BASE/"observed_multi_species_same_year_303.csv")
    if len(sites)!=595 or len(cosurvey)!=303:
        raise ValueError("Original pan-Antarctic co-census source drift")
    icemetadata=json.loads(args.full_ice_summary.read_text())
    ice=read(args.full_ice_csv)
    if (len(ice)!=71400 or
        icemetadata["status"]!="PANANTARCTIC_ORIGINAL_30YR_MONTHLY_SIC_MACRO_SOURCE_COMPLETE"):
        raise ValueError("Original 595×120 monthly environmental source incomplete")
    by_month=defaultdict(dict)
    for r in ice:
        site=r["site_id"];year=int(r["year"]);month=int(r["month"])
        if site not in sites or not (1991<=year<=2020) or month not in (8,9,10,11):
            raise ValueError("Unexpected Antarctic source geography/year")
        key=(site,year)
        if month in by_month[key]:raise ValueError("Duplicate native OSI monthly SIC at site")
        if r["source_full_595_site_monthly_support"]=="OK":
            v=float(r["source_25km_buffer_mean_SIC_pct"])
            if not 0<=v<=100:raise ValueError("Nonphysical original SIC")
            by_month[key][month]=v
        else:
            by_month[key][month]=None
    if len(by_month)!=595*30 or any(set(z)!={8,9,10,11} for z in by_month.values()):
        raise ValueError("Full original 30-year ice source keys incomplete")
    sic={(site,year):float(np.mean(list(vals.values())))
         if all(v is not None for v in vals.values()) else None
         for (site,year),vals in by_month.items()}
    actual=[]
    duplicate=set()
    for source in cosurvey:
        year=int(source["census_season"])
        if not 1991<=year<=2020:
            continue
        site=source["site_id"]
        key=(site,year)
        if key in duplicate:raise ValueError("Duplicate original same site-year source")
        duplicate.add(key)
        for a,b in PAIRS:
            a0=source[a+"_observed_nests"];b0=source[b+"_observed_nests"]
            if a0=="" or b0=="":continue
            x=float(a0);y=float(b0)
            if not (math.isfinite(x) and math.isfinite(y) and x>=0 and y>=0
                    and x.is_integer() and y.is_integer()):
                raise ValueError("Original two species observed counts malformed")
            iceval=sic.get(key)
            if iceval is None:raise ValueError("Missing actually co-censused year SIC: "+str(key))
            sit=sites[site]
            if sit["source_region"]!=source["source_region"]:
                raise ValueError("Source species and geo region labels differ")
            actual.append({
                "species_pair":a+"__"+b,
                "site_id":site,"census_season":year,
                "source_region":source["source_region"],
                "polar_250km_block":sit["polar_250km_fixed_grid_block"],
                "first_species":a,"second_species":b,
                "first_observed_nests":int(x),
                "second_observed_nests":int(y),
                "log1p_first_minus_log1p_second":math.log1p(x)-math.log1p(y),
                "same_year_AugNov_original_SIC_pct":iceval,
                "both_species_actually_counted":True,
                "missing_species_count_is_not_zero":True,
                "original_colony_census_methods":source["count_methods_recorded"]
            })
    bypair=defaultdict(list)
    for z in actual:bypair[z["species_pair"]].append(z)
    bysites=[];bytemporal=[];summaries={}
    for pairindex,(a,b) in enumerate(PAIRS):
        pair=a+"__"+b
        data=bypair[pair]
        nsite=len({z["site_id"] for z in data})
        if (len(data),nsite)!=EXPECTED[a,b]:
            raise ValueError(f"Predeclared original {pair} site-years changed: {len(data)}/{nsite}")
        grouped=defaultdict(list)
        for r in data:grouped[r["site_id"]].append(r)
        site_rows=[]
        temp_rows=[]
        for site,records in sorted(grouped.items()):
            r0=records[0]
            years=sorted(int(z["census_season"]) for z in records)
            if len(years)!=len(set(years)):
                raise ValueError("Co-censused source site/year duplicate")
            x=np.array([z["same_year_AugNov_original_SIC_pct"] for z in records])
            y=np.array([z["log1p_first_minus_log1p_second"] for z in records])
            r={
                "species_pair":pair,"site_id":site,
                "source_region":r0["source_region"],
                "polar_250km_block":r0["polar_250km_block"],
                "n_co_census_years":len(records),
                "first_year":min(years),"last_year":max(years),
                "mean_SIC_pct":float(np.mean(x)),
                "mean_log_nest_ratio":float(np.mean(y)),
                "n_observed_co_census_zeros":sum(z["first_observed_nests"]==0 or
                                                z["second_observed_nests"]==0 for z in records)
            }
            site_rows.append(r)
            v=slope(years,x/10.,y)
            eligible=(len(years)>=3 and max(years)-min(years)>=5)
            if eligible:
                temp_rows.append({
                    "species_pair":pair,"site_id":site,
                    "source_region":r0["source_region"],
                    "polar_250km_block":r0["polar_250km_block"],
                    "n_actual_co_census_years":len(years),
                    "year_span":max(years)-min(years),
                    "SIC_range_pp":float(np.ptp(x)),
                    "within_site_change_in_log_ratio_per_10SICpp":v if v is not None else "",
                    "status":"OBSERVED_TEMPORAL_SLOPE" if v is not None else "SIC_NO_VARIATION",
                    "does_not_estimate_dispersal_or_causality":True
                })
        if len(site_rows)!=nsite:raise ValueError("Site collapsing changed source unit")
        bysites.extend(site_rows)
        bytemporal.extend(temp_rows)
        temp_valid=[float(z["within_site_change_in_log_ratio_per_10SICpp"])
                    for z in temp_rows if z["status"]=="OBSERVED_TEMPORAL_SLOPE"]
        region=Counter(z["source_region"] for z in site_rows)
        block=Counter(z["polar_250km_block"] for z in site_rows)
        siteequal_raw=corr([z["mean_SIC_pct"] for z in site_rows],
                           [z["mean_log_nest_ratio"] for z in site_rows])
        desc={
           "source_same_year_co_census_observations":len(data),
           "unique_original_colony_sites":nsite,
           "n_original_regions":len(region),
           "region_counts":dict(sorted(region.items())),
           "n_polar_250km_blocks":len(block),
           "co_census_3plus_year_sites":sum(z["n_co_census_years"]>=3 for z in site_rows),
           "co_census_5plus_year_sites":sum(z["n_co_census_years"]>=5 for z in site_rows),
           "pooled_siteyear_r_naive_not_inferential":corr(
               [z["same_year_AugNov_original_SIC_pct"] for z in data],
               [z["log1p_first_minus_log1p_second"] for z in data]),
           "site_equal_mean_r_geographic":siteequal_raw,
           "site_equal_region_demeaned_r":region_corr(site_rows),
           "region_demeaned_250km_block_interval":block_boot(site_rows,pairindex),
           "site_temporal_slope_3plus_year_5plus_span_candidates":len(temp_rows),
           "site_temporal_slope_valid":len(temp_valid),
           "site_temporal_slope_median_per_10SICpp":float(np.median(temp_valid)) if temp_valid else None,
           "site_temporal_slope_positive":sum(z>0 for z in temp_valid),
           "site_temporal_slope_negative":sum(z<0 for z in temp_valid),
           "site_temporal_slope_unique_250km_blocks":len({z["polar_250km_block"] for z in temp_rows}),
           "not_all_18_regions_represented":True
        }
        summaries[pair]=desc
    write(OUT/"original_cocensused_3species_pairs_1991_2020.csv",actual)
    write(OUT/"original_pair_site_mean_environment_and_nest_ratio.csv",bysites)
    write(OUT/"original_pair_within_site_repeat_year_slopes.csv",bytemporal)
    result={
        "status":"ORIGINAL_ANTARCTIC_CO_CENSUS_SPECIES_NICHE_SPATIAL_AND_TEMPORAL_QA_COMPLETE",
        "source_595_colony_original_count_frame":True,
        "n_original_all_3species_source_sites":595,
        "n_original_all_penguincount_records":2456,
        "n_original_complete_seaice_site_months":71400,
        "co_census_is_a_regional_peninsula_subpanel_not_continental_species_distribution":True,
        "pairs_fixed_before_statistical_outcome":summaries,
        "limits":[
            "Only survey site-years where BOTH species actually counted; missing species is unknown, never imputed ecological absence.",
            "Observed nest ratio is conditional community allocation, not true fraction of all colonies or competitive exclusion.",
            "Three source pairs are a post-result fixed descriptive family, not prospectively independent confirmation.",
            "The majority of observed pairs belong to the western Antarctic Peninsula and surrounding islands.",
            "Region means/site-equal geography and within-site slopes answer different questions, do not interpret pooled r as temporal climate effect.",
            "Repeated site-year pairs share sites and some share source SIC ocean grid cells; no naive per-row p-value.",
            "Small 250km block counts make region-demeaned spatial effects non-generalizable.",
            "Original sighting years are not complete absence/detection surveys and source count definitions may change in effort despite method grouping.",
            "No annual greening, individual movement, physiological prey preference, causality or 2050–2100 future nest probability is identified."
        ]}
    (OUT/"three_species_cocensus_niche_summary.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PANANTARCTIC_COCENSUS_NICHE_VERDICT="+json.dumps(result,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
