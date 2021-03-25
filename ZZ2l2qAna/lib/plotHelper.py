from ROOT import *
import time


class plotHelper:

    def __init__(self,samples,year):
        #attribute
        gStyle.SetOptStat(False)
        self.year = year
        self.lumi = 0.0
        self.trees={}
        self.sumWeights = {}
        self.sample_names = samples
        self.sample_paths = ["/cms/user/guojl/Sample/ZZ_TuneCP5_13TeV-pythia8_RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2_skimed.root",
                              "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIISummer19UL17MiniAOD-106X_skimed.root",
                              "/cms/user/guojl/Sample/WW_TuneCP5_13TeV-pythia8_RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2_skimed.root"]
        self.colors = {}
        self.Constructor()

    def Constructor(self):
        for sample_path in self.sample_paths:
            for sample_name in self.sample_names:
                if(sample_path.find(sample_name)!=-1):
                    print "[INFO] find {0:s} sample, stroe in {1:s}".format(sample_name,sample_path)
                    #tempfile = TFile(sample_path)
                    self.trees[sample_name] = TChain("Ana/passedEvents")
                    self.trees[sample_name].Add(sample_path)
                    #self.sumWeights[sample_name] = tempfile.Ana.Get("sumWeights").GetBinContent(1)

        self.colors["Data"] = kBlack
        self.colors["ZZ"] = kMagenta
        self.colors["DYJets"] = kGreen + 1
        self.colors["WW"] = kBlue

        if(self.year==2016):
            self.lumi = 35.9
        elif(self.year==2017):
            self.lumi = 41.5
        elif(self.year==2018):
            self.lumi = 59.7
        else:
            print "[ERROR] Please set year to 2016 or 2017 or 2018"
            sys.exit()



    #Method
    #def createHistos(self):
    def SetHistStyles(self,histo,sample,var_name):
        if sample == 'Data':
            histo.SetLineColor(kBlack)
            histo.SetMarkerStyle(20)
            histo.SetMarkerSize(0.8)
        else:
            #histo.SetFillColor(self.colors[sample])
            histo.SetLineColor(self.colors[sample])

        histo.GetYaxis().SetTitle("Normalized")
        histo.GetYaxis().SetTitleSize(0.03)
        histo.GetXaxis().SetTitle(var_name)



    def MakeCMSandLumiLabel(self):
        cms=TLatex()
        cms.SetTextSize(0.03)
        cms.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')

        lumi=TLatex()
        lumi.SetTextSize(0.03)
        lumi.SetTextAlign(31)
        lumi.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))

        return cms,lumi


    def MakeLegend(self):
        leg = TLegend( .70, .70, .97, .85 )
        leg.SetFillColor(0)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        return leg

    def DrawOnCanv(self,histo,sample,var_name):
        c = TCanvas(sample+"_"+var_name,sample+"_"+var_name,600,600)

        cms_label,lumi_label = plotHelper.MakeCMSandLumiLabel(self)


    def DrawTogether(self,histos,samples,var_name):
        c = TCanvas(var_name,var_name,600,600)

        cms_label,lumi_label = plotHelper.MakeCMSandLumiLabel(self)
        legend = plotHelper.MakeLegend(self)

        #find max value of histos
        Draw_max = 0
        for sample in samples:
            temp_max = histos[sample][var_name].GetBinContent(histos[sample][var_name].GetMaximumBin())
            if(temp_max>Draw_max):
                Draw_max = temp_max


        for sample in samples:
            if(sample=='ZZ'): legend.AddEntry(histos[sample][var_name],"ZZ",'f')
            if(sample=="DYJets"): legend.AddEntry(histos[sample][var_name],"Z + Jets",'f')
            if(sample=='WW'): legend.AddEntry(histos[sample][var_name],"WW", 'f')
            histos[sample][var_name].SetMaximum(Draw_max*1.1)
            if(samples.index(sample)==0):
                histos[sample][var_name].Draw('histo')
            else:
                histos[sample][var_name].Draw('same histo')

        cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
        lumi_label.Draw('same')
        legend.Draw()

        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        plotname = "../plot/{0:s}_{1:s}".format(var_name,str(localtime))
        plotHelper.SavePlots(self,c,plotname)



    def SavePlots(self,c,name):
        c.SaveAs(name+".png")
