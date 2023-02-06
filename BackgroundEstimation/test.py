import uproot 
import hist
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward as ak
import pandas as pd
import numpy as np
import seaborn as sns

import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

import ROOT

class GetROOTHisto(setting):
    def __init__(self,year: str, cutcat: str) -> None:
        '''input: lep, resolved merged_notag or merged_tag or all'''
        super().__init__() #attribute from setting

        self.year = year
        self.cutcat = cutcat
        self.hist = {}
        self.inputrootfile = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root'

        #self.file = ROOT.TFile.Open(self.inputrootfile,'READ')
        self.file = None

        self.massZZvarb = {
            'resolved':'mass2l2jet_rebin',
            'merged_tag':'mass2lj_rebin'
        }

        use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
        if use_helvet:
            CMShelvet = hep.style.CMS
            CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
            plt.style.use(CMShelvet)
        else:
            plt.style.use(hep.style.CMS)

        #if self.cutcat == 'lep':
        #    self.hist['lep'] = self.getlepthisto()
        #elif self.cutcat=='resolved':
        #    self.hist['resolved'] = {}
        #    for sample in self.fileset[self.year].keys():
        #        for reg in self.regions:
        #            for cat in self.leptonic_cut_cats:
        #                for tag in self.tags:
        #                    for varb in self.config['bininfo'].keys():
        #                        if varb == 'mass2l2jet':
        #                            #h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin'].to_boost()
        #                            #h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin']
        #                            self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin']
        #                            if self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin']==None:
        #                                print("error can not get histo")
        #                            #if f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'] and reg=='SR':
        #                            #temphitoname = f'DY/resolved/{reg}/{cat}/{tag}/massZZ'
        #                            #if reg=='SR' and (temphitoname in f.keys()):
        #                                #h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'].to_boost()
        #                            #    h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f.Get(f'DY/resolved/{reg}/{cat}/{tag}/massZZ')#[f'DY/resolved/{reg}/{cat}/{tag}/massZZ']
        #                        #h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_boost()
        #                        #h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}']
        #                        self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}']
        #    #print(self.hist['resolved'])
        #    #print('1')
        #######################################################################
        #self.GetRootHisto()
        #self.AlphaProduce()
        self.AlphaPlot()
    def GetRootHisto(self):
        self.file = ROOT.TFile.Open(self.inputrootfile,'READ')

        if self.cutcat == 'lep':
            self.hist['lep'] = self.getlepthisto()
        elif self.cutcat=='resolved':
            self.hist['resolved'] = {}
            for sample in self.fileset[self.year].keys():
                for reg in self.regions:
                    for cat in self.leptonic_cut_cats:
                        for tag in self.tags:
                            for varb in self.config['bininfo'].keys():
                                if varb == 'mass2l2jet':
                                    #h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin'].to_boost()
                                    #h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin']
                                    self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin']
                                    if self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin']==None:
                                        print("error can not get histo")
                                    #if f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'] and reg=='SR':
                                    #temphitoname = f'DY/resolved/{reg}/{cat}/{tag}/massZZ'
                                    #if reg=='SR' and (temphitoname in f.keys()):
                                        #h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'].to_boost()
                                    #    h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f.Get(f'DY/resolved/{reg}/{cat}/{tag}/massZZ')#[f'DY/resolved/{reg}/{cat}/{tag}/massZZ']
                                #h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_boost()
                                #h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}']
                                self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}']

    def AlphaProduce(self):
        #for cutcat in self.cutcats:
        #with uproot.recreate(f"{self.outAlphafilepath}/AlphaHisto_{self.year}.root") as fout:
        with uproot.recreate(f"./AlphaHistoTEST_{self.year}.root") as fout:
            #AlphaBranch = {}
            for cat in self.leptonic_cut_cats:
                for tag in self.tags:
                    #c = ROOT.TCanvas(f'alhpa_{cat}_{tag}',f'alhpa_{cat}_{tag}',600,600)
                    hist_DY_CR = self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}']
                    hist_DY_CR.Sumw2()
                    #hist_DY_CR.Add(self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_CR.Add(self.hist[self.cutcat][f'DY_pt100To250_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_CR.Add(self.hist[self.cutcat][f'DY_pt250To400_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_CR.Add(self.hist[self.cutcat][f'DY_pt400To650_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_CR.Add(self.hist[self.cutcat][f'DY_pt650ToInf_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])

                    hist_DY_SR = self.hist[self.cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'] 
                    hist_DY_SR.Sumw2()
                    hist_DY_SR.Add(self.hist[self.cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_SR.Add(self.hist[self.cutcat][f'DY_pt100To250_SR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_SR.Add(self.hist[self.cutcat][f'DY_pt250To400_SR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_SR.Add(self.hist[self.cutcat][f'DY_pt400To650_SR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_SR.Add(self.hist[self.cutcat][f'DY_pt650ToInf_SR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])

                    hist_DY_SR.Divide(hist_DY_CR)

                    fout[f'{cutcat}_{cat}_{tag}'] = hist_DY_SR

                    #f, ax = plt.subplots(figsize=(10, 10))
                    #hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %self.config['lumi'][self.year], fontname='sans-serif')
                    #hep.histplot(hist_DY_SR,label = 'Alhpa Ratio')
                    #ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
                    #ax.set_ylabel('Ratio', ha='right', y=1.0)
                    #plt.savefig(f'./alhpa_{cat}_{tag}_test.png')
                    #hist_DY_SR.Draw()
                    #c.SaveAs(f'./alhpa_{cat}_{tag}_test.png')

    def AlphaPlot(self):
        x_axis = np.append(self.massZZ_low_bins,self.massZZ_high_bins)
        #with uproot.open(f"./AlphaHistoTEST_{self.year}.root") as file:
        file = ROOT.TFile(f"./AlphaHistoTEST_{self.year}.root","READ")
        self.leptonic_cut_cats = ['2lep']
        for cat in self.leptonic_cut_cats:
            for tag in self.tags:
                #h = file[f'{cutcat}_{cat}_{tag}'].to_hist()
                h = file.Get(f'{cutcat}_{cat}_{tag}')
                #h_content = h.view(flow=False).value
                #h_err = np.sqrt(h_content)
                #print(f'{tag} {h_err}')
                #plot
                x_pos = []
                y_val = []
                x_err = []
                y_err = []
                f, ax = plt.subplots(figsize=(10, 10))
                hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %self.config['lumi'][self.year], fontname='sans-serif')
                #hep.histplot(h,label = 'Alhpa Ratio',histtype='errorbar', color='k', markersize=15, elinewidth=1.5)
                for i in range(0,len(x_axis)-1):
                    x = (x_axis[i]+x_axis[i+1])/2
                    x_pos.append(x)
                    #y = h_content[i]
                    y = h.GetBinContent(i)
                    y_val.append(y)
                    xerr = (x_axis[i+1]-x_axis[i])/2
                    x_err.append(xerr)
                    #yerr = h_err[i]
                    yerr = h.GetBinError(i)
                    y_err.append(yerr)
                    ax.plot(x,y,'o', markersize=2 ,color='black')
                print(f'{tag} {y_err}')
                ax.errorbar(x_pos,y_val,xerr=x_err,yerr=y_err,elinewidth = 1.0,linestyle='none',color='black',label = 'Alpha Ratio')
                ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
                ax.set_ylabel('Ratio', ha='right', y=1.0)
                if tag == 'untag':
                    ax.set_ylim(-0.5, 1.0)
                else:
                    ax.set_ylim(-0.5, 1.5)
                ax.text(0.05, 0.92, f'{self.text[cat]}', transform=ax.transAxes, fontweight='bold')
                ax.legend(loc='upper right') 
                plt.savefig(f'./alhpa_{cat}_{tag}_test.png')
                #plt.close()
    #def AlphaApply(self):

if __name__=='__main__':
    cutcat = 'resolved'
    year = '2016'
    GetROOTHisto(year,cutcat)