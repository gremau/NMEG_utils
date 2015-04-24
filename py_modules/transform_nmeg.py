# transform_nmeg.py
# Greg Maurer

""" 
Functions for loading various NMEG data files
"""

import numpy as np
import ipdb as ipdb
import datetime as dt
import pandas as pd
import os



def sum_30min_c_flux( df ) :
    """
    Convert 30min molar C flux to mass flux ( umol/m^2/s to g/m^2 ) and
    sum (integrate) for the 30min periods for each column of data frame
    in the colnames variable.
    """
    
    df_int = df.copy()
    export_cols = []

    for cname in df.columns :
        #
        export_cname = cname + '_g_int'
        export_cols.append( export_cname )
        df_int[ export_cname ] = df_int[ cname ] * ( 12.011/1e+06 ) * 1800

    return df_int[ export_cols ]

def sum_30min_et( df, t_air ) :
    """
    Convert 30min latent heat flux to ET ( W/m^2 to mm/s ) and sum (integrate) 
    for each 30min period. 

    see http://bwc.berkeley.edu/Amflux/equations/Gretchen-latent-heat-flux.htm

    Should we sum this for the entire day or for only daytime hours?
    """

    df_int = df.copy()

    lmbda = ( 2.501 - 0.00236 * t_air ) * 1000

    for i, cname in enumerate( df.columns ) :
        #
        export_cname = 'ET_mm_int_' + str( i )
        et_mms = ( 1 / ( lmbda * 1000 )) * df_int[ cname ]
        et_mm_int = et_mms * 1800
        df_int[ export_cname ] = et_mm_int

    return df_int[ export_cname ]

def resample_aflx( df, freq='1D', c_fluxes=[ 'GPP', 'RE', 'FC',  ], 
        le_flux=[ 'LE' ], avg_cols=[ 'TA', 'RH', 'Rg', 'RNET' ], 
        precip_col='PRECIP' , tair_col='TA' ):
    
    # Calculate integrated c fluxes
    c_flux_sums = sum_30min_c_flux( df[ c_fluxes ] )
    # Calculate integrated ET
    et_flux_sum = sum_30min_et( df[ le_flux ], df[ tair_col ] )

    # Subset site data into summable and averagable data
    df_sum = pd.concat( [ c_flux_sums, et_flux_sum, df[ precip_col ]], 
                          axis=1 );
    df_avg = df[ avg_cols ]
    
    # Resample to daily using sum or mean
    sums_resamp = df_sum.resample( freq, how='sum' )
    avg_resamp = df_avg.resample( freq, how='mean' )

    # Put to dataframes back together
    df_resamp = pd.concat( [ sums_resamp, avg_resamp ], axis=1 )

    return df_resamp


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
    wy = df.index + dt.timedelta(days=61) #61 = Nov 1st, 91 = Oct 1st wy start
    df_wy['year_w'] = wy.year
    df_wy['doy_w'] = wy.dayofyear
    # Add hydrologic season columns
    df_wy['season'] = 'Null'
    df_wy.season[(df_wy.index.month > 10) | (df_wy.index.month < 3)] = 'cold'
    df_wy.season[(df_wy.index.month > 2) & (df_wy.index.month < 7)] = 'spring'
    df_wy.season[(df_wy.index.month > 6) & (df_wy.index.month < 11)] = 'monsoon'

    return df_wy
