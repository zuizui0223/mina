"""Public original data intake; verify file identity, inspect structural support only."""
import csv,hashlib,io,json,re,zipfile
from pathlib import Path
from urllib.parse import urlparse
import requests
import pandas as pd
OUT=Path('build/antarctic-cryptogam-v15')
OUT.mkdir(parents=True,exist_ok=True)
URL='https://zenodo.org/api/records/17112197'
CAP=20_000_000
r={'status':'SOURCE_NOT_ACQUIRED','doi':'10.5281/zenodo.17112197','http':[],'files':[],'ecological_fit':False}
s=requests.Session()
s.headers.update({'User-Agent':'mina-research-public-source-audit/1.0','Accept-Encoding':'identity'})
def get(u,cap):
    if urlparse(u).scheme!='https' or urlparse(u).hostname not in ('zenodo.org','www.zenodo.org'):raise ValueError('unverified host')
    with s.get(u,stream=True,timeout=(15,45),allow_redirects=False) as z:
        r['http'].append({'url':u,'status':z.status_code,'content_type':z.headers.get('Content-Type'),'content_length':z.headers.get('Content-Length')})
        if z.status_code!=200:raise ValueError('HTTP '+str(z.status_code))
        if z.headers.get('Content-Length','').isdigit() and int(z.headers['Content-Length'])>cap:raise ValueError('declared cap')
        b=bytearray()
        for c in z.iter_content(65536):
            b.extend(c)
            if len(b)>cap:raise ValueError('byte cap')
        return bytes(b)
def schema(raw,name):
    l=name.lower()
    if l.endswith(('.csv','.tsv','.txt')):
        for enc in ('utf-8-sig','cp1252'):
            try:t=raw.decode(enc);break
            except UnicodeDecodeError:continue
        try:
            dialect=csv.Sniffer().sniff(t[:25000],delimiters=',;\t')
            a=list(csv.reader(io.StringIO(t),dialect))
        except csv.Error:return {'text_excerpt':t[:1800]}
        if not a:return {'empty':True}
        widths={}
        for x in a:widths[str(len(x))]=widths.get(str(len(x)),0)+1
        return {'encoding':enc,'rows_including_header':len(a),'header':a[0],'width_counts':widths,
                'candidate_identifier_values':{h:sorted({x[i] for x in a[1:] if len(x)==len(a[0])})[:50] for i,h in enumerate(a[0]) if re.search(r'year|season|site|location|region|transect|plant|host|cryptogam|species|origin|source|influenc|disturb|impact|date',h,re.I)}}
    if l.endswith(('.xlsx','.xls')):
        x=pd.ExcelFile(io.BytesIO(raw));return {'sheets':[{'name':n,'shape':list(x.parse(n,header=None).shape),'first_row':[str(v)[:120] for v in x.parse(n,header=None).iloc[0].values]} for n in x.sheet_names]}
    if l.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            if sum(x.file_size for x in z.infolist())>50_000_000:raise ValueError('expanded cap')
            assert z.testzip() is None
            return {'members':[{'name':i.filename,'bytes':i.file_size,'schema':schema(z.read(i.filename),i.filename) if i.filename.lower().endswith(('.csv','.tsv','.xlsx','.xls','.txt')) else None} for i in z.infolist() if not i.is_dir()]}
    if l.endswith(('.r','.rmd','.md')):return {'text_excerpt':raw.decode('utf-8',errors='replace')[:2500]}
    return {'format_uninspected':True}
try:
    raw=get(URL,1_000_000);d=json.loads(raw);m=d['metadata']
    assert int(d['id'])==17112197 and d['doi']==r['doi']
    r['metadata']={k:m.get(k) for k in ('title','publication_date','creators','license','related_identifiers','description')}
    (OUT/'metadata.json').write_bytes(raw)
    if not m.get('license'):raise ValueError('license absent')
    files=d['files'];r['available_files']=[{'key':x['key'],'size':x['size'],'checksum':x['checksum']} for x in files]
    if sum(x['size'] for x in files)>CAP:raise ValueError('total source cap')
    for x in files:
        key=x['key'];assert key=='ingeborgklara/How-the-small-host-the-small-v1.0.0.zip'
        name=Path(key).name
        b=get(x['links']['self'],x['size']+1)
        assert len(b)==x['size']
        alg,expected=x['checksum'].split(':',1);assert alg in ('md5','sha256') and hashlib.new(alg,b).hexdigest()==expected
        (OUT/name).write_bytes(b)
        f={'name':name,'bytes':len(b),'checksum':x['checksum'],'sha256':hashlib.sha256(b).hexdigest()}
        try:f['schema']=schema(b,name)
        except Exception as e:f['schema_error']=type(e).__name__+': '+str(e)
        r['files'].append(f)
    r['status']='ORIGINAL_SOURCE_ACQUIRED_SCHEMA_REVIEW_REQUIRED'
except Exception as e:r['error']=type(e).__name__+': '+str(e)
(OUT/'receipt.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
print('V15_SOURCE='+json.dumps({k:v for k,v in r.items() if k!='metadata'},ensure_ascii=False,separators=(',',':')))
