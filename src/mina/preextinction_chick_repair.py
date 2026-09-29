"""Post-primary identifier-coherence repair for Palmer chick/extinction join."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_extinction_hazard import build_transitions, load_rows, standardize_risk_sets
from .preextinction_chick import _observed_summary, simulate_null

N_SIMULATIONS = 100_000
SEED = 20260930


def _finite(x: str | None) -> bool:
    try:
        return x not in {None, "", "NULL", "NA", "NaN", "nan"} and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def load_coherent_chick_candidates(path: str | Path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        rows=list(csv.DictReader(f))
    groups=defaultdict(list)
    for row in rows:
        island=str(row.get("Island","")).strip()
        code=str(row.get("Colony","")).strip()
        date=str(row.get("Date GMT","")).strip()
        if not island or not code or not _finite(row.get("Chicks")):
            continue
        try:
            season=int(date[:4])-1
        except ValueError:
            continue
        chicks=float(row["Chicks"])
        adults=float(row["Adults"]) if _finite(row.get("Adults")) else None
        if chicks < 0 or (adults is not None and adults < 0):
            raise ValueError("negative chick-table count")
        groups[(island,code,season)].append((adults,chicks))

    out={}
    audit={"raw_rows":len(rows),"candidate_keys":len(groups),
           "conflicting_chick_keys":0,"ambiguous_adult_keys":0,
           "identical_duplicates_resolved":0}
    for key,vals in sorted(groups.items()):
        chick_values=sorted({v[1] for v in vals})
        if len(chick_values)!=1:
            audit["conflicting_chick_keys"]+=1
            continue
        if len(vals)==1:
            adult=vals[0][0]
        else:
            positive=[v[0] for v in vals if v[0] is not None and v[0]>0]
            positive_unique=sorted(set(positive))
            all_pairs=set(vals)
            if len(positive_unique)==1:
                adult=positive_unique[0]
                audit["identical_duplicates_resolved"]+=1
            elif len(all_pairs)==1:
                adult=vals[0][0]
                audit["identical_duplicates_resolved"]+=1
            else:
                audit["ambiguous_adult_keys"]+=1
                continue
        out[key]={"chicks":float(chick_values[0]),"chick_adults":adult}
    audit["cleaned_keys"]=len(out)
    return out,audit


def build_sets(adult_census: str | Path, chick_path: str | Path, fold: float):
    if fold <= 1:
        raise ValueError("fold must be >1")
    adults=load_rows(adult_census)
    standardized=standardize_risk_sets(build_transitions(adults))
    chicks,audit=load_coherent_chick_candidates(chick_path)
    groups=defaultdict(list)
    exact_matches=0; coherent=0; coherent_events=0
    for row in standardized:
        key=(str(row["island"]),str(row["colony_code"]),int(row["start_year"]))
        rec=chicks.get(key)
        if rec is None:
            continue
        exact_matches+=1
        A=rec["chick_adults"]; N=float(row["prior_count"])
        if A is None or A<=0 or N<=0:
            continue
        ratio=float(A/N)
        if not (1.0/fold <= ratio <= fold):
            continue
        coherent+=1; coherent_events+=int(row["event"])
        x=dict(row);x["chicks"]=rec["chicks"];x["chick_adults"]=float(A);x["adult_ratio"]=ratio
        groups[(str(row["island"]),int(row["start_year"]))].append(x)

    risk_sets=[]
    for (island,season),local in sorted(groups.items()):
        event=np.asarray([int(r["event"]) for r in local],int)
        if len(local)<2 or event.sum()==0 or event.sum()==len(local):
            continue
        prior=np.asarray([float(r["prior_count"]) for r in local])
        y=np.asarray([float(r["chicks"]) for r in local])
        C=int(round(float(y.sum())))
        p=prior/prior.sum();mu=C*p
        residual=(y-mu)/np.sqrt(np.maximum(mu,1e-12))
        risk_sets.append({
            "island":island,"season":season,"rows":local,"event":event,
            "prior":prior,"chicks":y,"total_chicks":C,"probs":p,"expected":mu,
            "pearson_residual":residual,
            "observed_contrast":float(residual[event==1].mean()-residual[event==0].mean())
        })
    info={**audit,"fold_threshold":fold,"exact_key_matches":exact_matches,
          "coherence_passing_rows":coherent,"coherence_passing_events":coherent_events,
          "informative_risk_sets":len(risk_sets),
          "informative_events":int(sum(np.sum(r["event"]) for r in risk_sets))}
    return risk_sets,info


def run_one(adult_census,chick_path,fold,simulations,seed):
    risk,info=build_sets(adult_census,chick_path,fold)
    if len(risk)<5:
        return {"estimable":False,"inventory":info,
                "reason":"fewer than five informative risk sets"}
    observed=_observed_summary(risk)
    null=simulate_null(risk,simulations=simulations,seed=seed)
    return {"estimable":True,"inventory":info,"observed":observed,"null":null}


def analyze(adult_census,chick_path,simulations=N_SIMULATIONS,seed=SEED):
    primary=run_one(adult_census,chick_path,2.0,simulations,seed)
    strict=run_one(adult_census,chick_path,1.5,simulations,seed+1)
    lenient=run_one(adult_census,chick_path,3.0,simulations,seed+2)
    support=False
    if primary["estimable"] and strict["estimable"] and lenient["estimable"]:
        support=bool(
            primary["null"]["supported"]
            and strict["null"]["observed_contrast"]<0
            and lenient["null"]["observed_contrast"]<0
        )
    return {
      "schema_version":1,
      "analysis_id":"mina-palmer-chick-identifier-coherence-repair-v1",
      "contract_id":"mina-palmer-chick-identifier-coherence-repair-v1",
      "source":{
        "adult_census_sha256":hashlib.sha256(Path(adult_census).read_bytes()).hexdigest(),
        "chick_snapshot_sha256":hashlib.sha256(Path(chick_path).read_bytes()).hexdigest()
      },
      "primary_2x":primary,
      "sensitivities":{"strict_1_5x":strict,"lenient_3x":lenient},
      "decision":{
        "exploratory_preextinction_reproductive_penalty":support,
        "confirmatory_status":"post_primary_provenance_repaired_exploratory"
      }
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--adult-census",required=True,type=Path)
    p.add_argument("--chicks",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--simulations",type=int,default=N_SIMULATIONS)
    p.add_argument("--seed",type=int,default=SEED)
    a=p.parse_args()
    x=analyze(a.adult_census,a.chicks,a.simulations,a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
