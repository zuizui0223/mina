#!/usr/bin/env python3
"""Frozen Stage-C paired abandonment/recolonization hysteresis test.

Primary support requires:
1) positive species-balanced H with the frozen species sign-flip test; and
2) positive H beyond a structured trajectory-phase circular-shift null.
"""
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
PHASE_B=9999


def transition_midpoint(parent_excl_a:float,parent_excl_b:float)->float:
    return 0.5*(np.log1p(parent_excl_a)+np.log1p(parent_excl_b))


def spell_effect(matrix:pd.DataFrame,site:str,spell:dict)->dict:
    years=[int(spell[k]) for k in ("abandon_from","abandon_to","recolonize_from","recolonize_to")]
    for y in years:
        if y not in matrix.index:
            raise ValueError(f"spell year {y} missing from matrix")
    if site not in matrix.columns:
        raise ValueError(f"spell site {site} missing from matrix")

    # Magnitude-opening execution must reproduce the categorical Stage-B spell.
    if not (float(matrix.loc[years[0],site])>0):
        raise ValueError("abandon_from is not positive in opened magnitude data")
    if not (float(matrix.loc[years[1],site])==0):
        raise ValueError("abandon_to is not explicit zero in opened magnitude data")
    if not (float(matrix.loc[years[2],site])==0):
        raise ValueError("recolonize_from is not explicit zero in opened magnitude data")
    if not (float(matrix.loc[years[3],site])>0):
        raise ValueError("recolonize_to is not positive in opened magnitude data")

    def parent_excl(y:int)->float:
        row=matrix.loc[y].astype(float)
        value=float(row.sum()-float(row.loc[site]))
        if value<0:
            raise ValueError("negative leave-one-site-out parent abundance")
        return value

    ae=transition_midpoint(parent_excl(years[0]),parent_excl(years[1]))
    ac=transition_midpoint(parent_excl(years[2]),parent_excl(years[3]))
    return {
        "abandon_state":float(ae),
        "recolonize_state":float(ac),
        "H":float(ac-ae),
    }


def hierarchy_weights(frame:pd.DataFrame)->np.ndarray:
    """Linear weights reproducing spell -> Site -> MasterSite -> species averaging."""
    d=frame.reset_index(drop=True).copy()
    if d.empty:
        raise ValueError("empty spell frame")

    site_cols=["species","master_site","unit","site_id"]
    panel_cols=["species","master_site","unit"]

    n_species=int(d["species"].nunique())
    if n_species<=0:
        raise ValueError("no species")

    site_spell_n=d.groupby(site_cols)["spell_id"].transform("count").astype(float)

    site_table=d[site_cols].drop_duplicates()
    sites_per_panel=(
        site_table.groupby(panel_cols).size().astype(float).to_dict()
    )

    panel_table=d[panel_cols].drop_duplicates()
    panels_per_species=(
        panel_table.groupby("species").size().astype(float).to_dict()
    )

    weights=[]
    for idx,row in d.iterrows():
        panel_key=(row["species"],row["master_site"],row["unit"])
        weights.append(
            (1.0/n_species)
            * (1.0/panels_per_species[row["species"]])
            * (1.0/sites_per_panel[panel_key])
            * (1.0/site_spell_n.iloc[idx])
        )

    w=np.asarray(weights,float)
    if not np.isclose(float(w.sum()),1.0,rtol=0,atol=1e-10):
        raise ValueError(f"hierarchy weights do not sum to 1: {w.sum()}")
    return w


def aggregate(frame:pd.DataFrame)->dict:
    site=(
        frame.groupby(["species","master_site","unit","site_id"],as_index=False)["H"]
        .mean().rename(columns={"H":"site_mean_H"})
    )
    master=(
        site.groupby(["species","master_site","unit"],as_index=False)["site_mean_H"]
        .mean().rename(columns={"site_mean_H":"master_mean_H"})
    )
    species=(
        master.groupby("species",as_index=False)["master_mean_H"]
        .mean().rename(columns={"master_mean_H":"species_mean_H"})
    )
    vals=species["species_mean_H"].to_numpy(float)
    if len(vals)==0:
        raise ValueError("no species effects")
    T=float(vals.mean())

    s=len(vals)
    if s<=20:
        stats=np.asarray([
            float(np.mean(vals*np.asarray(signs,float)))
            for signs in itertools.product((-1.0,1.0),repeat=s)
        ],float)
        p=float(np.sum(stats>=T)/len(stats))
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
        "sign_flip_supported":bool(T>0 and p<=0.05),
        "site_means":site.to_dict(orient="records"),
        "master_means":master.to_dict(orient="records"),
        "species_means":species.to_dict(orient="records"),
    }


