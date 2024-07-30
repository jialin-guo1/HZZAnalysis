#!/usr/bin/env python3
import ROOT
import math, numpy as np
import correctionlib
from ROOT import TFile, TH1F, TH2F, BTagCalibration, BTagCalibrationReader
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from array import array
from ROOT.BTagEntry import OP_LOOSE, OP_MEDIUM, OP_TIGHT, OP_RESHAPING
from ROOT.BTagEntry import FLAV_B, FLAV_C, FLAV_UDSG

def effevt(pass_cut, self, event):
    pass_cut += 1
    self.out.passCut[0] = pass_cut
    self.out.eelumiWeight[0] = self.lumiWeight
    if self.isData: self.out.eegenWeight[0] = 1
    else: self.out.eegenWeight[0] = event.genWeight/abs(event.genWeight)
    self.out.effevt.Fill()

def select_muons(event, year, selected_idx):
    muons = Collection(event, 'Muon')
    for imu in range(event.nMuon):
        if not event.Muon_pt[imu] > 15: continue
        if not abs(event.Muon_eta[imu]) < 2.4: continue 
        if not event.Muon_dxy[imu] < 0.2: continue
        if not event.Muon_dz[imu] < 0.5: continue
        #if not event.Muon_miniPFRelIso_all[imu] < 0.4: continue
        if not event.Muon_pfRelIso04_all[imu] < 0.25: continue
        if not event.Muon_looseId[imu]: continue
        selected_idx['muon_L'].append(imu) 
        pt_cutsT = 10000 
        if year == '2018': pt_cutsT = 26
        if year == '2017': pt_cutsT = 29  
        if year == '2016': pt_cutsT = 26  
        if year == '2016APV': pt_cutsT = 26 
        if not event.Muon_pt[imu] > pt_cutsT: continue
        #if not event.Muon_miniPFRelIso_all[imu] < 0.1: continue
        if not event.Muon_pfRelIso04_all[imu] < 0.15: continue
        if not event.Muon_tightId[imu]: continue
        selected_idx['muon_T'].append(imu)

def select_electrons(event, year, selected_idx):
    electrons = Collection(event, 'Electron')
    muons = Collection(event, 'Muon')
    for iele in range(event.nElectron):
        if not event.Electron_pt[iele] > 15: continue
        if not abs(event.Electron_eta[iele]) < 2.5: continue
        if 1.444 < abs(event.Electron_eta[iele]) < 1.566: continue
        overlap = check_overlap(selected_idx['muon_L'], muons, electrons[iele].p4(), 0.4)
        if overlap: continue
        if not event.Electron_mvaFall17V2Iso_WP90[iele]: continue
        selected_idx['electron_L'].append(iele)
        pt_cutsT = 10000 
        if year == '2018': pt_cutsT = 33
        if year == '2017': pt_cutsT = 33  
        if year == '2016': pt_cutsT = 26  
        if year == '2016APV': pt_cutsT = 26
        if not event.Electron_pt[iele] > pt_cutsT: continue
        eta_cuts = 0.0 
        if year == '2018': eta_cuts = 2.5
        if year == '2017': eta_cuts = 2.5  
        if year == '2016': eta_cuts = 2.1 
        if year == '2016APV': eta_cuts = 2.1
        if not abs(event.Electron_eta[iele]) < eta_cuts: continue
        if not event.Electron_mvaFall17V2Iso_WP80[iele]: continue
        selected_idx['electron_T'].append(iele)

def is_overlap(objectA_p4, objectB_p4, value):
    if objectA_p4.DeltaR(objectB_p4)>value: return False
    else: return True

def check_overlap(objectA_list, objectA_name, objectB_p4, value):
    overlap = False
    for imu in range(len(objectA_list)):
        overlap = is_overlap(objectA_name[objectA_list[imu]].p4(), objectB_p4, value)
        if (overlap == True): break
    return overlap

def select_top_jets(event, year, selected_idx):
    fatjets = Collection(event, 'FatJet')
    muons = Collection(event, 'Muon')
    electrons = Collection(event, 'Electron')
    for ifatjet in range(event.nFatJet):
        # Kinematic
        if not event.FatJet_pt[ifatjet] >= 200: continue
        if not abs(event.FatJet_eta[ifatjet]) < 2.4: continue #This is the recommendation for all the fat jets (there are not reconstructed forward fat jets)
        # ID
        jet_id = 10000 #Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/JetID#Recommendations_for_13_TeV_data and https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVUL ("Please note: For AK8 jets, the corresponding (CHS or PUPPI) AK4 jet ID should be used.")
        if year == '2018': jet_id = 2  # tight ID
        if year == '2017': jet_id = 2  # tight ID
        if year == '2016' or year == '2016APV': jet_id = 3  # tight ID
        if not event.FatJet_jetId[ifatjet] >= jet_id: continue
        # Cleaning
        overlap_mu = check_overlap(selected_idx['muon_L'], muons, fatjets[ifatjet].p4(), 0.8)
        if overlap_mu: continue
        overlap_e = check_overlap(selected_idx['electron_L'], electrons, fatjets[ifatjet].p4(), 0.8)
        if overlap_e: continue
        # Top tagged jet
        if not event.FatJet_pt[ifatjet] >= 300: continue
        pNet_id = 10000 #Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs
        if year == '2018': pNet_id = 0.58  # loose ID
        if year == '2017': pNet_id = 0.58  # loose ID
        if year == '2016': pNet_id = 0.50  # loose ID
        if year == '2016APV': pNet_id = 0.49  # loose ID
        if not event.FatJet_particleNet_TvsQCD[ifatjet] >= pNet_id: continue
        selected_idx['jetsTop_L'].append(ifatjet)
        pNet_id = 10000 #Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs
        if year == '2018': pNet_id = 0.80  # medium ID
        if year == '2017': pNet_id = 0.80  # medium ID
        if year == '2016': pNet_id = 0.73  # medium ID
        if year == '2016APV': pNet_id = 0.74  # medium ID
        if not event.FatJet_particleNet_TvsQCD[ifatjet] >= pNet_id: continue
        selected_idx['jetsTop_M'].append(ifatjet)
        pNet_id = 10000 #Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs
        if year == '2018': pNet_id = 0.97  # tight ID
        if year == '2017': pNet_id = 0.97  # tight ID
        if year == '2016': pNet_id = 0.96  # tight ID
        if year == '2016APV': pNet_id = 0.96 #Tight ID
        if not event.FatJet_particleNet_TvsQCD[ifatjet] >= pNet_id: continue
        selected_idx['jetsTop_T'].append(ifatjet)

