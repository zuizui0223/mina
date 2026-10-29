"""Resolve and inspect an actual original OSI450-a1 Southern monthly file."""
from __future__ import annotations
import argparse, hashlib, json, re, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
ROOT='https://thredds.met.no/thredds/catalog/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly/catalog.xml'
HOST='thredds.met.no'
MAX_BYTES=25_000_000

def get(url,limit=MAX_BYTES):
    u=urllib.parse.urlparse(url)
    if u.scheme!='https' or u.hostname!=HOST:raise ValueError('not original publisher URL')
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'mina-monthly-marine-ice-source-v4/1.0'}),timeout=45) as r:
        if urllib.parse.urlparse(r.geturl()).hostname!=HOST:raise ValueError('unexpected publisher redirect')
        raw=r.read(limit+1)
    if not raw or len(raw)>limit:raise ValueError('empty or oversized source')
    return raw

def catalog(raw,url):
    root=ET.fromstring(raw)
    if root.tag.split('}')[-1]!='catalog':raise ValueError('not THREDDS catalog')
    refs=[];files=[]
    for e in root.iter():
        name=e.tag.split('}')[-1]
        if name=='catalogRef':
            href=e.attrib.get('{http://www.w3.org/1999/xlink}href','')
            target=urllib.parse.urljoin(url,href)
            if urllib.parse.urlparse(target).hostname==HOST:
                refs.append({'name':e.attrib.get('name',e.attrib.get('{http://www.w3.org/1999/xlink}title','')),'url':target})
        if name=='dataset' and e.attrib.get('urlPath'):
            files.append({'name':e.attrib.get('name',''),'url_path':e.attrib['urlPath']})
    return {'refs':refs,'datasets':files}

def needed_refs(refs,years):
    return [r['url'] for r in refs if r['name'].strip() in {str(y) for y in years}]

def choose_file(rows,year,month):
    pattern=re.compile(r'ice_conc_sh_ease2-250_cdr-v3p1_'+f'{year:04d}{month:02d}'+r'\.nc$')
    names=[r['url_path'] for r in rows if '/monthly/' in r['url_path'] and pattern.search(r['url_path'])]
    if len(names)!=1:raise ValueError(f'exact original monthly source missing/ambiguous: {year}-{month}: {names}')
    return names[0]

def safe_json(x):
    if hasattr(x,'tolist'):return x.tolist()
    return str(x)

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    report={'status':'SOURCE_UNVERIFIED','catalogs':[]}
    try:
        raw=get(ROOT,4_000_000);d=catalog(raw,ROOT)
        (a.out/'monthly_catalog.xml').write_bytes(raw)
        report['catalogs'].append({'url':ROOT,'sha256':hashlib.sha256(raw).hexdigest(),**d})
        files=d['datasets']
        for i,url in enumerate(needed_refs(d['refs'],[1993])):
            raw=get(url,4_000_000);part=catalog(raw,url);files+=part['datasets']
            (a.out/f'monthly_catalog_child{i}.xml').write_bytes(raw)
            report['catalogs'].append({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),**part})
        rel=choose_file(files,1993,8)
        url='https://thredds.met.no/thredds/fileServer/'+rel
        data=get(url)
        if not (data.startswith(b'CDF') or data.startswith(b'\x89HDF')):raise ValueError('not original NetCDF')
        target=a.out/Path(rel).name;target.write_bytes(data)
        import xarray as xr
        with xr.open_dataset(target,decode_times=False) as z:
            attrs={k:{'dims':list(z[k].dims),'shape':list(z[k].shape),'attrs':dict(z[k].attrs),'encoding':{j:z[k].encoding.get(j) for j in ['dtype','scale_factor','add_offset','_FillValue']}} for k in z.variables}
            report.update(status='ORIGINAL_MONTHLY_NETCDF_VERIFIED',source_url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),global_attrs=dict(z.attrs),variables=attrs)
    except Exception as e:report.update(status='SOURCE_HOLD',error=type(e).__name__+': '+str(e))
    (a.out/'monthly_sample_receipt.json').write_text(json.dumps(report,default=safe_json,indent=2)+'\n')
    print('MONTHLY_SAMPLE_RECEIPT='+json.dumps(report,default=safe_json),flush=True)
    return 0 if report['status']=='ORIGINAL_MONTHLY_NETCDF_VERIFIED' else 2
if __name__=='__main__':raise SystemExit(main())
