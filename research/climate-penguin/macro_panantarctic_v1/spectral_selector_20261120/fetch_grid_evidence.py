"""Retrieve exact public supplementary inputs, preserving publisher bytes."""
import hashlib
import argparse
import gzip
import json
from pathlib import Path
import requests

root=Path(__file__).parent/'public_grid_evidence'
parser=argparse.ArgumentParser();parser.add_argument('--data-only',action='store_true');args=parser.parse_args()
for receipt in json.loads((root/'source_receipts.json').read_text()):
    path=root/receipt['file']
    if args.data_only and path.suffix in ('.pdf','.docx'):continue
    if path.exists():raw=path.read_bytes()
    elif path.with_suffix(path.suffix+'.gz').exists():raw=gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())
    else:
        response=requests.get(receipt['url'],timeout=90);response.raise_for_status();raw=response.content
    if hashlib.sha256(raw).hexdigest()!=receipt['sha256'] or len(raw)!=receipt['bytes']:
        raise ValueError('Publisher source identity changed: '+receipt['file'])
    path.write_bytes(raw)
    print('Verified',receipt['file'],len(raw))
