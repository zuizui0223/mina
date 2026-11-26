"""Pan-Antarctic V22: actual mapped terrestrial proximity, not nutrient flux."""
import csv, hashlib, io, json, math, pathlib, statistics, sys, urllib.request, zipfile
from collections import Counter, defaultdict
import numpy as np
import shapefile
import shapely as sh
from shapely.geometry import Point, shape, Polygon
from shapely.strtree import STRtree
from pyproj import CRS, Transformer

root=pathlib.Path(sys.argv[1])
out=pathlib.Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
macro=root/'research/climate-penguin/macro_panantarctic_v1'
SP=('ADPE','CHPE','GEPE'); RADII=(250,1000,5000)
def load(p,blob=None):
    raw=p.read_bytes()
    if blob: assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob, str(p)
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
def dump(name,obj):
    (out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def table(name,rows):
    assert rows
    with (out/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
site=load(macro/'outputs/panantarctic_595_site_inventory.csv')
obs=load(macro/'outputs/source_observed_2456.csv')
assert len(site)==595 and len(obs)==2456 and len({x['site_id'] for x in site})==595
assert len({x['source_region'] for x in site})==18
byid={r['site_id']:r for r in site}
roster=[r for r in site if float(r['latitude'])<=-60]
ids=[r['site_id'] for r in roster]; idset=set(ids)
positive={s:{r['site_id'] for r in obs if r['species']==s and r['site_id'] in idset and 2017<=int(r['season'])<=2023 and int(r['observed_nest_count'])>0} for s in SP}
modern=set.union(*positive.values())
groups={'all_known':idset,'modern_positive':modern,**{'modern_'+s:positive[s] for s in SP}}
site_rows={r['site_id']:r for r in roster}
transform=Transformer.from_crs(4326,3031,always_xy=True)
points={r['site_id']:Point(*transform.transform(float(r['longitude']),float(r['latitude']))) for r in roster}
assert all(not p.is_empty and p.is_valid for p in points.values())
pair=load(macro/'allocation_20261115/original_strict_paired_end_50_source_site_species.csv','31f7915d34a4c3ced6a16ab6f18c933cf677403e')
tri=load(macro/'allocation_20261115/original_three_decade_43_source_site_species.csv','a5ccb7a527605d28804ef389109f416bd6dea090')
assert Counter(x['species'] for x in pair)=={'ADPE':26,'CHPE':12,'GEPE':12}
assert Counter(x['species'] for x in tri)=={'ADPE':19,'CHPE':12,'GEPE':12}
pk={(x['site_id'],x['species']):x for x in pair}
tk={(x['site_id'],x['species']):x for x in tri}
assert len(pk)==50 and len(tk)==43 and set(tk)<=set(pk)
dyn=[]
for key,r in pk.items():
    sid,s=key; st=byid[sid]
    assert st['source_region']==r['source_region'] and float(st['latitude'])==float(r['latitude']) and st['polar_250km_fixed_grid_block']==r['polar_250km_block']
    z=[o for o in obs if o['site_id']==sid and o['species']==s]
    counts=[]
    for a,b,tag in [(1991,2000,'early'),(2011,2020,'late')]:
        vals=[int(o['observed_nest_count']) for o in z if a<=int(o['season'])<=b]
        assert len(vals)==int(r['n_original_count_years_'+tag])>=2,(key,tag,len(vals))
        assert statistics.median(vals)==float(r['site_median_observed_nests_'+tag]),(key,tag)
        counts.append(statistics.median(vals))
    if key in tk:
        t=tk[key];assert float(t['longitude'])==float(st['longitude'])
        assert float(t['median_original_nest_count_0'])==counts[0] and float(t['median_original_nest_count_2'])==counts[1]
    if sid in idset:dyn.append({'site_id':sid,'species':s,'region':r['source_region'],'block':r['polar_250km_block'],'early':counts[0],'late':counts[1],'three_decade':key in tk})
dump('support.json',{'atlas_sites':len(site),'atlas_regions':18,'observed_rows':len(obs),'map_domain_sites':len(roster),'north_excluded':len(site)-len(roster),'groups':{k:len(v) for k,v in groups.items()},'paired_roster_total':len(pair),'paired_domain_by_species':dict(Counter(x['species'] for x in dyn)),'three_decade_domain_by_species':dict(Counter(x['species'] for x in dyn if x['three_decade']))})
print('SUPPORT='+ (out/'support.json').read_text(),flush=True)
url='https://figshare.com/ndownloader/files/43483098'
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mina-source-audit/1.0'}),timeout=70) as f: raw=f.read(15000001)
sha=hashlib.sha256(raw).hexdigest()
assert len(raw)==5414267 and sha=='7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236'
z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
shps=[n for n in z.namelist() if n.lower().endswith('.shp')];assert len(shps)==1
stem=shps[0][:-4]
assert CRS.from_wkt(z.read(stem+'.prj').decode(errors='replace')).equals(CRS.from_epsg(3031))
reader=shapefile.Reader(shp=io.BytesIO(z.read(stem+'.shp')),shx=io.BytesIO(z.read(stem+'.shx')),dbf=io.BytesIO(z.read(stem+'.dbf')))
geoms=defaultdict(list); classes=Counter(); invalid=Counter(); invalid_areas=Counter()
for sr in reader.iterShapeRecords():
    cl=str(sr.record.as_dict()['Vegetation']);classes[cl]+=1
    if cl not in ('Vegetation','Lichen'): continue
    g=shape(sr.shape.__geo_interface__)
    if g.is_empty or not g.is_valid or g.geom_type not in ('Polygon','MultiPolygon'):
        invalid[cl]+=1;invalid_areas[cl]+=g.area
    else:geoms[cl].append(g)
assert classes=={'Vegetation':58740,'Lichen':24876,'Snow Algae':3775}
geometry_audit={'sha256':sha,'bytes':len(raw),'source_class_counts':dict(classes),'invalid_or_empty':dict(invalid),'invalid_source_polygon_area_m2':dict(invalid_areas)}
dump('geometry_audit.json',geometry_audit)
print('GEOMETRY_AUDIT='+json.dumps(geometry_audit),flush=True)
if invalid:
    dump('result.json',{'status':'STOP_ORIGINAL_GEOMETRY_INVALID','geometry_audit':geometry_audit})
    sys.exit(0)
# Exact union of map polygons and of clipped groups. The disjoint subset
# algorithm is appropriate for sparse separated polar vegetation polygons.
def union(gg):
    if not len(gg):return Polygon()
    return sh.disjoint_subset_union_all(np.asarray(gg,dtype=object))
def polygons(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for x in g.geoms for p in polygons(x)]
mapped={}
for cl,gg in geoms.items():mapped[cl]=union(gg)
mapped['Union']=union(list(mapped.values()))
maparea={k:float(g.area) for k,g in mapped.items()}
assert all(a>0 and math.isfinite(a) for a in maparea.values())
assert max(maparea['Vegetation'],maparea['Lichen'])<=maparea['Union']+1e-4<=maparea['Vegetation']+maparea['Lichen']+1e-4
pieces={k:np.asarray(polygons(g),dtype=object) for k,g in mapped.items()}
trees={k:STRtree(v) for k,v in pieces.items()}
print('MAP_AREA='+json.dumps(maparea),flush=True)
area_rows=[]; coverage=[]; region_rows=[]; site_area={}
for rad in RADII:
    clips={}
    for sid,p in points.items():
        b=p.buffer(rad,quad_segs=32)
        clips[sid]={}
        for cl,tree in trees.items():
            ii=tree.query(b,predicate='intersects')
            inter=sh.intersection(pieces[cl][ii],b)
            g=union(inter)
            assert g.area<=b.area+1e-4
            clips[sid][cl]=g
            site_area[(sid,rad,cl)]=float(g.area)
        assert max(clips[sid]['Vegetation'].area,clips[sid]['Lichen'].area)<=clips[sid]['Union'].area+1e-4
        area_rows.append({'site_id':sid,'region':site_rows[sid]['source_region'],'block':site_rows[sid]['polar_250km_fixed_grid_block'],'radius_m':rad,**{cl+'_m2':site_area[sid,rad,cl] for cl in mapped}})
    for name,ss in groups.items():
        for cl in mapped:
            a=float(union([clips[sid][cl] for sid in sorted(ss)]).area)
            assert a<=maparea[cl]+1e-4
            coverage.append({'group':name,'radius_m':rad,'class':cl,'n_sites':len(ss),'union_covered_m2':a,'all_map_m2':maparea[cl],'fraction_all_mapped':a/maparea[cl]})
    if rad==1000:
        for reg in sorted({site_rows[sid]['source_region'] for sid in modern}):
            ss=sorted(sid for sid in modern if site_rows[sid]['source_region']==reg)
            a=float(union([clips[sid]['Union'] for sid in ss]).area)
            region_rows.append({'region':reg,'n_modern_positive_sites':len(ss),'union_covered_m2':a,'radius_m':rad})
    print('COVERAGE_RADIUS='+str(rad),flush=True)
for name in groups:
    for cl in mapped:
        vals=[r['union_covered_m2'] for r in coverage if r['group']==name and r['class']==cl]
        assert vals[0]<=vals[1]+1e-4 and vals[1]<=vals[2]+1e-4
for rad in RADII:
    for cl in mapped:
        dd={r['group']:r['union_covered_m2'] for r in coverage if r['class']==cl and r['radius_m']==rad}
        assert dd['modern_positive']<=dd['all_known']+1e-4
        assert all(dd['modern_'+s]<=dd['modern_positive']+1e-4 for s in SP)

def accounting(rows,rad,cl):
    n0=sum(x['early'] for x in rows);n1=sum(x['late'] for x in rows)
    assert n0>0 and n1>0
    i0=sum(x['early']*site_area[x['site_id'],rad,cl] for x in rows)
    i1=sum(x['late']*site_area[x['site_id'],rad,cl] for x in rows)
    a0=i0/n0;a1=i1/n1;ref=i0*n1/n0
    reweight=n1*(a1-a0);total=(n1-n0)*a0
    assert math.isclose(i1-i0,total+reweight,rel_tol=1e-10,abs_tol=1e-4)
    assert math.isclose(i1-ref,reweight,rel_tol=1e-10,abs_tol=1e-4)
    return {'n_sites':len(rows),'regions':len({x['region'] for x in rows}),'early_count_median_sum':n0,'late_count_median_sum':n1,'early_weighted_map_area_m2':a0,'late_weighted_map_area_m2':a1,'delta_weighted_map_area_m2':a1-a0,'late_over_proportional_index':i1/ref if ref>0 else None,'early_proximity_index':i0,'late_proximity_index':i1,'proportional_reference':ref,'total_component':total,'reweighting_component':reweight}
dynamic=[];omissions=[]
for s in SP:
    for subset in ('paired','three_decade'):
        rows=[x for x in dyn if x['species']==s and (subset=='paired' or x['three_decade'])]
        for rad in RADII:
            for cl in mapped:
                dynamic.append({'species':s,'roster':subset,'radius_m':rad,'class':cl,**accounting(rows,rad,cl)})
        for reg in sorted({x['region'] for x in rows}):
            rest=[x for x in rows if x['region']!=reg]
            if rest and sum(x['early'] for x in rest)>0 and sum(x['late'] for x in rest)>0:
                omissions.append({'species':s,'roster':subset,'excluded_region':reg,'radius_m':1000,'class':'Union',**accounting(rest,1000,'Union')})
table('site_buffer_area.csv',area_rows);table('static_coverage.csv',coverage);table('region_coverage.csv',region_rows);table('dynamic_reweighting.csv',dynamic);table('region_omissions.csv',omissions)
res={'status':'EXECUTED_FIXED_MAP_GEOGRAPHY_NOT_NUTRIENT_FLUX','geometry_audit':geometry_audit,'support':json.loads((out/'support.json').read_text()),'map_area_m2':maparea,'coverage':coverage,'dynamic':dynamic,'region_omissions':omissions}
dump('result.json',res)
print('MACRO_RESULT='+json.dumps({'support':res['support'],'map_area_m2':maparea,'primary_coverage':[x for x in coverage if x['radius_m']==1000 and x['class']=='Union'],'primary_dynamic':[x for x in dynamic if x['radius_m']==1000 and x['class']=='Union'],'region_omissions':omissions}),flush=True)
