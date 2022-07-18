import uproot
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward1 as ak
import pandas as pd
import numpy as np
import seaborn as sns

import functools
import operator
#cat = 'lep'
#year ='2016'

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-c","--cat",dest="cat",default='lep', help="choose cat to decide wichle cut selection will be used. Options: lep,ak4,ak8,net")
args = parser.parse_args()
#===========================================load config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *

import yaml
sf_particleNet_signal = {}
with open('/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/NetSF_signal_2016Legacy.yml') as f:
    sf_particleNet_signal = yaml.safe_load(f)
config = {}
with open("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL16.yml") as f:
    config = yaml.safe_load(f)
#======================================================================================================================================================


#==================================================set plot color==================================================
def set_sns_color(*args):
    sns.palplot(sns.color_palette(*args))
    sns.set_palette(*args)

color_order_bkg = sns.color_palette('Accent', 3)
color_order_bkg.reverse()

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
#extract branch for each sample
def extractCutedBranch(config):
    #load root file and read array
    bkg_array = {}
    data_array = None
    signal_array = {}
    sumWeight = {}
    filepath = config['ori_dir']+f'/{args.year}/'
    print(f'File path is {filepath}')
    for sample in config['Samples_lists']:
        print(f"This is {sample}")
        if sample!='Data':
            indir = config['ori_dir']+f'/{args.year}/'+config['samples_inf'][sample][0]+'/skimed'
            files = find_this_rootfiles(indir)
            sumWeight[sample] = 0

            for file in files:
                with uproot.open(f'{indir}/{file}') as f:
                    this_sumWeight_h = f['sumWeights'].to_boost()
                    this_sumWeight = this_sumWeight_h.sum()
                    #print(f'this sum weight = {this_sumWeight}')
                    sumWeight[sample] += this_sumWeight

            bkg_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=config['var_read_lists'])

        else:
            data_path = config['ori_dir']+f'/{args.year}/'+f'Data/skimed/Data{args.year}UL_noDuplicates.root'
            data_array = uproot.lazy([f"{data_path}:passedEvents"],filter_name=config['var_read_lists'])

    if(args.year!='2016APV' and args.year!='2017'):
        for sample in config['signal_lists']:
            print(f"This is {sample}")
            signal_path = config['ori_dir']+f"/{args.year}/"+config['samples_inf'][sample][0]

            sumWeight[sample] = 0
            with uproot.open(signal_path) as f:
                this_sumWeight_h = f['sumWeights'].to_boost()
                this_sumWeight = this_sumWeight_h.sum()
                sumWeight[sample] += this_sumWeight

                signal_array[sample] = f['passedEvents'].arrays(filter_name=config['var_read_lists'],library="ak")

    #=======cut
    regions = ['CR','SR']
    #regions = ['CR']
    bkg_array_cut = {}; data_array_cut = {}; signal_array_cut = {}
    for reg in regions:
        bkg_array_cut[reg] = {}; data_array_cut[reg] = {}; signal_array_cut[reg] = {}
        for channel in config['channel']:
            bkg_array_cut[reg][channel] = {}; data_array_cut[reg][channel] = None; signal_array_cut[reg][channel] = {}
            for sample in config['Samples_lists']:
                print(f"This is {sample} in {reg} in {channel}")
                #print(f"selection text = {selection}")
                selection = config['cut'][reg][channel][args.cat]
                print(f"selection text = {selection}")

                if sample!='Data':
                    temp_array = bkg_array[sample]
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    #cut_array = make_cut(temp_array,region = reg, cat = cat)
                    bkg_array_cut[reg][channel][sample] = temp_array[cut_array]
                else:
                    temp_array = data_array
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    #cut_array = make_cut(temp_array,region = reg, cat = cat)
                    data_array_cut[reg][channel] = temp_array[cut_array]
            if(args.year!='2016APV' and args.year!='2017'):
                for sample in config['signal_lists']:
                    temp_array = signal_array[sample]
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    #cut_array = make_cut(temp_array,region = reg, cat = cat)
                    signal_array_cut[reg][channel][sample] = temp_array[cut_array]


    return bkg_array_cut,signal_array_cut,data_array_cut,sumWeight

####======================================================================================================
####======================================Draw lists of  varbs============================================
####======================================And save plots==================================================
####======================================================================================================
bkg_array,signal_array,data_array,sumWeight = extractCutedBranch(config)
###====================set draw var according to different selections==========================================================
#varbs = ['pt2l','mass2l','particleNetZvsQCD','massmerged','ptmerged']
#varbs = ['massmerged','pt2l','mass2l','particleNetXbbvsQCD','Met']
#varbs = ['massmerged','pt2l','mass2l']
if(args.cat=='lep'):
    varbs = ['pt2l','mass2l']
