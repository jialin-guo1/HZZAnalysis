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
var_tau1 = ['Z1_pt','GenZ1_pt','Z1_pt_noweight','GenZ1_pt_noweight']
PH = plotHelper(sample,2018) #initialize a plot class


#book out file to store raw histograms
outfilename = "../RawHistos/%s_ZPtcombine.root"%args.sample
outfile = TFile(outfilename,'recreate')

#book histos
histos = {}
histos[args.sample]={}
histos[args.sample]['Z1_pt']=TH1D(args.sample+'_Z1_pt',args.sample+'_Z1_pt',70,100,1500)
histos[args.sample]['GenZ1_pt']=TH1D(args.sample+'_GenZ1_pt',args.sample+'_GenZ1_pt',70,100,1500)
histos[args.sample]['Z1_pt_noweight']=TH1D(args.sample+'_Z1_pt_noweight',args.sample+'_Z1_pt_noweight',70,100,1500)
histos[args.sample]['GenZ1_pt_noweight']=TH1D(args.sample+'_GenZ1_pt_noweight',args.sample+'_GenZ1_pt_noweight',70,100,1500)

for var_name in var_tau1:
    PH.SetHistStyles(histos[args.sample][var_name],args.sample,var_name)


#================================Ana==================================================
tempTree = PH.trees[args.sample]
nentries = PH.trees[args.sample].GetEntries()
print "[INFO] Start %s analysis"%args.sample
data = 0
for ievent,event in enumerate(tempTree):
    #if(ievent==1000): break
    if(ievent%100000==0):
        print "[INFO] {0:s}/{1:s}".format(str(ievent),str(nentries))
    nlep = event.lep_pt.size()

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

    leadingZindex = 0
    temp_Zpt = 0.0

    if(event.GENZ_pt.size()>=1):
        for i in range(event.GENZ_pt.size()):
            if(event.GENZ_pt[i]>temp_Zpt):
                temp_Zpt = event.GENZ_pt[i]
                leadingZindex = i

        histos[args.sample]['GenZ1_pt'].Fill(event.GENZ_pt[leadingZindex],weight)
        histos[args.sample]['GenZ1_pt_noweight'].Fill(event.GENZ_pt[leadingZindex])



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


    l1_H = TLorentzVector()
    l2_H = TLorentzVector()
    l1_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[0]],event.lepFSR_eta[lep_Hindex[0]],event.lepFSR_phi[lep_Hindex[0]],event.lepFSR_mass[lep_Hindex[0]])
    l2_H.SetPtEtaPhiM(event.lepFSR_pt[lep_Hindex[1]],event.lepFSR_eta[lep_Hindex[1]],event.lepFSR_phi[lep_Hindex[1]],event.lepFSR_mass[lep_Hindex[1]])
    leptonic_Z = l1_H+l2_H
    histos[args.sample]['Z1_pt'].Fill(leptonic_Z.Pt(),weight)
    histos[args.sample]['Z1_pt_noweight'].Fill(leptonic_Z.Pt())


if(data!=0):
    print '[INFO] this is data'


#======================================================================================

#Write raw histograms into rootfile
outfile.cd()

for var_name in var_tau1:
    histos[args.sample][var_name].Write()


outfile.Close()
