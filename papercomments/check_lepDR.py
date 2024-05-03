import ROOT
import hist
import matplotlib.pyplot as plt
import mplhep as hep

#define a TChain to combine all signal samples
sample_path = "/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggh/"
chain = ROOT.TChain("Ana/passedEvents")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M400_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M600_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M700_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v2_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M800_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M900_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M1000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M1500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v2_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M2000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M2500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
chain.Add(f"{sample_path}GluGluHToZZTo2L2Q_M3000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")

#define a function a compte deltaR
#def deltaR(eta1, phi1, eta2, phi2):
#    deta = eta1 - eta2
#    dphi = phi1 - phi2
#    if dphi > ROOT.TMath.Pi():
#        dphi -= 2*ROOT.TMath.Pi()
#    if dphi < -ROOT.TMath.Pi():
#        dphi += 2*ROOT.TMath.Pi()
#    return ROOT.TMath.Sqrt(deta*deta + dphi*dphi)

import numpy as np
import math

def deltaR( eta1, phi1, eta2, phi2):
    if abs(phi1-phi2)>np.pi:
        dR = math.sqrt((2.*np.pi - abs(phi1 - phi2)) * (2.*np.pi - abs(phi1 - phi2)) + (eta1 - eta2) * (eta1 - eta2))
    else:
        dR = math.sqrt((phi1 - phi2) * (phi1 - phi2) + (eta1 - eta2) * (eta1 - eta2))
    return dR

#loop over the chain and compte DR fill the histogram DR vs GEN_H_mass
h_ee = hist.Hist(
              hist.axis.Regular(100, 0, 3000, name="GEN_H_mass", label="GEN_H_mass [GeV]"),
              hist.axis.Regular(30, 0, 3, name="DR", label="DR")
              )
h_mumu = hist.Hist(
                hist.axis.Regular(100, 0, 3000, name="GEN_H_mass", label="GEN_H_mass [GeV]"),
                hist.axis.Regular(30, 0, 3, name="DR", label="DR")
                )

for ievent,event in enumerate(chain):
    if ievent % 10000 == 0:
        print(f"Processing event {ievent}")
    #check if all the leptons are from the Higgs
    if event.GENlep_MomMomId[0] != 25 or event.GENlep_MomMomId[1] != 25:
        print("Warning: not all the leptons are from the Higgs!")
        continue
    #check if the lepton pair has opposite charge
    if event.GENlep_id[0] * event.GENlep_id[1] > 0:
        print("Warning: the lepton pair has the same charge!")
        continue

    #check fill the historgam base on eletron channel and muon channel
    if abs(event.GENlep_id[0]) == 11 and abs(event.GENlep_id[1]) == 11:
        dr = deltaR(event.GENlep_eta[0], event.GENlep_phi[0], event.GENlep_eta[1], event.GENlep_phi[1])
        h_ee.fill(GEN_H_mass=event.GENH_mass[0], DR=dr)
    elif abs(event.GENlep_id[0]) == 13 and abs(event.GENlep_id[1]) == 13:
        dr = deltaR(event.GENlep_eta[0], event.GENlep_phi[0], event.GENlep_eta[1], event.GENlep_phi[1])
        h_mumu.fill(GEN_H_mass=event.GENH_mass[0], DR=dr)
    else:
        print("Warning: the lepton is not electron or muon channel!")
        continue
        
    
#plot the histogram
h_ee.plot2d(cmap='rainbow')
#set the x-axis and y-axis label
plt.xlabel("GEN_H_mass [GeV]")
plt.ylabel("DR(e,e)")

#make a horzontal line at y=0.35
plt.axhline(y=0.05, color='r', linestyle='--')
#save the plot
plt.savefig("DR_vs_GEN_H_mass_ee.png")
#close the current figure
plt.close()

#plot the histogram
h_mumu.plot2d(cmap='rainbow')
#set the x-axis and y-axis label
plt.xlabel("GEN_H_mass [GeV]")
plt.ylabel("DR(mu,mu)")

#make a horzontal line at y=0.35
plt.axhline(y=0.05, color='r', linestyle='--')
#save the plot
plt.savefig("DR_vs_GEN_H_mass_mumu.png")