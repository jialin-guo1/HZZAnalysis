from ROOT import *
from deltaR import *
import math
from array import array
import FakeRates as FR

class SSMethod:
    def __init__(self):
        self.cat_states=['corrected','uncorrected']
        self.cat_names=['EE','EB']
        self.var_names=['el','mu']
        self.nprocess=['data','WZ','Total']

        self.FR_SS_electron_EB_unc=TGraphErrors()
        self.FR_SS_electron_EE_unc=TGraphErrors()
        self.FR_SS_muon_EE_unc=TGraphErrors()
        self.FR_SS_muon_EE_unc=TGraphErrors()
        self.FR_SS_electron_EB=TGraphErrors()
        self.FR_SS_electron_EE=TGraphErrors()
        self.FR_SS_muon_EE=TGraphErrors()
        self.FR_SS_muon_EE=TGraphErrors()

        self.passing={}
        self.failing={}

        self.vector_X={}
        self.vector_Y={}
        self.vector_EX={} #errors
        self.vector_EY={}

        self.Constructor()

    #===========================================================================
    #==============initialize variables=========================================
    #===========================================================================
    def Constructor(self):
        for iprocess in self.nprocess:
            self.passing[iprocess]={}
            self.failing[iprocess]={}
            for var_name in self.var_names:
                self.passing[iprocess][var_name]=TH2D('pass'+iprocess+var_name,'pass'+iprocess+var_name,80, 0, 80, 2, 0, 2)
                self.failing[iprocess][var_name]=TH2D('failing'+iprocess+var_name,'failing'+iprocess+var_name,80, 0, 80, 2, 0, 2)

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



    #============================================================================
    #=====================Get Control Region samples=============================
    #============================================================================
    def foundSSCRCandidate(self,event,lep_index):
        passedSSCRselection = False
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
                # opposite sign and same flavour for Z ; same sign same flavour for fack leptons
                if(event.lep_id[i1]+event.lep_id[i2]!=0 or event.lep_id[j1]*event.lep_id[j2]<0 or abs(event.lep_id[j1])!=abs(event.lep_id[j2])): continue
                lep1 = TLorentzVector()
                lep2 = TLorentzVector()
                lep3 = TLorentzVector()
                lep4 = TLorentzVector()
                lep1.SetPtEtaPhiM(event.lepFSR_pt[i1],event.lepFSR_eta[i1],event.lepFSR_phi[i1],event.lepFSR_mass[i1])
                lep2.SetPtEtaPhiM(event.lepFSR_pt[i2],event.lepFSR_eta[i2],event.lepFSR_phi[i2],event.lepFSR_mass[i2])
                lep3.SetPtEtaPhiM(event.lepFSR_pt[j1],event.lepFSR_eta[j1],event.lepFSR_phi[j1],event.lepFSR_mass[j1])
                lep4.SetPtEtaPhiM(event.lepFSR_pt[j2],event.lepFSR_eta[j2],event.lepFSR_phi[j2],event.lepFSR_mass[j2])

                Z1 = TLorentzVector()
                SSleps = TLorentzVector()
                SSleps = lep3+lep4
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
                if(Z1.M()<40 or Z1.M()>120 or SSleps.M()<12 or SSleps.M()>120): continue
                #mass4l = (lep1+lep2+lep3+lep4).M()
                # if(mass4l<100): continue
                # Check if this candidate has the best Z1 and highest scalar sum of Z2 lepton pt
                if(Z1DeltaM<minZ1DeltaM):
                    minZ1DeltaM = Z1DeltaM
                    massZ1 = Z1.M()
                    lep_index[0] = Z1_lepindex[0]
                    lep_index[1] = Z1_lepindex[1]
                    lep_index[2] = j1
                    lep_index[3] = j2
                    passedSSCRselection = True


        return passedSSCRselection


    #===========================================================================
    #================Fill passing/failling histos===============================
    #===========================================================================
    def FillFRHistos(self,file,process):
        inputfile = TFile(file)
        inputTree = inputfile.Get("passedEvents")
        #self.passing[process]={}
        #self.failing[process]={}
        #for var_name in self.var_names:
        #    self.passing[process][var_name]=TH2D('pass'+process+var_name,'pass'+process+var_name,80, 0, 80, 2, 0, 2)
        #    self.failing[process][var_name]=TH2D('failing'+process+var_name,'failing'+process+var_name,80, 0, 80, 2, 0, 2)

        #loop events and save passing and failing hitos
        for ievent,event in enumerate(inputTree):
            #if(ievent==100): break
            if(not event.passedZ1LSelection): continue
            if(process=='WZ'):
                weight = 59.7*1000*4.67*event.eventWeight/32584720.0
            else:
                weight = 1
            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l3 = TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[2]])
            Z1 = TLorentzVector()
            Z1 = l1+l2
            if(Z1.M()<40 or Z1.M()>120):continue
            if(event.lepFSR_pt[event.lep_Hindex[0]]<20 or event.lepFSR_pt[event.lep_Hindex[1]]<10): continue
            if(event.met>25.0):continue
            if(event.lep_Sip[event.lep_Hindex[2]]>4.0): continue
            if(event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35):
                if(abs(event.lep_id[event.lep_Hindex[2]])==11):
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        self.passing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)  #0.5 for EB 1.5 for EE
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        self.passing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
                if(abs(event.lep_id[event.lep_Hindex[2]])==13):
                    if(abs(event.lep_eta[event.lep_Hindex[2]])<1.2):
                        self.passing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    if(abs(event.lep_eta[event.lep_Hindex[2]])>=1.2):
                        self.passing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
                    #if(event.lep_isEE[event.lep_Hindex[2]]):
                    #    self.passing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    #if(event.lep_isEB[event.lep_Hindex[2]]):
                    #    self.passing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
            else:
                if(abs(event.lep_id[event.lep_Hindex[2]])==11):
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        self.failing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        self.failing[process]['el'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
                if(abs(event.lep_id[event.lep_Hindex[2]])==13):
                    if(abs(event.lep_eta[event.lep_Hindex[2]])<1.2):
                        self.failing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    if(abs(event.lep_eta[event.lep_Hindex[2]])>=1.2):
                        self.failing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)
                    #if(event.lep_isEE[event.lep_Hindex[2]]):
                    #    self.failing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],0.5,weight)
                    #if(event.lep_isEB[event.lep_Hindex[2]]):
                    #    self.failing[process]['mu'].Fill(event.lep_pt[event.lep_Hindex[2]],1.5,weight)



    #===========================================================================
    #=================Save Raw passing and failing histos=======================
    #===========================================================================
    def SaveFRHistos(self,year,subtractWZ,remove_negative_bins):
        outfilename="../RawHistos/FRHistos_SS_%s_Legacy.root"%year
        outfile = TFile(outfilename,"recreate")
        outfile.cd()
        #self.passing['Total']={}
        #self.failing['Total']={}
        for var_name in self.var_names:
            #self.passing['Total'][var_name]=TH2D('pass'+'Total'+var_name,'pass'+'Total'+var_name,80, 0, 80, 2, 0, 2)
            #self.failing['Total'][var_name]=TH2D('failing'+'Total'+var_name,'failing'+'Total'+var_name,80, 0, 80, 2, 0, 2)
            self.passing['Total'][var_name].Add(self.passing['data'][var_name],1.)
            self.failing['Total'][var_name].Add(self.failing['data'][var_name],1.)

        # Subtract WZ contribution from MC estimate
        if(subtractWZ):
            SSMethod.subtractWZ(self)

        if(remove_negative_bins):
            for var_name in self.var_names:
                SSMethod.RemoveNegativeBins2D(self,self.passing['Total'][var_name])
                SSMethod.RemoveNegativeBins2D(self,self.passing['Total'][var_name])
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
        self.passing['Total']['mu'].Add(self.passing['WZ']['mu'],-1.)
        self.failing['Total']['mu'].Add(self.failing['WZ']['mu'],-1.)
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
    def GetFRHistos(self,year):
        filename="../RawHistos/FRHistos_SS_%s_Legacy.root"%year
        inputfile = TFile.Open(filename)
        if(inputfile):
            print "[INFO] successfully handle file FRHistos_SS_%s_Legacy.root"%year
        #for var_name in self.var_names:
        #    for iprocess in self.nprocess:
        #        self.passing[iprocess][var_name]=inputfile.Get('pass'+iprocess+var_name)
        #        self.failing[iprocess][var_name]=inputfile.Get('failing'+iprocess+var_name)

        for iprocess in self.nprocess:
            self.passing[iprocess]={}
            self.failing[iprocess]={}
            for var_name in self.var_names:
                self.passing[iprocess][var_name]=inputfile.Get('pass'+iprocess+var_name)
                self.failing[iprocess][var_name]=inputfile.Get('failing'+iprocess+var_name)
                print "[INFO] get histos="+iprocess+var_name

        print "enter produce FR function"

        print "[INFO] All FakeRate histograms retrieved from file."


    #============================================================================
    #==================prodece FakeRate from data================================
    #============================================================================
    def SSFRproduce(self,year,process):

        filename="../RawHistos/FRHistos_SS_%s_Legacy.root"%year
        inputfile = TFile(filename)
        if(inputfile):
            print "[INFO] successfully handle file FRHistos_SS_%s_Legacy.root"%year
        #for var_name in self.var_names:
        #    for iprocess in self.nprocess:
        #        self.passing[iprocess][var_name]=inputfile.Get('pass'+iprocess+var_name)
        #        self.failing[iprocess][var_name]=inputfile.Get('failing'+iprocess+var_name)

        for iprocess in self.nprocess:
            self.passing[iprocess]={}
            self.failing[iprocess]={}
            for var_name in self.var_names:
                self.passing[iprocess][var_name]=inputfile.Get('pass'+iprocess+var_name)
                self.failing[iprocess][var_name]=inputfile.Get('failing'+iprocess+var_name)
                print "[INFO] get histos="+iprocess+var_name

        print "enter produce FR function"

        print "[INFO] All FakeRate histograms retrieved from file."
        c=TCanvas()
        self.passing['Total']['mu'].Draw()
        c.SaveAs("SStest_total.png")
        outfilename="../RawHistos/FakeRates_SS_%s_Legacy.root"%year
        #initialize x and y axis for FakeRate
        #for cat_state in self.cat_states:
        #    self.vector_X[cat_state]={}
        #    self.vector_Y[cat_state]={}
        #    self.vector_EX[cat_state]={}
        #    self.vector_EY[cat_state]={}
        #    for cat_name in self.cat_names:
        #        self.vector_X[cat_state][cat_name]={}
        #        self.vector_Y[cat_state][cat_name]={}
        #        self.vector_EX[cat_state][cat_name]={}
        #        self.vector_EY[cat_state][cat_name]={}
        #        for var_name in self.var_names:
        #            self.vector_X[cat_state][cat_name][var_name]=[]
        #            self.vector_Y[cat_state][cat_name][var_name]=[]
        #            self.vector_EY[cat_state][cat_name][var_name]=[]

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

                tempNPaxis = self.passing['Total'][var_name].GetXaxis()
                tempNFaxis = self.failing['Total'][var_name].GetXaxis()

                print "pt_bins[i_pt_bin] = "+ str(pt_bins[i_pt_bin])
                print "pt_bins[i_pt_bin]+1 = "+str(pt_bins[i_pt_bin+1])
                print "bin number of pt_bins[i_pt_bin] = "+ str(tempNPaxis.FindBin(pt_bins[i_pt_bin]))
                print "bin number of pt_bins[i_pt_bin+1]-1 = "+str(tempNPaxis.FindBin(pt_bins[i_pt_bin+1])-1)

                temp_NP = self.passing['Total'][var_name].IntegralAndError(tempNPaxis.FindBin(pt_bins[i_pt_bin]),tempNPaxis.FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NP))
                temp_NF = self.failing['Total'][var_name].IntegralAndError(tempNPaxis.FindBin(pt_bins[i_pt_bin]),tempNPaxis.FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NF))

                #temp_NP = self.passing['Total'][var_name].IntegralAndError(self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, temp_error_NP)
                #temp_NF = self.failing['Total'][var_name].IntegralAndError(self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, temp_error_NF)

                self.vector_X['corrected']['EB'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['corrected']['EB'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['corrected']['EB'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['corrected']['EB'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

                temp_NP = self.passing['Total'][var_name].IntegralAndError(self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NP))
                temp_NF = self.failing['Total'][var_name].IntegralAndError(self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NF))

                self.vector_X['corrected']['EE'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['corrected']['EE'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['corrected']['EE'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['corrected']['EE'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*pow(temp_error_NF,2)))

                #Just for fake rate plots calculate the same for histograms without WZ subtraction
                temp_NP = self.passing['data'][var_name].IntegralAndError(self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NP))
                temp_NF = self.failing['data'][var_name].IntegralAndError(self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NF))

                self.vector_X['uncorrected']['EB'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['uncorrected']['EB'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['uncorrected']['EB'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['uncorrected']['EB'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

                temp_NP = self.passing['data'][var_name].IntegralAndError(self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NP))
                temp_NF = self.failing['data'][var_name].IntegralAndError(self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NF))

                self.vector_X['uncorrected']['EE'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['uncorrected']['EE'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['uncorrected']['EE'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['uncorrected']['EE'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

        print " check type "
        print "vector_X['uncorrected']['EB']['el'][0]  = " +str(self.vector_X['uncorrected']['EB']['el'][0])



        self.FR_SS_electron_EB_unc = TGraphErrors (len(self.vector_X['uncorrected']['EB']['el']),
											  self.vector_X['uncorrected']['EB']['el'],
											  self.vector_Y['uncorrected']['EB']['el'],
											  self.vector_EX['uncorrected']['EB']['el'],
											  self.vector_EY['uncorrected']['EB']['el'])
        self.FR_SS_electron_EB_unc.SetName("FR_SS_electron_EB_unc")

        self.FR_SS_electron_EE_unc = TGraphErrors (len(self.vector_X['uncorrected']['EE']['el']),
											  self.vector_X['uncorrected']['EE']['el'],
											  self.vector_Y['uncorrected']['EE']['el'],
											  self.vector_EX['uncorrected']['EE']['el'],
											  self.vector_EY['uncorrected']['EE']['el'])
        self.FR_SS_electron_EE_unc.SetName("FR_SS_electron_EE_unc")

        self.FR_SS_muon_EE_unc = TGraphErrors (len(self.vector_X['uncorrected']['EE']['mu']),
										  self.vector_X['uncorrected']['EE']['mu'],
										  self.vector_Y['uncorrected']['EE']['mu'],
										  self.vector_EX['uncorrected']['EE']['mu'],
										  self.vector_EY['uncorrected']['EE']['mu'])
        self.FR_SS_muon_EE_unc.SetName("FR_SS_muon_EE_unc")

        self.FR_SS_muon_EB_unc = TGraphErrors (len(self.vector_X['uncorrected']['EB']['mu']),
										  self.vector_X['uncorrected']['EB']['mu'],
										  self.vector_Y['uncorrected']['EB']['mu'],
										  self.vector_EX['uncorrected']['EB']['mu'],
										  self.vector_EY['uncorrected']['EB']['mu'])
        self.FR_SS_muon_EB_unc.SetName("FR_SS_muon_EE_unc")

        self.FR_SS_muon_EE = TGraphErrors (len(self.vector_X['corrected']['EE']['mu']),
										  self.vector_X['corrected']['EE']['mu'],
										  self.vector_Y['corrected']['EE']['mu'],
										  self.vector_EX['corrected']['EE']['mu'],
										  self.vector_EY['corrected']['EE']['mu'])
        self.FR_SS_muon_EE.SetName("FR_SS_muon_EE")

        self.FR_SS_muon_EB = TGraphErrors (len(self.vector_X['corrected']['EB']['mu']),
										  self.vector_X['corrected']['EB']['mu'],
										  self.vector_Y['corrected']['EB']['mu'],
										  self.vector_EX['corrected']['EB']['mu'],
										  self.vector_EY['corrected']['EB']['mu'])
        self.FR_SS_muon_EB.SetName("FR_SS_muon_EE")

        # Electron fake rates must be corrected using average number of missing hits
        #CorrectElectronFakeRate(file)

        self.FR_SS_electron_EB = TGraphErrors (len(self.vector_X['corrected']['EB']['el']),
											  self.vector_X['corrected']['EB']['el'],
											  self.vector_Y['corrected']['EB']['el'],
											  self.vector_EX['corrected']['EB']['el'],
											  self.vector_EY['corrected']['EB']['el'])
        self.FR_SS_electron_EB_unc.SetName("FR_SS_electron_EB_unc")

        self.FR_SS_electron_EE_unc = TGraphErrors (len(self.vector_X['uncorrected']['EE']['el']),
											  self.vector_X['uncorrected']['EE']['el'],
											  self.vector_Y['uncorrected']['EE']['el'],
											  self.vector_EX['uncorrected']['EE']['el'],
											  self.vector_EY['uncorrected']['EE']['el'])
        self.FR_SS_electron_EE_unc.SetName("FR_SS_electron_EE_unc")

        self.FR_SS_muon_EE_unc = TGraphErrors (len(self.vector_X['uncorrected']['EE']['mu']),
										  self.vector_X['uncorrected']['EE']['mu'],
										  self.vector_Y['uncorrected']['EE']['mu'],
										  self.vector_EX['uncorrected']['EE']['mu'],
										  self.vector_EY['uncorrected']['EE']['mu'])
        self.FR_SS_muon_EE_unc.SetName("FR_SS_muon_EE_unc")



        SSMethod.plotFR(self)
        SSMethod.SaveFRGragh(self,outfilename)

        #OutFRFile=TFile(outfilename,"RECREATE")
        #OutFRFile.cd()
        #self.FR_SS_electron_EB_unc.Write()
        #self.FR_SS_electron_EE_unc.Write()
        #self.FR_SS_muon_EE_unc.Write()
        #self.FR_SS_muon_EB_unc.Write()
        #self.FR_SS_electron_EB.Write()
        #self.FR_SS_electron_EE.Write()
        #self.FR_SS_muon_EE.Write()
        #self.FR_SS_muon_EB.Write()
        #OutFRFile.Close()

        #print "[INFO] All FakeRate histograms were saved."


    #===========================================================================
    #===================save raw FakeRates Gragh================================
    #===========================================================================
    def SaveFRGragh(self,outfilename):
        OutFRFile=TFile(outfilename,"RECREATE")
        OutFRFile.cd()
        print " type of Gragh = "+str(type(self.FR_SS_electron_EB_unc))
        self.FR_SS_electron_EB_unc.Write()
        self.FR_SS_electron_EE_unc.Write()
        self.FR_SS_muon_EE_unc.Write()
        self.FR_SS_muon_EB_unc.Write()
        self.FR_SS_electron_EB.Write()
        self.FR_SS_electron_EE.Write()
        self.FR_SS_muon_EE.Write()
        self.FR_SS_muon_EB.Write()
        OutFRFile.Close()

        print "[INFO] All FakeRate histograms were saved."

    #============================================================================
    #==================corrected electron FakeRate===============================
    #============================================================================
    #def CorrectElectronFakeRate(self,file):




    #============================================================================
    #==================Draw FR plots=============================================
    #============================================================================
    def plotFR(self):
        c_ele=TCanvas("FR_ele", "FR_ele", 600,600)
        c_muon=TCanvas("FR_muon","FRmuon",600,600)
        mg_electrons=TMultiGraph()
        mg_muons=TMultiGraph()

        mg_electrons.Add(self.FR_SS_electron_EB_unc)
        self.FR_SS_electron_EB_unc.SetLineColor(kBlue)
        self.FR_SS_electron_EB_unc.SetLineStyle(1)
        self.FR_SS_electron_EB_unc.SetMarkerSize(0)
        self.FR_SS_electron_EB_unc.SetTitle("barel uncorrected")
        mg_electrons.Add(self.FR_SS_electron_EE_unc)
        self.FR_SS_electron_EE_unc.SetLineColor(kRed);
        self.FR_SS_electron_EE_unc.SetLineStyle(1);
        self.FR_SS_electron_EE_unc.SetMarkerSize(0);
        self.FR_SS_electron_EE_unc.SetTitle("endcap uncorrected")

        mg_electrons.Add(self.FR_SS_electron_EB)
        self.FR_SS_electron_EB.SetLineColor(kBlue)
        self.FR_SS_electron_EB.SetLineStyle(2)
        self.FR_SS_electron_EB.SetMarkerSize(0)
        self.FR_SS_electron_EB.SetTitle("barel corrected")
        mg_electrons.Add(self.FR_SS_electron_EE)
        self.FR_SS_electron_EE.SetLineColor(kRed);
        self.FR_SS_electron_EE.SetLineStyle(2);
        self.FR_SS_electron_EE.SetMarkerSize(0);
        self.FR_SS_electron_EE.SetTitle("endcap corrected")

        mg_muons.Add(self.FR_SS_muon_EB_unc)
        self.FR_SS_muon_EB_unc.SetLineColor(kBlue)
        self.FR_SS_muon_EB_unc.SetLineStyle(1)
        self.FR_SS_muon_EB_unc.SetMarkerSize(0)
        self.FR_SS_muon_EB_unc.SetTitle("barel uncorrected")
        mg_muons.Add(self.FR_SS_muon_EE_unc)
        self.FR_SS_muon_EE_unc.SetLineColor(kRed)
        self.FR_SS_muon_EE_unc.SetLineStyle(1)
        self.FR_SS_muon_EE_unc.SetMarkerSize(0)
        self.FR_SS_muon_EE_unc.SetTitle("endcap uncorrected")

        mg_muons.Add(self.FR_SS_muon_EB)
        self.FR_SS_muon_EB.SetLineColor(kBlue)
        self.FR_SS_muon_EB.SetLineStyle(2)
        self.FR_SS_muon_EB.SetMarkerSize(0)
        self.FR_SS_muon_EB.SetTitle("barel corrected")
        mg_muons.Add(self.FR_SS_muon_EE)
        self.FR_SS_muon_EE.SetLineColor(kRed)
        self.FR_SS_muon_EE.SetLineStyle(2)
        self.FR_SS_muon_EE.SetMarkerSize(0)
        self.FR_SS_muon_EE.SetTitle("endcap corrected")

        gStyle.SetEndErrorSize(0)

        leg_ele = TLegend()
        leg_muon = TLegend()
        c_ele.cd()
        mg_electrons.Draw("AP");
	mg_electrons.GetXaxis().SetTitle("p_{T} [GeV]")
	mg_electrons.GetYaxis().SetTitle("Fake Rate")
	mg_electrons.SetTitle("Electron fake rate")
        mg_electrons.SetMaximum(0.35);
        leg_ele = SSMethod.CreateLegend_FR(self,"left",self.FR_SS_electron_EB_unc,self.FR_SS_electron_EE_unc,self.FR_SS_electron_EB,self.FR_SS_electron_EE)
        leg_ele.Draw()
        SSMethod.SavePlots(self,c_ele, "plot/FR_SS_electrons")

        c_muon.cd();
        mg_muons.Draw("AP");
	mg_muons.GetXaxis().SetTitle("p_{T} [GeV]");
	mg_muons.GetYaxis().SetTitle("Fake Rate");
	mg_muons.SetTitle("Muon fake rate");
        mg_muons.SetMaximum(0.35);
        leg_mu = SSMethod.CreateLegend_FR(self,"left",self.FR_SS_muon_EB_unc,self.FR_SS_muon_EE_unc,self.FR_SS_muon_EB,self.FR_SS_muon_EE);
        leg_mu.Draw();
        SSMethod.SavePlots(self,c_muon, "plot/FR_SS_muons");

    #=============================================================================
    #=============Create Legend for FakeRates=====================================
    #=============================================================================
    def CreateLegend_FR(self,position,EB_unc,EE_unc,EB_cor,EE_cor):
        if(position=='right'):
            leg = TLegend( .64, .65, .97, .9 )
        elif(position=='left'):
            leg=TLegend(.18,.65,.51,.9)
        else:
            print "[Error] Please enter \"left\" or \"right\" "
        leg.AddEntry( EB_unc, "barrel uncorrected", "l" )
        leg.AddEntry( EB_cor, "barrel corrected","l")
        leg.AddEntry( EE_unc, "endcap uncorrected", "l" )
        leg.AddEntry( EE_cor, "endcap corrected", "l" )
        return leg

    #============================================================================
    #=======================Save plots===========================================
    #============================================================================
    def SavePlots(self,c,name):
        c.SaveAs(name+".png")
