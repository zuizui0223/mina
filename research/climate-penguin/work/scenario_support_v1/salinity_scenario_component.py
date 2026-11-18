"""Salt-only conditional component, holding other fitted environments fixed.

Not a complete biological forecast: future water temperature is not supplied.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/salinity_scenario_component_v1'
PATHS = {
    'future': 'scenario_support_v1/observed_range_audit.csv',
    'baseline': 'scenario_support_v1/recent_comparison/overlap_site_levels.csv',
    'coefficients': 'salinity_sensitivity_v1/specifications.csv',
    'year_delete': 'salinity_sensitivity_v1/year_deletions.csv',
    'site_delete': 'salinity_site_influence_v1/site_deletions.csv',
}


def main():
    OUT.mkdir(exist_ok=True)
    tables = {k: pd.read_csv(ROOT/'outputs'/p) for k, p in PATHS.items()}
    f = tables['future'].query("variable_id == 'sos'").copy()
    b = tables['baseline'].query("variable_id == 'sos'").rename(
        columns={'scenario_branch':'experiment_id', 'model_mean':'matched_model_baseline',
                 'observed_mean':'matched_observed_mean'})
    keys = ['scope','species','cam','source_id','member_id','variable_id','experiment_id']
    j = f.merge(b[keys+['matched_model_baseline','matched_observed_mean','n_years',
                        'first_year','last_year']], on=keys, validate='many_to_one')
    assert len(j) == len(f)
    assert np.allclose(j.observed_mean, j.matched_observed_mean, atol=1e-10, rtol=0)
    assert (j.observed_years == j.n_years).all()
    assert (j.first_observed_year == j.first_year).all()
    assert (j.last_observed_year == j.last_year).all()
    j['matched_delta_salt'] = j.future_model_mean-j.matched_model_baseline
    j['additive_future_salt'] = j.observed_mean+j.matched_delta_salt
    j['outside_site_observed_range'] = ~j.additive_future_salt.between(j.observed_min,j.observed_max)
    j['outside_species_observed_range'] = ~j.additive_future_salt.between(j.species_observed_min,j.species_observed_max)
    j.to_csv(OUT/'matched_salt_changes.csv', index=False)
    coef = tables['coefficients'].query("controls == 'ice_water_air'")
    parts = j.merge(coef[['scope','species','mode','coefficient_per_01']],
                    on=['scope','species'], validate='many_to_many')
    assert len(parts) == 2*len(j)
    parts['salt_only_index_component'] = parts.matched_delta_salt/0.1*parts.coefficient_per_01
    parts.to_csv(OUT/'site_components.csv', index=False)
    group = ['scope','species','mode','source_id','member_id','experiment_id','period']
    records = []
    for key, a in parts.groupby(group):
        assert not a.cam.duplicated().any()
        rec = dict(zip(group,key))
        delta = a.matched_delta_salt.mean()
        beta = a.coefficient_per_01.iloc[0]
        assert a.coefficient_per_01.nunique() == 1
        value = a.salt_only_index_component.mean()
        assert np.isclose(value,delta/0.1*beta, atol=1e-10)
        rec.update(sites=len(a),mean_delta_salt=delta,coefficient_per_01=beta,
                   mean_salt_only_component=value,
                   outside_site_range=int(a.outside_site_observed_range.sum()),
                   outside_species_range=int(a.outside_species_observed_range.sum()))
        for label in ['site','year']:
            d = tables[label+'_delete']
            q = d[(d.scope==rec['scope']) & (d.species==rec['species']) &
                  (d['mode']==rec['mode']) & (d.controls=='ice_water_air')]
            assert len(q)>0
            # Hold the target sites and climate changes fixed; vary coefficients only.
            shifts = q.coefficient_per_01.to_numpy()*delta/0.1
            rec[label+'_coefficient_delete_min']=float(shifts.min())
            rec[label+'_coefficient_delete_max']=float(shifts.max())
        records.append(rec)
    summary = pd.DataFrame(records)
    assert len(summary)==144
    summary.to_csv(OUT/'summary.csv', index=False)
    (OUT/'validation.json').write_text(json.dumps({
        'status':'passed_with_interpretation_limits','matched_site_scenarios':len(j),
        'site_components':len(parts),'scenario_summaries':len(summary),
        'input_sha256':{p:hashlib.sha256((ROOT/'outputs'/p).read_bytes()).hexdigest() for p in PATHS.values()},
        'limits':['Salt-only component holds water temperature, air temperature and ice fixed',
                  'Never add this to the previous two-variable model coefficients',
                  'Coefficient deletion ranges are not confidence or prediction intervals',
                  'Additive change is not validated bias correction; shared coarse cells remain',
                  'Index origin unresolved; values are not days'],
    },indent=2)+'\n',encoding='utf-8')
    print(summary.query("scope=='all_source_labels' and experiment_id=='ssp585' and period=='2081-2100'")
          [['species','mode','source_id','mean_delta_salt','mean_salt_only_component',
            'year_coefficient_delete_min','year_coefficient_delete_max','outside_site_range','sites']].to_string(index=False))


if __name__=='__main__':
    main()
