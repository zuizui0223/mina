#!/usr/bin/env python3
"""Outcome-blind observation-method overlap audit for Paper 2."""
from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import pyreadr

MAPPPDR_COMMIT="88c73a507e0921b2541c218c71eaf16721bc6502"
SPECIES=("ADPE","CHPE","GEPE")
WINDOW=(1980,2025)
DIRECT={"ground","aerial","offshore_vessel"}
IMAGE={"ground_photo","aerial_photo","uav","vhr","landsat","sentinel"}


def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        frame=x[expected]
    elif len(x)==1:
        frame=next(iter(x.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(x)}")
    if not isinstance(frame,pd.DataFrame):
        raise TypeError(expected)
    return frame


def family(value)->str:
    if pd.isna(value):
        return "unknown"
    v=str(value)
    if v in DIRECT:
        return "direct"
    if v in IMAGE:
        return "image_based"
    return "other"


def thirds(start:int,end:int):
    width=end-start+1
    cut1=start+(width//3)-1
    cut2=start+(2*width//3)-1
    return (start,cut1),(cut1+1,cut2),(cut2+1,end)


def frozen_units(obs:pd.DataFrame):
    nest=obs[
        obs["species_id"].isin(SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest["season"]=pd.to_numeric(nest["season"],errors="coerce")
    base=[]
    for (site,sp),local in nest.dropna(subset=["year"]).groupby(["site_id","species_id"]):
        years=sorted(set(int(v) for v in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            base.append((str(site),str(sp)))
    if len(base)!=152:
        raise ValueError(f"Gate0 drift: {len(base)}")

    start,end=WINDOW
    first,_,last=thirds(start,end)
    grouped={
        (str(site),str(sp)):local
        for (site,sp),local in nest.groupby(["site_id","species_id"])
    }
    bridged=[]
    for site,sp in base:
        local=grouped[(site,sp)]
        seasons=sorted(set(
            int(v) for v in pd.to_numeric(local["season"],errors="coerce").dropna()
            if start<=int(v)<=end
        ))
        n=len(seasons)
        span=(max(seasons)-min(seasons)) if seasons else 0
        has_first=any(first[0]<=v<=first[1] for v in seasons)
        has_last=any(last[0]<=v<=last[1] for v in seasons)
        if n>=5 and span>=10 and has_first and has_last:
            bridged.append((site,sp))
    if len(bridged)!=107:
        raise ValueError(f"season cohort drift: {len(bridged)} != 107")
    keys=set(bridged)
    cohort=nest[
        nest.apply(lambda r:(str(r["site_id"]),str(r["species_id"])) in keys,axis=1)
        & nest["season"].between(start,end,inclusive="both")
    ].copy()
    return bridged,cohort


def raw_vantage(value)->str:
    return "missing" if pd.isna(value) else str(value)


def accuracy_group(value)->str:
    v=int(value)
    if v==1:
        return "1"
    if v==2:
        return "2"
    return "3-5"


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()

    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    units,cohort=frozen_units(obs)
    cohort["vantage_raw"]=cohort["vantage"].map(raw_vantage)
    cohort["vantage_family"]=cohort["vantage"].map(family)
    cohort["accuracy_group"]=cohort["accuracy"].map(accuracy_group)
    cohort["date_parsed"]=pd.to_datetime(cohort["date"],errors="coerce")

    record_vantage=cohort["vantage_raw"].value_counts().to_dict()
    record_family=cohort["vantage_family"].value_counts().to_dict()
    accuracy_by_family={
        fam:{
            str(k):int(v)
            for k,v in local["accuracy_group"].value_counts().sort_index().items()
        }
        for fam,local in cohort.groupby("vantage_family")
    }

    season_groups=[]
    raw_pair_counts=Counter()
    family_pair_counts=Counter()
    mixed_family_by_species=Counter()
    exact_date_direct_image=0
    within14_direct_image=0
    known_date_direct_image_pairs=0
    repeat_accuracy_groups=Counter()

    for (site,sp,season),local in cohort.groupby(["site_id","species_id","season"]):
        raws=sorted(set(local["vantage_raw"]))
        fams=sorted(set(local["vantage_family"]))
        repeated=len(local)>=2
        if repeated:
            for pair in itertools.combinations(raws,2):
                raw_pair_counts[tuple(sorted(pair))]+=1
            for pair in itertools.combinations(fams,2):
                family_pair_counts[tuple(sorted(pair))]+=1

            for ag,ag_local in local.groupby("accuracy_group"):
                if len(ag_local)>=2:
                    repeat_accuracy_groups[ag]+=1

        direct=local[local["vantage_family"]=="direct"]
        image=local[local["vantage_family"]=="image_based"]
        mixed_di=len(direct)>0 and len(image)>0
        if mixed_di:
            mixed_family_by_species[str(sp)]+=1
            for _,drow in direct.iterrows():
                for _,irow in image.iterrows():
                    d1=drow["date_parsed"]; d2=irow["date_parsed"]
                    if pd.notna(d1) and pd.notna(d2):
                        known_date_direct_image_pairs+=1
                        delta=abs((d1-d2).days)
                        if delta==0:
                            exact_date_direct_image+=1
                        if delta<=14:
                            within14_direct_image+=1

        season_groups.append({
            "site_id":str(site),
            "species_id":str(sp),
            "season":int(season),
            "n_records":int(len(local)),
            "n_raw_vantages":len(raws),
            "raw_vantages":";".join(raws),
            "n_vantage_families":len(fams),
            "vantage_families":";".join(fams),
            "mixed_direct_image":bool(mixed_di),
            "any_known_date":bool(local["date_parsed"].notna().any()),
        })

    group_frame=pd.DataFrame(season_groups)

    unit_family_change={}
    for (site,sp),local in cohort.groupby(["site_id","species_id"]):
        fam_by_season=(
            local.groupby("season")["vantage_family"]
            .agg(lambda s: tuple(sorted(set(s))))
        )
        nonunknown=set(
            fam for fams in fam_by_season
            for fam in fams
            if fam!="unknown"
        )
        unit_family_change[f"{site}|{sp}"]={
            "families":sorted(nonunknown),
            "has_direct_and_image":bool({"direct","image_based"}<=nonunknown),
            "seasons":int(len(fam_by_season))
        }

    mixed_di_groups=int(group_frame["mixed_direct_image"].sum())
    species_mixed={sp:int(mixed_family_by_species.get(sp,0)) for sp in SPECIES}
    mean_offset_identified=(
        mixed_di_groups>=20
        and sum(v>=5 for v in species_mixed.values())>=2
    )

    acc_counts={k:int(repeat_accuracy_groups.get(k,0)) for k in ("1","2","3-5")}
    separate_acc=all(v>=20 for v in acc_counts.values())

    raw_connected_to_ground={}
    cats=sorted(set(cohort["vantage_raw"]))
    for cat in cats:
        if cat=="ground":
            raw_connected_to_ground[cat]=None
        else:
            raw_connected_to_ground[cat]=int(
                raw_pair_counts.get(tuple(sorted(("ground",cat))),0)
            )

    result={
        "schema_version":1,
        "audit_id":"mina-paper2-observation-overlap-audit-v1",
        "mapppdr_commit":MAPPPDR_COMMIT,
        "primary_time_field":"season",
        "primary_window":[1980,2025],
        "bridged_site_species_units":107,
        "records_in_primary_cohort_window":int(len(cohort)),
        "record_vantage_counts":{str(k):int(v) for k,v in record_vantage.items()},
        "record_family_counts":{str(k):int(v) for k,v in record_family.items()},
        "accuracy_group_counts_by_family":accuracy_by_family,
        "site_species_season_groups":int(len(group_frame)),
        "repeated_record_groups":int((group_frame["n_records"]>=2).sum()),
        "mixed_raw_vantage_groups":int((group_frame["n_raw_vantages"]>=2).sum()),
        "mixed_family_groups":int((group_frame["n_vantage_families"]>=2).sum()),
        "mixed_direct_image_groups":mixed_di_groups,
        "mixed_direct_image_groups_by_species":species_mixed,
        "direct_image_pairs_with_known_dates":known_date_direct_image_pairs,
        "direct_image_pairs_exact_date":exact_date_direct_image,
        "direct_image_pairs_within_14_days":within14_direct_image,
        "raw_vantage_pair_group_counts":{
            "|".join(pair):int(v)
            for pair,v in sorted(raw_pair_counts.items())
        },
        "raw_vantage_same_season_links_to_ground":raw_connected_to_ground,
        "repeated_observation_groups_by_accuracy_class":acc_counts,
        "unit_family_change":{
            "units_with_direct_and_image_across_seasons":int(
                sum(v["has_direct_and_image"] for v in unit_family_change.values())
            ),
            "unit_details":unit_family_change
        },
        "decision":{
            "primary_direct_vs_image_mean_offset":bool(mean_offset_identified),
            "mean_offset_rule":"at least 20 mixed direct-image season groups overall and at least two species with >=5 groups",
            "accuracy_variance_model":(
                "separate_1_2_3to5" if separate_acc else "split_1_vs_2to5"
            ),
            "raw_vantage_offsets_primary":False,
            "missing_vantage_exclusion_sensitivity_required":True,
            "ground_only_sensitivity_required":True,
            "no_count_magnitudes_opened":True
        },
        "season_group_csv":a.out_csv.name
    }

    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    group_frame.to_csv(a.out_csv,index=False)
    print(json.dumps({k:v for k,v in result.items() if k!="unit_family_change"},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
