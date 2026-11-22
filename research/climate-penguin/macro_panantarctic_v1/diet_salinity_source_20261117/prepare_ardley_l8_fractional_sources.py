"""Cache public source metadata for the Ardley fractional-pixel experiment."""
import argparse
import json
from pathlib import Path

import requests
from remotezip import RemoteZip


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    if not (args.cache / 'zip_entries.json').exists():
        response = requests.get('https://zenodo.org/api/records/14503437', timeout=60)
        response.raise_for_status()
        source = response.json()['files'][0]
        assert source['size'] == 4109917595
        assert source['checksum'] == 'md5:62bb5a89ca7f5f06e54b74e26bf5de5d'
        url = source['links']['self']
        with RemoteZip(url) as archive:
            entries = [{'name': a.filename, 'offset': a.header_offset, 'size': a.compress_size,
                        'usize': a.file_size, 'crc': a.CRC, 'compression': a.compress_type}
                       for a in archive.infolist() if a.filename.startswith('Guano/')]
        (args.cache / 'zip_entries.json').write_text(json.dumps(entries), encoding='utf-8')
        (args.cache / 'zip_url.txt').write_text(url, encoding='utf-8')
    if not (args.cache / 'ardley_scenes.json').exists():
        response = requests.post('https://planetarycomputer.microsoft.com/api/stac/v1/search', json={
            'collections': ['landsat-c2-l2'], 'bbox': [-58.94, -62.23, -58.9, -62.2],
            'datetime': '2013-11-01T00:00:00Z/2018-03-01T00:00:00Z',
            'query': {'platform': {'eq': 'landsat-8'}}, 'limit': 1000}, timeout=60)
        response.raise_for_status()
        scenes = response.json()
        if any(link.get('rel') == 'next' for link in scenes.get('links', [])):
            raise ValueError('Catalog now requires pagination; do not silently truncate')
        assert all(s['properties']['platform'] == 'landsat-8' for s in scenes['features'])
        (args.cache / 'ardley_scenes.json').write_text(json.dumps(scenes), encoding='utf-8')


if __name__ == '__main__':
    main()
