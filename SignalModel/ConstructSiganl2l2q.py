import ROOT
from ROOT import RooRealVar, RooHistPdf, RooDataHist, RooArgSet, TCanvas, RooFit, RooAbsPdf, TSpline3
# load C++ library
ROOT.gInterpreter.ProcessLine('#include "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/SplinePdf.h"')

class ConstructSignal2l2q:
    def __init__(self,production='ggf'):
        self.low_mass = 0
        self.high_mass = 3500
        self.mH = 1000
        self.width_bw = 700
        self.production = production

        self.build_RooRealvar()
        self.build_splinepdf()

    def build_RooRealvar(self):
        self.mass_zz2l2q = ROOT.RooRealVar("mass", "Mass", self.low_mass, self.high_mass)
        self.mean = ROOT.RooRealVar("mean", "Mean", self.mH,self.low_mass, self.high_mass)
        self.width = ROOT.RooRealVar("width", "Width", self.width_bw,0,100)

    def build_splinepdf(self):
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

    def build_sighisto(self,ifplot=False):
        '''
        build signal pdf
        '''
        # test pdf
        nbins = 3500
        self.hsig_2l2q = ROOT.TH1F('hsig_2l2q','hsig_2l2q',2*nbins,self.low_mass,self.high_mass)
        for ib in range(1,2*nbins+1):
            x = self.hsig_2l2q.GetBinCenter(ib)
            self.mass_zz2l2q.setVal(x)
            if(((x<self.mH-3*self.width_bw) & (x<self.mH-0.5*0.5)) | ((x>self.mH+3*self.width_bw) & (x>self.mH+0.5*0.5)) | (self.width_bw>10*0.5)):
                bc = self.higgspdf.getVal()
                bc_range = self.higgspdf.getValV()*0.5
            else:
                bc = 0
                bc_range = 0
                for j in range(-500,500):
                    xx = self.mH + j*0.02*self.width_bw
                    if(xx>x-0.5*0.5 & xx<=x+0.5*0.5):
                        self.mass_zz2l2q.setVal(xx)
                        bc += self.higgspdf.getVal()
                        bc_range += self.higgspdf.getValV()*0.02*self.width_bw
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
    
    def build_sigpdf(self,ifplot=False):
        #check if self.hsig_2l2q is exist, if not, build it
        if not hasattr(self,'hsig_2l2q'):
            self.build_sighisto(ifplot)
        
        nbins = 2*self.high_mass
        self.mass_zz2l2q.setBins(nbins)

        # create RooDataHist
        datahist = RooDataHist("datahist", "datahist", ROOT.RooArgList(self.mass_zz2l2q), self.hsig_2l2q)

        # create RooHistPdf
        self.sigpdf = RooHistPdf("sigpdf", "sigpdf", ROOT.RooArgSet(self.mass_zz2l2q), datahist)

        #check if pdf is normalised
        print("Integral of signal pdf: ", self.sigpdf.createIntegral(ROOT.RooArgSet(self.mass_zz2l2q)))

        # plot RooDataHist
        if ifplot:
            frame = self.mass_zz2l2q.frame()
            datahist.plotOn(frame)

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

    def build_dcb(self,ifplot=False):

        f_dcb = ROOT.TFile("2l2q_resolution_resolved.root")

        # Define variables
        name = "a1_ggH_"
        a1_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("a1")).GetListOfFunctions().First().Eval(self.mH))
        name = "a2_ggH_"
        a2_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("a2")).GetListOfFunctions().First().Eval(self.mH))
        name = "n1_ggH_"
        n1_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("n1")).GetListOfFunctions().First().Eval(self.mH))
        name = "n2_ggH_"
        n2_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("n2")).GetListOfFunctions().First().Eval(self.mH))
        ##mean and sigma
        name = "mean_ggH_"
        mean_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("mean")).GetListOfFunctions().First().Eval(self.mH))
        #mean_ggH.setVal(0)
        name = "sigma_ggH_"
        sigma_ggH = ROOT.RooRealVar(name,name, (f_dcb.Get("sigma")).GetListOfFunctions().First().Eval(self.mH))

        #build DCB
        name = "sig_dcb_"
        self.sig_dcb = ROOT.RooDoubleCB(name,name,self.mass_zz2l2q,mean_ggH,sigma_ggH,a1_ggH,n1_ggH,a2_ggH,n2_ggH)

        #plot DCB
        if ifplot:
            frame = self.mass_zz2l2q.frame()
            self.sig_dcb.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooDoubleCB of sig", 1000, 800)
            frame.Draw()
            canvas.SaveAs("sig_RooDoubleCB.png")

    def buid_conv_pdf(self,ifplot=False):
        # build convolution pdf
        self.sig_conv = ROOT.RooFFTConvPdf("sig_conv","sig_conv",self.mass_zz2l2q,self.sigpdf,self.sig_dcb,2)
        print(self.sig_conv)

        #plot convolution pdf
        if ifplot:
            frame = self.mass_zz2l2q.frame()
            self.sig_conv.plotOn(frame)

            # Draw the plot
            canvas = ROOT.TCanvas("canvas", "RooDoubleCB of sig", 1000, 800)
            frame.Draw()
            canvas.SaveAs("sig_convolution.png")


#define this script as main
if __name__ == '__main__':
    # create object of ConstructSignal2l2q
    sig_constructor = ConstructSignal2l2q()

    # build signal histogram
    #sig_constructor.build_sigpdf(ifplot=True)
    sig_constructor.build_sighisto(ifplot=False)

    # build signal pdf
    #sig_constructor.build_sigpdf(ifplot=True)
    sig_constructor.build_sigpdf(ifplot=False)

    # build resolution function
    #sig_constructor.build_dcb(ifplot=True)
    sig_constructor.build_dcb(ifplot=True)

    # build convolution pdf
    sig_constructor.buid_conv_pdf(ifplot=True)


