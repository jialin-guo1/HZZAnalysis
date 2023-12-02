import uproot
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward1 as ak
import pandas as pd
import numpy as np
import seaborn as sns
from array import array

import hist

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
with open("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL16_old.yml") as f:
    config = yaml.safe_load(f)

use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
if use_helvet:
    CMShelvet = hep.style.CMS
    CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.style.use(CMShelvet)
else:
    plt.style.use(hep.style.CMS)

#===========================================initial function and variables====================================================================
def reshape(histo,mean,width):
    h = bh.Histogram(bh.axis.Regular(nbins, xmin, xmax))
    h.fill(np.random.normal(loc=mean, scale=width, size=int(histo.view().value.sum())))
    reshape_weight = h.view()/histo.view().value
    np.nan_to_num(reshape_weight,0)
    return reshape_weight

branchs = ['GEN_H1_mass','EventWeight','foundZ1LCandidate','foundTTCRCandidate','foundZ2JCandidate','foundZ2MergedCandidata','foundTTCRCandidate','passedfullmerged','passedfullresolved','particleNetZvsQCD','passedNassociated',
                        'massmerged','ptmerged','mass2jet',
                        'mass2l2jet', 'mass2lj',]
#samples = ['ggh125','ggh300','ggh350','ggh400','ggh450','ggh500','ggh550','ggh600','ggh700','ggh800','ggh900','ggh1000','ggh1500','ggh2500','ggh3000']
samples = ['ggh']; sam = 'ggh'
#samples = ['vbf'] ; sam = 'vbf'
#samples = ['sig'] ; sam = 'sig'

year = '2018'

#massList = [125,300,350,400,450,500,550,600,700,800,900,1000,1500,2500,3000]
massList = []
for mass in range(500,1000,50):
    massList.append(mass)
for mass in range(1000,1600,100):
    massList.append(mass)
for mass in range(1600,3200,200):
    massList.append(mass)
# Set plot color
color_order = sns.color_palette('Accent', len(massList))
set_sns_color(color_order)
####
#sig_arr, sumWeight = extractSpecialBranch(config,year,samples,branchs)
branchs = config['var_read_lists'].append('GEN_H1_mass')
sig_arr, sumWeight = extractSpecialBranch(config,year,samples,branchs)

region = "SR"
tags = ['btag','untag','vbftag','all']
#channels = ['isEE','isMuMu','2lep']
channels = ['isEE','isMuMu','2lep']
cases = ['merged','resolved']
if(sam=='ggh'):
    pro_str = 'spin0_ggH'
elif(sam=='vbf'):
    pro_str = 'spin0_VBF'
chanName = {'isEE':'eeqq','isMuMu':'mumuqq','2lep':'llqq'}
caseName = {'merged':"Merged",'resolved':"Resolved"}
tagName = {'btag':'b-tagged','untag':'untagged','vbftag':'vbf-tagged'}

