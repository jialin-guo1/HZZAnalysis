from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

DY_pt100To250 = ['DYJetsToLL_Pt-100To250_01','DYJetsToLL_Pt-100To250_02','DYJetsToLL_Pt-100To250_03','DYJetsToLL_Pt-100To250_04','DYJetsToLL_Pt-100To250_05']
DY_pt250To400 = ['DYJetsToLL_Pt-250To400_01','DYJetsToLL_Pt-250To400_02','DYJetsToLL_Pt-250To400_03','DYJetsToLL_Pt-250To400_04','DYJetsToLL_Pt-250To400_05']
#DY_pt100To250 = ['DYJetsToLL_Pt-100To250_01','DYJetsToLL_Pt-100To250_02','DYJetsToLL_Pt-100To250_03','DYJetsToLL_Pt-100To250_04','DYJetsToLL_Pt-100To250_05','DYJetsToLL_Pt-100To250_06','DYJetsToLL_Pt-100To250_07','DYJetsToLL_Pt-100To250_08','DYJetsToLL_Pt-100To250_09','DYJetsToLL_Pt-100To250_10']
#DY_pt250To400 = ['DYJetsToLL_Pt-250To400_01','DYJetsToLL_Pt-250To400_02','DYJetsToLL_Pt-250To400_03','DYJetsToLL_Pt-250To400_04','DYJetsToLL_Pt-250To400_05','DYJetsToLL_Pt-250To400_06','DYJetsToLL_Pt-250To400_07','DYJetsToLL_Pt-250To400_08','DYJetsToLL_Pt-250To400_09','DYJetsToLL_Pt-250To400_10','DYJetsToLL_Pt-250To400_11']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
signal = ['GluGluHToZZTo2L2Q_M1000']
otherBKG = ['WZ','ZZ_TuneCP5','TTJets']
samples = otherBKG+DY_pt250To400+DY_pt_400ToInf+DY_pt100To250+signal
#samples = signal
var_names = ['SDmass_SR','SDmass_CR','Pt','eta','Z1mass','Z1_pt','Hmass','dR_lep','dR_ZZ','ZvsQCD_de','tau21_DDT']
#var_names = ['HvsSD']
#var_names = ['Z1_pt']
PH = plotHelper(samples,2018)

files={}
for sample in samples:
    files[sample] = TFile("../RawHistos/%s_allCut_test.root"%sample)


#book ROOT file storing raw histos
histos={}
for sample in samples:
    #inputfilename = "../RawHistos/%s_test.root"%sample
    #inputfile = TFile(inputfilename)
    files[sample].cd()
    #if(inputfile):
    #    print "[INFO] find raw histograms file: "+inputfilename
    if(files[sample]):
        print "[INFO] find raw histograms file: %s_allCut_test.root"%sample

    #h = files[sample].Get(sample+"_"+'Z1_mass')

    #handle histos from root file
    histos[sample]={}
    for var_name in var_names:
        #histos[sample][var_name] = TH1D()
        print "[INFO] this var_name: %s"%var_name
        if(var_name=='HvsSD'):
            histos[sample][var_name] = files[sample].Get(sample+var_name)
        else:
            histos[sample][var_name] = files[sample].Get(sample+'_'+var_name)
        if(histos[sample][var_name]):
            print "[INFO] find raw histograms : {}_{}".format(sample,var_name)



#histos['GluGluHToZZTo2L2Q_M1000']['ZvsQCD_de'].SetLineColor(PH.colors['GluGluHToZZTo2L2Q_M1000'])
#histos['DYJetsToLL_Pt-400To650']['dR_ZZ'].SetLineColor(PH.colors['DYJetsToLL_Pt-400To650'])
#print " passed set"

for sample in samples:
    for var_name in var_names:
        print "this histos = {}_{}".format(sample,var_name)
        PH.SetHistStyles(histos[sample][var_name],sample,var_name)


#inputfilename = "../RawHistos/FinalCut_test.root"
#inputfile = TFile(inputfilename)
#if(inputfile):
#    print "[INFO] find raw histograms file: "+inputfilename


#Draw Plots
print "[INFO] Start draw plots on canvas"
plotname = 'allCut'
for var_name in var_names:
    print "[INFO] start to draw %s variable"%var_name
    if(var_name=='HvsSD'):
        PH.Draw2DPlots(histos,samples,var_name,plotname)
    else:
        PH.DrawStack(histos,samples,var_name,plotname)
