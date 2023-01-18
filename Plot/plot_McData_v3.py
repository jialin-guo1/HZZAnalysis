print('[INFO] Please kindly let me know which selection case you want to study. And only following options are avaiable:')
print('1.lep, 2.resolved, 3.merged_notag, 4.merged_tag')
cutcat = input()

import uproot as up
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward as ak
import pandas as pd
import numpy as np
import seaborn as sns

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2018', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-c","--cat",dest="cat",default='lep', help="choose cat to decide wichle cut selection will be used. Options: lep,ak4,ak8,net")
args = parser.parse_args()

#===========================================load config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

config = setting().config
#==================================================set plot color==================================================
def set_sns_color(*args):
    sns.palplot(sns.color_palette(*args))
    sns.set_palette(*args)

color_order_bkg = sns.color_palette('Accent', 3)
color_order_bkg.reverse()
set_sns_color(color_order_bkg)

use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
if use_helvet:
    CMShelvet = hep.style.CMS
    CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.style.use(CMShelvet)
else:
    plt.style.use(hep.style.CMS)
#=================================================================================================================================================================================================
#=================================================================================================================================================================================================
#=================================================================================================================================================================================================
hist = GetHisto(args.year,cutcat).hist
#==============================get raw histo

def plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data):
    '''
        input: histogram as oder of zv,tt,dy and data
    '''
    ###########start to draw######################
    plot_unce = True
    f = plt.figure(figsize=(12,12))
    gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0)
    ##================================ Upper histogram panel=========================================
    ax = f.add_subplot(gs[0])
    hep.cms.label(data=True, llabel='Preliminary',year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%config['lumi'][args.year], fontname='sans-serif')
    ax.set_xlim(xmin, xmax); ax.set_xticklabels([]); ax.set_ylabel('Events / bin', ha='right', y=1.0)
    ##BACKGRUND
    plot_hist([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
    bkg_tot = (hist_zv+hist_tt+hist_DY).values()
    bkg_err = get_err(hist_zv+hist_tt+hist_DY)
    if plot_unce:
        ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.
    
    ##DATA
    data_err = get_err(hist_data)
    data = hist_data.values()
    plot_hist(hist_data,label='Data', histtype='errorbar', color='k', markersize=15, elinewidth=1.5) ## draw dat
    if islogY:
        ax.set(yscale = "log")
        ax.set_ylim(1e-1, 3*ax.get_ylim()[1])
    else:
        ax.set_ylim(0, ax.get_ylim()[1])
        ax.set_ylim(0, 1.5*max(data))
    ax.text(0.05, 0.92, f'{setting().text[cat]}', transform=ax.transAxes, fontweight='bold')
    hep.plot.yscale_legend
    ax.legend(fontsize=18)
    ##==========================================Ratio panel========================
    ax1 = f.add_subplot(gs[1]); ax1.set_xlim(xmin, xmax); ax1.set_ylim(0.001, 1.999)
    ax1.set_xlabel(config['bininfo'][var][3], ha='right', x=1.0); ax1.set_ylabel('Data / MC', ha='center')
    ax1.plot([xmin,xmax], [1,1], 'k'); ax1.plot([xmin,xmax], [0.5,0.5], 'k:'); ax1.plot([xmin,xmax], [1.5,1.5], 'k:')
    ratio=np.nan_to_num((data/bkg_tot),nan=-1)
    ratio_err = np.nan_to_num((data_err/bkg_tot),nan=-1)
    hep.histplot(ratio, yerr = ratio_err,bins=edge, histtype='errorbar', color='k', markersize=15, elinewidth=1)
    #hep.histplot(data/bkg_tot, yerr = data_err/bkg_err,bins=edge, histtype='errorbar', color='k', markersize=15, elinewidth=1)
    if plot_unce:
        ratio_unc_low = np.nan_to_num(((bkg_tot-bkg_err)/bkg_tot),nan=-1)
        ratio_unc_up = np.nan_to_num(((bkg_tot+bkg_err)/bkg_tot),nan=-1)
        ax1.fill_between(edge, ratio_unc_low.tolist()+[0],ratio_unc_up.tolist()+[0], step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.




##=================================================================================================================================================
##=====================================Draw variable===============================================================================================
##=================================================================================================================================================
###Set which var will be draw
if(cutcat=='lep'):
    varbs = ['pt2l','mass2l','lep_1_pt','lep_2_pt']
if(cutcat=='resolved'):
    varbs = ['mass2jet','pt2jet','pt2l','mass2l','KD_jjVBF','mass2l2jet','KD_Zjj']
if(cutcat.find('merged') != -1):
    varbs = ['massmerged','ptmerged','pt2l','mass2l','KD_JVBF','particleNetZvsQCD','particleNetZbbvslight','mass2lj','KD_ZJ']

for var in varbs:
    print(f"[INFO] it is {var} plot")
    nbins, xmin, xmax = config['bininfo'][var][0], config['bininfo'][var][1], config['bininfo'][var][2]
    edge = np.linspace(xmin, xmax, nbins+1)
    if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2jl')!=-1 or var.find('mass2l2jet')!=-1:
        islogY = True
    else:
        islogY = False    
    if cutcat=='lep' or cutcat=='merged_notag':
        for cat in setting().leptonic_cut_cats:
            #add hist
            hist_DY = hist[cutcat][f'DY_pt50To100_{cat}_{var}']+hist[cutcat][f'DY_pt100To250_{cat}_{var}'] \
                    +hist[cutcat][f'DY_pt250To400_{cat}_{var}']+hist[cutcat][f'DY_pt400To650_{cat}_{var}']+hist[cutcat][f'DY_pt650ToInf_{cat}_{var}']
            hist_tt = hist[cutcat][f'TTTo2L2Nu_{cat}_{var}']+hist[cutcat][f'WWTo2L2Nu_{cat}_{var}']
            hist_zv = hist[cutcat][f'WZTo2Q2L_{cat}_{var}']+hist[cutcat][f'ZZTo2Q2L_{cat}_{var}']
            hist_data = hist[cutcat][f'Data_{cat}_{var}']

            plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data)

            savepath = f'./plots/{cutcat}/{args.year}'
            if not os.path.exists(savepath):
                os.mkdir(savepath)
            plt.savefig(f'./plots/{cutcat}/{args.year}/{var}_{cat}.png')
            #plt.show()
            plt.close()

    if cutcat=='resolved' or cutcat=='merged_tag':
        for reg in setting().regions:
            for cat in setting().leptonic_cut_cats:
                for tag in setting().tags:
                    #add hist
                    hist_DY = hist[cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_{var}']+hist[cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_{var}'] \
                            +hist[cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_{var}']+hist[cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_{var}']+hist[cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_{var}']
                    hist_tt = hist[cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{var}']+hist[cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}']
                    hist_zv = hist[cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{var}']+hist[cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{var}']
                    hist_data = hist[cutcat][f'Data_{reg}_{cat}_{tag}_{var}']

                    plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data)

                    savepath = f'./plots/{cutcat}/{args.year}'
                    if not os.path.exists(savepath):
                        os.mkdir(savepath)
                    plt.savefig(f'./plots/{cutcat}/{args.year}/{var}_{reg}_{cat}_{tag}.png')
                    #plt.show()
                    plt.close()

    





    
