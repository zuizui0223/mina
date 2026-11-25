"""Public source intake, only the exact three advertised files; no outcome fit."""
import hashlib, json, csv, io
from pathlib import Path
from urllib.parse import urlparse
import requests
OUT=Path('build/pygoscelis-soil-v16');OUT.mkdir(parents=True,exist_ok=True)
URL='https://zenodo.org/api/records/17742676'
PINS={'Methods.txt':'0a2430c1943387e5369159ea950774f2','Pygoscelis_metadata.csv':'b58d6e6b476c98afeb9f4e75f8f520fe','Pygoscelis_PP.csv':'fa57915e1d1253a6eeac36e70579ccf9'}
r={'status':'SOURCE_NOT_ACQUIRED','doi':'10.5281/zenodo.17742676','http':[],'files':[],'ecological_fit':False}
s=requests.Session();s.headers.update({'User-Agent':'mina-research-public-source-audit/1.0','Accept-Encoding':'identity'})
def get(u,cap):
    if urlparse(u).scheme!='https' or urlparse(u).hostname not in ('zenodo.org','www.zenodo.org'):raise ValueError('unverified host')
    with s.get(u,stream=True,timeout=(12,30),allow_redirects=False) as x:
        r['http'].append({'url':u,'status':x.status_code,'content_type':x.headers.get('Content-Type')})
        if x.status_code!=200:raise ValueError('HTTP '+str(x.status_code))
        b=bytearray()
        for c in x.iter_content(16384):
            b.extend(c)
            if len(b)>cap:raise ValueError('byte cap')
    return bytes(b)
try:
    raw=get(URL,1_000_000);d=json.loads(raw);m=d['metadata']
    assert d['id']==17742676 and d['doi']==r['doi'] and m.get('license')
    assert {x['key'] for x in d['files']}==set(PINS)
    r['metadata']={k:m.get(k) for k in ['title','creators','publication_date','license','related_identifiers']}
    (OUT/'metadata.json').write_bytes(raw)
    assert sum(x['size'] for x in d['files'])<=1_000_000
    for x in d['files']:
        name=x['key'];assert x['checksum']=='md5:'+PINS[name]
        b=get(x['links']['self'],x['size']+1);assert len(b)==x['size'] and hashlib.md5(b).hexdigest()==PINS[name]
        (OUT/name).write_bytes(b)
        f={'name':name,'size':len(b),'md5':PINS[name],'sha256':hashlib.sha256(b).hexdigest()}
        try:t=b.decode('utf-8-sig');f['encoding']='utf-8-sig'
        except UnicodeDecodeError:
            t=b.decode('cp1252');assert t.encode('cp1252')==b;f['encoding']='cp1252'
        if name.endswith('.csv'):
            dialect=csv.Sniffer().sniff(t[:10000],delimiters=',;\t')
            a=list(csv.reader(io.StringIO(t),dialect));f['rows_excluding_header']=len([v for v in a[1:] if any(z.strip() for z in v)]);f['header']=a[0];f['widths']=sorted({len(v) for v in a})
            # Only expose metadata field values, not chemical outcomes until study grain is reviewed.
            if name=='Pygoscelis_metadata.csv':
                f['field_support']={h:{'nonblank':sum(i<len(v) and bool(v[i].strip()) for v in a[1:]),'unique':len({v[i] for v in a[1:] if i<len(v)})} for i,h in enumerate(a[0])}
        else:f['methods_text']=t
        r['files'].append(f)
    r['status']='SOURCE_VERIFIED_SCHEMA_REVIEW_REQUIRED'
except Exception as e:r['error']=type(e).__name__+': '+str(e)
(OUT/'receipt.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
print('V16_RECEIPT='+json.dumps(r,separators=(',',':'),ensure_ascii=False))
