#!/usr/bin/env python3
"""Fetch the frozen Palmer Station daily weather dataset used by the local-filter test."""
from __future__ import annotations

import argparse
import hashlib
import urllib.error
import urllib.request
from pathlib import Path

PACKAGE="knb-lter-pal.28.8"
DOI="10.6073/pasta/cddd3985350334b876cd7d6d1a5bc7bf"
ENTITY="375b34051b162d84516ec2d02f864675"
CANDIDATES=(
    f"https://pasta.lternet.edu/package/data/eml/knb-lter-pal/28/8/{ENTITY}",
    f"http://pasta.lternet.edu/package/data/eml/knb-lter-pal/28/8/{ENTITY}",
)
UA="Mozilla/5.0 mina-island-reassembly/0.5"


def fetch(url: str) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/csv,text/plain,*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read()


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("out",type=Path)
    args=parser.parse_args()
    failures=[]
    data=None
    used=None
    for url in CANDIDATES:
        try:
            candidate=fetch(url)
        except Exception as exc:
            failures.append(f"{url}: {exc!r}")
            continue
        text=candidate[:500].decode("utf-8","replace")
        if len(candidate)<1000 or "not authorized" in text.lower():
            failures.append(f"{url}: rejected response bytes={len(candidate)} head={text!r}")
            continue
        data=candidate
        used=url
        break
    if data is None:
        raise RuntimeError(
            "Palmer weather entity could not be fetched from frozen EDI endpoints. "
            + " | ".join(failures)
        )
    if b"Date" not in data[:1000] or b"Precip" not in data[:2000]:
        raise RuntimeError("weather entity lacks expected Date/Precipitation schema")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(data)
    print(f"package={PACKAGE}")
    print(f"doi={DOI}")
    print(f"entity={ENTITY}")
    print(f"transport_url={used}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    print("first_lines=")
    for line in data.decode("utf-8-sig","replace").splitlines()[:4]:
        print(line[:1000])
    return 0


if __name__=="__main__":
    raise SystemExit(main())
