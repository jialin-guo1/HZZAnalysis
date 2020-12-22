
import os
import Plot_Configs as PC
import Analyzer_Configs as AC
from ROOT import *

#####################################################################

def LoadNtuples(ana_cfg):
    ntuples = {}
    print " list of samp_names = "+str(ana_cfg.samp_names)
    for sample in ana_cfg.samp_names:
        if(sample=='data'):
            print "will open data file"
            #tmpfile = TFile(ana_cfg.sample_loc + '/2018_noDuplicates.root')
            ntuples[sample] = TChain("passedEvents","chain_" + sample)
            ntuples[sample]. Add(ana_cfg.sample_loc + '/2018_noDuplicates.root')

        else:
            print "will open file"+ana_cfg.sample_loc + '/%s_2018.root' %sample
            #tmpfile = TFile(ana_cfg.sample_loc + '/%s_2018.root' %sample)
	    ntuples[sample] = TChain("Ana/passedEvents","chain_" + sample)
            ntuples[sample]. Add(ana_cfg.sample_loc + '/%s_2018.root' %sample)
        if(ntuples[sample]):
            print " number of events = " + str(ntuples[sample].GetEntries())
            print " do a loop testing"
            for ievent,event in enumerate(ntuples[sample]):
                if ievent==1: break
                print " success to loop %s sample "%sample

    return ntuples


def MakeStack(histos, ana_cfg, var_name):
    stacks = {}
    stacks['data']  = THStack("h_stack_"+var_name, var_name)
    stacks['sig']  = THStack("h_stack_"+var_name, var_name)
    stacks['bkg']  = THStack("h_stack_"+var_name, var_name)
    stacks['data'].Add(histos['data'])
    for sample in ana_cfg.sig_names:
        stacks['sig'].Add(histos[sample])
    #    stacks['all'].Add(histos[sample])
    for sample in ana_cfg.bkg_names:
        stacks['bkg'].Add(histos[sample])
    #    stacks['all'].Add(histos[sample])
    return stacks


def CreateCanvas(canv_name):
    canv = TCanvas(canv_name, canv_name,800,800)
    return canv


def MakeLumiLabel(lumi):
    tex = TLatex()
    tex.SetTextSize(0.035)
    tex.SetTextAlign(31)
    tex.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)' %lumi)
    return tex


def MakeCMSDASLabel():
    tex = TLatex()
    tex.SetTextSize(0.03)
    tex.DrawLatexNDC(0.15, 0.85, '#scale[1.5]{CMS}preliminary')
    return tex

def MakeDataLabel(stack_data,cat_name):
    histo = stack_data.GetStack().Last()
    histo.GetXaxis().SetTitle('m_{%s}'%cat_name)
    #histo.GetXaxis().SetTitleSize(0.20)
    histo.GetYaxis().SetTitle('Events / %.2f' %histo.GetBinWidth(1))
    #histo.GetYaxis().SetTitleSize(0.20)
    return histo



def ScaleSignal(plt_cfg,stack_sig,var_name):
    sig_hist = stack_sig.GetStack().Last()
    sig_hist.Scale(plt_cfg.sig_scale)
    sig_hist.SetLineColor(kRed)
    sig_hist.SetLineWidth(2)
    sig_hist.SetFillStyle(0)

    sig_hist.GetXaxis().SetTitle(var_name)
    sig_hist.GetXaxis().SetTitleSize(0.20)
    sig_hist.GetYaxis().SetTitle('Events / %.2f' %sig_hist.GetBinWidth(1))
    sig_hist.GetYaxis().SetTitleSize(0.20)
    return sig_hist

def MakeRatioPlot(h_data, h_MC, var_name):
    ratio_plot = TGraphAsymmErrors()
    ratio_plot.Divide(h_data, h_MC, "pois")
    ratio_plot.SetName("ratiograph_" + var_name)
    ratio_plot.SetMinimum(0.4)
    ratio_plot.SetMaximum(2.0)
    ratio_plot.SetMarkerStyle(20)

    ratio_plot.GetXaxis().SetRangeUser( h_data.GetXaxis().GetXmin(), h_data.GetXaxis().GetXmax() )
    ratio_plot.GetXaxis().SetLabelSize(0.15)
    ratio_plot.GetXaxis().SetTitle(var_name)
    ratio_plot.GetXaxis().SetTitleSize(0.20)
    ratio_plot.GetXaxis().SetTitleOffset(0.5)

    ratio_plot.GetYaxis().SetNdivisions(505)
    ratio_plot.GetYaxis().SetLabelSize(0.13)
    ratio_plot.GetYaxis().SetTitle("Data/MC")
    ratio_plot.GetYaxis().SetTitleSize(0.20)
    ratio_plot.GetYaxis().SetTitleOffset(0.2)

    return ratio_plot


def MakeLegend(plt_cfg, histos):
    legend = TLegend(0.65,0.65,0.85,0.85)
    legend.SetNColumns(1)
    legend.SetLineColor(10)

    legend.AddEntry(histos["data"], "data")
    #for sample in plt_cfg.ana_cfg.sig_names:
    #    legend.AddEntry(histos[sample], sample )
    #    legend.AddEntry(scaled_signal, "signal X%d" %plt_cfg.sig_scale)
    for sample in plt_cfg.ana_cfg.bkg_names:
        legend.AddEntry(histos[sample],sample,"f")
    return legend


def DrawOnCanv(canv, var_name, plt_cfg, stacks, histos, scaled_sig,legend, lumi_label, cms_label):
    canv.cd()
    #histos['data'].GetXaxis().SetTitle(var_name)
    #hist.GetXaxis().SetTitleSize(0.20)
    #histos['data'].GetYaxis().SetTitle('Events / %.2f' %histos['data'].GetBinWidth(1))
    #hist.GetYaxis().SetTitleSize(0.20)
    #upper_pad = TPad("upperpad_"+var_name, "upperpad_"+var_name, 0,0.2, 1,1)
    #upper_pad.SetBottomMargin(0.05)
    #upper_pad.Draw()
    #upper_pad.cd()
    #if plt_cfg.logY:
        #upper_pad.SetLogy()
    	#stacks['all'].SetMinimum(1e-1)
        #stacks['all'].SetMaximum(1e8)
    #c2 = TCanvas()
    histos['data'].Draw('PE')
    stacks['bkg'].Draw("same histo")
    #histos['data'].SetMarkerStyle(20)
    histos['data'].Draw('SAME PE')
    #c2.SaveAs("plot/test.png")
    #scaled_sig.Draw('SAMEPE')
    #print "type of stacks = " + str(type(stacks['bkg']))

    legend.Draw()
    cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
    cms_label.Draw('same')
    lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)' %plt_cfg.lumi)
    lumi_label.Draw('same')
    #histos['data'].Draw('SAME PE')
    #scaled_sig.Draw('SAMEPE')
    #histos['data'].Draw('SAME E1')

    #canv.cd()
    #lower_pad = TPad("lowerpad_"+var_name, "lowerpad_"+var_name, 0, 0, 1,0.2)
    #lower_pad.SetTopMargin(0.05)
    #lower_pad.SetGridy()
    #lower_pad.Draw()
    #lower_pad.cd()
    #ratio_plot.Draw()


def SaveCanvPic(canv, save_dir, save_name):
    canv.cd()
    #canv.SaveAs(save_dir + '/' + save_name + '.pdf')
    canv.SaveAs(save_dir + '/' + save_name +'OS2018' + '.png')
