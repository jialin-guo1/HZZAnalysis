import os
import sys
import Analyzer_Configs as AC
from ROOT import *

class Plot_Config:

    def __init__(self, ana_cfg):
	self.ana_cfg = ana_cfg
	self.colors  = {}
	self.logY    = True
	self.lumi    = '35.9'
	self.sig_scale  = 50

	self.LoadColors()

    def LoadColors(self):
	self.colors["Data"] = kBlack

        self.colors["ggH"] = kRed
        self.colors["VBF"] = kOrange + 7
        self.colors["ZH"] =  kBlue + 1
        self.colors["WH"] =  kGreen + 2
        self.colors["ttH"]  = kPink + 6

	# trying to use blue for Z, green for W, yellow for top, red for g/q
        self.colors["ZJets"]  =  kGreen + 1
	    self.colors["tt_ll"] = kYellow - 9
	    self.colors["tX"]  = kOrange + 6
	    self.colors["WW"] =  kSpring -1
        self.colors["WZ"] =  kGreen - 9
	    self.colors["ZZ"] =  kCyan - 7
	    self.colors["ggZZ"] = kViolet - 9
        self.colors["ttV"] = kOrange - 9
        self.colors["tZq"] = kRed - 7
        self.colors["VVV"] = kPink + 6

    # def LoadColors(self):


    def SetHistStyles(self, hist, sample):
	if sample == 'data':
	    hist.SetMarkerStyle(20)
	elif sample in self.ana_cfg.sig_names:
	    hist.SetLineColor(self.colors[sample])
	    hist.SetLineWidth(2)
	    hist.SetFillColor(kGray)
	elif sample in self.ana_cfg.bkg_names:
	    hist.SetFillColor(self.colors[sample])
