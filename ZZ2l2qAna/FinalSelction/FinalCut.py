from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-s","--sample", dest="sample", default='GluGluHToZZTo2L2Q_M1000',help="input sample")
args = parser.parse_args()

#samples = ['GluGluHToZZTo2L2Q_M1000','DYJetsToLL_Pt-250To400','DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf','TTJets','WZ','ZZ_TuneCP5']#'GluGluHToZZTo2L2Q_M1500','GluGluHToZZTo2L2Q_M2000','GluGluHToZZTo2L2Q_M2500','GluGluHToZZTo2L2Q_M3000'] #['ZZ','DYJets','WZ',
sample = [args.sample]
var_names = ['ZvsQCD_de','tau21_DDT','particleNet_ZvsQCD_de','ZbbvsQCD_de']
var_tau1 = ['SDmass_SR','SDmass_CR','Pt','eta','Z1_mass','Z1_pt','Hmass','dR_lep','dR_ZZ','HvsSD']
PH = plotHelper(sample,'2018Legacy') #initialize a plot class


#book out file to store raw histograms
outfilename = "../RawHistos/%s_particleNetCut.root"%args.sample
outfile = TFile(outfilename,'recreate')

#book histos
histos = {}
histos[args.sample]={}
histos[args.sample]['SDmass_SR']=TH1D(args.sample+'_SDmass_SR',args.sample+'_SDmass_SR',56,40,180)
histos[args.sample]['SDmass_CR']=TH1D(args.sample+'_SDmass_CR',args.sample+'_SDmass_CR',56,40,180)
histos[args.sample]['Pt']=TH1D(args.sample+'_Pt',args.sample+'_Pt',40,200,1000)
histos[args.sample]['eta']=TH1D(args.sample+'_eta',args.sample+'_eta',20,-5,5)
histos[args.sample]['Z1_mass']=TH1D(args.sample+'_Z1_mass',args.sample+'_Z1_mass',60,40,160)
histos[args.sample]['Z1_pt']=TH1D(args.sample+'_Z1_pt',args.sample+'_Z1_pt',70,150,1550)
histos[args.sample]['Hmass']=TH1D(args.sample+'_Hmass',args.sample+'_Hmass',60,500,3500)
histos[args.sample]['dR_lep']=TH1D(args.sample+'_dR_lep',args.sample+'_dR_lep',20,0,5)
histos[args.sample]['dR_ZZ']=TH1D(args.sample+'_dR_ZZ',args.sample+'_dR_ZZ',20,0,5)
histos[args.sample]['HvsSD']=TH2D(args.sample+'_HvsSD',args.sample+'_HvsSD',60,500,3500,56,40,180)
#temp histos
histos[args.sample]['GENH_mass']=TH1D(args.sample+"_GENH_mass",args.sample+"_GENH_mass",60,500,3500)
histos[args.sample]['GENH_massall']=TH1D(args.sample+"_GENH_massall",args.sample+"_GENH_massall",60,500,3500)
for var_name in var_names:
    histos[args.sample][var_name]=TH1D(args.sample+"_"+var_name,args.sample+"_"+var_name,20,0,1)
    PH.SetHistStyles(histos[args.sample][var_name],args.sample,var_name)

for var_name in var_tau1:
    PH.SetHistStyles(histos[args.sample][var_name],args.sample,var_name)


