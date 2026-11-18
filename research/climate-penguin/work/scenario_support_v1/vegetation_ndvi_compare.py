"""Rebuild daily NDVI from saved DN with native-checked flagged offsets."""
from pathlib import Path
import itertools,json,hashlib,warnings
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/vegetation_annual_ndvi_v1';SUP=ROOT/'outputs/vegetation_annual_pixels_v1';CHECK=OUT/'checked_arrays';CHECK.mkdir(exist_ok=True)
s=pd.read_csv(OUT/'annual_support.csv');native=pd.read_csv(OUT/'offset_native_checks.csv');decisions=[]
for scene,g in native.groupby('scene_id'):
 action='unresolved'
 if len(g)==2 and g.status.eq('ok').all() and g.valid_pixels.ge(100).all():
  if g.difference1000_pixels.eq(g.valid_pixels).all():action='already_applied_use_zero'
  elif g.equal_pixels.eq(g.valid_pixels).all():action='not_applied_use_asset_offset'
 decisions.append(dict(scene_id=scene,decision=action))
dec=pd.DataFrame(decisions);dec.to_csv(OUT/'offset_decisions.csv',index=False);lookup=dec.set_index('scene_id').decision.to_dict()
rows=[]
for r in s.itertuples():
 meta=json.loads((OUT/f'{r.site_id}_{r.image_year}.json').read_text());path=OUT/r.array_file;assert hashlib.sha256(path.read_bytes()).hexdigest()==r.array_sha256
 with np.load(path) as a:raw=a['raw_bands'];ids=a['scene_ids']
 with np.load(SUP/'pixels'/f'{r.site_id}_{r.image_year}.npz') as a:mask={d:m for d,m in zip(a['dates'],a['land'])}
 records={v['scene_id']:v for v in meta['records'] if v['status']=='ok'};bydate={};excluded=[]
 for scene,bands in zip(ids,raw):
  rec=records[str(scene)];action=lookup.get(str(scene))
  if action=='unresolved':excluded.append(str(scene));continue
  red,nir,scl=bands;reflect=[]
  for band,values in [('red',red),('nir',nir)]:
   bm=rec['bands'][band];offset=0 if action=='already_applied_use_zero' else bm['used_offset'];reflect.append(values*bm['scale']+offset)
  red,nir=reflect;valid=mask[rec['date']]&np.isin(scl,[4,5])&np.isfinite(red)&np.isfinite(nir)&(red>0)&(nir>0)
  nd=np.full((50,50),np.nan);nd[valid]=(nir[valid]-red[valid])/(nir[valid]+red[valid]);assert np.abs(nd[valid]).max(initial=0)<=1
  bydate.setdefault(rec['date'],[]).append(nd)
 dates=sorted(bydate)
 with warnings.catch_warnings():
  warnings.simplefilter('ignore',RuntimeWarning)
  daily=np.stack([np.nanmedian(np.stack(bydate[d]),axis=0) for d in dates]) if dates else np.full((0,50,50),np.nan)
  n=np.isfinite(daily).sum(axis=0)
  median=np.nanmedian(daily,axis=0) if dates else np.full((50,50),np.nan)
  spread=np.nanquantile(daily,.75,axis=0)-np.nanquantile(daily,.25,axis=0) if dates else np.full((50,50),np.nan)
 median[n<2]=np.nan;spread[n<2]=np.nan
 out=CHECK/f'{r.site_id}_{r.image_year}.npz';np.savez_compressed(out,dates=np.array(dates),daily_ndvi=daily,annual_median=median,daily_iqr=spread,valid_dates=n)
 rows.append(dict(site_id=r.site_id,image_year=r.image_year,pixels_two_dates=int((n>=2).sum()),successful_dates=len(dates),read_errors=r.errors,excluded_offset_scenes=len(excluded),checked_file='checked_arrays/'+out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest()))
a=pd.DataFrame(rows);a.to_csv(OUT/'checked_support.csv',index=False)
pairs=[]
for site,g in a.groupby('site_id'):
 for l,r in itertools.combinations(list(g.itertuples()),2):
  if l.read_errors or r.read_errors or l.excluded_offset_scenes or r.excluded_offset_scenes:continue
  with np.load(OUT/l.checked_file) as left,np.load(OUT/r.checked_file) as right:
   v=left['annual_median'];w=right['annual_median'];common=np.isfinite(v)&np.isfinite(w)
   if not common.any():continue
   delta=w[common]-v[common]
   pairs.append(dict(site_id=site,first_year=l.image_year,last_year=r.image_year,common_pixels=int(common.sum()),median_pixel_ndvi_change=float(np.median(delta)),mean_pixel_ndvi_change=float(delta.mean()),spatial_difference_q25=float(np.quantile(delta,.25)),spatial_difference_q75=float(np.quantile(delta,.75)),first_within_month_iqr_median=float(np.median(left['daily_iqr'][common])),last_within_month_iqr_median=float(np.median(right['daily_iqr'][common])),first_scene_date_range=';'.join([min(left['dates']),max(left['dates'])]),last_scene_date_range=';'.join([min(right['dates']),max(right['dates'])])))
pd.DataFrame(pairs).to_csv(OUT/'same_pixel_changes.csv',index=False)
print(dec.to_string(index=False));print(pd.DataFrame(pairs).query('common_pixels >= 100').to_string(index=False))
