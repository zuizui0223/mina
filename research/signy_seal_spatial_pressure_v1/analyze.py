"""Six fixed census zones: source-audited before/after descriptive redistribution."""
import argparse,csv,hashlib,io,json,re,zipfile
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
PIN="58f87d83afdd78f30daf5489f45f4221af30b1e413090c3d9a5493e602eacb3a"
ZONES=tuple("123456")
FIELDS={"fur":"Number_of_fur_seals","elephant":"Number_of_elephant_seals","weddell":"Number_of_weddell_seals"}
EARLY=tuple(range(2010,2015))
LATE=tuple(range(2016,2025))
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError("ZIP CRC")
        names=[n for n in z.namelist() if n.endswith("/Signy_seal_annual_counts_by_area.csv") or n=="Signy_seal_annual_counts_by_area.csv"]
        if len(names)!=1:raise ValueError("ambiguous original member")
        b=z.read(names[0])
    if sha(b)!=PIN:raise ValueError("source CSV drift")
    rows=list(csv.reader(io.StringIO(b.decode("utf-8-sig"))))
    i=next(i for i,r in enumerate(rows) if r and r[0]=="Year")
    header=rows[i];body=[r for r in rows[i+1:] if any(v.strip() for v in r)]
    if len(body)!=3452 or len(set(header))!=len(header) or any(len(r)!=len(header) for r in body):raise ValueError("source row/schema drift")
    if not {"Year","Month","Zone","Area","Comments",*FIELDS.values()}<=set(header):raise ValueError("required source fields missing")
    return [dict(zip(header,map(str.strip,r))) for r in body],{"csv_sha256":PIN,"member":names[0],"archive_sha256":sha(path.read_bytes()),"rows":len(body)}
def integer(s):
    try:
        v=float(s.replace(",",""))
        return int(v) if np.isfinite(v) and v>=0 and v.is_integer() else None
    except (ValueError,TypeError,AttributeError):return None
def area_tokens(a):
    a=a.strip().casefold()
    if re.fullmatch(r"\d+\s*(?:[-–]\s*\d+)?(?:\s*,\s*\d+\s*(?:[-–]\s*\d+)?)*",a):
        nums=[]
        for part in a.split(","):
            n=[int(x) for x in re.split("[-–]",part)]
            if len(n)==2 and not 0<=n[1]-n[0]<=150:raise ValueError("invalid numeric range")
            nums.extend(range(n[0],n[-1]+1))
        if len(nums)!=len(set(nums)):raise ValueError("within-label overlap")
        return ["num:"+str(n) for n in nums],False
    if re.search(r"\d|\b(total|subtotal|all|whole|unknown|near|not split|unspecified)\b",a) or not a:raise ValueError("ambiguous area label")
    return ["name:"+re.sub(r"\s+"," ",a)],True
def audit_year(rows,y):
    reasons=[];named=[];areas=defaultdict(list);labels=defaultdict(set);zdata={sp:defaultdict(list) for sp in FIELDS}
    if not rows:return {"year":y,"eligible":False,"reasons":["no source rows"],"named_areas":[]},{}
    months={r["Month"].upper() for r in rows if r["Month"]}
    if months!={"FEB"}:reasons.append("month not confirmed February only")
    for i,r in enumerate(rows):
        z=r["Zone"];a=r["Area"]
        if z not in ZONES:reasons.append("unassigned zone");continue
        if re.search(r"\b(not counted|not surveyed|not split|incomplete|not visited|no count|missing data)\b",r["Comments"],re.I):reasons.append("explicit incomplete survey "+z+":"+a)
        try:tok,isname=area_tokens(a)
        except ValueError as e:reasons.append(str(e)+" "+z+":"+a);continue
        if labels[z].intersection(tok):reasons.append("overlapping area identifiers "+z+":"+a)
        labels[z].update(tok);areas[z].append(a)
        if isname:named.append(z+":"+a)
        for sp,col in FIELDS.items():zdata[sp][z].append(integer(r[col]))
    if set(areas)!=set(ZONES):reasons.append("not all six zones")
    counts={}
    for sp,zz in zdata.items():
        if set(zz)==set(ZONES) and all(all(v is not None for v in zz[z]) for z in ZONES):
            counts[sp]=[sum(zz[z]) for z in ZONES]
    if "fur" not in counts:reasons.append("missing/invalid fur count")
    elif sum(counts["fur"])<2:reasons.append("total <2")
    return {"year":y,"eligible":not reasons,"reasons":sorted(set(reasons)),"rows":len(rows),"months":sorted(months),"area_labels":dict(areas),"named_areas":sorted(set(named)),"species_count_available":sorted(counts)},counts
def metric(count):
    x=np.asarray(count,dtype=float);n=x.sum()
    if n<2:raise ValueError("total <2")
    p=x/n
    return float(np.sum(x*(x-1))/(n*(n-1))),float(1/(p@p))
