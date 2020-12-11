import ROOT

Signal = ROOT.TFile('/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/Data2016_new.root')
t = Signal.Get('passedEvents')
DY = ROOT.TChain("passedEvents")
DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN01.root")
DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN02.root")
#DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_M-10to50_FL01.root")
#qqZZ = ROOT.TFile("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/ZZTo4L_FL02.root")
#qqZZt = qqZZ.Get('passedEvents')

#Z+X
c = ROOT.TCanvas()
def SetDataState(histo):
    histo.GetYaxis().SetTitle("Events / 20 GeV")
    histo.SetMarkerStyle(20)
    histo.SetMarkerColor(ROOT.kBlack)
    histo.SetMarkerSize(1.2)
    histo.SetLineWidth(1)


dataP3F1_4e = ROOT.TH1D("dataP3F1_4e","dataP3F1_4e",40,70,870)
dataP3F1_4e.SetLineColor(ROOT.kRed)
dataP3F1_4mu = ROOT.TH1D("dataP3F1_4mu","dataP3F1_4mu",40,70,870)
dataP3F1_4mu.SetLineColor(ROOT.kRed)
dataP3F1_2e2mu = ROOT.TH1D("dataP3F1_2e2mu","dataP3F1_2e2mu",40,70,870)
dataP3F1_2e2mu.SetLineColor(ROOT.kRed)
dataP3F1_2mu2e = ROOT.TH1D("dataP3F1_2mu2e","dataP3F1_2mu2e",40,70,870)
dataP3F1_2mu2e.SetLineColor(ROOT.kRed)


dataP2F2_4e =ROOT.TH1D("dataP2F2_4e","dataP2F2_4e",40,70,870)
dataP2F2_4e.SetLineColor(ROOT.kBlue)
dataP2F2_4mu =ROOT.TH1D("dataP2F2_4mu","dataP2F2_4mu",40,70,870)
dataP2F2_4mu.SetLineColor(ROOT.kBlue)
dataP2F2_2e2mu =ROOT.TH1D("dataP2F2_2e2mu","dataP2F2_2e2mu",40,70,870)
dataP2F2_2e2mu.SetLineColor(ROOT.kBlue)
dataP2F2_2mu2e =ROOT.TH1D("dataP2F2_2mu2e","dataP2F2_2mu2e",40,70,870)
dataP2F2_2mu2e.SetLineColor(ROOT.kBlue)

MCP3F1_4e = ROOT.TH1D("MCP3F1_4e","MCP3F1_4e",40,70,870)
MCP3F1_4e.SetFillColor(ROOT.kGreen)
MCP3F1_4mu = ROOT.TH1D("MCP3F1_4mu","MCP3F1_4mu",40,70,870)
MCP3F1_4mu.SetFillColor(ROOT.kGreen)
MCP3F1_2e2mu = ROOT.TH1D("MCP3F1_2e2mu","MCP3F1_2e2mu",40,70,870)
MCP3F1_2e2mu.SetFillColor(ROOT.kGreen)
MCP3F1_2mu2e = ROOT.TH1D("MCP3F1_2mu2e","MCP3F1_2mu2e",40,70,870)
MCP3F1_2mu2e.SetFillColor(ROOT.kGreen)

ZZP3F1_4e = ROOT.TH1D("ZZP3F1_4e","ZZP3F1_4e",40,70,870)
ZZP3F1_4e.SetFillColor(ROOT.kCyan-7)
ZZP3F1_4mu = ROOT.TH1D("ZZP3F1_4mu","ZZP3F1_4mu",40,70,870)
ZZP3F1_4mu.SetFillColor(ROOT.kCyan-7)
ZZP3F1_2e2mu = ROOT.TH1D("ZZP3F1_2e2mu","ZZP3F1_2e2mu",40,70,870)
ZZP3F1_2e2mu.SetFillColor(ROOT.kCyan-7)
ZZP3F1_2mu2e = ROOT.TH1D("ZZP3F1_2mu2e","ZZP3F1_2mu2e",40,70,870)
ZZP3F1_2mu2e.SetFillColor(ROOT.kCyan-7)


MCP2F2_4e =ROOT.TH1D("MCP2F2_4e","MCP2F2_4e",40,70,870)
MCP2F2_4e.SetFillColor(ROOT.kGreen)
MCP2F2_4mu =ROOT.TH1D("MCP2F2_4mu","MCP2F2_4mu",40,70,870)
MCP2F2_4mu.SetFillColor(ROOT.kGreen)
MCP2F2_2e2mu =ROOT.TH1D("MCP2F2_2e2mu","MCP2F2_2e2mu",40,70,870)
MCP2F2_2e2mu.SetFillColor(ROOT.kGreen)
MCP2F2_2mu2e =ROOT.TH1D("MCP2F2_2mu2e","MCP2F2_2mu2e",40,70,870)
MCP2F2_2mu2e.SetFillColor(ROOT.kGreen)

idOS = ROOT.TH1D("idOS","idOS",50,-200,200)


# test bin Width
axis = dataP3F1_4e.GetXaxis()
print " bin Width = " + str(axis.GetBinWidth(axis.FindBin(100)))

