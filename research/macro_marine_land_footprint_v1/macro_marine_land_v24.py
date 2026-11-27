"""V24 original v5 same-source adjacent pairs and common marine-land allocation."""
import csv,hashlib,io,json,math,pathlib,statistics,sys,urllib.request,zipfile
from collections import Counter,defaultdict
import numpy as np
from pyproj import CRS,Transformer,Geod

root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
SP=('ADPE','CHPE','GEPE');RADII=(250,1000,5000)
BASE='https://www.penguinmap.com/api/v1/'
SOURCES={'release':('release/?format=json','8f676f6498b1bc79708a67fb05d4ac8ee73249444e85402af87f6a3c64280a65'),'sites':('sites/?format=csv','36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34'),'p1':('observations/?format=csv&page_size=5000&page=1','cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075'),'p2':('observations/?format=csv&page_size=5000&page=2','c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3')}
NZ='manaakiwhenua2021aerial'
def dump(name,obj): (out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def read(raw):
    d=csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline=''))
    assert d.fieldnames and len(d.fieldnames)==len(set(d.fieldnames))
    r=list(d);assert all(None not in x for x in r)
    return r
def table(name,rows):
    if not rows:return
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def get(url,pin,maxbytes=20000000):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mina-source-audit/1.0'}),timeout=70) as f:
        b=f.read(maxbytes+1)
    assert 0<len(b)<=maxbytes and hashlib.sha256(b).hexdigest()==pin,(url,len(b),hashlib.sha256(b).hexdigest())
    return b
raw={k:get(BASE+p,s) for k,(p,s) in SOURCES.items()}
release=json.loads(raw['release']);assert release['version']=='5.0' and release['release_date']=='2026-10-21' and release['license'].startswith('CC BY 4.0')
sites=read(raw['sites']);p1=read(raw['p1']);p2=read(raw['p2'])
assert len(sites)==729 and len(p1)==5000 and len(p2)==487 and int(p1[-1]['id'])+1==int(p2[0]['id'])
S={x['site_id']:x for x in sites};assert len(S)==729 and all(x['mapppd_version']=='5.0' and x['region'] and x['site_name'] for x in sites)
obs=p1+p2;assert len({x['id'] for x in obs})==5487
grp=defaultdict(list);flags=Counter();zero_flags=Counter()
def number(v):
    try:
        x=float(v.replace(',','').strip())
        return x if math.isfinite(x) and 0<=x<1e10 else None
    except (ValueError,AttributeError):return None
def known(x):return x.strip().casefold() not in ('','unknown','na','n/a','none','null','unspecified','-','not specified')
for x in obs:
    assert x['site_id'] in S and x['site_name']==S[x['site_id']]['site_name'] and x['mapppd_version']=='5.0'
    if x['species_id'] not in SP or x['type']!='nests':continue
    flags[x['presence']]+=1
    n=number(x['count'])
    if n==0:zero_flags[x['presence']]+=1
    try:y=int(x['season'])
    except ValueError:continue
    if str(y)!=x['season'] or not 1890<=y<=2026 or x['presence']!='1' or n is None:continue
    grp[(x['site_id'],x['species_id'],y)].append({**x,'year':y,'n':n})
valid={k:v[0] for k,v in grp.items() if len(v)==1}
dup={k:v for k,v in grp.items() if len(v)>1}
assert len(dup)==426 and sum(map(len,dup.values()))==1022,(len(dup),sum(map(len,dup.values())))
pairs=[]
for (sid,sp,y),a in valid.items():
    b=valid.get((sid,sp,y+1))
    if b and a['citekey'].strip() and a['citekey']==b['citekey'] and a['vantage'].strip() and a['vantage']==b['vantage']:
        pairs.append((sid,sp,y,a,b))
assert len(pairs)==771 and len({x[0] for x in pairs})==95 and len({S[x[0]]['region'] for x in pairs})==11 and Counter(x[1] for x in pairs)=={'ADPE':414,'CHPE':152,'GEPE':205}
pre=defaultdict(set)
for sid,sp,y,a,b in pairs:pre[sp,S[sid]['region'],y].add(sid)
assert sum(len(v)>=5 for v in pre.values())==54
domain={sid for sid,sp,y in valid if float(S[sid]['latitude'])<=-60}
assert all(-90<=float(S[s]['latitude'])<=-60 and -180<=float(S[s]['longitude'])<=180 for s in domain)

# Original archived source ZIPs, source bytes frozen in earlier audits.
PINS={13669533413:'add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a',
13671496095:'58c9bacc331b8aefb35027ee248a09076cf96e4f71f681543444da1850347bd8',
13829236358:'64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5',
14926710177:'b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8',
15102504516:'80c8ec2f64b54ed12138ce52c362cad750428a60cb675e35d221c092eb32d0fc'}
def member(i,name):
    b=(root/f'{i}.zip').read_bytes()
    assert hashlib.sha256(b).hexdigest()==PINS[i],(i,hashlib.sha256(b).hexdigest())
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        assert z.testzip() is None
        names=[x for x in z.namelist() if pathlib.PurePosixPath(x).name==name]
        assert len(names)==1,(i,name,names)
        return read(z.read(names[0]))
