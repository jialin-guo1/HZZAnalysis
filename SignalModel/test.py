import ROOT
from ROOT import RooAbsPdf, RooRealProxy, RooListProxy, RooArgList, RooRealVar, TSpline3
from math import pow

#load C++ library
ROOT.gInterpreter.ProcessLine('#include "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/SplinePdf.h"')

# input spline file
f_spline_ggh = ROOT.TFile("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/GeliangShare/public/h4l_highmass/ggf_input_spline.root")
f_spline_vbf = ROOT.TFile("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/GeliangShare/public/h4l_highmass/vbf_input_spline.root")

# load splines
spline_ggh = f_spline_ggh.Get("sp_xsec_ggf_2e2mu")
spline_vbf = f_spline_vbf.Get("sp_xsec_vbf_2e2mu")

#define RooRealVar
low_mass = 0; high_mass = 3500; current_mass = 1000; this_width = 700
bw_m4l = 0.5

mass_range = ROOT.RooRealVar('mass_range','mass_range',low_mass,high_mass)
width = ROOT.RooRealVar('width','width',this_width,0,100)
mass_2l2q = ROOT.RooRealVar('mass_2l2q','mass_2l2q',current_mass,low_mass,high_mass)
mass_gen = ROOT.RooRealVar('mass_gen','mass_gen',low_mass,high_mass)

# create SplinePdf
higgspdf = ROOT.SplinePdf("higgspdf","higgspdf",mass_gen,mass_2l2q,width,spline_ggh)

# test pdf
nbins = 3500
hsig_2l2q = ROOT.TH1F('hsig_2l2q','hsig_2l2q',nbins,low_mass,high_mass)
for ib in range(1,4*nbins+1):
    x = hsig_2l2q.GetBinCenter(ib)
    mass_gen.setVal(x)
    mass_gen_set = ROOT.RooArgSet(mass_gen)
    if(((x<current_mass-3*this_width) & (x<current_mass-0.5*bw_m4l)) | ((x>current_mass+3*this_width) & (x>current_mass+0.5*bw_m4l)) | (this_width>10*bw_m4l)):
        bc = higgspdf.getVal(mass_gen_set)
        bc_range = higgspdf.getVal(mass_gen_set)*bw_m4l
    else:
        bc = 0
        bc_range = 0
        for j in range(-500,500):
            xx = current_mass + j*0.02*this_width
            if(xx>x-bw_m4l*0.5 & xx<=x+bw_m4l*0.5):
                mass_gen.setVal(xx)
                mass_gen_set = ROOT.RooArgSet(mass_gen)
                bc += higgspdf.getVal(mass_gen_set)
                bc_range += higgspdf.getVal(mass_gen_set)*0.02*this_width
    if bc<0: bc = 0
    hsig_2l2q.SetBinContent(ib,bc)
print("Integral of signal pdf: ", hsig_2l2q.Integral())
#plot histogram
c = ROOT.TCanvas('c','c',800,600)
hsig_2l2q.Draw()
c.Draw()
c.SaveAs('test_histo.png')
c.Close()

# save histogram in root file
f = ROOT.TFile('test_histo.root','recreate')
hsig_2l2q.Write()
f.Close()

#plot pdf
#c = ROOT.TCanvas('c','c',800,600)
#frame = mass_2l2q.frame()
#higgspdf.plotOn(frame)
#frame.Draw()
#c.Draw()
#
##save plot 
#c.SaveAs('test.png')
