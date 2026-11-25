"""Public GeoTIFF metadata only: strict HTTP range and total byte budget."""
import io,json,hashlib,re,struct,math
from pathlib import Path
import requests
import tifffile
from urllib.parse import urlparse
ROOT='https://datashare.ed.ac.uk'
UUID='814f5d65-506c-4fd4-8f3c-4b9163b0e484'
META=ROOT+'/server/api/core/bitstreams/'+UUID
URL=META+'/content'
SIZE=17538362940
BLOCK=32768
BUDGET=4*1024*1024
OUT=Path('build/cape-hallett-raster-metadata')
OUT.mkdir(parents=True,exist_ok=True)
r={'status':'SOURCE_NOT_YET_VERIFIED','doi':'10.7488/ds/3417','bitstream':UUID,'expected_size':SIZE,'whole_file_verified':False,'pixel_decoding':False,'requests':[]}
s=requests.Session()
s.headers.update({'User-Agent':'mina-public-geotiff-metadata-audit/1.0','Accept-Encoding':'identity'})
def meta():
    with s.get(META,stream=True,allow_redirects=False,timeout=(10,20)) as x:
        x.raise_for_status()
        if x.status_code!=200:raise ValueError('metadata status '+str(x.status_code))
        b=bytearray()
        for c in x.iter_content(32768):
            b.extend(c)
            if len(b)>250000:raise ValueError('metadata size cap')
    d=json.loads(b);assert d['uuid']==UUID and d['sizeBytes']==SIZE
    assert d['checkSum']['value']=='5375a61824f97d927c19ec3bbb5f6619'
    return {k:d[k] for k in ['uuid','name','sizeBytes','checkSum']}
class RangeFile(io.RawIOBase):
    def __init__(self):
        self.pos=0;self.cache={};self.spent=0;self.name='public_rudy_2018.tif'
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        p=offset+(0 if whence==0 else self.pos if whence==1 else SIZE)
        if p<0:raise ValueError('negative seek')
        self.pos=p;return p
    def chunk(self,a):
        if a in self.cache:return self.cache[a]
        b=min(a+BLOCK,SIZE)-1;n=b-a+1
        if n<1:raise ValueError('range past EOF')
        if self.spent+n>BUDGET or len(r['requests'])>=128:raise ValueError('metadata range budget reached')
        self.spent+=n
        with s.get(URL,headers={'Range':f'bytes={a}-{b}'},stream=True,allow_redirects=False,timeout=(12,20)) as x:
            e={'first':a,'last':b,'http':x.status_code,'content_range':x.headers.get('Content-Range'),'content_length':x.headers.get('Content-Length'),'encoding':x.headers.get('Content-Encoding')}
            r['requests'].append(e)
            if x.status_code!=206:raise ValueError('server did not honor byte range; response body not read')
            if e['content_range']!=f'bytes {a}-{b}/{SIZE}' or e['encoding'] not in (None,'identity'):raise ValueError('range integrity')
            raw=bytearray()
            for c in x.iter_content(32768):
                raw.extend(c)
                if len(raw)>n:raise ValueError('range overrun')
            if len(raw)!=n:raise ValueError('range size mismatch')
            data=bytes(raw);e['sha256']=hashlib.sha256(data).hexdigest();e['bytes']=len(data)
        self.cache[a]=data;return data
    def read(self,size=-1):
        if size is None or size<0:raise ValueError('unbounded read refused')
        if size>BUDGET:raise ValueError('single metadata read exceeds budget')
        end=min(SIZE,self.pos+size);out=bytearray()
        while self.pos<end:
            a=(self.pos//BLOCK)*BLOCK;d=self.chunk(a);n=min(end-self.pos,len(d)-(self.pos-a))
            if n<=0:raise ValueError('invalid range length')
            out.extend(d[self.pos-a:self.pos-a+n]);self.pos+=n
        return bytes(out)
    def readinto(self,b):
        d=self.read(len(b));b[:len(d)]=d;return len(d)
def plain(x):
    if hasattr(x,'tolist'):return plain(x.tolist())
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    if isinstance(x,dict):return {str(k):plain(v) for k,v in x.items()}
    if isinstance(x,bytes):return x.decode('utf-8','replace')[:4000]
    if isinstance(x,(str,int,float,bool)) or x is None:return x
    return str(x)[:4000]
def page_info(p):
    tags={}
    for n in (33550,33922,34264,34735,34736,34737,42113):
        if n in p.tags:tags[str(n)]=plain(p.tags[n].value)
    return {'shape':list(p.shape),'dtype':str(p.dtype),'tiled':bool(p.is_tiled),'tilewidth':p.tilewidth,'tilelength':p.tilelength,'compression':str(p.compression),'geotags':tags,'geotiff_metadata':plain(p.geotiff_tags)}
try:
    r['publisher']=meta()
    f=RangeFile()
    # Check TIFF signature before library access. Refuse compressed or HTML response.
    sig=f.read(16);f.seek(0)
    r['header_hex']=sig.hex()
    assert sig[:4] in (b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+'),'not TIFF'
    with tifffile.TiffFile(f) as t:
        r['is_bigtiff']=t.is_bigtiff
        r['first_page']=page_info(t.pages[0])
        r['status']='PUBLIC_GEOTIFF_HEADER_ACQUIRED'
        r['pages_probe']=[]
        # Limited page probe, no arrays or pixels.
        for i in range(1,5):
            try:q=t.pages[i];r['pages_probe'].append({'index':i,'shape':list(q.shape),'is_reduced':bool(q.is_reduced)})
            except IndexError:break
        r['status']='PUBLIC_GEOTIFF_METADATA_ACQUIRED'
except Exception as e:r['error']=type(e).__name__+': '+str(e)
r['bytes_received']=sum(x.get('bytes',0) for x in r['requests'])
r['georeference_scope']='Header tags alone do not prove grid/plot crosswalk or later image overlap. No raster pixels decoded.'
(OUT/'receipt.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
print('RASTER_META='+json.dumps(r,separators=(',',':'),ensure_ascii=False))
