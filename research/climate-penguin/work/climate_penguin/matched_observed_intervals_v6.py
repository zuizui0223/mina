"""V6: exact co-source penguin records at consecutive OBSERVED paired seasons.

Different estimand from V1 annual contrasts and V3--V5 climate regressions.
Never fills absent seasons, bridges a known zero/source conflict, or claims
current mapped land is independent historical breeding habitat.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

CONTRASTS = [('ADPE','GEPE'),('CHPE','GEPE'),('ADPE','CHPE')]
UNKNOWN = {'','unknown','na','nan','none'}
CONTINENT_FID = 17692
EXACT = 'EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON'
PINS = {
 'release.json':'8f676f6498b1bc79708a67fb05d4ac8ee73249444e85402af87f6a3c64280a65',
 'sites.csv':'36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34',
 'observations_p1.csv':'cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075',
 'observations_p2.csv':'c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3',
}


def numeric(value):
    try:
        x = float(str(value).replace(',','').strip())
    except (ValueError,TypeError):
        return None
    return x if math.isfinite(x) and 0 <= x < 1e10 else None


def context(r):
    return r['citekey'], r['vantage']


def admissible(r):
    n = numeric(r['count'])
    return (r['presence']=='1' and n is not None and n>0 and
            all(x.strip().lower() not in UNKNOWN for x in context(r)))


def month(r):
    try:
        y,m = int(r['year']),int(r['month'])
    except (KeyError,ValueError,TypeError):
        return None
    return (y,m) if 1800<=y<=2026 and 1<=m<=12 else None


def build_intervals(rows, sites, a, b):
    """Select adjacent joint observations, then reject intervening bad evidence."""
    groups, years, seen = defaultdict(list),defaultdict(set),set()
    audit = Counter()
    for r in rows:
        if r['id'] in seen:
            raise ValueError('duplicate observation ID')
        seen.add(r['id'])
        if r['site_id'] not in sites:
            raise ValueError('orphan original site')
        if r['species_id'] not in (a,b) or r['type']!='nests':
            continue
        try:
            year = int(r['season'])
        except (ValueError,TypeError):
            continue
        if not 1890<=year<=2026:
            continue
        groups[r['site_id'],r['species_id'],year].append(r)
        years[r['site_id']].add(year)
    result = []
    audit['duplicate_site_species_seasons'] = sum(len(v)>1 for v in groups.values())
    for sid, yrset in sorted(years.items()):
        joint = []
        for y in sorted(yrset):
            rr = [groups.get((sid,sp,y),[]) for sp in (a,b)]
            if any(len(z)!=1 for z in rr):
                continue
            ra,rb = rr[0][0],rr[1][0]
            if not (admissible(ra) and admissible(rb)):
                continue
            if context(ra)!=context(rb):
                continue
            joint.append((y,ra,rb))
        audit['eligible_joint_seasons'] += len(joint)
        for (start,as_,bs),(end,ae,be) in zip(joint,joint[1:]):
            audit['consecutive_joint_endpoint_candidates'] += 1
            c = context(as_)
            if c!=context(ae):
                audit['endpoint_context_change'] += 1
                continue
            intervening = [groups.get((sid,sp,y),[]) for y in yrset
                           if start<y<end for sp in (a,b)]
            conflict = any(len(rr)>1 or any(not admissible(r) or context(r)!=c
                                            for r in rr) for rr in intervening)
            if conflict:
                audit['intervening_conflict'] += 1
                continue
            gap = end-start
            ga = math.log(numeric(ae['count']))-math.log(numeric(as_['count']))
            gb = math.log(numeric(be['count']))-math.log(numeric(bs['count']))
            ma0,mb0,ma1,mb1 = month(as_),month(bs),month(ae),month(be)
            result.append(dict(
                site_id=sid,site_name=sites[sid]['site_name'],region=sites[sid]['region'],
                species_a=a,species_b=b,start=start,end=end,gap=gap,
                original_citekey=c[0],original_vantage=c[1],
                source_a_start=as_['id'],source_a_end=ae['id'],
                source_b_start=bs['id'],source_b_end=be['id'],
                n_a_start=numeric(as_['count']),n_a_end=numeric(ae['count']),
                n_b_start=numeric(bs['count']),n_b_end=numeric(be['count']),
                log_ratio_change=gb-ga,annualized_log_ratio_change=(gb-ga)/gap,
                annualized_a_growth=ga/gap,annualized_b_growth=gb/gap,
                same_known_month_at_both_endpoints=bool(ma0 and ma1 and ma0==mb0 and ma1==mb1),
                unobserved_years_interpolated=False,
                actual_elapsed_days_verified=False))
    result.sort(key=lambda z:(z['site_id'],z['start'],z['end']))
    audit['retained_observed_intervals'] = len(result)
    return result,dict(audit)


def summarize(rows, geo=None):
    """Period-length weighted site rates; then equal site or equal land weights."""
    kept, omitted = [],set()
    for r in rows:
        if geo is not None:
            g = geo[r['site_id']]
            if g['category']!=EXACT or g.get('original_land_fid')==CONTINENT_FID:
                omitted.add(r['site_id']);continue
        kept.append(r)
    groups = defaultdict(list)
    for r in kept:
        groups[r['site_id']].append(r)
    ss = []
    for sid,rr in sorted(groups.items()):
        ordered = sorted(rr,key=lambda x:x['start'])
        if any(x['end']>y['start'] for x,y in zip(ordered,ordered[1:])):
            raise ValueError('overlapping source intervals within site')
        duration = sum(r['gap'] for r in rr)
        rate = sum(r['log_ratio_change'] for r in rr)/duration
        ss.append(dict(site_id=sid,region=rr[0]['region'],n_intervals=len(rr),
            observed_season_gap_sum=duration,first_start=min(r['start'] for r in rr),
            last_end=max(r['end'] for r in rr),period_weighted_annualized_rate=rate,
            equal_interval_annualized_rate=statistics.mean(r['annualized_log_ratio_change'] for r in rr)))
    vals = [x['period_weighted_annualized_rate'] for x in ss]
    out = dict(n_intervals=len(kept),n_sites=len(ss),
        n_regions=len({r['region'] for r in kept}),
        regions=sorted({r['region'] for r in kept}),
        gap_counts={str(k):v for k,v in sorted(Counter(r['gap'] for r in kept).items())},
        observed_gap_sum_site_seasons=sum(r['gap'] for r in kept),
        n_positive_site_rates=sum(x>0 for x in vals),
        equal_site_mean_annualized_rate=statistics.mean(vals) if vals else None,
        equal_site_mean_of_interval_rates=statistics.mean(x['equal_interval_annualized_rate'] for x in ss) if ss else None,
        leave_one_site_out_range_not_CI=[min((sum(vals)-v)/(len(vals)-1) for v in vals),
                                       max((sum(vals)-v)/(len(vals)-1) for v in vals)] if len(vals)>=3 else None,
        same_known_month_endpoint_intervals=sum(bool(r.get('same_known_month_at_both_endpoints',False)) for r in kept),
        excluded_sites=sorted(omitted),site_summaries=ss,
        independent_observations_or_islands_verified=False,
        conditional_on_positive_endpoints=True,climate_effect_estimated=False)
    if geo is not None:
        land = defaultdict(list)
        for s in ss:
            land[geo[s['site_id']]['original_land_fid']].append(s)
        lv = [statistics.mean(s['period_weighted_annualized_rate'] for s in z) for z in land.values()]
        out.update(n_mapped_land_units=len(land),equal_land_mean_annualized_rate=statistics.mean(lv) if lv else None,
           leave_one_land_out_range_not_CI=[min((sum(lv)-v)/(len(lv)-1) for v in lv),
                                           max((sum(lv)-v)/(len(lv)-1) for v in lv)] if len(lv)>=3 else None,
           land_summaries=[dict(source_land_fid=f,site_ids=[z['site_id'] for z in ss_],
                 mean_annualized_rate=statistics.mean(z['period_weighted_annualized_rate'] for z in ss_))
                 for f,ss_ in sorted(land.items())])
    return out


def readcsv(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def land_mapping(sites, selected_ids, out):
    from pyproj import Transformer
    from shapely.geometry import Point
    p = Path(__file__).with_name('audit_palmer_original_island_rock_v1.py')
    spec = importlib.util.spec_from_file_location('original_land_v6',p)
    helper = importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    project = Transformer.from_crs('EPSG:4326','EPSG:3031',always_xy=True)
    pts = {s:Point(*project.transform(float(sites[s]['longitude']),float(sites[s]['latitude'])))
           for s in sorted(selected_ids)}
    raw = helper.original_publisher_zip()
    (out/'source').mkdir(exist_ok=True)
    (out/'source/SCAR_original_highres_land.zip').write_bytes(raw)
    with tempfile.TemporaryDirectory(prefix='mina-observed-v6-') as temp:
        shp = helper.unpack(raw,Path(temp))
        polygons,surfaces = helper.geometry_source_candidates(shp,pts)
    geos = {s:helper.classify(pt,polygons) for s,pt in pts.items()}
    return geos,dict(source_land_sha256=hashlib.sha256(raw).hexdigest(),source_surface_counts=surfaces,
                     currently_mapped_land_not_historical_nest_polygon=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--with-geometry',action='store_true')
    args = ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    src = args.original_dir/'source'
    for name,pin in PINS.items():
        if sha(src/name)!=pin:
            raise ValueError('original source SHA drift: '+name)
    observations = readcsv(src/'observations_p1.csv')+readcsv(src/'observations_p2.csv')
    registry = readcsv(src/'sites.csv')
    sites = {r['site_id']:r for r in registry}
    if len(observations)!=5487 or len(sites)!=729 or len(registry)!=729:
        raise ValueError('source dimensions drift')
    baseline = readcsv(args.original_dir/'matched_species_annual_contrasts.csv')
    rows,details = [],{}
    for a,b in CONTRASTS:
        rr,audit = build_intervals(observations,sites,a,b)
        old = {(r['site_id'],int(r['start']),int(r['end'])):r for r in baseline
               if (r['species_a'],r['species_b'])==(a,b)}
        annual = [r for r in rr if r['gap']==1]
        if set(old)!={(r['site_id'],r['start'],r['end']) for r in annual}:
            raise ValueError('original annual endpoint set changed')
        for r in annual:
            original = old[(r['site_id'],r['start'],r['end'])]
            if any(r[k]!=original[k] for k in ('source_a_start','source_a_end','source_b_start','source_b_end')):
                raise ValueError('original annual record identity drift')
            if not math.isclose(r['log_ratio_change'],float(original['delta_log_ratio_b_over_a']),abs_tol=1e-12):
                raise ValueError('original annual outcome drift')
        old_sites = {r['site_id'] for r in annual}
        new_sites = sorted({r['site_id'] for r in rr}-old_sites)
        for r in rr:
            r['site_new_to_this_contrast_vs_annual_only'] = r['site_id'] in new_sites
        details[a+'__'+b] = dict(eligibility=audit,all_observed=summarize(rr),
            annual_only_unchanged=summarize(annual),
            nonannual_only=summarize([r for r in rr if r['gap']>1]),
            added_site_ids=new_sites,
            previously_annual_sites_all_observed=summarize([r for r in rr if r['site_id'] in old_sites]),
            added_sites_only=summarize([r for r in rr if r['site_id'] in new_sites]))
        rows.extend(rr)
    geo,geo_source = {},None
    if args.with_geometry:
        geo,geo_source = land_mapping(sites,{r['site_id'] for r in rows},args.out)
        for a,b in CONTRASTS:
            rr = [r for r in rows if (r['species_a'],r['species_b'])==(a,b)]
            v = details[a+'__'+b]
            v['current_land_all_observed'] = summarize(rr,geo)
            v['current_land_annual_unchanged'] = summarize([r for r in rr if r['gap']==1],geo)
            v['current_land_added_sites_only'] = summarize([r for r in rr if r['site_new_to_this_contrast_vs_annual_only']],geo)
            old_lands = {geo[r['site_id']]['original_land_fid'] for r in rr if r['gap']==1 and
                         geo[r['site_id']]['category']==EXACT and geo[r['site_id']]['original_land_fid']!=CONTINENT_FID}
            new_lands = {geo[r['site_id']]['original_land_fid'] for r in rr if
                         geo[r['site_id']]['category']==EXACT and geo[r['site_id']]['original_land_fid']!=CONTINENT_FID}
            v['additional_mapped_land_ids_vs_annual_only'] = sorted(new_lands-old_lands)
    with (args.out/'observed_species_intervals_v6.csv').open('w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    report = dict(schema=1,status='postexploration_observed_interval_macro_source_extension',
        source_run=40868828790,source_sha256=PINS,source_observations=len(observations),
        old_annual_rows_reproduced=len(baseline),total_species_interval_rows=len(rows),
        distinct_source_site_ids=len({r['site_id'] for r in rows}),
        interval_unit='consecutive jointly observed breeding-season endpoints, not filled annual observations',
        contrasts=details,geography=geo,geographic_source=geo_source,
        limits=[
            'Existing source outcomes were exposed; this is exploratory expansion, not independent biological confirmation.',
            'A multi-year rate is a net change per elapsed breeding season, not observed constant annual growth.',
            'Same source and vantage cannot certify equal detection effort or same census day.',
            'Positive endpoints condition on observed presence; explicit zeros and known conflicts block bridging.',
            'Species contrasts share source records and are not independent samples or additive replication.',
            'No additional climate exposure, causal climate effect, competition or dispersal is measured.',
            'Current SCAR point containment does not verify historical nesting polygons or ecological independence.',
            'Fixed44 V3--V5 estimand, observations, covariates and earlier216 testing family are unchanged.'
        ])
    (args.out/'observed_species_intervals_v6_result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('OBSERVED_SPECIES_INTERVALS_V6='+json.dumps({
        'source_run':40868828790,'rows':len(rows),'sites':report['distinct_source_site_ids'],
        'summary':{k:{'intervals':v['all_observed']['n_intervals'],'sites':v['all_observed']['n_sites'],
          'new_sites':v['added_site_ids'],'mean_rate':v['all_observed']['equal_site_mean_annualized_rate'],
          'land_count':v.get('current_land_all_observed',{}).get('n_mapped_land_units'),
          'land_mean':v.get('current_land_all_observed',{}).get('equal_land_mean_annualized_rate')}
          for k,v in details.items()}},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
