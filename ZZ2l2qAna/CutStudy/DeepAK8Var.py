from ROOT import *
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *


samples = ['ZZ','DYJets']
var_names = ['ZvsQCD','tau21','tau1','tau2']
var_tau1 = ['tau1_Zero_pt','tau1_Zero_eta','tau1_Zero_SDmass','tau1_Zero_mass','tau1_notZero_mass','tau1_notZero_SDmass','tau1_notZero_pt','tau1_notZero_eta']
PH = plotHelper(samples,2017) #initialize a plot class

#book out file to store raw histograms
outfilename = "../RawHistos/DeepAK8Var.root"
outfile = TFile(outfilename,"recreate")

#book histos
histos = {}
for sample in samples:
    histos[sample]={}
    histos[sample]['tau1_notZero_pt'] = TH1D(sample+'_tau1_notZero_pt',sample+'_tau1_notZero_pt',30,200,800)
    histos[sample]['tau1_notZero_eta'] = TH1D(sample+'_tau1_notZero_eta',sample+'_tau1_notZero_eta',10,-5,5)
    histos[sample]['tau1_notZero_SDmass'] = TH1D(sample+'_tau1_notZero_SDmass',sample+'_tau1_notZero_SDmass',80,-5,155)
    histos[sample]['tau1_notZero_mass'] = TH1D(sample+'_tau1_notZero_mass',sample+'_tau1_notZero_mass',80,-5,155)
    histos[sample]['tau1_Zero_pt'] = TH1D(sample+'_tau1_Zero_pt',sample+'_tau1_Zero_pt',30,200,800)
    histos[sample]['tau1_Zero_eta'] = TH1D(sample+'_tau1_Zero_eta',sample+'_tau1_Zero_eta',10,-5,5)
    histos[sample]['tau1_Zero_SDmass'] = TH1D(sample+'_tau1_Zero_SDmass',sample+'_tau1_Zero_SDmass',80,-5,155)
    histos[sample]['tau1_Zero_mass'] = TH1D(sample+'_tau1_Zero_mass',sample+'_tau1_Zero_mass',80,-5,155)
    for var_name in var_names:
        histos[sample][var_name]=TH1D(sample+"_"+var_name,sample+"_"+var_name,50,0,1)
        PH.SetHistStyles(histos[sample][var_name],sample,var_name)

for sample in samples:
    for var_name in var_tau1:
        PH.SetHistStyles(histos[sample][var_name],sample,var_name)

