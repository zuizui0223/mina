#!/usr/bin/env python3
"""Static 2017–2023 mapped vegetation versus contemporaneously observed counts.

One site/species summary is one observation. The composite map is never copied
into annual records. Non-detection remains a mapping signal, not plant absence.
All analyses here are new exploratory descriptions, not causal or trend forecasts.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[2]
AREA = 'mapped_terrestrial_union_area_2km_m2'
SPECIES = ('ADPE', 'CHPE', 'GEPE')
PERIOD = (2017, 2023)


def selected_counts(counts):
    """Keep real, unambiguous observations in the fixed composite period."""
    p = counts.loc[counts.species_id.isin(SPECIES) & counts.season.between(*PERIOD)].copy()
    if p.duplicated(['site_id', 'species_id', 'season']).any():
        raise ValueError('Repeated site/species/season: use the unambiguous count source')
    if (p['count'].dropna() < 0).any():
        raise ValueError('Negative observed count')
    p = p.loc[np.isfinite(p['count'])].copy()
    if p[['site_id', 'region', 'latitude', 'longitude']].isna().any().any():
        raise ValueError('Required geographic metadata missing')
    return p


def build_site_cohort(counts, areas):
    p = selected_counts(counts)
    if areas.duplicated('site_id').any():
        raise ValueError('Repeated map site')
    rows = []
    for (site, species), q in p.groupby(['site_id', 'species_id'], sort=True):
        q = q.sort_values('season')
        years = q.season.to_numpy(float)
        log_counts = np.log1p(q['count'].to_numpy(float))
        dx = years - years.mean()
        slope = float(dx @ (log_counts-log_counts.mean()) / (dx @ dx)) if len(q)>1 else np.nan
        rows.append(dict(site_id=site, species_id=species, site_name=q.site_name.iloc[0],
            region=q.region.iloc[0], latitude=q.latitude.iloc[0], longitude=q.longitude.iloc[0],
            observed_seasons=len(q), first_observed_season=int(years.min()), last_observed_season=int(years.max()),
            observed_year_span=int(years.max()-years.min()), observed_season_list=';'.join(str(int(y)) for y in years),
            observed_zero_seasons=int(q['count'].eq(0).sum()), count_median=float(q['count'].median()),
            log1p_count_median=float(np.log1p(q['count'].median())),
            observed_log_count_slope_per_year=slope, count_methods=';'.join(sorted(q.method.fillna('unknown').unique())),
            all_counts_ground=bool(q.method.eq('ground').all())))
    result = pd.DataFrame(rows).merge(areas[['site_id', AREA]], on='site_id', how='left', validate='many_to_one')
    result['positive_mapped_detection'] = result[AREA].gt(0)
    result['map_status'] = np.where(result[AREA].isna(), 'missing_map_summary',
        np.where(result[AREA].gt(0), 'positive_mapped_detection', 'no_mapped_polygon_absence_unresolved'))
    result['log1p_mapped_area_m2'] = np.log1p(result[AREA])
    return result


def build_matched_species(counts, areas, first, second):
    p = selected_counts(counts)
    # Only simultaneous observed site-season records enter the contrast.
    left = p.loc[p.species_id.eq(first)]
    right = p.loc[p.species_id.eq(second), ['site_id', 'season', 'count']]
    matches = left.merge(right, on=['site_id', 'season'], suffixes=('_first', '_second'), validate='one_to_one')
    rows=[]
    for site,q in matches.groupby('site_id', sort=True):
        q=q.sort_values('season')
        delta=np.log1p(q['count_second'].to_numpy(float))-np.log1p(q['count_first'].to_numpy(float))
        rows.append(dict(site_id=site, first_species=first, second_species=second,
            region=q.region.iloc[0], latitude=q.latitude.iloc[0], longitude=q.longitude.iloc[0],
            common_seasons=len(q), common_season_list=';'.join(q.season.astype(str)),
            mean_log_count_difference_second_minus_first=float(delta.mean())))
    columns=['site_id','first_species','second_species','region','latitude','longitude','common_seasons',
             'common_season_list','mean_log_count_difference_second_minus_first']
    result=pd.DataFrame(rows,columns=columns).merge(areas[['site_id',AREA]],on='site_id',how='left',validate='many_to_one')
    result['positive_mapped_detection']=result[AREA].gt(0)
    result['log1p_mapped_area_m2']=np.log1p(result[AREA])
    return result


def _demean(values, groups):
    out=values.copy()
    for group in np.unique(groups):
        idx=groups==group
        out[idx]-=out[idx].mean()
    return out


def association(x,y,groups,adjust_region):
    x=np.asarray(x,float); y=np.asarray(y,float); groups=np.asarray(groups)
    keep=np.isfinite(x)&np.isfinite(y)&pd.notna(groups)
    x=x[keep]; y=y[keep]; groups=groups[keep]
    rx=rankdata(x); ry=rankdata(y)
    if adjust_region:
        x=_demean(x,groups); y=_demean(y,groups)
        rx=_demean(rx,groups); ry=_demean(ry,groups)
    x=x-x.mean() if len(x) else x
    y=y-y.mean() if len(y) else y
    rx=rx-rx.mean() if len(rx) else rx
    ry=ry-ry.mean() if len(ry) else ry
    xx=float(x@x); yy=float(y@y); rxx=float(rx@rx); ryy=float(ry@ry)
    return dict(n=len(x), n_regions=len(np.unique(groups)),
        informative_sites=int(np.count_nonzero(np.abs(x)>1e-12)),
        slope=float(x@y/xx) if xx>1e-12 else np.nan,
        pearson_r=float(x@y/np.sqrt(xx*yy)) if xx>1e-12 and yy>1e-12 else np.nan,
        rank_r=float(rx@ry/np.sqrt(rxx*ryy)) if rxx>1e-12 and ryy>1e-12 else np.nan)


def spatial_blocks(data, threshold_km=10.):
    """Connected geographic groups; prevent treating adjacent sites as bootstrap units."""
    q=data[['site_id','latitude','longitude']].drop_duplicates().sort_values('site_id')
    if q.site_id.duplicated().any():
        raise ValueError('Inconsistent coordinates for same site')
    ids=q.site_id.tolist(); lat=np.radians(q.latitude.to_numpy(float)); lon=np.radians(q.longitude.to_numpy(float))
    parent=list(range(len(q)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]; i=parent[i]
        return i
    for i in range(len(q)):
        a=np.sin((lat[i]-lat)/2)**2+np.cos(lat[i])*np.cos(lat)*np.sin((lon[i]-lon)/2)**2
        distance=2*6371.0088*np.arcsin(np.sqrt(np.clip(a,0,1)))
        for j in np.flatnonzero(distance<=threshold_km):
            ri,rj=root(i),root(int(j))
            if ri!=rj: parent[max(ri,rj)]=min(ri,rj)
    return {site:f'geo_{root(i):04d}' for i,site in enumerate(ids)}


def result_rows(data, endpoint, cohort, species, bootstrap_reps=999):
    q=data.loc[np.isfinite(data[endpoint]) & np.isfinite(data.log1p_mapped_area_m2)].copy().reset_index(drop=True)
    x=q.log1p_mapped_area_m2.to_numpy(float); y=q[endpoint].to_numpy(float); groups=q.region.to_numpy()
    blocks=q.spatial_block.to_numpy(); unique=np.unique(blocks)
    block_indices=[np.flatnonzero(blocks==b) for b in unique]
    rng=np.random.default_rng(20261030)
    samples=[]
    if len(unique):
        for _ in range(bootstrap_reps):
            samples.append(np.concatenate([block_indices[i] for i in rng.integers(0,len(unique),len(unique))]))
    rows=[]
    for adjusted in [False,True]:
        result=association(x,y,groups,adjusted)
        boot=[association(x[idx],y[idx],groups[idx],adjusted) for idx in samples]
        row=dict(cohort=cohort,endpoint=endpoint,species=species,adjustment='region_fixed_effects' if adjusted else 'unadjusted',
                 n_spatial_blocks=len(unique),**result)
        for metric in ['slope','pearson_r','rank_r']:
            values=np.array([b[metric] for b in boot],float); values=values[np.isfinite(values)]
            lo,hi=np.percentile(values,[2.5,97.5]) if len(values) else (np.nan,np.nan)
            row[f'{metric}_bootstrap_low']=lo; row[f'{metric}_bootstrap_high']=hi
            row[f'{metric}_bootstrap_valid']=len(values)
        rows.append(row)
    return rows


def write_plot(cohort,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':9})
    fig,axs=plt.subplots(1,3,figsize=(11.4,3.7),sharey=True)
    colors={'ADPE':'#2563a6','CHPE':'#bb7022','GEPE':'#26805d'}
    for ax,species in zip(axs,SPECIES):
        q=cohort.loc[cohort.species_id.eq(species)&cohort.positive_mapped_detection&cohort.observed_log_count_slope_per_year.notna()]
        x=_demean(q.log1p_mapped_area_m2.to_numpy(float),q.region.to_numpy())
        y=_demean(q.observed_log_count_slope_per_year.to_numpy(float),q.region.to_numpy())
        two=q.observed_seasons.eq(2).to_numpy()
        ax.axhline(0,color='#ccc',lw=.8); ax.axvline(0,color='#ccc',lw=.8)
        ax.scatter(x[~two],y[~two],c=colors[species],s=34,alpha=.8,label='3+ observed seasons')
        ax.scatter(x[two],y[two],facecolors='none',edgecolors=colors[species],s=40,label='2 observed seasons')
        fit=association(x,y,q.region.to_numpy(),False)
        if len(x)>1 and np.isfinite(fit['slope']):
            xx=np.array([x.min(),x.max()]); ax.plot(xx,fit['slope']*xx,color=colors[species],lw=1.2)
        ax.set_title(f"{species}: n={len(q)}, r={fit['pearson_r']:.2f}")
        ax.set_xlabel('Within-region log(1 + mapped area, m²)')
        ax.spines[['top','right']].set_visible(False)
    axs[0].set_ylabel('Within-region log-count slope (per year)')
    axs[-1].legend(loc='best',fontsize=8,frameon=False)
    fig.suptitle('2017–2023 vegetation composite and observed breeding-count change',fontsize=12)
    fig.text(.5,.005,'Positive mapped detections only. Static map, irregular count years; descriptive association, not a vegetation trend.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,.96]); fig.savefig(path,dpi=180); plt.close(fig)


def run(out, bootstrap_reps=999):
    source=ROOT/'outputs/comparison_audit'
    count_path=source/'mapppd_unambiguous_site_seasons.csv'; area_path=source/'vegetation_2km_mapped_area.csv'
    counts=pd.read_csv(count_path); areas=pd.read_csv(area_path)
    out.mkdir(parents=True,exist_ok=True)
    cohort=build_site_cohort(counts,areas)
    blocks=spatial_blocks(cohort)
    cohort['spatial_block']=cohort.site_id.map(blocks)
    cohort.to_csv(out/'site_species_cohort.csv',index=False)
    result=[]
    endpoints=['observed_log_count_slope_per_year','log1p_count_median']
    for cohort_name,subset in [('positive_detections',cohort.loc[cohort.positive_mapped_detection]),('all_mapped_signals_sensitivity',cohort)]:
        for species in SPECIES:
            data=subset.loc[subset.species_id.eq(species)]
            for endpoint in endpoints:
                result.extend(result_rows(data,endpoint,cohort_name,species,bootstrap_reps))
    matched_frames=[]; matched_results=[]
    for first,second in itertools.combinations(SPECIES,2):
        matched=build_matched_species(counts,areas,first,second)
        matched['spatial_block']=matched.site_id.map(blocks)
        matched_frames.append(matched)
        positive=matched.loc[matched.positive_mapped_detection]
        matched_results.extend(result_rows(positive,'mean_log_count_difference_second_minus_first',
            'positive_detections_same_site_same_seasons',f'{second}_minus_{first}',bootstrap_reps))
    associations=pd.DataFrame(result); associations.to_csv(out/'associations.csv',index=False)
    matches=pd.concat(matched_frames,ignore_index=True); matches.to_csv(out/'matched_species_cohort.csv',index=False)
    pd.DataFrame(matched_results).to_csv(out/'matched_species_associations.csv',index=False)
    support=cohort.groupby(['species_id','positive_mapped_detection'],as_index=False).agg(
        site_species=('site_id','size'),observed_site_seasons=('observed_seasons','sum'),
        with_repeated_counts=('observed_seasons',lambda s:int(s.ge(2).sum())),
        with_three_or_more_counts=('observed_seasons',lambda s:int(s.ge(3).sum())))
    support.to_csv(out/'support.csv',index=False)
    # Same single census year, chosen by largest total observed site-species count,
    # provides a composition diagnostic without making static vegetation annual.
    selected=selected_counts(counts)
    year_support=selected.groupby('season').size().sort_values(ascending=False,kind='stable')
    common_year=int(year_support.index[0]); common=build_site_cohort(selected.loc[selected.season.eq(common_year)],areas)
    common['spatial_block']=common.site_id.map(blocks); common_results=[]
    for species in SPECIES:
        q=common.loc[common.species_id.eq(species)&common.positive_mapped_detection]
        common_results.extend(result_rows(q,'log1p_count_median',f'positive_detections_single_year_{common_year}',species,bootstrap_reps))
    pd.DataFrame(common_results).to_csv(out/'single_year_abundance_sensitivity.csv',index=False)
    write_plot(cohort,out/'vegetation_observed_count_change.png')
    files=[count_path,area_path,Path(__file__)]
    summary=dict(schema_version=1,analysis_status='executed_exploratory_relationships',period=list(PERIOD),
        fixed_species=list(SPECIES),fixed_endpoints=endpoints,bootstrap_replicates=bootstrap_reps,
        bootstrap_seed=20261030,spatial_bootstrap='10 km connected geographic components; uncertainty sensitivity, not independence proof',
        n_site_species=len(cohort),n_unique_sites=int(cohort.site_id.nunique()),
        n_positive_site_species=int(cohort.positive_mapped_detection.sum()),n_observed_site_seasons=int(cohort.observed_seasons.sum()),
        n_with_repeated_counts=int(cohort.observed_seasons.ge(2).sum()),
        n_positive_with_repeated_counts=int((cohort.positive_mapped_detection&cohort.observed_seasons.ge(2)).sum()),
        n_two_season_only=int(cohort.observed_seasons.eq(2).sum()),common_census_year_sensitivity=common_year,
        static_map_copied_to_annual_records=False,unobserved_counts_imputed=False,
        vegetation_non_detection_treated_as_biological_absence=False,vegetation_temporal_trend_estimated=False,
        causal_effect_estimated=False,forecast_estimated=False,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        primary_source_urls=['https://doi.org/10.1038/s41561-024-01492-4','https://doi.org/10.6084/m9.figshare.24745956.v1',
            'https://github.com/CCheCastaldo/mapppdr/tree/88c73a507e0921b2541c218c71eaf16721bc6502'],
        limitations=['2017–2023 composite provides spatial mapped detection only, no vegetation growth rate.',
            'Map non-detection can reflect coverage/classification limits; the all-sites sensitivity is mapped signal only.',
            'Count slopes summarize irregular observed seasons; two-point changes are not established biological trends.',
            'Region adjustment does not remove continuous latitude, ice-free land area, terrain, microclimate or survey-method differences.',
            'Vegetation and breeding counts overlap in time, so direction and temporal precedence are unidentified.',
            '10 km bootstrap blocks reduce immediate spatial pseudoreplication but do not guarantee independent errors.',
            'Counts concern surveyed known breeding sites; no inference about unobserved occupation or new site selection.',
            'All fixed combinations are reported; no multiple-testing significance claims or result-based model selection.'])
    (out/'checks.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    cols=['cohort','endpoint','species','adjustment','n','n_spatial_blocks','pearson_r','slope','slope_bootstrap_low','slope_bootstrap_high']
    print(associations[cols].to_string(index=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'outputs/vegetation_response_v1')
    parser.add_argument('--bootstrap-reps',type=int,default=999)
    args=parser.parse_args(); run(args.out,args.bootstrap_reps)
