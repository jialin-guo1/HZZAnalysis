from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

samples = ['GluGluHToZZTo2L2Q_M1000','DYJetsToLL_Pt-250To400','DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']#'GluGluHToZZTo2L2Q_M1500','GluGluHToZZTo2L2Q_M2000','GluGluHToZZTo2L2Q_M2500','GluGluHToZZTo2L2Q_M3000'] #['ZZ','DYJets','WZ',
#samples = ['DYJetsToLL_Pt-650ToInf']
var_names = ['ZvsQCD_de','tau21_DDT']
var_tau1 = ['SDmass','Pt','eta','Z1_mass','Hmass']
PH = plotHelper(samples,2018) #initialize a plot class


#book out file to store raw histograms
outfilename = "../RawHistos/invariantmass.root"
outfile = TFile(outfilename,"recreate")

#book histos
histos = {}
for sample in samples:
    histos[sample]={}
    histos[sample]['SDmass']=TH1D(sample+'_SDmass',sample+'_SDmass',26,40,300)
    histos[sample]['Pt']=TH1D(sample+'_Pt',sample+'_Pt',40,200,1000)
    histos[sample]['eta']=TH1D(sample+'_eta',sample+'_eta',20,-5,5)
    histos[sample]['Z1_mass']=TH1D(sample+'_Z1mass',sample+'_Z1mass',60,40,160)
    histos[sample]['Hmass']=TH1D(sample+'_Hmass',sample+'_Hmass',60,500,3500)
    for var_name in var_names:
        histos[sample][var_name]=TH1D(sample+"_"+var_name,sample+"_"+var_name,20,0,1)
        PH.SetHistStyles(histos[sample][var_name],sample,var_name)

for sample in samples:
    for var_name in var_tau1:
        PH.SetHistStyles(histos[sample][var_name],sample,var_name)


