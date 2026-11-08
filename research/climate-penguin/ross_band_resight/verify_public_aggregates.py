#!/usr/bin/env python3
"""Validate publicly shareable Ross penguin aggregate outputs (no raw bird IDs)."""
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/"outputs"

def load(name):
    with (OUT/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))
def main():
    data=json.loads((OUT/"verified_aggregate_no_individual_ids.json").read_text(encoding="utf-8"))
    visit=load("anonymous_off_natal_resight_vs_nest_by_route.csv")
    annual=load("anonymous_colony_season_record_availability.csv")
    natal=load("natal_chick_banded_nesting_other_colony.csv")
    switches=load("breeding_colony_switch_observed.csv")
    if (len(visit),len(annual),len(natal),len(switches))!=(11,36,6,3):
        raise ValueError("Unexpected original aggregate support shape")
    def sumcol(rows,key):
        return sum(int(row[key]) for row in rows)
    if sumcol(visit,"n_unique_bands_with_strict_active_nest_at_other_colony")!=64:
        raise ValueError("Off-natal nests and observed route table inconsistent")
    if sumcol(visit,"n_unique_bands_observed_at_other_colony_age2_plus")!=520:
        raise ValueError("Visit-route sum changed")
    if sumcol(annual,"verified_resight_event_rows")!=94678:
        raise ValueError("Original eligible observation total changed")
    if sumcol(annual,"strict_active_nest_event_rows")!=15157:
        raise ValueError("Original active nests total changed")
    if sumcol(natal,"distinct_source_birds")!=64:
        raise ValueError("Natal offsite nests in published routes changed")
    if sumcol(switches,"individuals")!=3:
        raise ValueError("Observed nesting-switch cases changed")
    if (data["n_CHIC_post_age2_ever_verified_resighted_any_site"],
        data["n_CHIC_post_age2_ever_verified_resighted_off_natal"],
        data["n_CHIC_off_natal_first_documented_strict_nesting_year"],
        data["n_CHIC_off_natal_ever_documented_strict_nesting_at_natal_site"],
        data["n_birds_with_active_nests_at_two_colonies_in_distinct_seasons"],
        data["n_verified_colony_season_coverage_cells"])!=(7132,506,64,2,3,36):
        raise ValueError("Public JSON stage or source-coverage reconciliation failed")
    aggregate=defaultdict(lambda:{"n_seasons":0,"events":0,"nest_events":0})
    for row in annual:
        site=row["colony"];z=aggregate[site]
        z["n_seasons"]+=1
        z["events"]+=int(row["verified_resight_event_rows"])
        z["nest_events"]+=int(row["strict_active_nest_event_rows"])
    expected={"BEAU":(1,3,0),"BIRD":(5,5693,493),"CROZ":(19,80437,14206),"ROYD":(11,8545,458)}
    for site,(n,events,nests) in expected.items():
        got=aggregate[site]
        if (got["n_seasons"],got["events"],got["nest_events"])!=(n,events,nests):
            raise ValueError("Public site/year effort numbers inconsistent: "+site)
    for site_row in data["original_observation_records_by_colony"]:
        key=site_row["colony"]
        if site_row["verified_resight_events"]!=aggregate[key]["events"]:
            raise ValueError("JSON observation-support report mismatch")
    forbid={"bandnumb","individual_id","tag_id","band_id","raw_band","initials","notes","observer","raw_date"}
    for name in ("anonymous_off_natal_resight_vs_nest_by_route.csv",
                 "anonymous_colony_season_record_availability.csv",
                 "natal_chick_banded_nesting_other_colony.csv",
                 "breeding_colony_switch_observed.csv"):
        with (OUT/name).open(encoding="utf-8") as f:
            h=set(next(csv.reader(f)))
        if h&forbid:
            raise ValueError("Potential private original individual column exported: "+name)
    print("ROSS_PUBLIC_AGGREGATE_QA_PASS="+json.dumps({
        "n_source_qualifying_events":94678,"n_strict_nest_event_rows":15157,
        "n_colony_season_availability":36,
        "n_chick_banded_ever_observed_off_natal":506,
        "n_chick_banded_off_natal_nest":64,
        "n_individuals_strict_two_colony_nesting":3,
        "n_original_usable_chick_banded_resight_individuals":7132,
        "raw_individual_band_ids_distributed":False},ensure_ascii=False))
if __name__=="__main__":
    main()
