"""V10: source-matched nest/chick composition, not certified fledging or causality."""
from __future__ import annotations
import argparse, csv, hashlib, json, math, statistics, sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recorded_chick_output_v9 as v9
GEOGRAPHY_SHA='9ab362853535e8bdbbc63cc83803d1e7636ec37eeab7d55d17151f27036360ff'
COAST_SHA='66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4'
MAINLAND_FID=17692
PRIMARY='CHPE|GEPE'
ORDERED='nest_interval_precedes_chick_interval'

def valid_count(value):
    if value is None: raise ValueError('missing count is not zero')
    value=float(value)
    if not math.isfinite(value) or value<0: raise ValueError('invalid original count')
    return value

def dominant(a,b,sa,sb):
    return sb if b>a else sa if a>b else 'tie'

def stage_metrics(a,b):
    sa,sb=a['species_id'],b['species_id']
    if sa==sb: raise ValueError('distinct species required')
    na,nb=valid_count(a['nest_count']),valid_count(b['nest_count'])
    ca,cb=valid_count(a['chick_count']),valid_count(b['chick_count'])
    if min(na,nb)<=0: raise ValueError('positive nests required')
    ra,rb=ca/na,cb/nb
    pn=nb/(na+nb);pc=cb/(ca+cb) if ca+cb>0 else None
    ln=math.log(nb/na)
    lc=math.log(cb/ca) if min(ca,cb)>0 else None
    lr=math.log(rb/ra) if min(ra,rb)>0 else None
    return dict(species_a=sa,species_b=sb,nest_count_a=na,nest_count_b=nb,
        chick_count_a=ca,chick_count_b=cb,recorded_output_a=ra,recorded_output_b=rb,
        output_difference_b_minus_a=rb-ra,nest_share_b=pn,chick_share_b=pc,
        share_shift_b=pc-pn if pc is not None else None,
        log_nest_ratio_b_over_a=ln,log_chick_ratio_b_over_a=lc,
        log_output_ratio_b_over_a=lr,
        log_identity_error=lc-ln-lr if lc is not None else None,
        nest_dominant_species=dominant(na,nb,sa,sb),
        chick_dominant_species=dominant(ca,cb,sa,sb),
        output_dominant_species=dominant(ca*nb,cb*na,sa,sb),
        nest_leader_lower_output=(nb-na)*(cb*na-ca*nb)<0,
        nest_chick_rank_reversal=(nb-na)*(cb-ca)<0,
        ratio_above_two_any=ra>2 or rb>2)

def build_contrasts(pairs,sites,geography):
    groups=defaultdict(list)
    seen=set()
    for row in pairs:
        key=(row['site_id'],int(row['season_start']),row['citekey'],row['vantage'])
        full=key+(row['species_id'],)
        if full in seen: raise ValueError('duplicate source species-stage pair')
        seen.add(full);groups[key].append(row)
    contrasts=[]
    for (site,season,cite,vantage),rows in sorted(groups.items()):
        for a,b in combinations(sorted(rows,key=lambda r:r['species_id']),2):
            metrics=stage_metrics(a,b)
            ordered=all(r['chronology']==ORDERED for r in (a,b))
            full=all(r[s+'_date_precision']=='full_date' for r in (a,b) for s in ('nest','chick'))
            same=ordered and full and all(a[s+'_date_lower']==a[s+'_date_upper']==b[s+'_date_lower']==b[s+'_date_upper'] for s in ('nest','chick'))
            geo=geography.get(site,{})
            exact=geo.get('category')=='EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON'
            landid=geo.get('original_land_fid') if exact else None
            item=dict(site_id=site,site_name=sites[site]['site_name'],region=sites[site]['region'],
                season_start=season,citekey=cite,vantage=vantage,
                pair=a['species_id']+'|'+b['species_id'],both_stages_ordered=ordered,
                same_full_dates_across_species=same,
                exact_source_land_fid=landid,
                current_mapped_nonmainland_land=exact and landid!=MAINLAND_FID,
                original_land_category=geo.get('category','not_in_V6_source_roster'),
                field_nest_boundary_verified=False,equal_chick_age_verified=False,
                fledging_verified=False,**metrics)
            for suffix,r in [('a',a),('b',b)]:
                for stage in ('nest','chick'):
                    for key in ('source_id','date_precision','date_lower','date_upper'):
                        item[f'{stage}_{key}_{suffix}']=r[f'{stage}_{key}']
            contrasts.append(item)
    biological=Counter((r['site_id'],r['season_start'],r['pair']) for r in contrasts)
    for row in contrasts:
        row['ambiguous_site_season_pair']=biological[row['site_id'],row['season_start'],row['pair']]>1
    return contrasts,dict(source_contrasts=len(contrasts),
        ambiguous_source_rows=sum(r['ambiguous_site_season_pair'] for r in contrasts),
        distinct_site_season_species_pairs=len(biological))