'''
def select_w_jets(event, year, selected_idx):
    fatjets = Collection(event, 'FatJet')
    muons = Collection(event, 'Muon')
    electrons = Collection(event, 'Electron')
    for ifatjet in range(event.nFatJet):
        # Kinematic
        if not event.FatJet_pt[ifatjet] >= 200: continue
        if not abs(event.FatJet_eta[ifatjet]) < 2.4: continue  # This is the recommendation for all the fat jets (there are not reconstructed forward fat jets)
        # ID
        jet_id = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/JetID#Recommendations_for_13_TeV_data and https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVUL ("Please note: For AK8 jets, the corresponding (CHS or PUPPI) AK4 jet ID should be used.")
        if year == "2018": jet_id = 2  # tight ID
        if year == "2017": jet_id = 2  # tight ID
        if year == "2016" or year == "2016APV": jet_id = 3  # tight ID
        if not event.FatJet_jetId[ifatjet] >= jet_id: continue
        # Cleaning
        overlap_mu = check_overlap(selected_idx['muon_L'], muons, fatjets[ifatjet].p4(), 0.8)
        if overlap_mu: continue
        overlap_e = check_overlap(selected_idx['electron_L'], electrons, fatjets[ifatjet].p4(), 0.8)
        if overlap_e: continue
        overlap_top = check_overlap(selected_idx['jetsTop_M'], fatjets, fatjets[ifatjet].p4(), 0.8)
        if overlap_top: continue
        # W tagged jet
        pNet_id = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs
        if year == "2018": pNet_id = 0.70  # loose ID
        if year == "2017": pNet_id = 0.71  # loose ID
        if year == "2016": pNet_id = 0.67  # loose ID
        if year == "2016APV": pNet_id = 0.68  # loose ID
        if not event.FatJet_particleNet_WvsQCD[ifatjet] >= pNet_id: continue
        selected_idx['jetsW_L'].append(ifatjet)
        pNet_id = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs
        if year == "2018": pNet_id = 0.94 #Medium ID
        if year=="2017": pNet_id = 0.94 #Medium ID 
        if year=="2016": pNet_id = 0.93 #Medium ID
        if year=="2016APV": pNet_id = 0.94 #Medium ID
        if not event.FatJet_particleNet_WvsQCD[ifatjet] >= pNet_id: continue
        selected_idx['jetsW_M'].append(ifatjet)
        pNet_id = 10000 #Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/ParticleNetTopWSFs
        if year=="2018": pNet_id = 0.98 #Tight ID 
        if year=="2017": pNet_id = 0.98 #Tight ID 
        if year=="2016": pNet_id = 0.97 #Tight ID
        if year=="2016APV": pNet_id = 0.97 #Tight ID
        if not event.FatJet_particleNet_WvsQCD[ifatjet] >= pNet_id: continue
        selected_idx['jetsW_T'].append(ifatjet)
'''

def select_jets(event, year, selected_idx):
    muons = Collection(event, 'Muon')
    electrons = Collection(event, 'Electron')
    fatjets = Collection(event, 'FatJet')
    jets = Collection(event, 'Jet')
    for ijet in range(event.nJet):
        # kinematic
        if not event.Jet_pt[ijet] >= 30: continue
        jet_eta = -1
        if year == "2016" or year == "2016APV": jet_eta = 2.4
        if year == "2017": jet_eta = 2.5
        if year == "2018": jet_eta = 2.5
        if not abs(event.Jet_eta[ijet]) < jet_eta: continue
        # ID
        jet_id = 10000  # Recommendation in https://twiki.cern.ch/twiki/bin/view/CMS/JetID#Recommendations_for_13_TeV_data and https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVUL ("Please note: For AK8 jets, the corresponding (CHS or PUPPI) AK4 jet ID should be used.")
        if year == "2016" or year == "2016APV": jet_id = 3  # tight ID
        if year == "2017": jet_id = 2  # tight ID
        if year == "2018": jet_id = 2  # tight ID
        if not event.Jet_jetId[ijet] >= jet_id: continue
        selected_idx['jets_4HT'].append(ijet)
        # cleaning
        overlap_mu = check_overlap(selected_idx['muon_L'], muons, jets[ijet].p4(), 0.4)
        if overlap_mu: continue
        overlap_e = check_overlap(selected_idx['electron_L'], electrons, jets[ijet].p4(), 0.4)
        if overlap_e: continue
        selected_idx['jets_noCleaned_against_boostedJets'].append(ijet)  # all the AK4 jets contain boosted jet
        overlap_top = check_overlap(selected_idx['jetsTop_M'], fatjets, jets[ijet].p4(), 0.8)
        if overlap_top: continue
        #overlap_w = check_overlap(selected_idx['jetsW_M'], fatjets, jets[ijet].p4(), 0.8)
        #if overlap_w: continue
        # save idx
        selected_idx['jets_cleaned'].append(ijet)  # used in the top reconstruction part for the resolved hadronic decay
        # b-jet
        bjet_eta = -1
        if year=="2016" or year=="2016APV": bjet_eta = 2.4
        if year=="2017": bjet_eta = 2.5
        if year=="2018": bjet_eta = 2.5
        if abs(event.Jet_eta[ijet]) < bjet_eta: 
            #loose working point 
            bjet_id = 10000 #Recommendation in https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation
            if year=="2016APV": bjet_id = 0.0508 #L,M,T: 0.0508,0.2598,0.6502 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16preVFP   
            if year=="2016": bjet_id = 0.0480 #L,M,T: 0.0480,0.2489,0.6377 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16postVFP
            if year=="2017": bjet_id = 0.0532 #L,M,T: 0.0532,0.3040,0.7476 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL17
            if year=="2018": bjet_id = 0.0490 #L,M,T: 0.0490,0.2783,0.7100 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL18
            if not event.Jet_btagDeepFlavB[ijet] >= bjet_id: continue
            selected_idx['jetsB_L'].append(ijet)
            #medium working point 
            bjet_id = 10000
            if year=="2016APV": bjet_id = 0.2598 #L,M,T: 0.0508,0.2598,0.6502 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16preVFP   
            if year=="2016": bjet_id = 0.2489 #L,M,T: 0.0480,0.2489,0.6377 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16postVFP
            if year=="2017": bjet_id = 0.3040 #L,M,T: 0.0532,0.3040,0.7476 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL17
            if year=="2018": bjet_id = 0.2783 #L,M,T: 0.0490,0.2783,0.7100 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL18
            if not event.Jet_btagDeepFlavB[ijet] >= bjet_id: continue
            selected_idx['jetsB_M'].append(ijet)
            #tight working point
            bjet_id = 10000
            if year=="2016APV": bjet_id = 0.6502 #L,M,T: 0.0508,0.2598,0.6502 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16preVFP   
            if year=="2016": bjet_id = 0.6377 #L,M,T: 0.0480,0.2489,0.6377 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16postVFP
            if year=="2017": bjet_id = 0.7476 #L,M,T: 0.0532,0.3040,0.7476 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL17
            if year=="2018": bjet_id = 0.7100 #L,M,T: 0.0490,0.2783,0.7100 see https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL18
            if not event.Jet_btagDeepFlavB[ijet] >= bjet_id: continue
            selected_idx['jetsB_T'].append(ijet)

def calculate_HT(event,selectedJets):
    HT = 0.0 
    for ijet in range(len(selectedJets)): HT = HT + event.Jet_pt[selectedJets[ijet]]
    return HT

def calculate_ST(toplist):
    ST = 0.0 
    if (len(toplist)==0): ST = -1.0
    else:
        for itop in range(len(toplist)): ST = ST + toplist[itop].Pt()
    return ST

def save_mass(self, num_top, particle_list, list_name):
    for i in range(0, num_top): exec("self.out.{}_mass{}[0] = -1".format(list_name, i))
    for itop in range(0, min(len(particle_list), num_top)): exec("self.out.{}_mass{}[0] = particle_list[itop].M()".format(list_name, itop))

def save_chi2(self, num_top, chi2_list, name):
    for i in range(0,num_top): exec('self.out.{}_{}[0] = -1'.format(name, i))
    for itop in range(0,min(len(chi2_list),num_top)): exec('self.out.{}_{}[0] = chi2_list[itop]'.format(name, itop))

