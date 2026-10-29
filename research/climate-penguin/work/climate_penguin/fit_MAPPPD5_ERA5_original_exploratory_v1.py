"""Post-exploration recorded nest-change versus contemporaneous ERA5-change.

Original 381-row cohort is frozen by the previous source-only overlap audit.
No refitting on favorable outcomes, no p-values, no anthropogenic causality.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,sys
from collections import Counter
from pathlib import Path
import numpy as np
import requests

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import derive_MAPPPD5_original_macro_source_v1 as original
import audit_MAPPPD5_ERA5_40site_overlap_v1 as climate_gate

P_SOURCE_SHA=climate_gate.REQUIRED_PAIR_SHA
E_SOURCE_SHA=climate_gate.REQUIRED_ERA5_SHA
SPECIES=("ADPE","CHPE","GEPE")
MIN_PAIRS=20
MIN_SITES=5
MIN_YEARS=6
TOL=1e-10

def csvrows(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def design_matrix(rows,effects):
    n=len(rows)
    columns=[np.ones(n,dtype=float)]
    for label in effects:
        keys=sorted({str(r[label]) for r in rows})
        for key in keys[1:]:
            columns.append(np.asarray([float(str(r[label])==key) for r in rows]))
    return np.column_stack(columns)

def slope(rows,xname,effects):
    if len(rows)<MIN_PAIRS:return None
    if len({r["site_id"] for r in rows})<MIN_SITES:return None
    if len({r["end_year"] for r in rows})<MIN_YEARS:return None
    x=np.asarray([r[xname] for r in rows],dtype=float)
    y=np.asarray([r["delta_log1p_nests"] for r in rows],dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("SOURCE_STOP nonfinite original pair or environment")
    matrix=design_matrix(rows,effects)
    xres=x-matrix@np.linalg.lstsq(matrix,x,rcond=None)[0]
    yres=y-matrix@np.linalg.lstsq(matrix,y,rcond=None)[0]
    den=float(xres@xres)
    if den<=TOL:return None
    return float(xres@yres/den)

def model_support(rows,term,effects):
    ids=sorted({r["site_id"] for r in rows})
    grids=sorted({r["era5_grid_id"] for r in rows})
    regions=sorted({r["source_region"] for r in rows})
    years=sorted({r["end_year"] for r in rows})
    value=slope(rows,term,effects)
    loo=[]
    if value is not None:
        for grid in grids:
            keep=[r for r in rows if r["era5_grid_id"]!=grid]
            b=slope(keep,term,effects)
            if b is not None:loo.append(b)
    return {
      "original_pair_rows":len(rows),
      "source_site_ids":len(ids),"actual_ERA5_grid_ids":len(grids),
      "original_source_regions":len(regions),"distinct_breeding_years":len(years),
      "species":dict(sorted(Counter(r["species_id"] for r in rows).items())),
      "year_label_min_max":[min(years),max(years)] if years else None,
      "x_name":term,"effects":list(effects),
      "beta_delta_log1p_nests_per_plus1C_annual_environment_change":value,
      "leave_one_ERA5_grid_out_beta_min_max":[min(loo),max(loo)] if loo else None,
      "leave_one_ERA5_grid_out_valid_refits":len(loo),
      "inferential_p_value":None,"calibrated_confidence_interval":None,
      "source_month_before_count_confirmed":False,
      "physical_island_factor_measured":False,
    }

def original_observations():
    with requests.Session() as session:
        session.headers.update({"User-Agent":"mina-2026-original-macroclimate-exploratory-count/1.0"})
        raw={k:original.source_data(session,k) for k in original.SOURCE}
    release=json.loads(raw["release"])
    if release.get("version")!="5.0" or release.get("release_date")!="2026-10-21":
        raise ValueError("SOURCE_STOP published release label changed")
    p1=original.tabular(raw["observations_p1"],original.OBS_FIELDS)
    p2=original.tabular(raw["observations_p2"],original.OBS_FIELDS)
    assert len(p1)==5000 and len(p2)==487
    obs={r["id"]:r for r in p1+p2}
    assert len(obs)==5487
    return obs,{k:hashlib.sha256(v).hexdigest() for k,v in raw.items()}

def run(pair_file,overlap_file,era_file,obs):
    if sha(pair_file)!=P_SOURCE_SHA or sha(era_file)!=E_SOURCE_SHA:
        raise ValueError("SOURCE_STOP original cohort or climate source changed")
    pairs=csvrows(pair_file);overlap=csvrows(overlap_file);monthly=csvrows(era_file)
    assert len(pairs)==len(overlap)==771 and len(monthly)==14400
    eligible=[r for r in overlap if r["paired_september_ERA5_complete"]=="True"]
    if (len(eligible)!=381 or Counter(r["species_id"] for r in eligible)!=
        {"ADPE":294,"CHPE":29,"GEPE":58}):
        raise ValueError("SOURCE_STOP independently frozen 381-row species support drift")
    index={(r["site_id"],r["species_id"],r["start"],r["end"]):r for r in pairs}
    assert len(index)==len(pairs)
    lookup={(r["site_id"],int(r["year"]),int(r["month"])):r
            for r in monthly}
    assert len(lookup)==14400
    source=[]
    for q in eligible:
        k=(q["site_id"],q["species_id"],q["start"],q["end"])
        r=index[k]
        a=obs[r["source_early_observation_id"]]
        b=obs[r["source_late_observation_id"]]
        if not (r["original_citekey"]==a["citekey"]==b["citekey"] and
                r["original_vantage"]==a["vantage"]==b["vantage"] and
                a["species_id"]==b["species_id"]==r["species_id"] and
                a["site_id"]==b["site_id"]==r["site_id"] and
                int(a["season"])+1==int(b["season"])):
            raise ValueError("SOURCE_STOP original observation ID lineage mismatch")
        if not original.numeric(a["count"]) or not original.numeric(b["count"]):
            raise ValueError("SOURCE_STOP nonnumerical original nest count")
        n0,n1=float(a["count"].replace(",","")),float(b["count"].replace(",",""))
        grid=q["actual_ERA5_grid_id"]
        if not grid:raise ValueError("SOURCE_STOP missing physical source grid identity")
        years=(int(q["start"]),int(q["end"]))
        def month_mean(year, months):
            vals=[lookup[(r["site_id"],year,m)] for m in months]
            if not all(z["complete_month"]=="True" and z["air2m_mean_c"] for z in vals):
                raise ValueError("SOURCE_STOP prior frozen climate availability failed")
            if any(f"{float(z['returned_grid_latitude'])}|{float(z['returned_grid_longitude'])}"!=grid for z in vals):
                # Canonical string formatting is not physically relevant; if
                # formatting differs fail and inspect rather than silently reassign.
                raise ValueError("SOURCE_STOP climate grid ID drift")
            return sum(float(z["air2m_mean_c"]) for z in vals)/len(vals)
        sep=month_mean(years[1],[9])-month_mean(years[0],[9])
        augnov=month_mean(years[1],[8,9,10,11])-month_mean(years[0],[8,9,10,11])
        source.append({
            "site_id":r["site_id"],"species_id":r["species_id"],
            "site_species":r["site_id"]+"|"+r["species_id"],
            "end_year":years[1],"start_year":years[0],
            "source_region":r["source_region"],"era5_grid_id":grid,
            "nests_start":n0,"nests_end":n1,
            "delta_log1p_nests":math.log1p(n1)-math.log1p(n0),
            "delta_September_ERA5_C":sep,
            "delta_AugNov_ERA5_C":augnov,
            "publisher_citekey":r["original_citekey"],
            "publisher_vantage":r["original_vantage"],
            "month_census_verified":False,
            "physical_island_polygon_verified":False,
        })
    return source

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--overlap-dir",type=Path,required=True)
    p.add_argument("--era5-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    obs,pins=original_observations()
    pair_file=args.source_dir/"original_MAPPPD5_strict_three_taxa_macro_pair_support.csv"
    overlap_file=args.overlap_dir/"original_MAPPPD5_ERA5_40site_overlap_v1.csv"
    era_file=args.era5_dir/"era5_monthly_1991_2020.csv"
    cohort=run(pair_file,overlap_file,era_file,obs)
    results={}
    for term in ("delta_September_ERA5_C","delta_AugNov_ERA5_C"):
        results[term]={}
        for name,data in [("all_three_taxa",cohort)]+[
           (sp,[r for r in cohort if r["species_id"]==sp]) for sp in SPECIES]:
            results[term][name]={
             "site_species_fixed":model_support(data,term,["site_species"]),
             "site_species_plus_breeding_year_fixed":model_support(data,term,["site_species","end_year"])
            }
    report={
       "schema":1,"date":"2026-10-29",
       "status":"POST_EXPLORATION_CLIMATE_COUNTS_ASSOCIATION_NO_CAUSAL_ATTRIBUTION",
       "original_publisher_source_sha256":pins,
       "original_381_cohort_source_sha256":sha(overlap_file),
       "source_original_ERA5_sha256":sha(era_file),
       "observed_source_rows":len(cohort),
       "zero_count_pairs":sum(r["nests_start"]==0 or r["nests_end"]==0 for r in cohort),
       "result":results,
       "no_mechanism_identified":True,
       "assumptions_unverified":[
         "Source breeding-season year is not original survey date; many climate months can occur after original census.",
         "40 site roster is Adélie selected; three species are unequal and not independent continental samples.",
         "Publisher records sharing original citation/vantage still have observation uncertainty and possible dependency.",
         "Site fixed effects remove between-site differences; common-year fixed effects change estimand and may remove true broad climate signals.",
         "Published site ID is not a unique physical island/colony or independently mapped habitat patch.",
         "Leave-one-grid-out ranges are not inferential confidence intervals or hypothesis tests.",
         "Anthropogenic warming/nearshore ice/snow/vegetation effects are not identified.",
       ]
    }
    with (args.out/"original_MAPPPD5_381_pairs_count_ERA5_join.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(cohort[0]));w.writeheader();w.writerows(cohort)
    (args.out/"macro_three_species_count_climate_exploratory_v1.json").write_text(
      json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print("MACRO_THREE_SPECIES_COUNT_CLIMATE_RECEIPT="+json.dumps(report,ensure_ascii=False,allow_nan=False),flush=True)

if __name__=="__main__":main()
