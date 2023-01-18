import uproot
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward1 as ak
import pandas as pd
import numpy as np
import seaborn as sns

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-c","--cat",dest="cat",default='tt', help="choose cat to decide wichle cut selection will be used. Options: lep,ak4,ak8,net")
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

outfilepath = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/ttoutfile"
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
bkg_array,signal_array,data_array,sumWeight = extractCutedBranch(config,args.year,args.cat)

##====================================================================================================================================================================================
##===========================first plot TT CR========================================================================================================================
##===============================================================================================================================================================================================================
channels = ['ak4','net']
massZZ_low_bins = np.linspace(500,1700,25)
massZZ_high_bins = np.array([2000,3500])
massZZ_bins = bh.axis.Variable(ak.from_numpy(np.append(massZZ_low_bins,massZZ_high_bins)).to_list())
ratioBranch={}
with uproot.recreate(f"{outfilepath}/tt_bkg.root") as outfile:
    for channel in channels:
        if channel=='ak4':
            #varbs = ['mass2jet','pt2jet','mass2l2jet']
            varbs = ['mass2l2jet']
        if channel=='net':
            #varbs = ['massmerged','ptmerged','mass2lj']
            varbs = ['mass2lj']

        for var in varbs:
            #print(f"[INFO] it is {var} plot")
            nbins, xmin, xmax = config['bininfo'][var][0], config['bininfo'][var][1], config['bininfo'][var][2]
            if(var=="mass2l2jet" or var=="mass2lj"):
                edge = np.append(massZZ_low_bins,massZZ_high_bins)
            else:
                edge = np.linspace(xmin, xmax, nbins+1)

            if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2jl')!=-1 or var.find('mass2l2jet')!=-1:
                islogY = True
            else:
                islogY = False
                
            #fill histo 
            bkg_hists = {}; Data_hist = {}; signal_hists = {}
            regions = ['CR','SR']

            for reg in regions:
                print(f"[INFO] it is {var} in {reg} with {channel} cat plot")
                #if reg=='SR' and (var=='mass2l2jet' or var=='mass2lj'): continue
                bkg_hists[reg] = {}; Data_hist[reg] = {}; signal_hists[reg] = {}
                bkg_hists[reg][channel] = [None,None,None]; Data_hist[reg][channel] = None; signal_hists[reg][channel] = []
                for sample in config['Samples_lists']:
                    print(f"This is {sample} in {channel}")
                    if sample!='Data':
                        temp_array = bkg_array[reg][channel][sample]
                        #retray weight and apply paritcleNet weight
                        weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                            
                        if channel=='net':
                            if sample == 'ZZTo2Q2L' or sample =='WZTo2Q2L':
                                sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)
                                #elif sample.find('DY')!=-1:
                                #    sf_Net = GetParticleNetbkgSF(temp_array,'ZvsQCD','DY')
                                #elif sample.find('TTJets')!=-1 or sample.find('WWTo2L2Nu')!=-1:
                                #    sf_Net = GetParticleNetbkgSF(temp_array,'ZvsQCD','TT')
                            else:
                                sf_Net = ak.ones_like(temp_array['EventWeight'])
                            weights = weights*sf_Net

                        if(var=="mass2l2jet" or var=="mass2lj"):
                            temp_hist = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                            #print(temp_array[var])
                            #print(weights)
                            temp_hist.fill(temp_array[var],weight = weights)
                        else:
                            temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)


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
                        if(var=="mass2l2jet" or var=="mass2lj"):
                            Data_hist[reg][channel] = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                            Data_hist[reg][channel].fill(temp_array[var],weight=weights)
                        else:
                            Data_hist[reg][channel] = get_hist(temp_array[var],weights,nbins,xmin,xmax)


                    
                for sample in config['signal_lists']:
                    temp_array = signal_array[reg][channel][sample]
                    weights = (temp_array['EventWeight']*config['lumi'][args.year]*config['samples_inf'][sample][1]*100)/sumWeight[sample] #scale 100
                    temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                    signal_hists[reg][channel].append(temp_hist)
            
                print(f"Fill done {var}")

                #draw var
                print(f"[INFO] it is {channel} plot")

                if channel =='ak4':
                    text = 'resolved'
                elif channel =='net':
                    text = 'merged'

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
                ax.set_xlim(xmin, xmax); ax.set_xticklabels([])
                ax.set_ylabel('Events / bin', ha='right', y=1.0)
                
                ##SIGNAL
                #if(args.year!='2016APV' and args.year!='2017'):
                #    colors = ['blue', 'red']
                #    plot_hist(signal_hists[reg][channel],label=[ var for var in ['ggH(m1000)','VBF(m1500)']],linestyle=[style for style in [':','--']], color=[color for color in colors])
                
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
                savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{args.cat}/{args.year}'
                if not os.path.exists(savepath):
                    os.mkdir(savepath)
                plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{args.cat}/{args.year}/{var}_{text}_in{reg}.png')
                #plt.show()
                plt.close()  
            

            ##===================================================================================================================================================================
            ##===========================second: drive ratio of Data(CR_eu)/MC(CR_eu) MZZ==========================================================================================
            ##===================================================================================================================================================================
            if(var=='mass2l2jet'):
                print("[INFO] Get eu CR in resolved case. Star to drive ratio")
                data_content = Data_hist[reg][channel].view(flow=False).value
                MC_content = (bkg_hists['CR'][channel])[1].view(flow=False).value
                data_content_err = get_err(Data_hist[reg][channel])
                MC_content_err = get_err((bkg_hists['CR'][channel])[1])  
                temp_raio = data_content/MC_content
                temp_raio = np.nan_to_num(temp_raio,nan=1.0)
                temp_raio_err = np.sqrt(((data_content_err/data_content)*(data_content_err/data_content))+((MC_content_err/MC_content)*(MC_content_err/MC_content)))
                temp_raio_err = np.nan_to_num(temp_raio_err,nan=1.0)

                ratioBranch['resolevd_raio'] = temp_raio
                ratioBranch['resolevd_raio_err'] = temp_raio_err
                print("[INFO] resolevd_raio = ",temp_raio)
                print("[INFO] resolevd_raio_err = ",ratioBranch['resolevd_raio_err'])

                hist_tt_SR = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                hist_tt_SR.fill((bkg_hists['SR'][channel])[1].view(flow=False).value,weight=temp_raio)
                outfile['resolved_tt'] = hist_tt_SR

                ######plot and store ratio
                #print("[INFO] plot raio in resolved case")
                #x_axis = np.append(massZZ_low_bins,massZZ_high_bins)
                ##width = 0.15  # the width of the bars
                #x_pos = []
                #y_val = []
                #x_err = []
                #y_err = []
                #f, ax = plt.subplots(figsize=(10, 10))
                #hep.cms.label(data=True, llabel='Preliminary', year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %config['lumi'][args.year], fontname='sans-serif')
                #for i in range(0,len(x_axis)-1):
                #    x = (x_axis[i]+x_axis[i+1])/2
                #    x_pos.append(x)
                #    y = temp_raio[i]
                #    y_val.append(y)
                #    xerr = (x_axis[i+1]-x_axis[i])/2
                #    x_err.append(xerr)
                #    yerr = temp_raio_err[i]
                #    y_err.append(yerr)
                #    ax.plot(x,y,'o', markersize=8 ,color='black')
                #ax.errorbar(x_pos,y_val,xerr=x_err,yerr=y_err,elinewidth = 1.5,linestyle='none',color='black',label = 'Data/MC eu Ratio')
