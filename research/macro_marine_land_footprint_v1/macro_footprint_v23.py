"""V23 exact original v5 expansion; no causal or biological flux claims."""
import csv,hashlib,io,json,math,pathlib,statistics,sys,urllib.request,zipfile
from collections import Counter,defaultdict
import numpy as np
import shapefile
import shapely as sh
from shapely.geometry import Point,shape,Polygon
from shapely.strtree import STRtree
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
old=read((root/'research/climate-penguin/macro_panantarctic_v1/outputs/panantarctic_595_site_inventory.csv').read_bytes())
assert len(old)==595
oldmap={x['site_id']:x for x in old}
gd=Geod(ellps='WGS84');overlap=[]
for sid in sorted(domain&set(oldmap)):
    a,b=oldmap[sid],S[sid]
    _,_,d=gd.inv(float(a['longitude']),float(a['latitude']),float(b['longitude']),float(b['latitude']))
    overlap.append({'site_id':sid,'distance_m':d,'region_equal':a['source_region']==b['region']})
table('v22_v23_coordinate_overlap.csv',overlap)
groups={'all_known_v5':domain}
for yr in (2023,2025):
    pos={sp:{sid for (sid,s,y),x in valid.items() if s==sp and sid in domain and 2017<=y<=yr and x['n']>0} for sp in SP}
    groups[f'positive_2017_{yr}']=set.union(*pos.values())
    groups.update({f'positive_2017_{yr}_{sp}':v for sp,v in pos.items()})
def cohorts(strict,exclude_nz):
    by=defaultdict(list)
    for (sid,sp,y),x in valid.items():
        if sid not in domain or not (1991<=y<=2000 or 2011<=y<=2020) or not known(x['vantage']) or (strict and not known(x['citekey'])) or (exclude_nz and x['citekey']==NZ):continue
        key=(sid,sp,x['citekey'] if strict else '',x['vantage'])
        by[key].append(x)
    candidates=defaultdict(list)
    for (sid,sp,cite,vantage),rows in by.items():
        a=sorted([x for x in rows if x['year']<=2000],key=lambda x:x['year']);b=sorted([x for x in rows if x['year']>=2011],key=lambda x:x['year'])
        if len(a)<2 or len(b)<2:continue
        candidates[sid,sp].append((a,b,cite,vantage))
    result=[]
    for (sid,sp),lst in sorted(candidates.items()):
        a,b,cite,vantage=sorted(lst,key=lambda z:(-len(z[0])-len(z[1]),z[2],z[3]))[0]
        result.append({'site_id':sid,'species':sp,'region':S[sid]['region'],'citekey':cite,'vantage':vantage,'early':statistics.median(x['n'] for x in a),'late':statistics.median(x['n'] for x in b),'early_years':';'.join(str(x['year']) for x in a),'late_years':';'.join(str(x['year']) for x in b),'early_ids':';'.join(x['id'] for x in a),'late_ids':';'.join(x['id'] for x in b),'contains_nz':any(x['citekey']==NZ for x in a+b)})
    return result
coh={f'{k}{suffix}':cohorts(k=='strict',bool(suffix)) for k in ('strict','vantage') for suffix in ('','_no_nz')}
oldpairs=read((root/'research/climate-penguin/macro_panantarctic_v1/allocation_20261115/original_strict_paired_end_50_source_site_species.csv').read_bytes());assert len(oldpairs)==50
oldp={(x['site_id'],x['species']):x for x in oldpairs}
for k,v in coh.items():
    table('cohort_'+k+'.csv',v)
support={'site_count_729':len(S),'observation_count':len(obs),'valid_focal_site_species_year':len(valid),'duplicate_groups':len(dup),'presence_flags':dict(flags),'zero_by_presence_flag':dict(zero_flags),'domain_known_sites':len(domain),'old_site_overlap':len(overlap),'old_coord_within_1m':sum(x['distance_m']<=1 for x in overlap),'old_region_equal':sum(x['region_equal'] for x in overlap),'static_groups':{k:len(v) for k,v in groups.items()},'cohorts':{k:{'n':len(v),'species':dict(Counter(x['species'] for x in v)),'regions':len({x['region'] for x in v}),'old_keys':sum((x['site_id'],x['species']) in oldp for x in v),'old_both_medians_equal':sum((x['site_id'],x['species']) in oldp and x['early']==float(oldp[x['site_id'],x['species']]['site_median_observed_nests_early']) and x['late']==float(oldp[x['site_id'],x['species']]['site_median_observed_nests_late']) for x in v)} for k,v in coh.items()},'strict_prior_annual_pairs':len(pairs)}
dump('support.json',support);print('SUPPORT='+json.dumps(support),flush=True)
b=get('https://figshare.com/ndownloader/files/43483098','7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236',15000000)
assert len(b)==5414267
z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
stems=[x[:-4] for x in z.namelist() if x.endswith('.shp')];assert len(stems)==1
st=stems[0];assert CRS.from_wkt(z.read(st+'.prj').decode(errors='replace')).equals(CRS.from_epsg(3031))
rd=shapefile.Reader(shp=io.BytesIO(z.read(st+'.shp')),shx=io.BytesIO(z.read(st+'.shx')),dbf=io.BytesIO(z.read(st+'.dbf')))
geoms=defaultdict(list);clcounts=Counter()
for sr in rd.iterShapeRecords():
    cl=str(sr.record.as_dict()['Vegetation']);clcounts[cl]+=1
    if cl in ('Vegetation','Lichen'):
        g=shape(sr.shape.__geo_interface__)
        assert g.is_valid and not g.is_empty and g.geom_type in ('Polygon','MultiPolygon')
        geoms[cl].append(g)
