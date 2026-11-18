#!/usr/bin/env python3
"""Independent arithmetic validation for same-year three-species census sensitivity.
This does not use the Node calculation functions or alter source eligibility.
"""
from __future__ import annotations
from collections import defaultdict
import csv, json, math, statistics
from pathlib import Path

D = Path(__file__).resolve().parent / "outputs"
def csvrows(name):
    with (D / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
def slope(x, y):
    xm=statistics.mean(x); ym=statistics.mean(y)
    return 10*sum((a-xm)*(b-ym) for a,b in zip(x,y))/sum((a-xm)**2 for a in x)
def eq(a,b):
    if not math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-10):
        raise AssertionError(f"independent calculation mismatch: {a}, {b}")

p=csvrows("three_species_same_year_54.csv")
c=csvrows("site_6_support_gate.csv")
s=csvrows("site_6_summary_with_BISC_unavailable.csv")
summ=json.loads((D/"summary.json").read_text(encoding="utf-8"))
assert len(p)==54 and len(c)==67 and len(s)==6
assert len({(r["site_id"],r["year"]) for r in p})==54
assert sum(r["three_species_eligible"]=="true" for r in c)==54
by=defaultdict(list)
for row in p:
    a,g,h=[int(row[k]) for k in ["Adelie_nests","Gentoo_nests","Chinstrap_nests"]]
    assert a>0 and g>0 and h>=0
    assert int(row["focal_pair_nests"])==a+g
    assert int(row["three_species_subtotal_nests"])==a+g+h
    assert math.isclose(sum(float(row[k]) for k in [
        "Adelie_three_share","Gentoo_three_share","Chinstrap_three_share"]),1,abs_tol=1e-12)
    assert math.isclose(float(row["Chinstrap_three_share"]),h/(a+g+h),abs_tol=1e-12)
    by[row["site_id"]].append(row)
assert set(by)=={"ARDL","LION","LLAN","PCHA","PETE"}
ep2=ep3=sl2=sl3=conc_end=conc_slope=robust3=robust_eligible=0
pcts=[]
for site in s:
    if site["status"]=="NO_COMPLETE_THREE_SPECIES_YEARS":
        assert site["site_id"]=="BISC" and int(site["n_triplet_years"])==0
        continue
    d=sorted(by[site["site_id"]],key=lambda x:int(x["year"]))
    assert len(d)==int(site["n_triplet_years"])
    years=[int(row["year"]) for row in d]
    t2=[int(row["focal_pair_nests"]) for row in d]
    t3=[int(row["three_species_subtotal_nests"]) for row in d]
    eq(100*(t2[-1]/t2[0]-1),site["pair_pct_change"])
    eq(100*(t3[-1]/t3[0]-1),site["three_pct_change"])
    eq(slope(years,[math.log(x) for x in t2]),site["pair_log_slope_decade"])
    eq(slope(years,[math.log(x) for x in t3]),site["three_log_slope_decade"])
    ep2+=t2[-1]>t2[0]; ep3+=t3[-1]>t3[0]
    sl2+=float(site["pair_log_slope_decade"])>0
    sl3+=float(site["three_log_slope_decade"])>0
    conc_end+=((t2[-1]-t2[0])*(t3[-1]-t3[0]))>0
    conc_slope+=float(site["pair_log_slope_decade"])*float(site["three_log_slope_decade"])>0
    pcts.append(100*(t3[-1]/t3[0]-1))
    if len(d)>=6:
        robust_eligible+=1
        q1=slope(years[1:],[math.log(x) for x in t3[1:]])
        q2=slope(years[:-1],[math.log(x) for x in t3[:-1]])
        eq(q1,site["three_dropfirst_slope_decade"])
        eq(q2,site["three_droplast_slope_decade"])
        robust3+=float(site["three_log_slope_decade"])>0 and q1>0 and q2>0
    else:
        assert site["three_dropfirst_slope_decade"]=="" and site["three_droplast_slope_decade"]==""
assert (ep2,ep3,sl2,sl3,conc_end,conc_slope)==tuple(summ[k] for k in [
    "same_year_pair_positive_endpoints","same_year_three_positive_endpoints",
    "same_year_pair_positive_slopes","same_year_three_positive_slopes",
    "endpoint_sign_concordance","slope_sign_concordance"])
assert robust_eligible==summ["eligible_three_endpoint_robustness_sites"]
assert robust3==summ["robust_three_positive_slopes"]
eq(statistics.median(pcts),summ["median_three_pct_change"])
assert summ["n_missing_chinstrap_records"]==13
print(json.dumps({"status":"INDEPENDENT_RECOMPUTATION_PASS",
    "complete_site_years":len(p),"eligible_sites":len(by),
    "pair_endpoint_positive":ep2,"three_endpoint_positive":ep3,
    "pair_slope_positive":sl2,"three_slope_positive":sl3,
    "three_positive_endpoint_robust":robust3,
    "median_three_pct_change":statistics.median(pcts)},ensure_ascii=False))
