#!/usr/bin/env python3
"""Audit source 2017–2023 Plantarctica positive-vegetation x penguin census by unique colony.
Exploratory cross-sectional analysis only; no causal guano, greening or occupancy.
"""
import csv, hashlib, io, json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'outputs/vegetation_response_v1/site_species_cohort.csv'
OUT=Path(__file__).resolve().parent
EXPECTED_BLOB='23fea5988889303ecdc16f4b5309073cf38e366a'
def pearson(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    return float(np.corrcoef(a,b)[0,1]) if len(a)>2 and np.std(a)>1e-12 and np.std(b)>1e-12 else None
def region_center(df,cols):
    return {col:df[col]-df.groupby('region')[col].transform('mean') for col in cols}
def fit(df,xname,extra=True):
    y=df['log_mapped_area'].to_numpy(float)
    x=[np.ones(len(df)),df[xname].to_numpy(float)]
    names=['intercept',xname]
    for reg in sorted(df.region.unique())[1:]:
        names.append('region_'+reg)
        x.append((df.region==reg).to_numpy(float))
    if extra:
        for var in ['south_lat','log_max_seasons','n_recorded_species']:
            names.append(var); x.append(df[var].to_numpy(float))
    A=np.stack(x,axis=1)
    rank=int(np.linalg.matrix_rank(A))
    if rank<len(names):return {'n':len(df),'rank':rank,'nterms':len(names),'valid':False}
    beta=np.linalg.lstsq(A,y,rcond=None)[0]
    return {'n':len(df),'rank':rank,'nterms':len(names),'valid':True,'beta_size':float(beta[1]),
            'r2':float(1-((y-A@beta)**2).sum()/((y-y.mean())**2).sum())}
def main():
    raw=SRC.read_bytes()
    sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()
    assert sha==EXPECTED_BLOB,(sha,EXPECTED_BLOB)
    d=pd.read_csv(io.BytesIO(raw))
    assert len(d)==246 and d.site_id.nunique()==222
    assert d.positive_mapped_detection.sum()==197
    assert d.loc[d.positive_mapped_detection,'site_id'].nunique()==173
    assert (d.mapped_terrestrial_union_area_2km_m2>=0).all()
    assert not d.duplicated(['site_id','species_id']).any()
    assert (d.observed_seasons>0).all()
    items=[]
    for sid,g in d.groupby('site_id'):
        for col in ['mapped_terrestrial_union_area_2km_m2','region','latitude','longitude']:
            assert g[col].nunique()==1,(sid,col)
        area=float(g.mapped_terrestrial_union_area_2km_m2.iloc[0])
        med=g.count_median.to_numpy(float)
        methods=set(';'.join(g.count_methods.astype(str)).split(';'))
        items.append({
            'site_id':sid,'region':g.region.iloc[0], 'latitude':float(g.latitude.iloc[0]),
            'longitude':float(g.longitude.iloc[0]),'south_lat':-float(g.latitude.iloc[0]),
            'mapped_area_m2':area,'log_mapped_area':float(np.log1p(area)),
            'positive_mapped_detection':bool(area>0),'n_recorded_species':int(len(g)),
            'species_recorded':';'.join(sorted(g.species_id.astype(str))),
            'has_gentoo_record':bool((g.species_id=='GEPE').any()),
            'has_adelie_record':bool((g.species_id=='ADPE').any()),
            'has_chinstrap_record':bool((g.species_id=='CHPE').any()),
            'max_species_median_nests':float(np.max(med)),
            'sum_species_medians_not_simultaneous':float(np.sum(med)),
            'log_max_nests':float(np.log1p(np.max(med))),
            'log_sum_medians_not_simultaneous':float(np.log1p(np.sum(med))),
            'max_observed_seasons':int(g.observed_seasons.max()),
            'log_max_seasons':float(np.log1p(g.observed_seasons.max())),
            'n_source_census_seasons_sum_species':int(g.observed_seasons.sum()),
            'n_distinct_count_methods_in_site':len(methods),
            'source_year_min':int(g.first_observed_season.min()),
            'source_year_max':int(g.last_observed_season.max()),
            'note':'Mapped area detected in one 2017–2023 composite; nest medians are species-specific and generally non-synchronous'
        })
    site=pd.DataFrame(items).sort_values('site_id')
    assert len(site)==222 and site.positive_mapped_detection.sum()==173
    site.to_csv(OUT/'original_222_unique_sites_static_vegetation_vs_counts.csv',index=False)
    positive=site[site.positive_mapped_detection].copy()
    def info(frame,name):
        v=region_center(frame,['log_mapped_area','log_max_nests','log_sum_medians_not_simultaneous','south_lat'])
        return {'cohort':name,'sites':len(frame),'regions':int(frame.region.nunique()),
                'r_raw_mapped_area_vs_log_max_site_species_count':pearson(frame.log_mapped_area,frame.log_max_nests),
                'r_region_centered_mapped_area_vs_log_max_site_species_count':pearson(v['log_mapped_area'],v['log_max_nests']),
                'r_raw_mapped_area_vs_log_sum_species_medians':pearson(frame.log_mapped_area,frame.log_sum_medians_not_simultaneous),
                'r_region_centered_mapped_area_vs_log_sum_species_medians':pearson(v['log_mapped_area'],v['log_sum_medians_not_simultaneous']),
                'r_raw_mapped_area_vs_latitude':pearson(frame.log_mapped_area,frame.south_lat),
                'recorded_species_n':frame.n_recorded_species.value_counts().to_dict(),
                'OLS_log_area_response_region_FE':fit(frame,'log_max_nests',extra=False),
                'OLS_log_area_response_region_lat_observation_and_species':fit(frame,'log_max_nests',extra=True)}
    summaries=[info(positive,'positive_map_only_173_sites'),
               info(site,'all_mapped_signals_222_sites_no_detection_not_absence')]
    for s in summaries:
        s['recorded_species_n']={str(k):v for k,v in s['recorded_species_n'].items()}
    out={'source_blob_sha1':sha,'source_site_species_rows':len(d),
        'unique_site_rows':len(site),'positive_mapped_sites':len(positive),
        'mapping':'original Plantarctica 2017–2023 Vegetation+Lichen union polygons within 2km',
        'response':'one log1p positive-mapped polygon area per unique site, NOT annual vegetation change or true coverage fraction',
        'size_proxy':'max among observed focal species medians at each site; not synchronized total colony abundance',
        'limits':['No independent controls for ice-free land area, mapping detection footprint, slope, trampling or source plant class.','Identified penguin species not equal true community absence.','Non-detections are not biological zero.','Observed counts from 2017–2023 overlap the vegetation composite; cause and effect cannot be ordered.'],
        'results':summaries}
    (OUT/'original_222_sites_vegetation_reverse_source_audit.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    # input source itself is safe to distribute only subject to upstream permissions; archive for exact QA.
    (OUT/'source_246_site_species_original.csv').write_bytes(raw)
    print('GUANO_STATIC_LAND_SOURCE_QA='+json.dumps(out,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
