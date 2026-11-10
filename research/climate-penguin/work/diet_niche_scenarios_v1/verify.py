"""Recompute climate deltas from compressed original extracts using csv/stdlib."""
from pathlib import Path
import argparse,csv,gzip,hashlib,json,math
import numpy as np
import pandas as pd

def run(out):
    root=Path(__file__).resolve().parents[2]
    manifest=json.loads((out/'source_manifest.json').read_text())
    for entry in manifest:assert hashlib.sha256((root/entry['file']).read_bytes()).hexdigest()==entry['sha256']
    obs=[]
    with (root/'outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            if r['site_id']=='GOPT' and r['inner_km']=='0' and 1995<=int(r['year'])<=2014:obs.append(float(r['sic_mean']))
    assert len(obs)==80;baseline=sum(obs)/80
    d=pd.read_csv(root/'outputs/niche_multiscale_v1/annual_distances.csv').query('variant=="full" and metric=="fish" and pair=="Gentoo-vs-others"').sort_values('year')
    beta=np.linalg.lstsq(np.column_stack([np.ones(9),d.sic_aug_nov]),d.distance,rcond=None)[0]
    rows=pd.read_csv(out/'conditional_scenarios.csv');monthly={}
    for r in rows.itertuples():
        for exp in ['historical',r.scenario]:
            key=(r.model,r.member,exp)
            if key in monthly:continue
            p=root/f'outputs/cmip6_projection_v1/monthly_{r.model}_{r.member}_siconc_{exp}.csv.gz'
            with gzip.open(p,'rt',newline='') as f:monthly[key]=[q for q in csv.DictReader(f) if q['location_id']=='loc020']
        lo,hi=map(int,r.period.split('-'))
        hist=[float(q['value']) for q in monthly[r.model,r.member,'historical'] if 1995<=int(q['year'])<=2014]
        future=[float(q['value']) for q in monthly[r.model,r.member,r.scenario] if lo<=int(q['year'])<=hi]
        assert len(hist)==len(future)==80
        delta=sum(future)/80-sum(hist)/80;sic=baseline+delta
        assert np.isclose(delta,r.model_delta_sic_pp) and np.isclose(sic,r.delta_adjusted_sic)
        inside=d.sic_aug_nov.min()<=sic<=d.sic_aug_nov.max()
        assert bool(r.within_observed_diet_sic_range)==inside
        if inside:assert np.isclose(beta[1]*delta,r.conditional_gap_change_ols)
        else:assert math.isnan(r.conditional_gap_change_ols)
    pred=pd.read_csv(out/'rolling_origin_predictions.csv')
    for r in pred.itertuples():
        train=d[d.year<r.year];test=d[d.year==r.year];assert len(train)==r.n_training_years
        b=np.linalg.lstsq(np.column_stack([np.ones(len(train)),train.sic_aug_nov]),train.distance,rcond=None)[0]
        assert np.isclose(train.distance.mean(),r.past_mean) and np.isclose(b[0]+b[1]*test.sic_aug_nov.iloc[0],r.ols)
    validation=dict(status='pass',source_hashes_checked=len(manifest),scenarios_independently_reconstructed=len(rows),monthly_values_per_period=80,rolling_OLS_and_baselines_checked=8,scope='raw climate deltas, interpolation gates, OLS changes and training time order; not ecological validation or global CI')
    (out/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8',newline='\n');print(json.dumps(validation))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
