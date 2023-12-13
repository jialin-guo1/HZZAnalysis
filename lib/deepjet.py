import numpy as np
import os 
import correctionlib
import yaml

class DeepJet:
    def __init__(self,year,array,config = None,WP = 'M'):
        self.year = year
        self.array = array
        self.WP = WP

        if config == None:
            with open(f"/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL{self.year}.yml") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = config

    def get_deepjet_sf(self):
        