"""V9 source-matched recorded chick output, not field-certified fledging success.

No source count correction, missing-as-zero, unknown-date imputation, population
recruitment model, climate fitting or modification of V1--V8 is performed here.
"""
from __future__ import annotations
import argparse, calendar, csv, hashlib, json, math, statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

FOCAL_SOURCE = 'kpri2020report6'
FOCAL_SITES = ('ARDL', 'BART')
FOCAL_SPECIES = ('CHPE', 'GEPE')
FOCAL_SEASONS = tuple(range(2010, 2020))
UNKNOWN = {'', 'unknown', 'na', 'nan', 'none'}
ROOT = Path(__file__).resolve().parents[2]
PINS = {
 'release.json':'8f676f6498b1bc79708a67fb05d4ac8ee73249444e85402af87f6a3c64280a65',
 'sites.csv':'36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34',
 'observations_p1.csv':'cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075',
 'observations_p2.csv':'c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3',
}

def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def number(value):
    try:
        value = float(str(value).replace(',', '').strip())
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) and 0 <= value < 1e10 else None

def calendar_bounds(row):
    """Intervals reflect reported precision; a missing month remains a full year."""
    try:
        y = int(row.get('year', ''))
        if not 1800 <= y <= 2026:
            raise ValueError('year outside source scope')
        raw_m, raw_d = str(row.get('month', '')).strip(), str(row.get('day', '')).strip()
        if raw_m.lower() in UNKNOWN:
            if raw_d.lower() not in UNKNOWN:
                return None, None, 'inconsistent_day_without_month'
            return date(y, 1, 1), date(y, 12, 31), 'year_only'
        m = int(raw_m)
        if not 1 <= m <= 12:
            raise ValueError('invalid source month')
        if raw_d.lower() in UNKNOWN:
            return date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1]), 'year_month'
        d = date(y, m, int(raw_d))
        return d, d, 'full_date'
    except (ValueError, TypeError):
        return None, None, 'invalid_or_unknown'

def chronology(nest, chick):
    n0, n1, np = calendar_bounds(nest)
    c0, c1, cp = calendar_bounds(chick)
    order = 'unresolved'
    if None not in (n0, n1, c0, c1):
        if n1 < c0:
            order = 'nest_interval_precedes_chick_interval'
        elif c1 < n0:
            order = 'reported_chicks_before_nests'
    return dict(chronology=order, nest_date_precision=np, chick_date_precision=cp,
        nest_date_lower=n0.isoformat() if n0 else None,
        nest_date_upper=n1.isoformat() if n1 else None,
        chick_date_lower=c0.isoformat() if c0 else None,
        chick_date_upper=c1.isoformat() if c1 else None)

def stage_pairs(rows):
    groups = defaultdict(lambda: defaultdict(list))
    ids = set()
    audit = Counter()
    for row in rows:
        ident = str(row['id'])
        if ident in ids:
            raise ValueError('duplicate observation ID: ' + ident)
        ids.add(ident)
        if row.get('species_id') not in {'ADPE', 'CHPE', 'GEPE'} or row.get('type') not in {'nests', 'chicks'}:
            continue
        try:
            season = int(row['season'])
        except (ValueError, TypeError):
            audit['invalid_season'] += 1
            continue
        if not 1890 <= season <= 2026:
            audit['invalid_season'] += 1
            continue
        cite = str(row.get('citekey', '')).strip()
        vantage = str(row.get('vantage', '')).strip()
        if cite.lower() in UNKNOWN or vantage.lower() in UNKNOWN:
            audit['unknown_source_or_vantage'] += 1
            continue
        # Include duplicates before numerical filtering; an incomplete second
        # stage record cannot be silently removed to manufacture uniqueness.
        key = row['site_id'], row['species_id'], season, cite, vantage
        groups[key][row['type']].append(row)
    pairs = []
    for (site, sp, season, cite, vantage), stages in sorted(groups.items()):
        if any(len(v) > 1 for v in stages.values()):
            audit['duplicate_stage_groups'] += 1
            continue
        if set(stages) != {'nests', 'chicks'}:
            audit['missing_stage_groups'] += 1
            continue
        nest, chick = stages['nests'][0], stages['chicks'][0]
        n, c = number(nest.get('count')), number(chick.get('count'))
        if n is None or c is None:
            audit['invalid_count_groups'] += 1
            continue
        if n <= 0:
            audit['nonpositive_nests'] += 1
            continue
        ratio = c / n
        item = dict(site_id=site, species_id=sp, season_start=season,
            season_end=season+1, citekey=cite, vantage=vantage,
            nest_count=n, chick_count=c, recorded_chicks_per_nest=ratio,
            nest_source_id=str(nest['id']), chick_source_id=str(chick['id']),
            nest_accuracy=nest.get('accuracy', ''), chick_accuracy=chick.get('accuracy', ''),
            nest_presence=nest.get('presence', ''), chick_presence=chick.get('presence', ''),
            ratio_above_two=ratio > 2,
            fledging_stage_confirmed=False, same_count_extent_confirmed=False,
            **chronology(nest, chick))
        pairs.append(item)
    audit['paired_source_stage_groups'] = len(pairs)
    audit['distinct_source_sites'] = len({r['site_id'] for r in pairs})
    audit['distinct_site_species_seasons'] = len({(r['site_id'], r['species_id'], r['season_start']) for r in pairs})
    audit['observed_zero_chick_groups'] = sum(r['chick_count'] == 0 for r in pairs)
    audit['ratio_above_two_groups'] = sum(r['ratio_above_two'] for r in pairs)
    return pairs, dict(audit)

