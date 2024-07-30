import ROOT
from ROOT import RooRealVar, RooHistPdf, RooDataHist, RooArgSet, TCanvas, RooFit, RooAbsPdf, TSpline3
from higgs_width import parameters as width_parameters
import os
import sys
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from logset import *
# load C++ library
ROOT.gInterpreter.ProcessLine('#include "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/SplinePdf.h"')

class ConstructSignal2l2q:
    def __init__(self,mass,width,production='ggf'):
        self.low_mass = 0
        self.high_mass = 3500
        self.mH = int(mass)
        self.width_bw = float(width)
        self.production = production

        self.sigpdf = RooHistPdf()
        self.sig_dcb = ROOT.RooDoubleCB()
        self.datahist = None
        self.sig_conv = None
        self.a1_ggH = None
        self.a2_ggH = None
        self.n1_ggH = None
        self.n2_ggH = None
        self.mean_ggH = None
        self.sigma_ggH = None

        #SM Higgs
        self.hsig_125 = ROOT.TH1F('h_h125','h_h125',3500,self.low_mass,self.high_mass)
        self.width_higgs = ROOT.RooRealVar("w_higgs", "w_higgs", 0.00407,0,1000)
        #self.BR_higgsZZTo2l2q = 0.0262*0.156*0.03368*2
        self.BR_higgsZZTo2l2q = 1 # test with 1

        #dir name for saving plots
        self.name_dir = 'PlotsSignalModel'

        #reco level information
        self.hsig_reco = ROOT.TH1F('hsig_reco','hsig_reco',3500,self.low_mass,self.high_mass)
        self.roohist_sig_reco = None
        self.sigpdf_reco = None

        self.mass_zz2l2q = ROOT.RooRealVar("mass", "Mass", self.low_mass, self.high_mass)
        nbins = self.high_mass
        self.mass_zz2l2q.setBins(nbins)

        self.mass_zz2l2q = ROOT.RooRealVar("mass", "Mass", self.low_mass, self.high_mass)
        self.mean = ROOT.RooRealVar("mean", "Mean", self.mH,self.low_mass, self.high_mass)
        self.width = ROOT.RooRealVar("width", "Width", self.width_bw,0,1000)

        #self.build_RooRealvar()
        self.init_splinepdf()
        self.init_saveplots_dir()
        self.init_reco_rootfile()

    def init_saveplots_dir(self):
        '''
        create directory to save plots
        '''
        if not os.path.exists(self.name_dir):
            os.makedirs(self.name_dir)

    def init_splinepdf(self):
        '''
        create a higgs pdf
        defualt production is ggf, if production is vbf, set production = 'vbf'
        input aguments m2l2q_gen, Mass and Width should be RooRealVar
        '''

        # input spline file
        f_spline = ROOT.TFile("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/GeliangShare/public/h4l_highmass/{}_input_spline.root".format(self.production))

        # load splines
        spline = f_spline.Get("sp_xsec_{}_2e2mu".format(self.production))

        # create SplinePdf
        self.higgspdf = ROOT.SplinePdf("higgspdf","higgspdf",self.mass_zz2l2q,self.mean,self.width,spline)

    def init_reco_rootfile(self):
        '''
        Atumaticaly crab the root file name of MC signal sample based on mass
        '''
        base_dir = "/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggh/skimed/"
        # get root file name under base_dir
        for root,dirs,files in os.walk(base_dir):
            for file in files:
                if ("_M"+str(self.mH)+"_") in file:
                    self.sig_mc_file = file
                    print("Signal MC file: ", self.sig_mc_file)
                
    def build_sighisto(self,ifplot=False):
        '''
        build signal pdf
        '''
        # test pdf
        nbins = 3500
        self.hsig_2l2q = ROOT.TH1F('hsig_2l2q','hsig_2l2q',nbins,self.low_mass,self.high_mass)
        for ib in range(1,nbins+1):
            x = self.hsig_2l2q.GetBinCenter(ib)
            self.mass_zz2l2q.setVal(x)
            mass_set = ROOT.RooArgSet(self.mass_zz2l2q)
            if(((x<self.mH-3*self.width_bw) & (x<self.mH-0.5*0.5)) | ((x>self.mH+3*self.width_bw) & (x>self.mH+0.5*0.5)) | (self.width_bw>10*0.5)):
                bc = self.higgspdf.getVal(mass_set)
                bc_range = self.higgspdf.getVal(mass_set)*0.5
            else:
                bc = 0
                bc_range = 0
                for j in range(-500,500):
                    xx = self.mH + j*0.02*self.width_bw
                    if(xx>x-0.5*0.5 & xx<=x+0.5*0.5):
                        self.mass_zz2l2q.setVal(xx)
                        mass_set = ROOT.RooArgSet(self.mass_zz2l2q)
                        bc += self.higgspdf.getVal(mass_set)
                        bc_range += self.higgspdf.getVal(mass_set)*0.02*self.width_bw
            if bc<0: bc = 0
            self.hsig_2l2q.SetBinContent(ib,bc)
        print("Integral of signal histogram: ", self.hsig_2l2q.Integral())
        #plot histogram
        if ifplot:
            c = ROOT.TCanvas('c','c',800,600)
            self.hsig_2l2q.Draw()
            c.Draw()
            c.SaveAs('test_histo.png')
            c.Close()

        # save histogram in root file
        f = ROOT.TFile('test_histo.root','recreate')
        self.hsig_2l2q.Write()
        f.Close()

    def build_sighisto_debug(self,ifplot=False):
        '''
        build signal pdf
        '''
        self.f_eff = ROOT.TFile("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/Files/2l2q_Efficiency_spin0_ggH_2018.root")
        self.sig_eff = self.f_eff.Get("spin0_ggH_eeqq_Merged_untagged")

        # test pdf
        nbins = 3500
        self.hsig_2l2q = ROOT.TH1F('hsig_2l2q','hsig_2l2q',nbins,self.low_mass,self.high_mass)
        for ib in range(1,nbins+1):
            x = self.hsig_2l2q.GetBinCenter(ib)
            self.mass_zz2l2q.setVal(x)
            mass_set = ROOT.RooArgSet(self.mass_zz2l2q)
            #bc = self.higgspdf.getVal(mass_set)*self.BR_higgsZZTo2l2q*1000*59.83*self.sig_eff.Eval(x)
            bc = self.higgspdf.getVal(mass_set)*self.BR_higgsZZTo2l2q*1000*59.83
            if bc<0: bc = 0
            self.hsig_2l2q.SetBinContent(ib,bc)
        print("Integral of signal histogram: ", self.hsig_2l2q.Integral())
        #plot histogram
        if ifplot:
            c = ROOT.TCanvas('c','c',800,600)
            self.hsig_2l2q.Draw()
            c.Draw()
            c.SaveAs('test_histo.png')
            c.Close()

        # save histogram in root file
        #f = ROOT.TFile('test_histo.root','recreate')
        #self.hsig_2l2q.Write()
        #f.Close()   
    
    def build_sigpdf(self,ifplot=False):
        #check if self.hsig_2l2q is exist, if not, build it
        if not hasattr(self,'hsig_2l2q'):
            self.build_sighisto(ifplot)

        # create RooDataHist
        self.datahist = RooDataHist("datahist", "datahist", ROOT.RooArgList(self.mass_zz2l2q), self.hsig_2l2q)

        # create RooHistPdf
        self.sigpdf = RooHistPdf("sigpdf", "sigpdf", ROOT.RooArgSet(self.mass_zz2l2q), self.datahist)

        #check if pdf is normalised
        print("Integral of signal pdf: ", self.sigpdf.createIntegral(ROOT.RooArgSet(self.mass_zz2l2q)))

        #check value of pdf
        print("value of sigpdf: ", self.sigpdf.getVal())

        # plot RooDataHist
        if ifplot:
            frame = self.mass_zz2l2q.frame()
            self.datahist.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooDataHist of sig", 800, 600)
            frame.Draw()
            canvas.SaveAs("sig_RooDataHist.png")
        
        #plot RooHistPdf
        if ifplot:
            frame = self.mass_zz2l2q.frame()
            self.sigpdf.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooHistPdf of sig", 1000, 800)
            frame.Draw()
            canvas.SaveAs("sig_RooHistPdf.png")
        #return self.sigpdf.Clone("abc")

    def build_dcb(self,ifplot=False):
        #self.init_varables()

        f_dcb = ROOT.TFile("2l2q_resolution_resolved.root")

        # Define variables
        name = "a1_ggH_"
        self.a1_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("a1")).GetListOfFunctions().First().Eval(self.mH))
        name = "a2_ggH_"
        self.a2_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("a2")).GetListOfFunctions().First().Eval(self.mH))
        name = "n1_ggH_"
        self.n1_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("n1")).GetListOfFunctions().First().Eval(self.mH))
        name = "n2_ggH_"
        self.n2_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("n2")).GetListOfFunctions().First().Eval(self.mH))
        ##mean and sigma
        name = "mean_ggH_"
        self.mean_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("mean")).GetListOfFunctions().First().Eval(self.mH))
        self.mean_ggH.setVal(0)
        name = "sigma_ggH_"
        self.sigma_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("sigma")).GetListOfFunctions().First().Eval(self.mH))

        #build DCB
        name = "sig_dcb_"
        self.sig_dcb = ROOT.RooDoubleCB(name,name,self.mass_zz2l2q,self.mean_ggH,self.sigma_ggH,self.a1_ggH,self.n1_ggH,self.a2_ggH,self.n2_ggH)

        #check value of dcb
        print("value of sig_dcb: ", self.sig_dcb.getVal())

        #plot DCB
        if ifplot:
            frame = self.mass_zz2l2q.frame()
            self.sig_dcb.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooDoubleCB of sig", 1000, 800)
            frame.Draw()
            canvas.SaveAs("sig_RooDoubleCB.png")

    def build_conv_pdf(self,ifplot=False):
        #self.init_varables()
        # build convolution pdf
        #mass_zz2l2q = ROOT.RooRealVar("mass", "Mass", self.low_mass, self.high_mass)
        #mass_zz2l2q.setBins(10000, "cache")
        #check if self.sigpdf and self.sig_dcb 
        print("check value of sigpdf: ", self.sigpdf.getVal())
        print("check value of sig_dcb: ", self.sig_dcb.getVal())
        print("check value of mass_zz2l2q: ", self.mass_zz2l2q.getVal())
        self.sig_conv = ROOT.RooFFTConvPdf("sig_conv","sig_conv",self.mass_zz2l2q,self.sigpdf,self.sig_dcb)
        print(self.sig_conv.getVal())

        #plot convolution pdf
        if ifplot:
            frame = self.mass_zz2l2q.frame()
            self.sig_conv.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooDoubleCB of sig", 1000, 800)
            frame.Draw()
            canvas.SaveAs("sig_convolution.png")

    def build_reco_sig_hist(self,ifplot=False):
        '''
        build reco signal histogram
        '''

        f_sig = ROOT.TFile("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggh/skimed/{}".format(self.sig_mc_file))
        t_sig = f_sig.Get("passedEvents")
        w_sum = f_sig.Get("sumWeights").GetBinContent(1)

        for ievent,event in enumerate(t_sig):
            if ievent % 10000 == 0:
                print('Processing event {}'.format(ievent))
            #if not (event.Met<=150 and ((event.mass2jet>70) and (event.mass2jet<105)) and event.foundZ1LCandidate==True and event.foundZ2JCandidate==True) : continue
            #if not ((event.Met<=150) and ((event.massmerged>70) and (event.massmerged<105)) and (event.particleNetZvsQCD>0.9) and (event.foundZ1LCandidate==True) & (event.foundZ2MergedCandidata==True)) : continue
            weight = event.EventWeight*59.83*1000*event.p_Gen_CPStoBWPropRewgt/w_sum if float(self.mH)<=1000 else event.EventWeight*59.83*1000/w_sum
            #weight = event.EventWeight*59.83*1000*event.p_Gen_CPStoBWPropRewgt/w_sum

            if(event.Met<=150 and ((event.mass2jet>70) and (event.mass2jet<105)) and event.foundZ1LCandidate==True and event.foundZ2JCandidate==True):
                continue
                #self.hsig_reco.Fill(event.mass2l2jet,weight)
            elif((event.Met<=150) and ((event.massmerged>70) and (event.massmerged<105)) and (event.particleNetZvsQCD>0.9) and (event.foundZ1LCandidate==True) & (event.foundZ2MergedCandidata==True) and ((event.KD_JVBF<0.7) and (event.KD_JJVBF<0.5))):
                self.hsig_reco.Fill(event.mass2lj,weight)
            else:
                continue

            # fill histogram
            #weight = event.EventWeight*59.83*1000*event.p_Gen_CPStoBWPropRewgt/w_sum
            #weight = event.EventWeight*event.p_Gen_CPStoBWPropRewgt
            #self.hsig_reco.Fill(event.mass2lj,weight)
        
        if ifplot:
            c = ROOT.TCanvas('c','c',800,600)
            self.hsig_reco.Draw()
            c.Draw()
            c.SaveAs('test_histo_reco.png')
            c.Close()

    def build_reco_sig_pdf(self, ifplot=False):

        print("Integral of reco signal histogram: ", self.hsig_reco.Integral())

        self.roohist_sig_reco = RooDataHist("hsig_reco_pdf","hsig_reco_pdf",ROOT.RooArgList(self.mass_zz2l2q),self.hsig_reco)
        self.sigpdf_reco = RooHistPdf("sigpdf_reco","sigpdf_reco",ROOT.RooArgSet(self.mass_zz2l2q),self.roohist_sig_reco)

        if ifplot:
            frame = self.mass_zz2l2q.frame()
            self.sigpdf_reco.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooHistPdf of reco sig", 1000, 800)
            frame.Draw()
            canvas.SaveAs("sig_RooHistPdf_reco.png")
            canvas.Close()

            #plot RooDataHist
            frame = self.mass_zz2l2q.frame()
            self.roohist_sig_reco.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooDataHist of reco sig", 800, 600)
            frame.Draw()
            canvas.SaveAs("sig_RooDataHist_reco.png")

    def validate_sig_pdf(self):

        #plot sig pdf and sigpdf reco in one canvas to compare them
        canvas = ROOT.TCanvas("canvas", "canvas", 1000, 800)
        frame = self.mass_zz2l2q.frame()
        self.sigpdf.plotOn(frame, RooFit.LineColor(ROOT.kBlue))
        self.sigpdf_reco.plotOn(frame,RooFit.DrawOption("F"),RooFit.FillColor(ROOT.kOrange), RooFit.LineColor(ROOT.kOrange),RooFit.FillStyle(1001),RooFit.MarkerStyle(1))
        frame.Draw()
        #create a legend
        legend = ROOT.TLegend(0.6, 0.7, 0.85, 0.85)
        leg1 = legend.AddEntry(self.sigpdf,"Signal Model", "l"); leg1.SetLineColor(ROOT.kBlue); leg1.SetLineWidth(2)
        leg2 = legend.AddEntry(self.sigpdf_reco, "From MC", "l"); leg2.SetLineColor(ROOT.kOrange); leg2.SetLineWidth(2)
        legend.Draw()
        #set canvas
        canvas.SetGrid()
        canvas.Draw()
        canvas.SaveAs("{}/validationPDF_mH{}.png".format(self.name_dir,self.mH))

    def validate_sig_histo(self):
        '''
        plot signal histogram and reco histogram in one canvas to compare them
        '''

        #plot sig pdf and sigpdf reco in one canvas to compare them
        canvas = ROOT.TCanvas("canvas", "canvas", 1000, 800)
        self.hsig_2l2q.SetLineColor(ROOT.kRed)
        self.hsig_2l2q.SetLineWidth(2)
        self.hsig_2l2q.Draw()
        self.hsig_reco.Draw("same")
        #create a legend
        legend = ROOT.TLegend(0.6, 0.7, 0.85, 0.85)
        legend.AddEntry(self.hsig_2l2q, "Signal Model", "l")
        legend.AddEntry(self.hsig_reco, "From MC", "l")
        legend.Draw()
        #set canvas
        canvas.SetGrid()
        canvas.Draw()
        canvas.SaveAs("validationPDF_mH.png")

    def build_h125_histos_fromSample(self):
        f_h125 = ROOT.TFile("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggh/skimed/GluGluHToZZTo2L2Q_M125_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")
        t_h125 = f_h125.Get("passedEvents")
        w_sum = f_h125.Get("sumWeights").GetBinContent(1)

        #self.hsig_125 = ROOT.TH1F('h_h125','h_h125',3500,self.low_mass,self.high_mass)
        for ievent,event in enumerate(t_h125):
            if ievent % 10000 == 0:
                print('Processing event {}'.format(ievent))
            
            weight = event.EventWeight*59.83*1000*event.p_Gen_CPStoBWPropRewgt/w_sum if float(self.mH)<=1000 else event.EventWeight*59.83*1000/w_sum
            #weight = 1.0
            if(event.Met<=150 and ((event.mass2jet>70) and (event.mass2jet<105)) and event.foundZ1LCandidate==True and event.foundZ2JCandidate==True):
                #continue
                self.hsig_125.Fill(event.mass2l2jet,weight)
            elif((event.Met<=150) and ((event.massmerged>70) and (event.massmerged<105)) and (event.particleNetZvsQCD>0.9) and (event.foundZ1LCandidate==True) & (event.foundZ2MergedCandidata==True) and ((event.KD_JVBF<0.7) and (event.KD_JJVBF<0.5))):
                self.hsig_125.Fill(event.mass2lj,weight)
                #self.hsig_125.Fill(event.mass2lj,weight)

    def build_h125_histos_fromLineShape(self):
        # input spline file
        f_spline = ROOT.TFile("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/GeliangShare/public/h4l_highmass/{}_input_spline.root".format(self.production))

        # load splines
        spline = f_spline.Get("sp_xsec_{}_2e2mu".format(self.production))

        # create SplinePdf
        m_higgs = ROOT.RooRealVar("m_higgs","m_higgs",125,self.low_mass, self.high_mass)
        h125_pdf = ROOT.SplinePdf("h125pdf","h125pdf",self.mass_zz2l2q,m_higgs,self.width_higgs,spline)

        for ib in range(1,3501):
            x = self.hsig_125.GetBinCenter(ib)
            self.mass_zz2l2q.setVal(x)
            mass_set = ROOT.RooArgSet(self.mass_zz2l2q)
            #bc = h125_pdf.getVal(mass_set)*self.BR_higgsZZTo2l2q*1000*59.83*self.sig_eff.Eval(x)
            bc = h125_pdf.getVal(mass_set)*self.BR_higgsZZTo2l2q*1000*59.83
            if bc<0: bc = 0
            self.hsig_125.SetBinContent(ib,bc)

        #plot histogram
        c = ROOT.TCanvas('c','c',800,600)
        self.hsig_125.Draw()
        c.Draw()
        c.SaveAs('test_histo_h125.png')
        
    def build_interference_histos(self,ifplot=False):

        # build SM Higgs histogram for interference
        #self.build_h125_histos_fromSample()
        self.build_h125_histos_fromLineShape()

        #fphase
        f_fphase_noweight = ROOT.TFile("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/GeliangShare/public/h4l_highmass/fphase_ggH.root")
        cosfunc = f_fphase_noweight.Get("cosspline")
        sinfunc = f_fphase_noweight.Get("sinspline")

        histo_sig_h125_inter = ROOT.TH1F('histo_sig_h125_inter','histo_sig_h125_inter',3500,self.low_mass,self.high_mass)
        nbins = 3500
        for ib in range(1,nbins+1):
            x = self.hsig_2l2q.GetBinCenter(ib)
            self.mass_zz2l2q.setVal(x)
            mass_set = ROOT.RooArgSet(self.mass_zz2l2q)

            bc_sig = self.hsig_2l2q.GetBinContent(ib)
            bc_125 = self.hsig_125.GetBinContent(ib)

            # high mass signal
            a = x*x-self.mH*self.mH
            b = self.mH*self.width_bw
            cossig = a/ROOT.TMath.Sqrt(a*a+b*b)
            sinsig = b/ROOT.TMath.Sqrt(a*a+b*b)

            #SM Higgs, a = mass^2 - M(h125)^2, b = M(h125)*width
            a125 = x*x-125*125
            b125 = 125*0.00407
            cos125 = a125/ROOT.TMath.Sqrt(a125*a125+b125*b125)
            sin125 = b125/ROOT.TMath.Sqrt(a125*a125+b125*b125)

            maphase = x
            if x>3000: maphase = 3000

            cosfuncv = cosfunc.Eval(maphase)
            sinfuncv = sinfunc.Eval(maphase)
            if self.production == 'ggf':
                cosfuncv = cosfuncv/1.76*2
                sinfuncv = sinfuncv/1.76*2
            
            sig_h125_sqrt = ROOT.TMath.Sqrt(bc_sig*bc_125)

            inter_sig_h125 = 2*sig_h125_sqrt*(cos125*cossig+sin125*sinsig)

            histo_sig_h125_inter.SetBinContent(ib,inter_sig_h125)

            #debug info
            if inter_sig_h125==0 and ib<=1000:
                logger.debug("bin {} content of h125 histogram: {} when int. is Zero".format(ib,bc_125))
                logger.debug("bin {} content of hsig histogram: {} when int. is Zero".format(ib,bc_sig))

        #debug info
        logger.debug("Integral of interference histogram: {}".format(histo_sig_h125_inter.Integral()))
        

        #plot histogram
        if ifplot:
            c = ROOT.TCanvas('c','c',800,600)
            # Hide the statistics box
            #sig
            self.hsig_2l2q.SetLineColor(ROOT.kBlue); self.hsig_2l2q.SetFillColor(ROOT.kWhite)
            self.hsig_2l2q.SetStats(0)
            self.hsig_2l2q.SetMinimum(-50)
            self.hsig_2l2q.Draw()
            #interference
            histo_sig_h125_inter.SetStats(0)
            histo_sig_h125_inter.SetLineColor(ROOT.kRed); histo_sig_h125_inter.SetFillColor(ROOT.kWhite)
            histo_sig_h125_inter.Draw("same")
            #add legend
            legend = ROOT.TLegend(0.3, 0.65, 0.9, 0.85); legend.SetTextSize(0.032)
            leg1 = legend.AddEntry(histo_sig_h125_inter, "Int(Sig,H125). Sig(M={} GeV, #Gamma = {} GeV ) ".format(self.mH,self.width_bw), "l")
            leg1.SetLineColor(ROOT.kRed)
            leg2 = legend.AddEntry(self.hsig_2l2q, "Sig(M={} GeV, #Gamma = {} GeV)".format(self.mH,self.width_bw), "l")
            leg2.SetLineColor(ROOT.kBlue)
            legend.Draw()
            c.Draw()
            c.SaveAs('PlotsSignalModel/inter_sig{}_h125.png'.format(self.mH))
            c.Close()

        #save histogram in root file
        f = ROOT.TFile('PlotsSignalModel/inter_sig{}_h125.root'.format(self.mH),'recreate')
        histo_sig_h125_inter.Write()
        f.Close()

        #convert inter_sig_h125 to pdf
        roohist_inter_sig_h125 = RooDataHist("inter_sig_h125","inter_sig_h125",ROOT.RooArgList(self.mass_zz2l2q),histo_sig_h125_inter)
        sigpdf_inter_h125 = RooHistPdf("sigpdf_inter_h125","sigpdf_inter_h125",ROOT.RooArgSet(self.mass_zz2l2q),roohist_inter_sig_h125)

        #plot interference pdf
        #if ifplot:
        #    frame = self.mass_zz2l2q.frame()
        #    sigpdf_inter_h125.plotOn(frame, RooFit.LineColor(ROOT.kRed))
        #    self.sigpdf.plotOn(frame, RooFit.LineColor(ROOT.kBlue))
