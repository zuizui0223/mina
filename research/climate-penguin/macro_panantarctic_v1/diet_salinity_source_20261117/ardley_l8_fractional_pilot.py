"""Match dated public guano annotations to native Landsat 8 pixels.

The response is annotated area fraction. Unannotated pixels are not certified
non-guano controls. No isotope outcome is produced by this diagnostic.
"""
import argparse
import io
import json
import struct
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import planetary_computer
import rasterio
import requests
import shapefile
from pyproj import CRS, Transformer
from rasterio.windows import from_bounds
from shapely.geometry import box, shape
from shapely.ops import transform, unary_union
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr

BANDS = ['blue', 'green', 'red', 'nir08', 'swir16', 'swir22']


def get_masks(cache):
    entries = json.loads((cache / 'zip_entries.json').read_text())
    start = min(x['offset'] for x in entries)
    end = max(x['offset'] + x['size'] + len(x['name'].encode()) + 100 for x in entries)
    target = cache / 'guano_source_range.bin'
    if not target.exists():
        response = requests.get((cache / 'zip_url.txt').read_text(),
                                headers={'Range': f'bytes={start}-{end}'}, timeout=120)
        response.raise_for_status()
        if response.status_code != 206 or not response.headers['Content-Range'].startswith(f'bytes {start}-'):
            raise ValueError('Provider did not return the requested byte range')
        target.write_bytes(response.content)
    blob = target.read_bytes()
    members = {}
    for entry in entries:
        offset = entry['offset'] - start
        header = struct.unpack_from('<IHHHHHIIIHH', blob, offset)
        assert header[0] == 0x04034B50
        first = offset + 30 + header[-2] + header[-1]
        data = blob[first:first + entry['size']]
        if entry['compression'] == 8:
            data = zlib.decompress(data, -15)
        elif entry['compression'] != 0:
            raise ValueError('Unsupported compression')
        assert len(data) == entry['usize'] and zlib.crc32(data) == entry['crc']
        members[entry['name']] = data
    masks = {}
    for name in sorted(members):
        if not name.endswith('.shp'):
            continue
        stem = name[:-4]
        assert CRS.from_wkt(members[stem + '.prj'].decode()).to_epsg() == 32721
        date = name.split('/')[-1].split('_')[1]
        species = name.split('/')[-1].split('_')[2].split('.')[0]
        with shapefile.Reader(shp=io.BytesIO(members[name]),
                              shx=io.BytesIO(members[stem + '.shx']),
                              dbf=io.BytesIO(members[stem + '.dbf'])) as reader:
            geometry = unary_union([shape(s.__geo_interface__) for s in reader.shapes()])
        masks.setdefault(date, {})[species] = geometry
    assert len(masks) == 22
    return masks


