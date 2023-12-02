import uproot
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward1 as ak
import pandas as pd
import numpy as np
import seaborn as sns
import hist

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-c","--cat",dest="cat",default='tt', help="choose cat to decide wichle cut selection will be used. Options: resolved,merged_tag")
args = parser.parse_args()
#===========================================load config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

logger.setLevel(logging.DEBUG)

import yaml
sf_particleNet_signal = {}
with open('/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/NetSF_signal_2016Legacy.yml') as f:
    sf_particleNet_signal = yaml.safe_load(f)
config = {}
with open("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL16_old.yml") as f:
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
##===================================================================================================================================================================
def Conditional_norm_2Dhisto(h,nbins):
    temp_h = h
    for bin in range(0,nbins):
        nevents = temp_h[bin,:].values(flow=False).sum()
        if(nevents==0.0): continue
        #temp_h.view(flow=False).value[bin,:]  = np.nan_to_num(temp_h.view(flow=False).value[bin,:],0.0)
        temp_h.view(flow=False).value[bin,:] = temp_h.view(flow=False).value[bin,:]/nevents
    return temp_h

#evaluate alpha value by given massZZ histogram as type of boost_histogram from alpha histo and create a new alpha array
def getAlphaArray(alpha_histo,massZZ_histo):
    nbins = massZZ_histo.axes[0].size
    nbins_alpha = alpha_histo.axes[0].size
    logger.debug(f'nbins for this massZZ histo = {nbins}')
    alpha_array = np.zeros(nbins)
    for i in range(nbins):
        logger.debug(f'i for loop nbins = {i}')
        massZZ = massZZ_histo.axes[0].centers[i]
        logger.debug(f'massZZ = {massZZ}')
        bin = alpha_histo.axes[0].index(int(massZZ))
        #if the range of massZZ is out of alpha histo range, set the bin to the last bin of alpha histo
        if bin>=nbins_alpha:
            bin = nbins_alpha-1
            logger.warning(f'bin is out of alpha histo range, set bin to the last bin of alpha histo. last bin value of alpha histo = {alpha_histo.axes[0].centers[bin]}')
            alpha_array[i] = alpha_histo[bin].value
        else:
            logger.debug(f'bin = {bin}')
            logger.debug(f'alpha_histo.axes[0].centers[bin] = {alpha_histo.axes[0].centers[bin]}')
            logger.debug(f'alpha_histo[bin].value = {alpha_histo[bin].value}')
            alpha_array[i] = alpha_histo[bin].value
        #alpha_array[i] = alpha_histo[int(massZZ)].value
    return alpha_array

##=====================================================================makecut to each sample========================================================================
#samples = ['DY_pt50To100','DY_pt100To250','DY_pt250To400','DY_pt400To650','DY_pt650ToInf','TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L','WWTo1L1Nu2Q','tZq','ZZTo2L2Nu','WZTo1L1Nu2Q','ggh1000','ggh500','sig','ggh2000']
samples = ['DY_pt50To100','DY_pt100To250','DY_pt250To400','DY_pt400To650','DY_pt650ToInf','TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L','tZq','sig']
arr = {}
sumweight = {}
for sample in samples:
    arr[sample] = uproot.lazy([f"{setting().fileset[args.year][sample][0]}:passedEvents"])
    
    f = uproot.open(setting().fileset[args.year][sample][0])['sumWeights']
    sumweight[sample] = (f.to_boost()).sum()
    f.close()


selection = "((mass2jet>70) & (mass2jet<105)) & (foundZ1LCandidate==True) & (foundZ2JCandidate==True)" if args.cat == 'resolved' \
    else "((mass2jet>70) & (mass2jet<105)) & (particleNetZvsQCD>0.9) & (foundZ1LCandidate==True) & (foundZ2MergedCandidata==True)"

arr_cut = {}
for sample in samples:
    cut = ak.numexpr.evaluate(selection,arr[sample])
    arr_cut[sample] = arr[sample][cut]
