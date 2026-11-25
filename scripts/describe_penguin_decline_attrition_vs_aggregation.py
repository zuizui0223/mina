#!/usr/bin/env python3
"""Decompose penguin breeding-space concentration into attrition versus absolute gains."""
from __future__ import annotations

import argparse, json, math
from collections import defaultdict
from pathlib import Path

import numpy as np

from scripts.describe_concentration_dominance import (
    SIGNY_ADELIE_UNITS,
    SIGNY_CHINSTRAP_UNITS,
    canonical_adelie,
    load_palmer,
    signy_panel,
)
from scripts.audit_signy_replication_support import read_official_zip

PALMER_ISLANDS=("COR","HUM","LIT")


def effective_number(v):
    x=np.asarray(v,float)
    total=float(x.sum())
    if total<=0:
        return float("nan")
    p=x/total
    ss=float(np.sum(p*p))
    return 1.0/ss if ss>0 else float("nan")


def palmer_panels(path:Path):
    rows=load_palmer(path)
    out={}
    for island in PALMER_ISLANDS:
        local=[r for r in rows if r["island"]==island]
        by=defaultdict(dict)
        for r in local:
            by[int(r["year"])][str(r["unit"])]=float(r["count"])
        years=sorted(by)
        rosters=[set(by[y]) for y in years]
        if not rosters or any(r!=rosters[0] for r in rosters[1:]):
            raise ValueError(f"{island}: unstable roster")
        units=sorted(rosters[0])
        matrix=np.asarray([[by[y][u] for y in years] for u in units],float)
        out[f"ADPE_PALMER_{island}"]=(units,np.asarray(years,int),matrix)
    return out


def component_endpoint_summary(units,years,matrix):
    totals=matrix.sum(axis=0)
    positive=np.where(totals>0)[0]
    if len(positive)==0:
        return None
    first_i=int(positive[0]); last_i=int(positive[-1])
    first=matrix[:,first_i]; last=matrix[:,last_i]
    first_total=float(first.sum()); last_total=float(last.sum())
    fs=first/first_total; ls=last/last_total
    initial_dom=int(np.argmax(fs)); final_dom=int(np.argmax(ls))
    comps=[]
    for i,u in enumerate(units):
        comps.append({
            "unit":str(u),
            "first_count":float(first[i]),
            "last_count":float(last[i]),
            "delta_count":float(last[i]-first[i]),
            "first_share":float(fs[i]),
            "last_share":float(ls[i]),
            "delta_share":float(ls[i]-fs[i]),
            "share_up_count_down":bool(ls[i]>fs[i] and last[i]<first[i]),
        })
    return {
        "first_year":int(years[first_i]),
        "last_positive_year":int(years[last_i]),
        "first_total":first_total,
        "last_positive_total":last_total,
        "components":comps,
        "components_net_positive":int(np.sum(last>first)),
        "components_share_up_count_down":int(np.sum((ls>fs)&(last<first))),
        "initial_dominant":{
            "unit":str(units[initial_dom]),
            "first_count":float(first[initial_dom]),
            "last_count":float(last[initial_dom]),
            "first_share":float(fs[initial_dom]),
            "last_share":float(ls[initial_dom]),
            "absolute_count_increased":bool(last[initial_dom]>first[initial_dom]),
        },
        "final_dominant":{
            "unit":str(units[final_dom]),
            "first_count":float(first[final_dom]),
            "last_count":float(last[final_dom]),
            "first_share":float(fs[final_dom]),
            "last_share":float(ls[final_dom]),
            "absolute_count_increased":bool(last[final_dom]>first[final_dom]),
        },
    }


