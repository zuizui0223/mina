#!/usr/bin/env Rscript
# ONE frozen post-result distributional sensitivity for observed colony nest counts.
# No pseudoabsences; NB GAM does not account for missing detectability or site effort.
suppressPackageStartupMessages(library(mgcv))
args <- grep("^--file=",commandArgs(),value=TRUE)
stopifnot(length(args)==1)
here <- dirname(normalizePath(sub("^--file=","",args[1])))
out <- file.path(here,"nb_outputs")
dir.create(out,showWarnings=FALSE,recursive=TRUE)
source_data <- file.path(here,"outputs","marine_observed_site_species_year_661.csv")
d <- read.csv(source_data,stringsAsFactors=FALSE)
stopifnot(nrow(d)==661,length(unique(d$site_species))==56,
          length(unique(d$site_id))==40,
          sum(d$observed_nest_count==0)==44,
          all(d$observed_nest_count>=0),
          all(d$observed_nest_count==floor(d$observed_nest_count)),
          setequal(unique(d$species),c("ADPE","CHPE","GEPE")))
d$species <- factor(d$species,levels=c("ADPE","CHPE","GEPE"))
d$site_species <- factor(d$site_species)
d$year_c <- d$year - 2005
stopifnot(all(is.finite(d$sic_site_anomaly_per10pp)),all(is.finite(d$sphere_x)),
          all(is.finite(d$sphere_y)),all(is.finite(d$sphere_z)))
null_formula <- observed_nest_count ~ species +
  s(year_c,by=species,k=6) +
  s(sphere_x,sphere_y,sphere_z,k=12) +
  s(site_species,bs="re")
sic_formula <- update(null_formula, . ~ . +
  s(sic_site_anomaly_per10pp,by=species,k=4))

fit_nb <- function(formula, data) {
  set.seed(20261109)
  suppressWarnings(mgcv::gam(formula,data=data,family=mgcv::nb(),
              method="REML",select=TRUE))
}
models <- list(
  nb_no_sic=fit_nb(null_formula,d),
  nb_with_sic=fit_nb(sic_formula,d))
smaller <- droplevels(subset(d,region!="Victoria Land"))
stopifnot(nrow(smaller)==353,length(unique(smaller$site_id))==14)
models$nb_sic_without_Victoria_Land <- fit_nb(sic_formula,smaller)
meta <- list()
smooths <- list()
n <- 0L
for (name in names(models)) {
  m <- models[[name]]
  summary <- summary(m)
  n <- n + 1L
  theta <- m$family$getTheta(TRUE)
  ok <- isTRUE(m$converged)
  if (!ok)stop("FITTING_HOLD: mgcv did not converge for ",name)
  if (!is.finite(theta)||theta<=0||!is.finite(AIC(m))||
      !is.finite(summary$dev.expl))stop("FITTING_HOLD: invalid NB theta/AIC/deviance: ",name)
  meta[[n]] <- data.frame(
    model=name,
    n=nobs(m),
    n_unique_sites=if (name=="nb_sic_without_Victoria_Land") 14L else 40L,
    family="negative_binomial_native_integer_counts",
    estimated_theta=as.numeric(theta),
    converged=ok,
    AIC=as.numeric(AIC(m)),
    explained_deviance=as.numeric(summary$dev.expl),
    edf_total=sum(m$edf),
    ice_was_included=(name!="nb_no_sic"),
    post_result_exploratory=TRUE,
    unobserved_sites_or_years_imputed=FALSE,
    external_validation_or_climate_causality=FALSE,
    stringsAsFactors=FALSE)
  tab <- summary$s.table
  statcol <- if ("Chi.sq" %in% colnames(tab)) "Chi.sq" else if ("F" %in% colnames(tab)) "F" else NA_character_
  if (is.na(statcol))stop("FITTING_HOLD: expected NB mgcv smooth summary columns")
  for (i in seq_len(nrow(tab))) {
    smooths[[length(smooths)+1L]] <- data.frame(
      model=name,term=rownames(tab)[i],
      edf=as.numeric(tab[i,"edf"]),
      reference_df=as.numeric(tab[i,"Ref.df"]),
      approximate_statistic_name=statcol,
      approximate_statistic=as.numeric(tab[i,statcol]),
      approximate_unadjusted_p=as.numeric(tab[i,"p-value"]),
      robust_colony_or_region_cluster_p=FALSE,
      project_wide_multiplicity_adjusted_p=FALSE,
      stringsAsFactors=FALSE)
  }
  cat("NB_NATIVE_GAM_FIT=",name," n=",nobs(m),
      " theta=",sprintf("%.8g",theta),
      " AIC=",sprintf("%.8g",AIC(m)),
      " explained=",sprintf("%.8g",summary$dev.expl),"\n",sep="")
  writeLines(c("Observed colonies only. Post-hoc NB model, no detection/effort calibration.",
               capture.output(summary)),
             file.path(out,paste0(name,"_summary.txt")))
}
metadata <- do.call(rbind,meta)
smoothing <- do.call(rbind,smooths)
metadata$delta_AIC_vs_fixed_no_sic <- NA_real_
metadata$delta_AIC_vs_fixed_no_sic[metadata$model=="nb_with_sic"] <-
  metadata$AIC[metadata$model=="nb_with_sic"] -
  metadata$AIC[metadata$model=="nb_no_sic"]
write.csv(metadata,file.path(out,"fixed_nb_fit_metrics.csv"),row.names=FALSE)
write.csv(smoothing,file.path(out,"fixed_nb_approximate_smooths.csv"),row.names=FALSE)
ice <- subset(smoothing, grepl("sic_site_anomaly_per10pp",term,fixed=TRUE))
if (nrow(ice)!=6)stop("FITTING_HOLD: expected 3 species across full and minus Victoria")
for (i in seq_len(nrow(ice))) {
  cat("NB_ICE_SMOOTH=",ice$model[i],"|",ice$term[i],
      "|edf=",sprintf("%.8g",ice$edf[i]),
      "|p_nominal=",sprintf("%.8g",ice$approximate_unadjusted_p[i]),"\n",sep="")
}
cat("NB_NATIVE_GAM_FITS_COMPLETE=3\n")
