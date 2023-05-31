import hist 
import uproot
import sys,os
import math
import mplhep as hep
import seaborn as sns
import matplotlib.pyplot as plt
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

class FinalSigScan(setting):
    def __init__(self,year,cutcat) -> None:
        super().__init__() #attribute from setting
        self.year = year
        self.cutcat = cutcat

        #self.massList = setting().massList

        #self.hist = {}
        #self.input_hist[cutcat] = GetHisto(self.year,cutcat).hist

        self.cat = '2lep'
        self.tag = 'all'
        self.reg = 'SR'

        self.inbkgfile = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root'
        self.insigfile = uproot.open(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/Histos_sig_{self.year}.root')
        
        self.hist = None
        self.hist_bkg = None
        self.hist_sig = None

        use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
        if use_helvet:
            CMShelvet = hep.style.CMS
            CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
            plt.style.use(CMShelvet)
        else:
            plt.style.use(hep.style.CMS)
        
        #setMcDataPlotsColor
        color_order_bkg = sns.color_palette('Accent', 3)
        color_order_bkg.reverse()
        self.set_sns_color(color_order_bkg)

    def set_sns_color(self,*args):
        sns.palplot(sns.color_palette(*args))
        sns.set_palette(*args)
        pass

    def ComputSignificant(self,hist):
        #print(self.hist.keys())
        varb = 'mass2l2jet_rebin'
        #add TTbar and vz
        #samplelist = ['TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L']
        #with uproot.open(self.inbkgfile) as file:
        #    for sample in samplelist:
        #        print(f'[INFO] Add {sample}')
        #        self.hist_bkg += file[f'{sample}/resolved/{self.reg}/{self.cat}/{self.tag}/{varb}'].to_hist()
        #    #add DY
        #    sample = 'DY'
        #    varb = 'massZZ'
        #    self.hist_bkg += file[f'{sample}_resolved_{self.reg}_{self.cat}_{self.tag}_{varb}'].to_hist()
#
        #bkgtot = self.hist_bkg.values().sam()
        samplelist = ['TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L']
        for sample in samplelist:
            print(f'[INFO] Add {sample}')
            if(self.hist_bkg == None): 
                self.hist_bkg = hist[self.cutcat][f'{sample}_{self.reg}_{self.cat}_{self.tag}_{varb}']
            else:
                self.hist_bkg += hist[self.cutcat][f'{sample}_{self.reg}_{self.cat}_{self.tag}_{varb}']
        self.hist_bkg += hist[self.cutcat][f'DY_{self.reg}_{self.cat}_{self.tag}_massZZ']
        bkgtot = self.hist_bkg.values().sam()
        #each sig mass opint
        y = []
        for mass in self.massList:
            self.hist_sig = self.insigfile[f'sig{mass}_resolved']
            sigtot = self.hist_sig.values().sam()

            #compute
            significant = sigtot/math.sqrt(sigtot+bkgtot)
            y.append(significant)
        f, ax = plt.subplots(figsize=(10, 10))
        hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %self.config['lumi'][self.year], fontname='sans-serif')
        ax.plot(self.massList,'ro:',label = 'significant', linewidth = 1,markersize=1)
        ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
        ax.set_ylabel('Ratio', ha='right', y=1.0)
        ax.legend(loc='upper right') 
        plt.savefig(f'../significant_resolved.png')
        plt.close()

    def run(self):
        hist = GetHisto(self.year,self.cutcat).hist
        print(hist.keys())
        self.ComputSignificant(hist)
        



