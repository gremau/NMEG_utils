# Script to create and export monthly data files
# these include SPEI values calculated from our fluxes

import sys
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )

# Name of the data release, set paths
drelease = 'FLUXNET2015_a'

af_path = '/home/greg/sftp/eddyflux/Ameriflux_files/' + drelease + '/'
outpath = '/home/greg/current/NMEG_utils/processed_data/monthly_spei_flux/' + drelease + '/'

import load_nmeg as ld
import transform_nmeg as tr
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pdb as pdb
import datetime as dt


# Years to load
start = 2007
end = 2016
# Sites to load
sites = ['Seg', 'Ses', 'Sen', 'Wjs', 'Mpj', 'Mpg', 'Vcp', 'Vcm']
#sites = ['Vcs']


# Load hourly data into multiyear dataframes (1/site) within a dict
hourly = { x :
        ld.get_multiyr_aflx( 'US-' + x, af_path, gapfilled=True,
            startyear=start, endyear=end) 
        for x in sites }

# Now calculate the hours of C uptake
for site in sites:
    # Add a column with 0.5 for each uptake period (to sum)
    hourly[site]['hrs_C_uptake'] = 0
    test = hourly[site].FC_F < 0
    hourly[site].loc[test, 'hrs_C_uptake'] = 0.5
    
# Turn this into a daily dataset
daily = { x : 
         tr.resample_30min_aflx( hourly[x], freq='1D', 
             avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET_F', 'VPD_F'], 
             minmax_cols=['TA_F', 'VPD_F', 'GPP', 'RECO'],
             sum_cols=[ 'P_F', 'hrs_C_uptake' ] , tair_col='TA_F' )
         for x in hourly.keys() }

# Now calculate degree days and time of peak fluxes
# Do this on a daily basis and add to the dataframes in daily dict
for i, site in enumerate(sites):
    # Add columns with degree days (and remove <0 values from second)
    daily[site]['degree_days'] = (daily[site].TA_F_max - daily[site].TA_F_min)/2
    daily[site]['degree_days2'] = (daily[site].TA_F_max + daily[site].TA_F_min)/2
    test = daily[site].degree_days2 < 0
    daily[site].degree_days2[test] = 0

    h = hourly[site]
    # Get the time of day for peak GPP each day
    gpp_grp = h.GPP.groupby(h.index.date)
    peakGPP_t = gpp_grp.apply(lambda x: x.index[x==x.max()].time)
    # Get the time of day for peak NEE each day
    nee_grp = h.FC_F.groupby(h.index.date)
    peakNEE_t = nee_grp.apply(lambda x: x.index[x==x.min()].time)
    # Get the time of day for peak RECO each day
    reco_grp = h.RECO.groupby(h.index.date)
    peakRECO_t = reco_grp.apply(lambda x: x.index[x==x.min()].time)
    def get_frac( arr ):
        # Sometimes these are empty
        if len(arr)==0:
            return np.nan
        else:
            return (arr[0].hour*3600 + arr[0].minute*60)/(3600*24)
    
    # Calculate daily ET and PET 
    # (see NMEG_utils/py_modules/transform_nmeg for documentation)
    daily_et_pet = tr.get_daytime_et_pet( h, freq='1D')
    
    daily[site][ 'peakGPP_dayfrac'] = peakGPP_t.apply( get_frac )
    daily[site][ 'peakNEE_dayfrac'] = peakNEE_t.apply( get_frac )
    daily[site][ 'peakRECO_dayfrac'] = peakRECO_t.apply( get_frac )
    daily[site][ 'ET_mm_dayint'] = daily_et_pet.ET_mm_dayint
    daily[site][ 'PET_mm_dayint'] = daily_et_pet.PET_mm_dayint


# Create a monthly file. Columns from daily will need to be resampled and added
monthly = { x : 
         tr.resample_30min_aflx( hourly[x], freq='1M', 
             c_fluxes=[ 'GPP', 'RECO', 'FC_F' ], 
             le_flux=[ 'LE_F' ], 
             avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET_F', 'VPD_F'], 
             sum_cols=[ 'P_F', 'hrs_C_uptake' ] , tair_col='TA_F' )
         for x in hourly.keys() }

