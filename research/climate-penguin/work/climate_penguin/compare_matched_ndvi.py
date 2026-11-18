"""Same-pixel two-date reflectance comparison; no vegetation attribution."""
from pathlib import Path
import json,hashlib
import pandas as pd,numpy as np,rasterio
from scipy.ndimage import binary_erosion
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/climate_penguin'
pairs=pd.read_csv(OUT/'reflectance_matched_date_pairs.csv')
meta=pd.read_csv(OUT/'reflectance_offset_sensitivity.csv')
validation=pd.read_csv(OUT/'reflectance_original_pixel_validation.csv')
assert len(validation)==28 and validation.status.eq('ok').all()
assert validation.loc[validation.year.eq(2019),'equal_pixels'].eq(validation.loc[validation.year.eq(2019),'valid_pixels']).all()
assert validation.loc[validation.year.eq(2024),'difference1000_pixels'].eq(validation.loc[validation.year.eq(2024),'valid_pixels']).all()
rr,cc=np.indices((50,50));inside=((-490+cc*20)**2+(490-rr*20)**2<=500**2)
rows=[];pixelrows=[]
for pair in pairs.itertuples(index=False):
    nd=[];masks=[];hashes=[];grid=None
    for year in [2019,2024]:
        m=meta[meta.location_id.eq(pair.location_id)&meta.year.eq(year)].iloc[0]
        path=ROOT/m.raw_crop;assert hashlib.sha256(path.read_bytes()).hexdigest()==m.raw_sha256
        hashes.append(m.raw_sha256)
        with rasterio.open(path) as src:
            if grid is None:grid=(src.crs,src.transform)
            else:assert grid==(src.crs,src.transform)
            red,nir,scl=src.read()
        # Selected COGs have already removed the 2024 additive offset, verified above.
        red=red*m.red_scale;nir=nir*m.nir_scale
        with np.errstate(divide='ignore',invalid='ignore'):v=(nir-red)/(nir+red)
        mask=inside&np.isin(scl,[4,5])&np.isfinite(v)&(red>0)&(nir>0)&(nir+red>1e-6)
        assert np.all(np.abs(v[mask])<=1+1e-6)
        nd.append(v);masks.append(mask)
    common=masks[0]&masks[1];core=binary_erosion(common,structure=np.ones((3,3),bool),border_value=0)
    delta=nd[1]-nd[0]
    for name,mask in [('common_land',common),('eroded_common_land',core)]:
        v=delta[mask];row=dict(location_id=pair.location_id,site_id=pair.site_id,cohort=pair.cohort,date_gap_days=pair.date_gap_days,mask=name,pixels=int(mask.sum()),ndvi2019_median=float(np.median(nd[0][mask])) if len(v) else np.nan,ndvi2024_median=float(np.median(nd[1][mask])) if len(v) else np.nan,median_pixel_difference=float(np.median(v)) if len(v) else np.nan,mean_pixel_difference=float(v.mean()) if len(v) else np.nan,difference_q25=float(np.quantile(v,.25)) if len(v) else np.nan,difference_q75=float(np.quantile(v,.75)) if len(v) else np.nan)
        rows.append(row)
    pix=pd.DataFrame(dict(location_id=pair.location_id,site_id=pair.site_id,row=rr[common],col=cc[common],ndvi2019=nd[0][common],ndvi2024=nd[1][common],difference=delta[common],eroded_core=core[common]));pixelrows.append(pix)
r=pd.DataFrame(rows);r.to_csv(OUT/'matched_ndvi_descriptive_comparison.csv',index=False)
pd.concat(pixelrows).to_csv(OUT/'matched_ndvi_common_pixels.csv.gz',index=False,compression='gzip')
checks=dict(pairs=len(pairs),source_images=len(meta),native_band_validation_rows=len(validation),climate_attribution=False,vegetation_classification_validated=False,spatial_pixels_used_as_independent_replicates=False,
 source_sha256={f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in ['reflectance_matched_date_pairs.csv','reflectance_offset_sensitivity.csv','reflectance_original_pixel_validation.csv']})
(OUT/'matched_ndvi_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(r.to_string(index=False))
