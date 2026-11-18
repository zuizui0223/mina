"""Independent stdlib arithmetic verification of all September aggregates/joins."""
from pathlib import Path
import csv
import gzip
import json
import math
from collections import defaultdict
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/scenario_support_v1'
def read(path):
    with path.open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))
groups = defaultdict(list)
for path in (ROOT/'outputs/cmip6_projection_v1').glob('monthly_*.csv.gz'):
    with gzip.open(path,'rt',encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            if r['month'] != '9':
                continue
            period = '1995-2014' if r['experiment_id']=='historical' else ('2041-2060' if int(r['year'])<=2060 else '2081-2100')
            key = tuple(r[k] for k in ['source_id','member_id','variable_id','experiment_id','location_id'])+(period,)
            groups[key].append(float(r['value']))
assert all(len(v)==20 for v in groups.values())
means = {k:mean(v) for k,v in groups.items()}
for r in read(OUT/'september_climatologies.csv'):
    key = tuple(r[k] for k in ['source_id','member_id','variable_id','experiment_id','location_id','period'])
    assert math.isclose(float(r['mean']),means[key],abs_tol=1e-10)
raw = {r['source_row_1based']:r['location_id'] for r in read(ROOT/'outputs/climate_penguin/behavior_environment_coordinate_join.csv')}
cohorts = defaultdict(list)
for r in read(ROOT/'outputs/relationship_response_v1/cohort.csv'):
    cohorts[(r['scope'],r['species'],r['cam'])].append(r)
audit = read(OUT/'observed_range_audit.csv')
for r in audit:
    obs = cohorts[(r['scope'],r['species'],r['cam'])]
    values = []
    for observation in obs:
        diffs = []
        for source in observation['source_rows'].split('|'):
            location = raw[source]
            prefix = (r['source_id'],r['member_id'],r['variable_id'])
            diffs.append(means[prefix+(r['experiment_id'],location,r['period'])]-means[prefix+('historical',location,'1995-2014')])
        values.append(mean(diffs))
    assert math.isclose(mean(values),float(r['delta']),abs_tol=1e-10)
    assert math.isclose(float(r['observed_mean'])+mean(values),float(r['observed_mean_plus_delta']),abs_tol=1e-10)
result = {'passed':True,'independently_checked_climatologies':len(means),'independently_checked_coordinate_weighted_deltas':len(audit)}
(OUT/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
