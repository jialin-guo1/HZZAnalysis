#!/usr/bin/env python
import ROOT
from array import array

ROOT.gStyle.SetOptStat(False)

# input file and get tree
ggTozz2e2u16 = ROOT.TChain("passedEvents")
ggTozz2e2u16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/GluGluToContinToZZTo2e2mu_FL01.root")
ggTozz2e2u17 = ROOT.TChain("passedEvents")
ggTozz2e2u17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/GluGluToContinToZZTo2e2mu_CN01.root")
ggTozz2e2u18 = ROOT.TChain("passedEvents")
ggTozz2e2u18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/GluGluToContinToZZTo2e2mu_FL01.root")

ggTozz2u2t16 = ROOT.TChain("passedEvents")
ggTozz2u2t16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/GluGluToContinToZZTo2mu2tau_FL02.root")
ggTozz2u2t17 = ROOT.TChain("passedEvents")
ggTozz2u2t17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/GluGluToContinToZZTo2mu2tau_CN01.root")
ggTozz2u2t18 = ROOT.TChain("passedEvents")
ggTozz2u2t18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/GluGluToContinToZZTo2mu2tau_CN01.root")

ggTozz2e2t16 = ROOT.TChain("passedEvents")
ggTozz2e2t16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/GluGluToContinToZZTo2e2tau_FL01.root")
ggTozz2e2t17 = ROOT.TChain("passedEvents")
ggTozz2e2t17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/GluGluToContinToZZTo2e2tau_CN01.root")
ggTozz2e2t18 = ROOT.TChain("passedEvents")
ggTozz2e2t18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/GluGluToContinToZZTo2e2tau_CN01.root")

ggTozz4e16 = ROOT.TChain("passedEvents")
ggTozz4e16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/GluGluToContinToZZTo4e_FL01.root")
ggTozz4e17 = ROOT.TChain("passedEvents")
ggTozz4e17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/GluGluToContinToZZTo4e_CN01.root")
ggTozz4e18 = ROOT.TChain("passedEvents")
ggTozz4e18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/GluGluToContinToZZTo4e_CN01.root")

ggTozz4u16 = ROOT.TChain("passedEvents")
ggTozz4u16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/GluGluToContinToZZTo4mu_FL02.root")
ggTozz4u17 = ROOT.TChain("passedEvents")
ggTozz4u17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/GluGluToContinToZZTo4mu_CN01.root")
ggTozz4u18 = ROOT.TChain("passedEvents")
ggTozz4u18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/GluGluToContinToZZTo4mu_CN01.root")

ggTozz4t16 = ROOT.TChain("passedEvents")
ggTozz4t16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/GluGluToContinToZZTo4tau_FL01.root")
ggTozz4t17 = ROOT.TChain("passedEvents")
ggTozz4t17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/GluGluToContinToZZTo4tau_CN01.root")
ggTozz4t18 = ROOT.TChain("passedEvents")
ggTozz4t18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/GluGluToContinToZZTo4tau_CN01.root")

qqTozz16 = ROOT.TChain("passedEvents")
#qqTozz.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/ZZTo4L_FL04.root")
#qqTozz.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/ZZTo4L_FL02.root")
qqTozz16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/ZZTo4L_FLALL.root")
qqTozz17 = ROOT.TChain("passedEvents")
qqTozz17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/ZZTo4L_FL01.root")
qqTozz18 = ROOT.TChain("passedEvents")
qqTozz18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/ZZTo4L_CN01.root")

#qqTozz0 = ROOT.TChain("passedEvents")
#qqTozz0.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/ZZTo4L_FL02.root")

DataSim_gg16 = ROOT.TChain("passedEvents")
DataSim_gg16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/GluGluHToZZTo4L*.root")
DataSim_gg17 = ROOT.TChain("passedEvents")
DataSim_gg17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/GluGluHToZZTo4L_CN01.root")
DataSim_gg18 = ROOT.TChain("passedEvents")
DataSim_gg18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/GluGluHToZZTo4L_CN01.root")

