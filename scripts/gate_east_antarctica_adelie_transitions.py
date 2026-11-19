#!/usr/bin/env python3
"""Count support only for East Antarctic Adelie occupancy transitions."""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path
import openpyxl

def season_start(v):
    s=str(v).strip()
    # Accept labels such as 2019-20, 2019/20, or numeric year.
    for sep in ("-","/"):
        if sep in s:
            left=s.split(sep,1)[0].strip()
            try: return int(float(left))
            except ValueError: pass
    try: return int(float(s))
    except ValueError: return None

def read_sheet(path: Path, target: str):
    wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
    ws=wb[target]
    rows=ws.iter_rows(values_only=True)
    header=[str(x).strip() if x is not None else "" for x in next(rows)]
    idx={k:i for i,k in enumerate(header)}
    return idx, rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--occupancy",required=True,type=Path)
    p.add_argument("--geog-sites",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()

    idx, rows=read_sheet(a.occupancy,"2_search events")
    need={"sub_group","geog_site_id","season","occurrence","vantage",
          "species_code","species_expert_validation","site_expert_validation",
          "occurrence_expert_validation"}
    if not need.issubset(idx): raise ValueError(f"missing occupancy columns: {sorted(need-set(idx))}")

    raw=defaultdict(lambda: {"occ":[],"subgroups":set(),"vantage":[],"validation":[]})
    for row in rows:
        sp=str(row[idx["species_code"]] or "").strip()
        if sp != "ADP": raise ValueError(f"unexpected species_code {sp!r}")
        site=str(row[idx["geog_site_id"]] or "").strip()
        yr=season_start(row[idx["season"]])
        occ=str(row[idx["occurrence"]] or "").strip().upper()
        if not site or yr is None or occ not in {"P","A","NR"}: continue
        key=(site,yr)
        raw[key]["occ"].append(occ)
        raw[key]["subgroups"].add(str(row[idx["sub_group"]] or "").strip())
        raw[key]["vantage"].append(str(row[idx["vantage"]] or "").strip())
        raw[key]["validation"].append((
            str(row[idx["species_expert_validation"]] or "").strip().upper(),
            str(row[idx["site_expert_validation"]] or "").strip().upper(),
            str(row[idx["occurrence_expert_validation"]] or "").strip().upper(),
        ))

    state={}
    meta={}
    for key,rec in raw.items():
        occs=set(rec["occ"])
        st="P" if "P" in occs else ("A" if "A" in occs else None)
        if st is None: continue
        state[key]=st
        meta[key]=rec

    # site feature lookup; no association is calculated
    gidx, grows=read_sheet(a.geog_sites,"2_geog_sites_all")
    feat={}
    for row in grows:
        site=str(row[gidx["geog_site_id"]] or "").strip()
        if site: feat[site]=str(row[gidx["geog_site_feature"]] or "").strip().lower()

    bysite=defaultdict(dict)
    for (site,yr),st in state.items(): bysite[site][yr]=st

    transitions=[]
    seen_p_before=defaultdict(bool)
    for site,years in bysite.items():
        for yr in sorted(years):
            st=years[yr]
            nxt=years.get(yr+1)
            if nxt in {"P","A"}:
                kind=st+nxt
                history="na"
                if st=="A" and nxt=="P":
                    history="recolonization" if seen_p_before[site] else "first_colonization"
                transitions.append({
                    "site":site,"year":yr,"kind":kind,"history":history,
                    "feature":feat.get(site,""),
                    "subgroups":sorted(meta[(site,yr)]["subgroups"]),
                    "all_occurrence_validated":all(v[2]=="Y" for v in meta[(site,yr)]["validation"]),
                    "any_ground":any(v=="G" for v in meta[(site,yr)]["vantage"]),
                })
            if st=="P": seen_p_before[site]=True

    kinds=Counter(t["kind"] for t in transitions)
    hist=Counter(t["history"] for t in transitions if t["kind"]=="AP")
    first=[t for t in transitions if t["history"]=="first_colonization"]
    recol=[t for t in transitions if t["history"]=="recolonization"]
    arisk=[t for t in transitions if t["kind"] in {"AA","AP"}]

    def support(events):
        return {
            "events":len(events),
            "distinct_sites":len({t["site"] for t in events}),
            "distinct_seasons":len({t["year"] for t in events}),
            "distinct_subgroups":len({g for t in events for g in t["subgroups"] if g}),
            "feature_counts":dict(Counter(t["feature"] for t in events)),
            "all_occurrence_validated_events":sum(t["all_occurrence_validated"] for t in events),
            "any_ground_events":sum(t["any_ground"] for t in events),
        }

    prior_a_risk=[]
    # A-risk transitions at sites with observed P strictly before risk year
    for t in arisk:
        site=t["site"]; yr=t["year"]
        if any(y<yr and st=="P" for y,st in bysite[site].items()):
            prior_a_risk.append(t)

    expansion_pass=(len(first)>=10 and len(arisk)>=50 and support(first)["distinct_subgroups"]>=3)
    recovery_pass=(len(recol)>=10 and len(prior_a_risk)>=30 and support(recol)["distinct_subgroups"]>=3)
    ap_by_feature=Counter(t["feature"] for t in transitions if t["kind"]=="AP")
    risk_by_feature=Counter(t["feature"] for t in arisk)
    feature_pass=all(ap_by_feature.get(k,0)>=5 and risk_by_feature.get(k,0)>=20 for k in ("island","continent"))

    result={
      "schema_version":1,
      "analysis_id":"east-antarctica-adelie-transition-support-gate-v1",
      "status":"support_counts_only_no_spatial_effects",
      "state_counts":dict(Counter(state.values())),
      "explicit_state_site_seasons":len(state),
      "transition_counts":dict(kinds),
      "ap_history_counts":dict(hist),
      "first_colonization_support":support(first),
      "recolonization_support":support(recol),
      "all_a_risk_support":support(arisk),
      "previously_occupied_a_risk_support":support(prior_a_risk),
      "gates":{
        "expansion_gate_passes":expansion_pass,
        "recovery_gate_passes":recovery_pass,
        "island_feature_interaction_gate_passes":feature_pass,
        "requirements":{
          "expansion":">=10 first colonizations, >=50 A-risk transitions, >=3 subgroups",
          "recovery":">=10 recolonizations, >=30 previously-occupied A-risk transitions, >=3 subgroups",
          "feature":">=5 A->P and >=20 A-risk in both island and continent classes"
        }
      },
      "distances_computed":False,"area_association_computed":False,
      "abundance_effect_computed":False,"p_values_computed":False
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()
