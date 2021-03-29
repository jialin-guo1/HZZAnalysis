from ROOT import *
import os,sys
import time
from array import array
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

#================================================================================
#this macro does not do any analysis, just get plots for RawHistos and draw singal and background efficiency
#================================================================================

samples = ['ZZ','DYJets']
var_names = ['ZvsQCD','tau21']
PH = plotHelper(samples,2017) #initialize plot

#book ROOT file storing raw histos
inputfilename = "../RawHistos/DeepAK8Var.root"
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
        efficiency[sample][var_name] = array('f',[])



#start to caculate efficiency in each setted cut
for i in range(0,50):
    cut = Double(i)/50
    for sample in samples:
        for var_name in var_names:
            binx1 = histos[sample][var_name].GetXaxis().FindBin(cut)
            binx2 = histos[sample][var_name].GetXaxis().FindBin(1)
            temp_numerator = histos[sample][var_name].Integral(binx1,binx2)
            temp_denominator = histos[sample][var_name].Integral()
            temp_efficiency = temp_numerator/temp_denominator
            if(var_name=='tau21'):
                efficiency[sample][var_name].append(1-temp_efficiency)
            else:
                efficiency[sample][var_name].append(temp_efficiency)


#for sample in samples:
#    for var_name in var_names:
#        efficiency[sample][var_name].sort()

vector_X = {} #for singal
vector_Y ={}  #for backgrounds
graph = {}
for var_name in var_names:
    vector_X[var_name] = efficiency['ZZ'][var_name]
    vector_Y[var_name] = efficiency['DYJets'][var_name]

    graph[var_name] = TGraph( len(vector_X[var_name]) , vector_X[var_name] , vector_Y[var_name] )


graphs = TMultiGraph()
#graphs.SetLogy()
for var_name in var_names:
    graphs.Add(graph[var_name])

    graph['ZvsQCD'].SetLineColor(kRed)
    graph['ZvsQCD'].SetTitle("ZvsQCD")

    graph['tau21'].SetLineColor(kBlack)
    graph['tau21'].SetTitle("tau21")

graphs.GetXaxis().SetTitle("Signal efficiency")
graphs.GetYaxis().SetTitle("Background efficiency")

c = TCanvas('efficiency','efficiency',700,700)
graphs.Draw("AC")

leg = PH.MakeLegend('left')
leg.AddEntry(graph['ZvsQCD'], 'ZvsQCD')
leg.AddEntry(graph['tau21'], 'tau21')
leg.Draw()


savename = "../plot/efficiency"
PH.SavePlots(c,savename)
