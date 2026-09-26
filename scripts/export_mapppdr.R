#!/usr/bin/env Rscript

# Export focal APBP/MAPPPD source tables from pinned .rda files using base R.
#
# This intentionally avoids requiring an installed mapppdr package. GitHub
# Actions and local users both read the exact repository objects frozen here.
#
# Source:
#   CCheCastaldo/mapppdr
#   commit 88c73a507e0921b2541c218c71eaf16721bc6502

COMMIT <- "88c73a507e0921b2541c218c71eaf16721bc6502"
BASE <- sprintf(
  "https://raw.githubusercontent.com/CCheCastaldo/mapppdr/%s/data",
  COMMIT
)

args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args) >= 1) args[[1]] else "build/mapppdr"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

tmp <- tempfile("mapppdr-")
dir.create(tmp)

objects <- c("penguin_obs", "sites", "species", "site_species")
for (object in objects) {
  target <- file.path(tmp, paste0(object, ".rda"))
  url <- sprintf("%s/%s.rda", BASE, object)
  download.file(url, target, mode = "wb", quiet = TRUE)
  loaded <- load(target, envir = .GlobalEnv)
  if (!(object %in% loaded)) {
    stop(sprintf("expected object %s not found in %s", object, target))
  }
}

focal_sites <- sites[
  grepl("Biscoe|Dream|Torgersen", sites$site_name, ignore.case = TRUE),
  ,
  drop = FALSE
]

focal_species <- species[
  species$genus == "Pygoscelis" &
    species$species %in% c("adeliae", "antarcticus", "papua"),
  ,
  drop = FALSE
]

focal_site_species <- site_species[
  site_species$site_id %in% focal_sites$site_id &
    site_species$species_id %in% focal_species$species_id,
  ,
  drop = FALSE
]

focal_obs <- penguin_obs[
  penguin_obs$site_id %in% focal_sites$site_id &
    penguin_obs$species_id %in% focal_species$species_id,
  ,
  drop = FALSE
]

write.csv(focal_sites, file.path(out_dir, "sites.csv"), row.names = FALSE, na = "")
write.csv(focal_species, file.path(out_dir, "species.csv"), row.names = FALSE, na = "")
write.csv(
  focal_site_species,
  file.path(out_dir, "site_species.csv"),
  row.names = FALSE,
  na = ""
)
write.csv(focal_obs, file.path(out_dir, "penguin_obs.csv"), row.names = FALSE, na = "")

cat(sprintf(
  paste0(
    "mapppdr_commit=%s\n",
    "sites=%d\n",
    "species=%d\n",
    "site_species=%d\n",
    "observations=%d\n",
    "out_dir=%s\n"
  ),
  COMMIT,
  nrow(focal_sites),
  nrow(focal_species),
  nrow(focal_site_species),
  nrow(focal_obs),
  out_dir
))