#
                #ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0); ax.set_ylabel('Ratio', ha='right', y=1.0)
                #ax.set_ylim(-0.5, 2)
                #ax.text(0.05, 0.92, f'{text}', transform=ax.transAxes, fontweight='bold') 
                #ax.legend(loc='upper right')
#
                #plt.savefig('resolved_rato.png')



            if(var=='mass2lj'):
                print("[INFO] Get eu CR in merged case. Star to drive ratio")
                data_content = Data_hist['CR'][channel].view(flow=False).value
                MC_content = (bkg_hists['CR'][channel])[1].view(flow=False).value
                data_content_err = get_err(Data_hist['CR'][channel])
                MC_content_err = get_err((bkg_hists['CR'][channel])[1])  
                print("[INFO] data_content = ",data_content)
                print("[INFO] MC_content = ",MC_content)

                temp_raio = data_content/MC_content
                temp_raio = np.nan_to_num(temp_raio,nan=1.0)
                temp_raio_err = np.sqrt(((data_content_err/data_content)*(data_content_err/data_content))+((MC_content_err/MC_content)*(MC_content_err/MC_content)))
                temp_raio_err = np.nan_to_num(temp_raio_err,nan=1.0)

                ratioBranch['merged_raio'] = temp_raio
                ratioBranch['merged_raio_err'] = temp_raio_err

                print("[INFO] merged_raio = ",ratioBranch['merged_raio'])

                #================TT SR
                hist_tt_SR = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                hist_tt_SR.fill((bkg_hists['SR'][channel])[1].view(flow=False).value,weight=temp_raio)
                outfile['merged_tt'] = hist_tt_SR



                ######plot and store ratio
                #print("[INFO] plot raio in merged case")
                #x_axis = np.append(massZZ_low_bins,massZZ_high_bins)
                ##width = 0.15  # the width of the bars
                #x_pos = []
                #y_val = []
                #x_err = []
                #y_err = []
                #f, ax = plt.subplots(figsize=(10, 10))
                #hep.cms.label(data=True, llabel='Preliminary', year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %config['lumi'][args.year], fontname='sans-serif')
                #for i in range(0,len(x_axis)-1):
                #    x = (x_axis[i]+x_axis[i+1])/2
                #    x_pos.append(x)
                #    y = temp_raio[i]
                #    y_val.append(y)
                #    xerr = (x_axis[i+1]-x_axis[i])/2
                #    x_err.append(xerr)
                #    yerr = temp_raio_err[i]
                #    y_err.append(yerr)
                #    ax.plot(x,y,'o', markersize=8 ,color='black')
                #ax.errorbar(x_pos,y_val,xerr=x_err,yerr=y_err,elinewidth = 1.5,linestyle='none',color='black',label = 'Data/MC eu Ratio')
#
                #ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0); ax.set_ylabel('Ratio', ha='right', y=1.0)
                #ax.set_ylim(-0.5, 2)
                #ax.text(0.05, 0.92, f'{text}', transform=ax.transAxes, fontweight='bold') 
                #ax.legend(loc='upper right')
#
                #plt.savefig('merged_rato.png')
                print("[info] merged raio down")

    #print(ratioBranch.keys())
    #print(ratioBranch[i] for i in ratioBranch.keys())
    outfile['ratio'] = ratioBranch
            
            





                



                


