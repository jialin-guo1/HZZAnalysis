from ROOT import *
import os,sys
import time
from array import array
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

#================================================================================
#this macro does not do any analysis, just get plots from RawHistos and show cut table
#================================================================================

DY_pt100To250 = ['DYJetsToLL_Pt-100To250_01','DYJetsToLL_Pt-100To250_02','DYJetsToLL_Pt-100To250_03','DYJetsToLL_Pt-100To250_04','DYJetsToLL_Pt-100To250_05','DYJetsToLL_Pt-100To250_06','DYJetsToLL_Pt-100To250_07']
DY_pt250To400 = ['DYJetsToLL_Pt-250To400_01','DYJetsToLL_Pt-250To400_02','DYJetsToLL_Pt-250To400_03','DYJetsToLL_Pt-250To400_04','DYJetsToLL_Pt-250To400_05','DYJetsToLL_Pt-250To400_06','DYJetsToLL_Pt-250To400_07','DYJetsToLL_Pt-250To400_08','DYJetsToLL_Pt-250To400_09','DYJetsToLL_Pt-250To400_10','DYJetsToLL_Pt-250To400_11','DYJetsToLL_Pt-250To400_12','DYJetsToLL_Pt-250To400_13']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
samples = DY_pt100To250+DY_pt250To400+DY_pt_400ToInf+['GluGluHToZZTo2L2Q_M3000']
signal = 'GluGluHToZZTo2L2Q_M3000'
bkg = 'QCD'
var_names = ['ZvsQCD_de','tau21_DDT','particleNet_ZvsQCD_de']

PH = plotHelper(samples,'2018Legacy') #initialize plot

#book ROOT file storing raw histos
files={}
for sample in samples:
    files[sample] = TFile("../RawHistos/%s_particleNetDeepTau.root"%sample)

#book histos and efficiency
histos={}
efficiency={}
efficiency['SIG']={}
efficiency['BKG']={}
for sample in samples:
    histos[sample]={}
    for var_name in var_names:
        #histos[sample][var_name] = TH1D()
        histos[sample][var_name] = files[sample].Get(sample+"_"+var_name)
for var_name in var_names:
    efficiency['SIG'][var_name] = {}
    efficiency['BKG'][var_name] = {}
    for i in range(0,100):
        cut = Double(i)/100
        efficiency['SIG'][var_name][cut] = 0.0
        efficiency['BKG'][var_name][cut] = 0.0

histosBKG = {}
histosSIG = {}
for var_name in var_names:
    histosBKG[var_name] = TH1D('bkg'+var_name,'bkg'+var_name,100,0,1)
    histosSIG[var_name] = TH1D('SIG'+var_name,'SIG'+var_name,100,0,1)
    histosBKG[var_name].Sumw2()
    histosSIG[var_name].Sumw2()
    for sample in samples:
        if(sample.find('DYJets')!=-1 or sample.find('DYBJets')!=-1):
            histosBKG[var_name].Add(histos[sample][var_name])
            print "[INFO] add bkg: "+sample
        else:
            histosSIG[var_name].Add(histos[sample][var_name])
            print "[INFO] add singal: "+sample

#start to caculate efficiency in each setted cut
#and print the cut point and efficiency
for i in range(0,100):
    cut = Double(i)/100
    for var_name in var_names:
        binx1 = histosSIG[var_name].GetXaxis().FindBin(cut)
        binx2 = histosSIG[var_name].GetXaxis().FindBin(1)

        temp_numerator = histosSIG[var_name].Integral(binx1,binx2)
        temp_denominator = histosSIG[var_name].Integral()
        temp_efficiency = temp_numerator/temp_denominator

        if(var_name=='tau21' or var_name =='tau21_DDT'):
            efficiency['SIG'][var_name][cut]=(1-temp_efficiency)
        else:
            efficiency['SIG'][var_name][cut]=(temp_efficiency)

        temp_numerator = histosBKG[var_name].Integral(binx1,binx2)
        temp_denominator = histosBKG[var_name].Integral()
        temp_efficiency = temp_numerator/temp_denominator

        if(var_name=='tau21' or var_name =='tau21_DDT'):
            efficiency['BKG'][var_name][cut]=(1-temp_efficiency)
        else:
            efficiency['BKG'][var_name][cut]=(temp_efficiency)



bkg_efficiency_cuttables = [0.025,0.050,0.075,0.100,0.150,0.2]
for var_name in var_names:
    print "[INFO] start get cut point in %s varable"%var_name
    #loop over the bkg_efficiency_cuttables to find cut point
    for bkg_efficiency_cuttable in bkg_efficiency_cuttables:
        tmepDeltaeff = 9999.9
        tmepefficiency = 0.0
        tmep_signaleff = 0.0
        tmep_cutpoint = 0.0
        for i in range(0,100):
            cut = Double(i)/100
            #binx1 = histos['GluGluHToZZTo2L2Q_MAll'][var_name].GetXaxis().FindBin(cut)
            #binx2 = histos['GluGluHToZZTo2L2Q_MAll'][var_name].GetXaxis().FindBin(1)
            #temp_numerator = histos['GluGluHToZZTo2L2Q_MAll'][var_name].Integral(binx1,binx2)
            #weighted_signal = temp_numerator*PH.lumi*3000*0.1023/

            if((bkg_efficiency_cuttable-efficiency['BKG'][var_name][cut]<=tmepDeltaeff) and (bkg_efficiency_cuttable-efficiency['BKG'][var_name][cut]>=0)):
                tmepDeltaeff = bkg_efficiency_cuttable-efficiency['BKG'][var_name][cut]
                tmepefficiency = efficiency['BKG'][var_name][cut]
                tmep_signaleff = efficiency['SIG'][var_name][cut]
                tmep_cutpoint = cut
            else:
                continue

        print "[INFO] signal efficiency = {0}, when bkg efficiency less than {1}, the cut point = {2}.".format(tmep_signaleff,tmepefficiency,tmep_cutpoint)
