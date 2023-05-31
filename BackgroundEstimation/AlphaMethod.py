import uproot 
import boost_histogram as bh
import awkward as ak
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import numpy as np
import seaborn as sns

import ROOT

#===========================================load self.config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

class AlphaMethodUnit(setting):
    def __init__(self,year) -> None:
        super().__init__() #attribute from setting
        self.debug = True
        self.useuproot = False
        self.year = year
        self.alphaCR = 'SB'
        self.alphaSR = 'VR'
        self.alphafilestr = 'Validation'
        self.regions = self.regions+['VR','SB']
        self.xmin = 500
        self.xmax = 3500
        self.input_hist = {}
        self.hist = {}
        self.inputrootfile = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}_masszz.root'
        #self.cutcats = ['resolved','merged_tag']
        self.cutcats = ['resolved']
        self.varb = {
            'resolved':'mass2l2jet_rebin',
            'merged_tag':'mass2lj_rebin'
        }
        self.massZZvarb = {
            'resolved':'mass2l2jet_rebin',
            'merged_tag':'mass2lj_rebin'
        }
        self.AlphaBranch = {}
        self.outAlphafilepath = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile'
        self.outplotpath = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/'

        if(self.useuproot):
            for cutcat in self.cutcats:
                self.input_hist[cutcat] = GetHisto(self.year,cutcat).hist
        else:
            self.GetRootHisto()

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

        
    def AlphaProduce_fromUproot(self):

        with uproot.recreate(f"{self.outAlphafilepath}/AlphaHisto_{self.year}.root") as fout:
            AlphaBranch = {}
            x_axis = np.append(setting().massZZ_low_bins,setting().massZZ_high_bins)
            for cutcat in self.cutcats:
                for cat in setting().leptonic_cut_cats:
                    for tag in setting().tags:
                        #add hist
                        hist_DY_CR = self.input_hist[cutcat][cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'DY_pt100To250_CR_{cat}_{tag}_{self.varb[cutcat]}'] \
                                +self.input_hist[cutcat][cutcat][f'DY_pt250To400_CR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'DY_pt400To650_CR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'DY_pt650ToInf_CR_{cat}_{tag}_{self.varb[cutcat]}']
                        
                        hist_DY_SR = self.input_hist[cutcat][cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'DY_pt100To250_SR_{cat}_{tag}_{self.varb[cutcat]}'] \
                                +self.input_hist[cutcat][cutcat][f'DY_pt250To400_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'DY_pt400To650_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'DY_pt650ToInf_SR_{cat}_{tag}_{self.varb[cutcat]}']
                        sig_content = hist_DY_SR.view(flow=False).value
                        bkg_content = hist_DY_CR.view(flow=False).value
                        sig_content_err = get_err(hist_DY_SR)
                        bkg_content_err = get_err(hist_DY_CR)

                        sig_content_ave = np.average(sig_content)
                        bkg_content_ave = np.average(bkg_content)

                        alpha = sig_content/bkg_content
                        #alpha_err = np.sqrt(((sig_content_err/sig_content)*(sig_content_err/sig_content))+((bkg_content_err/bkg_content)*(bkg_content_err/bkg_content)))
                        alpha_err = np.sqrt(((sig_content_err/sig_content_ave)*(sig_content_err/sig_content_ave))+((bkg_content_err/bkg_content_ave)*(bkg_content_err/bkg_content_ave)))
                        #alpha_err = sig_content_err/bkg_content_err

                        if self.debug:
                            print(f'sig content in {cutcat}_{cat}_{tag} = {sig_content}')
                            print(f'sig  err in {cutcat}_{cat}_{tag} = {sig_content_err}')
                            print(f'bkg content in {cutcat}_{cat}_{tag} = {bkg_content}')
                            print(f'bkg  err in {cutcat}_{cat}_{tag} = {bkg_content_err}')
                            print(f'alpha raio in {cutcat}_{cat}_{tag} = {alpha}')
                            print(f'alpha raio err in {cutcat}_{cat}_{tag} = {alpha_err}')

                        AlphaBranch[f'{cutcat}_{cat}_{tag}'] = alpha
                        AlphaBranch[f'Err_{cutcat}_{cat}_{tag}'] = alpha_err

                        #plot
                        x_pos = []
                        y_val = []
                        x_err = []
                        y_err = []
                        f, ax = plt.subplots(figsize=(10, 10))
                        hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %setting().config['lumi'][self.year], fontname='sans-serif')
                        for i in range(0,len(x_axis)-1):
                            x = (x_axis[i]+x_axis[i+1])/2
                            x_pos.append(x)
                            y = alpha[i]
                            y_val.append(y)
                            xerr = (x_axis[i+1]-x_axis[i])/2
                            x_err.append(xerr)
                            yerr = alpha_err[i]
                            y_err.append(yerr)
                            ax.plot(x,y,'o', markersize=8 ,color='black')
                        ax.errorbar(x_pos,y_val,xerr=x_err,yerr=y_err,elinewidth = 1.5,linestyle='none',color='black',label = 'Alpha Ratio')
                
                        ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0); ax.set_ylabel('Ratio', ha='right', y=1.0)
                        ax.set_ylim(-0.5, 1.5)
                        ax.text(0.05, 0.92, f'{setting().text[cat]}', transform=ax.transAxes, fontweight='bold') 
                        ax.legend(loc='upper right')

                        plt.savefig(f'{self.outplotpath}{cutcat}/{self.year}/AlphaRaio_{cat}_{tag}.png')
                        plt.close()
            fout['alphatree'] = AlphaBranch
    

    def AlphaProduce_fromROOT(self):
        #with uproot.recreate(f"{self.outAlphafilepath}/AlphaHistoFromROOT_{self.year}.root") as fout:
        with ROOT.TFile.Open(f"{self.outAlphafilepath}/AlphaHistoFromROOT_{self.year}.root","recreate") as fout:
            x_axis = np.append(self.massZZ_low_bins,self.massZZ_high_bins)
            for cutcat in self.cutcats:
                for cat in self.leptonic_cut_cats:
                    for tag in self.tags:
                        hist_DY_CR = self.hist[cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}']
                        hist_DY_CR.Sumw2()
                        #hist_DY_CR.Add(self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                        hist_DY_CR.Add(self.hist[cutcat][f'DY_pt100To250_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                        hist_DY_CR.Add(self.hist[cutcat][f'DY_pt250To400_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                        hist_DY_CR.Add(self.hist[cutcat][f'DY_pt400To650_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                        hist_DY_CR.Add(self.hist[cutcat][f'DY_pt650ToInf_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])

                        hist_DY_SR = self.hist[cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[cutcat]}'] 
                        hist_DY_SR.Sumw2()
                        hist_DY_SR.Add(self.hist[cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                        hist_DY_SR.Add(self.hist[cutcat][f'DY_pt100To250_SR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                        hist_DY_SR.Add(self.hist[cutcat][f'DY_pt250To400_SR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                        hist_DY_SR.Add(self.hist[cutcat][f'DY_pt400To650_SR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                        hist_DY_SR.Add(self.hist[cutcat][f'DY_pt650ToInf_SR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])

                        hist_DY_SR.Divide(hist_DY_CR)

                        fout[f'{cutcat}_{cat}_{tag}'] = hist_DY_SR
                        #====================================up
                        hist_DY_CR_up = self.hist[cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}']
                        hist_DY_CR_up.Sumw2()
                        #hist_DY_CR_up.Add(self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                        hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt100To250_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])
                        hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt250To400_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])
                        hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt400To650_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])
                        hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt650ToInf_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])

                        hist_DY_SR_up = self.hist[cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'] 
                        hist_DY_SR_up.Sumw2()
                        hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])
                        hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt100To250_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])
                        hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt250To400_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])
                        hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt400To650_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])
                        hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt650ToInf_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}'])

                        hist_DY_SR_up.Divide(hist_DY_CR_up)

                        hist_DY_SR_up.Write(f'{cutcat}_{cat}_{tag}_up')
                        #fout[f'{cutcat}_{cat}_{tag}_up'] = hist_DY_SR_up

                        #====================================dn
                        hist_DY_CR_dn = self.hist[cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}']
                        hist_DY_CR_dn.Sumw2()
                        #hist_DY_CR_dn.Add(self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                        hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt100To250_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])
                        hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt250To400_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])
                        hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt400To650_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])
                        hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt650ToInf_CR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])

                        hist_DY_SR_dn = self.hist[cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'] 
                        hist_DY_SR_dn.Sumw2()
                        hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt50To100_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])
                        hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt100To250_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])
                        hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt250To400_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])
                        hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt400To650_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])
                        hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt650ToInf_SR_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}'])

                        hist_DY_SR_dn.Divide(hist_DY_CR_dn)

                        fout[f'{cutcat}_{cat}_{tag}_dn'] = hist_DY_SR_dn

                        #==============================Integral bincontents to calculate error=====================
                        mean = hist_DY_SR.Integral()
                        up = hist_DY_SR_up.Integral()
                        dn = hist_DY_SR_dn.Integral()

                        uncertainty_up = abs(up-mean)/mean
                        uncertainty_dn = abs(dn-mean)/mean

                        print(f'alpha uncertainty UP in {cutcat}_{cat}_{tag} = {uncertainty_up}')
                        print(f'alpha uncertainty DOWN in {cutcat}_{cat}_{tag} = {uncertainty_dn}')

                        #plot
                        x_pos = []
                        y_val = []
                        y_val_up = []
                        y_val_dn = []
                        x_err = []
                        y_err = []
                        f, ax = plt.subplots(figsize=(10, 10))
                        hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %self.config['lumi'][self.year], fontname='sans-serif')
                        for i in range(0,len(x_axis)-1):
                            x = (x_axis[i]+x_axis[i+1])/2
                            x_pos.append(x)
                            #y = h_content[i]
                            y = hist_DY_SR.GetBinContent(i)
                            y_up = hist_DY_SR_up.GetBinContent(i)
                            y_dn = hist_DY_SR_dn.GetBinContent(i)
                            y_val.append(y)
                            y_val_up.append(y_up)
                            y_val_dn.append(y_dn)
                            xerr = (x_axis[i+1]-x_axis[i])/2
                            x_err.append(xerr)
                            #yerr = h_err[i]
                            yerr = hist_DY_SR.GetBinError(i)
                            y_err.append(yerr)
                            ax.plot(x,y,'o', markersize=2 ,color='black')
                        ax.plot(x_pos,y_val_up,'ro:',label = 'JES UP', linewidth = 1),
                        ax.plot(x_pos,y_val_up,'bo:',label = 'JES DOWN', linewidth = 1),
                        print(f'{self.year} {cutcat} {tag}: ratio = {y_val} err = {y_err}')
                        ax.errorbar(x_pos,y_val,xerr=x_err,yerr=y_err,elinewidth = 1.0,linestyle='none',color='black',label = 'Alpha Ratio')
                        ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
                        ax.set_ylabel('Ratio', ha='right', y=1.0)
                        if tag == 'untag' and cutcat == 'resolved':
                            ax.set_ylim(-0.5, 1.0)
                        else:
                            ax.set_ylim(-0.5, 1.5)
                        ax.text(0.05, 0.92, f'{self.text[cat]}', transform=ax.transAxes, fontweight='bold')
                        ax.legend(loc='upper right') 
                        plt.savefig(f'{self.outplotpath}{cutcat}/{self.year}/AlphaRaioFromRoot_{cat}_{tag}.png')
                        plt.close()



    def AlphaProduce_fromRawROOT(self):
        #with uproot.recreate(f"{self.outAlphafilepath}/AlphaHistoFromROOT_{self.year}.root") as fout:
        #with ROOT.TFile.Open(f"{self.outAlphafilepath}/AlphaHistoFromROOT_{self.year}.root","recreate") as fout:
        fout = ROOT.TFile(f"{self.outAlphafilepath}/AlphaHistoFromROOT{self.alphafilestr}_{self.year}.root","recreate")
        fout.cd()
        #x_axis = np.append(self.massZZ_low_bins,self.massZZ_high_bins)
        for cutcat in self.cutcats:
            #get x axis from hb.axis
            x_axis = self.massZZ_bins[cutcat].edges 
            for cat in self.leptonic_cut_cats:
                for tag in self.tags:
                    hist_DY_CR = self.hist[cutcat][f'DY_pt50To100_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw']
                    hist_DY_CR.Sumw2()
                
                    #hist_DY_CR.Add(self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_CR.Add(self.hist[cutcat][f'DY_pt100To250_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])
                    hist_DY_CR.Add(self.hist[cutcat][f'DY_pt250To400_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])
                    hist_DY_CR.Add(self.hist[cutcat][f'DY_pt400To650_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])
                    hist_DY_CR.Add(self.hist[cutcat][f'DY_pt650ToInf_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])

                    hist_DY_SR = self.hist[cutcat][f'DY_pt50To100_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'] 
                    hist_DY_SR.Sumw2()
                    hist_DY_SR.Add(self.hist[cutcat][f'DY_pt50To100_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])
                    hist_DY_SR.Add(self.hist[cutcat][f'DY_pt100To250_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])
                    hist_DY_SR.Add(self.hist[cutcat][f'DY_pt250To400_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])
                    hist_DY_SR.Add(self.hist[cutcat][f'DY_pt400To650_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])
                    hist_DY_SR.Add(self.hist[cutcat][f'DY_pt650ToInf_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}_raw'])

                    hist_DY_SR.Divide(hist_DY_CR)

                    print(fout)
                    hist_DY_SR.Write(f'{cutcat}_{cat}_{tag}')
                    #fout[f'{cutcat}_{cat}_{tag}'] = hist_DY_SR
                    #====================================up
                    hist_DY_CR_up = self.hist[cutcat][f'DY_pt50To100_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw']
                    hist_DY_CR_up.Sumw2()
                    #hist_DY_CR_up.Add(self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt100To250_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])
                    hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt250To400_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])
                    hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt400To650_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])
                    hist_DY_CR_up.Add(self.hist[cutcat][f'DY_pt650ToInf_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])

                    hist_DY_SR_up = self.hist[cutcat][f'DY_pt50To100_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'] 
                    hist_DY_SR_up.Sumw2()
                    hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt50To100_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])
                    hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt100To250_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])
                    hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt250To400_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])
                    hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt400To650_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])
                    hist_DY_SR_up.Add(self.hist[cutcat][f'DY_pt650ToInf_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_up_")}_raw'])

                    hist_DY_SR_up.Divide(hist_DY_CR_up)

                    hist_DY_SR_up.Write(f'{cutcat}_{cat}_{tag}_up')
                    #fout[f'{cutcat}_{cat}_{tag}_up'] = hist_DY_SR_up

                    #====================================dn
                    hist_DY_CR_dn = self.hist[cutcat][f'DY_pt50To100_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw']
                    hist_DY_CR_dn.Sumw2()
                    #hist_DY_CR_dn.Add(self.hist[self.cutcat][f'DY_pt50To100_CR_{cat}_{tag}_{self.massZZvarb[self.cutcat]}'])
                    hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt100To250_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])
                    hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt250To400_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])
                    hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt400To650_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])
                    hist_DY_CR_dn.Add(self.hist[cutcat][f'DY_pt650ToInf_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])

                    hist_DY_SR_dn = self.hist[cutcat][f'DY_pt50To100_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'] 
                    hist_DY_SR_dn.Sumw2()
                    hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt50To100_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])
                    hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt100To250_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])
                    hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt250To400_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])
                    hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt400To650_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])
                    hist_DY_SR_dn.Add(self.hist[cutcat][f'DY_pt650ToInf_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat].replace("_", "_dn_")}_raw'])

                    hist_DY_SR_dn.Divide(hist_DY_CR_dn)
                    
                    hist_DY_SR_dn.Write(f'{cutcat}_{cat}_{tag}_dn')
                    #fout[f'{cutcat}_{cat}_{tag}_dn'] = hist_DY_SR_dn

                    #==============================Integral bincontents to calculate error=====================
                    mean = hist_DY_SR.Integral()
                    up = hist_DY_SR_up.Integral()
                    dn = hist_DY_SR_dn.Integral()

                    uncertainty_up = abs(up-mean)/mean
                    uncertainty_dn = abs(dn-mean)/mean

                    print(f'[INFO] Alpha uncertainty UP in {cutcat}_{cat}_{tag} = {uncertainty_up}')
                    print(f'[INFO] Alpha uncertainty DOWN in {cutcat}_{cat}_{tag} = {uncertainty_dn}')

                    #plot
                    x_pos = []
                    y_val = []
                    y_val_up = []
                    y_val_dn = []
                    x_err = []
                    y_err = []
                    f, ax = plt.subplots(figsize=(10, 10))
                    hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %self.config['lumi'][self.year], fontname='sans-serif')
                    for i in range(0,len(x_axis)-1):
                        x = (x_axis[i]+x_axis[i+1])/2
                        x_pos.append(x)
                        #y = h_content[i]
                        y = hist_DY_SR.GetBinContent(i)
                        y_up = hist_DY_SR_up.GetBinContent(i)
                        y_dn = hist_DY_SR_dn.GetBinContent(i)
                        y_val.append(y)
                        y_val_up.append(y_up)
                        y_val_dn.append(y_dn)
                        xerr = (x_axis[i+1]-x_axis[i])/2
                        x_err.append(xerr)
                        #yerr = h_err[i]
                        yerr = hist_DY_SR.GetBinError(i)
                        y_err.append(yerr)
                        ax.plot(x,y,'o', markersize=2 ,color='black')
                    ax.plot(x_pos,y_val_up,'ro:',label = 'JES UP', linewidth = 1,markersize=1),
                    ax.plot(x_pos,y_val_dn,'bo:',label = 'JES DOWN', linewidth = 1,markersize=1),
                    print(f'{self.year} {cutcat} {tag}: ratio = {y_val} err = {y_err}')
                    ax.errorbar(x_pos,y_val,xerr=x_err,yerr=y_err,elinewidth = 1.0,linestyle='none',color='black',label = 'Alpha Ratio')
                    ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
                    ax.set_ylabel('Ratio', ha='right', y=1.0)
                    if tag == 'untag' and cutcat == 'resolved':
                        ax.set_ylim(-0.5, 1.0)
                    else:
                        ax.set_ylim(-0.5, 1.5)
                    ax.text(0.05, 0.92, f'{self.text[cat]}', transform=ax.transAxes, fontweight='bold')
                    ax.legend(loc='upper right') 
                    plt.savefig(f'{self.outplotpath}{cutcat}/{self.year}/AlphaRaioFromRawRoot_{cat}_{tag}.png')
                    plt.close()
        
        fout.Write()

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

    def AlphaApply(self):
        alpha_arr = uproot.lazy([f"{self.outAlphafilepath}/AlphaHisto_{self.year}.root:alphatree"])
        with uproot.update(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root') as fout:
            for cutcat in self.cutcats:
                for cat in setting().leptonic_cut_cats:
                    for tag in setting().tags:
                        hist_tt_CR = self.input_hist[cutcat][cutcat][f'TTTo2L2Nu_CR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'WWTo2L2Nu_CR_{cat}_{tag}_{self.varb[cutcat]}']
                        hist_zv_CR = self.input_hist[cutcat][cutcat][f'WZTo2Q2L_CR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'ZZTo2Q2L_CR_{cat}_{tag}_{self.varb[cutcat]}']
                        hist_tt_SR = self.input_hist[cutcat][cutcat][f'TTTo2L2Nu_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'WWTo2L2Nu_SR_{cat}_{tag}_{self.varb[cutcat]}']
                        hist_zv_SR = self.input_hist[cutcat][cutcat][f'WZTo2Q2L_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'ZZTo2Q2L_SR_{cat}_{tag}_{self.varb[cutcat]}']
                        hist_data = self.input_hist[cutcat][cutcat][f'Data_CR_{cat}_{tag}_{self.varb[cutcat]}']

                        tt_content = hist_tt_CR.view(flow=False).value
                        zv_content = hist_zv_CR.view(flow=False).value
                        data_content = hist_data.view(flow=False).value

                        data_SB = (data_content - zv_content ) - tt_content

                        dy_SR_content = data_SB * alpha_arr[f'{cutcat}_{cat}_{tag}']

                        dy_SR_histo = bh.Histogram(setting().massZZ_bins)
                        dy_SR_histo[:] = dy_SR_content

                        print(f'content dy in {cutcat}_{cat}_{tag} = {dy_SR_histo.values()}')

                        fout[f'DY/{cutcat}/SR/{cat}/{tag}/massZZ'] = dy_SR_histo

                        edge = np.append(setting().massZZ_low_bins,setting().massZZ_high_bins)
                        f, ax = plt.subplots(figsize=(10, 10))
                        hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %setting().config['lumi'][self.year], fontname='sans-serif')
                        #hep.cms.label(data=True, year=year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%lumi[year], fontname='sans-serif')
                    
                        hep.histplot([hist_zv_SR,hist_tt_SR,dy_SR_histo],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
                        ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
                        ax.set_ylabel('Events / bin', ha='right', y=1.0)
                    
                        ##SIGNAL
                        #colors = ['blue', 'red']
                        #hep.histplot(signal_hists['SR'][cat],label=[ var for var in ['ggH(m1000)x10','VBF(m1500)x10']],linestyle=[style for style in [':','--']], color=[color for color in colors])
                    
                        #bkg_hist = bkg_hists['SR']['isEE'][0]+bkg_hists['SR']['isEE'][1]+bkg_hists['SR']['isEE'][2]
                        bkg_tot = hist_zv_SR.values()+hist_tt_SR.values()+dy_SR_histo.values()
                        #bkg_err = np.sqrt(bkg_tot)
                        bkg_err = get_err(hist_zv_SR+hist_tt_SR+dy_SR_histo)
                        #print(f'bkg_err in {cat} = {bkg_err}')
                        ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.
                        ax.fill_between(edge, (bkg_tot-bkg_err-alpha_arr[f'Err_{cutcat}_{cat}_{tag}']).tolist()+[0], (bkg_tot-bkg_err).tolist()+[0], label='Alpha total unce.', step='post', hatch='xx', edgecolor='darkgrey', facecolor='none', linewidth=0) ## draw bkg unce.
                        ax.fill_between(edge, (bkg_tot+bkg_err).tolist()+[0], (bkg_tot+bkg_err+alpha_arr[f'Err_{cutcat}_{cat}_{tag}']).tolist()+[0],step='post', hatch='xx', edgecolor='darkgrey', facecolor='none', linewidth=0) ## draw bkg unce.
                    
                        ax.set(yscale = "log")
                        ax.set_ylim(1e-1, 3*ax.get_ylim()[1])
                        ax.text(0.05, 0.92, f'{setting().text[cat]}', transform=ax.transAxes, fontweight='bold') 
                        ax.legend(fontsize=18)

                        savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{cutcat}/{self.year}'
                        if not os.path.exists(savepath):
                            os.mkdir(savepath)
                        plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{cutcat}/{self.year}/massZZ_SR_{cat}_{tag}.png')
                        #plt.show()
                        plt.close()

    def AlphaApplyFromROOT(self):
        alpha_file = ROOT.TFile(f"{self.outAlphafilepath}/AlphaHistoFromROOT_{self.year}.root","READ")
        fout = ROOT.TFile(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root','UPDATE')
        #with uproot.update(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root') as fout:
        for cutcat in self.cutcats:
            for cat in self.leptonic_cut_cats:
                for tag in self.tags:
                    hist_tt_CR = self.hist[cutcat][f'TTTo2L2Nu_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_tt_CR.Sumw2()
                    #hist_tt_CR = self.hist[cutcat][f'TTJets_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_tt_CR.Sumw2()
                    hist_tt_CR.Add(self.hist[cutcat][f'WWTo2L2Nu_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                    hist_zv_CR = self.hist[cutcat][f'WZTo2Q2L_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_zv_CR.Sumw2()
                    hist_zv_CR.Add(self.hist[cutcat][f'ZZTo2Q2L_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                    hist_data = self.hist[cutcat][f'Data_CR_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_data.Sumw2()
                    hist_data.Add(hist_tt_CR,-1)
                    hist_data.Add(hist_zv_CR,-1)
                    alpha_hist = alpha_file.Get(f'{cutcat}_{cat}_{tag}')
                    hist_data.Multiply(alpha_hist)

                    fout.cd(); hist_data.Write(f'DY_{cutcat}_SR_{cat}_{tag}_massZZ')
                    #fout[f'DY/{cutcat}/SR/{cat}/{tag}/massZZ'] = hist_data
        fout.Write()
        fout.Close()

    #crate boost_histogram object from ROOT histogram
    def CreateBoostHistoFromROOT(self, hist):
        '''
            input: ROOT histogram
           output: boost_histogram object
        '''
        # Get the number of bins
        n_bins = hist.GetNbinsX()

        # Get the bin edges
        bin_edges = [hist.GetBinLowEdge(i) for i in range(1, n_bins + 2)]

        # Create an empty boost_histogram object
        boost_hist = bh.Histogram(bh.axis.Variable(bin_edges), storage=bh.storage.Double())

        # Fill the boost_histogram object with bin contents
        for i in range(1, n_bins + 1):
            bin_content = hist.GetBinContent(i)
            boost_hist[i - 1] = bin_content

        return boost_hist

    
    def Validation(self):
        #open the alpha file
        alpha_file = ROOT.TFile(f"{self.outAlphafilepath}/AlphaHistoFromROOT_{self.year}.root","READ")

        #make cut for Data, TTbar, WZ, ZZ and WW samples in VR to get array of massZZ in each cutcat , channel and tag
        for cutcat in self.cutcats:
            for cat in self.leptonic_cut_cats:
                for tag in self.tags:
                    #To get zjet contribution in VR by applying alpha to (data - ttbar - WZ - ZZ - WW) in SB
                    hist_tt_CR = self.hist[cutcat][f'TTTo2L2Nu_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_tt_CR.Sumw2()
                    hist_tt_CR.Add(self.hist[cutcat][f'WWTo2L2Nu_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                    hist_zv_CR = self.hist[cutcat][f'WZTo2Q2L_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_zv_CR.Sumw2()
                    hist_zv_CR.Add(self.hist[cutcat][f'ZZTo2Q2L_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                    hist_zjet = self.hist[cutcat][f'Data_{self.alphaCR}_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_zjet.Sumw2()
                    print('Data_content before subtract TT and ZV= ',self.GetHistInfoFromROOT(hist_zjet)[0])
                    hist_zjet.Add(hist_tt_CR,-1)
                    hist_zjet.Add(hist_zv_CR,-1)
                    print('Data_content after subtract TT and ZV= ',self.GetHistInfoFromROOT(hist_zjet)[0])

                    #get alpha histogram from alpha file
                    alpha_hist = alpha_file.Get(f'{cutcat}_{cat}_{tag}')
                    print('alpha_content = ',self.GetHistInfoFromROOT(alpha_hist)[0])
                    #get the massZZ histogram by applying alpha to data
                    hist_zjet.Multiply(alpha_hist)

                    #retrieve the massZZ histogram from the root file for data ttbar WZ ZZ WW in VR
                    hist_data = self.hist[cutcat][f'Data_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_data.Sumw2()
                    hist_tt_VR = self.hist[cutcat][f'TTTo2L2Nu_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_tt_VR.Sumw2()
                    hist_tt_VR.Add(self.hist[cutcat][f'WWTo2L2Nu_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}'])
                    hist_zv_VR = self.hist[cutcat][f'WZTo2Q2L_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}']; hist_zv_VR.Sumw2()
                    hist_zv_VR.Add(self.hist[cutcat][f'ZZTo2Q2L_{self.alphaSR}_{cat}_{tag}_{self.massZZvarb[cutcat]}'])

                    self.plotMassZZFromROOT(hist_zv_VR,hist_tt_VR,hist_zjet,hist_data,cat)

                    #savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/Plot/{self.year}'
                    #if not os.path.exists(savepath):
                    #    os.mkdir(savepath)

                    plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/Plots/{self.year}/AplaValidation_{cutcat}_{cat}_{tag}.png')
                    plt.close()

    


    #get content, edges and error of a ROOT histogram
    def GetHistInfoFromROOT(self,hist):
        '''
            input: ROOT histogram
           output: content, edges and error
        '''
        # Get the number of bins
        n_bins = hist.GetNbinsX()

        # Get the bin edges
        bin_edges = np.array([hist.GetBinLowEdge(i) for i in range(1, n_bins + 2)])

        # Get the bin contents
        bin_contents = np.array([hist.GetBinContent(i) for i in range(1, n_bins + 1)])

        # Get the bin errors
        bin_errors = np.array([hist.GetBinError(i) for i in range(1, n_bins + 1)])

        return bin_contents, bin_edges, bin_errors
    
    #plot the massZZ distribution with ROOT histogram as input. Data/MC ratio and error band are also plotted
    def plotMassZZFromROOT(self,hist_zv,hist_tt,hist_zjet,hist_data,cat):
        f = plt.figure(figsize=(12,12))
        gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0)

        #get xmin and xmax from massZZ bins
        
        ##===Upper histogram panel
        ax = f.add_subplot(gs[0])
        hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %setting().config['lumi'][self.year], fontname='sans-serif')
        ax.set_xlim(self.xmin, self.xmax); ax.set_xticklabels([]); ax.set_ylabel('Events / bin', ha='right', y=1.0)

        #plot background as stacked histogram
        hep.histplot([hist_zv,hist_tt,hist_zjet],label=[f'{var}' for var in ['MC (WZ,ZZ {})'.format(round(hist_zv.Integral(),2),'.2f'),'MC (TT,WW {})'.format(round(hist_tt.Integral(),2),'.2f'),'Data Driven (Z+jets {})'.format(round(hist_zjet.Integral(),2),'.2f')]],histtype='fill', edgecolor='k', linewidth=1, stack=True)

        #add them to get the total background
        hist_bkg = hist_zv; hist_bkg.Sumw2()
        hist_bkg.Add(hist_tt); hist_bkg.Add(hist_zjet)

        #get the bin content, edges and error of the total background
        contents_bkg, bin_edges, errors_bkg = self.GetHistInfoFromROOT(hist_bkg)
        print('BKG INFO=============================================')
        print('bin_edges = ',bin_edges)
        print('contents_bkg = ',contents_bkg)
        print('errors_bkg = ',errors_bkg)

        #plot the error band
        ax.fill_between(bin_edges, (contents_bkg - errors_bkg).tolist()+[0], (contents_bkg + errors_bkg).tolist()+[0], hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0, label='BKG total unce.')
        print('err_low = ',(contents_bkg - errors_bkg).tolist()+[0])
        print('err_up = ',(contents_bkg + errors_bkg).tolist()+[0])

        ##Data
        #get the bin content, edges and error of data
        contents_data, bin_edges, errors_data = self.GetHistInfoFromROOT(hist_data)
        print('DATA INFO=============================================')
        print('bin_edges = ',bin_edges)
        print('contents_data = ',contents_data)
        print('errors_data = ',errors_data)
        #plot data
        hep.histplot(hist_data, label='Data ({})'.format(round(hist_data.Integral(),2),'2.f'), color='k', histtype='errorbar', linewidth=1.5,markersize=15)
        
        ##set log scale for y axis
        ax.set_yscale('log')
        ax.set_ylim(1e-1, 3*ax.get_ylim()[1])

        #lepton channel text
        ax.text(0.05, 0.92, f'{self.text[cat]}', transform=ax.transAxes, fontweight='bold')
        #plot legend
        hep.plot.yscale_legend
        ax.legend(fontsize=18)
        ##===Lower ratio panel
        ax1 = f.add_subplot(gs[1]); ax1.set_ylim(0.001, 1.999)
        ax1.set_ylabel('Data / MC', ha='center')
        ax1.set_xlim(self.xmin, self.xmax); ax1.set_xlabel(r'$m_{ZZ}$ [GeV]', ha='right', x=1.0)
        ax1.plot([self.xmin,self.xmax], [1,1], 'k'); ax1.plot([self.xmin,self.xmax], [0.5,0.5], 'k:'); ax1.plot([self.xmin,self.xmax], [1.5,1.5], 'k:')
        ratio=np.nan_to_num((contents_data/contents_bkg),nan=-1) #get the ratio of data and total background
        ratio_err=np.nan_to_num((errors_data/contents_bkg),nan=-1) #get the error of the ratio
        #plot the ratio
        hep.histplot(ratio, yerr=ratio_err, bins = bin_edges ,histtype='errorbar', color='k', linewidth=1.5,markersize=15)
        #plot the ratio error band
        ratio_unc_low = np.nan_to_num(((contents_bkg-errors_bkg)/contents_bkg),nan=0)
        ratio_unc_high = np.nan_to_num(((contents_bkg+errors_bkg)/contents_bkg),nan=0)
        print('Ratio INFO=============================================')
        print('ratio = ',ratio)
        print('ratio_unc_low = ',ratio_unc_low)
        print('ratio_unc_high = ',ratio_unc_high)
        ax1.fill_between(bin_edges, ratio_unc_low.tolist()+[0], ratio_unc_high.tolist()+[0], hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0)

    def massZZplot(self):
        if(not self.useuproot):
            for cutcat in self.cutcats:
                self.input_hist[cutcat] = GetHisto(self.year,cutcat).hist
        with uproot.update(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root') as fout:
            for cutcat in self.cutcats:
                for cat in self.leptonic_cut_cats:
                    for tag in self.tags:
                        #print(self.input_hist[cutcat][cutcat].keys())
                        hist_tt_SR = self.input_hist[cutcat][cutcat][f'TTTo2L2Nu_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'WWTo2L2Nu_SR_{cat}_{tag}_{self.varb[cutcat]}']
                        #hist_tt_SR = self.input_hist[cutcat][cutcat][f'TTJets_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'WWTo2L2Nu_SR_{cat}_{tag}_{self.varb[cutcat]}']
                        hist_zv_SR = self.input_hist[cutcat][cutcat][f'WZTo2Q2L_SR_{cat}_{tag}_{self.varb[cutcat]}']+self.input_hist[cutcat][cutcat][f'ZZTo2Q2L_SR_{cat}_{tag}_{self.varb[cutcat]}']
                        dy_SR_histo = self.input_hist[cutcat][cutcat][f'DY_SR_{cat}_{tag}_massZZ']

                        edge = np.append(setting().massZZ_low_bins,setting().massZZ_high_bins)
                        f, ax = plt.subplots(figsize=(10, 10))
                        hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %setting().config['lumi'][self.year], fontname='sans-serif')
                        #hep.cms.label(data=True, year=year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%lumi[year], fontname='sans-serif')

                        hep.histplot([hist_zv_SR,hist_tt_SR,dy_SR_histo],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
                        ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
                        ax.set_ylabel('Events / bin', ha='right', y=1.0)

                        ##SIGNAL
                        #colors = ['blue', 'red']
                        #hep.histplot(signal_hists['SR'][cat],label=[ var for var in ['ggH(m1000)x10','VBF(m1500)x10']],linestyle=[style for style in [':','--']], color=[color for color in colors])

                        #bkg_hist = bkg_hists['SR']['isEE'][0]+bkg_hists['SR']['isEE'][1]+bkg_hists['SR']['isEE'][2]
                        bkg_tot = hist_zv_SR.values()+hist_tt_SR.values()+dy_SR_histo.values()
                        print(f'bkg_tot in {cutcat}_{cat}_{tag} = {bkg_tot}')
                        bkg_err = np.sqrt(bkg_tot)
                        #bkg_err = get_err(hist_zv_SR+hist_tt_SR+dy_SR_histo)
                        #print(f'bkg_err in {cat} = {bkg_err}')
                        ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.
                        #ax.fill_between(edge, (bkg_tot-bkg_err-alpha_arr[f'Err_{cutcat}_{cat}_{tag}']).tolist()+[0], (bkg_tot-bkg_err).tolist()+[0], label='Alpha total unce.', step='post', hatch='xx', edgecolor='darkgrey', facecolor='none', linewidth=0) ## draw bkg unce.
                        #ax.fill_between(edge, (bkg_tot+bkg_err).tolist()+[0], (bkg_tot+bkg_err+alpha_arr[f'Err_{cutcat}_{cat}_{tag}']).tolist()+[0],step='post', hatch='xx', edgecolor='darkgrey', facecolor='none', linewidth=0) ## draw bkg unce.

                        ax.set(yscale = "log")
                        ax.set_ylim(1e-1, 3*ax.get_ylim()[1])
                        ax.text(0.05, 0.92, f'{setting().text[cat]}', transform=ax.transAxes, fontweight='bold') 
                        ax.legend(fontsize=18)
                        savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plotnew/{cutcat}/{self.year}'
                        if not os.path.exists(savepath):
                            os.mkdir(savepath)
                        plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plotnew/{cutcat}/{self.year}/massZZ_SR_{cat}_{tag}.png')
                        #plt.show()
                        plt.close()
    
    #Vaildate the alpha method by apply alpha to the Validation region which defined as the dijet mass between 135 and 165 GeV

    def GetRootHisto(self):
        self.file = ROOT.TFile.Open(self.inputrootfile,'READ')
        print("[INFO] Get root files as form of ROOT")

        for cutcat in self.cutcats:
            self.hist[cutcat] = {}
            for sample in self.fileset[self.year].keys():
                for reg in self.regions:
                    for cat in self.leptonic_cut_cats:
                        for tag in self.tags:
                            for varb in self.config['bininfo'].keys():
                                if varb == 'mass2l2jet' and cutcat == 'resolved':
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin_raw'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin_raw')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_up_rebin'] = self.file.Get(f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}_up_rebin')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_up_rebin_raw'] = self.file.Get(f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}_up_rebin_raw')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_dn_rebin'] = self.file.Get(f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}_dn_rebin')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_dn_rebin_raw'] = self.file.Get(f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}_dn_rebin_raw')
                                elif varb == 'mass2lj' and cutcat == 'merged_tag':
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin_raw'] = self.file.Get(f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin_raw')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_up_rebin'] = self.file.Get(f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}_up_rebin')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_up_rebin_raw'] = self.file.Get(f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}_up_rebin_raw')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_dn_rebin'] = self.file.Get(f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}_dn_rebin')
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_dn_rebin_raw'] = self.file.Get(f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}_dn_rebin_raw')
                        
        #if self.cutcat == 'lep':
        #    self.hist['lep'] = {}
        #    for sample in self.fileset[self.year].keys():
#
        #elif self.cutcat=='resolved':
        #    self.hist['resolved'] = {}
        #    for sample in self.fileset[self.year].keys():
        #        for reg in self.regions:
        #            for cat in self.leptonic_cut_cats:
        #                for tag in self.tags:
        #                    for varb in self.config['bininfo'].keys():
        #                        if varb == 'mass2l2jet':
        #                            self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin')#[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin']
        #                            if self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin']==None:
        #                                print("error can not get histo")
        #                        self.hist['resolved'][f'{sample}_{reg}_{cat}_{tag}_{varb}'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}')

    def run(self):
        #print('\033[1;34mStep 1. compute alpha ratio from Z+jet(SR)/Z+jet(CR)\033[0m')
        #self.AlphaProduce()
        #self.AlphaProduce_fromROOT()
        #self.AlphaProduce_fromRawROOT()
        #print('\033[1;34mStep 2. Apply alpha ratio to data CR to get Z+jet result\033[0m')
        #self.AlphaApply()
        #self.AlphaApplyFromROOT()
        print('\033[1;34mStep 3. Plot massZZ in validation region\033[0m')
        #self.massZZplot()
        self.Validation()