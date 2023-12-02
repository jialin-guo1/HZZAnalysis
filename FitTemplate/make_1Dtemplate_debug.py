import uproot
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward1 as ak
import pandas as pd
import numpy as np
import seaborn as sns
import hist as hist2

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2018', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-c","--cat",dest="cat",default='resolved', help="choose cat to decide wichle cut selection will be used. Options: resolved,merged")
parser.add_argument('-log',"--loggerlevel",dest="loggerlevel",default='INFO', help="set logger level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL")
args = parser.parse_args()
#===========================================load config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *

#===========================================setup parameters====================================================================

logger.setLevel(logging.DEBUG)

file_PNsf_signal = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/NetSF_signal_2016Legacy.yml'
file_param_config = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL16_old.yml'
logger.info(f'use file_param_config = {file_param_config}')
outfilepath = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/ttoutfile"

signal_store_lists = ['ggh1000','vbf1000','sig'] # stroe the signal name in the root file

import yaml
sf_particleNet_signal = {}
with open(file_PNsf_signal) as f:
    sf_particleNet_signal = yaml.safe_load(f)
config = {}
with open(file_param_config) as f:
    config = yaml.safe_load(f)

#massZZ_bins = np.linspace(0,4000,81)
#setup bins content
bins = 80; minbin = 0; maxbin = 4000

regions = ['CR','SR']
#tags = ['btag','untag','vbftag']
tags = ['untag']
#cats = ['isEE','isMuMu','2lep']
cats = ['2lep']
pro_str = 'perInvFb_Bin50GeV'
#reg = 'SR'
#print(f'massZZ bins = {massZZ_bins}')

if(args.cat=='resolved'):
    massZZ='mass2l2jet'; kd = 'KD_Zjj'; case= 'resolved'; str_alpha = 'resolved'
elif(args.cat=='merged'):
    massZZ='mass2lj'; kd = 'KD_ZJ'; case='merged'; str_alpha = 'merged_tag'

#For 2016preAPV and 2016postAPV, use 2016 Alpha file
if args.year=='2016preAPV' or args.year=='2016postAPV':
    Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaHistoFromROOTProduction_2016.root'
    Alpha_file = uproot.open(Alph_path)
else:
    Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaHistoFromROOTProduction_{args.year}.root'
    Alpha_file = uproot.open(Alph_path)
        
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
signal_array = extract_cuted_signal_branch(config,args.year,args.cat)

#verfy whether the bkg_array, signal_array and data_array are empty
logger.debug(f'legnth of  signal_array = {len(signal_array)}')
logger.debug(f'keys of signal_array = {signal_array.keys()}')

##==================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================

#nbins, xmin, xmax = config['bininfo'][kd][0], config['bininfo'][kd][1], config['bininfo'][kd][2]
for cat in cats:
    if cat=='isMuMu':
        file_channel = '2mu'
    elif cat=='isEE':
        file_channel = '2e'
    else:
        file_channel = '2l'
    
    #create histogram for each background each region and category
    histo = {}
    with uproot.recreate(f'Files/Template1D_spin0_{file_channel}_{args.cat}_{args.year}_debug.root') as outfile:
        for reg in regions:
            if reg=='SR':
                region = 'SR'
            else:
                region = 'SB'
            
            histo[reg] = {}
            for tag in tags:
                if tag =='untag':
                    tag_str = '_'
                elif tag=='btag':
                    tag_str = 'btag_'
                elif tag=='vbftag':
                    tag_str = 'vbf_'

                histo[reg][tag] = {}
                #store signal template in root file
                for sam in signal_store_lists:
                    logger.info(f"Processing {sam} {cat} {region} {tag}")
                    histo[reg][tag][sam] = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())
                    temp_array = signal_array[reg][cat][tag][sam]
                    weights = (temp_array['EventWeight']*config['lumi'][args.year]*temp_array['CrossSectionWeight'])
                    logger.debug(f"CrossSectionWeight = {temp_array['CrossSectionWeight']}")
                    if args.cat == 'merged':
                        sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)
                    else:
                        sf_Net = ak.ones_like(temp_array['EventWeight'])
                    #sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)
                    weights = weights*sf_Net
                    logger.debug(f"SF for {sam} {cat} {region} {tag} = {weights}")
                    logger.debug(f"total weight for {sam} {cat} {region} {tag} = {weights}")

                    histo[reg][tag][sam].fill(temp_array[massZZ],weight = weights)
                    histo[reg][tag][sam].view().value = np.maximum(histo[reg][tag][sam].view().value,0)
                    
                    if histo[reg][tag][sam].view().value.sum()==0:
                        logger.error(f"histogram {sam} {cat} {region} {tag} is empty")

                    outfile[f'hmass_{args.cat}{region}{tag_str}{sam}_{pro_str}'] = histo[reg][tag][sam]