DataSim_qq16 = ROOT.TChain("passedEvents")
DataSim_qq16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/VBF_HToZZTo4L*.root")
DataSim_qq17 = ROOT.TChain("passedEvents")
DataSim_qq17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/VBF_HToZZTo4L_CN01.root")
DataSim_qq18 = ROOT.TChain("passedEvents")
DataSim_qq18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/VBF_HToZZTo4L_CN01.root")

DataSim_WplusH16 = ROOT.TChain("passedEvents")
DataSim_WplusH16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/WplusH*.root")
DataSim_WplusH17 = ROOT.TChain("passedEvents")
DataSim_WplusH17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/WplusH_HToZZTo4L_CN01.root")
DataSim_WplusH18 = ROOT.TChain("passedEvents")
DataSim_WplusH18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/WplusH_HToZZTo4L_CN01.root")

DataSim_WminH16 = ROOT.TChain("passedEvents")
DataSim_WminH16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/WminusH*.root")
DataSim_WminH17 = ROOT.TChain("passedEvents")
DataSim_WminH17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/WminusH_HToZZTo4L_CN01.root")
DataSim_WminH18 = ROOT.TChain("passedEvents")
DataSim_WminH18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/WminusH_HToZZTo4L_CN01.root")


DataSim_ZH16 = ROOT.TChain("passedEvents")
DataSim_ZH16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/ZH_HToZZ*.root")
DataSim_ZH17 = ROOT.TChain("passedEvents")
DataSim_ZH17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/ZH_HToZZ_4L_CN01.root")
DataSim_ZH18 = ROOT.TChain("passedEvents")
DataSim_ZH18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/ZH_HToZZ_4L_CN01.root")

DataSim_ttH16 = ROOT.TChain("passedEvents")
DataSim_ttH16.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC1/ZH_HToZZ*.root")
DataSim_ttH17 = ROOT.TChain("passedEvents")
DataSim_ttH17.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/MC/ttH_HToZZ_CN01.root")
DataSim_ttH18 = ROOT.TChain("passedEvents")
DataSim_ttH18.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/MC/ttH_HToZZ_CN01.root")


#Signal = ROOT.TFile('/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/2016_allsignal_new.root')
#t = Signal.Get('passedEvents')
t = ROOT.TChain("passedEvents")
t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/2016_noDuplicates_new.root")
t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/2017_noDuplicates_new.root")
t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/2018_noDuplicates_new.root")

# book histogram and canvas
c = ROOT.TCanvas()
gg2e2u16 = ROOT.TH1D("gg->ggTozz2e2u6","Backgrund(2016)",50,70,170)
gg2e2u16.SetFillColor(ROOT.kBlue)
gg2e2u16.GetYaxis().SetTitle("Events / 2 GeV")
gg2e2u17 = ROOT.TH1D("gg->ggTozz2e2u7","Backgrund(2016)",50,70,170)
gg2e2u17.SetFillColor(ROOT.kBlue)
gg2e2u17.GetYaxis().SetTitle("Events / 2 GeV")
gg2e2u18 = ROOT.TH1D("gg->ggTozz2e2u8","Backgrund(2016)",50,70,170)
gg2e2u18.SetFillColor(ROOT.kBlue)
gg2e2u18.GetYaxis().SetTitle("Events / 2 GeV")

gg2u2t16 = ROOT.TH1D("gg->ggTozz2u2t6","Backgrund(2016)",50,70,170)
gg2u2t16.SetFillColor(ROOT.kBlue)
gg2u2t16.GetYaxis().SetTitle("Events / 2 GeV")
gg2u2t17 = ROOT.TH1D("gg->ggTozz2u2t7","Backgrund(2016)",50,70,170)
gg2u2t17.SetFillColor(ROOT.kBlue)
gg2u2t17.GetYaxis().SetTitle("Events / 2 GeV")
gg2u2t18 = ROOT.TH1D("gg->ggTozz2u2t8","Backgrund(2016)",50,70,170)
gg2u2t18.SetFillColor(ROOT.kBlue)
gg2u2t18.GetYaxis().SetTitle("Events / 2 GeV")

