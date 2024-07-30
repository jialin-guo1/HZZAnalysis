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
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016preAVP, 2016psotAPV, 2017,2018,all")
parser.add_argument("-c","--cat",dest="cat",default='tt', help="choose cat to decide wichle cut selection will be used. Options: resolved,merged")
args = parser.parse_args()
#===========================================load config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from deepjet import DeepJet as dj
from setting import setting

logger.setLevel(logging.DEBUG) # DEBUG, INFO, WARNING, ERROR, CRITICAL. Default is ERROR.

import yaml
sf_particleNet_signal = {}
with open('/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/NetSF_signal_2016Legacy.yml') as f:
    sf_particleNet_signal = yaml.safe_load(f)
config = {}
with open(f"/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL{args.year}.yml") as f:
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
#if year is 2016, combine 2016postAPV and 2016preAPV ntuples together. Otherewise, just use the year ntuples
if args.year=='2016':
    print('[INFO] Combine 2016postAPV and 2016preAPV ntuples together')
    #combine bkg_array
    bkg_array_2016preAPV = extractCutedCatBranch(config,'2016preAPV',args.cat)[0]
    bkg_array_2016postAPV = extractCutedCatBranch(config,'2016postAPV',args.cat)[0]

    #concatenate bkg_array for 2016preAPV and 2016postAPV
    print('[INFO] concatenate bkg_array for 2016preAPV and 2016postAPV')
    bkg_array = ak.concatenate([bkg_array_2016preAPV,bkg_array_2016postAPV],axis=0)

    #access data_array for 2016preAPV and 2016postAPV
    data_array_2016preAPV = extractCutedCatBranch(config,'2016preAPV',args.cat)[2]
    data_array_2016postAPV = extractCutedCatBranch(config,'2016postAPV',args.cat)[2]

    #concatenate data_array for 2016preAPV and 2016postAPV
    print('[INFO] concatenate data_array for 2016preAPV and 2016postAPV')
    data_array = ak.concatenate([data_array_2016preAPV,data_array_2016postAPV],axis=0)

    #access sumWeight for sum of 2016preAPV and 2016postAPV
    sumWeight = extractCutedCatBranch(config,'2016preAPV',args.cat)[3]+extractCutedCatBranch(config,'2016postAPV',args.cat)[3]
    print(f'sumWeight = {sumWeight}')
else:
    bkg_array,signal_array,data_array,sumWeight = extractCutedCatBranch(config,args.year,args.cat)

##==================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================
##===================================================================================================================================================================
#evaluate alpha value by given massZZ histogram as type of boost_histogram from alpha histo and create a new alpha array
def getAlphaArray(alpha_histo,massZZ_histo):
    nbins = massZZ_histo.axes[0].size
    alpha_array = np.zeros(nbins)
    for i in range(nbins):
        massZZ = massZZ_histo.axes[0].centers[i]
        bin = alpha_histo.axes[0].index(int(massZZ))
        alpha_array[i] = alpha_histo[bin].value
        #alpha_array[i] = alpha_histo[int(massZZ)].value
    return alpha_array

#massZZ_bins = np.linspace(0,4000,81)
#setup bins content
bins = 80; minbin = 0; maxbin = 4000

regions = ['CR','SR']
tags = ['btag','untag','vbftag']
#tags = ['vbftag','untag']
cats = ['isEE','isMuMu','2lep']
#cats = ['isEE']
pro_str = 'perInvFb_Bin50GeV'
#reg = 'SR'
#print(f'massZZ bins = {massZZ_bins}')

if(args.cat=='resolved'):
    massZZ='mass2l2jet'; kd = 'KD_Zjj'; case= 'resolved'; str_alpha = 'resolved'
    #bins = setting().massZZ_bins['resolved']
elif(args.cat=='merged'):
    massZZ='mass2lj'; kd = 'KD_ZJ'; case='merged'; str_alpha = 'merged_tag'
    #bins = setting().massZZ_bins['merged']

#For 2016preAPV and 2016postAPV, use 2016 Alpha file
if args.year=='2016preAPV' or args.year=='2016postAPV':
    Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaHistoFromROOT_2016.root'
    Alpha_file = uproot.open(Alph_path)
else:
    Alph_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile/AlphaHistoFromROOT_{args.year}.root'
    Alpha_file = uproot.open(Alph_path)

