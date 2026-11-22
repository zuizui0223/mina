#!/usr/bin/env python3
"""Join source-verified penguin nest-status transitions to original annual SIC.

Physical *co-observation* audit only. This does not estimate recruitment,
colonization, ecological sea-ice tolerance or a causal effect. Transition
intervals with census years outside 1991-2020 retain missing SIC, not 0;
a target-first-positive sea-ice value is not a pre-settlement exposure if nest
survey timing is uncertain. Every source month is preserved for original
595×30×4. Dynamic land substrate is NOT observed in these sources.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np

MONTHS=(8,9,10,11)

def csvread(path):
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
def zipread(path,name):
    with zipfile.ZipFile(path) as f:
        assert f.testzip() is None
        return list(csv.DictReader(io.StringIO(f.read(name).decode("utf-8-sig"))))
def source_climate(zipfile_path):
    data=zipread(zipfile_path,"ice_595_outputs/original_595_site_months_120_source_QA.csv")
    assert len(data)==71400
    d=defaultdict(dict)
    for row in data:
        key=(row["site_id"],int(row["year"]))
        m=int(row["month"])
        assert m in MONTHS and m not in d[key]
        assert row["source_full_595_site_monthly_support"]=="OK"
        value=float(row["source_25km_buffer_mean_SIC_pct"])
        assert np.isfinite(value) and 0<=value<=100
        d[key][m]=value
    assert len(d)==595*30
    assert all(set(x)==set(MONTHS) for x in d.values())
    return {key:float(np.mean([months[k] for k in MONTHS])) for key,months in d.items()}

def pair_sic(ice,site,y):
    if y<1991 or y>2020:return None
    return ice[site,y]

def run(events,ice):
    out=[]
    for ev in events:
        site=ev["site_id"]
        y1=int(ev["last_previous_census_season"])
        y2=int(ev["first_changed_census_season"])
        pre=pair_sic(ice,site,y1)
        post=pair_sic(ice,site,y2)
        # SIC is contemporaneous, not necessarily before actual nesting.
        change=post-pre if pre is not None and post is not None else None
        # Last three physically observed years before first record-positive;
        # a wholly physical climate descriptor, not direct colony access.
        preyrs=[ice[site,y] for y in range(y2-3,y2) if 1991<=y<=2020]
        previous3=float(np.mean(preyrs)) if len(preyrs)==3 else None
        out.append({
          "site_id":site,"species":ev["species"],"source_region":ev["source_region"],
          "transition":ev["transition"],"from_source_count_year":y1,
          "to_source_count_year":y2,
          "source_census_gap_years":int(ev["inter_census_gap_years"]),
          "n_confirmed_followup_positive_censuses":int(ev["n_followup_positive_censuses"]),
          "sustained_initial_0_positive":
             ev["four_positive_followups_without_recorded_zero_from_initial_recorded_zero"]=="True",
          "true_original_0_year_SIC_AugNov_pp":pre,
          "true_first_changed_year_SIC_AugNov_pp":post,
          "change_in_SIC_AugNov_from_recorded0_to_first_positive_pp":change,
          "three_year_mean_SIC_before_changed_census_pp":previous3,
          "site_relative_SIC_at_change_vs_previous_three_years_pp":
             post-previous3 if post is not None and previous3 is not None else None,
          "SIC_at_new_nest_census_can_overlap_actual_nesting":True,
          "no_seaice_value_imputed_for_1984_or_other_pre1991_counts":True,
          "no_temporal_icefree_land_measurement":True
        })
    assert len(out)==35
    b=[x for x in out if x["sustained_initial_0_positive"]]
    assert len(b)==5 and all(x["species"]=="GEPE" for x in b)
    return out,b

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--status-events",type=Path,required=True)
    p.add_argument("--source-SIC-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    ev=csvread(a.status_events)
    assert len(ev)==35
    ice=source_climate(a.source_SIC_zip)
    out,focused=run(ev,ice)
    cols=list(out[0])
    with (a.out/"all_35_source_census_transitions_annual_original_SIC.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(out)
    with (a.out/"five_recorded_gentoo_appearance_events_original_SIC.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(focused)
    observed=sum(r["change_in_SIC_AugNov_from_recorded0_to_first_positive_pp"] is not None
                 for r in focused)
    limits=sum(r["true_original_0_year_SIC_AugNov_pp"] is None for r in focused)
    results={
      "status":"PASS_SOURCE_CENSUS_EVENT_TO_TRUE_ORIGINAL_SIC_CONTEXT_ONLY",
      "original_595_1991_2020_AugNov_site_months":71400,
      "original_595_1991_2020_site_years":len(ice),
      "original_transitions_checked":len(out),
      "all_original_sustained_gentoo_nesting_cases":len(focused),
      "n_five_gentoo_cases_with_both_recorded_0_year_and_first_positive_year_SIC":observed,
      "n_five_gentoo_cases_with_0_year_before_original_1991_satellite_support":limits,
      "source_SIC_zip_sha256":hashlib.sha256(a.source_SIC_zip.read_bytes()).hexdigest(),
      "source_fixed_three_year_window_census_year_regardless_of_observation_month":True,
      "SIC_1991_2020_only_no_1984_ice_invention":True,
      "no_annual_ice_free_land_or_foraging_behavior_available":True,
      "no_independent_regions_or_climate_selection_test":True,
      "case_rows":focused,
    }
    (a.out/"original_ice_nesting_transition_support_receipt.json").write_text(
        json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PENGUIN_NEST_TRANSITION_SIC_SOURCE="+json.dumps(results,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
