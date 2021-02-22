from ROOT import *
from deltaR import *
import math
from array import array
import FakeRates as FR
import sys

class OSMethod:
    def __init__(self,year):
        self.year = year
        self.cat_states=['corrected','uncorrected']
        self.cat_names=['EE','EB']
        self.var_names=['el','mu']
        self.nprocess=['data','WZ','TT','DY','qqZZ','Total']
        self.cat_CRnames=['4e', '4mu', '2mu2e', '2e2mu','inclusive']
        self.cat_CRtoSRnames=['2P2F_SR','3P1F','3P1F_bkg','3P1F_ZZ']
        self.cat_failnames = ['3P1F','2P2F']
        self.lep_CRindex=[0,0,0,0]
        self.passedOSCRselection = False

        self.FR_OS_electron_EB_unc=TGraphErrors()
        self.FR_OS_electron_EE_unc=TGraphErrors()
        self.FR_OS_muon_EB_unc=TGraphErrors()
        self.FR_OS_muon_EE_unc=TGraphErrors()
        self.FR_OS_electron_EB=TGraphErrors()
        self.FR_OS_electron_EE=TGraphErrors()
        self.FR_OS_muon_EB=TGraphErrors()
        self.FR_OS_muon_EE=TGraphErrors()

        self.passing={}
        self.failing={}

        self.CRHistos={}
        self.HFromCRHisto={}
        self.ZXHistos={}

        self.vector_X={}
        self.vector_Y={}
        self.vector_EX={} #errors
        self.vector_EY={}

        self.File_CRhisto=TFile()
        self.File_RFhisto=TFile()
        self.File_RFGragh=TFile()

        self.mg_electrons=TMultiGraph()
        self.mg_muons=TMultiGraph()

        self.Zmass = 91.1876

        self.Constructor()

    #===========================================================================
    #==============initialize variables=========================================
    #===========================================================================
    def Constructor(self):
        #book pass/fail histo for FR calculation
        for iprocess in self.nprocess:
            self.passing[iprocess]={}
            self.failing[iprocess]={}
            for var_name in self.var_names:
                self.passing[iprocess][var_name]=TH2D('pass'+iprocess+var_name,'pass'+iprocess+var_name,80, 0, 80, 2, 0, 2)
                self.failing[iprocess][var_name]=TH2D('failing'+iprocess+var_name,'failing'+iprocess+var_name,80, 0, 80, 2, 0, 2)
        #book CR histos
        for cat_failname in self.cat_failnames:
            self.CRHistos[cat_failname]={}
            for cat_CRname in self.cat_CRnames:
                self.CRHistos[cat_failname][cat_CRname]={}
                for iprocess in self.nprocess:
                    self.CRHistos[cat_failname][cat_CRname][iprocess]=TH1D("OSCR"+cat_failname+cat_CRname+iprocess,"OSCR"+cat_failname+cat_CRname+iprocess,40,70,870)

        #book CRtoSR histos
        for cat_name in self.cat_CRtoSRnames:
            self.HFromCRHisto[cat_name]={}
            for cat_CRname in self.cat_CRnames:
                self.HFromCRHisto[cat_name][cat_CRname]=TH1D("OSmidCR"+cat_CRname+cat_name,"OSmidCR"+cat_CRname+cat_name,40,70,870)


        #book ZX histos
        for cat_name in self.cat_CRnames:
            self.ZXHistos[cat_name]={}
            self.ZXHistos[cat_name]['data']=TH1D("ZX"+cat_name+'data',"ZX"+cat_name+'data',40,70,870)
            self.ZXHistos[cat_name]['qqZZ']=TH1D("ZX"+cat_name+'qqZZ',"ZX"+cat_name+'qqZZ',40,70,870)
            self.ZXHistos[cat_name]['data'].Sumw2()
            self.ZXHistos[cat_name]['qqZZ'].Sumw2()


        #book Gragh variables for FR plots
        for cat_state in self.cat_states:
            self.vector_X[cat_state]={}
            self.vector_Y[cat_state]={}
            self.vector_EX[cat_state]={}
            self.vector_EY[cat_state]={}
            for cat_name in self.cat_names:
                self.vector_X[cat_state][cat_name]={}
                self.vector_Y[cat_state][cat_name]={}
                self.vector_EX[cat_state][cat_name]={}
                self.vector_EY[cat_state][cat_name]={}
                for var_name in self.var_names:
                    self.vector_X[cat_state][cat_name][var_name]=array('f',[])
                    self.vector_Y[cat_state][cat_name][var_name]=array('f',[])
                    self.vector_EX[cat_state][cat_name][var_name]=array('f',[])
                    self.vector_EY[cat_state][cat_name][var_name]=array('f',[])

        #set lumi accoding to year
        if(self.year==2016):
            self.lumi = 35.9
        elif(self.year==2017):
            self.lumi = 41.5
        elif(self.year==2018):
            self.lumi = 59.7
        else:
            print "[ERROR] Please set year to 2016 or 2017 or 2018"
            sys.exit()


    #============================================================================
    #====================Fill SS Control Region histos===========================
    #============================================================================
    def FillCRHistos(self,file,process):
        inputfile = TFile(file)
        if (process=='data'):
            inputTree=inputfile.Get("passedEvents")
        else:
            inputTree=inputfile.Ana.Get("passedEvents")
            sumWeights = inputfile.Ana.Get("sumWeights").GetBinContent(1)

        if(inputfile):
            print "[INFO] get file"+" "+str(file)+" "+"for filling CR histos"

        #loop evnet to Fill
        for ievent,event in enumerate(inputTree):
            #if(ievent==100): break
            self.passedOSCRselection = False
            if(event.lep_pt.size()<4): continue

            OSMethod.foundOSCRCandidate(self,event)
            if(not self.passedOSCRselection): continue
            if(process=='WZ'):
                weight= self.lumi*1000*4.67*event.eventWeight/sumWeights
            elif(process=='DY'):
                weight = self.lumi*1000*6225.4*event.eventWeight/sumWeights
            elif(process=='TT'):
                weight = self.lumi*1000*87.31*event.eventWeight/sumWeights
            elif(process=='qqZZ'):
                weight= self.lumi*1000*event.crossSection*event.k_qqZZ_ewk*event.k_qqZZ_qcd_M*event.eventWeight/sumWeights
            else:
                weight=1

            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l3 = TLorentzVector()
            l4 = TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[0]],event.lepFSR_eta[self.lep_CRindex[0]],event.lepFSR_phi[self.lep_CRindex[0]],event.lepFSR_mass[self.lep_CRindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[1]],event.lepFSR_eta[self.lep_CRindex[1]],event.lepFSR_phi[self.lep_CRindex[1]],event.lepFSR_mass[self.lep_CRindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lepFSR_phi[self.lep_CRindex[2]],event.lepFSR_mass[self.lep_CRindex[2]])
            l4.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lepFSR_phi[self.lep_CRindex[3]],event.lepFSR_mass[self.lep_CRindex[3]])
            mass4l = (l1+l2+l3+l4).M()

            #check number of failing
            nZXCRFailedLeptons = 0
            for i in range(0,4):
                if(not (event.lep_tightId[self.lep_CRindex[i]] and event.lep_RelIsoNoFSR[self.lep_CRindex[i]]<0.35)):
                    nZXCRFailedLeptons+=1
            #fill histos
            if(nZXCRFailedLeptons==1):
                self.CRHistos['3P1F']['inclusive'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.CRHistos['3P1F']['4e'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.CRHistos['3P1F']['4mu'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==11 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.CRHistos['3P1F']['2e2mu'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==13 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.CRHistos['3P1F']['2mu2e'][process].Fill(mass4l,weight)
            if(nZXCRFailedLeptons==2):
                self.CRHistos['2P2F']['inclusive'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.CRHistos['2P2F']['4e'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.CRHistos['2P2F']['4mu'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==11 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.CRHistos['2P2F']['2e2mu'][process].Fill(mass4l,weight)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==13 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.CRHistos['2P2F']['2mu2e'][process].Fill(mass4l,weight)

    def FillCRHistosTest(self,file,process):
        inputfile = TFile(file)
        if (process=='data'):
            inputTree=inputfile.Get("passedEvents")
        else:
            inputTree=inputfile.Ana.Get("passedEvents")
            sumWeights = inputfile.Ana.Get("sumWeights").GetBinContent(1)

        if(inputfile):
            print "[INFO] get file"+" "+str(file)+" "+"for filling CR histos"

        #loop evnet to Fill
        for ievent, event in enumerate(inputTree):
            #if(ievent==100):break
            if(not event.passedZXCRSelection): continue
            if(process=='WZ'):
                weight= self.lumi*1000*4.67*event.eventWeight/sumWeights
            elif(process=='DY'):
                weight = self.lumi*1000*6225.4*event.eventWeight/sumWeights
            elif(process=='TT'):
                weight = self.lumi*1000*87.31*event.eventWeight/sumWeights
            elif(process=='qqZZ'):
                weight= self.lumi*1000*event.crossSection*event.k_qqZZ_ewk*event.k_qqZZ_qcd_M*event.eventWeight/sumWeights
            else:
                weight=1
            if(event.nZXCRFailedLeptons==1):
                self.CRHistos['3P1F']['inclusive'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.CRHistos['3P1F']['4e'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.CRHistos['3P1F']['4mu'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==11 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.CRHistos['3P1F']['2e2mu'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==13 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.CRHistos['3P1F']['2mu2e'][process].Fill(event.mass4l,weight)
            if(event.nZXCRFailedLeptons==2):
                self.CRHistos['2P2F']['inclusive'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.CRHistos['2P2F']['4e'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.CRHistos['2P2F']['4mu'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==11 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.CRHistos['2P2F']['2e2mu'][process].Fill(event.mass4l,weight)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==13 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.CRHistos['2P2F']['2mu2e'][process].Fill(event.mass4l,weight)




    #===========================================================================
    #================Get Control Region candidates==============================
    #===========================================================================
    def foundOSCRCandidate(self,event):
        n_Zs = 0
        Z_pt = []
        Z_eta = []
        Z_phi = []
        Z_mass = []
        Z_lepindex1 = []
        Z_lepindex2 = []

        Zmass = 91.1876
        minZ1DeltaM = 99999.99
        Nlep = event.lep_pt.size()

        # make all Z candidates including any FSR photons,
        for i in range(Nlep):
            for j in range(i+1,Nlep):
                lifsr = TLorentzVector()
                ljfsr = TLorentzVector()
                lifsr.SetPtEtaPhiM(event.lepFSR_pt[i], event.lepFSR_eta[i], event.lepFSR_phi[i], event.lepFSR_mass[i])
                ljfsr.SetPtEtaPhiM(event.lepFSR_pt[j], event.lepFSR_eta[j], event.lepFSR_phi[j], event.lepFSR_mass[j])
                Z = TLorentzVector()
                Z = (lifsr + ljfsr)
                if(Z.M()>0):
                    n_Zs = n_Zs + 1
                    Z_pt.append(Z.Pt())
                    Z_eta.append(Z.Eta())
                    Z_phi.append(Z.Phi())
                    Z_mass.append(Z.M())
                    Z_lepindex1.append(i)
                    Z_lepindex2.append(j)

        # consider all Z and same sign cnadidate
        for i in range(n_Zs):
            for j in range(i+1,n_Zs):
                i1 = Z_lepindex1[i]
                i2 = Z_lepindex2[i]
                j1 = Z_lepindex1[j]
                j2 = Z_lepindex2[j]
                if(i1 == j1 or i1==j2 or i2==j1 or i2==j2): continue
                # opposite sign and same flavour for Z ; opposite sign same flavour for fack leptons
                if(event.lep_id[i1]+event.lep_id[i2]!=0 or event.lep_id[j1]+event.lep_id[j2]!=0): continue
                lep1 = TLorentzVector()
                lep2 = TLorentzVector()
                lep3 = TLorentzVector()
                lep4 = TLorentzVector()
                lep1.SetPtEtaPhiM(event.lepFSR_pt[i1],event.lepFSR_eta[i1],event.lepFSR_phi[i1],event.lepFSR_mass[i1])
                lep2.SetPtEtaPhiM(event.lepFSR_pt[i2],event.lepFSR_eta[i2],event.lepFSR_phi[i2],event.lepFSR_mass[i2])
                lep3.SetPtEtaPhiM(event.lepFSR_pt[j1],event.lepFSR_eta[j1],event.lepFSR_phi[j1],event.lepFSR_mass[j1])
                lep4.SetPtEtaPhiM(event.lepFSR_pt[j2],event.lepFSR_eta[j2],event.lepFSR_phi[j2],event.lepFSR_mass[j2])

                Z1 = TLorentzVector()
                OSleps = TLorentzVector()
                OSleps = lep3+lep4
                Z1 = lep1 + lep2
                Z1_lepindex = [0,0]
                Z1DeltaM = abs(Z1.M()-Zmass)

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
                if (deltaR(lep1.Eta(),lep1.Phi(),lep3.Eta(),lep3.Phi())<0.02): continue
                if (deltaR(lep1.Eta(),lep1.Phi(),lep4.Eta(),lep4.Phi())<0.02): continue
                if (deltaR(lep2.Eta(),lep2.Phi(),lep3.Eta(),lep3.Phi())<0.02): continue
                if (deltaR(lep2.Eta(),lep2.Phi(),lep4.Eta(),lep4.Phi())<0.02): continue
                if (deltaR(lep3.Eta(),lep3.Phi(),lep4.Eta(),lep4.Phi())<0.02): continue
                # Check M(l+,l-)>4.0 GeV for any OS pair , Do not include FSR photons
                allM = []
                lep1_noFSR = TLorentzVector()
                lep2_noFSR = TLorentzVector()
                lep3_noFSR = TLorentzVector()
                lep4_noFSR = TLorentzVector()
                lep1_noFSR.SetPtEtaPhiM(event.lep_pt[i1],event.lep_eta[i1],event.lep_phi[i1],event.lep_mass[i1])
                lep2_noFSR.SetPtEtaPhiM(event.lep_pt[i2],event.lep_eta[i2],event.lep_phi[i2],event.lep_mass[i2])
                lep3_noFSR.SetPtEtaPhiM(event.lep_pt[j1],event.lep_eta[j1],event.lep_phi[j1],event.lep_mass[j1])
                lep4_noFSR.SetPtEtaPhiM(event.lep_pt[j2],event.lep_eta[j2],event.lep_phi[j2],event.lep_mass[j2])
                i1i2 = TLorentzVector()
                i1i2 = lep1_noFSR+lep2_noFSR
                allM.append(i1i2.M())
                if(event.lep_id[i1]*event.lep_id[j1]<0):
                    i1j1 = TLorentzVector()
                    i1j2 = TLorentzVector()
                    i1j2 = lep1_noFSR+lep4_noFSR
                    i1j1 = lep1_noFSR+lep3_noFSR
                    allM.append(i1j1.M())
                    allM.append(i1j2.M())
                else:
                    i2j1 = TLorentzVector()
                    i2j2 = TLorentzVector()
                    i2j1 = lep2_noFSR+lep3_noFSR
                    i2j2 = lep2_noFSR+lep4_noFSR
                    allM.append(i2j1.M())
                    allM.append(i2j2.M())
                allM.sort()
                # print " list of OS pair mass after sort : " + str(allM)
                if(allM[0]<4.0): continue

                # Check isolation cut (without FSR ) for Z1 leptons
                #if(abs(event.lep_id[Z1_lepindex[0]])==13):
                if( event.lep_RelIsoNoFSR[Z1_lepindex[0]]>0.35): continue
                #if(abs(event.lep_id[Z1_lepindex[1]])==13):
                if( event.lep_RelIsoNoFSR[Z1_lepindex[1]]>0.35): continue

                # Check tight ID cut for Z1 leptons
                if (not event.lep_tightId[Z1_lepindex[0]]): continue
                if (not event.lep_tightId[Z1_lepindex[1]]): continue
                #if (not event.lep_tightId[j1]): continue
                #if (not event.lep_tightId[j2]): continue

                # check the masswindow
                if(Z1.M()<40 or Z1.M()>120 or OSleps.M()<12 or OSleps.M()>120): continue
                #mass4l = (lep1+lep2+lep3+lep4).M()
                # if(mass4l<100): continue
                # Check if this candidate has the best Z1 and highest scalar sum of Z2 lepton pt
                if(Z1DeltaM<minZ1DeltaM):
                    minZ1DeltaM = Z1DeltaM
                    massZ1 = Z1.M()
                    self.lep_CRindex[0] = Z1_lepindex[0]
                    self.lep_CRindex[1] = Z1_lepindex[1]
                    self.lep_CRindex[2] = j1
                    self.lep_CRindex[3] = j2
                    self.passedOSCRselection = True

    #===========================================================================
    #===============Save raw Control Region=====================================
    #===========================================================================
    def SaveCRHistos(self):
        file = "../RawHistos/CRHistos_OS_%s_Legacy.root"%str(self.year)
        outfile  = TFile(file,"recreate")
        outfile.cd()

        for cat_failname in self.cat_failnames:
            for cat_name in self.cat_CRnames:
                for iprocess in self.nprocess:
                    self.CRHistos[cat_failname][cat_name][iprocess].Write()

        outfile.Close()
        print "[INFO] All Control Region histograms saved."


    #==========================================================================
    #================Get Raw Control Region histos=============================
    #==========================================================================
    def GetCRHistos(self):
        file = "../RawHistos/CRHistos_OS_%s_Legacy.root"%str(self.year)
        self.File_CRhisto = TFile(file)

        for cat_failname in self.cat_failnames:
            for cat_name in self.cat_CRnames:
                for iprocess in self.nprocess:
                    self.CRHistos[cat_failname][cat_name][iprocess]= self.File_CRhisto.Get("OSCR"+cat_failname+cat_name+iprocess)

        print "[INFO] All Control Region histograms retrieved from file."

    #==========================================================================
    #=======================plot Control Region================================
    #==========================================================================
    def PlotCR(self):
        c = TCanvas("CR","CR",600,600)
        for cat_failname in self.cat_failnames:
            for cat_name in self.cat_CRnames:
                self.CRHistos[cat_failname][cat_name]['WZ'].SetFillColor(kMagenta)
                self.CRHistos[cat_failname][cat_name]['qqZZ'].SetFillColor(kCyan+1)
                self.CRHistos[cat_failname][cat_name]['DY'].SetFillColor(kGreen + 1)
                self.CRHistos[cat_failname][cat_name]['TT'].SetFillColor(kBlue + 1)

                self.CRHistos[cat_failname][cat_name]['WZ'].SetLineColor(kMagenta)
                self.CRHistos[cat_failname][cat_name]['qqZZ'].SetLineColor(kCyan+1)
                self.CRHistos[cat_failname][cat_name]['DY'].SetLineColor(kGreen-1)
                self.CRHistos[cat_failname][cat_name]['TT'].SetLineColor(kBlue-2)

                self.CRHistos[cat_failname][cat_name]['data'].SetMarkerSize(0.8)
                self.CRHistos[cat_failname][cat_name]['data'].SetMarkerStyle(20)
                self.CRHistos[cat_failname][cat_name]['data'].SetBinErrorOption(TH1.kPoisson)
                self.CRHistos[cat_failname][cat_name]['data'].SetLineColor(kBlack)

                stack = THStack("stack","stack")
                stack.Add(self.CRHistos[cat_failname][cat_name]['qqZZ'])
                stack.Add(self.CRHistos[cat_failname][cat_name]['WZ'])
                stack.Add(self.CRHistos[cat_failname][cat_name]['TT'])
                stack.Add(self.CRHistos[cat_failname][cat_name]['DY'])
                stack.Draw("histo")

                data_max = self.CRHistos[cat_failname][cat_name]['data'].GetBinContent(self.CRHistos[cat_failname][cat_name]['data'].GetMaximumBin())
                data_max_error = self.CRHistos[cat_failname][cat_name]['data'].GetBinErrorUp(self.CRHistos[cat_failname][cat_name]['data'].GetMaximumBin())
                stack.SetMaximum((data_max+data_max_error)*1.1)
                stack.SetMinimum(0)

                if(cat_name=='4e'): label="m_{4#font[12]{e}} (GeV)"
                if(cat_name=='4mu'): label="m_{4#font[12]{#mu}} (GeV)"
                if(cat_name=='2e2mu'): label="m_{2#font[12]{e}2#font[12]{#mu}} (GeV)"
                if(cat_name=='2mu2e'): label="m_{2#font[12]{#mu}2#font[12]{e}} (GeV)"

                stack.GetXaxis().SetTitle(label)
                stack.GetXaxis().SetTitleSize(0.04)
                stack.GetXaxis().SetLabelSize(0.04)
                stack.GetYaxis().SetTitle("Event/%s GeV"%str(self.CRHistos[cat_failname][cat_name]['data'].GetBinWidth(1)))
                stack.GetYaxis().SetTitleSize(0.04)
                stack.GetYaxis().SetLabelSize(0.04)

                self.CRHistos[cat_failname][cat_name]['data'].Draw("SAME p E1 X0")

                legend = TLegend()
                legend = OSMethod.CreateLegend_CR(self,'right',cat_name,cat_failname)
                legend.Draw()

                cms_label,lumi_label = OSMethod.MakeCMSandLumiLabel(self)

                lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
                lumi_label.Draw('same')
                cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
                cms_label.Draw('same')

                plotname = "plot/OSCR_"+cat_failname+cat_name+"_%s"%str(self.year)
                OSMethod.SavePlots(self,c,plotname)


    #============================================================================
    #=============make cms and lumi label========================================
    #============================================================================
    def MakeCMSandLumiLabel(self):
        cms=TLatex()
        cms.SetTextSize(0.03)
        cms.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')

        lumi=TLatex()
        lumi.SetTextSize(0.03)
        lumi.SetTextAlign(31)
        lumi.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))

        return cms,lumi


    #============================================================================
    #===================create CR legend=========================================
    #============================================================================
    def CreateLegend_CR(self,position,cat_name,cat_failname):
        leg = TLegend()
        if(position=='right'):
            leg = TLegend( .64, .65, .97, .85 )
        elif(position=='left'):
            leg=TLegend(.18,.65,.51,.85)
        else:
            print "[Error] Please enter \"left\" or \"right\" "

        leg.SetFillColor(0)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        leg.AddEntry(self.CRHistos[cat_failname][cat_name]['data'],"data",'p')
        leg.AddEntry(self.CRHistos[cat_failname][cat_name]['WZ'],"WZ",'f')
        leg.AddEntry(self.CRHistos[cat_failname][cat_name]['TT'],"t#bar{t} + jets",'f')
        leg.AddEntry(self.CRHistos[cat_failname][cat_name]['qqZZ'],"Z#gamma*, ZZ",'f')
        leg.AddEntry(self.CRHistos[cat_failname][cat_name]['DY'],"Z + jets",'f')

        return leg


    #===========================================================================
    #============Fill FakeRates histos==========================================
    #===========================================================================
    def FillFRHistos(self,file,process):
        inputfile = TFile(file)
        if(process=='WZ'):
            inputTree = inputfile.Ana.Get("passedEvents")
            sumWeights = inputfile.Ana.Get("sumWeights").GetBinContent(1)
        else:
            inputTree = inputfile.Get("passedEvents")

        if(inputfile):
            print "[INFO] get file"+" "+str(file)+" "+"for filling pass/fail histos"

        for ievent,event in enumerate(inputTree):
            #if(ievent==100):break
            if(not event.passedZ1LSelection): continue
            if(event.met>25): continue
            #check |Z1-Zm|<7 to reduce effiection of photon conversion
            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
            Z1 = TLorentzVector()
            Z1 = l1+l2
            if(abs(Z1.M()-self.Zmass)>7): continue
            if(process=='WZ'):
                weight = 59.7*1000*4.67*event.eventWeight/sumWeights
            else:
                weight = 1
            if(event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35 and event.lep_tightId[event.lep_Hindex[2]]):
                if(abs(event.lep_id[event.lep_Hindex[2]])==11):
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        self.passing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)  #0.5 for EB 1.5 for EE
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        self.passing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
                if(abs(event.lep_id[event.lep_Hindex[2]])==13):
                    if(abs(event.lep_eta[event.lep_Hindex[2]])<1.2):
                        self.passing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    if(abs(event.lep_eta[event.lep_Hindex[2]])>=1.2):
                        self.passing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
            else:
                if(abs(event.lep_id[event.lep_Hindex[2]])==11):
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        self.failing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        self.failing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
                if(abs(event.lep_id[event.lep_Hindex[2]])==13):
                    if(abs(event.lep_eta[event.lep_Hindex[2]])<1.2):
                        self.failing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    if(abs(event.lep_eta[event.lep_Hindex[2]])>=1.2):
                        self.failing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)

        print "[INFO] passing and failing histos have been created"


    #===========================================================================
    #=================Save Raw passing and failing histos=======================
    #===========================================================================
    def SaveFRHistos(self,subtractWZ,remove_negative_bins):
        outfilename="../RawHistos/FRHistos_OS_%s_Legacy.root"%str(self.year)
        outfile = TFile(outfilename,"recreate")
        outfile.cd()
        for var_name in self.var_names:
            self.passing['Total'][var_name].Add(self.passing['data'][var_name],1.)
            self.failing['Total'][var_name].Add(self.failing['data'][var_name],1.)

        # Subtract WZ contribution from MC estimate
        if(subtractWZ):
            OSMethod.subtractWZ(self)

        if(remove_negative_bins):
            for var_name in self.var_names:
                OSMethod.RemoveNegativeBins2D(self,self.passing['Total'][var_name])
                OSMethod.RemoveNegativeBins2D(self,self.passing['Total'][var_name])
            print "[INFO] Negative bins removed."


        # that will clear up histos, so when we want to use them again, we should handle them from where we stroe
        for var_name in self.var_names:
            for iprocess in self.nprocess:
                self.passing[iprocess][var_name].Write()
                self.failing[iprocess][var_name].Write()

        outfile.Close()
        print "[INFO] All FakeRate histograms saved."


    #===========================================================================
    #==================Subtract WZ contribution from MC estimate================
    #===========================================================================
    def subtractWZ(self):
        for var_name in self.var_names:
            self.passing['Total'][var_name].Sumw2()
            self.failing['Total'][var_name].Sumw2()
            self.passing['Total'][var_name].Add(self.passing['WZ'][var_name],-1.)
            self.failing['Total'][var_name].Add(self.failing['WZ'][var_name],-1.)
        print "[INFO] WZ contribution subtracted."


    #===========================================================================
    #==================Remove Negative Bins=====================================
    #===========================================================================
    def  RemoveNegativeBins2D(self,histo):
        for i_bin_x in range(1,histo.GetXaxis().GetNbins()):
            for i_bin_y in range(1,histo.GetYaxis().GetNbins()):
                if(histo.GetBinContent(i_bin_x,i_bin_y)<0):
                    histo.SetBinContent(i_bin_x,i_bin_y,0.0)


    #===========================================================================
    #================= Get FR Histos============================================
    #===========================================================================
    def GetFRHistos(self):

        filename="../RawHistos/FRHistos_OS_%s_Legacy.root"%str(self.year)
        self.File_RFhisto=TFile(filename)

        for iprocess in self.nprocess:
            self.passing[iprocess]={}
            self.failing[iprocess]={}
            for var_name in self.var_names:
                self.passing[iprocess][var_name]=self.File_RFhisto.Get('pass'+iprocess+var_name)
                self.failing[iprocess][var_name]=self.File_RFhisto.Get('failing'+iprocess+var_name)

        print "[INFO] All FakeRate histograms retrieved from file."



    #============================================================================
    #==================prodece FakeRate from data================================
    #============================================================================
    def OSFRproduce(self,process):

        outfilename="../RawHistos/FakeRates_OS_%s_Legacy.root"%str(self.year)

        #calculate FakeRates and save Gragh
        pt_bins=[5, 7, 10, 20, 30, 40, 50, 80]
        n_pt_bins=8
        for i_pt_bin in range(n_pt_bins-1):
            temp_NP = 0
            temp_NF = 0
            temp_error_x = 0
            temp_error_NP = 0.0
            temp_error_NF = 0.0
            for var_name in self.var_names:
                if(var_name=='el' and i_pt_bin==0): continue #electrons do not have 5 - 7 GeV bin
                temp_NP = self.passing['Total'][var_name].IntegralAndError(self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NP))
                temp_NF = self.failing['Total'][var_name].IntegralAndError(self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NF))
                temp_error_NP = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,1)
                temp_error_NF = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,1)


                self.vector_X['corrected']['EB'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['corrected']['EB'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['corrected']['EB'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['corrected']['EB'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

                temp_NP = self.passing['Total'][var_name].IntegralAndError(self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NP))
                temp_NF = self.failing['Total'][var_name].IntegralAndError(self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NF))
                temp_error_NP = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,2)
                temp_error_NF = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,2)

                self.vector_X['corrected']['EE'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['corrected']['EE'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['corrected']['EE'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['corrected']['EE'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*pow(temp_error_NF,2)))

                #Just for fake rate plots calculate the same for histograms without WZ subtraction
                temp_NP = self.passing['data'][var_name].IntegralAndError(self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NP))
                temp_NF = self.failing['data'][var_name].IntegralAndError(self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NF))
                temp_error_NP = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,1)
                temp_error_NF = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,1)

                self.vector_X['uncorrected']['EB'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['uncorrected']['EB'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['uncorrected']['EB'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['uncorrected']['EB'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

                temp_NP = self.passing['data'][var_name].IntegralAndError(self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NP))
                temp_NF = self.failing['data'][var_name].IntegralAndError(self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NF))
                temp_error_NP = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,2)
                temp_error_NF = OSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,2)

                self.vector_X['uncorrected']['EE'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['uncorrected']['EE'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['uncorrected']['EE'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['uncorrected']['EE'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

        print "[INFO] check type "
        print "vector_X['uncorrected']['EB']['el'][0]  = " +str(self.vector_X['uncorrected']['EB']['el'][0])


        print "[INFO] check value of vector ele after append value"
        print "vector_X['uncorrected']['EB']['el'] = "+str(self.vector_X['uncorrected']['EB']['el'])
        print "vector_Y['uncorrected']['EB']['el']= "+str(self.vector_Y['uncorrected']['EB']['el'])
        print "vector_EX['uncorrected']['EB']['el'] = "+str(self.vector_EX['uncorrected']['EB']['el'])
        print "vector_EY['uncorrected']['EB']['el'] = "+str(self.vector_EY['uncorrected']['EB']['el'])

        print "[INFO] check value of vector muon after append value"
        print "vector_X['uncorrected']['EE']['mu'] = "+str(self.vector_X['uncorrected']['EE']['mu'])
        print "vector_Y['uncorrected']['EE']['mu'] = "+str(self.vector_Y['uncorrected']['EE']['mu'])
        print "vector_EX['uncorrected']['EE']['mu'] = "+str(self.vector_EX['uncorrected']['EE']['mu'])
        print "vector_EY['uncorrected']['EE']['mu'] = "+str(self.vector_EY['uncorrected']['EE']['mu'])


        self.FR_OS_electron_EB_unc = TGraphErrors (len(self.vector_X['uncorrected']['EB']['el']),
											  self.vector_X['uncorrected']['EB']['el'],
											  self.vector_Y['uncorrected']['EB']['el'],
											  self.vector_EX['uncorrected']['EB']['el'],
											  self.vector_EY['uncorrected']['EB']['el'])
        self.FR_OS_electron_EB_unc.SetName("FR_OS_electron_EB_unc")

        self.FR_OS_electron_EE_unc = TGraphErrors (len(self.vector_X['uncorrected']['EE']['el']),
											  self.vector_X['uncorrected']['EE']['el'],
											  self.vector_Y['uncorrected']['EE']['el'],
											  self.vector_EX['uncorrected']['EE']['el'],
											  self.vector_EY['uncorrected']['EE']['el'])
        self.FR_OS_electron_EE_unc.SetName("FR_OS_electron_EE_unc")

        self.FR_OS_muon_EE_unc = TGraphErrors (len(self.vector_X['uncorrected']['EE']['mu']),
										  self.vector_X['uncorrected']['EE']['mu'],
										  self.vector_Y['uncorrected']['EE']['mu'],
										  self.vector_EX['uncorrected']['EE']['mu'],
										  self.vector_EY['uncorrected']['EE']['mu'])
        self.FR_OS_muon_EE_unc.SetName("FR_OS_muon_EE_unc")

        self.FR_OS_muon_EB_unc = TGraphErrors (len(self.vector_X['uncorrected']['EB']['mu']),
										  self.vector_X['uncorrected']['EB']['mu'],
										  self.vector_Y['uncorrected']['EB']['mu'],
										  self.vector_EX['uncorrected']['EB']['mu'],
										  self.vector_EY['uncorrected']['EB']['mu'])
        self.FR_OS_muon_EB_unc.SetName("FR_OS_muon_EB_unc")

        self.FR_OS_muon_EE = TGraphErrors (len(self.vector_X['corrected']['EE']['mu']),
										  self.vector_X['corrected']['EE']['mu'],
										  self.vector_Y['corrected']['EE']['mu'],
										  self.vector_EX['corrected']['EE']['mu'],
										  self.vector_EY['corrected']['EE']['mu'])
        self.FR_OS_muon_EE.SetName("FR_OS_muon_EE")

        self.FR_OS_muon_EB = TGraphErrors (len(self.vector_X['corrected']['EB']['mu']),
										  self.vector_X['corrected']['EB']['mu'],
										  self.vector_Y['corrected']['EB']['mu'],
										  self.vector_EX['corrected']['EB']['mu'],
										  self.vector_EY['corrected']['EB']['mu'])
        self.FR_OS_muon_EB.SetName("FR_OS_muon_EB")

        self.FR_OS_electron_EB = TGraphErrors (len(self.vector_X['corrected']['EB']['el']),
											  self.vector_X['corrected']['EB']['el'],
											  self.vector_Y['corrected']['EB']['el'],
											  self.vector_EX['corrected']['EB']['el'],
											  self.vector_EY['corrected']['EB']['el'])
        self.FR_OS_electron_EB.SetName("FR_OS_electron_EB")

        self.FR_OS_electron_EE = TGraphErrors (len(self.vector_X['corrected']['EE']['el']),
											  self.vector_X['corrected']['EE']['el'],
											  self.vector_Y['corrected']['EE']['el'],
											  self.vector_EX['corrected']['EE']['el'],
											  self.vector_EY['corrected']['EE']['el'])
        self.FR_OS_electron_EE.SetName("FR_OS_electron_EE")



        OSMethod.plotFR(self)
        OSMethod.SaveFRGragh(self,outfilename)

    #===========================================================================
    #===================calculate Error from Every bin==========================
    #===========================================================================
    def GetErorr(self,pt_bin,i_pt_bin,process,var_name,cat,loc):
        if(cat):
            ispass=True
        else:
            ispass=False
        if(loc==1):
            isEB=True
        else:
            isEB=False
        error = 0.0
        for x_pt in range(pt_bin[i_pt_bin],pt_bin[i_pt_bin+1]):
            #print "x_pt = "+str(x_pt)
            if(isEB):
                if(ispass):
                    x_bin = self.passing[process][var_name].GetXaxis().FindBin(x_pt)
                    error += self.passing[process][var_name].GetBinError(x_bin,1)*self.passing[process][var_name].GetBinError(x_bin,1)
                else:
                    x_bin = self.failing[process][var_name].GetXaxis().FindBin(x_pt)
                    error += self.failing[process][var_name].GetBinError(x_bin,1)*self.failing[process][var_name].GetBinError(x_bin,1)
            else:
                if(ispass):
                    x_bin = self.passing[process][var_name].GetXaxis().FindBin(x_pt)
                    error += self.passing[process][var_name].GetBinError(x_bin,2)*self.passing[process][var_name].GetBinError(x_bin,2)
                else:
                    x_bin = self.failing[process][var_name].GetXaxis().FindBin(x_pt)
                    error += self.failing[process][var_name].GetBinError(x_bin,2)*self.failing[process][var_name].GetBinError(x_bin,2)

        return math.sqrt(error)


    #============================================================================
    #==================Draw FR plots=============================================
    #============================================================================
    def plotFR(self):
        c_ele=TCanvas("FR_ele", "FR_ele", 700,700)
        c_muon=TCanvas("FR_muon","FRmuon",700,700)

        self.mg_electrons.Add(self.FR_OS_electron_EB_unc)
        self.FR_OS_electron_EB_unc.SetLineColor(kBlue)
        self.FR_OS_electron_EB_unc.SetLineStyle(1)
        self.FR_OS_electron_EB_unc.SetMarkerSize(0)
        self.FR_OS_electron_EB_unc.SetTitle("barel uncorrected")
        self.mg_electrons.Add(self.FR_OS_electron_EE_unc)
        self.FR_OS_electron_EE_unc.SetLineColor(kRed);
        self.FR_OS_electron_EE_unc.SetLineStyle(1);
        self.FR_OS_electron_EE_unc.SetMarkerSize(0);
        self.FR_OS_electron_EE_unc.SetTitle("endcap uncorrected")

        self.mg_electrons.Add(self.FR_OS_electron_EB)
        self.FR_OS_electron_EB.SetLineColor(kBlue)
        self.FR_OS_electron_EB.SetLineStyle(2)
        self.FR_OS_electron_EB.SetMarkerSize(0)
        self.FR_OS_electron_EB.SetTitle("barel corrected")
        self.mg_electrons.Add(self.FR_OS_electron_EE)
        self.FR_OS_electron_EE.SetLineColor(kRed);
        self.FR_OS_electron_EE.SetLineStyle(2);
        self.FR_OS_electron_EE.SetMarkerSize(0);
        self.FR_OS_electron_EE.SetTitle("endcap corrected")

        self.mg_muons.Add(self.FR_OS_muon_EB_unc)
        self.FR_OS_muon_EB_unc.SetLineColor(kBlue)
        self.FR_OS_muon_EB_unc.SetLineStyle(1)
        self.FR_OS_muon_EB_unc.SetMarkerSize(0)
        self.FR_OS_muon_EB_unc.SetTitle("barel uncorrected")
        self.mg_muons.Add(self.FR_OS_muon_EE_unc)
        self.FR_OS_muon_EE_unc.SetLineColor(kRed)
        self.FR_OS_muon_EE_unc.SetLineStyle(1)
        self.FR_OS_muon_EE_unc.SetMarkerSize(0)
        self.FR_OS_muon_EE_unc.SetTitle("endcap uncorrected")

        self.mg_muons.Add(self.FR_OS_muon_EB)
        self.FR_OS_muon_EB.SetLineColor(kBlue)
        self.FR_OS_muon_EB.SetLineStyle(2)
        self.FR_OS_muon_EB.SetMarkerSize(0)
        self.FR_OS_muon_EB.SetTitle("barel corrected")
        self.mg_muons.Add(self.FR_OS_muon_EE)
        self.FR_OS_muon_EE.SetLineColor(kRed)
        self.FR_OS_muon_EE.SetLineStyle(2)
        self.FR_OS_muon_EE.SetMarkerSize(0)
        self.FR_OS_muon_EE.SetTitle("endcap corrected")

        gStyle.SetEndErrorSize(0)

        leg_ele = TLegend()
        leg_muon = TLegend()
        c_ele.cd()
        self.mg_electrons.Draw("AP")
        self.mg_electrons.GetXaxis().SetTitle("p_{T} [GeV]")
        self.mg_electrons.GetYaxis().SetTitle("Fake Rate")
        self.mg_electrons.GetYaxis().SetTitleSize(0.029)
        self.mg_electrons.SetTitle("Electron fake rate")
        self.mg_electrons.SetMaximum(0.35)
        leg_ele = OSMethod.CreateLegend_FR(self,"left",self.FR_OS_electron_EB_unc,self.FR_OS_electron_EE_unc,self.FR_OS_electron_EB,self.FR_OS_electron_EE)
        leg_ele.Draw()
        OSMethod.SavePlots(self,c_ele, "plot/FR_OS_electrons")

        c_muon.cd()
        self.mg_muons.Draw("AP")
        self.mg_muons.GetXaxis().SetTitle("p_{T} [GeV]")
        self.mg_muons.GetYaxis().SetTitle("Fake Rate")
        self.mg_muons.GetYaxis().SetTitleSize(0.029)
        self.mg_muons.SetTitle("Muon fake rate")
        self.mg_muons.SetMaximum(0.35)
        leg_mu = OSMethod.CreateLegend_FR(self,"left",self.FR_OS_muon_EB_unc,self.FR_OS_muon_EE_unc,self.FR_OS_muon_EB,self.FR_OS_muon_EE)
        leg_mu.Draw()
        OSMethod.SavePlots(self,c_muon, "plot/FR_OS_muons")


    #===========================================================================
    #===================Create Legend for FakeRates=============================
    #===========================================================================
    def CreateLegend_FR(self,position,EB_unc,EE_unc,EB_cor,EE_cor):
        if(position=='right'):
            leg = TLegend( .64, .65, .97, .85 )
        elif(position=='left'):
            leg=TLegend(.18,.65,.51,.85)
        else:
            print "[Error] Please enter \"left\" or \"right\" "
        leg.AddEntry( EB_unc, "barrel uncorrected", "l" )
        leg.AddEntry( EB_cor, "barrel corrected","l")
        leg.AddEntry( EE_unc, "endcap uncorrected", "l" )
        leg.AddEntry( EE_cor, "endcap corrected", "l" )
        return leg



    #===========================================================================
    #===================save raw FakeRates Gragh================================
    #===========================================================================
    def SaveFRGragh(self,outfilename):
        self.File_RFGragh=TFile(outfilename,"RECREATE")
        self.File_RFGragh.cd()
        self.FR_OS_electron_EB_unc.Write()
        self.FR_OS_electron_EE_unc.Write()
        self.FR_OS_muon_EE_unc.Write()
        self.FR_OS_muon_EB_unc.Write()
        self.FR_OS_electron_EB.Write()
        self.FR_OS_electron_EE.Write()
        self.FR_OS_muon_EE.Write()
        self.FR_OS_muon_EB.Write()
        self.File_RFGragh.Close()

        print "[INFO] All FakeRate histograms were saved."


    #============================================================================
    #=======================make ZX histos=======================================
    #============================================================================
    def MakeHistogramsZX(self,FRfile,datafile,qqZZfile):
        OSMethod.GetZZ3P1F(self,qqZZfile,FRfile)
        FakeRate= FR.FakeRates(FRfile)
        file  = TFile(datafile)
        if(file):
            print"[INFO] get datafile to produce ZX"
        tree = file.Get("passedEvents")

        for ievent,event in enumerate(tree):
            #if(ievent==100):break
            self.passedOSCRselection = False
            OSMethod.foundOSCRCandidate(self,event)
            if(not self.passedOSCRselection): continue
            #f3 = FakeRate.GetFakeRate(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lep_id[self.lep_CRindex[2]])
            #f4 = FakeRate.GetFakeRate(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lep_id[self.lep_CRindex[3]])
            f3 = FakeRate.GetFakeRate(event.lep_pt[self.lep_CRindex[2]],event.lep_eta[self.lep_CRindex[2]],event.lep_id[self.lep_CRindex[2]])
            f4 = FakeRate.GetFakeRate(event.lep_pt[self.lep_CRindex[3]],event.lep_eta[self.lep_CRindex[3]],event.lep_id[self.lep_CRindex[3]])
            weight_2P2F_SR = (f3/(1-f3))*(f4/(1-f4))
            weight_3P1F_bkg = (f3/(1-f3))+(f4/(1-f4))

            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l3 = TLorentzVector()
            l4 = TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[0]],event.lepFSR_eta[self.lep_CRindex[0]],event.lepFSR_phi[self.lep_CRindex[0]],event.lepFSR_mass[self.lep_CRindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[1]],event.lepFSR_eta[self.lep_CRindex[1]],event.lepFSR_phi[self.lep_CRindex[1]],event.lepFSR_mass[self.lep_CRindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lepFSR_phi[self.lep_CRindex[2]],event.lepFSR_mass[self.lep_CRindex[2]])
            l4.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lepFSR_phi[self.lep_CRindex[3]],event.lepFSR_mass[self.lep_CRindex[3]])
            mass4l = (l1+l2+l3+l4).M()

            #check number of failing
            nZXCRFailedLeptons = 0
            for i in range(0,4):
                if(not (event.lep_tightId[self.lep_CRindex[i]] and event.lep_RelIsoNoFSR[self.lep_CRindex[i]]<0.35)):
                    nZXCRFailedLeptons+=1

            #find which lep failed in 3P1F case
            if(not (event.lep_tightId[self.lep_CRindex[2]] and event.lep_RelIsoNoFSR[self.lep_CRindex[2]]<0.35)):
                weight_3P1F_toSR = f3/(1-f3)
            if(not (event.lep_tightId[self.lep_CRindex[3]] and event.lep_RelIsoNoFSR[self.lep_CRindex[3]]<0.35)):
                weight_3P1F_toSR = f4/(1-f4)

            #fill histos
            if(nZXCRFailedLeptons==1):
                self.HFromCRHisto['3P1F']['inclusive'].Fill(mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.HFromCRHisto['3P1F']['4e'].Fill(mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.HFromCRHisto['3P1F']['4mu'].Fill(mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==11 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.HFromCRHisto['3P1F']['2e2mu'].Fill(mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==13 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.HFromCRHisto['3P1F']['2mu2e'].Fill(mass4l,weight_3P1F_toSR)
            if(nZXCRFailedLeptons==2):
                self.HFromCRHisto['2P2F_SR']['inclusive'].Fill(mass4l,weight_2P2F_SR)
                self.HFromCRHisto['3P1F_bkg']['inclusive'].Fill(mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.HFromCRHisto['2P2F_SR']['4e'].Fill(mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['4e'].Fill(mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.HFromCRHisto['2P2F_SR']['4mu'].Fill(mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['4mu'].Fill(mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==11 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.HFromCRHisto['2P2F_SR']['2e2mu'].Fill(mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['2e2mu'].Fill(mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==13 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.HFromCRHisto['2P2F_SR']['2mu2e'].Fill(mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['2mu2e'].Fill(mass4l,weight_3P1F_bkg*weight_3P1F_toSR)

        #Remove 3P1F_SR Negative bins
        #for cat_name in self.cat_CRtoSRnames:
        #    for cat_CRname in self.cat_CRnames:
        #        OSMethod.RemoveNegativeBins1D(self,self.HFromCRHisto[cat_name][cat_CRname])

        #fill ZX histos
        for cat_name in self.cat_CRnames:
            self.ZXHistos[cat_name]['data'].Add(self.ZXHistos[cat_name]['qqZZ'],-1)
            self.ZXHistos[cat_name]['data'].Add(self.HFromCRHisto['3P1F'][cat_name],1)
            self.ZXHistos[cat_name]['data'].Add(self.HFromCRHisto['3P1F_bkg'][cat_name],-1)
            #difference N_3P1F-N_3P1F_bkg-N_3P1F_qqZZ may be Negative.
            OSMethod.RemoveNegativeBins1D(self,self.ZXHistos[cat_name]['data'])
            self.ZXHistos[cat_name]['data'].Add(self.HFromCRHisto['2P2F_SR'][cat_name],1)

        #count events for each channel
        OSMethod.CountEvents(self)

    def MakeHistogramsZX_test(self,FRfile,datafile,qqZZfile):
        OSMethod.GetZZ3P1F(self,qqZZfile,FRfile)
        FakeRate= FR.FakeRates(FRfile)
        file  = TFile(datafile)
        if(file):
            print"[INFO] get datafile to produce ZX"
        tree = file.Get("passedEvents")

        for ievent,event in enumerate(tree):
            #if(ievent==100):break
            if(not event.passedZXCRSelection): continue
            f3 = FakeRate.GetFakeRate(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lep_id[event.lep_Hindex[2]])
            f4 = FakeRate.GetFakeRate(event.lepFSR_pt[event.lep_Hindex[3]],event.lepFSR_eta[event.lep_Hindex[3]],event.lep_id[event.lep_Hindex[3]])
            weight_2P2F_SR = (f3/(1-f3))*(f4/(1-f4))
            weight_3P1F_bkg = (f3/(1-f3))+(f4/(1-f4))

            #l1 = TLorentzVector()
            #l2 = TLorentzVector()
            #l3 = TLorentzVector()
            #l4 = TLorentzVector()
            #l1.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
            #l2.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
            #l3.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[2]])
            #l4.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[3]],event.lepFSR_eta[event.lep_Hindex[3]],event.lepFSR_phi[event.lep_Hindex[3]],event.lepFSR_mass[event.lep_Hindex[3]])
            #mass4l = (l1+l2+l3+l4).M()

            #find which lep failed in 3P1F case
            if(not (event.lep_tightId[event.lep_Hindex[2]] and event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35)):
                weight_3P1F_toSR = f3/(1-f3)
            if(not (event.lep_tightId[event.lep_Hindex[3]] and event.lep_RelIsoNoFSR[event.lep_Hindex[3]]<0.35)):
                weight_3P1F_toSR = f4/(1-f4)

            #fill histos
            if(event.nZXCRFailedLeptons==1):
                self.HFromCRHisto['3P1F']['inclusive'].Fill(event.mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.HFromCRHisto['3P1F']['4e'].Fill(event.mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.HFromCRHisto['3P1F']['4mu'].Fill(event.mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==11 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.HFromCRHisto['3P1F']['2e2mu'].Fill(event.mass4l,weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==13 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.HFromCRHisto['3P1F']['2mu2e'].Fill(event.mass4l,weight_3P1F_toSR)
            if(event.nZXCRFailedLeptons==2):
                self.HFromCRHisto['2P2F_SR']['inclusive'].Fill(event.mass4l,weight_2P2F_SR)
                self.HFromCRHisto['3P1F_bkg']['inclusive'].Fill(event.mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.HFromCRHisto['2P2F_SR']['4e'].Fill(event.mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['4e'].Fill(event.mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.HFromCRHisto['2P2F_SR']['4mu'].Fill(event.mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['4mu'].Fill(event.mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==11 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==13):
                    self.HFromCRHisto['2P2F_SR']['2e2mu'].Fill(event.mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['2e2mu'].Fill(event.mass4l,weight_3P1F_bkg*weight_3P1F_toSR)
                if(abs(event.lep_id[event.lep_Hindex[0]])==abs(event.lep_id[event.lep_Hindex[1]])==13 and abs(event.lep_id[event.lep_Hindex[2]])==abs(event.lep_id[event.lep_Hindex[3]])==11):
                    self.HFromCRHisto['2P2F_SR']['2mu2e'].Fill(event.mass4l,weight_2P2F_SR)
                    self.HFromCRHisto['3P1F_bkg']['2mu2e'].Fill(event.mass4l,weight_3P1F_bkg*weight_3P1F_toSR)

        #Remove 3P1F_SR Negative bins
        #for cat_name in self.cat_CRtoSRnames:
        #    for cat_CRname in self.cat_CRnames:
        #        OSMethod.RemoveNegativeBins1D(self,self.HFromCRHisto[cat_name][cat_CRname])

        #fill ZX histos
        for cat_name in self.cat_CRnames:
            self.ZXHistos[cat_name]['data'].Add(self.ZXHistos[cat_name]['qqZZ'],-1)
            self.ZXHistos[cat_name]['data'].Add(self.HFromCRHisto['3P1F'][cat_name],1)
            self.ZXHistos[cat_name]['data'].Add(self.HFromCRHisto['3P1F_bkg'][cat_name],-1)
            #difference N_3P1F-N_3P1F_bkg-N_3P1F_qqZZ may be Negative.
            OSMethod.RemoveNegativeBins1D(self,self.ZXHistos[cat_name]['data'])
            self.ZXHistos[cat_name]['data'].Add(self.HFromCRHisto['2P2F_SR'][cat_name],1)

        #count events for each channel
        OSMethod.CountEvents(self)





    #===========================================================================
    #===================Add weighted ZZ 3P1F distrbution to ZX=================
    #===========================================================================
    def GetZZ3P1F(self,qqZZfile,FRfile):
        FakeRate = FR.FakeRates(FRfile)
        file  = TFile(qqZZfile)
        if(file):
            print "[INFO] get qqZZ file to produce weighted ZZ 3P1F distrbution for ZX"
        tree = file.Ana.Get("passedEvents")
        sumWeights = file.Ana.Get("sumWeights").GetBinContent(1)

        for ievent,event in enumerate(tree):
            #if(ievent==100):break
            self.passedOSCRselection = False
            OSMethod.foundOSCRCandidate(self,event)
            if(not self.passedOSCRselection): continue

            weight= self.lumi*1000*1.256*event.k_qqZZ_ewk*event.k_qqZZ_qcd_M*event.eventWeight/sumWeights
            f3 = FakeRate.GetFakeRate(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lep_id[self.lep_CRindex[2]])
            f4 = FakeRate.GetFakeRate(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lep_id[self.lep_CRindex[3]])

            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l3 = TLorentzVector()
            l4 = TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[0]],event.lepFSR_eta[self.lep_CRindex[0]],event.lepFSR_phi[self.lep_CRindex[0]],event.lepFSR_mass[self.lep_CRindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[1]],event.lepFSR_eta[self.lep_CRindex[1]],event.lepFSR_phi[self.lep_CRindex[1]],event.lepFSR_mass[self.lep_CRindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lepFSR_phi[self.lep_CRindex[2]],event.lepFSR_mass[self.lep_CRindex[2]])
            l4.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lepFSR_phi[self.lep_CRindex[3]],event.lepFSR_mass[self.lep_CRindex[3]])
            mass4l = (l1+l2+l3+l4).M()

            #check number of failing
            nZXCRFailedLeptons = 0
            for i in range(0,4):
                if(not (event.lep_tightId[self.lep_CRindex[i]] and event.lep_RelIsoNoFSR[self.lep_CRindex[i]]<0.35)):
                    nZXCRFailedLeptons+=1

            #find which lep failed
            if(not (event.lep_tightId[self.lep_CRindex[2]] and event.lep_RelIsoNoFSR[self.lep_CRindex[2]]<0.35)):
                weight_3P1F_toSR = f3/(1-f3)
            if(not (event.lep_tightId[self.lep_CRindex[3]] and event.lep_RelIsoNoFSR[self.lep_CRindex[3]]<0.35)):
                weight_3P1F_toSR = f4/(1-f4)

            #fill histos
            if(nZXCRFailedLeptons==1):
                self.ZXHistos['inclusive']['qqZZ'].Fill(mass4l,weight*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.ZXHistos['4e']['qqZZ'].Fill(mass4l,weight*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.ZXHistos['4mu']['qqZZ'].Fill(mass4l,weight*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==11 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                    self.ZXHistos['2e2mu']['qqZZ'].Fill(mass4l,weight*weight_3P1F_toSR)
                if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==13 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                    self.ZXHistos['2mu2e']['qqZZ'].Fill(mass4l,weight*weight_3P1F_toSR)

        print "[INFO] weighted qqZZ 3P1F has been stored in ZX histos"



    #===========================================================================
    #==================Remove Negative Bins for TH1D============================
    #===========================================================================
    def RemoveNegativeBins1D(self,histo):
        for i_bin_x in range(1,histo.GetXaxis().GetNbins()):
            if(histo.GetBinContent(i_bin_x)<0):
                histo.SetBinContent(i_bin_x,0.0)



    #============================================================================
    #=======================count events from Histos=============================
    #============================================================================
    def CountEvents(self):
        ninclusive = self.ZXHistos['inclusive']['data'].Integral()
        n4e = self.ZXHistos['4e']['data'].Integral()
        n4mu = self.ZXHistos['4mu']['data'].Integral()
        n2e2mu = self.ZXHistos['2e2mu']['data'].Integral()
        n2mu2e = self.ZXHistos['2mu2e']['data'].Integral()
        print "[INFO] MassWindow number of inclusive ZX backgrounds estimation = "+str(ninclusive)
        print "[INFO] MassWindow number of 4e channel ZX backgrounds estimation = "+str(n4e)
        print "[INFO] MassWindow number of 4mu channel ZX backgrounds estimation = "+str(n4mu)
        print "[INFO] MassWindow number of 2e2mu channel ZX backgrounds estimation = "+str(n2e2mu)
        print "[INFO] MassWindow number of 4mu2e channel ZX backgrounds estimation = "+str(n2mu2e)

    #===========================================================================
    #===============Save raw ZX histo===========================================
    #===========================================================================
    def SaveZXHistos(self):
        outfilename = "../RawHistos/ZXHistos_OS_%s_Legacy.root"%str(self.year)
        outfile = TFile(outfilename,"recreate")
        for cat_name in self.cat_CRtoSRnames:
            for cat_CRname in self.cat_CRnames:
                self.HFromCRHisto[cat_name][cat_CRname].Write()
        for cat_name in self.cat_CRnames:
            self.ZXHistos[cat_name]['data'].Write()
            self.ZXHistos[cat_name]['qqZZ'].Write()





    #============================================================================
    #=======================Save plots===========================================
    #============================================================================
    def SavePlots(self,c,name):
        c.SaveAs(name+".png")
