#!/usr/bin/env python3
"""Source-only 3-axis overlap audit, not a new SDM or an exploratory p-value search.

Reads the two independently source-hash-pinned panels output by build_source_panels.py.
The 2017-2023 vegetation map is a single STATIC spatial composite, even if the
census on the same site occurred during 2017-2020. No yearly vegetation is imputed.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import csv,json,math
from pathlib import Path

HERE=Path(__file__).resolve().parent
SRC=HERE/"outputs"
OUT=HERE/"joint_support_outputs"
OUT.mkdir(exist_ok=True,parents=True)

def table(file):
    with (SRC/file).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def put(name,arr):
    if not arr:
        raise ValueError("Cannot write an empty support table")
    with (OUT/name).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(arr[0]))
        w.writeheader()
        w.writerows(arr)

def avg(v):
    if not v:raise ValueError("Empty cohort average")
    return sum(v)/len(v)

def corr(a,b):
    if len(a)!=len(b) or len(a)<3:raise ValueError("Invalid correlation population")
    x=avg(a);y=avg(b)
    num=sum((u-x)*(v-y) for u,v in zip(a,b))
    dx=sum((u-x)**2 for u in a);dy=sum((v-y)**2 for v in b)
    if min(dx,dy)<=0:raise ValueError("Environmental variable is constant")
    return num/math.sqrt(dx*dy)

def main():
    source=json.loads((SRC/"source_coverage.json").read_text(encoding="utf-8"))
    marine=table("marine_observed_site_species_year_661.csv")
    mapped=table("contemporary_vegetation_site_species_197.csv")
    if len(marine)!=661 or len(mapped)!=197:
        raise ValueError("Source-pinned input cohorts changed")
    if any(z["one_composite_2017to2023_not_yearly_ndvi"]!="True" for z in mapped):
        raise ValueError("Vegetation source is mislabelled as yearly vegetation")
    mapped_by={(z["site_id"],z["species"]):z for z in mapped}
    if len(mapped_by)!=len(mapped):raise ValueError("Duplicate source vegetation site×species")
    recent=[z for z in marine if 2017<=int(z["year"])<=2020]
    if len(recent)!=70 or len({z["site_id"] for z in recent})!=30:
        raise ValueError("Original contemporary observed-count sampling year support drift")
    joined=[]
    for z in recent:
        key=(z["site_id"],z["species"])
        land=mapped_by.get(key)
        if land is None:continue
        if z["region"]!=land["region"]:
            raise ValueError("Source region codes mismatch at same site")
        if (not math.isclose(float(z["latitude"]),float(land["latitude"]),abs_tol=1e-6) or
            not math.isclose(float(z["longitude"]),float(land["longitude"]),abs_tol=1e-6)):
            raise ValueError("Source site coordinate labels mismatch")
        year=int(z["year"]);area=float(land["static_mapped_vegetation_2km_m2"])
        sic=float(z["sic_AugNov_0to100km_pct"])
        if not (math.isfinite(area) and area>0 and 0<=sic<=100):
            raise ValueError("Source ice/vegetation outside physical support")
        joined.append({
            "site_id":z["site_id"],"species":z["species"],
            "region":z["region"],"actual_census_year":year,
            "observed_nest_count":int(z["observed_nest_count"]),
            "original_observed_zero_not_imputed":z["zero_is_observed_not_imputed"],
            "census_method":z["method"],
            "observed_year_aug_nov_SIC_pct":sic,
            "mapped_vegetation_2km_m2_static_composite_2017to2023":area,
            "land_panel_first_observed_season":land["first_observed_season"],
            "land_panel_last_observed_season":land["last_observed_season"],
            "land_panel_observed_seasons_count":land["observed_seasons"],
            "vegetation_is_single_multiyear_composite_not_synchronous":True,
            "matched_observation_is_actual_census_not_background_absence":True
        })
    joined.sort(key=lambda z:(z["site_id"],z["species"],z["actual_census_year"]))
    if len(joined)!=63:raise ValueError("Source 63 grain support changed")

    sitegroups=defaultdict(list)
    for z in joined:sitegroups[z["site_id"]].append(z)
    sitecontext=[]
    species_counts=Counter()
    region_counts=Counter()
    year_counts=Counter()
    siteyear_species=defaultdict(set)
    for z in joined:
        species_counts[z["species"]]+=1
        year_counts[z["actual_census_year"]]+=1
        siteyear_species[(z["site_id"],z["actual_census_year"])].add(z["species"])
    for site,rr in sorted(sitegroups.items()):
        unique_areas={float(z["mapped_vegetation_2km_m2_static_composite_2017to2023"]) for z in rr}
        if len(unique_areas)!=1:
            raise ValueError("Source 2km plant area differs across species/years for site "+site)
        ice_year={z["actual_census_year"]:z["observed_year_aug_nov_SIC_pct"] for z in rr}
        if any(not math.isclose(ice_year[z["actual_census_year"]],z["observed_year_aug_nov_SIC_pct"],abs_tol=1e-10) for z in rr):
            raise ValueError("Different sea ice source across species at same site-year")
        region={z["region"] for z in rr}
        if len(region)!=1:raise ValueError("Site spans different source regions")
        sp={z["species"] for z in rr}
        region_counts[next(iter(region))]+=1
        area=next(iter(unique_areas))
        sitecontext.append({
            "site_id":site,"region":next(iter(region)),
            "n_species_with_source_census":len(sp),
            "n_actually_surveyed_site_years":len(ice_year),
            "n_original_site_species_year_census_rows":len(rr),
            "avg_aug_nov_SIC_across_actually_surveyed_years_pct":avg(list(ice_year.values())),
            "static_2017to2023_mapped_vegetation_2km_m2":area,
            "log1p_static_mapped_vegetation_area":math.log1p(area),
            "vegetation_is_site_static_and_date_may_postdate_census":True
        })
    if len(sitecontext)!=25 or len(siteyear_species)!=50 or len({(z["site_id"],z["species"]) for z in joined})!=33:
        raise ValueError("Source co-located spatial/grain support changed")

    xs=[r["avg_aug_nov_SIC_across_actually_surveyed_years_pct"] for r in sitecontext]
    ys=[r["log1p_static_mapped_vegetation_area"] for r in sitecontext]
    region_means={}
    for region in region_counts:
        s=[r for r in sitecontext if r["region"]==region]
        region_means[region]=(avg([z["avg_aug_nov_SIC_across_actually_surveyed_years_pct"] for z in s]),
                              avg([z["log1p_static_mapped_vegetation_area"] for z in s]))
    xr=[r["avg_aug_nov_SIC_across_actually_surveyed_years_pct"]-region_means[r["region"]][0] for r in sitecontext]
    yr=[r["log1p_static_mapped_vegetation_area"]-region_means[r["region"]][1] for r in sitecontext]
    pooled=corr(xs,ys)
    within=corr(xr,yr)
    if not math.isclose(pooled,-0.6083201026857894,rel_tol=0,abs_tol=1e-9):
        raise ValueError(f"Source pooled spatial correlation drift: {pooled}")
    if not math.isclose(within,0.12387734081566852,rel_tol=0,abs_tol=1e-9):
        raise ValueError(f"Source region-demeaned spatial correlation drift: {within}")

    n_species_site=Counter(r["n_species_with_source_census"] for r in sitecontext)
    n_years_site=Counter(r["n_actually_surveyed_site_years"] for r in sitecontext)
    result={
        "status":"COLOCATED_SOURCE_PANEL_RECONSTRUCTED_NO_GO_FOR_ANNUAL_JOINT_NICHE_SDM",
        "design":"post-result source alignment audit; NO new fitted ecological p-values",
        "original_source_git_blobs":source["original_git_blobs"],
        "n_historical_marine_census_obs":len(marine),
        "n_modern_marine_2017_2020_obs":len(recent),
        "n_mapped_positive_contemporary_site_species":len(mapped),
        "n_exact_join_census_site_species_year":len(joined),
        "n_exact_join_distinct_site_species":len({(z["site_id"],z["species"]) for z in joined}),
        "n_exact_join_distinct_sites":len(sitecontext),
        "n_exact_join_actual_census_site_years":len(siteyear_species),
        "n_census_site_years_with_three_species":sum(len(v)==3 for v in siteyear_species.values()),
        "n_census_site_years_with_two_species":sum(len(v)==2 for v in siteyear_species.values()),
        "n_census_site_years_with_one_species":sum(len(v)==1 for v in siteyear_species.values()),
        "region_site_support":dict(sorted(region_counts.items())),
        "species_observed_count_rows":dict(sorted(species_counts.items())),
        "census_year_observation_rows":dict(sorted(year_counts.items())),
        "species_per_site_distribution":dict(sorted(n_species_site.items())),
        "observed_years_per_site_distribution":dict(sorted(n_years_site.items())),
        "n_sites_with_identical_vegetation_map_area_across_species_and_years":len(sitecontext),
        "pooled_site_mean_sic_vs_log1p_static_vegetation_pearson_r_no_p":pooled,
        "region_demeaned_site_mean_sic_vs_log1p_static_vegetation_pearson_r_no_p":within,
        "habitat_coverage_warning":"Plantarctica area is one static 2017-2023 mapped vegetation composite and may postdate 2017-2020 census; not annual greening or a causal variable. Existing habitat is positive mapped detection only; other sites are NOT true absences.",
        "bias_warning":"Victoria Land is 17 of 25 sites; most sites have one species recorded, not an actual absence of the others. Census years are missing-not-at-random, and per-site ice means use only surveyed census years.",
        "statistical_boundary":"No joint 1991-2020 dynamic SDM fit, no independent project-wide FDR p, no warming→greening→niche claim. Pooled r and residual r are separate descriptive geographic associations."
    }
    put("matched_63_observed_rows.csv",joined)
    put("site_25_environmental_context.csv",sitecontext)
    (OUT/"joint_support.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("JOINT_SDM_SUPPORT_GATE="+json.dumps(result,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
