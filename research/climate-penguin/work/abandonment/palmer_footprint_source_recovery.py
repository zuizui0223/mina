"""Bounded read-only retrieval of original Palmer maps and small documentation.

Downloaded maps are NOT authenticated historical colony polygons. This script
never estimates a vegetation effect and never downloads large drone archives.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

MAX_BYTES = 25 * 1024 * 1024
GEOMETRY_STATUS = 'not_authenticated_colony_polygons'
SOURCES = (
    ('aspa113_2014.pdf', 'https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/113.pdf', 'pdf'),
    ('patterson2001_rutgers.pdf', 'https://pallter.marine.rutgers.edu/docs/publications/documents/lterfinalms/204lterc.pdf', 'pdf'),
    ('era_litchfield_v3.pdf', 'https://www.era.gs/projects/palmer/Map7-LitchfieldIsland-v3.pdf', 'pdf'),
    ('era_torgersen_v3.pdf', 'https://www.era.gs/projects/palmer/Map5-TorgersenIsland-v3.pdf', 'pdf'),
    ('duke_site_guide.txt', 'https://research.repository.duke.edu/downloads/1z40kt742?locale=en', 'text'),
    ('duke_dataset.html', 'https://research.repository.duke.edu/concern/datasets/r207tq370?locale=en', 'html'),
    ('duke_orthomosaics.html', 'https://research.repository.duke.edu/concern/parent/r207tq370/datasets/pn89d753m', 'html'),
)

def valid_payload(raw: bytes, kind: str) -> bool:
    if not raw or len(raw) > MAX_BYTES:
        return False
    if kind == 'pdf':
        return raw.lstrip().startswith(b'%PDF-')
    text = raw[:4096].lstrip().lower()
    if kind == 'text':
        return not any(t in text for t in (b'<!doctype html', b'<html', b'<form'))
    if kind == 'html':
        return b'<html' in text or b'<!doctype html' in text
    raise ValueError('Unknown kind: ' + kind)

def retrieve(source: tuple[str,str,str], out: Path) -> dict:
    name, url, kind = source
    record = {'file': name, 'url': url, 'expected_type': kind,
              'status': 'failed', 'geometry_status': GEOMETRY_STATUS}
    try:
        request = Request(url, headers={'User-Agent':'mina-public-footprint-source-audit/1.0'})
        with urlopen(request, timeout=30) as response:
            raw = response.read(MAX_BYTES+1)
            record.update(http_status=response.status, final_url=response.geturl(),
                          content_type=response.headers.get('Content-Type',''), bytes=len(raw))
        if not valid_payload(raw, kind):
            raise ValueError('invalid, empty, oversized, or substituted payload')
        (out / name).write_bytes(raw)
        record.update(status='retrieved_payload', sha256=hashlib.sha256(raw).hexdigest())
    except Exception as exc:
        record['error'] = f'{type(exc).__name__}: {str(exc)[:300]}'
    return record

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda s:retrieve(s,args.out),SOURCES))
    result={'schema':1,'retrieved_utc':datetime.now(timezone.utc).isoformat(),
            'geometry_status':GEOMETRY_STATUS,'sources':records,
            'limits':['Source retrieval only; maps are not GPS-verified colony polygons.',
                      'HTML receipt is not proof of data download or authorized archive access.',
                      'No NDVI, vegetation effect, coordinate correction or count inference.']}
    (args.out/'source_receipts.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)
    return 0 if any(r['expected_type']=='pdf' and r['status']=='retrieved_payload' for r in records) else 2

if __name__=='__main__':
    raise SystemExit(main())
