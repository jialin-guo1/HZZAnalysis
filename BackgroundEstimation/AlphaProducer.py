import uproot 
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward as ak
import pandas as pd
import numpy as np

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
#parser.add_argument("-c","--cat",dest="cat",default='lep', help="choose cat to decide wichle cut selection will be used. Options: lep,ak4,ak8,net")
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
massZZ_low_bins = np.linspace(500,1700,25)
massZZ_high_bins = np.array([2000,3500])
massZZ_bins = bh.axis.Variable(ak.from_numpy(np.append(massZZ_low_bins,massZZ_high_bins)).to_list())
regions = ['CR','SR']
print(f'massZZ bins = {massZZ_bins}')

for case_str in ['ak4','net']:
    bkg_array,signal_array,data_array,sumWeight = extractCutedBranch(config,args.year,case_str)
    #set var draw 
    #varbs = ['mass2lj']
    if case_str=='ak4':
        varbs = ['mass2l2jet']; case='resolved'
    elif case_str=='net':
        varbs = ['mass2lj']; case = 'merged'
    for var in varbs:
        print(f"[INFO] it is {var} plot")
        nbins, xmin, xmax = config['bininfo'][var][0], config['bininfo'][var][1], config['bininfo'][var][2]
        edge = np.linspace(xmin, xmax, nbins+1)
        if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1:
            islogY = True
        else:
            islogY = True

        #fill histo 
        bkg_hists = {}; Data_hist = {}; signal_hists = {}
        for reg in regions:
            bkg_hists[reg] = {}; Data_hist[reg] = {}; signal_hists[reg] = {}
            for cat in config['channel']:
                bkg_hists[reg][cat] = [None,None,None]; Data_hist[reg][cat] = None; signal_hists[reg][cat] = []
                for sample in config['Samples_lists']:
                    print(f"This is {sample} in {cat}")
                    if sample!='Data':
                        temp_array = bkg_array[reg][cat][sample]
                        #retray weight and apply paritcleNet weight
                        weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                        r'''
                        if sample == 'ZZTo2Q2L' or sample =='WZTo2Q2L':
                            sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)
                        elif sample.find('DY')!=-1:
                            sf_Net = GetParticleNetbkgSF(temp_array,'ZvsQCD','DY')
                        elif sample.find('TTJets')!=-1 or sample.find('WWTo2L2Nu')!=-1:
                            sf_Net = GetParticleNetbkgSF(temp_array,'ZvsQCD','TT')
                        else:
                            sf_Net = ak.ones_like(temp_array['EventWeight'])
                        weights = weights*sf_Net
                        '''

                        #temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                        temp_hist = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                        #print(temp_array[var])
                        #print(weights)
                        temp_hist.fill(temp_array[var],weight = weights)


                        if sample.find('DY')!=-1:
                            if (bkg_hists[reg][cat])[2]==None:
                                (bkg_hists[reg][cat])[2] = temp_hist
                            else:
                                (bkg_hists[reg][cat])[2]+=temp_hist
                        if sample.find('TTJets')!=-1 or sample.find('WWTo2L2Nu')!=-1:
                            if (bkg_hists[reg][cat])[1]==None:
                                (bkg_hists[reg][cat])[1] = temp_hist
                            else:
                                (bkg_hists[reg][cat])[1]+=temp_hist
                        if sample.find('WZTo2Q2L')!=-1 or sample.find('ZZTo2Q2L')!=-1:
                            if (bkg_hists[reg][cat])[0]==None:
                                (bkg_hists[reg][cat])[0] = temp_hist
                            else:
                                (bkg_hists[reg][cat])[0]+=temp_hist
                    else:
                        temp_array = data_array[reg][cat]
                        weights = np.ones_like(temp_array['EventWeight'])
                        print(f'data weight  = {weights}')
                        Data_hist[reg][cat] = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                        #Data_hist[reg][cat] = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                        #temp_hist = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                        Data_hist[reg][cat].fill(temp_array[var],weight=weights)

    print("Fill done")

    #produce Alpha function and store in file 
    ###store histo to a root file 
    AlphaBranch = {}
    outAlphafilepath = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile'
    with uproot.recreate(f"{outAlphafilepath}/AlphaRaio{args.year}_{case}.root") as outfile:
        for cat in config['channel']:
            if cat =='isEE':
                text = 'twoEle'
            elif cat =='isMuMu':
                text = 'twoMuon'
            else:
                text = '2lep'

            sig_content = (bkg_hists['SR'][cat])[2].view(flow=False).value
            bkg_content = (bkg_hists['CR'][cat])[2].view(flow=False).value
            print(f"sig_content = {sig_content}")
            print(f"bkg_content = {bkg_content}")
            sig_content_err = get_err((bkg_hists['SR'][cat])[2])
            bkg_content_err = get_err((bkg_hists['CR'][cat])[2])
            alpha = sig_content/bkg_content
            alpha_err = np.sqrt(((sig_content_err/sig_content)*(sig_content_err/sig_content))+((bkg_content_err/bkg_content)*(bkg_content_err/bkg_content)))

            print(f'Alpha function in {cat} in {case} case = {alpha}')

            #AlphaBranch[f'merged_{cat}'] = alpha
            #AlphaBranch[f'merged_{cat}_err'] = alpha_err
            AlphaBranch[f'{case}_{cat}'] = alpha
            AlphaBranch[f'{case}_{cat}_err'] = alpha_err

            x_axis = np.append(massZZ_low_bins,massZZ_high_bins)

            #width = 0.15  # the width of the bars
            x_pos = []
            y_val = []
            x_err = []
            y_err = []
            f, ax = plt.subplots(figsize=(10, 10))
            hep.cms.label(data=True, llabel='Preliminary', year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %config['lumi'][args.year], fontname='sans-serif')
            for i in range(0,len(x_axis)-1):
                x = (x_axis[i]+x_axis[i+1])/2
                x_pos.append(x)
                y = alpha[i]
                y_val.append(y)
                xerr = (x_axis[i+1]-x_axis[i])/2
                x_err.append(xerr)
                yerr = alpha_err[i]
                y_err.append(yerr)
                ax.plot(x,y,'o', markersize=8 ,color='black')
            ax.errorbar(x_pos,y_val,xerr=x_err,yerr=y_err,elinewidth = 1.5,linestyle='none',color='black',label = 'Alpha Ratio')

            ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0); ax.set_ylabel('Ratio', ha='right', y=1.0)
            ax.set_ylim(-0.5, 1.5)
            ax.text(0.05, 0.92, f'{text}', transform=ax.transAxes, fontweight='bold') 
            ax.legend(loc='upper right')
        outfile['alphatree'] = AlphaBranch


for case_str in ['resolved','merged']:
    