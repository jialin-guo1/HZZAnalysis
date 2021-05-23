from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

DY_pt100To250 = ['DYJetsToLL_Pt-100To250_01','DYJetsToLL_Pt-100To250_02','DYJetsToLL_Pt-100To250_03','DYJetsToLL_Pt-100To250_04','DYJetsToLL_Pt-100To250_05']
DY_pt250To400 = ['DYJetsToLL_Pt-250To400_01','DYJetsToLL_Pt-250To400_02','DYJetsToLL_Pt-250To400_03','DYJetsToLL_Pt-250To400_04','DYJetsToLL_Pt-250To400_05']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
signal = ['GluGluHToZZTo2L2Q_M1000','GluGluHToZZTo2L2Q_M1500']
otherBKG = ['WZ','ZZ_TuneCP5','TTJets']
samples = otherBKG+DY_pt100To250+DY_pt250To400+DY_pt_400ToInf+signal
var_names = ['SDmass_SR','Hmass']
#var_names = ['Z1_pt']
PH = plotHelper(samples,2018)

files={}
for sample in samples:
    files[sample] = TFile("../RawHistos/%s_allCut_test.root"%sample)

#book ROOT file storing raw histos
HvsSD = {}
histos={}
for sample in samples:
    files[sample].cd()
    if(files[sample]):
        print "[INFO] find raw histograms file: %s_allCut_test.root"%sample
    histos[sample]={}
    HvsSD[sample]=TH2Poly()
    for var_name in var_names:
        print "[INFO] this var_name: %s"%var_name
        histos[sample][var_name] = files[sample].Get(sample+"_"+var_name)
        if(histos[sample][var_name]):
            print "[INFO] find raw histograms : {}_{}".format(sample,var_name)

    HvsSD[sample].Add(histos[sample]['Hmass'],histos[sample]['SDmass_SR'])

    HvsSD[sample].Draw()