#for resolved category, open a txt file to store the uncertainty of deepjet SFs
if args.cat=='resolved':
    dj_uncertainty_file = open(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/txtfiles/deepjet_uncertainty_{args.year}.txt','w')

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
    with uproot.recreate(f'Files/Template1D_spin0_{file_channel}_{args.cat}_{args.year}.root') as outfile:
    #with uproot.update(f'Files/Template1D_spin0_{file_channel}_{args.cat}_{args.year}.root') as outfile:
        logger.info(f"outfile = Files/Template1D_spin0_{file_channel}_{args.cat}_{args.year}.root")
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
                for sam in ['TTplusWW','VZ']:
                    histo[reg][tag][sam] = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())
                    #histo[reg][tag][sam] = bh.Histogram(bins,storage=bh.storage.Weight())
                for sample in config['Samples_lists']:
                    print(f"This is {sample} {cat} {region} {tag}")
                    #make histo to store the template ttbar and VZ, skip the DY MC 
                    if sample!='Data':
                        #if sample.find('DY')!=-1 and reg=="CR": continue
                        if sample.find('DY')!=-1: continue
                        temp_array = bkg_array[reg][cat][tag][sample]

                        #define histogram for filling
                        #temp_hist = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())

                        #retray weight and apply paritcleNet weight
                        weights = (temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                        if (sample == 'ZZTo2Q2L' or sample =='WZTo2Q2L') and args.cat=='merged':
                            sf_Net = GetParticleNetSignalSF(temp_array,'ZvsQCD',sf_particleNet_signal)   
                        else:
                            sf_Net = ak.ones_like(temp_array['EventWeight'])
                        weights = weights*sf_Net

                        #Deepjet SFs for btag in resolved category only
                        if args.cat=='resolved':
                            if tag=='btag' or tag == 'untag':
                                logger.info(f'Produce deepjet SFs for sample = {sample}, cat = {args.cat}, tag = {tag}')
                                #dj_helper = dj(args.year,temp_array)
                                #sf_jet1,sf_jet2 = dj_helper.get_deepjet_sf('central')
                                #logger.info(f'sf = {sf_jet1*sf_jet2}')
                                #weights = weights*sf_jet1*sf_jet2

                                #compute uncertainty for deepjet SFs.
                                #sf_jet1_up,sf_jet2_up = dj_helper.get_deepjet_sf('up')
                                #sf_jet1_down,sf_jet2_down = dj_helper.get_deepjet_sf('down')
                                #sf_certral = (sf_jet1+sf_jet2).sum()
                                #sf_up = (sf_jet1_up+sf_jet2_up).sum()
                                #sf_down = (sf_jet1_down+sf_jet2_down).sum()
                                #uncertainty_up = abs(sf_up-sf_certral)/sf_certral
                                #uncertainty_down = abs(sf_down-sf_certral)/sf_certral
                                #dj_uncertainty_file.write(f'{cat} {sample} {reg} {uncertainty_up}/{uncertainty_down}\n')

                                weights = (temp_array['w_deepjet']*temp_array['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]

                                #temp_hist.fill(temp_array[massZZ],weight = weights)
                            #elif tag=='untag':
                            #    #logger.info(f'Produce deepjet SFs for sample = {sample} cat = {args.cat}, tag = {tag}')
                            #    #dj_helper = dj(args.year,temp_array)
                            #    ##new_arr = dj_helper.get_untag_deepjet_array(sample)
                            #    #new_arr = dj_helper.get_untag_deepjet_weight(sample)
                            #    #weights = (new_arr['w_btag']*new_arr['EventWeight']*config['lumi'][args.year]*1000*config['samples_inf'][sample][1])/sumWeight[sample]
                            #    #temp_hist.fill(new_arr[massZZ],weight = weights)
                            #    pass
                            #else: #vbf tag
                            #    temp_hist.fill(temp_array[massZZ],weight = weights)
                        #else:
                            #temp_hist = get_hist(temp_array[var],weights,nbins,xmin,xmax)
                            #temp_hist = bh.Histogram(massZZ_bins,storage=bh.storage.Weight())
                        temp_hist = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())
                        #temp_hist = bh.Histogram(bins,storage=bh.storage.Weight())
                        temp_hist.fill(temp_array[massZZ],weight = weights)

                        if sample.find('TTTo2L2Nu')!=-1 or sample.find('WWTo2L2Nu')!=-1:
                            histo[reg][tag]['TTplusWW']+=temp_hist
                        if sample.find('WZTo2Q2L')!=-1 or sample.find('ZZTo2Q2L')!=-1:
                            histo[reg][tag]['VZ']+=temp_hist

                #stroe the template ttbar and VZ in root file
                for sam in ['TTplusWW','VZ']:
                    histo[reg][tag][sam].view().value = np.maximum(histo[reg][tag][sam].view().value,0)
                    outfile[f'hmass_{args.cat}{region}{tag_str}{sam}_{pro_str}'] = histo[reg][tag][sam]

        #setup the Zjet background histogram in CR and SR region. In CR, Zjet = Data - TT - VZ. In SR, Zjet = (Data - TT - VZ - DY)*alpha
        #Zjet in CR. Setup for each category and tag
        reg = 'CR'
        for tag in tags:
            if tag =='untag':
                tag_str = '_'
            elif tag=='btag':
                tag_str = 'btag_'
            elif tag=='vbftag':
                tag_str = 'vbf_'

            logger.info(f"produce Zjet in {reg} region for {cat} {tag} tag")
            
            #create a histogram to store the Zjet in CR
            hist = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())
            #hist = bh.Histogram(bins,storage=bh.storage.Weight())
            temp_array = data_array[reg][cat][tag]
            weight = ak.ones_like(temp_array['EventWeight'])
            hist.fill(temp_array[massZZ],weight=weight)
            logger.debug(f"massZZ = {temp_array[massZZ]} weight = {weight} reg = {reg} cat = {cat} tag = {tag}")

            #substrct ttbar and VZ from data to get Zjet in CR
            hist.view().value = hist.view().value - histo[reg][tag]['TTplusWW'].view().value - histo[reg][tag]['VZ'].view().value
            logger.debug(f"massZZ = {hist.view().value}  after substrct ttbar and VZ from data to get Zjet in CR")

            #store the Zjet in CR into root file
            hist.view().value = np.maximum(hist.view().value,0)
            outfile[f'hmass_{args.cat}SB{tag_str}Zjet_{pro_str}'] = hist

            #get alpha histogram from alpha file
            temp_alpha = Alpha_file[f'{str_alpha}_{cat}_{tag}'].to_hist()
            #get alpha ratio array according to the massZZ from alpha histogram
            alpha_array = getAlphaArray(temp_alpha,hist)
            logger.debug(f"alpha array = {alpha_array}")

            #apply alpha ratio to get Zjet in SR
            hist.view().value = hist.view().value*alpha_array
            logger.debug(f"massZZ = {hist.view().value} after apply alpha ratio to get Zjet in SR")

            #stroe the Zjet in SR into root file
            hist.view().value = np.maximum(hist.view().value,0)
            outfile[f'hmass_{args.cat}SR{tag_str}Zjet_{pro_str}'] = hist


                    #else:
                    #    #make histo to store the data and produce DY from Data*alpha in Data CR
                    #    if reg=='SR': continue
                    #    temp_array = data_array[reg][cat][tag]
                    #    temp_hist = bh.Histogram(bh.axis.Regular(bins=bins, start=minbin, stop=maxbin),storage=bh.storage.Weight())
                    #    weight = ak.ones_like(temp_array['EventWeight'])
                    #    temp_hist.fill(temp_array[massZZ],weight=weight)
#
                    #    histo['Data'] = temp_hist
                    #    #make DY from data*alpha
                    #    temp_alpha = Alpha_file[f'{args.cat}_{cat}_{tag}'].to_hist()
                    #    #alpha_array = temp_alpha.view().value
#
#
#
                    #    #substrct ttbar and VZ from data
                    #    histo['DY'].view().value = histo['Data'].view().value-histo['TTplusWW'].view().value-histo['VZ'].view().value
                    #    
                    #    #get alpha ratio array according to the massZZ
                    #    alpha_array = getAlphaArray(temp_alpha,histo['DY'])
                    #    
                    #    #apply alpha to data
                    #    histo['DY'].view().value = histo['DY'].view().value*alpha_array


                #for sam in ['TTplusWW','VZ','DY']:
                #    histo[sam].view().value = np.maximum(histo[sam].view().value,0)
                #    outfile[f'hmass_{args.cat}{region}{tag_str}{sam}_{pro_str}'] = histo[sam]