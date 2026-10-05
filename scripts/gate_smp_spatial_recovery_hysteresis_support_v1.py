#!/usr/bin/env python3
"""Stage-B state-only support gate for SMP spatial-recovery hysteresis.

Uses only positive/explicit-zero/missing count states on the already-frozen
structural panel roster. Count magnitudes are never retained or emitted.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from scripts.audit_smp_macro_support import _count_state
from scripts.gate_smp_master_site_support_v1 import (
    EXPOSED_MASTER,
    SENSITIVE,
    _direct_record_mask,
    _find_column,
    _load,
    _norm,
    _not_merged_mask,
    _whole_colony_mask,
    _year_from_date,
)

MIN_SPELLS=30
MIN_SITES=20
MIN_MASTERS=10
MIN_SPECIES=5
MIN_SPECIES_3SPELLS=4
MIN_SPECIES_2MASTERS=3


def _state_frame(path: Path, *, assume_whole_colony_extract: bool=False) -> pd.DataFrame:
    df=_load(path)
    species_col=_find_column(df,["Species"])
    site_id_col=_find_column(df,["SiteID","Site ID","Site code"])
    master_col=_find_column(df,["MasterSite","Master Site"])
    method_col=_find_column(df,["Method"],required=False)
    unit_col=_find_column(df,["Unit"])
    accuracy_col=_find_column(df,["Accuracy"])
    estimate_col=_find_column(df,["Estimate","Estimate type"],required=False)
    comments_col=_find_column(df,["Comments","Comment"],required=False)
    plot_col=_find_column(df,["Plot","Plot site name","Spatial level"],required=False)
    count_col=_find_column(df,["Count"])
    year_col=_find_column(df,["Year"],required=False)
    date_col=_find_column(df,["Start date","Date","StartDate"],required=year_col is None)

    year=(df[year_col].map(_year_from_date) if year_col is not None else df[date_col].map(_year_from_date))
    x=df.assign(_year=year)
    x=x[x["_year"].between(1986,2024,inclusive="both")].copy()

    direct=_direct_record_mask(x,accuracy_col,estimate_col)
    whole=_whole_colony_mask(x,plot_col,assume_whole_colony_extract)
    not_merged=_not_merged_mask(x,comments_col)
    x=x[direct & whole & not_merged].copy()

    x["_species"]=x[species_col].map(_norm)
    x["_master"]=x[master_col].map(lambda z:str(z).strip())
    x["_master_norm"]=x[master_col].map(_norm)
    x["_site_id"]=x[site_id_col].map(lambda z:str(z).strip())
    x["_unit"]=x[unit_col].map(lambda z:str(z).strip())
    x["_method"]=x[method_col].map(lambda z:str(z).strip()) if method_col else ""
    x["year"]=x["_year"].astype(int)
    x["state"]=x[count_col].map(lambda z:_count_state(str(z)))

    x=x[~x["_species"].isin(SENSITIVE)].copy()
    pilot=x["_species"].str.contains("kittiwake",regex=False) & (x["_master_norm"]==EXPOSED_MASTER)
    x=x[~pilot].copy()

    # Only one usable row per panel-site-year may enter the state sequence.
    key=["_species","_master","_unit","_site_id","year"]
    usable=x[x["state"].isin(["observed_positive","explicit_zero"])].copy()
    dup=usable.groupby(key,dropna=False).size().rename("_n").reset_index()
    unique=dup[dup["_n"]==1][key]
    x=x.merge(unique,on=key,how="inner")

    if method_col:
        method_n=(
            x[x["_method"].map(_norm)!=""]
            .groupby(["_species","_master","_unit","_site_id"])["_method"]
            .nunique().rename("_method_n").reset_index()
        )
        x=x.merge(method_n,on=["_species","_master","_unit","_site_id"],how="left")
        x["_method_n"]=x["_method_n"].fillna(0)
        x=x[x["_method_n"]<=1].copy()

    # Hard blind: keep only categorical state and identifiers.
    return x[["_species","_master","_master_norm","_unit","_site_id","year","state"]].copy()


def completed_spells_for_site(years:list[int], states:list[str]) -> list[dict]:
    """Return every completed calendar-consecutive positive->zero...->positive spell.

    The recolonization year is allowed to begin a new spell immediately in the
    following year, so sequences like 1,0,1,0,1 produce two spells.
    """
    by={int(y):str(s) for y,s in zip(years,states)}
    ordered=sorted(by)
    spells=[]
    i=0
    while i < len(ordered)-1:
        y=ordered[i]
        y1=ordered[i+1]
        if (
            y1 != y+1
            or by[y]!="observed_positive"
            or by[y1]!="explicit_zero"
        ):
            i += 1
            continue

        abandon_from=y
        abandon_to=y1
        j=i+1

        # Extend the explicit-zero run only across consecutive calendar years.
        while j+1 < len(ordered):
            cur=ordered[j]
            nxt=ordered[j+1]
            if nxt != cur+1:
                break
            if by[nxt]=="explicit_zero":
                j += 1
                continue
            if by[nxt]=="observed_positive":
                spells.append({
                    "abandon_from":int(abandon_from),
                    "abandon_to":int(abandon_to),
                    "recolonize_from":int(cur),
                    "recolonize_to":int(nxt),
                    "vacancy_years":int(nxt-abandon_to),
                })
                # Reconsider the recolonization year as a possible new
                # occupied->zero spell start.
                i=j+1
                break
            break
        else:
            i += 1
            continue

        if spells and spells[-1]["recolonize_to"]==ordered[i]:
            continue
        i += 1
    return spells


def run(input_path:Path,support_json:Path,*,assume_whole_colony_extract:bool=False)->dict:
    support=json.loads(support_json.read_text(encoding="utf-8"))
    if not support.get("decision",{}).get("structural_gate_passed"):
        raise ValueError("identity-resolved structural gate did not pass")
    if not support.get("decision",{}).get("zero_positive_state_scan_authorized"):
        raise ValueError("identity gate did not authorize zero/positive state scan")
    for panel in support.get("eligible_panels", []):
        if not panel.get("identity_gate_resolved"):
            raise ValueError("unresolved physical SiteID identity in hysteresis roster")

    x=_state_frame(input_path,assume_whole_colony_extract=assume_whole_colony_extract)
    all_spells=[]
    for panel in support["eligible_panels"]:
        species=str(panel["species"])
        master=str(panel["master_site"])
        unit=str(panel["unit"])
        roster={str(v) for v in panel["retained_site_ids"]}
        years=[int(v) for v in panel["complete_years"]]

        g=x[
            x["_species"].eq(species)
            & x["_master_norm"].eq(_norm(master))
            & x["_unit"].eq(unit)
            & x["_site_id"].isin(roster)
            & x["year"].isin(years)
        ].copy()

        # The Stage-A roster guarantees complete observation support; verify state rows.
        n_expected=len(roster)*len(years)
        if len(g)!=n_expected:
            raise ValueError(f"state support drift: {species}|{master}|{unit}: {len(g)} != {n_expected}")

        for site in sorted(roster):
            sg=g[g["_site_id"].eq(site)].sort_values("year")
            spells=completed_spells_for_site(
                sg["year"].astype(int).tolist(),
                sg["state"].astype(str).tolist(),
            )
            for k,sp in enumerate(spells,1):
                all_spells.append({
                    "spell_id":f"{species}|{master}|{unit}|{site}|{k}",
                    "species":species,
                    "master_site":master,
                    "unit":unit,
                    "site_id":site,
                    **sp,
                })

    frame=pd.DataFrame(all_spells)
    n_spells=int(len(frame))
    n_sites=int(frame["site_id"].nunique()) if n_spells else 0
    n_masters=int(frame["master_site"].nunique()) if n_spells else 0
    n_species=int(frame["species"].nunique()) if n_spells else 0
    sp_counts=Counter(frame["species"]) if n_spells else Counter()
    sp_masters=(
        frame.groupby("species")["master_site"].nunique().to_dict()
        if n_spells else {}
    )
    species_3=sorted([sp for sp,n in sp_counts.items() if n>=3])
    species_2masters=sorted([sp for sp,n in sp_masters.items() if int(n)>=2])

    passed=bool(
        n_spells>=MIN_SPELLS
        and n_sites>=MIN_SITES
        and n_masters>=MIN_MASTERS
        and n_species>=MIN_SPECIES
        and len(species_3)>=MIN_SPECIES_3SPELLS
        and len(species_2masters)>=MIN_SPECIES_2MASTERS
    )

    return {
        "schema_version":1,
        "analysis_id":"mina-smp-spatial-recovery-hysteresis-support-v1",
        "status":"state_only_completed_vacancy_spells",
        "completed_spells":all_spells,
        "support":{
            "completed_spells":n_spells,
            "distinct_siteids_with_spells":n_sites,
            "mastersites_with_spells":n_masters,
            "species_with_spells":n_species,
            "species_with_at_least_3_spells":species_3,
            "species_with_spells_in_at_least_2_mastersites":species_2masters,
        },
        "thresholds":{
            "minimum_completed_spells":MIN_SPELLS,
            "minimum_distinct_siteids_with_spells":MIN_SITES,
            "minimum_mastersites_with_spells":MIN_MASTERS,
            "minimum_species_with_spells":MIN_SPECIES,
            "minimum_species_with_at_least_3_spells":MIN_SPECIES_3SPELLS,
            "minimum_species_with_spells_in_at_least_2_mastersites":MIN_SPECIES_2MASTERS,
        },
        "decision":{
            "hysteresis_magnitude_execution_authorized":passed,
            "if_failed":"Stop; do not lower support thresholds or bridge missing years."
        },
        "forbidden_outputs_confirmed_absent":[
            "count magnitudes","panel abundance totals","abandonment abundance",
            "recolonization abundance","hysteresis width H","E","kappa","gamma"
        ]
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--support-json",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--assume-whole-colony-extract",action="store_true")
    a=p.parse_args()
    result=run(a.input,a.support_json,assume_whole_colony_extract=a.assume_whole_colony_extract)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="completed_spells"},indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
