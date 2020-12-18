import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from SSMethod import *

tree = {}
Signal = ROOT.TFile('/cms/user/guojl/Sample/DY_2018.root')
tree['t'] = Signal.Ana.Get('passedEvents')
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
ntup = tree['t']
print type(ntup)
print ntup.GetEntries()
for ievent,event in enumerate(ntup):
    lep_index = [0,0,0,0]
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
