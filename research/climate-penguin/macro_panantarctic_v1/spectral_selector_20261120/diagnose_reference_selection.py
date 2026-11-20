"""OOF comparison of reference-concordant vs other RDS positives in SAME images."""
import gzip
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.special import expit
from diagnose_grid_spectra import BANDS,PIXEL_MASK,RAD_MASK
from diagnose_fixed_failure import block_mean_intervals

ROOT=Path(__file__).parent
CACHE=ROOT/'matched_training_cache'

def main():
    original=pd.read_csv(ROOT/'source_positive_records.csv')
    reference=pd.read_csv(ROOT/'published_pixel_exact_matches.csv')
    saved=pd.read_csv(ROOT/'matched_training_heldout_scores.csv');saved=saved[saved.label.eq(1)]
    sites=pd.read_csv(ROOT/'source_sites.csv');tr=Transformer.from_crs(4326,3031,always_xy=True)
    sites['x'],sites['y']=tr.transform(sites.colony_lon.to_numpy(),sites.colony_lat.to_numpy())
    matches=pd.read_csv(ROOT/'scene_matches.csv')
    folds={x['heldout_region']:x for x in json.loads((ROOT/'matched_training_fold_models.json').read_text())}
    mapping=json.loads((ROOT/'matched_holdout_verdict.json').read_text())['shared_scene_block_map']
    threshold=json.loads((ROOT/'matched_center_frozen_model.json').read_text())['threshold']
    items={i['id']:i for p in (ROOT/'metadata_cache').glob('*.json') for i in json.loads(p.read_text())}
    frames=[];receipts=[]
    for (site,product),ref in reference.groupby(['site_id','Landsat.Product.Identifier.L1']):
        group=site+'_'+product;scene=matches.loc[matches.original_product.eq(product),'scene_id'].iloc[0]
        g=original[original.site_id.eq(site)&original['Landsat.Product.Identifier.L1'].eq(product)].copy()
        t=items[scene]['properties']['proj:transform'];st=sites[sites.site_id.eq(site)].iloc[0];cx,cy=st.x,st.y
        r0=int(np.floor((max(cy+3100,ref.northing.max()+100)-t[5])/-30))
        c0=int(np.floor((min(cx-3100,ref.easting.min()-100)-t[2])/30))
        r1=int(np.floor((min(cy-3100,ref.northing.min()-100)-t[5])/-30))
        c1=int(np.floor((max(cx+3100,ref.easting.max()+100)-t[2])/30))
        arrays={b:np.load(CACHE/(group+'_'+b+'.npy')) for b in (*BANDS,'qa_pixel','qa_radsat')}
        if any(a.shape!=(r1-r0+1,c1-c0+1) for a in arrays.values()):raise ValueError('Cached window differs')
        valid=(arrays['qa_pixel']&PIXEL_MASK)==0;valid&=(arrays['qa_radsat']&RAD_MASK)==0
        for b in BANDS:valid &= arrays[b]!=0
        v4=valid[:-1,:-1]&valid[1:,:-1]&valid[:-1,1:]&valid[1:,1:]
        cc=(g.easting.to_numpy()-t[2])/30;rr=(g.northing.to_numpy()-t[5])/-30
        if not(np.allclose(cc,np.round(cc),atol=1e-6,rtol=0) and np.allclose(rr,np.round(rr),atol=1e-6,rtol=0)):raise ValueError('Non half-grid source')
        r=np.round(rr).astype(int)-r0-1;c=np.round(cc).astype(int)-c0-1
        inside=(r>=0)&(c>=0)&(r<v4.shape[0])&(c<v4.shape[1]);good=np.zeros(len(g),dtype=bool)
        good[inside]=v4[r[inside],c[inside]]
        receipts.append(dict(site_id=site,scene_id=scene,source_rows=len(g),outside_window=int((~inside).sum()),qa_pass=int(good.sum())))
        g=g[good].copy();r=r[good];c=c[good]
        for b in BANDS:
            a=arrays[b].astype(float)*2.75e-5-.2
            avg=(a[:-1,:-1]+a[1:,:-1]+a[:-1,1:]+a[1:,1:])/4
            g[b]=avg[r,c]
        g['reference_concordant']=g.cell.isin(ref.cell);g['scene_id']=scene;g['block']=g.region.map(mapping)
        fold=folds[g.region.iloc[0]]
        g['score']=expit(((g[list(BANDS)].to_numpy()-fold['scaler_mean'])/fold['scaler_scale'])@np.array(fold['coefficients'])+fold['intercept'])
        g['recovered']=g.score.ge(threshold);frames.append(g)
    d=pd.concat(frames,ignore_index=True)
    concordant=d[d.reference_concordant]
    check=concordant.merge(saved,on=['site_id','scene_id','cell'],validate='one_to_one',suffixes=('_new','_saved'))
    if len(check)!=len(saved) or len(check)!=len(concordant):raise ValueError('Reference positive set not reproduced')
    for col in [*BANDS,'score']:
        if not np.allclose(check[col+'_new'],check[col+'_saved'],rtol=1e-12,atol=1e-12):raise ValueError('Existing values differ: '+col)
    group=d.groupby(['site_id','region','block','scene_id','reference_concordant'])
    g=group.agg(recovery=('recovered','mean'),n=('cell','size'),**{b:(b,'mean') for b in BANDS}).reset_index()
    yes=g[g.reference_concordant].drop(columns='reference_concordant');no=g[~g.reference_concordant].drop(columns='reference_concordant')
    pairs=yes.merge(no,on=['site_id','region','block','scene_id'],suffixes=('_concordant','_other'),validate='one_to_one')
    pairs['recovery_difference']=pairs.recovery_concordant-pairs.recovery_other
    for b in BANDS:pairs[b+'_difference']=pairs[b+'_concordant']-pairs[b+'_other']
    results=[]
    for minimum in [1,3]:
        q=pairs[(pairs.n_concordant>=minimum)&(pairs.n_other>=minimum)]
        cols=['recovery_concordant','recovery_other','recovery_difference']+[b+'_difference' for b in BANDS]
        s=q.groupby(['site_id','region','block'])[cols].mean().reset_index()
        out=block_mean_intervals(s,cols);out['minimum_group_rows']=minimum;out['paired_site_scenes']=len(q);out['regions']=s.region.nunique();results.append(out)
    pd.concat(results).to_csv(ROOT/'failure_reference_selection_contrasts.csv',index=False,lineterminator='\n')
    pairs.to_csv(ROOT/'failure_reference_selection_pairs.csv',index=False,lineterminator='\n')
    pd.DataFrame(receipts).to_csv(ROOT/'failure_reference_selection_receipts.csv',index=False,lineterminator='\n')
    (ROOT/'failure_reference_selection_scores.csv.gz').write_bytes(gzip.compress(d.to_csv(index=False,lineterminator='\n').encode(),mtime=0))
    print('Reproduced original OOF rows',len(check),'all same-scene QA positives',len(d))
    result=pd.concat(results);print(result[result.variable.isin(['recovery_concordant','recovery_other','recovery_difference','swir16_difference','swir22_difference'])].to_string(index=False))

if __name__=='__main__':main()
