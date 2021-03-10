import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
import FakeRates as FR
import SSMethod
from Plot_Helper import *
from deltaR import *


gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(False)
ROOT.ROOT.EnableImplicitMT(4)

def main():
    lumi2016=35.9
    lumi2017=41.5
    lumi2018=59.7
    years=['2016','2017','2018']
    outfilename = "RuIICat"
    save_dir = 'plot'
    outfile=ROOT.TFile("../RawHistos/"+outfilename+".root","RECREATE")
    analyzer_cfg = AC.Analyzer_Config('inclusive')
    SS = SSMethod.SSMethod()


    ntuples={}
    for year in years:
        ntuples[year] = LoadNtuples(analyzer_cfg,year)

    #cat_names = ['untagged','VBF-1jet','VBF-2jets','VH-leptonic','VH-hadronic','ttH-hadronic','ttH-leptonic']
    cat_names = ['inclusive']
    plot_cfg = PC.Plot_Config(analyzer_cfg)
    print analyzer_cfg.samp_names
    histos = {}
    for cat_name in cat_names:
        histos[cat_name]={}
        for year in years:
            histos[cat_name][year]={}
            for sample in analyzer_cfg.samp_names:
                histos[cat_name][year][sample] = ROOT.TH1D(year+cat_name+sample,year+cat_name+sample,680,100,3500)
                histos[cat_name][year][sample].GetXaxis().SetLabelOffset(99)


    lep_index = [0,0,0,0]
    for year in years:
        if(year=='2016'):
            lumi=lumi2016
            filename='/cms/user/guojl/Sample/FakeRates/FakeRates_SS_2016_Legacy.root'
            FakeRate= FR.FakeRates(filename)
        elif(year=='2017'):
            lumi=lumi2017
            filename='/cms/user/guojl/Sample/FakeRates/FakeRates_SS_2017_Legacy.root'
            FakeRate= FR.FakeRates(filename)
        else:
            filename='/cms/user/guojl/Sample/FakeRates/FakeRates_SS_2018_Legacy.root'
            FakeRate= FR.FakeRates(filename)
            lumi=lumi2018
        for sample in analyzer_cfg.samp_names:
            ntup = ntuples[year][sample]
            #====================start analysis=====================
            for ievent,event in enumerate(ntup):
                #if(ievent==10): break
                if(sample == 'ZX'):
                    passedSSCRselection = SS.foundSSCRCandidate(event,lep_index)
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
                        histos['inclusive'][year][sample].Fill(mass4l,weight)
                elif(sample == 'data'):
                    if(not event.passedFullSelection): continue
                    histos['inclusive'][year][sample].Fill(event.mass4l)
                else:
                    weight = Getbkgweight(event,sample,lumi)
                    histos['inclusive'][year][sample].Fill(event.H_FSR,weight)
            #==================end analysis============================

    #set histoStyles and save raw histograms
    #outfile.cd()
    for year in years:
        for cat_name in cat_names:
            for sample in analyzer_cfg.samp_names:
                plot_cfg.SetHistStyles(histos[cat_name][year][sample], sample,cat_name)
    #            histos[year][cat_name][sample].Write()
    #outfile.Close()

    # save stack plots and make ratio plots
    lumi_label = MakeLumiLabel(plot_cfg.lumi)
    cms_label  = MakeCMSDASLabel()

    stackBkg={}
    SumData={}
    SumSim={}
    SumZX={}
    SumggZZ={}
    SumqqZZ={}
    for cat_name in cat_names:
        SumData[cat_name]=ROOT.TH1D("data"+cat_name,"data"+cat_name,680,100,3500)
        SumData[cat_name].Sumw2()
        SumData[cat_name].GetXaxis().SetLabelOffset(99)
        SumSim[cat_name]=ROOT.TH1D("Sim"+cat_name,"Sim"+cat_name,680,100,3500)
        SumSim[cat_name].Sumw2()
        SumSim[cat_name].GetXaxis().SetLabelOffset(99)
        SumSim[cat_name].SetFillColor(ROOT.kRed-7)
        SumZX[cat_name]=ROOT.TH1D("ZX"+cat_name,"ZX"+cat_name,680,100,3500)
        SumZX[cat_name].Sumw2()
        SumZX[cat_name].GetXaxis().SetLabelOffset(99)
        SumZX[cat_name].SetFillColor(ROOT.kGreen + 3)
        SumggZZ[cat_name]=ROOT.TH1D("ggZZ"+cat_name,"ggZZ"+cat_name,680,100,3500)
        SumggZZ[cat_name].Sumw2()
        SumggZZ[cat_name].GetXaxis().SetLabelOffset(99)
        SumggZZ[cat_name].SetFillColor(ROOT.kAzure -1)
        SumqqZZ[cat_name]=ROOT.TH1D("qqZZ"+cat_name,"qqZZ"+cat_name,680,100,3500)
        SumqqZZ[cat_name].Sumw2()
        SumqqZZ[cat_name].GetXaxis().SetLabelOffset(99)
        SumqqZZ[cat_name].SetFillColor(ROOT.kAzure +6)
        for year in years:
            SumData[cat_name].Add(histos[cat_name][year]['data'],1.0)
            Simhito,GGZZhito = AddHistos(histos[cat_name][year],analyzer_cfg,cat_name,year)
            SumSim[cat_name].Add(SumSim[cat_name],Simhito)
            SumggZZ[cat_name].Add(SumggZZ[cat_name],GGZZhito)
            SumZX[cat_name].Add(SumZX[cat_name],histos[cat_name][year]['ZX'])
            SumqqZZ[cat_name].Add(SumqqZZ[cat_name],histos[cat_name][year]['ZZTo4L'])
        stacks = MakeStack(histos[cat_name],analyzer_cfg,cat_name,SumSim[cat_name],SumggZZ[cat_name],SumZX[cat_name],SumqqZZ[cat_name])
        legend = ROOT.TLegend(0.65,0.65,0.85,0.85)
        legend.SetNColumns(1)
        legend.SetLineColor(10)
        legend.AddEntry(SumData[cat_name], "data")
        legend.AddEntry(SumSim[cat_name],"H(125)","f")
        legend.AddEntry(SumqqZZ[cat_name],"q#bar{q}->ZZ, Z#gamma*","f")
        legend.AddEntry(SumggZZ[cat_name],"gg->ZZ, Z#gamma*","f")
        legend.AddEntry(SumZX[cat_name],"Z+X","f")
        canv = CreateCanvas(cat_name)
        canv.cd()
        SumData[cat_name].SetMarkerStyle(20)
        SumData[cat_name].SetLineColor(ROOT.kBlack)
        SumData[cat_name].GetXaxis().SetTitle('m_{4l}')
        #hist.GetXaxis().SetTitleSize(0.20)
        SumData[cat_name].GetYaxis().SetTitle('Events / %d GeV' %SumData[cat_name].GetBinWidth(1))
        SumData[cat_name].Draw('PE')
        stacks['bkg'].Draw('same histo')
        SumData[cat_name].Draw('SAME PE')
        legend.Draw()
        cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)' %plot_cfg.lumi)
        lumi_label.Draw('same')
        # draw x label
        x_low = 100
        x_up =3500
        step = 10
        latex={}
        label_margin = -0.02
        for i in range(100,3500,step):
            if(i==200 or i==300 or i==400 or i==500 or i==1000 or i==2000 or i==3000):
                i_x = i
                latex[i] = ROOT.TLatex(i_x,label_margin,"%.0f"%i_x)
                latex[i].SetTextAlign(23)
                latex[i].SetTextFont (42)
                latex[i].SetTextSize (0.04)
                latex[i].Draw()
        save_name = "{0:s}XToZZRunII".format(cat_name)
        SaveCanvPic(canv, save_dir, save_name)

main()
