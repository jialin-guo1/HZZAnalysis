import uproot 
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward as ak
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
        self.input_hist = {}
        self.hist = {}
        self.inputrootfile = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root'
        self.cutcats = ['resolved','merged_tag']
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
        with uproot.recreate(f"{self.outAlphafilepath}/AlphaHistoFromROOT_{self.year}.root") as fout:
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

                        #plot
                        x_pos = []
                        y_val = []
                        x_err = []
                        y_err = []
                        f, ax = plt.subplots(figsize=(10, 10))
                        hep.cms.label(data=True, llabel='Preliminary', year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %self.config['lumi'][self.year], fontname='sans-serif')
                        for i in range(0,len(x_axis)-1):
                            x = (x_axis[i]+x_axis[i+1])/2
                            x_pos.append(x)
                            #y = h_content[i]
                            y = hist_DY_SR.GetBinContent(i)
                            y_val.append(y)
                            xerr = (x_axis[i+1]-x_axis[i])/2
                            x_err.append(xerr)
                            #yerr = h_err[i]
                            yerr = hist_DY_SR.GetBinError(i)
                            y_err.append(yerr)
                            ax.plot(x,y,'o', markersize=2 ,color='black')
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

    def GetRootHisto(self):
        self.file = ROOT.TFile.Open(self.inputrootfile,'READ')

        for cutcat in self.cutcats:
            self.hist[cutcat] = {}
            for sample in self.fileset[self.year].keys():
                for reg in self.regions:
                    for cat in self.leptonic_cut_cats:
                        for tag in self.tags:
                            for varb in self.config['bininfo'].keys():
                                if varb == 'mass2l2jet' and cutcat == 'resolved':
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin')
                                elif varb == 'mass2lj' and cutcat == 'merged_tag':
                                    self.hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = self.file.Get(f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin')
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
        print('\033[1;34mStep 1. compute alpha ratio from Z+jet(SR)/Z+jet(CR)\033[0m')
        #self.AlphaProduce()
        self.AlphaProduce_fromROOT()
        print('\033[1;34mStep 2. Apply alpha ratio to data CR to get Z+jet result\033[0m')
        #self.AlphaApply()