gg2e2t16 = ROOT.TH1D("gg->ggTozz2e2t6","Backgrund(2016)",50,70,170)
gg2e2t16.SetFillColor(ROOT.kBlue)
gg2e2t16.GetYaxis().SetTitle("Events / 2 GeV")
gg2e2t17 = ROOT.TH1D("gg->ggTozz2e2t7","Backgrund(2016)",50,70,170)
gg2e2t17.SetFillColor(ROOT.kBlue)
gg2e2t17.GetYaxis().SetTitle("Events / 2 GeV")
gg2e2t18 = ROOT.TH1D("gg->ggTozz2e2t8","Backgrund(2016)",50,70,170)
gg2e2t18.SetFillColor(ROOT.kBlue)
gg2e2t18.GetYaxis().SetTitle("Events / 2 GeV")

gg4e16 = ROOT.TH1D("gg->ggTozz4e6","Backgrund(2016)",50,70,170)
gg4e16.SetFillColor(ROOT.kBlue)
gg4e16.GetYaxis().SetTitle("Events / 2 GeV")
gg4e17 = ROOT.TH1D("gg->ggTozz4e7","Backgrund(2016)",50,70,170)
gg4e17.SetFillColor(ROOT.kBlue)
gg4e17.GetYaxis().SetTitle("Events / 2 GeV")
gg4e18 = ROOT.TH1D("gg->ggTozz4e8","Backgrund(2016)",50,70,170)
gg4e18.SetFillColor(ROOT.kBlue)
gg4e18.GetYaxis().SetTitle("Events / 2 GeV")

gg4u16 = ROOT.TH1D("gg->ggTozz4u6","Backgrund(2016)",50,70,170)
gg4u16.SetFillColor(ROOT.kBlue)
gg4u16.GetYaxis().SetTitle("Events / 2 GeV")
gg4u17 = ROOT.TH1D("gg->ggTozz4u7","Backgrund(2016)",50,70,170)
gg4u17.SetFillColor(ROOT.kBlue)
gg4u17.GetYaxis().SetTitle("Events / 2 GeV")
gg4u18 = ROOT.TH1D("gg->ggTozz4u8","Backgrund(2016)",50,70,170)
gg4u18.SetFillColor(ROOT.kBlue)
gg4u18.GetYaxis().SetTitle("Events / 2 GeV")

gg4t16 = ROOT.TH1D("gg->ggTozz4t6","Backgrund(2016)",50,70,170)
gg4t16.SetFillColor(ROOT.kBlue)
gg4t16.GetYaxis().SetTitle("Events / 2 GeV")
gg4t17 = ROOT.TH1D("gg->ggTozz4t7","Backgrund(2016)",50,70,170)
gg4t17.SetFillColor(ROOT.kBlue)
gg4t17.GetYaxis().SetTitle("Events / 2 GeV")
gg4t18 = ROOT.TH1D("gg->ggTozz4t8","Backgrund(2016)",50,70,170)
gg4t18.SetFillColor(ROOT.kBlue)
gg4t18.GetYaxis().SetTitle("Events / 2 GeV")

qq16 = ROOT.TH1D("qq->zz16","Backgrund(2016)",50,70,170)
qq16.SetFillColor(7)
qq16.GetYaxis().SetTitle("Events / 2 GeV")
qq17 = ROOT.TH1D("qq->zz17","Backgrund(2016)",50,70,170)
qq17.SetFillColor(7)
qq17.GetYaxis().SetTitle("Events / 2 GeV")
qq18 = ROOT.TH1D("qq->zz18","Backgrund(2016)",50,70,170)
qq18.SetFillColor(7)
qq18.GetYaxis().SetTitle("Events / 2 GeV")

