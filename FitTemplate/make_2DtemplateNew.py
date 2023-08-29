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
#=================================================================================================================================================================================================
#=================================================================================================================================================================================================
#=================================================================================================================================================================================================
#bkg_array,signal_array,data_array,sumWeight = extractCutedBranch(config,args.year,args.cat)
invarbs = ['mass2l2jet'] if args.cat == 'resolved' else ['mass2lj']
hist = GetHisto(args.year,args.cat,invarb=invarbs).hist
#hist = GetHisto(args.year,args.cat).hist
#logger.debug(f'keys in hist = {hist[args.cat].keys()}')
logger.info(f'Get Hist done')

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
##==================================================================================================================================================================

##===================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================
#massZZ_low_bins = np.linspace(500,1700,25)
##massZZ_high_bins = np.array([2000,3500])
#massZZ_high_bins = np.array([2000,4000])
#massZZ_bins = bh.axis.Variable(ak.from_numpy(np.append(setting().massZZ_low_bins,setting().massZZ_high_bins)).to_list())
massZZ_bins = setting().massZZ_bins['resolved' if args.cat =='resolved' else 'merged']
#massZZ_bins = setting().massZZ_bins()
regions = ['CR','SR']
#reg = 'SR'
print(f'massZZ bins = {massZZ_bins}')

if(args.cat=='resolved'):
    massZZ='mass2l2jet'; kd = 'KD_Zjj'; case= 'resolved'; casename = 'resolved'
elif(args.cat=='merged_tag'):
    massZZ='mass2lj'; kd = 'KD_ZJ'; case='merged'; casename = 'merged_tag'
extra_str = 'rebin_2d'

#Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaRaio{args.year}_{case}.root'
#Alph_array = uproot.lazy([f"{Alph_path}:alphatree"])

Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaHistoFromROOTProduction_{args.year}.root'
Alpha_file = uproot.open(Alph_path)

