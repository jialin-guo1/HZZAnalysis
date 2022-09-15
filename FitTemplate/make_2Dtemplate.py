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

##===================================================================================================================================================================
def Conditional_norm_2Dhisto(h,nbins):
    temp_h = h
    for bin in range(0,nbins):
        nevents = temp_h[bin,:].values(flow=False).sum()
        if(nevents==0.0): continue
        #temp_h.view(flow=False).value[bin,:]  = np.nan_to_num(temp_h.view(flow=False).value[bin,:],0.0)
        temp_h.view(flow=False).value[bin,:] = temp_h.view(flow=False).value[bin,:]/nevents
    return temp_h

##==================================================================================================================================================================

##===================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================
massZZ_low_bins = np.linspace(500,1700,25)
#massZZ_high_bins = np.array([2000,3500])
massZZ_high_bins = np.array([2000,4000])
massZZ_bins = bh.axis.Variable(ak.from_numpy(np.append(massZZ_low_bins,massZZ_high_bins)).to_list())
regions = ['CR','SR']
#reg = 'SR'
print(f'massZZ bins = {massZZ_bins}')

if(args.cat=='ak4'):
    massZZ='mass2l2jet'; kd = 'KD_Zjj'; case= 'resolved'
elif(args.cat=='net'):
    massZZ='mass2lj'; kd = 'KD_ZJ'; case='merged'

Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaRaio{args.year}_{case}.root'
Alph_array = uproot.lazy([f"{Alph_path}:alphatree"])

