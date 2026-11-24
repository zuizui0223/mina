# NOAA independent nest-level reproduction source and published network support (2026-11-24)

Source support, not raw nest-level reanalysis. Hinke et al. 2018 MEE DOI 10.1111/2041-210x.13015, [official NOAA paper](https://repository.library.noaa.gov/view/noaa/53434/noaa_53434_DS1.pdf), Table 1 printed p.1856, CC BY 4.0. PDF/HTML indexed text cross-checked; PDF screenshot failed (cache miss), visual verification pending. NOAA accession 0171619 DOI 10.7289/V5Z036F7, [InPort 52162](https://www.fisheries.noaa.gov/inport/item/52162), [repro field definitions 52186](https://www.fisheries.noaa.gov/inport/item/52186), [historical intervals 52185](https://www.fisheries.noaa.gov/inport/item/52185). Camera network 2015–17; historical lay/hatch intervals are not 40 years of annual breeding success (interval schema has no year). Published regional network comparison covers 2016/17 only.

## Executed source support calculation

17 species-locality entries/13 distinct localities. Sum of transcribed Table 1 monitored nests 453 (427 with known creche count); article prose says 455, retain discrepancy and do not silently reconcile. Four same-locality contrasts, calculated from exact integer nest and chick counts rather than rounded published ratios. Exact atlas and native winter source ZIP hashes checked: artifact 13669533413 add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a; artifact 14926710177 b48ad3c97e35bc487ad6ebca955bbbec5478f75359e9f0300296910821a050b8. WGS84 geodesic match to 595 census centres, require exactly one centre within 2km. This is a geographic candidate, not proven source-colony identity.

| Locality | Pair | Other species chicks/nests | Gentoo chicks/nests | Difference chicks/nest | Unique candidate centre |
|---|---|---|---|---:|---|
|Copacabana|ADPE/GEPE|76/50|89/58|+0.014483|No, LLAN and PTHO|
|Lion's Rump|ADPE/GEPE|55/41|24/19|-0.078306|LION 0.266 km|
|Cape Shirreff|CHPE/GEPE|13/10|13/8|+0.325000|SHIR 0.291 km|
|Cierva Cove|CHPE/GEPE|50/30|22/15|-0.200000|No, PING and CIER|

All four differences independently verified using integer cross-products. Six of 13 localities pass unique 2km geometry support; only two of four pair-localities pass. Candidate 2016 June–Oct P100 at LION 1.361980 pp, SHIR 3.907414 pp. Different pairs, no independent year replication. No P regression or ecological inference. Creche-stage chicks per monitored nest is not Signy's later pre-fledging count per counted pair, nor juvenile survival. No demonstrated cross-site reproduction of Signy association.

## Retrieval and next decision

First public acquisition [run 45411506462](https://github.com/zuizui0223/mina/actions/runs/45411506462), artifact 14926679417 SHA256 f71ba5e8c416d8bace614b0b67f820bd866f69f9794272930adcd3c5b604ff9c: guessed archive paths 404, metadata retrieved, no raw workbooks. Exact official metadata locator FTP arc0118/0171619 and NOAA download endpoint used in corrected [run 45411730259](https://github.com/zuizui0223/mina/actions/runs/45411730259), artifact 14927118922 SHA256 853e8b433296ea498452952b09545cce39140a1680ba534284ea44378ff7b9ab. All five HTTPS attempts timed out; no original workbooks. Workflow success only indicates receipt saved. Do not repeat identical blocked acquisition. NOAA long-term census accession 0185113 DOI 10.25921/58yq-7g68 [InPort schema 55436](https://www.fisheries.noaa.gov/inport/item/55436) has Year and five species-count columns only, not separate chick/pair success. Next high-value candidate independent life-stage data Hinke et al. 2020 DOI 10.5061/dryad.2v6wwpzkh, [NOAA InPort 63282](https://www.fisheries.noaa.gov/inport/item/63282), 1982–2018, tracks, fledgling weights, recruitment index, carcass counts and voltage. Metadata verified only; retrieve originals and inspect true cohort-year/site and censoring before any climate fit. No raw-data redistributions, no main merge or manuscript edits.

Local reproduction bundle noaa_nest_polynya_support_20261124.zip SHA256 a0247be7cfec2a727a3abb25ede0bb1159d524f6c3a38ba9d29791d9fa35ea5f, executed audit_published_network.py SHA256 3adbb35025ca8c00dc529ad93b37e9f99a9aff345f9b458f0b6379c5fa4fa280, three tables, summary and README.