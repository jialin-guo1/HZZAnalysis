#from typing import Text
import ROOT
from array import array

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
parser.add_argument("-c","--cat",dest="cat",default='tt', help="choose cat to decide wichle cut selection will be used. Options: lep,ak4,ak8,net")
args = parser.parse_args()

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(1111); ROOT.gStyle.SetStatBorderSize(0)
ROOT.gStyle.SetStatX(.4); ROOT.gStyle.SetStatY(.89)
c = ROOT.TCanvas('c','c',1000,800)

mzz_name = "zz2l2q_mass"
#inputfile = ROOT.TFile("Histos_sig.root")
inputfile = ROOT.TFile("Histos_sig_{}.root".format(args.year))
#massList = [500,600,700,800,900,1000,1500,2500,3000]
massList = []
for mass in range(500,1000,50):
    massList.append(mass)
for mass in range(1000,1600,100):
    massList.append(mass)
for mass in range(1600,3000,200):
    massList.append(mass)
#massList = [500]
parmList = ['mean','sigma','a1','a2','n1','n2']
cases = ['merged','resolved']
#case = 'merged'
sam = 'sig'

#intial Parm TGraphError
for case in cases:

    parm_graph = {}
    parm_graphX = array('f',massList); parm_graphXerr = array('f',[])
    for i in parm_graphX:
        parm_graphXerr.append(0)
    parm_graphY = {}; parm_graphYerr = {}
    for p in parmList:
        parm_graphY[p] = array('f',[])
        parm_graphYerr[p] = array('f',[])
    for mass in massList:
        print "[INFO] fit to {}".format(mass)

        #Set fit histo and fit function
        low_M = mass-500; high_M = mass+500
        bins = int((high_M-low_M)/10)
        zz2l2q_mass = ROOT.RooRealVar(mzz_name,mzz_name,low_M,high_M)
        zz2l2q_mass.setBins(bins)

        mean = ROOT.RooRealVar('mean','',mass,mass-500,mass+500)
        sigma = ROOT.RooRealVar('sigma','',0,120)
        a1 = ROOT.RooRealVar('a1','',0,10)
        a2 = ROOT.RooRealVar('a2','',0,10)
        n1 = ROOT.RooRealVar('n1','',0,25)
        n2 = ROOT.RooRealVar('n2','',0,25)

        signalCB_ggH = ROOT.RooDoubleCB('signalCB_ggH','signalCB_ggH',zz2l2q_mass,mean,sigma,a1,n1,a2,n2)

        #h = inputfile.Get('ggh{}_merged'.format(mass))
        h = inputfile.Get('{}{}_{}'.format(sam,mass,case))
        roo_h = ROOT.RooDataHist("sig","sig",ROOT.RooArgList(zz2l2q_mass),h)
        #Fit 
        signalCB_ggH.fitTo(roo_h)
        #retrieve Parm
        mean_fit_val = mean.getVal(); sigma_fit_val = sigma.getVal(); a1_fit_val = a1.getVal(); a2_fit_val = a2.getVal(); n1_fit_val = n1.getVal(); n2_fit_val = n2.getVal()
        mean_fit_err = mean.getError(); sigma_fit_err = sigma.getError(); a1_fit_err = a1.getError(); a2_fit_err = a2.getError(); n1_fit_err = n1.getError(); n2_fit_err = n2.getError()

        parm_graphY['mean'].append(mean_fit_val); parm_graphY['sigma'].append(sigma_fit_val); parm_graphY['a1'].append(a1_fit_val); parm_graphY['a2'].append(a2_fit_val); parm_graphY['n1'].append(n1_fit_val); parm_graphY['n2'].append(n2_fit_val)
        parm_graphYerr['mean'].append(mean_fit_err); parm_graphYerr['sigma'].append(sigma_fit_err); parm_graphYerr['a1'].append(a1_fit_err); parm_graphYerr['a2'].append(a2_fit_err); parm_graphYerr['n1'].append(n1_fit_err); parm_graphYerr['n2'].append(n2_fit_err)

        #======================================================plot fit======================================================================
        frame_massZZ = zz2l2q_mass.frame()
        roo_h.plotOn(frame_massZZ)
        signalCB_ggH.plotOn(frame_massZZ,ROOT.RooFit.LineColor(ROOT.EColor.kBlue))
        #signalCB_ggH.paramOn(frame_massZZ,roo_h,"",1,"NELU",0.6,0.9,0.9)

        frame_massZZ.SetTitle("DoubleCB Fit on Mass2l2q"); frame_massZZ.SetTitleSize(0.02)
        frame_massZZ.GetXaxis().SetTitle('mass2l2q'); frame_massZZ.GetXaxis().SetTitleSize(0.025); frame_massZZ.GetXaxis().SetLabelSize(0.025)
        frame_massZZ.GetYaxis().SetTitle("Events/(10 GeV)"); frame_massZZ.GetYaxis().SetTitleSize(0.025); frame_massZZ.GetYaxis().SetLabelSize(0.025)
        frame_massZZ.Draw()

        cms_label = ROOT.TLatex(); cms_label.SetTextSize(0.03);cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        lumi_label = ROOT.TLatex(); lumi_label.SetTextSize(0.03); lumi_label.DrawLatexNDC(0.80, 0.91, '%s fb^{-1} (13 TeV)'%str(36.33))
        ##Draw Parm
        parm_text = ROOT.TLatex(); parm_text.SetNDC(); parm_text.SetTextSize(0.03); parm_text.SetTextFont(42); parm_text.SetTextAlign(23)
        parm_text.DrawLatexNDC(0.78,0.88,"mean = %s"%mean_fit_val)
        parm_text.DrawLatexNDC(0.78,0.85,"sigma = %s"%sigma_fit_val)
        parm_text.DrawLatexNDC(0.78,0.82,"a1 = %s"%a1_fit_val)
        parm_text.DrawLatexNDC(0.78,0.79,"a2 = %s"%a2_fit_val)
        parm_text.DrawLatexNDC(0.78,0.76,"n1 = %s"%n1_fit_val)
        parm_text.DrawLatexNDC(0.78,0.73,"n2 = %s"%n2_fit_val)  
        c.SaveAs("./plots/{}/Fit_mH{}_{}.png".format(args.year,mass,case))
    c.Close()
    #======================================================plot Parms Graph======================================================================

    f = ROOT.TFile("2l2q_resolution_{}_{}.root".format(case,args.year),"recreate")
    f.cd()
    colorList = [ROOT.EColor.kGreen,ROOT.EColor.kYellow+2,ROOT.EColor.kRed,ROOT.EColor.kMagenta,ROOT.EColor.kBlue,ROOT.EColor.kCyan]; i=0
    MultiGraph = ROOT.TMultiGraph()
    leg = ROOT.TLegend( .64, .65, .97, .85 )
    for p in parmList:
        c1 = ROOT.TCanvas('c1','c1',1000,800)
        parm_graph[p] = ROOT.TGraphErrors(len(parm_graphX ),parm_graphX,parm_graphY[p],parm_graphXerr,parm_graphYerr[p])
        parm_graph[p].SetMarkerSize(1)
        parm_graph[p].SetMarkerStyle(20)
        parm_graph[p].SetLineColor(colorList[i]) ; i +=1
        if p!='mean':
            leg.AddEntry(parm_graph[p],'{}'.format(p),"l")
            MultiGraph.Add(parm_graph[p],'PL')
        parm_graph[p].Fit("pol5","qw")
        parm_graph[p].SetTitle("{}_{}".format(p,case))
        parm_graph[p].GetXaxis().SetTitle("M_{2l2q} [GeV]")
        parm_graph[p].Draw()

        #force drawing of canvas to generate the fit TPaveStats
        c1.Update()
        stats = parm_graph[p].GetListOfFunctions().FindObject("stats")
        stats.SetX1NDC(0.12); stats.SetX2NDC(0.40); stats.SetY1NDC(0.75)
        c1.Modified()

        parm_graph[p].Write(p)
        c1.SetTitle("{}_{}".format(p,case))
        c1.SaveAs("./plots/{}/Fit_{}_{}.png".format(args.year,p,case))
        c1.SaveAs("./plots/{}/Fit_{}_{}.pdf".format(args.year,p,case))
        c1.Close()

    c1 = ROOT.TCanvas('c1','c1',1000,800)
    MultiGraph.Draw("ap")
    MultiGraph.GetXaxis().SetTitle('M_2l2q [GeV]')
    MultiGraph.GetYaxis().SetTitle("parms"); MultiGraph.GetYaxis().SetTitleSize(0.025)
    MultiGraph.SetTitle('Parms')
    leg.Draw()

    c1.SaveAs('./plots/{}/parms_{}.png'.format(args.year,case))
    c1.Close()


    f.Write()