#qq0 = ROOT.TH1D("qq->zz0","Backgrund(2016)",50,70,170)
#qq0.SetFillColor(7)
#qq0.GetYaxis().SetTitle("Events / 2 GeV")

Sim_gg16 = ROOT.TH1D("Sim_gg16","Backgrund(2016)",50,70,170)
Sim_gg16.SetFillColor(ROOT.kRed)
Sim_gg16.GetYaxis().SetTitle("Events / 2 GeV")
Sim_gg17 = ROOT.TH1D("Sim_gg17","Backgrund(2016)",50,70,170)
Sim_gg17.SetFillColor(ROOT.kRed)
Sim_gg17.GetYaxis().SetTitle("Events / 2 GeV")
Sim_gg18 = ROOT.TH1D("Sim_gg18","Backgrund(2016)",50,70,170)
Sim_gg18.SetFillColor(ROOT.kRed)
Sim_gg18.GetYaxis().SetTitle("Events / 2 GeV")

Sim_qq16 = ROOT.TH1D("Sim_qq16","Backgrund(2016)",50,70,170)
Sim_qq16.SetFillColor(ROOT.kRed)
Sim_qq16.GetYaxis().SetTitle("Events / 2 GeV")
Sim_qq17 = ROOT.TH1D("Sim_qq17","Backgrund(2016)",50,70,170)
Sim_qq17.SetFillColor(ROOT.kRed)
Sim_qq17.GetYaxis().SetTitle("Events / 2 GeV")
Sim_qq18 = ROOT.TH1D("Sim_qq18","Backgrund(2016)",50,70,170)
Sim_qq18.SetFillColor(ROOT.kRed)
Sim_qq18.GetYaxis().SetTitle("Events / 2 GeV")

Sim_WplusH16 = ROOT.TH1D("Sim_WplusH16","Backgrund(2016)",50,70,170)
Sim_WplusH16.SetFillColor(ROOT.kRed)
Sim_WplusH16.GetYaxis().SetTitle("Events / 2 GeV")
Sim_WplusH17 = ROOT.TH1D("Sim_WplusH17","Backgrund(2016)",50,70,170)
Sim_WplusH17.SetFillColor(ROOT.kRed)
Sim_WplusH17.GetYaxis().SetTitle("Events / 2 GeV")
Sim_WplusH18 = ROOT.TH1D("Sim_WplusH18","Backgrund(2016)",50,70,170)
Sim_WplusH18.SetFillColor(ROOT.kRed)
Sim_WplusH18.GetYaxis().SetTitle("Events / 2 GeV")

Sim_WminH16 = ROOT.TH1D("Sim_WminH16","Backgrund(2016)",50,70,170)
Sim_WminH16.SetFillColor(ROOT.kRed)
Sim_WminH16.GetYaxis().SetTitle("Events / 2 GeV")
Sim_WminH17 = ROOT.TH1D("Sim_WminH17","Backgrund(2016)",50,70,170)
Sim_WminH17.SetFillColor(ROOT.kRed)
Sim_WminH17.GetYaxis().SetTitle("Events / 2 GeV")
Sim_WminH18 = ROOT.TH1D("Sim_WminH18","Backgrund(2016)",50,70,170)
Sim_WminH18.SetFillColor(ROOT.kRed)
Sim_WminH18.GetYaxis().SetTitle("Events / 2 GeV")

Sim_ttH16 = ROOT.TH1D("Sim_ttH16","Backgrund(2016)",50,70,170)
Sim_ttH16.SetFillColor(ROOT.kRed)
Sim_ttH16.GetYaxis().SetTitle("Events / 2 GeV")
Sim_ttH17 = ROOT.TH1D("Sim_ttH17","Backgrund(2016)",50,70,170)
Sim_ttH17.SetFillColor(ROOT.kRed)
Sim_ttH17.GetYaxis().SetTitle("Events / 2 GeV")
Sim_ttH18 = ROOT.TH1D("Sim_ttH18","Backgrund(2016)",50,70,170)
Sim_ttH18.SetFillColor(ROOT.kRed)
Sim_ttH18.GetYaxis().SetTitle("Events / 2 GeV")

