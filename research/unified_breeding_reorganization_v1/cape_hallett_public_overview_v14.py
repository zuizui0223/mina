"""Public source discovery and one bounded overview alpha-support audit; no ecological fit."""
from pathlib import Path
import json,hashlib,io,re
import numpy as np
import requests,tifffile
from PIL import Image
from rasterio.features import geometry_mask
from affine import Affine
OUT=Path('build/cape-hallett-v14'); OUT.mkdir(parents=True,exist_ok=True)
SESSION=requests.Session();SESSION.headers.update({'User-Agent':'mina-public-source-audit/1.0','Accept-Encoding':'identity'})
def digest(b):return hashlib.sha256(b).hexdigest()
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def bounded_response(method,url,cap,**kw):
    with SESSION.request(method,url,stream=True,allow_redirects=False,timeout=(12,35),**kw) as z:
        status=z.status_code
        if status!=200:return status,None,{'content_type':z.headers.get('Content-Type'),'location':z.headers.get('Location')}
        if z.headers.get('Content-Length','').isdigit() and int(z.headers['Content-Length'])>cap:raise ValueError('declared size cap')
        data=bytearray()
        for chunk in z.iter_content(65536):
            data.extend(chunk)
            if len(data)>cap:raise ValueError('response cap')
        return status,bytes(data),{'content_type':z.headers.get('Content-Type')}
def catalogue():
    url='https://antcat.antarcticanz.govt.nz/geonetwork/srv/api/search/records/_search'
    out={'status':'CATALOGUE_SEARCH_ATTEMPTED','api_doc':'https://antarcticanz.github.io/antcat_docs/qsearch.html','queries':[]}
    for i,q in enumerate(['"Cape Hallett"','Rudolph','Hallett AND vegetation']):
        rec={'query':q,'url':url}
        try:
            status,raw,headers=bounded_response('POST',url,5_000_000,json={'from':0,'size':100,'query':{'query_string':{'query':q}}})
            rec.update(http=status,headers=headers)
            if raw is not None:
                doc=json.loads(raw);hits=doc['hits']['hits'];rec.update(total=doc['hits']['total'],retrieved=len(hits),sha256=digest(raw))
                (OUT/f'antcat_{i}.json').write_bytes(raw)
                rec['records']=[]
                for h in hits:
                    s=h.get('_source',{})
                    title={k:v for k,v in s.items() if ('title' in k.lower() or k.lower() in ('uuid','id','link','linkurl','linkprotocol','resourceidentifier'))}
                    rec['records'].append({'id':h.get('_id'),'fields':title})
        except Exception as e:rec['error']=f'{type(e).__name__}: {e}'
        out['queries'].append(rec)
    u='https://cmr.earthdata.nasa.gov/search/collections.umm_json?concept_id=C1214593590-SCIOPS'
    a={'url':u}
    try:
        code,raw,headers=bounded_response('GET',u,2_000_000);a.update(http=code,headers=headers)
        if raw:
            d=json.loads(raw);(OUT/'cmr_collection.json').write_bytes(raw);a['sha256']=digest(raw);a['hits']=d.get('hits')
            a['records']=[{'meta':v.get('meta'), 'title':v.get('umm',{}).get('EntryTitle'),'related_urls':v.get('umm',{}).get('RelatedUrls')} for v in d.get('items',[])]
    except Exception as e:a['error']=f'{type(e).__name__}: {e}'
    out['cmr']=a
    save('catalogue_receipt.json',out)
    print('CATALOGUE_RECEIPT='+json.dumps(out,separators=(',',':'),ensure_ascii=False))
