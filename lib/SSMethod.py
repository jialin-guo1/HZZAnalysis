from ROOT import *
from deltaR import *
import math
from array import array
import FakeRates as FR
import sys

class SSMethod:
    def __init__(self,year):
        self.Datafile = "/cms/user/guojl/Sample/skimed/2018_noDuplicates.root"
        self.year = year
        self.lumi = 0
        self.cat_states=['corrected','uncorrected']
        self.cat_names=['EE','EB']
        self.var_names=['el','mu']
        self.nprocess=['data','WZ','TT','DY','qqZZ','Total']
        self.cat_CRnames=['4e', '4mu', '2mu2e', '2e2mu','inclusive']
        self.ZmassWindows=['_40_MZ1_120','_MZ1mMZtrue_7','_60_MZ1_120','_MZ1EmMZtrue_5']
        self.lep_CRindex=[0,0,0,0]
        self.passedSSCRselection = False


        self.FR_SS_electron_EB_unc=TGraphErrors()
        self.FR_SS_electron_EE_unc=TGraphErrors()
        self.FR_SS_muon_EB_unc=TGraphErrors()
        self.FR_SS_muon_EE_unc=TGraphErrors()
        self.FR_SS_electron_EB=TGraphErrors()
        self.FR_SS_electron_EE=TGraphErrors()
        self.FR_SS_muon_EB=TGraphErrors()
        self.FR_SS_muon_EE=TGraphErrors()
        self.FR_MissingHits={}

        self.nMissingHits={}
        self.npassing={}
        self.nfailing={}

        self.ele_FR_correction_function={}

        self.n_OSevents = {}
        self.n_SSevents = {}
        self.R_OS_over_SS = {}

        self.passing={}
        self.failing={}

        self.CRHistos={}
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

        self.pt_bins=[5, 7, 10, 20, 30, 40, 50, 80]
        self.n_pt_bins=8

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
        for cat_name in self.cat_CRnames:
            self.CRHistos[cat_name]={}
            for iprocess in self.nprocess:
                self.CRHistos[cat_name][iprocess]=TH1D("SSCR"+cat_name+iprocess,"SSCR"+cat_name+iprocess,40,70,870)

        #book OS and SS number dir for ratio calculation
        for cat_name in self.cat_CRnames:
            self.n_OSevents[cat_name]=0.0
            self.n_SSevents[cat_name]=0.0
            self.R_OS_over_SS[cat_name]=0.0

        #book ZX histos
        for cat_name in self.cat_CRnames:
            self.ZXHistos[cat_name]={}
            self.ZXHistos[cat_name]['data']=TH1D("ZX"+cat_name+'data',"ZX"+cat_name+'data',40,70,870)
            self.ZXHistos[cat_name]['data'].Sumw2()


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

        #book array for electron correction
        for ZmassWindow in self.ZmassWindows:
            self.nMissingHits[ZmassWindow]={}
            self.npassing[ZmassWindow]={}
            self.nfailing[ZmassWindow]={}
            for cat_name in self.cat_names:
                self.nMissingHits[ZmassWindow][cat_name]={}
                self.npassing[ZmassWindow][cat_name]={}
                self.nfailing[ZmassWindow][cat_name]={}
                for i_pt in range(self.n_pt_bins-2):
                    self.nMissingHits[ZmassWindow][cat_name][self.pt_bins[i_pt]]=0.0
                    self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]=0.0
                    self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]]=0.0
        #book Gragh for electron correction
        for i_pt in range(0,self.n_pt_bins-2):
            self.FR_MissingHits[self.pt_bins[i_pt]]={}
            self.ele_FR_correction_function[self.pt_bins[i_pt]]={}
            for cat_name in self.cat_names:
                self.FR_MissingHits[self.pt_bins[i_pt]][cat_name]=TGraphErrors()
                self.ele_FR_correction_function[self.pt_bins[i_pt]][cat_name]=TF1()

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

        #loop event to Fill
        for ievent,event in enumerate(inputTree):
            #if(ievent==1000): break
            self.passedSSCRselection=False
            if(event.lep_pt.size()<4): continue

            SSMethod.foundSSCRCandidate(self,event)
            if(not self.passedSSCRselection): continue
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
            #print "passedSSCRselection="+str(self.passedSSCRselection)
            #print "lep_CRindex="+str(self.lep_CRindex)
            #print "lep_pt="+str(event.lepFSR_pt)
            #print "pt 2 ="+str(event.lepFSR_pt[3])
            l1.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[0]],event.lepFSR_eta[self.lep_CRindex[0]],event.lepFSR_phi[self.lep_CRindex[0]],event.lepFSR_mass[self.lep_CRindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[1]],event.lepFSR_eta[self.lep_CRindex[1]],event.lepFSR_phi[self.lep_CRindex[1]],event.lepFSR_mass[self.lep_CRindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lepFSR_phi[self.lep_CRindex[2]],event.lepFSR_mass[self.lep_CRindex[2]])
            l4.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lepFSR_phi[self.lep_CRindex[3]],event.lepFSR_mass[self.lep_CRindex[3]])
            mass4l = (l1+l2+l3+l4).M()

            #fill inclusive
            self.CRHistos['inclusive'][process].Fill(mass4l,weight)
            #fill 4e, 4mu, 2e2mu, 2mu2e
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                self.CRHistos['4e'][process].Fill(mass4l,weight)
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                self.CRHistos['4mu'][process].Fill(mass4l,weight)
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==11 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                self.CRHistos['2e2mu'][process].Fill(mass4l,weight)
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==13 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                self.CRHistos['2mu2e'][process].Fill(mass4l,weight)



    #============================================================================
    #=====================Get Control Region samples=============================
    #============================================================================
    def foundSSCRCandidate(self,event):
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
                    self.lep_CRindex[0] = Z1_lepindex[0]
                    self.lep_CRindex[1] = Z1_lepindex[1]
                    self.lep_CRindex[2] = j1
                    self.lep_CRindex[3] = j2
                    self.passedSSCRselection = True


    #============================================================================
    #====================Save Raw Control Region histos==========================
    #============================================================================
    def SaveCRHistos(self):
        file = "../RawHistos/CRHistos_SS_%s_Legacy.root"%str(self.year)
        outfile = TFile(file,"recreate")
        outfile.cd()

        #c=TCanvas()
        #self.CRHistos['4e']['data'].Write()
        #c.SaveAs('SSCR_test.png')
        for cat_name in self.cat_CRnames:
            for iprocess in self.nprocess:
                self.CRHistos[cat_name][iprocess].Write()

        outfile.Close()
        print "[INFO] All Control Region histograms saved."


    #============================================================================
    #================Get Raw Control Region histos===============================
    #============================================================================
    def GetCRHistos(self):
        file = "../RawHistos/CRHistos_SS_%s_Legacy.root"%str(self.year)
        self.File_CRhisto = TFile(file)

        for cat_name in self.cat_CRnames:
            for iprocess in self.nprocess:
                self.CRHistos[cat_name][iprocess] = self.File_CRhisto.Get("SSCR"+cat_name+iprocess)

        print "[INFO] All Control Region histograms retrieved from file."

    #=============================================================================
    #=================plot Control Region=========================================
    #=============================================================================

    def PlotCR(self):
         c = TCanvas("CR","CR",600,600)
         for cat_name in self.cat_CRnames:
             self.CRHistos[cat_name]['WZ'].SetFillColor(kMagenta)
             self.CRHistos[cat_name]['qqZZ'].SetFillColor(kCyan+1)
             self.CRHistos[cat_name]['DY'].SetFillColor(kGreen + 1)
             self.CRHistos[cat_name]['TT'].SetFillColor(kBlue + 1)

             self.CRHistos[cat_name]['WZ'].SetLineColor(kMagenta)
             self.CRHistos[cat_name]['qqZZ'].SetLineColor(kCyan+1)
             self.CRHistos[cat_name]['DY'].SetLineColor(kGreen-1)
             self.CRHistos[cat_name]['TT'].SetLineColor(kBlue-2)

             self.CRHistos[cat_name]['data'].SetMarkerSize(0.8)
             self.CRHistos[cat_name]['data'].SetMarkerStyle(20)
             self.CRHistos[cat_name]['data'].SetBinErrorOption(TH1.kPoisson)
             self.CRHistos[cat_name]['data'].SetLineColor(kBlack)

             stack = THStack("stack","stack")
             stack.Add(self.CRHistos[cat_name]['qqZZ'])
             stack.Add(self.CRHistos[cat_name]['WZ'])
             stack.Add(self.CRHistos[cat_name]['TT'])
             stack.Add(self.CRHistos[cat_name]['DY'])
             stack.Draw("histo")

             data_max = self.CRHistos[cat_name]['data'].GetBinContent(self.CRHistos[cat_name]['data'].GetMaximumBin())
             data_max_error = self.CRHistos[cat_name]['data'].GetBinErrorUp(self.CRHistos[cat_name]['data'].GetMaximumBin())
             stack.SetMaximum((data_max+data_max_error)*1.1)
             stack.SetMinimum(0)

             if(cat_name=='4e'): label="m_{4#font[12]{e}} (GeV)"
             if(cat_name=='4mu'): label="m_{4#font[12]{#mu}} (GeV)"
             if(cat_name=='2e2mu'): label="m_{2#font[12]{e}2#font[12]{#mu}} (GeV)"
             if(cat_name=='2mu2e'): label="m_{2#font[12]{#mu}2#font[12]{e}} (GeV)"

             stack.GetXaxis().SetTitle(label)
             stack.GetXaxis().SetTitleSize(0.04)
             stack.GetXaxis().SetLabelSize(0.04)
             stack.GetYaxis().SetTitle("Event/%s GeV"%str(self.CRHistos[cat_name]['data'].GetBinWidth(1)))
             stack.GetYaxis().SetTitleSize(0.04)
             stack.GetYaxis().SetLabelSize(0.04)

             self.CRHistos[cat_name]['data'].Draw("SAME p E1 X0")

             legend = TLegend()
             legend = SSMethod.CreateLegend_CR(self,'right',cat_name)
             legend.Draw()

             cms_label,lumi_label = SSMethod.MakeCMSandLumiLabel(self)

             lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
             lumi_label.Draw('same')
             cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
             cms_label.Draw('same')

             plotname = "plot/SSCR_"+cat_name+"_%s"%str(self.year)
             #plotname = "SSCR_"+cat_name+"_%s"%str(self.year)
             SSMethod.SavePlots(self,c,plotname)

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
    def CreateLegend_CR(self,position,cat_name):
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

        leg.AddEntry(self.CRHistos[cat_name]['data'],"data",'p')
        leg.AddEntry(self.CRHistos[cat_name]['WZ'],"WZ",'f')
        leg.AddEntry(self.CRHistos[cat_name]['TT'],"t#bar{t} + jets",'f')
        leg.AddEntry(self.CRHistos[cat_name]['qqZZ'],"Z#gamma*, ZZ",'f')
        leg.AddEntry(self.CRHistos[cat_name]['DY'],"Z + jets",'f')

        return leg


    #============================================================================
    #=================calculate MC ratio of SS and OS Control Region=============
    #============================================================================
    def Calculate_SSOS_Ratio(self,OSCRfile):
        file = TFile(OSCRfile)
        temp_OS_CRhistos = {}
        for cat_name in self.cat_CRnames:
            temp_OS_CRhistos[cat_name]={}
            for iprocess in self.nprocess:
                temp_OS_CRhistos[cat_name][iprocess]=file.Get("OSCR"+"2P2F"+cat_name+iprocess)

        for cat_name in self.cat_CRnames:
            for iprocess in self.nprocess:
                if(iprocess=='data' or iprocess == 'qqZZ'):continue
                self.n_OSevents[cat_name] += temp_OS_CRhistos[cat_name][iprocess].Integral()
                self.n_SSevents[cat_name] += self.CRHistos[cat_name][iprocess].Integral()

        for cat_name in self.cat_CRnames:
            self.R_OS_over_SS[cat_name] = self.n_OSevents[cat_name]/self.n_SSevents[cat_name]
            print "[INFO] OS/SS in %s final state = "%cat_name + str(self.n_OSevents[cat_name]/self.n_SSevents[cat_name]) + "+/-" + str(math.sqrt(1.0/self.n_OSevents[cat_name]+1.0/self.n_SSevents[cat_name]))



    #===========================================================================
    #================Fill passing/failling histos===============================
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
            if(not event.passedZ1LSelection): continue
            if(event.met>25): continue
            #if(event.lep_Sip[event.lep_Hindex[2]]>4.0): continue
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
        outfilename="../RawHistos/FRHistos_SS_%s_Legacy.root"%str(self.year)
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
    #==================Remove Negative Bins for TH2D============================
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
        #self.a=2
        filename="../RawHistos/FRHistos_SS_%s_Legacy.root"%str(self.year)
        #inputfile = TFile.Open(filename)
        self.File_RFhisto=TFile(filename)
        #if(inputfile):
        #    print "[INFO] successfully handle file FRHistos_SS_%s_Legacy.root"%year
        #for var_name in self.var_names:
        #    for iprocess in self.nprocess:
        #        self.passing[iprocess][var_name]=inputfile.Get('pass'+iprocess+var_name)
        #        self.failing[iprocess][var_name]=inputfile.Get('failing'+iprocess+var_name)

        for iprocess in self.nprocess:
            self.passing[iprocess]={}
            self.failing[iprocess]={}
            for var_name in self.var_names:
                #self.passing[iprocess][var_name]=inputfile.Get('pass'+iprocess+var_name)
                #self.failing[iprocess][var_name]=inputfile.Get('failing'+iprocess+var_name)
                self.passing[iprocess][var_name]=self.File_RFhisto.Get('pass'+iprocess+var_name)
                self.failing[iprocess][var_name]=self.File_RFhisto.Get('failing'+iprocess+var_name)
                #print "[INFO] get histos="+iprocess+var_name

        #self.passing['Total']['el'].Draw()

        print "[INFO] All FakeRate histograms retrieved from file."


    #============================================================================
    #==================prodece FakeRate from data================================
    #============================================================================
    def SSFRproduce(self,process,file):

        outfilename="../RawHistos/FakeRates_SS_%s_Legacy.root"%str(self.year)
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
                temp_error_NP = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,1)
                temp_error_NF = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,1)


                self.vector_X['corrected']['EB'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['corrected']['EB'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['corrected']['EB'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['corrected']['EB'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

                temp_NP = self.passing['Total'][var_name].IntegralAndError(self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NP))
                temp_NF = self.failing['Total'][var_name].IntegralAndError(self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['Total'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NF))
                temp_error_NP = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,2)
                temp_error_NF = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,2)

                self.vector_X['corrected']['EE'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['corrected']['EE'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['corrected']['EE'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['corrected']['EE'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*pow(temp_error_NF,2)))

                #Just for fake rate plots calculate the same for histograms without WZ subtraction
                temp_NP = self.passing['data'][var_name].IntegralAndError(self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NP))
                temp_NF = self.failing['data'][var_name].IntegralAndError(self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 1, 1, Double(temp_error_NF))
                temp_error_NP = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,1)
                temp_error_NF = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,1)

                self.vector_X['uncorrected']['EB'][var_name].append((pt_bins[i_pt_bin] + pt_bins[i_pt_bin + 1])/2)
                self.vector_Y['uncorrected']['EB'][var_name].append(temp_NP/(temp_NP+temp_NF))
                self.vector_EX['uncorrected']['EB'][var_name].append((pt_bins[i_pt_bin + 1] - pt_bins[i_pt_bin])/2)
                self.vector_EY['uncorrected']['EB'][var_name].append(math.sqrt(math.pow((temp_NF/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NP,2) + math.pow((temp_NP/math.pow(temp_NF+temp_NP,2)),2)*math.pow(temp_error_NF,2)))

                temp_NP = self.passing['data'][var_name].IntegralAndError(self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.passing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NP))
                temp_NF = self.failing['data'][var_name].IntegralAndError(self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin]),self.failing['data'][var_name].GetXaxis().FindBin(pt_bins[i_pt_bin+1]) - 1, 2, 2, Double(temp_error_NF))
                temp_error_NP = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,True,2)
                temp_error_NF = SSMethod.GetErorr(self,pt_bins,i_pt_bin,process,var_name,False,2)

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
        self.FR_SS_muon_EB_unc.SetName("FR_SS_muon_EB_unc")

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
        self.FR_SS_muon_EB.SetName("FR_SS_muon_EB")

        # Electron fake rates must be corrected using average number of missing hits
        SSMethod.CorrectElectronFakeRate(self,file)

        self.FR_SS_electron_EB = TGraphErrors (len(self.vector_X['corrected']['EB']['el']),
											  self.vector_X['corrected']['EB']['el'],
											  self.vector_Y['corrected']['EB']['el'],
											  self.vector_EX['corrected']['EB']['el'],
											  self.vector_EY['corrected']['EB']['el'])
        self.FR_SS_electron_EB.SetName("FR_SS_electron_EB")

        self.FR_SS_electron_EE = TGraphErrors (len(self.vector_X['uncorrected']['EE']['el']),
											  self.vector_X['uncorrected']['EE']['el'],
											  self.vector_Y['uncorrected']['EE']['el'],
											  self.vector_EX['uncorrected']['EE']['el'],
											  self.vector_EY['uncorrected']['EE']['el'])
        self.FR_SS_electron_EE.SetName("FR_SS_electron_EE")



        SSMethod.plotFR(self)
        SSMethod.SaveFRGragh(self,outfilename)



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


    #===========================================================================
    #===================save raw FakeRates Gragh================================
    #===========================================================================
    def SaveFRGragh(self,outfilename):

        #print "[INFO] check value of vector ele in SaveFRGragh function "
        #c=TCanvas()
        #self.FR_SS_electron_EB_unc.Draw()
        #c.SaveAs("FR_SS_electron_EB_unc")



        self.File_RFGragh=TFile(outfilename,"RECREATE")
        self.File_RFGragh.cd()
        self.FR_SS_electron_EB_unc.Write()
        self.FR_SS_electron_EE_unc.Write()
        self.FR_SS_muon_EE_unc.Write()
        self.FR_SS_muon_EB_unc.Write()
        self.FR_SS_electron_EB.Write()
        self.FR_SS_electron_EE.Write()
        self.FR_SS_muon_EE.Write()
        self.FR_SS_muon_EB.Write()
        self.File_RFGragh.Close()

        print "[INFO] All FakeRate histograms were saved."

    #============================================================================
    #==================corrected electron FakeRate===============================
    #============================================================================
    def CorrectElectronFakeRate(self,file):

        SSMethod.Calculate_FR_nMissingHits(self,file)
        SSMethod.Fit_FRnMH_graphs(self)
        SSMethod.Correct_Final_FR(self,file)

    #============================================================================
    #===============calculate  average nMissingHits==============================
    #============================================================================
    def Calculate_FR_nMissingHits(self,file):
        inputfile = TFile(file)
        inputTree = inputfile.Get("passedEvents")
        if(inputTree):
            print "[INFO] get file to calculate electron nMissingHits"
        else:
            print "[ERROR] No tree in file. Process end!"
            sys.exit()

        #loop events
        for ievent,event in enumerate(inputTree):
            if(not event.passedZ1LSelection): continue
            if(event.met>25): continue
            if(abs(event.lep_id[evnet.lep_Hindex[2]])!=11): continue # only consider electron
            current_pt_bin = Find_pt_bin(event.lepFSR_pt[event.lep_Hindex[2]])
            current_eta_bin  = Find_eta_bin(event.lepFSR_eta[event.lep_Hindex[2]])
            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l3 = TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[0]],event.lepFSR_phi[event.lep_Hindex[0]],event.lepFSR_mass[event.lep_Hindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[1]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[1]],event.lepFSR_mass[event.lep_Hindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[2]],event.lepFSR_eta[event.lep_Hindex[2]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[2]])
            Z1mass = (l1+l2).M()
            if(Z1mass>40 and Z1mass<120):
                self.nMissingHits['_40_MZ1_120'][current_eta_bin][current_pt_bin]+=evnet.lep_missingHits[event.lep_Hindex[2]]
                if(event.lep_tightId[lep_Hindex[2]] and event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35):
                    self.npassing['_40_MZ1_120'][current_eta_bin][current_pt_bin]+=1
                else:
                    self.nfailing['_40_MZ1_120'][current_eta_bin][current_pt_bin]+=1
            if(abs(Z1mass-self.Zmass)<7):
                self.nMissingHits['_MZ1mMZtrue_7'][current_eta_bin][current_pt_bin]+=evnet.lep_missingHits[event.lep_Hindex[2]]
                if(event.lep_tightId[lep_Hindex[2]] and event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35):
                    self.npassing['_MZ1mMZtrue_7'][current_eta_bin][current_pt_bin]+=1
                else:
                    self.nfailing['_MZ1mMZtrue_7'][current_eta_bin][current_pt_bin]+=1
            if(Z1mass>40 and Z1mass<120):
                self.nMissingHits['_60_MZ1_120'][current_eta_bin][current_pt_bin]+=evnet.lep_missingHits[event.lep_Hindex[2]]
                if(event.lep_tightId[lep_Hindex[2]] and event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35):
                    self.npassing['_60_MZ1_120'][current_eta_bin][current_pt_bin]+=1
                else:
                    self.nfailing['_60_MZ1_120'][current_eta_bin][current_pt_bin]+=1
            if(abs((l1+l2+l3).M()-self.Zmass)<5):
                self.nMissingHits['_MZ1EmMZtrue_5'][current_eta_bin][current_pt_bin]+=evnet.lep_missingHits[event.lep_Hindex[2]]
                if(event.lep_tightId[lep_Hindex[2]] and event.lep_RelIsoNoFSR[event.lep_Hindex[2]]<0.35):
                    self.npassing['_MZ1EmMZtrue_5'][current_eta_bin][current_pt_bin]+=1
                else:
                    self.nfailing['_MZ1EmMZtrue_5'][current_eta_bin][current_pt_bin]+=1
        #book array
        vector_X={}
        vector_Y={}
        vector_EX={}
        vector_EY={}
        for cat_name in self.cat_names:
            vector_X[cat_name]={}
            vector_EX[cat_name]={}
            vector_Y[cat_name]={}
            vector_EY[cat_name]={}
            for i_pt in range(0,self.n_pt_bins-2):
                vector_X[cat_name][self.pt_bins[i_pt]]=array('f',[])
                vector_EX[cat_name][self.pt_bins[i_pt]]=array('f',[])
                vector_Y[cat_name][self.pt_bins[i_pt]]=array('f',[])
                vector_EY[cat_name][self.pt_bins[i_pt]]=array('f',[])
        for i_pt in range(0,self.n_pt_bins-2):
            for cat_name in self.cat_names:
                for ZmassWindow in self.ZmassWindows:
                    vector_X[cat_name][self.pt_bins[i_pt]].append(self.nMissingHits[ZmassWindow][cat_name][self.pt_bins[i_pt]]/(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]]))
                    vector_EX[cat_name][self.pt_bins[i_pt]].append(math.sqrt(math.pow(1.0/math.pow(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]],1),2)*self.nMissingHits[ZmassWindow][cat_name][self.pt_bins[i_pt]]+math.pow(self.nMissingHits[ZmassWindow][cat_name][self.pt_bins[i_pt]]/math.pow(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]],2),2)*(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]])))

                    vector_Y[cat_name][self.pt_bins[i_pt]].append(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]/(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]]))
                    vector_EY[cat_name][self.pt_bins[i_pt]].append(math.sqrt(math.pow(self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]]/math.pow(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]],2),2)*self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+math.pow(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]/math.pow(self.npassing[ZmassWindow][cat_name][self.pt_bins[i_pt]]+self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]],2),2)*self.nfailing[ZmassWindow][cat_name][self.pt_bins[i_pt]]))

        for i_pt in range(0,self.n_pt_bins-2):
            for cat_name in self.cat_names:
                self.FR_MissingHits[self.pt_bins[i_pt]][cat_name]=TGraphErrors(len(vector_X[cat_name][self.pt_bins[i_pt]]),vector_X[cat_name][self.pt_bins[i_pt]],vector_Y[cat_name][self.pt_bins[i_pt]],vector_EX[cat_name][self.pt_bins[i_pt]],vector_EY[cat_name][self.pt_bins[i_pt]])


    #============================================================================
    #=================fit electron FR Gragh======================================
    #============================================================================
    def Fit_FRnMH_graphs(self):
        for i_pt in range(0,self.n_pt_bins-2):
            for cat_name in self.cat_names:
                func_name = "FR_MissingHits_func_{0:s}_{1:s}".format(str(self.n_pt_bins[i_pt]),cat_name)
                self.ele_FR_correction_function[self.n_pt_bins[i_pt]][cat_name]=TF1(func_name,"[0]*x+[1]",0,3)
                self.ele_FR_correction_function[self.n_pt_bins[i_pt]][cat_name].SetParameter(0,1.)
                self.ele_FR_correction_function[self.n_pt_bins[i_pt]][cat_name].SetParameter(1.,0)

                self.FR_MissingHits[self.n_pt_bins[i_pt]][cat_name].Fit(self.ele_FR_correction_function[self.n_pt_bins[i_pt]][cat_name],"Q")

                gragh_name = "FR_MissingHits_gragh_{0:s}_{1:s}".format(str(self.n_pt_bins[i_pt]),cat_name)
                self.FR_MissingHits[self.n_pt_bins[i_pt]][cat_name].SetName(graph_name)
                self.FR_MissingHits[self.n_pt_bins[i_pt]][cat_name].GetXaxis().SetTitle("<# Missing Hits>")
                self.FR_MissingHits[self.n_pt_bins[i_pt]][cat_name].GetYaxis().SetTitle("Fake Rate")

                c = TCanvas(gragh_name,gragh_name,900,900)
                self.FR_MissingHits[self.n_pt_bins[i_pt]][cat_name].Draw("AP")
                SSMethod.SavePlots(self,c,"Fit"+gragh_name)




    #============================================================================
    #==================calculate final correction================================
    #============================================================================
    def Correct_Final_FR(self,file):
        inputfile = TFile(file)
        inputTree = inputfile.Get("passedEvents")
        if(inputTree):
            print "[INFO] get file to calculate electron nMissingHits"
        else:
            print "[ERROR] No tree in file. Process end!"
            sys.exit()

        #book variables
        nMissingHits={}
        avgMissingHits={}
        passing={}
        failing={}
        for cat_name in self.cat_names:
            nMissingHits[cat_name]={}
            avgMissingHits[cat_name]={}
            passing[cat_name]={}
            failing[cat_name]={}
            for i_pt in range(0,self.n_pt_bins-2):
                nMissingHits[cat_name][self.pt_bins[i_pt]]=0.0
                avgMissingHits[cat_name][self.pt_bins[i_pt]]=0.0
                passing[cat_name][self.pt_bins[i_pt]]=0.0
                failing[cat_name][self.pt_bins[i_pt]]=0.0


        #loop events
        for ievent,event in enumerate(inputTree):
            #if(ievent==1000): break
            self.passedSSCRselection=False
            if(event.lep_pt.size()<4): continue

            SSMethod.foundSSCRCandidate(self,event)
            if(not self.passedSSCRselection): continue
            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l3 = TLorentzVector()
            l4 = TLorentzVector()
            #print "passedSSCRselection="+str(self.passedSSCRselection)
            #print "lep_CRindex="+str(self.lep_CRindex)
            #print "lep_pt="+str(event.lepFSR_pt)
            #print "pt 2 ="+str(event.lepFSR_pt[3])
            l1.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[0]],event.lepFSR_eta[self.lep_CRindex[0]],event.lepFSR_phi[self.lep_CRindex[0]],event.lepFSR_mass[self.lep_CRindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[1]],event.lepFSR_eta[self.lep_CRindex[1]],event.lepFSR_phi[self.lep_CRindex[1]],event.lepFSR_mass[self.lep_CRindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lepFSR_phi[self.lep_CRindex[2]],event.lepFSR_mass[self.lep_CRindex[2]])
            l4.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lepFSR_phi[self.lep_CRindex[3]],event.lepFSR_mass[self.lep_CRindex[3]])
            mass4l = (l1+l2+l3+l4).M()
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):

                current_pt_bin = Find_pt_bin(event.lepFSR_pt[self.lep_CRindex[2]])
                current_eta_bin = Find_eta_bin(event.lepFSR_eta[self.lep_CRindex[2]])
                nMissingHits[current_eta_bin][current_pt_bin]+=event.lep_missingHits[self.lep_CRindex[2]]
                if(event.lep_tightId[self.lep_CRindex[2]] and event.lep_RelIsoNoFSR[self.lep_CRindex[2]]<0.35):
                    passing[current_eta_bin][current_pt_bin]+=1
                else:
                    failing[current_eta_bin][current_pt_bin]+=1

                current_pt_bin = Find_pt_bin(event.lepFSR_pt[self.lep_CRindex[3]])
                current_eta_bin = Find_eta_bin(event.lepFSR_eta[self.lep_CRindex[3]])
                nMissingHits[current_eta_bin][current_pt_bin]+=event.lep_missingHits[self.lep_CRindex[3]]
                if(event.lep_tightId[self.lep_CRindex[3]] and event.lep_RelIsoNoFSR[self.lep_CRindex[3]]<0.35):
                    passing[current_eta_bin][current_pt_bin]+=1
                else:
                    failing[current_eta_bin][current_pt_bin]+=1

        #crrecte
        for i_pt in range(0,self.n_pt_bins-2):
            sigma = 0.0
            avgMissingHits['EB'][self.pt_bins[i_pt]] = nMissingHits['EB'][self.pt_bins[i_pt]]/(passing['EB'][self.pt_bins[i_pt]]+failling['EB'][self.pt_bins[i_pt]])
            sigma = math.sqrt(math.pow((1./pow(failing['EB'][self.pt_bins[i_pt]]+passing['EB'][self.pt_bins[i_pt]],1)),2)*nMissingHits['EB'][self.pt_bins[i_pt]] + math.pow((nMissingHits['EB'][self.pt_bins[i_pt]]/math.pow(failing['EB'][i_pt]+passing['EB'][self.pt_bins[i_pt]],2)),2)*(failing['EB'][self.pt_bins[i_pt]]+passing['EB'][self.pt_bins[i_pt]]))
            self.vector_X['corrected']['EB']['el']=(self.pt_bins[i_pt+1]+self.pt_bins[i_pt+2])/2
            self.vector_Y['corrected']['EB']['el']=self.ele_FR_correction_function[self.pt_bins[i_pt]]['EB'].Eval(avgMissingHits['EB'][self.pt_bins[i_pt]])
            self.vector_EX['corrected']['EB']['el']=(self.pt_bins[i_pt+1]+self.pt_bins[i_pt+2])/2
            self.vector_EY['corrected']['EB']['el']=self.ele_FR_correction_function[self.pt_bins[i_pt]]['EB'].Eval(avgMissingHits['EB'][self.pt_bins[i_pt]])-self.ele_FR_correction_function[self.pt_bins[i_pt]]['EB'].Eval(avgMissingHits['EB'][self.pt_bins[i_pt]]-sigma)

            avgMissingHits['EE'][self.pt_bins[i_pt]] = nMissingHits['EE'][self.pt_bins[i_pt]]/(passing['EE'][self.pt_bins[i_pt]]+failling['EE'][self.pt_bins[i_pt]])
            sigma = math.sqrt(math.pow((1./pow(failing['EE'][self.pt_bins[i_pt]]+passing['EE'][self.pt_bins[i_pt]],1)),2)*nMissingHits['EE'][self.pt_bins[i_pt]] + math.pow((nMissingHits['EE'][self.pt_bins[i_pt]]/math.pow(failing['EE'][i_pt]+passing['EE'][self.pt_bins[i_pt]],2)),2)*(failing['EE'][self.pt_bins[i_pt]]+passing['EE'][self.pt_bins[i_pt]]))
            self.vector_X['corrected']['EE']['el']=(self.pt_bins[i_pt+1]+self.pt_bins[i_pt+2])/2
            self.vector_Y['corrected']['EE']['el']=self.ele_FR_correction_function[self.pt_bins[i_pt]]['EE'].Eval(avgMissingHits['EE'][self.pt_bins[i_pt]])
            self.vector_EX['corrected']['EE']['el']=(self.pt_bins[i_pt+1]+self.pt_bins[i_pt+2])/2
            self.vector_EY['corrected']['EE']['el']=self.ele_FR_correction_function[self.pt_bins[i_pt]]['EE'].Eval(avgMissingHits['EE'][self.pt_bins[i_pt]])-self.ele_FR_correction_function[self.pt_bins[i_pt]]['EE'].Eval(avgMissingHits['EE'][self.pt_bins[i_pt]]-sigma)




    #============================================================================
    #==================Draw FR plots=============================================
    #============================================================================
    def plotFR(self):

        #print "[INFO] check value of vector ele in plot function "
        #print "vector_X['uncorrected']['EB']['el'] = "+str(self.vector_X['uncorrected']['EB']['el'])
        #print "vector_Y['uncorrected']['EB']['el']= "+str(self.vector_Y['uncorrected']['EB']['el'])
        #print "vector_EX['uncorrected']['EB']['el'] = "+str(self.vector_EX['uncorrected']['EB']['el'])
        #print "vector_EY['uncorrected']['EB']['el'] = "+str(self.vector_EX['uncorrected']['EB']['el'])

        c_ele=TCanvas("FR_ele", "FR_ele", 700,700)
        c_muon=TCanvas("FR_muon","FRmuon",700,700)
        #mg_electrons=TMultiGraph()
        #mg_muons=TMultiGraph()

        self.mg_electrons.Add(self.FR_SS_electron_EB_unc)
        self.FR_SS_electron_EB_unc.SetLineColor(kBlue)
        self.FR_SS_electron_EB_unc.SetLineStyle(1)
        self.FR_SS_electron_EB_unc.SetMarkerSize(0)
        self.FR_SS_electron_EB_unc.SetTitle("barel uncorrected")
        self.mg_electrons.Add(self.FR_SS_electron_EE_unc)
        self.FR_SS_electron_EE_unc.SetLineColor(kRed);
        self.FR_SS_electron_EE_unc.SetLineStyle(1);
        self.FR_SS_electron_EE_unc.SetMarkerSize(0);
        self.FR_SS_electron_EE_unc.SetTitle("endcap uncorrected")

        self.mg_electrons.Add(self.FR_SS_electron_EB)
        self.FR_SS_electron_EB.SetLineColor(kBlue)
        self.FR_SS_electron_EB.SetLineStyle(2)
        self.FR_SS_electron_EB.SetMarkerSize(0)
        self.FR_SS_electron_EB.SetTitle("barel corrected")
        self.mg_electrons.Add(self.FR_SS_electron_EE)
        self.FR_SS_electron_EE.SetLineColor(kRed);
        self.FR_SS_electron_EE.SetLineStyle(2);
        self.FR_SS_electron_EE.SetMarkerSize(0);
        self.FR_SS_electron_EE.SetTitle("endcap corrected")

        self.mg_muons.Add(self.FR_SS_muon_EB_unc)
        self.FR_SS_muon_EB_unc.SetLineColor(kBlue)
        self.FR_SS_muon_EB_unc.SetLineStyle(1)
        self.FR_SS_muon_EB_unc.SetMarkerSize(0)
        self.FR_SS_muon_EB_unc.SetTitle("barel uncorrected")
        self.mg_muons.Add(self.FR_SS_muon_EE_unc)
        self.FR_SS_muon_EE_unc.SetLineColor(kRed)
        self.FR_SS_muon_EE_unc.SetLineStyle(1)
        self.FR_SS_muon_EE_unc.SetMarkerSize(0)
        self.FR_SS_muon_EE_unc.SetTitle("endcap uncorrected")

        self.mg_muons.Add(self.FR_SS_muon_EB)
        self.FR_SS_muon_EB.SetLineColor(kBlue)
        self.FR_SS_muon_EB.SetLineStyle(2)
        self.FR_SS_muon_EB.SetMarkerSize(0)
        self.FR_SS_muon_EB.SetTitle("barel corrected")
        self.mg_muons.Add(self.FR_SS_muon_EE)
        self.FR_SS_muon_EE.SetLineColor(kRed)
        self.FR_SS_muon_EE.SetLineStyle(2)
        self.FR_SS_muon_EE.SetMarkerSize(0)
        self.FR_SS_muon_EE.SetTitle("endcap corrected")

        gStyle.SetEndErrorSize(0)

        leg_ele = TLegend()
        leg_muon = TLegend()
        c_ele.cd()
        self.mg_electrons.Draw("AP");
	self.mg_electrons.GetXaxis().SetTitle("p_{T} [GeV]")
	self.mg_electrons.GetYaxis().SetTitle("Fake Rate")
        self.mg_electrons.GetYaxis().SetTitleSize(0.029)
	self.mg_electrons.SetTitle("Electron fake rate")
        self.mg_electrons.SetMaximum(0.35)
        leg_ele = SSMethod.CreateLegend_FR(self,"left",self.FR_SS_electron_EB_unc,self.FR_SS_electron_EE_unc,self.FR_SS_electron_EB,self.FR_SS_electron_EE)
        leg_ele.Draw()
        SSMethod.SavePlots(self,c_ele, "plot/FR_SS_electrons")

        c_muon.cd()
        self.mg_muons.Draw("AP")
	self.mg_muons.GetXaxis().SetTitle("p_{T} [GeV]")
	self.mg_muons.GetYaxis().SetTitle("Fake Rate")
        self.mg_muons.GetYaxis().SetTitleSize(0.029)
	self.mg_muons.SetTitle("Muon fake rate")
        self.mg_muons.SetMaximum(0.35)
        leg_mu = SSMethod.CreateLegend_FR(self,"left",self.FR_SS_muon_EB_unc,self.FR_SS_muon_EE_unc,self.FR_SS_muon_EB,self.FR_SS_muon_EE);
        leg_mu.Draw()
        SSMethod.SavePlots(self,c_muon, "plot/FR_SS_muons")

    #=============================================================================
    #=============Create Legend for FakeRates=====================================
    #=============================================================================
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

    #============================================================================
    #=================create ZX histos===========================================
    #============================================================================
    def FillZXHistos(self,FRfile,datafile):
        ninclusive = 0
        n4e = 0
        n4mu = 0
        n2e2mu = 0
        n2mu2e = 0
        FakeRate= FR.FakeRates(FRfile)
        print "type of g_FR_e_EE = "+str(FakeRate.g_FR_e_EE)
        print "g_FR_e_EE.GetY()[2] = "+str(FakeRate.g_FR_e_EE.GetY()[2])
        file = TFile(datafile)
        if(file):
            print"[INFO] get datafile to produce ZX"
        tree = file.Get("passedEvents")
        for ievent,event in enumerate(tree):
            self.passedSSCRselection=False

            SSMethod.foundSSCRCandidate(self,event)
            if(not self.passedSSCRselection): continue
            #weight=FakeRate.GetFakeRate(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lep_id[self.lep_CRindex[2]])*FakeRate.GetFakeRate(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lep_id[self.lep_CRindex[3]])
            weight=FakeRate.GetFakeRate(event.lep_pt[self.lep_CRindex[2]],event.lep_eta[self.lep_CRindex[2]],event.lep_id[self.lep_CRindex[2]])*FakeRate.GetFakeRate(event.lep_pt[self.lep_CRindex[3]],event.lep_eta[self.lep_CRindex[3]],event.lep_id[self.lep_CRindex[3]])

            l1 = TLorentzVector()
            l2 = TLorentzVector()
            l3 = TLorentzVector()
            l4 = TLorentzVector()
            l1.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[0]],event.lepFSR_eta[self.lep_CRindex[0]],event.lepFSR_phi[self.lep_CRindex[0]],event.lepFSR_mass[self.lep_CRindex[0]])
            l2.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[1]],event.lepFSR_eta[self.lep_CRindex[1]],event.lepFSR_phi[self.lep_CRindex[1]],event.lepFSR_mass[self.lep_CRindex[1]])
            l3.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[2]],event.lepFSR_eta[self.lep_CRindex[2]],event.lepFSR_phi[self.lep_CRindex[2]],event.lepFSR_mass[self.lep_CRindex[2]])
            l4.SetPtEtaPhiM(event.lepFSR_pt[self.lep_CRindex[3]],event.lepFSR_eta[self.lep_CRindex[3]],event.lepFSR_phi[self.lep_CRindex[3]],event.lepFSR_mass[self.lep_CRindex[3]])
            mass4l = (l1+l2+l3+l4).M()

            #fill inclusive
            self.ZXHistos['inclusive']['data'].Fill(mass4l,weight*self.R_OS_over_SS['inclusive'])
            ninclusive+=1
            #fill 4e, 4mu, 2e2mu, 2mu2e
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                self.ZXHistos['4e']['data'].Fill(mass4l,weight*self.R_OS_over_SS['4e'])
                if(0<=mass4l<=300):
                    n4e+=1
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                self.ZXHistos['4mu']['data'].Fill(mass4l,weight*self.R_OS_over_SS['4mu'])
                if(0<=mass4l<=300):
                    n4mu+=1
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==11 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==13):
                self.ZXHistos['2e2mu']['data'].Fill(mass4l,weight*self.R_OS_over_SS['2e2mu'])
                if(0<=mass4l<=300):
                    n2e2mu+=1
            if(abs(event.lep_id[self.lep_CRindex[0]])==abs(event.lep_id[self.lep_CRindex[1]])==13 and abs(event.lep_id[self.lep_CRindex[2]])==abs(event.lep_id[self.lep_CRindex[3]])==11):
                self.ZXHistos['2mu2e']['data'].Fill(mass4l,weight*self.R_OS_over_SS['2mu2e'])
                if(0<=mass4l<=300):
                    n2mu2e+=1

        print "[INFO] Total number of inclusive ZX backgrounds estimation = "+str(ninclusive)
        print "[INFO] Total number of 4e channel ZX backgrounds estimation = "+str(n4e)
        print "[INFO] Total number of 4mu channel ZX backgrounds estimation = "+str(n4mu)
        print "[INFO] Total number of 2e2mu channel ZX backgrounds estimation = "+str(n2e2mu)
        print "[INFO] Total number of 4e channel ZX backgrounds estimation = "+str(n2mu2e)
        SSMethod.CountEvents(self,'data')


    #============================================================================
    #=======================count events from Histos=============================
    #============================================================================
    def CountEvents(self,process):
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



    #============================================================================
    #=======================Save plots===========================================
    #============================================================================
    def SavePlots(self,c,name):
        c.SaveAs(name+".png")

    #============================================================================
    #==============check lep size in file========================================
    #============================================================================
