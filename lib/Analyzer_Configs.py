import os
import sys
from ROOT import *


class Analyzer_Config:
    def __init__(self, channel):
	self.channel    = channel
	self.sample_loc = 'NONE'
	self.sig_names  = []
	self.bkg_names  = []
 	self.samp_names = []

	self.Config_Analyzer()

    def Config_Analyzer(self):
        if self.channel == 'inclusive' or self.channel == 'ggH' or self.channel == 'VBF' or self.channel == 'WH_3l' or self.channel == 'ZH_4l' or self.channel == 'ttH_lep':
    	    self.sample_loc = '/cms/user/guojl/Sample'
    	    self.sig_names  = []
    	    self.bkg_names  = ['DY','WZ','TT','qqZZ']
    	    self.samp_names = self.bkg_names + ['data']
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
