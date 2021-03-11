from ROOT import *


class plotHelper(sampels,year):
    #attribute
    self.lumi = 0.0
    self.trees={}
    self.sumWeights = {}
    self.sample_names = samples
    self.sample_paths = ["/cms/user/guojl/Sample/ZZ_TuneCP5_13TeV-pythia8_RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2.root",
                          "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIISummer19UL17MiniAODv2-106X.root"]
    self.colors = {}
    self.Constructor()

    def Constructor(self):
        for sample_path in self.sample_paths:
            for sample_name iin self.sample_names:
                if(sample_path.find(sample_name)!=-1):
                    print "[INFO] find {0:s} sample, stroe in {1:s}".format(sample_name,sample_path)
                    tempfile = TFile(sample_path)
                    self.trees[sample_name] = tempfile.Ana.Get("passedEvents")
                    self.sumWeights[sample_name] = tempfile.Ana.Get("sumWeights").GetBinContent(1)

        self.colors["Data"] = kBlack
        self.colors["ZZ"] = kMagenta
        self.colors["DYJet"] = kGreen + 1

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
    def SetHistStyles(self,histo,sample):
        if sample == 'Data':
            histo.SetLineColor(kBlack)
            histo.SetMarkerStyle(20)
            histo.SetMarkerSize(0.8)
        else:
            histo.SetFillColor(self.colors[sample])
            histo.SetLineColor(self.colors[sample])

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
        leg = TLegend( .64, .65, .97, .85 )
        leg.SetFillColor(0)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        return leg

    def SavePlots(self,c,name):
        c.SaveAs(name+".png")
