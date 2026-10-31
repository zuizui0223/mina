"""Audit frozen Zenodo record 17642754; no effects fit or automatic site matches."""
from pathlib import Path
import hashlib, json, math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).parent
OUT = ROOT / 'outputs/climate_penguin'
OUT.mkdir(parents=True, exist_ok=True)
f = RAW / 'Curated_lat_AllenvironTempIceProd.csv'
d = pd.read_csv(f)
d.insert(0, 'source_row_1based', np.arange(1,len(d)+1))
d['season_start_year'] = 2000+d.season.str[1:3].astype(int)
d['season_end_year'] = 2000+d.season.str[4:6].astype(int)
d['settlement_unit_status'] = 'integer_day_index_origin_unverified'
d['site_match_status'] = 'candidate_only_not_accepted'
d.to_csv(OUT/'phenology_observed_cohort.csv', index=False)
summary = d.groupby('species').agg(records=('species','size'), geographic_codes=('cam','nunique'), original_camera_codes=('colname','nunique'), canonical_camera_codes=('colname3','nunique'), first_start_year=('season_start_year','min'), last_start_year=('season_start_year','max'))
g = d.groupby(['species','cam','season_start_year']).agg(n_camera_records=('settlement','size'), n_canonical_cameras=('colname3','nunique'), settlement_min_raw=('settlement','min'), settlement_max_raw=('settlement','max'))
summary['code_species_seasons'] = g.groupby('species').size()
summary.to_csv(OUT/'phenology_species_support.csv')
g.reset_index().to_csv(OUT/'phenology_code_season_support.csv',index=False)
series = d.groupby(['species','cam']).agg(n_seasons=('season_start_year','nunique'), records=('species','size'), start=('season_start_year','min'), end=('season_start_year','max'), camera_ids=('colname3',lambda s:';'.join(sorted(set(s)))), latitude_min=('lat','min'),latitude_max=('lat','max'),longitude_min=('long','min'),longitude_max=('long','max'))
series.to_csv(OUT/'phenology_series_support.csv')
d.isna().sum().rename('missing_rows').to_csv(OUT/'phenology_missingness.csv')
m = pd.read_csv(ROOT/'outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv')
sites = m[['site_id','site_name','region','latitude','longitude']].drop_duplicates()
def km(a,b,c,e):
    a,b,c,e=map(math.radians,[a,b,c,e]);return 6371*2*math.asin(min(1,math.sqrt(math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((e-b)/2)**2)))
rows=[]
spmap={'Adelie':'ADPE','Chinstrap':'CHPE','Gentoo':'GEPE'}
for code,x in d.groupby('cam'):
    candidates=sites[sites.site_id.eq(code)]
    if candidates.empty:
        rows.append(dict(phenology_code=code,status='no_exact_code_candidate',accepted_match=False));continue
    for _,s in candidates.iterrows():
        dist=[km(a,b,s.latitude,s.longitude) for a,b in x[['lat','long']].drop_duplicates().itertuples(index=False,name=None)]
        counts=m[m.site_id.eq(s.site_id)]
        keys=set(zip(counts.species_id,counts.season))
        pairs={(spmap[r.species],r.season_start_year) for r in x.itertuples()}
        rows.append(dict(phenology_code=code,mapppd_site_id=s.site_id,mapppd_site_name=s.site_name,region=s.region,min_camera_distance_km=min(dist),max_camera_distance_km=max(dist),status='reject_code_collision' if min(dist)>10 else 'code_and_proximity_candidate_needs_name_camera_metadata',accepted_match=False,nominal_species_season_overlap=len(keys & pairs)))
cross=pd.DataFrame(rows);cross.to_csv(OUT/'phenology_mapppd_candidates.csv',index=False)
meta=json.loads((RAW/'zenodo_metadata.json').read_text())
pd.DataFrame([dict(source='Juarez Martinez et al. settlement dataset',record='17642754',version='record-specific DOI; version index 0',doi='10.5281/zenodo.17642754',publication_date=meta['metadata']['publication_date'],license=meta['metadata']['license']['id'],file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),url=meta['files'][0]['links']['self'],status='downloaded; unit origin and camera alias audit pending')]).to_csv(OUT/'phenology_source_inventory.csv',index=False)
checks={'records':len(d),'columns_original':56,'distinct_camseason':d.camseason.nunique(),'distinct_camera_original':d.colname.nunique(),'distinct_camera_canonical':d.colname3.nunique(),'geographic_codes':d.cam.nunique(),'code_species_seasons':len(g),'duplicate_species_canonicalcamera_season':int(d.duplicated(['species','colname3','season']).sum()),'full_duplicate_rows':int(d.drop(columns='source_row_1based').duplicated().sum()),'series_3plus_seasons':int((series.n_seasons>=3).sum()),'series_5plus_seasons':int((series.n_seasons>=5).sum()),'exact_code_candidates':int(cross.mapppd_site_id.notna().sum()),'rejected_code_collisions':int(cross.status.eq('reject_code_collision').sum()),'accepted_matches':0,'unconfirmed_candidate_overlap':int(cross.loc[cross.status.str.startswith('code_and'),'nominal_species_season_overlap'].sum())}
(OUT/'phenology_audit_checks.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2));print(summary.to_string())

# Independent archive: retain source-grain daily observations, never call rows birds.
noaa=RAW/'noaa/0171619/1.1/data/1-data'
inventory=pd.read_csv(OUT/'phenology_source_inventory.csv').to_dict('records')
ns=[]
for nf in sorted(noaa.glob('*-DATA.csv')):
    nd=pd.read_csv(nf)
    inventory.append(dict(source='Hinke et al. nest-level phenology',record='0171619',version='1.1',doi='10.7289/V5Z036F7',publication_date='',license='NOAA metadata: no access/use constraints; cite source',file=nf.name,bytes=nf.stat().st_size,sha256=hashlib.sha256(nf.read_bytes()).hexdigest(),url='https://www.ncei.noaa.gov/archive/accession/0171619/1.1',status='downloaded; daily records and metadata inspected'))
    row=dict(file=nf.name,rows=len(nd),rookeries=nd.ROOKERY.nunique(),species=nd['SPP' if 'SPP' in nd else 'SPECIES'].nunique())
    yr='YEAR' if 'YEAR' in nd else 'SEASON' if 'SEASON' in nd else None
    if yr:
        row['seasons']=';'.join(sorted(nd[yr].unique()))
        row['rookery_species_seasons']=len(nd[[yr,'ROOKERY','SPP']].drop_duplicates())
        row['unique_nest_seasons']=len(nd[[yr,'ROOKERY','COLONY','CAMERA','SPP','NEST']].drop_duplicates())
        nd.groupby([yr,'ROOKERY','SPP']).size().rename('source_rows').to_csv(OUT/('noaa_'+nf.name.split()[0]+'_support.csv'))
    ns.append(row)
pd.DataFrame(ns).to_csv(OUT/'noaa_phenology_archive_support.csv',index=False)
pd.DataFrame(inventory).to_csv(OUT/'phenology_source_inventory.csv',index=False)
