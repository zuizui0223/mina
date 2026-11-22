#!/usr/bin/env python3
"""Source-gated penguin colony baseline-neighborhood analysis (1980–2000 vs 2005–2025).

Exploratory original source 2456-count pilot (159 series) is NOT a verification
of an external 265-series v5 cohort. All neighborhood pressure values use ONLY
genuine *early-period* counts from the full same-version original site catalog.
Never infer missing conspecific observations as biological absence.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod
R=(10,25,50,100)
EARLY=(1980,2000);LATE=(2005,2025)
SPECIES=("ADPE","CHPE","GEPE")
GEOD=Geod(ellps="WGS84")
def load(path,filename):
    if path.suffix.lower()==".zip":
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            raw=z.read(filename)
    else:
        raw=path.read_bytes()
    return pd.read_csv(io.BytesIO(raw)),hashlib.sha256(raw).hexdigest()
def calc(source,inventory):
    required={"site_id","species","season","observed_nest_count",
              "source_region","latitude","longitude","original_survey_method"}
    sites_required={"site_id","source_region","latitude","longitude",
                    "polar_250km_fixed_grid_block"}
    assert required.issubset(source.columns) and sites_required.issubset(inventory.columns)
    assert set(source.species).issubset(SPECIES)
    assert len(source)==2456 or len(source)>2456
    assert len(inventory)==inventory.site_id.nunique()
    assert not source.duplicated(["site_id","species","season"]).any(), "Same-site species year duplicate: do not average"
    assert (source.observed_nest_count>=0).all()
    assert source[["site_id","species","season","observed_nest_count"]].notna().all().all()
    assert set(source.site_id).issubset(set(inventory.site_id))
    for col in ["source_region","latitude","longitude"]:
        check=source.merge(inventory[["site_id",col]],on="site_id",suffixes=("_obs","_site"))
        if col=="source_region":
            assert (check[col+"_obs"]==check[col+"_site"]).all(),col
        else:
            assert np.allclose(check[col+"_obs"],check[col+"_site"],rtol=0,atol=1e-7),col
    src=source[source.season.between(*EARLY)]
    dst=source[source.season.between(*LATE)]
    a=src.groupby(["site_id","species"],as_index=False).agg(
        early_n=("observed_nest_count","median"), early_years=("season","nunique"),
        early_median_year=("season","median"),early_positive=("observed_nest_count",lambda x:bool((x>0).any())))
    c=dst.groupby(["site_id","species"],as_index=False).agg(
        late_n=("observed_nest_count","median"),late_years=("season","nunique"),
        late_median_year=("season","median"))
    cohort=a.merge(c,on=["site_id","species"],validate="one_to_one").merge(
        inventory[["site_id","source_region","latitude","longitude",
                   "polar_250km_fixed_grid_block"]],on="site_id",validate="many_to_one")
    assert (cohort.late_median_year>cohort.early_median_year).all()
    cohort["early_log_n"]=np.log1p(cohort.early_n)
    cohort["growth_per_decade"]=10*(np.log1p(cohort.late_n)-np.log1p(cohort.early_n)) / (
        cohort.late_median_year-cohort.early_median_year)
    cohort["has_at_least_2_each"]=cohort.early_years.ge(2)&cohort.late_years.ge(2)
    assert not cohort.duplicated(["site_id","species"]).any()
    # Same original catalog is used as reference for both measured conspecifics
    # and the unmeasured/unknown prospective conspecific neighborhood denominator.
    lat_all=inventory.latitude.to_numpy(float)
    lon_all=inventory.longitude.to_numpy(float)
    rows=[]
    for t in cohort.itertuples(index=False):
        _,_,dist=GEOD.inv(np.full(len(inventory),t.longitude),
                          np.full(len(inventory),t.latitude),lon_all,lat_all)
        km=np.asarray(dist)/1000.
        other=inventory.site_id.ne(t.site_id).to_numpy()
        candidate=inventory[["site_id"]].copy()
        candidate["distance_km"]=km
        q=candidate.loc[other].merge(
            a[a.species.eq(t.species)][["site_id","early_n","early_years"]],on="site_id",how="left",
            validate="one_to_one")
        measured=q.early_years.notna()
        observed_positive=measured&q.early_n.gt(0)
        nearest=q.loc[observed_positive,"distance_km"].min()
        entry={"site_id":t.site_id,"species":t.species,"source_region":t.source_region,
               "polar_250km_block":t.polar_250km_fixed_grid_block,
               "early_n":float(t.early_n),"late_n":float(t.late_n),
               "early_years":int(t.early_years),"late_years":int(t.late_years),
               "early_median_year":float(t.early_median_year),
               "late_median_year":float(t.late_median_year),
               "growth_per_decade":float(t.growth_per_decade),
               "log_early_n":float(t.early_log_n),
               "nearest_actual_early_positive_conspecific_km":float(nearest) if pd.notna(nearest) else np.nan,
               "n_catalogued_other_sites":len(q)}
        for radius in R:
            close=q.distance_km.le(radius)
            measured_near=close&measured
            positive_near=close&observed_positive
            early_sum=float(q.loc[positive_near,"early_n"].sum())
            key=f"{radius}km"
            entry[f"n_observed_early_same_species_positive_{key}"]=int(positive_near.sum())
            entry[f"n_actual_early_surveyed_zero_{key}"]=int((measured_near&q.early_n.eq(0)).sum())
            entry[f"n_early_unobserved_species_sites_UNKNOWN_{key}"]=int((close&~measured).sum())
            entry[f"n_all_catalogued_other_sites_{key}"]=int(close.sum())
            entry[f"observed_early_conspecific_nest_sum_{key}"]=early_sum
            entry[f"log1p_observed_early_conspecific_nests_{key}"]=np.log1p(early_sum)
            assert int(positive_near.sum())+int((measured_near&q.early_n.eq(0)).sum())+int((close&~measured).sum())==int(close.sum())
        rows.append(entry)
    out=pd.DataFrame(rows).sort_values(["species","site_id"]).reset_index(drop=True)
    assert len(out)==len(cohort)
    return out,a,cohort
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True,help="Frozen method-selected source CSV or ZIP")
    parser.add_argument("--inventory",type=Path,help="CSV or same ZIP containing all source known sites")
    parser.add_argument("--source-member",default="source_observed_2456.csv")
    parser.add_argument("--inventory-member",default="panantarctic_595_site_inventory.csv")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--expected-series",type=int,default=265,
                        help="Must be matched in run-of-record; legacy pilot override with 159")
    parser.add_argument("--legacy-pilot",action="store_true",
                        help="Label as old-2456 159-series pilot, never verify a 265-source result")
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    if args.legacy_pilot and args.expected_series!=159:
        parser.error("--legacy-pilot must be used with --expected-series 159")
    source,digest=load(args.source,args.source_member)
    inventory,inventory_sha=load(args.inventory or args.source,args.inventory_member)
    z,early,cohort=calc(source,inventory)
    n=len(z)
    species=z.species.value_counts().to_dict()
    passed=(n==args.expected_series and not args.legacy_pilot)
    state="SOURCE_MATCHED_HYPOTHESIS_DATA" if passed else (
          "LEGACY_2456_159_PILOT_NOT_265_VERIFICATION" if args.legacy_pilot else "STOP_SOURCE_SERIES_MISMATCH")
    result={"status":state,"early_window":EARLY,"late_window":LATE,
            "source_count_rows":len(source),"source_catalogue_sites":len(inventory),
            "source_sha256":digest,"inventory_sha256":inventory_sha,
            "expected_source_series":args.expected_series,
            "observed_series":n,"observed_by_species":species,
            "n_early_conspecific_catalogue_rows":len(early),
            "radii_km":R,"primary_radius_km":50,
            "source_early_counts_only":True,"missing_is_not_zero":True,
            "n_all_no_early_positive_neighbor":int(z.nearest_actual_early_positive_conspecific_km.isna().sum()),
            "n_unique_250km_blocks":int(z.polar_250km_block.nunique()),
            "n_original_regions":int(z.source_region.nunique()),
            "causal_climate_dose_response_verified":False,
            "future_nest_forecast_authorized":False,
            "inference":"Measured early conspecific counts are a known-observation lower bound; other catalogue sites are UNKNOWN"}
    z.to_csv(args.output/"conspecific_neighborhood_10_25_50_100km.csv",index=False)
    cohort.to_csv(args.output/"original_early_late_cohort.csv",index=False)
    (args.output/"source_gate.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not args.legacy_pilot and not passed:
        raise SystemExit("STOP_SOURCE_SERIES_MISMATCH: do not transfer 265-series coefficients")
if __name__=="__main__":main()
