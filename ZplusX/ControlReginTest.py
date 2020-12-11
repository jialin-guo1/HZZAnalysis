import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *

Signal = ROOT.TFile('/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/2018_noDuplicates.root')
t = Signal.Get('passedEvents')
#DY = ROOT.TChain("passedEvents")
#DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN01.root")
#DY.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/MC/DYJetsToLL_CN02.root")


data4e = ROOT.TH1D("data4mu","data4mu",40,70,870)

lep_leadingPt = ROOT.TH1D("lep_leadingPt","lep_leadingPt",50,30,100)
lep_leadingPt.SetLineColor(ROOT.kRed)
lep_subleadingPt = ROOT.TH1D("lep_subleadingPt","lep_subleadingPt",50,10,100)
lep_subleadingPt.SetLineColor(ROOT.kBlue)

Zm = ROOT.TH1D("Zmass","Zmass",40,40,120)
ZlepCharge = ROOT.TH1D("ZlepCharge","ZlepCharge",40,-200,200)
ZlepCharge.SetLineColor(ROOT.kRed)
SSlepcharg = ROOT.TH1D("SSlepcharg","SSlepcharg",40,-200,200)
SSlepcharg.SetLineColor(ROOT.kBlue)

c = ROOT.TCanvas()

nindexpair = 0
npassedid  = 0
npassedpt = 0
npassedDR = 0
npassedM2l = 0
npassedios = 0
npassedtight = 0
npassedMwindow = 0
npassed4e = 0
for ievent,event in enumerate(t):

    passedSSCRselection = False
    n_Zs = 0
    Z_pt = []
    Z_eta = []
    Z_phi = []
    Z_mass = []
    Z_lepindex1 = []
    Z_lepindex2 = []
    lep_index = [0,0,0,0]

    Zmass = 91.1876
    minZ1DeltaM = 99999.99
    Nlep = event.lep_pt.size()

    # make all Z candidates including any FSR photons,
    for i in range(Nlep):
        for j in range(i+1,Nlep):
            lifsr = ROOT.TLorentzVector()
            ljfsr = ROOT.TLorentzVector()
            lifsr.SetPtEtaPhiM(event.lepFSR_pt[i], event.lepFSR_eta[i], event.lepFSR_phi[i], event.lepFSR_mass[i])
            ljfsr.SetPtEtaPhiM(event.lepFSR_pt[j], event.lepFSR_eta[j], event.lepFSR_phi[j], event.lepFSR_mass[j])
            Z = ROOT.TLorentzVector()
            Z = (lifsr + ljfsr)
            if(Z.M()>0):
                n_Zs = n_Zs + 1
                Z_pt.append(Z.Pt())
                Z_eta.append(Z.Eta())
                Z_phi.append(Z.Phi())
                Z_mass.append(Z.M())
                Z_lepindex1.append(i)
                Z_lepindex2.append(j)

    # consider all Z and same sign cnadidate
    for i in range(n_Zs):
        for j in range(i+1,n_Zs):
            i1 = Z_lepindex1[i]
            i2 = Z_lepindex2[i]
            j1 = Z_lepindex1[j]
            j2 = Z_lepindex2[j]
            if(i1 == j1 or i1==j2 or i2==j1 or i2==j2): continue
            nindexpair += 1
            # opposite sign and same flavour for Z ; same sign same flavour for fack leptons
            if(event.lep_id[i1]+event.lep_id[i2]!=0 or event.lep_id[j1]*event.lep_id[j2]<0 or abs(event.lep_id[j1])!=abs(event.lep_id[j2])): continue
            npassedid += 1
            lep1 = ROOT.TLorentzVector()
            lep2 = ROOT.TLorentzVector()
            lep3 = ROOT.TLorentzVector()
            lep4 = ROOT.TLorentzVector()
            lep1.SetPtEtaPhiM(event.lepFSR_pt[i1],event.lepFSR_eta[i1],event.lepFSR_phi[i1],event.lepFSR_mass[i1])
            lep2.SetPtEtaPhiM(event.lepFSR_pt[i2],event.lepFSR_eta[i2],event.lepFSR_phi[i2],event.lepFSR_mass[i2])
            lep3.SetPtEtaPhiM(event.lepFSR_pt[j1],event.lepFSR_eta[j1],event.lepFSR_phi[j1],event.lepFSR_mass[j1])
            lep4.SetPtEtaPhiM(event.lepFSR_pt[j2],event.lepFSR_eta[j2],event.lepFSR_phi[j2],event.lepFSR_mass[j2])

            Z1 = ROOT.TLorentzVector()
            SSleps = ROOT.TLorentzVector()
            SSleps = lep3+lep4
            Z1 = lep1 + lep2
            Z1_lepindex = [0,0]
            Z1DeltaM = abs(Z1.M()-Zmass)

            # Check Leading and Subleading pt Cut
            if(lep1.Pt()>lep2.Pt()):
                Z1_lepindex[0] = i1
                Z1_lepindex[1] = i2
                if(lep1.Pt()<20 or lep2.Pt()<10): continue
            else:
                Z1_lepindex[0] = i2
                Z1_lepindex[1] = i1
                if(lep2.Pt()<20 or lep1.Pt()<10): continue
            npassedpt += 1
            # Check dR(li,lj)>0.02 for any i,j
            if (deltaR(lep1.Eta(),lep1.Phi(),lep2.Eta(),lep2.Phi())<0.02): continue
            if (deltaR(lep1.Eta(),lep1.Phi(),lep3.Eta(),lep3.Phi())<0.02): continue
            if (deltaR(lep1.Eta(),lep1.Phi(),lep4.Eta(),lep4.Phi())<0.02): continue
            if (deltaR(lep2.Eta(),lep2.Phi(),lep3.Eta(),lep3.Phi())<0.02): continue
            if (deltaR(lep2.Eta(),lep2.Phi(),lep4.Eta(),lep4.Phi())<0.02): continue
            if (deltaR(lep3.Eta(),lep3.Phi(),lep4.Eta(),lep4.Phi())<0.02): continue
            npassedDR += 1
            # Check M(l+,l-)>4.0 GeV for any OS pair , Do not include FSR photons
            allM = []
            lep1_noFSR = ROOT.TLorentzVector()
            lep2_noFSR = ROOT.TLorentzVector()
            lep3_noFSR = ROOT.TLorentzVector()
            lep4_noFSR = ROOT.TLorentzVector()
            lep1_noFSR.SetPtEtaPhiM(event.lep_pt[i1],event.lep_eta[i1],event.lep_phi[i1],event.lep_mass[i1])
            lep2_noFSR.SetPtEtaPhiM(event.lep_pt[i2],event.lep_eta[i2],event.lep_phi[i2],event.lep_mass[i2])
            lep3_noFSR.SetPtEtaPhiM(event.lep_pt[j1],event.lep_eta[j1],event.lep_phi[j1],event.lep_mass[j1])
            lep4_noFSR.SetPtEtaPhiM(event.lep_pt[j2],event.lep_eta[j2],event.lep_phi[j2],event.lep_mass[j2])
            i1i2 = ROOT.TLorentzVector()
            i1i2 = lep1_noFSR+lep2_noFSR
            allM.append(i1i2.M())
            if(event.lep_id[i1]*event.lep_id[j1]<0):
                i1j1 = ROOT.TLorentzVector()
                i1j2 = ROOT.TLorentzVector()
                i1j2 = lep1_noFSR+lep4_noFSR
                i1j1 = lep1_noFSR+lep3_noFSR
                allM.append(i1j1.M())
                allM.append(i1j2.M())
            else:
                i2j1 = ROOT.TLorentzVector()
                i2j2 = ROOT.TLorentzVector()
                i2j1 = lep2_noFSR+lep3_noFSR
                i2j2 = lep2_noFSR+lep4_noFSR
                allM.append(i2j1.M())
                allM.append(i2j2.M())
            allM.sort()
            # print " list of OS pair mass after sort : " + str(allM)
            if(allM[0]<4.0): continue

            npassedM2l += 1
            # Check isolation cut (without FSR ) for Z1 leptons
            #if(abs(event.lep_id[Z1_lepindex[0]])==13):
            if( event.lep_RelIsoNoFSR[Z1_lepindex[0]]>0.35): continue
            #if(abs(event.lep_id[Z1_lepindex[1]])==13):
            if( event.lep_RelIsoNoFSR[Z1_lepindex[1]]>0.35): continue
            npassedios +=1
            # Check tight ID cut for Z1 leptons
            if (not event.lep_tightId[Z1_lepindex[0]]): continue
            if (not event.lep_tightId[Z1_lepindex[1]]): continue
            #if (not event.lep_tightId[j1]): continue
            #if (not event.lep_tightId[j2]): continue
            npassedtight += 1
            # check the masswindow
            if(Z1.M()<12 or Z1.M()>120 or SSleps.M()<12 or SSleps.M()>120): continue
            #mass4l = (lep1+lep2+lep3+lep4).M()
            # if(mass4l<100): continue
            npassedMwindow +=1
            # Check if this candidate has the best Z1 and highest scalar sum of Z2 lepton pt
            if(Z1DeltaM<minZ1DeltaM):
                minZ1DeltaM = Z1DeltaM
                massZ1 = Z1.M()
                lep_index[0] = Z1_lepindex[0]
                lep_index[1] = Z1_lepindex[1]
                lep_index[2] = j1
                lep_index[3] = j2
                passedSSCRselection = True


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
            data4e.Fill(mass4l)




print " nindexpair  = " + str(nindexpair)
print " npassedid = " + str(npassedid)
print " npassedpt = " + str(npassedpt)
print " npassedDR = " + str(npassedDR)
print " npassedM2l = " + str(npassedM2l)
print " npassedios = " + str(npassedios)
print " npassedtight = " + str(npassedtight)
print " npassedMwindow = " + str(npassedMwindow)
print " npassed4e = " + str(npassed4e)

data4e.Draw()
c.SaveAs("plot/dataP2F2_4e_SS.png")
#Zm.Draw()
#c.SaveAs("plot/ZmassCRSS.png")
