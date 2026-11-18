#!/usr/bin/env python3
"""Fixed 3-species 100 site-species trend comparison at Pan-Antarctic scale.

No pseudoabsences. Same sampled 1991-2020 census years for biological trends
and original OSI SAF 8-11 monthly ice trends. Never interpret current-site
r as warming-caused abundance or future colony occupancy.
"""
from __future__ import annotations
import argparse,csv,json,math,random
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PRIMARY=HERE/"outputs"
DEST=HERE/"three_species_100_outputs"
DEST.mkdir(exist_ok=True,parents=True)
REGIONS_MIN=2
SEED=20261109
B=2000
SP=("ADPE","CHPE","GEPE")

def table(p):
    with p.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def save(p,records):
    if not records:raise ValueError("Empty source data output: "+str(p))
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)
def slope(y,x):
    xx=np.asarray(x,dtype=float);yy=np.asarray(y,dtype=float)
    if len(xx)<5 or np.ptp(xx)<10 or not(np.isfinite(xx).all() and np.isfinite(yy).all()):
        raise ValueError("Invalid original long time-series support")
    a=xx-np.mean(xx)
    return float(np.dot(a,yy-np.mean(yy))/np.dot(a,a)*10.)
def correlate(rows,x,y):
    if len(rows)<3:return None
    a=np.array([z[x] for z in rows]);b=np.array([z[y] for z in rows])
    if np.std(a)<1e-12 or np.std(b)<1e-12:return None
    return float(np.corrcoef(a,b)[0,1])
def region_residuals(data):
    groups=defaultdict(list)
    for i,row in enumerate(data):groups[row["source_region"]].append(i)
    xx=np.array([z["sic_trend_pp_per_decade"] for z in data],dtype=float)
    yy=np.array([z["observed_log_nest_trend_per_decade"] for z in data],dtype=float)
    for ix in groups.values():
        xx[ix]-=np.mean(xx[ix])
        yy[ix]-=np.mean(yy[ix])
    return xx,yy
def region_corr(data):
    if len(data)<4:return None
    a,b=region_residuals(data)
    if np.std(a)<1e-12 or np.std(b)<1e-12:return None
    return float(np.corrcoef(a,b)[0,1])