def panel_summary(pop,units,years,matrix):
    events=[]
    for t in range(len(years)-1):
        if int(years[t+1])-int(years[t])!=1:
            continue
        a=matrix[:,t].astype(float)
        b=matrix[:,t+1].astype(float)
        ta=float(a.sum()); tb=float(b.sum())
        if ta<=0:
            continue
        ea=effective_number(a)
        eb=effective_number(b)
        if not np.isfinite(ea):
            continue
        d=b-a
        gg=float(np.maximum(d,0).sum())
        gl=float(np.maximum(-d,0).sum())
        event={
            "population":pop,
            "year_from":int(years[t]),
            "year_to":int(years[t+1]),
            "total_from":ta,
            "total_to":tb,
            "delta_total":float(tb-ta),
            "E_from":float(ea),
            "E_to":float(eb) if np.isfinite(eb) else None,
            "delta_E":float(eb-ea) if np.isfinite(eb) else None,
            "gross_gain":gg,
            "gross_loss":gl,
            "gain_loss_ratio":float(gg/gl) if gl>0 else None,
            "gaining_components":int(np.sum(d>0)),
            "losing_components":int(np.sum(d<0)),
            "unchanged_components":int(np.sum(d==0)),
        }
        events.append(event)

    decline=[e for e in events if e["delta_total"]<0]
    joint=[e for e in decline if e["delta_E"] is not None and e["delta_E"]<0]
    ratios=np.asarray([e["gain_loss_ratio"] for e in joint if e["gain_loss_ratio"] is not None],float)
    sum_gain=float(sum(e["gross_gain"] for e in joint))
    sum_loss=float(sum(e["gross_loss"] for e in joint))
    return {
        "population":pop,
        "n_components":len(units),
        "calendar_consecutive_transitions":len(events),
        "total_decline_transitions":len(decline),
        "joint_N_down_E_down_transitions":len(joint),
        "joint_with_any_component_gain":int(sum(e["gaining_components"]>0 for e in joint)),
        "fraction_joint_with_any_component_gain":(
            float(np.mean([e["gaining_components"]>0 for e in joint])) if joint else None
        ),
        "median_gain_loss_ratio_joint":float(np.median(ratios)) if len(ratios) else None,
        "summed_gross_gain_joint":sum_gain,
        "summed_gross_loss_joint":sum_loss,
        "weighted_gain_loss_ratio_joint":float(sum_gain/sum_loss) if sum_loss>0 else None,
        "endpoint":component_endpoint_summary(units,years,matrix),
        "joint_events":joint,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--palmer-census",required=True,type=Path)
    p.add_argument("--signy-adelie-zip",required=True,type=Path)
    p.add_argument("--signy-chinstrap-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()

    panels=palmer_panels(a.palmer_census)
    ad,_=read_official_zip(a.signy_adelie_zip)
    panels["ADPE_SIGNY"]=signy_panel(ad,units=SIGNY_ADELIE_UNITS,canonicalize=canonical_adelie)
    ch,_=read_official_zip(a.signy_chinstrap_zip)
    panels["CHPE_SIGNY"]=signy_panel(ch,units=SIGNY_CHINSTRAP_UNITS,canonicalize=None)

    summaries=[]
    for pop,(units,years,matrix) in panels.items():
        summaries.append(panel_summary(pop,units,years,matrix))

    all_joint=[e for s in summaries for e in s["joint_events"]]
    total_gain=float(sum(e["gross_gain"] for e in all_joint))
    total_loss=float(sum(e["gross_loss"] for e in all_joint))
    endpoints=[s["endpoint"] for s in summaries if s["endpoint"]]
    all_components=[c for ep in endpoints for c in ep["components"]]
    pooled={
        "joint_N_down_E_down_transitions":len(all_joint),
        "joint_with_any_component_gain":int(sum(e["gaining_components"]>0 for e in all_joint)),
        "fraction_joint_with_any_component_gain":(
            float(np.mean([e["gaining_components"]>0 for e in all_joint])) if all_joint else None
        ),
        "summed_gross_gain_joint":total_gain,
        "summed_gross_loss_joint":total_loss,
        "weighted_gain_loss_ratio_joint":float(total_gain/total_loss) if total_loss>0 else None,
        "components_first_to_last":len(all_components),
        "components_net_positive_first_to_last":int(sum(c["delta_count"]>0 for c in all_components)),
        "components_share_up_count_down_first_to_last":int(sum(c["share_up_count_down"] for c in all_components)),
    }

    out={
        "schema_version":1,
        "analysis_id":"mina-penguin-decline-attrition-vs-aggregation-v1",
        "status":"post_outcome_descriptive_only_no_p_values",
        "populations":summaries,
        "pooled_descriptive":pooled,
        "boundary":[
            "Absolute gains do not identify individual movement.",
            "Absolute losses do not distinguish mortality, emigration, recruitment failure or breeding non-participation.",
            "The analysis is descriptive and uses no inferential p-values.",
            "No threshold is used to label attrition or aggregation."
        ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
