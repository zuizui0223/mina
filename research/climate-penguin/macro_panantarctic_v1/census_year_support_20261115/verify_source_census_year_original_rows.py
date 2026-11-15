#!/usr/bin/env python3
"""Verify real original recorded nest counts and 1,484 deterministic source-year sensitivities.

NO inferred absences, independent climate test, or population confidence interval.
These are nested survey-site cohorts; compare source values, not p-values.
"""
from __future__ import annotations
import csv, json, random, statistics
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
KM=111.195

def read(path):
    with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))

source=read(HERE/"source_original_514_observed_nest_census_rows_1990s_2010s.csv")
assert len(source)==514
assert not any(int(x["observed_nest_count"])<0 for x in source)
assert len(set((x["site_id"],x["species"],x["season"]) for x in source))==514
data=defaultdict(list)
for r in source:
    y=int(r["season"])
    if 1991<=y<=2000:era="early"
    elif 2011<=y<=2020:era="late"
    else:raise ValueError("Unexpected source census year")
    data[(r["species"],r["site_id"],era)].append((y,int(r["observed_nest_count"]),r["original_survey_method"]))
for k in data:data[k].sort()
assert len(data)==118
assert len({(sp,site) for sp,site,_ in data})==59

adpe=read(ROOT/"latitudinal_scale_20261115/original_adelie_19_26_35_site_growth_cohorts.csv")
three=read(ROOT/"allocation_20261115/original_three_decade_43_source_site_species.csv")
assert len(adpe)==80 and len(three)==43
cohorts=defaultdict(dict)
for r in adpe:
    cohorts[r["cohort"]][r["site_id"]]=r
assert {k:len(v) for k,v in cohorts.items()}=={
    "all_three_decades":19,"two_plus_endpoint_years":26,"one_plus_endpoint_year":35}
triples=defaultdict(dict)
for r in three:triples[r["species"]][r["site_id"]]=r
assert {k:len(v) for k,v in triples.items()}=={"ADPE":19,"CHPE":12,"GEPE":12}
assert set(triples["ADPE"])==set(cohorts["all_three_decades"])

def get_counts(sp,site,era):
    z=data[(sp,site,era)]
    assert z and len({t[0] for t in z})==len(z)
    assert len(set(t[2] for t in z))==1
    return z

def exact(sp,rows):
    first={};last={}
    for site,r in rows.items():
        n0=[v for _,v,_ in get_counts(sp,site,"early")]
        n1=[v for _,v,_ in get_counts(sp,site,"late")]
        key0,key1=(("n_early","n_late") if sp=="ADPE" and "n_early" in r else
                   ("median_original_nest_count_0","median_original_nest_count_2"))
        assert abs(statistics.median(n0)-float(r[key0]))<1e-8
        assert abs(statistics.median(n1)-float(r[key1]))<1e-8
        first[site]=float(r[key0]);last[site]=float(r[key1])
    return first,last

def south(rows,n0,n1):
    t0=sum(n0.values());t1=sum(n1.values())
    assert t0>0 and t1>0
    e=sum(float(rows[s]["latitude"])*v for s,v in n0.items())/t0
    l=sum(float(rows[s]["latitude"])*v for s,v in n1.items())/t1
    return KM*(e-l)

def hill(n0,n1):
    e=sum(n0.values());l=sum(n1.values())
    return 100*((l*l/sum(x*x for x in n1.values()))/(e*e/sum(x*x for x in n0.values()))-1)

for label,rows in cohorts.items():exact("ADPE",rows)
for sp,rows in triples.items():exact(sp,rows)

max_error=0.
def check(value,archived):
    global max_error
    diff=abs(value-float(archived))
    max_error=max(max_error,diff)
    if diff>1e-7:raise AssertionError(("Source census QA mismatch",value,archived,diff))
