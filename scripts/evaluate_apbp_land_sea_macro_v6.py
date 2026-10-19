#!/usr/bin/env python3
"""First exploratory APBP x ADD x NOAA land–sea macroecological comparison.

V6 scientific contract in contracts/APBP_LAND_SEA_ISLAND_MACRO_V6_PRE_EFFECT.md
was committed BEFORE any biological response/environment coefficient was fitted.
Original public-source derived CSVs have mandatory exact SHA256 checks; no
missing survey is turned into a zero and no duplicated season chosen by effect.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

SOURCES = {
    "population": (
        "APBP_ALL_ORIGINAL_MEASUREMENTS_V2.csv",
        "75c98ad9174f6ca8b88ae915adb8bb39de5d279099b45ce1ae7d1b2e25d5ba59",
    ),
    "medium_rock": (
        "APBP_ADD_719_SITE_LAND_ROCK_LINK_V3.csv",
        "e51b4ddf14677c2b01f03be91629104d8be47a46d29c0f1fc1ed0f6427de8016",
    ),
    "high_land": (
        "APBP_719_HIGHRES_COAST_MATCH_V4.csv",
        "b93c4e85667d7a12ae76166620e5ff5d4ea6482c182457cf3ca4cd0321551c41",
    ),
    "marine": (
        "APBP_NOAA_1979_2022_SITEYEAR_OCEAN_SIC_V5.csv",
        "44d0b7feea08b7c0216cc5595b3e17bbf48ce4fd0b197a758afa33aceea9c8b4",
    ),
}
SPECIES = (
    "Pygoscelis adeliae",
    "Pygoscelis antarcticus",
    "Pygoscelis papua",
)
ISLAND = "ISLAND_SEPARATE_LAND_POLYGON_PROXY"
MAINLAND = "CONTINENT_LARGEST_POLYGON_PROXY"
ALPHA = 20.0
BLOCK_METERS = 250000
CONTROL = [
    "year", "year2", "log_n_prev", "accuracy_prev", "accuracy_curr",
    "lat", "lon_sin", "lon_cos", "chin", "gent",
]
MARINE = CONTROL + [
    "ice_near", "ice_far", "ice_near_chin", "ice_near_gent",
    "ice_far_chin", "ice_far_gent",
]
LAND_SEA = MARINE + [
    "island", "logrock", "island_logrock", "ice_near_island",
    "ice_near_logrock", "ice_near_island_logrock",
]
MODELS = {"B0_baseline":CONTROL, "B1_marine":MARINE, "B2_land_island_marine":LAND_SEA}
INTERACTION = "ice_near_island_logrock"

def verified_csv(path: Path, group: str):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    wanted = SOURCES[group][1]
    if digest != wanted:
        raise ValueError("SOURCE_STOP original "+group+" derived source SHA drift")
    return pd.read_csv(path, low_memory=False)

def prepare(pop, med, hi, ice):
    if not set(SPECIES).issubset(set(pop.scientificName_accepted.unique())):
        raise ValueError("ROSTER_STOP original Pygoscelis source names missing")
    s=pop.loc[
        pop.eligibility.eq("ELIGIBLE_NEST_RECORD_ONLY") &
        pop.scientificName_accepted.isin(SPECIES)
    ].copy()
    # Counts are original source values; prohibit nonfinite or noninteger inputs.
    n=pd.to_numeric(s.nest_numeric_candidate,errors="coerce")
    if n.isna().any() or (n<0).any() or (n!=np.floor(n)).any():
        raise ValueError("COUNT_STOP source reported nest record has invalid numeric count")
    s["nest_numeric_candidate"]=n.astype(np.int64)
    date=s.event_date.fillna("").astype(str).str.extract(
        r"^(?P<year>\d{4})-(?P<month>\d{2})(?:-\d{2})?$"
    )
    s["month"]=pd.to_numeric(date["month"], errors="coerce")
    years=pd.to_numeric(date["year"],errors="coerce")
    s["season"]=years - s["month"].isin((1,2)).astype(int)
    date_ok=s["month"].isin([12,1,2]) & s["season"].between(1979,2022)
    n_date=int(date_ok.sum())
    s=s.loc[date_ok].copy()
    s["season"]=s.season.astype(int)

    keys=["site_id_original","scientificName_accepted","season"]
    freq=s.groupby(keys).size().rename("source_duplicates").reset_index()
    ambiguous=freq.loc[freq.source_duplicates>1]
    # Entire ambiguous same-site×species×season groups are excluded.
    s=s.merge(freq.loc[freq.source_duplicates==1,keys],on=keys,validate="many_to_one")
    s=s.merge(
        hi[["source_locationID","high_class","medium_to_high_class_disagreement",
            "high_original_feature_id","original_APBP_max_uncertainty_m"]],
        left_on="site_id_original",right_on="source_locationID",
        how="left",validate="many_to_one",
    )
    s=s.merge(
        med[["original_locationID","rock_2000m_mapped_km2","latitude",
             "longitude","land_polygon_id"]],
        left_on="site_id_original",right_on="original_locationID",
        how="left",validate="many_to_one",
    )
    s=s.merge(
        ice[["original_APBP_locationID","breeding_start_year",
             "sic_25_75km_anomaly","sic_75_150km_anomaly"]],
        left_on=["site_id_original","season"],
        right_on=["original_APBP_locationID","breeding_start_year"],
        how="left",validate="many_to_one",
    )
    eligible=s[
        s.high_class.isin((ISLAND,MAINLAND)) &
        s.rock_2000m_mapped_km2.notna() &
        s.sic_25_75km_anomaly.notna() & s.sic_75_150km_anomaly.notna() &
        ~s.medium_to_high_class_disagreement.fillna(True).astype(bool)
    ].copy()
    if eligible.empty:
        raise ValueError("PANEL_STOP no geographical/temporal source support")
    # An identical species and original site must be measured exactly in t-1,t.
    pairs=eligible.assign(season=eligible.season+1).merge(
        eligible,on=keys,suffixes=("_prev","_curr"),validate="one_to_one"
    )
    # A real source site cannot change published land or mapped rock class
    # between its two repeat surveys.
    if ((pairs.high_class_prev!=pairs.high_class_curr) |
        (pairs.rock_2000m_mapped_km2_prev!=pairs.rock_2000m_mapped_km2_curr)).any():
        raise ValueError("PANEL_STOP source geographical class inconsistent")
    tr=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    xx,yy=tr.transform(pairs.longitude_curr.to_numpy(dtype=float),
                       pairs.latitude_curr.to_numpy(dtype=float))
    pairs["block250k"]=[
        str(int(math.floor(x/BLOCK_METERS)))+"_"+str(int(math.floor(y/BLOCK_METERS)))
        for x,y in zip(xx,yy)
    ]
    year_values=sorted(pairs.season.unique().tolist())
    report={
        "original_three_species_measured_nests":len(pop.loc[
            pop.eligibility.eq("ELIGIBLE_NEST_RECORD_ONLY") &
            pop.scientificName_accepted.isin(SPECIES)]),
        "dated_dec_jan_feb_rows":n_date,
        "ambiguous_duplicate_site_species_season_groups_discarded":len(ambiguous),
        "source_rows_in_ambiguous_groups_discarded":int(ambiguous.source_duplicates.sum()),
        "unique_season_rows_before_geographic_QA":len(s),
        "unique_season_rows_after_geo_marine_QA":len(eligible),
        "valid_consecutive_site_species_pairs":len(pairs),
        "distinct_source_site_ids":int(pairs.site_id_original.nunique()),
        "distinct_source_land_polygon_features":int(pairs.high_original_feature_id_curr.nunique()),
        "spatial_250km_blocks":int(pairs.block250k.nunique()),
        "pairs_in_biggest_spatial_block":int(pairs.block250k.value_counts().max()),
        "pairs_by_species":pairs.scientificName_accepted.value_counts().to_dict(),
        "pairs_by_provisional_land_class":pairs.high_class_curr.value_counts().to_dict(),
        "first_last_comparable_season":[min(year_values),max(year_values)],
        "original_precision_missing_in_second_observation":int(
            pairs.measurementAccuracy_original_curr.isna().sum()),
        "zero_to_zero_original_measured_pairs":int(
            ((pairs.nest_numeric_candidate_prev==0) &
             (pairs.nest_numeric_candidate_curr==0)).sum()),
        "source_dec_jan_feb_season_definition":"t=Dec YYYY or Jan-Feb YYYY+1; year-only records excluded",
    }
    return pairs,report

def features(pairs):
    v=lambda key:pairs[key].to_numpy(dtype=float)
    lon=np.deg2rad(v("longitude_curr"))
    species=pairs.scientificName_accepted
    ch=(species=="Pygoscelis antarcticus").astype(float).to_numpy()
    gt=(species=="Pygoscelis papua").astype(float).to_numpy()
    ice_near=v("sic_25_75km_anomaly_curr")-v("sic_25_75km_anomaly_prev")
    ice_far=v("sic_75_150km_anomaly_curr")-v("sic_75_150km_anomaly_prev")
    rock=np.log1p(v("rock_2000m_mapped_km2_curr"))
    island=(pairs.high_class_curr==ISLAND).astype(float).to_numpy()
    t=(v("season")-2000)/20
    cols={
        "year":t,
        "year2":t*t,
        "log_n_prev":np.log1p(v("nest_numeric_candidate_prev")),
        "accuracy_prev":v("measurementAccuracy_original_prev"),
        "accuracy_curr":v("measurementAccuracy_original_curr"),
        "lat":v("latitude_curr"),
        "lon_sin":np.sin(lon),
        "lon_cos":np.cos(lon),
        "chin":ch, "gent":gt,
        "ice_near":ice_near, "ice_far":ice_far,
        "ice_near_chin":ice_near*ch, "ice_near_gent":ice_near*gt,
        "ice_far_chin":ice_far*ch, "ice_far_gent":ice_far*gt,
        "island":island, "logrock":rock, "island_logrock":island*rock,
        "ice_near_island":ice_near*island,
        "ice_near_logrock":ice_near*rock,
        "ice_near_island_logrock":ice_near*island*rock,
    }
    response=np.log1p(v("nest_numeric_candidate_curr"))-np.log1p(v("nest_numeric_candidate_prev"))
    if any(not np.isfinite(x).all() for x in [response,*cols.values()]):
        raise ValueError("MODEL_STOP NA/nonfinite feature in prespecified complete cases")
    return response,cols

def ridge_predict(response,cols,model,training,alpha=ALPHA):
    names=MODELS[model]
    # All continuous and categorical features use training-fold z scoring
    # with intercept not penalized. No outcome-driven tuning.
    raw=np.column_stack([cols[name] for name in names])
    means=raw[training].mean(axis=0)
    scales=raw[training].std(axis=0)
    scales[scales<1e-12]=1.
    x=(raw-means)/scales
    design=np.column_stack([np.ones(len(response)),x])
    D=design[training]
    yy=response[training]
    penalty=np.diag(np.array([0.]+[alpha]*len(names)))
    beta=np.linalg.solve(D.T@D+penalty,D.T@yy)
    coef={name:float(beta[j+1]/scales[j]) for j,name in enumerate(names)}
    return design@beta,coef

def evaluate(pairs):
    target,columns=features(pairs)
    blocks=pairs.block250k.to_numpy(dtype=str)
    known=sorted(np.unique(blocks))
    if len(known)<5:
        raise ValueError("MODEL_STOP too few geographically separated blocks")
    errors={name:{} for name in MODELS}
    pred={name:np.full(len(target),np.nan) for name in MODELS}
    for blocked in known:
        train=blocks!=blocked
        held=~train
        for model in MODELS:
            prediction,_=ridge_predict(target,columns,model,train)
            pred[model][held]=prediction[held]
            errors[model][blocked]=float(np.mean((target[held]-prediction[held])**2))
    macro={model:float(np.mean(list(mse.values()))) for model,mse in errors.items()}
    micro={model:float(np.mean((target-pred[model])**2)) for model in MODELS}
    largest=max(known,key=lambda b:sum(blocks==b))
    full,_=ridge_predict(target,columns,"B2_land_island_marine",
                         np.ones(len(target),dtype=bool))
    _,fullcoef=ridge_predict(target,columns,"B2_land_island_marine",
                             np.ones(len(target),dtype=bool))
    _,without=ridge_predict(target,columns,"B2_land_island_marine",blocks!=largest)
    diff_marine=macro["B0_baseline"]-macro["B1_marine"]
    diff_land=macro["B1_marine"]-macro["B2_land_island_marine"]
    n_better=sum(errors["B1_marine"][b]>errors["B2_land_island_marine"][b] for b in known)
    largest_improved=errors["B2_land_island_marine"][largest]<errors["B1_marine"][largest]
    full_inter=fullcoef[INTERACTION]
    no_big_inter=without[INTERACTION]
    stable=(full_inter*no_big_inter)>0
    support=diff_land>0 and n_better>=8 and largest_improved and stable
    by_block=[]
    for b in known:
        item={"block_id_250km_polar_stereographic":b,
              "original_pairs":int((blocks==b).sum())}
        for model in MODELS:
            item[model+"_MSE"]=round(errors[model][b],9)
        item["marine_MSE_improvement"]=round(
            errors["B0_baseline"][b]-errors["B1_marine"][b],9)
        item["land_MSE_improvement"]=round(
            errors["B1_marine"][b]-errors["B2_land_island_marine"][b],9)
        by_block.append(item)
    return {
        "status":"EXPLORATORY_OUT_OF_REGION_PREDICTIVE_TEST",
        "source_scope":"original_APBP_v2.3_ADD2025_2026_NSIDC_v6",
        "model_contract":"contracts/APBP_LAND_SEA_ISLAND_MACRO_V6_PRE_EFFECT.md",
        "sample_unit":"same_source_locationID_species_consecutive_surveyed_nest_seasons",
        "model_coefficients_no_confirmation":True,
        "baseline_source_no_missing_as_zero":True,
        "equivalent_to_independent_islands":False,
        "response":"log1p(original measured nests in season t)-log1p(nests in t-1)",
        "CV":"Leave one EPSG3031 250km geographic block out; fixed ridge alpha20",
        "n_heldout_spatial_blocks":len(known),
        "largest_block_id":largest,
        "largest_block_pair_n":int(sum(blocks==largest)),
        "Ridge_alpha":ALPHA,
        "macro_equal_block_MSE":{k:round(v,9) for k,v in macro.items()},
        "micro_pair_weighted_MSE":{k:round(v,9) for k,v in micro.items()},
        "land_over_marine_macro_MSE_improvement":round(diff_land,9),
        "marine_over_baseline_macro_MSE_improvement":round(diff_marine,9),
        "spatial_blocks_land_features_improve":n_better,
        "gate_minimum_blocks_improved":8,
        "largest_block_heldout_land_improved":bool(largest_improved),
        "largest_block_B1_MSE":round(errors["B1_marine"][largest],9),
        "largest_block_B2_MSE":round(errors["B2_land_island_marine"][largest],9),
        "island_rock_marine_threeway_coef_full":round(full_inter,9),
        "island_rock_marine_threeway_coef_omit_largest_block":round(no_big_inter,9),
        "threeway_coef_sign_stable_omit_largest":bool(stable),
        "all_predeclared_H1_support_gates_passed":bool(support),
        "ecological_decision":(
            "TENTATIVE_OUT_OF_REGION_PATTERN_NOT_CAUSAL_PROOF"
            if support else "NOT_SUPPORTED_BY_THIS_DATA"
        ),
        "novel_island_mechanism_demonstrated":False,
        "original_block_holdout_statistics":by_block,
        "structural_limits":[
            "Only 61 repeated nest survey sites with 12 unequal spatial regions",
            "Half of consecutive pairs from one geographical block",
            "Two/three-dimensional island × rock × sea ice interaction confounded by species ranges",
            "ADD modern rock is not measured historical available nest habitat",
            "Static coastline geomatching uncertain for coastal records; often >1km source coordinate uncertainty",
            "G02202 offshore 25km SIC is not breeding fast ice or krill",
            "Original surveys may differ in date and measurement detection effort",
            "CV prediction differences are exploratory and not species causal mechanisms",
        ]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--population",required=True,type=Path)
    ap.add_argument("--medium-rock",required=True,type=Path)
    ap.add_argument("--high-land",required=True,type=Path)
    ap.add_argument("--marine",required=True,type=Path)
    ap.add_argument("--out-json",required=True,type=Path)
    ap.add_argument("--out-csv",required=True,type=Path)
    args=ap.parse_args()
    record={"status":"HOLD_SOURCE_MODEL_OR_SUPPORT","novel_island_mechanism_demonstrated":False}
    try:
        input_data={
            name:verified_csv(getattr(args,{"population":"population",
                                            "medium_rock":"medium_rock",
                                            "high_land":"high_land",
                                            "marine":"marine"}[name]),name)
            for name in SOURCES
        }
        pairs,support=prepare(input_data["population"],input_data["medium_rock"],
                              input_data["high_land"],input_data["marine"])
        if len(pairs)!=406 or pairs.site_id_original.nunique()!=61 or pairs.block250k.nunique()!=12:
            raise ValueError("SAMPLE_STOP prespecified consecutive site panel no longer equals initial 406/61/12")
        out= evaluate(pairs)
        args.out_csv.parent.mkdir(parents=True,exist_ok=True)
        safe_columns=["site_id_original","scientificName_accepted","season","block250k",
                      "nest_numeric_candidate_prev","nest_numeric_candidate_curr",
                      "high_class_curr","rock_2000m_mapped_km2_curr",
                      "sic_25_75km_anomaly_prev","sic_25_75km_anomaly_curr",
                      "sic_75_150km_anomaly_prev","sic_75_150km_anomaly_curr",
                      "measurementAccuracy_original_prev",
                      "measurementAccuracy_original_curr"]
        pairs[safe_columns].to_csv(args.out_csv,index=False)
        record={**out,"original_panel_support":support,
                "derived_matched_panel_SHA256":hashlib.sha256(args.out_csv.read_bytes()).hexdigest(),
                "input_derived_source_csv_SHAs":{k:v[1] for k,v in SOURCES.items()},
                "full_matched_panel_saved_as_CI_artifact_only":True}
    except Exception as exc:
        record["error_type"]=type(exc).__name__
        record["error"]=str(exc)[:650]
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(record,ensure_ascii=False))
    if record["status"].startswith("HOLD"):
        raise SystemExit(2)

if __name__=="__main__":
    main()
