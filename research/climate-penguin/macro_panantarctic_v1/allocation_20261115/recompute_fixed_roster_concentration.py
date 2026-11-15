#!/usr/bin/env python3
"""Recompute source-constrained colony allocation from real frozen 43/50 rows.

No census missingness imputation, independent site p values, inferred
colonization/migration, biological effective population size, or climate cause.
"""
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPECIES = ("ADPE", "CHPE", "GEPE")
EARLY = "1991-2000"
LATE = "2011-2020"


def read(name):
    with (HERE / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def eff(counts, q=2):
    v = [float(n) for n in counts]
    assert all(math.isfinite(n) and n >= 0 for n in v) and sum(v) > 0
    p = [n / sum(v) for n in v if n > 0]
    if q == 2:
        return 1 / sum(x*x for x in p)
    if q == 1:
        return math.exp(-sum(x*math.log(x) for x in p))
    raise ValueError(q)


def row_stats(rows, key):
    v = [float(r[key]) for r in rows]
    return {"total_decade_site_medians_NOT_synchronous_population":sum(v),
            "hill1":eff(v, 1), "hill2":eff(v, 2),
            "maximum_colony_weight":max(v) / sum(v),
            "maximum_colony":rows[v.index(max(v))]["site_id"]}


def source_set(rows):
    ids = [(r["site_id"], r["species"]) for r in rows]
    assert len(ids) == len(set(ids))
    return set(ids)


def change(a, b):
    return (b / a - 1) * 100


def main():
    three = read("original_three_decade_43_source_site_species.csv")
    pair = read("original_strict_paired_end_50_source_site_species.csv")
    assert len(three) == 43 and len(pair) == 50
    assert set(SPECIES) == set(r["species"] for r in three + pair)
    assert source_set(three).issubset(source_set(pair))
    assert len(source_set(pair) - source_set(three)) == 7
    by_pair = {(r["site_id"], r["species"]):r for r in pair}
    for r in three:
        p = by_pair[r["site_id"],r["species"]]
        for old,new in [("median_original_nest_count_0","site_median_observed_nests_early"),
                        ("median_original_nest_count_2","site_median_observed_nests_late")]:
            assert abs(float(r[old])-float(p[new])) < 1e-8
        assert r["source_region"] == p["source_region"]
        assert r["polar_250km_block"] == p["polar_250km_block"]
        assert all(int(r["n_census_years_"+str(i)]) >= 2 for i in range(3))
        assert r["no_original_unobserved_absences_imputed"].lower() == "true"
    assert {sp:sum(r["species"]==sp for r in three) for sp in SPECIES} == {"ADPE":19,"CHPE":12,"GEPE":12}
    assert {sp:sum(r["species"]==sp for r in pair) for sp in SPECIES} == {"ADPE":26,"CHPE":12,"GEPE":12}

    results=[]
    for sp in SPECIES:
        for cohort,rows,columns in (
          ("three_decades_2plus_each",[r for r in three if r["species"]==sp],
           ("median_original_nest_count_0","median_original_nest_count_1","median_original_nest_count_2")),
          ("end_decades_2plus_each",[r for r in pair if r["species"]==sp],
           ("site_median_observed_nests_early","site_median_observed_nests_late"))):
            stages=[row_stats(rows,c) for c in columns]
            q2_change=change(stages[0]["hill2"],stages[-1]["hill2"])
            omit_sites={}
            for row in rows:
                subset=[q for q in rows if q["site_id"]!=row["site_id"]]
                omit_sites[row["site_id"]]=change(eff([q[columns[0]] for q in subset]),
                                                  eff([q[columns[-1]] for q in subset]))
            results.append({
                "species":sp,"observational_cohort":cohort,"site_ids":len(rows),
                "source_reporting_regions":len(set(r["source_region"] for r in rows)),
                "source_250km_blocks":len(set(r["polar_250km_block"] for r in rows)),
                "period_stats":stages,
                "percentage_change_sum_site_medians":change(stages[0]["total_decade_site_medians_NOT_synchronous_population"],
                                                              stages[-1]["total_decade_site_medians_NOT_synchronous_population"]),
                "percentage_change_hill2":q2_change,
                "percentage_change_hill1":change(stages[0]["hill1"],stages[-1]["hill1"]),
                "leave_one_colony_site_out_hill2_change_percent":omit_sites,
                "site_omission_that_reverses_full_cohort_sign":
                    [site for site,d in omit_sites.items() if d*q2_change < 0],
            })
    get=lambda cohort:next(x for x in results if x["species"]=="ADPE" and x["observational_cohort"]==cohort)
    x=get("three_decades_2plus_each")
    y=get("end_decades_2plus_each")
    assert abs(x["period_stats"][0]["hill2"]-5.246333258879388)<1e-10
    assert abs(x["period_stats"][2]["hill2"]-3.6736139701740416)<1e-10
    assert abs(y["period_stats"][0]["hill2"]-3.6180059640994426)<1e-10
    assert abs(y["period_stats"][1]["hill2"]-3.912913792176839)<1e-10
    assert x["site_omission_that_reverses_full_cohort_sign"]==["CRZW"]
    assert y["site_omission_that_reverses_full_cohort_sign"]==["ADAR"]
    assert x["percentage_change_hill2"]<0 and y["percentage_change_hill2"]>0
    extra=[r for r in pair if (r["site_id"],r["species"]) not in source_set(three)]
    assert sorted(x["site_id"] for x in extra)==["ADAR","CSOU","JONE","MAND","PHIL","PTHO","WHEA"]
    meta={"status":"SOURCE_REPRODUCED_NONINFERENTIAL_ROSTER_SENSITIVITY",
          "source_actions_runs":[42844104869,42788030834],
          "source_artifact_ids":[13776484021,13750780064],
          "n_three_decade_colony_species":43,"n_end_decade_colony_species":50,
          "no_absence_imputation":True,
          "cohort_choice_reverses_ADPE_hill2_direction":True,
          "direct_main_source_outputs":results,
          "no_inferred_continental_population_size_or_climate_causality":True}
    print(json.dumps(meta,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
