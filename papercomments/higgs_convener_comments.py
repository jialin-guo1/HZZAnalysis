# import packages
import uproot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplhep as hep
import awkward as ak
import os
import sys
import hist

#include comstomized module
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from setting import setting
from logset import *
logger.setLevel(logging.INFO)

def setup_cmsplot():
    # set cms plot style
    use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
    if use_helvet:
        CMShelvet = hep.style.CMS
        CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
        plt.style.use(CMShelvet)
    else:
        plt.style.use(hep.style.CMS)

def setup_config(year):
    import yaml
    config_path = f"/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL{year}.yml"
    with open( config_path) as f:
        config = yaml.safe_load(f)
    return config

#=============Add the DY pT binned sample validation
def loadfiles_getsumweight(file_path,varb=None):
    """
    1.loop over all the files in the file_path and get the sum of the weight
    2.return the sum of the weight and loaded files as array
    """
    sumweight = 0.0
    for file in os.listdir(file_path):
        if file.endswith(".root"):
            f = uproot.open(file_path+"/"+file)
            #= f['Ana/sumWeights'].to_numpy()[0].sum()
            #temp_sumweight = h.sum().value
            sumweight += f['sumWeights'].to_numpy()[0].sum()
            f.close()
    print(sumweight)
    print("load all files")
    arr = uproot.lazy([f"{file_path}/:passedEvents"],filter_name = [f"{varb}"]) if varb is not None else uproot.lazy([f"{file_path}/*root:Ana/passedEvents"])
    return sumweight,arr

def loadfile_getsumweight(file,varb=None):
    """
    1.load the file and get the sum of the weight
    2.return the sum of the weight and loaded file as array
    """
    f = uproot.open(file)
    sumweight = f['sumWeights'].to_numpy()[0].sum()
    f.close()
    arr = uproot.lazy([f"{file}:passedEvents"],filter_name = [f"{varb}"]) if varb is not None else uproot.lazy([f"{file}:passedEvents"])
    return sumweight,arr

def make_cut(selection,arr):
    """
    1.make the cut on the array
    2.return the cut array
    """
    cut = ak.numexpr.evaluate(selection,arr)
    return arr[cut]

def plot_flotting(h_mean,h_up,h_down,sample):
    """
    1.plot the floating histogram
    """
    fig, ax = plt.subplots()
    h_mean.plot1d(label='JES Up')
    h_up.plot1d(label='mean')
    h_down.plot1d(label='JES down')
    
    plt.xlabel('M_{2l2q} [GeV]')
    plt.ylabel('Events')
    plt.legend()
    plt.title(f"{sample}_" + "M_{2l2q} distribution")
    plt.savefig(f"{sample}_flotting_M2l2q_CR.png")




if __name__ == "__main__":
    #set up the plot style
    setup_cmsplot()
    #set up the config
    year = "2018"
    config = setup_config(year)

    #define samples
    samples = ['WWTo2L2Nu','ZZTo2Q2L','WZTo2Q2L','DY_pt50To100','DY_pt100To250','DY_pt250To400','DY_pt400To650','DY_pt650ToInf','ggh']
    #,'TTTo2L2Nu','tZq'

    arr = {}
    sumWeight = {}
    for sample in samples:
        #load files and get sum of weight
        logger.info(f"loading {sample}")
        sumWeight[sample],arr[sample] = loadfile_getsumweight(f"{setting().fileset[year][sample][0]}")


    #get cut criteria
    #selection = config['cut']['SR']['2lep']['resolved']['all']
    selection = config['cut']['CR']['2lep']['resolved']['all']
    logger.info(f"cut criteria: {selection}")

    #make cut for each sample
    arr_cut = {}
    for sample in samples:
        logger.info(f"making cut for {sample}")
        arr_cut[sample] = make_cut(selection,arr[sample])

    
    #create histogram for each sample and fill
    h = {'mean':{},'up':{},'down':{}}
    bins = hist.axis.Regular(bins=70,start= 0 ,stop = 3500)
    for sample in samples:
        h['mean'][sample] = hist.Hist(bins)
        h['up'][sample] = hist.Hist(bins)
        h['down'][sample] = hist.Hist(bins)

        h['mean'][sample].fill(arr_cut[sample].mass2l2jet,weight=ak.numexpr.evaluate(f'EventWeight*59.83*1000/{sumWeight[sample]}',arr_cut[sample]))
        h['up'][sample].fill(arr_cut[sample].mass2l2jet_up,weight=ak.numexpr.evaluate(f'EventWeight*59.83*1000/{sumWeight[sample]}',arr_cut[sample]))
        h['down'][sample].fill(arr_cut[sample].mass2l2jet_dn,weight=ak.numexpr.evaluate(f'EventWeight*59.83*1000/{sumWeight[sample]}',arr_cut[sample]))

    
    #plot the floating histogram
    logger.info(f"plotting floating histogram for zjets")
    h_mean_zjets = h['mean']['DY_pt50To100']+h['mean']['DY_pt100To250']+h['mean']['DY_pt250To400']+h['mean']['DY_pt400To650']+h['mean']['DY_pt650ToInf']
    h_up_zjets = h['up']['DY_pt50To100']+h['up']['DY_pt100To250']+h['up']['DY_pt250To400']+h['up']['DY_pt400To650']+h['up']['DY_pt650ToInf']
    h_down_zjets = h['down']['DY_pt50To100']+h['down']['DY_pt100To250']+h['down']['DY_pt250To400']+h['down']['DY_pt400To650']+h['down']['DY_pt650ToInf']
    plot_flotting(h_mean_zjets,h_up_zjets,h_down_zjets,"zjets")

    #plot the floating histogram
    #logger.info(f"plotting floating histogram for ttbar")
    #h_mean_ttbar = h['mean']['TTTo2L2Nu']+h['mean']['tZq']
    #h_up_ttbar = h['up']['TTTo2L2Nu']+h['up']['tZq']
    #h_down_ttbar = h['down']['TTTo2L2Nu']+h['down']['tZq']
    #plot_flotting(h_mean_ttbar,h_up_ttbar,h_down_ttbar,"ttbar")

    #plot the floating histogram
    logger.info(f"plotting floating histogram for diboson")
    h_mean_diboson = h['mean']['WWTo2L2Nu']+h['mean']['ZZTo2Q2L']+h['mean']['WZTo2Q2L']
    h_up_diboson = h['up']['WWTo2L2Nu']+h['up']['ZZTo2Q2L']+h['up']['WZTo2Q2L']
    h_down_diboson = h['down']['WWTo2L2Nu']+h['down']['ZZTo2Q2L']+h['down']['WZTo2Q2L']
    plot_flotting(h_mean_diboson,h_up_diboson,h_down_diboson,"diboson")

    #plot the floating histogram
    logger.info(f"plotting floating histogram for ggh")
    h_mean_ggh = h['mean']['ggh']
    h_up_ggh = h['up']['ggh']
    h_down_ggh = h['down']['ggh']
    plot_flotting(h_mean_ggh,h_up_ggh,h_down_ggh,"Signal")

    #create histogram for each sample and fill
    #h = {}
    #h['50'] = hist.Hist(hist.axis.Regular(bins=140, start=0, stop=1400))
    #h['50'].fill(arr_50.GEN_Z1_pt,weight=ak.numexpr.evaluate(f'EventWeight*59.83*1000/{sumWeight}',arr_50))