#!/usr/bin/env python3
"""Original Adélie 19/26/35 source-cohort region/block locked allocation bounds.

Source: original observed 80 cohort-colony records archived in
../latitudinal_scale_20261115/original_adelie_19_26_35_site_growth_cohorts.csv.
No species absences imputed; climate causality, bird migration and p-values
are not estimated. Permutations hold observed region/block 2010s subtotals
fixed and relabel relative-growth ratios among source-positive colonies.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd

KM=111.195
COUNTS={'all_three_decades':19,'two_plus_endpoint_years':26,'one_plus_endpoint_year':35}
LEVELS={'reporting_region':['source_region'],
        'region_and_250km_block':['source_region','polar_250km_block']}
EXPECTED_SOURCE_SHA256='af310e2c8787074ef2bfd69b9a00aab1d863e8cdc3cd53edfd700b5e65460592'

def envelope(df,keys,field,early):
    lo=hi=0.
    for _,g in df.groupby(keys,sort=True):
        weight=float(g.n_late.sum())
        lo+=weight*g[field].min()
        hi+=weight*g[field].max()
    return (lo/df.n_late.sum()-early,hi/df.n_late.sum()-early)

def permuted_centroids(df,keys,n,seed,baseline):
    rng=np.random.default_rng(seed)
    early=df.n_early.to_numpy(float)
    late=df.n_late.to_numpy(float)
    south=df.south_lat.to_numpy(float)
    weights=np.zeros((n,len(df)),float)
    for _,inds in df.groupby(keys,sort=True).indices.items():
        inds=np.asarray(inds,int)
        e=early[inds];l=late[inds]
        live=e>0
        assert np.all(l[~live]==0)
        if not np.any(live):continue
        ratio=l[live]/e[live]
        if len(ratio)==1:
            out=np.repeat(l[live][None,:],n,axis=0)
        else:
            order=np.argsort(rng.random((n,len(ratio))),axis=1)
            out=e[live][None,:]*ratio[order]
            assert np.all(out.sum(axis=1)>0)
            out*=l.sum()/out.sum(axis=1)[:,None]
        weights[:,inds[live]]=out
    assert np.max(np.abs(weights.sum(axis=1)-late.sum()))<1e-5
    return KM*(weights@south/late.sum()-baseline)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cohort-csv',type=Path,
        default=Path(__file__).resolve().parent.parent/'latitudinal_scale_20261115'/'original_adelie_19_26_35_site_growth_cohorts.csv')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--permutations',type=int,default=50000)
    ap.add_argument('--seed',type=int,default=20261115)
    args=ap.parse_args()
    assert hashlib.sha256(args.cohort_csv.read_bytes()).hexdigest()==EXPECTED_SOURCE_SHA256
    all_=pd.read_csv(args.cohort_csv)
    assert len(all_)==80 and all_.groupby('cohort').size().to_dict()==COUNTS
    assert all_.species.eq('ADPE').all()
    assert not all_.duplicated(['cohort','site_id']).any()
    assert (all_[['n_early','n_late']]>=0).all().all()
    summaries=[];randomizations=[];group_rows=[]
    for cohort,count in COUNTS.items():
        g=all_.loc[all_.cohort==cohort].copy().reset_index(drop=True)
        g['south_lat']=-g.latitude
        assert len(g)==count
        n0=float(g.n_early.sum()); n1=float(g.n_late.sum())
        early=float(np.dot(g.n_early,g.south_lat)/n0)
        late=float(np.dot(g.n_late,g.south_lat)/n1)
        old_ice=float(np.dot(g.n_early,g.sic_early)/n0)
        new_ice=float(np.dot(g.n_late,g.sic_late)/n1)
        observed=KM*(late-early)
        assert abs(observed-{'all_three_decades':107.31034633747,
                            'two_plus_endpoint_years':88.41083229452,
                            'one_plus_endpoint_year':99.60262662670}[cohort])<1e-7
        row={'cohort':cohort,'n_known_source_colonies':count,
            'n_source_reporting_regions':g.source_region.nunique(),
            'n_unique_250km_blocks':g.polar_250km_block.nunique(),
            'observed_southward_count_weighted_km':observed,
            'early_source_nest_count_median_sum':n0,'late_source_nest_count_median_sum':n1,
            'observed_weighted_nearshore_SIC_change_pp':new_ice-old_ice,
            'observed_double_zero_site_codes':';'.join(g.loc[(g.n_early==0)&(g.n_late==0),'site_id'])}
        for level,keys in LEVELS.items():
            a,b=envelope(g,keys,'south_lat',early)
            ia,ib=envelope(g,keys,'sic_late',old_ice)
            low,high=KM*a,KM*b
            assert low-1e-8<=observed<=high+1e-8
            row[level+'_southward_min_km']=low
            row[level+'_southward_max_km']=high
            row[level+'_nearshore_ice_change_min_pp']=ia
            row[level+'_nearshore_ice_change_max_pp']=ib
            row[level+'_guaranteed_southward_for_any_nonnegative_within_group_nest_weights']=low>0
            draws=permuted_centroids(g,keys,args.permutations,args.seed,early)
            assert draws.min()>=low-1e-8 and draws.max()<=high+1e-8
            randomizations.append({
               'cohort':cohort,'null_label':level,
               'n_permutations':args.permutations,'seed':args.seed,
               'observed_southward_km':observed,'null_median_km':np.median(draws),
               'null_central_2p5_km':np.quantile(draws,.025),
               'null_central_97p5_km':np.quantile(draws,.975),
               'null_min_km':draws.min(),'null_max_km':draws.max(),
               'fraction_of_source_constrained_random_reassignments_southward':np.mean(draws>0),
               'fraction_of_source_constrained_random_reassignments_greater_or_equal_to_observed':np.mean(draws>=observed),
               'not_a_p_value':True})
        for (region,block),b in g.groupby(['source_region','polar_250km_block'],sort=True):
            group_rows.append({
               'cohort':cohort,'source_region':region,'source_250km_block':block,
               'n_actual_source_colonies':len(b),'site_codes':';'.join(b.site_id),
               'source_1990s_nest_median_sum':b.n_early.sum(),
               'source_2010s_nest_median_sum':b.n_late.sum(),
               'minimum_source_south_latitude_deg':b.south_lat.min(),
               'maximum_source_south_latitude_deg':b.south_lat.max(),
               '2010s_nesting_share_in_fixed_cohort':b.n_late.sum()/n1})
        summaries.append(row)
    args.out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(summaries).to_csv(args.out/'observed_source_roster_exact_geographic_envelopes.csv',index=False,float_format='%.14g')
    pd.DataFrame(randomizations).to_csv(args.out/'growth_factor_permutation_source_diagnostics.csv',index=False,float_format='%.14g')
    pd.DataFrame(group_rows).to_csv(args.out/'source_reporting_region_250km_block_counts_and_latitude_limits.csv',index=False,float_format='%.14g')
    receipt={'source_sha256':EXPECTED_SOURCE_SHA256,'source_original_runs':[42788030834,42844104869],
             'n_source_rows':len(all_),'seed':args.seed,'n_relabelings':args.permutations,
             'exact_source_envelopes':summaries,'permutation_summaries':randomizations,
             'no_independent_p_values_or_causal_inferences':True}
    (args.out/'source_constrained_allocation_receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    print('PASS: three source-verified rosters, region/block exact bounds and conditional relabelings')

if __name__=='__main__':main()
