""" 
Functions for conversions and transforms of NMEG data

 transform_nmeg.py
 Greg Maurer
"""

#import ipdb as ipdb
import datetime as dt
import pandas as pd
import numpy as np

now = dt.datetime.now()

def sum_30min_c_flux( df ) :
    """
    Convert 30min molar C flux to mass flux ( umol/m^2/s to g/m^2 ) and
    sum (integrate) for the 30min periods for each column of data frame
    in the colnames variable.
    """
    # Initialize returned variables
    df_int = df.copy()
    export_cols = []
    # For each input column create a new header and convert values to mass flux
    for cname in df.columns :
        export_cname = cname + '_g_int'
        export_cols.append( export_cname )
        df_int[ export_cname ] = df_int[ cname ] * ( 12.011/1e+06 ) * 1800

    return df_int[ export_cols ]


def sum_30min_et( df, t_air ) :
    """
    THIS IS AN OUTDATED METHOD
    Convert 30min latent heat flux to ET ( W/m^2 to mm/s ) and sum (integrate) 
    for each 30min period. Note that this method sums the full day of ET,
    rather than just daytime values (see get_daytime_et function below).

    see http://bwc.berkeley.edu/Amflux/equations/Gretchen-latent-heat-flux.htm
    """

    df_int = df.copy()
    # Define the lambda parameter
    lmbda = ( 2.501 - 0.00236 * t_air ) * 1000
    # For each input column create a new header and convert values to ET
    for i, cname in enumerate( df.columns ) :
        export_cname = 'ET_mm_fullday_' + str( i )
        et_mms = ( 1 / ( lmbda * 1000 )) * df_int[ cname ]
        et_mm_int = et_mms * 1800
        df_int[ export_cname ] = et_mm_int

    return df_int[ export_cname ]


def get_daytime_et_pet( df, freq='1D',
        le_col='LE_F', tair_col='TA_F', sw_col='SW_IN_F', h_col='H_F'):
    """
    Integrate 30 minute ET data into a daily (or longer) frequency file.
    Latent heat flux is converted to ET using daily mean LE from
    DAYTIME ONLY values. This is a pretty sensible way to do it and compares
    well with what Laura Morillas has done in the past (see email corresp.)

    Also see:
    http://bwc.berkeley.edu/Amflux/equations/Gretchen-latent-heat-flux.htm

    
    Args:
        df          : pandas DataFrame object (hourly - usually from AF file)
        freq        : frequency to resample to (default daily)
        le_col      : latent heat flux header name(s)
        tair_col    : air temperature header (string) used for ET calculation
        swin_col    : incoming shortwave header (string) to determine daytime
        h_col       : sensible heat flux header name (string)

    Return:
        df_le_daily   : pandas dataframe with ET & PET data at new frequency
    """

    # Make a subset dataframe with LE and Tair
    df_le = df[[le_col, tair_col, h_col]].copy()
    # Make a column to indicate daytime periods
    df_le['daytime_obs'] = 0
    # Mark daytime observations and nightime LE/Tair to NaN
    daytest = df['SW_IN_F'] > 5
    df_le.loc[daytest, 'daytime_obs'] = 1
    df_le.loc[~daytest, [le_col,tair_col]] = np.nan

    # Calculate mean daily LE and Tair
    df_le_daily = df_le.resample( freq, how='mean')
    # Sum the number of daytime observations
    df_le_daily['daytime_obs'] = df_le.daytime_obs.resample( freq, how='sum')
    # Calculate the lambda value for each day
    df_le_daily['lmbda'] = ( 2.501 - 0.00236 * df_le_daily[tair_col] ) * 1000
    # Calculate ET ( mean daily LE / (1000*lambda) * # daytime seconds
    df_le_daily['ET_mm_daytime'] = ( ( 1 / ( df_le_daily.lmbda * 1000 )) * 
            df_le_daily[ le_col ] * (df_le_daily.daytime_obs * 1800) )

    # Now calculate PET
    alphaPT = 1.26
    # Saturation vapor pressure temp curve (Tetens, 1930)
    slopeSAT = (
            (2508.3 / (df_le_daily[tair_col].values + 237.3)**2) * 
            np.exp(17.3 * df_le_daily[tair_col].values / 
                (df_le_daily[tair_col].values + 237.3))
            )
    
    # Psychometric constant (kPa / degC)
    PSI = 0.066

    # LE potential and ET potential (from Priestly-Taylor).
    # Note here, Rn-G is substituted with H + LE
    LEpot = alphaPT *(slopeSAT * (df_le_daily[ h_col ] + 
        df_le_daily[ le_col ]) / (slopeSAT + PSI))
    
    df_le_daily['PET_mm_daytime'] = (
            LEpot * 1800 * df_le_daily.daytime_obs / 
            (1000 * df_le_daily['lmbda']))

    return df_le_daily