def contiguous_blocks(years:list[int])->list[list[int]]:
    yy=sorted({int(y) for y in years})
    if not yy:
        return []
    blocks=[[yy[0]]]
    for y in yy[1:]:
        if y==blocks[-1][-1]+1:
            blocks[-1].append(y)
        else:
            blocks.append([y])
    return blocks


def _block_for_spell(years:list[int],spell:dict)->list[int]:
    needed={
        int(spell["abandon_from"]),int(spell["abandon_to"]),
        int(spell["recolonize_from"]),int(spell["recolonize_to"]),
    }
    matches=[b for b in contiguous_blocks(years) if needed.issubset(set(b))]
    if len(matches)!=1:
        raise ValueError(f"spell does not belong to exactly one contiguous complete-year block: {spell}")
    return matches[0]


def _shifted_spell_H(
    matrix:pd.DataFrame,
    site:str,
    spell:dict,
    block_years:list[int],
    lag:int,
)->float:
    pos={y:i for i,y in enumerate(block_years)}
    L=len(block_years)
    if L<3:
        raise ValueError("trajectory-phase block too short")

    def source_year(target:int)->int:
        if target not in pos:
            raise ValueError("spell target year outside phase-null block")
        # Equivalent to a common circular row shift of the full panel matrix.
        return block_years[(pos[target]-lag)%L]

    def parent_excl(target:int)->float:
        sy=source_year(target)
        row=matrix.loc[sy].astype(float)
        value=float(row.sum()-float(row.loc[site]))
        if value<0:
            raise ValueError("negative shifted leave-one-site-out abundance")
        return value

    ae=transition_midpoint(
        parent_excl(int(spell["abandon_from"])),
        parent_excl(int(spell["abandon_to"])),
    )
    ac=transition_midpoint(
        parent_excl(int(spell["recolonize_from"])),
        parent_excl(int(spell["recolonize_to"])),
    )
    return float(ac-ae)


def trajectory_phase_null(
    frame:pd.DataFrame,
    matrices:dict[tuple[str,str,str],pd.DataFrame],
    panel_years:dict[tuple[str,str,str],list[int]],
    *,
    B:int=PHASE_B,
    seed:int=SEED,
)->dict:
    """Structured circular-shift calibration preserving spells and trajectories."""
    d=frame.reset_index(drop=True).copy()
    weights=hierarchy_weights(d)
    observed=float(np.sum(weights*d["H"].to_numpy(float)))

    block_rows={}
    block_years_map={}
    for i,row in d.iterrows():
        key=(str(row["species"]),str(row["master_site"]),str(row["unit"]))
        if key not in matrices or key not in panel_years:
            raise ValueError(f"phase-null panel missing: {key}")
        block=_block_for_spell(panel_years[key],row.to_dict())
        bkey=key+(int(block[0]),int(block[-1]))
        block_rows.setdefault(bkey,[]).append(i)
        block_years_map[bkey]=block

    # For each independent panel/block and each possible lag, precompute its
    # weighted contribution to the final species-balanced statistic.
    contributions={}
    for bkey,idxs in block_rows.items():
        key=bkey[:3]
        block=block_years_map[bkey]
        matrix=matrices[key]
        vals=np.empty(len(block),float)
        for lag in range(len(block)):
            total=0.0
            for i in idxs:
                row=d.iloc[i]
                h=_shifted_spell_H(
                    matrix,
                    str(row["site_id"]),
                    row.to_dict(),
                    block,
                    lag,
                )
                total += float(weights[i])*h
            vals[lag]=total
        contributions[bkey]=vals

    rng=np.random.default_rng(int(seed))
    null=np.zeros(int(B),float)
    for bkey,vals in contributions.items():
        picks=rng.integers(0,len(vals),size=int(B))
        null += vals[picks]

    p=float((1+np.sum(null>=observed))/(len(null)+1))
    return {
        "observed_T":observed,
        "resamples":int(B),
        "seed":int(seed),
        "panel_blocks":int(len(contributions)),
        "median":float(np.median(null)),
        "q025":float(np.quantile(null,0.025)),
        "q975":float(np.quantile(null,0.975)),
        "one_sided_p":p,
        "supported":bool(observed>0 and p<=0.05),
    }


