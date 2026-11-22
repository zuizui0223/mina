# Research-reproducibility request to the original Youngflesh et al. (2026) authors — unsent draft

**2026-11-20 JST | Mina Draft PR #214 | UNSENT: not an email delivery, not author collaboration consent.** Contact address is from the [original author's published GitHub README](https://github.com/caseyyoungflesh/penguin_diet_from_space). No data have been requested or received as of this document.

**To:** cyoungf@clemson.edu

**Subject:** Research reproducibility request: Landsat guano-pixel selection and Landsat 8 OLI validation (Youngflesh et al. 2026)

Dear Dr. Youngflesh,

I am conducting a source-verified macroecological reanalysis of Antarctic Adélie penguin satellite-derived optical δ15N variation and its association with winter coastal polynya extent, building on your 2026 *Current Biology* study.

I have examined the published code repository (`caseyyoungflesh/penguin_diet_from_space`) and original data (Zenodo 17409948). I reproduced the laboratory-stage 103-guano-sample spectral calibration using the original R `pls` orthogonal-scores PLSR implementation with 1,000 stratified train/validation splits. A separately fitted Landsat 8 OLI six-band laboratory model gave performance comparable to the Landsat 7 ETM+ calibration (median holdout RMSE 1.742 versus 1.739 per mille on identical calibration splits). I recognize that equivalent laboratory cross-validation does not establish comparable isotope inference on new satellite scenes.

The methodological bottleneck is the processing stage before `Scripts/3-predict-diet.R`. The public code reads the prefiltered `landsat_reflectance_L457-2025-07-16.rds`, which contains `guano_bin=1` and `bad=0` for all retained original pixels. I could not locate the original image selection/guano-mask procedure in the repository or published dataset archive.

Would you be willing to point me to the source code, methods documentation, or existing reproducibility files for the following, if available?

1. The upstream Landsat scene acquisition and guano-pixel classification or ROI procedure, including cloud/snow/rock screening, QA flags, spectral scaling, and georeferencing.
2. Any contemporaneous independently annotated guano/non-guano examples or accuracy checks, ideally with coordinates and acquisition dates.
3. Any validated Landsat 8 OLI extension, sensor-harmonization procedure, or imagery-based validation for 2013–2021.
4. If available to share, the ensemble coefficient files or additional uncertainty notes for the published satellite-to-isotope model.

I would use these only to establish observation and measurement comparability before applying a **pre-specified negative-direction hypothesis** to a genuinely separate period. At present the polynya association is exploratory, and I am not treating it as an independently confirmed dietary shift. I would be glad to share the exact source-provenance and calibration audit.

Thank you for your time and consideration.

Best regards,

[Your name / affiliation]

---

## Before sending

- Review the wording and the exact scope of the project and contact; replace the signature placeholder. **User approval needed to send.**
- The 1,000-fold L7/L8 laboratory numbers are from [successful GitHub Actions #44676042238](https://github.com/zuizui0223/mina/actions/runs/44676042238) and original source MD5/SHA-verified inputs.
- The original author repo is pinned at commit `4ab7c992fc2232b7905af0d1aa949d88dc9561ea` and the source of correspondence address is the README. No claim of direct 2013–2021 isotope or guano classification validation.
- A Gmail draft attempt through the user-connected service was **not authorized by the user** and did **not** create or send any email. Do not retry connected Gmail actions without explicit user approval.