def bootstrap(data,blocks,sp):
    rng=random.Random(SEED+SP.index(sp))
    keys=sorted({z["polar_250km_block"] for z in data})
    if len(keys)<5:
        return {"status":"INSUFFICIENT_SPATIAL_BLOCKS","n_original_blocks":len(keys),
                "valid_bootstrap_reps":0,"interval_95_percentile":None}
    by=defaultdict(list)
    for z in data:by[z["polar_250km_block"]].append(z)
    vals=[]
    for j in range(B):
        trial=[z for key in (rng.choice(keys) for k in range(len(keys))) for z in by[key]]
        cc=region_corr(trial)
        if cc is not None and math.isfinite(cc):vals.append(cc)
    if len(vals)<.75*B:
        return {"status":"BOOTSTRAP_UNSTABLE_OR_REGION_UNIDENTIFIABLE",
                "n_original_blocks":len(keys),
                "valid_bootstrap_reps":len(vals),"interval_95_percentile":None}
    return {"status":"DESCRIPTIVE_SPATIAL_BLOCK_INTERVAL_ONLY",
            "n_original_blocks":len(keys),"valid_bootstrap_reps":len(vals),
            "interval_95_percentile":[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--full-ice-csv",required=True,type=Path)
    ap.add_argument("--full-ice-summary",required=True,type=Path)
    args=ap.parse_args()
    coverage=json.loads((PRIMARY/"macro_original_coverage.json").read_text())
    if coverage["n_focal_unique_sites"]!=595:
        raise ValueError("Main Pan-Antarctic census frame changed")
    c=table(PRIMARY/"source_observed_2456.csv")
    sites={x["site_id"]:x for x in table(PRIMARY/"panantarctic_595_site_inventory.csv")}
    ice=table(args.full_ice_csv)
    with args.full_ice_summary.open(encoding="utf-8") as f:metadata=json.load(f)
    if (len(c),len(sites),len(ice))!=(2456,595,595*30*4):
        raise ValueError("Expected fixed full 595×30×4 original sources")
    if metadata["status"]!="PANANTARCTIC_ORIGINAL_30YR_MONTHLY_SIC_MACRO_SOURCE_COMPLETE":
        raise ValueError("Full original source horizon did not complete")
    byice=defaultdict(dict)
    for rec in ice:
        site=rec["site_id"];year=int(rec["year"]);month=int(rec["month"])
        if site not in sites or year not in range(1991,2021) or month not in (8,9,10,11):
            raise ValueError("Unexpected SIC source site/year/month")
        k=(site,year)
        if month in byice[k]:raise ValueError("Duplicate native SIC site-year-month")
        if rec["source_full_595_site_monthly_support"]=="OK":
            v=float(rec["source_25km_buffer_mean_SIC_pct"])
            if not math.isfinite(v) or not 0<=v<=100:raise ValueError("Invalid original sea ice")
            byice[k][month]=v
        else:byice[k][month]=None
    if len(byice)!=595*30:raise ValueError("Original 595×30 ice completeness grain changed")
    annually={}
    for key,dates in byice.items():
        if set(dates)!={8,9,10,11}:raise ValueError("Incomplete original source calendar")
        annually[key]=float(np.mean(list(dates.values()))) if all(x is not None for x in dates.values()) else None

    counted=defaultdict(list)
    for rec in c:
        y=int(rec["season"])
        if 1991<=y<=2020:
            if rec["species"] not in SP or rec["site_id"] not in sites:
                raise ValueError("Original focal count cohort changed")
            counted[rec["site_id"],rec["species"]].append(rec)
    if sum(len(z) for z in counted.values())!=1691 or len(counted)!=495:
        raise ValueError("Source-locked 1991–2020 census-groups drift")
    eligible=[]
    for (site,species),rows in sorted(counted.items()):
        years=sorted({int(r["season"]) for r in rows})
        if len(years)>=5 and years[-1]-years[0]>=10:
            eligible.append((site,species,rows,years))
    if len(eligible)!=100 or len({z[0] for z in eligible})!=77:
        raise ValueError("Source-defined >=5 census years and >=10 year span cohort changed")
    if Counter(x[1] for x in eligible)!=Counter({"ADPE":37,"CHPE":27,"GEPE":36}):
        raise ValueError("Focal species trend support drift")
    summaryrows=[];dropped=[]
    for site,species,rows,years in eligible:
        assert len(rows)==len(years)
        yearcount={int(z["season"]):int(z["observed_nest_count"]) for z in rows}
        ice_years=[annually[site,y] for y in years]
        if any(v is None for v in ice_years):
            dropped.append({"site_id":site,"species":species,"reason":"MISSING_ONE_OR_MORE_EXACT_CENSUS_YEAR_SIC",
                            "n_original_counts":len(rows),"n_matched_climate_seasons":sum(z is not None for z in ice_years)})
            continue
        geo=sites[site]
        summaryrows.append({
          "site_id":site,"species":species,"source_region":geo["source_region"],
          "polar_100km_block":geo["polar_100km_fixed_grid_block"],
          "polar_250km_block":geo["polar_250km_fixed_grid_block"],
          "n_original_census_years":len(years),
          "census_year_min":years[0],"census_year_max":years[-1],
          "observed_method":rows[0]["original_survey_method"],
          "observed_log_nest_trend_per_decade":slope(
             [math.log1p(yearcount[year]) for year in years],years),
          "sic_trend_pp_per_decade":slope(ice_years,years),
          "mean_source_SIC_during_observed_census_years":float(np.mean(ice_years)),
          "source_time_span_years":years[-1]-years[0],
          "model_is_future_demographic_prediction":False
        })
    if dropped:
        save(DEST/"source_failed_climate_matches.csv",dropped)
    else:
        (DEST/"source_failed_climate_matches.csv").write_text(
            "site_id,species,reason,n_original_counts,n_matched_climate_seasons\n")
    save(DEST/"100_original_site_species_observed_trends.csv",summaryrows)
    bysp={sp:[r for r in summaryrows if r["species"]==sp] for sp in SP}
    reports={}
    for sp,rows in bysp.items():
        raw=correlate(rows,"sic_trend_pp_per_decade","observed_log_nest_trend_per_decade")
        residual=region_corr(rows)
        leavereg={}
        for region in sorted({r["source_region"] for r in rows}):
            a=[r for r in rows if r["source_region"]!=region]
            leavereg[region]={"n":len(a),"region_demeaned_correlation":region_corr(a)}
        boot=bootstrap(rows,None,sp)
        signs={np.sign(z["sic_trend_pp_per_decade"]) for z in rows}
        reports[sp]={
          "original_eligible_series":sum(species==sp for site,species,records,years in eligible),
          "matched_original_series":len(rows),
          "n_unique_sites":len({z["site_id"] for z in rows}),
          "n_region_labels":len({z["source_region"] for z in rows}),
          "n_original_250km_blocks":len({z["polar_250km_block"] for z in rows}),
          "raw_site_species_trend_correlation":raw,
          "within_region_demeaned_correlation":residual,
          "250km_spatial_block_bootstrap":boot,
          "leave_one_source_region_out":leavereg,
          "n_sites_SIC_decreasing":sum(z["sic_trend_pp_per_decade"]<0 for z in rows),
          "n_sites_SIC_increasing":sum(z["sic_trend_pp_per_decade"]>0 for z in rows),
          "n_sites_observed_nests_decreasing":sum(z["observed_log_nest_trend_per_decade"]<0 for z in rows),
          "n_sites_observed_nests_increasing":sum(z["observed_log_nest_trend_per_decade"]>0 for z in rows)
        }
    # Pooled species-demeaned slope relationship for context, explicitly not
    # the primary preselected 3-species within-region association family.
    pooled=[]
    for sp,rows in bysp.items():
        if not rows:continue
        ax=float(np.mean([z["sic_trend_pp_per_decade"] for z in rows]))
        ay=float(np.mean([z["observed_log_nest_trend_per_decade"] for z in rows]))
        for z in rows:pooled.append({"x":z["sic_trend_pp_per_decade"]-ax,
                                    "y":z["observed_log_nest_trend_per_decade"]-ay})
    pooled_r=correlate(pooled,"x","y")
    ret={
      "status":"PANANTARCTIC_THREE_SPECIES_LONG_COUNT_AND_ICE_TRENDS_COMPLETE",
      "original_macro_site_support":{"all_sites":595,"original_count_rows":2456,
          "census_1991to2020_rows":1691,"census_1991to2020_sites":410,
          "original_site_species_1991to2020":495,
          "eligible_trend_site_species":len(eligible),
          "eligible_trend_distinct_sites":len({z[0] for z in eligible}),
          "eligible_trend_regions":len({sites[z[0]]["source_region"] for z in eligible}),
          "validated_trend_series":len(summaryrows),"missing_climate_series":len(dropped)},
      "original_ice_source":{"n_original_monthly_site_month_rows":len(ice),
             "n_original_files":metadata["n_original_source_netCDF_files"],
             "marine_reference_geometry":"fixed 1993-09 original EASE2 25km 0-100km coast site pixel IDs",
             "months":[8,9,10,11],"years":[1991,2020]},
      "pre_fixed_family_three_species":reports,
      "post_result_pooled_species_demeaned_descriptive_correlation":pooled_r,
      "inference_limits":[
        "Source-matched trends, NOT direct ocean-to-nest causality, adjusted climate effect, or future SSP forecast.",
        "Survey years vary among colonies; no missing census year was filled with zero.",
        "A source colony ID and polar block are not necessarily independent climate replicates.",
        "Bootstrap blocks and source region means may be too few or unbalanced; no naive independent-site p-value.",
        "Census method fixed within each site×species; observation errors and colony footpoint changing remain.",
        "Many original sites have too few/short observations; 100 trend series do not exhaust the 595 original geographic sites.",
        "No annual vegetation series is modeled as a mediator; current Plantarctica is only a 2017–2023 static site context.",
        "No additional latitude, time lag, p-value family, or post-hoc region exclusion was selected after results."
      ]}
    (DEST/"three_species_macro_climate_trend_verdict.json").write_text(
      json.dumps(ret,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PAN_ANTARCTIC_THREE_SPECIES_TREND_TEST="+json.dumps(ret,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
