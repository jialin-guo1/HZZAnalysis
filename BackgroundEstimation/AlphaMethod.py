import uproot 
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward as ak
import pandas as pd
import numpy as np
import seaborn as sns

#===========================================load self.config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

class AlphaMethodUnit():
    def __init__(self,year) -> None:
        self.year = year
        self.input_hist = {}
        self.cutcats = ['resolved','merged_tag']
        self.varb = {
            'resolved':'mass2l2jet_rebin',
            'merged_tag':'mass2lj_rebin'
        }
        self.AlphaBranch = {}
        self.outAlphafilepath = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation/AlphaFile'
        self.outplotpath = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/'

        for cutcat in self.cutcats:
            self.input_hist[cutcat] = GetHisto(self.year,cutcat).hist

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

        
    def AlphaProduce(self):
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

                        alpha = sig_content/bkg_content
                        alpha_err = np.sqrt(((sig_content_err/sig_content)*(sig_content_err/sig_content))+((bkg_content_err/bkg_content)*(bkg_content_err/bkg_content)))

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

                        print(f'content dy = {dy_SR_histo.values()} in {cutcat}_{cat}_{tag}')

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
                        print(f'bkg_err in {cat} = {bkg_err}')
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

    def run(self):
        print('\033[1;34mStep 1. compute alpha ratio from Z+jet(SR)/Z+jet(CR)\033[0m')
        self.AlphaProduce()
        print('\033[1;34mStep 2. Apply alpha ratio to data CR to get Z+jet result\033[0m')
        self.AlphaApply()
