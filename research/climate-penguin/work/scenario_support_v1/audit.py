"""September-only projection support audit; no biological forecast or p-values.

Run with Python from any directory. Uses only versioned inputs. Coordinate weights
follow source_rows of each species-camera-year, then give observed years equal weight.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/scenario_support_v1'
OUT.mkdir(parents=True, exist_ok=True)
INPUT = ROOT / 'outputs/cmip6_projection_v1'
cohort_path = ROOT / 'outputs/relationship_response_v1/cohort.csv'
join_path = ROOT / 'outputs/climate_penguin/behavior_environment_coordinate_join.csv'
cohort = pd.read_csv(cohort_path)
raw = pd.read_csv(join_path)
assert not raw.source_row_1based.duplicated().any()
mapping = raw.set_index('source_row_1based').location_id
parts = []
paths = sorted(INPUT.glob('monthly_*.csv.gz'))
assert len(paths) == 27
for path in paths:
    d = pd.read_csv(path)
    d = d[d.month.eq(9)].copy()
    assert not d.duplicated(['source_id', 'member_id', 'variable_id', 'experiment_id', 'year', 'location_id']).any()
    assert np.isfinite(d.value).all()
    d['period'] = np.where(d.experiment_id.eq('historical'), '1995-2014',
                           np.where(d.year.le(2060), '2041-2060', '2081-2100'))
    keys = ['source_id', 'member_id', 'variable_id', 'experiment_id', 'location_id', 'period', 'units']
    z = d.groupby(keys, as_index=False).agg(mean=('value', 'mean'), n=('year', 'nunique'), first=('year','min'), last=('year','max'))
    assert z.n.eq(20).all()
    assert ((z['last'] - z['first']) == 19).all()
    parts.append(z)
climate = pd.concat(parts, ignore_index=True)
climate.to_csv(OUT / 'september_climatologies.csv', index=False)
keys = ['source_id', 'member_id', 'variable_id', 'location_id']
base = climate[climate.experiment_id.eq('historical')][keys + ['mean']].rename(columns={'mean':'historical_mean'})
future = climate[~climate.experiment_id.eq('historical')].merge(base, on=keys, validate='many_to_one')
future['delta'] = future['mean'] - future.historical_mean
future.to_csv(OUT / 'september_changes.csv', index=False)
variables = {'tas': ('airC', 1.), 'siconc': ('ice10', 10.), 'sos': ('salt01', .1)}
rows = []
for (scope, species, cam), obs in cohort.groupby(['scope', 'species', 'cam']):
    # One weight per actual original row within a year, one weight per observed year.
    weight = {}
    for ids in obs.source_rows:
        ids = [int(x) for x in str(ids).split('|')]
        locs = mapping.loc[ids]
        assert locs.notna().all()
        for loc in locs:
            weight[loc] = weight.get(loc, 0.) + 1 / len(ids) / len(obs)
    assert np.isclose(sum(weight.values()), 1.)
    for (model, member, var, experiment, period), f in future.groupby(['source_id', 'member_id', 'variable_id', 'experiment_id', 'period']):
        f = f.set_index('location_id').loc[list(weight)]
        w = np.array([weight[x] for x in f.index])
        column, scale = variables[var]
        observed = obs[column] * scale
        population = cohort[(cohort.scope == scope) & (cohort.species == species)][column] * scale
        delta = float(w @ f.delta)
        anchor = float(observed.mean())
        shifted = anchor + delta
        rows.append(dict(scope=scope, species=species, cam=cam, source_id=model, member_id=member,
                         variable_id=var, experiment_id=experiment, period=period,
                         observed_years=len(obs), first_observed_year=int(obs.year.min()), last_observed_year=int(obs.year.max()),
                         coordinate_count=len(weight), observed_mean=anchor, observed_min=observed.min(), observed_max=observed.max(),
                         species_observed_min=population.min(), species_observed_max=population.max(),
                         historical_model_mean=float(w @ f.historical_mean), future_model_mean=float(w @ f['mean']), delta=delta,
                         observed_mean_plus_delta=shifted,
                         outside_site_range=bool(shifted < observed.min() or shifted > observed.max()) if len(obs)>=3 else None,
                         outside_species_range=bool(shifted < population.min() or shifted > population.max()),
                         ice_delta_outside_physical_bounds=bool(var=='siconc' and (shifted<0 or shifted>100))))
result = pd.DataFrame(rows)
result.to_csv(OUT / 'observed_range_audit.csv', index=False)
summary = result.groupby(['scope','species','variable_id','source_id','experiment_id','period'], as_index=False).agg(
    sites=('cam','size'), outside_species_range=('outside_species_range','sum'),
    sites_with_at_least_3_years=('outside_site_range','count'), outside_site_range=('outside_site_range','sum'),
    physically_invalid_ice_shifts=('ice_delta_outside_physical_bounds','sum'))
summary.to_csv(OUT / 'support_summary.csv', index=False)
receipt = {'status':'descriptive_support_audit_not_biological_forecast', 'month':9,
           'climatology_rows':len(climate), 'delta_rows':len(future), 'audit_rows':len(result),
           'source_commit':'238449c4017501c314fc8bb9076b7199576e6970',
           'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths+[cohort_path,join_path]},
           'limitations':['1995-2014 model baseline differs from observed 2011-2020 years; additive shifts are sensitivity inputs, not bias-corrected forecasts',
           'Observed min/max is sample dependent, not a confidence interval; no hypothesis test performed',
           'Air logger, ocean reanalysis and model grid have different spatial/measurement support',
           'Marginal range overlap does not establish joint environmental support',
           'Species-camera sites and climate model cells are not independent replicates',
           'Ice values outside 0-100 are flagged, never clipped or used as physical forecasts']}
(OUT / 'validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:receipt[k] for k in ['status','climatology_rows','delta_rows','audit_rows']}))
