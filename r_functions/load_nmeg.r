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

# Function to load one 30 minute ameriflux file
# Roughly equivalent to the similarly named python function in 
# load_nmeg.py
load_aflx_file <- function( fname, year ){

    header <- read.csv(fname, skip=3, nrows=1)
    df <- read.csv(fname, skip=5, header=FALSE)
    df[df==-9999] <- NA
    colnames(df) <- colnames(header)

    return( df )
}


# Function to load a multiyear, 30 minute ameriflux file
# Roughly equivalent to the similarly named python function in 
# load_nmeg.py
get_multiyr_aflx <- function( site, afpath, 
                             startyear=as.numeric(format(Sys.Date(), '%Y' )-1),
                             endyear=as.numeric(format(Sys.Date(), '%Y' )),
                             gapfilled=TRUE, old_dparse=FALSE){
    if (gapfilled==TRUE) {
        file_gap_type <- 'gapfilled'
    } else {
        file_gap_type <- 'with_gaps'
    }
    
    filenames <- list.files(afpath, full.names=TRUE)
    filenames <- filenames[grepl(site, filenames)]
    filenames <- filenames[grepl(file_gap_type, filenames)]

    my_df <- NULL

    for (i in 1:length(filenames)){
        file <- filenames[i]
        header <- read.csv(file, skip=3, nrows=1)
        df <- read.csv(file, skip=5, header=FALSE)
        df[df==-9999] <- NA
        colnames(df) <- colnames(header)

        if (is.data.frame( my_df )){
            my_df <- rbind(my_df, df)
        } else { 
            my_df <- df
        }
    }

    return( my_df )
}

get_daily_file <- function( site, dlypath, make_new=FALSE ){
    if (make_new==TRUE){
        system('python ../py_modules/export_daily_files.py')
    }
    filenames <- list.files(dlypath, full.names=TRUE)
}

