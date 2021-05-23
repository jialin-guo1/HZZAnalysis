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
        self.sample_paths = {2018 :["//cms/user/guojl/Sample/2L2Q/raw/skimed/GluGluHToZZTo2L2Q_M1000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/GluGluHToZZTo2L2Q_M1500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/GluGluHToZZTo2L2Q_M2000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/GluGluHToZZTo2L2Q_M2500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/GluGluHToZZTo2L2Q_M3000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/GluGluHToZZTo2L2Q_MAll_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_01MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_02MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_03MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_04MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_05MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_06MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_07MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_08MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_09MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_10MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-250To400_11MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_01MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_02MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_03MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_04MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_05MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_06MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_07MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_08MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_09MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/raw/skimed/DYJetsToLL_Pt-100To250_10MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-100To250_01MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-100To250_02MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-100To250_03MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-100To250_04MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-100To250_05MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-250To400_01MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-250To400_02MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-250To400_03MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-250To400_04MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    #"/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-250To400_05MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/DYJetsToLL_Pt-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer20UL18MiniAOD-106X_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/ZZ_TuneCP5_13TeV-pythia8_RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v2_skimed.root",
                                    "/cms/user/guojl/Sample/2L2Q/WZ_TuneCP5_13TeV-pythia8_RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v2_skimed.root",
                                    '/cms/user/guojl/Sample/2L2Q/raw/skimed/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIISummer19UL18MiniAOD-106X_skimed.root',
                                    "/cms/user/guojl/Sample/QCD_Pt-150to3000_TuneCP5_FlatPower7_13TeV_pythia8_RunIISummer19UL18MiniAOD-106X_skimed.root"],
                             2017 :["/cms/user/guojl/Sample/ZZ_TuneCP5_13TeV-pythia8_RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2_skimed.root",
                                     "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIISummer19UL17MiniAOD-106X_skimed.root",
                                     "/cms/user/guojl/Sample/WZ_TuneCP5_13TeV-pythia8_RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2_skimed.root",]}
        self.colors = {}
        self.Constructor()

    def Constructor(self):
        #initialize sumWeights for each sample
        for sample_name in self.sample_names:
            self.sumWeights[sample_name] = 0.0

        for sample_path in self.sample_paths[self.year]:
            for sample_name in self.sample_names:
                if(sample_path.find(sample_name)!=-1):
                    print "[INFO] find {0:s} sample, stroe in {1:s}".format(sample_name,sample_path)
                    tempfile = TFile(sample_path)
                    self.trees[sample_name] = TChain("Ana/passedEvents")
                    self.trees[sample_name].Add(sample_path)
                    if((sample_name.find('DYJetsToLL_Pt-100To250') != -1) or (sample_name.find('DYJetsToLL_Pt-250To400') != -1)): continue
                    self.sumWeights[sample_name] = tempfile.Ana.Get("sumWeights").GetBinContent(1)
                    print "[INFO] sumWeights of {} sample = {}".format(sample_name,self.sumWeights[sample_name])

        #sumWeights for DYJetsToLL_Pt100To250 and DYJetsToLL_Pt250To400 and TTJets
        for sample_name in self.sample_names:
            #print "[INFO] start to test sumWeights"
            #print sample_name.find('DYJetsToLL_Pt250To400')
            if((sample_name.find('DYJetsToLL_Pt-100To250') == -1) and (sample_name.find('DYJetsToLL_Pt-250To400') == -1)): continue
            if(sample_name.find('DYJetsToLL_Pt-100To250') != -1):
                print "[INFO] this is DYJetsToLL_Pt-100To250 sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYJetsToLL_Pt-100To250') !=-1):
                        print "[INFO] find {0:s} sample, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYJetsToLL_Pt-100To250 = {}".format(self.sumWeights[sample_name])
            if(sample_name.find('DYJetsToLL_Pt-250To400') != -1):
                print "[INFO] this is DYJetsToLL_Pt-250To400 sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYJetsToLL_Pt-250To400') !=-1):
                        print "[INFO] find {0:s} sample, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYJetsToLL_Pt-250To400 = {}".format(self.sumWeights[sample_name])


        #set different color to each kind of sample
        #for sample_name in self.sample_names:
        #    if(sample_name.find("GluGluHToZZTo2L2Q")!=-1): #set all singal to red
        #        self.colors[sample_name] = kRed
        #    else:
        self.colors["Data"] = kBlack
        self.colors["ZZ_TuneCP5"] = kMagenta
        self.colors["DYJets"] = kGreen + 1
        self.colors["WZ"] = kMagenta
        self.colors["TTJets"] = kBlue
        self.colors["QCD"] = kMagenta
        self.colors["GluGluHToZZTo2L2Q_M1000"] = kCyan
        self.colors["GluGluHToZZTo2L2Q_M1500"] = kBlue
        self.colors["GluGluHToZZTo2L2Q_M2000"] = kPink + 10
        self.colors["GluGluHToZZTo2L2Q_M2500"] = kOrange + 3
        self.colors["GluGluHToZZTo2L2Q_M3000"] = kYellow
        self.colors["GluGluHToZZTo2L2Q_MAll"] = kRed+3

        self.colors["DYJetsToLL_Pt-100To250"] = kGreen-1
        self.colors["DYJetsToLL_Pt-250To400"] = kGreen-1
        self.colors["DYJetsToLL_Pt-400To650"] = kGreen-1
        self.colors["DYJetsToLL_Pt-650ToInf"] = kGreen-1




        #Math year to lumi
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
    #============================================================================
    def SetHistStyles(self,histo,sample,var_name):
        if sample == 'Data':
            histo.SetLineColor(kBlack)
            histo.SetMarkerStyle(20)
            histo.SetMarkerSize(0.8)
        elif sample.find('GluGluHToZZTo2L2Q') != -1:
            histo.SetLineColor(self.colors[sample])
        elif sample.find('DYJetsToLL_Pt-250To400') !=-1:
            histo.SetFillColor(self.colors['DYJetsToLL_Pt-250To400'])
            histo.SetLineColor(self.colors['DYJetsToLL_Pt-250To400'])
        elif sample.find('DYJetsToLL_Pt-100To250') !=-1:
            histo.SetFillColor(self.colors['DYJetsToLL_Pt-100To250'])
            histo.SetLineColor(self.colors['DYJetsToLL_Pt-100To250'])
        else:
            histo.SetFillColor(self.colors[sample])
            histo.SetLineColor(self.colors[sample])

        #histo.GetYaxis().SetTitle("Normalized")
        #histo.GetYaxis().SetTitle("Events/%s GeV"%str(histo.GetBinWidth(1)))
        #histo.GetYaxis().SetTitleSize(0.03)
        #histo.GetXaxis().SetTitle(var_name)


    #============================================================================
    def MakeCMSandLumiLabel(self):
        cms=TLatex()
        cms.SetTextSize(0.03)
        cms.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')

        lumi=TLatex()
        lumi.SetTextSize(0.03)
        lumi.SetTextAlign(31)
        lumi.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))

        return cms,lumi


    #============================================================================
    def MakeLegend(self,position):
        if(position=='right'):
            leg = TLegend( .65, .65, .90, .90 )
        elif(position=='left'):
            leg=TLegend(.18,.65,.51,.85)
        else:
            print "[Error] Please enter \"left\" or \"right\" "

        leg.SetFillColor(0)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        return leg

    def DrawOnCanv(self,histo,sample,var_name):
        c = TCanvas(sample+"_"+var_name,sample+"_"+var_name,600,600)

        cms_label,lumi_label = plotHelper.MakeCMSandLumiLabel(self)


    #============================================================================
    def DrawTogether(self,histos,samples,var_name):
        c = TCanvas(var_name,var_name,600,600)

        cms_label,lumi_label = plotHelper.MakeCMSandLumiLabel(self)
        legend = plotHelper.MakeLegend(self,'right')

        #find max value of histos
        Draw_max = 0
        for sample in samples:
            temp_max = histos[sample][var_name].GetBinContent(histos[sample][var_name].GetMaximumBin())
            if(temp_max>Draw_max):
                Draw_max = temp_max


        for sample in samples:
            if(sample=='ZZ_TuneCP5'): legend.AddEntry(histos[sample][var_name],"ZZ",'f')
            if(sample=="DYJets"): legend.AddEntry(histos[sample][var_name],"Z + Jets",'f')
            if(sample=='WZ'): legend.AddEntry(histos[sample][var_name],"WZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1000'): legend.AddEntry(histos[sample][var_name], "H(1000)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1500'): legend.AddEntry(histos[sample][var_name], "H(1500)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2000'): legend.AddEntry(histos[sample][var_name], "H(2000)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2500'): legend.AddEntry(histos[sample][var_name], "H(2500)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M3000'): legend.AddEntry(histos[sample][var_name], "H(3000)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_MAll'): legend.AddEntry(histos[sample][var_name], "ggH #rightarrow ZZ", 'f')
            if(sample=='QCD'): legend.AddEntry(histos[sample][var_name], "QCD", 'f')
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



    #============================================================================
    def DrawTogetherEeachBin(self,histos,samples,var_name,bin):
        c = TCanvas(var_name+"pt"+str(bin),var_name+"pt"+str(bin),600,600)

        cms_label,lumi_label = plotHelper.MakeCMSandLumiLabel(self)
        legend = plotHelper.MakeLegend(self,'right')

        #find max value of histos
        Draw_max = 0
        for sample in samples:
            temp_max = histos[sample][var_name][bin].GetBinContent(histos[sample][var_name][bin].GetMaximumBin())
            if(temp_max>Draw_max):
                Draw_max = temp_max


        for sample in samples:
            if(sample=='ZZ_TuneCP5'): legend.AddEntry(histos[sample][var_name][bin],"ZZ",'f')
            if(sample=="DYJets"): legend.AddEntry(histos[sample][var_name][bin],"Z + Jets",'f')
            if(sample=='WZ'): legend.AddEntry(histos[sample][var_name][bin],"WZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1000'): legend.AddEntry(histos[sample][var_name][bin], "H(1000)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1500'): legend.AddEntry(histos[sample][var_name][bin], "H(1500)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2000'): legend.AddEntry(histos[sample][var_name][bin], "H(2000)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2500'): legend.AddEntry(histos[sample][var_name][bin], "H(2500)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M3000'): legend.AddEntry(histos[sample][var_name][bin], "H(3000)", 'f')
            if(sample=='GluGluHToZZTo2L2Q_MAll'): legend.AddEntry(histos[sample][var_name][bin], "ggH #rightarrow ZZ", 'f')
            if(sample=='QCD'): legend.AddEntry(histos[sample][var_name][bin], "QCD", 'f')
            histos[sample][var_name][bin].SetMaximum(Draw_max*1.1)
            if(samples.index(sample)==0):
                histos[sample][var_name][bin].Draw('histo')
            else:
                histos[sample][var_name][bin].Draw('same histo')

        cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
        lumi_label.Draw('same')
        legend.Draw()

        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        plotname = "../plot/{0}_{1}".format(var_name,"pt"+str(bin))
        plotHelper.SavePlots(self,c,plotname)



    #============================================================================
    def DrawStack(self,histos,samples,var_name,name):
        c = TCanvas(var_name,var_name,600,600)


        cms_label,lumi_label = self.MakeCMSandLumiLabel()
        legend = self.MakeLegend('right')

        #find max value of histos
        Draw_max = 0
        for sample in samples:
            temp_max = histos[sample][var_name].GetBinContent(histos[sample][var_name].GetMaximumBin())
            Draw_max +=temp_max

        stack = THStack(var_name,var_name)
        temp_sample = 'nosample'
        for sample in samples:
            if(sample=='Data'): continue
            temp_sample = sample
            if(sample=='ZZ_TuneCP5'): legend.AddEntry(histos[sample][var_name],"ZZ,WZ",'f')
            if(sample=="DYJets"): legend.AddEntry(histos[sample][var_name],"Z + Jets",'f')
            if(sample=='TTJets'): legend.AddEntry(histos[sample][var_name],"t#bar{t}",'f')
            #if(sample=='WZ'): legend.AddEntry(histos[sample][var_name],"WZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1000'): legend.AddEntry(histos[sample][var_name], "ggH(1000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1500'): legend.AddEntry(histos[sample][var_name], "ggH(1500) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2000'): legend.AddEntry(histos[sample][var_name], "ggH(2000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2500'): legend.AddEntry(histos[sample][var_name], "ggH(2500) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M3000'): legend.AddEntry(histos[sample][var_name], "ggH(3000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_MAll'): legend.AddEntry(histos[sample][var_name], "ggH #rightarrow ZZ", 'f')
            if(sample=='QCD'): legend.AddEntry(histos[sample][var_name], "QCD", 'f')
            if(sample.find("DYJetsToLL_Pt-250To400_01")!=-1): legend.AddEntry(histos[sample][var_name],"Z+Jets",'f')
            #if(sample.find("DYJetsToLL_Pt-250To400_01")!=-1): legend.AddEntry(histos[sample][var_name],"ZJets_pt-250To400",'f')
            #if(sample.find("DYJetsToLL_Pt-100To250_01")!=-1): legend.AddEntry(histos[sample][var_name],"ZJets_pt-100To250",'f')
            #if(sample.find("DYJetsToLL_Pt-400To650")!=-1): legend.AddEntry(histos[sample][var_name],"ZJets_pt-400To650",'f')
            #if(sample.find("DYJetsToLL_Pt-650ToInf")!=-1): legend.AddEntry(histos[sample][var_name],"ZJets_pt-650ToInf",'f')

            #histos[sample][var_name].SetMaximum(Draw_max*1.1)

            if(sample.find('GluGluHToZZTo2L2Q')==-1):
                stack.Add(histos[sample][var_name])

            if(var_name == 'Hmass' or var_name == 'Z1_pt' or var_name == 'GenZ1_pt'):
                stack.SetMaximum(10e3)
                stack.SetMinimum(10e-2)
            else:
                if(var_name=='SDmass_SR' or var_name=='SDmass_CR'):
                    stack.SetMaximum(1300)
                    stack.SetMinimum(0)
                else:
                    stack.SetMaximum(Draw_max)
                    stack.SetMinimum(0)

        if(var_name == 'Hmass' or var_name == 'Z1_pt' or var_name == 'GenZ1_pt'):
            pad = TPad(var_name,var_name,0,0,1,1)
            pad.Draw()
            pad.cd()
            print "[INFO] scale logY on pad"
            pad.SetLogy()

        print "[INFO] draw stack"
        stack.Draw('histo')
        stack.GetYaxis().SetTitle("Events/%s GeV"%str(histos[temp_sample][var_name].GetBinWidth(1)))
        #stack.GetYaxis().SetTitle("Events/%s GeV"%str(50))
        stack.GetYaxis().SetTitleSize(0.025)
        stack.GetYaxis().SetLabelSize(0.025)
        stack.GetXaxis().SetTitle(var_name)
        stack.GetXaxis().SetTitleSize(0.025)

        for sample in samples:
            if(sample.find('GluGluHToZZTo2L2Q')!=-1):
                histos[sample][var_name].Draw('same histo')



        cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
        lumi_label.Draw('same')
        legend.Draw()

        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        plotname = "../plot/{0}_{1}".format(var_name,name)
        plotHelper.SavePlots(self,c,plotname)


    #============================================================================
    def Draw2DPlots(self,histos,samples,var_name,name):
        c = TCanvas(var_name,var_name,600,600)

        cms_label,lumi_label = self.MakeCMSandLumiLabel()
        legend = self.MakeLegend('right')


        stack = TH2D(var_name,var_name,60,500,3500,56,40,180)
        stack.Sumw2()
        for sample in samples:
            print "Add smaple: "+sample
            stack.Add(histos[sample][var_name])


        stack.Draw('COLZ')
        cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
        lumi_label.Draw('same')
        legend.Draw()

        plotname = "../plot/{0}_signal_{1}".format(var_name,name)
        self.SavePlots(c,plotname)




    def SavePlots(self,c,name):
        c.SaveAs(name+".png")
