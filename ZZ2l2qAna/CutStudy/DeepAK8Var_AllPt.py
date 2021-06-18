from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-s","--sample", dest="sample", default='DYJetsToLL_Pt-250To400_01',help="input sample")
args = parser.parse_args()



samples = [args.sample]
var_names = ['ZvsQCD','tau21','ZvsQCD_de','tau21_DDT','ZbbvsZlight_de','particleNet_ZvsQCD_de','particleNet_Zbbvslight_de','ZbbvsQCD_de']
PH = plotHelper(samples,'2018Legacy') #initialize a plot class

#book out file targs.samplee raw histograms
outfilename = "../RawHistos/%s_particleNetDeepTau.root"%args.sample
outfile = TFile(outfilename,"recreate")

#book histos
histos = {}
histos[args.sample] = {}
for var_name in var_names:
    histos[args.sample][var_name]=TH1D(args.sample+"_"+var_name,args.sample+"_"+var_name,100,0,1)
    PH.SetHistStyles(histos[args.sample][var_name],args.sample,var_name)



#================================Ana==================================================
tempTree = PH.trees[args.sample]
print "[INFO] Start %s analysis"%args.sample

for ievent,event in enumerate(tempTree):
    #if(ievent==1000): break
    nlep = event.lep_pt.size()
    nmergedjets = event.mergedjet_pt.size()
    if(nmergedjets<1): continue

    weight = PH.GetWeight(args.sample,event)
    #print "weight = "+str(weight)
    if(weight>300):
        print "[INFO] this weight = "+str(weight)
        continue
    #if(weight>300): continue

    #find ZToll
    passedZ1Selection = False
    Zmass = 91.1876
    minZ1DeltaM = 99999.99
    n_Zs = 0
    Z_lepindex1 = []
    Z_lepindex2 = []
    massZ1 = 0
    #QCD ntuples needn't select a Z
    if(args.sample!='QCD'):
        for i in range(nlep):
            for j in range(i+1,nlep):
                if(event.lep_id[i]+event.lep_id[j]!=0): continue
                lifsr = TLorentzVector()
                ljfsr = TLorentzVector()
                lifsr.SetPtEtaPhiM(event.lepFSR_pt[i], event.lepFSR_eta[i], event.lepFSR_phi[i], event.lepFSR_mass[i])
                ljfsr.SetPtEtaPhiM(event.lepFSR_pt[j], event.lepFSR_eta[j], event.lepFSR_phi[j], event.lepFSR_mass[j])
                Z = TLorentzVector()
                Z = (lifsr + ljfsr)
                if(Z.M()>0):
                    n_Zs +=1
                    Z_lepindex1.append(i)
                    Z_lepindex2.append(j)
        #consider all Z
        for i in range(n_Zs):
            i1 = Z_lepindex1[i]
            i2 = Z_lepindex2[i]
            lep1 = TLorentzVector()
            lep2 = TLorentzVector()
            lep1.SetPtEtaPhiM(event.lepFSR_pt[i1],event.lepFSR_eta[i1],event.lepFSR_phi[i1],event.lepFSR_mass[i1])
            lep2.SetPtEtaPhiM(event.lepFSR_pt[i2],event.lepFSR_eta[i2],event.lepFSR_phi[i2],event.lepFSR_mass[i2])

            Z1 = lep1+lep2
            Z1DeltaM = abs(Z1.M()-Zmass)
            Z1_lepindex = [0,0]

            # Check Leading and Subleading pt Cut
            if(lep1.Pt()>lep2.Pt()):
                Z1_lepindex[0] = i1
                Z1_lepindex[1] = i2
                if(lep1.Pt()<40 or lep2.Pt()<24): continue
            else:
                Z1_lepindex[0] = i2
                Z1_lepindex[1] = i1
                if(lep2.Pt()<40 or lep1.Pt()<24): continue

            # Check dR(li,lj)>0.02 for any i,j
            if (deltaR(lep1.Eta(),lep1.Phi(),lep2.Eta(),lep2.Phi())<0.02): continue

            # Check M(l+,l-)>4.0 GeV for any OS pair , Do not include FSR photons
            lep1_noFSR = TLorentzVector()
            lep2_noFSR = TLorentzVector()
            lep1_noFSR.SetPtEtaPhiM(event.lep_pt[i1],event.lep_eta[i1],event.lep_phi[i1],event.lep_mass[i1])
            lep2_noFSR.SetPtEtaPhiM(event.lep_pt[i2],event.lep_eta[i2],event.lep_phi[i2],event.lep_mass[i2])
            if((lep1_noFSR+lep2_noFSR).M()<4.0): continue

            # Check isolation cut (without FSR ) for Z1 leptons
            if( event.lep_RelIsoNoFSR[Z1_lepindex[0]]>0.35): continue
            if( event.lep_RelIsoNoFSR[Z1_lepindex[1]]>0.35): continue

            # Check tight ID cut for Z1 leptons
            if (not event.lep_tightId[Z1_lepindex[0]]): continue
            if (not event.lep_tightId[Z1_lepindex[1]]): continue

            # check the masswindow
            if(Z1.M()<76 or Z1.M()>106): continue
            if(Z1.Pt()<100): continue
            if(Z1DeltaM<minZ1DeltaM):
                minZ1DeltaM = Z1DeltaM
                massZ1 = Z1.M()
                passedZ1Selection = True

    if((not passedZ1Selection) and args.sample!='QCD'): continue

    #mergedjet analysis
    for i in range(0,nmergedjets):
        tempDeltaR = 999.0
        isclean_H4l = True

        #select the leading jet
        #temp_pt = 0.0
        leadingIndex = 0
        deltaM=9999.9
        for k in range(0,nmergedjets):
            if(abs(event.mergedjet_subjet_softDropMass[k]-Zmass)<deltaM):
                deltaM = abs(event.mergedjet_subjet_softDropMass[k]-Zmass)
                leadingIndex = k

        #MassWindow check
        if(event.mergedjet_subjet_softDropMass[leadingIndex]>105 or event.mergedjet_subjet_softDropMass[leadingIndex]<70): continue


        #leptons and photons clear
        nlep =event.lep_pt.size()
        for j in range(nlep):
            if(not event.lep_tightId[j]): continue
            if(event.lep_RelIsoNoFSR[j]>0.35): continue
            thisLep = TLorentzVector()
            thisLep.SetPtEtaPhiM(event.lep_pt[j],event.lep_eta[j],event.lep_phi[j],event.lep_mass[j])
            tempDeltaR = deltaR(event.mergedjet_eta[i],event.mergedjet_phi[i],thisLep.Eta(),thisLep.Phi())
            if(tempDeltaR<0.8):
                isclean_H4l = False

        #only passed leptons clear jets
        if(isclean_H4l):
            #fill histos
            tempNsubjet = event.mergedjet_nsubjet[leadingIndex]
            temptau1 = event.mergedjet_tau1[leadingIndex]
            temptau2 = event.mergedjet_tau2[leadingIndex]

            if(temptau1 != 0):
                histos[args.sample]['ZvsQCD'].Fill(event.mergedjet_ZvsQCD[leadingIndex],weight)
                histos[args.sample]['ZvsQCD_de'].Fill(event.mergedjet_ZvsQCD_de[leadingIndex],weight)
                histos[args.sample]['ZbbvsQCD_de'].Fill(event.mergedjet_ZbbvsQCD_de[leadingIndex],weight)
                histos[args.sample]['tau21'].Fill(temptau2/temptau1,weight)
                temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_subjet_softDropMass[leadingIndex]*event.mergedjet_subjet_softDropMass[leadingIndex])/event.mergedjet_pt[leadingIndex])
                histos[args.sample]['tau21_DDT'].Fill(temp_tauDDT,weight)

                temp_ZbbvsZlight = (event.mergedjet_ZbbvsQCD_de[leadingIndex]*(1-event.mergedjet_ZvsQCD_de[leadingIndex]))/(event.mergedjet_ZvsQCD_de[leadingIndex]*(1-event.mergedjet_ZbbvsQCD_de[leadingIndex]))
                histos[args.sample]['ZbbvsZlight_de'].Fill(temp_ZbbvsZlight,weight)

                #particleNet
                temp_particleNetZvsQCD = event.mergedjet_Net_Xbb_de[leadingIndex]+event.mergedjet_Net_Xcc_de[leadingIndex]+event.mergedjet_Net_Xqq_de[leadingIndex]
                temp_particleNetZbbvslight = event.mergedjet_Net_Xbb_de[leadingIndex]/(1-event.mergedjet_Net_Xbb_de[leadingIndex]-event.mergedjet_Net_Xcc_de[leadingIndex])
                histos[args.sample]['particleNet_ZvsQCD_de'].Fill(temp_particleNetZvsQCD,weight)
                histos[args.sample]['particleNet_Zbbvslight_de'].Fill(temp_particleNetZbbvslight)

#======================================================================================

#Write raw histograms into rootfile
outfile.cd()
for var_name in var_names:
    histos[args.sample][var_name].Write()

outfile.Close()
