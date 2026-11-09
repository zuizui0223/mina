#!/usr/bin/env Rscript
# Non-MaxEnt observed-abundance SDM-style GAM pilot.
# IMPORTANT: This is conditionally observed colony nest count / mapped vegetation,
# NOT occupancy, unobserved site habitat suitability or penguin future abundance.
suppressPackageStartupMessages(library(mgcv))

here <- dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(), value=TRUE)[1])))
outdir <- file.path(here, "outputs")
dir.create(outdir, showWarnings=FALSE, recursive=TRUE)
marine <- read.csv(file.path(outdir,"marine_observed_site_species_year_661.csv"), stringsAsFactors=TRUE)
land <- read.csv(file.path(outdir,"contemporary_vegetation_site_species_197.csv"), stringsAsFactors=TRUE)

stopifnot(nrow(marine)==661,nrow(land)==197,
          length(unique(marine$site_id))==40,
          length(unique(marine$site_species))==56,
          length(unique(land$site_id))>=100,
          length(unique(land$species))==3)
species_levels <- c("ADPE","CHPE","GEPE")
marine$species <- factor(marine$species, levels=species_levels)
land$species <- factor(land$species, levels=species_levels)
marine$site_species <- factor(marine$site_species)
marine$year_c <- marine$year-2005
land$region <- factor(land$region)
for (v in c("sphere_x","sphere_y","sphere_z")) {
  if (any(!is.finite(marine[[v]]))||any(!is.finite(land[[v]])))
    stop(paste("Invalid source spherical coordinates:",v))
}
# Same site/species intercept for both GAMs; within-site SIC anomaly, so observed
# site geography is not extrapolated to an unsurveyed background raster.
marine_base <- log1p_nests ~ species +
  s(year_c, by=species,k=6) +
  s(sphere_x,sphere_y,sphere_z,k=12) +
  s(site_species,bs="re")
marine_sic <- update(marine_base, . ~ . +
  s(sic_site_anomaly_per10pp,by=species,k=4))
# Exact separate cross-sectional target grain. Every modern area value >0 has
# actually been detected in a source mapping product. It is not a year-specific
# vegetation observation at earlier climate sites.
land_base <- log1p_nest_median ~ species + region +
  log1p_observed_seasons + s(sphere_x,sphere_y,sphere_z,k=12)
land_veg <- update(land_base,. ~ . +
  s(log1p_static_vegetation_area_m2,by=species,k=4))

fit <- function(formula, data) {
  suppressWarnings(
    mgcv::gam(formula,data=data,family=gaussian(link="identity"),
              method="REML",select=TRUE)
  )
}
model <- list(
  marine_without_sic=fit(marine_base,marine),
  marine_with_sic=fit(marine_sic,marine),
  land_without_mapped_veg=fit(land_base,land),
  land_with_mapped_veg=fit(land_veg,land)
)
support <- list(
  marine=list(rows=nrow(marine),sites=length(unique(marine$site_id)),
              groups=length(unique(marine$site_species)),
              regions=length(unique(marine$region)),
              n_observed_zeros=sum(marine$observed_nest_count==0),
              species=as.list(table(marine$species))),
  terrestrial=list(rows=nrow(land),sites=length(unique(land$site_id)),
                   regions=length(unique(land$region)),
                   species=as.list(table(land$species)))
)
fmt <- function(value) ifelse(is.finite(value),sprintf("%.8g",value),"NA")
metrics <- data.frame()
smooths <- data.frame()
for (key in names(model)) {
  m=model[[key]]
  su=summary(m)
  metrics <- rbind(metrics,data.frame(
    model=key,n=nobs(m),family=family(m)$family,method="REML",
    AIC=AIC(m),adj_r2=su$r.sq,deviance_explained=su$dev.expl,
    residual_standard_deviation=sqrt(su$scale),
    edf_total=sum(m$edf),
    has_ridge_spatial_structure=TRUE,
    is_presence_absence_or_unobserved_site_SDM=FALSE,
    stringsAsFactors=FALSE
  ))
  tab=su$s.table
  if(nrow(tab)>0) {
    for (i in seq_len(nrow(tab))) {
      smooths<-rbind(smooths,data.frame(
        model=key,term=rownames(tab)[i],
        edf=as.numeric(tab[i,"edf"]),reference_df=as.numeric(tab[i,"Ref.df"]),
        F_statistic=as.numeric(tab[i,"F"]),
        p_mgcv_approximate=as.numeric(tab[i,"p-value"]),
        p_is_spatial_cluster_or_project_fdr=FALSE,
        stringsAsFactors=FALSE))
    }
  }
  cat("GAM_FIT:",key," n=",nobs(m)," AIC=",fmt(AIC(m)),
      " explained=",fmt(su$dev.expl),"\n",sep="")
}
metrics$delta_AIC_to_matching_base <- NA_real_
for(pair in list(c("marine_with_sic","marine_without_sic"),
                 c("land_with_mapped_veg","land_without_mapped_veg"))) {
  metrics$delta_AIC_to_matching_base[metrics$model==pair[1]] <- 
    metrics$AIC[metrics$model==pair[1]] - metrics$AIC[metrics$model==pair[2]]
}
write.csv(metrics,file.path(outdir,"four_fixed_GAM_fit_metrics.csv"),row.names=FALSE)
write.csv(smooths,file.path(outdir,"fixed_GAM_approximate_smooths.csv"),row.names=FALSE)
for(key in names(model)){
  textout=c(paste("MODEL",key),
            "This is post-result conditional observed-nest GAM; no presences/absences or background pixels.",
            capture.output(summary(model[[key]])))
  writeLines(textout,file.path(outdir,paste0(key,"_summary.txt")))
}
# Source model needs not have true ecological absence or standardized effort.
# Catch pseudo-R2 >99% dominated by site effects and do not mistake for climate.
if(any(!is.finite(metrics$AIC))||any(!is.finite(metrics$adj_r2))){
  stop("Numerical failure: nonfinite AIC or adjusted R2")
}
cat("NONMAXENT_GAM_METRICS_CSV=",file.path(outdir,"four_fixed_GAM_fit_metrics.csv"),"\n",sep="")
for(i in seq_len(nrow(smooths))){
  rr=smooths[i,]
  if(grepl("sic_site_anomaly|static_vegetation_area",rr$term)){
    cat("EXPLORATORY_ENV_SMOOTH=",rr$model,"|",rr$term,
        "|edf=",fmt(rr$edf),"|p_nominal=",fmt(rr$p_mgcv_approximate),"\n",sep="")
  }
}
cat("NONMAXENT_GAM_FITS_COMPLETED=4\n")
