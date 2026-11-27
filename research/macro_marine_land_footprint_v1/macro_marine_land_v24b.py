"""V24b: fix species-column collision, replay exact verified joined data; no new source or estimand."""
import csv,hashlib,io,json,math,pathlib,statistics,sys,zipfile
from collections import Counter,defaultdict
import numpy as np
SP=('ADPE','CHPE','GEPE');NZ='manaakiwhenua2021aerial'
out=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
PINS={13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',13671496095:'58c9bacc331b8aefb35027ee248a09076cf96e4f71f681543444da1850347bd8',13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5',14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',15102504516:'80c8ec2f64b54ed12138ce52c362cad750428a60cb675e35d221c092eb32d0fc',15168609505:'f2e81ac26759d678815c8f550f15fe9c63447337a3abb7478feb0ec7b133572c'}
def dump(name,obj): (out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
b=pathlib.Path(sys.argv[1]).read_bytes();assert hashlib.sha256(b).hexdigest()==PINS[15168609505]
with zipfile.ZipFile(io.BytesIO(b)) as z:
    assert z.testzip() is None
    name=[x for x in z.namelist() if pathlib.PurePosixPath(x).name=='source_join.csv'];assert len(name)==1
    source=z.read(name[0])
    rows=list(csv.DictReader(io.StringIO(source.decode('utf-8-sig'))))
assert len(rows)==771 and len({(x['site'],x['species'],x['year']) for x in rows})==771
assert Counter(x['species'] for x in rows)=={'ADPE':414,'CHPE':152,'GEPE':205}
for r in rows:
    r['year']=int(r['year'])
    for k in ['distance_m','n0','n1','map_m2']+[v+str(t) for v in ('sic','sss','sst','p100') for t in (0,1)]:
        r[k]=float(r[k]) if r[k]!='' else None
    for k in ('wet0','wet1'):r[k]=r[k] or None
    assert r['n0']>=0 and r['n1']>=0 and r['map_m2']>=0 and r['distance_m']>=0
reject=Counter()
def groupkey(r):return (r['species'],r['region'],r['year'])
vars_by={'sic':('sic',),'hydro':('sic','sss','sst'),'joint':('sic','sss','sst','p100')}
cohorts={};support=[]
def info(v):
    return {'rows':len(v),'sites':len({r['site'] for r in v}),'regions':len({r['region'] for r in v}),'region_names':sorted({r['region'] for r in v}),'years':len({r['year'] for r in v}),'blocks':len({r['block'] for r in v}),'wet_cells':len({r['wet0'] for r in v if r['wet0'] is not None}),'species':dict(Counter(r['species'] for r in v))}
for dist in (1,1000,5000):
    for end in (2018,2020):
        for no_nz in (False,True):
            for name,vs in vars_by.items():
                vv=[r for r in rows if r['distance_m']<=dist and r['year']+1<=end and (not no_nz or r['citekey']!=NZ) and all(r[v+str(t)] is not None for v in vs for t in (0,1))]
                gg=defaultdict(list)
                for r in vv:gg[groupkey(r)].append(r)
                good={k:v for k,v in gg.items() if len(v)>=5 and sum(r['n0'] for r in v)>0 and sum(r['n1'] for r in v)>0}
                eligible=[r for v in good.values() for r in v]
                tag=(dist,end,no_nz,name);cohorts[tag]=good
                support.append({'dist_m':dist,'end_year':end,'no_nz':no_nz,'cohort':name,'available':info(vv),'eligible':info(eligible),'all_groups':len(gg),'groups_ge5':len(good),'eligible_groups_by_species':dict(Counter(k[0] for k in good))})
dump('support.json',{'pairs':771,'nominal_joined':len(rows),'rejected':dict(reject),'cohorts':support})
print('SUPPORT_V24='+json.dumps({'pairs':771,'nominal_joined':len(rows),'rejected':dict(reject),'primary':[x for x in support if x['dist_m']==1000 and x['end_year']==2018]}),flush=True)
def account(v,vs):
    n0=math.fsum(r['n0'] for r in v);n1=math.fsum(r['n1'] for r in v)
    p=np.array([r['n0']/n0 for r in v]);q=np.array([r['n1']/n1 for r in v])
    a=np.array([r['map_m2'] for r in v]);a0=float(p@a);a1=float(q@a)
    out={'N0':n0,'N1':n1,'TV':float(.5*np.abs(q-p).sum()),'map_A0':a0,'map_A1':a1,'map_delta':float((q-p)@a),'map_ratio':a1/a0 if a0>0 else None}
    assert math.isclose(out['map_delta'],a1-a0,abs_tol=1e-7)
    for s in vs:
        x=np.array([r[s+'0'] for r in v]);y=np.array([r[s+'1'] for r in v])
        total=float(q@y-p@x);local=float(((p+q)/2)@(y-x));alloc=float((q-p)@((x+y)/2));align=float((q-p)@(y-x))
        assert math.isclose(total,local+alloc,rel_tol=1e-10,abs_tol=1e-8)
        assert math.isclose(align,float(q@(y-x)-p@(y-x)),abs_tol=1e-8)
        out.update({s+'_total':total,s+'_local':local,s+'_allocation':alloc,s+'_alignment':align})
    return out
strata=[];summ=[];loo=[];fit=[]
def summarise(rr,metric):
    val=[r[metric] for r in rr if r.get(metric) is not None]
    regs=sorted({r['region'] for r in rr if r.get(metric) is not None})
    rm=[statistics.mean(r[metric] for r in rr if r['region']==reg and r.get(metric) is not None) for reg in regs]
    return {'n':len(val),'regions':len(regs),'positive':sum(x>1e-10 for x in val),'negative':sum(x< -1e-10 for x in val),'median':statistics.median(val) if val else None,'mean':statistics.mean(val) if val else None,'equal_region_mean':statistics.mean(rm) if rm else None}
def regression(v,vs):
    groups={groupkey(r) for r in v};z=info(v)
    if len(groups)<5 or z['sites']<20 or z['regions']<3 or z['blocks']<8:return {**z,'status':'SUPPORT_NO_FIT','groups':len(groups)}
    sites=sorted({(r['site'],r['species']) for r in v});gs=sorted(groups)
    ii={s:i for i,s in enumerate(sites)};jj={s:i for i,s in enumerate(gs)}
    D=np.zeros((len(v),len(sites)+len(gs)))
    for i,r in enumerate(v):D[i,ii[r['site'],r['species']]]=1;D[i,len(sites)+jj[groupkey(r)]]=1
    scale={'sic':10,'sss':1,'sst':1,'p100':10}
    X=np.array([[(r[s+'1']-r[s+'0'])/scale[s] for s in vs] for r in v]);y=np.array([math.log1p(r['n1'])-math.log1p(r['n0']) for r in v])
    both=np.column_stack((y,X));res=both-D@np.linalg.lstsq(D,both,rcond=None)[0]
    x=res[:,1:];yr=res[:,0];rank=np.linalg.matrix_rank(x,tol=1e-9);df=len(v)-np.linalg.matrix_rank(D)-len(vs)
    if rank!=len(vs) or df<=10:return {**z,'status':'RANK_OR_DF_NO_FIT','groups':len(groups),'residual_rank':int(rank),'residual_df':int(df)}
    beta=np.linalg.lstsq(x,yr,rcond=None)[0]
    return {**z,'status':'DESCRIPTIVE_FIT','groups':len(groups),'residual_df':int(df),'beta':dict(zip(vs,map(float,beta))),'within_R2':float(1-np.sum((yr-x@beta)**2)/np.sum(yr**2)) if np.sum(yr**2)>0 else None}
for (dist,end,no_nz,name),gg in cohorts.items():
    vs=vars_by[name];tag={'dist_m':dist,'end_year':end,'no_nz':no_nz,'cohort':name}
    rr=[]
    for k,v in sorted(gg.items()):
        r={**tag,**info(v),'species':k[0],'region':k[1],'year':k[2],**account(v,vs)}
        rr.append(r);strata.append(r)
    for s in SP:
        sr=[r for r in rr if r['species']==s]
        assert len(sr)==sum(k[0]==s for k in gg), 'species aggregation mismatch'
        for m in ['TV','map_delta','map_ratio']+[v+'_'+t for v in vs for t in ('total','local','allocation','alignment')]:
            summ.append({**tag,'species':s,'metric':m,**summarise(sr,m)})
            if dist==1000 and end==2018 and not no_nz:
                for reg in sorted({r['region'] for r in sr}):
                    loo.append({**tag,'species':s,'metric':m,'excluded_region':reg,**summarise([r for r in sr if r['region']!=reg],m)})
    if dist==1000 and end==2018:
        v=[r for g in gg.values() for r in g]
        fit.append({**tag,'excluded_region':None,**regression(v,vs)})
        for reg in sorted({r['region'] for r in v}):
            fit.append({**tag,'excluded_region':reg,**regression([r for r in v if r['region']!=reg],vs)})
# Union columns for varying nested cohorts.
def write_union(name,v):
    if not v:return
    fields=list(dict.fromkeys(k for r in v for k in r))
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(v)
write_union('strata.csv',strata);write_union('summary.csv',summ);write_union('loo.csv',loo)
res={'status':'EXECUTED_ANNUAL_COMMON_SUPPORT_ACCOUNTING','source_pins':PINS,'join':{'pairs':771,'nominal_joined':len(rows),'rejected':dict(reject)},'support':support,'summary':summ,'region_omissions':loo,'regression':fit}


# Independent summary and original count arithmetic check, on all nested groups.
checks=0;err=0.
for row in strata:
    tag=(row['dist_m'],row['end_year'],row['no_nz'],row['cohort'])
    k=(row['species'],row['region'],row['year'])
    v=cohorts[tag][k]
    n0=sum(r['n0'] for r in v);n1=sum(r['n1'] for r in v)
    def ck(a,b):
        global checks,err
        assert math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-7),(a,b)
        checks+=1;err=max(err,abs(a-b))
    ck(sum(r['n1']*r['map_m2'] for r in v)/n1-sum(r['n0']*r['map_m2'] for r in v)/n0,row['map_delta'])
    for f in vars_by[row['cohort']]:
        ck(sum(r['n1']*(r[f+'1']-r[f+'0']) for r in v)/n1-sum(r['n0']*(r[f+'1']-r[f+'0']) for r in v)/n0,row[f+'_alignment'])
for s in support:
    z=[x for x in summ if all(x[k]==s[k] for k in ('dist_m','end_year','no_nz','cohort')) and x['metric']=='TV']
    assert sum(x['n'] for x in z)==s['groups_ge5']
    checks+=1
res['QA']={'checks':checks,'max_abs_discrepancy':err,'source_join_sha256':hashlib.sha256(source).hexdigest(),'repair':'species field overwritten by info(v) in V24; V24b restores scalar species label and validates all group counts'}
dump('result.json',res)
print('V24B_QA='+json.dumps(res['QA']),flush=True)
print('V24_RESULT='+json.dumps({'join':res['join'],'primary_support':[x for x in support if x['dist_m']==1000 and x['end_year']==2018],'primary_summary':[x for x in summ if x['dist_m']==1000 and x['end_year']==2018 and not x['no_nz'] and x['metric'] in ('map_delta','map_ratio','sic_alignment','sss_alignment','sst_alignment','p100_alignment','sic_allocation','sss_allocation','p100_allocation')],'regression':fit}),flush=True)