#===========================================GEN Raw mass Higgs====================================================================
####Get Gen leval histograms
sig_hist_gen = {}
sig_hist = []
sig_gen_hist_raw = {}
nbins, xmin, xmax = 400,0,4000
edge = np.linspace(xmin, xmax, nbins+1)
with uproot.recreate(f"Histos_MakeShape_{sam}_{year}_Oct10.root") as fout:
    for i,sample in enumerate(samples):
        print(sample)
        #temp_arr = sig_arr[sample]
        weights = np.ones_like(sig_arr[sample]['GEN_H1_mass'])
        #temp_h = hist.Hist(hist.axis.Regular(nbins,xmin,xmax),name = 'GEN_H1_mass').fill(sig_arr[sample]['GEN_H1_mass'],weight =  weights)
        #sig_hist.append(
        #    hist.Hist(hist.axis.Regular(nbins,xmin,xmax),name = 'GEN_H1_mass').fill(sig_arr[sample]['GEN_H1_mass'],weight =  weights)
        #)
        sig_hist.append(get_hist(sig_arr[sample]['GEN_H1_mass'],weights,nbins,xmin,xmax))
        sig_hist_gen[sample] = get_hist(sig_arr[sample]['GEN_H1_mass'],weights,nbins,xmin,xmax)

        #sig_hist_gen[sample] = hist.Hist(hist.axis.Regular(nbins,xmin,xmax),name = 'GEN_H1_mass').fill(sig_arr[sample]['GEN_H1_mass'],weight =  weights)

        #reshape
        #re_weight = reshape(sig_hist_gen[sample],massList[i],width)
        #sig_hist_gen[sample].view().value = (sig_hist_gen[sample].view().value)*re_weight
        
        fout[sample] = sig_hist_gen[sample]
    ###plot Gen Higgs mass
    f = plt.figure(figsize=(12,12))
    ax = f.add_subplot()
    hep.cms.label(data=True, llabel='Preliminary',year=year,rlabel=r'%s $fb^{-1}$ (13 TeV)'%config['lumi'][year], fontname='sans-serif')
    ax.set_xlim(xmin, xmax); ax.set_xticklabels([]); ax.set_ylabel('Events / bin', ha='right', y=1.0)
    ax.set_xlabel(r'M(2l2q) GeV', ha='right', x=1.0)
    #plot_hist(sig_hist,label=[ var for var in samples])
    hep.histplot(sig_hist,label=[ var for var in samples])
    plt.legend()
    plt.savefig(f'GenH_{sam}_{year}.png')
    print('[INFO] DONE')
    plt.close()
    #===========================================reco mass Higgs====================================================================
    sig_arr_cut = {}; sig_hist_cut = {}
    for channel in channels:
        sig_arr_cut[channel] = {}; sig_hist_cut[channel]={}
        for case in cases:
            if case=='merged':
                massZZ = 'mass2lj'
            elif case=='resolved':
                massZZ = 'mass2l2jet'
            sig_arr_cut[channel][case] = {}; sig_hist_cut[channel][case] = {}# eff[channel][case] = {}; eff_GraphY[channel][case] = {}; eff_graph[channel][case]={}
            for tag in tags:
                sig_arr_cut[channel][case][tag] = {}; sig_hist_cut[channel][case][tag] = []# eff[channel][case][tag] = {}; eff_GraphY[channel][case][tag] = array('f',[]); eff_graph[channel][case][tag]=None
                selection = config['cut'][region][channel][case][tag]
                print(f"[INFO] cut selection = {selection}")
                for i,mass in enumerate(massList):
                    #sig_hist_dir[sam] = restored_sig_hist
                    sample = f'{sam}{mass}'
                    #print(f'[INFO] This is {channel} {case} {tag} in {sample}')
                    #selection = config['cut'][region][channel][case][tag]
                    cut_array = ak.numexpr.evaluate(selection,sig_arr[sam])
                    sig_arr_cut[channel][case][tag][sample] = sig_arr[sam][cut_array]
                    weights = (sig_arr_cut[channel][case][tag][sample]['EventWeight']*config['lumi'][year]*config['samples_inf']['ggh'][1]*1000)/sumWeight[sam]
                    temp_hist = get_hist(sig_arr_cut[channel][case][tag][sample][massZZ],weights,nbins,xmin,xmax)
                    sig_hist_cut[channel][case][tag].append(temp_hist)
                    ######calculate eff
                    temp_hist_unweight = get_hist(sig_arr_cut[channel][case][tag][sample][massZZ],ak.ones_like(sig_arr_cut[channel][case][tag][sample]['EventWeight']),nbins,xmin,xmax)
                    #temp_hist_unweight = hist.Hist(hist.axis.Regular(nbins,xmin,xmax),name = f'{channel}_{case}_{tag}_{sample}_massZZ').fill(sig_arr_cut[channel][case][tag][sample][massZZ],weight =  ak.ones_like(sig_arr_cut[channel][case][tag][sample]['EventWeight']))
                    #print(temp_hist_unweight.view())
                    #print(f'[INFO] sum of events after applying selections in {channel} {case} {tag} {sample} = {temp_hist_unweight.view().value.sum()}')
                    #print(f'[INFO] sum of events after applying selections and weight in {channel} {case} {tag} {sample} = {temp_hist.view().value.sum()}')
                    #print(f'[INFO] sum of events in GEN level in {sample} = {sig_hist_dir[sample].view().value.sum()}')
                    if(massList[i]>0): #reshape if mass lager than 700
                        width = massList[i]*0.03
                        re_weight = reshape(sig_hist[0],mass,width) #sig_hist = GEN_sig_hist_withoutCut
                        temp_hist_unweight.view().value = (temp_hist_unweight.view().value)*re_weight
                        #print(f'reshape weight = {re_weight}')
                        #temp_hist_unweight.view() = temp_hist_unweight.view().
                        #temp_hist_reweight = hist.Hist(hist.axis.Regular(nbins,xmin,xmax),name = f'{channel}_{case}_{tag}_{sample}_massZZ').fill(sig_arr_cut[channel][case][tag][sample][massZZ],weight = re_weight)
                        #*re_weight
                        #print(f'after rewight = {temp_hist_reweight.view()}')
                        #= temp_hist_unweight.view()*re_weight #reconstruction level cutted reshaped histo
                        #reshape gen hist
                        #temp_gen_hist_unweight = sig_gen_hist_raw[mass]
                        #temp_gen_hist_unweight.view().value = (temp_gen_hist_unweight.view().value)*re_weight
                        fout[f'reshape_{channel}_{case}_{tag}_{massList[i]}'] = temp_hist_unweight

