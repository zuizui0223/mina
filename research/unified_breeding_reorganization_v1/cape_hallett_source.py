"""Bounded public source acquisition. No effect estimation, no large image downloads."""
import csv,hashlib,io,json,sys,re
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
ROOT='https://datashare.ed.ac.uk'
UUID='3110f25b-7bcd-448f-923b-334b159e759a'
OUT=Path('build/cape-hallett-source')
OUT.mkdir(parents=True,exist_ok=True)
TARGETS={'Plot data for McNemar test.csv','ground truthing.csv','Metadata.docx'}
LIMIT=4_000_000
r={'status':'SOURCE_NOT_YET_ACQUIRED','doi':'10.7488/ds/3417','item_uuid':UUID,'http':[],'members':[],'ecological_fit':False,'animal_plant_temporal_join':False}
def get(u,limit=LIMIT):
    if urlparse(u).scheme!='https' or urlparse(u).hostname!='datashare.ed.ac.uk':raise ValueError('unverified host '+u)
    with requests.get(u,timeout=(12,30),stream=True,allow_redirects=False,headers={'Accept':'*/*','User-Agent':'mina-public-data-source-audit/1.0'}) as x:
        rec={'url':u,'status':x.status_code,'content_type':x.headers.get('Content-Type'),'content_length':x.headers.get('Content-Length')}
        r['http'].append(rec)
        if x.is_redirect:
            target=urljoin(u,x.headers.get('Location',''))
            if target==u:raise ValueError('redirect loop')
            # One public redirect only, same publisher host.
            if urlparse(target).hostname!='datashare.ed.ac.uk':raise ValueError('external redirect not followed')
            with requests.get(target,timeout=(12,30),stream=True,allow_redirects=False) as z:
                r['http'].append({'url':target,'status':z.status_code})
                z.raise_for_status()
                if z.is_redirect:raise ValueError('multiple redirects')
                return bounded(z,limit)
        x.raise_for_status()
        return bounded(x,limit)
def bounded(x,limit):
    if x.headers.get('Content-Length','').isdigit() and int(x.headers['Content-Length'])>limit:raise ValueError('size exceeds limit')
    b=bytearray()
    for c in x.iter_content(65536):
        b.extend(c)
        if len(b)>limit:raise ValueError('size limit')
    return bytes(b)
def js(u):return json.loads(get(u))
def digest(b):return hashlib.sha256(b).hexdigest()
def inspect(b):
    try:t=b.decode('utf-8-sig');encoding='utf-8-sig'
    except UnicodeDecodeError:
        # Legacy degree signs in original publisher CSV; preserve byte identity.
        t=b.decode('cp1252');encoding='cp1252'
        assert t.encode('cp1252')==b
    d=csv.Sniffer().sniff(t[:12000],delimiters=',;\t')
    rows=list(csv.reader(io.StringIO(t),d));h=rows[0];a=[x for x in rows[1:] if any(v.strip() for v in x)]
    if any(len(x)!=len(h) for x in a):raise ValueError('ragged CSV')
    def describe(i):
        vals=[x[i].strip() for x in a];u=sorted(set(vals))
        return {'n_blank':vals.count(''),'distinct':len(u),'values_if_small':u if len(u)<=20 else None}
    return {'encoding':encoding,'rows':len(a),'columns':h,'duplicate_rows':len(a)-len(set(map(tuple,a))),'column_support':{str(i)+':'+k:describe(i) for i,k in enumerate(h)}}
try:
    item=js(ROOT+'/server/api/core/items/'+UUID)
    if item.get('uuid')!=UUID:raise ValueError('item identity')
    r['metadata']=item.get('metadata',{})
    if not any('10.7488/ds/3417' in str(z) for z in r['metadata'].values()):raise ValueError('DOI not verified')
    bundles=js(ROOT+'/server/api/core/items/'+UUID+'/bundles?size=100').get('_embedded',{}).get('bundles',[])
    original=[b for b in bundles if b.get('name')=='ORIGINAL']
    if len(original)!=1:raise ValueError('ORIGINAL bundle ambiguous')
    b=original[0]
    url=b.get('_links',{}).get('bitstreams',{}).get('href') or ROOT+'/server/api/core/bundles/'+b['uuid']+'/bitstreams'
    bit=js(url+('' if '?' in url else '?size=100')).get('_embedded',{}).get('bitstreams',[])
    r['available_files']=[{'name':x.get('name'),'size':x.get('sizeBytes'),'uuid':x.get('uuid'),'checkSum':x.get('checkSum')} for x in bit]
    for x in bit:
        if x.get('name') not in TARGETS:continue
        name=x['name'];rec={'name':name,'uuid':x['uuid']}
        try:
            u=x.get('_links',{}).get('content',{}).get('href') or ROOT+'/server/api/core/bitstreams/'+x['uuid']+'/content'
            raw=get(u)
            if len(raw)!=x['sizeBytes']:raise ValueError('publisher size mismatch')
            cs=x.get('checkSum',{})
            if cs.get('checkSumAlgorithm','').upper()=='MD5':
                if hashlib.md5(raw).hexdigest()!=cs.get('value'):raise ValueError('publisher MD5 mismatch')
            rec.update(bytes=len(raw),sha256=digest(raw),source_checksum=cs)
            if name.endswith('.csv'):
                (OUT/name).write_bytes(raw)
                rec['schema']=inspect(raw)
            else:
                import zipfile
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    if z.testzip() is not None:raise ValueError('docx CRC')
                    rec['docx_members']=z.namelist()[:30]
                    import xml.etree.ElementTree as ET
                    tree=ET.fromstring(z.read('word/document.xml'))
                    rec['metadata_text']=' '.join(n.text or '' for n in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))[:16000]
            rec['status']='ACQUIRED';(OUT/name).write_bytes(raw)
        except Exception as e:rec['status']='FAILED';rec['error']=str(e)
        r['members'].append(rec)
    if any(x['name']=='Plot data for McNemar test.csv' and x['status']=='ACQUIRED' for x in r['members']):r['status']='VEGETATION_CSV_ACQUIRED_SCHEMA_REVIEW_REQUIRED'
except Exception as e:r['error']=type(e).__name__+': '+str(e)
(OUT/'source_receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
# Keep verbose raw metadata out of workflow log; archived receipt retains it.
print('CAPE_SOURCE_RESULT='+json.dumps({k:v for k,v in r.items() if k!='metadata'},ensure_ascii=False,separators=(',',':')))
