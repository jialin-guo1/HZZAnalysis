import uproot as up
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

class PlotUnit():
    def __init__(self,year,cutcat) -> None:
        self.year = year
        self.cutcat = cutcat
        self.config = setting().config
        self.cat  = None
        self.plotdir = 'plotnew'

        #setMcDataPlotsColor
        color_order_bkg = sns.color_palette('Accent', 3)
        color_order_bkg.reverse()
        self.set_sns_color(color_order_bkg)

        use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
        if use_helvet:
            CMShelvet = hep.style.CMS
            CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
            plt.style.use(CMShelvet)
        else:
            plt.style.use(hep.style.CMS)
        
    
    def set_sns_color(self,*args):
        sns.palplot(sns.color_palette(*args))
        sns.set_palette(*args)
        pass

    def plot1DDataMC(self,hist_zv,hist_tt,hist_DY,hist_data,var):
        '''
            input: histogram as oder of zv,tt,dy and data
        '''
        nbins, xmin, xmax = self.config['bininfo'][var][0], self.config['bininfo'][var][1], self.config['bininfo'][var][2]
        edge = np.linspace(xmin, xmax, nbins+1)
        if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2jl')!=-1 or var.find('mass2l2jet')!=-1:
            islogY = True
        else:
            islogY = False 
        ###########start to draw######################
        plot_unce = True

        if hist_data !=None:
            f = plt.figure(figsize=(12,12))
            gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0)
            ##================================ Upper histogram panel=========================================
            ax = f.add_subplot(gs[0])
            hep.cms.label(data=True, llabel='Preliminary',year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%self.config['lumi'][self.year], fontname='sans-serif')
            ax.set_xlim(xmin, xmax); ax.set_xticklabels([]); ax.set_ylabel('Events / bin', ha='right', y=1.0)
            ##BACKGRUND
            plot_hist([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            bkg_tot = (hist_zv+hist_tt+hist_DY).values()
            bkg_err = get_err(hist_zv+hist_tt+hist_DY)
            if plot_unce:
                ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.

            ##DATA
            data_err = get_err(hist_data)
            data = hist_data.values()
            plot_hist(hist_data,label='Data', histtype='errorbar', color='k', markersize=15, elinewidth=1.5) ## draw dat
            if islogY:
                ax.set(yscale = "log")
                ax.set_ylim(1e-1, 3*ax.get_ylim()[1])
            else:
                ax.set_ylim(0, ax.get_ylim()[1])
                ax.set_ylim(0, 1.5*max(data))
            ax.text(0.05, 0.92, f'{setting().text[self.cat]}', transform=ax.transAxes, fontweight='bold')
            hep.plot.yscale_legend
            ax.legend(fontsize=18)
            ##==========================================Ratio panel========================
            ax1 = f.add_subplot(gs[1]); ax1.set_xlim(xmin, xmax); ax1.set_ylim(0.001, 1.999)
            ax1.set_xlabel(self.config['bininfo'][var][3], ha='right', x=1.0); ax1.set_ylabel('Data / MC', ha='center')
            ax1.plot([xmin,xmax], [1,1], 'k'); ax1.plot([xmin,xmax], [0.5,0.5], 'k:'); ax1.plot([xmin,xmax], [1.5,1.5], 'k:')
            ratio=np.nan_to_num((data/bkg_tot),nan=-1)
            ratio_err = np.nan_to_num((data_err/bkg_tot),nan=-1)
            hep.histplot(ratio, yerr = ratio_err,bins=edge, histtype='errorbar', color='k', markersize=15, elinewidth=1)
            #hep.histplot(data/bkg_tot, yerr = data_err/bkg_err,bins=edge, histtype='errorbar', color='k', markersize=15, elinewidth=1)
            if plot_unce:
                ratio_unc_low = np.nan_to_num(((bkg_tot-bkg_err)/bkg_tot),nan=-1)
                ratio_unc_up = np.nan_to_num(((bkg_tot+bkg_err)/bkg_tot),nan=-1)
                ax1.fill_between(edge, ratio_unc_low.tolist()+[0],ratio_unc_up.tolist()+[0], step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.
        else:
            f, ax = plt.subplots(figsize=(10, 10))
            hep.cms.label(data=True, llabel='Preliminary',year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%self.config['lumi'][self.year], fontname='sans-serif')
            ax.set_xlim(xmin, xmax); ax.set_xticklabels([]); ax.set_ylabel('Events / bin', ha='right', y=1.0)
            ##BACKGRUND
            plot_hist([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            bkg_tot = (hist_zv+hist_tt+hist_DY).values()
            bkg_err = get_err(hist_zv+hist_tt+hist_DY)
            if plot_unce:
                ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.
            ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)


    def DrawVariable(self,hist):
        ###Set which var will be draw
        if(self.cutcat=='lep'):
            varbs = ['pt2l','mass2l','lep_1_pt','lep_2_pt']
        if(self.cutcat=='resolved'):
            varbs = ['mass2jet','pt2jet','pt2l','mass2l','KD_jjVBF','mass2l2jet','KD_Zjj']
        if(self.cutcat.find('merged') != -1):
            varbs = ['massmerged','ptmerged','pt2l','mass2l','KD_JVBF','particleNetZvsQCD','particleNetZbbvslight','mass2lj','KD_ZJ']

        for var in varbs:
            print(f"[INFO] it is {var} plot")   
            if self.cutcat=='lep' or self.cutcat=='merged_notag':
                for cat in setting().leptonic_cut_cats:
                    self.cat = cat
                    #add hist
                    hist_DY = hist[self.cutcat][f'DY_pt50To100_{cat}_{var}']+hist[self.cutcat][f'DY_pt100To250_{cat}_{var}'] \
                            +hist[self.cutcat][f'DY_pt250To400_{cat}_{var}']+hist[self.cutcat][f'DY_pt400To650_{cat}_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{cat}_{var}']
                    hist_tt = hist[self.cutcat][f'TTTo2L2Nu_{cat}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{cat}_{var}']
                    hist_zv = hist[self.cutcat][f'WZTo2Q2L_{cat}_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{cat}_{var}']
                    hist_data = hist[self.cutcat][f'Data_{cat}_{var}']

                    self.plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data,var)

                    savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}'
                    if not os.path.exists(savepath):
                        os.mkdir(savepath)
                    plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}/{var}_{cat}.png')
                    #plt.show()
                    plt.close()

            if self.cutcat=='resolved' or self.cutcat=='merged_tag':
                for reg in setting().regions:
                    for cat in setting().leptonic_cut_cats:
                        self.cat = cat
                        for tag in setting().tags:
                            #add hist
                            hist_DY = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_{var}'] \
                                    +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_{var}']
                            hist_tt = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}']
                            hist_zv = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{var}']
                            hist_data = hist[self.cutcat][f'Data_{reg}_{cat}_{tag}_{var}']

                            self.plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data,var)

                            savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}'
                            if not os.path.exists(savepath):
                                os.mkdir(savepath)
                            plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}/{var}_{reg}_{cat}_{tag}.png')
                            #plt.show()
                            plt.close()

                            #if((var == 'mass2l2jet' or var == 'mass2lj') and reg == 'SR'):
                            #    hist_DY = hist[self.cutcat][f'DY_{reg}_{cat}_{tag}_massZZ']
#
                            #    self.plot1DDataMC(hist_zv,hist_tt,hist_DY,None,var)
#
                            #    savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{self.cutcat}/{self.year}'
                            #    if not os.path.exists(savepath):
                            #        os.mkdir(savepath)
                            #    plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{self.cutcat}/{self.year}/massZZ_{reg}_{cat}_{tag}.png')
                            #    #plt.show()
                            #    plt.close()

    def run(self):
        hist = GetHisto(self.year,self.cutcat).hist
        self.DrawVariable(hist)



