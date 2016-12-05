# Script to create and export data files for Joel Biederman's synthesis

import sys
sys.path.append( '/home/greg/current/NMEG_utils/py_modules/' )

import load_nmeg as ld
import transform_nmeg as tr
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pdb as pdb

# These two paths should lead to identical data folders (local and ftp copy)
#datapath = ('/home/greg/sftp/eddyflux/Ameriflux_files/FLUXNET2015_a/')
datapath = ('/home/greg/data/rawdata/NMEG/FLUXNET2015_a/')

fileList = os.listdir(datapath)

startyear = 2007
endyear = 2015

# List AF site names in same order
siteNames = [ 'US-Vcm','US-Vcp','US-Wjs','US-Mpj','US-Ses','US-Seg','US-Sen' ]
#siteNames = [ 'US-Sen' ]

# Function for plotting fixed and original data
# Plot filled series over original data
def plotpartition(sitename):
    fig = plt.figure()
    plt.suptitle(sitename)
    fig.add_subplot(2,1,1)
    plt.plot(site_df_resamp.index, site_df_resamp.GPP_g_int, '-k')
    plt.plot(site_df_resamp.index, site_df_resamp.GPP_MR2005_g_int, '--r')
    plt.plot(site_df_resamp.index, site_df_resamp.GPP_GL2010_g_int, '--b')
    plt.plot(site_df_resamp.index, site_df_resamp.GPP_MR2005_g_int_ecb, ':r')
    plt.plot(site_df_resamp.index, site_df_resamp.GPP_GL2010_g_int_ecb, ':b')

    plt.ylabel('GPP')
    plt.legend(['Litvak AF','Reichstein 05','Lasslop 10', 'Reich05 ECB',
        'Lass10 ECB'])
    fig.add_subplot(2,1,2)
    plt.plot(site_df_resamp.index, site_df_resamp.RECO_g_int, '-k')
    plt.plot(site_df_resamp.index, site_df_resamp.Reco_MR2005_g_int, '--r')
    plt.plot(site_df_resamp.index, site_df_resamp.Reco_GL2010_g_int, '--b')
    plt.plot(site_df_resamp.index, site_df_resamp.Reco_MR2005_g_int_ecb, ':r')
    plt.plot(site_df_resamp.index, site_df_resamp.Reco_GL2010_g_int_ecb, ':b')

    plt.ylabel('Reco')
    plt.show()
    return fig

for i, site in enumerate( siteNames ):

    # Get the multi-year ameriflux dataframe 
    site_df = ld.get_multiyr_aflx( site, datapath, gapfilled=True, 
                                   startyear=startyear, endyear=endyear )

    # Create a daily dataframe these are pretty much the defaults
    site_df_resamp = tr.resample_30min_aflx( site_df, 
            freq='1D', c_fluxes=[ 'GPP', 'RECO', 'FC_F' ], 
            le_flux=['LE_F'], avg_cols=['TA_F', 'RH_F', 'SW_IN_F', 'RNET_F'], 
            sum_cols=['P_F'] , tair_col='TA_F' )
    
    # Get multiyear eddyproc file
    site_df_MR2005 = ld.get_multiyr_eddyproc( site, datapath + 'eddyproc_out/',
            GL2010=False, startyear=startyear, endyear=endyear )
    # Ensure carbon balance steps (GPP = RE-NEE, add negative values to RE)
    # Raw GPP (contains negative values)
    diff = site_df_MR2005.Reco - site_df.FC_F
    negGPPix = diff<0
    site_df_MR2005['GPP_ecb'] = diff
    site_df_MR2005.GPP_ecb.loc[negGPPix] = 0
    site_df_MR2005['Reco_ecb'] = site_df_MR2005.Reco
    site_df_MR2005.Reco_ecb[negGPPix] = (
            site_df_MR2005.Reco_ecb[negGPPix] - diff[negGPPix])


    # Create a daily dataframe using just C fluxes
    site_df_MR2005_resamp = tr.resample_30min_aflx( site_df_MR2005, 
            freq='1D', c_fluxes=[ 'GPP_f', 'Reco', 'GPP_ecb', 'Reco_ecb'], 
            le_flux=[], avg_cols=[], int_cols=[], minmax_cols=[],
            sum_cols=[] , tair_col=None)

    # Get multiyear eddyproc file - GL2010
    site_df_GL2010 = ld.get_multiyr_eddyproc( site, datapath + 'eddyproc_out/',
            GL2010=True, startyear=startyear, endyear=endyear )
    # Ensure carbon balance steps (GPP = RE-NEE, add negative values to RE)
    # Raw GPP (contains negative values)
    diff = site_df_GL2010.Reco_HBLR - site_df.FC_F
    negGPPix = diff<0
    site_df_GL2010['GPP_HBLR_ecb'] = diff
    site_df_GL2010.GPP_HBLR_ecb.loc[negGPPix] = 0
    site_df_GL2010['Reco_HBLR_ecb'] = site_df_GL2010.Reco_HBLR
    site_df_GL2010.Reco_HBLR_ecb[negGPPix] = (
            site_df_GL2010.Reco_HBLR_ecb[negGPPix] - diff[negGPPix])

    # Create a daily dataframe using just C fluxes
    site_df_GL2010_resamp = tr.resample_30min_aflx( site_df_GL2010, 
            freq='1D', c_fluxes=[ 'GPP_HBLR','Reco_HBLR',
                                  'GPP_HBLR_ecb','Reco_HBLR_ecb'],
            le_flux=[], avg_cols=[], int_cols=[],
            minmax_cols=[],
            sum_cols=[] , tair_col=None )

    # Add resampled MR2005 and GL2010 (raw, not balanced) columns to output
    site_df_resamp['Reco_MR2005_g_int'] = site_df_MR2005_resamp.Reco_g_int
    site_df_resamp['GPP_MR2005_g_int'] = site_df_MR2005_resamp.GPP_f_g_int
    site_df_resamp['Reco_MR2005_g_int_ecb'] = site_df_MR2005_resamp.Reco_ecb_g_int
    site_df_resamp['GPP_MR2005_g_int_ecb'] = site_df_MR2005_resamp.GPP_ecb_g_int

    site_df_resamp['Reco_GL2010_g_int'] = site_df_GL2010_resamp.Reco_HBLR_g_int
    site_df_resamp['GPP_GL2010_g_int'] = site_df_GL2010_resamp.GPP_HBLR_g_int
    site_df_resamp['Reco_GL2010_g_int_ecb'] = site_df_GL2010_resamp.Reco_HBLR_ecb_g_int
    site_df_resamp['GPP_GL2010_g_int_ecb'] = site_df_GL2010_resamp.GPP_HBLR_ecb_g_int

    # Export
    site_df_resamp.to_csv( '../processed_data/biederman_synth/' + site 
            + '_biederman_synth_20161206.csv',
            na_rep = '-9999')
    fig = plotpartition(site)
    
    #pdb.set_trace()