nbins, xmin, xmax = config['bininfo'][kd][0], config['bininfo'][kd][1], config['bininfo'][kd][2]
with uproot.recreate(f'./Files/template_{case}_{args.year}.root') as outfile:
    cat = '2lep'
    bkg_hists = {}; Data_hist = {}; signal_hists = {}
    for reg in regions:
        bkg_hists[reg] = {}; Data_hist[reg] = {}; signal_hists[reg] = {}
        bkg_hists[reg][cat] = [None,None,None]; Data_hist[reg][cat] = None; signal_hists[reg][cat] = {}
        signal_hists[reg][cat] = {'ggh':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
                              'vbf':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
                              'sig':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()) }

        for sample in config['Samples_lists']:
            print(f"This is {sample} in {cat}")
            if sample!='Data':
                if sample.find('DY')!=-1 and reg=="CR": continue
                temp_array = bkg_array[reg][cat][sample]
                #retray weight and apply paritcleNet weight
                weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]

                if (sample == 'ZZTo2Q2L' or sample =='WZTo2Q2L') and args.cat=='net':
                    sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)   
                else:
                    sf_Net = ak.ones_like(temp_array['EventWeight'])
                weights = weights*sf_Net


                #temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                temp_hist = bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight())
                temp_hist.fill(temp_array[massZZ],temp_array[kd],weight = weights)
                
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
                    #print(f"this is ZV in {reg} with {cat} = ", (bkg_hists[reg][cat])[0].view(flow=False).value)
                    #print(f'massZZ  = {massZZ}, KD = {kd}')
            else:
                temp_array = data_array[reg][cat]
                weights = np.ones_like(temp_array['EventWeight'])
                print(f'data weight  = {weights}')
                #Data_hist[reg][cat] = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                Data_hist[reg][cat] = bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight())
                Data_hist[reg][cat].fill(temp_array[massZZ],temp_array[kd],weight=weights)
                #Data_hist[reg][cat] = temp_hist

        if(args.year!='2016APV'):
            for sample in config['signal_lists']:
                temp_array = signal_array[reg][cat][sample]
                if args.year=='2016': 
                    weights = (temp_array['EventWeight']*36.33*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                else:
                    weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                if args.cat=='net':
                    sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal) 
                else:
                    sf_Net = ak.ones_like(temp_array['EventWeight'])
                weights = weights*sf_Net

                temp_hist = bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight())
                temp_hist.fill(temp_array[massZZ],temp_array[kd],weight = weights)

                if sample.find('ggh')!=-1:
                    signal_hists[reg][cat]['ggh'] = signal_hists[reg][cat]['ggh']+temp_hist
                elif sample.find('vbf')!=-1:
                    signal_hists[reg][cat]['vbf'] = signal_hists[reg][cat]['vbf']+temp_hist
                elif sample.find('sig')!=-1:
                    signal_hists[reg][cat]['sig'] = signal_hists[reg][cat]['sig']+temp_hist

    reg='SR'
    xbins = massZZ_bins.size
    dir_h = {}
    #signal
    print(f"[INOF] make 2D template in {reg}")
    if(args.year!='2016APV' ):
        print(f"[INOF] this is signal")
        #sig_hist = (signal_hists[reg][cat]['ggh']+signal_hists[reg][cat]['vbf'])
        sig_hist = Conditional_norm_2Dhisto((signal_hists[reg][cat]['sig']),xbins)
        #for x in range(0,xbins):
        #    nevents = sig_hist[x,:].values(flow=False).sum()
        #    sig_hist.view(flow=False).value[x,:] = sig_hist.view(flow=False).value[x,:]/nevents
        #nevents = sig_hist.view(flow=False).value.sum()
        #weight_one = ak.full_like(sig_hist.view(flow=False).value,1/nevents)
        #sig_hist.view(flow=False).value = sig_hist.view(flow=False).value*weight_one


        #outfile[f'sig_{case}'] = (signal_hists[reg][cat]['ggh']+signal_hists[reg][cat]['vbf'])
        #outfile[f'sig_{case}_up'] = (signal_hists[reg][cat]['ggh']+signal_hists[reg][cat]['vbf'])
        #outfile[f'sig_{case}_dn'] = (signal_hists[reg][cat]['ggh']+signal_hists[reg][cat]['vbf'])
        outfile[f'sig_{case}'] = sig_hist
        outfile[f'sig_{case}_up'] = sig_hist
        outfile[f'sig_{case}_dn'] = sig_hist

        dir_h['sig'] = sig_hist
    #TTbar and Diboson
    print(f"[INOF] this is TTbar")
    print((bkg_hists[reg][cat])[1].view(flow=False).value)
    TTbar_hist = Conditional_norm_2Dhisto((bkg_hists[reg][cat])[1],xbins)
    outfile[f'TTbar_{case}']  = TTbar_hist
    outfile[f'TTbar_{case}_up']  = TTbar_hist
    outfile[f'TTbar_{case}_dn']  = TTbar_hist

    dir_h['TTbar'] = TTbar_hist

    print(f"[INOF] this is Diboson")
    print((bkg_hists[reg][cat])[0].view(flow=False).value)
    Diboson_hist = Conditional_norm_2Dhisto((bkg_hists[reg][cat])[0],xbins)
    outfile[f'Diboson_{case}']  = Diboson_hist    
    outfile[f'Diboson_{case}_up']  = Diboson_hist    
    outfile[f'Diboson_{case}_dn']  = Diboson_hist

    dir_h['Diboson'] = Diboson_hist

    #Z+jet
    print(f"[INOF] this is Z+jet")
    #apply Alph ratio
    Data_hist['CR']['2lep'].view(flow=False).value = Data_hist['CR']['2lep'].view(flow=False).value - (bkg_hists['CR']['2lep'])[0].view(flow=False).value- (bkg_hists['CR']['2lep'])[1].view(flow=False).value
    Data_hist['CR']['2lep'].view(flow=False).value[:,0] = Data_hist['CR']['2lep'].view(flow=False).value[:,0]*Alph_array[f'{case}_{cat}']
    #replace KD in data CR by MC SR
    for x in range(0,xbins):
        Data_hist['CR']['2lep'].view(flow=False).value[x,:] = bkg_hists['SR']['2lep'][2].view(flow=False).value[x,:]
    #norm
    print(Data_hist['CR']['2lep'].view(flow=False).value)
    data_hist = Conditional_norm_2Dhisto(Data_hist['CR']['2lep'],xbins)
    

    outfile[f'DY_{case}'] = data_hist
    outfile[f'DY_{case}_up'] = data_hist
    outfile[f'DY_{case}_dn'] = data_hist

    dir_h['DY'] = data_hist

    ##===================================================================PLOT===================================================================
    for key in dir_h.keys():

        fig, ax = plt.subplots(figsize=(12,12))
        if key=='sig' and args.year=='2016':
            hep.cms.label(data=True, llabel='Preliminary',year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%36.33, fontname='sans-serif')
        else:
            hep.cms.label(data=True, llabel='Preliminary',year=args.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%config['lumi'][args.year], fontname='sans-serif')
        #mesh = ax.pcolormesh(*hist2D['ggh'].axes.edges.T, density.T)
        hep.hist2dplot(dir_h[key])
        ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
        ax.set_ylabel('A.U', ha='right', y=1.0)
        #fig.colorbar(mesh)
        plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{args.cat}/{args.year}/template_2D_{key}.png')
        plt.close()
