# Prey accessibility is prior art; island breeding-space and independent resources remain the new research gap

2026-10-31 — mina / research-climate-penguin, Draft PR #206 only.

## What is ALREADY established

- Rusch, Lindstrøm, Krafft & Lowther, **"Chinstrap penguins prioritize prey accessibility over absolute abundance"**, *ICES Journal of Marine Science*, DOI [10.1093/icesjms/fsag115](https://doi.org/10.1093/icesjms/fsag115), published **2026-07-07**. Study: 2022 Monroe Island 31 usable animals and 2023 Powell Island 14, acoustic krill surveys and animal-borne GPS + 1Hz TDR, diel vertical prey accessibility, foraging habitat shaped by encounter depth and energetics rather than only maximum biomass. The underlying full data are NOT freely available; the authors' Data availability section specifies IMR/NPI **request and collaboration agreements**. Do not claim free access or download/source calibrated prey consumption from the paper alone.
- Schoombie et al. 2024, "Identifying prey capture events of a free-ranging marine predator using bio-logger data and deep learning", *Royal Society Open Science*, DOI [10.1098/rsos.240271](https://doi.org/10.1098/rsos.240271). Video-labelled Monroe2022/Powell2023 accelerometer + TDR, **41 individuals**, approximate **23,000** observed prey-capture events in ~151 hours video / 3184 dives, validated individual capture CNN/VNet. Public EXAMPLE and CODE (VANTAGE DOI [10.25375/uct.25415857](https://doi.org/10.25375/uct.25415857)), not full model calibration/raw videos for every individual. Existing BAS 2011-19 v2 TDR+GPS includes no accelerometers, so don't directly apply these classifiers to uncalibrated 1Hz pressure.
- IMR [2023 survey report](https://www.hi.no/en/hi/nettrapporter/toktrapport-en-2023-8) describes **Powell 2023 penguin tagging plus about 21 days Sailbuoy echosounder near chinstrap foraging waters**. This is the most promising contemporaneous link for true spatial prey availability, but its source GPS and original geolocated acoustics were NOT supplied to mina in a freely accessible joined format.
- IMR published overall-stratum (regional, not foraging-position) acoustic summaries 2023 36.7 g/m² CV .51, 2024 80.5 CV .11, 2025 102.0 CV .75. Frozen [source data + all 2011–25 observed years](inputs/IMR_annual_overall_acoustic_2011_2025_v1.csv) and [analytic audit](outputs/IMR_independent_acoustic_2023_2025_v1/REPORT_JA.md). These new 2023–25 summaries were **not in Freer 2011–2020 training**, but no direct spatial 2023–25 Freer predictions exist and they cannot be applied to 2011/13/15 GPS/day responses.

## What is genuinely NOT yet shown across scales

**New proposed hypothesis (not empirical conclusion):** in flightless, colonial penguins on Antarctic islands, local breeding-space contraction, redistribution and recoverability depend on a *mismatch* between (a) reachable, energetically profitable PREY opportunities at actual dive depth/time and (b) real ice/snow-free LAND nesting opportunities and local colony state. The same broad krill biomass or a single satellite ice field may be insufficient. This must be tested in independent islands/years and Adélie/Chinstrap/Gentoo where data align, explicitly reporting stage-specific fledging/recruitment and physical nest-unit mapping.

1. **Independent actual marine prey:** time/space-resolved acoustics never used to train the hindcast GAM, with survey/transducer/frequency/transect flags. Pair with same-week native GPS/TDR with original device clock and wet/dive QA.
2. **Accessible prey not merely abundance:** validated depth/time encounter measure from acoustic swarms plus dive range, or video capture labels for the actual paired animals. The new 2026 prior paper ALREADY investigates this, so produce only novel cross-scale discrimination versus breeding-space effects.
3. **Annual land/nest opportunity:** actual breeding-patch physical GIS footprints and annual snow, ice, vegetation/guano—separate from static 2km plant presence.
4. **Predictive gate:** compare marine-only, land-only, and combined models on years/colonies held out from fitting. Only a transferable demographic coefficient to nest abundance and N_eff would allow a credible future CMIP6 biological projection.

## Stop gates

- Historical source 25km OSI monthly/daily satellite SIC does not prove true route impassability. All 4320 ice-graph source sensitivities had **0 disconnected low-ice GPS cells**; 39 native island×day GPS SIC cells >=15% were observed only in 2013, none >=30%. No new accessibility mechanism from binarization.
- Present Freer krill GAM used acoustics + ice + salinity: historic GPS-traversed *GAM* ratios are not independent food supply or a causal inference. Independent 2023–25 IMR regional survey values alone are neither individual diet nor 2011–19 same-day krill.
- A published 2026 paper already establishes the basic accessible-prey proposition. Do not relabel it as our new result.
- Future 2050/2100 breeding pairs, true GIS patch N_eff, species replacement, greening/vegetation have **not** passed out-of-time/source-level demographic forecast validation. Don't provide numerical projections as facts.

All references are scientific provenance and novel-gap screening, NOT user outreach to IMR/NPI or an unconsented data request. PR #206 remains Draft; Paper1 PR189 and Paper2 PR199 and main remain untouched.