Sim_ZH16 = ROOT.TH1D("Sim_ZH16","Backgrund(2016)",50,70,170)
Sim_ZH16.SetFillColor(ROOT.kRed)
Sim_ZH16.GetYaxis().SetTitle("Events / 2 GeV")
Sim_ZH17 = ROOT.TH1D("Sim_ZH17","Backgrund(2016)",50,70,170)
Sim_ZH17.SetFillColor(ROOT.kRed)
Sim_ZH17.GetYaxis().SetTitle("Events / 2 GeV")
Sim_ZH18 = ROOT.TH1D("Sim_ZH18","Backgrund(2016)",50,70,170)
Sim_ZH18.SetFillColor(ROOT.kRed)
Sim_ZH18.GetYaxis().SetTitle("Events / 2 GeV")


#Data = ROOT.TH1D("Data","Data(2016)",50,70,170)
Data = ROOT.TH1D("Data","result(RuII)",50,70,170)
Data.GetYaxis().SetTitle("Events / 2 GeV")
Data.SetMarkerStyle(20)
Data.SetMarkerColor(ROOT.kBlack)
Data.SetMarkerSize(1.2)
Data.SetLineColor(ROOT.kBlack)
Data.SetLineWidth(1)
#Data.SetStats(ROOT.kFALSE)


#Loop over all the events and fill histogram
for ievent,event in enumerate(ggTozz2e2u16):
    gg2e2u16.Fill(event.H_FSR,35.9*1000*0.0039*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz2e2u17):
    gg2e2u17.Fill(event.H_FSR,41.5*1000*0.0039*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz2e2u18):
    gg2e2u18.Fill(event.H_FSR,59.7*1000*0.0039*event.weight*event.k_gg/event.cross)

for ievent,event in enumerate(ggTozz2e2t16):
    gg2e2t16.Fill(event.H_FSR,35.9*1000*0.00319*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz2e2t17):
    gg2e2t17.Fill(event.H_FSR,41.5*1000*0.00319*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz2e2t18):
    gg2e2t18.Fill(event.H_FSR,59.7*1000*0.00319*event.weight*event.k_gg/event.cross)


for ievent,event in enumerate(ggTozz2u2t16):
    gg2u2t16.Fill(event.H_FSR,35.9*1000*0.00319*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz2u2t17):
    gg2u2t17.Fill(event.H_FSR,41.5*1000*0.00319*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz2u2t18):
    gg2u2t18.Fill(event.H_FSR,59.7*1000*0.00319*event.weight*event.k_gg/event.cross)

for ievent,event in enumerate(ggTozz4e16):
    gg4e16.Fill(event.H_FSR,35.9*1000*0.00159*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz4e17):
    gg4e17.Fill(event.H_FSR,41.5*1000*0.00159*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz4e18):
    gg4e18.Fill(event.H_FSR,59.7*1000*0.00159*event.weight*event.k_gg/event.cross)

for ievent,event in enumerate(ggTozz4u16):
    gg4u16.Fill(event.H_FSR,35.9*1000*0.00159*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz4u17):
    gg4u17.Fill(event.H_FSR,41.5*1000*0.00159*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz4u18):
    gg4u18.Fill(event.H_FSR,59.7*1000*0.00159*event.weight*event.k_gg/event.cross)

for ievent,event in enumerate(ggTozz4t16):
    gg4t16.Fill(event.H_FSR,35.9*1000*0.00159*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz4t17):
    gg4t17.Fill(event.H_FSR,41.5*1000*0.00159*event.weight*event.k_gg/event.cross)
