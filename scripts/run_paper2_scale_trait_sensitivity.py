#!/usr/bin/env python3
"""Prespecified descriptive radius/Shannon sensitivities for Paper 2."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pyreadr

from scripts.run_paper2_real_v3_fit import build_frozen_real_records, calibrate_observation
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames, fit_spatial_species

SPECIES=("ADPE","CHPE","GEPE")
VARIANTS={
  "radius_1000m":("mapped_ice_free_area_ha_1000m","tier2_richness_1000m"),
  "radius_5000m":("mapped_ice_free_area_ha_5000m","tier2_richness_5000m"),
  "shannon_2000m":("mapped_ice_free_area_ha_2000m","tier2_shannon_2000m"),
}


def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:return x[expected]
    if len(x)==1:return next(iter(x.values()))
    raise ValueError(expected)


def zscore(x:pd.Series)->pd.Series:
    x=pd.to_numeric(x,errors="coerce")
    sd=float(x.std(ddof=0))
    if not np.isfinite(sd) or sd<=0: raise ValueError(f"zero variance {x.name}")
    return (x-float(x.mean()))/sd


def build_variant_frames(forcing_result,forcing_units,breeding,variant):
    base=build_v3_frames(forcing_result,forcing_units,breeding)
    acol,hcol=VARIANTS[variant]
    site=breeding[["site_id",acol,hcol]].copy()
    frames={}
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    for sp in SPECIES:
        f=base[sp].copy()
        # Remove primary A/H/AH then merge the frozen sensitivity fields.
        f=f.drop(columns=["A","H","AH"],errors="ignore")
        f=f.merge(site,on="site_id",how="left",validate="many_to_one")
        f["A_raw_variant"]=np.log1p(pd.to_numeric(f[acol],errors="coerce"))
        f["H_raw_variant"]=pd.to_numeric(f[hcol],errors="coerce")
        if f[["A_raw_variant","H_raw_variant"]].isna().any().any():
            bad=f.loc[
                f[["A_raw_variant","H_raw_variant"]].isna().any(axis=1),
                "unit_id"
            ].astype(str).tolist()
            raise ValueError(f"{variant} missing predictor rows {sp}: {bad}")
        f["A"]=zscore(f["A_raw_variant"])
        f["H"]=zscore(f["H_raw_variant"])
        f["AH"]=f["A"]*f["H"]
        frames[sp]=f
    got={sp:len(f) for sp,f in frames.items()}
    if got!=expected: raise ValueError(f"frame drift {variant}: {got} != {expected}")
    return frames


def local_records(records,frame):
    ids=set(frame["unit_id"].astype(str))
    x=records.copy()
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    return x[x["unit_id"].isin(ids)].copy().reset_index(drop=True)


def fit_variant(frames,records,cal):
    species={}
    for sp in SPECIES:
        fit=fit_spatial_species(
            frames[sp].reset_index(drop=True),
            local_records(records,frames[sp]),
            delta_image=float(cal["delta_image"]),
            sigma1=float(cal["accuracy"]["1"]["sigma"]),
            sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
            truth_forcing=None,true_lambda=None,
        )
        ga=float(fit["gamma_a"]);gh=float(fit["gamma_h"]);gah=float(fit["gamma_ah"])
        species[sp]={
          "gamma_a":ga,"gamma_h":gh,"gamma_ah":gah,
          "low_area_H_slope":gh-gah,
          "high_area_H_slope":gh+gah,
          "crossover_classification":bool(gah<0 and gh-gah>=0 and gh+gah<0),
          "process_sd":float(fit["process_sd"]),
          "loading_residual_sd":float(fit["loading_residual_sd"]),
        }
    vals=np.asarray([species[sp]["gamma_ah"] for sp in SPECIES],float)
    return {
      "species":species,
      "cross_species_median_gamma_ah":float(np.median(vals)),
      "negative_species":int(np.sum(vals<0)),
      "crossover_species":[sp for sp in SPECIES if species[sp]["crossover_classification"]],
    }


def run(fr,fu,br,obs):
    records=build_frozen_real_records(obs)
    cal=calibrate_observation(records)
    out={}
    for variant in VARIANTS:
        frames=build_variant_frames(fr,fu,br,variant)
        out[variant]=fit_variant(frames,records,cal)
    return {
      "schema_version":1,
      "analysis_id":"mina-paper2-scale-trait-sensitivity-v1",
      "variants":out,
      "primary_reference":{
        "variant":"radius_2000m_tier2_richness",
        "cross_species_median_gamma_ah":-0.31822603579776854,
        "species_gamma_ah":{"ADPE":-0.303571047069412,"CHPE":-1.1843982732708647,"GEPE":-0.31822603579776854},
        "primary_permutation_p":0.0947
      },
      "interpretation_boundary":{
        "descriptive_only":True,
        "new_p_values_created":False,
        "primary_result_replaced":False,
      },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",type=Path,required=True)
    p.add_argument("--forcing-csv",type=Path,required=True)
    p.add_argument("--breeding-csv",type=Path,required=True)
    p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    out=run(fr,fu,br,obs)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":main()