def save_4mass(self, num_top, particle_list, tagger_list, particle_name):
    for i in range(0, num_top):
        exec('self.out.{}_mass{}[0] = -1'.format(particle_name, i))
        exec('self.out.{}_mass{}_boosted[0] = -1'.format(particle_name, i))
        #exec('self.out.{}_mass{}_partially_boosted[0] = -1'.format(particle_name, i))
        exec('self.out.{}_mass{}_hadronic[0] = -1'.format(particle_name, i))
        exec('self.out.{}_mass{}_leptonic[0] = -1'.format(particle_name, i))
    for itop in range(0, min(len(particle_list), num_top)):
        exec('self.out.{}_mass{}[0] = particle_list[itop].M()'.format(particle_name, itop))
        if tagger_list[itop] == 0: exec('self.out.{}_mass{}_boosted[0] = particle_list[itop].M()'.format(particle_name, itop))
        else: exec('self.out.{}_mass{}_boosted[0] = -1'.format(particle_name, itop))
        #if tagger_list[itop] == 1: exec('self.out.{}_mass{}_partially_boosted[0] = particle_list[itop].M()'.format(particle_name, itop))
        #else: exec('self.out.{}_mass{}_partially_boosted[0] = -1'.format(particle_name, itop))
        if tagger_list[itop] == 2: exec('self.out.{}_mass{}_hadronic[0] = particle_list[itop].M()'.format(particle_name, itop))
        else: exec('self.out.{}_mass{}_hadronic[0] = -1'.format(particle_name, itop))
        if tagger_list[itop] == 3: exec('self.out.{}_mass{}_leptonic[0] = particle_list[itop].M()'.format(particle_name, itop))
        else: exec('self.out.{}_mass{}_leptonic[0] = -1'.format(particle_name, itop))

def save_pt_eta_particle(event, self, num_lep, object_idx, object_name, particle_type):
    pt_array_name = particle_type + '_pt'
    eta_array_name = particle_type + '_eta'
    exec('self.out.num_{}[0] = {}'.format(object_name, len(object_idx)))
    for i in range(0,num_lep):
        exec('self.out.{}{}_pt[0] = -1'.format(object_name, i))
        exec('self.out.{}{}_eta[0] = 9999'.format(object_name, i))
    for ilep in range(0, len(object_idx)):
        exec('self.out.{}{}_pt[0] = {}'.format(object_name, ilep, event[pt_array_name][object_idx[0]]))
        exec('self.out.{}{}_eta[0] = {}'.format(object_name, ilep, event[eta_array_name][object_idx[0]]))

def save_multiplicity_3wp(self, selected_jetsL_idx, selected_jetsM_idx, selected_jetsT_idx, jets_name):
    exec('self.out.num_{}L[0] = {}'.format(jets_name,len(selected_jetsL_idx)))
    exec('self.out.num_{}M[0] = {}'.format(jets_name,len(selected_jetsM_idx)))
    exec('self.out.num_{}T[0] = {}'.format(jets_name,len(selected_jetsT_idx)))

def pt_decrease(top_list):
    top_pt_all = []
    top_all = []
    sorted_pt = []
    sorted_top = []
    for index in range(0,len(top_list)):
        top_all.append(top_list[index])
        top_pt_all.append(top_list[index].Pt())
    if (len(top_list)>0):
        sorted_pt_top = sorted(zip(top_pt_all,top_all), key=lambda x:x[0])
        sorted_pt, sorted_top = list(map(list, list(zip(*sorted_pt_top))))
        sorted_pt.reverse()
        sorted_top.reverse()
    return (sorted_pt,sorted_top)

def pt_decrease_without_boosted_top(top_list):
    top_pt_all = []
    top_all = []
    sorted_pt = []
    sorted_top = []
    for index in range(1,len(top_list)):
        top_all.append(top_list[index])
        top_pt_all.append(top_list[index].Pt())
    if (len(top_all)>0):
        sorted_pt_top = sorted(zip(top_pt_all,top_all), key=lambda x:x[0])
        sorted_pt, sorted_top = list(map(list, list(zip(*sorted_pt_top))))
        sorted_pt.reverse()
        sorted_top.reverse()
    return (sorted_pt,sorted_top)
  
def closest_dR(top_list):
    dR = 9999.0
    tagger_2top = []
    dR_2top = []
    for itop in range(0,len(top_list)):
        for jtop in range(itop+1,len(top_list)):
            if (top_list[itop].DeltaR(top_list[jtop])<dR): 
                dR = top_list[itop].DeltaR(top_list[jtop])
                tagger_2top = [itop,jtop]
                dR_2top = [dR]
    return (dR_2top, tagger_2top)

def closest_dR_with_boosted_top(top_list):
    dR = 9999.0
    tagger_top = []
    dR_2top = []
    for itop in range(1,len(top_list)):
        if (top_list[itop].DeltaR(top_list[0])<dR): 
            dR = top_list[itop].DeltaR(top_list[0])
            tagger_top = [itop]
            dR_2top = [dR]
    return (dR_2top, tagger_top)

def highest_mass(top_list):
    zprime_mass = 0.0
    position_2top=[]
    reco_zprime_mass=[]
    for itop in range(0,len(top_list)):
        for jtop in range(itop+1,len(top_list)):
            if ((top_list[itop]+top_list[jtop]).M()>zprime_mass):
                zprime_mass = (top_list[itop]+top_list[jtop]).M()
                position_2top=[itop,jtop]
                reco_zprime_mass=[zprime_mass]
    return (reco_zprime_mass,position_2top)

def highest_mass_with_boosted_top(top_list):
    zprime_mass = 0.0
    position_top=[]
    reco_zprime_mass=[]
    for jtop in range(1,len(top_list)):
        if ((top_list[0]+top_list[jtop]).M()>zprime_mass):
            zprime_mass = (top_list[0]+top_list[jtop]).M()
            position_top=[jtop]
            reco_zprime_mass=[zprime_mass]
    return (reco_zprime_mass,position_top)

def get_mu_trigSF(year, trigger_file, muon_pt, muon_abseta):
    trig_weight = 1  
    trig_weight_up = 1 
    trig_weight_down = 1
    binX = 0
    binY = 0
    if(muon_pt<=30): binY = 1
    if(muon_pt>30 and muon_pt<=40):   binY = 2
    if(muon_pt>40 and muon_pt<=50):   binY = 3
    if(muon_pt>50 and muon_pt<=60):   binY = 4
    if(muon_pt>60 and muon_pt<=120):  binY = 5
    if(muon_pt>120):   binY = 6
    if(muon_abseta<0.9):   binX = 1
    if(muon_abseta>=0.9 and muon_abseta<1.2): binX = 2
    if(muon_abseta>=1.2 and muon_abseta<2.1): binX = 3
    if(muon_abseta>=2.1 and muon_abseta<2.4): binX = 4
    trigger_hist = trigger_file.Get("SF_2D")
    trig_weight = trigger_hist.GetBinContent(binX,binY)
    trig_weight_up = trigger_hist.GetBinContent(binX,binY)+trigger_hist.GetBinError(binX,binY)
    trig_weight_down = trigger_hist.GetBinContent(binX,binY)-trigger_hist.GetBinError(binX,binY)
    return trig_weight, trig_weight_up, trig_weight_down

