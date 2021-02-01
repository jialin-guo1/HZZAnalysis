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
        self.cat_failnames = ['3P1F','2P2F']
        self.lep_CRindex=[0,0,0,0]
        self.passedOSCRselection = False

        self.FR_SS_electron_EB_unc=TGraphErrors()
        self.FR_SS_electron_EE_unc=TGraphErrors()
        self.FR_SS_muon_EB_unc=TGraphErrors()
        self.FR_SS_muon_EE_unc=TGraphErrors()
        self.FR_SS_electron_EB=TGraphErrors()
        self.FR_SS_electron_EE=TGraphErrors()
        self.FR_SS_muon_EB=TGraphErrors()
        self.FR_SS_muon_EE=TGraphErrors()

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
            for cat_name in self.cat_CRnames:
                self.CRHistos[cat_failname][cat_name]={}
                for iprocess in self.nprocess:
                    self.CRHistos[cat_failname][cat_name][iprocess]=TH1D("OSCR"+cat_failname+cat_name+iprocess,"OSCR"+cat_failname+cat_name+iprocess,40,70,870)

        #book ZX histos
        for cat_name in self.cat_CRnames:
            self.ZXHistos[cat_name]={}
            self.ZXHistos[cat_name]['data']=TH1D("ZX"+cat_name+'data',"ZX"+cat_name+'data',150,0,300)

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
            #print "passedSSCRselection="+str(self.passedSSCRselection)
            #print "lep_CRindex="+str(self.lep_CRindex)
            #print "lep_pt="+str(event.lepFSR_pt)
            #print "pt 2 ="+str(event.lepFSR_pt[3])
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
    #============
    #===========================================================================
    #def


    #============================================================================
    #=======================Save plots===========================================
    #============================================================================
    def SavePlots(self,c,name):
        c.SaveAs(name+".png")
