"""Native QA support at frozen recurrent historical guano coordinates.

One lowest catalog-cloud scene per site-season, with date/id tie breaking.
This is an image-availability pilot, not exhaustive clear-scene coverage.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import planetary_computer
from pyproj import Transformer
import rasterio
import requests


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--roi', type=Path, required=True)
    p.add_argument('--catalog', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    raw = args.catalog.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '575dc514c6103b1aaefb0bce1bf7f5084aedc5d2c4edb3519d0ac03af82a2750'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = next(n for n in z.namelist() if n.endswith('original_88_L8_real_scene_metadata_no_Y.csv'))
        catalog = pd.read_csv(z.open(name))
    roi = pd.read_csv(args.roi)
    catalog = catalog[catalog.period.eq('new') & catalog.site_id.isin(roi.site_id)].copy()
    chosen = catalog.sort_values(['eo_cloud_cover_scene_percent', 'source_scene_datetime', 'scene_id']).drop_duplicates(['site_id', 'season'])
    chosen.to_csv(args.out / 'fixed_scene_selection.csv', index=False, lineterminator='\n')
    jobs = list(chosen.groupby('scene_id', sort=True))

    def one(job):
        scene, selected = job
        receipt = args.out / (scene + '_bounds_checked.json')
        if receipt.exists():
            return json.loads(receipt.read_text())
        rows = []
        try:
            response = requests.get('https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l2/items/' + scene, timeout=45)
            response.raise_for_status()
            item = response.json()
            assert item['id'] == scene and item['properties']['platform'] == 'landsat-8'
            points = roi[roi.site_id.isin(selected.site_id)].copy().reset_index(drop=True)
            arrays, keys = [], None
            missing = np.zeros(len(points), dtype=bool)
            for band in ('qa_pixel', 'qa_radsat'):
                url = planetary_computer.sign(item['assets'][band]['href'])
                with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT=45):
                    with rasterio.open(url) as source:
                        x, y = Transformer.from_crs('EPSG:3031', source.crs, always_xy=True).transform(points.east.to_numpy(), points.north.to_numpy())
                        indexes = [source.index(a, b) for a, b in zip(x, y)]
                        if keys is None:
                            keys = indexes
                        else:
                            assert indexes == keys
                        sampled = np.ma.array(list(source.sample(list(zip(x, y)), indexes=1, masked=True)))[:, 0]
                        missing |= np.ma.getmaskarray(sampled)
                        missing |= np.array([r < 0 or c < 0 or r >= source.height or c >= source.width for r, c in indexes])
                        arrays.append(np.ma.filled(sampled, 0).astype(int))
            qa, sat = arrays
            valid = (~missing) & ((qa & sum(1 << i for i in (0, 1, 2, 3, 4, 5, 7))) == 0) & ((sat & (127 | (1 << 11))) == 0)
            points['native_key'] = [str(k) for k in keys]
            points['valid'] = valid
            for row in selected.itertuples():
                sub = points[points.site_id == row.site_id].drop_duplicates('native_key')
                rows.append({'site_id': row.site_id, 'season': int(row.season), 'region': row.original_region,
                             'scene_id': scene, 'historical_points': int((points.site_id == row.site_id).sum()),
                             'distinct_native_pixels': len(sub), 'qa_valid_native_pixels': int(sub.valid.sum()), 'error': None})
        except Exception as exc:
            rows = [{'site_id': r.site_id, 'season': int(r.season), 'region': r.original_region,
                     'scene_id': scene, 'qa_valid_native_pixels': None, 'error': str(exc)[:240]} for r in selected.itertuples()]
        receipt.write_text(json.dumps(rows), encoding='utf-8', newline='\n')
        return rows

    rows = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, result in enumerate(pool.map(one, jobs), 1):
            rows.extend(result)
            pd.DataFrame(rows).to_csv(args.out / 'recurrent_roi_native_qa.csv', index=False, lineterminator='\n')
            if i % 10 == 0 or i == len(jobs):
                print('scenes', i, '/', len(jobs), 'site-seasons', len(rows), flush=True)


if __name__ == '__main__':
    main()
