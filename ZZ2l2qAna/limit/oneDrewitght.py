from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *


import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-s","--sample", dest="sample", default='GluGluHToZZTo2L2Q_MAll',help="input sample")
args = parser.parse_args()


samples=[args.sample]
var_names =['Hmass','HvsSD','GENH_mass','GENH_massall','GENH_mass_weight','GENH_massall_weight']
tmp_var = ['GENH_mass','GENH_massall']

PH = plotHelper(samples,2018)


#book out file to store raw histograms
outfilename = "../RawHistos/%s_limit.root"%args.sample
outfile = TFile(outfilename,'recreate')


histos = {}
histos[args.sample]={}
histos[args.sample]['GENH_mass']=TH1D(args.sample+"_GENH_mass",args.sample+"_GENH_mass",60,500,3500)
histos[args.sample]['GENH_massall']=TH1D(args.sample+"_GENH_massall",args.sample+"_GENH_massall",60,500,3500)
histos[args.sample]['GENH_mass_weight']=TH1D(args.sample+"_GENH_mass_weight",args.sample+"_GENH_mass_weight",60,500,3500)
histos[args.sample]['GENH_massall_weight']=TH1D(args.sample+"_GENH_massall_weight",args.sample+"_GENH_massall_weight",60,500,3500)
histos[args.sample]['Hmass']=TH1D(args.sample+"Hmass",args.sample+"Hmass",60,500,3500)
histos[args.sample]['HvsSD']=TH2D(args.sample+'HvsSD',args.sample+'HvsSD',60,500,3500,7,70,105)

for var_name in var_names:
    PH.SetHistStyles(histos[args.sample][var_name],args.sample,var_name)


