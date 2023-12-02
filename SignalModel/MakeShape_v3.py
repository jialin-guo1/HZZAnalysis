#from ROOT import *
import ROOT
import math
import sys
#import uproot
import numpy as np

sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
#from setting import setting
import argparse
parser = argparse.ArgumentParser(description="Rasahpe Higgs gen to guass")
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-s","--sample",dest="sample",default='ggh', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
args = parser.parse_args()

#########=======================initial Variables=========================
sample = args.sample
year = args.year; reg = "SR" #samples = ['ggh','vbf'];
#reco_root_file_path = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{}.root'.format(year)
reco_root_file_path = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{}_signal.root'.format(year)
print("open file {}".format(reco_root_file_path))
varbs = {
            'resolved':'mass2l2jet_fit',
            'merged_tag':'mass2lj_fit'
}
cutcats = ['resolved','merged_tag']
tags = ['btag','untag','vbftag','all']
#channels = ['isEE','isMuMu','2lep']
channels = ['isEE','isMuMu']#,'2lep']
leptonic_cut_cats=['isEE','isMuMu','2lep']

#massList = []
#for mass in range(200,1000,50):
#    massList.append(mass)
#for mass in range(1000,1600,100):
#    massList.append(mass)
#for mass in range(1600,3400,200):
#    massList.append(mass)

massList = [200,250,300,350,400,450,500,550,600,700,750,800,900,1500,2000,2500,3000]

#########=======================reweight function=========================
def reshape(hist,mean,width):
    h = ROOT.TH1D('h','h',4000,0,4000); h.Sumw2()
    h.FillRandom("gaus",int(hist.Integral()))
    h.Divide(hist)
    return h

def drawHisto(h,str):
    c = ROOT.TCanvas('c','c',800,800)
    h.Draw()
    h.SetTitle(str)
    h.GetYaxis().SetTitle("Events/(1 GeV)")
    h.GetXaxis().SetTitle("massZZ(GeV)")
    h.SetMinimum(0)
    cms_label = ROOT.TLatex(); cms_label.SetTextSize(0.03);cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
    c.SaveAs("./plots/{}/{}.png".format(args.year,str))

##########out file
#out_file = {}
#for sample in samples:
#    out_file[sample] = uproot.recreate('Histos_MakeShape_{}_{}.root'.format(sample,year))
#out_file = uproot.recreate('Histos_MakeShape_{}_{}.root'.format(sample,year))
out_file = ROOT.TFile('./Histos_MakeShape_{}_{}_{}.root'.format(sample,year,'individual'),'recreate')
out_file.cd()

###get histos
hist = {}
input_file = ROOT.TFile(reco_root_file_path,'READ')
for mass in massList:
    print("[INFO] This is mass {}".format(mass))
    sample  = args.sample+str(mass)
    hist_gen = input_file.Get('{}/nevents'.format(sample))
    print("[INFO] the total number of events is {}".format(hist_gen.Integral()))
    out_file.cd()
    hist_gen.Write('gen_hist_{}'.format(sample))
    for cutcat in cutcats:
        hist[cutcat] = {}
        for cat in leptonic_cut_cats:
            for tag in tags:
                #hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varbs[cutcat]}'] = input_file.Get(f'{sample}/{cutcat}/{reg}/{cat}/{tag}/{varbs[cutcat]}')
                hist[cutcat]['{}_{}_{}_{}_{}'.format(sample,reg,cat,tag,varbs[cutcat])] = input_file.Get('{}/{}/{}/{}/{}/{}'.format(sample,cutcat,reg,cat,tag,varbs[cutcat]))

                out_file.cd()
                #hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varbs[cutcat]}'].Write(f'reshape_{cat}_{cutcat}_{tag}_{massList[i]}')
                hist[cutcat]['{}_{}_{}_{}_{}'.format(sample,reg,cat,tag,varbs[cutcat])].Write('reshape_{}_{}_{}_{}'.format(cat,cutcat,tag,mass))
                #out_file[f'reshape_{cat}_{cutcat}_{tag}_{massList[i]}'] = hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varbs[cutcat]}']

out_file.Write(); out_file.Close()

#print output file name 
print("[INFO] Output file name: {}".format(out_file.GetName()))
#for sample in samples:
#    out_file[sample].Write()

#for sample in samples:
#    for cutcat in cutcats:
#        print(hist[cutcat].keys())
#        n_gen_events = hist[cutcat][f'{sample}_GEN_H1_mass'].Integral()
#        for cat in leptonic_cut_cats:
#            for tag in tags:
#


                    






