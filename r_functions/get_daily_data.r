# This file creates datasets from NMEG Ameriflux files and calculates
# Annual sums of fluxes.
#
# Greg Maurer - Nov 23, 2014

#setwd('~/current/NMEG_fluxdata/data_analysis/R/')

proc_path <- 'processed_data/'

library(plyr)
library(reshape2)

# Function for renaming sites
rename_vars <- function(df) {
  colnames(df)[grep('US.Vcm', colnames(df))] <- 'Mixed conifer'
  colnames(df)[grep('US.Vcp', colnames(df))] <- 'Ponderosa pine'
  colnames(df)[grep('US.Wjs', colnames(df))] <- 'Juniper savannah'
  colnames(df)[grep('US.Mpj', colnames(df))] <- 'PJ woodland'
  colnames(df)[grep('US.Ses', colnames(df))] <- 'Shrubland'
  colnames(df)[grep('US.Seg', colnames(df))] <- 'Grassland'
  
  df$season <- revalue(df$season, c("cold"="Cold",
                            "monsoon"="Monsoon",
                            "spring"="Spring"))
  
  reorder <- c('Cold', 'Spring', 'Monsoon')
  df$season <- factor(df$season, levels=reorder)
  
  return(df)
}


# C flux columns to keep
keep <- c("season", "year_w", "Vcm", "Vcp", "Mpj", "Wjs", "Ses", "Seg")

# NEE
fname <- paste( proc_path, 'FC_int_daily.csv', sep='')
FC_daily <- read.csv( fname, na.strings=c("NA","NaN", " ") )
FC_daily <- subset(FC_daily, subset = (year_w > 2007))
#FC_daily[FC_daily$year_w==2013, 'US.Vcm_int'] <- NA
FC_daily <- FC_daily[, keep]
FC_daily <- rename_vars(FC_daily)

# GPP
fname <- paste( proc_path, 'GPP_int_daily.csv', sep='')
GPP_daily <- read.csv(fname, na.strings=c("NA","NaN", " "))
GPP_daily <- subset(GPP_daily, subset = (year_w > 2007))
#GPP_daily[GPP_daily$year_w == 2013, 'US.Vcm_int'] <- NA
GPP_daily <- GPP_daily[, keep]
GPP_daily <- rename_vars(GPP_daily)

# Ecosystem respiration
fname <- paste( proc_path, 'RE_int_daily.csv', sep='')
RE_daily <- read.csv(fname, na.strings=c("NA","NaN", " "))
RE_daily <- subset(RE_daily, subset = (year_w > 2007))
#RE_daily[RE_daily$year_w == 2013, 'US.Vcm_int'] <- NA
RE_daily <- RE_daily[, keep]
RE_daily <- rename_vars(RE_daily)

# Ecosystem respiration
fname <- paste( proc_path, 'ET_int_daily.csv', sep='')
ET_daily <- read.csv(fname, na.strings=c("NA","NaN", " "))
ET_daily <- subset(ET_daily, subset = (year_w > 2007))
#ET_daily[RE_daily$year_w == 2013, 'US.Vcm_int'] <- NA
ET_daily <- ET_daily[, keep]
ET_daily <- rename_vars(ET_daily)

# Precip data
fname <- paste( proc_path, 'daily_precip.csv', sep='')
P_daily <- read.csv(fname, na.strings=c("NA","NaN", " "))
#keep <- c("season", "year_w", "US.Vcm", "US.Vcp", "US.Mpj", "US.Wjs",
#          "US.Ses", "US.Seg")
keep <- c("season", "year_w", "Vcm_gauge", "Vcp_gauge", "Mpj_gauge",
          "Wjs_gauge","Ses_gauge", "Seg_gauge")
P_daily <- subset(P_daily, subset = (year_w > 2007))
P_gauge_daily <- P_daily[, keep]
P_gauge_daily <- rename_vars(P_gauge_daily)


keep <- c("season", "year_w", "Vcm_PRISM", "Vcp_PRISM", "Mpj_PRISM",
          "Wjs_PRISM","Ses_PRISM", "Seg_PRISM")
P_PRISM_daily <- P_daily[, keep]
P_PRISM_daily <- rename_vars(P_PRISM_daily)

# PJ VWC data
fname <- paste( proc_path, 'PJ_VWC_daily.csv', sep='')
VWC_daily <- read.csv(fname, na.strings=c("NA","NaN", " "))
VWC_daily <- subset(VWC_daily, subset = (year_w > 2007))
#VWC_daily <- VWC_daily[, keep]
VWC_daily <- rename_vars(VWC_daily)

