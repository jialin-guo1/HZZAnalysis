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

samples = ['GluGluHToZZTo2L2Q_MAll','QCD']
var_names = ['ZvsQCD','tau21','WvsQCD','ZvsQCD_de','WvsQCD_de','tau21_DDT']
PH = plotHelper(samples,2018) #initialize plot

#book ROOT file storing raw histos
inputfilename = "../RawHistos/DeepAK8VarAll_noptbins.root"
inputfile = TFile(inputfilename)
if(inputfile):
    print "[INFO] find raw histograms file: "+inputfilename

#book histos and efficiency
histos={}
efficiency={}
for sample in samples:
    histos[sample]={}
    efficiency[sample]={}
    for var_name in var_names:
        #histos[sample][var_name] = TH1D()
        histos[sample][var_name] = inputfile.Get(sample+"_"+var_name)
        efficiency[sample][var_name] = {}
        for i in range(0,100):
            cut = Double(i)/100
            efficiency[sample][var_name][cut] = 0.0

#start to caculate efficiency in each setted cut
#and print the cut point and efficiency
for i in range(0,100):
    cut = Double(i)/100
    for sample in samples:
        for var_name in var_names:
            binx1 = histos[sample][var_name].GetXaxis().FindBin(cut)
            binx2 = histos[sample][var_name].GetXaxis().FindBin(1)
            temp_numerator = histos[sample][var_name].Integral(binx1,binx2)
            temp_denominator = histos[sample][var_name].Integral()
            temp_efficiency = temp_numerator/temp_denominator
            if(var_name=='tau21' or var_name =='tau21_DDT'):
                efficiency[sample][var_name][cut]=(1-temp_efficiency)
            else:
                efficiency[sample][var_name][cut]=(temp_efficiency)

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
            binx1 = histos['GluGluHToZZTo2L2Q_MAll'][var_name].GetXaxis().FindBin(cut)
            binx2 = histos['GluGluHToZZTo2L2Q_MAll'][var_name].GetXaxis().FindBin(1)
            temp_numerator = histos['GluGluHToZZTo2L2Q_MAll'][var_name].Integral(binx1,binx2)
            #weighted_signal = temp_numerator*PH.lumi*3000*0.1023/

            if((bkg_efficiency_cuttable-efficiency['QCD'][var_name][cut]<=tmepDeltaeff) and (bkg_efficiency_cuttable-efficiency['QCD'][var_name][cut]>=0)):
                tmepDeltaeff = bkg_efficiency_cuttable-efficiency['QCD'][var_name][cut]
                tmepefficiency = efficiency['QCD'][var_name][cut]
                tmep_signaleff = efficiency['GluGluHToZZTo2L2Q_MAll'][var_name][cut]
                tmep_cutpoint = cut
            else:
                continue

        print "[INFO] signal efficiency = {0}, when bkg efficiency less than {1}, the cut point = {2}.".format(tmep_signaleff,tmepefficiency,tmep_cutpoint)