def mean_or_none(values):
    values=[x for x in values if x is not None]
    return statistics.mean(values) if values else None

def summary(rows):
    groups=defaultdict(list)
    for row in rows: groups[row['site_id']].append(row)
    site_summary=[]
    for site,part in sorted(groups.items()):
        site_summary.append(dict(site_id=site,n=len(part),region=part[0]['region'],
            mean_share_shift_b=mean_or_none([r['share_shift_b'] for r in part]),
            mean_output_difference_b_minus_a=mean_or_none([r['output_difference_b_minus_a'] for r in part]),
            nest_leader_lower_output_n=sum(r['nest_leader_lower_output'] for r in part),
            nest_chick_rank_reversals=sum(r['nest_chick_rank_reversal'] for r in part)))
    site_means=[r['mean_share_shift_b'] for r in site_summary if r['mean_share_shift_b'] is not None]
    deletion=[statistics.mean([v for j,v in enumerate(site_means) if j!=i]) for i in range(len(site_means))] if len(site_means)>1 else []
    return dict(n_source_comparisons=len(rows),n_sites=len(groups),
        n_regions=len({r['region'] for r in rows}),
        regions=dict(sorted(Counter(r['region'] for r in rows).items())),
        source_count=len({r['citekey'] for r in rows}),
        seasons=sorted({r['season_start'] for r in rows}),
        site_summaries=site_summary,
        row_mean_share_shift_b=mean_or_none([r['share_shift_b'] for r in rows]),
        equal_site_mean_share_shift_b=mean_or_none(site_means),
        equal_site_mean_output_difference_b_minus_a=mean_or_none([r['mean_output_difference_b_minus_a'] for r in site_summary]),
        leave_one_site_mean_shift_range_not_CI=[min(deletion),max(deletion)] if deletion else None,
        nest_leader_lower_output_n=sum(r['nest_leader_lower_output'] for r in rows),
        nest_chick_rank_reversal_n=sum(r['nest_chick_rank_reversal'] for r in rows),
        nest_rank_tie_n=sum(r['nest_dominant_species']=='tie' for r in rows),
        chick_rank_tie_n=sum(r['chick_dominant_species']=='tie' for r in rows),
        total_chicks_zero_n=sum(r['chick_share_b'] is None for r in rows),
        ratio_above_two_rows=sum(r['ratio_above_two_any'] for r in rows),
        positive_share_shift_b_n=sum(r['share_shift_b'] is not None and r['share_shift_b']>0 for r in rows),
        output_b_greater_n=sum(r['output_difference_b_minus_a']>0 for r in rows),
        output_b_equal_n=sum(r['output_difference_b_minus_a']==0 for r in rows),
        p_value=None,confidence_interval=None,causal_effect_identified=False)

