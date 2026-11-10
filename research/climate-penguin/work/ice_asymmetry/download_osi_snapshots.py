import requests,pathlib,concurrent.futures,json,hashlib
p=pathlib.Path('work/ice_asymmetry/osi_snapshots');p.mkdir(exist_ok=True)
base='https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/drift_455m_files/merged/'
def fetch(z):
 y,m=z;name=f'ice_drift_sh_ease2-750_cdr-v1p0_24h-{y}{m:02d}151200.nc';u=base+f'{y}/{m:02d}/'+name;f=p/name
 try:
  if not f.exists():
   r=requests.get(u,timeout=25);r.raise_for_status();f.write_bytes(r.content)
  b=f.read_bytes();ok=b.startswith(b'\x89HDF') or b.startswith(b'CDF');return {'year':y,'month':m,'url':u,'file':str(f),'ok':ok,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 except Exception as e:return {'year':y,'month':m,'url':u,'ok':False,'error':str(e)[:150]}
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for i,r in enumerate(ex.map(fetch,[(y,m) for y in range(1991,2021) for m in [4,5,9,10]])):
  rows.append(r)
  if (i+1)%20==0:print('completed',i+1,flush=True)
pathlib.Path('outputs/ice_asymmetry/osi_download_manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print('success',sum(x['ok'] for x in rows),'/',len(rows))
