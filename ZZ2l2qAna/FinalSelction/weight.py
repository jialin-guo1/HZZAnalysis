from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

#samples = ['GluGluHToZZTo2L2Q_M1000','DYJetsToLL_Pt-250To400','DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf','TTJets','WZ','ZZ_TuneCP5']#'GluGluHToZZTo2L2Q_M1500','GluGluHToZZTo2L2Q_M2000','GluGluHToZZTo2L2Q_M2500','GluGluHToZZTo2L2Q_M3000'] #['ZZ','DYJets','WZ',
samples = ['DYJetsToLL_Pt-250To400']
var_names = ['ZvsQCD_de','tau21_DDT']
var_tau1 = ['SDmass_SR','SDmass_CR','Pt','eta','weight','eventWeight','pileupWeight','genWeight']


PH = plotHelper(samples,2018) #initialize a plot class

file = open('weight_0.85_0.9.txt','w')


#book histos
histos = {}
for sample in samples:
    histos[sample]={}
    histos[sample]['SDmass_SR']=TH1D(sample+'_SDmass_SR',sample+'_SDmass_SR',56,40,180)
    histos[sample]['SDmass_CR']=TH1D(sample+'_SDmass_CR',sample+'_SDmass_CR',56,40,180)
    histos[sample]['Pt']=TH1D(sample+'_Pt',sample+'_Pt',40,200,1000)
    histos[sample]['eta']=TH1D(sample+'_eta',sample+'_eta',20,-5,5)
    histos[sample]['weight']=TH1D(sample+'_weight',sample+'_weight',60,-1.5,1.5)
    histos[sample]['eventWeight']=TH1D(sample+'_eventWeight',sample+'_eventWeight',40,-2,2)
    histos[sample]['pileupWeight']=TH1D(sample+'_pileupWeight',sample+'_pileupWeight',20,0,2)
    histos[sample]['genWeight']=TH1D(sample+'_genWeight',sample+'_genWeight',300,-1.5,1.5)
    histos[sample]['Z1_pt'] = TH1D(sample+'_Z1_pt',sample+'_Z1_pt',70,150,1500)

    for var_name in var_names:
        histos[sample][var_name]=TH1D(sample+"_"+var_name,sample+"_"+var_name,20,0,1)
        PH.SetHistStyles(histos[sample][var_name],sample,var_name)

for sample in samples:
    for var_name in var_tau1:
        PH.SetHistStyles(histos[sample][var_name],sample,var_name)


#================================Ana==================================================
for sample in samples:
    tempTree = PH.trees[sample]
    nentries = PH.trees[sample].GetEntries()
    print "[INFO] Start %s analysis"%sample

    for ievent,event in enumerate(tempTree):
        #if(ievent==20000): break
        if(ievent%100000==0):
            print "[INFO] {0:s}/{1:s}".format(str(ievent),str(nentries))

        if(event.nInt!=0): continue


        nlep = event.lep_pt.size()
        nmergedjets = event.mergedjet_pt.size()
        if(nmergedjets<1): continue

        #mergedjet analysis
        #pt, eta, ZvsQCD_de, masswindow, lepton and photon clear
        passedMergedJetSelection = False
        passedMergedJetSRSelection = False
        passedMergedJetCRSelection = False
        mergedjet_index=[]
        for i in range(0,nmergedjets):
            tempDeltaR = 999.0
            isclean_H4l = True

            if(event.mergedjet_tau1<=0): continue
            #final cut
            if(abs(event.mergedjet_eta[i])>2.4): continue
            if(event.mergedjet_ZvsQCD_de[i]<0.85): continue
            if(event.mergedjet_ZvsQCD_de[i]>0.9):continue


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

            if(not isclean_H4l): continue

            #MassWindow check
            if(event.mergedjet_softdropmass[i]<=0 or event.mergedjet_softdropmass[i]>180): continue
            passedMergedJetSelection = True

            mergedjet_index.append(i)

        if(not passedMergedJetSelection): continue

        #find ZToll
        passedZ1Selection = False
        Zmass = 91.1876
        minZ1DeltaM = 99999.99
        n_Zs = 0
        Z_lepindex1 = []
        Z_lepindex2 = []
        lep_Hindex=[0,0]
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

        #event weight
        if(sample=='DYJetsToLL_Pt-250To400'):
            weight = PH.lumi*1000*3.681*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='DYJetsToLL_Pt-400To650'):
            weight = PH.lumi*1000*0.4999*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='DYJetsToLL_Pt-650ToInf'):
            weight = PH.lumi*1000*0.04699*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='TTJets'):
            weight = PH.lumi*1000*722.8*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='ZZ_TuneCP5'):
            weight = PH.lumi*1000*16.52*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='WZ'):
            weight = PH.lumi*1000*27.6*event.eventWeight/PH.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M1000'):
            weight = PH.lumi*1000*0.1023*event.eventWeight/PH.sumWeights[sample]
        else:
            weight=1


        histos[sample]['weight'].Fill(weight)
        histos[sample]['eventWeight'].Fill(event.eventWeight)
        histos[sample]['genWeight'].Fill(event.genWeight)
        histos[sample]['pileupWeight'].Fill(event.pileupWeight)

        print "[INFO] this weight = {}, eventWeight = {}, pileupWeight = {}, genWeight = {}, nInt = {}, Run = {}, Event = {}".format(weight,event.eventWeight,event.pileupWeight,event.genWeight,event.nInt,event.Run,event.Event)



        #select the leading jet, if this event passed all selection
        #temp_pt = 0.0
        #leadingIndex = 0
        #for i in mergedjet_index:
        #    if(event.mergedjet_pt[i]>temp_pt):
        #        temp_pt = event.mergedjet_pt[i]
        #        leadingIndex = i

        #if(event.mergedjet_softdropmass[leadingIndex]>=70 and event.mergedjet_softdropmass[leadingIndex]<=105):
        #    passedMergedJetSRSelection = True
        #else:
        #    passedMergedJetCRSelection = True

        #fill histos in CR and SR region
        #if(passedMergedJetSRSelection):
        #    temptau1 = event.mergedjet_tau1[leadingIndex]
        #    temptau2 = event.mergedjet_tau2[leadingIndex]

        #    histos[sample]['ZvsQCD_de'].Fill(event.mergedjet_ZvsQCD_de[leadingIndex],weight)
        #    histos[sample]['SDmass_SR'].Fill(event.mergedjet_softdropmass[leadingIndex],weight)
        #    histos[sample]['eta'].Fill(event.mergedjet_eta[leadingIndex],weight)
        #    histos[sample]['Pt'].Fill(event.mergedjet_pt[leadingIndex],weight)

            #print "event.mergedjet_softdropmass = " +str(event.mergedjet_softdropmass[leadingIndex])
            #print "event.mergedjet_pt = "+str(event.mergedjet_pt[leadingIndex])
        #    temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_softdropmass[leadingIndex]*event.mergedjet_softdropmass[leadingIndex])/event.mergedjet_pt[leadingIndex])
        #    histos[sample]['tau21_DDT'].Fill(temp_tauDDT,weight)

        #if(passedMergedJetCRSelection):
        #    histos[sample]['SDmass_CR'].Fill(event.mergedjet_softdropmass[leadingIndex],weight)


##Draw Plots
#print "[INFO] Start draw plots on canvas"
#plotname = 'weight_test'
#for var_name in var_names:
#    PH.DrawStack(histos,samples,var_name,plotname)

#for var_name in var_tau1:
#    PH.DrawStack(histos,samples,var_name,plotname)