def analyze(pairs,sites,geography):
    rows,audit=build_contrasts(pairs,sites,geography)
    results={}
    for pair in sorted({r['pair'] for r in rows}):
        all_rows=[r for r in rows if r['pair']==pair and not r['ambiguous_site_season_pair']]
        ordered=[r for r in all_rows if r['both_stages_ordered']]
        same=[r for r in all_rows if r['same_full_dates_across_species']]
        mapped=[r for r in ordered if r['current_mapped_nonmainland_land']]
        results[pair]={label:summary(part) for label,part in [
            ('all_unique_sources',all_rows),('ordered_stages_primary',ordered),
            ('same_full_dates_secondary',same),('ordered_mapped_nonmainland',mapped)]}
        results[pair]['ordered_mapped_nonmainland']['mapped_land_fids']=sorted({r['exact_source_land_fid'] for r in mapped})
    return rows,dict(schema=1,status='POST_EXPLORATION_STAGE_COMPOSITION_NOT_CAUSAL',
        primary_species_pair=PRIMARY,source_matching=audit,contrasts=results,
        maximum_log_identity_error=max([abs(r['log_identity_error']) for r in rows if r['log_identity_error'] is not None] or [0]),
        limits=[
            'Same source/date does not certify same census footprint, chick age or fledging stage.',
            'Recorded nest and chick ranks are not adult survival, recruitment or population growth.',
            'No regression of colony size against its own denominator ratio; no Allee/density claim.',
            'Multiple seasons at one site, and sites within one current land, are not independent repetitions.',
            'Selection of sites with both positive nests and reported chicks excludes unobserved or vanished breeding groups.',
            'Current SCAR land IDs are not historical nesting polygons or biologically independent populations.',
            'Neither synchrony, competition, movement nor climate attribution is identified.',
            'All species pairs and timing cohorts remain separately reported; no new p-values or revised previous multiplicity correction.'
        ])

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--original-dir',required=True,type=Path)
    p.add_argument('--geography-json',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    folder=args.original_dir/'source' if (args.original_dir/'source').is_dir() else args.original_dir
    for name,expected in v9.PINS.items():
        if v9.digest(folder/name)!=expected: raise ValueError('raw source SHA mismatch: '+name)
    if v9.digest(args.geography_json)!=GEOGRAPHY_SHA: raise ValueError('V6 geography result changed')
    geo=json.loads(args.geography_json.read_text())
    if geo['geographic_source']['source_land_sha256']!=COAST_SHA: raise ValueError('coastline edition changed')
    raw=v9.read_csv(folder/'observations_p1.csv')+v9.read_csv(folder/'observations_p2.csv')
    if len(raw)!=5487: raise ValueError('original observation count changed')
    pairs,stage_audit=v9.stage_pairs(raw)
    if len(pairs)!=274: raise ValueError('V9 original source-stage reconstruction changed')
    site_rows=v9.read_csv(folder/'sites.csv')
    sites={r['site_id']:r for r in site_rows}
    if len(sites)!=len(site_rows): raise ValueError('source site duplicate')
    rows,result=analyze(pairs,sites,geo['geography'])
    if len(rows)!=75: raise ValueError('metadata-only source cross-species support changed')
    primary=result['contrasts'][PRIMARY]
    if [primary[k]['n_source_comparisons'] for k in ('all_unique_sources','ordered_stages_primary','same_full_dates_secondary')]!=[41,21,8]:
        raise ValueError('frozen timing opportunity changed')
    result.update(source_stage_audit=stage_audit,original_source_sha256=v9.PINS,
        geography_json_sha256=GEOGRAPHY_SHA,source_release='MAPPPD 5.0 2026-10-21',
        scope='Observed source counts, not continent-wide demography or verified fledging.')
    v9.write_csv(args.out/'stage_species_composition_v10.csv',rows)
    v9.write_csv(args.out/'rebuilt_source_stage_pairs_v10.csv',pairs)
    v9.write_csv(args.out/'primary_site_summaries_v10.csv',primary['ordered_stages_primary']['site_summaries'])
    (args.out/'stage_species_composition_v10_result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print('STAGE_COMPOSITION_V10='+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)

if __name__=='__main__':main()
