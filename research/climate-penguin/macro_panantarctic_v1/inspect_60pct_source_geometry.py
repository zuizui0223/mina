#!/usr/bin/env python3
"""Post-result diagnostic of predeclared full-grid ring failure; no new thresholds."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("result",type=Path)
    args=ap.parse_args()
    result=json.loads(args.result.read_text(encoding="utf-8"))
    audit=result["full_contour_component_audit"]
    print("ORIGINAL_60PCT_GEOMETRY_RESULT="+json.dumps({
      "source_verified":result["source"]["baseline_595_site_reconstruction"],
      "n_source_files":result["source"]["original_monthly_ice_files_sha_verified"],
      "paired_first_last_AugNov":[x for x in audit if x["paired_start"]=="1991-2000"
                                   and x["paired_end"]=="2011-2020"
                                   and x["climate_month_basis"]=="aug_nov"],
      "paired_first_last_September":[x for x in audit if x["paired_start"]=="1991-2000"
                                   and x["paired_end"]=="2011-2020"
                                   and x["climate_month_basis"]=="september"],
      "all_geometry":[{"start":x["paired_start"],"end":x["paired_end"],"basis":x["climate_month_basis"],
          "period":x["period"],"status":x["status"],
          "valid_original_marine_cells":x["n_exact_common_source_valid_ocean_pixels"],
          "n_large":x.get("large_contour_components"),
          "best_coverage":x.get("best_coverage"),
          "selected_contour_sectors":x.get("selected_contour_sectors"),
          "selected_contour_vertices":x.get("selected_contour_vertices")}
          for x in audit],
    },ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