#================================Ana==================================================
for sample in samples:
    tempTree = PH.trees[sample]
    print "[INFO] Start %s analysis"%sample

    for ievent,event in enumerate(tempTree):
        #if(ievent==1000): break
        nlep = event.lep_pt.size()
        nmergedjets = event.mergedjet_pt.size()
        if(nmergedjets<1): continue

        #find ZToll
        passedZ1Selection = False
        Zmass = 91.1876
        minZ1DeltaM = 99999.99
        n_Zs = 0
        Z_lepindex1 = []
        Z_lepindex2 = []
        lep_Hindex = [0,0]
        massZ1 = 0
        #QCD ntuples needn't select a Z
        if(sample!='QCD'):
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
                    if(lep1.Pt()<20 or lep2.Pt()<10): continue
                else:
                    Z1_lepindex[0] = i2
                    Z1_lepindex[1] = i1
                    if(lep2.Pt()<20 or lep1.Pt()<10): continue

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
                    lep_Hindex[0]=Z1_lepindex[0]
                    lep_Hindex[1]=Z1_lepindex[1]
                    passedZ1Selection = True

        if((not passedZ1Selection) and sample!='QCD'): continue

        #mergedjet analysis
        #pt, eta, ZvsQCD_de, masswindow, lepton and photon clear
        passedMergedJetSelection = False
        mergedjet_index=[]
        for i in range(0,nmergedjets):
            tempDeltaR = 999.0
            isclean_H4l = True

            if(event.mergedjet_tau1<=0): continue
            #final cut
            if(abs(event.mergedjet_eta[i])>2.4): continue
            if(event.mergedjet_ZvsQCD_de[i]<0.7): continue

            #select the jetmass closest Zmass
            #deltaM=9999.9
            #for k in range(0,nmergedjets):
            #    if(abs(event.mergedjet_softdropmass[k]-Zmass)<deltaM):
            #        deltaM = abs(event.mergedjet_softdropmass[k]-Zmass)
            #        leadingIndex = k

            #MassWindow check
            if(event.mergedjet_softdropmass[i]>105 or event.mergedjet_softdropmass[i]<70): continue
            #if(event.mergedjet_softdropmass[leadingIndex]<=0): continue

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

            #nfsrphoton = event.fsrPhotons_pt.size()
            #for j in range(nfsrphoton):
            #    if(not event.lep_tightId[event.fsrPhotons_lepindex[j]]): continue
            #    RelIsoNoFSR=event.lep_RelIsoNoFSR[event.fsrPhotons_lepindex[j]]
            #    if(RelIsoNoFSR>0.35): continue
            #    thispho = TLorentzVector()
            #    thispho.SetPtEtaPhiM(event.fsrPhotons_pt[j],event.fsrPhotons_eta[j],event.fsrPhotons_phi[j],0.0)
            #    tempDeltaR = deltaR(event.mergedjet_eta[i],event.mergedjet_phi[i],thispho.Eta(),thispho.Phi())
            #    if(tempDeltaR<0.8):
            #        isclean_H4l = False

            if(not isclean_H4l): continue

            mergedjet_index.append(i)
            passedMergedJetSelection = True

        if(not passedMergedJetSelection): continue

        #event weight
        if(sample=='DYJetsToLL_Pt-250To400'):
            weight = PH.lumi*1000*3.681*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='DYJetsToLL_Pt-400To650'):
            weight = PH.lumi*1000*0.4999*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='DYJetsToLL_Pt-650ToInf'):
            weight = PH.lumi*1000*0.04699*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M1000'):
            weight = PH.lumi*1000*0.1023*event.eventWeight/PH.sumWeights[sample]
        else:
            weight=1

        #select the leading jet, if this event passed all selection
        temp_pt = 0.0
        leadingIndex = 0
        for i in mergedjet_index:
            if(event.mergedjet_pt[i]>temp_pt):
                temp_pt = event.mergedjet_pt[i]
                leadingIndex = i

        #fill histos
        temptau1 = event.mergedjet_tau1[leadingIndex]
        temptau2 = event.mergedjet_tau2[leadingIndex]

        histos[sample]['Z1_mass'].Fill(massZ1,weight)
        histos[sample]['ZvsQCD_de'].Fill(event.mergedjet_ZvsQCD_de[leadingIndex],weight)
        histos[sample]['SDmass'].Fill(event.mergedjet_softdropmass[leadingIndex],weight)
        histos[sample]['eta'].Fill(event.mergedjet_eta[leadingIndex],weight)
        histos[sample]['Pt'].Fill(event.mergedjet_pt[leadingIndex],weight)

        #print "event.mergedjet_softdropmass = " +str(event.mergedjet_softdropmass[leadingIndex])
        #print "event.mergedjet_pt = "+str(event.mergedjet_pt[leadingIndex])
        temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_softdropmass[leadingIndex]*event.mergedjet_softdropmass[leadingIndex])/event.mergedjet_pt[leadingIndex])
        histos[sample]['tau21_DDT'].Fill(temp_tauDDT,weight)

        higgscand = TLorentzVector()
        l1_H = TLorentzVector()
        l2_H = TLorentzVector()
        mergedjet_H = TLorentzVector()
        l1_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[0]],event.lepFSR_eta[lep_Hindex[0]],event.lepFSR_phi[lep_Hindex[0]],event.lepFSR_mass[lep_Hindex[0]])
        l2_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[1]],event.lepFSR_eta[lep_Hindex[1]],event.lepFSR_phi[lep_Hindex[1]],event.lepFSR_mass[lep_Hindex[1]])
        mergedjet_H.SetPtEtaPhiM(event.mergedjet_pt[leadingIndex],event.mergedjet_eta[leadingIndex],event.mergedjet_phi[leadingIndex],event.mergedjet_softdropmass[leadingIndex])
        higgscand = l1_H+l2_H+mergedjet_H
        histos[sample]['Hmass'].Fill(higgscand.M(),weight)




#======================================================================================

#Write raw histograms into rootfile
outfile.cd()
for sample in samples:
    for var_name in var_names:
        histos[sample][var_name].Write()

for sample in samples:
    for var_name in var_tau1:
        histos[sample][var_name].Write()

#Draw Plots
print "[INFO] Start draw plots on canvas"
plotname = 'FinalCut_noCR'
for var_name in var_names:
    PH.DrawStack(histos,samples,var_name,plotname)

for var_name in var_tau1:
    PH.DrawStack(histos,samples,var_name,plotname)

outfile.Close()
