"""Prospectively specified GIS *description*, not evidence of ecological causality.

Run only on actual-year, common-coverage, equal-CRS colony polygon layers
and a separately audited common-area mask. Never treat copied/cloud-filled
polygon geometry as a distinct observation at the labelled year.
"""
import argparse
import json
from pathlib import Path


def union_geoms(geometries):
    from shapely.ops import unary_union
    geoms = list(geometries)
    if not geoms or any(g is None or g.is_empty or not g.is_valid for g in geoms):
        raise ValueError('Empty/invalid input geometry: stop; no silent repair.')
    return unary_union(geoms)


def audit_provenance(receipt, early_year, late_year):
    if not isinstance(receipt, dict):
        raise ValueError('Provenance receipt is mandatory.')
    if receipt.get('observed_years') != [early_year, late_year]:
        raise ValueError('Source dates do not match both analysis years.')
    mandatory = ('original_year_for_both_species', 'common_valid_coverage_mask',
                 'cloud_infill_excluded', 'coordinate_registration_audited',
                 'source_layers_species_verified')
    if not all(receipt.get(k) is True for k in mandatory):
        raise ValueError('STOP: source/coverage provenance gate unresolved.')


def compute_exchange(chin_early, chin_late, mac_early, mac_late, support):
    """Area decomposition, without movement, individual or competition inference."""
    inputs = [chin_early, chin_late, mac_early, mac_late, support]
    if any(g is None or g.is_empty or not g.is_valid for g in inputs):
        raise ValueError('Nonempty valid GIS geometries required.')
    c0, c1, m0, m1 = [g.intersection(support) for g in inputs[:4]]
    lost_c = c0.difference(c1)
    gained_m = m1.difference(m0)
    gained_c = c1.difference(c0)
    lost_m = m0.difference(m1)
    converted = gained_m.intersection(lost_c)
    simultaneous = gained_m.intersection(c0.intersection(c1))
    no_c_at_start = gained_m.difference(c0)
    reverse = gained_c.intersection(lost_m)
    a = lambda g: round(g.area, 6)
    g_area = gained_m.area
    components = [converted.area, simultaneous.area, no_c_at_start.area]
    if abs(sum(components) - g_area) > max(1e-7, 1e-8 * g_area):
        raise AssertionError('Spatial partition incomplete')
    return {
        'units': 'm2 (provided audited projected CRS)',
        'chin_area_early_m2': a(c0), 'chin_area_late_m2': a(c1),
        'mac_area_early_m2': a(m0), 'mac_area_late_m2': a(m1),
        'chin_lost_area_m2': a(lost_c),
        'mac_gained_area_m2': a(gained_m),
        'mac_gain_on_chin_lost_m2': a(converted),
        'mac_gain_on_persistent_chin_m2': a(simultaneous),
        'mac_gain_without_chin_at_start_m2': a(no_c_at_start),
        'chin_gain_on_mac_lost_m2': a(reverse),
        'exchange_fraction_of_mac_gain': (round(converted.area / g_area, 6)
                                          if g_area > 0 else None),
        'reciprocal_exchange_fraction_of_chin_loss':
            (round(converted.area / lost_c.area, 6) if lost_c.area > 0 else None),
        'status': 'DESCRIPTIVE_ONLY_NO_CAUSAL_IDENTIFICATION',
    }


def read_layer(path, label):
    import geopandas as gpd
    frame = gpd.read_file(path)
    if frame.empty or frame.crs is None:
        raise ValueError(f'{label}: no geometry or missing CRS')
    if frame.crs.to_epsg() != 32726:
        raise ValueError(f'{label}: EPSG:32726 required, found {frame.crs}')
    return union_geoms(frame.geometry)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--chin-early', required=True)
    p.add_argument('--chin-late', required=True)
    p.add_argument('--mac-early', required=True)
    p.add_argument('--mac-late', required=True)
    p.add_argument('--support-mask', required=True)
    p.add_argument('--provenance-json', required=True)
    p.add_argument('--early-year', type=int, required=True)
    p.add_argument('--late-year', type=int, required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    allowed = [(2011, 2016), (2016, 2020), (2020, 2022), (2022, 2025)]
    if (args.early_year, args.late_year) not in allowed:
        raise ValueError(f'Only predeclared intervals permitted: {allowed}')
    receipt = json.loads(Path(args.provenance_json).read_text(encoding='utf-8'))
    audit_provenance(receipt, args.early_year, args.late_year)
    geometries = [read_layer(v, n) for n, v in [
        ('chin-early', args.chin_early), ('chin-late', args.chin_late),
        ('mac-early', args.mac_early), ('mac-late', args.mac_late),
        ('support', args.support_mask)]]
    result = compute_exchange(*geometries)
    result['years'] = [args.early_year, args.late_year]
    result['source_doi'] = '10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308'
    Path(args.out).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