#================================Ana==================================================
tempTree = PH.trees[args.sample]
nentries = PH.trees[args.sample].GetEntries()
print "[INFO] Start %s analysis"%args.sample
data = 0
if(args.sample=='GluGluHToZZTo2L2Q_MAll'):
    for ievent,event in enumerate(tempTree):
        #if(ievent==10000): break
        if(ievent%100000==0):
            print "[INFO] {0:s}/{1:s}".format(str(ievent),str(nentries))

        nGENHigss = event.GENH_mass.size()
        if(nGENHigss<=0): continue

        weight = weight = PH.lumi*1000*0.02314*event.eventWeight/PH.sumWeights[args.sample]
        if(weight>300): continue


        #GEN
        GENleadingIndex = 0
        GENtemp_pt = 0.0
        for i in range(nGENHigss):
            if(event.GENH_pt[i]>GENtemp_pt):
                GENleadingIndex = i
                GENtemp_pt = event.GENH_pt[i]

        histos[args.sample]['GENH_massall'].Fill(event.GENH_mass[GENleadingIndex],weight)

        if((event.GENH_mass[GENleadingIndex]>=950 and event.GENH_mass[GENleadingIndex]<=1050) or (event.GENH_mass[GENleadingIndex]>=1800 and event.GENH_mass[GENleadingIndex]<=1950)):
            histos[args.sample]['GENH_mass'].Fill(event.GENH_mass[GENleadingIndex],weight)

        #Reco
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
            if(event.mergedjet_pt[i]<200): continue
            if(abs(event.mergedjet_eta[i])>2.4): continue
            #MassWindow check
            if(event.mergedjet_subjet_softDropMass[i]<=0 or event.mergedjet_subjet_softDropMass[i]>180): continue
            if(event.mergedjet_ZvsQCD_de[i]<0.7): continue

            temptau1 = event.mergedjet_tau1[i]
            temptau2 = event.mergedjet_tau2[i]
            if(temptau1<=0): continue
            temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_subjet_softDropMass[i]*event.mergedjet_subjet_softDropMass[i])/event.mergedjet_pt[i])
            #if(temp_tauDDT>0.6): continue

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
                    lep_Hindex[0]=Z1_lepindex[0]
                    lep_Hindex[1]=Z1_lepindex[1]
                    passedZ1Selection = True

        if((not passedZ1Selection) and args.sample!='QCD'): continue

        #select the leading jet, if this event passed all selection
        temp_pt = 0.0
        leadingIndex = 0
        for i in mergedjet_index:
            if(event.mergedjet_pt[i]>temp_pt):
                temp_pt = event.mergedjet_pt[i]
                leadingIndex = i


        if(event.mergedjet_subjet_softDropMass[leadingIndex]>=70 and event.mergedjet_subjet_softDropMass[leadingIndex]<=105):
            passedMergedJetSRSelection = True
        else:
            passedMergedJetCRSelection = True

        if(passedMergedJetSRSelection):
            if((event.GENH_mass[GENleadingIndex]>=950 and event.GENH_mass[GENleadingIndex]<=1050) or (event.GENH_mass[GENleadingIndex]>=1800 and event.GENH_mass[GENleadingIndex]<=1950)):
                higgscand = TLorentzVector()
                l1_H = TLorentzVector()
                l2_H = TLorentzVector()
                mergedjet_H = TLorentzVector()
                l1_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[0]],event.lepFSR_eta[lep_Hindex[0]],event.lepFSR_phi[lep_Hindex[0]],event.lepFSR_mass[lep_Hindex[0]])
                l2_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[1]],event.lepFSR_eta[lep_Hindex[1]],event.lepFSR_phi[lep_Hindex[1]],event.lepFSR_mass[lep_Hindex[1]])
                mergedjet_H.SetPtEtaPhiM(event.mergedjet_pt[leadingIndex],event.mergedjet_eta[leadingIndex],event.mergedjet_phi[leadingIndex],event.mergedjet_subjet_softDropMass[leadingIndex])
                higgscand = l1_H+l2_H+mergedjet_H
                leptonic_Z = l1_H+l2_H
                histos[args.sample]['Hmass'].Fill(higgscand.M(),weight)
                histos[args.sample]['HvsSD'].Fill(higgscand.M(),event.mergedjet_subjet_softDropMass[leadingIndex],weight)

                temptau1 = event.mergedjet_tau1[leadingIndex]
                temptau2 = event.mergedjet_tau2[leadingIndex]

                histos[args.sample]['Z1_mass'].Fill(massZ1,weight)
                histos[args.sample]['ZvsQCD_de'].Fill(event.mergedjet_ZvsQCD_de[leadingIndex],weight)
                histos[args.sample]['SDmass_SR'].Fill(event.mergedjet_subjet_softDropMass[leadingIndex],weight)
                histos[args.sample]['eta'].Fill(event.mergedjet_eta[leadingIndex],weight)
                histos[args.sample]['Pt'].Fill(event.mergedjet_pt[leadingIndex],weight)

                #print "event.mergedjet_subjet_softDropMass = " +str(event.mergedjet_subjet_softDropMass[leadingIndex])
                #print "event.mergedjet_pt = "+str(event.mergedjet_pt[leadingIndex])
                temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_subjet_softDropMass[leadingIndex]*event.mergedjet_subjet_softDropMass[leadingIndex])/event.mergedjet_pt[leadingIndex])
                histos[args.sample]['tau21_DDT'].Fill(temp_tauDDT,weight)

    nEvents = Double(histos[args.sample]['GENH_massall'].Integral())


    nbins = [950,1000,1050,1800,1850,1900,1950]#[2050,2100,2850,2900,2950,3000,3050,3100,3150]
    for bin in nbins:
        if(bin == 1950): continue

        down_bin = histos[args.sample]['GENH_mass'].GetXaxis().FindBin(bin)
        up_bin = histos[args.sample]['GENH_mass'].GetXaxis().FindBin(bin+50)

        temp_nevents = Double(histos[args.sample]['GENH_mass'].Integral(down_bin,up_bin))

        reweight = temp_nevents/nEvents

        thisbin = histos[args.sample]['Hmass'].GetXaxis().FindBin(bin)
        thisContent = histos[args.sample]['Hmass'].GetBinContent(thisbin)
        histos[args.sample]['Hmass'].SetBinContent(thisbin,thisContent*reweight)
        histos[args.sample]['HvsSD'].SetBinContent(thisbin,thisContent*reweight)
