import ROOT

Signal = ROOT.TFile('/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/2016_noDuplicates.root')
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
    nlep = event.lep_pt.size()
    if(not event.passedZXCRSelection): continue
    if(event.nZXCRFailedLeptons==1):
        for i in range(nlep):
            if( abs(event.lep_id[event.lep_Hindex[0]]) == abs(event.lep_id[event.lep_Hindex[1]]) == abs(event.lep_id[event.lep_Hindex[2]]) == abs(event.lep_id[event.lep_Hindex[3]]) == 11 ):
                l1FSR = ROOT.TLorentzVector()
                l2FSR = ROOT.TLorentzVector()
                l3FSR = ROOT.TLorentzVector()
                l4FSR = ROOT.TLorentzVector()
                l1FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
                l2FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
                l3FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[2]])
                l4FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[3]],event.lepFSR_eta[event.lep_Hindex[3]],event.lepFSR_phi[event.lep_Hindex[3]],event.lepFSR_mass[event.lep_Hindex[3]])
                H4massFSR = ROOT.TLorentzVector()
                H4massFSR = l1FSR+l2FSR+l3FSR+l4FSR
                dataP3F1_4e.Fill(H4massFSR.M())
                dataP3F1_4mu.Fill(event.mass4l)
#               data.dataP3F1_2e2mu.Fill(event.H_FSR)
#            if(abs(event.lep_id[event.lep_Hindex[0]]) == abs(event.lep_id[event.lep_Hindex[1]]) == abs(event.lep_id[event.lep_Hindex[2]]) == abs(event.lep_id[event.lep_Hindex[3]]) == 13):
#                dataP3F1_4mu.Fill(event.mass4l)

    if(event.nZXCRFailedLeptons==2):
        for i in range(nlep):
            if( abs(event.lep_id[event.lep_Hindex[0]]) == abs(event.lep_id[event.lep_Hindex[1]]) == abs(event.lep_id[event.lep_Hindex[2]]) == abs(event.lep_id[event.lep_Hindex[3]]) == 11 ):
                l1FSR = ROOT.TLorentzVector()
                l2FSR = ROOT.TLorentzVector()
                l3FSR = ROOT.TLorentzVector()
                l4FSR = ROOT.TLorentzVector()
                l1FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
                l2FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
                l3FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[2]])
                l4FSR.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[3]],event.lepFSR_eta[event.lep_Hindex[3]],event.lepFSR_phi[event.lep_Hindex[3]],event.lepFSR_mass[event.lep_Hindex[3]])
                H4massFSR = ROOT.TLorentzVector()
                H4massFSR = l1FSR+l2FSR+l3FSR+l4FSR
                dataP2F2_4e.Fill(H4massFSR.M())

#for ievent,event in enumerate(DY):
#    if(not event.passedZXCRSelection): continue
#    if(event.nZXCRFailedLeptons==1):
#        if(abs(lep1_id) == abs(lep2_id) == abs(lep3_id) == abs(lep4_id) == 11):
#            DY.Fill(H_FSR,35.6*1000*6104*event.weight/event.cross)

dataP3F1_4e.Draw()
c.SaveAs("dataP3F1CR_4e.png")
dataP3F1_4mu.Draw()
c.SaveAs("dataP3F1CR_4mu.png")
dataP2F2_4e.Draw()
c.SaveAs("dataP2F2CR_4e.png")




#    nZX.Fill(event.nZXCRFailedLeptons)
#    ZX1.Fill(event.lep_RelIsoNoFSR1)
#    ZX2.Fill(event.lep_RelIsoNoFSR2)
#    ZX3.Fill(event.lep_RelIsoNoFSR3)
#    ZX4.Fill(event.lep_RelIsoNoFSR4)

#ZX1.Draw()
#ZX2.Draw("same")
#ZX3.Draw("same")
#ZX4.Draw("same")
#c.SaveAs("ZX01.png")

#nZX.Draw()
#c.SaveAs("passedZXCR.png")
