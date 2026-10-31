"""Align tos to frozen observed years and site/source-row weights."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/surface_temperature_projection_v1'


def main():
    paths=sorted(OUT.glob('*.csv.gz'))
    assert len(paths)==9
    for p in paths:
        meta=json.loads(p.with_suffix('').with_suffix('.json').read_text())
        assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256']
    raw=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
    assert len(raw)==30528 and np.isfinite(raw.value).all()
    assert not raw.duplicated(['source_id','member_id','experiment_id','location_id','year']).any()
    cpath=ROOT/'outputs/relationship_response_v1/cohort.csv'
    mpath=ROOT/'outputs/climate_penguin/behavior_environment_coordinate_join.csv'
    cohort=pd.read_csv(cpath);mapping=pd.read_csv(mpath)
    assert not mapping.source_row_1based.duplicated().any()
    lookup=mapping.set_index('source_row_1based').location_id
    expanded=cohort.copy()
    expanded['row']=expanded.source_rows.astype(str).str.split('|')
    expanded=expanded.explode('row')
    expanded['location_id']=expanded.row.astype(int).map(lookup)
    assert expanded.location_id.notna().all()
    keys=['scope','species','cam','source_id','member_id','experiment_id']
    records=[];annual=[]
    for (model,member),d in raw.groupby(['source_id','member_id']):
        for branch in ['ssp245','ssp585']:
            current=d[(d.experiment_id.isin(['historical',branch])) & (d.year<=2020)]
            assert not current.duplicated(['location_id','year']).any()
            joined=expanded.merge(current[['location_id','year','value']],on=['location_id','year'],validate='many_to_one')
            assert len(joined)==len(expanded)
            a=joined.groupby(['scope','species','cam','year'],as_index=False).agg(model_value=('value','mean'),observed=('waterC','first'))
            assert len(a)==len(cohort)
            a=a.assign(source_id=model,member_id=member,experiment_id=branch)
            annual.append(a)
            base=a.groupby(keys,as_index=False).agg(model_baseline=('model_value','mean'),observed_mean=('observed','mean'),
                observed_min=('observed','min'),observed_max=('observed','max'),n_years=('year','nunique'))
            for start,end in [(2041,2060),(2081,2100)]:
                future=d[(d.experiment_id==branch)&d.year.between(start,end)]
                assert (future.groupby('location_id').year.nunique()==20).all()
                values=future.groupby('location_id',as_index=False).value.mean()
                # Preserve original-row weighting within each observed camera-season,
                # then equal-year weighting within cameras, as in the frozen baseline.
                z=expanded.merge(values,on='location_id',validate='many_to_one')
                site=z.groupby(['scope','species','cam','year']).value.mean().groupby(['scope','species','cam']).mean().reset_index(name='future_model_mean')
                t=base.merge(site,on=['scope','species','cam'],validate='one_to_one')
                t['period']=f'{start}-{end}'
                t['delta_water_C']=t.future_model_mean-t.model_baseline
                t['model_minus_reanalysis_C']=t.model_baseline-t.observed_mean
                t['additive_future_water_C']=t.observed_mean+t.delta_water_C
                t['outside_site_range']=~t.additive_future_water_C.between(t.observed_min,t.observed_max)
                records.append(t)
    annual=pd.concat(annual,ignore_index=True);sites=pd.concat(records,ignore_index=True)
    assert len(annual)==1896 and len(sites)==984
    annual.to_csv(OUT/'observed_year_alignment.csv',index=False)
    sites.to_csv(OUT/'matched_site_changes.csv',index=False)
    summary=sites.groupby(['scope','species','source_id','member_id','experiment_id','period'],as_index=False).agg(
        sites=('cam','size'),mean_delta_water_C=('delta_water_C','mean'),
        mean_model_minus_reanalysis_C=('model_minus_reanalysis_C','mean'),outside_site_range=('outside_site_range','sum'))
    assert len(summary)==72
    summary.to_csv(OUT/'summary.csv',index=False)
    (OUT/'alignment_validation.json').write_text(json.dumps(dict(status='passed_environment_alignment_only',
        monthly_values=len(raw),observed_year_matches=len(annual),site_changes=len(sites),summaries=len(summary),
        inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths+[cpath,mpath]},
        limitation='tos is sea surface temperature; observed waterC is top-level potential temperature, not identical measurement definitions'),indent=2)+'\n')
    print(summary.query("scope=='all_source_labels' and experiment_id=='ssp585' and period=='2081-2100'").to_string(index=False))


if __name__=='__main__':main()
