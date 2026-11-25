"""Descriptive additive decomposition of the already audited six-zone panel.
No independent replication, significance test, or ecological pressure estimate.
Usage: python reaggregate_three_species.py artifact.zip result.json
"""
import csv, hashlib, io, json, sys, zipfile
from pathlib import Path
from statistics import mean

PIN = '9e0a8b1684221c5874d8e23d7307d051d6fecddf0c8dfc91f0207fc1c162f781'
EARLY = (2010, 2012, 2013, 2014)
LATE = (2016, 2017, 2018, 2019, 2020, 2022, 2023, 2024)
SPECIES = ('fur', 'elephant', 'weddell')
ZONES = tuple(range(1, 7))

def run(source):
    raw = Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('audited artifact SHA256 mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        rows = list(csv.DictReader(io.StringIO(z.read('annual_zone_counts.csv').decode('utf-8'))))
    counts = {}
    for r in rows:
        key = (int(r['year']), int(r['zone']), r['species'])
        n = int(r['count'])
        if key in counts or n < 0:
            raise ValueError('duplicate key or negative count')
        counts[key] = n
    expected = {(y, z, s) for y in EARLY + LATE for z in ZONES for s in SPECIES}
    if set(counts) != expected:
        raise ValueError('fixed panel coverage mismatch')
    def contrast(early, late, zones):
        a = {s: mean(sum(counts[y,z,s] for z in zones) for y in early) for s in SPECIES}
        b = {s: mean(sum(counts[y,z,s] for z in zones) for y in late) for s in SPECIES}
        delta = {s: b[s]-a[s] for s in SPECIES}
        ea, lb = sum(a.values()), sum(b.values())
        if delta['fur'] >= 0:
            raise ValueError('offset fraction undefined without fur decline')
        return {'early_means': a, 'late_means': b, 'early_total': ea, 'late_total': lb,
                'species_changes': delta, 'combined_change_pct': 100*(lb/ea-1),
                'other_species_offset_pct': 100*(delta['elephant']+delta['weddell'])/(-delta['fur']),
                'early_shares_pct': {s:100*a[s]/ea for s in SPECIES},
                'late_shares_pct': {s:100*b[s]/lb for s in SPECIES}}
    windows = [(tuple(y for y in EARLY if y != k), LATE) for k in EARLY] + [(EARLY, tuple(y for y in LATE if y != k)) for k in LATE]
    result = {}
    for label, zones in [('island', ZONES)]+[(str(z), (z,)) for z in ZONES]:
        r=contrast(EARLY,LATE,zones)
        loo=[contrast(a,b,zones) for a,b in windows]
        for k in ('combined_change_pct','other_species_offset_pct'):
            r[k+'_leave_one_year_out_range']=[min(v[k] for v in loo),max(v[k] for v in loo)]
        result[label]=r
    return {'status':'DESCRIPTIVE_DERIVED_REAGGREGATION_ONLY','artifact_id':14917157831,'artifact_sha256':PIN,
            'early_years': EARLY,'late_years': LATE,'n_rows':len(rows),'n_islands':1,
            'same_source_as_existing_seal_zone_analysis':True,'causal_pressure_or_competition_inference':False,
            'all_six_zones_combined_count_declines_in_every_loo':all(result[str(z)]['combined_change_pct_leave_one_year_out_range'][1]<0 for z in ZONES),
            'contrasts':result}

if __name__=='__main__':
    result=run(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