def resample_30min_aflx( df, freq='1D', c_fluxes=[ 'GPP', 'RECO', 'FC_F' ], 
        le_flux=[ 'LE_F' ], avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET' ],
        minmax_cols=[ 'TA_F', 'VPD_F' ],
        sum_cols=[ 'P_F' ] , tair_col='TA_F' ):
    """
    Integrate 30 minute flux data into a daily (or longer) frequency file. C
    fluxes are converted from molar to mass flux and summed. Latent heat    
    flux is converted to ET and summed. A variable number for other met and 
    radiation values can be converted to averages, sums, or min/max outputs.

    Args:
        df          : pandas DataFrame object (usually derived from AF file)
        freq        : frequency to resample to (default daily)
        c_fluxes    : list of C flux header names (strings) to integrate
        le_flux     : latent heat flux header name(s)
        avg_cols    : list of header names (strings) to average
        minmax_cols : list of header names (strings) to convert to min/max
        sum_cols    : list of header names (strings) to sum
        tair_col    : air temperature header (string) used for ET calculation

    Return:
        df_resamp   : pandas dataframe with AF data at new frequency
    """

    # Calculate integrated c fluxes
    c_flux_sums = sum_30min_c_flux( df[ c_fluxes ] )
    # Calculate integrated ET
    et_flux_sum = sum_30min_et( df[ le_flux ], df[ tair_col ] )

    # Subset site data into summable and averagable data
    df_sum = pd.concat( [ c_flux_sums, et_flux_sum, df[ sum_cols ]], 
                          axis=1 );
    df_avg = df[ avg_cols ]
    df_min = df[ minmax_cols ]
    df_max = df[ minmax_cols ]
    
    # Resample to daily using sum or mean
    sums_resamp = df_sum.resample( freq, how='sum' )
    avg_resamp = df_avg.resample( freq, how='mean' )
    min_resamp = df_min.resample( freq, how='min' )
    max_resamp = df_max.resample( freq, how='max' )

    # Rename the min/max columns
    for i in minmax_cols:
        min_resamp.rename(columns={ i:i + '_min'}, inplace=True)
        max_resamp.rename(columns={ i:i + '_max'}, inplace=True)

    # Put to dataframes back together
    df_resamp = pd.concat( [ sums_resamp, avg_resamp, 
        min_resamp, max_resamp ], axis=1 )

    return df_resamp

def get_var_allsites( datadict, varname, sites, startyear=now.year - 1,
                      endyear=now.year - 1 ):
    """
    Take a dictionary of dataframes indexed by sitename, extract requested
    variable from each one, and place in column (named by site) in a new
    dataframe.

    Args:
        datadict    : Dictionary of dataframes with site keys
        varname     : Desired Ameriflux variable
        sites       : List of site names ( Ameriflux style )
        startyear   : First year of data to include
        endyear     : Last year of data to include

    Return:
        new_df     : pandas DataFrame containing multiple years of data
                      from one site
    """
    
    # Create empty dataframe spanning startyear to endyear
    # Will contain the multi-year column for each site at the correct frequency
    frequency = datadict[sites[1]].index.freq
    newidx = pd.date_range(str(startyear) + '-01-01',
                           str(endyear + 1) + '-01-01', freq = frequency)
    new_df = pd.DataFrame(index = newidx)
    
    # Loop through site names and extract variable
    for i, site in enumerate(sites):
        # Get the multi-year data for the site
        site_df = datadict[ site ]
        new_df[ site ] = site_df[ varname ]

    return new_df

def add_WY_cols( df ) :
    """
    Add water year columns
    
    Args:
        df (obj) : a pandas Data.Frame object with a timeseries index

    Return:
        df_wy (obj) : a copy of df with water year columns added 
    """
    df_wy = df.copy()
    # Add water year columns
    wy = df.index + dt.timedelta(days=91) #61 = Nov 1st, 91 = Oct 1st wy start
    df_wy['year_w'] = wy.year
    df_wy['doy_w'] = wy.dayofyear
    # Add hydrologic season columns
    df_wy['season'] = 'Null'
    df_wy.season[(df_wy.index.month > 10) | (df_wy.index.month < 3)] = 'cold'
    df_wy.season[(df_wy.index.month > 2) & (df_wy.index.month < 7)] = 'spring'
    df_wy.season[(df_wy.index.month > 6) & (df_wy.index.month < 11)] = 'monsoon'

    return df_wy