else:
    for ievent,event in enumerate(tempTree):
        #if(ievent==10000): break
        if(ievent%100000==0):
            print "[INFO] {0:s}/{1:s}".format(str(ievent),str(nentries))
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
            if(event.mergedjet_pt[i]<200): continue
            if(abs(event.mergedjet_eta[i])>2.4): continue
            #MassWindow check
            if(event.mergedjet_subjet_softDropMass[i]<=0 or event.mergedjet_subjet_softDropMass[i]>180): continue
            temp_particleNetZvsQCD = event.mergedjet_Net_Xbb_de[i]+event.mergedjet_Net_Xcc_de[i]+event.mergedjet_Net_Xqq_de[i]
            if(temp_particleNetZvsQCD<0.89): continue
            #if(event.mergedjet_ZvsQCD_de[i]<0.7): continue

            temptau1 = event.mergedjet_tau1[i]
            temptau2 = event.mergedjet_tau2[i]
            if(temptau1<=0): continue
            temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_subjet_softDropMass[i]*event.mergedjet_subjet_softDropMass[i])/event.mergedjet_pt[i])
            #if(temp_tauDDT>0.6): continue

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
                    lep_Hindex[0]=Z1_lepindex[0]
                    lep_Hindex[1]=Z1_lepindex[1]
                    passedZ1Selection = True

        if((not passedZ1Selection) and args.sample!='QCD'): continue

        #event weight
        if(args.sample.find('DYJetsToLL_Pt-100To250')!=-1):
            weight = PH.lumi*1000*94.48*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample.find('DYJetsToLL_Pt-250To400')!=-1):
            weight = PH.lumi*1000*3.648*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='DYJetsToLL_Pt-400To650'):
            weight = PH.lumi*1000*0.4999*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='DYJetsToLL_Pt-650ToInf'):
            weight = PH.lumi*1000*0.04699*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='TTJets'):
            weight = PH.lumi*1000*722.8*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='ZZ_TuneCP5'):
            weight = PH.lumi*1000*12.10*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='WZ'):
            weight = PH.lumi*1000*27.27*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M1000'):
            weight = PH.lumi*1000*0.1023*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M1500'):
            weight = PH.lumi*1000*0.01308*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M2000'):
            weight = PH.lumi*1000*0.0055*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M2500'):
            weight = PH.lumi*1000*0.002207*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M3000'):
            weight = PH.lumi*1000*0.001037*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M1000'):
            weight = PH.lumi*1000*0.03883*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M2000'):
            weight = PH.lumi*1000*0.001029*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        elif(args.sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M3000'):
            weight = PH.lumi*1000*0.0000666*event.eventWeight*event.lep_dataMC[lep_Hindex[0]]*event.lep_dataMC[lep_Hindex[1]]/PH.sumWeights[args.sample]
        else:
            data +=1
            weight=1

        if(weight>300): continue

        #select the leading jet, if this event passed all selection
        temp_pt = 0.0
        leadingIndex = 0
        for i in mergedjet_index:
            if(event.mergedjet_pt[i]>temp_pt):
                temp_pt = event.mergedjet_pt[i]
                leadingIndex = i


        if(event.mergedjet_subjet_softDropMass[leadingIndex]>=70 and event.mergedjet_subjet_softDropMass[leadingIndex]<=105):
            passedMergedJetSRSelection = True
        else:
            passedMergedJetCRSelection = True

        #fill histos in CR and SR region
        if(passedMergedJetSRSelection):
            temptau1 = event.mergedjet_tau1[leadingIndex]
            temptau2 = event.mergedjet_tau2[leadingIndex]

            histos[args.sample]['Z1_mass'].Fill(massZ1,weight)
            histos[args.sample]['ZvsQCD_de'].Fill(event.mergedjet_ZvsQCD_de[leadingIndex],weight)
            histos[args.sample]['ZbbvsQCD_de'].Fill(event.mergedjet_ZvsQCD_de[leadingIndex],weight)
            histos[args.sample]['SDmass_SR'].Fill(event.mergedjet_subjet_softDropMass[leadingIndex],weight)
            histos[args.sample]['eta'].Fill(event.mergedjet_eta[leadingIndex],weight)
            histos[args.sample]['Pt'].Fill(event.mergedjet_pt[leadingIndex],weight)
            histos[args.sample]['particleNet_ZvsQCD_de'].Fill(event.mergedjet_Net_Xbb_de[leadingIndex]+event.mergedjet_Net_Xcc_de[leadingIndex]+event.mergedjet_Net_Xqq_de[leadingIndex],weight)

            #print "event.mergedjet_subjet_softDropMass = " +str(event.mergedjet_subjet_softDropMass[leadingIndex])
            #print "event.mergedjet_pt = "+str(event.mergedjet_pt[leadingIndex])
            temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_subjet_softDropMass[leadingIndex]*event.mergedjet_subjet_softDropMass[leadingIndex])/event.mergedjet_pt[leadingIndex])
            histos[args.sample]['tau21_DDT'].Fill(temp_tauDDT,weight)

            higgscand = TLorentzVector()
            l1_H = TLorentzVector()
            l2_H = TLorentzVector()
            mergedjet_H = TLorentzVector()
            l1_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[0]],event.lepFSR_eta[lep_Hindex[0]],event.lepFSR_phi[lep_Hindex[0]],event.lepFSR_mass[lep_Hindex[0]])
            l2_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[1]],event.lepFSR_eta[lep_Hindex[1]],event.lepFSR_phi[lep_Hindex[1]],event.lepFSR_mass[lep_Hindex[1]])
            mergedjet_H.SetPtEtaPhiM(event.mergedjet_pt[leadingIndex],event.mergedjet_eta[leadingIndex],event.mergedjet_phi[leadingIndex],event.mergedjet_subjet_softDropMass[leadingIndex])
            higgscand = l1_H+l2_H+mergedjet_H
            leptonic_Z = l1_H+l2_H
            histos[args.sample]['Hmass'].Fill(higgscand.M(),weight)
            histos[args.sample]['HvsSD'].Fill(higgscand.M(),event.mergedjet_subjet_softDropMass[leadingIndex],weight)
            histos[args.sample]['Z1_pt'].Fill(leptonic_Z.Pt(),weight)

            deltaR_lep = deltaR(l1_H.Eta(),l1_H.Phi(),l2_H.Eta(),l2_H.Phi())
            histos[args.sample]['dR_lep'].Fill(deltaR_lep,weight)

            deltaR_ZZ = deltaR(leptonic_Z.Eta(),leptonic_Z.Phi(),event.mergedjet_eta[leadingIndex],event.mergedjet_phi[leadingIndex])
            histos[args.sample]['dR_ZZ'].Fill(deltaR_ZZ,weight)

        if(passedMergedJetCRSelection):
            histos[args.sample]['SDmass_CR'].Fill(event.mergedjet_subjet_softDropMass[leadingIndex],weight)


if(data!=0):
    print '[INFO] this is data'


#======================================================================================

#Write raw histograms into rootfile
outfile.cd()
for var_name in var_names:
    histos[args.sample][var_name].Write()

for var_name in var_tau1:
    histos[args.sample][var_name].Write()


outfile.Close()