#
        #    # Draw the plot
        #    canvas = ROOT.TCanvas("canvas", "RooHistPdf of inter sig h125", 1000, 800)
        #    frame.Draw()
        #    canvas.SaveAs("PlotsSignalModel/interPDF_sig{}_h125.png".format(self.mH))

    def debug(self):

        print("debug sigpdf: ", self.sigpdf.getVal())
        print("debug sig_dcb: ", self.sig_dcb.getVal())

def set_log_level(log_level):
    '''
    Set log level
    '''
    if log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        logger.setLevel(logging.INFO)
    elif log_level == 'WARNING':
        logger.setLevel(logging.WARNING)
    elif log_level == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif log_level == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.INFO)

def run_sig_model(constructor):
    '''
    Run signal model
    '''
    constructor.build_sighisto(ifplot=True)
    constructor.build_sigpdf(ifplot=True)
    constructor.build_dcb(ifplot=True)
    constructor.build_conv_pdf(ifplot=True)
    constructor.build_reco_sig_hist(ifplot=True)
    constructor.build_reco_sig_pdf(ifplot=True)
    constructor.validate_sig_pdf()
    #constructor.validate_sig_histo()

#define this script as main
if __name__ == '__main__':
    # input arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--production', type=str, default='ggf', help='production mode')
    parser.add_argument('--mH','-m',default=1000,type=str,help='mass of Higgs boson')
    parser.add_argument('--width','-w',default=0.00407,type=str,help='width that you want to use for the signal')
    parser.add_argument('--log-level', '-l', default='INFO', help='log level')
    args = parser.parse_args()

    # set log level
    set_log_level(args.log_level.upper())

    if_plot = True

    # set up width according to mass, if user input width, use user input width
    if args.width == 0.00407:
        width_higgs = width_parameters[str(args.mH)]
    else:
        width_higgs = args.width

    # create object of ConstructSignal2l2q
    sig_constructor = ConstructSignal2l2q(args.mH,width_higgs)

    # build signal histogram
    #sig_constructor.build_sighisto(ifplot=if_plot)
    sig_constructor.build_sighisto_debug(ifplot=if_plot)

    # build signal pdf
    sig_constructor.build_sigpdf(ifplot=if_plot)

    # build resolution function
    sig_constructor.build_dcb(ifplot=if_plot)

    #sig_constructor.debug()

    # build convolution pdf
    sig_constructor.build_conv_pdf(ifplot=if_plot)

    # build reco signal histogram
    sig_constructor.build_reco_sig_hist(ifplot=if_plot)

    # build reco signal pdf
    sig_constructor.build_reco_sig_pdf(ifplot = if_plot)

    # validate signal pdf
    sig_constructor.validate_sig_pdf()

    #validate signal histogram
    sig_constructor.validate_sig_histo()

    ## interference
    sig_constructor.build_interference_histos(ifplot=True)


