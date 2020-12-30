import os
import sys
from ROOT import *


class Analyzer_Config:
    def __init__(self, channel):
        #self.year = years
	self.channel    = channel
	self.sample_loc = 'NONE'
	self.sig_names  = []
	self.bkg_names  = []
 	self.samp_names = []

	self.Config_Analyzer()

    def Config_Analyzer(self):
        if self.channel == 'inclusive' or self.channel == 'ggH' or self.channel == 'VBF' or self.channel == 'WH_3l' or self.channel == 'ZH_4l' or self.channel == 'ttH_lep':
    	    self.sample_loc = '/cms/user/guojl/Sample/skimed'
            #self.sample_loc = '/cms/user/guojl/Sample'
    	    self.sig_names  = ['GluGluHToZZTo4L','VBF_HToZZTo4L','WminusH_HToZZTo4L','WplusH_HToZZTo4L','ZH_HToZZ_4L','ttH_HToZZ','bbH_HToZZTo4L']
    	    #self.bkg_names  = ['qqZZ','WZ','TT','DY']
            self.bkg_names  = ['ZX','GluGluToContinToZZTo2e2mu','GluGluToContinToZZTo2e2tau','GluGluToContinToZZTo2mu2tau','GluGluToContinToZZTo4e','GluGluToContinToZZTo4mu','GluGluToContinToZZTo4tau','ZZTo4L']
    	    self.samp_names = self.bkg_names + self.sig_names + ['data']
    	else:
    	    print "channel is invalid: channel = %s" %self.channel
    	    sys.exit()

    def Print_Config(self):
        print 'Running analysis in channel: %s' %self.channel
    	print 'getting ntuples from: %s' %self.sample_loc
    	print 'using signals: '
    	print self.sig_names
    	print 'using backgrounds:'
    	print self.bkg_names
