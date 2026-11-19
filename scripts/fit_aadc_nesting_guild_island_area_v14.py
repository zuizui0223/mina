#!/usr/bin/env python3
"""V14 first original eight-seabird guild-by-island terrestrial-area test.

Only ORIGINAL reported breeding presence P and explicit breeding absence A
(never NR) from real AADC site×species×breeding-season observation sheets.
Species nesting guilds and nested statistical models were fixed in the V14
contract before slopes/results. Geographic heldouts include whole sites,
not repeated observations from one source station.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from sklearn.linear_model import LogisticRegression

ORIGINAL_SITE_SHA="48c716c38c41a054eefc20c03de3c21d75047049e6e277d471d9b9135aab7da5"
ORIGINAL_SURVEYS_SHA="dba39d79f6309f90e23e896415177ea75086aaf2ecb5523256e48895e95dfc5c"
REGION_SIZE_M=250000
MIN_SITE_PER_BLOCK=5
MIN_BLOCKS=8
MIN_ROWS=200
REG_C=0.3
GUILDS={
    "SGP":"OPEN",
    "SK":"OPEN",
    "AP":"LEDGE",
    "CP":"LEDGE",
    "SF":"LEDGE",
    "SP":"CREVICE",
    "WSP":"CREVICE",
}
SPECIES=tuple(sorted(GUILDS))
UNORDERED_GUILDS=("OPEN","LEDGE","CREVICE")
BASE=(
    "season_year","latitude","longitude_sin","longitude_cos",
    "log_station_distance","station_distance_missing",
    "expert_occurrence_Y","expert_species_Y","expert_site_Y",
    "vantage_A","vantage_S",
    *("species_"+name for name in SPECIES if name!="AP"),
)
PHYSICAL=BASE+("log_site_area","island","island_log_site_area")
GUILD=PHYSICAL+(
    "ledge_logarea","crevice_logarea",
    "ledge_island","crevice_island",
    "ledge_island_logarea","crevice_island_logarea",
)
MODELS={"B0_survey_species_geography":BASE,
        "B1_site_area_island":PHYSICAL,
        "B2_nesting_mode_area_island":GUILD}
CONTINUOUS=set((
    "season_year","latitude","longitude_sin","longitude_cos",
    "log_station_distance","log_site_area","island_log_site_area",
    "ledge_logarea","crevice_logarea",
    "ledge_island_logarea","crevice_island_logarea",
))
TESTED_TRIPLE="crevice_island_logarea"


def checked_csv(path:Path,expected:str) -> pd.DataFrame:
    raw=path.read_bytes()
    actual=hashlib.sha256(raw).hexdigest()
    if actual!=expected:
        raise ValueError("SOURCE_STOP exact original first-party AADC derived CSV SHA drift")
    return pd.read_csv(path,dtype={"geog_site_id":str,"species_code":str,
                                   "season":str},low_memory=False)


def frame_data(surveys:pd.DataFrame,geog:pd.DataFrame):
    needed={
        "geog_site_id","species_code","season","occurrence",
        "occurrence_cert_cat","certainty_lookup","vantage",
        "occurrence_expert_validation","site_expert_validation",
        "species_expert_validation",
    }
    if not needed.issubset(surveys.columns):
        raise ValueError("SOURCE_STOP incomplete original source survey roster")
    if geog.geog_site_id.duplicated().any():
        raise ValueError("SOURCE_STOP original geographic site IDs not unique")
    df=surveys.loc[surveys.species_code.isin(SPECIES)].copy()
    # Preserve the exact source 6-digit YYYY(YY+1) breeding-season code.
    season=df.season.fillna("").str.strip()
    fmt=season.str.fullmatch(r"(?:18|19|20)\d{4}",na=False)
    first_year=pd.to_numeric(season.str[:4],errors="coerce")
    end_year=pd.to_numeric(season.str[4:6],errors="coerce")
    chronology=fmt & end_year.eq((first_year+1)%100)
    in_period=chronology & first_year.between(1980,2020)
    n_source_after_year=int(in_period.sum())
    source=df.copy()
    df=df.loc[in_period].copy()
    df["season_year"]=first_year.loc[df.index].astype("int64")

    # Drop ALL original repeated same-site/species/season groups, including
    # P/A conflicts, before selecting direct observed P/A statuses.
    key=["geog_site_id","species_code","season"]
    group_sizes=df.groupby(key,dropna=False).size().rename("n_source_reports")
    duplicate=group_sizes[group_sizes>1]
    conflict=0
    for group,_ in duplicate.items():
        row=df.loc[(df.geog_site_id==group[0]) &
                   (df.species_code==group[1]) &
                   (df.season==group[2])]
        if row.occurrence.nunique()>1:
            conflict+=1
    unique=group_sizes[group_sizes==1].reset_index()[key]
    # The LEFT source deliberately still includes duplicate original rows;
    # the right-side singleton keys are unique and exclude their entire group.
    df=df.merge(unique,on=key,how="inner",validate="many_to_one")
    if df.duplicated(key).any():
        raise ValueError("SOURCE_STOP original source duplicate survey survived exclusion")
    status=df.occurrence.isin(("P","A"))
    direct=df.loc[status].copy()
    category=pd.to_numeric(direct.occurrence_cert_cat,errors="coerce")
    consistent=(
        ((direct.occurrence=="P") & category.eq(5)) |
        ((direct.occurrence=="A") & category.eq(4))
    ) & direct.certainty_lookup.eq("EXACT_CERTAINTY_RULE")
    rejected_cert=int((~consistent).sum())
    direct=direct.loc[consistent].copy()
    direct["y"]=direct.occurrence.eq("P").astype(int)

    geocols=[
        "geog_site_id","sub_group","geog_site_feature",
        "geog_site_area","geog_site_area_cat3",
        "latitude","longitude","distance_station","distance_inland_coast"
    ]
    direct=direct.merge(
        geog[geocols],on="geog_site_id",how="left",
        validate="many_to_one",suffixes=("","_geo"),
    )
    direct["area"]=pd.to_numeric(direct.geog_site_area,errors="coerce")
    direct["lat"]=pd.to_numeric(direct.latitude,errors="coerce")
    direct["lon"]=pd.to_numeric(direct.longitude,errors="coerce")
    direct["stationdist"]=pd.to_numeric(direct.distance_station,errors="coerce")
    feature=direct.geog_site_feature.fillna("").str.strip().str.lower()
    valid=(
        feature.isin(("island","continent")) &
        direct.area.gt(0) & np.isfinite(direct.area) &
        direct.lat.between(-90,-60) & direct.lon.between(-180,180)
    )
    invalid_geo=int((~valid).sum())
    direct=direct.loc[valid].copy()
    direct["guild"]=direct.species_code.map(GUILDS)
    direct["island"]=direct.geog_site_feature.str.lower().eq("island").astype(int)
    direct["log_site_area"]=np.log10(direct.area)
    direct["station_distance_missing"]=(~np.isfinite(direct.stationdist) |
                                        direct.stationdist.lt(0)).astype(float)
    direct["log_station_distance"]=np.log1p(direct.stationdist.mask(
        direct.station_distance_missing.eq(1),np.nan))
    direct["expert_occurrence_Y"]=direct.occurrence_expert_validation.eq("Y").astype(float)
    direct["expert_species_Y"]=direct.species_expert_validation.eq("Y").astype(float)
    direct["expert_site_Y"]=direct.site_expert_validation.eq("Y").astype(float)
    direct["vantage_A"]=direct.vantage.eq("A").astype(float)
    direct["vantage_S"]=direct.vantage.eq("S").astype(float)

    x,y=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True).transform(
        direct.lon.to_numpy(dtype=float),direct.lat.to_numpy(dtype=float)
    )
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("SOURCE_STOP original geographic coordinate projection invalid")
    direct["block250km"]=[
        f"{math.floor(a/REGION_SIZE_M)}_{math.floor(b/REGION_SIZE_M)}"
        for a,b in zip(x,y)
    ]
    supported=direct.groupby("block250km").geog_site_id.nunique()
    eligible_blocks=set(supported[supported>=MIN_SITE_PER_BLOCK].index)
    sample=direct.loc[direct.block250km.isin(eligible_blocks)].copy()
    if sample.empty:
        raise ValueError("SAMPLE_STOP no original P/A surveys in eligible independent regions")
    # Repeated annual studies of one site+species do NOT produce 10 new islands.
    n_per_original_site_species=sample.groupby(
        ["geog_site_id","species_code"]).geog_site_id.transform("size")
    sample["site_species_weight"]=1./n_per_original_site_species
    summary={
        "raw_eight_flying_species_search_rows":len(source),
        "original_season_1980_2020_rows":n_source_after_year,
        "original_same_site_species_season_duplicate_groups":len(duplicate),
        "original_observation_rows_in_duplicate_groups":int(duplicate.sum()),
        "original_source_status_conflict_groups_dropped":conflict,
        "original_P_or_direct_A_after_duplicate_drops":int(len(df.loc[status])),
        "status_or_certainty_mismatch_removed":rejected_cert,
        "original_geography_missing_or_invalid_removed":invalid_geo,
        "strict_direct_P_A_site_species_season_rows_before_block_gate":len(direct),
        "eligible_region_site_species_season_rows":len(sample),
        "eligible_original_geographic_site_IDs":int(sample.geog_site_id.nunique()),
        "eligible_site_species_histories":int(
            sample.groupby(["geog_site_id","species_code"]).ngroups),
        "eligible_spatial_blocks_ge5_unique_sites":int(sample.block250km.nunique()),
        "eligible_region_original_site_counts":{
            str(k):int(v) for k,v in supported.loc[list(eligible_blocks)].items()
        },
        "eligible_source_species_counts":sample.species_code.value_counts().to_dict(),
        "eligible_direct_P_A_statuses":sample.occurrence.value_counts().to_dict(),
        "eligible_island_vs_continent_report_counts":sample.geog_site_feature.value_counts().to_dict(),
        "eligible_island_vs_continent_site_counts":sample.groupby(
            "geog_site_feature").geog_site_id.nunique().to_dict(),
        "source_sites_across_island_and_mainland":direct.groupby(
            "geog_site_feature").geog_site_id.nunique().to_dict(),
        "source_excluded_nonreporting_not_zero":True,
        "rare_yearly_original_source_events_not_independent_islands":True,
        "original_area_unit":"source geog_site_area; log10 units, source not reinterpreted as new land availability",
    }
    return sample,summary


def feature_arrays(data):
    n=len(data)
    lon=np.deg2rad(data.lon.to_numpy(dtype=float))
    sp=data.species_code
    guild=data.guild
    year=(data.season_year.to_numpy(dtype=float)-2000)/20
    area=data.log_site_area.to_numpy(dtype=float)
    island=data.island.to_numpy(dtype=float)
    ledge=guild.eq("LEDGE").to_numpy(dtype=float)
    crevice=guild.eq("CREVICE").to_numpy(dtype=float)
    source={
        "season_year":year,
        "latitude":data.lat.to_numpy(dtype=float),
        "longitude_sin":np.sin(lon),
        "longitude_cos":np.cos(lon),
        "log_station_distance":data.log_station_distance.to_numpy(dtype=float),
        "station_distance_missing":data.station_distance_missing.to_numpy(dtype=float),
        "expert_occurrence_Y":data.expert_occurrence_Y.to_numpy(dtype=float),
        "expert_species_Y":data.expert_species_Y.to_numpy(dtype=float),
        "expert_site_Y":data.expert_site_Y.to_numpy(dtype=float),
        "vantage_A":data.vantage_A.to_numpy(dtype=float),
        "vantage_S":data.vantage_S.to_numpy(dtype=float),
        **{f"species_{t}":sp.eq(t).to_numpy(dtype=float)
           for t in SPECIES if t!="AP"},
        "log_site_area":area,
        "island":island,
        "island_log_site_area":island*area,
        "ledge_logarea":ledge*area,
        "crevice_logarea":crevice*area,
        "ledge_island":ledge*island,
        "crevice_island":crevice*island,
        "ledge_island_logarea":ledge*island*area,
        "crevice_island_logarea":crevice*island*area,
    }
    if any(len(v)!=n for v in source.values()):
        raise ValueError("FEATURE_STOP unequal predeclared feature lengths")
    return source


def model_fit(y,columns,model,training,weights):
    names=MODELS[model]
    raw=np.column_stack([columns[name] for name in names]).astype(float)
    train=raw[training]
    # All missing values are predeclared station-distance input only.
    # Fit median + all scales from OTHER geographical blocks only.
    median=np.nanmedian(train,axis=0)
    median[~np.isfinite(median)]=0
    full=np.where(np.isfinite(raw),raw,median)
    avgs=np.zeros(len(names),dtype=float)
    scales=np.ones(len(names),dtype=float)
    for i,name in enumerate(names):
        if name in CONTINUOUS:
            avgs[i]=float(np.mean(full[training,i]))
            scales[i]=float(np.std(full[training,i]))
            if scales[i]<1e-10:scales[i]=1
    design=(full-avgs)/scales
    if len(np.unique(y[training]))!=2:
        raise ValueError("MODEL_STOP training original field survey split contains one response class")
    training_weights=weights[training]
    # Preserve same site/species weighting with average effective training
    # observation weight one for fixed, non-tuned regularization.
    training_weights=training_weights/float(np.mean(training_weights))
    estimator=LogisticRegression(C=REG_C,solver="lbfgs",max_iter=500,tol=1e-6)
    estimator.fit(design[training],y[training],sample_weight=training_weights)
    probability=estimator.predict_proba(design)[:,1]
    beta={name:float(estimator.coef_[0,i]/scales[i])
          for i,name in enumerate(names)}
    return probability,beta


def weighted_brier(observed,predicted,weight):
    return float(np.sum(weight*(observed-predicted)**2)/np.sum(weight))


def spatial_cv(data):
    y=data.y.to_numpy(dtype=int)
    w=data.site_species_weight.to_numpy(dtype=float)
    x=feature_arrays(data)
    groups=data.block250km.to_numpy(dtype=str)
    blocks=sorted(set(groups))
    if len(blocks)<MIN_BLOCKS or len(data)<MIN_ROWS:
        raise ValueError("MODEL_STOP too few original geographic observation blocks/rows")
    results={name:{"by_block":{}, "prediction":np.full(len(y),np.nan)} for name in MODELS}
    for block in blocks:
        train=groups!=block
        held=~train
        for name in MODELS:
            predicted,_=model_fit(y,x,name,train,w)
            results[name]["prediction"][held]=predicted[held]
            results[name]["by_block"][block]=weighted_brier(y[held],predicted[held],w[held])
    mean_scores={k:float(np.mean(list(result["by_block"].values())))
                 for k,result in results.items()}
    micro_scores={k:weighted_brier(y,result["prediction"],w)
                  for k,result in results.items()}
    # Reporting only: retain the original history-weighted score and expose
    # the contracted raw-row average with its different denominator.
    original_row_scores={
        k:float(np.mean((y-result["prediction"])**2))
        for k,result in results.items()
    }
    original_row_block_scores={
        k:{block:float(np.mean((y[groups==block]-
                                result["prediction"][groups==block])**2))
           for block in blocks}
        for k,result in results.items()
    }
    block_improv={
        block:results["B1_site_area_island"]["by_block"][block]
              -results["B2_nesting_mode_area_island"]["by_block"][block]
        for block in blocks
    }
    block_counts=data.groupby("block250km").geog_site_id.nunique()
    largest=max(blocks,key=lambda x:(block_counts[x],sum(groups==x)))
    _,full=model_fit(y,x,"B2_nesting_mode_area_island",
                     np.ones(len(y),dtype=bool),w)
    _,omit=model_fit(y,x,"B2_nesting_mode_area_island",groups!=largest,w)
    paired_robust=full[TESTED_TRIPLE]*omit[TESTED_TRIPLE]>0
    return {
        "all_eligible_geographic_block_ids":blocks,
        "n_spatial_blocks":len(blocks),
        "original_sites_per_block":block_counts.astype(int).to_dict(),
        "original_rows_per_block":data.groupby("block250km").size().astype(int).to_dict(),
        "site_species_histories_per_block":data.drop_duplicates(
            ["geog_site_id","species_code"]).groupby("block250km").size().astype(int).to_dict(),
        "largest_heldout_block":largest,
        "largest_block_definition":"unique_sites_then_original_rows",
        "macro_equal_geographic_block_Brier":mean_scores,
        "weighted_observation_Brier":micro_scores,
        "weighted_observation_Brier_definition":"global_site_species_history_weighted_mean",
        "original_row_Brier":original_row_scores,
        "site_species_weighted_Brier_by_block":{
            k:result["by_block"] for k,result in results.items()},
        "original_row_Brier_by_block":original_row_block_scores,
        "B1_minus_B2_macro_Brier_improvement":
            mean_scores["B1_site_area_island"]-mean_scores["B2_nesting_mode_area_island"],
        "B0_minus_B1_macro_Brier_improvement":
            mean_scores["B0_survey_species_geography"]-mean_scores["B1_site_area_island"],
        "B2_guild_land_gain_by_block":block_improv,
        "n_geographic_blocks_where_guild_improves":sum(g>0 for g in block_improv.values()),
        "largest_source_block_guild_improves":block_improv[largest]>0,
        "full_model_crevice_x_island_x_area_coefficient":full[TESTED_TRIPLE],
        "without_largest_block_crevice_x_island_x_area_coefficient":omit[TESTED_TRIPLE],
        "crevice_triple_coefficient_sign_stable":bool(paired_robust),
        "raw_model_original_input_standardisation_training_fold_only":True,
        "novel_causal_island_biogeography_effect":False,
    }


def physical_overlap_gate(data):
    conditions={}
    success=True
    for guild in UNORDERED_GUILDS:
        groups={}
        for feature in ("island","continent"):
            part=data[(data.guild==guild)&
                      (data.geog_site_feature==feature)].drop_duplicates("geog_site_id")
            groups[feature]={
                "distinct_original_geographic_sites":len(part),
                "q25_log10_raw_site_area":float(part.log_site_area.quantile(.25)) if len(part) else None,
                "q75_log10_raw_site_area":float(part.log_site_area.quantile(.75)) if len(part) else None,
            }
        left,right=groups["island"],groups["continent"]
        if left["distinct_original_geographic_sites"]<8 or right["distinct_original_geographic_sites"]<8:
            ok=False;overlap=0
        else:
            overlap=min(left["q75_log10_raw_site_area"],right["q75_log10_raw_site_area"])-max(
                left["q25_log10_raw_site_area"],right["q25_log10_raw_site_area"])
            ok=overlap>0
        conditions[guild]={"site_classes":groups,
                            "raw_area_IQR_overlap":float(overlap),
                            "guild_land_comparison_identifiable":bool(ok)}
        success &= bool(ok)
    return bool(success),conditions


def sensitivity(data,subset_name):
    if subset_name=="EXPERT_VALIDATED":
        sample=data.loc[data.occurrence_expert_validation.eq("Y")].copy()
    elif subset_name=="GROUND_ONLY":
        sample=data.loc[data.vantage.eq("G")].copy()
    else:
        raise ValueError("MODEL_STOP unexpected sensitivity")
    eligible=sample.groupby("block250km").geog_site_id.nunique()
    sample=sample.loc[sample.block250km.isin(
        eligible[eligible>=MIN_SITE_PER_BLOCK].index)].copy()
    if len(sample)<MIN_ROWS or sample.block250km.nunique()<MIN_BLOCKS:
        return {"status":"HOLD_SUBSET_REGIONAL_SAMPLE_SUPPORT",
                "eligible_rows":len(sample),
                "eligible_blocks":int(sample.block250km.nunique()),
                "eligible_sites":int(sample.geog_site_id.nunique())}
    counts=sample.groupby(["geog_site_id","species_code"]).geog_site_id.transform("size")
    sample["site_species_weight"]=1/counts
    return {"status":"SENSITIVITY_EVALUATED", **spatial_cv(sample)}


def analyse(surveys,geog):
    dataset,source_qa=frame_data(surveys,geog)
    report={
        "status":"V14_EXPLORATORY_SURVEY_CONDITIONAL_SITE_NESTING_GUILD_TEST",
        "study":"Eight Antarctic land nesting seabirds, primary seven flying taxa",
        "source_DOI":"10.26179/5n29-r073",
        "original_2025_geographic_site_dataset_rows":len(geog),
        "source_frozen_before_effects":"contracts/AADC_EAST_ANTARCTIC_NESTING_GUILD_AREA_V14.md",
        "source_qa":source_qa,
        "guild_definition":GUILDS,
        "original_abstract_count_status":"Y=1 direct P, Y=0 direct A; NR strictly discarded",
        "positive_or_negative_not_all_surveyed_potential_sites":True,
        "novel_island_causal_mechanism_demonstrated":False,
    }
    if len(dataset)<MIN_ROWS or dataset.block250km.nunique()<MIN_BLOCKS:
        report["status"]="HOLD_INSUFFICIENT_INDEPENDENT_GEOGRAPHIC_SUPPORT"
        return report,dataset
    area_ok,overlap=physical_overlap_gate(dataset)
    report["fixed_guild_by_land_area_IQR_overlap_gate"]=overlap
    model=spatial_cv(dataset)
    blocks=len(model["all_eligible_geographic_block_ids"])
    support=(
        model["B1_minus_B2_macro_Brier_improvement"]>0 and
        model["n_geographic_blocks_where_guild_improves"]>=math.ceil(2*blocks/3) and
        model["largest_source_block_guild_improves"] and
        model["crevice_triple_coefficient_sign_stable"] and area_ok
    )
    report.update({
        "primary_regional_holdout_comparison":model,
        "prespecified_area_overlap_gate_pass":bool(area_ok),
        "all_predefined_descriptive_guild_conditions_supported":bool(support),
        "scientific_decision":(
            "TENTATIVE_SURVEY_CONDITIONAL_GUILD_BY_ISLAND_AREA_PATTERN"
            if support else "NOT_SUPPORTED_OR_UNIDENTIFIABLE"
        ),
        "expert_validated_only":sensitivity(dataset,"EXPERT_VALIDATED"),
        "ground_vantage_only":sensitivity(dataset,"GROUND_ONLY"),
        "interpretation_limits":[
            "Original source authors already published survey uncertainty, known occupancy and 2025 richness maps",
            "The dependent data are only explicitly P/A reports conditional on searched geographic sites",
            "Original nonreporting NR, including medium-certainty unreporting, is NOT a biological zero",
            "Island is source terrestrial island feature and continent means exposed continental rock, not all Antarctica",
            "Area is static mapped GIS feature size, not measured future available nesting capacity",
            "Species nesting guild is a coarse mode rather than observed substrate at each individual nest",
            "Survey nonrandomness, nesting detectability, source expert validation and seasonal changes remain confounding",
            "Repeated original source sites or seasons never represent independent Antarctic islands",
            "Out-of-region prediction cannot show competition, causal island isolation or colony formation",
        ]
    })
    return report,dataset


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--sites",type=Path,required=True)
    parser.add_argument("--surveys",type=Path,required=True)
    parser.add_argument("--json",type=Path,required=True)
    parser.add_argument("--csv",type=Path,required=True)
    args=parser.parse_args()
    receipt={"status":"HOLD_ORIGINAL_SURVEY_MODEL_OR_SUPPORT",
             "novel_island_causal_mechanism_demonstrated":False}
    try:
        site=checked_csv(args.sites,ORIGINAL_SITE_SHA)
        survey=checked_csv(args.surveys,ORIGINAL_SURVEYS_SHA)
        receipt,data=analyse(survey,site)
        args.csv.parent.mkdir(parents=True,exist_ok=True)
        data.to_csv(args.csv,index=False)
        receipt["original_source_derived_csv_sha256"]={
            "geography":ORIGINAL_SITE_SHA,"surveys":ORIGINAL_SURVEYS_SHA}
        receipt["eligible_survey_rows_SHA256"]=hashlib.sha256(args.csv.read_bytes()).hexdigest()
        receipt["source_original_derived_sample_only_in_Actions_artifact"]=True
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:700]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
