"""Same-row current versus previous September associations, no causal lag claim."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'outputs/climate_penguin'
OUT=ROOT/'outputs/previous_september_v1'


def correlation(a,mode,extra=None):
    z=pd.get_dummies(a.cam,dtype=float).to_numpy()
    if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.season_start_year,drop_first=True,dtype=float)])
    if extra is not None:z=np.column_stack([z,a[extra]])
    v=a[['x','y']].to_numpy();r=v-z@np.linalg.lstsq(z,v,rcond=None)[0]
    if np.min((r*r).sum(axis=0))<1e-10:return np.nan
    return float(np.corrcoef(r.T)[0,1])


def main():
    OUT.mkdir(exist_ok=True)
    paths=[SRC/'behavior_ocean_join.csv',SRC/'ocean_monthly_2011_2021.csv']
    raw=pd.read_csv(paths[0]);o=pd.read_csv(paths[1]);o=o[o.month==9].copy()
    ocean=['surface_salinity','surface_potential_temperature_c']
    o.loc[~o.grid_within_25km,ocean]=np.nan
    env=o[['location_id','year']+ocean]
    ice=[]
    for span in ['1991_2010','2011_2020']:
        path=SRC/f'daily_concentration_{span}_aug_nov.csv.gz';paths.append(path)
        d=pd.read_csv(path);d=d[(d.inner_km==0)&d.date.str[5:7].eq('09')&d.date.str[:4].astype(int).ge(2010)].copy()
        d['year']=d.date.str[:4].astype(int)
        d['valid']=(d.n_valid/d.n_ocean>=.8)&np.isfinite(d.sic_percent_mean)
        g=d.groupby(['location_id','year']).agg(sic=('sic_percent_mean','mean'),days=('date','nunique'),valid=('valid','all')).reset_index()
        g.loc[~(g.days.eq(30)&g.valid),'sic']=np.nan
        ice.append(g[['location_id','year','sic']])
    env=env.merge(pd.concat(ice),on=['location_id','year'],how='outer',validate='one_to_one')
    mapping={'sea_ice':('sic','near_sic_mean_month9'), 'salinity':('surface_salinity','ocean_m9_surface_salinity'),
             'water_temperature':('surface_potential_temperature_c','ocean_m9_surface_potential_temperature_c')}
    points=[];rows=[];support=[];deletions=[]
    for scope in ['all_source_labels','appendix_consistent']:
        base=raw if scope=='all_source_labels' else raw[raw.appendix_range_consistent.eq(True)]
        for feature,(column,current) in mapping.items():
            now=env[['location_id','year',column]].rename(columns={'year':'season_start_year',column:'recomputed_current'})
            lag=env[['location_id','year',column]].copy();lag['year']+=1
            lag=lag.rename(columns={'year':'season_start_year',column:'previous'})
            j=base.merge(now,on=['location_id','season_start_year'],how='left',validate='many_to_one').merge(lag,on=['location_id','season_start_year'],how='left',validate='many_to_one')
            both=j[[current,'recomputed_current']].notna().all(axis=1)
            assert np.allclose(j.loc[both,current],j.loc[both,'recomputed_current'],atol=1e-8)
            j['current']=j[current]
            for species,a in j.groupby('species'):
                available=a[['current','settlement']].notna().all(axis=1)
                pairs=available&a.previous.notna()
                support.append(dict(scope=scope,species=species,feature=feature,source_rows=len(a),current_rows=int(available.sum()),paired_rows=int(pairs.sum()),missing_prior_rows=int((available&~pairs).sum())))
                # Aggregate only identical source rows for both environmental times.
                a=a[pairs]
                g=a.groupby(['cam','season_start_year'],as_index=False).agg(current=('current','mean'),previous=('previous','mean'),y=('settlement','mean'),source_rows=('source_row_1based',lambda x:'|'.join(map(str,sorted(x)))))
                g=g.assign(scope=scope,species=species,feature=feature);points.append(g)
                for mode in ['site','site_year']:
                    r=dict(scope=scope,species=species,feature=feature,mode=mode,n=len(g),sites=g.cam.nunique(),years=g.season_start_year.nunique(),first_year=int(g.season_start_year.min()),last_year=int(g.season_start_year.max()))
                    r['current_r']=correlation(g.assign(x=g.current),mode)
                    r['previous_r']=correlation(g.assign(x=g.previous),mode)
                    r['previous_given_current_r']=correlation(g.assign(x=g.previous),mode,'current')
                    r['current_given_previous_r']=correlation(g.assign(x=g.current),mode,'previous')
                    r['environment_serial_r']=correlation(g.assign(x=g.current,y=g.previous),mode)
                    for cluster,column in [('site','cam'),('year','season_start_year')]:
                        vals=[]
                        for value in sorted(g[column].unique()):
                            sub=g[g[column]!=value]
                            v=correlation(sub.assign(x=sub.previous),mode,'current')
                            deletions.append(dict(scope=scope,species=species,feature=feature,mode=mode,cluster=cluster,deleted=str(value),previous_given_current_r=v))
                            vals.append(v)
                        r[cluster+'_delete_min']=float(np.nanmin(vals));r[cluster+'_delete_max']=float(np.nanmax(vals))
                    rows.append(r)
    t=pd.DataFrame(rows);assert len(t)==36
    t.to_csv(OUT/'correlations.csv',index=False)
    pd.concat(points,ignore_index=True).to_csv(OUT/'paired_cohort.csv',index=False)
    pd.DataFrame(support).to_csv(OUT/'coverage.csv',index=False)
    pd.DataFrame(deletions).to_csv(OUT/'lag_deletions.csv',index=False)
    (OUT/'validation.json').write_text(json.dumps(dict(status='descriptive_lag_associations',comparisons=36,
        inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        limits=['No significance or selection claim','Previous-year correlation not carryover causality',
                'Lag pair availability changes cohort; current comparisons use identical source rows',
                'Source season labels retained; settlement calendar origin unresolved']),indent=2)+'\n')
    print(t.query("scope=='all_source_labels'").to_string(index=False))


if __name__=='__main__':main()
