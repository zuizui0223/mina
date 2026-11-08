#!/usr/bin/env python3
"""Independent arithmetic check of six-site compensation output (standard library only)."""
from __future__ import annotations
from collections import defaultdict
import csv,json,math,statistics
from pathlib import Path
P=Path(__file__).parent/"outputs"
def rows(name):
    with (P/name).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def slope(xs,ys):
    a=statistics.mean(xs);b=statistics.mean(ys)
    return 10*sum((x-a)*(y-b) for x,y in zip(xs,ys))/sum((x-a)**2 for x in xs)
def close(a,b):
    if not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10):
        raise AssertionError(f"Independent calculation failed: {a} vs {b}")
s=json.loads((P/"summary.json").read_text(encoding="utf-8"))
d=rows("six_site_yearly_focal_pair_counts.csv")
m=rows("six_site_compensation_metrics.csv")
c=rows("chinstrap_observability_audit.csv")
assert len(d)==67 and len(c)==67 and len(m)==6
assert s["n_pair_site_years"]==67 and s["n_sites"]==6
by=defaultdict(list)
assert len({(r["site_id"],int(r["year"])) for r in d})==len(d)
for row in d:
    a,g,p=[float(row[k]) for k in ("Adelie_nests","Gentoo_nests","focal_pair_subtotal_nests")]
    assert a>0 and g>0 and a.is_integer() and g.is_integer()
    close(a+g,p)
    close(g/p,float(row["Gentoo_share_within_pair"]))
    close(math.log(g/a),float(row["log_Gentoo_Adelie_ratio"]))
    close(math.log(p),float(row["log_focal_pair_subtotal"]))
    by[row["site_id"]].append(row)
assert set(by)==set(r["site_id"] for r in m)
end_positive=0;slopes_positive=0;stable_positive=0;pct=[]
for r in m:
    group=sorted(by[r["site_id"]],key=lambda x:int(x["year"]))
    yy=[int(x["year"]) for x in group]
    sub=[float(x["focal_pair_subtotal_nests"]) for x in group]
    ad=[float(x["Adelie_nests"]) for x in group]
    ge=[float(x["Gentoo_nests"]) for x in group]
    assert len(group)==int(r["n_shared_years"])
    close(100*(sub[-1]/sub[0]-1),float(r["subtotal_pct_change"]))
    close((ge[-1]/ad[-1])/(ge[0]/ad[0]),float(r["ratio_fold"]))
    close(slope(yy,list(map(math.log,sub))),float(r["all_year_log_subtotal_slope_per_decade"]))
    close(slope(yy[1:],list(map(math.log,sub[1:]))),float(r["subtotal_drop_first_year_slope_per_decade"]))
    close(slope(yy[:-1],list(map(math.log,sub[:-1]))),float(r["subtotal_drop_last_year_slope_per_decade"]))
    close(slope(yy,list(map(math.log,ad))),float(r["all_year_log_Adelie_slope_per_decade"]))
    close(slope(yy,list(map(math.log,ge))),float(r["all_year_log_Gentoo_slope_per_decade"]))
    end_positive+=sub[-1]>sub[0]
    slopes_positive+=float(r["all_year_log_subtotal_slope_per_decade"])>0
    stable_positive+=r["subtotal_deletion_sign_stable"]=="true"
    pct.append(100*(sub[-1]/sub[0]-1))
assert s["count_endpoint_subtotal_increases"]==end_positive
assert s["count_all_year_subtotal_growth_slopes"]==slopes_positive
assert s["count_positive_slope_stable_to_drop_first_and_last"]==stable_positive
close(statistics.median(pct),s["median_subtotal_pct_change"])
nc=sum(r["chinstrap_record_exists"]=="true" for r in c)
mch=sum(r["chinstrap_method_matches_both"]=="true" for r in c)
assert nc==s["chinstrap_source"]["n_paired_years_with_source_chinstrap_record"]
assert mch==s["chinstrap_source"]["n_paired_years_with_same_method_chinstrap_record"]
print(json.dumps({"status":"INDEPENDENT_NUMERIC_RECOMPUTATION_SUCCESS",
                  "site_years":len(d),"sites":len(m),"endpoint_gains":end_positive,
                  "all_year_gains":slopes_positive,"both_endpoint_deletions_stable":stable_positive,
                  "median_pct":statistics.median(pct),"chinstrap_support":nc},ensure_ascii=False))
