#!/usr/bin/env Rscript
# 2026-11-20 source-only: compare Landsat7 ETM and Landsat8 OLI lab guano
# five-component PLSR in the author's OWN R pls/oscorespls and 1000 stratified
# 65% train 35% holdout resamples. Same source 103 samples, same seeds and
# 1000 partition indices. Frozen before opening ANY 2013+ L8 optical isotope Y.
# Adapted from Youngflesh et al 2026 public original source
# https://github.com/caseyyoungflesh/penguin_diet_from_space
# Scripts/2-PLSR.R; uses new L8 RSR, not L7 coefficients. NO real L8 image pixels.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=2) stop("Expected <published_original103_synthetic_L7_L8_bands_csv> <output_folder>")
data_path <- args[[1]]
out <- args[[2]]
dir.create(out,recursive=TRUE,showWarnings=FALSE)
suppressPackageStartupMessages(library(pls))
suppressPackageStartupMessages(library(jsonlite))
pls.options(plsralg="oscorespls")

d <- read.csv(data_path,check.names=FALSE)
expected_cols <- c("d_15N",paste0("L7_",c("blue","green","red","nir","swir1","swir2")),
                   paste0("L8_",c("blue","green","red","nir","swir1","swir2")))
if (nrow(d)!=103L || !identical(names(d),expected_cols)) stop("Fixed original 103 samples or band order changed")
if (!all(is.finite(as.matrix(d))))stop("Lab isotope or spectral original data nonfinite")
y <- d$d_15N
reps <- 1000L
prop_cv <- 0.65
ncomp <- 5L
model_ncomp_original <- 6L
# Author's 1000 x 65% 5-bin stratified draw, seed 1 per sensor, ncomp=6 fitted,
# predict/extract ncomp=5, scale=FALSE, method=orthogonal scores.
do_sensor <- function(name) {
  x <- as.matrix(d[,paste0(name,"_",c("blue","green","red","nir","swir1","swir2"))])
  stopifnot(dim(x)[1]==103L,dim(x)[2]==6L)
  set.seed(1)
  bands <- paste0("B",c("1","2","3","4","5","7"))
  coefs <- matrix(NA_real_,nrow=reps,ncol=7L)
  colnames(coefs) <- c("intercept",bands)
  score <- data.frame(iteration=1:reps,sensor=name,
    ntrain=rep(NA_integer_,reps),ntest=rep(NA_integer_,reps),
    rmse_source_PLSR5=rep(NA_real_,reps),
    rmse_training_mean_null=rep(NA_real_,reps))
  fold_hashes <- character(reps)
  for(i in seq_len(reps)){
    bins <- stats::quantile(y,probs=c(0,.2,.4,.6,.8),names=FALSE)
    b <- findInterval(y,bins)
    if (!identical(sort(unique(b)),as.integer(1:5))) stop("Original 103 d15N stratification bins unexpected")
    train <- integer()
    for(j in seq_along(bins)){
      idx <- which(b==j)
      size <- floor(prop_cv*length(idx))
      if(size<2)stop("Original author R training stratum too small")
      train <- c(train,sample(idx,size=size))
    }
    if(anyDuplicated(train))stop("Original author training sampled duplicate index")
    test <- setdiff(seq_along(y),train)
    if(length(train)<40 || length(test)<25)stop("Original sample 65/35 split unexpectedly small")
    Xtrain <- data.frame(d_15N=y[train],Spectra=I(x[train,,drop=FALSE]))
    Xtest <- data.frame(d_15N=y[test],Spectra=I(x[test,,drop=FALSE]))
    model <- pls::plsr(d_15N~Spectra,scale=FALSE,
       ncomp=model_ncomp_original,validation="none",data=Xtrain,trace=FALSE)
    yp <- as.vector(predict(model,newdata=Xtest,ncomp=ncomp,type="response"))
    cof <- as.numeric(pls::coef(model,ncomp=ncomp,intercept=TRUE))
    if(length(cof)!=7L || any(!is.finite(cof)) || !all(is.finite(yp))) {
      stop("Source original R PLSR oscorespls coefficients not finite")
    }
    coefs[i,] <- cof
    score$ntrain[i] <- length(train)
    score$ntest[i] <- length(test)
    score$rmse_source_PLSR5[i] <- sqrt(mean((y[test]-yp)^2))
    score$rmse_training_mean_null[i] <- sqrt(mean((y[test]-mean(y[train]))^2))
    # Nonsecret test of exactly identical splits across L7/L8 on R seed reset:
    # keep sorted integer IDs in a tiny source-only split ledger.
    fold_hashes[i] <- paste(sort(train),collapse=",")
  }
  if(any(!is.finite(score$rmse_source_PLSR5)))stop("Nonfinite original ensemble holdout score")
  # The source author uses all 1000 different fitted coefficients as ensemble.
  # Predictions = mean predictions of all 1000 coefs; retain them as model artifact.
  coeff_frame <- data.frame(iteration=seq_len(reps),sensor=name,
      as.data.frame(coefs,check.names=FALSE),check.names=FALSE)
  write.csv(score,file.path(out,paste0(name,"_103_orig_spectral_1000_R_pls_validation.csv")),row.names=FALSE)
  write.csv(coeff_frame,file.path(out,paste0(name,"_1000_author_style_5component_PLSR_CV_ensemble_coefficients.csv")),row.names=FALSE)
  list(score=score,coefs=coefs,train_ids=fold_hashes,
    summary=list(
      sensor=name,source_original_R_PLSR_algorithm="pls::plsr oscorespls ncomp=6 fit, ncomp=5 pred, scale=FALSE",
      original_103_same_lab_samples=103L,training_fraction=prop_cv,
      original_author_seed_restarted_each_sensor=1L,
      author_style_stratified_resamples=reps,
      median_cv_rmse=median(score$rmse_source_PLSR5),
      median_train_mean_null_rmse=median(score$rmse_training_mean_null),
      fraction_1000_partitions_model_better_than_train_mean_null=mean(score$rmse_source_PLSR5<score$rmse_training_mean_null),
      ensemble_coefficient_means=as.numeric(colMeans(coefs)),
      ensemble_coefficient_sds=as.numeric(apply(coefs,2,sd))))
}
old <- do_sensor("L7")
new <- do_sensor("L8")
if (!identical(old$train_ids,new$train_ids))stop("Source original 1000 folds differ between L7 and L8 despite same author seed")
rmse_diff <- new$score$rmse_source_PLSR5 - old$score$rmse_source_PLSR5
status <- if (new$summary$median_cv_rmse<2.0 &&
             new$summary$median_cv_rmse<new$summary$median_train_mean_null_rmse)
  "PASS_L8_ORIGINAL_R_1000_ENSEMBLE_SOURCE_ONLY_LAB_CV" else
  "NO_GO_L8_ORIGINAL_R_1000_ENSEMBLE_LAB_CV"
