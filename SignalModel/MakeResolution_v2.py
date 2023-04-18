import awkward as ak
import hist
import uproot
import sys
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from setting import setting

class MakeResolution():
    def __init__(self,config = None,year = None,fileset = None):
        self.config = config
        self.year = year
        self.fileset = fileset
        self.sumWeight = 0.0
        self.leptonic_cut_cats='2lep'
        self.regions = 'SR'
        self.tags = 'all'
        self.massZZ_bins = setting().massZZ_bins
        self.gen_higss_str = 'GEN_H1_mass'
        self.varb = {'resolved':'mass2l2jet','merged':'mass2lj'}