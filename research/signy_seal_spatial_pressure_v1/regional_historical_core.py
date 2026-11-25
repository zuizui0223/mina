"""Reproduce frozen regional historical-core contrast from archived 43-row source.
Usage: python regional_historical_core.py source.csv result.json
"""
import csv, hashlib, json, math, sys
from pathlib import Path
from collections import defaultdict
PIN="a5ccb7a527605d28804ef389109f416bd6dea090"
def run(path):
    b=Path(path).read_bytes()
    if hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()!=PIN:
        raise ValueError("archived Git blob mismatch")
    rows=list(csv.DictReader(b.decode("utf-8-sig").splitlines()))
    if len(rows)!=43 or len({(r["site_id"],r["species"]) for r in rows})!=43:
        raise ValueError("fixed source roster mismatch")
    groups=defaultdict(list)
    for r in rows:
        if r["no_original_unobserved_absences_imputed"].lower()!="true":
            raise ValueError("absence imputation")
        if not all(int(r["n_census_years_"+str(i)])>=2 for i in range(3)):
            raise ValueError("insufficient census support")
        n=[float(r["median_original_nest_count_"+str(i)]) for i in range(3)]
        if not all(math.isfinite(v) and v>=0 for v in n):
            raise ValueError("invalid counts")
        groups[(r["species"],r["source_region"])].append(
            {"id":r["site_id"],"block":r["polar_250km_block"],"n":n})
    result=[]
    def total(rows,i):return sum(r["n"][i] for r in rows)
    for (sp,reg),g in groups.items():
        d={"group":sp+" | "+reg,"n_sites":len(g),"n_blocks":len({r["block"] for r in g})}
        if len(g)<3:
            result.append(dict(d,status="BLOCKED_FEWER_THAN_3_SITES"));continue
        g=sorted(g,key=lambda r:(-r["n"][0],r["id"]))
        c,rem=g[0],g[1:]
        a=c["n"];b=[total(rem,i) for i in range(3)];t=[x+y for x,y in zip(a,b)]
        if a[0]<=0 or a[0]==rem[0]["n"][0] or a[1]<=0 or b[1]<=0 or t[2]<=0:
            result.append(dict(d,status="BLOCKED_RANK_OR_DENOMINATOR"));continue
        p=[x/y for x,y in zip(a,t)]
        def share_change(rr):
            m=a[1]+total(rr,1);l=a[2]+total(rr,2)
            return 100*(a[2]/l-a[1]/m) if min(m,l)>0 else None
        loo=[{"omitted_site":r["id"],"delta_core_share_pp":share_change([v for v in rem if v is not r])} for r in rem]
        v=[x["delta_core_share_pp"] for x in loo]
        dc=a[2]-a[1];dr=b[2]-b[1];dn=t[2]-t[1]
        result.append(dict(d,status="DESCRIPTIVE",core_site=c["id"],core_block=c["block"],core_counts=a,
            remainder_counts=b,totals=t,core_shares=p,core_retention=a[2]/a[1],remainder_retention=b[2]/b[1],
            delta_core_share_pp=100*(p[2]-p[1]),total_change_pct=100*(t[2]/t[1]-1),
            core_excess=a[2]-p[1]*t[2],core_change=dc,remainder_change=dr,total_change=dn,
            core_fraction_net_change=dc/dn if dn else None,loo_remainder=loo,
            loo_range_pp=[min(v),max(v)] if all(x is not None for x in v) else None))
    return {"status":"EXPLORATORY_REGIONAL_CORE_DESCRIPTIVE","source_blob":PIN,
        "not_synchronized_population_totals":True,"results":result}
if __name__=="__main__":
    Path(sys.argv[2]).write_text(json.dumps(run(sys.argv[1]),indent=2)+"\n")
