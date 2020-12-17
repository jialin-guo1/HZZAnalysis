import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *

Signal = ROOT.TFile('/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/Data2018_new.root')
t = Signal.Get('passedEvents')
#DY = ROOT.TChain("passedEvents")
#DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN01.root")
#DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN02.root")



data4e = ROOT.TH1D("data4e","data4e",40,70,870)
data4mu = ROOT.TH1D("data4mu","data4mu",40,70,870)
data2e2mu = ROOT.TH1D("data2e2mu","data2e2mu",40,70,870)
data2mu2e = ROOT.TH1D("data2mu2e","data2mu2e",40,70,870)

c = ROOT.TCanvas()

for ievent,event in enumerate(t):
    if(event.passedSSCRSelection):
        data4e.Fill(event.SS4e)


data4e.Draw()
c.SaveAs("SS4e.png")
