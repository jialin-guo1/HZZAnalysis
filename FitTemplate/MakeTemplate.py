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
parser.add_argument("-c","--cat",dest="cat",default='tt', help="choose cat to decide wichle cut selection will be used. Options: resolved,merged")
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
with open("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL16_old.yml") as f:
    config = yaml.safe_load(f)

outfilepath = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/ttoutfile"
class Make1Dtemplate():
    def __init__(self,year,cat):
        self.year = year
        self.cat = cat

        self.sf_particleNet_signal = {}
        with open('/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/NetSF_signal_2016Legacy.yml') as f:
            self.sf_particleNet_signal = yaml.safe_load(f)
        
        self.config = {}
        with open("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL16_old.yml") as f:
            self.config = yaml.safe_load(f)

        self.bins = 80
        self.minbin = 0
        self.maxbin = 4000
        

        

        
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
bkg_array,signal_array,data_array,sumWeight = extractCutedCatBranch(config,args.year,args.cat)

##==================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================
#massZZ_bins = np.linspace(0,4000,81)
bins = 80; minbin = 0; maxbin = 4000
regions = ['CR','SR']
tags = ['btag','untag','vbftag']
#tags = ['vbftag']
cats = ['isEE','isMuMu','2lep']
#cats = ['isEE']
pro_str = 'perInvFb_Bin50GeV'
#reg = 'SR'
print(f'massZZ bins = {massZZ_bins}')

if(args.cat=='resolved'):
    massZZ='mass2l2jet'; kd = 'KD_Zjj'; case= 'resolved'
elif(args.cat=='merged'):
    massZZ='mass2lj'; kd = 'KD_ZJ'; case='merged'

#Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaRaioVaildation_{case}.root'
#Alph_array = uproot.lazy([f"{Alph_path}:alphatree"])

#nbins, xmin, xmax = config['bininfo'][kd][0], config['bininfo'][kd][1], config['bininfo'][kd][2]
for cat in cats:
    if cat=='isMuMu':
        file_channel = '2mu'
    elif cat=='isEE':
        file_channel = '2e'
    else:
        file_channel = '2l'
    with uproot.recreate(f'Files/Template1D_spin0_{file_channel}_{args.cat}_{args.year}.root') as outfile:
        #bkg_hists = {}; Data_hist = {}; signal_hists = {}
        for reg in regions:
            if reg=='SR':
                region = 'SR'
            else:
                region = 'SB'
            #bkg_hists[reg] = {}; Data_hist[reg] = {}; signal_hists[reg] = {}
            #bkg_hists[reg][cat] = [None,None,None]; Data_hist[reg][cat] = None; signal_hists[reg][cat] = {}
            for tag in tags:
                if tag =='untag':
                    tag_str = '_'
                elif tag=='btag':
                    tag_str = 'btag_'
                elif tag=='vbftag':
                    tag_str = 'vbf_'
                #bkg_hists[reg][cat][tag] = [None,None,None]; Data_hist[reg][cat][tag] = None; signal_hists[reg][cat][tag] = {}
                histo = {}
                for sam in ['TTplusWW','VZ',]:
                    #histo[sam] = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                    histo[sam] = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())
                for sample in config['Samples_lists']:
                    print(f"This is {sample} {cat} {region} {tag}")
                    if sample!='Data':
                        if sample.find('DY')!=-1 and reg=="CR": continue
                        temp_array = bkg_array[reg][cat][tag][sample]
                        #retray weight and apply paritcleNet weight
                        weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                        if (sample == 'ZZTo2Q2L' or sample =='WZTo2Q2L') and args.cat=='merged':
                            sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)   
                        else:
                            sf_Net = ak.ones_like(temp_array['EventWeight'])
                        weights = weights*sf_Net
                        #temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                        #temp_hist = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                        temp_hist = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())
                        temp_hist.fill(temp_array[massZZ],weight = weights)

                        if sample.find('TTTo2L2Nu')!=-1 or sample.find('WWTo2L2Nu')!=-1:
                            #if (bkg_hists[reg][cat])[1]==None:
                            #    (bkg_hists[reg][cat])[1] = temp_hist
                            #else:
                            #    (bkg_hists[reg][cat])[1]+=temp_hist
                            histo['TTplusWW']+=temp_hist
                        if sample.find('WZTo2Q2L')!=-1 or sample.find('ZZTo2Q2L')!=-1:
                            #if (bkg_hists[reg][cat])[0]==None:
                            #    (bkg_hists[reg][cat])[0] = temp_hist
                            #else:
                            #    (bkg_hists[reg][cat])[0]+=temp_hist
                            histo['VZ']+=temp_hist
                    #else:
                    #    temp_array = data_array[reg][cat]
                    #    weights = np.ones_like(temp_array['EventWeight'])
                    #    print(f'data weight  = {weights}')
                    #    #Data_hist[reg][cat] = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                    #    Data_hist[reg][cat] = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                    #    Data_hist[reg][cat].fill(temp_array[massZZ],weight=weights)
                    #    #Data_hist[reg][cat] = temp_hist
                #if(args.year!='2016APV' and args.year!='2017'):
                #    for sample in config['signal_lists']:
                #        temp_array = signal_array[reg][cat][sample]
                #        if args.year=='2016': 
                #            weights = (temp_array['EventWeight']*36.33*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                #        else:
                #            weights = (temp_array['EventWeight']*config['lumi'][args.year]*config['samples_inf'][sample][1])/sumWeight[sample]
                #        if args.cat=='net':
                #            sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal) 
                #        else:
                #            sf_Net = ak.ones_like(temp_array['EventWeight'])
                #        weights = weights*sf_Net
                #        temp_hist = bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight())
                #        temp_hist.fill(temp_array[massZZ],temp_array[kd],weight = weights)
                #        if sample.find('ggh')!=-1:
                #            signal_hists[reg][cat]['ggh'] = signal_hists[reg][cat]['ggh']+temp_hist
                #        elif sample.find('vbf')!=-1:
                #            signal_hists[reg][cat]['vbf'] = signal_hists[reg][cat]['vbf']+temp_hist
                for sam in ['TTplusWW','VZ',]:
                    histo[sam].view().value = np.maximum(histo[sam].view().value,0)
                    outfile[f'hmass_{args.cat}{region}{tag_str}{sam}_{pro_str}'] = histo[sam]