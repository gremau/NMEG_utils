""" 
Functions for basic plots of NMEG data

 plot_nmeg.py
 Greg Maurer
"""

#import ipdb as ipdb
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt

gcolour= [0.9, 0.5, 0.0];
scolour=[0.6, 0.2, 0];
jcolour=[0.25, 1.0, 0.0];
pjcolour=[0.0, 0.5, 0.0];
pcolour=[0.5, 0.5, 1.0];
mcolour=[0.0, 0.0, 0.6];

sites = ['Seg', 'Ses', 'Wjs', 'Mpj', 'Vcp', 'Vcm']
names = ['Grassland', 'Shrubland', 'Juniper Sav.', 
              'Pinyon-Juniper', 'Ponderosa Pine', 'Mixed Conifer']
palette = [gcolour, scolour, jcolour, pjcolour, pcolour, mcolour]


def plot_tseries( dict_in, varname, texty, fighandle, ylab,
        xlims=[ dt.datetime( 2007, 1, 1 ), dt.datetime( 2014, 12, 31 )],
        ylims=None, sitelist=sites, sitenames=names,
        colors=palette):
    ax = list();
    for i, site in enumerate(sitelist):
        # Pull out x and y axes
        idx = dict_in[site].index
        if type(dict_in[site]) is pd.Series:
            var = dict_in[site]
        else:
            var = dict_in[site][varname]
            
        ax.append(fighandle.add_subplot(6, 1, i+1))
        plt.plot( xlims, [0, 0], ':k')
        if len(var.shape) == 2:
            plt.plot( idx, var[varname[0]], color=colors[i], lw=1.25 )
            plt.plot( idx, -var[varname[1]], color=colors[i], lw=1.25,
                    alpha=0.5 )
        else:
            plt.plot( idx, var, color=colors[i], lw=1.25 )
        if ylims:
            plt.ylim( ylims )
            
        plt.xlim( xlims )
        plt.text( dt.datetime( 2007, 2, 1 ), texty, sitenames[i], size=14  )
        plt.setp( ax[i].get_yticklabels(), fontsize=13)
        if i < 5:
            plt.setp( ax[i].get_xticklabels(), visible=False)
    
    for i in (0, 2, 4):
        ax[i].set_ylabel(ylab, fontsize=14)
    
    plt.setp( ax[5].get_xticklabels(), fontsize=14 )
    return ax
