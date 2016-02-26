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


# Years to load
start = 2007
end = 2014
# Sites to load
sites = ['Seg', 'Ses', 'Wjs', 'Mpj', 'Vcp', 'Vcm']

outfile = '../processed_data/annual_files/annual_NMEG_fluxes.csv'

# Create a wateryear-based annual file?
wyear=True

# Fill a dict with multiyear dataframes for each site in sites
hourly = { x :
        ld.get_multiyr_aflx( 'US-' + x, af_path, gapfilled=True,
            startyear=start, endyear=end) 
        for x in sites }

# Shift the index if using wateryear
if wyear:
    for x in hourly.keys():
        hourly[x].index = hourly[x].index + dt.timedelta(days=91)
        
    outfile = '../processed_data/annual_files/wateryear_NMEG_fluxes.csv'

#Annual file for marcy
yearly = { x :
         tr.resample_30min_aflx( hourly[x], freq='A', 
             c_fluxes=[ 'GPP', 'RECO', 'FC_F' ], 
             le_flux=[ 'LE_F' ], 
             avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET_F', 'VPD_F'], 
             sum_cols=[ 'P_F' ] , tair_col='TA_F' )
         for x in hourly.keys() }

yearly_sums = pd.DataFrame()
for i in yearly.keys():
    new = yearly[i]
    new['site'] = i
    yearly_sums = yearly_sums.append(new)
    
yearly_sums.to_csv(outfile, na_rep=-9999, date_format='%Y')