assert clcounts=={'Vegetation':58740,'Lichen':24876,'Snow Algae':3775}
def union(gg):return sh.disjoint_subset_union_all(np.asarray(gg,dtype=object)) if len(gg) else Polygon()
def polygons(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for x in g.geoms for p in polygons(x)]
mapped={k:union(v) for k,v in geoms.items()};mapped['Union']=union(list(mapped.values()))
maparea={k:float(v.area) for k,v in mapped.items()};assert all(abs(maparea[k]-v)<1e-4 for k,v in {'Vegetation':34513500,'Lichen':8640400,'Union':43153800}.items())
parts={k:np.asarray(polygons(g),dtype=object) for k,g in mapped.items()};trees={k:STRtree(v) for k,v in parts.items()}
proj=Transformer.from_crs(4326,3031,always_xy=True)
pts={sid:Point(*proj.transform(float(S[sid]['longitude']),float(S[sid]['latitude']))) for sid in sorted(domain)}
areas={};cover=[];arows=[]
for rad in RADII:
    clips={}
    for sid,p in pts.items():
        buf=p.buffer(rad,quad_segs=32);clips[sid]={}
        for cl,t in trees.items():
            ii=t.query(buf,predicate='intersects');g=union(sh.intersection(parts[cl][ii],buf));clips[sid][cl]=g
            areas[sid,rad,cl]=float(g.area);assert g.area<=buf.area+1e-4
            if rad!=250:assert areas[sid,rad,cl]>=areas[sid,RADII[RADII.index(rad)-1],cl]-1e-4
        arows.append({'site_id':sid,'region':S[sid]['region'],'radius_m':rad,**{cl+'_m2':areas[sid,rad,cl] for cl in mapped}})
    for name,ss in groups.items():
        for cl in mapped:
            a=float(union([clips[sid][cl] for sid in sorted(ss)]).area);assert 0<=a<=maparea[cl]+1e-4
            cover.append({'group':name,'radius_m':rad,'class':cl,'sites':len(ss),'area_m2':a,'fraction':a/maparea[cl]})
    print('GEOGRAPHY_RADIUS_DONE='+str(rad),flush=True)
# Compare archived V22 1km map areas where original coordinate shift <=1m; use exact coordinates separately.
oldarea_files=list(pathlib.Path(sys.argv[3]).rglob('site_buffer_area.csv')) if len(sys.argv)>3 else []
oldarea={x['site_id']:float(x['Union_m2']) for x in read(oldarea_files[0].read_bytes()) if int(x['radius_m'])==1000} if len(oldarea_files)==1 else {}
geoQA=[]
for x in overlap:
    if x['site_id'] in oldarea and x['distance_m']<=1:
        sid=x['site_id'];diff=areas[sid,1000,'Union']-oldarea[sid]
        if x['distance_m']<1e-5:assert abs(diff)<1e-4,(sid,diff)
        geoQA.append({'site_id':sid,'coord_distance_m':x['distance_m'],'old_area':oldarea[sid],'new_area':areas[sid,1000,'Union'],'delta_m2':diff})
def account(rows,rad,cl):
    n0=math.fsum(x['early'] for x in rows);n1=math.fsum(x['late'] for x in rows)
    if min(n0,n1)<=0:return None
    i0=math.fsum(x['early']*areas[x['site_id'],rad,cl] for x in rows);i1=math.fsum(x['late']*areas[x['site_id'],rad,cl] for x in rows)
    a0=i0/n0;a1=i1/n1;ref=i0*n1/n0
    assert math.isclose(i1-ref,n1*(a1-a0),rel_tol=1e-9,abs_tol=1e-4)
    return {'sites':len(rows),'regions':len({x['region'] for x in rows}),'N0':n0,'N1':n1,'A0':a0,'A1':a1,'delta_A':a1-a0,'ratio':a1/a0 if a0>0 else None,'I_ratio':i1/i0 if i0>0 else None}
