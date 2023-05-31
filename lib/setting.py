import yaml
import numpy as np
import boost_histogram as bh
import awkward as ak

class setting():
    def __init__(self) -> None:
        #config
        self.config_path = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL16.yml"
        with open( self.config_path) as f:
            self.config = yaml.safe_load(f)
        #globale parameter
        #self.leptonic_cut_cats=['isEE','isMuMu','2lep']
        self.leptonic_cut_cats=['2lep']
        #self.regions = ['CR','SR','ALL','LSB','HSB','SB','VR']
        #self.regions = ['SB','VR']
        #self.regions = ['LSB','HSB']
        self.regions = ['CR']
        #self.tags = ['btag','untag','vbftag','all']
        self.tags = ['all']
        self.text = {
        'isEE':'twoEle',
        'isMuMu':'twoMuon',
        '2lep':'2lep'
        }

        #samples list
        self.sample_list = ['DY_pt50To100','DY_pt100To250','DY_pt250To400','DY_pt400To650','DY_pt650ToInf','TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L','Data']

        #self.plot_store_dir_name = 'plots' 
        self.plot_store_dir_name = 'plotsMay15' 
        #self.plot_store_dir_name = 'plotnew' 

        self.massZZ_low_bins = np.linspace(0,1700,35)
        #massZZ_high_bins = np.array([2000,3500])
        self.massZZ_high_bins = np.array([2000,4000])
        #self.massZZ_bins = bh.axis.Variable(ak.from_numpy(np.append(self.massZZ_low_bins,self.massZZ_high_bins)).to_list())
        self.massZZstr = {'resolved':'mass2l2jet','merged':'mass2lj','merged_tag':'mass2lj'}

        #creat massZ bins for merged and resolved category sperately
        self.massZZ_bins = {}
        #merged
        temp_bin1 = np.linspace(500,1000,11)
        temp_bin2 = np.array([1100,1200,1400,1600,2000,2400,3000,3500])
        bin = np.concatenate((temp_bin1,temp_bin2))
        self.massZZ_bins['merged'] = bh.axis.Variable(ak.from_numpy(bin).to_list())
        self.massZZ_bins['merged_tag'] = bh.axis.Variable(ak.from_numpy(bin).to_list())
        #resolved
        temp_bin1 = np.linspace(500,1200,15)
        temp_bin2 = np.array([1300,1400,1500,1600,2000,2400,3000,3500])
        bin = np.concatenate((temp_bin1,temp_bin2))
        self.massZZ_bins['resolved'] = bh.axis.Variable(ak.from_numpy(bin).to_list())

        self.massList = []
        for mass in range(400,1000,50):
            self.massList.append(mass)
        for mass in range(1000,1600,100):
            self.massList.append(mass)
        for mass in range(1600,3200,200):
            self.massList.append(mass)
        
        #self.massList = [500]

        self.sigfileset = {}
        self.fileset = {}
        self.filepath = '/cms/user/guojl/Sample/2L2Q/UL_Legacy'
        for year in ['2016','2016preAPV','2016postAPV','2017','2018','2018new']:
            self.fileset[year] = {
                'DY_pt50To100':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt50To100.root'],
                'DY_pt100To250':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt100To250.root'],
                'DY_pt250To400':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt250To400.root'],
                'DY_pt400To650':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt400To650.root'],
                'DY_pt650ToInf':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt650ToInf.root'],
                #'TTJets':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/TTJets.root'],
                'TTTo2L2Nu':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/skimed/TTTo2L2Nu.root'],
                #'WW_TuneCP5':'MC/WW_TuneCP5_13TeV-pythia8',
                'WWTo2L2Nu':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/skimed/WWTo2L2Nu.root'],
                'WZTo2Q2L':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/WZTo2Q2L.root'],
                'ZZTo2Q2L':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/ZZTo2Q2L.root'],
                'ggh':[f'{self.filepath}/{year}/MC/ggh/skimed/ggh.root'],
                'vbf':[f'{self.filepath}/{year}/MC/vbf/skimed/vbf.root'],
                'sig':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/sig/skimed/sig.root'],
                #'ggh1000':[f'{self.filepath}/{year}/MC/ggh1000/skimed/ggh1000.root'],
                #'ggh500':[f'{self.filepath}/{year}/MC/ggh500/skimed/ggh500.root'],
                #'ggh3000':[f'{self.filepath}/{year}/MC/ggh3000/skimed/ggh3000.root'],
                #'vbf1000':[f'{self.filepath}/{year}/MC/vbf1000/skimed/vbf1000.root'],
                #'ZH_HToBB':[f'{self.filepath}/{year}/MC/ZH_HToBB_ZToLL_M-125_TuneCP5_13TeV-powheg-pythia8/skimed/ZH_HToBB_ZToLL.root'],
                'Data':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/Data/skimed/Data{year}UL_noDuplicates.root'], 
            }
            self.sigfileset[year] = {
                'ggh125':[f'{self.filepath}/{year}/MC/ggh/skimed/GluGluHToZZTo2L2Q_M125_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh500':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh600':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M600_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh700':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M700_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v2_0.root'],
                'ggh800':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M800_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh900':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M900_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh1000':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M1000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh1500':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M1500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v2_0.root'],
                'ggh2000':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M2000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh2500':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M2500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'ggh3000':[f'{self.filepath}/{year}/MC/sig/skimed/GluGluHToZZTo2L2Q_M3000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root'],
                'sig':[f'{self.filepath}/{year}/MC/sig/skimed/sig.root'],
            }