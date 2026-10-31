"""V9 official recent monitoring sources: retrieve, hash, render; no fitted effect."""
from __future__ import annotations
import argparse, hashlib, json, urllib.request
from pathlib import Path
from urllib.parse import urlparse

SOURCES={
 'UBA2025':'https://www.umweltbundesamt.de/system/files/medien/11850/publikationen/63_2025_texte.pdf',
 'ASPA171_2024':'https://documents.ats.aq/recatt/att783_e.pdf',
}
MAX_BYTES=100_000_000

def validate_bytes(raw):
    if not raw.startswith(b'%PDF-') or not 1000<=len(raw)<=MAX_BYTES:
        raise ValueError('Invalid PDF or size')
    return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def main():
    import pymupdf
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    results={}
    for key,url in SOURCES.items():
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'mina-official-monitoring-source/1.0'})
            with urllib.request.urlopen(req,timeout=90) as response:
                if urlparse(response.url).hostname!=urlparse(url).hostname:
                    raise ValueError('Publisher redirect requires review')
                raw=response.read(MAX_BYTES+1)
            rec=validate_bytes(raw);doc=pymupdf.open(stream=raw,filetype='pdf')
            rec.update(url=url,pages=len(doc),status='DOWNLOADED_RENDERED_NOT_YET_TRANSCRIBED')
            (args.out/(key+'.pdf')).write_bytes(raw)
            text='\n'.join(f'=== PDF PAGE INDEX {i} ===\n'+page.get_text() for i,page in enumerate(doc))
            (args.out/(key+'.txt')).write_text(text,encoding='utf-8')
            selected=([50,56,57,58,59,60,61,108,109,231,232,233,234]
                      if key=='UBA2025' else range(min(8,len(doc))))
            for i in selected:
                if i<len(doc):
                    doc[i].get_pixmap(matrix=pymupdf.Matrix(1.8,1.8),alpha=False).save(
                        args.out/f'{key}_page{i:03}.png')
            results[key]=rec
        except Exception as error:
            results[key]={'url':url,'status':'SOURCE_HOLD','error':type(error).__name__+': '+str(error)}
    receipt={'sources':results,'no_counts_inferred':True,'no_effect_fitted':True,
       'season_is_start_end_not_single_census_year':True}
    (args.out/'primary_documents_v9_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('MAXWELL_PRIMARY_DOCUMENTS_V9='+json.dumps(receipt),flush=True)
    return 0 if all(r['status'].startswith('DOWNLOADED') for r in results.values()) else 2

if __name__=='__main__':raise SystemExit(main())
