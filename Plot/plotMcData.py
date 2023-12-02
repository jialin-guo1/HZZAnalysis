
import uproot
import uproot as up
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward as ak
import pandas as pd
import numpy as np
import seaborn as sns
import hist

#===========================================load self.config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

class PlotUnit():
    def __init__(self,year,cutcat,varb=None) -> None:
        self.year = year
        self.cutcat = cutcat
        self.config = setting().config
        self.cat  = None
        #self.plotdir = 'plotnew'
        self.plotdir = setting().plot_store_dir_name
        self.varb = varb # a list object 
        self.hits_ggh500 = None
        self.hits_ggh1000 = None
        self.hits_ggh3000 = None
        self.hits_vbf1000 = None
        self.hits_ZH_HToBB = None
        self.plotSig = True
        self.particlenet_sf_dy = 1.18
        #self.plotSig = False

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
    
    def plot_variables_with_different_histogrm(self,histo,labels,varb = None, ifnormalize = False) ->None:
        r'''
           input: list of histogram, list of label for each histogram, list of color for each histogram, variable name
           plot the histogram with different color and label without ratio plot
        '''
        #check if list of histo and list of label have the same length, otherwise exit
        if len(histo)!=len(labels):
            print('the length of histogram and label are not the same')
            print('length of histogram: ',len(histo))
            print('length of label: ',len(labels))
            exit("length of histogram and label are not the same")
        #set color for each histogram acroding to the length of histogram
        color_order = sns.color_palette("tab10",len(histo))
        self.set_sns_color(color_order)
        #if isnormalize, the histogram will update to be normalized histogram
        if ifnormalize:
            for i in range(len(histo)):
                sum_of_bins = np.sum(histo[i].values())
                histo[i] = histo[i]/sum_of_bins


        x_max = histo[0].axes[0].edges[-1]; x_min = histo[0].axes[0].edges[0]
        f, ax = plt.subplots(figsize=(12,12))
        hep.cms.label(data=True, llabel='Preliminary',year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%self.config['lumi'][self.year], fontname='sans-serif')
        ax.set_ylabel('Events / bin', ha='right', y=1.0)
        hep.histplot(histo,stack=False,label=labels,histtype='step',linewidth=1)
        ax.set_xlabel(varb, ha='right', x=1.0)
        ax.set_xlim(x_min,x_max)
        ax.legend(fontsize=18)


    def plotupdn(self,hist_mean,hist_up,hist_dn,var):
        if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2jl')!=-1 or var.find('mass2l2jet')!=-1:
            islogY = False
        else:
            islogY = False
        nbins, xmin, xmax = self.config['bininfo'][var][0], self.config['bininfo'][var][1], self.config['bininfo'][var][2]
        f, ax = plt.subplots(figsize=(12,12))
        hep.cms.label(data=True, llabel='Preliminary',year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%self.config['lumi'][self.year], fontname='sans-serif')
        ax.set_xlim(xmin, xmax); ax.set_ylabel('Events / bin', ha='right', y=1.0)

        plot_hist([hist_mean,hist_up,hist_dn],label=[f'MC ({var})' for var in ['mean','up','donw']],histtype='step', linewidth=1, stack=False) ## draw MC

        if islogY:
            ax.set(yscale = "log")
            ax.set_ylim(1e-0, 3*ax.get_ylim()[1])
        ax.set_xlabel(self.config['bininfo'][var][3], ha='right', x=1.0)
        ax.legend(fontsize=18)

    #def plot1DDataMC(self,hist_zv,hist_tt,hist_DY,hist_data,hits_ggh1000=None,hits_vbf1000=None,var):
    def plot1DDataMC(self,hist_zv,hist_tt,hist_DY,hist_data,var,bin=None):
        '''
            input: histogram as oder of zv,tt,dy and data
        '''
        #if var!='massZZ':
        #    nbins, xmin, xmax = self.config['bininfo'][var][0], self.config['bininfo'][var][1], self.config['bininfo'][var][2]
        #    edge = np.linspace(xmin, xmax, nbins+1)
        #else:
        #    edge = np.append(setting().massZZ_low_bins,setting().massZZ_high_bins)
        #    #get the binning from edge
        #    nbins = len(edge)-1
        #    #xmin = edge[0]
        #    xmin = 500 #fix the xmin to 500
        #    xmax = edge[-1]

        edge, nbins, xmin, xmax = GetBinInfoFromBH(hist_zv)
        
        #if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2lj')!=-1 or var.find('mass2l2jet')!=-1 or var.find('KD')!=-1:
        if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2lj')!=-1 or var.find('mass2l2jet')!=-1:
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
            #plot_hist([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ {}'.format(hist_zv.values().sum(),'.1f'),'TT,WW {}'.format(hist_tt.values().sum(),'.1f'),'Z+jets {}'.format(hist_DY.values().sum(),'.1f')]],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            hep.histplot([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ {}'.format(round(hist_zv.values().sum(),2),'.2f'),'TT,WW {}'.format(round(hist_tt.values().sum(),2),'.2f'),'Z+jets {}'.format(round(hist_DY.values().sum(),2),'.2f')]],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            bkg_tot = (hist_zv+hist_tt+hist_DY).values()
            bkg_err = get_err(hist_zv+hist_tt+hist_DY)
            if plot_unce:
                ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.

            if(self.plotSig):
                colors = ['blue', 'red']
                #plot_hist([self.hits_ggh500,self.hits_ggh1000,self.hits_ggh3000],label=[ var for var in ['ggH(m500) {}'.format(self.hits_ggh500.values().sum()),'ggh(m1000) {}'.format(self.hits_ggh1000.values().sum()),'ggh(m3000) {}'.format(self.hits_ggh3000.values().sum())]],linestyle=[style for style in [':','--','-']], color=[color for color in colors])
                hep.histplot([self.hits_ggh1000,self.hits_vbf1000],label=[ var for var in ['ggH(m1000) {}'.format(self.hits_ggh1000.values().sum()),'vbf(m1000) {}'.format(self.hits_vbf1000.values().sum())]],linestyle=[style for style in [':','--']], color=[color for color in colors])

            ##DATA
            data_err = get_err(hist_data)
            data = hist_data.values()
            #plot_hist(hist_data,label='Data', histtype='errorbar', color='k', markersize=15, elinewidth=1.5) ## draw dat
            hep.histplot(hist_data,label='Data ({})'.format(round(hist_data.values().sum(),2),'.2f'), histtype='errorbar', color='k', markersize=15, elinewidth=1.5) ## draw dat
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
            ax.set_xlim(xmin, xmax); ax.set_ylabel('Events / bin', ha='right', y=1.0)
            ##BACKGRUND
            #plot_hist([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ','TT,WW','Z+jets']],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            #plot_hist([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ {}'.format(hist_zv.values().sum(),'.1f'),'TT,WW {}'.format(hist_tt.values().sum(),'.1f'),'Z+jets {}'.format(hist_DY.values().sum(),'.1f')]],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            hep.histplot([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ {}'.format(hist_zv.values().sum(),'.1f'),'TT,WW {}'.format(hist_tt.values().sum(),'.1f'),'Z+jets {}'.format(hist_DY.values().sum(),'.1f')]],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            bkg_tot = (hist_zv+hist_tt+hist_DY).values()
            bkg_err = get_err(hist_zv+hist_tt+hist_DY)
            if plot_unce:
                ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.
            ax.set_xlabel(self.config['bininfo'][var][3])

            if(self.plotSig):
                colors = ['blue', 'red']
                #plot_hist([self.hits_ggh500,self.hits_ggh1000,self.hits_ggh3000],label=[ var for var in ['ggH(m500) {}'.format(self.hits_ggh500.values().sum()),'ggh(m1000) {}'.format(self.hits_ggh1000.values().sum()),'ggh(m3000) {}'.format(self.hits_ggh3000.values().sum())]],linestyle=[style for style in [':','--','-']], color=[color for color in colors])
                #hep.histplot([self.hits_ggh500,self.hits_ggh1000,self.hits_ggh3000],label=[ var for var in ['ggH(m500) {}'.format(self.hits_ggh500.values().sum()),'ggh(m1000) {}'.format(self.hits_ggh1000.values().sum()),'ggh(m3000) {}'.format(self.hits_ggh3000.values().sum())]],linestyle=[style for style in [':','--','-']], color=[color for color in colors])
                hep.histplot([self.hits_ggh1000,self.hits_vbf1000,],label=[ var for var in ['ggH(m1000) {}'.format(self.hits_ggh1000.values().sum()),'vbf(m1000) {}'.format(self.hits_vbf1000.values().sum())]],linestyle=[style for style in [':','--']], color=[color for color in colors])

            if islogY:
                ax.set(yscale = "log")
                ax.set_ylim(1e-1, 3*ax.get_ylim()[1])

            hep.plot.yscale_legend
            ax.legend(fontsize=18)

    def plot1DDataMCRegionALL(self,hist_zv,hist_tt,hist_DY,hist_data,var):
        '''
            input: histogram as oder of zv,tt,dy and data
        '''
        nbins, xmin, xmax = self.config['bininfo'][var][0], self.config['bininfo'][var][1], self.config['bininfo'][var][2]
        edge = np.linspace(xmin, xmax, nbins+1)
        #if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2jl')!=-1 or var.find('mass2l2jet')!=-1:
        if var.find('pt')!=-1 or var.find('mass2l2jet')!=-1:
            islogY = True
        else:
            islogY = False 
        ###########start to draw######################
        plot_unce = True

        if hist_data !=None:
            f = plt.figure(figsize=(16,12))
            gs = mpl.gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0)
            ##================================ Upper histogram panel=========================================
            ax = f.add_subplot(gs[0])
            hep.cms.label(data=True, llabel='Preliminary',year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%self.config['lumi'][self.year], fontname='sans-serif')
            ax.set_xlim(xmin, xmax); ax.set_xticklabels([]); ax.set_ylabel('Events / bin', ha='right', y=1.0)
            ##BACKGRUND

            #plot_hist([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ {}'.format(hist_zv.values().sum(),'.1f'),'TT,WW {}'.format(hist_tt.values().sum(),'.1f'),'Z+jets {}'.format(hist_DY.values().sum(),'.1f')]],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            hep.histplot([hist_zv,hist_tt,hist_DY],label=[f'MC ({var})' for var in ['WZ,ZZ {}'.format(hist_zv.values().sum(),'.1f'),'TT,WW {}'.format(hist_tt.values().sum(),'.1f'),'Z+jets {}'.format(hist_DY.values().sum(),'.1f')]],histtype='fill', edgecolor='k', linewidth=1, stack=True) ## draw MC
            bkg_tot = (hist_zv+hist_tt+hist_DY).values()
            bkg_err = get_err(hist_zv+hist_tt+hist_DY)
            if plot_unce:
                ax.fill_between(edge, (bkg_tot-bkg_err).tolist()+[0], (bkg_tot+bkg_err).tolist()+[0], label='BKG total unce.', step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.

            if(self.plotSig):
                colors = ['blue', 'red','green']
                #plot_hist(self.hits_ggh500,label='ggH(m500) {}'.format(self.hits_ggh500.values().sum()),linestyle='--', color='red')
                #hep.histplot(self.hits_ggh500,label='ggH(m500) {}'.format(self.hits_ggh500.values().sum()),linestyle='--', color='red')
                #plot_hist(self.hits_ZH_HToBB,label='ZH(bb) {}'.format(self.hits_ZH_HToBB.values().sum()),linestyle=':', color='blue')
                hep.histplot([self.hits_ggh1000,self.hits_vbf1000,],label=[ var for var in ['ggH(m1000) {}'.format(self.hits_ggh1000.values().sum()),'vbf(m1000) {}'.format(self.hits_vbf1000.values().sum())]],linestyle=[style for style in [':','--']], color=[color for color in colors])


            ##DATA
            data_err = get_err(hist_data)
            data = hist_data.values()
            hep.histplot(hist_data[hist.loc(30):hist.loc(70)],label='Data', histtype='errorbar', color='k', markersize=15, elinewidth=1.5)
            hep.histplot(hist_data[hist.loc(135):],histtype='errorbar', color='k', markersize=15, elinewidth=1.5)
            #plot_hist(hist_data,label='Data', histtype='errorbar', color='k', markersize=15, elinewidth=1.5) ## draw dat
            
            ##axvline and text
            #LSB and CR
            ax.text(50,max(data)*0.5,'C.R',fontweight='bold')
            ax.text(50,max(data),'S.R',fontweight='bold')
            #SR
            #ymax is  max value of y axis
            ymax = ax.get_ylim()[1]
            ax.axvline(x=70,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            ax.axvline(x=105,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            #ax.axvline(x=105,ymin = 0, ymax = 1.1*max(data),color = 'black',linestyle = '--')
            ax.text(84,max(data),'Signal',fontweight='bold')
            #remove
            ax.axvline(x=135,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            ax.text(113,max(data),'Remove',fontweight='bold')
            y = np.linspace(0,int(max(data)),100)
            ax.fill_betweenx(y,105,135,step='post',hatch='\\\\',facecolor='none',linewidth=0)
            #VR
            ax.axvline(x=165,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            ax.text(140,max(data),'Validation',fontweight='bold')
            #HSB and CR
            ax.text(160,max(data)*0.5,'C.R',fontweight='bold')
            ax.text(170,max(data),'S.B',fontweight='bold')

            if islogY:
                ax.set(yscale = "log")
                ax.set_ylim(1e-1, 3*ax.get_ylim()[1])
            else:
                ax.set_ylim(0, ax.get_ylim()[1])
                ax.set_ylim(0, 1.8*max(data))
            ax.text(0.85, 0.92, f'{setting().text[self.cat]}', transform=ax.transAxes, fontweight='bold') #leptonic cat text
            hep.plot.yscale_legend
            ax.legend(fontsize=18)
            ##==========================================Ratio panel========================
            ax1 = f.add_subplot(gs[1]); ax1.set_xlim(xmin, xmax); ax1.set_ylim(0.001, 1.999)
            ax1.set_xlabel(self.config['bininfo'][var][3], ha='right', x=1.0); ax1.set_ylabel('Data / MC', ha='center')
            ax1.plot([xmin,xmax], [1,1], 'k'); ax1.plot([xmin,xmax], [0.5,0.5], 'k:'); ax1.plot([xmin,xmax], [1.5,1.5], 'k:')
            ##axvline on ratio panel
            ymax = ax1.get_ylim()[1]
            ax1.axvline(x=70,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            ax1.axvline(x=105,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            ax1.axvline(x=135,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            ax1.axvline(x=165,ymin = 0, ymax = ymax,color = 'black',linestyle = '--')
            ##40-70
            data_h = hist_data[hist.loc(30):hist.loc(70)]
            data = data_h.values()
            data_err = get_err(data_h)

            bkg_tot_h = (hist_zv+hist_tt+hist_DY)[hist.loc(30):hist.loc(70)]
            bkg_tot_low = bkg_tot_h.values()

            ratio=np.nan_to_num((data/bkg_tot_low),nan=-1)
            ratio_err = np.nan_to_num((data_err/bkg_tot_low),nan=-1)

            #edge_low = np.linspace(40, 70, 5)
            #get edges from bkg_tot_h
            edge_low = bkg_tot_h.axes[0].edges
            print(ratio)
            print(ratio_err)
            print(edge_low)
            hep.histplot(ratio, yerr = ratio_err,bins=edge_low, histtype='errorbar', color='k', markersize=15, elinewidth=1)

            ##135-180
            data_h = hist_data[hist.loc(135):]
            data = data_h.values()
            data_err = get_err(data_h)

            bkg_tot_h = (hist_zv+hist_tt+hist_DY)[hist.loc(135):]
            bkg_tot_upper = bkg_tot_h.values()

            ratio=np.nan_to_num((data/bkg_tot_upper),nan=-1)
            ratio_err = np.nan_to_num((data_err/bkg_tot_upper),nan=-1)
            edge_upper = bkg_tot_h.axes[0].edges
            hep.histplot(ratio, yerr = ratio_err,bins=edge_upper, histtype='errorbar', color='k', markersize=15, elinewidth=1)
            ##
            y = np.linspace(0,2,10)
            ax1.fill_betweenx(y,105,135,step='post',hatch='\\\\',facecolor='none',linewidth=0)
            #hep.histplot(data/bkg_tot, yerr = data_err/bkg_err,bins=edge, histtype='errorbar', color='k', markersize=15, elinewidth=1)
            if plot_unce:
                ratio_unc_low = np.nan_to_num(((bkg_tot-bkg_err)/bkg_tot),nan=-1)
                ratio_unc_up = np.nan_to_num(((bkg_tot+bkg_err)/bkg_tot),nan=-1)
                ax1.fill_between(edge, ratio_unc_low.tolist()+[0],ratio_unc_up.tolist()+[0], step='post', hatch='\\\\', edgecolor='darkblue', facecolor='none', linewidth=0) ## draw bkg unce.

    def DrawVariableFromArray(self,arr,bins,start,stop,):
        filesets = setting().fileset[self.year]
        h = {}
        for sample in filesets.keys():
            path = filesets[sample]
            f = uproot.open(path[0])['sumWeights']
            sumWeight = (f.to_boost()).sum()
            f.close()
            xsec = self.config['samples_inf'][sample][1]

            h[sample] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
        pass
    
    def draw_variable_v2(self,hist):
        ###Set which var will be draw
        if self.varb!= None:
            varbs = self.varb
        elif(self.cutcat=='lep'):
            varbs = ['pt2l','mass2l','lep_1_pt','lep_2_pt','Nleptons','Ntightleptons']
        elif(self.cutcat=='resolved'):
            varbs = ['mass2jet','pt2jet','pt2l','mass2l','KD_jjVBF','mass2l2jet','KD_Zjj','Nleptons','Ntightleptons','mass2l2jet_allrange']
        elif(self.cutcat.find('merged') != -1):
            varbs = ['massmerged','ptmerged','pt2l','mass2l','KD_JVBF','particleNetZvsQCD','particleNetZbbvslight','mass2lj','KD_ZJ','Nleptons','Ntightleptons']
        
        for var in varbs:
            logger.info(f"It is {var} plot")
            if self.cutcat=='lep' or self.cutcat=='merged_notag':
                for cat in setting().leptonic_cut_cats:
                    self.cat = cat
                    for sample in self.plot_sample_lists:
                        self.sample = sample
                        self.plot_hist(hist,var)
        pass
    
    def DrawVariable(self,hist):
        ###Set which var will be draw
        if self.varb!= None:
            varbs = self.varb
        elif(self.cutcat=='lep'):
            varbs = ['pt2l','mass2l','lep_1_pt','lep_2_pt','Nleptons','Ntightleptons']
        elif(self.cutcat=='resolved'):
            varbs = ['mass2jet','pt2jet','pt2l','mass2l','KD_jjVBF','mass2l2jet','KD_Zjj','Nleptons','Ntightleptons','mass2l2jet_allrange']
        elif(self.cutcat.find('merged') != -1):
            varbs = ['massmerged','ptmerged','pt2l','mass2l','KD_JVBF','particleNetZvsQCD','particleNetZbbvslight','mass2lj','KD_ZJ','Nleptons','Ntightleptons']
            ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)

        for var in varbs:
            print(f"[INFO] it is {var} plot")   
            if self.cutcat=='lep' or self.cutcat=='merged_notag':
                for cat in setting().leptonic_cut_cats:
                    self.cat = cat
                    #add hist
                    hist_DY = hist[self.cutcat][f'DY_pt50To100_{cat}_{var}']+hist[self.cutcat][f'DY_pt100To250_{cat}_{var}'] \
                            +hist[self.cutcat][f'DY_pt250To400_{cat}_{var}']+hist[self.cutcat][f'DY_pt400To650_{cat}_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{cat}_{var}']
                    hist_tt = hist[self.cutcat][f'TTTo2L2Nu_{cat}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{cat}_{var}']
                    #hist_tt = hist[self.cutcat][f'TTJets_{cat}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{cat}_{var}']
                    hist_zv = hist[self.cutcat][f'WZTo2Q2L_{cat}_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{cat}_{var}']
                    hist_data = hist[self.cutcat][f'Data_{cat}_{var}']

                    if(self.plotSig):
                        #self.hits_ggh500 = hist[self.cutcat][f'ggh500_{reg}_{cat}_{tag}_{var}']
                        #self.hits_ggh3000 = hist[self.cutcat][f'ggh3000_{reg}_{cat}_{tag}_{var}']
                        self.hits_ggh1000 = hist[self.cutcat][f'ggh1000_{cat}_{var}']
                        self.hits_vbf1000 = hist[self.cutcat][f'vbf1000_{cat}_{var}']
                        #self.hits_ZH_HToBB = hist[self.cutcat][f'ZH_HToBB_{reg}_{cat}_{tag}_{var}']
                    self.plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data,var)

                    savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}'
                    if not os.path.exists(savepath):
                        #os.mkdir(savepath)
                        os.makedirs(savepath) #create subdirectory
                    plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}/{var}_{cat}.png')
                    #plt.show()
                    plt.close()

            else: # means resolved and merged_tag
                for reg in setting().regions:
                    if (reg == "ALL") and ((var!= 'massmerged') and (var!='mass2jet')): continue
                    #print(f"[INFO] it is {var} plot in full mass region")
                    for cat in setting().leptonic_cut_cats:
                        self.cat = cat
                        for tag in setting().tags:
                            #add hist
                            #in control region, plot mass2l2jet and mass2lj with DY coming from Data - other bkg
                            if reg == 'CR' and (var == 'mass2l2jet' or var == 'mass2lj'):
                                hist_data = hist[self.cutcat][f'Data_{reg}_{cat}_{tag}_{var}']
                                hist_tt = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}']
                                hist_zv = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{var}']

                                hist_DY = hist_data.copy()
                                hist_DY.view(flow=True).value = hist_DY.view(flow=True).value - hist_tt.view(flow=True).value - hist_zv.view(flow=True).value
                            else:
                                hist_DY = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_{var}'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_{var}']
                                hist_tt = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}']
                                #hist_tt = hist[self.cutcat][f'TTJets_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}']
                                hist_zv = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{var}']
                                
                                #if case is maerged_tag, apply PN SF to DY by scaling 1.18
                                if self.cutcat == 'merged_tag':
                                    hist_DY.view(flow=True).value = hist_DY.view(flow=True).value*self.particlenet_sf_dy

                            if reg != 'SR':
                                hist_data = hist[self.cutcat][f'Data_{reg}_{cat}_{tag}_{var}']
                            else:
                                hist_data = None

                            if(self.plotSig):
                                #self.hits_ggh500 = hist[self.cutcat][f'ggh500_{reg}_{cat}_{tag}_{var}']
                                #self.hits_ggh3000 = hist[self.cutcat][f'ggh3000_{reg}_{cat}_{tag}_{var}']
                                self.hits_ggh1000 = hist[self.cutcat][f'ggh1000_{reg}_{cat}_{tag}_{var}']
                                self.hits_vbf1000 = hist[self.cutcat][f'vbf1000_{reg}_{cat}_{tag}_{var}']
                                #self.hits_ZH_HToBB = hist[self.cutcat][f'ZH_HToBB_{reg}_{cat}_{tag}_{var}']

                            ##if(plotdatamc)
                            #self.plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data,hits_ggh1000,hits_vbf1000,var)
                            if reg=='ALL':
                               self. plot1DDataMCRegionALL(hist_zv,hist_tt,hist_DY,hist_data,var)
                            else:
                                self.plot1DDataMC(hist_zv,hist_tt,hist_DY,hist_data,var)

                            savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}'
                            if not os.path.exists(savepath):
                                os.makedirs(savepath)
                            plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}/{var}_{reg}_{cat}_{tag}.png')
                            #plt.show()
                            plt.close()

                            #if((var == 'mass2l2jet' or var == 'mass2lj') and reg == 'SR'):
                            #    hist_DY = hist[self.cutcat][f'DY_{reg}_{cat}_{tag}_massZZ']

                            #    self.plot1DDataMC(hist_zv,hist_tt,hist_DY,None,var)
                            #    savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{self.cutcat}/{self.year}'
                            #    if not os.path.exists(savepath):
                            #        os.mkdir(savepath)
                            #    plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/plots/{self.cutcat}/{self.year}/massZZ_{reg}_{cat}_{tag}.png')
                            #    #plt.show()
                            #    plt.close()
                            #plot up mean and dn comparison
                            #if var == 'pt2l' or var == 'mass2l' or self.varb != None or var.find('leptons')!=-1: continue
                            #else:
                            #    hist_mean = hist_DY + hist_tt + hist_zv

                            #    hist_DY_up = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_{var}_up']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_{var}_up'] \
                            #            +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_{var}_up']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_{var}_up']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_{var}_up']
                            #    hist_tt_up = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{var}_up']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}_up']
                            #    #hist_tt_up = hist[self.cutcat][f'TTJets_{reg}_{cat}_{tag}_{var}_up']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}_up']
                            #    hist_zv_up = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{var}_up']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{var}_up']
                            #    hist_up = hist_DY_up + hist_tt_up + hist_zv_up

                            #    hist_DY_dn = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_{var}_dn']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_{var}_dn'] \
                            #            +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_{var}_dn']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_{var}_dn']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_{var}_dn']
                            #    hist_tt_dn = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{var}_dn']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}_dn']
                            #    #hist_tt_dn = hist[self.cutcat][f'TTJets_{reg}_{cat}_{tag}_{var}_dn']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{var}_dn']
                            #    hist_zv_dn = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{var}_dn']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{var}_dn']
                            #    hist_dn = hist_DY_dn + hist_tt_dn + hist_zv_dn
                            #    #hist_data = hist[self.cutcat][f'Data_{reg}_{cat}_{tag}_{var}']

                            #    self.plotupdn(hist_mean,hist_up,hist_dn,var)

                            #    savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}'
                            #    if not os.path.exists(savepath):
                            #        os.mkdir(savepath)
                            #    plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}/{var}_{reg}_{cat}_{tag}_updn.png')
                            #    #plt.show()
                            #    plt.close()

    def run(self):
        if self.varb==None:
            hist = GetHisto(self.year,self.cutcat).hist
        #elif self.varb.find('mass2l2jet')!=-1 or self.varb.find('mass2lj')!=-1: 
        elif 'mass2l2jet' in self.varb or 'mass2lj' in self.varb:
            hist = GetHisto(self.year,self.cutcat,invarb=self.varb,option='masszz').hist
        else:
            option = None
            for var in self.varb:
                if var.find('mass2l2jet')!=-1 or var.find('mass2lj')!=-1:
                    option = 'masszz'
                    break
            if option != None:
                hist = GetHisto(self.year,self.cutcat,invarb=self.varb,option=option).hist
            else:
                hist = GetHisto(self.year,self.cutcat,invarb=self.varb).hist
        self.DrawVariable(hist)


