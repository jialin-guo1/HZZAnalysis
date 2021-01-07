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
    lumi=41.5
    outfilename = "2017Cat"
    save_dir = 'plot'
    outfile=ROOT.TFile("../RawHistos/"+outfilename+".root","RECREATE")

    #create object for FakeRate
    filename = '/cms/user/guojl/Sample/FakeRates/FakeRates_SS_2017_Legacy.root'
    FakeRate = FR.FakeRates(filename)

    analyzer_cfg = AC.Analyzer_Config('inclusive')
    ntuples = LoadNtuples(analyzer_cfg)

    cat_names = ['untagged','VBF-1jet','VBF-2jets','VH-leptonic','VH-hadronic','ttH-hadronic','ttH-leptonic']
    plot_cfg = PC.Plot_Config(analyzer_cfg)
    histos = {}
    for cat_name in cat_names:
        histos[cat_name]={}
        for sample in analyzer_cfg.samp_names:
            histos[cat_name][sample] = ROOT.TH1D(cat_name+sample,cat_name+sample,50,70,170)

    lep_index = [0,0,0,0]
    for sample in analyzer_cfg.samp_names:
        ntup = ntuples[sample]
        #====================start analysis=====================
        for ievent,event in enumerate(ntup):
            #if(ievent==10000): break
            if(sample == 'data' or sample == 'ZX' or sample == 'bbH_HToZZTo4L'):
                if(event.EventCat==1):
                    cat='VBF-1jet'
                elif(event.EventCat==2):
                    cat='VBF-2jets'
                elif(event.EventCat==3):
                    cat='VH-leptonic'
                elif(event.EventCat==4):
                    cat='VH-hadronic'
                elif(event.EventCat==5):
                    cat='ttH-hadronic'
                elif(event.EventCat==6):
                    cat='ttH-leptonic'
                else:
                    cat='untagged'
            else:
                if(event.Cat==1):
                    cat='VBF-1jet'
                elif(event.Cat==2):
                    cat='VBF-2jets'
                elif(event.Cat==3):
                    cat='VH-leptonic'
                elif(event.Cat==4):
                    cat='VH-hadronic'
                elif(event.Cat==5):
                    cat='ttH-hadronic'
                elif(event.Cat==6):
                    cat='ttH-leptonic'
                else:
                    cat='untagged'
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
                    histos[cat][sample].Fill(mass4l,weight)
            elif(sample == 'data'):
                if(not event.passedFullSelection): continue
                histos[cat][sample].Fill(event.mass4l)
            else:
                weight = Getbkgweight(event,sample,lumi)
                if(sample == 'bbH_HToZZTo4L'):
                    if(not event.passedFullSelection): continue
                    histos[cat][sample].Fill(event.mass4l,weight)
                else:
                    histos[cat][sample].Fill(event.H_FSR,weight)
        #==================end analysis============================

    #set histoStyles and save raw histograms
    outfile.cd()
    for cat_name in cat_names:
        for sample in analyzer_cfg.samp_names:
            plot_cfg.SetHistStyles(histos[cat_name][sample], sample,cat_name)
            histos[cat_name][sample].Write()
    outfile.Close()

    # save stack plots and make ratio plots
    lumi_label = MakeLumiLabel(plot_cfg.lumi)
    cms_label  = MakeCMSDASLabel()

    for cat_name in cat_names:
        Simhito,GGZZhito = AddHistos(histos[cat_name],analyzer_cfg,cat_name)
        stacks = MakeStack(histos[cat_name], analyzer_cfg, cat_name,Simhito,GGZZhito)
        scaled_data = MakeDataLabel(stacks['data'], cat_name)
        legend = MakeLegend(plot_cfg, histos[cat_name],Simhito,GGZZhito)
        canv = CreateCanvas(cat_name)
        DrawOnCanv(canv, cat_name, plot_cfg, stacks, histos[cat_name],scaled_data,legend, lumi_label, cms_label)
        save_name = "{0:s}2017".format(cat_name)
        SaveCanvPic(canv, save_dir, save_name)

main()
