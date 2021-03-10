from ROOT import *
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
from Plot_Helper import *
from deltaR import *
from OSMethod import *

WZfile_1 = "/cms/user/guojl/Sample/WZTo3LNu_TuneCP5_13TeV_filter2l.root"
WZfile_2 = "/cms/user/guojl/Sample/WZTo3LNu_TuneCP5_13TeV_ext_filter2l.root"
datafile  = "/cms/user/guojl/Sample/skimed/2018_noDuplicates.root"

#chain = TChain("Ana/passedEvents")
#chain.Add(WZfile_1)
#chain.Add(WZfile_2)
file = TFile(datafile)
tree = file.Get("passedEvents")

histos={}
cat_names = ['4e2P2F','4mu2P2F','2e2mu2P2F','2mu2e2P2F']
for cat_name in cat_names:
    histos[cat_name]=TH1D(cat_name,cat_name,40,70,870)

#Nentries = chain.GetEntries()
#print "[INFO] There are {0:s} entries in tree.".format(str(Nentries))

#f1 = TFile(WZfile_1)
#f2 = TFile(WZfile_2)
#SumWHistos = f1.Ana.Get("sumWeights")
#SumW = SumWHistos.GetBinContent(1)
#print "[INFO] Total number of events in WZ for lumi weight = " +str(SumW)
#SumWHistos = f2.Ana.Get("sumWeights")
#SumW += SumWHistos.GetBinContent(1)
#print "[INFO] Total number of events in WZ + WZ_ext for lumi weight = " +str(SumW)

#weightHisto = TH1D("weight","weight",100,-1,1)
#inclusiveHisto = TH1D("WZ_inclusive","WZ_inclusive",40,70,870)
#Histo4e = TH1D("WZ_4e","WZ_4e",40,70,870)
#weightarray=[]
#eventWeight=[]
#lumiWeight=[]
#N4looseLep = 0
#N3looseLep = 0
#Nlarger4looseLep = 0
#NpassedCR =0
#NpassedID = 0
#Npassed3tight = 0
#Npassedinclusive = 0
#Npassed4e = 0
for ievent,event in enumerate(tree):
    #if(ievent==100):break
    #if(event.lep1_id*event.lep2_id>0 or event.lep3_id*event.lep4_id>0): continue
    if(not event.passedZXCRSelection): continue
    if(event.nZXCRFailedLeptons==2):
        l1 = TLorentzVector()
        l2 = TLorentzVector()
        l3 = TLorentzVector()
        l4 = TLorentzVector()
        l1.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
        l2.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
        l3.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[2]])
        l4.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[3]],event.lepFSR_eta[event.lep_Hindex[3]],event.lepFSR_phi[event.lep_Hindex[3]],event.lepFSR_mass[event.lep_Hindex[3]])
        mass4l = (l1+l2+l3+l4).M()
        if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
            histos['4e2P2F'].Fill(mass4l,1)
        if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
            histos['4mu2P2F'].Fill(mass4l,1)
        if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==11 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
            histos['2e2mu2P2F'].Fill(mass4l,1)
        if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==13 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
            histos['2mu2e2P2F'].Fill(mass4l,1)

    #if(event.nZXCRFailedLeptons==1):
    #    if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==11):
    #        dataP3F1_4e.Fill(event.lep_4mass)
    #    if(abs(event.lep1_id)==abs(event.lep2_id)==abs(event.lep3_id)==abs(event.lep4_id)==13):
    #        dataP3F1_4mu.Fill(event.lep_4mass)
    #    if(abs(event.lep1_id)==abs(event.lep2_id)==11 and abs(event.lep3_id)==abs(event.lep4_id)==13):
    #        dataP3F1_2e2mu.Fill(event.lep_4mass)
    #    if(abs(event.lep1_id)==abs(event.lep2_id)==13 and abs(event.lep3_id)==abs(event.lep4_id)==11):
    #        dataP3F1_2mu2e.Fill(event.lep_4mass)




#print "[INFO] There are {0:s} events containing 4 leptons in raw ntuple.".format(str(N4looseLep))
#print "[INFO] There are {0:s} events containing 3 leptons in raw ntuple.".format(str(N3looseLep))
#print "[INFO] There are {0:s} events containing more than 4 leptons in raw ntuple.".format(str(Nlarger4looseLep))
#print "[INFO] There are {0:s} events passed Control Region selection. That means each event contain Z1 and at least one loose lepton in addtional two leptons ".format(str(NpassedCR))
#print "[INFO] There are {0:s} events passed opposite sign selection.(addtional two leptons are opposite sign)".format(str(NpassedID))
#print "[INFO] There are {0:s} events passed 3P1F selection.".format(str(Npassed3tight))
#print "[INFO] There are {0:s} events in 4e channel.".format(str(Npassed4e))
#print "[INFO] Every 3P1F weight will be shown(include lumi weight)."
#print str(weightarray)
#print "[INFO] Every 3P1F weight will be shown(without lumi weight)"
#print str(eventWeight)
#print "[INFO] Inclusive, 4e channel and weight will be Draw."

c=TCanvas("c","c",600,600)
for cat_name in cat_names:
    histos[cat_name].Draw("E1")
    c.SaveAs("OSCR_"+cat_name+".png")
#inclusiveHisto.SetFillColor(kMagenta -4)
#Histo4e.SetFillColor(kMagenta -4)

#inclusiveHisto.Draw('histo')
#c.SaveAs("plot/OS_CRtest_WZinclusive.png")
#Histo4e.Draw('histo')
#c.SaveAs("plot/OS_CRtest_WZ4e.png")
#weightHisto.Draw()
#c.SaveAs("plot/OS_CRtest_weight.png")
