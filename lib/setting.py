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
        self.leptonic_cut_cats=['isEE','isMuMu','2lep']
        self.regions = ['CR','SR']
        self.tags = ['btag','untag','vbftag','all']
        self.text = {
        'isEE':'twoEle',
        'isMuMu':'twoMuon',
        '2lep':'2lep'
        }

        self.massZZ_low_bins = np.linspace(500,1700,11)
        #massZZ_high_bins = np.array([2000,3500])
        self.massZZ_high_bins = np.array([2000,4000])
        self.massZZ_bins = bh.axis.Variable(ak.from_numpy(np.append(self.massZZ_low_bins,self.massZZ_high_bins)).to_list())

        self.fileset = {}
        self.filepath = '/cms/user/guojl/Sample/2L2Q/UL_Legacy'
        for year in ['2016','2017','2018','2018new']:
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
                #'ggh':[f'{self.filepath}/{year}/MC/ggh/skimed/gghAll.root'],
                #'vbf':[f'{self.filepath}/{year}/MC/vbf/skimed/vbfAll.root'],
                'sig':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy//{year}/MC/sig/skimed/sig.root'],
                'Data':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/Data/skimed/Data{year}UL_noDuplicates.root'], 
            }
            #self.fileset[year] = {
            #    'DY_pt50To100':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_Pt-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt50To100.root'],
            #    'DY_pt100To250':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_Pt-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt100To250.root'],
            #    'DY_pt250To400':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_Pt-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt250To400.root'],
            #    'DY_pt400To650':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_Pt-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt400To650.root'],
            #    'DY_pt650ToInf':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/DYJetsToLL_Pt-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/DY_pt650ToInf.root'],
            #    'TTJets':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/TTJets.root'],
            #    #'TTTo2L2Nu':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/skimed/TTTo2L2Nu.root'],
            #    #'WW_TuneCP5':'MC/WW_TuneCP5_13TeV-pythia8',
            #    'WWTo2L2Nu':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/skimed/WWTo2L2Nu.root'],
            #    'WZTo2Q2L':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/WZTo2Q2L.root'],
            #    'ZZTo2Q2L':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8/skimed/ZZTo2Q2L.root'],
            #    #'ggh':[f'{self.filepath}/{year}/MC/ggh/skimed/gghAll.root'],
            #    #'vbf':[f'{self.filepath}/{year}/MC/vbf/skimed/vbfAll.root'],
            #    'Data':[f'/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/Data/skimed/Data{year}UL_noDuplicates.root'], 
            #}