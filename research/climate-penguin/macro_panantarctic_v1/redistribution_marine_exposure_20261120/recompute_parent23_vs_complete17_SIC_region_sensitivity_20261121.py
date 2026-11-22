#!/usr/bin/env python3
"""Retrospective Adélie SIC-only complete 23 vs marine-complete 17 decomposition.

No outcome hunting, source changes, fitted causal effects, CI or forecasting.
The +5.5837pp 17-site R was already known before this coverage diagnostic.
Read immutable original-derived matched_support.csv; compare two existing
source-defined rosters without filling missing GLORYS salinity/SST values.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "matched_support.csv"
PARENT_AUDIT = HERE / "parent_roster_support_diagnostic.csv"
FULL17_AUDIT = HERE / "REGIONAL_SORTING_NULL_RESULT_20261121.json"
OUT = HERE / "SIC_23_VS_17_REGION_DECOMPOSITION_20261121.json"
EXCLUDED = {"BRDM", "BRDN", "BRDS", "CRZE", "CRZW", "ROYD"}


def load(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close(x, y, what, tol=1e-9):
    assert math.isclose(x, y, rel_tol=0.0, abs_tol=tol), (what, x, y)


def decompose(rows):
    """Symmetric exact two-time Shapley/Oaxaca-like accounting identity."""
    if len({r["site_id"] for r in rows}) != len(rows):
        raise AssertionError("Repeated site key")
    N0 = sum(float(r["n0"]) for r in rows)
    N1 = sum(float(r["n1"]) for r in rows)
    assert min(N0, N1) > 0
    groups = defaultdict(list)
    for r in rows:
        groups[r["source_region"]].append(r)
    parts = {}
    local, redistrib, early, late = 0.0, 0.0, 0.0, 0.0
    for r in rows:
        n0, n1 = float(r["n0"]), float(r["n1"])
        e0, e1 = float(r["sic_pp0"]), float(r["sic_pp1"])
        a, b = n0/N0, n1/N1
        early += a*e0
        late += b*e1
        local += 0.5*(a+b)*(e1-e0)
        redistrib += (b-a)*0.5*(e1+e0)

    between, within = 0.0, 0.0
    for region, members in groups.items():
        n0 = sum(float(r["n0"]) for r in members)
        n1 = sum(float(r["n1"]) for r in members)
        assert n0>0 and n1>0
        E, V = 0.0, 0.0
        for r in members:
            v0=float(r["n0"])/n0
            v1=float(r["n1"])/n1
            e=(float(r["sic_pp0"])+float(r["sic_pp1"]))/2
            E += 0.5*(v0+v1)*e
            V += (v1-v0)*e
        be=(n1/N1-n0/N0)*E
        wi=0.5*(n1/N1+n0/N0)*V
        between += be
        within += wi
        parts[region] = {
            "sites":len(members),"n0_median_sum":n0,"n1_median_sum":n1,
            "n0_share":n0/N0,"n1_share":n1/N1,
            "between_region_pp":be,"within_region_pp":wi,
        }
    close(redistrib, between+within, "within + between")
    close(late-early, local+redistrib, "local + allocation")
    return {
        "n_sites":len(rows),"n_regions":len(groups),"n0_median_sum":N0,
        "n1_median_sum":N1,"early_ice_pp":early,"late_ice_pp":late,
        "net_exposure_change_pp":late-early, "local_environment_component_pp":local,
        "nest_reallocation_component_pp":redistrib,
        "between_region_pp":between,"within_region_pp":within,
        "between_share_of_reallocation":between/redistrib if redistrib else None,
        "region_details":parts,
    }


def main():
    original = load(SOURCE)
    long = [r for r in original if r["comparison"]=="long" and r["radius"]=="0"]
    assert len(long)==23, f"Expected exactly 23 original early/late Adélie sites, got {len(long)}"
    for r in long:
        assert r["eligible_counts"]=="True", ("not source-qualified",r["site_id"])
        assert all(r[k] for k in ("n0","n1","sic_pp0","sic_pp1","source_region")),r
        assert float(r["n0"])>=0 and float(r["n1"])>=0
        if float(r["n0"]) == 0.0:
            assert float(r["n1"]) == 0.0, "True zero-to-positive colonization needs a separate formula"
    complete = [r for r in long if r["salinity0"] and r["salinity1"] and
                r["sst_C0"] and r["sst_C1"]]
    assert len(complete)==17
    removed = {r["site_id"] for r in long} - {r["site_id"] for r in complete}
    assert removed==EXCLUDED, ("Wrong source exclusion support",removed)
    assert {r["source_region"] for r in long} == {
        "Victoria Land","South Shetland Islands",
        "Central-west Antarctic Peninsula","Adelie Land",
    }
    assert {r["source_region"] for r in long if r["site_id"] in removed} == {"Victoria Land"}

    parent=decompose(long)
    matched=decompose(complete)
    src_parent = [r for r in load(PARENT_AUDIT) if r["comparison"]=="long" and r["radius"]=="0" and r["variable"]=="sic_pp"]
    assert len(src_parent)==1
    old=src_parent[0]
    for dest,src in [("early_ice_pp","early"),("late_ice_pp","late"),
                     ("net_exposure_change_pp","total"),("local_environment_component_pp","local"),
                     ("nest_reallocation_component_pp","redistribution")]:
        close(parent[dest],float(old[src]),"parent original "+src)
    prev=json.loads(FULL17_AUDIT.read_text(encoding="utf-8"))
    for key, val in [("nest_reallocation_component_pp","total"),
                     ("between_region_pp","between"),("within_region_pp","within")]:
        close(matched[key],prev["results"]["sic_pp"]["observed"][val],"17 original "+key)
    close(matched["between_share_of_reallocation"],
          prev["results"]["sic_pp"]["between_share_of_observed_R"],"17 share")

    loo_site=[]
    for drop in sorted(r["site_id"] for r in long):
        d=decompose([r for r in long if r["site_id"] != drop])
        loo_site.append({"dropped_site":drop, "dropped_region":next(r["source_region"] for r in long if r["site_id"]==drop),
                         "n_sites":d["n_sites"],"redistribution_pp":d["nest_reallocation_component_pp"],
                         "between_region_pp":d["between_region_pp"],
                         "within_region_pp":d["within_region_pp"]})
    loo_region=[]
    for drop in sorted({r["source_region"] for r in long}):
        d=decompose([r for r in long if r["source_region"] != drop])
        loo_region.append({"dropped_region":drop,"n_sites":d["n_sites"],
                           "redistribution_pp":d["nest_reallocation_component_pp"],
                           "between_region_pp":d["between_region_pp"],
                           "within_region_pp":d["within_region_pp"]})

    results={
        "status":"SOURCE_GATED_EXPLORATORY_COVERAGE_SENSITIVITY_NOT_CAUSAL",
        "periods":{"early":"1993-2000","late":"2011-2020"},
        "input":"matched_support.csv / parent_roster_support_diagnostic.csv / REGIONAL_SORTING_NULL_RESULT_20261121.json",
        "full23_sic_only":parent,"complete17_sic_salt_sst":matched,
        "six_victoria_land_sites_missing_glorys":sorted(removed),
        "complete17_vs_full23_early_nest_weight":matched["n0_median_sum"]/parent["n0_median_sum"],
        "complete17_vs_full23_late_nest_weight":matched["n1_median_sum"]/parent["n1_median_sum"],
        "leave_one_site":loo_site,"leave_one_region":loo_region,
        "sensitivity":{
            "all23_leave_one_site_between_positive":all(r["between_region_pp"]>0 for r in loo_site),
            "all4_leave_one_region_between_positive":all(r["between_region_pp"]>0 for r in loo_region),
            "all23_leave_one_site_total_reallocation_positive":all(r["redistribution_pp"]>0 for r in loo_site),
            "all4_leave_one_region_total_reallocation_positive":all(r["redistribution_pp"]>0 for r in loo_region),
            "leave_one_site_within_positive":[r["dropped_site"] for r in loo_site if r["within_region_pp"]>0],
            "leave_one_site_between_minmax":[min(r["between_region_pp"] for r in loo_site),max(r["between_region_pp"] for r in loo_site)],
            "leave_one_site_within_minmax":[min(r["within_region_pp"] for r in loo_site),max(r["within_region_pp"] for r in loo_site)],
        },
        "source_observation_warning":"Decade-specific nest medians are not synchronized total abundance; nested 23 are not independent regions.",
        "not_bird_migration_or_adaptation":True,"no_climate_causal_model_fitted":True,
        "not_a_future_penguin_population_forecast":True,
    }
    assert results["sensitivity"]["all23_leave_one_site_between_positive"]
    assert results["sensitivity"]["all4_leave_one_region_between_positive"]
    assert results["sensitivity"]["leave_one_site_within_positive"]==["CRZW"]
    OUT.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":results["status"],
        "n23":parent["n_sites"],"n17":matched["n_sites"],
        "full23_reallocation":parent["nest_reallocation_component_pp"],
        "full23_between":parent["between_region_pp"],
        "full23_within":parent["within_region_pp"],
        "complete17_reallocation":matched["nest_reallocation_component_pp"],
        "complete17_between":matched["between_region_pp"],
        "complete17_within":matched["within_region_pp"],
        "complete17_parent_nest_share_early":results["complete17_vs_full23_early_nest_weight"],
        "complete17_parent_nest_share_late":results["complete17_vs_full23_late_nest_weight"],
        "full23_loo_within_positive_only":results["sensitivity"]["leave_one_site_within_positive"],
        "full23_all_region_omissions_reallocation_positive":results["sensitivity"]["all4_leave_one_region_total_reallocation_positive"],
        "no_bird_migration_or_adaptation":True},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
