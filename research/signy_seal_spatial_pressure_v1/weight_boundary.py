"""Exact fixed-panel break-even calculation; weights are scenarios, not estimates."""
import csv, hashlib, io, json, sys, zipfile
from fractions import Fraction as F
from pathlib import Path
from statistics import mean
PIN='9e0a8b1684221c5874d8e23d7307d051d6fecddf0c8dfc91f0207fc1c162f781'
EARLY=(2010,2012,2013,2014)
LATE=(2016,2017,2018,2019,2020,2022,2023,2024)
SPECIES=('fur','elephant','weddell')
ZONES=tuple(range(1,7))
SCENARIOS=((1,1),(5,5),(10,5),(20,5),(30,5),(50,10),(100,10))
def calc(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=PIN: raise ValueError('artifact digest mismatch')
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None: raise ValueError('CRC failed')
        rows=list(csv.DictReader(io.StringIO(z.read('annual_zone_counts.csv').decode('utf-8'))))
    x={}
    for row in rows:
        k=(int(row['year']),int(row['zone']),row['species']); v=int(row['count'])
        if k in x or v<0: raise ValueError('duplicate or invalid count')
        x[k]=v
    if set(x)!={(y,z,s) for y in EARLY+LATE for z in ZONES for s in SPECIES}: raise ValueError('panel coverage mismatch')
    def means(years,zones):
        return tuple(F(sum(x[y,z,s] for y in years for z in zones),len(years)) for s in SPECIES)
    def values(e,l,zones):
        a,b=means(e,zones),means(l,zones)
        d=tuple(v-u for u,v in zip(a,b))
        if d[0]>=0: raise ValueError('fur decline required')
        return a,b,d
    def boundary(d,w):
        return (-d[0]-d[2]*w)/d[1] if d[1]>0 else None
    def eq_boundary(d):
        return -d[0]/(d[1]+d[2]) if d[1]+d[2]>0 else None
    def max_box_boundary(d):
        positive=sum(max(F(0),v) for v in d[1:])
        return -d[0]/positive if positive>0 else None
    def change(a,b,w):
        aa=sum(v*q for v,q in zip(a,w)); bb=sum(v*q for v,q in zip(b,w))
        return 100*(bb-aa)/aa
    def f(v):return float(v) if v is not None else None
    def rng(vals):
        return [f(min(vals)),f(max(vals))] if vals and all(v is not None for v in vals) else None
    loo=[(tuple(y for y in EARLY if y!=k),LATE) for k in EARLY]+[(EARLY,tuple(y for y in LATE if y!=k)) for k in LATE]
    out={}
    for name,zones in [('island',ZONES)]+[(str(z),(z,)) for z in ZONES]:
        a,b,d=values(EARLY,LATE,zones); variants=[values(e,l,zones) for e,l in loo]
        r={'early_means':list(map(f,a)),'late_means':list(map(f,b)),'delta_counts':list(map(f,d)),
           'equal_other_weight_break_even':f(eq_boundary(d)),
           'independent_nonnegative_weight_box_break_even':f(max_box_boundary(d)),
           'independent_nonnegative_weight_box_min_across_full_and_loo':f(min(v for v in [max_box_boundary(d)]+[max_box_boundary(t[2]) for t in variants] if v is not None)) if any(v is not None for v in [max_box_boundary(d)]+[max_box_boundary(t[2]) for t in variants]) else None,
           'equal_other_weight_loo_range':rng([eq_boundary(v[2]) for v in variants]),
           'equal_other_weight_no_finite_positive_break_even_loo_n':sum(eq_boundary(v[2]) is None for v in variants),
           'elephant_weight_break_even_at_weddell_5':f(boundary(d,5)),
           'elephant_weight_break_even_at_weddell_5_loo_range':rng([boundary(v[2],5) for v in variants]),
           'scenarios':[]}
        for we,ww in SCENARIOS:
            w=(1,we,ww); c=change(a,b,w); cs=[change(u,v,w) for u,v,_ in variants]
            r['scenarios'].append({'elephant_weight':we,'weddell_weight':ww,'weighted_count_change_pct':f(c),'loo_range_pct':rng(cs)})
        out[name]=r
    # Check exact additive changes and threshold identity.
    for i in range(3):
        assert abs(sum(out[str(z)]['delta_counts'][i] for z in ZONES)-out['island']['delta_counts'][i])<1e-9
    a,b,d=values(EARLY,LATE,ZONES); t=eq_boundary(d)
    assert change(a,b,(1,t,t))==0
    return {'status':'CONDITIONAL_WEIGHT_BOUNDARY_NOT_ECOLOGICAL_EFFECT','source_artifact_sha256':PIN,'early':EARLY,'late':LATE,'n_rows':len(rows),'species_order':SPECIES,'assumptions':['fixed nonnegative weight per counted animal of each species across periods and zones','fur weight normalized to 1','not calibrated animal-days, body mass, trampling or nutrient flux','same single-island panel, no independent replication'],'results':out}
if __name__=='__main__':
    result=calc(sys.argv[1]); Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
