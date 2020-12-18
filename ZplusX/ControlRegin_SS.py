import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
from Plot_Helper import *
from deltaR import *
from SSMethod import *

save_dir = 'plot'
analyzer_cfg = AC.Analyzer_Config('inclusive')
ntuples = LoadNtuples(analyzer_cfg)
print "get ntuples"


cat_names = ['4e', '4mu', '2mu2e', '2e2mu']
plot_cfg = PC.Plot_Config(analyzer_cfg)

#declare hito
histos = {}
for cat_name in cat_names:
    histos[cat_name] = {}
for sample in analyzer_cfg.samp_names:
    histos['4e'][sample] = ROOT.TH1D(sample+'4e',sample+'4e',40,70,800)
    histos['4mu'][sample] = ROOT.TH1D(sample+'4mu',sample+'4mu',40,70,800)
    histos['2mu2e'][sample] = ROOT.TH1D(sample+'2mu2e',sample+'2mu2e',40,70,800)
    histos['2e2mu'][sample] = ROOT.TH1D(sample+'2e2mu',sample+'2e2mu',40,70,800)
print " get histos"

#loop over samples and events
for sample in analyzer_cfg.samp_names:
    lep_index = [0,0,0,0]
    print " enter the loop of samples = " + sample
    ntup = ntuples[sample]
    print type(ntup)
    print "get ntuple"
    print ntup.GetEntries()
    for ievent,event in enumerate(ntup):
        print "enter the loop of events"
        passedSSCRselection = foundSSCRCandidate(event)
        if(passedSSCRselection):
            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l3 = ROOT.TLorentzVector()
            l4 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[lep_index[0]],event.lepFSR_eta[lep_index[0]],event.lepFSR_phi[lep_index[0]],event.lepFSR_mass[lep_index[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[lep_index[1]],event.lepFSR_eta[lep_index[1]],event.lepFSR_phi[lep_index[1]],event.lepFSR_mass[lep_index[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[lep_index[2]],event.lepFSR_eta[lep_index[2]],event.lepFSR_phi[lep_index[2]],event.lepFSR_mass[lep_index[2]])
            l4.SetPtEtaPhiM(event.lepFSR_pt[lep_index[3]],event.lepFSR_eta[lep_index[3]],event.lepFSR_phi[lep_index[3]],event.lepFSR_mass[lep_index[3]])
            mass4l = (l1+l2+l3+l4).M()

            if(abs(event.lep_id[lep_index[0]])==abs(event.lep_id[lep_index[1]])==abs(event.lep_id[lep_index[2]])==abs(event.lep_id[lep_index[3]])==11):
                histo['4e'][sample].Fill(mass4l)
            if(abs(event.lep_id[lep_index[0]])==abs(event.lep_id[lep_index[1]])==abs(event.lep_id[lep_index[2]])==abs(event.lep_id[lep_index[3]])==13):
                histo['4mu'][sample].Fill(mass4l)
            if(abs(event.lep_id[lep_index[0]])==abs(event.lep_id[lep_index[1]])==11 and abs(event.lep_id[lep_index[2]])==abs(event.lep_id[lep_index[3]])==13):
                histo['2e2mu'][sample].Fill(mass4l)
            if(abs(event.lep_id[lep_index[0]])==abs(event.lep_id[lep_index[1]])==13 and abs(event.lep_id[lep_index[2]])==abs(event.lep_id[lep_index[3]])==11):
                histo['2mu2e'][sample].Fill(mass4l)


# save stack plots and make ratio plots
lumi_label = MakeLumiLabel(plot_cfg.lumi)
cms_label  = MakeCMSDASLabel()

for cat_name in cat_names:
    stacks = MakeStack(histos[cat_name], analyzer_cfg, cat_name)
    scaled_data = MakeDataLabel(histo[cat_name]['data'],cat_name)
    legend = MakeLegend(plot_cfg, histos[cat_name], scaled_data)

    canv = CreateCanvas(cat_name)
    DrawOnCanv(canv, cat_name, plot_cfg, stacks, histos[cat_name], scaled_data,legend, lumi_label, cms_label)
    SaveCanvPic(canv, save_dir, cat_name)
