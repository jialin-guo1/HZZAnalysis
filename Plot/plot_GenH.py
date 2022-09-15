import uproot
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward1 as ak
import pandas as pd
import numpy as np
import seaborn as sns

def set_sns_color(*args):
    sns.palplot(sns.color_palette(*args))
    sns.set_palette(*args)

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
samples = ['ggh500','ggh600','ggh700','ggh800','ggh900','ggh1000','ggh1500','ggh2500','ggh3000']
branchs = 'GEN_H1_mass'
year = '2016'
sig_arr, sumWeight = extractSpecialBranch(config,year,samples,branchs)

sig_hist = []
nbins, xmin, xmax = 80,0,4000
edge = np.linspace(xmin, xmax, nbins+1)
for sample in samples:
    print(sample)
    #temp_arr = sig_arr[sample]
    weights = np.ones_like(sig_arr[sample]['GEN_H1_mass'])
    sig_hist.append(get_hist(sig_arr[sample]['GEN_H1_mass'],weights,nbins,xmin,xmax))

color_order = sns.color_palette('Accent', len(samples))
set_sns_color(color_order)

f = plt.figure(figsize=(12,12))
plot_hist(sig_hist,label=[ var for var in samples])
plt.savefig(f'GenH.png')
print('[INFO] DONE')