def run(
    input_path:Path,
    structural_json:Path,
    cycle_json:Path,
    *,
    assume_whole_colony_extract:bool=False,
)->tuple[dict,pd.DataFrame]:
    structural=json.loads(structural_json.read_text(encoding="utf-8"))
    cycles=json.loads(cycle_json.read_text(encoding="utf-8"))

    if not structural.get("decision",{}).get("structural_gate_passed"):
        raise ValueError("identity-resolved structural gate did not pass")
    if not structural.get("decision",{}).get("zero_positive_state_scan_authorized"):
        raise ValueError("identity gate did not authorize the hysteresis state scan")
    if not cycles.get("decision",{}).get("hysteresis_magnitude_execution_authorized"):
        raise ValueError("state-only hysteresis support gate did not pass")

    x=_prepare_raw(input_path,assume_whole_colony_extract=assume_whole_colony_extract)

    panel_map={
        (str(p["species"]),str(p["master_site"]),str(p["unit"])):p
        for p in structural["eligible_panels"]
    }
    cache={}
    panel_years={}
    rows=[]

    for sp in cycles["completed_spells"]:
        key=(str(sp["species"]),str(sp["master_site"]),str(sp["unit"]))
        if key not in panel_map:
            raise ValueError(f"cycle panel not in frozen identity-resolved roster: {key}")

        if key not in cache:
            panel=panel_map[key]
            if not panel.get("identity_gate_resolved"):
                raise ValueError(f"panel identity not resolved: {key}")
            roster=[str(v) for v in panel["retained_site_ids"]]
            years=[int(v) for v in panel["complete_years"]]
            g=x[
                x["_species"].eq(key[0])
                & x["_master_norm"].eq(_norm(key[1]))
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
            if (mat.to_numpy(float)<0).any():
                raise ValueError(f"negative count in frozen panel: {key}")
            cache[key]=mat.astype(float)
            panel_years[key]=years

        eff=spell_effect(cache[key],str(sp["site_id"]),sp)
        rows.append({**sp,**eff})

    frame=pd.DataFrame(rows)
    macro=aggregate(frame)
    phase=trajectory_phase_null(frame,cache,panel_years,B=PHASE_B,seed=SEED)
    if not np.isclose(
        phase["observed_T"],
        macro["primary_T_species_balanced_mean_H"],
        rtol=0,atol=1e-10
    ):
        raise ValueError("phase-null and hierarchy aggregation disagree")

    supported=bool(
        macro["primary_T_species_balanced_mean_H"]>0
        and macro["sign_flip_supported"]
        and phase["supported"]
    )

    result={
        "schema_version":1,
        "analysis_id":"mina-smp-spatial-recovery-hysteresis-effect-v1",
        "status":"first_and_only_frozen_magnitude_execution",
        "spell_count":int(len(frame)),
        "macro":macro,
        "trajectory_phase_null":phase,
        "decision":{
            "spatial_recovery_hysteresis_supported":supported,
            "requires_positive_T":True,
            "species_sign_flip_required":True,
            "trajectory_phase_null_required":True,
        },
        "boundary":[
            "Supported H establishes history-dependent spatial recovery at retained SiteIDs, not a unique social mechanism.",
            "The focal SiteID is excluded from the parent abundance at abandonment and recolonization.",
            "Stable physical SiteID pairing controls fixed place identity/quality.",
            "The trajectory-phase null calibrates generic temporal alignment while preserving each panel/block abundance trajectory and frozen spell timing.",
            "Neither same-site pairing nor the phase null removes time-varying habitat, disturbance, predator, or management confounding.",
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
    result,frame=run(
        a.input,a.structural_json,a.cycle_json,
        assume_whole_colony_extract=a.assume_whole_colony_extract
    )
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    frame.to_csv(a.out_spells_csv,index=False)
    print(json.dumps({
        "analysis_id":result["analysis_id"],
        "spell_count":result["spell_count"],
        "decision":result["decision"],
        "macro":{
            k:v for k,v in result["macro"].items()
            if k not in {"site_means","master_means","species_means"}
        },
        "trajectory_phase_null":result["trajectory_phase_null"],
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
