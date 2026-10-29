"""Post-result current-mapped-land dependence diagnostic for paired species growth.

No source point snapping; no named-island independence or historical habitat claim.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,statistics,tempfile
from collections import defaultdict
from pathlib import Path

CONTINENT_FID=17692
EXACT='EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON'
SOURCE_RUN=40868828790
ROOT=Path(__file__).resolve().parent

def readcsv(path):
    with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def aggregate(rows,geo):
    sites=defaultdict(list);omitted=set()
    for r in rows:
        g=geo[r['site_id']]
        if g['category']!=EXACT or g['original_land_fid']==CONTINENT_FID:
            omitted.add(r['site_id']);continue
        sites[r['site_id']].append(float(r['delta_log_ratio_b_over_a']))
    lands=defaultdict(list);members=defaultdict(list)
    for s,v in sorted(sites.items()):
        f=geo[s]['original_land_fid'];lands[f].append(statistics.mean(v));members[f].append(s)
    means=[statistics.mean(v) for v in lands.values()]
    loo=[statistics.mean(means[:i]+means[i+1:]) for i in range(len(means))] if len(means)>=3 else []
    return dict(retained_intervals=sum(len(v) for v in sites.values()),retained_sites=len(sites),
       retained_land_features=len(lands),excluded_sites=sorted(omitted),
       same_sample_equal_site_mean=statistics.mean(statistics.mean(v) for v in sites.values()) if sites else None,
       equal_land_mean_of_site_means=statistics.mean(means) if means else None,
       leave_one_land_out_range=[min(loo),max(loo)] if loo else None,
       land_groups=[dict(source_land_fid=f,sites=members[f],site_mean_difference=statistics.mean(v)) for f,v in sorted(lands.items())],
       independent_physical_islands_verified=False,
       field_coordinate_precision_verified=False,historical_colony_geometry_measured=False,
       interval_weights='site means within current mapped land, then equal mapped-land means')

def main():
    from pyproj import Transformer
    from shapely.geometry import Point
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    pairs=readcsv(args.source_dir/'matched_species_annual_contrasts.csv')
    original=json.loads((args.source_dir/'matched_species_growth_result.json').read_text())
    raw_sites=args.source_dir/'source/sites.csv'
    digest=hashlib.sha256(raw_sites.read_bytes()).hexdigest()
    if digest!=original['source_receipts']['sites']['sha256']:raise ValueError('source registry SHA mismatch')
    ids={r['site_id'] for r in pairs};meta={r['site_id']:r for r in readcsv(raw_sites) if r['site_id'] in ids}
    if len(meta)!=len(ids):raise ValueError('unmatched source site')
    s=importlib.util.spec_from_file_location('original_land',ROOT/'audit_palmer_original_island_rock_v1.py')
    land=importlib.util.module_from_spec(s);s.loader.exec_module(land)
    transform=Transformer.from_crs('EPSG:4326','EPSG:3031',always_xy=True)
    points={sid:Point(*transform.transform(float(r['longitude']),float(r['latitude']))) for sid,r in meta.items()}
    raw=land.original_publisher_zip()
    with tempfile.TemporaryDirectory(prefix='source-matched-lands-') as temp:
        shp=land.unpack(raw,Path(temp));polygons,surfaces=land.geometry_source_candidates(shp,points)
    geo={sid:land.classify(pt,polygons) for sid,pt in points.items()}
    results={}
    for pair in ('ADPE__GEPE','CHPE__GEPE','ADPE__CHPE'):
        a,b=pair.split('__');rows=[r for r in pairs if r['species_a']==a and r['species_b']==b]
        results[pair]=aggregate(rows,geo)
    report=dict(schema=1,status='post_result_current_land_dependence_diagnostic',source_run=SOURCE_RUN,
      original_registry_sha256=digest,coast_original_sha256=hashlib.sha256(raw).hexdigest(),
      source_land_surface_counts=surfaces,n_candidate_sites=len(meta),geography=geo,effects=results,
      limits=['Current source coastline is not an observed historical colony footprint.',
              'Site centroids lack certified positional uncertainty; exact containment alone does not certify named-island independence.',
              'Near-source points stay excluded; zero map matches are not biological habitat absence.',
              'Same source sample is retained for comparing site versus land weighting.',
              'This diagnostic is post-result and not a new confirmatory climate test.'])
    (args.out/'matched_species_land_result.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('MAPPPD_MATCHED_SPECIES_LAND_RESULT='+json.dumps(report,allow_nan=False),flush=True)

if __name__=='__main__':main()