#================================Ana==================================================
tempTree = PH.trees[args.sample]
nentries = PH.trees[args.sample].GetEntries()
print "[INFO] Start %s analysis"%args.sample
if(args.sample.find('GluGluHToZZTo2L2Q')!=-1):
    for ievent,event in enumerate(tempTree):
        if(ievent==10000): break
        if(ievent%100000==0):
            print "[INFO] {0:s}/{1:s}".format(str(ievent),str(nentries))

        nGENHigss = event.GENH_mass.size()
        if(nGENHigss<=0): continue

        if(args.sample=='GluGluHToZZTo2L2Q_MAll'):
            weight = weight = PH.lumi*1000*0.02314*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M1000'):
            weight = PH.lumi*1000*0.1023*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M1500'):
            weight = PH.lumi*1000*0.01308*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M2000'):
            weight = PH.lumi*1000*0.0055*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M2500'):
            weight = PH.lumi*1000*0.002207*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M3000'):
            weight = PH.lumi*1000*0.001037*event.eventWeight/PH.sumWeights[args.sample]
        else:
            weight = 1


        #GEN
        nGENlep = event.GENlep_pt.size()
        nGENZjet  = event.GENZjet_pt.size()
        if(nGENlep<2 or nGENZjet<2): continue

        GENZ_lepindex1=[]
        GENZ_lepindex2=[]
        GENlep_Hindex=[0,0]
        nGENZ1 = 0
        GENZmass = 91.1876
        minZ1DeltaM = 99999.99
        passedGENZ1Selection = False
        for i in range(nGENlep):
            for j in range(i+1, nGENlep):
                if(event.GENlep_id[i]+event.GENlep_id[j]!=0): continue
                if(event.GENlep_MomId[i]!=23 or event.GENlep_MomId[j]!=23): continue
                if(event.GENlep_MomMomId[i]!=25 or event.GENlep_MomMomId[j]!=25): continue
                li = TLorentzVector()
                lj = TLorentzVector()
                li.SetPtEtaPhiM(event.GENlep_pt[i],event.GENlep_eta[i],event.GENlep_phi[i],event.GENlep_phi[i])
                lj.SetPtEtaPhiM(event.GENlep_pt[j],event.GENlep_eta[j],event.GENlep_phi[j],event.GENlep_phi[j])
                Z = TLorentzVector()
                Z = (li+lj)
                if(Z.M()>0):
                    nGENZ1 += 1
                    Z_lepindex1.append(i)
                    Z_lepindex2.append(j)
        for i in range(nGENZ1):
            i1 = Z_lepindex1[i]
            i2 = Z_lepindex2[i]
            lep1 = TLorentzVector()
            lep2 = TLorentzVector()
            lep1.SetPtEtaPhiM(event.GENlep_pt[i1],event.GENlep_eta[i1],event.GENlep_phi[i1],event.GENlep_phi[i1])
            lep2.SetPtEtaPhiM(event.GENlep_pt[i2],event.GENlep_eta[i2],event.GENlep_phi[i2],event.GENlep_phi[i2])
            Z1 = lep1+lep2
            GENZ1DeltaM = abs(Z1.M()-Zmass)
            if(GENZ1DeltaM<minZ1DeltaM):
                GENlep_Hindex[0] = i1
                GENlep_Hindex[1] = i2
                passedGENZ1Selection = True

        if(not passedGENZ1Selection): continue

        passedGENJetSelection = False
        GENZ_jetindex1=[]
        GENZ_jetindex2=[]
        GENZjet_Hindex=[0,0]
        nGENZjet = 0
        minZjetDeltaM = 99999.99
        for i in range(nGENZjet):
            for j in range(i+1, nGENZjet):
                if(event.GENZjet_momID[i]!=23 or event.GENZjet_momID[j]!=23): continue
                if(event.GENZjet_mommomID[i]!=25 or event.GENZjet_mommomID[j]!=25): continue
                jeti = TLorentzVector()
                jetj = TLorentzVector()
                jeti.SetPtEtaPhiM(event.GENZjet_pt[i],event.GENZjet_eta[i],event.GENZjet_phi[i],event.GENZjet_mass[i])
                jetj.SetPtEtaPhiM(event.GENZjet_pt[i],event.GENZjet_eta[i],event.GENZjet_phi[i],event.GENZjet_mass[i])
                Zjet = TLorentzVector()
                Zjet = jeti + jetj
                if(Zjet.M()>0):
                    nGENZjet += 1
                    GENZ_jetindex1.append(i)
                    GENZ_jetindex2.append(j)
        for i in range(nGENZjet):
            jet1 = GENZ_jetindex1[i]
            jet2 = GENZ_jetindex2[i]
            jeti = TLorentzVector()
            jetj = TLorentzVector()
            jeti.SetPtEtaPhiM(event.GENZjet_pt[jet1],event.GENZjet_eta[jet1],event.GENZjet_phi[jet1],event.GENZjet_mass[jet1])
            jetj.SetPtEtaPhiM(event.GENZjet_pt[jet2],event.GENZjet_eta[jet2],event.GENZjet_phi[jet2],event.GENZjet_mass[jet2])
            Zjet = jeti + jetj
            GENZjetDeltaM = abs(Zjet.M()-GENZmass)
            if(GENZjetDeltaM<minZjetDeltaM):
                GENZjet_Hindex[0] = jet1
                GENZjet_Hindex[1] = jet2
                passedGENJetSelection = True

        if(passedGENZ1Selection and passedGENJetSelection):
            lep1 = TLorentzVector()
            lep2 = TLorentzVector()
            jet1 = TLorentzVector()
            jet2 = TLorentzVector()
            lep1.SetPtEtaPhiM(event.GENlep_pt[GENlep_Hindex[0]],event.GENlep_eta[GENlep_Hindex[0]],event.GENlep_phi[GENlep_Hindex[0]],event.GENlep_mass[GENlep_Hindex[0]])
            lep2.SetPtEtaPhiM(event.GENlep_pt[GENlep_Hindex[1]],event.GENlep_eta[GENlep_Hindex[1]],event.GENlep_phi[GENlep_Hindex[1]],event.GENlep_mass[GENlep_Hindex[1]])
            jet1.SetPtEtaPhiM(event.GENZjet_pt[GENZjet_Hindex[0]],event.GENZjet_eta[GENZjet_Hindex[0]],event.GENZjet_phi[GENZjet_Hindex[0]],event.GENZjet_mass[GENZjet_Hindex[1]])
            jet2.SetPtEtaPhiM(event.GENZjet_pt[GENZjet_Hindex[1]],event.GENZjet_eta[GENZjet_Hindex[1]],event.GENZjet_phi[GENZjet_Hindex[1]],event.GENZjet_mass[GENZjet_Hindex[1]])

            GENHigss = lep1+lep2+jet2+jet1

            histos[args.sample]['GENH_massall'].Fill(GENHigss.M())
            histos[args.sample]['GENH_massall_weight'].Fill(GENHigss.M(),weight)

            if((GENHigss.M()>=950 and GENHigss.M()<=1050) or (GENHigss.M()>=1800 and GENHigss.M()<=1950)):
                histos[args.sample]['GENH_mass'].Fill(GENHigss.M())
                histos[args.sample]['GENH_mass_weight'].Fill(GENHigss.M(),weight)

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
            if(event.mergedjet_softdropmass[i]<=0 or event.mergedjet_softdropmass[i]>180): continue
            if(event.mergedjet_ZvsQCD_de[i]<0.7): continue

            temptau1 = event.mergedjet_tau1[i]
            temptau2 = event.mergedjet_tau2[i]
            if(temptau1<=0): continue
            temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_softdropmass[i]*event.mergedjet_softdropmass[i])/event.mergedjet_pt[i])
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


        if(event.mergedjet_softdropmass[leadingIndex]>=70 and event.mergedjet_softdropmass[leadingIndex]<=105):
            passedMergedJetSRSelection = True
        else:
            passedMergedJetCRSelection = True

        if(passedMergedJetSRSelection):
            higgscand = TLorentzVector()
            l1_H = TLorentzVector()
            l2_H = TLorentzVector()
            mergedjet_H = TLorentzVector()
            l1_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[0]],event.lepFSR_eta[lep_Hindex[0]],event.lepFSR_phi[lep_Hindex[0]],event.lepFSR_mass[lep_Hindex[0]])
            l2_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[1]],event.lepFSR_eta[lep_Hindex[1]],event.lepFSR_phi[lep_Hindex[1]],event.lepFSR_mass[lep_Hindex[1]])
            mergedjet_H.SetPtEtaPhiM(event.mergedjet_pt[leadingIndex],event.mergedjet_eta[leadingIndex],event.mergedjet_phi[leadingIndex],event.mergedjet_softdropmass[leadingIndex])
            higgscand = l1_H+l2_H+mergedjet_H
            leptonic_Z = l1_H+l2_H
            if((event.GENH_mass[GENleadingIndex]>=950 and event.GENH_mass[GENleadingIndex]<=1050) or (event.GENH_mass[GENleadingIndex]>=1800 and event.GENH_mass[GENleadingIndex]<=1950)):
                histos[args.sample]['Hmass'].Fill(higgscand.M(),weight)
                histos[args.sample]['HvsSD'].Fill(higgscand.M(),event.mergedjet_softdropmass[leadingIndex],weight)

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
            if(event.mergedjet_softdropmass[i]<=0 or event.mergedjet_softdropmass[i]>180): continue
            if(event.mergedjet_ZvsQCD_de[i]<0.7): continue

            temptau1 = event.mergedjet_tau1[i]
            temptau2 = event.mergedjet_tau2[i]
            if(temptau1<=0): continue
            temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_softdropmass[i]*event.mergedjet_softdropmass[i])/event.mergedjet_pt[i])
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
            weight = PH.lumi*1000*94.48*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample.find('DYJetsToLL_Pt-250To400')!=-1):
            weight = PH.lumi*1000*3.648*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='DYJetsToLL_Pt-400To650'):
            weight = PH.lumi*1000*0.4999*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='DYJetsToLL_Pt-650ToInf'):
            weight = PH.lumi*1000*0.04699*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='TTJets'):
            weight = PH.lumi*1000*722.8*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='ZZ_TuneCP5'):
            weight = PH.lumi*1000*12.10*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='WZ'):
            weight = PH.lumi*1000*27.27*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M1000'):
            weight = PH.lumi*1000*0.1023*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M1500'):
            weight = PH.lumi*1000*0.01308*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M2000'):
            weight = PH.lumi*1000*0.0055*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M2500'):
            weight = PH.lumi*1000*0.002207*event.eventWeight/PH.sumWeights[args.sample]
        elif(args.sample=='GluGluHToZZTo2L2Q_M3000'):
            weight = PH.lumi*1000*0.001037*event.eventWeight/PH.sumWeights[args.sample]
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


        if(event.mergedjet_softdropmass[leadingIndex]>=70 and event.mergedjet_softdropmass[leadingIndex]<=105):
            passedMergedJetSRSelection = True
        else:
            passedMergedJetCRSelection = True

        #fill histos in CR and SR region
        if(passedMergedJetSRSelection):
            higgscand = TLorentzVector()
            l1_H = TLorentzVector()
            l2_H = TLorentzVector()
            mergedjet_H = TLorentzVector()
            l1_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[0]],event.lepFSR_eta[lep_Hindex[0]],event.lepFSR_phi[lep_Hindex[0]],event.lepFSR_mass[lep_Hindex[0]])
            l2_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[1]],event.lepFSR_eta[lep_Hindex[1]],event.lepFSR_phi[lep_Hindex[1]],event.lepFSR_mass[lep_Hindex[1]])
            mergedjet_H.SetPtEtaPhiM(event.mergedjet_pt[leadingIndex],event.mergedjet_eta[leadingIndex],event.mergedjet_phi[leadingIndex],event.mergedjet_softdropmass[leadingIndex])
            higgscand = l1_H+l2_H+mergedjet_H
            leptonic_Z = l1_H+l2_H
            histos[args.sample]['Hmass'].Fill(higgscand.M(),weight)
            histos[args.sample]['HvsSD'].Fill(higgscand.M(),event.mergedjet_softdropmass[leadingIndex],weight)


#Write raw histograms into rootfile
outfile.cd()
for var_name in var_names:
    histos[args.sample][var_name].Write()

outfile.Close()
