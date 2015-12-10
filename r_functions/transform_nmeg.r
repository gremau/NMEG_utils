# This file creates datasets from NMEG Ameriflux files and calculates
# Annual sums of fluxes.
#
# Greg Maurer - Nov 23, 2014

#setwd('~/current/NMEG_fluxdata/data_analysis/R/')

library(plyr)
library(xts)

# Function for renaming sites
rename_vars <- function(df) {
  colnames(df)[grep('Vcm', colnames(df))] <- 'Mixed conifer'
  colnames(df)[grep('Vcp', colnames(df))] <- 'Ponderosa pine'
  colnames(df)[grep('Wjs', colnames(df))] <- 'Juniper savannah'
  colnames(df)[grep('Mpj', colnames(df))] <- 'PJ woodland'
  colnames(df)[grep('Ses', colnames(df))] <- 'Shrubland'
  colnames(df)[grep('Seg', colnames(df))] <- 'Grassland'
  
  return(df)
}

#    Take a list of dataframes indexed by sitename, extract requested
#    variable from each one, and place in column (named by site) in a new
#    dataframe.
#
#    Args:
#        datalist    : List of dataframes
#        varname     : Desired Ameriflux variable
#        sites       : List of site names ( same order as datalist )
#        startyear   : First year of data to include
#        endyear     : Last year of data to include
#
#    Return:
#        site_df     : New dataframe ( 'varname' from all 'sites' )

get_var_allsites <- function( datalist, varname, sites, 
                             startyear=as.numeric(format(Sys.Date(), '%Y' ))-1,
                             endyear=as.numeric(format(Sys.Date(), '%Y' ))){
    
    #newidx <- as.Date(as.Date(paste(startyear, "-1-1", sep='')):
    #                  as.Date(paste(endyear, "-12-31", sep='')))
    
    # Loop through list and extract variable from dataframes
    # Use xts objects to make sure date indexes merge
    for (i in 1:length(datalist)){
        if (i==1){
            df <- datalist[[1]]
            site_df <- as.xts(df[varname], as.Date(df[,1]))
            colnames(site_df) <- sites[1]
 
        } else {
            df <- datalist[[i]]
            new <- as.xts(df[varname], as.Date(df[,1]))
            colnames(new) <- sites[i]
            site_df <- cbind(site_df, new)
        }
    }
    # Subset to desired years
    st <- paste(as.character(startyear), '-01-01', sep='')
    en <- paste(as.character(endyear), '-12-31', sep='')
    rng <- paste( st, '/', en, sep='')
    site_df <- site_df[rng]
    # Back to dataframe
    site_df <- data.frame(date=index(site_df),coredata(site_df))
    return( site_df )
}

# Add water year, water year doy, and season columns to a dataframe
# using the time series index

add_WY_cols <- function( df ){
    # TS object, water year TS object
    df_ts <- as.xts(df[,2:ncol(df)], as.Date(df[,1]))
    diff <- as.Date("2007-01-01") - as.Date("2006-10-01")
    df_wy <- as.xts(df[,2:ncol(df)], as.Date(df[,1])+diff)

    # Align time by one day so months/days are correct and add water year cols
    df_wy <- align.time(df_wy, n=60*60*24)
    df_ts$year_w <- .indexyear(df_wy) + 1900
    df_ts$doy_w <- .indexyday(df_wy) + 1

    # Back to dataframe
    df_new <- data.frame(date=index(df_ts),coredata(df_ts))

    # Add hydrologic season columns
    df_new[,'season'] <- as.vector(rep(NA, nrow(df_ts)))
    df_new$season[(.indexmon(df_ts) > 10) | (.indexmon(df_ts) < 3)] = 'cold'
    df_new$season[(.indexmon(df_ts) > 2) & (.indexmon(df_ts) < 7)] = 'spring'
    df_new$season[(.indexmon(df_ts) > 6) & (.indexmon(df_ts) < 11)] = 'monsoon'

    return(df_new)
}
