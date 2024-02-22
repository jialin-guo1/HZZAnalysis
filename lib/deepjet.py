import numpy as np
import os 
import correctionlib
import yaml

class DeepJet:
    def __init__(self,year,array,config = None,WP = 'M'):
        self.year = year
        self.array = array
        self.WP = WP
        self.file_sf_path = f"/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/deepjetSFsfiles/{year}/btagging.json.gz"
        self.file_sf = correctionlib.CorrectionSet.from_file(self.file_sf_path)

        self.bcjet_sf_name = 'deepJet_comb'
        self.lightjet_sf_name = 'deepJet_incl'



        if config == None:
            with open(f"/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL{self.year}.yml") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = config

    def get_deepjet_sf(self,type):
        r"""
            Get the deepjet SF for each jet in the array.
            SF is separated by jet flavor, pt, abs(eta), and WP.

            input:
            type: related to the uncertainty type, such as "central", "up", "down".

            output:
            sf_jet1: the deepjet SF for jet 1 in the array.
            sf_jet2: the deepjet SF for jet 2 in the array.
        """
        # Get the SF for each jet in the array for jet 1 and jet 2.
        #jet 1
        #bcjet
        sf_jet1_bcjet = self.file_sf[self.bcjet_sf_name].evaluate(
            f"{type}",
            f"{self.WP}",
            self.array.jet_1_hadronflavor[self.array.jet_1_hadronflavor != 0],
            abs(self.array.jet_1_eta[self.array.jet_1_hadronflavor != 0]),
            self.array.jet_1_pt[self.array.jet_1_hadronflavor != 0],
            )
        #lightjet
        sf_jet1_lightjet = self.file_sf[self.lightjet_sf_name].evaluate(
            f"{type}",
            f"{self.WP}",
            self.array.jet_1_hadronflavor[self.array.jet_1_hadronflavor == 0],
            abs(self.array.jet_1_eta[self.array.jet_1_hadronflavor == 0]),
            self.array.jet_1_pt[self.array.jet_1_hadronflavor == 0],
            )
        #combine
        sf_jet1 = np.append(sf_jet1_bcjet,sf_jet1_lightjet)

        #jet 2
        #bcjet
        sf_jet2_bcjet = self.file_sf[self.bcjet_sf_name].evaluate(
            f"{type}",
            f"{self.WP}",
            self.array.jet_2_hadronflavor[self.array.jet_2_hadronflavor != 0],
            abs(self.array.jet_2_eta[self.array.jet_2_hadronflavor != 0]),
            self.array.jet_2_pt[self.array.jet_2_hadronflavor != 0],
            )
        #lightjet
        sf_jet2_lightjet = self.file_sf[self.lightjet_sf_name].evaluate(
            f"{type}",
            f"{self.WP}",
            self.array.jet_2_hadronflavor[self.array.jet_2_hadronflavor == 0],
            abs(self.array.jet_2_eta[self.array.jet_2_hadronflavor == 0]),
            self.array.jet_2_pt[self.array.jet_2_hadronflavor == 0],
            )
        #combine
        sf_jet2 = np.append(sf_jet2_bcjet,sf_jet2_lightjet)

        return sf_jet1,sf_jet2

        