for ievent,event in enumerate(ggTozz4t18):
    gg4t18.Fill(event.H_FSR,59.7*1000*0.00159*event.weight*event.k_gg/event.cross)

for ievent,event in enumerate(qqTozz16):
    qq16.Fill(event.H_FSR,35.9*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross)
for ievent,event in enumerate(qqTozz17):
    qq17.Fill(event.H_FSR,41.5*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross)
for ievent,event in enumerate(qqTozz18):
    qq18.Fill(event.H_FSR,59.7*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross)

#for ievent,event in enumerate(qqTozz0):
#    qq0.Fill(event.H_FSR,35.9*1000*event.weight*event.k_qq_qcd_M*event.k_qq_ewk)

for ievent,event in enumerate(DataSim_gg16):
    Sim_gg16.Fill(event.H_FSR,35.9*12.31*event.weight/event.cross)
for ievent,event in enumerate(DataSim_gg17):
    Sim_gg17.Fill(event.H_FSR,41.5*12.31*event.weight/event.cross)
for ievent,event in enumerate(DataSim_gg18):
    Sim_gg18.Fill(event.H_FSR,59.7*12.31*event.weight/event.cross)

for ievent,event in enumerate(DataSim_qq16):
    Sim_qq16.Fill(event.H_FSR,35.9*1.044*event.weight/event.cross)
for ievent,event in enumerate(DataSim_qq17):
    Sim_qq17.Fill(event.H_FSR,41.5*1.044*event.weight/event.cross)
for ievent,event in enumerate(DataSim_qq18):
    Sim_qq18.Fill(event.H_FSR,59.7*1.044*event.weight/event.cross)

for ievent,event in enumerate(DataSim_WplusH16):
    Sim_WplusH16.Fill(event.H_FSR,35.9*0.232*event.weight/event.cross)
for ievent,event in enumerate(DataSim_WplusH17):
    Sim_WplusH17.Fill(event.H_FSR,41.5*0.232*event.weight/event.cross)
for ievent,event in enumerate(DataSim_WplusH18):
    Sim_WplusH18.Fill(event.H_FSR,59.7*0.232*event.weight/event.cross)

for ievent,event in enumerate(DataSim_WminH16):
    Sim_WminH16.Fill(event.H_FSR,35.9*0.147*event.weight/event.cross)
for ievent,event in enumerate(DataSim_WminH17):
    Sim_WminH17.Fill(event.H_FSR,41.5*0.147*event.weight/event.cross)
for ievent,event in enumerate(DataSim_WminH18):
    Sim_WminH18.Fill(event.H_FSR,59.7*0.147*event.weight/event.cross)

for ievent,event in enumerate(DataSim_ZH16):
    Sim_ZH16.Fill(event.H_FSR,35.9*0.668*event.weight/event.cross)
for ievent,event in enumerate(DataSim_ZH17):
    Sim_ZH17.Fill(event.H_FSR,41.5*0.668*event.weight/event.cross)
for ievent,event in enumerate(DataSim_ZH18):
    Sim_ZH18.Fill(event.H_FSR,59.7*0.668*event.weight/event.cross)

for ievent,event in enumerate(DataSim_ttH16):
    Sim_ttH16.Fill(event.H_FSR,35.9*0.393*event.weight/event.cross)
for ievent,event in enumerate(DataSim_ttH17):
    Sim_ttH17.Fill(event.H_FSR,41.5*0.393*event.weight/event.cross)
for ievent,event in enumerate(DataSim_ttH18):
    Sim_ttH18.Fill(event.H_FSR,56.7*0.393*event.weight/event.cross)

for ievent,event in enumerate(t):
    Data.Fill(event.H_FSR)




#normal
#gg.Scale(35.9*1000*0.00637)
#qq.Scale(35.9*1000*2.468)
#Sim_gg.Scale(35.9*12.18)
#Sim_qq.Scale(35.9*1.044)

