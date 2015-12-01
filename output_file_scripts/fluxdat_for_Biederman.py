# Script to create and export data files for Joel Biederman's synthesis

import sys
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )

import load_nmeg as ld
import transform_nmeg as tr
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipdb as ipdb

datapath = ('/home/greg/sftp/eddyflux/Ameriflux_files/provisional/')
fileList = os.listdir(datapath)

startyear = 2007
endyear = 2014

# List AF site names in same order
siteNames = [ 'US-Vcm', 'US-Vcp', 'US-Wjs', 'US-Mpj', 'US-Ses' ]

for i, site in enumerate( siteNames ):

    # Get the multi-year ameriflux dataframe 
    site_df = ld.get_multiyr_aflx( site, datapath, gapfilled=True, 
                                   startyear=startyear, endyear=endyear )

    # Create a daily dataframe these are pretty much the defaults
    site_df_resamp = tr.resample_30min_aflx( site_df, 
            freq='1D', c_fluxes=[ 'GPP', 'RECO', 'FC_F' ], 
            le_flux=[ 'LE_F' ], avg_cols=[ 'TA_F', 'RH_F', 'SW_IN_F', 'RNET' ], 
            precip_col='P_F' , tair_col='TA_F' )


    #ipdb.set_trace()

    # Export
    site_df_resamp.to_csv( '../processed_data/' + site 
            + '_biederman_synth.csv',
            na_rep = '-9999')


# Function for plotting fixed and original data
#def plotfixed(df, var1):
#    # Plot filled series over original data
#    plt.figure()
#    plt.plot(df.index, df[var1], '-r', df.index, df[var1 + '_fixed'], '-b')
#    #plt.plot(df.index, df[var2], 'om')
#    plt.legend(['Orig ' + var1, 'Fixed ' + var1, 'Lin'])
#    plt.title(var1 + ' data filling')
