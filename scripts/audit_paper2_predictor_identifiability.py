#!/usr/bin/env python3
"""Outcome-blind predictor-identifiability audit for Paper 2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

MIN_COMPLETE_UNITS=25
MIN_GROUP_UNITS=5
MIN_GROUP_H_UNIQUE=3
MIN_QUADRANT_UNITS=3
MAX_CROSSOVER_CONDITION=10.0
MAX_INTERACTION_VIF=5.0


def _quadrants(frame:pd.DataFrame)->dict[str,int]:
    counts={"++":0,"+-":0,"-+":0,"--":0}
    for a,h in zip(frame["A"],frame["H"]):
        if a>=0 and h>=0:
            counts["++"]+=1
        elif a>=0 and h<0:
            counts["+-"]+=1
        elif a<0 and h>=0:
            counts["-+"]+=1
        else:
            counts["--"]+=1
    return counts


def _eta_squared(frame:pd.DataFrame,column:str)->float|None:
    grand=float(frame[column].mean())
    total=float(((frame[column]-grand)**2).sum())
    if total<=0:
        return None
    between=0.0
    for _,local in frame.groupby("group"):
        between+=len(local)*(float(local[column].mean())-grand)**2
    return float(between/total)


def _design_matrix(frame:pd.DataFrame,include_relief:bool)->pd.DataFrame:
    group=pd.get_dummies(frame[["group"]],drop_first=True,dtype=float)
    cols=["A","H"]+(["R"] if include_relief else [])+["AH"]
    return pd.concat(
        [pd.Series(1.0,index=frame.index,name="intercept"),group,frame[cols]],
        axis=1,
    )


def _interaction_vif(frame:pd.DataFrame)->float:
    design=_design_matrix(frame,include_relief=False)
    y=design["AH"].to_numpy(dtype=float)
    x=design.drop(columns=["AH"]).to_numpy(dtype=float)
    if float(np.var(y))<=0:
        return float("inf")
    beta=np.linalg.lstsq(x,y,rcond=None)[0]
    residual=y-x@beta
    denom=float(((y-y.mean())@(y-y.mean())))
    r2=1.0-float(residual@residual)/denom
    if r2>=1.0:
        return float("inf")
    return float(1.0/(1.0-r2))


def diagnose_species(frame:pd.DataFrame)->dict:
    """Diagnose whether the predeclared A x H crossover is estimable."""
    required={"unit_id","group","A","H","R","H_raw"}
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    local=frame.dropna(subset=["A","H","R","H_raw","group"]).copy()
    local=local.sort_values("unit_id").reset_index(drop=True)
    local["AH"]=local["A"]*local["H"]

    group_support=[]
    for group,g in local.groupby("group",sort=True):
        group_support.append({
            "group":str(group),
            "n_complete_units":int(len(g)),
            "unique_habitat_complex_values":int(g["H_raw"].nunique()),
            "A_sd":float(g["A"].std(ddof=0)),
            "H_sd":float(g["H"].std(ddof=0)),
            "R_sd":float(g["R"].std(ddof=0)),
        })

    crossover=_design_matrix(local,include_relief=False)
    combined=_design_matrix(local,include_relief=True)
    design_rank=int(np.linalg.matrix_rank(crossover.to_numpy(dtype=float)))
    design_columns=int(crossover.shape[1])
    crossover_condition=float(np.linalg.cond(crossover.to_numpy(dtype=float)))
    combined_condition=float(np.linalg.cond(combined.to_numpy(dtype=float)))
    vif=_interaction_vif(local)
    quadrant_counts=_quadrants(local)

    correlations={
        a:{b:float(local[[a,b]].corr().iloc[0,1]) for b in ("A","H","R")}
        for a in ("A","H","R")
    }
    group_eta2={col:_eta_squared(local,col) for col in ("A","H","R")}

    checks={
        "complete_units":len(local)>=MIN_COMPLETE_UNITS,
        "group_units":all(x["n_complete_units"]>=MIN_GROUP_UNITS for x in group_support),
        "group_habitat_levels":all(
            x["unique_habitat_complex_values"]>=MIN_GROUP_H_UNIQUE
            for x in group_support
        ),
        "quadrant_replication":all(
            quadrant_counts[q]>=MIN_QUADRANT_UNITS for q in ("++","+-","-+","--")
        ),
        "full_rank":design_rank==design_columns,
        "crossover_condition":crossover_condition<=MAX_CROSSOVER_CONDITION,
        "interaction_vif":vif<=MAX_INTERACTION_VIF,
    }
    return {
        "n_complete_units":int(len(local)),
        "selected_groups":int(local["group"].nunique()),
        "group_support":group_support,
        "quadrant_counts":quadrant_counts,
        "design_rank":design_rank,
        "design_columns":design_columns,
        "crossover_condition_number":crossover_condition,
        "interaction_vif":vif,
        "secondary_combined_condition_number":combined_condition,
        "predictor_correlations":correlations,
        "group_eta_squared":group_eta2,
        "checks":checks,
        "crossover_eligible":bool(all(checks.values())),
    }


def _zscore(series:pd.Series)->pd.Series:
    sd=float(series.std(ddof=0))
    if sd<=0:
        raise ValueError(f"zero predictor variance: {series.name}")
    return (series-float(series.mean()))/sd


def build_analysis_table(
    forcing_json:dict,
    forcing:pd.DataFrame,
    breeding:pd.DataFrame,
    terrain:pd.DataFrame,
)->pd.DataFrame:
    eligible=forcing_json["decision"]["modeling_eligibility_by_species"]
    selected=[]
    for species_id,meta in eligible.items():
        level=meta["level"]
        for unit_id in meta["covered_units"]:
            selected.append({
                "unit_id":str(unit_id),
                "species_id":str(species_id),
                "forcing_level":level,
            })
    selected=pd.DataFrame(selected)

    table=forcing.merge(
        selected,on=["unit_id","species_id"],how="inner",validate="one_to_one"
    )
    table=table.merge(
        breeding[[
            "site_id","mapped_ice_free_area_ha_2000m","tier2_richness_2000m"
        ]],
        on="site_id",how="left",validate="many_to_one",
    )
    table=table.merge(
        terrain[["site_id","elevation_relief_p90_p10_m_2000m"]],
        on="site_id",how="left",validate="many_to_one",
    )

    table["group"]=np.where(
        table["forcing_level"].eq("ccamlr"),
        table["ccamlr_id"],
        np.where(
            table["forcing_level"].eq("apbp_region"),
            table["region"],
            table["species_id"],
        ),
    )
    table["A_raw"]=np.log1p(table["mapped_ice_free_area_ha_2000m"])
    table["H_raw"]=table["tier2_richness_2000m"]
    table["R_raw"]=np.log1p(table["elevation_relief_p90_p10_m_2000m"])

    pieces=[]
    for species_id,local in table.groupby("species_id",sort=True):
        local=local.copy()
        complete=local.dropna(subset=["A_raw","H_raw","R_raw","group"]).copy()
        complete["A"]=_zscore(complete["A_raw"])
        complete["H"]=_zscore(complete["H_raw"])
        complete["R"]=_zscore(complete["R_raw"])
        pieces.append(complete)
    if not pieces:
        return pd.DataFrame()
    return pd.concat(pieces,ignore_index=True)


def audit(
    forcing_json_path:Path,
    forcing_csv_path:Path,
    breeding_csv_path:Path,
    terrain_csv_path:Path,
)->dict:
    forcing_json=json.loads(forcing_json_path.read_text(encoding="utf-8"))
    forcing=pd.read_csv(forcing_csv_path)
    breeding=pd.read_csv(breeding_csv_path)
    terrain=pd.read_csv(terrain_csv_path)

    table=build_analysis_table(forcing_json,forcing,breeding,terrain)
    species={}
    for species_id,local in table.groupby("species_id",sort=True):
        species[str(species_id)]=diagnose_species(
            local[["unit_id","group","A","H","R","H_raw"]]
        )

    source_units={
        sp:len(meta["covered_units"])
        for sp,meta in forcing_json["decision"]["modeling_eligibility_by_species"].items()
    }
    complete_units={
        sp:int((table["species_id"]==sp).sum())
        for sp in sorted(source_units)
    }
    dropped_for_missing_predictors={
        sp:int(source_units[sp]-complete_units.get(sp,0))
        for sp in sorted(source_units)
    }

    return {
        "schema_version":1,
        "audit_id":"mina-paper2-predictor-identifiability-audit-v1",
        "source_coupling_units":int(sum(source_units.values())),
        "complete_predictor_units":int(len(table)),
        "source_units_by_species":source_units,
        "complete_units_by_species":complete_units,
        "dropped_for_missing_predictors_by_species":dropped_for_missing_predictors,
        "species":species,
        "decision":{
            "crossover_eligible_by_species":{
                sp:bool(meta["crossover_eligible"]) for sp,meta in species.items()
            },
            "program_level_crossover_primary":bool(
                species and all(meta["crossover_eligible"] for meta in species.values())
            ),
            "no_demographic_outcomes_opened":True,
            "primary_crossover_model":"group + A + H + A:H",
            "secondary_combined_model":"group + A + H + R + A:H",
        },
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",required=True,type=Path)
    p.add_argument("--forcing-csv",required=True,type=Path)
    p.add_argument("--breeding-csv",required=True,type=Path)
    p.add_argument("--terrain-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()

    result=audit(a.forcing_json,a.forcing_csv,a.breeding_csv,a.terrain_csv)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