n_deleted=0
for r in read(HERE/"source_one_actual_census_year_omission_per_site.csv"):
    rows=cohorts[r["cohort"]];n0,n1=exact("ADPE",rows)
    era=r["period"];site=r["site_id"];year=int(r["deleted_observed_year"])
    remaining=[v for y,v,_ in get_counts("ADPE",site,era) if y!=year]
    assert len(remaining)>=1
    if era=="early":n0[site]=statistics.median(remaining)
    else:n1[site]=statistics.median(remaining)
    check(south(rows,n0,n1),r["southward_km_after_deletion"])
    check(hill(n0,n1),r["hill2_pct_after_deletion"])
    n_deleted+=1
assert n_deleted==745

n_anchor=0
for r in read(HERE/"source_nearest_observed_100_joint_anchor_years.csv"):
    rows=cohorts[r["cohort"]];year0=int(r["anchor_early_year"]);year1=int(r["anchor_late_year"])
    n0={};n1={}
    for site in rows:
        n0[site]=min(get_counts("ADPE",site,"early"),key=lambda v:(abs(v[0]-year0),v[0]))[1]
        n1[site]=min(get_counts("ADPE",site,"late"),key=lambda v:(abs(v[0]-year1),v[0]))[1]
    check(south(rows,n0,n1),r["southward_km_nearest_real_original_count"])
    check(hill(n0,n1),r["hill2_pct_nearest_original_count"])
    n_anchor+=1
assert n_anchor==300

n_other=0
for r in read(HERE/"three_penguin_species_true_census_year_deletion.csv"):
    sp=r["species"];rows=triples[sp];n0,n1=exact(sp,rows)
    site=r["site_id"];era=r["period"];yr=int(r["deleted_real_census_year"])
    v=[n for y,n,_ in get_counts(sp,site,era) if y!=yr]
    assert len(v)>=1
    if era=="early":n0[site]=statistics.median(v)
    else:n1[site]=statistics.median(v)
    check(south(rows,n0,n1),r["one_observed_year_removed_southward_km"])
    n_other+=1
assert n_other==439

stat=read(HERE/"source_1990s_2010s_census_year_resampling_summary.csv")
assert len(stat)==24
for r in stat:
    if r["metric"]=="southward_km" and r["sampling_sensitivity"]=="year_bootstrap":
        label=r["cohort"]
        n0,n1=exact("ADPE",cohorts[label])
        check(south(cohorts[label],n0,n1),r["published_source_baseline"])
        assert float(r["fraction_positive"])==1.0

rng=random.Random(20261120)
independent_simulations=2000
positive_adpe=0
positive_gentoo=0
for i in range(independent_simulations):
    for sp in ("ADPE","GEPE"):
        rows=triples[sp]
        n0={site:rng.choice(get_counts(sp,site,"early"))[1] for site in rows}
        n1={site:rng.choice(get_counts(sp,site,"late"))[1] for site in rows}
        flag=south(rows,n0,n1)>0
        if sp=="ADPE":positive_adpe+=int(flag)
        else:positive_gentoo+=int(flag)
assert positive_adpe==independent_simulations
assert 0<positive_gentoo<independent_simulations
result={"status":"PASS all original 514 records with 1484 deterministic diagnostic rows",
        "unique_true_source_census_rows":len(source),
        "nested_adpe_roster_sizes":{k:len(v) for k,v in cohorts.items()},
        "source_three_species_roster_sizes":{k:len(v) for k,v in triples.items()},
        "n_single_site_year_deletions":n_deleted,
        "n_common_anchor_year_scenarios":n_anchor,
        "n_three_species_site_year_deletions":n_other,
        "maximum_original_CSV_rounding_discrepancy":max_error,
        "independent_visit_draws":independent_simulations,
        "Adelie_southward_draws":positive_adpe,
        "Gentoo_southward_draws":positive_gentoo,
        "no_new_independent_biological_samples":True,
        "not_a_population_CI_nor_causal_seaice_test":True}
print(json.dumps(result,ensure_ascii=False,indent=2))
