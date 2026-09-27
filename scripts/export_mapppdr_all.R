#!/usr/bin/env Rscript

# Export the complete pinned APBP/MAPPPD tables needed to assess whether
# multi-site demographic synchrony can be analysed at island boundaries.
#
# Source is frozen to the same mapppdr commit already used elsewhere in mina.

COMMIT <- "88c73a507e0921b2541c218c71eaf16721bc6502"
BASE <- sprintf(
  "https://raw.githubusercontent.com/CCheCastaldo/mapppdr/%s/data",
  COMMIT
)

args <- commandArgs(trailingOnly = TRUE)
out_dir <- if (length(args) >= 1) args[[1]] else "build/mapppdr_all"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

tmp <- tempfile("mapppdr-all-")
dir.create(tmp)

objects <- c("penguin_obs", "sites", "species", "site_species")
for (object in objects) {
  target <- file.path(tmp, paste0(object, ".rda"))
  url <- sprintf("%s/%s.rda", BASE, object)
  download.file(url, target, mode = "wb", quiet = TRUE)
  loaded <- load(target, envir = .GlobalEnv)
  if (!(object %in% loaded)) {
    stop(sprintf("expected object %s not found", object))
  }
  write.csv(
    get(object),
    file.path(out_dir, paste0(object, ".csv")),
    row.names = FALSE,
    na = ""
  )
  cat(sprintf("%s_rows=%d\n", object, nrow(get(object))))
}

cat(sprintf("mapppdr_commit=%s\n", COMMIT))
cat(sprintf("out_dir=%s\n", out_dir))
