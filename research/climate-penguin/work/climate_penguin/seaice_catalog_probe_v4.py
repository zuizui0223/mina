"""Bounded publisher-only OSI-450-a1 catalog inspection; no biological models."""
from __future__ import annotations
import argparse,hashlib,json,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
HOST='thredds.met.no'
ROOTS=['https://thredds.met.no/thredds/catalog/osisaf/osisaf_cdrseaiceconc.xml','https://thredds.met.no/thredds/catalog/osisaf/met.no/reprocessed/ice/conc_450a1_files/catalog.xml']
MAX_CATALOGS=12
MAX_BYTES=4_000_000

def parse_catalog(raw: bytes,url: str)->dict:
    root=ET.fromstring(raw)
    if root.tag.split('}')[-1]!='catalog':raise ValueError('not a publisher THREDDS catalog')
    refs=[];datasets=[]
    for e in root.iter():
        name=e.tag.split('}')[-1]
        if name=='catalogRef':
            href=e.attrib.get('{http://www.w3.org/1999/xlink}href','')
            target=urllib.parse.urljoin(url,href)
            if urllib.parse.urlparse(target).hostname==HOST and target.startswith('https://'):
                refs.append({'name':e.attrib.get('name',e.attrib.get('{http://www.w3.org/1999/xlink}title','')),'url':target})
        if name=='dataset' and e.attrib.get('urlPath'):
            datasets.append({'name':e.attrib.get('name',''),'url_path':e.attrib['urlPath']})
    return {'refs':refs,'datasets':datasets}

def fetch(url: str)->bytes:
    if urllib.parse.urlparse(url).hostname!=HOST:raise ValueError('not original publisher')
    req=urllib.request.Request(url,headers={'User-Agent':'mina-OSI450-monthly-source-v4/1.0'})
    with urllib.request.urlopen(req,timeout=25) as r:
        if urllib.parse.urlparse(r.geturl()).hostname!=HOST:raise ValueError('unexpected redirect')
        raw=r.read(MAX_BYTES+1)
    if not raw or len(raw)>MAX_BYTES:raise ValueError('invalid catalog size')
    return raw

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    queue=list(ROOTS);seen=set();receipts=[]
    while queue and len(seen)<MAX_CATALOGS:
        url=queue.pop(0)
        if url in seen:continue
        seen.add(url);item={'url':url}
        try:
            raw=fetch(url);item.update(parse_catalog(raw,url));item.update(status='retrieved_catalog',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
            (a.out/f'catalog_{len(receipts):02d}.xml').write_bytes(raw)
            preferred=[]
            for ref in item['refs']:
                text=(ref['name']+' '+ref['url']).lower()
                if any(t in text for t in ('monthly','monthly_mean','v3p1','450a1')):preferred.append(ref['url'])
            queue=preferred+queue
        except Exception as e:item.update(status='SOURCE_ACCESS_HOLD',error=type(e).__name__+': '+str(e)[:350])
        receipts.append(item);print('CATALOG_RECEIPT='+json.dumps(item),flush=True)
    report={'status':'original_catalog_inspection_only','sources':receipts,'no_seaice_values_or_population_effects_opened':True}
    (a.out/'catalog_result.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if any(r['status']=='retrieved_catalog' for r in receipts) else 2
if __name__=='__main__':raise SystemExit(main())