nbins, xmin, xmax = config['bininfo'][kd][0], config['bininfo'][kd][1], config['bininfo'][kd][2]
#with uproot.recreate(f'./Files/template_{case}_{args.year}.root') as outfile:
with uproot.recreate(f'./template_{case}_{args.year}.root') as outfile:
    cat = '2lep'
    bkg_hists = {}; Data_hist = {}; signal_hists = {}
    for reg in regions:
        bkg_hists[reg] = {}; Data_hist[reg] = {}; signal_hists[reg] = {}
        Data_hist[reg][cat] = {}
        bkg_hists[reg][cat]={}; bkg_hists[reg][cat]['mean'] = [None,None,None];   bkg_hists[reg][cat]['up'] = [None,None,None];  bkg_hists[reg][cat]['dn'] = [None,None,None]
        signal_hists[reg][cat] = {}
        #signal_hists[reg][cat]['mean'] = {'ggh':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
        #                      'vbf':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
        #                      'sig':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()) }
        #signal_hists[reg][cat]['up'] = {'ggh':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
        #                      'vbf':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
        #                      'sig':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()) }
        #signal_hists[reg][cat]['dn'] = {'ggh':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
        #                      'vbf':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()),
        #                      'sig':bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight()) }
        signal_hists[reg][cat]['mean'] = {}
        signal_hists[reg][cat]['up'] = {}
        signal_hists[reg][cat]['dn'] = {}

        ##DY
        (bkg_hists[reg][cat]['mean'])[2] = hist[args.cat][f'DY_pt50To100_{reg}_{cat}_all_{massZZ}_{extra_str}']+hist[args.cat][f'DY_pt100To250_{reg}_{cat}_all_{massZZ}_{extra_str}'] \
                                    +hist[args.cat][f'DY_pt250To400_{reg}_{cat}_all_{massZZ}_{extra_str}']+hist[args.cat][f'DY_pt400To650_{reg}_{cat}_all_{massZZ}_{extra_str}']+hist[args.cat][f'DY_pt650ToInf_{reg}_{cat}_all_{massZZ}_{extra_str}']
        (bkg_hists[reg][cat]['up'])[2] = hist[args.cat][f'DY_pt50To100_{reg}_{cat}_all_{massZZ}_up_{extra_str}']+hist[args.cat][f'DY_pt100To250_{reg}_{cat}_all_{massZZ}_up_{extra_str}'] \
                                        +hist[args.cat][f'DY_pt250To400_{reg}_{cat}_all_{massZZ}_up_{extra_str}']+hist[args.cat][f'DY_pt400To650_{reg}_{cat}_all_{massZZ}_up_{extra_str}']+hist[args.cat][f'DY_pt650ToInf_{reg}_{cat}_all_{massZZ}_up_{extra_str}']
        (bkg_hists[reg][cat]['dn'])[2] = hist[args.cat][f'DY_pt50To100_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']+hist[args.cat][f'DY_pt100To250_{reg}_{cat}_all_{massZZ}_dn_{extra_str}'] \
                                        +hist[args.cat][f'DY_pt250To400_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']+hist[args.cat][f'DY_pt400To650_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']+hist[args.cat][f'DY_pt650ToInf_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']    

        ##TT,WW
        #(bkg_hists[reg][cat]['mean'])[1] = hist[args.cat][f'TTTo2L2Nu_{reg}_{cat}_all_{massZZ}_{extra_str}']+hist[args.cat][f'WWTo2L2Nu_{reg}_{cat}_all_{massZZ}_{extra_str}']
        #(bkg_hists[reg][cat]['up'])[1] = hist[args.cat][f'TTTo2L2Nu_{reg}_{cat}_all_{massZZ}_up_{extra_str}']+hist[args.cat][f'WWTo2L2Nu_{reg}_{cat}_all_{massZZ}_up_{extra_str}']
        #(bkg_hists[reg][cat]['dn'])[1] = hist[args.cat][f'TTTo2L2Nu_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']+hist[args.cat][f'WWTo2L2Nu_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']
        (bkg_hists[reg][cat]['mean'])[1] = hist[args.cat][f'TTTo2L2Nu_{reg}_{cat}_all_{massZZ}_{extra_str}']+hist[args.cat][f'tZq_{reg}_{cat}_all_{massZZ}_{extra_str}']
        (bkg_hists[reg][cat]['up'])[1] = hist[args.cat][f'TTTo2L2Nu_{reg}_{cat}_all_{massZZ}_up_{extra_str}']+hist[args.cat][f'tZq_{reg}_{cat}_all_{massZZ}_up_{extra_str}']
        (bkg_hists[reg][cat]['dn'])[1] = hist[args.cat][f'TTTo2L2Nu_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']+hist[args.cat][f'tZq_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']

        ##ZV
        (bkg_hists[reg][cat]['mean'])[0] = hist[args.cat][f'WZTo2Q2L_{reg}_{cat}_all_{massZZ}_{extra_str}']+hist[args.cat][f'ZZTo2Q2L_{reg}_{cat}_all_{massZZ}_{extra_str}']+hist[args.cat][f'WWTo2L2Nu_{reg}_{cat}_all_{massZZ}_{extra_str}']
        (bkg_hists[reg][cat]['up'])[0] = hist[args.cat][f'WZTo2Q2L_{reg}_{cat}_all_{massZZ}_up_{extra_str}']+hist[args.cat][f'ZZTo2Q2L_{reg}_{cat}_all_{massZZ}_up_{extra_str}']+hist[args.cat][f'WWTo2L2Nu_{reg}_{cat}_all_{massZZ}_up_{extra_str}']
        (bkg_hists[reg][cat]['dn'])[0] = hist[args.cat][f'WZTo2Q2L_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']+hist[args.cat][f'ZZTo2Q2L_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']+hist[args.cat][f'WWTo2L2Nu_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']

        ##sig
        signal_hists[reg][cat]['mean']['sig'] = hist[args.cat][f'sig_{reg}_{cat}_all_{massZZ}_{extra_str}']
        signal_hists[reg][cat]['up']['sig'] = hist[args.cat][f'sig_{reg}_{cat}_all_{massZZ}_up_{extra_str}']
        signal_hists[reg][cat]['dn']['sig'] = hist[args.cat][f'sig_{reg}_{cat}_all_{massZZ}_dn_{extra_str}']


        ##data
        Data_hist[reg][cat]['mean']  = hist[args.cat][f'Data_{reg}_{cat}_all_{massZZ}_{extra_str}']
        Data_hist[reg][cat]['up']  = hist[args.cat][f'Data_{reg}_{cat}_all_{massZZ}_{extra_str}']
        Data_hist[reg][cat]['dn']  = hist[args.cat][f'Data_{reg}_{cat}_all_{massZZ}_{extra_str}']

        #if(args.year!='2016APV'):
        #    for sample in config['signal_lists']:
        #        #temp_array = signal_array[reg][cat][sample]
        #        #if args.year=='2016': 
        #        #    weights = (temp_array['EventWeight']*36.33*1000*config['samples_inf'][sample][1])/sumWeight[sample]
        #        #else:
        #        #    weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]
        #        #if args.cat=='net':
        #        #    sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal) 
        #        #else:
        #        #    sf_Net = ak.ones_like(temp_array['EventWeight'])
        #        #weights = weights*sf_Net