#================================Ana==================================================
ntau1_Zero_ZZ = 0.0
ntau1_notZero_ZZ = 0.0
ntau1_notZero_DYJets = 0.
ntau1_Zero_DYJets = 0.
for sample in samples:
    tempTree = PH.trees[sample]
    print "[INFO] Start %s analysis"%sample
    for ievent,event in enumerate(tempTree):
        #if(ievent==1000): break
        nmergedjets = event.mergedjet_pt.size()
        if(nmergedjets<1): continue

        #leptons and photons clear
        for i in range(0,nmergedjets):
            tempDeltaR = 999.0
            isclean_H4l = True

            nlep =event.lep_pt.size()
            for j in range(nlep):
                if(not event.lep_tightId[j]): continue
                if(event.lep_RelIsoNoFSR[j]>0.35): continue
                thisLep = TLorentzVector()
                thisLep.SetPtEtaPhiM(event.lep_pt[j],event.lep_eta[j],event.lep_phi[j],event.lep_mass[j])
                tempDeltaR = deltaR(event.mergedjet_eta[i],event.mergedjet_phi[i],thisLep.Eta(),thisLep.Phi())
                if(tempDeltaR<0.8):
                    isclean_H4l = False

            nfsrphoton = event.fsrPhotons_pt.size()
            for j in range(nfsrphoton):
                if(not event.lep_tightId[event.fsrPhotons_lepindex[j]]): continue
                RelIsoNoFSR=event.lep_RelIsoNoFSR[event.fsrPhotons_lepindex[j]]
                if(RelIsoNoFSR>0.35): continue
                thispho = TLorentzVector()
                thispho.SetPtEtaPhiM(event.fsrPhotons_pt[j],event.fsrPhotons_eta[j],event.fsrPhotons_phi[j],0.0)
                tempDeltaR = deltaR(event.mergedjet_eta[i],event.mergedjet_phi[i],thispho.Eta(),thispho.Phi())
                if(tempDeltaR>0.8):
                    isclean_H4l = False
                    
            #only passed leptons clear jets
            if(isclean_H4l):

                #select the leading jet
                temp_pt = 0.0
                leadingIndex = 0
                for k in range(0,nmergedjets):
                    if(event.mergedjet_pt[k]>temp_pt):
                        temp_pt = event.mergedjet_pt[k]
                        leadingIndex = k

                #fill histos
                tempNsubjet = event.mergedjet_nsubjet[leadingIndex]
                temptau1 = event.mergedjet_tau1[leadingIndex]
                temptau2 = event.mergedjet_tau2[leadingIndex]
                histos[sample]['tau1'].Fill(temptau1)
                histos[sample]['tau2'].Fill(temptau2)

                if(temptau1 != 0):
                    if(sample=='ZZ'):
                        ntau1_notZero_ZZ +=1
                    else:
                        ntau1_notZero_DYJets +=1
                    histos[sample]['ZvsQCD'].Fill(event.mergedjet_ZvsQCD[leadingIndex])
                    histos[sample]['tau21'].Fill(temptau2/temptau1)
                    histos[sample]['tau1_notZero_pt'].Fill(event.mergedjet_pt[leadingIndex])
                    histos[sample]['tau1_notZero_eta'].Fill(event.mergedjet_eta[leadingIndex])
                    histos[sample]['tau1_notZero_mass'].Fill(event.mergedjet_mass[leadingIndex])
                    Sumsubjet = TLorentzVector()
                    for i in range(0,tempNsubjet):
                        tempsubjet = TLorentzVector()
                        tempsubjet.SetPtEtaPhiM(event.mergedjet_subjet_pt[leadingIndex][i],event.mergedjet_subjet_eta[leadingIndex][i],event.mergedjet_subjet_phi[leadingIndex][i],event.mergedjet_subjet_mass[leadingIndex][i])
                        Sumsubjet += tempsubjet
                    histos[sample]['tau1_notZero_SDmass'].Fill(Sumsubjet.M())
                else:
                    if(sample=='ZZ'):
                        ntau1_Zero_ZZ +=1
                    else:
                        ntau1_Zero_DYJets +=1
                    Sumsubjet = TLorentzVector()
                    for i in range(0,tempNsubjet):
                        tempsubjet = TLorentzVector()
                        tempsubjet.SetPtEtaPhiM(event.mergedjet_subjet_pt[leadingIndex][i],event.mergedjet_subjet_eta[leadingIndex][i],event.mergedjet_subjet_phi[leadingIndex][i],event.mergedjet_subjet_mass[leadingIndex][i])
                        #print "[TEST] this subjet mass = "+str(event.mergedjet_subjet_mass[0][i])
                        Sumsubjet += tempsubjet
                    histos[sample]['tau1_Zero_SDmass'].Fill(Sumsubjet.M())
                    histos[sample]['tau1_Zero_pt'].Fill(event.mergedjet_pt[leadingIndex])
                    histos[sample]['tau1_Zero_eta'].Fill(event.mergedjet_eta[leadingIndex])
                    histos[sample]['tau1_Zero_mass'].Fill(event.mergedjet_mass[leadingIndex])
print "[INFO] number of tau1=0 in ZZ: "+str(ntau1_Zero_ZZ)
print "[INFO] ratio of tau1=0 in ZZ: "+str(ntau1_Zero_ZZ/(ntau1_Zero_ZZ+ntau1_notZero_ZZ))
print "[INFO] ratio of tau1=0 in DYJets: "+str(ntau1_Zero_DYJets/(ntau1_Zero_DYJets+ntau1_notZero_DYJets))
#======================================================================================

#Write raw histograms into rootfile
outfile.cd()
for sample in samples:
    for var_name in var_names:
        histos[sample][var_name].Write()

for sample in samples:
    for var_name in var_tau1:
        histos[sample][var_name].Write()

#normalize to one
for sample in samples:
    for var_name in var_names:
        print "[INFO] start Integral {0:s} {1:s}".format(sample,var_name)
        histos[sample][var_name].Scale(1/histos[sample][var_name].Integral())

if(ntau1_Zero_ZZ>0 and ntau1_Zero_DYJets>0):
    for sample in samples:
        for var_name in var_tau1:
            histos[sample][var_name].Scale(1/histos[sample][var_name].Integral())




#Draw Plots
print "[INFO] Start draw plots on canvas"
for var_name in var_names:
    PH.DrawTogether(histos,samples,var_name)

for var_name in var_tau1:
    PH.DrawTogether(histos,samples,var_name)

outfile.Close()