# Now add some calculated values and SPEI to the monthly data
spei_path = '../processed_data/spei/'

for site in sites:
    # First remove some columns from monthly dataframe
    monthly[site].drop( ['VPD_F_min', 'VPD_F_max', 'TA_F_min', 'TA_F_max'],
            axis=1, inplace=True)
    # Now add the calculated values (many come from daily data)
    monthly[site]['GPP_over_RE'] = (
            monthly[site].GPP_g_int/monthly[site].RECO_g_int)
    monthly[site]['ET_mm_dayint'
            ] = daily[site].ET_mm_dayint.resample('1M').sum()
    monthly[site]['PET_mm_dayint'
            ] = daily[site].PET_mm_dayint.resample('1M').sum()
    monthly[site]['hrs_C_uptake_dayavg'] = daily[site].hrs_C_uptake_sum.resample(
            '1M').mean()
    monthly[site]['GPP_dailymax_avg'] = daily[site].GPP_max.resample(
            '1M').mean()
    monthly[site]['RECO_dailymax_avg'] = daily[site].RECO_max.resample(
            '1M').mean()
    monthly[site]['TA_F_max_avg'] = daily[site].TA_F_max.resample('1M').mean()
    monthly[site]['TA_F_min_avg'] = daily[site].TA_F_min.resample('1M').mean()
    monthly[site]['growing_deg_days_sum'
            ] = daily[site].degree_days.resample('1M').sum()
    monthly[site]['growing_deg_days_2_sum'
            ] = daily[site].degree_days2.resample('1M').sum()
    monthly[site]['peak_NEE_dayfrac_avg'
            ] = daily[site].peakNEE_dayfrac.resample('1M').mean()
    monthly[site]['peak_GPP_dayfrac_avg'
            ] = daily[site].peakGPP_dayfrac.resample('1M').mean()
    monthly[site]['peak_RECO_dayfrac_avg'
            ] = daily[site].peakRECO_dayfrac.resample('1M').mean()

    
    # Load monthly SPEI file for the site
    spei = pd.read_csv(spei_path + 'SPEI_monthly_US-' + site + '_nainterp.csv', 
            index_col=0, parse_dates=True, na_values=['NA'])
    spei['spei3mon_vwet'] = spei.SPEI_monthly_3 >= 1.5
    spei['spei3mon_wet'] = np.logical_and(spei.SPEI_monthly_3 >= 0.5,
            spei.SPEI_monthly_3 < 1.5)
    spei['spei3mon_avg'] = np.logical_and(spei.SPEI_monthly_3 > -0.5,
            spei.SPEI_monthly_3 < 0.5)
    spei['spei3mon_dry'] = np.logical_and(spei.SPEI_monthly_3 <= -0.5,
            spei.SPEI_monthly_3 > -1.5)
    spei['spei3mon_vdry'] = spei.SPEI_monthly_3 <= -1.5
    spei['spei9mon_vwet'] = spei.SPEI_monthly_9 >= 1.5
    spei['spei9mon_wet'] = np.logical_and(spei.SPEI_monthly_9 >= 0.5,
            spei.SPEI_monthly_9 < 1.5)
    spei['spei9mon_avg'] = np.logical_and(spei.SPEI_monthly_9 > -0.5,
            spei.SPEI_monthly_9 < 0.5)
    spei['spei9mon_dry'] = np.logical_and(spei.SPEI_monthly_9 <= -0.5,
            spei.SPEI_monthly_9 > -1.5)
    spei['spei9mon_vdry'] = spei.SPEI_monthly_9 <= -1.5


    # Join the two files on the date index
    monthly_join = pd.concat([monthly[site], spei], axis=1)
   
    # Write file
    import subprocess as sp
    git_sha = sp.check_output(
            ['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    meta_data = pd.Series([('site: {0}'.format(site)),
        ('date generated: {0}'.format(str(dt.datetime.now()))),
        ('script: monthly_spei_flux_files.py'),
        ('git HEAD SHA: {0}'.format(git_sha)),('--------')])
    with open(outpath + 'monthly_spei_flux_'
            + site + '.csv', 'w') as fout:
        fout.write('---file metadata---\n')
        meta_data.to_csv(fout, index=False)
        monthly_join.to_csv(fout, na_rep='NA')