def get_ele_trigSF(year, trigger_file, electron_pt, electron_eta):
    trig_weight = 1  
    trig_weight_up = 1 
    trig_weight_down = 1
    binX = 0
    binY = 0
    if year == '2016' or year == '2016APV':
        if(electron_pt<=26):   binX = 1
        if(electron_pt>26 and electron_pt<=35):   binX = 2
        if(electron_pt>35 and electron_pt<=50):   binX = 3
        if(electron_pt>50 and electron_pt<=75):   binX = 4
        if(electron_pt>75 and electron_pt<=100):  binX = 5
        if(electron_pt>100):   binX = 6
    if year == '2017' or year == '2018':
        if(electron_pt<=20):   binX = 1
        if(electron_pt>20 and electron_pt<=33):   binX = 2
        if(electron_pt>33 and electron_pt<=50):   binX = 3
        if(electron_pt>50 and electron_pt<=75):   binX = 4
        if(electron_pt>75 and electron_pt<=100):  binX = 5
        if(electron_pt>100):   binX = 6
    if(electron_eta<=-2.0):    
        if year == '2016': binY = 8
        if year == '2017' or year == '2018' or year == '2016APV':    binY = 1
    if(electron_eta>-2.0 and electron_eta<=-1.566):   binY = 2
    if(electron_eta>-1.444 and electron_eta<=-0.8):   binY = 3
    if(electron_eta>-0.8 and electron_eta<=0.0):      binY = 4
    if(electron_eta>0.0 and electron_eta<=0.8):       binY = 5
    if(electron_eta>=0.8 and electron_eta<1.444):     binY = 6
    if(electron_eta>=1.566 and electron_eta<2.0):     binY = 7
    if(electron_eta>=2.0):                            binY = 8
    trigger_hist = trigger_file.Get("SF2D")
    trig_weight = trigger_hist.GetBinContent(binX,binY)
    trig_weight_up = trigger_hist.GetBinContent(binX,binY)+trigger_hist.GetBinError(binX,binY)
    trig_weight_down = trigger_hist.GetBinContent(binX,binY)-trigger_hist.GetBinError(binX,binY)
    return trig_weight, trig_weight_up, trig_weight_down

def get_mu_IDSF(ID_file, hist_name, muon_pt, muon_abseta):
    mu_weight = 1  
    mu_weight_up = 1 
    mu_weight_down = 1
    if(muon_pt<=20): binY = 1
    if(muon_pt>20 and muon_pt<=25):   binY = 2
    if(muon_pt>25 and muon_pt<=30):   binY = 3
    if(muon_pt>30 and muon_pt<=40):   binY = 4
    if(muon_pt>40 and muon_pt<=50):   binY = 5
    if(muon_pt>50 and muon_pt<=60):   binY = 6
    if(muon_pt>60):  binY = 7
    if(muon_abseta<0.9): binX = 1
    if(muon_abseta>=0.9 and muon_abseta<1.2): binX = 2
    if(muon_abseta>=1.2 and muon_abseta<2.1): binX = 3
    if(muon_abseta>=2.1 and muon_abseta<2.4): binX = 4
    ID_hist = ID_file.Get(hist_name)
    mu_weight = ID_hist.GetBinContent(binX,binY)
    mu_weight_up = ID_hist.GetBinContent(binX,binY)+ID_hist.GetBinError(binX,binY)
    mu_weight_down = ID_hist.GetBinContent(binX,binY)-ID_hist.GetBinError(binX,binY)
    return mu_weight, mu_weight_up, mu_weight_down

def get_mu_PFIsoSF(ID_file, muon_pt, muon_abseta):
    mu_iso_weight = 1  
    mu_iso_weight_up = 1 
    mu_iso_weight_down = 1
    if(muon_pt<=20): binY = 1
    if(muon_pt>20 and muon_pt<=25):   binY = 2
    if(muon_pt>25 and muon_pt<=30):   binY = 3
    if(muon_pt>30 and muon_pt<=40):   binY = 4
    if(muon_pt>40 and muon_pt<=50):   binY = 5
    if(muon_pt>50 and muon_pt<=60):   binY = 6
    if(muon_pt>60):  binY = 7
    if(muon_abseta<0.9): binX = 1
    if(muon_abseta>=0.9 and muon_abseta<1.2): binX = 2
    if(muon_abseta>=1.2 and muon_abseta<2.1): binX = 3
    if(muon_abseta>=2.1 and muon_abseta<2.4): binX = 4
    ID_hist = ID_file.Get("SF")
    mu_iso_weight = ID_hist.GetBinContent(binX,binY)
    mu_iso_weight_up = ID_hist.GetBinContent(binX,binY)+ID_hist.GetBinError(binX,binY)
    mu_iso_weight_down = ID_hist.GetBinContent(binX,binY)-ID_hist.GetBinError(binX,binY)
    return mu_iso_weight, mu_iso_weight_up, mu_iso_weight_down

def get_ele_IDSF(year, ID_file, hist_name, electron_pt, electron_eta):
    electronWeight = 1  
    electronWeightUp = 1 
    electronWeightDown = 1
    if(electron_pt<=20):       binY = 1
    if(electron_pt>20 and electron_pt<=35):   binY = 2
    if(electron_pt>35 and electron_pt<=50):   binY = 3
    if(electron_pt>50 and electron_pt<=100):  binY = 4
    if year == '2016' or year == '2016APV':
        if(electron_pt>100):   binY = 5
    if year == '2017' or year == '2018':
        if(electron_pt>100 and electron_pt<=200):   binY = 5
        if(electron_pt>200):   binY = 6
    if(electron_eta<-2.0):     binX = 1
    if(electron_eta>=-2.0 and electron_eta<=-1.566): binX = 2
    if(electron_eta>=-1.444 and electron_eta<-0.8): binX = 4
    if(electron_eta>=-0.8 and electron_eta<0):      binX = 5
    if(electron_eta>=0 and electron_eta<0.8):       binX = 6
    if(electron_eta>=0.8 and electron_eta<=1.444):   binX = 7
    if(electron_eta>=1.566 and electron_eta<2.0):   binX = 9
    if(electron_eta>=2.0):     binX = 10
    ID_hist = ID_file.Get(hist_name)
    electronWeight = ID_hist.GetBinContent(binX,binY)
    electronWeightUp = ID_hist.GetBinContent(binX,binY)+ID_hist.GetBinError(binX,binY)
    electronWeightDown = ID_hist.GetBinContent(binX,binY)-ID_hist.GetBinError(binX,binY)
    return electronWeight, electronWeightUp, electronWeightDown