Sim = ROOT.TH1D("Sim","Backgrund(2016)",50,70,170)
Sim.SetFillColor(ROOT.kRed)
Sim.Sumw2()
Sim.Add(Sim_gg16,Sim_qq16)
Sim.Add(Sim,Sim_ZH16)
Sim.Add(Sim,Sim_WplusH16)
Sim.Add(Sim,Sim_WminH16)
Sim.Add(Sim,Sim_ttH16)
Sim.Add(Sim,Sim_gg17)
Sim.Add(Sim,Sim_qq17)
Sim.Add(Sim,Sim_ZH17)
Sim.Add(Sim,Sim_WplusH17)
Sim.Add(Sim,Sim_WminH17)
Sim.Add(Sim,Sim_ttH17)
Sim.Add(Sim,Sim_qq18)
Sim.Add(Sim,Sim_gg18)
Sim.Add(Sim,Sim_ZH18)
Sim.Add(Sim,Sim_WplusH18)
Sim.Add(Sim,Sim_WminH18)
Sim.Add(Sim,Sim_ttH18)

Data.Draw("E1")
Sim.Draw("same hito")
c.SaveAs("Sum.png")

ggSum = ROOT.TH1D("ggSum","Backgrund(2016)",50,70,170)
ggSum.SetFillColor(ROOT.kBlue)
ggSum.Sumw2()
ggSum.Add(gg2e2u16,gg2u2t16)
ggSum.Add(ggSum,gg2e2t16)
ggSum.Add(ggSum,gg4e16)
ggSum.Add(ggSum,gg4u16)
ggSum.Add(ggSum,gg4t16)
ggSum.Add(ggSum,gg2e2t17)
ggSum.Add(ggSum,gg2e2u17)
ggSum.Add(ggSum,gg2u2t17)
ggSum.Add(ggSum,gg4e17)
ggSum.Add(ggSum,gg4u17)
ggSum.Add(ggSum,gg4t17)
ggSum.Add(ggSum,gg2e2t18)
ggSum.Add(ggSum,gg2e2u18)
ggSum.Add(ggSum,gg2u2t18)
ggSum.Add(ggSum,gg4e18)
ggSum.Add(ggSum,gg4u18)
ggSum.Add(ggSum,gg4t18)

qqSum = ROOT.TH1D("qqSum","Backgrund(2016)",50,70,170)
qqSum.SetFillColor(7)
qqSum.Add(qq16,qq17)
qqSum.Add(qqSum,qq18)



#qqSum = ROOT.TH1D("qqSum","Backgrund(2016)",50,70,170)
#qqSum.SetFillColor(7)
#qqSum.Sumw2()
#qqSum.Add(qq,qq0)

print "number of all MC = " + str(Sim.Integral())


# set leg
leg = ROOT.TLegend(0.7, 0.7, 0.85, 0.85)
leg.AddEntry(Data,"Data","PE1")
leg.AddEntry(ggSum,"gg->zz","f")
leg.AddEntry(qqSum,"qq->zz","f")
leg.AddEntry(Sim,"H(125)","f")
leg.SetTextSize(0.038)
leg.SetFillColor(10)
leg.SetLineColor(10)


#set histo and drew
Data.Draw("E1")
hstack = ROOT.THStack("hstack","2016reuslt")
hstack.Add(ggSum)
hstack.Add(qqSum)
hstack.Add(Sim)
#hstack.Add(Sim_gg)
#hstack.Add(Sim_qq)
#hstack.Add(Sim_ZH)
#hstack.Add(Sim_ttH)
#hstack.Add(Sim_WminH)
#hstack.Add(Sim_WplusH)
hstack.Draw("same histo")
#Sim.Draw("same histo")
#qq.Draw("same histo")
#ggSum.Draw("same histo")
leg.Draw()
Data.Draw("same")
c.SaveAs("resultRunII.png")

#qq.Draw("histo")
#Data.Draw("same E1")
#c.SaveAs("qqZZ.png")
