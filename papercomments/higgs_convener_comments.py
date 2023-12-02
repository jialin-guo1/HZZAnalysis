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

file_path = '/Users/rogerguo/projects/uprootframe/File/'

# set cms plot style
use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
if use_helvet:
    CMShelvet = hep.style.CMS
    CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.style.use(CMShelvet)
else:
    plt.style.use(hep.style.CMS)

#=============Add the DY pT binned sample validation
def loadfiele_getsumweight(file_path,varb):
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
            sumweight += f['Ana/sumWeights'].to_numpy()[0].sum()
            f.close()
    print(sumweight)
    print("load all files")
    arr = uproot.lazy([f"{file_path}/*root:Ana/passedEvents"],filter_name = [f"{varb}"])
    return sumweight,arr

#load files and get sum of weight
sumweight_50,arr_50 = loadfiele_getsumweight("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8",'GEN_Z1_pt')
#sumweight_100,arr_100 = loadfiele_getsumweight("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8",'GEN_Z1_pt')
#sumweight_250,arr_250 = loadfiele_getsumweight("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8",'GEN_Z1_pt')
#sumweight_400,arr_400 = loadfiele_getsumweight("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8",'GEN_Z1_pt')
#sumweight_650,arr_650 = loadfiele_getsumweight("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8",'GEN_Z1_pt')


#create histogram for each sample and fill
h = {}
h['50'] = hist.Hist(hist.axis.Regular(bins=140, start=0, stop=1400))
h['50'].fill(arr_50.GEN_Z1_pt,weight=ak.numexpr.evaluate(f'EventWeight*59.83*1000/{sumWeight}',arr_50))