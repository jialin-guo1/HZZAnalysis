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
        print "[INFO] Get FakeRate file: %s"%self.filename
        if(self.filename.find('OS')!=-1):
            print "[INFO] Get OS FakeRate file "
            self.g_FR_mu_EB = self.input_file_FR.Get("FR_OS_muon_EB")
            self.g_FR_mu_EE = self.input_file_FR.Get("FR_OS_muon_EE")
            self.g_FR_e_EB = self.input_file_FR.Get("FR_OS_electron_EB")
            self.g_FR_e_EE = self.input_file_FR.Get("FR_OS_electron_EE")
        if(self.filename.find('SS')!=-1):
            print "[INFO] Get SS FakeRate file "
            self.g_FR_mu_EB = self.input_file_FR.Get("FR_SS_muon_EB")
            self.g_FR_mu_EE = self.input_file_FR.Get("FR_SS_muon_EE")
            self.g_FR_e_EB = self.input_file_FR.Get("FR_SS_electron_EB")
            self.g_FR_e_EE = self.input_file_FR.Get("FR_SS_electron_EE")
            #self.g_FR_e_EB = self.input_file_FR.Get("FR_SS_electron_EB_unc")
            #self.g_FR_e_EE = self.input_file_FR.Get("FR_SS_electron_EE_unc")

    #============================================================================
    #==================Get FakeRate from existing file===========================
    #============================================================================
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