def effects(a,b):
    a=np.array(a,float);b=np.array(b,float)
    ha=np.array([metric(x)[0] for x in a]);hb=np.array([metric(x)[0] for x in b])
    pa=a/a.sum(1)[:,None];pb=b/b.sum(1)[:,None]
    ma=a.mean(0);mb=b.mean(0);ref=pa.mean(0)*mb.sum()
    def safe_ratio(x,y):return float(x/y) if y>0 else None
    return {"delta_unbiased_concentration":float(hb.mean()-ha.mean()),
            "mean_concentration_reference":float(ha.mean()),"mean_concentration_late":float(hb.mean()),
            "mean_effective_zones_reference":float(np.mean([metric(x)[1] for x in a])),
            "mean_effective_zones_late":float(np.mean([metric(x)[1] for x in b])),
            "mean_total_reference":float(ma.sum()),"mean_total_late":float(mb.sum()),
            "total_ratio_late_reference":safe_ratio(mb.sum(),ma.sum()),
            "zones":[{"zone":z,"mean_count_reference":float(ma[i]),"mean_count_late":float(mb[i]),
                      "count_ratio":safe_ratio(mb[i],ma[i]),
                      "mean_share_reference":float(pa[:,i].mean()),"mean_share_late":float(pb[:,i].mean()),
                      "delta_share_pp":float(100*(pb[:,i].mean()-pa[:,i].mean())),
                      "expected_late_under_fixed_reference_share":float(ref[i]),"late_minus_expected":float(mb[i]-ref[i])}
                     for i,z in enumerate(ZONES)],
            "nondecreasing_absolute_count_zones":[z for i,z in enumerate(ZONES) if mb[i]>=ma[i]]}
def summarize(eligible,counts,sp,strict=False):
    early=[y for y in EARLY if y in eligible and (not strict or not eligible[y]["named_areas"])]
    late=[y for y in LATE if y in eligible and (not strict or not eligible[y]["named_areas"])]
    out={"early_years":early,"late_years":late,"named_area_excluded":strict}
    if min(len(early),len(late))<4:return dict(out,status="BLOCKED_MINIMUM_YEARS")
    if any(sp not in counts[y] or sum(counts[y][sp])<2 for y in early+late):return dict(out,status="BLOCKED_SPECIES_SUPPORT")
    a=np.array([counts[y][sp] for y in early]);b=np.array([counts[y][sp] for y in late])
    res=effects(a,b)
    loo=[effects(np.delete(a,i,axis=0),b) for i in range(len(a))]+[effects(a,np.delete(b,i,axis=0)) for i in range(len(b))]
    res["leave_one_year_out_delta_concentration_range"]=[min(t["delta_unbiased_concentration"] for t in loo),max(t["delta_unbiased_concentration"] for t in loo)]
    for i,r in enumerate(res["zones"]):
        vals=[t["zones"][i]["count_ratio"] for t in loo if t["zones"][i]["count_ratio"] is not None]
        r["leave_one_year_out_count_ratio_range"]=[min(vals),max(vals)] if len(vals)==len(loo) else None
    return dict(out,status="DESCRIPTIVE_ONLY",**res)
def selftest():
    rows=[dict(Year="2010",Month="FEB",Zone=z,Area="1,2-3",Comments="",**{c:"10" for c in FIELDS.values()}) for z in ZONES]
    a,x=audit_year(rows,2010);assert a["eligible"] and x["fur"]==[10]*6
    bad=rows+[dict(rows[0],Area="2")]
    assert not audit_year(bad,2010)[0]["eligible"]
    assert not audit_year([dict(r,Number_of_fur_seals="") if r["Zone"]=="1" else r for r in rows],2010)[0]["eligible"]
    assert not audit_year([dict(r,Comments="Not counted") if r["Zone"]=="1" else r for r in rows],2010)[0]["eligible"]
    assert abs(metric([2,2,0,0,0,0])[0]-1/3)<1e-12
    a=[[100,100,100,100,100,100]]*4;b=[[100,0,0,0,0,0]]*4
    r=effects(a,b);assert r["delta_unbiased_concentration"]>0 and r["nondecreasing_absolute_count_zones"]==["1"]
    print("synthetic source and effect tests passed")
def main():
    p=argparse.ArgumentParser();p.add_argument("--selftest",action="store_true");p.add_argument("--source",type=Path);p.add_argument("--out",type=Path);a=p.parse_args()
    if a.selftest:selftest();return
    a.out.mkdir(parents=True,exist_ok=True)
    rows,source=read(a.source);group=defaultdict(list)
    for r in rows:group[int(r["Year"])].append(r)
    audits={};counts={};elig={}
    for y in EARLY+LATE:
        receipt,c=audit_year(group[y],y);audits[y]=receipt;counts[y]=c
        if receipt["eligible"]:elig[y]=receipt
    result={"status":"SOURCE_AUDITED","source":source,"audit":audits,"species":{sp:summarize(elig,counts,sp) for sp in FIELDS},"numeric_only_fur_sensitivity":summarize(elig,counts,"fur",True),"causal_or_vegetation_inference":False,"independent_islands":1}
    with (a.out/"annual_zone_counts.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["year","species","zone","count"])
        for y in sorted(elig):
            for sp,values in counts[y].items():
                for z,v in zip(ZONES,values):w.writerow([y,sp,z,v])
    (a.out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"source":source,"eligible":sorted(elig),"excluded":{y:v["reasons"] for y,v in audits.items() if not v["eligible"]},"species":result["species"],"numeric_only_fur_sensitivity":result["numeric_only_fur_sensitivity"]}))
if __name__=="__main__":main()
