import os
import sys
import Analyzer_Configs as AC
from ROOT import *

class Plot_Config:
    def __init__(self, ana_cfg):
        self.ana_cfg = ana_cfg
    	self.colors  = {}
    	self.logY    = True
    	self.lumi    = '59.7'
        #self.lumi    = '35.9'
    	self.sig_scale  = 50
	self.LoadColors()

    def LoadColors(self):
        self.colors["Data"] = kBlack
        self.colors["ggH"] = kRed
        self.colors["VBF"] = kOrange + 7
        self.colors["ZH"] =  kBlue + 1
        self.colors["WH"] =  kGreen + 2
        self.colors["ttH"]  = kPink + 6
        self.colors["DY"]  = kGreen + 1
        self.colors["ZX"] = kGreen + 3
        self.colors["GluGluHToZZTo4L"]  = kRed-7
        self.colors["VBF_HToZZTo4L"]  = kRed-7
        self.colors["WminusH_HToZZTo4L"]  = kRed-7
        self.colors["WplusH_HToZZTo4L"]  = kRed-7
        self.colors["ZH_HToZZ_4L"]  = kRed-7
        self.colors["ttH_HToZZ"]  = kRed-7
        self.colors["bbH_HToZZTo4L"] = kRed - 7
        self.colors["GluGluToContinToZZTo2e2mu"]  = kAzure -1
        self.colors["GluGluToContinToZZTo2e2tau"]  = kAzure -1
        self.colors["GluGluToContinToZZTo2mu2tau"]  = kAzure -1
        self.colors["GluGluToContinToZZTo4e"]  = kAzure -1
        self.colors["GluGluToContinToZZTo4mu"]  = kAzure -1
        self.colors["GluGluToContinToZZTo4tau"]  = kAzure -1
        self.colors["ZZTo4L"] = kAzure +6

	# trying to use blue for Z, green for W, yellow for top, red for g/q
        self.colors["ZJets"]  =  kGreen + 1
	self.colors["tt_ll"] = kYellow - 9
	self.colors["TT"]  = kBlue + 1
	self.colors["WW"] =  kSpring -1
        self.colors["WZ"] =  kMagenta -4
	self.colors["qqZZ"] =  kCyan - 7
	self.colors["ggZZ"] = kViolet - 9
        self.colors["ttV"] = kOrange - 9
        self.colors["tZq"] = kRed - 7
        self.colors["VVV"] = kPink + 6


    def SetHistStyles(self, hist, sample,cat_name):
        if sample == 'data':
    	    hist.SetMarkerStyle(20)
            hist.SetLineColor(kBlack)
            hist.GetXaxis().SetTitle('m_{%s}'%cat_name)
            #hist.GetXaxis().SetTitleSize(0.20)
            hist.GetYaxis().SetTitle('Events / %d GeV' %hist.GetBinWidth(1))
            #hist.GetYaxis().SetTitleSize(0.20)
    	elif sample in self.ana_cfg.sig_names:
    	    #hist.SetLineColor(self.colors[sample])
    	    hist.SetFillColor(self.colors[sample])
    	elif sample in self.ana_cfg.bkg_names:
            #hist.SetLineColor(self.colors[sample])
    	    hist.SetFillColor(self.colors[sample])