#
        #        temp_hist = bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight())
        #        temp_hist.fill(temp_array[massZZ],temp_array[kd],weight = weights)
#
        #        temp_hist_up = bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight())
        #        temp_hist_up.fill(temp_array[f'{massZZ}_up'],temp_array[f'{kd}_up'],weight = weights)
#
        #        temp_hist_dn = bh.Histogram(massZZ_bins,bh.axis.Regular(50, 0, 1),storage=bh.storage.Weight())
        #        temp_hist_dn.fill(temp_array[f'{massZZ}_dn'],temp_array[f'{kd}_dn'],weight = weights)
#
        #        if sample.find('ggh')!=-1:
        #            signal_hists[reg][cat]['mean']['ggh'] = signal_hists[reg][cat]['ggh']+temp_hist
        #            signal_hists[reg][cat]['up']['ggh'] = signal_hists[reg][cat]['ggh']+temp_hist_up
        #            signal_hists[reg][cat]['dn']['ggh'] = signal_hists[reg][cat]['ggh']+temp_hist_dn
        #        elif sample.find('vbf')!=-1:
        #            signal_hists[reg][cat]['mean']['vbf'] = signal_hists[reg][cat]['vbf']+temp_hist
        #            signal_hists[reg][cat]['up']['vbf'] = signal_hists[reg][cat]['vbf']+temp_hist_up
        #            signal_hists[reg][cat]['dn']['vbf'] = signal_hists[reg][cat]['vbf']+temp_hist_dn
        #        elif sample.find('sig')!=-1:
        #            signal_hists[reg][cat]['mean']['sig'] = signal_hists[reg][cat]['sig']+temp_hist
        #            signal_hists[reg][cat]['up']['sig'] = signal_hists[reg][cat]['sig']+temp_hist_up
        #            signal_hists[reg][cat]['dn']['sig'] = signal_hists[reg][cat]['sig']+temp_hist_dn

    reg='SR'
    xbins = massZZ_bins.size
    dir_h = {}
    #signal
    print(f"[INOF] make 2D template in {reg}")
    if(args.year!='2016APV' ):
        print(f"[INOF] this is signal")
        #sig_hist = (signal_hists[reg][cat]['ggh']+signal_hists[reg][cat]['vbf'])
        sig_hist = Conditional_norm_2Dhisto((signal_hists[reg][cat]['mean']['sig']),xbins)
        sig_hist_up = Conditional_norm_2Dhisto((signal_hists[reg][cat]['up']['sig']),xbins)
        sig_hist_dn = Conditional_norm_2Dhisto((signal_hists[reg][cat]['dn']['sig']),xbins)
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
        outfile[f'sig_{case}_up'] = sig_hist_up
        outfile[f'sig_{case}_dn'] = sig_hist_up

        dir_h['sig'] = sig_hist
    #TTbar and Diboson
    print(f"[INOF] this is TTbar")
    print((bkg_hists[reg][cat]['mean'])[1].view(flow=False).value)
    TTbar_hist = Conditional_norm_2Dhisto((bkg_hists[reg][cat]['mean'])[1],xbins)
    TTbar_hist_up = Conditional_norm_2Dhisto((bkg_hists[reg][cat]['up'])[1],xbins)
    TTbar_hist_up = Conditional_norm_2Dhisto((bkg_hists[reg][cat]['dn'])[1],xbins)
    outfile[f'TTbar_{case}']  = TTbar_hist
    outfile[f'TTbar_{case}_up']  = TTbar_hist_up
    outfile[f'TTbar_{case}_dn']  = TTbar_hist_up

    dir_h['TTbar'] = TTbar_hist

    print(f"[INOF] this is Diboson")
    print((bkg_hists[reg][cat]['mean'])[0].view(flow=False).value)
    Diboson_hist = Conditional_norm_2Dhisto((bkg_hists[reg][cat]['mean'])[0],xbins)
    Diboson_hist_up = Conditional_norm_2Dhisto((bkg_hists[reg][cat]['up'])[0],xbins)
    Diboson_hist_dn = Conditional_norm_2Dhisto((bkg_hists[reg][cat]['dn'])[0],xbins)
    outfile[f'Diboson_{case}']  = Diboson_hist    
    outfile[f'Diboson_{case}_up']  = Diboson_hist_up  
    outfile[f'Diboson_{case}_dn']  = Diboson_hist_dn

    dir_h['Diboson'] = Diboson_hist

    #Z+jet
    print(f"[INOF] this is Z+jet")
    #apply Alph ratio
    Alph_hist = Alpha_file[f'{casename}_{cat}_all'].to_hist()
    Alpha_array = Alph_hist.values()
    Data_hist['CR']['2lep']['mean'].view(flow=False).value = Data_hist['CR']['2lep']['mean'].view(flow=False).value - (bkg_hists['CR']['2lep']['mean'])[0].view(flow=False).value- (bkg_hists['CR']['2lep']['mean'])[1].view(flow=False).value
    Data_hist['CR']['2lep']['mean'].view(flow=False).value[:,0] = Data_hist['CR']['2lep']['mean'].view(flow=False).value[:,0]*Alpha_array

    Data_hist['CR']['2lep']['up'].view(flow=False).value = Data_hist['CR']['2lep']['up'].view(flow=False).value - (bkg_hists['CR']['2lep']['up'])[0].view(flow=False).value- (bkg_hists['CR']['2lep']['up'])[1].view(flow=False).value
    Data_hist['CR']['2lep']['up'].view(flow=False).value[:,0] = Data_hist['CR']['2lep']['up'].view(flow=False).value[:,0]*Alpha_array
    
    Data_hist['CR']['2lep']['dn'].view(flow=False).value = Data_hist['CR']['2lep']['dn'].view(flow=False).value - (bkg_hists['CR']['2lep']['dn'])[0].view(flow=False).value- (bkg_hists['CR']['2lep']['dn'])[1].view(flow=False).value
    Data_hist['CR']['2lep']['dn'].view(flow=False).value[:,0] = Data_hist['CR']['2lep']['dn'].view(flow=False).value[:,0]*Alpha_array
    #replace KD in data CR by MC SR
    for x in range(0,xbins):
        Data_hist['CR']['2lep']['mean'].view(flow=False).value[x,:] = bkg_hists['SR']['2lep']['mean'][2].view(flow=False).value[x,:]
        Data_hist['CR']['2lep']['up'].view(flow=False).value[x,:] = bkg_hists['SR']['2lep']['up'][2].view(flow=False).value[x,:]
        Data_hist['CR']['2lep']['dn'].view(flow=False).value[x,:] = bkg_hists['SR']['2lep']['dn'][2].view(flow=False).value[x,:]
    #norm
    print(Data_hist['CR']['2lep']['mean'].view(flow=False).value)
    data_hist = Conditional_norm_2Dhisto(Data_hist['CR']['2lep']['mean'],xbins)
    data_hist_up = Conditional_norm_2Dhisto(Data_hist['CR']['2lep']['up'],xbins)
    data_hist_dn = Conditional_norm_2Dhisto(Data_hist['CR']['2lep']['dn'],xbins)
    

    outfile[f'DY_{case}'] = data_hist
    outfile[f'DY_{case}_up'] = data_hist_up
    outfile[f'DY_{case}_dn'] = data_hist_dn

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
        plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plotnew/{args.cat}/{args.year}/template_2D_{key}.png')
        plt.close()

