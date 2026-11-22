#!/usr/bin/env Rscript
# Reconstruct the published Youngflesh (2026) colony-level pixel-support rule.
# No isotope modeling; source audit only; no post-hoc threshold selection.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=2) stop("Usage Rscript author_source_support_gate.R <publisher.rds> <output_dir>")
src <- args[[1]]; out <- args[[2]]
dir.create(out,recursive=TRUE,showWarnings=FALSE)
r <- readRDS(src)
if(!is.data.frame(r)) stop("Expected author-published data frame")
required <- c("site_id","ccamlr_id","region","season","year","month","day","bad","guano_bin","geometry")
if(!all(required %in% names(r))) stop("Author source schema drift")
if(!identical(nrow(r),179462L)) stop(paste("Unexpected RDS row total",nrow(r)))
r <- r[!is.na(r$site_id)&!is.na(r$season)&!is.na(r$month)&!is.na(r$day)&
       !is.na(r$bad)&r$bad==0&!is.na(r$guano_bin)&r$guano_bin==1,,drop=FALSE]
source_n <- nrow(r)
# Author script 4-diet-est.R: count images grouped by (site_id, season, month, day);
# average n_pix over pixel rows within each site (not site-year).
key <- paste(r$site_id,r$season,r$month,r$day,sep="|")
tab <- table(key)
n_pix <- as.numeric(tab[key])
mean_site <- tapply(n_pix,r$site_id,mean)
eligible <- names(mean_site)[mean_site>=2]
keep <- r$site_id %in% eligible
r2 <- r[keep,,drop=FALSE]
# For each site-year, record pixels, distinct image-days, original reported region,
# projected median pixel-centre coordinates, and original author site-level threshold.
coords <- vapply(r2$geometry,function(z) as.numeric(z[1:2]), numeric(2))
id <- paste(r2$site_id,r2$season,sep="|")
seqsites <- unique(id)
rows <- lapply(seqsites,function(k) {
  idx <- which(id==k)
  row <- r2[idx[1],,drop=FALSE]
  data.frame(site_id=as.character(row$site_id),
             season=as.integer(row$season),
             ccamlr_id=as.character(row$ccamlr_id),
             region=as.character(row$region),
             n_pixels=length(idx),
             n_image_days=length(unique(paste(r2$year[idx],r2$month[idx],r2$day[idx],sep="-"))),
             author_site_avg_n_pix=as.numeric(mean_site[as.character(row$site_id)]),
             x_m=median(coords[1,idx]), y_m=median(coords[2,idx]),
             stringsAsFactors=FALSE)
})
support <- do.call(rbind,rows)
support <- support[order(support$site_id,support$season),]
write.csv(support,file.path(out,"published_author_site_level_support_all_years.csv"),row.names=FALSE)
era <- support[support$season %in% 2004:2010,,drop=FALSE]
write.csv(era,file.path(out,"published_author_site_level_support_2004_2010.csv"),row.names=FALSE)
small <- aggregate(season~site_id+region,data=era,FUN=length)
names(small)[3] <- "n_source_seasons"
write.csv(small,file.path(out,"source_site_region_count_2004_2010.csv"),row.names=FALSE)
# Format machine-readable audit without any package dependencies.
cat(sprintf("SOURCE_RDS_ROWS=%d\nQUALIFIED_PIXEL_ROWS=%d\n",source_n,nrow(r2)))
cat(sprintf("SOURCE_SITES=%d\nAUTHOR_QUALIFIED_SITES=%d\n",length(unique(r$site_id)),length(unique(r2$site_id))))
cat(sprintf("TOTAL_AUTHOR_SOURCE_SITE_YEARS=%d\n",nrow(support)))
cat(sprintf("ERA_2004_2010_SITE_YEARS=%d\nERA_2004_2010_SITES=%d\n",nrow(era),length(unique(era$site_id))))
cat("ERA_2004_2010_REGION_COUNTS:\n")
print(sort(table(era$region),decreasing=TRUE))
cat("SITE_YEARS_FOR_THREE_NONINFORMATIVE_REGIONS:\n")
print(era[era$region %in% c("Adelie Land","Palmer Land","Queen Mary Land"),c("site_id","season","region")],row.names=FALSE)
gate <- paste(
  sprintf("source_n=%d",source_n),
  sprintf("author_pixel_n=%d",nrow(r2)),
  sprintf("site_n=%d",length(unique(r2$site_id))),
  sprintf("era_site_year_n=%d",nrow(era)),
  sprintf("era_site_n=%d",length(unique(era$site_id))),
  sep="\n")
writeLines(gate,file.path(out,"original_author_support_receipt.txt"))
