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

save_dir = 'plot'

analyzer_cfg = AC.Analyzer_Config('inclusive')
plot_cfg = PC.Plot_Config(analyzer_cfg)

years=['2016','2017','2018']
cat_names = ['untagged','VBF_1jet','VBF_2jets','VH_leptonic','VH_hadronic','ttH_hadronic','ttH_leptonic']
plot_cfg = PC.Plot_Config(analyzer_cfg)
histos = {}
for year in years:
    tempFile = ROOT.TFile("../RawHistos/{0:s}Cat.root".format(year))
    histos[year]={}
    for cat_name in cat_names:
        temp_cat_name=cat_name.replace('_','-')
        histos[year][cat_name]={}
        for sample in analyzer_cfg.samp_names:
            print "to get histogram: "+temp_cat_name+sample
            histos[year][cat_name][sample] = tempFile.Get(cat_name+sample)

for year in years:
    for cat_name in cat_names:
        for sample in analyzer_cfg.samp_names:
            plot_cfg.SetHistStyles(histos[year][cat_name][sample], sample,cat_name)

lumi_label = MakeLumiLabel(plot_cfg.lumi)
cms_label  = MakeCMSDASLabel()

stackBkg={}
SumData={}
SumSim={}
SumZX={}
SumggZZ={}
SumqqZZ={}
for cat_name in cat_names:
    SumData[cat_name]=ROOT.TH1D("data"+cat_name,"data"+cat_name,50,70,170)
    SumData[cat_name].Sumw2()
    SumSim[cat_name]=ROOT.TH1D("Sim"+cat_name,"Sim"+cat_name,50,70,170)
    SumSim[cat_name].Sumw2()
    SumSim[cat_name].SetFillColor(ROOT.kRed-7)
    SumZX[cat_name]=ROOT.TH1D("ZX"+cat_name,"ZX"+cat_name,50,70,170)
    SumZX[cat_name].Sumw2()
    SumZX[cat_name].SetFillColor(ROOT.kGreen + 3)
    SumggZZ[cat_name]=ROOT.TH1D("ggZZ"+cat_name,"ggZZ"+cat_name,50,70,170)
    SumggZZ[cat_name].Sumw2()
    SumggZZ[cat_name].SetFillColor(ROOT.kAzure -1)
    SumqqZZ[cat_name]=ROOT.TH1D("qqZZ"+cat_name,"qqZZ"+cat_name,50,70,170)
    SumqqZZ[cat_name].Sumw2()
    SumqqZZ[cat_name].SetFillColor(ROOT.kAzure +6)
    stackBkg[cat_name]=THStack("bkg"+cat_name, "bkg"+cat_name)
    for year in years:
        SumData[cat_name].Add(SumData[cat_name],hitos[year][cat_name]['data'])
        Simhito,GGZZhito = AddHistos(histos[year][cat_name],analyzer_cfg,cat_name)
        SumSim[cat_name].Add(SumSim[cat_name],Simhito)
        SumggZZ[cat_name].Add(SumggZZ[cat_name],GGZZhito)
        SumZX[cat_name].Add(SumZX[cat_name],histos[year][cat_name]['ZX'])
        SumqqZZ[cat_name].Add(SumqqZZ[cat_name],histos[year][cat_name]['ZZTo4L'])
        stacks = MakeStack(histos[year][cat_name],analyzer_cfg,cat_name,Simhito,GGZZhito)
        stackBkg[cat_name].Add(stacks['bkg'])
    legend = ROOT.TLegend(0.65,0.65,0.85,0.85)
    legend.SetNColumns(1)
    legend.SetLineColor(10)
    legend.AddEntry(SumData[cat_name], "data")
    legend.AddEntry(SumSim[cat_name],"H(125)","f")
    legend.AddEntry(SumqqZZ[cat_name],"qq->ZZ","f")
    legend.AddEntry(SumggZZ[cat_name],"gg->ZZ","f")
    legend.AddEntry(SumZX[cat_name],"Z+X","f")
    canv = CreateCanvas(cat_name)
    canv.cd()
    SumData[cat_name].Draw('PE')
    stackBkg[cat_name].Draw('same histo')
    SumData[cat_name].Draw('SAME PE')
    legend.Draw()
    cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
    cms_label.Draw('same')
    lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)' %plt_cfg.lumi)
    lumi_label.Draw('same')
    save_name = "{0:s}RunII".format(cat_name)
    SaveCanvPic(canv, save_dir, save_name)
