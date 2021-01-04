from ROOT import *

class FakeRates():
    def __init__(self,filename):
        self.filename = filename
        self.input_file_FR = TFile(filename)
        self.g_FR_mu_EB = TGraph()
        self.g_FR_mu_EE = TGraph()
        self.g_FR_e_EB = TGraph()
        self.g_FR_e_EE = TGraph()
        self.FakeRates_Constructor()

    def FakeRates_Constructor(self):
        if(self.filename.find('OS')!=-1):
            self.g_FR_mu_EB = self.input_file_FR.Get("FR_OS_muon_EB")
            self.g_FR_mu_EE = self.input_file_FR.Get("FR_OS_muon_EE")
            self.g_FR_e_EB = self.input_file_FR.Get("FR_OS_electron_EB")
            self.g_FR_e_EE = self.input_file_FR.Get("FR_OS_electron_EE")
        if(self.filename.find('SS')!=-1):
            self.g_FR_mu_EB = self.input_file_FR.Get("FR_SS_muon_EB")
            self.g_FR_mu_EE = self.input_file_FR.Get("FR_SS_muon_EE")
            self.g_FR_e_EB = self.input_file_FR.Get("FR_SS_electron_EB")
            self.g_FR_e_EE = self.input_file_FR.Get("FR_SS_electron_EE")

    #==================Get FakeRate from existing file===========================
    def GetFakeRate(self,lep_pt,lep_eta,lep_id):
        if(lep_pt>=80):
            my_lep_Pt = 79.0
        else:
            my_lep_Pt = lep_pt
        my_lep_id = abs(lep_id)
        bin = 0
        if( my_lep_Pt > 5 and my_lep_Pt <= 7 ):
            bin = 0
        elif(my_lep_Pt >  7 and my_lep_Pt <= 10):
            bin = 1
        elif(my_lep_Pt > 10 and my_lep_Pt <= 20):
            bin = 2
        elif(my_lep_Pt > 20 and my_lep_Pt <= 30):
            bin = 3
        elif(my_lep_Pt > 30 and my_lep_Pt <= 40):
            bin = 4
        elif(my_lep_Pt > 40 and my_lep_Pt <= 50):
            bin = 5
        elif(my_lep_Pt > 50 and my_lep_Pt <= 80):
            bin = 6
        if(my_lep_id==11):
            bin = bin-1
            if(abs(lep_eta)<1.479):
                return self.g_FR_e_EB.GetY()[bin]
            else:
                return self.g_FR_e_EE.GetY()[bin]
        elif(my_lep_id==13):
            if(abs(lep_eta)<1.2):
                return self.g_FR_mu_EB.GetY()[bin]
            else:
                return self.g_FR_mu_EE.GetY()[bin]
        else:
            print "[ERROR] Wrong lepton ID:" + str(my_lep_id)
            return 0


    #==================prodece FakeRate from data================================
    def SSFRproduce(self,file):
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

        #=====================loop events and save passing and failing hitos=================
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
        #====================calculate FakeRates and save Gragh==========================
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


        FR_SS_electron_EB_unc = TGraphErrors (vector_X['EB']['electron'].size(),
											  vector_X['EB']['electron'][0],
											  vector_Y['EB']['electron'][0],
											  vector_EX['EB']['electron'][0],
											  vector_EY['EB']['electron'][0])
        FR_SS_electron_EB_unc.SetName("FR_SS_electron_EB_unc")

        FR_SS_electron_EE_unc = TGraphErrors (vector_X['EE']['electron'].size(),
											  vector_X['EE']['electron'][0],
											  vector_Y['EE']['electron'][0],
											  vector_EX['EE']['electron'][0],
											  vector_EY['EE']['electron'][0])
        FR_SS_electron_EE_unc.SetName("FR_SS_electron_EE_unc")

        FR_SS_muon_EE_unc = TGraphErrors (vector_X['EE']['muon'].size(),
										  vector_X['EE']['muon'][0],
										  vector_Y['EE']['muon'][0],
										  vector_EX['EE']['muon'][0],
										  vector_EY['EE']['muon'][0])
        FR_SS_muon_EE_unc.SetName("FR_SS_muon_EE_unc")

        FR_SS_muon_EB_unc = TGraphErrors (vector_X['EB']['muon'].size(),
										  vector_X['EB']['muon'][0],
										  vector_Y['EB']['muon'][0],
										  vector_EX['EB']['muon'][0],
										  vector_EY['EB']['muon'][0])
        FR_SS_muon_EB_unc.SetName("FR_SS_muon_EE_unc")
