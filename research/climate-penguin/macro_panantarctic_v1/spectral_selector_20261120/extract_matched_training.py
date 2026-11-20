"""Fixed source-matched historical SR positives and UNLABELED background candidates."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import io
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
import planetary_computer
import rasterio
from rasterio.windows import Window
from scipy.spatial import cKDTree
import requests
import threading
import time
from diagnose_grid_spectra import BANDS,PIXEL_MASK,RAD_MASK

ROOT=Path(__file__).parent
CACHE=ROOT/'matched_training_cache'

def one(key,g,sites,grids,matches,known_tree):
    site,product=key;group=site+'_'+product
    output=CACHE/(group+'_extracted.csv');receipt_path=CACHE/(group+'_receipt.json')
    if output.exists() and receipt_path.exists():return pd.read_csv(output),json.loads(receipt_path.read_text())
    scene=matches.loc[matches.original_product.eq(product),'scene_id'].iloc[0]
    st=sites[sites.site_id.eq(site)].iloc[0];fit=grids[grids.site_id.eq(site)].iloc[0]
    cx,cy=float(st.x),float(st.y)
    other=sites[~sites.site_id.eq(site)][['x','y']].to_numpy();other_tree=cKDTree(other)
    item_path=CACHE/(scene+'.json')
    if item_path.exists():item=json.loads(item_path.read_text())
    else:
        response=requests.get('https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/'+scene,timeout=50)
        response.raise_for_status();item=response.json()
        if item['id']!=scene:raise ValueError('Source scene mismatch')
        temporary=item_path.with_suffix(f'.{threading.get_ident()}.tmp')
        temporary.write_text(json.dumps(item),encoding='utf-8');temporary.replace(item_path)
    arrays={};transform=None
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='YES',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.TIF,.tif',GDAL_HTTP_TIMEOUT='60',GDAL_HTTP_MAX_RETRY='2'):
        for band in (*BANDS,'qa_pixel','qa_radsat'):
            asset=item['assets'][band]
            with rasterio.open(planetary_computer.sign(asset['href'])) as src:
                if src.crs.to_epsg()!=3031 or tuple(src.res)!=(30.,30.):raise ValueError('Unexpected native grid')
                if transform is None:
                    transform=src.transform
                    r0,c0=src.index(min(cx-3100,g.easting.min()-100),max(cy+3100,g.northing.max()+100))
                    r1,c1=src.index(max(cx+3100,g.easting.max()+100),min(cy-3100,g.northing.min()-100))
                    if r0<0 or c0<0 or r1>=src.height or c1>=src.width:raise ValueError('Window outside native image')
                    window=Window(c0,r0,c1-c0+1,r1-r0+1)
                elif src.transform!=transform:raise ValueError('Band grid mismatch')
                path=CACHE/(group+'_'+band+'.npy')
                if path.exists():a=np.load(path)
                else:a=src.read(1,window=window);np.save(path,a)
                if a.shape!=(int(window.height),int(window.width)):raise ValueError('Cache window mismatch')
                arrays[band]=a
                if band in BANDS:
                    meta=asset['raster:bands'][0]
                    if (meta['scale'],meta['offset'],meta['nodata'])!=(2.75e-5,-.2,0):raise ValueError('Scale drift')
    valid=(arrays['qa_pixel']&PIXEL_MASK)==0
    valid &= (arrays['qa_radsat']&RAD_MASK)==0
    for band in BANDS:valid &= arrays[band]!=0
    # All matched source centers lie on native grid intersections. Four equal areas.
    v4=valid[:-1,:-1]&valid[1:,:-1]&valid[:-1,1:]&valid[1:,1:]
    means={}
    for band in BANDS:
        a=arrays[band].astype(float)*2.75e-5-.2
        means[band]=(a[:-1,:-1]+a[1:,:-1]+a[:-1,1:]+a[1:,1:])/4
    def index(points):
        cc=(points[:,0]-transform.c)/30;rr=(points[:,1]-transform.f)/-30
        if not(np.allclose(cc,np.round(cc),rtol=0,atol=1e-6) and np.allclose(rr,np.round(rr),rtol=0,atol=1e-6)):
            raise ValueError('Point is not the documented half-grid center')
        return np.round(rr).astype(int)-r0-1,np.round(cc).astype(int)-c0-1
    r,c=index(g[['easting','northing']].to_numpy());keep=v4[r,c]
    positives=g.loc[keep].copy();rp,cp=r[keep],c[keep]
    receipt=dict(site_id=site,scene_id=scene,original_product=product,region=g.region.iloc[0],season=int(g.season.iloc[0]),
      original_matched_positives=len(g),positive_qa_pass=int(keep.sum()),candidate_pool={},selected_candidates={})
    if positives.empty:
        receipt['status']='NO_QA_POSITIVES';return pd.DataFrame(),receipt
    ox=round(float(fit.first_index_easting),6);oy=round(float(fit.first_index_northing),6)
    xs=ox+np.arange(np.ceil((cx-3000-ox)/30),np.floor((cx+3000-ox)/30)+1)*30
    ys=oy+np.arange(np.ceil((cy-3000-oy)/30),np.floor((cy+3000-oy)/30)+1)*30
    xx,yy=np.meshgrid(xs,ys);points=np.column_stack((xx.ravel(),yy.ravel()))
    dist=np.hypot(points[:,0]-cx,points[:,1]-cy)
    points=points[(dist>=1000)&(dist<=3000)]
    points=points[(known_tree.query(points)[0]>60)&(other_tree.query(points)[0]>1000)]
    r,c=index(points);qok=v4[r,c];points=points[qok];r=r[qok];c=c[qok]
    q=arrays['qa_pixel'][r+1,c+1]
    classes=np.where(q&(1<<5),'snow',np.where(q&(1<<7),'water','other'))
    rng=np.random.default_rng(np.random.SeedSequence([20261120,int(hashlib.sha256(group.encode()).hexdigest()[:8],16)]))
    chosen=[]
    for category in ('snow','water','other'):
        ids=np.flatnonzero(classes==category);n=min(len(ids),len(positives))
        receipt['candidate_pool'][category]=len(ids);receipt['selected_candidates'][category]=n
        if n:
            for k in rng.choice(ids,size=n,replace=False):
                rec=dict(site_id=site,scene_id=scene,region=g.region.iloc[0],season=int(g.season.iloc[0]),
                  label=0,background_class=category,cell='',easting=points[k,0],northing=points[k,1],sampling_probability=n/len(ids))
                rec.update({b:means[b][r[k],c[k]] for b in BANDS});chosen.append(rec)
    if not chosen:
        receipt['status']='NO_CANDIDATE_BACKGROUND';return pd.DataFrame(),receipt
    records=[]
    for k,(_,row) in enumerate(positives.iterrows()):
        rec=dict(site_id=site,scene_id=scene,region=row.region,season=int(row.season),label=1,background_class='source_positive',
          cell=int(row.cell),easting=row.easting,northing=row.northing,sampling_probability=1.)
        rec.update({b:means[b][rp[k],cp[k]] for b in BANDS});records.append(rec)
    records.extend(chosen);frame=pd.DataFrame(records)
    receipt['status']='PAIRED_SOURCE_CANDIDATES';frame.to_csv(output,index=False,lineterminator='\n')
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(site,scene,len(positives),len(chosen),flush=True)
    return frame,receipt

def main(phase='train',shard=0,n_shards=1):
    global CACHE
    CACHE=ROOT/('matched_training_cache' if phase=='train' else 'matched_test_cache')
    CACHE.mkdir(exist_ok=True)
    source='published_pixel_exact_matches.csv' if phase=='train' else 'matched_center_test_candidates.csv'
    d=pd.read_csv(ROOT/source)
    if not d.phase.eq(phase).all() or not d.in_final_scene_table.all():raise ValueError('Unexpected source subset')
    if not 0<=shard<n_shards:raise ValueError('Invalid shard')
    products=sorted(d['Landsat.Product.Identifier.L1'].unique())
    products=set(products[shard::n_shards])
    d=d[d['Landsat.Product.Identifier.L1'].isin(products)]
    sites=pd.read_csv(ROOT/'source_sites.csv');tr=Transformer.from_crs(4326,3031,always_xy=True)
    sites['x'],sites['y']=tr.transform(sites.colony_lon.to_numpy(),sites.colony_lat.to_numpy())
    grids=pd.read_csv(ROOT/'training_recovered_lattices.csv');matches=pd.read_csv(ROOT/'scene_matches.csv')
    source_positions=ROOT/'known_training_positive_positions.csv'
    if not source_positions.exists():source_positions=ROOT/'known_training_positive_positions.csv.gz'
    known=pd.read_csv(source_positions)[['easting','northing']].to_numpy()
    text=(ROOT/'public_grid_evidence/schwaller2013_pangaea804588.txt').read_text(encoding='utf-8')
    old=pd.read_csv(io.StringIO(text.split('*/',1)[1].lstrip()),sep='\t')[['UTM east [m]','UTM north [m]']].to_numpy()
    known_tree=cKDTree(np.vstack([known,old]))
    def safe(task):
        key,g=task
        for attempt in range(3):
            try:return one(key,g,sites,grids,matches,known_tree)
            except Exception as e:
                error=str(e).split('?')[0]
                if attempt<2:time.sleep(2**attempt)
        print('ACCESS/EXTRACTION ERROR',key[0],error,flush=True)
        return pd.DataFrame(),dict(site_id=key[0],original_product=key[1],status='ACCESS_OR_EXTRACTION_ERROR',error=error)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(safe,list(d.groupby(['site_id','Landsat.Product.Identifier.L1']))))
    frames=[x for x,r in results if not x.empty]
    prefix='matched_training' if phase=='train' else f'matched_test_shard{shard}'
    if frames:pd.concat(frames,ignore_index=True).to_csv(ROOT/(prefix+'_samples.csv'),index=False,lineterminator='\n')
    (ROOT/(prefix+'_receipts.json')).write_text(json.dumps([r for x,r in results],indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Finished',len(results),'site-scene pairs,',sum(len(x) for x in frames),'rows',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['train','test'],default='train')
    parser.add_argument('--shard',type=int,default=0);parser.add_argument('--n-shards',type=int,default=1)
    a=parser.parse_args();main(a.phase,a.shard,a.n_shards)
