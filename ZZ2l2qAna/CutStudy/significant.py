from ROOT import *
import os,sys
import time
from array import array
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *
import math

#================================================================================
#this macro does not do any analysis, just get plots for RawHistos and draw singal and background efficiency
#================================================================================

DY_pt100To250 = ['DYJetsToLL_Pt-100To250_01','DYJetsToLL_Pt-100To250_02','DYJetsToLL_Pt-100To250_03','DYJetsToLL_Pt-100To250_04','DYJetsToLL_Pt-100To250_05','DYJetsToLL_Pt-100To250_06','DYJetsToLL_Pt-100To250_07']
DY_pt250To400 = ['DYJetsToLL_Pt-250To400_01','DYJetsToLL_Pt-250To400_02','DYJetsToLL_Pt-250To400_03','DYJetsToLL_Pt-250To400_04','DYJetsToLL_Pt-250To400_05','DYJetsToLL_Pt-250To400_06','DYJetsToLL_Pt-250To400_07','DYJetsToLL_Pt-250To400_08','DYJetsToLL_Pt-250To400_09','DYJetsToLL_Pt-250To400_10','DYJetsToLL_Pt-250To400_11','DYJetsToLL_Pt-250To400_12','DYJetsToLL_Pt-250To400_13']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
samples = DY_pt100To250+DY_pt250To400+DY_pt_400ToInf+['GluGluHToZZTo2L2Q_M3000']#['BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M3000']
signal = 'GluGluHToZZTo2L2Q_M3000'
bkg = 'QCD'
var_names = ['ZvsQCD_de','tau21_DDT','particleNet_ZvsQCD_de','particleNet_Zbbvslight_de','ZbbvsQCD_de']

PH = plotHelper(samples,'2018Legacy') #initialize plot

#book ROOT file storing raw histos
files={}
for sample in samples:
    files[sample] = TFile("../RawHistos/%s_particleNetDeepTau.root"%sample)


#book histos and efficiency
histos={}
significant={}
for sample in samples:
    files[sample].cd()
    histos[sample]={}
    for var_name in var_names:
        #histos[sample][var_name] = TH1D()
        histos[sample][var_name] = files[sample].Get(sample+"_"+var_name)
        significant[var_name] = array('f',[])

histosBKG = {}
histosSIG = {}
for var_name in var_names:
    histosBKG[var_name] = TH1D('bkg'+var_name,'bkg'+var_name,100,0,1)
    histosSIG[var_name] = TH1D('SIG'+var_name,'SIG'+var_name,100,0,1)
    histosBKG[var_name].Sumw2()
    histosSIG[var_name].Sumw2()
    for sample in samples:
        if(sample.find('DYJets')!=-1):
            histosBKG[var_name].Add(histos[sample][var_name])
            print "[INFO] add bkg: "+sample
        else:
            histosSIG[var_name].Add(histos[sample][var_name])
            print "[INFO] add singal: "+sample

vector_X =  array('f',[])#for cut pint
#start to caculate significant in each setted cut
for i in range(0,100):
    cut = Double(i)/100
    vector_X.append(cut)
    for var_name in var_names:
        #print "start var_name = "+var_name
        binx1 = histosSIG[var_name].GetXaxis().FindBin(cut)
        binx2 = histosSIG[var_name].GetXaxis().FindBin(1)
        if(var_name=='tau21' or var_name =='tau21_DDT'):
            temp_numerator = histosSIG[var_name].Integral(0,binx1)
            temp_denominator = math.sqrt(temp_numerator+histosBKG[var_name].Integral(0,binx1))
        else:
            temp_numerator = histosSIG[var_name].Integral(binx1,binx2)
            temp_denominator = math.sqrt(temp_numerator+histosBKG[var_name].Integral(binx1,binx2))

        #print "temp_numerator = "+str(temp_numerator)
        #print "temp_denominator = "+str(temp_denominator)
        if(temp_denominator == 0 or temp_numerator==0):
            significant[var_name].append(0.0)
        else:
            significant[var_name].append(temp_numerator/temp_denominator)


vector_Y = {} #for significant
graph = {}
for var_name in var_names:
    vector_Y[var_name] = significant[var_name]

    graph[var_name] = TGraph( len(vector_X) , vector_X , vector_Y[var_name] )


graphs = TMultiGraph()
for var_name in var_names:

    graphs.Add(graph[var_name])

    graph['ZvsQCD_de'].SetLineColor(kRed)
    graph['ZvsQCD_de'].SetTitle("ZvsQCD_decorrelated")
    graph['ZvsQCD_de'].SetLineStyle(2)

    graph['tau21_DDT'].SetLineColor(kBlack)
    graph['tau21_DDT'].SetTitle("tau21_DDT")
    graph['tau21_DDT'].SetLineStyle(2)

    graph['particleNet_ZvsQCD_de'].SetLineColor(kBlue)
    graph['particleNet_ZvsQCD_de'].SetTitle("particleNet_ZvsQCD_de")
    graph['particleNet_ZvsQCD_de'].SetLineStyle(2)

    graph['ZbbvsQCD_de'].SetLineColor(kGreen)
    graph['ZbbvsQCD_de'].SetTitle("ZbbvsQCD_decorrelated")
    graph['ZbbvsQCD_de'].SetLineStyle(2)

    graph['particleNet_Zbbvslight_de'].SetLineColor(kYellow)
    graph['particleNet_Zbbvslight_de'].SetTitle("particleNet_ZbbvsQCD_de")
    graph['particleNet_Zbbvslight_de'].SetLineStyle(2)

graphs.GetXaxis().SetTitle("Cut Point")
graphs.GetYaxis().SetTitle("Significant")

c = TCanvas('efficiency','efficiency',700,700)
graphs.Draw("AC")

leg = PH.MakeLegend('left')
#leg.AddEntry(graph['ZvsQCD'], 'ZvsQCD')
#leg.AddEntry(graph['tau21'], 'tau21')
#leg.AddEntry(graph['WvsQCD'], 'WvsQCD')
#leg.AddEntry(graph['WvsQCD_de'], 'WvsQCD_decorrelated')
leg.AddEntry(graph['ZvsQCD_de'], 'ZvsQCD_decorrelated')
leg.AddEntry(graph['ZbbvsQCD_de'], 'ZbbvsQCD_decorrelated')
leg.AddEntry(graph['tau21_DDT'], 'tau21_DDT')
leg.AddEntry(graph['particleNet_ZvsQCD_de'],'particleNet_decorrelated')
leg.AddEntry(graph['particleNet_Zbbvslight_de'],'particleNet_btag_decorrelated')
leg.Draw()


savename = "../plot/significant"
PH.SavePlots(c,savename)
