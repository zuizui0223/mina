"""Source-count support for independent breeding-zero events before any moss linkage.

Original MAPPPD observational source remains unchanged. Exact recorded zero !=
never surveyed or permanent extinction. No greening, warming or hazard model.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]/"outputs/comparison_audit"
ZERO=BASE/"mapppd_zero_episodes.csv"
STATE=BASE/"mapppd_consistent_observed_states.csv"
VEG=BASE/"vegetation_mapppd_spatial_support.csv"
SPECIES=("ADPE","CHPE","GEPE","MCPE","EMPE")
MIN_DISTINCT_ZERO_VISITS=2
MIN_INDEPENDENT_SITES_FOR_SPECIES_MACRO=5
MIN_INDEPENDENT_REGIONS_FOR_SPECIES_MACRO=3

def readcsv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit():
    zeros=readcsv(ZERO)
    observed=readcsv(STATE)
    plant=readcsv(VEG)
    assert len(zeros)==38 and len(observed)>3000
    assert len({(r["site_id"],r["species_id"],r["first_observed_zero"]) for r in zeros})==38
    # A source site/species may have >1 zero episode followed by reoccupation.
    # Those are separate spells, not independent islands or species×sites.
    assert len({(r["site_id"],r["species_id"]) for r in zeros})==37
    assert all(r["species_id"] in SPECIES for r in zeros)
    obs=defaultdict(list)
    for r in observed:
        if r["occupied"] not in ("0","1"):continue
        obs[r["site_id"],r["species_id"]].append(r)
    map2={(r["site_id"],r["radius_m"]):r for r in plant}
    decisions=[]
    for r in zeros:
        key=(r["site_id"],r["species_id"])
        seq=sorted(obs.get(key,[]),key=lambda x:int(x["season"]))
        first=int(r["first_observed_zero"])
        last=int(r["last_observed_zero"])
        prev=int(r["last_positive"])
        assert prev<first and first<=last
        prior=[x for x in seq if int(x["season"])<=prev and x["occupied"]=="1"]
        later_zero=[x for x in seq if first<=int(x["season"])<=last and x["occupied"]=="0"]
        visit_years=sorted({int(x["season"]) for x in later_zero})
        documented=len(visit_years)>=MIN_DISTINCT_ZERO_VISITS
        originally_reported=int(r["n_zero_visits"])
        if len(visit_years)!=originally_reported:
            raise ValueError(f"SOURCE_STOP zero-year mismatch for {key}: {len(visit_years)} vs {originally_reported}")
        region=next((x["region"] for x in seq if x["region"]),None)
        vegrow=map2.get((r["site_id"],"2000"))
        decisions.append({
         "site_id":r["site_id"],"species_id":r["species_id"],
         "original_region":region,"last_recorded_positive_year":prev,
         "first_observed_zero_year":first,"last_observed_zero_year":last,
         "recorded_zero_visit_years":";".join(map(str,visit_years)),
         "zero_visit_years_n":len(visit_years),
         "previous_positive_visited_years_n":len({int(x["season"]) for x in prior}),
         "recorded_reappearance":bool(r["reappearance"].strip()),
         "repeat_zero_source_support":documented,
         "no_observed_reappearance_in_snapshot":not bool(r["reappearance"].strip()),
         "eligible_as_repeated_zero_source_candidate":documented and not bool(r["reappearance"].strip()),
         "Plantarctica_2km_source_detected":None if vegrow is None else vegrow["mapped_terrestrial_detected"]=="True",
         "Plantarctica_is_static_2024_composite":True,
         "verified_colony_nest_polygon":False,
         "verified_never_occupied_control":False,
         "genuine_historical_island_vegetation_trend":False
        })
    by_species={}
    for species in SPECIES:
        arr=[x for x in decisions if x["species_id"]==species]
        candidate=[x for x in arr if x["eligible_as_repeated_zero_source_candidate"]]
        regions=sorted({x["original_region"] for x in candidate if x["original_region"]})
        by_species[species]={
            "apparent_first_zero_episodes":len(arr),
            "zero_episodes_with_at_least_two_original_surveyed_zeros":sum(x["repeat_zero_source_support"] for x in arr),
            "repeated_zero_without_recorded_reappearance":len(candidate),
            "distinct_site_ids":len({x["site_id"] for x in candidate}),
            "regions_in_repeated_zero_candidates":regions,
            "passes_exploratory_macro_source_replication_floor":(
                len({x["site_id"] for x in candidate})>=MIN_INDEPENDENT_SITES_FOR_SPECIES_MACRO and
                len(regions)>=MIN_INDEPENDENT_REGIONS_FOR_SPECIES_MACRO
            )
        }
    result={
       "schema":1,
       "status":"ORIGINAL_SOURCE_REPEATED_ZERO_SUPPORT_NOT_ISLAND_GRENNING",
       "sources":{"zero_episodes_SHA256":sha(ZERO),"observed_states_SHA256":sha(STATE),
                  "mapped_vegetation_static_source_SHA256":sha(VEG)},
       "method":"Original 38 MAPPPD documented zero-episode records across species. Confirm >=2 distinct surveyed years with actual numeric zero and no recorded reappearance in frozen source. Never turn missing years into zero.",
       "input_original_zero_episodes":len(zeros),
       "distinct_site_species_in_original_episodes":len({(r["site_id"],r["species_id"]) for r in zeros}),
       "multiple_zero_spells_not_independent_sites":True,
       "original_source_species":by_species,
       "n_repeated_zero_no_reappearance":sum(z["eligible_as_repeated_zero_source_candidate"] for z in decisions),
       "strict_island_status_qualified":False,
       "source_panel_ready_for_ant_wide_causal_greening":False,
       "critical_limits":[
          "Repeated observed zero is not proof biological permanent extinction or standardized full-island survey.",
          "Source site IDs may be a mainland coast or multiple plots, not uniquely verified physical islands.",
          "Litchfield official ASPA primary data have 2009–2012 zeros missing from this frozen MAPPPD snapshot; add only as explicitly separate original-source crosswalk, never silent override.",
          "No source-confirmed never-occupied controls, historical nest polygons or annually matched vegetation histories here.",
          "A 2024 published single-season vegetation composite cannot estimate post-event plant gain.",
          "These outcomes have been exposed before eligibility gates; this is a support diagnostic, not prospective hypothesis confirmation."
       ]}
    return decisions,result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    rows,receipt=audit()
    with (args.out/"recorded_zero_source_gate.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    (args.out/"recorded_zero_source_result.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("ORIGINAL_PENGUIN_ZERO_SUPPORT_GATE="+json.dumps(receipt,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