if(args.cat=='ak4'):
    varbs = ['mass2jet','pt2jet','pt2l','mass2l','KD_jjVBF','mass2l2jet','KD_Zjj']
if(args.cat=='ak8'):
    varbs = ['massmerged','ptmerged','pt2l','mass2l','KD_JVBF','particleNetZvsQCD','mass2lj','KD_ZJ']
if(args.cat=='net'):
    varbs = ['massmerged','ptmerged','pt2l','mass2l','KD_JVBF','particleNetZvsQCD','mass2lj','KD_ZJ']


for var in varbs:
    print(f"[INFO] it is {var} plot")
    nbins, xmin, xmax = config['bininfo'][var][0], config['bininfo'][var][1], config['bininfo'][var][2]
    edge = np.linspace(xmin, xmax, nbins+1)
    if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2jl')!=-1 or var.find('mass2l2jet')!=-1:
        islogY = True
    else:
        islogY = False

    #fill histo
    bkg_hists = {}; Data_hist = {}; signal_hists = {}
    regions = ['CR','SR']
    for reg in regions:
        if reg=='SR' and (var=='mass2l2jet' or var=='mass2lj'): continue

        bkg_hists[reg] = {}; Data_hist[reg] = {}; signal_hists[reg] = {}
        for channel in config['channel']:
            bkg_hists[reg][channel] = [None,None,None]; Data_hist[reg][channel] = None; signal_hists[reg][channel] = []
            for sample in config['Samples_lists']:
                print(f"This is {sample} in {channel}")
                if sample!='Data':
                    temp_array = bkg_array[reg][channel][sample]
                    #retray weight and apply paritcleNet weight
                    weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]

                    if args.cat=='net':
                        if sample == 'ZZTo2Q2L' or sample =='WZTo2Q2L':
                            sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)
                        elif sample.find('DY')!=-1:
                            sf_Net = GetParticleNetbkgSF(temp_array,'ZvsQCD','DY')
                        elif sample.find('TTJets')!=-1 or sample.find('WWTo2L2Nu')!=-1:
                            sf_Net = GetParticleNetbkgSF(temp_array,'ZvsQCD','TT')
                        else:
                            sf_Net = ak.ones_like(temp_array['EventWeight'])
                        weights = weights*sf_Net

                    temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                    #temp_hist = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                    #print(temp_array[var])
                    #print(weights)
                    #temp_hist.fill(temp_array[var],weight = weights)


                    if sample.find('DY')!=-1:
                        if (bkg_hists[reg][channel])[2]==None:
                            (bkg_hists[reg][channel])[2] = temp_hist
                        else:
                            (bkg_hists[reg][channel])[2]+=temp_hist
                    if sample.find('TTJets')!=-1 or sample.find('WWTo2L2Nu')!=-1:
                        if (bkg_hists[reg][channel])[1]==None:
                            (bkg_hists[reg][channel])[1] = temp_hist
                        else:
                            (bkg_hists[reg][channel])[1]+=temp_hist
                    if sample.find('WZTo2Q2L')!=-1 or sample.find('ZZTo2Q2L')!=-1:
                        if (bkg_hists[reg][channel])[0]==None:
                            (bkg_hists[reg][channel])[0] = temp_hist
                        else:
                            (bkg_hists[reg][channel])[0]+=temp_hist
                else:
                    temp_array = data_array[reg][channel]
                    weights = np.ones_like(temp_array['EventWeight'])
                    print(f'data weight  = {weights}')
                    Data_hist[reg][channel] = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                    #temp_hist = bh.Histogram(massZZ_bins)
                    #temp_hist.fill(temp_array[var],weight=weights)
            if(args.year!='2016APV' and args.year!='2017'):

                for sample in config['signal_lists']:
                    temp_array = signal_array[reg][channel][sample]
                    weights = (temp_array['EventWeight']*config['lumi'][args.year]*config['samples_inf'][sample][1]*100)/sumWeight[sample] #scale 100
                    temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                    signal_hists[reg][channel].append(temp_hist)

        print(f"Fill done {var}")

        #draw var
        for channel in config['channel']:

            print(f"[INFO] it is {channel} plot")

            if channel =='isEE':
                text = 'twoEle'
            elif channel =='isMuMu':
                text = 'twoMuon'

            plot_unce = True
            set_sns_color(color_order_bkg)
            f = plt.figure(figsize=(12,12))
            gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0)
            ##================================ Upper histogram panel=========================================
            ax = f.add_subplot(gs[0])
            hep.cms.label(data=True, llabel='Preliminary',year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%config['lumi'][args.year], fontname='sans-serif')
            ax.set_xlim(xmin, xmax); ax.set_xticklabels([]); ax.set_ylabel('Events / bin', ha='right', y=1.0)

            ##BACKGRUND
            #hep.histplot(bkg_hists[channel],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            plot_hist(bkg_hists[reg][channel],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            bkg_hist = bkg_hists[reg][channel][0]+bkg_hists[reg][channel][1]+bkg_hists[reg][channel][2]
            bkg_tot = bkg_hist.values()
            bkg_err = get_err(bkg_hist)
            #bkg_err = np.sqrt(bkg_hist.view(flow=False).variance)

            if plot_unce:
                #ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='dimgrey', facecolor='none', linewidth=0) ## draw bkg unce.
                ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.
            ax.set_xlim(xmin, xmax); ax.set_xticklabels([]);
            ax.set_ylabel('Events / bin', ha='right', y=1.0);

            ##SIGNAL
            if(args.year!='2016APV' and args.year!='2017'):
                colors = ['blue', 'red']
                plot_hist(signal_hists[reg][channel],label=[ var for var in ['ggH(m1000)','VBF(m1500)']],linestyle=[style for style in [':','--']], color=[color for color in colors])

            ##DATA
            data_err = get_err(Data_hist[reg][channel])
            data = Data_hist[reg][channel].values()
            #hep.histplot(Data_hist[channel], yerr=data_err,label='Data', histtype='errorbar', color='k', markersize=15, elinewidth=1.5) ## draw data
            plot_hist(Data_hist[reg][channel],label='Data', histtype='errorbar', color='k', markersize=15, elinewidth=1.5) ## draw data
            if islogY:
                ax.set(yscale = "log")
                ax.set_ylim(1e-1, 3*ax.get_ylim()[1])
            else:
                ax.set_ylim(0, ax.get_ylim()[1])
                ax.set_ylim(0, 1.5*max(data))
            ax.text(0.05, 0.92, f'{text}', transform=ax.transAxes, fontweight='bold')
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

            #plt.savefig(f'./plots/leptionic_{var}_{text}.png')
            savepath = f'./plots/{args.cat}/{args.year}'
            if not os.path.exists(savepath):
                os.mkdir(savepath)
            plt.savefig(f'./plots/{args.cat}/{args.year}/{var}_{text}_in{reg}.png')
            #plt.show()
            plt.close()

    #=====================================plot 2D for KD=========================================================
    if(args.year!='2016APV' and args.year!='2017'):
        if(var.find("KD_Z")!=-1):
            if var=='KD_Zjj':
                massZZ = 'mass2l2jet'
            elif var=="KD_ZJ":
                massZZ = 'mass2lj'
            print("[INFO} plot 2D for KD")
            regions = ['CR','SR']
            for reg in regions:
                hist2D={}
                hist2D['ggh'] = bh.Histogram(bh.axis.Regular(50, 300, 3500), bh.axis.Regular(50, 0, 1))
                hist2D['VBF'] = bh.Histogram(bh.axis.Regular(50, 300, 3500), bh.axis.Regular(50, 0, 1))
                hist2D['DY'] = bh.Histogram(bh.axis.Regular(50, 300, 3500), bh.axis.Regular(50, 0, 1))
                array_DY = None
                for sample in config['Samples_lists']:

                    if sample.find('DY')!=-1:
                        temp_array = bkg_array[reg][channel][sample]
                        hist2D['DY'].fill(temp_array[massZZ],temp_array[var])

                hist2D['ggh'].fill(signal_array[reg][channel]['ggH1000'][massZZ],signal_array[reg][channel]['ggH1000'][var])
                hist2D['VBF'].fill(signal_array[reg][channel]['VBF1500'][massZZ],signal_array[reg][channel]['VBF1500'][var])

                for key in hist2D.keys():
                    areas = functools.reduce(operator.mul, hist2D[key].axes.widths)
                    density = hist2D[key].view() / hist2D[key].sum() / areas
                    fig, ax = plt.subplots(figsize=(12,12))
                    hep.cms.label(data=True, llabel='Preliminary',year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%config['lumi'][args.year], fontname='sans-serif')
                    mesh = ax.pcolormesh(*hist2D['ggh'].axes.edges.T, density.T)
                    ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
                    ax.set_ylabel('A.U', ha='right', y=1.0)
                    fig.colorbar(mesh)

                    plt.savefig(f'./plots/{args.cat}/{args.year}/2D_{key}_{var}_{text}_in{reg}.png')

                plt.close()
