"""Check all L8 scenes within eight days of the 22 annotation dates.

Use local QA, rather than whole-scene cloud percentage, to select source images.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import numpy as np
import pandas as pd
import planetary_computer
from pyproj import Transformer
import rasterio
from rasterio.windows import from_bounds
from shapely.geometry import box
from shapely.ops import transform, unary_union

from ardley_l8_fractional_pilot import get_masks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    masks = get_masks(args.cache)
    extent = box(*unary_union([g for day in masks.values() for g in day.values()]).bounds).buffer(150).envelope
    scenes = json.loads((args.cache / 'ardley_scenes.json').read_text())['features']
    candidates = [s for s in scenes if any(
        abs((pd.Timestamp(s['properties']['datetime']).tz_localize(None) - pd.Timestamp(d)).total_seconds()) / 86400 <= 8
        for d in masks)]

    def one(item):
        receipt = args.cache / (item['id'] + '_local_qa.json')
        if receipt.exists():
            return json.loads(receipt.read_text())
        try:
            values = []
            for band in ['qa_pixel', 'qa_radsat']:
                url = planetary_computer.sign(item['assets'][band]['href'])
                with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT=45):
                    with rasterio.open(url) as source:
                        projected = transform(Transformer.from_crs('EPSG:32721', source.crs, always_xy=True).transform, extent)
                        window = from_bounds(*projected.bounds, source.transform).round_offsets().round_lengths()
                        values.append(source.read(1, window=window).astype(int))
            qa, sat = values
            valid = ((qa & sum(1 << i for i in (0, 1, 2, 3, 4, 5, 7))) == 0) & ((sat & (127 | (1 << 11))) == 0)
            result = {'scene_id': item['id'], 'valid_pixels': int(valid.sum()), 'window_pixels': int(valid.size), 'error': None}
        except Exception as exc:
            result = {'scene_id': item['id'], 'valid_pixels': None, 'error': str(exc)[:300]}
        receipt.write_text(json.dumps(result), encoding='utf-8', newline='\n')
        return result

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = []
        for result in pool.map(one, candidates):
            rows.append(result)
            print(result, flush=True)
    pd.DataFrame(rows).to_csv(args.cache / 'all_69_local_qa.csv', index=False, lineterminator='\n')


if __name__ == '__main__':
    main()
