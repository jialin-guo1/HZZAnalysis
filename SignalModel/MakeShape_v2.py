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
varbs = {
            'resolved':'mass2l2jet_fit',
            'merged_tag':'mass2lj_fit'
}
cutcats = ['resolved','merged_tag']
tags = ['btag','untag','vbftag','all']
#channels = ['isEE','isMuMu','2lep']
channels = ['isEE','isMuMu']#,'2lep']
leptonic_cut_cats=['isEE','isMuMu','2lep']

massList = []
for mass in range(200,1000,50):
    massList.append(mass)
for mass in range(1000,1600,100):
    massList.append(mass)
for mass in range(1600,3800,200):
    massList.append(mass)

massList = [600]

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
out_file = ROOT.TFile('./Histos_MakeShape_{}_{}_{}.root'.format(sample,year,'1GeVbin'),'recreate')
out_file.cd()

###get histos
hist = {}
input_file = ROOT.TFile(reco_root_file_path,'READ')
hist_gen  = input_file.Get('{}/GEN_H1_mass'.format(sample))
drawHisto(hist_gen,'Gen_Higgs')
out_file.cd(); hist_gen.Write('gen_hist')
#out_file['gen_hist'] = hist_gen
n_gen_events = hist_gen.Integral()
for cutcat in cutcats:
    hist[cutcat] = {}
    #for sample in samples:
    #hist[cutcat][f'{sample}_GEN_H1_mass'] = input_file.Get(f'{sample}/GEN_H1_mass')
    #n_gen_events = hist[cutcat][f'{sample}_GEN_H1_mass'].Integral()
    for cat in leptonic_cut_cats:
        for tag in tags:
            #hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varbs[cutcat]}'] = input_file.Get(f'{sample}/{cutcat}/{reg}/{cat}/{tag}/{varbs[cutcat]}')
            hist[cutcat]['{}_{}_{}_{}_{}'.format(sample,reg,cat,tag,varbs[cutcat])] = input_file.Get('{}/{}/{}/{}/{}/{}'.format(sample,cutcat,reg,cat,tag,varbs[cutcat]))
            for i,mass in enumerate(massList):
                if(massList[i]>0):
                    width = massList[i]*0.03
                    #####
                    #h_gaus = ROOT.TH1D(f'{cutcat}_{mass}',f'{cutcat}_{mass}',400,0,4000)
                    h_gaus = ROOT.TH1D('{}_{}'.format(cutcat,mass),'{}_{}'.format(cutcat,mass),4000,0,4000)
                    h_gaus.FillN(int(n_gen_events),np.random.normal(loc=mass, scale=width, size=int(n_gen_events)),np.ones(int(n_gen_events)))
                    drawHisto(h_gaus,'Gaus_{}'.format(mass))
                    #print(f'sum of gen events  = {n_gen_events}')
                    #for j in range(int(n_gen_events)):
                    #    x = gRandom.Gaus(mass,width)
                    #    h_gaus.Fill(x)
                    #print(f'sum of gaus = {h_gaus.Integral()}')
                    h_gaus.Divide(hist_gen)
                    drawHisto(h_gaus,'Weight_{}'.format(mass))
                    #print(f'sum of weight = {h_gaus.Integral()} ')
                    #####
                    #h_out = hist[cutcat][f'{sample}_{reg}_{cat}_{tag}_{varbs[cutcat]}'.format].Clone()
                    h_out = hist[cutcat]['{}_{}_{}_{}_{}'.format(sample,reg,cat,tag,varbs[cutcat])].Clone()
                    drawHisto(h_out,'RecoRaw_{}_{}_{}_{}'.format(cutcat,cat,tag,mass))
                    #h_out.Sumw2()

                    h_out.Multiply(h_gaus)
                    out_file.cd()
                    #h_out.Write(f'reshape_{cat}_{cutcat}_{tag}_{massList[i]}')
                    h_out.Write('reshape_{}_{}_{}_{}'.format(cat,cutcat,tag,massList[i]))
                    #out_file[f'reshape_{cat}_{cutcat}_{tag}_{massList[i]}'] = h_out

out_file.Write(); out_file.Close()
#for sample in samples:
#    out_file[sample].Write()

#for sample in samples:
#    for cutcat in cutcats:
#        print(hist[cutcat].keys())
#        n_gen_events = hist[cutcat][f'{sample}_GEN_H1_mass'].Integral()
#        for cat in leptonic_cut_cats:
#            for tag in tags:
#


                    






