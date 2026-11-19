# V24 — NOAA ERSSTv6 winter SST environmental mechanism gate: STOP

**2026-10-21.** This is an executed independent NOAA original marine environmental-source analysis, not a new regression on the three Gentoo islands. It was designed AFTER observing V23 near/far correlations and is explicitly exploratory. [Frozen V24 contract](../contracts/NOAA_ERSSTV6_GENTOO_WINTER_V24.md) and [source original GitHub Actions #39449995433](https://github.com/zuizui0223/mina/actions/runs/39449995433) document the exact attempted grid, 2009–2019 source period, fixed winter July–September (months 7/8/9), and original 8 bird growth windows 2011–2018.

## Executed source
- Downloaded NOAA/PSL **current ERSSTv6** monthly SST 2° original official THREDDS NCSS subset at -62 to -52 S, 312 to 326 E, 2009–2019, 56,798 original netCDF bytes, with valid netCDF signature and Celsius source units. Latest subset binary SHA256 f1cce1d84c1f08e13f8e5267771c0340c86519a7fb839f6143d7d3c6c9722b12. The earlier original request returned the same byte count with a different file SHA (c45f48c9ff1f9be1b72f8ac5a7cb394be67e24ac6e967466b2d120a96161881a); generated netCDF file-level digest is not established to be stable, and no post-hoc source substitution is made.
- Independently original-source pinned BAS Gentoo V23 near-far contrast was reproduced exactly at **+1.0154800142899**, with exactly 8 common annual-growth start years.
- Closest verified 2° gridded regional SST centers: Bird Island **54°S, 38°W**, Maiviken **54°S, 36°W**, Signy **60°S, 46°W**. These are NOAA regional open-water reconstruction grid centers, **not observed nesting beaches/krill foraging tracks**.
- Valid complete 2011–2019 July–September winter-year coverage: Bird Island **9/9 years**; Maiviken **9/9**; Signy **8/9**. NOAA Signy 2011 September regional SST cell is **NONFINITE_SOURCE_VALUE**, confirmed on source re-read: neither zero°C nor valid SST, not an observed ice-concentration value. Other required cells were source valid. Do NOT assume the origin of the nonfinite source field is definitively sea ice; ERSST input/mask processing also matters.

## Scientific decision

**STOP_INCOMPLETE_ORIGINAL_ERSST_WINTER_DATA.** The predeclared environmental analysis required all three original July–September monthly SST values for all 9 winters spanning the 8 V23 growth windows. One original source value was nonfinite, so **no winter ΔSST across-sites correlations and NO Gentoo growth–SST correlation were computed**. No missing-value interpolation, adjacent-cell replacement, alternative winter months, ice-edge recoding, or cherry-picked shorter subset occurred. This is an environmental support failure, not evidence for or against temperature causing penguin demographic synchrony.

NOAA OISSTv2.1 (0.25° gridded SST and sea-ice coverage, official NOAA NCEI [OISST product](https://www.ncei.noaa.gov/products/optimum-interpolation-sst)) is a separate possible *a priori new* marine dataset, but must be frozen as a new source and physical hypothesis before any estimates. A conceptual climate predictor alone does not identify causation with 3 physical landmasses and 8 adjacent-year bird windows.

[Machine-readable original source QA and STOP](../results/NOAA_ERSSTV6_BAS_GENTOO_WINTER_V24.json) · [Original strict no-missing test](../tests/test_noaa_ersstv6_gentoo_winter_v24.py).
