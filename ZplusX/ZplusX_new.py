import ROOT

Signal = ROOT.TFile('/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/Data2016_new.root')
t = Signal.Get('passedEvents')
DY = ROOT.TChain("passedEvents")
DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN01.root")
DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN02.root")

#Z+X
c = ROOT.TCanvas()


dataP3F1_4e = ROOT.TH1D("dataP3F1_4e","dataP3F1_4e",41,60,880)
dataP3F1_4e.SetLineColor(ROOT.kRed)
dataP3F1_4mu = ROOT.TH1D("dataP3F1_4mu","dataP3F1_4mu",41,60,880)
dataP3F1_4mu.SetLineColor(ROOT.kRed)
dataP3F1_2e2mu = ROOT.TH1D("dataP3F1_2e2mu","dataP3F1_2e2mu",41,60,880)
dataP3F1_2e2mu.SetLineColor(ROOT.kRed)
dataP3F1_2mu2e = ROOT.TH1D("dataP3F1_2mu2e","dataP3F1_2mu2e",41,60,880)
dataP3F1_2mu2e.SetLineColor(ROOT.kRed)


dataP2F2_4e =ROOT.TH1D("dataP2F2_4e","dataP2F2_4e",41,60,880)
dataP2F2_4e.SetLineColor(ROOT.kBlue)
dataP2F2_4mu =ROOT.TH1D("dataP2F2_4mu","dataP2F2_4mu",41,60,880)
dataP2F2_4e.SetLineColor(ROOT.kBlue)
dataP2F2_2e2mu =ROOT.TH1D("dataP2F2_2e2mu","dataP2F2_2e2mu",41,60,880)
dataP2F2_2e2mu.SetLineColor(ROOT.kBlue)
dataP2F2_2mu2e =ROOT.TH1D("dataP2F2_2mu2e","dataP2F2_2mu2e",41,60,880)
dataP2F2_2mu2e.SetLineColor(ROOT.kBlue)

Zjet = ROOT.TH1D("Zjet","Zjet",41,60,880)


# test bin Width
axis = dataP3F1_4e.GetXaxis()
print " bin Width = " + str(axis.GetBinWidth(axis.FindBin(100)))


for ievent,event in enumerate(t):
    if(not event.passedZXCRSelection): continue
    if(event.nZXCRFailedLeptons==2):
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==11):
            dataP2F2_4e.Fill(event.H_FSR)

dataP3F1_4e.Draw()
c.SaveAs("P3F2_4e.png")
