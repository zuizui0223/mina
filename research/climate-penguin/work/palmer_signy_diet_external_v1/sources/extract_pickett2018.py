#!/usr/bin/env python3
"""Extract Pickett et al. (2018) Table 1 and verify against a second retrieval.

Inputs are saved representations of the same primary publication. No network
access is needed to re-run. This writes plain CSV/JSON source-data intermediates,
not a workbook. All percentages use percentage-point units (0..100).
"""
from pathlib import Path
from xml.etree import ElementTree as ET
from decimal import Decimal
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
XML_PATH = ROOT / 'pickett2018_europepmc.xml'
WEB_PATH = ROOT / 'web_wiley_table1_excerpt.txt'
DOI = '10.1002/ece3.4445'
TABLE_ID = 'ece34445-tbl-0001'
SOURCE_URL = 'https://onlinelibrary.wiley.com/doi/10.1002/ece3.4445'
XML_URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6202752/fullTextXML'
PREY = {
    'Euphausia superba (%)': 'e_superba',
    'Thysanoessa macrura (%)': 't_macrura',
    'Unidentified fish (%)': 'fish',
    'Other prey items (%)': 'other',
}
SPECIES = [('Adelie', 'Pygoscelis adeliae'), ('Gentoo', 'Pygoscelis papua')]
PATTERN = re.compile(r'([0-9]+(?:\.[0-9]+)?)\s*±\s*([0-9]+(?:\.[0-9]+)?)\s*\(([0-9]+(?:\.[0-9]+)?)\)')


def norm(s):
    return ' '.join(s.split())


def parsed_cell(cell):
    match = PATTERN.fullmatch(norm(cell))
    if match is None:
        raise ValueError(f'Unexpected diet cell: {cell!r}')
    return match.groups()


def bounds(display, percent_cap=False):
    """Conservative closed envelope conditional on nearest displayed precision."""
    d = Decimal(display)
    quantum = Decimal(1).scaleb(d.as_tuple().exponent)
    lower = max(Decimal('0'), d - quantum / 2)
    upper = d + quantum / 2
    if percent_cap:
        upper = min(Decimal('100'), upper)
    return format(lower, 'f'), format(upper, 'f'), format(quantum, 'f')


root = ET.parse(XML_PATH).getroot()
table = root.find(f'.//table-wrap[@id="{TABLE_ID}"]')
assert table is not None
xml_rows = table.findall('./table/tbody/tr')
assert len(xml_rows) == 24
long_rows = []
prey_label = None
for table_row, tr in enumerate(xml_rows, 1):
    cells = [''.join(td.itertext()).strip() for td in tr.findall('td')]
    if len(cells) == 8:
        prey_label = norm(cells.pop(0))
        assert prey_label in PREY
    assert len(cells) == 7 and prey_label is not None
    year = int(cells[0])
    for (species, latin), ci, ni in zip(SPECIES, (1, 3), (2, 4)):
        mean, sd, occurrence = parsed_cell(cells[ci])
        mean_lo, mean_hi, mean_q = bounds(mean, True)
        sd_lo, sd_hi, sd_q = bounds(sd)
        occ_lo, occ_hi, occ_q = bounds(occurrence, True)
        long_rows.append({
            'source_id': 'Pickett2018_Table1',
            'source_doi': DOI,
            'source_table_id': TABLE_ID,
            'source_table_row': table_row,
            'wiley_reader_line': 264 + table_row,
            'source_year_label': year,
            'season_start_year': year,
            'season_end_year': year + 1,
            'season_label': f'{year}/{str(year + 1)[-2:]}',
            'species': species,
            'scientific_name': latin,
            'prey_category': PREY[prey_label],
            'source_prey_label': prey_label,
            'n': int(cells[ni]),
            'mean_pct': mean,
            'sd_pct': sd,
            'occurrence_pct': occurrence,
            'mean_rounding_lower_pct': mean_lo,
            'mean_rounding_upper_pct': mean_hi,
            'mean_display_quantum_pp': mean_q,
            'sd_rounding_lower_pct': sd_lo,
            'sd_rounding_upper_pct': sd_hi,
            'sd_display_quantum_pp': sd_q,
            'occurrence_rounding_lower_pct': occ_lo,
            'occurrence_rounding_upper_pct': occ_hi,
            'occurrence_display_quantum_pp': occ_q,
            'raw_cell': cells[ci],
        })
assert len(long_rows) == 48

# Independent parsing of the publisher's web-reader table representation.
web_rows = []
web_prey = None
for line in WEB_PATH.read_text(encoding='utf-8').splitlines():
    m = re.match(r'^L(\d+): (.*)$', line)
    if not m or not 265 <= int(m.group(1)) <= 288:
        continue
    cells = [norm(x) for x in m.group(2).split('|')]
    if len(cells) == 8:
        web_prey = cells.pop(0)
        assert web_prey in PREY
    assert len(cells) == 7
    for (species, _), ci, ni in zip(SPECIES, (1, 3), (2, 4)):
        web_rows.append((int(cells[0]), species, PREY[web_prey],
                         int(cells[ni]), *parsed_cell(cells[ci])))
