"""
    export_daily_soilmet.py
    -----------------------

    Script to create and export daily NMEG soilmet files for use in R 
    (or elsewhere). Similar to export_daily_aflx.py.
    
"""
import sys
# laptop
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )
import load_nmeg as ld
import transform_nmeg as tr
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import pandas as pd

sm_path = '/home/greg/sftp/eddyflux/Soil_files/provisional/'

# Years to load
startyr = 2007
endyr = 2015
# Sites to load
sites = ['Seg', 'Ses', 'Sen', 'Wjs', 'Mpj', 'Mpg', 'Vcp', 'Vcm']
altsites = ['GLand', 'SLand', 'New_GLand', 'JSav', 'PJ', 'PJ_girdle',
	    'PPine', 'MCon']

# Fill a dict with multiyear dataframes for each site in sites
hourly = { x : 
        ld.get_multiyr_soilmet( x, sm_path, ext='qc_rbd',
            startyear=startyr, endyear=endyr) 
        for x in altsites }

# Resample to daily means
daily = { x : hourly[x].resample('1D').mean()
        for x in hourly.keys() }

# Replace alternate sitenames with ameriflux style names
for i, asite in enumerate(altsites):
    daily[sites[i]] = daily.pop(asite)

# Add 3 soil moisture columns of different depth ranges
# Also interpolate over missing values
depth_rng = [list(range(0, 6)), list(range(6, 23)), list(range(23, 66))]
depth_str = ['shall', 'mid', 'deep']

def get_depth_mean( df, var,  d_string, d_range ):
    # Extract columns matching depth range
    cols = [h for h in df.columns if var in h and 'tcor' not in h]
    d_range = [str(i) for i in d_range] # Convert to string list
    col_select = list()
    for depth in d_range:
        get_col = [k for k in cols if '_' + depth + 'p' in k 
                or '_' + depth + '_' in k]
        col_select = col_select + get_col
    
    # Calculate depth range SWC mean
    df[d_string + '_swc'] = df[col_select].mean(axis=1, skipna=True)
    
    return(df)

def get_depth_mean_interp( df, site ):
    df['shall_swc_interp'] = df.shall_swc.interpolate(method='pchip')
    df['mid_swc_interp'] = df.mid_swc.interpolate(method='pchip')
    df['deep_swc_interp'] = df.deep_swc.interpolate(method='pchip')
    df.shall_swc.plot(title=site, legend=True)
    df.mid_swc.plot(title=site, legend=True)
    df.deep_swc.plot(title=site, legend=True)
    df.shall_swc_interp.plot(title=site, legend=True)
    df.mid_swc_interp.plot(title=site, legend=True)
    df.deep_swc_interp.plot(title=site, legend=True)
    plt.show()

    return(df)

# Append means for each depth range
for i in range(0, 3):
    daily = { x : get_depth_mean(daily[x], 'SWC', depth_str[i], depth_rng[i])
        for x in daily.keys() }

# Remove some bad data
idx = daily['Seg'].index.year < 2010
daily['Seg'].shall_swc[idx] = np.nan
daily['Seg'].mid_swc[idx] = np.nan
daily['Seg'].deep_swc[idx] = np.nan

daily['Ses'].shall_swc[daily['Ses'].index==dt.datetime(2011, 5, 23)] = np.nan
daily['Ses'].mid_swc[daily['Ses'].index==dt.datetime(2011, 5, 23)] = np.nan
daily['Ses'].deep_swc[daily['Ses'].index==dt.datetime(2011, 5, 23)] = np.nan
idx = daily['Ses'].index < dt.datetime(2011, 5, 23)
daily['Ses'].shall_swc[idx] = daily['Ses'].shall_swc[idx] + 0.022
daily['Ses'].mid_swc[idx] = daily['Ses'].mid_swc[idx] - 0.025
daily['Ses'].deep_swc[idx] = daily['Ses'].deep_swc[idx] - 0.037

# Append interpolated means for each depth range
daily = { x : get_depth_mean_interp(daily[x], x) for x in daily.keys() }

import subprocess as sp
git_sha = sp.check_output(
        ['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

for site in sites:
    meta_data = pd.Series([('site: {0}'.format(site)),
        ('date generated: {0}'.format(str(dt.datetime.now()))),
        ('script: export_daily_soilmet.py'),
        ('git HEAD SHA: {0}'.format(git_sha)),('--------')])
    with open('../processed_data/daily_soilmet/US-' + site +
            '_daily_soilmet.csv', 'w') as fout:
        fout.write('---file metadata---\n')
        meta_data.to_csv(fout, index=False)
        daily[site].to_csv(fout, na_rep='NA')

# For exporting monthly shallow, mid, and deep files
#outpath = '/home/greg/current/NMEG_utils/processed_data/'


# Pull out shall
#rbd_i = tr.get_var_allsites(daily, 'shall_swc_interp', sites, startyear=startyr, endyear=endyr)
#rbd_i = rbd_i.resample( '1M', how='mean' )
# Write files to outpath
#rbd_i.to_csv(outpath + 'NMEG_monthly_shallSWC.csv')

# Pull out mid
#rbd_i = tr.get_var_allsites(daily, 'mid_swc_interp', sites, startyear=startyr, endyear=endyr)
#rbd_i = rbd_i.resample( '1M', how='mean' )
# Write files to outpath
#rbd_i.to_csv(outpath + 'NMEG_monthly_midSWC.csv')

# Pull out deep
#rbd_i = tr.get_var_allsites(daily, 'deep_swc_interp', sites, startyear=startyr, endyear=endyr)
#rbd_i = rbd_i.resample( '1M', how='mean' )
# Write files to outpath
#rbd_i.to_csv(outpath + 'NMEG_monthly_deepSWC.csv')