npassedSS = 0
nfailed = 0
npassedid = 0
for ievent,event in enumerate(t):
    if(not event.passedZXCRSelection): continue
    if(event.lep1_id*event.lep2_id>0 or event.lep3_id*event.lep4_id>0): continue
    if(event.nZXCRFailedLeptons==2):
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==11):
            dataP2F2_4e.Fill(event.lep_4mass)
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==13):
            dataP2F2_4mu.Fill(event.lep_4mass)
        if(abs(event.lep1_id)==abs(event.lep2_id)==11 and abs(event.lep3_id)==abs(event.lep4_id)==13):
            dataP2F2_2e2mu.Fill(event.lep_4mass)
        if(abs(event.lep1_id)==abs(event.lep2_id)==13 and abs(event.lep3_id)==abs(event.lep4_id)==11):
            dataP2F2_2mu2e.Fill(event.lep_4mass)

    if(event.nZXCRFailedLeptons==1):
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==11):
            dataP3F1_4e.Fill(event.lep_4mass)
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==13):
            dataP3F1_4mu.Fill(event.lep_4mass)
        if(abs(event.lep1_id)==abs(event.lep2_id)==11 and abs(event.lep3_id)==abs(event.lep4_id)==13):
            dataP3F1_2e2mu.Fill(event.lep_4mass)
        if(abs(event.lep1_id)==abs(event.lep2_id)==13 and abs(event.lep3_id)==abs(event.lep4_id)==11):
            dataP3F1_2mu2e.Fill(event.lep_4mass)

for ievent,event in enumerate(DY):
    if(not event.passedZXCRSelection): continue
    if(event.lep1_id*event.lep2_id>0 or event.lep3_id*event.lep4_id>0): continue
    if(event.nZXCRFailedLeptons==2):
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==11):
            MCP2F2_4e.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==13):
            MCP2F2_4mu.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)
        if(abs(event.lep1_id)==abs(event.lep2_id)==11 and abs(event.lep3_id)==abs(event.lep4_id)==13):
            MCP2F2_2e2mu.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)
        if(abs(event.lep1_id)==abs(event.lep2_id)==13 and abs(event.lep3_id)==abs(event.lep4_id)==11):
            MCP2F2_2mu2e.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)

    if(event.nZXCRFailedLeptons==1):
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==11):
            MCP3F1_4e.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)
        if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==13):
            MCP3F1_4mu.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)
        if(abs(event.lep1_id)==abs(event.lep2_id)==11 and abs(event.lep3_id)==abs(event.lep4_id)==13):
            MCP3F1_2e2mu.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)
        if(abs(event.lep1_id)==abs(event.lep2_id)==13 and abs(event.lep3_id)==abs(event.lep4_id)==11):
            MCP3F1_2mu2e.Fill(event.lep_4mass,36.5*1000*6104*event.weight/event.cross/81781064.0)

#for ievent,event in enumerate(qqZZt):
#        if(not event.passedZXCRSelection): continue
#        if(event.lep1_id*event.lep2_id>0 or event.lep3_id*event.lep4_id>0): continue
#        if(event.nZXCRFailedLeptons==1):
#            if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==11):
#                ZZP3F1_4e.Fill(event.lep_4mass,35.9*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross)
#            if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==13):
#                ZZP3F1_4mu.Fill(event.lep_4mass,35.9*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross)
#            if(abs(event.lep1_id)==abs(event.lep2_id)==11 and abs(event.lep3_id)==abs(event.lep4_id)==13):
#                ZZP3F1_2e2mu.Fill(event.lep_4mass,35.9*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross)
#            if(abs(event.lep1_id)==abs(event.lep2_id)==13 and abs(event.lep3_id)==abs(event.lep4_id)==11):
#                ZZP3F1_2mu2e.Fill(event.lep_4mass,35.9*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross)



print "nfailed = " + str(nfailed)
print "npassedid = " +str(npassedid)

#stackP3F1_4e = ROOT.THStack("stackP3F1_4e","stackP3F1_4e")
#stackP3F1_4e.Add(MCP3F1_4e)
#stackP3F1_4e.Add(ZZP3F1_4e)

#stackP3F1_4mu = ROOT.THStack("stackP3F1_4mu","stackP3F1_4mu")
#stackP3F1_4mu.Add(MCP3F1_4mu)
#stackP3F1_4mu.Add(ZZP3F1_4mu)

#stackP3F1_2e2mu = ROOT.THStack("stackP3F1_2e2mu","stackP3F1_2e2mu")
#stackP3F1_2e2mu.Add(MCP3F1_2e2mu)
#stackP3F1_2e2mu.Add(ZZP3F1_2e2mu)

#stackP3F1_2mu2e = ROOT.THStack("2mu2e","2mu2e")
#stackP3F1_2mu2e.Add(MCP3F1_2mu2e)
#stackP3F1_2mu2e.Add(ZZP3F1_2mu2e)






#dataP3F1_4e.Draw("E1")
#stackP3F1_4e.Draw("same histo")
#c.SaveAs("plot/dataP3F1CR_4e_OS.png")
#dataP3F1_4mu.Draw("E1")
#stackP3F1_4mu.Draw("same histo")
#c.SaveAs("plot/dataP3F1CR_4mu_OS.png")
#dataP3F1_2e2mu.Draw("E1")
#stackP3F1_2e2mu.Draw("same histo")
#c.SaveAs("plot/dataP3F1CR_2e2mu_OS.png")
#dataP3F1_2mu2e.Draw("E1")
#stackP3F1_2mu2e.Draw("same histo")
#c.SaveAs("plot/dataP3F1CR_2mu2e_OS.png")

dataP2F2_4e.Draw("E1")
MCP2F2_4e.Draw("same histo")
c.SaveAs("plot/dataP2F2CR_4e_OS.png")
dataP2F2_4mu.Draw("E1")
MCP2F2_4mu.Draw("same histo")
c.SaveAs("plot/dataP2F2CR_4mu_OS.png")
dataP2F2_2e2mu.Draw("E1")
MCP2F2_2e2mu.Draw("same histo")
c.SaveAs("plot/dataP2F2CR_2e2mu_OS.png")
dataP2F2_2mu2e.Draw("E1")
MCP2F2_2mu2e.Draw("same histo")
c.SaveAs("plot/dataP2F2CR_2mu2e_OS.png")
