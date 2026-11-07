"""Regional grid SWE associations, explicitly stratified by land support."""
from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/september_snow_v1'


def main():
    snow_path=OUT/'september_summary.csv';raw_path=ROOT/'outputs/climate_penguin/behavior_ocean_join.csv'
    snow=pd.read_csv(snow_path);raw=pd.read_csv(raw_path)
    assert snow.complete.all() and len(snow)==1166
    snow=snow.rename(columns={'year':'season_start_year','september_00utc_mean_swe_m':'x'})
    joined=raw.merge(snow,on=['location_id','season_start_year'],how='left',validate='many_to_one')
    assert len(joined)==len(raw)
    rows=[];points=[]
    for scope in ['all_source_labels','appendix_consistent']:
        base=joined if scope=='all_source_labels' else joined[joined.appendix_range_consistent.eq(True)]
        for label,mask in [('all_grids',base.land_fraction.notna()),('land_above_03',base.land_fraction.gt(.3)),('land_at_least_05',base.land_fraction.ge(.5))]:
            eligible=base[mask].dropna(subset=['x','settlement'])
            for species in sorted(raw.species.unique()):
                d=eligible[eligible.species==species].copy()
                d['grid_id']=d.grid_lat.astype(str)+','+d.grid_lon.astype(str)
                a=d.groupby(['cam','season_start_year'],as_index=False).agg(x=('x','mean'),y=('settlement','mean'),
                    minimum_land_fraction=('land_fraction','min'),source_rows=('source_row_1based',lambda s:'|'.join(map(str,sorted(s)))),
                    grid_ids=('grid_id',lambda s:'|'.join(sorted(set(s)))))
                a=a.assign(scope=scope,land_support=label,species=species);points.append(a)
                for mode in ['site','site_year']:
                    rec=dict(scope=scope,land_support=label,species=species,mode=mode,n=len(a),sites=a.cam.nunique(),
                        years=a.season_start_year.nunique(),unique_grid_cells=len(d[['grid_lat','grid_lon']].drop_duplicates()),partial_r=np.nan,status='insufficient_support')
                    if len(a)>2:
                        z=pd.get_dummies(a.cam,dtype=float).to_numpy()
                        if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.season_start_year,drop_first=True,dtype=float)])
                        v=a[['x','y']].to_numpy();res=v-z@np.linalg.lstsq(z,v,rcond=None)[0]
                        rec['residual_df']=len(a)-np.linalg.matrix_rank(z)-1
                        if rec['residual_df']>0 and np.min((res*res).sum(axis=0))>1e-12:
                            rec.update(partial_r=float(np.corrcoef(res.T)[0,1]),status='regional_association_only')
                    rows.append(rec)
    pd.DataFrame(rows).to_csv(OUT/'regional_correlations.csv',index=False)
    pd.concat(points,ignore_index=True).to_csv(OUT/'regional_cohort.csv',index=False)
    (OUT/'association_validation.json').write_text(json.dumps(dict(status='descriptive_regional_context_only',
        comparisons=len(rows),input_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [snow_path,raw_path]},
        limits=['SWE includes model snow/ice representation, not validated snow on nesting ground',
        'Land-support filters change populations; differences are not adjustment effects',
        'Shared grids and limited sites; no p-values or causal claims','Daily 00 UTC sample, not hourly mean']),indent=2)+'\n')
    print(pd.DataFrame(rows).query("scope=='all_source_labels'").to_string(index=False))


if __name__=='__main__':main()