########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
class PlotUpDn():
    def __init__(self,year,cutcat,varb=None) -> None:
        self.year = year
        self.cutcat = cutcat
        self.config = setting().config
        self.cat  = None
        #self.plotdir = 'plotnew'
        self.plotdir = setting().plot_store_dir_name
        self.varb = varb
        self.hits_ggh500 = None
        self.hits_ggh1000 = None
        self.hits_ggh3000 = None
        self.hits_ZH_HToBB = None
        #self.plotSig = True
        self.plotSig = False

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
    
    def plotUpDown(self,hist_mean,hist_up,hist_dn,var):
        if var.find('pt')!=-1 or var.find('massmerged')!=-1 or var.find('mass2jet')!=-1 or var.find('mass2jl')!=-1 or var.find('mass2l2jet')!=-1:
            islogY = False
        else:
            islogY = False
        nbins, xmin, xmax = self.config['bininfo_resolved_split']['jet_1_pt'][0], self.config['bininfo_resolved_split']['jet_1_pt'][1], self.config['bininfo_resolved_split']['jet_1_pt'][2]
        f, ax = plt.subplots(figsize=(12,12))
        hep.cms.label(data=True, llabel='Preliminary',year=self.year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)'%self.config['lumi'][self.year], fontname='sans-serif')
        ax.set_xlim(xmin, xmax); ax.set_ylabel('Events / bin', ha='right', y=1.0)

        plot_hist([hist_mean,hist_up,hist_dn],label=[f'{var} ({varb})' for varb in ['mean','up','donw']],histtype='step', linewidth=0.5, stack=False) ## draw MC

        if islogY:
            ax.set(yscale = "log")
            ax.set_ylim(1e-0, 3*ax.get_ylim()[1])
        ax.set_xlabel(self.config['bininfo_resolved_split']['jet_1_pt'][3], ha='right', x=1.0)
        ax.legend(fontsize=18)

    def DrawSplitUnc(self,hist):
        ###Set which var will be draw
        if self.varb!= None:
            varbs = [self.varb]
        elif(self.cutcat=='lep'):
            varbs = None
        elif(self.cutcat=='resolved'):
            varbs = ['Total','Abs', 'Abs_year', 'BBEC1', 'BBEC1_year', 'EC2', 'EC2_year', 'FlavQCD', 'HF', 'HF_year', 'RelBal', 'RelSample_year']
        elif(self.cutcat.find('merged') != -1):
            varbs = None

        for var in varbs:
            print(f"[INFO] it is {var} plot")
            if self.cutcat=='resolved' or self.cutcat=='merged_tag':
                for reg in setting().regions:
                    for cat in setting().leptonic_cut_cats:
                        self.cat = cat
                        for tag in setting().tags:

                            hist_mean = {}; hist_up = {}; hist_dn = {}
                            
                            hist_mean["DY"] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jet_1_pt'] \
                                    +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jet_1_pt'] \
                                    +hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jet_2_pt'] \
                                    +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jet_2_pt']
        
                            hist_up['DY'] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                    +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                    +hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}'] \
                                    +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']  
                                     
                            hist_dn['DY'] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                    +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                    +hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}'] \
                                    +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']

                            hist_mean['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jet_1_pt'] + hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jet_1_pt'] \
                                           +hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jet_2_pt'] + hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jet_2_pt']
                            
                            hist_up['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                           +hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                            
                            hist_dn['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                           +hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']

                            hist_mean['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jet_1_pt'] \
                                         + hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jet_2_pt']
                            
                            hist_up['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                         + hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                            
                            hist_dn['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                         + hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']

                            hist_mean['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jet_1_pt'] + hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jet_2_pt']
                            hist_up['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] + hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                            hist_dn['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] + hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']

                            hist_mean['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jet_1_pt'] + hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jet_2_pt']
                            hist_up['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] + hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                            hist_dn['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] + hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']
         

                            savepath = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}'
                            if not os.path.exists(savepath):
                                 os.makedirs(savepath)
                            for sample in ['DY','zv','tt','ggh','vbf']:
                                self.plotUpDown(hist_mean[sample],hist_up[sample],hist_dn[sample],var)
                                plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot/{self.plotdir}/{self.cutcat}/{self.year}/{sample}_{var}_{reg}_{cat}_{tag}.png')
                                #plt.show()
                                plt.close()
    
    def run(self):
        hist = GetHisto(self.year,self.cutcat).hist
        #self.DrawSplitUnc(hist)
        #hist = GetHisto(self.year,self.cutcat).hist
        self.DrawVariable(hist)
