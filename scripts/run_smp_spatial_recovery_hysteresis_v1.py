#!/usr/bin/env python3
"""Frozen Stage-C paired abandonment/recolonization hysteresis test."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.gate_smp_trend_balance_v1 import _prepare_raw
from scripts.gate_smp_master_site_support_v1 import _norm


SEED=20261005
BOOT_B=9999
RANDOM_SIGN_B=100000


def transition_midpoint(parent_excl_a:float,parent_excl_b:float)->float:
    return 0.5*(np.log1p(parent_excl_a)+np.log1p(parent_excl_b))


def spell_effect(matrix:pd.DataFrame,site:str,spell:dict)->dict:
    years=[int(spell[k]) for k in ("abandon_from","abandon_to","recolonize_from","recolonize_to")]
    for y in years:
        if y not in matrix.index:
            raise ValueError(f"spell year {y} missing from matrix")
    if site not in matrix.columns:
        raise ValueError(f"spell site {site} missing from matrix")

    def parent_excl(y:int)->float:
        row=matrix.loc[y].astype(float)
        return float(row.sum()-float(row.loc[site]))

    ae=transition_midpoint(parent_excl(years[0]),parent_excl(years[1]))
    ac=transition_midpoint(parent_excl(years[2]),parent_excl(years[3]))
    return {
        "abandon_state":float(ae),
        "recolonize_state":float(ac),
        "H":float(ac-ae),
    }


def aggregate(frame:pd.DataFrame)->dict:
    site=(
        frame.groupby(["species","master_site","site_id"],as_index=False)["H"]
        .mean().rename(columns={"H":"site_mean_H"})
    )
    master=(
        site.groupby(["species","master_site"],as_index=False)["site_mean_H"]
        .mean().rename(columns={"site_mean_H":"master_mean_H"})
    )
    species=(
        master.groupby("species",as_index=False)["master_mean_H"]
        .mean().rename(columns={"master_mean_H":"species_mean_H"})
    )
    vals=species["species_mean_H"].to_numpy(float)
    T=float(vals.mean())

    s=len(vals)
    if s<=20:
        stats=[]
        for signs in itertools.product((-1.0,1.0),repeat=s):
            stats.append(float(np.mean(vals*np.asarray(signs,float))))
        stats=np.asarray(stats,float)
        p=float((np.sum(stats>=T))/len(stats))
        sign_mode="exact"
        sign_n=int(len(stats))
    else:
        rng=np.random.default_rng(SEED)
        stats=np.empty(RANDOM_SIGN_B,float)
        for i in range(RANDOM_SIGN_B):
            signs=rng.choice(np.array([-1.0,1.0]),size=s,replace=True)
            stats[i]=float(np.mean(vals*signs))
        p=float((1+np.sum(stats>=T))/(RANDOM_SIGN_B+1))
        sign_mode="monte_carlo"
        sign_n=RANDOM_SIGN_B

    rng=np.random.default_rng(SEED+17)
    boot=np.empty(BOOT_B,float)
    for i in range(BOOT_B):
        sample=rng.choice(vals,size=s,replace=True)
        boot[i]=float(np.mean(sample))
    ci=[float(np.quantile(boot,0.025)),float(np.quantile(boot,0.975))]

    return {
        "primary_T_species_balanced_mean_H":T,
        "species_count":int(s),
        "species_positive_H":int(np.sum(vals>0)),
        "sign_flip":{
            "mode":sign_mode,
            "replicates_or_exact_states":sign_n,
            "one_sided_p":p,
        },
        "species_bootstrap_95":ci,
        "supported":bool(T>0 and p<=0.05),
        "site_means":site.to_dict(orient="records"),
        "master_means":master.to_dict(orient="records"),
        "species_means":species.to_dict(orient="records"),
    }


def run(input_path:Path,structural_json:Path,cycle_json:Path,*,assume_whole_colony_extract:bool=False)->tuple[dict,pd.DataFrame]:
    structural=json.loads(structural_json.read_text(encoding="utf-8"))
    cycles=json.loads(cycle_json.read_text(encoding="utf-8"))
    if not structural.get("decision",{}).get("structural_gate_passed"):
        raise ValueError("structural gate did not pass")
    if not cycles.get("decision",{}).get("hysteresis_magnitude_execution_authorized"):
        raise ValueError("state-only hysteresis support gate did not pass")

    x=_prepare_raw(input_path,assume_whole_colony_extract=assume_whole_colony_extract)

    panel_map={
        (str(p["species"]),_norm(p["master_site"]),str(p["unit"])):p
        for p in structural["eligible_panels"]
    }
    cache={}
    rows=[]
    for sp in cycles["completed_spells"]:
        key=(str(sp["species"]),_norm(sp["master_site"]),str(sp["unit"]))
        if key not in panel_map:
            raise ValueError(f"cycle panel not in frozen roster: {key}")
        if key not in cache:
            panel=panel_map[key]
            roster=[str(v) for v in panel["retained_site_ids"]]
            years=[int(v) for v in panel["complete_years"]]
            g=x[
                x["_species"].eq(key[0])
                & x["_master_norm"].eq(key[1])
                & x["_unit"].eq(key[2])
                & x["_site_id"].isin(roster)
                & x["year"].isin(years)
            ].copy()
            mat=(
                g.pivot(index="year",columns="_site_id",values="_count")
                .reindex(index=years,columns=roster)
            )
            if mat.isna().any().any():
                raise ValueError(f"count matrix drift: {key}")
            cache[key]=mat.astype(float)
        eff=spell_effect(cache[key],str(sp["site_id"]),sp)
        rows.append({**sp,**eff})

    frame=pd.DataFrame(rows)
    macro=aggregate(frame)
    result={
        "schema_version":1,
        "analysis_id":"mina-smp-spatial-recovery-hysteresis-effect-v1",
        "status":"first_and_only_frozen_magnitude_execution",
        "spell_count":int(len(frame)),
        "macro":macro,
        "decision":{
            "spatial_recovery_hysteresis_supported":bool(macro["supported"])
        },
        "boundary":[
            "H>0 demonstrates history-dependent spatial recovery at retained SiteIDs, not a unique social mechanism.",
            "The focal SiteID is excluded from the parent abundance used at both transitions.",
            "Stable site pairing does not remove time-varying habitat or disturbance confounding.",
            "No first-colonization events enter the primary paired test."
        ]
    }
    return result,frame


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--structural-json",required=True,type=Path)
    p.add_argument("--cycle-json",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-spells-csv",required=True,type=Path)
    p.add_argument("--assume-whole-colony-extract",action="store_true")
    a=p.parse_args()
    result,frame=run(a.input,a.structural_json,a.cycle_json,assume_whole_colony_extract=a.assume_whole_colony_extract)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    frame.to_csv(a.out_spells_csv,index=False)
    print(json.dumps({k:v for k,v in result.items() if k!="macro"},indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in result["macro"].items() if not k.endswith("_means")},indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
