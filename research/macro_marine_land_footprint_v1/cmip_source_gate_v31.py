"""V31: exact original CMIP6 stores plus same-member actual sea surface temperature."""
import csv,hashlib,io,json,pathlib,sys,urllib.request,concurrent.futures
from collections import defaultdict
old,root=map(pathlib.Path,sys.argv[1:3]);root.mkdir(parents=True,exist_ok=True)
def dump(n,v):(root/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def get(url,cap):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mina-source-audit/1.0'}),timeout=90) as f:
        b=f.read(cap+1)
    assert len(b)<=cap and len(b)>0,(url,len(b))
    return b
models={'ACCESS-CM2':'r1i1p1f1','BCC-CSM2-MR':'r1i1p1f1','CESM2':'r4i1p1f1'}
experiments=('historical','ssp245','ssp585')
oldraw=old.read_bytes();previous=list(csv.DictReader(io.StringIO(oldraw.decode('utf-8-sig'))));assert len(previous)==27
assert {(r['source_id'],r['member_id']) for r in previous}==set(models.items())
pinned=[r for r in previous if r['variable_id'] in ('siconc','sos')];assert len(pinned)==18
catalog_url='https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv'
catalog=get(catalog_url,150000000)
selected=pinned.copy();missing=[];catalog_rows=defaultdict(list)
for r in csv.DictReader(io.StringIO(catalog.decode('utf-8-sig'))):
    if r['source_id'] in models and r['member_id']==models[r['source_id']] and r['experiment_id'] in experiments and r['table_id']=='Omon' and r['variable_id']=='tos':
        catalog_rows[r['source_id']].append(r)
for s in models:
    rows=catalog_rows[s];grid=defaultdict(list)
    for r in rows:grid[r['grid_label']].append(r)
    common=[k for k,v in grid.items() if set(x['experiment_id'] for x in v)==set(experiments)]
    if not common:
        missing.append({'source_id':s,'variable':'tos','reason':'no same-member shared grid across all three experiments','available':sorted({(r['experiment_id'],r['grid_label']) for r in rows})})
        continue
    g=sorted(common,key=lambda x:(x!='gn',x))[0]
    for exp in experiments:
        v=[r for r in grid[g] if r['experiment_id']==exp];assert v
        selected.append(sorted(v,key=lambda r:(r['version'],r['zstore']))[-1])
assert len({(r['source_id'],r['variable_id'],r['experiment_id']) for r in selected})==len(selected)
fields=list(previous[0])
with (root/'selected_stores.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(selected)
# Inventory native source metadata before opening any climate values.
def inspect(r):
    ident={k:r[k] for k in ('source_id','member_id','variable_id','experiment_id','grid_label','zstore','version')}
    url=r['zstore'].replace('gs://','https://storage.googleapis.com/').rstrip('/')+'/.zmetadata'
    try:
        b=get(url,10000000);meta=json.loads(b)['metadata'];v=r['variable_id']
        a=meta[v+'/.zattrs'];ar=meta[v+'/.zarray'];rootattrs=meta.get('.zattrs',{});ta=meta['time/.zattrs']
        for key in ('source_id','experiment_id','variant_label'):
            expected=r['member_id'] if key=='variant_label' else r[key]
            if key in rootattrs:assert rootattrs[key]==expected,(key,rootattrs[key],expected)
        if r['experiment_id']!='historical' and rootattrs.get('parent_variant_label'):
            assert rootattrs['parent_variant_label']==r['member_id']
        units=a.get('units','')
        valid={'siconc':('%','percent','percentage','1','fraction'),'sos':('0.001','psu','1e-3','1.e-3','g kg-1','g/kg'),'tos':('K','kelvin','degC','degrees_C','degree_Celsius','degrees_Celsius')}
        assert units in valid[v],(v,units)
        return {**ident,'status':'verified_metadata','metadata_sha256':hashlib.sha256(b).hexdigest(),'units':units,'shape':ar['shape'],'chunks':ar['chunks'],'dimensions':a['_ARRAY_DIMENSIONS'],'calendar':ta.get('calendar'),'time_units':ta.get('units'),'tracking_id':rootattrs.get('tracking_id'),'parent_variant_label':rootattrs.get('parent_variant_label')}
    except Exception as e:return {**ident,'status':'failed','error':type(e).__name__+': '+str(e)[:500]}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
    result=list(e.map(inspect,selected))
good=[r for r in result if r['status']=='verified_metadata']
complete=[s for s in models if sum(r['source_id']==s for r in good)==9]
report={'status':'ALL_THREE_MODEL_METADATA_READY' if len(complete)==3 else 'PARTIAL_SOURCE_HOLD','original_selection_sha256':hashlib.sha256(oldraw).hexdigest(),'catalog_sha256':hashlib.sha256(catalog).hexdigest(),'selected_stores':len(selected),'metadata_verified':len(good),'complete_models':complete,'missing':missing,'metadata_failures':[r for r in result if r['status']!='verified_metadata'],'stores':result,'limits':'Source catalog/metadata only; native coordinates, time coverage, climate values and scenario outputs not yet verified.'}
dump('receipt.json',report);print('V31_CMIP_SOURCE='+json.dumps(report),flush=True)