dynamic=[];omissions=[]
for name,rows in coh.items():
    for sp in SP:
        v=[x for x in rows if x['species']==sp]
        for rad in RADII:
            for cl in mapped:
                a=account(v,rad,cl)
                if a is not None:dynamic.append({'cohort':name,'species':sp,'radius_m':rad,'class':cl,**a})
        for region in sorted({x['region'] for x in v}):
            a=account([x for x in v if x['region']!=region],1000,'Union')
            if a is not None:omissions.append({'cohort':name,'species':sp,'excluded_region':region,**a})
annual=[];annual_support={}
for ex in (False,True):
    ag=defaultdict(list)
    for sid,sp,y,a,b in pairs:
        if sid not in domain or not known(a['citekey']) or not known(a['vantage']) or (ex and a['citekey']==NZ):continue
        ag[sp,S[sid]['region'],y].append({'site_id':sid,'region':S[sid]['region'],'early':a['n'],'late':b['n']})
    tag='no_nz' if ex else 'all'
    annual_support[tag]={'eligible_pairs':sum(map(len,ag.values())),'strata_ge5':sum(len(v)>=5 for v in ag.values())}
    for (sp,reg,y),rows in sorted(ag.items()):
        if len(rows)<5:continue
        for rad in RADII:
            for cl in mapped:
                a=account(rows,rad,cl)
                if a is not None:annual.append({'cohort':tag,'species':sp,'region':reg,'start':y,'radius_m':rad,'class':cl,**a})
def summarize(v):
    ratios=[x['ratio'] for x in v if x['ratio'] is not None]
    regs=sorted({x['region'] for x in v})
    means=[statistics.mean(x['delta_A'] for x in v if x['region']==r) for r in regs]
    return {'strata':len(v),'regions':len(regs),'region_names':regs,'years':len({x['start'] for x in v}),'positive_delta':sum(x['delta_A']>0 for x in v),'negative_delta':sum(x['delta_A']<0 for x in v),'zero_delta':sum(x['delta_A']==0 for x in v),'defined_ratio':len(ratios),'median_ratio':statistics.median(ratios) if ratios else None,'mean_delta_m2':statistics.mean(x['delta_A'] for x in v) if v else None,'equal_region_mean_delta_m2':statistics.mean(means) if means else None}
summ=[];annual_loo=[]
for tag in ('all','no_nz'):
    for sp in SP:
        for rad in RADII:
            for cl in mapped:
                v=[x for x in annual if x['cohort']==tag and x['species']==sp and x['radius_m']==rad and x['class']==cl]
                summ.append({'cohort':tag,'species':sp,'radius_m':rad,'class':cl,**summarize(v)})
                if rad==1000 and cl=='Union':
                    for reg in sorted({x['region'] for x in v}):
                        annual_loo.append({'cohort':tag,'species':sp,'excluded_region':reg,**summarize([x for x in v if x['region']!=reg])})
for n,r in [('site_buffer_area.csv',arows),('static_coverage.csv',cover),('dynamic.csv',dynamic),('region_omissions.csv',omissions),('annual_strata.csv',annual),('annual_summary.csv',summ),('annual_loo.csv',annual_loo),('old_geometry_qa.csv',geoQA)]:table(n,r)
result={'status':'EXECUTED_V5_FIXED_MAP_REWEIGHTING','support':support,'map_area_m2':maparea,'static_coverage':cover,'dynamic':dynamic,'omissions':omissions,'annual_support':annual_support,'annual_summary':summ,'annual_loo':annual_loo,'old_geometry_QA':{'n':len(geoQA),'exact_coordinate_n':sum(x['coord_distance_m']<1e-5 for x in geoQA),'max_abs_exact_coordinate_diff':max((abs(x['delta_m2']) for x in geoQA if x['coord_distance_m']<1e-5),default=None)}}
dump('result.json',result)
print('V23_RESULT='+json.dumps({'support':support,'static_union':[x for x in cover if x['class']=='Union' and x['radius_m']==1000],'dynamic_union':[x for x in dynamic if x['class']=='Union'],'omissions':omissions,'annual_support':annual_support,'annual_primary':[x for x in summ if x['radius_m']==1000 and x['class']=='Union'],'annual_loo':annual_loo,'old_geometry_QA':result['old_geometry_QA']}),flush=True)
