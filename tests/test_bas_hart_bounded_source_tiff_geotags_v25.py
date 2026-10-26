"""BAS source TIFF bounded HTTP range and publisher path integrity regression tests."""
from __future__ import annotations
import io
import sys
from pathlib import Path
import numpy as np
import pytest
import tifffile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_bas_hart_bounded_source_tiff_geotags_v25 as v25


def test_four_fixed_original_source_representative_TIFF_paths():
    records=[]
    for site,path in v25.FILE_NAMES.items():
        basename=path.split("/")[-1]
        records.append({
            "top_level_source_locality_folder":site,
            "original_archive_relative_path":path,
            "original_publisher_file_name":basename,
            "original_source_file_type":"tif",
            "original_publisher_archive_id":"id-"+site,
            "source_file_url_https":
                "https://ramadda.data.bas.ac.uk/repository/entry/get/"+
                basename+"?entryid=original"
        })
    records += [{"original_archive_relative_path":f"other_{i}",
                 "top_level_source_locality_folder":"Zavodovski",
                 "original_source_file_type":"tif"} for i in range(160)]
    source={"status":v25.SOURCE_STATUS,"original_all_file_metadata_only":records}
    selected=v25.source_image_paths(source)
    assert len(selected)==4
    assert set(selected)==set(v25.FILE_NAMES)


def test_unsupported_full_tiff_download_is_stopped_before_body_read(monkeypatch):
    class Resp:
        status_code=200
        headers={"Content-Type":"image/tiff","Content-Length":"400000000"}
        url="https://ramadda.data.bas.ac.uk/repository/entry/get/image.tif"
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def raise_for_status(self):return None
        def iter_content(self,*args):
            raise AssertionError("Unsafe unbounded image stream read attempted")
    class Fake:
        def __enter__(self):return self
        def __exit__(self,*a):return False
        def get(self,*a,**k):return Resp()
    monkeypatch.setattr(v25.requests,"Session",Fake)
    r=v25.fetch_bounded_original_tiff_header({
        "original_archive_relative_path":"image.tif",
        "original_publisher_archive_id":"test",
        "source_file_url_https":"https://ramadda.data.bas.ac.uk/repository/entry/get/image.tif"
    })
    assert r["status"]=="SOURCE_RANGE_NOT_SUPPORTED_FULL_IMAGE_NOT_DOWNLOADED"
    assert r["entire_original_source_image_downloaded"] is False


def test_tiff_in_bounded_partial_range_reads_only_IFD_metadata(monkeypatch):
    bio=io.BytesIO()
    tifffile.imwrite(bio,np.zeros((12,12),dtype=np.uint8))
    raw=bio.getvalue()
    assert len(raw)<v25.MAX_BYTES
    class Resp:
        status_code=206
        headers={"Content-Type":"image/tiff",
                 "Content-Range":f"bytes 0-{len(raw)-1}/{len(raw)}"}
        url="https://ramadda.data.bas.ac.uk/repository/entry/get/small.tif"
        def __enter__(self):return self
        def __exit__(self,*args):return False
        def raise_for_status(self):return None
        def iter_content(self,*args,**kwargs):
            yield raw
    class Fake:
        def __enter__(self):return self
        def __exit__(self,*a):return False
        def get(self,*a,**k):return Resp()
    monkeypatch.setattr(v25.requests,"Session",Fake)
    result=v25.fetch_bounded_original_tiff_header({
        "original_archive_relative_path":"small.tif",
        "original_publisher_archive_id":"test",
        "source_file_url_https":"https://ramadda.data.bas.ac.uk/repository/entry/get/small.tif"
    })
    assert result["status"]=="ORIGINAL_BAS_GEOTIFF_IFD_PARTIAL_HEADER_READ"
    assert result["original_TIFF_first_IFD_shape"]==[12,12]
    assert result["original_image_data_pixel_values_read"]==0
    assert result["original_TIFF_geo_bounds_and_nest_common_coverage_verified"] is False