def getPileupWeight (event, puFile, puFileUp, puFileDown, year):
    if year == '2018':
        nPUMax = 99
        npuProbs = [8.89374611122e-07, 1.1777062868e-05, 3.99725585118e-05, 0.000129888015252, 0.000265224848687, 0.000313088635109, 0.000353781668514, 0.000508787237162, 0.000873670065767, 0.00147166880932, 0.00228230649018, 0.00330375581273, 0.00466047608406, 0.00624959203029, 0.00810375867901, 0.010306521821, 0.0129512453978, 0.0160303925502, 0.0192913204592, 0.0223108613632, 0.0249798930986, 0.0273973789867, 0.0294402350483, 0.031029854302, 0.0324583524255, 0.0338264469857, 0.0351267479019, 0.0360320204259, 0.0367489568401, 0.0374133183052, 0.0380352633799, 0.0386200967002, 0.039124376968, 0.0394201612616, 0.0394673457109, 0.0391705388069, 0.0384758587461, 0.0372984548399, 0.0356497876549, 0.0334655175178, 0.030823567063, 0.0278340752408, 0.0246009685048, 0.0212676009273, 0.0180250593982, 0.0149129830776, 0.0120582333486, 0.00953400069415, 0.00738546929512, 0.00563442079939, 0.00422052915668, 0.00312446316347, 0.00228717533955, 0.00164064894334, 0.00118425084792, 0.000847785826565, 0.000603466454784, 0.000419347268964, 0.000291768785963, 0.000199761337863, 0.000136624574661, 9.46855200945e-05, 6.80243180179e-05, 4.94806013765e-05, 3.53122628249e-05, 2.556765786e-05, 1.75845711623e-05, 1.23828210848e-05, 9.31669724108e-06, 6.0713272037e-06, 3.95387384933e-06, 2.02760874107e-06, 1.22535149516e-06, 9.79612472109e-07, 7.61730246474e-07, 4.2748847738e-07, 2.41170461205e-07, 1.38701083552e-07, 3.37678010922e-08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if year == '2017':
        nPUMax = 99
        npuProbs = [1.1840841518e-05, 3.46661037703e-05, 8.98772521472e-05, 7.47400487733e-05, 0.000123005176624, 0.000156501700614, 0.000154660478659, 0.000177496185603, 0.000324149805611, 0.000737524009713, 0.00140432980253, 0.00244424508696, 0.00380027898037, 0.00541093042612, 0.00768803501793, 0.010828224552, 0.0146608623707, 0.01887739113, 0.0228418813823, 0.0264817796874, 0.0294637401336, 0.0317960986171, 0.0336645950831, 0.0352638818387, 0.036869429333, 0.0382797316998, 0.039386705577, 0.0398389681346, 0.039646211131, 0.0388392805703, 0.0374195678161, 0.0355377892706, 0.0333383902828, 0.0308286549265, 0.0282914440969, 0.0257860718304, 0.02341635055, 0.0213126338243, 0.0195035612803, 0.0181079838989, 0.0171991315458, 0.0166377598339, 0.0166445341361, 0.0171943735369, 0.0181980997278, 0.0191339792146, 0.0198518804356, 0.0199714909193, 0.0194616474094, 0.0178626975229, 0.0153296785464, 0.0126789254325, 0.0100766041988, 0.00773867100481, 0.00592386091874, 0.00434706240169, 0.00310217013427, 0.00213213401899, 0.0013996000761, 0.000879148859271, 0.000540866009427, 0.000326115560156, 0.000193965828516, 0.000114607606623, 6.74262828734e-05, 3.97805301078e-05, 2.19948704638e-05, 9.72007976207e-06, 4.26179259146e-06, 2.80015581327e-06, 1.14675436465e-06, 2.52452411995e-07, 9.08394910044e-08, 1.14291987912e-08, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if year == '2016' or year == '2016APV':
        nPUMax = 99
        npuProbs = [1.00402360149e-05, 5.76498797172e-05, 7.37891400294e-05, 0.000110932895295, 0.000158857714773, 0.000368637432599, 0.000893114107873, 0.00189700774575, 0.00358880167437, 0.00636052573486, 0.0104173961179, 0.0158122597405, 0.0223785660712, 0.0299186888073, 0.0380275944896, 0.0454313901624, 0.0511181088317, 0.0547434577348, 0.0567906239028, 0.0577145461461, 0.0578176902735, 0.0571251566494, 0.0555456541498, 0.053134383488, 0.0501519041462, 0.0466815838899, 0.0429244592524, 0.0389566776898, 0.0348507152776, 0.0307356862528, 0.0267712092206, 0.0229720184534, 0.0193388653099, 0.0159602510813, 0.0129310510552, 0.0102888654183, 0.00798782770975, 0.00606651703058, 0.00447820948367, 0.00321589786478, 0.0022450422045, 0.00151447388514, 0.000981183695515, 0.000609670479759, 0.000362193408119, 0.000211572646801, 0.000119152364744, 6.49133515399e-05, 3.57795801581e-05, 1.99043569043e-05, 1.13639319832e-05, 6.49624103579e-06, 3.96626216416e-06, 2.37910222874e-06, 1.50997403362e-06, 1.09816650247e-06, 7.31298519122e-07, 6.10398791529e-07, 3.74845774388e-07, 2.65177281359e-07, 2.01923536742e-07, 1.39347583555e-07, 8.32600052913e-08, 6.04932421298e-08, 6.52536630583e-08, 5.90574603808e-08, 2.29162474068e-08, 1.97294602668e-08, 1.7731096903e-08, 3.57547932012e-09, 1.35039815662e-09, 8.50071242076e-09, 5.0279187473e-09, 4.93736669066e-10, 8.13919708923e-10, 5.62778926097e-09, 5.15140589469e-10, 8.21676746568e-10, 0.0, 1.49166873577e-09, 8.43517992503e-09, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    s = 0
    sUp = 0
    sDown = 0
    result = [0 for i in range(0, nPUMax)]
    resultUp = [0 for i in range(0, nPUMax)]
    resultDown = [0 for i in range(0, nPUMax)]
    puHist = puFile.Get("pileup")
    puHistUp = puFileUp.Get("pileup")
    puHistDown = puFileDown.Get("pileup")
    for npu in range(0, nPUMax):
        npu_estimated = puHist.GetBinContent(puHist.GetXaxis().FindBin(npu))
        npu_estimatedUp = puHistUp.GetBinContent(puHistUp.GetXaxis().FindBin(npu))
        npu_estimatedDown = puHistDown.GetBinContent(puHistDown.GetXaxis().FindBin(npu))
        if (npuProbs[npu] != 0):
            result[npu] = npu_estimated / npuProbs[npu]
            resultUp[npu] = npu_estimatedUp / npuProbs[npu]
            resultDown[npu] = npu_estimatedDown / npuProbs[npu]
        else:
            result[npu] = 0
            resultUp[npu] = 0
            resultDown[npu] = 0
        s = s + npu_estimated
        sUp = sUp + npu_estimatedUp
        sDown = sDown + npu_estimatedDown
    for npu in range(0, nPUMax):
        result[npu] =  result[npu]/s
        resultUp[npu] =  resultUp[npu]/sUp
        resultDown[npu] =  resultDown[npu]/sDown
    Pileup_nTrueInt = event.Pileup_nTrueInt
    if event.Pileup_nTrueInt>=nPUMax:
        Pileup_nTrueInt = nPUMax-1
    puWeight = result[int(Pileup_nTrueInt)]
    puWeightUp = resultUp[int(Pileup_nTrueInt)]
    puWeightDown = resultDown[int(Pileup_nTrueInt)]
    return puWeight, puWeightUp, puWeightDown

def getTopTagWeight(event, year, boosted_top_list):  #medium WP
    topTagWeight = 1
    topTagWeightUp = 1
    topTagWeightDown = 1
    fatjets = Collection(event, 'FatJet')
    for ifatjet in range(len(boosted_top_list)):
        topTagSF = 1
        topTagSFUp = 1
        topTagSFDown = 1
        if 300 <= event.FatJet_pt[boosted_top_list[ifatjet]] <= 400: 
            if year == '2018': 
                topTagSF = 1.19
                topTagSFUp = 0.12
                topTagSFDown = 0.12
            if year == '2017':
                topTagSF = 1.11
                topTagSFUp = 0.08
                topTagSFDown = 0.08
            if year == '2016':
                topTagSF = 1.07
                topTagSFUp = 0.10
                topTagSFDown = 0.10
            if year == '2016APV':
                topTagSF = 1.23
                topTagSFUp = 0.13
                topTagSFDown = 0.14
        if 400 <= event.FatJet_pt[boosted_top_list[ifatjet]] <= 480:
            if year == '2018': 
                topTagSF = 0.98
                topTagSFUp = 0.04
                topTagSFDown = 0.04
            if year == '2017':
                topTagSF = 1.01
                topTagSFUp = 0.04
                topTagSFDown = 0.04
            if year == '2016':
                topTagSF = 0.97
                topTagSFUp = 0.05
                topTagSFDown = 0.05
            if year == '2016APV':
                topTagSF = 1.07
                topTagSFUp = 0.13
                topTagSFDown = 0.05
        if 480 <= event.FatJet_pt[boosted_top_list[ifatjet]] <= 600:
            if year == '2018': 
                topTagSF = 0.96
                topTagSFUp = 0.03
                topTagSFDown = 0.03
            if year == '2017':
                topTagSF = 1.05
                topTagSFUp = 0.04
                topTagSFDown = 0.04
            if year == '2016':
                topTagSF = 1.03
                topTagSFUp = 0.05
                topTagSFDown = 0.04
            if year == '2016APV':
                topTagSF = 1.06
                topTagSFUp = 0.06
                topTagSFDown = 0.05
        if 600 <= event.FatJet_pt[boosted_top_list[ifatjet]] <= 1200:
            if year == '2018': 
                topTagSF = 0.97
                topTagSFUp = 0.05
                topTagSFDown = 0.05
            if year == '2017':
                topTagSF = 1.00
                topTagSFUp = 0.05
                topTagSFDown = 0.05
            if year == '2016':
                topTagSF = 1.34
                topTagSFUp = 0.24
                topTagSFDown = 0.27
            if year == '2016APV':
                topTagSF = 1.10
                topTagSFUp = 0.29
                topTagSFDown = 0.10
        topTagWeight = topTagWeight*topTagSF
        topTagWeightUp = topTagWeightUp*topTagSFUp
        topTagWeightDown = topTagWeightDown*topTagSFDown
    return topTagWeight, topTagWeightUp, topTagWeightDown

def fillbtagEfficiencies(event,selectedJetsIdx,btagLooseWP,btagMediumWP,btagTightWP,histsBtagging):
    for ijet in range(len(selectedJetsIdx)):
        flav = event.Jet_hadronFlavour[selectedJetsIdx[ijet]]
        is_taggedT = (event.Jet_btagDeepFlavB[selectedJetsIdx[ijet]]>btagTightWP)
        is_taggedM = (event.Jet_btagDeepFlavB[selectedJetsIdx[ijet]]>btagMediumWP)
        is_taggedL = (event.Jet_btagDeepFlavB[selectedJetsIdx[ijet]]>btagLooseWP)
        pt = event.Jet_pt[selectedJetsIdx[ijet]]
        eta = abs(event.Jet_eta[selectedJetsIdx[ijet]])
        if(flav == 5):
            histsBtagging[0].Fill(pt, eta)
            histsBtagging[1].Fill(pt, eta)
            histsBtagging[2].Fill(pt, eta)
            if(is_taggedT): histsBtagging[3].Fill(pt, eta)
            if(is_taggedM): histsBtagging[4].Fill(pt, eta)
            if(is_taggedL): histsBtagging[5].Fill(pt, eta)
        elif(flav == 4):
            histsBtagging[6].Fill(pt, eta)
            histsBtagging[7].Fill(pt, eta)
            histsBtagging[8].Fill(pt, eta)
            if(is_taggedT): histsBtagging[9].Fill(pt, eta)
            if(is_taggedM): histsBtagging[10].Fill(pt, eta)
            if(is_taggedL): histsBtagging[11].Fill(pt, eta)
        else:
            histsBtagging[12].Fill(pt, eta)
            histsBtagging[13].Fill(pt, eta)
            histsBtagging[14].Fill(pt, eta)
            if(is_taggedT): histsBtagging[15].Fill(pt, eta)
            if(is_taggedM): histsBtagging[16].Fill(pt, eta)
            if(is_taggedL): histsBtagging[17].Fill(pt, eta)

def readbtagSF(cset,jetpt, jet_abseta, jetflav,WP):
    minJetPt = 20
    maxJetPt = 1000
    doubleUncertainty = False
    if(jetpt<=minJetPt): 
        doubleUncertainty = True
        jetpt = minJetPt+0.1
    if(jetpt>=maxJetPt): 
        doubleUncertainty = True
        jetpt = maxJetPt-0.1
    jet_scalefactor    = 1
    jet_scalefactor_up = 1
    jet_scalefactor_do = 1
    if(jetflav==5 or jetflav==4):
        jet_scalefactor    = cset["deepJet_comb"].evaluate("central", WP, jetflav, jet_abseta, jetpt)
        jet_scalefactor_up = cset["deepJet_comb"].evaluate("up", WP, jetflav, jet_abseta, jetpt)
        jet_scalefactor_do = cset["deepJet_comb"].evaluate("down", WP, jetflav, jet_abseta, jetpt)
    else:
        jet_scalefactor    = cset["deepJet_incl"].evaluate("central", WP, jetflav, jet_abseta, jetpt)
        jet_scalefactor_up = cset["deepJet_incl"].evaluate("up", WP, jetflav, jet_abseta, jetpt) 
        jet_scalefactor_do = cset["deepJet_incl"].evaluate("down", WP, jetflav, jet_abseta, jetpt)
    if(doubleUncertainty):
        jet_scalefactor_up = 2*(jet_scalefactor_up - jet_scalefactor) + jet_scalefactor
        jet_scalefactor_do = 2*(jet_scalefactor_do - jet_scalefactor) + jet_scalefactor
    if(jet_scalefactor==0):
        jet_scalefactor    = 1
        jet_scalefactor_up = 1
        jet_scalefactor_do = 1
    return jet_scalefactor, max(abs(jet_scalefactor-jet_scalefactor_up),abs(jet_scalefactor-jet_scalefactor_do))

def readbtagSF_2016(cset,cset_4incl,jetpt, jet_abseta, jetflav,WP):
    minJetPt = 20
    maxJetPt = 1000
    doubleUncertainty = False
    if(jetpt<=minJetPt): 
        doubleUncertainty = True
        jetpt = minJetPt+0.1
    if(jetpt>=maxJetPt): 
        doubleUncertainty = True
        jetpt = maxJetPt-0.1
    jet_scalefactor    = 1
    jet_scalefactor_up = 1
    jet_scalefactor_do = 1
    if(jetflav==5 or jetflav==4):
        jet_scalefactor    = cset["deepJet_comb"].evaluate("central", WP, jetflav, jet_abseta, jetpt)
        jet_scalefactor_up = cset["deepJet_comb"].evaluate("up", WP, jetflav, jet_abseta, jetpt)
        jet_scalefactor_do = cset["deepJet_comb"].evaluate("down", WP, jetflav, jet_abseta, jetpt)
    else:
        jet_scalefactor    = cset_4incl["deepJet_incl"].evaluate("central", WP, jetflav, jet_abseta, jetpt)
        jet_scalefactor_up = cset_4incl["deepJet_incl"].evaluate("up", WP, jetflav, jet_abseta, jetpt) 
        jet_scalefactor_do = cset_4incl["deepJet_incl"].evaluate("down", WP, jetflav, jet_abseta, jetpt)
    if(doubleUncertainty):
        jet_scalefactor_up = 2*(jet_scalefactor_up - jet_scalefactor) + jet_scalefactor
        jet_scalefactor_do = 2*(jet_scalefactor_do - jet_scalefactor) + jet_scalefactor
    if(jet_scalefactor==0):
        jet_scalefactor    = 1
        jet_scalefactor_up = 1
        jet_scalefactor_do = 1
    return jet_scalefactor, max(abs(jet_scalefactor-jet_scalefactor_up),abs(jet_scalefactor-jet_scalefactor_do))

def getbtagWeight(event, btagWPvalue, selectedJetsIdx, cset, WP, histoB, histoC, histoUdsg):
    mcTag = 1.
    mcNoTag = 1.
    dataTag = 1.
    dataNoTag = 1.
    err1 = 0.
    err2 = 0.
    err3 = 0.
    err4 = 0.
    for ijet in range(len(selectedJetsIdx)):
        jetpt   = event.Jet_pt[selectedJetsIdx[ijet]]
        jeteta  = abs(event.Jet_eta[selectedJetsIdx[ijet]])
        jetflav = event.Jet_hadronFlavour[selectedJetsIdx[ijet]]
        minJetPt = 20
        maxJetPt = 1000
        if(jetpt<minJetPt): 
            jetpt = minJetPt
        if(jetpt>maxJetPt): 
            jetpt = maxJetPt
        etaBin = 1
        ptBin = 1
        if(jetpt>=20 and jetpt<=30):   ptBin = 1
        if(jetpt>30  and jetpt<=50):   ptBin = 2
        if(jetpt>50  and jetpt<=70):   ptBin = 3
        if(jetpt>70  and jetpt<=100):  ptBin = 4
        if(jetpt>100 and jetpt<=140):  ptBin = 5
        if(jetpt>140 and jetpt<=200):  ptBin = 6
        if(jetpt>200 and jetpt<=300):  ptBin = 7
        if(jetpt>300 and jetpt<=600):  ptBin = 8
        if(jetpt>600 and jetpt<=1000): ptBin = 9
        if(jetflav!=5 and jetflav!=4): ptBin = 1
        eff = 1
        if(jetflav == 5): eff = histoB.GetBinContent(ptBin,etaBin)
        elif(jetflav == 4): eff = histoC.GetBinContent(ptBin,etaBin)
        else: eff = histoUdsg.GetBinContent(ptBin,etaBin)
        SF, SFerr = readbtagSF(cset,jetpt, jeteta, jetflav,WP)
        btag = event.Jet_btagDeepFlavB[selectedJetsIdx[ijet]]
        if(btag>btagWPvalue):
            #print"passed b tag"
            #print"eff:%s" %(eff)
            mcTag *= eff
            #print"mcTag:%s" %(mcTag)
            dataTag *= eff*SF
            #print"SF:%s" %(SF)
            #print"dataTag:%s" %(dataTag)
            if(jetflav==5 or jetflav ==4):  err1 += SFerr/SF
            else: err3 += SFerr/SF
        else:
            #print"not passed b tag"
            #print"1-eff:%s" %(1-eff)
            mcNoTag *= (1- eff)
            #print"mcNoTag:%s" %(mcNoTag)
            dataNoTag *= (1- eff*SF)
            #print"SF:%s" %(SF)
            #print"dataNoTag:%s" %(dataNoTag)
            if(jetflav==5 or jetflav ==4 ): err2 += (-eff*SFerr)/(1-eff*SF)
            else: err4 +=  (-eff*SFerr)/(1-eff*SF)
    wtbtag        = 1
    wtbtagErrBC   = 0
    wtbtagErrUDSG = 0
    if((mcNoTag*mcTag)!=0): 
        wtbtag        = (dataNoTag * dataTag ) / ( mcNoTag * mcTag )
        #print"b tag weight:%s" %(wtbtag)
        #print""
    if((mcNoTag*mcTag)!=0): wtbtagErrBC   = abs(err1+err2) * wtbtag
    if((mcNoTag*mcTag)!= 0): wtbtagErrUDSG = abs(err3+err4) * wtbtag
    w_Btag     = wtbtag 
    w_BtagUp   = wtbtag+math.sqrt(wtbtagErrBC*wtbtagErrBC+wtbtagErrUDSG*wtbtagErrUDSG)
    w_BtagDown = wtbtag-math.sqrt(wtbtagErrBC*wtbtagErrBC+wtbtagErrUDSG*wtbtagErrUDSG)
    return w_Btag, w_BtagUp, w_BtagDown

def getbtagWeight_all(event, btagWPL, btagWPM, btagWPT, selectedJetsIdx, cset, histoBT, histoCT, histoUdsgT,histoBM, histoCM, histoUdsgM, histoBL, histoCL, histoUdsgL):
    mcTagT = 1.
    mcTagM = 1.
    mcTagL = 1.
    mcNoTag = 1.
    dataTagT = 1.
    dataTagM = 1.
    dataTagL = 1.
    dataNoTag = 1.
    err1 = 0.
    err2 = 0.
    err3 = 0.
    err4 = 0.
    for ijet in range(len(selectedJetsIdx)):
        jetpt   = event.Jet_pt[selectedJetsIdx[ijet]]
        jeteta  = abs(event.Jet_eta[selectedJetsIdx[ijet]])
        jetflav = event.Jet_hadronFlavour[selectedJetsIdx[ijet]]
        minJetPt = 20
        maxJetPt = 1000
        if(jetpt<minJetPt): 
            jetpt = minJetPt
        if(jetpt>maxJetPt): 
            jetpt = maxJetPt
        etaBin = 1
        ptBin = 1
        if(jetpt>=20 and jetpt<=30):   ptBin = 1
        if(jetpt>30  and jetpt<=50):   ptBin = 2
        if(jetpt>50  and jetpt<=70):   ptBin = 3
        if(jetpt>70  and jetpt<=100):  ptBin = 4
        if(jetpt>100 and jetpt<=140):  ptBin = 5
        if(jetpt>140 and jetpt<=200):  ptBin = 6
        if(jetpt>200 and jetpt<=300):  ptBin = 7
        if(jetpt>300 and jetpt<=600):  ptBin = 8
        if(jetpt>600 and jetpt<=1000): ptBin = 9
        if(jetflav!=5 and jetflav!=4): ptBin = 1
        eff_t = 1
        eff_m = 1
        eff_l = 1
        if(jetflav == 5): 
            eff_t = histoBT.GetBinContent(ptBin,etaBin)
            eff_m = histoBM.GetBinContent(ptBin,etaBin)
            eff_l = histoBL.GetBinContent(ptBin,etaBin)
        elif(jetflav == 4): 
            eff_t = histoCT.GetBinContent(ptBin,etaBin)
            eff_m = histoCM.GetBinContent(ptBin,etaBin)
            eff_l = histoCL.GetBinContent(ptBin,etaBin)
        else: 
            eff_t = histoUdsgT.GetBinContent(ptBin,etaBin)
            eff_m = histoUdsgM.GetBinContent(ptBin,etaBin)
            eff_l = histoUdsgL.GetBinContent(ptBin,etaBin)
        SF_t, SFerr_t = readbtagSF(cset,jetpt, jeteta, jetflav,'T')
        SF_m, SFerr_m = readbtagSF(cset,jetpt, jeteta, jetflav,'M')
        SF_l, SFerr_l = readbtagSF(cset,jetpt, jeteta, jetflav,'L')
        btag = event.Jet_btagDeepFlavB[selectedJetsIdx[ijet]]
        if(btag>btagWPT):
            #print"passed b tag"
            #print"eff:%s" %(eff)
            mcTagT = mcTagT*eff_t
            #print"mcTag:%s" %(mcTag)
            dataTagT = dataTagT*(eff_t*SF_t)
            #print"SF:%s" %(SF)
            #print"dataTag:%s" %(dataTag)
            if(jetflav==5 or jetflav ==4):  err1 += SFerr_t/SF_t
            else: err3 += SFerr_t/SF_t
        elif(btagWPM<btag<btagWPT):
            #print"passed b tag"
            #print"eff:%s" %(eff)
            mcTagM = mcTagM*(eff_m-eff_t)
            #print"mcTag:%s" %(mcTag)
            dataTagM = dataTagM*(eff_m*SF_m-eff_t*SF_t)
            #print"SF:%s" %(SF)
            #print"dataTag:%s" %(dataTag)
            if(jetflav==5 or jetflav ==4):  err1 += (SFerr_m/SF_m - SFerr_t/SF_t)
            else: err3 += (SFerr_m/SF_m - SFerr_t/SF_t)
        elif(btagWPL<btag<btagWPM):
            #print"passed b tag"
            #print"eff:%s" %(eff)
            mcTagL = mcTagL*(eff_l-eff_m)
            #print"mcTag:%s" %(mcTag)
            dataTagL = dataTagL*(eff_l*SF_l-eff_m*SF_m)
            #print"SF:%s" %(SF)
            #print"dataTag:%s" %(dataTag)
            if(jetflav==5 or jetflav ==4):  err1 += (SFerr_l/SF_l - SFerr_m/SF_m)
            else: err3 += (SFerr_l/SF_l - SFerr_m/SF_m)
        else:
            #print"not passed b tag"
            #print"1-eff:%s" %(1-eff)
            mcNoTag *= (1- eff_l)
            #print"mcNoTag:%s" %(mcNoTag)
            dataNoTag *= (1- eff_l*SF_l)
            #print"SF:%s" %(SF)
            #print"dataNoTag:%s" %(dataNoTag)
            if(jetflav==5 or jetflav ==4 ): err2 += (-eff_l*SFerr_l)/(1-eff_l*SF_l)
            else: err4 +=  (-eff_l*SFerr_l)/(1-eff_l*SF_l)
    wtbtag        = 1
    wtbtagErrBC   = 0
    wtbtagErrUDSG = 0
    if((mcNoTag*mcTagT*mcTagM*mcTagL)!=0): 
        wtbtag        = (dataNoTag * dataTagT * dataTagM * dataTagL ) / ( mcNoTag * mcTagT *mcTagM *mcTagL )
        #print"b tag weight:%s" %(wtbtag)
        #print""
    if((mcNoTag*mcTagT*mcTagM*mcTagL)!=0): wtbtagErrBC   = abs(err1+err2) * wtbtag
    if((mcNoTag*mcTagT*mcTagM*mcTagL)!= 0): wtbtagErrUDSG = abs(err3+err4) * wtbtag
    w_Btag     = wtbtag 
    w_BtagUp   = wtbtag+math.sqrt(wtbtagErrBC*wtbtagErrBC+wtbtagErrUDSG*wtbtagErrUDSG)
    w_BtagDown = wtbtag-math.sqrt(wtbtagErrBC*wtbtagErrBC+wtbtagErrUDSG*wtbtagErrUDSG)
    return w_Btag, w_BtagUp, w_BtagDown

def getbtagWeight_2016(event, btagWPL, btagWPM, btagWPT, selectedJetsIdx, cset, cset_4incl, histoBT, histoCT, histoUdsgT,histoBM, histoCM, histoUdsgM, histoBL, histoCL, histoUdsgL):
    mcTagT = 1.
    mcTagM = 1.
    mcTagL = 1.
    mcNoTag = 1.
    dataTagT = 1.
    dataTagM = 1.
    dataTagL = 1.
    dataNoTag = 1.
    err1 = 0.
    err2 = 0.
    err3 = 0.
    err4 = 0.
    for ijet in range(len(selectedJetsIdx)):
        jetpt   = event.Jet_pt[selectedJetsIdx[ijet]]
        jeteta  = abs(event.Jet_eta[selectedJetsIdx[ijet]])
        jetflav = event.Jet_hadronFlavour[selectedJetsIdx[ijet]]
        minJetPt = 20
        maxJetPt = 1000
        if(jetpt<minJetPt): 
            jetpt = minJetPt
        if(jetpt>maxJetPt): 
            jetpt = maxJetPt
        etaBin = 1
        ptBin = 1
        if(jetpt>=20 and jetpt<=30):   ptBin = 1
        if(jetpt>30  and jetpt<=50):   ptBin = 2
        if(jetpt>50  and jetpt<=70):   ptBin = 3
        if(jetpt>70  and jetpt<=100):  ptBin = 4
        if(jetpt>100 and jetpt<=140):  ptBin = 5
        if(jetpt>140 and jetpt<=200):  ptBin = 6
        if(jetpt>200 and jetpt<=300):  ptBin = 7
        if(jetpt>300 and jetpt<=600):  ptBin = 8
        if(jetpt>600 and jetpt<=1000): ptBin = 9
        if(jetflav!=5 and jetflav!=4): ptBin = 1
        eff_t = 1
        eff_m = 1
        eff_l = 1
        if(jetflav == 5): 
            eff_t = histoBT.GetBinContent(ptBin,etaBin)
            eff_m = histoBM.GetBinContent(ptBin,etaBin)
            eff_l = histoBL.GetBinContent(ptBin,etaBin)
        elif(jetflav == 4): 
            eff_t = histoCT.GetBinContent(ptBin,etaBin)
            eff_m = histoCM.GetBinContent(ptBin,etaBin)
            eff_l = histoCL.GetBinContent(ptBin,etaBin)
        else: 
            eff_t = histoUdsgT.GetBinContent(ptBin,etaBin)
            eff_m = histoUdsgM.GetBinContent(ptBin,etaBin)
            eff_l = histoUdsgL.GetBinContent(ptBin,etaBin)
        SF_t, SFerr_t = readbtagSF_2016(cset,cset_4incl,jetpt, jeteta, jetflav,'T')
        SF_m, SFerr_m = readbtagSF_2016(cset,cset_4incl,jetpt, jeteta, jetflav,'M')
        SF_l, SFerr_l = readbtagSF_2016(cset,cset_4incl,jetpt, jeteta, jetflav,'L')
        btag = event.Jet_btagDeepFlavB[selectedJetsIdx[ijet]]
        if(btag>btagWPT):
            mcTagT = mcTagT*eff_t
            dataTagT = dataTagT*(eff_t*SF_t)
            if(jetflav==5 or jetflav ==4):  err1 += SFerr_t/SF_t
            else: err3 += SFerr_t/SF_t
        elif(btagWPM<btag<btagWPT):
            mcTagM = mcTagM*(eff_m-eff_t)
            dataTagM = dataTagM*(eff_m*SF_m-eff_t*SF_t)
            if(jetflav==5 or jetflav ==4):  err1 += (SFerr_m/SF_m - SFerr_t/SF_t)
            else: err3 += (SFerr_m/SF_m - SFerr_t/SF_t)
        elif(btagWPL<btag<btagWPM):
            mcTagL = mcTagL*(eff_l-eff_m)
            dataTagL = dataTagL*(eff_l*SF_l-eff_m*SF_m)
            if(jetflav==5 or jetflav ==4):  err1 += (SFerr_l/SF_l - SFerr_m/SF_m)
            else: err3 += (SFerr_l/SF_l - SFerr_m/SF_m)
        else:
            mcNoTag *= (1- eff_l)
            dataNoTag *= (1- eff_l*SF_l)
            if(jetflav==5 or jetflav ==4 ): err2 += (-eff_l*SFerr_l)/(1-eff_l*SF_l)
            else: err4 +=  (-eff_l*SFerr_l)/(1-eff_l*SF_l)
    wtbtag        = 1
    wtbtagErrBC   = 0
    wtbtagErrUDSG = 0
    if((mcNoTag*mcTagT*mcTagM*mcTagL)!=0): 
        wtbtag        = (dataNoTag * dataTagT * dataTagM * dataTagL ) / ( mcNoTag * mcTagT *mcTagM *mcTagL )
    if((mcNoTag*mcTagT*mcTagM*mcTagL)!=0): wtbtagErrBC   = abs(err1+err2) * wtbtag
    if((mcNoTag*mcTagT*mcTagM*mcTagL)!= 0): wtbtagErrUDSG = abs(err3+err4) * wtbtag
    w_Btag     = wtbtag 
    w_BtagUp   = wtbtag+math.sqrt(wtbtagErrBC*wtbtagErrBC+wtbtagErrUDSG*wtbtagErrUDSG)
    w_BtagDown = wtbtag-math.sqrt(wtbtagErrBC*wtbtagErrBC+wtbtagErrUDSG*wtbtagErrUDSG)
    return w_Btag, w_BtagUp, w_BtagDown