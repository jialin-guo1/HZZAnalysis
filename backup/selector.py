#!/usr/bin/env python3
from bdb import effective
import os, sys
import ROOT
import correctionlib
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from variables import *
from functions import *
from topsXFinder import *



class declareVariables(variables):
    def __init__(self, name):
        super(declareVariables, self).__init__(name)

class Producer(Module):
    def __init__(self, **kwargs):
        #User inputs
        self.channel     = kwargs.get('channel') 
        self.isData      = 'data' in kwargs.get('dataType')
        self.year        = kwargs.get('year') 
        self.lumiWeight  = kwargs.get('lumiWeight')
        self.maxNumEvt   = kwargs.get('maxNumEvt')
        self.processName = kwargs.get('processName')
        self.btagEff     = kwargs.get('btagEff')
        self.prescaleEvt = kwargs.get('prescaleEvt')
  
        #Analysis quantities
        if self.year=="2018":
            #Trigger 
            if self.channel=="mu": self.trigger = lambda e: (hasattr(e, 'HLT_IsoMu24') and e.HLT_IsoMu24)
            if self.channel=="e": self.trigger = lambda e: (hasattr(e, 'HLT_Ele32_WPTight_Gsf') and e.HLT_Ele32_WPTight_Gsf) 
            #metfilter
            self.metfilter = lambda e: e.Flag_goodVertices and e.Flag_globalSuperTightHalo2016Filter and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadPFMuonDzFilter and e.Flag_eeBadScFilter and e.Flag_ecalBadCalibFilter #and e.Flag_BadChargedCandidateFilter 
        elif self.year=="2017":
            #Trigger
            if self.channel=="mu": self.trigger = lambda e: (hasattr(e, 'HLT_IsoMu27') and e.HLT_IsoMu27)
            if self.channel=="e": 
                self.trigger = lambda e: (hasattr(e, 'HLT_Ele32_WPTight_Gsf_L1DoubleEG') and e.HLT_Ele32_WPTight_Gsf_L1DoubleEG)
                self.metfilter = lambda e: e.hltEGL1SingleEGOrFilter  
            #metfilter
            self.metfilter = lambda e: e.Flag_goodVertices and e.Flag_globalSuperTightHalo2016Filter and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadPFMuonDzFilter and e.Flag_eeBadScFilter and e.Flag_ecalBadCalibFilter #and e.Flag_BadChargedCandidateFilter 
        elif self.year=="2016":
            #Trigger
            if self.channel=="mu": self.trigger = lambda e: ((hasattr(e, 'HLT_IsoMu24') and e.HLT_IsoMu24) or (hasattr(e, 'HLT_IsoTkMu24') and e.HLT_IsoTkMu24)) 
            if self.channel=="e": self.trigger = lambda e: (hasattr(e, 'HLT_Ele25_eta2p1_WPTight_Gsf') and e.HLT_Ele25_eta2p1_WPTight_Gsf)
            #metfilter
            self.metfilter = lambda e: e.Flag_goodVertices and e.Flag_globalSuperTightHalo2016Filter and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadPFMuonDzFilter and e.Flag_eeBadScFilter and e.Flag_ecalBadCalibFilter #and e.Flag_BadChargedCandidateFilter
        elif self.year=="2016APV":
            #Trigger
            if self.channel=="mu": self.trigger = lambda e: ((hasattr(e, 'HLT_IsoMu24') and e.HLT_IsoMu24) or (hasattr(e, 'HLT_IsoTkMu24') and e.HLT_IsoTkMu24)) 
            if self.channel=="e": self.trigger = lambda e: (hasattr(e, 'HLT_Ele25_eta2p1_WPTight_Gsf') and e.HLT_Ele25_eta2p1_WPTight_Gsf)
            #metfilter
            self.metfilter = lambda e: e.Flag_goodVertices and e.Flag_globalSuperTightHalo2016Filter and e.Flag_HBHENoiseFilter and e.Flag_HBHENoiseIsoFilter and e.Flag_EcalDeadCellTriggerPrimitiveFilter and e.Flag_BadPFMuonFilter and e.Flag_BadPFMuonDzFilter and e.Flag_eeBadScFilter and e.Flag_ecalBadCalibFilter #and e.Flag_BadChargedCandidateFilter
        else:
            raise ValueError('Year must be above 2016 (included).')

        #ID
  
        #Corrections

        #Cut flow table
        
    def beginJob(self):
        print("Here is beginJob")
        path_weights = "/cms/user/houxiaonan/ttZprime/SF/"  
        if self.year == '2018':
            #trigger
            if self.channel=="mu": 
                self.triggerFile = TFile(path_weights+'trigger/2018muon_official_new.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Mu2018_loose.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Mu2018_tight.root','READ')
                self.leptonTIsoFile = TFile(path_weights+'lepton_ID/Mu2018_tightIso.root','READ')
            if self.channel=="e": 
                self.triggerFile = TFile(path_weights+'trigger/sf_el_2018_HLTEle32.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Ele2018_wp90iso.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Ele2018_wp80iso.root','READ')
            #Pileup 
            self.puFile = TFile(path_weights+'PU/PU_Hist_2018.root','READ')
            self.puFileUp = TFile(path_weights+'PU/PU_Hist_2018_up.root','READ')
            self.puFileDown = TFile(path_weights+'PU/PU_Hist_2018_down.root','READ')
            #b tagging
            self.cset = correctionlib.CorrectionSet.from_file(path_weights+"btag/btagging18.json")
            self.btagLooseWP  = 0.0490
            self.btagMediumWP = 0.2783
            self.btagTightWP  = 0.7100
        if self.year == '2017':
            #trigger
            if self.channel=="mu": 
                self.triggerFile = TFile(path_weights+'trigger/2017muon_official_new.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Mu2017_loose.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Mu2017_tight.root','READ')
                self.leptonTIsoFile = TFile(path_weights+'lepton_ID/Mu2017_tightIso.root','READ')
            if self.channel=="e": 
                self.triggerFile = TFile(path_weights+'trigger/sf_el_2017_HLTEle32.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Ele2017_wp90iso.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Ele2017_wp80iso.root','READ')
            #Pileup 
            self.puFile = TFile(path_weights+'PU/PU_Hist_2017.root','READ')
            self.puFileUp = TFile(path_weights+'PU/PU_Hist_2017_up.root','READ')
            self.puFileDown = TFile(path_weights+'PU/PU_Hist_2017_down.root','READ')
            #b tagging
            self.cset = correctionlib.CorrectionSet.from_file(path_weights+"btag/btagging17.json.gz")
            self.btagLooseWP  = 0.0532
            self.btagMediumWP = 0.3040
            self.btagTightWP  = 0.7476
        if self.year == '2016APV':
            #trigger
            if self.channel=="mu": 
                self.triggerFile = TFile(path_weights+'trigger/2016APVmuon_official_new.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Mu2016APV_loose.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Mu2016APV_tight.root','READ')
                self.leptonTIsoFile = TFile(path_weights+'lepton_ID/Mu2016APV_tightIso.root','READ')
            if self.channel=="e": 
                self.triggerFile = TFile(path_weights+'trigger/sf_el_2016pre_HLTEle25.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Ele2016APV_wp90iso.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Ele2016APV_wp80iso.root','READ')
            #Pileup 
            self.puFile = TFile(path_weights+'PU/PU_Hist_2016.root','READ')
            self.puFileUp = TFile(path_weights+'PU/PU_Hist_2016_up.root','READ')
            self.puFileDown = TFile(path_weights+'PU/PU_Hist_2016_down.root','READ')
            #b tagging
            self.cset = correctionlib.CorrectionSet.from_file(path_weights+"btag/btagging16pre.json.gz")
            self.btagLooseWP  = 0.0508
            self.btagMediumWP = 0.2598
            self.btagTightWP  = 0.6502
        if self.year == '2016':
            #trigger
            if self.channel=="mu": 
                self.triggerFile = TFile(path_weights+'trigger/2016muon_official_new.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Mu2016_loose.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Mu2016_tight.root','READ')
                self.leptonTIsoFile = TFile(path_weights+'lepton_ID/Mu2016_tightIso.root','READ')
            if self.channel=="e": 
                self.triggerFile = TFile(path_weights+'trigger/sf_el_2016post_HLTEle25.root','READ')
                self.leptonLIDFile = TFile(path_weights+'lepton_ID/Ele2016_wp90iso.root','READ')
                self.leptonTIDFile = TFile(path_weights+'lepton_ID/Ele2016_wp80iso.root','READ')
            #Pileup 
            self.puFile = TFile(path_weights+'PU/PU_Hist_2016.root','READ')
            self.puFileUp = TFile(path_weights+'PU/PU_Hist_2016_up.root','READ')
            self.puFileDown = TFile(path_weights+'PU/PU_Hist_2016_down.root','READ')
            #b tagging
            self.cset = correctionlib.CorrectionSet.from_file(path_weights+"btag/btagging16post.json.gz")
            self.cset_4incl = correctionlib.CorrectionSet.from_file(path_weights+"btag/btagging16pre.json.gz")
            self.btagLooseWP  = 0.0480
            self.btagMediumWP = 0.2489
            self.btagTightWP  = 0.6377
        
        #btagging weight
        if not self.btagEff and not self.isData:
            #DeepFlavour
            self.btagFileName = path_weights+"btag/CR_c2/muon/"+str(self.year)+"/"+self.processName+".root"            
            self.btagFile     = TFile(self.btagFileName,'READ')
            self.histoBL    = self.btagFile.Get('histLDeepFlavour_b_passing')
            self.hDenBL     = self.btagFile.Get('histLDeepFlavour_b_total')
            self.histoCL    = self.btagFile.Get('histLDeepFlavour_c_passing')
            self.hDenCL     = self.btagFile.Get('histLDeepFlavour_c_total')
            self.histoUdsgL = self.btagFile.Get('histLDeepFlavour_udsg_passing')
            self.hDenUdsgL  = self.btagFile.Get('histLDeepFlavour_udsg_total')
            self.histoBL.Divide(self.hDenBL)
            self.histoCL.Divide(self.hDenCL)
            self.histoUdsgL.Divide(self.hDenUdsgL)
            self.histoBM    = self.btagFile.Get('histMDeepFlavour_b_passing')
            self.hDenBM     = self.btagFile.Get('histMDeepFlavour_b_total')
            self.histoCM    = self.btagFile.Get('histMDeepFlavour_c_passing')
            self.hDenCM     = self.btagFile.Get('histMDeepFlavour_c_total')
            self.histoUdsgM = self.btagFile.Get('histMDeepFlavour_udsg_passing')
            self.hDenUdsgM  = self.btagFile.Get('histMDeepFlavour_udsg_total')
            self.histoBM.Divide(self.hDenBM)
            self.histoCM.Divide(self.hDenCM)
            self.histoUdsgM.Divide(self.hDenUdsgM)
            self.histoBT    = self.btagFile.Get('histTDeepFlavour_b_passing')
            self.hDenBT     = self.btagFile.Get('histTDeepFlavour_b_total')
            self.histoCT    = self.btagFile.Get('histTDeepFlavour_c_passing')
            self.hDenCT     = self.btagFile.Get('histTDeepFlavour_c_total')
            self.histoUdsgT = self.btagFile.Get('histTDeepFlavour_udsg_passing')
            self.hDenUdsgT  = self.btagFile.Get('histTDeepFlavour_udsg_total')
            self.histoBT.Divide(self.hDenBT)
            self.histoCT.Divide(self.hDenCT)
            self.histoUdsgT.Divide(self.hDenUdsgT)
        #pass
        
    def endJob(self):
        print("Here is endJob")
        #pass
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print("Here is beginFile")
        self.sumNumEvt = 0
        self.sumgenWeight = 0
        self.out = declareVariables(inputFile)

        if self.btagEff and not self.isData:
            ptbins_bc   = array('d',[20,30,50,70,100,140,200,300,600,1000])
            ptbins_udsg = array('d',[20,1000])
            etabins     = array('d',[0.0,2.51])
            bins_bc = (len(ptbins_bc)-1,ptbins_bc,len(etabins)-1,etabins)
            bins_udsg = (len(ptbins_udsg)-1,ptbins_udsg,len(etabins)-1,etabins)
            #DeepFlavour
            self.histsBtaggingDeepFlavour = { }
            for histos in range(0, 18):
                if(histos ==  0): histname = "histTDeepFlavour_b_total"
                if(histos ==  1): histname = "histMDeepFlavour_b_total"
                if(histos ==  2): histname = "histLDeepFlavour_b_total"
                if(histos ==  3): histname = "histTDeepFlavour_b_passing"
                if(histos ==  4): histname = "histMDeepFlavour_b_passing"
                if(histos ==  5): histname = "histLDeepFlavour_b_passing"
                if(histos ==  6): histname = "histTDeepFlavour_c_total"
                if(histos ==  7): histname = "histMDeepFlavour_c_total"
                if(histos ==  8): histname = "histLDeepFlavour_c_total"
                if(histos ==  9): histname = "histTDeepFlavour_c_passing"
                if(histos == 10): histname = "histMDeepFlavour_c_passing"
                if(histos == 11): histname = "histLDeepFlavour_c_passing"
                if(histos == 12): histname = "histTDeepFlavour_udsg_total"
                if(histos == 13): histname = "histMDeepFlavour_udsg_total"
                if(histos == 14): histname = "histLDeepFlavour_udsg_total"
                if(histos == 15): histname = "histTDeepFlavour_udsg_passing"
                if(histos == 16): histname = "histMDeepFlavour_udsg_passing"
                if(histos == 17): histname = "histLDeepFlavour_udsg_passing"
                if histos<12:
                    self.histsBtaggingDeepFlavour[histos] = TH2F(histname,histname,*bins_bc)
                else:
                    self.histsBtaggingDeepFlavour[histos] = TH2F(histname,histname,*bins_udsg)
                self.histsBtaggingDeepFlavour[histos].SetDirectory(0)
        #pass
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):        
        print("Here is endFile")
        self.out.sumNumEvt[0] = self.sumNumEvt
        self.out.sumgenWeight[0] = self.sumgenWeight
        self.out.evtree.Fill()
        if self.btagEff and not self.isData:
            for histos in range(0, 18): self.histsBtaggingDeepFlavour[histos].Write()
        self.out.outputfile.Write()
        self.out.outputfile.Close()
        #pass
        
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #For all events
        if(self.sumNumEvt>self.maxNumEvt and self.maxNumEvt!=-1): return False
        self.sumNumEvt = self.sumNumEvt+1
        if not self.isData: self.sumgenWeight = self.sumgenWeight+(event.genWeight/abs(event.genWeight))
        if not self.sumNumEvt%self.prescaleEvt==0: return False
        pass_cut = 0 

        #weights
        #trigger weight
        trig_weight = 1
        trig_weight_up = 1
        trig_weight_down = 1
        lep_ID_weight = 1
        lep_ID_weight_up = 1
        lep_ID_weight_down = 1
        lep_Iso_weight = 1
        lep_Iso_weight_up = 1
        lep_Iso_weight_down = 1
        pu_weight = 1
        pu_weight_up = 1
        pu_weight_down = 1
        top_tag_weight = 1
        top_tag_weight_up = 1
        top_tag_weight_down = 1
        #btag weight
        btagWeight = 1
        btagWeightUp = 1
        btagWeightDown = 1

        selected_idx = {'muon_L': [], 'electron_L': [], 'muon_T': [], 'electron_T': [], 'jetsTop_L': [], 'jetsTop_M': [], 'jetsTop_T': [], 'jetsW_L': [], 'jetsW_M': [], 'jetsW_T': [], 'jets_4HT':[], 'jets_cleaned': [], 'jets_noCleaned_against_boostedJets': [], 'jetsB_L': [], 'jetsB_M': [], 'jetsB_T': []}
        muons = Collection(event, 'Muon')
        select_muons(event, self.year, selected_idx)

        eles = Collection(event, 'Electron')
        select_electrons(event, self.year, selected_idx)
        
        if (self.channel=="mu"):
            if not (len(selected_idx['muon_T'])==1 and len(selected_idx['muon_L'])==1 and len(selected_idx['electron_L'])==0): 
                effevt(pass_cut, self, event)
                return False
            pass_cut = pass_cut+1 #pass_cut = 1

            #if not (len(selected_idx['muon_L'])==1):
                #effevt(pass_cut, self, event)
                #return False
            #pass_cut = pass_cut+1 #pass_cut = 2

            #if not (len(selected_idx['electron_L'])==0):
                #effevt(pass_cut, self, event)
                #return False
            #pass_cut = pass_cut+1 #pass_cut = 3
            
        if (self.channel=="e"):
            if not (len(selected_idx['electron_T'])==1 and len(selected_idx['electron_L'])==1 and len(selected_idx['muon_L'])==0): 
                effevt(pass_cut, self, event)
                return False
            pass_cut = pass_cut+1 #pass_cut = 1

            #if not (len(selected_idx['electron_L'])==1):
                #effevt(pass_cut, self, event)
                #return False
            #pass_cut = pass_cut+1 #pass_cut = 2

            #if not (len(selected_idx['muon_L'])==0): 
                #effevt(pass_cut, self, event)
                #return False
            #pass_cut = pass_cut+1 #pass_cut = 3

        if not self.trigger(event):
            effevt(pass_cut, self, event)
            return False
        pass_cut = pass_cut+1 #pass_cut = 4

        if not self.metfilter(event):
            effevt(pass_cut, self, event)
            return False
        pass_cut = pass_cut+1 #pass_cut = 5

        fatjets = Collection(event, 'FatJet')
        select_top_jets(event, self.year, selected_idx)
        #select_w_jets(event, self.year, selected_idx)
  
        jets = Collection(event, 'Jet')
        select_jets(event, self.year, selected_idx)
        HT = 0.0
        HT = calculate_HT(event,selected_idx['jets_4HT'])
    
        if not (HT>700):
            effevt(pass_cut, self, event)
            return False
        pass_cut = pass_cut+1 #pass_cut = 6
    
        if not (event.MET_pt>60):
            effevt(pass_cut, self, event)
            return False
        pass_cut = pass_cut+1 #pass_cut = 7

        if not (len(selected_idx['jets_noCleaned_against_boostedJets'])>=6):
            effevt(pass_cut, self, event)
            return False
        pass_cut = pass_cut+1 #pass_cut = 8

        #btagging efficiencies
        if self.btagEff and not self.isData:
            fillbtagEfficiencies(event,selected_idx['jets_cleaned'],self.btagLooseWP,self.btagMediumWP,self.btagTightWP,self.histsBtaggingDeepFlavour)
        #btag weight 
        if not self.btagEff and not self.isData:
            if self.year == '2016': btagWeight, btagWeightUp, btagWeightDown = getbtagWeight_2016(event, self.btagLooseWP, self.btagMediumWP, self.btagTightWP, selected_idx['jets_cleaned'], self.cset, self.cset_4incl, self.histoBT, self.histoCT, self.histoUdsgT, self.histoBM, self.histoCM, self.histoUdsgM, self.histoBL, self.histoCL, self.histoUdsgL)
            else: btagWeight, btagWeightUp, btagWeightDown = getbtagWeight_all(event, self.btagLooseWP, self.btagMediumWP, self.btagTightWP, selected_idx['jets_cleaned'], self.cset, self.histoBT, self.histoCT, self.histoUdsgT, self.histoBM, self.histoCM, self.histoUdsgM, self.histoBL, self.histoCL, self.histoUdsgL)

        #pre-selections for each category
        pre_category_0T = len(selected_idx['jetsTop_M'])==0
        pre_category_1T = len(selected_idx['jetsTop_M'])==1
        pre_category_2T = len(selected_idx['jetsTop_M'])>=2
        
        if (pre_category_0T):
            if not (len(selected_idx['jetsB_L'])<3):
                effevt(pass_cut, self, event)
                return False
            pass_cut = pass_cut+1
  
        if (pre_category_1T):
            if not (len(selected_idx['jetsB_L'])<2):
                effevt(pass_cut, self, event)
                return False
            pass_cut = pass_cut+1 #pass_cut = 4
        
        if (pre_category_2T):
            if not (len(selected_idx['jetsB_L'])<1):
                effevt(pass_cut, self, event)
                return False
            pass_cut = pass_cut+1 #pass_cut = 4

        self.out.pre_category_0T[0] = pre_category_0T
        self.out.pre_category_1T[0] = pre_category_1T
        self.out.pre_category_2T[0] = pre_category_2T

        #top reconstruction
        #these are for the total results
        results ={'top':[], 'w':[], 'top_topology_decay':[], 'chi2':[]}#Top to keep all the Top(TLorentzVector), W to keep all the W(TLorentzVector) (boosted top part,just using (0,0,0,0) instead)
        #topTopologyDecay to define the kind of top (0: boosted, 1: partially-boosted, 2: resolved hadronic, 3: resolved leptonic) 
        top_type = {'boosted_top': True, 'partially_boosted_top': False, 'hadronic_top': True, 'leptonic_top': True}
        topsXFinder(event, selected_idx, top_type, results)

        #sorted all the cases into 4 kinds
        boosted_top = []
        #partially_boosted_top = []
        #partially_boosted_w = []
        hadronic_top = []
        hadronic_w = []
        leptonic_top = []
        leptonic_w = []
        for i in range(0, len(results['top_topology_decay'])):
            if (results['top_topology_decay'][i]==0): boosted_top.append(results['top'][i])
            #if results['top_topology_decay'][i]==1:
                #partially_boosted_top.append(results['top'][i])
                #partially_boosted_w.append(results['w'][i])
            if results['top_topology_decay'][i]==2:
                hadronic_top.append(results['top'][i])
                hadronic_w.append(results['w'][i])
            if results['top_topology_decay'][i]==3:
                leptonic_top.append(results['top'][i])
                leptonic_w.append(results['w'][i])
        
        if not (len(results['top'])>=2):
            effevt(pass_cut, self, event)
            return False
        pass_cut = pass_cut+1

        effevt(pass_cut, self, event)
        
        if not self.isData: 
            pu_weight, pu_weight_up, pu_weight_down = getPileupWeight(event, self.puFile, self.puFileUp, self.puFileDown, self.year)
            top_tag_weight, top_tag_weight_up, top_tag_weight_down = getTopTagWeight(event, self.year, selected_idx['jetsTop_M'])
            if (self.channel=="mu"): 
                trig_weight, trig_weight_up, trig_weight_down = get_mu_trigSF(self.year, self.triggerFile, event.Muon_pt[selected_idx['muon_T'][0]], abs(event.Muon_eta[selected_idx['muon_T'][0]]))
                lep_ID_weight, lep_ID_weight_up, lep_ID_weight_down = get_mu_IDSF(self.leptonTIDFile, "SF", event.Muon_pt[selected_idx['muon_T'][0]], abs(event.Muon_eta[selected_idx['muon_T'][0]]))
                lep_Iso_weight, lep_Iso_weight_up, lep_Iso_weight_down = get_mu_PFIsoSF(self.leptonTIsoFile, event.Muon_pt[selected_idx['muon_T'][0]], abs(event.Muon_eta[selected_idx['muon_T'][0]]))
            if (self.channel=="e"):  
                trig_weight, trig_weight_up, trig_weight_down = get_ele_trigSF(self.year, self.triggerFile, event.Electron_pt[selected_idx['electron_T'][0]], event.Electron_eta[selected_idx['electron_T'][0]])
                lep_ID_weight, lep_ID_weight_up, lep_ID_weight_down = get_ele_IDSF(self.year, self.leptonTIDFile, "h2_scaleFactorsEGamma", event.Electron_pt[selected_idx['electron_T'][0]], event.Electron_eta[selected_idx['electron_T'][0]])

        #Event
        self.out.run[0] = event.run
        self.out.luminosityBlock[0] = event.luminosityBlock
        self.out.event[0] = event.event #& 0xffffffffffffffff
        
        #Weight
        #Weight
        if self.isData: 
            self.out.genWeight[0] = 1
            self.out.L1PreFiringWeight_Dn[0] = 1
            self.out.L1PreFiringWeight_Nom[0] = 1
            self.out.L1PreFiringWeight_Up[0] = 1
        else: 
            self.out.genWeight[0] = event.genWeight/abs(event.genWeight)
            self.out.L1PreFiringWeight_Dn[0] = event.L1PreFiringWeight_Dn
            self.out.L1PreFiringWeight_Nom[0] = event.L1PreFiringWeight_Nom
            self.out.L1PreFiringWeight_Up[0] = event.L1PreFiringWeight_Up
        self.out.lumiWeight[0] = self.lumiWeight
        self.out.trig_weight[0] = trig_weight   
        self.out.trig_weight_up[0] = trig_weight_up
        self.out.trig_weight_down[0] = trig_weight_down
        self.out.lep_ID_weight[0] = lep_ID_weight   
        self.out.lep_ID_weight_up[0] = lep_ID_weight_up
        self.out.lep_ID_weight_down[0] = lep_ID_weight_down
        self.out.lep_Iso_weight[0] = lep_Iso_weight
        self.out.lep_Iso_weight_up[0] = lep_Iso_weight_up
        self.out.lep_Iso_weight_down[0] = lep_Iso_weight_down
        self.out.pu_weight[0] = pu_weight   
        self.out.pu_weight_up[0] = pu_weight_up
        self.out.pu_weight_down[0] = pu_weight_down
        self.out.top_tag_weight[0] = top_tag_weight
        self.out.top_tag_weight_up[0] = top_tag_weight_up
        self.out.top_tag_weight_down[0] = top_tag_weight_down
        self.out.b_tag_weight[0] = btagWeight
        self.out.b_tag_weight_up[0] = btagWeightUp
        self.out.b_tag_weight_down[0] = btagWeightDown
        
        #object
        save_pt_eta_particle(event, self, len(selected_idx['muon_L']), selected_idx['muon_L'], "muon_L", "Muon")
        save_pt_eta_particle(event, self, len(selected_idx['muon_T']), selected_idx['muon_T'], "muon_T", "Muon")
        save_pt_eta_particle(event, self, len(selected_idx['electron_L']), selected_idx['electron_L'], "electron_L", "Electron")
        save_pt_eta_particle(event, self, len(selected_idx['electron_T']), selected_idx['electron_T'], "electron_T", "Electron")
        self.out.num_reco_leps[0] = len(selected_idx['muon_T'])+len(selected_idx['electron_T'])
        if (len(selected_idx['muon_T'])>0): self.out.muon_T0_abseta[0] = abs(event.Muon_eta[selected_idx['muon_T'][0]])
        else: self.out.muon_T0_abseta[0] = -1
        if (len(selected_idx['electron_T'])>0): self.out.electron_T0_abseta[0] = abs(event.Electron_eta[selected_idx['electron_T'][0]])
        else: self.out.electron_T0_abseta[0] = -1
        self.out.num_jets[0] = len(selected_idx['jets_noCleaned_against_boostedJets'])
        if (len(selected_idx['jets_noCleaned_against_boostedJets'])>0):
            self.out.jet1_pt[0] = event.Jet_pt[selected_idx['jets_noCleaned_against_boostedJets'][0]]
            self.out.jet1_eta[0] = event.Jet_eta[selected_idx['jets_noCleaned_against_boostedJets'][0]]
        else:
            self.out.jet1_pt[0] = -1
            self.out.jet1_eta[0] = -999
        if (len(selected_idx['jets_noCleaned_against_boostedJets'])>1):
            self.out.jet2_pt[0] = event.Jet_pt[selected_idx['jets_noCleaned_against_boostedJets'][1]]
            self.out.jet2_eta[0] = event.Jet_eta[selected_idx['jets_noCleaned_against_boostedJets'][1]]
        else:
            self.out.jet2_pt[0] = -1
            self.out.jet2_eta[0] = -999
        if (len(selected_idx['jets_noCleaned_against_boostedJets'])>2):
            self.out.jet3_pt[0] = event.Jet_pt[selected_idx['jets_noCleaned_against_boostedJets'][2]]
            self.out.jet3_eta[0] = event.Jet_eta[selected_idx['jets_noCleaned_against_boostedJets'][2]]
        else:
            self.out.jet3_pt[0] = -1
            self.out.jet3_eta[0] = -999
        save_multiplicity_3wp(self, selected_idx['jetsB_L'], selected_idx['jetsB_M'], selected_idx['jetsB_T'], "BJets")
        save_multiplicity_3wp(self, selected_idx['jetsTop_L'], selected_idx['jetsTop_M'], selected_idx['jetsTop_T'], "TopJets")
  
        num_top = 4
        #reco tops
        self.out.num_top_total[0] = len(results['top'])
        save_4mass(self, num_top, results['top'], results['top_topology_decay'], "top")
  
        #reco W 
        self.out.num_w_total[0] = len(results['w'])
        save_4mass(self, num_top, results['w'], results['top_topology_decay'], "w")
  
        #for the top not boosted, we used chi2-increasing order, so here is the information about chi2 and mass
        save_chi2(self, num_top, results['chi2'], "chi2")
  
        #1.boosted top
        self.out.num_boosted_top[0] = len(boosted_top)
        save_mass(self, num_top, boosted_top, "boosted_top")
  
        #2.partially-boosted
        #self.out.num_partially_boosted_top[0] = len(partially_boosted_top)
        #save_mass(self, num_top, partially_boosted_top, "partially_boosted_top")

        #self.out.num_partially_boosted_w[0] = len(partially_boosted_w)
        #save_mass(self, num_top, partially_boosted_w, "partially_boosted_w")

        #3.resolved hadronic
        self.out.num_hadronic_top[0] = len(hadronic_top)
        save_mass(self, num_top, hadronic_top, "hadronic_top")
  
        self.out.num_hadronic_w[0] = len(hadronic_w)
        save_mass(self, num_top, hadronic_w, "hadronic_w")

        #4.resolved leptonic 
        self.out.num_leptonic_top[0] = len(leptonic_top)
        save_mass(self, 1, leptonic_top, "leptonic_top") #only have 1 lepton

        self.out.num_leptonic_w[0] = len(leptonic_w)
        save_mass(self, 1, leptonic_w, "leptonic_w")
  
        first_4top = [] #only use the first 4 tops
        if (len(results['top'])<=num_top):
            for itop in range(0,len(results['top'])):
                first_4top.append(results['top'][itop])
        else:
            for itop in range(0,num_top):
                first_4top.append(results['top'][itop])
        self.out.num_first_4top[0] = len(first_4top)

        #pt-decreasing order
        sorted_pt, sorted_top = pt_decrease(first_4top)
        if (len(boosted_top)>1): self.out.reco_zprime_mass1[0] = (boosted_top[0]+boosted_top[1]).M()
        if (len(boosted_top)==1): 
            sorted_pt1, sorted_top1 = pt_decrease_without_boosted_top(first_4top)
            if (len(sorted_top1)>0): self.out.reco_zprime_mass1[0] = (boosted_top[0]+sorted_top1[0]).M()
            else: self.out.reco_zprime_mass1[0] = -1
        if (len(boosted_top)<1): 
            if (len(sorted_top)>1): self.out.reco_zprime_mass1[0] = (sorted_top[0]+sorted_top[1]).M()
            else: self.out.reco_zprime_mass1[0] = -1
  
        #closest tops in dR
        dR_2top,tagger_2top = closest_dR(first_4top)
        if (len(boosted_top)>1): self.out.reco_zprime_mass2[0] = (boosted_top[0]+boosted_top[1]).M()
        if (len(boosted_top)==1): 
            dR_top,tagger_top = closest_dR_with_boosted_top(first_4top)
            if (len(dR_top)>0): self.out.reco_zprime_mass2[0] = (first_4top[0]+first_4top[tagger_top[0]]).M()
            else: self.out.reco_zprime_mass2[0] = -1
        if (len(boosted_top)<1):
            if (len(dR_2top)>0): self.out.reco_zprime_mass2[0] = (first_4top[tagger_2top[0]]+first_4top[tagger_2top[1]]).M()
            else: self.out.reco_zprime_mass2[0] = -1
  
        #highest mass for Z'
        RecoZprimeMass,position_2top = highest_mass(first_4top)
        if (len(boosted_top)>1): self.out.reco_zprime_mass3[0] = (boosted_top[0]+boosted_top[1]).M()
        if (len(boosted_top)==1):
            RecoMass,position_top = highest_mass_with_boosted_top(first_4top)
            if (len(RecoMass)>0): self.out.reco_zprime_mass3[0] = (first_4top[0]+first_4top[position_top[0]]).M()
            else: self.out.reco_zprime_mass3[0] = -1
        if (len(boosted_top)<1):
            if (len(RecoZprimeMass)>0): self.out.reco_zprime_mass3[0] = (first_4top[position_2top[0]]+first_4top[position_2top[1]]).M()
            else: self.out.reco_zprime_mass3[0] = -1

        #boosted+chi2 increasing order
        if(len(first_4top)>1): self.out.reco_zprime_mass4[0] = (first_4top[0]+first_4top[1]).M()
        else: self.out.reco_zprime_mass4[0] = -1

        #ST = sum pT of up to the first 4 tops
        ST = calculate_ST(first_4top)
        self.out.ST[0] = ST

        self.out.HT[0] = HT

        #Save tree
        self.out.Events.Fill() 
        return True

