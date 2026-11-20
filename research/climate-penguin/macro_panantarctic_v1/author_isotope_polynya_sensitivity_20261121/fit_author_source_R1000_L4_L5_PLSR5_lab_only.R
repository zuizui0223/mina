#!/usr/bin/env Rscript
# Pinned native Youngflesh et al 2026 Scripts/2-PLSR.R 1000x stratified
# 65% calibration/35% validation 6-component oscorespls then take 5 components.
# L4/L5 only; L7 original-author coefficients already fixed in old artifact.
# NO spatial/ecological effects and NO 2013+ imagery Y.
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=2L)stop("Usage: Rscript r1000.R original103_L4_L5_source_bands.csv out")
d <- read.csv(args[[1]],check.names=FALSE)
out <- args[[2]]
dir.create(out,recursive=TRUE,showWarnings=FALSE)
suppressPackageStartupMessages(library(pls))
suppressPackageStartupMessages(library(jsonlite))
pls.options(plsralg="oscorespls")
bandnames <- c("blue","green","red","nir","swir1","swir2")
expected <- c("d_15N",paste0("L4_",bandnames),paste0("L5_",bandnames))
stopifnot(nrow(d)==103L,identical(names(d),expected),all(is.finite(as.matrix(d))))
y <- d$d_15N
n <- nrow(d)
if(n!=103L)stop("Original published 103 lab measurements missing")
fold_labels <- stats::findInterval(y,stats::quantile(y,c(0,.2,.4,.6,.8),names=FALSE))
if(!identical(sort(unique(fold_labels)),1:5))stop("Original five isotope quantile bins changed")
fit_one <- function(name) {
  set.seed(1)
  x <- as.matrix(d[,paste0(name,"_",bandnames),drop=FALSE])
  B <- matrix(NA_real_,1000L,7L)
  colnames(B) <- c("intercept","B1","B2","B3","B4","B5","B7")
  S <- data.frame(iteration=seq_len(1000L),sensor=name,
                  ntrain=rep(NA_integer_,1000L),ntest=rep(NA_integer_,1000L),
                  rmse=rep(NA_real_,1000L),rmse_train_mean_null=rep(NA_real_,1000L))
  row_keys <- character(1000L)
  for(i in seq_len(1000L)) {
    train <- integer()
    for(j in seq_len(5L)){
      idx <- which(fold_labels==j)
      train <- c(train,sample(idx,size=floor(.65*length(idx))))
    }
    if(anyDuplicated(train) || length(train)<40)stop("Author original stratified training split changed")
    holdout <- setdiff(seq_len(n),train)
    tr <- data.frame(d_15N=y[train],Spectra=I(x[train,,drop=FALSE]))
    te <- data.frame(d_15N=y[holdout],Spectra=I(x[holdout,,drop=FALSE]))
    mod <- pls::plsr(d_15N~Spectra,scale=FALSE,
                     ncomp=6L,validation="none",data=tr,trace=FALSE)
    pred <- as.vector(predict(mod,newdata=te,ncomp=5L,type="response"))
    coef <- as.numeric(stats::coef(mod,ncomp=5L,intercept=TRUE))
    if(length(coef)!=7L || !all(is.finite(coef)) || !all(is.finite(pred)))
      stop("Actual original 5component R PLSR5 coefficients unidentifiable")
    B[i,] <- coef
    S$ntrain[i] <- length(train)
    S$ntest[i] <- length(holdout)
    S$rmse[i] <- sqrt(mean((y[holdout]-pred)^2))
    S$rmse_train_mean_null[i] <- sqrt(mean((y[holdout]-mean(y[train]))^2))
    row_keys[i] <- paste(sort(train),collapse=",")
  }
  if(length(unique(row_keys))<900)stop("1000 stratified partitions suspiciously repeated")
  if(!all(is.finite(B)) || !all(is.finite(S$rmse)))stop("Author source ensemble nonfinite")
  if(median(S$rmse)>=2.0 || median(S$rmse)>=median(S$rmse_train_mean_null))stop("Fixed source lab validation not supported")
  coeff <- data.frame(iteration=seq_len(1000L),sensor=name,as.data.frame(B,check.names=FALSE),check.names=FALSE)
  write.csv(coeff,file.path(out,paste0(name,"_1000_author_style_5component_PLSR_CV_ensemble_coefficients.csv")),row.names=FALSE)
  write.csv(S,file.path(out,paste0(name,"_1000_original103_lab_cv.csv")),row.names=FALSE)
  list(names=colnames(B),coefficients=B,folds=row_keys,
       receipt=list(sensor=name,original_lab_n=n,repetitions=1000L,
                    original_method="pls::plsr oscorespls ncomp6 fit and ncomp5 coefficient",
                    source_identical_5_strata_65pct_train=TRUE,
                    median_cv_rmse=median(S$rmse),
                    median_train_mean_null_rmse=median(S$rmse_train_mean_null),
                    coefficient_means=as.numeric(colMeans(B))))
}
a <- fit_one("L4")
b <- fit_one("L5")
if(!identical(a$folds,b$folds))stop("Original same-fold L4 and L5 mismatch")
receipt <- list(status="ORIGINAL_AUTHOR_R1000_L4_L5_LAB_ONLY_PASS",
                L4=a$receipt,L5=b$receipt,
                same_exact_1000_original_lab_sample_splits=TRUE,
                original_published_L7_ensemble_separately_previously_pinned=TRUE,
                no_2013_2021_L8_new_image_Y=TRUE,
                no_polynya_or_other_ecological_model_run=TRUE)
jsonlite::write_json(receipt,file.path(out,"L4_L5_AUTHOR_R1000_CV_SOURCE_ONLY_RECEIPT.json"),
  pretty=TRUE,auto_unbox=TRUE,digits=12)
cat(jsonlite::toJSON(receipt,pretty=TRUE,auto_unbox=TRUE,digits=12))
cat("\n")