ROOT='https://datashare.ed.ac.uk'
UUID='814f5d65-506c-4fd4-8f3c-4b9163b0e484';SIZE=17538362940
META=ROOT+'/server/api/core/bitstreams/'+UUID;URL=META+'/content'
BLOCK=65536;CAP=16*1024*1024;MAXREQ=384
r={'status':'OVERVIEW_NOT_VERIFIED','publisher_doi':'10.7488/ds/3417','whole_tiff_md5_verified':False,'requests':[],'grid_crosswalk_verified':False,'new_ecological_fit':False}
class RangeFile(io.RawIOBase):
    def __init__(self):self.pos=0;self.cache={};self.spent=0;self.name='public_rudy_2018.tif'
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        n=offset+(0 if whence==0 else self.pos if whence==1 else SIZE)
        if n<0:raise ValueError('negative seek')
        self.pos=n;return n
    def chunk(self,start):
        if start in self.cache:return self.cache[start]
        end=min(start+BLOCK,SIZE)-1;n=end-start+1
        if n<1 or self.spent+n>CAP or len(r['requests'])>=MAXREQ:raise ValueError('range budget')
        self.spent+=n
        with SESSION.get(URL,headers={'Range':f'bytes={start}-{end}'},stream=True,allow_redirects=False,timeout=(12,30)) as z:
            rec={'first':start,'last':end,'http':z.status_code,'content_range':z.headers.get('Content-Range'),'encoding':z.headers.get('Content-Encoding')}
            r['requests'].append(rec)
            if z.status_code!=206:raise ValueError('range not honored; no body read')
            if rec['content_range']!=f'bytes {start}-{end}/{SIZE}' or rec['encoding'] not in (None,'identity'):raise ValueError('range integrity')
            raw=bytearray()
            for c in z.iter_content(65536):
                raw.extend(c)
                if len(raw)>n:raise ValueError('range overrun')
            if len(raw)!=n:raise ValueError('range length')
            b=bytes(raw);rec.update(bytes=n,sha256=digest(b))
        self.cache[start]=b
        return b
    def read(self,n=-1):
        if n<0 or n>CAP:raise ValueError('unbounded/oversized read')
        end=min(SIZE,self.pos+n);out=bytearray()
        while self.pos<end:
            a=(self.pos//BLOCK)*BLOCK;b=self.chunk(a);k=min(end-self.pos,len(b)-(self.pos-a))
            if k<=0:raise ValueError('bad block')
            out.extend(b[self.pos-a:self.pos-a+k]);self.pos+=k
        return bytes(out)
    def readinto(self,b):d=self.read(len(b));b[:len(d)]=d;return len(d)
def overview():
    try:
        code,raw,_=bounded_response('GET',META,250000);assert code==200
        d=json.loads(raw);assert d['uuid']==UUID and d['sizeBytes']==SIZE and d['checkSum']['value']=='5375a61824f97d927c19ec3bbb5f6619'
        r['publisher']={k:d[k] for k in ['uuid','name','sizeBytes','checkSum']}
        f=RangeFile()
        with tifffile.TiffFile(f) as t:
            p=t.pages[0];h,w,bands=p.shape;assert (h,w,bands)==(99517,85323,4)
            g=p.geotiff_tags;assert g['GeographicTypeGeoKey']==4326 and g['GTRasterTypeGeoKey']==1
            sx,sy,_=map(float,p.tags[33550].value);i,j,k,west,north,z=map(float,p.tags[33922].value);assert (i,j,k)==(0,0,0)
            base_affine=Affine(sx,0,west,0,-sy,north)
            chosen=None;r['pages']=[]
            for j in range(1,10):
                try:q=t.pages[j]
                except IndexError:break
                sh=list(q.shape);r['pages'].append({'index':j,'shape':sh,'reduced':bool(q.is_reduced)})
                if max(sh[:2])<=2048:
                    if max(sh[:2])>=1024 and q.is_reduced and len(sh)==3 and sh[2]==4 and np.prod(sh[:2])<=4_000_000 and q.dtype==np.uint8 and abs(sh[1]/sh[0]-w/h)<.002:chosen=(j,q)
                    break
            if chosen is None:raise ValueError('pre-fixed overview not present')
            j,q=chosen;oh,ow,ob=q.shape
            ex=[int(x) for x in q.extrasamples];p_ex=[int(x) for x in p.extrasamples]
            r['chosen']={'index':j,'shape':list(q.shape),'extrasamples':ex,'base_extrasamples':p_ex,'tilewidth':q.tilewidth,'tilelength':q.tilelength,'compression':str(q.compression)}
            if ex not in ([1],[2]) or p_ex!=ex:raise ValueError('no explicit common alpha sample; no inferred validity')
            # Reconstruct full-field reduced pixel transform; use actual reduced tags if present.
            tr=base_affine*Affine.scale(w/ow,h/oh);r['overview_transform_source']='base extent scaled by exact reduced dimensions (nominal)'
            if 33550 in q.tags and 33922 in q.tags:
                a,b,_=map(float,q.tags[33550].value);x,y,zz,lon,lat,v=map(float,q.tags[33922].value)
                if (x,y,zz)!=(0,0,0):raise ValueError('overview tiepoint offset')
                gq=q.geotiff_tags
                if gq and gq.get('GeographicTypeGeoKey',4326)!=4326:raise ValueError('overview CRS mismatch')
                qtr=Affine(a,0,lon,0,-b,lat)
                if max(abs(qtr.c-tr.c),abs(qtr.f-tr.f),abs((qtr.a-tr.a)*ow),abs((qtr.e-tr.e)*oh))>max(tr.a,abs(tr.e))*2:raise ValueError('overview extent mismatch')
                tr=qtr;r['overview_transform_source']='reduced page tags checked against base extent'
            r['overview_transform']=list(tr)
            # Decode only selected reduced page, no whole-res pixels. Strict byte cap at file handle.
            a=q.asarray(maxworkers=1)
            assert a.shape==(oh,ow,4) and a.dtype==np.uint8
            r['pixel_decoding']='ONE_REDUCED_PAGE'
            alpha=a[:,:,3];r['alpha_histogram']={str(int(k)):int(v) for k,v in zip(*np.unique(alpha,return_counts=True))}
            zone=[(170+14/60+4.012/3600,-(72+19/60+11.219/3600)),(170+13/60+58.341/3600,-(72+19/60+10.43/3600)),(170+13/60+51.901/3600,-(72+19/60+14.479/3600)),(170+13/60+57.338/3600,-(72+19/60+15.299/3600))]
            mask=geometry_mask([{'type':'Polygon','coordinates':[zone+[zone[0]]]}],out_shape=(oh,ow),transform=tr,invert=True,all_touched=False)
            n=int(mask.sum());assert n>0
            r['alpha_support']={'image_pixels':int(alpha.size),'image_alpha_positive':int((alpha>0).sum()),'zone_center_pixels_inside_rectangle':n,'zone_alpha_positive':int(((alpha>0)&mask).sum()),'zone_alpha_opaque':int(((alpha==255)&mask).sum()),'zone_alpha_positive_fraction_within_rectangle':float((alpha[mask]>0).mean()),'zone_alpha_opaque_fraction_within_rectangle':float((alpha[mask]==255).mean())}
            # Preview is actual publicly licensed raster, not reconstructed grid or animal detections.
            im=Image.fromarray(a,mode='RGBA')
            im.save(OUT/'public_2018_overview.png')
            Image.fromarray((mask.astype(np.uint8)*255),mode='L').save(OUT/'official_zone_center_mask.png')
            r['preview_sha256']=digest((OUT/'public_2018_overview.png').read_bytes())
            r['status']='PUBLIC_OVERVIEW_ALPHA_SUPPORT_MEASURED'
    except Exception as e:r['error']=f'{type(e).__name__}: {e}'
    r['bytes_received']=sum(q.get('bytes',0) for q in r['requests'])
    r['limits']='2018 reduced-image alpha support only; alpha is not a snow/plant/animal classifier. No original grid transform, no exact animal positions, no later-image coverage or temporal effect.'
    save('overview_receipt.json',r)
    print('OVERVIEW_SUMMARY='+json.dumps({k:v for k,v in r.items() if k!='requests'},separators=(',',':')))
if __name__=='__main__':
    catalogue();overview()
