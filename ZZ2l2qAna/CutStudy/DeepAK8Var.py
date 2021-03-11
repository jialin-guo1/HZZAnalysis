from ROOT import *
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import plotHelper


sampels = ['ZZ','DYJets']
var_names = ['ZvsQCD','tau21']
PH = plotHelper(samples,2017)

#book histos
histos = {}
for sample in sampls:
    histos[sample]={}
    for var_name in var_names:
        histos[sample][var_name]=TH1D(sample+"_"+var_name,sample+"_"+var_name,50,0,1)
        PH.SetHistStyles(histos[sample][var_name],sample)


for sample in samples:
    tempTree = PH.trees[sample]
    for ievent,event in enumerate(tempTree):
        histos[sample]['ZvsQCD'].fill(event.mergedjet_ZvsQCD[0])
        temptau1 = event.mergedjet_tau1[0]
        temptau2 = event.mergedjet_tau2[0]
        histos[sample]['tau21'].fill(temptau2/temptau1)

#normalize to one
for sample in samples:
    for var_name in var_names:
        histos[sample][var_name].Scale(1/histos[sample][var_name].Integral())

c_ZvsQCD = TCanvas("ZvsQCD","ZvsQCD",600,600)
c_tau21 = TCanvas("tau21","tau21",600,600)

cms_label,lumi_label = PH.MakeCMSandLumiLabel()
legend = PH.MakeLegend()

c_ZvsQCD.cd()
for sample in sampels:
    histos[sample]['ZvsQCD'].GetYaxis().SetTitle("Normalized")
    if(sample=='ZZ'):
        legend.AddEntry(histos[sample]['ZvsQCD'],"ZZ",'f')
    if(sample=='DYJets'):
        legend.AddEntry(histos[sample]['ZvsQCD'],"Z + jets",'f')
histos['ZZ']['ZvsQCD'].Draw('histo')
histos.['DYJets']['ZvsQCD'].Draw('same histo')
cms_label.Draw('same')
lumi_label.Draw('same')
legend.Draw()

plotname = "../plot/Z_vsQCD"
PH.SavePlots(c_ZvsQCD,plotname)

c_tau21.cd()
for sample in sampels:
    histos[sample]['tau21'].GetYaxis().SetTitle("Normalized")
    if(sample=='ZZ'):
        legend.AddEntry(histos[sample]['tau21'],"ZZ",'f')
    if(sample=='DYJets'):
        legend.AddEntry(histos[sample]['tau21'],"Z + jets",'f')

histos['ZZ']['tau21'].Draw('histo')
histos.['DYJets']['tau21'].Draw('same histo')
cms_label.Draw('same')
lumi_label.Draw('same')
legend.Draw()

plotname = "../plot/tau21"
PH.SavePlots(c_tau21,plotname)