assert len(web_rows) == 48
xml_values = [(r['source_year_label'], r['species'], r['prey_category'],
               r['n'], r['mean_pct'], r['sd_pct'], r['occurrence_pct'])
              for r in long_rows]
assert xml_values == web_rows, 'Primary XML and publisher web table disagree'

wide_rows = []
for year in range(2009, 2015):
    for species, latin in SPECIES:
        items = [r for r in long_rows if r['season_start_year'] == year and r['species'] == species]
        assert len(items) == 4 and len({r['n'] for r in items}) == 1
        row = {
            'source_id': 'Pickett2018_Table1',
            'source_doi': DOI,
            'source_url': SOURCE_URL,
            'source_table_id': TABLE_ID,
            'source_year_label': year,
            'season_start_year': year,
            'season_end_year': year + 1,
            'season_label': f'{year}/{str(year + 1)[-2:]}',
            'species': species,
            'scientific_name': latin,
            'region': 'Palmer Station vicinity, Anvers Island region, western Antarctic Peninsula',
            'geographic_comparison_unit': 'same_region_different_primary_study_colonies',
            'sampling_phase': 'chick_rearing',
            'sample_n': items[0]['n'],
            'sample_n_status': ('table_total129_vs_methods128' if species == 'Gentoo' else 'table_total136_matches_methods136'),
            'composition_statistic': 'mean_of_diet_sample_wet_mass_percentages',
            'composition_unit': 'percent',
        }
        for item in items:
            p = item['prey_category']
            for k in ('mean_pct', 'sd_pct', 'occurrence_pct',
                      'mean_rounding_lower_pct', 'mean_rounding_upper_pct',
                      'source_table_row', 'raw_cell'):
                row[f'{p}_{k}'] = item[k]
        row['reported_composition_sum_pct'] = format(sum(Decimal(i['mean_pct']) for i in items), 'f')
        row['mean_display_quantum_pp'] = '0.1'
        row['sd_display_quantum_pp'] = '0.1'
        wide_rows.append(row)
assert len(wide_rows) == 12
assert len({(r['species'], r['season_start_year']) for r in wide_rows}) == 12

def write_csv(name, rows):
    with (ROOT / name).open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

write_csv('pickett2018_palmer_diet_species_season.csv', wide_rows)
write_csv('pickett2018_table1_long.csv', long_rows)

# Preserve a locally generated readable extraction without mislabelling it HTML.
excerpts = []
for sid in ('ece34445-sec-0003', 'ece34445-sec-0004', 'ece34445-sec-0008', 'ece34445-sec-0015'):
    sec = root.find(f'.//sec[@id="{sid}"]')
    excerpts.append(f"[{sid}] {''.join(sec.find('title').itertext())}")
    excerpts.extend(''.join(p.itertext()) for p in sec.findall('p'))
permissions = root.find('.//permissions')
excerpts.append('[article permissions] ' + ''.join(permissions.itertext()))
(ROOT / 'primary_source_excerpts.txt').write_text('\n\n'.join(excerpts) + '\n', encoding='utf-8')

sums = {s: sum(r['sample_n'] for r in wide_rows if r['species'] == s) for s, _ in SPECIES}
verification = {
    'retrieved_on': '2026-11-06',
    'source_doi': DOI,
    'source_url': SOURCE_URL,
    'xml_download_url': XML_URL,
    'pmc_url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6202752/',
    'xml_sha256': hashlib.sha256(XML_PATH.read_bytes()).hexdigest(),
    'xml_bytes': XML_PATH.stat().st_size,
    'web_table_excerpt_sha256': hashlib.sha256(WEB_PATH.read_bytes()).hexdigest(),
    'source_license': 'CC BY 4.0',
    'source_license_url': 'https://creativecommons.org/licenses/by/4.0/',
    'source_table_id': TABLE_ID,
    'primary_xml_table_rows': len(xml_rows),
    'species_season_rows': len(wide_rows),
    'species_season_prey_rows': len(long_rows),
    'second_representation_numeric_comparisons': 48 * 4,
    'second_representation_all_match': True,
    'n_same_across_prey_categories_in_each_species_season': True,
    'sample_n_totals_from_table': sums,
    'sample_n_totals_from_methods': {'Adelie': 136, 'Gentoo': 128},
    'unresolved_discrepancies': ['Gentoo Table 1 total n=129 versus methods n=128; no correction inferred'],
    'reported_composition_sums_pct': [
        {k: r[k] for k in ('species', 'season_label', 'reported_composition_sum_pct')}
        for r in wide_rows],
    'rounding_bounds': 'Closed conservative envelopes conditional on nearest rounding to displayed precision; percentage bounds clipped to 0..100. Not confidence intervals.',
    'data_is_aggregate': True,
    'individual_stomach_masses_obtained': False,
    'same_island_replication': False,
}
(ROOT / 'extraction_verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'wide_rows': len(wide_rows), 'long_rows': len(long_rows), '192_source_value_comparisons_match': True, 'n_totals': sums}, ensure_ascii=False))