def read_scene(item, extent, cache):
    path = cache / (item['id'] + '.npz')
    if path.exists():
        return dict(np.load(path))
    arrays = []
    transform_values = None
    for band in BANDS + ['qa_pixel', 'qa_radsat']:
        url = planetary_computer.sign(item['assets'][band]['href'])
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT=60):
            with rasterio.open(url) as source:
                projector = Transformer.from_crs('EPSG:32721', source.crs, always_xy=True)
                native = transform(projector.transform, extent)
                window = from_bounds(*native.bounds, source.transform).round_offsets().round_lengths()
                values = source.read(1, window=window)
                if transform_values is None:
                    transform_values = tuple(source.window_transform(window))
                    crs = str(source.crs)
                else:
                    assert tuple(source.window_transform(window)) == transform_values
                if band in BANDS:
                    metadata = item['assets'][band]['raster:bands'][0]
                    values = values.astype(float) * metadata['scale'] + metadata['offset']
                arrays.append(values)
    data = {'bands': np.stack(arrays[:6]), 'qa': arrays[6], 'sat': arrays[7],
            'transform': np.array(transform_values), 'crs': np.array(crs)}
    np.savez_compressed(path, **data)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--local-qa-csv', type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    masks = get_masks(args.cache)
    scenes = json.loads((args.cache / 'ardley_scenes.json').read_text())['features']
    pairs = []
    for date in sorted(masks):
        day = pd.Timestamp(date)
        choices = []
        for item in scenes:
            difference = abs((pd.Timestamp(item['properties']['datetime']).tz_localize(None) - day).total_seconds()) / 86400
            if difference <= 8:
                choices.append((item['properties']['eo:cloud_cover'], difference, item['id'], item))
        if choices:
            cloud, difference, _, item = min(choices, key=lambda x: x[:3])
            pairs.append({'date': date, 'scene_id': item['id'], 'difference_days': difference,
                          'scene_cloud_percent': cloud, 'item': item})
    # One annotation per scene; closest date wins, so pixels are not duplicated as replicates.
    selected = {}
    for pair in sorted(pairs, key=lambda x: (x['difference_days'], x['date'])):
        selected.setdefault(pair['scene_id'], pair)
    if args.local_qa_csv:
        local = pd.read_csv(args.local_qa_csv).set_index('scene_id')
        selected = {}
        for item in scenes:
            scene_id = item['id']
            if scene_id not in local.index or not (local.loc[scene_id, 'valid_pixels'] > 0):
                continue
            timestamp = pd.Timestamp(item['properties']['datetime']).tz_localize(None)
            difference, date = min((abs((timestamp - pd.Timestamp(d)).total_seconds()) / 86400, d) for d in masks)
            if difference > 8:
                continue
            day = timestamp.strftime('%Y%m%d')
            fraction = local.loc[scene_id, 'valid_pixels'] / local.loc[scene_id, 'window_pixels']
            pair = {'date': date, 'scene_id': scene_id, 'difference_days': difference,
                    'scene_cloud_percent': item['properties']['eo:cloud_cover'], 'item': item,
                    'local_QA_valid_fraction': float(fraction)}
            if day not in selected or fraction > selected[day]['local_QA_valid_fraction']:
                selected[day] = pair
    pd.DataFrame([{k: v for k, v in p.items() if k != 'item'} for p in pairs]).to_csv(
        args.out / 'all_22_date_matches.csv', index=False, lineterminator='\n')
    extent = box(*unary_union([g for day in masks.values() for g in day.values()]).bounds).buffer(150).envelope
    records, receipts = [], []
    for pair in sorted(selected.values(), key=lambda x: x['date']):
        print('reading', pair['date'], pair['scene_id'], flush=True)
        data = read_scene(pair['item'], extent, args.cache)
        affine = rasterio.Affine(*data['transform'][:6])
        projector = Transformer.from_crs('EPSG:32721', str(data['crs']), always_xy=True)
        geometries = {s: transform(projector.transform, g) for s, g in masks[pair['date']].items()}
        qa, sat = data['qa'].astype(int), data['sat'].astype(int)
        valid = ((qa & sum(1 << i for i in (0, 1, 2, 3, 4, 5, 7))) == 0) & ((sat & (127 | (1 << 11))) == 0)
        valid &= np.isfinite(data['bands']).all(axis=0)
        count = {s: 0 for s in geometries}
        fractions = {s: [] for s in geometries}
        for row, col in np.ndindex(qa.shape):
            x0, y0 = affine * (col, row)
            x1, y1 = affine * (col + 1, row + 1)
            pixel = box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            cover = {s: pixel.intersection(g).area / pixel.area for s, g in geometries.items()}
            for species, fraction in cover.items():
                count[species] += int(fraction > 0)
                if valid[row, col] and fraction > 0:
                    fractions[species].append(fraction)
            if valid[row, col]:
                records.append({'date': pair['date'], 'season': int(pair['date'][:4]) - int(int(pair['date'][4:6]) < 7),
                    'scene_id': pair['scene_id'], 'row': row, 'col': col,
                    **{s + '_annotated_fraction': f for s, f in cover.items()},
                    **dict(zip(BANDS, data['bands'][:, row, col]))})
        receipt = {k: v for k, v in pair.items() if k != 'item'}
        receipt.update({'qa_valid_pixels': int(valid.sum()), 'window_pixels': int(valid.size),
                        'crs': str(data['crs']), 'pixel_width_m': abs(affine.a),
                        'positive_pixels_before_QA': count, 'positive_fractions_after_QA': fractions})
        receipts.append(receipt)
        (args.out / 'scene_receipts.json').write_text(json.dumps(receipts, indent=2), encoding='utf-8', newline='\n')
        pd.DataFrame(records).to_csv(args.out / 'native_L8_annotated_fraction_pixels.csv', index=False, lineterminator='\n')
    frame = pd.DataFrame(records)
    scores = []
    for species in ('adelie', 'gentoo'):
        target = species + '_annotated_fraction'
        for season in sorted(frame.season.unique()):
            train, test = frame[frame.season != season], frame[frame.season == season]
            if train.empty or test.empty or train[target].max() == 0:
                continue
            model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
            model.fit(train[BANDS], train[target])
            predicted = model.predict(test[BANDS])
            mse = float(np.mean((test[target] - predicted) ** 2))
            baseline = float(np.mean((test[target] - train[target].mean()) ** 2))
            scores.append({'species': species, 'heldout_season': int(season), 'test_pixels': len(test),
                           'positive_test_pixels': int((test[target] > 0).sum()),
                           'mse': mse, 'train_mean_mse': baseline,
                           'skill_vs_train_mean': 1 - mse / baseline if baseline else None,
                           'spearman': float(spearmanr(test[target], predicted).statistic) if test[target].nunique() > 1 else None})
    (args.out / 'fractional_annotation_prediction.json').write_text(json.dumps(scores, indent=2), encoding='utf-8', newline='\n')
    print(json.dumps(scores, indent=2), flush=True)


if __name__ == '__main__':
    main()
