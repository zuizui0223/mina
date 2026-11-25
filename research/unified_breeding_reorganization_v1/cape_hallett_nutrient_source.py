"""Acquire only public BAS nutrient archive; structural inventory, no ecological fit."""
import io,json,hashlib,zipfile
from pathlib import Path
from urllib.parse import urlparse
import requests
OUT=Path('build/cape-hallett-nutrient')
ENTRY='eba81a75-2e49-4063-92c8-97c26f300ce5'
URL='https://ramadda.data.bas.ac.uk/repository/entry/show?entryid='+ENTRY+'&output=zip.tree'
r={'status':'SOURCE_NOT_ACQUIRED','doi':'10.5285/'+ENTRY,'url':URL,'rights':'Open Government Licence v3 (BAS metadata)','ecological_fit':False}
OUT.mkdir(parents=True,exist_ok=True)
try:
    with requests.get(URL,timeout=(15,45),stream=True,allow_redirects=False,headers={'Accept':'*/*','User-Agent':'mina-research-source-audit/1.0'}) as z:
        r['http']={'status':z.status_code,'content_type':z.headers.get('Content-Type'),'content_length':z.headers.get('Content-Length')}
        if z.is_redirect:raise ValueError('unreviewed redirect')
        z.raise_for_status()
        assert urlparse(z.url).hostname=='ramadda.data.bas.ac.uk'
        b=bytearray()
        for chunk in z.iter_content(65536):
            b.extend(chunk)
            if len(b)>4_000_000:raise ValueError('archive size limit')
    raw=bytes(b)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(x.file_size for x in z.infolist())>20_000_000:raise ValueError('expanded size limit')
        assert z.testzip() is None
        r['members']=[{'name':i.filename,'size':i.file_size,'sha256':hashlib.sha256(z.read(i.filename)).hexdigest()} for i in z.infolist() if not i.is_dir()]
        r['archive_sha256']=hashlib.sha256(raw).hexdigest()
        r['archive_bytes']=len(raw)
        (OUT/'original_source.zip').write_bytes(raw)
        r['status']='SOURCE_ACQUIRED_SCHEMA_REVIEW_REQUIRED'
        for f in r['members']:
            if not f['name'].lower().endswith(('.xls','.xlsx')):continue
            try:
                import pandas as pd
                xl=pd.ExcelFile(io.BytesIO(z.read(f['name'])))
                f['worksheets']=[]
                for name in xl.sheet_names:
                    d=xl.parse(name,header=None)
                    f['worksheets'].append({'sheet':name,'shape':list(d.shape),'first_rows':[[None if pd.isna(v) else str(v)[:120] for v in row] for row in d.iloc[:5,:20].values]})
            except Exception as e:f['schema_error']=type(e).__name__+': '+str(e)
except Exception as e:r['error']=type(e).__name__+': '+str(e)
(OUT/'receipt.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
print('NUTRIENT_SOURCE='+json.dumps(r,separators=(',',':'),ensure_ascii=False))
