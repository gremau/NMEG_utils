# This file creates datasets from NMEG Ameriflux files and calculates
# Annual sums of fluxes.
#
# Greg Maurer - Nov 23, 2014

library(xts)
library(plyr)

# Function to load one 30 minute ameriflux file
# Roughly equivalent to the similarly named python function in 
# load_nmeg.py
load_aflx_file <- function( fname ){

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

    for (i in startyear:endyear){
        fname <- paste(afpath, 'US-', site, '_', as.character(i),
                       '_', file_gap_type, '.txt', sep='')
        if (fname %in% filenames){
            df_yr <- load_aflx_file( fname )
        }
        if (is.data.frame( my_df )){
            my_df <- rbind.fill(my_df, df_yr)
        } else { 
            my_df <- df_yr
        }
    }
    return( my_df )
}


# Function to load one 30 minute soilmet file
# Roughly equivalent to the similarly named python function in 
# load_nmeg.py
load_soilmet_qc <- function( fname ){

    #header <- read.csv(fname, skip=3, nrows=1)
    dat <- read.csv(fname, header=TRUE)
    dat[dat=='NaN'] <- NA
    #colnames(df) <- colnames(header)

    return( dat )
}


# Function to load a multiyear, 30 minute ameriflux file
# Roughly equivalent to the similarly named python function in 
# load_nmeg.py
get_multiyr_soilmet <- function( site, base_path, ext,
                             startyear=as.numeric(format(Sys.Date(), '%Y' )-1),
                             endyear=as.numeric(format(Sys.Date(), '%Y' ))){
    
    filenames <- list.files(base_path, full.names=TRUE)
    filenames <- filenames[grepl(site, filenames)]
    filenames <- filenames[grepl(paste(ext, '.txt', sep=''), filenames)]

    my_df <- NULL

    for (i in startyear:endyear){
        fname <- paste(base_path, '/', site, '_', as.character(i),
                       '_soilmet_', ext, '.txt', sep='')
        
        if (fname %in% filenames){
            df_yr <- load_soilmet_qc( fname )
        }
        if (is.data.frame( my_df )){
            my_df <- rbind.fill(my_df, df_yr)
        } else { 
            my_df <- df_yr
        }
    }
    # Make a date column
    my_df[,'date'] <- with(my_df, ISOdatetime(year, month, day, 
                                              hour, min, second))
    return( my_df )
}

# Load shared daily file for a site from NMEG_utils. If asked, this script
# will call the python script that makes these files. Note that the python
# script that makes these fills in missing columns, standardizes the time
# period (2007-2014), reindexes the dataframe, and verifies the index. So,
# there should be no missing/duplicated data columns or time periods.

get_daily_file <- function( site, type, make_new=FALSE ){
    if (make_new==TRUE){
        system(paste('python ~/current/NMEG_utils/output_file_scripts/',
                     'export_daily_', type, '.py', sep=''))
    }
    # The daily files are put here:
    dlypath <- paste('~/current/NMEG_utils/processed_data/daily_', 
                     type, sep='')
    filenames <- list.files(dlypath, full.names=TRUE)
    filenames <- filenames[grepl(paste(site, '_daily_', type, sep=''),
                                 filenames)]
    df <- read.csv(filenames, header=TRUE)
    # Remove last row (2015 data containing NAs - added by python code)
    df <- df[1:nrow(df)-1,]
    return(df)
}

# Convert daily dataframe into a time series (xts) object
daily_to_xts <- function( df ){
    # Get time column (should be $X)
    df_t <- as.Date(df$X)
    # Separate into numeric columns 
    df_num <- df[,2:ncol(df)]
    # Convert to xt
    df_xts <- xts(df_num, df_t)

    return(df_xts)
}

# this is example code for filling in missing observations in a time series
# Will implement in above functions as needed
#dim(seg_s)
# timeseries is shorter than 8 full years of days (2922)
#sum(is.na(seg_s$SWC_G1_22p5_AVG))
# So, create a full 8 year time series to fill in gaps
#x <- as.Date("2007-01-01"):as.Date("2014-12-31")
#length(x)
# Merge it into seg_s - missing days will be populated with NA
#seg_s <- merge(seg_s, as.Date(x))
#dim(seg_s)
#sum(is.na(seg_s$SWC_G1_22p5_AVG)) # 224 more NA values