result <- list(
  status=status,
  publication_source_code="caseyyoungflesh/penguin_diet_from_space Scripts/2-PLSR.R",
  originally_published_R_source_1000_repeats=TRUE,
  originally_published_R_pls_oscorespls=TRUE,
  method_ncomp_six_fit_five_prediction=TRUE,
  no_2013_2021_L8_satellite_reflectance_or_isotope_proxy_opened=TRUE,
  no_current_new_guano_pixel_classifier_or_negative_labels=TRUE,
  no_polynya_environment_association_fit=TRUE,
  original_103_lab_reference_reused_across_two_sensors=TRUE,
  L7=old$summary,L8=new$summary,
  same_exact_1000_random_holdout_partitions=TRUE,
  paired_1000_folds_L8_minus_L7_rmse_median=median(rmse_diff),
  paired_1000_folds_L8_minus_L7_rmse_5_95pct=as.numeric(quantile(rmse_diff,c(.05,.95))),
  repeated_CV_partitions_not_independent_1000_biological_replicates=TRUE,
  CV_only_not_actual_post_2013_scene_inference=TRUE,
  new_2013_2021_future_Y_one_test_not_yet_permitted=TRUE
)
jsonlite::write_json(result,file.path(out,"AUTHOR_1000_R_PLSR_L7_L8_LAB_ONLY_CALIBRATION_RECEIPT.json"),
                     pretty=TRUE,auto_unbox=TRUE,digits=12)
cat(jsonlite::toJSON(result,pretty=TRUE,auto_unbox=TRUE,digits=12))
cat("\n")