def correlation(x, y):
    if len(x) != len(y) or len(x) < 3:
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    dx, dy = [v-mx for v in x], [v-my for v in y]
    den = math.sqrt(sum(v*v for v in dx)*sum(v*v for v in dy))
    return sum(a*b for a, b in zip(dx, dy))/den if den > 1e-12 else None

def neighbor_comparison(rows):
    focal = [r for r in rows if r['site_id'] in FOCAL_SITES and
        r['species_id'] in FOCAL_SPECIES and r['season_start'] in FOCAL_SEASONS and
        r['citekey'] == FOCAL_SOURCE and r['vantage'] == 'ground']
    index = {(r['site_id'], r['species_id'], r['season_start']):r for r in focal}
    if len(index) != len(focal):
        raise ValueError('duplicate focal source stage pair')
    seasons = [y for y in FOCAL_SEASONS if all((s, sp, y) in index
        for s in FOCAL_SITES for sp in FOCAL_SPECIES)]
    stats = {}
    for sp in FOCAL_SPECIES:
        annual = []
        for y in seasons:
            a, b = index['ARDL', sp, y], index['BART', sp, y]
            annual.append(dict(season_start=y, ardley=a['recorded_chicks_per_nest'],
                barton=b['recorded_chicks_per_nest'],
                ardley_minus_barton=a['recorded_chicks_per_nest']-b['recorded_chicks_per_nest']))
        a, b = [r['ardley'] for r in annual], [r['barton'] for r in annual]
        changes = {}
        for site in FOCAL_SITES:
            parts = [index[site, sp, y] for y in seasons]
            changes[site] = dict(n_seasons=len(parts),
                mean_recorded_chicks_per_nest=statistics.mean(z['recorded_chicks_per_nest'] for z in parts) if parts else None,
                nest_count_range=[min(z['nest_count'] for z in parts), max(z['nest_count'] for z in parts)] if parts else None,
                nest_count_endpoint_change=(parts[-1]['nest_count']/parts[0]['nest_count']-1) if len(parts)>1 else None,
                endpoint_seasons=[parts[0]['season_start'],parts[-1]['season_start']] if parts else [],
                confirmed_stage_chronology_n=sum(z['chronology']=='nest_interval_precedes_chick_interval' for z in parts))
        stats[sp] = dict(annual_recorded_ratios=annual,
            mean_ardley_minus_barton=statistics.mean(x-y for x,y in zip(a,b)) if a else None,
            seasons_ardley_above_barton=sum(x>y for x,y in zip(a,b)),
            across_site_pearson_r=correlation(a,b), by_site=changes)
    species_difference = {}
    for site in FOCAL_SITES:
        values = [index[site,'GEPE',y]['recorded_chicks_per_nest']-
                  index[site,'CHPE',y]['recorded_chicks_per_nest'] for y in seasons]
        species_difference[site] = dict(mean_gentoo_minus_chinstrap=statistics.mean(values) if values else None,
            seasons_gentoo_above_chinstrap=sum(v>0 for v in values), n_seasons=len(values))
    return dict(n_matched_seasons=len(seasons), matched_seasons=seasons,
        original_source=FOCAL_SOURCE, focal_stage_pair_rows=len(focal),
        by_species=stats, within_site_species_contrast=species_difference,
        causal_effect_identified=False, fledging_success_certified=False,
        independent_climate_replicates=False, p_values=None)

def other_source_counts(obs, focal):
    warnings = []
    for p in focal:
        for stage, field in [('nests','nest_count'), ('chicks','chick_count')]:
            matches = [r for r in obs if r['site_id']==p['site_id'] and r['species_id']==p['species_id']
                and r['season']==str(p['season_start']) and r['type']==stage and r['citekey']!=p['citekey']
                and number(r.get('count')) is not None]
            for r in matches:
                warnings.append(dict(site_id=p['site_id'],species_id=p['species_id'],season_start=p['season_start'],
                    type=stage, focal_count=p[field],other_count=number(r['count']),
                    focal_citekey=p['citekey'],other_citekey=r['citekey'],other_source_id=r['id'],
                    equal_value=p[field]==number(r['count']), resolution='retain_both_no_overwrite'))
    return warnings