def index(rows,fields):
    d={tuple(x[k] for k in fields):x for x in rows};assert len(d)==len(rows)
    return d
aa=member(13669533413,'panantarctic_595_site_inventory.csv')
ice=member(13671496095,'original_595_site_months_120_source_QA.csv')
hydro=member(13829236358,'original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv')
poly=member(14926710177,'winter_595.csv')
land=member(15102504516,'site_buffer_area.csv')
assert (len(aa),len(ice),len(hydro),len(poly),len(land))==(595,71400,16464,21420,594*3)
atlas={x['site_id']:x for x in aa};assert len(atlas)==595
H=index(hydro,['site_id','year']);P=index(poly,['site_id','radius_km','season'])
V={x['site_id']:x for x in land if int(x['radius_m'])==1000};assert len(V)==594
def validate(r,lat,lon):
    a=atlas[r['site_id']]
    assert r['source_region']==a['source_region'] and abs(float(r[lat])-float(a['latitude']))<1e-6 and abs(float(r[lon])-float(a['longitude']))<1e-6
for x in hydro:validate(x,'latitude','longitude')
for x in poly:validate(x,'colony_lat','colony_lon')
for x in V.values():assert x['region']==S[x['site_id']]['region'] and float(x['Union_m2'])>=0
ig=defaultdict(list)
assert len(index(ice,['site_id','year','month']))==71400
for x in ice:
    assert x['source_region']==atlas[x['site_id']]['source_region']
    ig[x['site_id'],x['year']].append(x)
I={}
for k,v in ig.items():
    assert len(v)==4 and {int(x['month']) for x in v}=={8,9,10,11}
    if all(x['source_full_595_site_monthly_support']=='OK' and x['source_25km_buffer_mean_SIC_pct']!='' for x in v):
        z=[float(x['source_25km_buffer_mean_SIC_pct']) for x in v];assert all(0<=a<=100 for a in z)
        I[k]=statistics.mean(z)
assert len(ig)==595*30
geo=Geod(ellps='WGS84')
# Capture support before any response summaries.
rows=[];reject=Counter()
for sid,sp,y,a,b in pairs:
    if sid not in domain or not known(a['citekey']) or not known(a['vantage']):reject['domain_or_source']+=1;continue
    if sid not in atlas or sid not in V:reject['site_not_shared']+=1;continue
    v=S[sid];o=atlas[sid]
    if v['region']!=o['source_region']:reject['region_changed']+=1;continue
    _,_,d=geo.inv(float(v['longitude']),float(v['latitude']),float(o['longitude']),float(o['latitude']))
    assert math.isfinite(d)
    row={'site':sid,'species':sp,'region':v['region'],'block':o['polar_250km_fixed_grid_block'],'year':y,'distance_m':d,'citekey':a['citekey'],'vantage':a['vantage'],'n0':a['n'],'n1':b['n'],'map_m2':float(V[sid]['Union_m2'])}
    for t in (0,1):
        yy=str(y+t);k=(sid,yy);h=H.get(k);p=P.get((sid,'100',yy))
        row['sic'+str(t)]=I.get(k)
        if h and h['original_source_4_GLORYS_months']=='4' and h['original_source_4_OSISAF_months']=='4':
            row['sss'+str(t)]=float(h['mean_GLORYS_salinity'])
            row['sst'+str(t)]=float(h['mean_GLORYS_thetao_C'])
            row['wet'+str(t)]=str(h['GLORYS_cell_y'])+':'+str(h['GLORYS_cell_x'])
            if k in I:assert math.isclose(float(h['mean_source_SIC_pp']),I[k],rel_tol=1e-9,abs_tol=1e-6),(sid,yy,h['mean_source_SIC_pp'],I[k])
        else:
            row['sss'+str(t)]=None;row['sst'+str(t)]=None;row['wet'+str(t)]=None
        row['p100'+str(t)]=100*float(p['direct_DEEPAA_coastal_polynya_fraction']) if p and p['n_valid_months'] in ('5','5.0') and p['direct_DEEPAA_coastal_polynya_fraction']!='' else None
    assert all(x is None or math.isfinite(x) for x in [row[v+str(t)] for v in ('sic','sss','sst','p100') for t in (0,1)])
    assert all(row['p100'+str(t)] is None or 0<=row['p100'+str(t)]<=100 for t in (0,1))
    if row['wet0'] is not None and row['wet1'] is not None:assert row['wet0']==row['wet1']
    rows.append(row)
assert len(rows)+sum(reject.values())==771
table('source_join.csv',rows)
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
        r={**tag,'species':k[0],'region':k[1],'year':k[2],**info(v),**account(v,vs)}
        rr.append(r);strata.append(r)
    for s in SP:
        sr=[r for r in rr if r['species']==s]
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
dump('result.json',res)
print('V24_RESULT='+json.dumps({'join':res['join'],'primary_support':[x for x in support if x['dist_m']==1000 and x['end_year']==2018],'primary_summary':[x for x in summ if x['dist_m']==1000 and x['end_year']==2018 and not x['no_nz'] and x['metric'] in ('map_delta','map_ratio','sic_alignment','sss_alignment','sst_alignment','p100_alignment','sic_allocation','sss_allocation','p100_allocation')],'regression':fit}),flush=True)
