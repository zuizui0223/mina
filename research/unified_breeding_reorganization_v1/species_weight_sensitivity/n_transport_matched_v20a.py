"""V20a; use the published 10-min gridded archive, not raw instrument data."""
import csv, collections, datetime as dt, hashlib, json, math, pathlib, statistics as st, sys, zipfile

SHA='f76c2ab1f5a99dc0ba875cb4968f2a50f124e948db17e1e6dafeb18d328e52e5'
p=pathlib.Path(sys.argv[1])
assert hashlib.sha256(p.read_bytes()).hexdigest()==SHA
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None
    source=z.read('dataset/data_10min_gridded.csv')
rows=list(csv.DictReader(source.decode('utf-8-sig').splitlines()))
assert len(rows)==9792
def f(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (ValueError,TypeError): return None
def date(r): return dt.datetime.strptime(r['time'],'%m/%d/%Y %H:%M')
times=[date(r) for r in rows]
assert len(set(times))==len(rows)
assert all(b-a==dt.timedelta(minutes=10) for a,b in zip(times,times[1:]))
assert times[0]==dt.datetime(2023,1,11) and times[-1]==dt.datetime(2023,3,19,23,50)
ys=[f(r['ammonia_mixing_ratio_ppb']) for r in rows]
observed=[v for v in ys if v is not None]
audit={'rows':len(rows),'finite_nh3':len(observed),'missing_nh3':len(rows)-len(observed),'below_0_0105':sum(v<.0105-1e-9 for v in observed),'zero':sum(v==0 for v in observed),'negative':sum(v<0 for v in observed)}
assert audit['finite_nh3']==4523
if audit['below_0_0105']:
    print(json.dumps({'status':'STOP_SOURCE_LOD_MISMATCH','audit':audit},indent=2))
    sys.exit(0)
cells=['pre_south','pre_comparison','post_south','post_comparison']
groups=collections.defaultdict(list)
support={c:{'met_rows':0,'available_nh3':0,'dates_met':set(),'dates_nh3':set()} for c in cells}
exclusion=collections.Counter()
for t,r,y in zip(times,rows,ys):
    d=t.date()
    if dt.date(2023,1,26)<=d<=dt.date(2023,2,20): phase='pre'
    elif dt.date(2023,2,22)<=d<=dt.date(2023,3,19): phase='post'
    else: exclusion['outside_fixed_windows']+=1;continue
    if r['pollution_flag']!='FALSE': exclusion['pollution']+=1;continue
    wd,ws,k=(f(r[a]) for a in ('wind_direction','wind_speed','ambient_temperature'))
    if any(v is None for v in (wd,ws,k)):exclusion['missing_meteorology']+=1;continue
    if not 0<=wd<360 or ws<1:exclusion['invalid_direction_or_calm']+=1;continue
    if 170<=wd<230:sector='south'
    elif 90<=wd<160 or 240<=wd<300:sector='comparison'
    else:exclusion['outside_fixed_sectors']+=1;continue
    c=phase+'_'+sector; key=(math.floor((k-273.15)/2),0 if ws<5 else 1 if ws<10 else 2 if ws<15 else 3)
    s=support[c];s['met_rows']+=1;s['dates_met'].add(d)
    if y is None:continue
    s['available_nh3']+=1;s['dates_nh3'].add(d)
    groups[(key,c,d)].append(y)
# Freeze support using only group keys and lengths before summarizing concentration.
qual={k:v for k,v in groups.items() if len(v)>=2}
allstrata=sorted({k[0] for k in qual})
def common(cs):
    strata=[s for s in allstrata if all(sum(k[0]==s and k[1]==c for k in qual)>=3 for c in cs)]
    dates={c:sorted({k[2] for k in qual if k[0] in strata and k[1]==c}) for c in cs}
    return strata,dates,len(strata)>=3 and all(len(v)>=5 for v in dates.values())
designs={'four_cell':cells,'south_only':['pre_south','post_south']}
gates={name:common(cs) for name,cs in designs.items()}
med={k:st.median(v) for k,v in qual.items()}
def estimate(cs,strata,drop=None):
    vals={}
    for c in cs:
        means=[]
        for s in strata:
            x=[v for (ss,cc,d),v in med.items() if ss==s and cc==c and d!=drop]
            if len(x)<2:return None
            means.append(st.mean(x))
        vals[c]=st.mean(means)
    if len(cs)==4:
        a=vals['pre_south']-vals['pre_comparison']; b=vals['post_south']-vals['post_comparison']
        return {'cell_means_ppb':vals,'pre_excess_ppb':a,'post_excess_ppb':b,'change_excess_ppb':b-a,'retained_fraction':b/a if a>0 else None}
    a=vals['pre_south'];b=vals['post_south']
    return {'cell_means_ppb':vals,'change_ppb':b-a,'post_pre_ratio':b/a if a>0 else None}
def evaluate(name,cs):
    strata,dates,passed=gates[name]
    out={'pass':passed,'common_strata':[list(x) for x in strata],'n_strata':len(strata),'distinct_dates_by_cell':{c:len(d) for c,d in dates.items()},'stratum_date_counts':[{'stratum':list(s),**{c:sum(k[0]==s and k[1]==c for k in qual) for c in cs}} for s in strata]}
    if not passed:return out
    e=estimate(cs,strata);assert e is not None;out['estimate']=e
    union=sorted(set().union(*[set(d) for d in dates.values()]))
    loo=[estimate(cs,strata,drop) for drop in union]
    assert all(x is not None for x in loo)
    out['leave_date_out_n']=len(loo)
    out['leave_date_out_ranges']={k:[min(x[k] for x in loo if x[k] is not None),max(x[k] for x in loo if x[k] is not None)] for k,v in e.items() if isinstance(v,(float,int)) and any(x[k] is not None for x in loo)}
    return out
# Independent arithmetic checks via per-date equal weights, per-stratum equal weights.
for name,cs in designs.items():
    strata,dates,passed=gates[name]
    if not passed:continue
    e=estimate(cs,strata)
    for c in cs:
        z=0.
        for s in strata:
            vs=[st.median(v) for (ss,cc,d),v in qual.items() if ss==s and cc==c]
            z+=sum(v/(len(strata)*len(vs)) for v in vs)
        assert math.isclose(z,e['cell_means_ppb'][c],abs_tol=1e-12,rel_tol=1e-12)
for s in support.values():
    s['dates_met']=len(s['dates_met']);s['dates_nh3']=len(s['dates_nh3'])
    s['availability_fraction']=s['available_nh3']/s['met_rows'] if s['met_rows'] else None
result={'status':'EXECUTED_CONDITIONAL_ONLY','archive_sha256':SHA,'audit':audit,'exclusions':dict(exclusion),'support':support,'eligible_met_rows':sum(s['met_rows'] for s in support.values()),'qualifying_date_sector_strata':len(qual),'results':{n:evaluate(n,cs) for n,cs in designs.items()},'limitations':'above-LOD reported NH3 only; missing includes censoring and possible downtime; one station, one season, observational, not emission or deposition'}
assert result['eligible_met_rows']+sum(exclusion.values())==len(rows)
output=json.dumps(result,indent=2,allow_nan=False)
pathlib.Path(sys.argv[2]).write_text(output+'\n')
print(output)
