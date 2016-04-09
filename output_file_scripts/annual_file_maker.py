# Script to create and export data files for Marcy

import sys
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
af_path = '/home/greg/sftp/eddyflux/Ameriflux_files/provisional/'

import load_nmeg as ld
import transform_nmeg as tr
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import pdb as pdb


# Years to load
start = 2007
end = 2015
# Sites to load
sites = ['Seg', 'Ses', 'Sen', 'Wjs', 'Mpj', 'Mpg', 'Vcp', 'Vcm']
#sites = ['Mpj', 'Mpg']

# Create a wateryear-based annual file?
wyear=True
wyear_days = 91
#wyear_days = 60
outfile = '../processed_data/annual_files/wateryear_NMEG_fluxes.csv'


# Load hourly data into multiyear dataframes (1/site) within a dict
hourly = { x :
        ld.get_multiyr_aflx( 'US-' + x, af_path, gapfilled=True,
            startyear=start, endyear=end) 
        for x in sites }

# Add an observations column to sum
for x in hourly.keys():
    # Count columns and nans in each timestamp
    ncol = hourly[x].shape[1]
    nan_count = hourly[x].apply(np.isnan).sum(axis=1)
    # For if all columns in timestamp are NaN, don't count as observation
    hourly[x].insert(1, 'n_obs', 1)
    hourly[x].loc[nan_count >= ncol, 'n_obs'] = 0

# Shift the index if using wateryear
if wyear:
    for x in hourly.keys():
        hourly[x].index = hourly[x].index + dt.timedelta(days=wyear_days)

# To get annual values of daytime ET we need to first calculate it on a daily
# basis. It can then be added to a dict
ET_dict = {}
for site in sites:
    # Get data for site
    h = hourly[site]
    # Calculate daily ET and PET 
    # (see NMEG_utils/py_modules/transform_nmeg for documentation)
    ET_dict[site] = tr.get_daytime_et_pet( h, freq='1D' )


# Create an annual dataset
yearly = { x :
         tr.resample_30min_aflx( hourly[x], freq='A', 
             c_fluxes=[ 'GPP', 'RECO', 'FC_F' ], 
             le_flux=[ 'LE_F' ], 
             avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET_F', 'VPD_F'], 
             sum_cols=[ 'P_F', 'n_obs' ] , tair_col='TA_F' )
         for x in hourly.keys() }

yearly_sums = pd.DataFrame()
for site in sites:
    # Get site data and rearrange cols
    new = yearly[site]
    new.insert(0, 'site', site)
    nobs = new.pop('n_obs_sum')
    new.insert(1, 'n_obs', nobs)
    # Add in resampled ET and PET data
    new['ET_F_mm_dayint'] = ET_dict[site].ET_mm_dayint.resample('A').sum()
    new['PET_F_mm_dayint'] = ET_dict[site].PET_mm_dayint.resample('A').sum()

    yearly_sums = yearly_sums.append(new)
    
yearly_sums.to_csv(outfile, na_rep=-9999, date_format='%Y')
