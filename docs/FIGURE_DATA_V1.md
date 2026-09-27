# Manuscript figure-data package v1

This package is intentionally downstream of the frozen ecological results. It
does **not** define new hypotheses or choose new predictors.

## Inputs

The workflow obtains the frozen Palmer LTER Adélie colony census, the pinned
APBP/MAPPPD site metadata for the seven frozen local-network sites, and result
receipts committed under `results/`.

## Figure 1

`figure1_sites.csv` contains the six primary islands plus Biscoe Point
benchmark, coordinates, known focal breeders and observed abundance endpoints.

## Figure 2

`figure2_trajectories.csv` regenerates the complete 1991–2017 five-island
panel directly from the colony census. `figure2_pairwise_synchrony.csv`
contains all ten annual-growth correlations.

The exporter fails if the regenerated PC1 variance fraction or median
annual-growth correlation differs from the frozen synchrony receipt.

## Figure 3

`figure3_mechanism_audit.csv` puts the predeclared tests on one plotting
table. Because the original tests use both MSE and RMSE, the common plotted
quantity is **relative held-out error reduction**, while the native error
metric and raw coefficient are retained in separate columns.

No coefficient magnitudes are compared across different predictors; only their
direction relative to the predeclared direction is shown.

## Figure 4

`figure4_colony_states.csv` and `figure4_colony_transitions.csv` regenerate
the colony-network state from raw census rows.

For the conditional scatter plot, both next-year growth and standardized
log-effective-colony number are residualized against exactly the frozen
baseline: island identity, current log abundance and secular year. The
partial-regression slope must equal the frozen effective-colony coefficient.

`figure4_external_torgersen.csv` carries only the frozen external spatial
triangulation summary. It does not imply that LTER colony codes have been
crosswalked to GIS polygons.

## Rendering

`mina-figures` writes PNG and PDF versions of Figures 1–4 from these tables.
Generated images are CI artifacts rather than hand-maintained source files.
