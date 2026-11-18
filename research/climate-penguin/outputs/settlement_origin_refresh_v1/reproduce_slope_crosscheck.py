"""Compare raw public settlement values with published Appendix S3.3 slopes."""
from pathlib import Path
import argparse
import hashlib
import json
import unicodedata
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--source-dir', type=Path, required=True)
args = parser.parse_args()
out = Path(__file__).resolve().parent
csv = args.source_dir / 'Curated_lat_AllenvironTempIceProd.csv'
supp = args.source_dir / 'JANE-95-455-s003.txt'
data = pd.read_csv(csv)
assert data.season.str.fullmatch(r's\d{2}-\d{2}').all()
data['year'] = data.season.str[1:3].astype(int) + 2000
def normal(value):
    return ''.join(x for x in unicodedata.normalize('NFKD', value)
                   if not unicodedata.combining(x)).lower()
data['sp'] = data.species.map(normal)
lines = supp.read_text(encoding='utf-8').splitlines()
rows = []
for i, colony in enumerate(lines):
    if colony not in set(data.cam) or i + 4 >= len(lines):
        continue
    try:
        count = int(lines[i + 2])
        slope = float(lines[i + 4])
    except ValueError:
        continue
    group = data[(data.cam == colony) & (data.sp == normal(lines[i + 1]))]
    # Raw camera rows, no camera/site averaging; centered OLS with intercept.
    x = group.year.to_numpy(dtype=float)
    y = group.settlement.to_numpy(dtype=float)
    x -= x.mean()
    fitted = float(x @ (y - y.mean()) / (x @ x))
    rows.append(dict(cam=colony, species=lines[i + 1], source_n=count,
                     csv_n=len(group), paper_slope=slope, csv_slope=fitted,
                     matches=abs(slope - fitted) <= 0.0005 + 1e-12))
result = pd.DataFrame(rows)
assert len(result) == 32 and result.matches.all()
assert result.source_n.eq(result.csv_n).all()
result.to_csv(out / 'source_slope_crosscheck.csv', index=False)
report = dict(source_groups=32, matching_slopes=32,
              total_camera_rows=int(result.csv_n.sum()),
              maximum_abs_rounding_difference=float(abs(result.csv_slope-result.paper_slope).max()),
              rounding_tolerance=0.0005,
              source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [csv, supp]},
              interpretation='Day-scale linkage supported; absolute origin and source-date conversion not recovered')
(out / 'slope_validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
