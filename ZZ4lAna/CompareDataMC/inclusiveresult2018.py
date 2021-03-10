import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
import FakeRates as FR
from Plot_Helper import *
from deltaR import *
from SSMethod import *

gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(False)
ROOT.ROOT.EnableImplicitMT(4)

def main():
    save_dir = 'plot'
    filename = '/cms/user/guojl/Sample/FakeRates/FakeRates_SS_2018_Legacy.root'
    FakeRate = FR.FakeRates(filename)

    analyzer_cfg = AC.Analyzer_Config('inclusive')
    ntuples = LoadNtuples(analyzer_cfg)

    cat_names = ['4l']
    plot_cfg = PC.Plot_Config(analyzer_cfg)
    histos = {}
    histos['4l'] = {}
    for sample in analyzer_cfg.samp_names:
        histos['4l'][sample] = ROOT.TH1D("4l"+sample,"4l"+sample,50,70,170)

    lep_index = [0,0,0,0]
    for sample in analyzer_cfg.samp_names:
        ntup = ntuples[sample]
        #====================start analysis=====================
        for ievent,event in enumerate(ntup):
            #if(ievent==10000): break
            if(sample == 'ZX'):
                passedSSCRselection = foundSSCRCandidate(event,lep_index)
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
                    weight = FakeRate.GetFakeRate(event.lepFSR_pt[lep_index[2]],event.lepFSR_eta[lep_index[2]],event.lep_id[lep_index[2]])*FakeRate.GetFakeRate(event.lepFSR_pt[lep_index[3]],event.lepFSR_eta[lep_index[3]],event.lep_id[lep_index[3]])
                    histos['4l'][sample].Fill(mass4l,weight)
            elif(sample == 'data'):
                if(not event.passedFullSelection): continue
                histos['4l'][sample].Fill(event.mass4l)
            else:
                weight = Getbkgweight(event,sample)
                if(sample == 'bbH_HToZZTo4L'):
                    if(not event.passedFullSelection): continue
                    histos['4l'][sample].Fill(event.mass4l,weight)
                else:
                    histos['4l'][sample].Fill(event.H_FSR,weight)
        #==================end analysis============================

    #set histoStyles and save raw histograms
    for sample in analyzer_cfg.samp_names:
        plot_cfg.SetHistStyles(histos['4l'][sample], sample,'4l')

    # save stack plots and make ratio plots
    lumi_label = MakeLumiLabel(plot_cfg.lumi)
    cms_label  = MakeCMSDASLabel()


    Simhito,GGZZhito = AddHistos(histos['4l'],analyzer_cfg,'4l')
    stacks = MakeStack(histos['4l'], analyzer_cfg, '4l',Simhito,GGZZhito)
    scaled_data = MakeDataLabel(stacks['data'], '4l')
    legend = MakeLegend(plot_cfg, histos['4l'],Simhito,GGZZhito)
    canv = CreateCanvas('4l')
    DrawOnCanv(canv, '4l', plot_cfg, stacks, histos['4l'],scaled_data,legend, lumi_label, cms_label)
    save_name = "result2018"
    SaveCanvPic(canv, save_dir, save_name)

main()
