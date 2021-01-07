from ROOT import *
from deltaR import *

class SSMethod:
    def __init__(self):
        self.FR_SS_electron_EB_unc=TGraphErrors()
        self.FR_SS_electron_EE_unc=TGraphErrors()
        self.FR_SS_muon_EE_unc=TGraphErrors()
        self.FR_SS_muon_EE_unc=TGraphErrors()




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
                lifsr = ROOT.TLorentzVector()
                ljfsr = ROOT.TLorentzVector()
                lifsr.SetPtEtaPhiM(event.lepFSR_pt[i], event.lepFSR_eta[i], event.lepFSR_phi[i], event.lepFSR_mass[i])
                ljfsr.SetPtEtaPhiM(event.lepFSR_pt[j], event.lepFSR_eta[j], event.lepFSR_phi[j], event.lepFSR_mass[j])
                Z = ROOT.TLorentzVector()
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
                lep1 = ROOT.TLorentzVector()
                lep2 = ROOT.TLorentzVector()
                lep3 = ROOT.TLorentzVector()
                lep4 = ROOT.TLorentzVector()
                lep1.SetPtEtaPhiM(event.lepFSR_pt[i1],event.lepFSR_eta[i1],event.lepFSR_phi[i1],event.lepFSR_mass[i1])
                lep2.SetPtEtaPhiM(event.lepFSR_pt[i2],event.lepFSR_eta[i2],event.lepFSR_phi[i2],event.lepFSR_mass[i2])
                lep3.SetPtEtaPhiM(event.lepFSR_pt[j1],event.lepFSR_eta[j1],event.lepFSR_phi[j1],event.lepFSR_mass[j1])
                lep4.SetPtEtaPhiM(event.lepFSR_pt[j2],event.lepFSR_eta[j2],event.lepFSR_phi[j2],event.lepFSR_mass[j2])

                Z1 = ROOT.TLorentzVector()
                SSleps = ROOT.TLorentzVector()
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
                lep1_noFSR = ROOT.TLorentzVector()
                lep2_noFSR = ROOT.TLorentzVector()
                lep3_noFSR = ROOT.TLorentzVector()
                lep4_noFSR = ROOT.TLorentzVector()
                lep1_noFSR.SetPtEtaPhiM(event.lep_pt[i1],event.lep_eta[i1],event.lep_phi[i1],event.lep_mass[i1])
                lep2_noFSR.SetPtEtaPhiM(event.lep_pt[i2],event.lep_eta[i2],event.lep_phi[i2],event.lep_mass[i2])
                lep3_noFSR.SetPtEtaPhiM(event.lep_pt[j1],event.lep_eta[j1],event.lep_phi[j1],event.lep_mass[j1])
                lep4_noFSR.SetPtEtaPhiM(event.lep_pt[j2],event.lep_eta[j2],event.lep_phi[j2],event.lep_mass[j2])
                i1i2 = ROOT.TLorentzVector()
                i1i2 = lep1_noFSR+lep2_noFSR
                allM.append(i1i2.M())
                if(event.lep_id[i1]*event.lep_id[j1]<0):
                    i1j1 = ROOT.TLorentzVector()
                    i1j2 = ROOT.TLorentzVector()
                    i1j2 = lep1_noFSR+lep4_noFSR
                    i1j1 = lep1_noFSR+lep3_noFSR
                    allM.append(i1j1.M())
                    allM.append(i1j2.M())
                else:
                    i2j1 = ROOT.TLorentzVector()
                    i2j2 = ROOT.TLorentzVector()
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

    #============================================================================
    #==================prodece FakeRate from data================================
    #============================================================================
    def SSFRproduce(self,file,year):
        outfilename="../RawHistos/FakeRates_SS_%s_Legacy.root"%year
        inputfile = TFile(file)
        inputTree = TFile.Get("passedEvents")
        cat_names=['EE','EB']
        var_names=['electron','muon']
        passing={}
        failing={}
        vector_X={}
        vector_Y={}
        vector_EX={}  #errors
        vector_EY={}
        for cat_name in cat_names:
            for var_name in var_names:
                passing[cat_name][var_name]=TH2D('pass'+cat_name+var_name,'pass'+cat_name+var_name,80, 0, 80, 2, 0, 2)
                failing[cat_name][var_name]=TH2D('fail'+cat_name+var_name,'fail'+cat_name+var_name,80, 0, 80, 2, 0, 2)
                vector_X[cat_name][var_name]=[]
                vector_Y[cat_name][var_name]=[]
                vector_EX[cat_name][var_name]=[]
                vector_EY[cat_name][var_name]=[]

        #loop events and save passing and failing hitos
        for ievent,event in enumerate(inputTree):
            if(not event.passedZ1LSelection): continue
            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l3 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[2]])
            Z1 = ROOT.TLorentzVector()
            Z1 = l1+l2
            if(Z1.M()<40 or Z1.M()>120):continue
            if(event.lepFSR_pt[event.lep_Hindex[0]]<20 or event.lepFSR_pt[event.lep_Hindex[1]]<10): continue
            if(event.met>25.0):continue
            if(event.lep_Sip[event.lep_Hindex[2]]>4.0): continue
            if(event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35):
                if(abs(event.lep_id[event.lep_Hindex[2]])==11):
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        passing['EE']['electron'].Fill(event.lep_pt[lep_Hindex[2]],0.5)
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        passing['EB']['electron'].Fill(event.lep_pt[lep_Hindex[2]],1.5)
                if(abs(event.lep_id[event.lep_Hindex[2]])==13):
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        passing['EE']['muon'].Fill(event.lep_pt[lep_Hindex[2]],0.5)
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        passing['EE']['muon'].Fill(event.lep_pt[lep_Hindex[2]],1.5)
            else:
                if(abs(event.lep_id[event.lep_Hindex[2]])==11):
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        failing['EE']['electron'].Fill(event.lep_pt[lep_Hindex[2]],0.5)
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        failing['EB']['electron'].Fill(event.lep_pt[lep_Hindex[2]],1.5)
                if(abs(event.lep_id[event.lep_Hindex[2]])==13):
                    if(event.lep_isEE[event.lep_Hindex[2]]):
                        failing['EE']['muon'].Fill(event.lep_pt[lep_Hindex[2]],0.5)
                    if(event.lep_isEB[event.lep_Hindex[2]]):
                        failing['EB']['muon'].Fill(event.lep_pt[lep_Hindex[2]],1.5)
        #calculate FakeRates and save Gragh
        pt_bins=[5, 7, 10, 20, 30, 40, 50, 80]
        n_pt_bins=8
        for i_pt_bin in range(n_pt_bins-1):
            temp_NP = 0
            temp_NF = 0
            temp_error_x = 0
            temp_error_NP = 0
            temp_error_NF = 0
            for cat_name in cat_names:
                for var_name in var_names:
                    if(var_name=='el' and i_pt_bin==0): continue #electrons do not have 5 - 7 GeV bin
                    temp_NP = passing[cat_name][var_name].IntegralAndError(passing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),passing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, temp_error_NP)
                    temp_NF = failing[cat_name][var_name].IntegralAndError(failing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),failing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, temp_error_NF)

                    vector_X[cat_name][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                    vector_Y[cat_name][var_name].append(temp_NP/(temp_NP+temp_NF))
                    vector_EX[cat_name][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                    vector_EY[cat_name][var_name].append(sqrt(pow((temp_NF/pow(temp_NF+temp_NP,2)),2)*pow(temp_error_NP,2) + pow((temp_NP/pow(temp_NF+temp_NP,2)),2)*pow(temp_error_NF,2)))

                    temp_NP = passing[cat_name][var_name].IntegralAndError(passing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),passing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, temp_error_NP)
                    temp_NF = failing[cat_name][var_name].IntegralAndError(failing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),failing[cat_name][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, temp_error_NF)

                    vector_X[cat_name][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                    vector_Y[cat_name][var_name].append(temp_NP/(temp_NP+temp_NF))
                    vector_EX[cat_name][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                    vector_EY[cat_name][var_name].append(sqrt(pow((temp_NF/pow(temp_NF+temp_NP,2)),2)*pow(temp_error_NP,2) + pow((temp_NP/pow(temp_NF+temp_NP,2)),2)*pow(temp_error_NF,2)))


        self.FR_SS_electron_EB_unc = TGraphErrors (vector_X['EB']['electron'].size(),
											  vector_X['EB']['electron'][0],
											  vector_Y['EB']['electron'][0],
											  vector_EX['EB']['electron'][0],
											  vector_EY['EB']['electron'][0])
        self.FR_SS_electron_EB_unc.SetName("FR_SS_electron_EB_unc")

        self.FR_SS_electron_EE_unc = TGraphErrors (vector_X['EE']['electron'].size(),
											  vector_X['EE']['electron'][0],
											  vector_Y['EE']['electron'][0],
											  vector_EX['EE']['electron'][0],
											  vector_EY['EE']['electron'][0])
        self.FR_SS_electron_EE_unc.SetName("FR_SS_electron_EE_unc")

        self.FR_SS_muon_EE_unc = TGraphErrors (vector_X['EE']['muon'].size(),
										  vector_X['EE']['muon'][0],
										  vector_Y['EE']['muon'][0],
										  vector_EX['EE']['muon'][0],
										  vector_EY['EE']['muon'][0])
        self.FR_SS_muon_EE_unc.SetName("FR_SS_muon_EE_unc")

        self.FR_SS_muon_EB_unc = TGraphErrors (vector_X['EB']['muon'].size(),
										  vector_X['EB']['muon'][0],
										  vector_Y['EB']['muon'][0],
										  vector_EX['EB']['muon'][0],
										  vector_EY['EB']['muon'][0])
        self.FR_SS_muon_EB_unc.SetName("FR_SS_muon_EE_unc")

        FakeRates.plotFR(self)

        OutFRFile=TFile(outfilename,"RECREATE")
        OutFRFile.cd()
        FR_SS_electron_EB_unc.Write()
        FR_SS_electron_EE_unc.Write()
        FR_SS_muon_EE_unc.Write()
        FR_SS_muon_EB_unc.Write()
        OutFRFile.Close()

        print "[INFO] All FakeRate histograms were saved."



    #============================================================================
    #==================Draw FR plots=============================================
    #============================================================================
    def plotFR(self):
        c_ele=TCanvas("FR_ele", "FR_ele", 600, 600)
        c_muon=TCanvas("FR_muon","FRmuon",600,600)
        mg_electrons=TMultiGraph()
        mg_muons=TMultiGraph()

        mg_electrons.Add(FR_SS_electron_EB)
        self.FR_SS_electron_EB_unc.SetLineColor(kBlue)
        self.FR_SS_electron_EB_unc.SetLineStyle(1)
        self.FR_SS_electron_EB_unc.SetMarkerSize(0)
        self.FR_SS_electron_EB_unc.SetTitle("barel uncorrected")
        mg_electrons.Add(FR_SS_electron_EE_unc)
        self.FR_SS_electron_EE_unc.SetLineColor(kRed);
        self.FR_SS_electron_EE_unc.SetLineStyle(1);
        self.FR_SS_electron_EE_unc.SetMarkerSize(0);
        self.FR_SS_electron_EE_unc.SetTitle("endcap uncorrected");

        mg_muons.Add(FR_SS_muon_EB_unc)
        self.FR_SS_muon_EB_unc.SetLineColor(kBlue);
        self.FR_SS_muon_EB_unc.SetLineStyle(1);
        self.FR_SS_muon_EB_unc.SetMarkerSize(0);
        self.FR_SS_muon_EB_unc.SetTitle("barel uncorrected");
        mg_muons.Add(FR_SS_muon_EE_unc);
        self.FR_SS_muon_EE_unc.SetLineColor(kRed);
        self.FR_SS_muon_EE_unc.SetLineStyle(1);
        self.FR_SS_muon_EE_unc.SetMarkerSize(0);
        self.FR_SS_muon_EE_unc.SetTitle("endcap uncorrected");

        gStyle.SetEndErrorSize(0)

        leg_ele = TLegend()
        leg_muon = TLegend()
        c_ele.cd()
        mg_electrons.Draw("AP");
	    mg_electrons.GetXaxis().SetTitle("p_{T} [GeV]")
	    mg_electrons.GetYaxis().SetTitle("Fake Rate")
	    mg_electrons.SetTitle("Electron fake rate")
        mg_electrons.SetMaximum(0.35);
        leg_ele = CreateLegend_FR("left",FR_SS_electron_EB_unc,FR_SS_electron_EB,FR_SS_electron_EE_unc,FR_SS_electron_EE)
        leg_ele.Draw()
        SavePlots(c_ele, "Plots/FR_SS_electrons")

        c_mu.cd();
        mg_muons.Draw("AP");
	    mg_muons.GetXaxis().SetTitle("p_{T} [GeV]");
	    mg_muons.GetYaxis().SetTitle("Fake Rate");
	    mg_muons.SetTitle("Muon fake rate");
        mg_muons.SetMaximum(0.35);
        leg_mu = CreateLegend_FR("left",FR_SS_muon_EB_unc,FR_SS_muon_EB,FR_SS_muon_EE_unc,FR_SS_muon_EE);
        leg_mu.Draw();
        SavePlots(c_mu, "Plots/FR_SS_muons");

    #=============================================================================
    #=============Create Legend for FakeRates=====================================
    #=============================================================================
