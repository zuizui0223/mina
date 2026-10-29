"""Post-exploration relative nesting-count change of co-source penguin taxa.

Matched site/year and same original citekey/vantage, shared ERA5 temperature.
No p values, causal response, same-day census or physical island inference.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter
from pathlib import Path
import numpy as np

PAIR_COUNTS={"ADPE|CHPE":24,"ADPE|GEPE":45,"CHPE|GEPE":22}
MIN_YEAR_SITE=15
MIN_SITES=3
MIN_REGIONS=2

def read(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def model(rows,term,year_effect):
    n=len(rows)
    sites=sorted({r["site_id"] for r in rows})
    regions={r["source_region"] for r in rows}
    years=sorted({str(r["end_year"]) for r in rows})
    grid={r["grid"] for r in rows}
    out={"source_pair_site_years":n,"unique_site_ids":len(sites),
         "publisher_regions":len(regions),"actual_ERA5_grid_IDs":len(grid),
         "distinct_years":len(years),
         "growth_difference_definition":"delta_log1p_nests_first_species_minus_second",
         "per_1C_climate_coefficient":None,
         "leave_one_original_site_out_range":None,
         "jackknife_refits_identifiable":0,
         "p_value":None,"confidence_interval":None,
         "original_census_month_confirmed":False,
         "physical_island_breeding_patch_confirmed":False}
    if n<MIN_YEAR_SITE or len(sites)<MIN_SITES or len(regions)<MIN_REGIONS:
        out["status"]="SOURCE_SUPPORT_BELOW_PREDECLARED_GROUP_GATE";return out
    def fit(subset):
        if len(subset)<MIN_YEAR_SITE or len({z["site_id"] for z in subset})<MIN_SITES or len({z["source_region"] for z in subset})<MIN_REGIONS:
            return None
        x=np.asarray([z[term] for z in subset])
        y=np.asarray([z["relative_growth"] for z in subset])
        if not (np.isfinite(x).all() and np.isfinite(y).all()):raise ValueError("nonfinite source")
        columns=[np.ones(len(subset))]
        for field in ["site_id"]+(["end_year"] if year_effect else []):
            keys=sorted({str(z[field]) for z in subset})
            for key in keys[1:]:
                columns.append(np.asarray([float(str(z[field])==key) for z in subset]))
        matrix=np.column_stack(columns)
        rx=x-matrix@np.linalg.lstsq(matrix,x,rcond=None)[0]
        ry=y-matrix@np.linalg.lstsq(matrix,y,rcond=None)[0]
        den=float(rx@rx)
        if den<=1e-10:return None
        return float(rx@ry/den)
    coef=fit(rows)
    if coef is None:
        out["status"]="RESIDUAL_CLIMATE_UNIDENTIFIABLE";return out
    out["status"]="EXPLORATORY_COEFFICIENT_FITTED_NOT_CAUSAL"
    out["per_1C_climate_coefficient"]=coef
    other=[fit([z for z in rows if z["site_id"]!=site]) for site in sites]
    valid=[v for v in other if v is not None and math.isfinite(v)]
    out["jackknife_refits_identifiable"]=len(valid)
    out["leave_one_original_site_out_range"]=[min(valid),max(valid)] if valid else None
    return out

def compare(primary,source):
    prim={(r["site_id"],int(r["start_year"]),r["species_id"]):r for r in primary}
    if len(prim)!=381:raise ValueError("SOURCE_STOP duplicate original source species-year")
    selected=[]
    for r in source:
        if r["eligible_same_source_and_vantage"]!="True":continue
        key=(r["site_id"],int(r["start_year"]))
        a=prim[key+(r["species_a"],)]
        b=prim[key+(r["species_b"],)]
        for field in ("delta_September_ERA5_C","delta_AugNov_ERA5_C"):
            if abs(float(a[field])-float(b[field]))>1e-9:
                raise ValueError("SOURCE_STOP same-site species exposure differs")
        diff=float(a["delta_log1p_nests"])-float(b["delta_log1p_nests"])
        if abs(diff-float(r["growth_a_minus_growth_b"]))>1e-9:
            raise ValueError("SOURCE_STOP co-observation growth difference changed")
        if a["publisher_citekey"]!=b["publisher_citekey"] or a["publisher_vantage"]!=b["publisher_vantage"]:
            raise ValueError("SOURCE_STOP different source in allegedly co-observed site-year")
        selected.append({
          "site_id":r["site_id"],"start_year":int(r["start_year"]),
          "end_year":int(r["end_year"]),"source_region":r["source_region"],
          "pair":r["species_a"]+"|"+r["species_b"],
          "grid":a["era5_grid_id"],"relative_growth":diff,
          "delta_September_ERA5_C":float(a["delta_September_ERA5_C"]),
          "delta_AugNov_ERA5_C":float(a["delta_AugNov_ERA5_C"])
        })
    if len(selected)!=91 or dict(Counter(x["pair"] for x in selected))!=PAIR_COUNTS:
        raise ValueError("SOURCE_STOP 91 original matched species paired support drift")
    return selected

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-381-dir",required=True,type=Path)
    p.add_argument("--matched-species-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    primary=args.original_381_dir/"original_MAPPPD5_381_pairs_count_ERA5_join.csv"
    second=args.matched_species_dir/"same_source_site_year_species_pairs.csv"
    record=json.loads((args.matched_species_dir/"same_source_site_year_species_source_result.json").read_text())
    if record["strict_same_citation_and_vantage_pair_rows"]!=91 or not record["direct_species_comparison_source_gate"]:
        raise ValueError("SOURCE_STOP original pre-effect source gate not confirmed")
    if record["input_original_count_join_sha256"]!=sha(primary):
        raise ValueError("SOURCE_STOP original 381 sample SHA differs from source support")
    paired=compare(read(primary),read(second))
    results={}
    for term in ("delta_September_ERA5_C","delta_AugNov_ERA5_C"):
        results[term]={}
        for pair in PAIR_COUNTS:
            subset=[z for z in paired if z["pair"]==pair]
            results[term][pair]={
                "site_fixed":model(subset,term,False),
                "site_year_fixed":model(subset,term,True)
            }
    output={
       "schema":1,"date":"2026-10-29",
       "status":"ORIGINAL_POSTEXPLORATORY_MATCHED_SPECIES_CLIMATE_DIFFERENCES_NOT_CAUSAL",
       "source_381_counts_ERA5_sha256":sha(primary),
       "source_same_site_year_species_sha256":sha(second),
       "n_strict_original_species_pair_comparisons":len(paired),
       "n_distinct_site_year_groups":len({(r["site_id"],r["start_year"]) for r in paired}),
       "fit_results":results,"causal_effect_identified":False,
       "species_climate_causal_difference_identified":False,
       "shared_original_source_citation_not_exact_field_date":True,
       "physical_island_polygon_cooccupancy_verified":False,
       "all_effects_are_post_exploration":True,
       "no_p_values_or_claimed_significance":True
    }
    (args.out/"original_91_matched_species_climate_growth_results.json").write_text(
       json.dumps(output,indent=2,ensure_ascii=False)+"\n")
    print("MATCHED_PENGUIN_SPECIES_CLIMATE_RECEIPT="+json.dumps(output,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
