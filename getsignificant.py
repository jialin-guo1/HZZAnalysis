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

massList = []
for mass in range(500,1000,50):
    massList.append(mass)
for mass in range(1000,1600,100):
    massList.append(mass)
for mass in range(1600,3200,200):
    massList.append(mass)

use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
if use_helvet:
    CMShelvet = hep.style.CMS
    CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.style.use(CMShelvet)
else:
    plt.style.use(hep.style.CMS)

#setMcDataPlotsColor
def set_sns_color(*args):
   sns.palplot(sns.color_palette(*args))
   sns.set_palette(*args)
   pass
color_order_bkg = sns.color_palette('Accent', 3)
color_order_bkg.reverse()
set_sns_color(color_order_bkg)


year = '2018'; cutcat = 'resloved'
cat = '2lep'
tag = 'all'
reg = 'SR'

inbkgfile = uproot.open(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{year}.root')

varb = 'mass2l2jet_rebin'
hist_bkg = None
hist_sig = None

#add TTbar and vz
samplelist = ['TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L']
#with uproot.open(inbkgfile) as file:
for sample in samplelist:
    print(f'[INFO] Add {sample}')
    if(hist_bkg==None):
        hist_bkg = inbkgfile[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_hist()
    else:
        hist_bkg += inbkgfile[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_hist()
#add DY
sample = 'DY'
varb = 'massZZ'
hist_bkg += inbkgfile[f'{sample}_resolved_{reg}_{cat}_{tag}_{varb}'].to_hist()

#bkgtot = hist_bkg[].values().sum()
bkgtot = hist_bkg[hist.loc(450),hist.loc(4000)].values().sum()

insigfile = uproot.open(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/Histos_sig_{year}.root')
y = []
for mass in massList:
    case = 'resolved;1'
    #hist_sig = insigfile['sig{}_{}'.format(mass,case)].to_hist()
    str = f"sig{mass}_resolved;1"
    hist_sig = insigfile[str].to_hist()
    #hist_sig = insigfile[f"sig{mass}_resolved;1"].to_hist()
    sigtot = hist_sig.values().sum()

    #compute
    significant = sigtot/math.sqrt(sigtot+bkgtot)
    y.append(significant)
#mass = 500
#str = f"sig{mass}_resolved;1"
#hist_sig = insigfile[str].to_hist()
######
#bkgcontent = hist_bkg.values()
#sigcontent = hist_bkg.values()

#y = sigcontent/





f, ax = plt.subplots(figsize=(10, 10))
hep.cms.label(data=True, llabel='Preliminary', year=year, ax=ax, rlabel=r'%s $fb^{-1}$ (13 TeV)' %setting().config['lumi'][year], fontname='sans-serif')
ax.plot(massList,y,'ro:',label = 'significant', linewidth = 2,markersize=1)
ax.set_xlabel(r'$M_{ZZ}$ [GeV]', ha='right', x=1.0)
ax.set_ylabel('Significant', ha='right', y=1.0)
ax.legend(loc='upper right') 
plt.savefig(f'./significant_resolved.png')
plt.close()
        