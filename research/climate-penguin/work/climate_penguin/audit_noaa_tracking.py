from pathlib import Path
import hashlib, json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'work/climate_penguin/tracking_noaa/copa_adpe_ncei.csv'
OUT = ROOT / 'outputs/climate_penguin'
d = pd.read_csv(SOURCE)
d['timestamp'] = pd.to_datetime(d.DateGMT + ' ' + d.TimeGMT, format='%d/%m/%Y %H:%M:%S', errors='raise', utc=True)
d['year'] = d.timestamp.dt.year
d['month'] = d.timestamp.dt.month
assert d.Latitude.between(-90, 90).all() and d.Longitude.between(-180, 180).all()
assert not d.duplicated().any()
d['quality_123'] = d.ArgosQuality.astype(str).isin(['1', '2', '3'])
summary = d.groupby(['Breed Stage', 'year', 'month']).agg(
    rows=('BirdId', 'size'), birds=('BirdId', 'nunique'), quality_123_rows=('quality_123', 'sum'))
summary.to_csv(OUT / 'noaa_tracking_monthly_support.csv')
w = d[d['Breed Stage'].eq('winter')]
w.groupby('BirdId').agg(start=('timestamp', 'min'), end=('timestamp', 'max'),
    rows=('BirdId', 'size'), quality_123_rows=('quality_123', 'sum')).to_csv(OUT / 'noaa_tracking_winter_individuals.csv')
checks = dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    source_url='https://www.ncei.noaa.gov/data/oceans/archive/arc0193/0244399/1.1/data/0-data/copa_adpe_ncei.csv',
    doi='10.25921/vdt2-vr91', rows=len(d), birds=d.BirdId.nunique(),
    winter_rows=len(w), winter_birds=w.BirdId.nunique(),
    winter_september_october_rows=len(w[w.month.isin([9, 10])]),
    winter_2011_2020_rows=len(w[w.year.between(2011, 2020)]),
    return_direction_calibration_eligible=False,
    exact_duplicate_rows=int(d.duplicated().sum()),
    raw_retained=True, quality_filter_applied_to_raw=False)
(OUT / 'noaa_tracking_checks.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps(checks, indent=2))
