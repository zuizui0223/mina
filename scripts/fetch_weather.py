#!/usr/bin/env python3
"""Fetch frozen Palmer Station daily weather, with AMRDC transport discovery."""
from __future__ import annotations

import argparse
import hashlib
import re
import urllib.request
from urllib.parse import urljoin
from pathlib import Path

PACKAGE="knb-lter-pal.28.8"
DOI="10.6073/pasta/cddd3985350334b876cd7d6d1a5bc7bf"
ENTITY="375b34051b162d84516ec2d02f864675"
EDI_URLS=(
    f"https://pasta.lternet.edu/package/data/eml/knb-lter-pal/28/8/{ENTITY}",
    f"http://pasta.lternet.edu/package/data/eml/knb-lter-pal/28/8/{ENTITY}",
)
AMRDC_BASE="https://amrc.ssec.wisc.edu/data/ftp/pub/palmer/climatology/"
UA="Mozilla/5.0 mina-island-reassembly/0.5"


def fetch(url: str) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read()


def valid_edi(data: bytes) -> bool:
    head=data[:2500]
    return len(data)>1000 and b"Date" in head and (b"Rainfall" in head or b"Precip" in head)


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("out",type=Path)
    args=parser.parse_args()
    failures=[]
    for url in EDI_URLS:
        try:
            data=fetch(url)
        except Exception as exc:
            failures.append(f"{url}: {exc!r}")
            continue
        if valid_edi(data):
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_bytes(data)
            print(f"scientific_package={PACKAGE}")
            print(f"doi={DOI}")
            print(f"entity={ENTITY}")
            print("transport=EDI direct")
            print(f"transport_url={url}")
            print(f"sha256={hashlib.sha256(data).hexdigest()}")
            print(f"bytes={len(data)}")
            return 0
        failures.append(f"{url}: invalid bytes={len(data)}")

    # EDI currently returns 403 to anonymous CI. Discover the upstream AMRDC
    # climatology archive used by the same Palmer Station weather product.
    try:
        listing=fetch(AMRDC_BASE).decode("utf-8","replace")
    except Exception as exc:
        raise RuntimeError(
            "EDI weather unavailable and AMRDC archive listing failed. "
            + " | ".join(failures) + f" | AMRDC: {exc!r}"
        ) from exc

    hrefs=[]
    for href in re.findall(r'href=["\']([^"\']+)["\']',listing,re.I):
        if href.startswith("?") or href in {"../","/"}:
            continue
        hrefs.append(urljoin(AMRDC_BASE,href))
    print(f"scientific_package={PACKAGE}")
    print(f"doi={DOI}")
    print(f"entity={ENTITY}")
    print("EDI_failures=" + " | ".join(failures))
    print(f"amrdc_listing_sha256={hashlib.sha256(listing.encode()).hexdigest()}")
    print(f"amrdc_link_count={len(hrefs)}")
    print("amrdc_links=")
    for url in hrefs[:200]:
        print(url)

    raise RuntimeError(
        "EDI entity is unavailable; AMRDC transport inventory printed above. "
        "Freeze a deterministic AMRDC reconstruction rule before opening values."
    )


if __name__=="__main__":
    raise SystemExit(main())
