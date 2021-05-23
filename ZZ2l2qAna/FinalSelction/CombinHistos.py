from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

samples = ['GluGluHToZZTo2L2Q_M1000','DYJetsToLL_Pt-250To400','DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf','TTJets','WZ','ZZ_TuneCP5']
var_names = ['ZvsQCD_de','tau21_DDT','SDmass_SR','SDmass_CR','Pt','eta','Z1_mass','Hmass','dR_lep','dR_ZZ']


#book ROOT file storing raw histos
histos={}
for sample in samples:
    inputfilename = "../RawHistos/%s_test.root"%sample
    inputfile = TFile(inputfilename)
    if(inputfile):
        print "[INFO] find raw histograms file: "+inputfilename

    #handle histos from root file
    histos[sample]={}
    for var_name in var_names:
        histos[sample][var_name] = inputfile.Get(sample+"_"+var_name)
        if(histos[sample][var_name]):
            print "[INFO] find raw histograms : {}_{}".format(sample,var_name)

outfilename = "../RawHistos/Combine_allcut.root"
outfile = TFile(outfilename,'recreate')

print "[INFO] start to Combine"
outfile.cd()
for sample in samples:
    for var_name in var_names:
        histos[sample][var_name].Write()
        print "[INFO] {}_{} has been written".format(sample,var_name)
outfile.Close()