def official_source_checks(records, focal):
    index = {(r['site_id'],r['species_id'],str(r['season_start'])):r for r in focal}
    comparisons = []
    for r in records:
        if r['document_id']!='UBA2025' or r['measure']!='breeding_pairs':
            continue
        key = r['site_id'],r['species_id'],r['season_start']
        if key not in index:
            continue
        p = index[key]
        comparisons.append(dict(site_id=r['site_id'],species_id=r['species_id'],season_start=int(r['season_start']),
            original_mapppd_nests=p['nest_count'],published_breeding_pairs=float(r['value']),
            source_values_equal=p['nest_count']==float(r['value']),
            mapppd_source_id=p['nest_source_id'],official_page_index=r['pdf_page_index'],
            source_disagreement_not_resolved=True, no_denominator_substitution=True))
    own = {(r['site_id'],r['species_id'],r['season_start']):r for r in records
        if r['document_id']=='UBA2025' and r['measure']=='breeding_pairs'}
    crosscheck = []
    for r in records:
        key=r['site_id'],r['species_id'],r['season_start']
        if r['document_id']=='ASPA171_2024' and key in own:
            crosscheck.append(dict(site_id=r['site_id'],species_id=r['species_id'],season_start=int(r['season_start']),
                uba_value=float(own[key]['value']),aspa_value=float(r['value']),
                equal=float(own[key]['value'])==float(r['value']),independent_field_replication=False))
    return comparisons,crosscheck

def write_csv(path, rows):
    if not rows:
        return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--original-dir',type=Path,required=True)
    p.add_argument('--official-records',type=Path,default=ROOT/'inputs/maxwell_official_report_records_v9.csv')
    p.add_argument('--official-documents-dir',type=Path)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    folder=args.original_dir/'source' if (args.original_dir/'source').exists() else args.original_dir
    for name,expected in PINS.items():
        if digest(folder/name)!=expected:
            raise ValueError('source SHA mismatch: '+name)
    obs=read_csv(folder/'observations_p1.csv')+read_csv(folder/'observations_p2.csv')
    if len(obs)!=5487:
        raise ValueError('original observation count changed')
    paired,audit=stage_pairs(obs)
    focal=[r for r in paired if r['site_id'] in FOCAL_SITES and r['species_id'] in FOCAL_SPECIES
        and r['season_start'] in FOCAL_SEASONS and r['citekey']==FOCAL_SOURCE and r['vantage']=='ground']
    comparison=neighbor_comparison(paired)
    if len(focal)!=40 or comparison['n_matched_seasons']!=10:
        raise ValueError('fixed ten-season source opportunity changed')
    alternate=other_source_counts(obs,focal)
    records=read_csv(args.official_records)
    check,cross=official_source_checks(records,focal)
    if args.official_documents_dir:
        for doc in {r['document_id'] for r in records}:
            expected={r['pdf_sha256'] for r in records if r['document_id']==doc}
            if len(expected)!=1 or digest(args.official_documents_dir/(doc+'.pdf')) not in expected:
                raise ValueError('official document hash mismatch: '+doc)
    reported=[r for r in records if r['measure']=='fledged_young_per_breeding_pair']
    out=dict(schema=1,status='POST_EXPLORATION_RECORDED_CHICK_OUTPUT_NOT_CERTIFIED_FLEDGING',
        source_sha256=PINS, official_transcription_sha256=digest(args.official_records),
        original_stage_pair_audit=audit,primary_comparison=comparison,
        original_stage_inventory_by_species=dict(Counter(r['species_id'] for r in paired)),
        original_stage_chronology=dict(Counter(r['chronology'] for r in paired)),
        focal_chronology=dict(Counter(r['chronology'] for r in focal)),
        alternate_original_source_count_records=alternate,
        official_barton_nests_vs_original=dict(overlap=len(check),matches=sum(r['source_values_equal'] for r in check),
            discrepancies=[r for r in check if not r['source_values_equal']]),
        official_barton_cross_document_nests=cross,
        recent_reported_fledged_per_breeding_pair=reported,
        limitations=[
          'MAPPPD chicks label alone does not certify fledging, survival or survey extent.',
          'Focal raw dates lack month/day and stage ordering is unverified; same season is not same survey.',
          'Sources can report different nest counts; no newer denominator replaces the original same-source ratio.',
          'Published success ratios are rounded; no integer fledgling count is back-calculated.',
          'Both official reports can reuse Korean field observations and are not independent biological replications.',
          'Similar chick output cannot identify adult/juvenile survival, dispersal, competition or density mechanisms.',
          'No climate effect, p values, causal demographic or next-year recruitment model is fitted.',
          'Original V1--V8 results, frozen papers and the 216-test correction are unchanged.',
        ])
    write_csv(args.out/'source_stage_pairs_v9.csv',paired)
    write_csv(args.out/'ardley_barton_recorded_chick_output_v9.csv',focal)
    write_csv(args.out/'original_alternate_counts_v9.csv',alternate)
    write_csv(args.out/'official_nest_source_comparison_v9.csv',check)
    (args.out/'recorded_chick_output_v9_result.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('RECORDED_CHICK_OUTPUT_V9='+json.dumps(out,allow_nan=False),flush=True)

if __name__=='__main__':main()
