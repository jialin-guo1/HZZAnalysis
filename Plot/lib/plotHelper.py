from ROOT import *
import time
import sys,os
import yaml
from array import array


class plotHelper:

    def __init__(self,samples,year):
        #attributes
        gStyle.SetOptStat(False)
        self.CurrentFileName = os.path.abspath(sys.argv[0])
        self.year = year
        self.lumi = 0.0
        self.trees={}
        self.sumWeights = {}
        self.sample_names = samples
        self.plotspaths = 'plot/Plot1229'
        self.colors = {}
        self.stack = THStack()

        #load smples path
        with open('/cms/user/guojl/Analysis/CMSSW_10_6_12/src/HZZAnalysis/ZZ2l2qAna/cards/config_2016Legacy_samples_Raw.yml') as f:
        #with open('/cms/user/guojl/Analysis/CMSSW_10_6_12/src/HZZAnalysis/ZZ2l2qAna/cards/config_2016Legacy_samples_skimedZ1.yml') as f:
            self.sample_paths = yaml.safe_load(f)
        #print self.sample_paths

        self.Constructor()


    def Constructor(self):
        print self.CurrentFileName
        #initialize sumWeights for each sample and handle ntuples
        if(self.CurrentFileName.find('plot.py')==-1):
            for sample_name in self.sample_names:
                self.sumWeights[sample_name] = 0.0

            for sample_path in self.sample_paths[self.year]:
                for sample_name in self.sample_names:
                    if(sample_path.find(sample_name)!=-1):
                        print "[INFO] find {0:s} sample, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        if(sample_name.find('Data') == -1 and sample_name.find('SingleMuon_Run2016') == -1):
                            self.trees[sample_name] = TChain("Ana/passedEvents")
                            self.trees[sample_name].Add(sample_path)
                            #if((sample_name.find('DYJetsToLL_Pt-50To100') != -1) or (sample_name.find('DYJetsToLL_Pt-100To250') != -1) or (sample_name.find('DYJetsToLL_Pt-250To400') != -1) or (sample_name.find('DYJetsToLL_Pt-400To650') != -1) or (sample_name.find('DYJetsToLL_Pt-650ToInf') != -1) or (sample_name.find('DYJetsToLL_M-50') != -1) or (sample_name.find('WZTo2L2Q') !=-1 ) or (sample_name.find('ZZTo2L2Q') !=-1 and sample_name.find('GluGluHToZZTo2L2Q_M') == -1) or (sample_name.find('TTJets_DiLept')!=-1)): continue
                            if(sample_name.find('GluGluHToZZTo2L2Q_M')!=-1):
                                print "[INFO] this is singal smaple"
                                self.sumWeights[sample_name] = tempfile.Ana.Get("sumWeights").GetBinContent(1)
                                print "[INFO] sumWeights of {} sample = {}".format(sample_name,self.sumWeights[sample_name])
                        else:
                            self.trees[sample_name] = TChain("passedEvents")
                            self.trees[sample_name].Add(sample_path)

            #sumWeights for DYJetsToLL_Pt100To250 and DYJetsToLL_Pt250To400 and TTJets
            sumWeights_sample_list = ['DYJetsToLL_Pt-50To100','DYJetsToLL_Pt-100To250','DYJetsToLL_Pt-250To400','DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf','DY1JetsToLL_M','DY2JetsToLL_M','DY3JetsToLL_M','DY4JetsToLL_M','DYBJetsToLL_M','WZTo2L2Q','WW_TuneCUETP8M1_13TeV','WWTo2L2Nu_13TeV-powheg','WZ_TuneCUETP8M1_13TeV','ZZTo2L2Q_13TeV','TTJets_DiLept','TTTo2L2Nu_TuneCUETP8M2','TTTo2L2Nu_TuneCP5_PSweights_13TeV','TTTo2L2Nu_TuneCP5_PSweights_13TeV','ST_s-channel','ST_t-channel','ST_tW','WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8']
            for sumWeights_sample in sumWeights_sample_list:
                if(sample_name.find('%s'%sumWeights_sample) != -1):
                    print "[INFO] this is %s sample"%sumWeights_sample
                    for sample_path in self.sample_paths[self.year]:
                        if(sample_path.find('%s'%sumWeights_sample) !=-1):
                            print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sumWeights_sample,sample_path)
                            tempfile = TFile(sample_path)
                            print "[INFO] sumWeights for %s = "%sumWeights_sample+str(self.sumWeights[self.sample_names[0]])
                            print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                            self.sumWeights[self.sample_names[0]] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                    print "[INFO] sumWeights for {} = {}".format(sumWeights_sample,self.sumWeights[self.sample_names[0]])



        #set different color to each kind of sample
        #for sample_name in self.sample_names:
        #    if(sample_name.find("GluGluHToZZTo2L2Q")!=-1): #set all singal to red
        #        self.colors[sample_name] = kRed
        #    else:
        self.colors["Data"] = kBlack
        self.colors["ZZ_TuneCP5"] = kMagenta
        self.colors["ZZTo2L2Q"] = kRed + 1
        self.colors["DYJets"] = kGreen + 1
        self.colors["WZ_TuneCUETP8M1_13TeV"] = kRed + 1
        self.colors["WZTo2L2Q"] = kRed + 1
        self.colors["TTJets"] = kYellow - 3
        self.colors["QCD"] = kMagenta
        self.colors["ST"] = kOrange + 3
        self.colors["WW_TuneCUETP8M1_13TeV"] = kBlue
        self.colors["WWTo2L2Nu_13TeV-powheg"] = kBlue
        self.colors["GluGluHToZZTo2L2Q_M1000"] = kCyan
        self.colors["GluGluHToZZTo2L2Q_M1500"] = kBlue
        self.colors["GluGluHToZZTo2L2Q_M2000"] = kPink + 10
        self.colors["GluGluHToZZTo2L2Q_M2500"] = kOrange + 3
        self.colors["GluGluHToZZTo2L2Q_M3000"] = kYellow
        self.colors["GluGluHToZZTo2L2Q_M900"] = kRed+3
        self.colors["GluGluHToZZTo2L2Q_MAll"] = kRed+3

        self.colors["BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M1000"] = kOrange + 7
        self.colors["BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M2000"] = kOrange + 7
        self.colors["BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M3000"] = kOrange + 7

        self.colors["DYJetsToLL_Pt-50To100"] = kGreen-1
        self.colors["DYJetsToLL_Pt-100To250"] = kGreen-1
        self.colors["DYJetsToLL_Pt-250To400"] = kGreen-1
        self.colors["DYJetsToLL_Pt-400To650"] = kGreen-1
        self.colors["DYJetsToLL_Pt-650ToInf"] = kGreen-1
        self.colors['DYBJetsToLL_M'] = kGreen-1
        self.colors["DYJetsToLL_M"] = kGreen-1
        self.colors["DYNJetsToLL_M"] = kGreen-1

        #colors for ingredient checking
        self.colors['Z1_notLep'] = kRed

        #Math year to lumi
        if(self.year==2016 or self.year=='2016Legacy'):
            self.lumi = 36.322
        elif(self.year==2017):
            self.lumi = 41.5
        elif(self.year==2018 or self.year=='2018Legacy'):
            #self.lumi = 59.74
            self.lumi = 27.65 #runABC
        else:
            print "[ERROR] Please set year to 2016 or 2017 or 2018"
            sys.exit()



    #Method
    #============================================================================
    def SetHistStyles(self,histo,sample,var_name):
        if sample.find('Data') !=-1 or sample.find('SingleMuon_Run2016') !=-1 or sample.find('SingleElectron_Run2016')!=-1:
            histo.SetLineColor(kBlack)
            histo.SetMarkerStyle(20)
            histo.SetMarkerSize(0.8)
            histo.SetBinErrorOption(TH1.kPoisson)
        elif sample.find('GluGluHToZZTo2L2Q') != -1:
            histo.SetLineColor(self.colors[sample])
            histo.SetLineWidth(2)
        elif sample.find('DYJetsToLL_Pt-50To100') !=-1:
            histo.SetFillColor(self.colors['DYJetsToLL_Pt-50To100'])
            histo.SetLineColor(self.colors['DYJetsToLL_Pt-50To100'])
            #histo.SetLineColor(kBlack)
        elif sample.find('DYJetsToLL_Pt-250To400') !=-1 and var_name.find("Gengamma")==-1 and var_name.find("Gennotmu")==-1:
            histo.SetFillColor(self.colors['DYJetsToLL_Pt-250To400'])
            histo.SetLineColor(self.colors['DYJetsToLL_Pt-250To400'])
            #histo.SetLineColor(kBlack)
        elif sample.find('DYJetsToLL_Pt-100To250') !=-1 and var_name.find("Gengamma")==-1 and var_name.find("Gennotmu")==-1:
            histo.SetFillColor(self.colors['DYJetsToLL_Pt-100To250'])
            histo.SetLineColor(self.colors['DYJetsToLL_Pt-100To250'])
            #histo.SetLineColor(kBlack)
        elif sample.find('DYJetsToLL_Pt-400To650') !=-1 and var_name.find("Gengamma")==-1 and var_name.find("Gennotmu")==-1:
            histo.SetFillColor(self.colors['DYJetsToLL_Pt-400To650'])
            histo.SetLineColor(self.colors['DYJetsToLL_Pt-400To650'])
            #histo.SetLineColor(kBlack)
        elif sample.find('DYJetsToLL_Pt-650ToInf') !=-1 and var_name.find("Gengamma")==-1 and var_name.find("Gennotmu")==-1:
            histo.SetFillColor(self.colors['DYJetsToLL_Pt-650ToInf'])
            histo.SetLineColor(self.colors['DYJetsToLL_Pt-650ToInf'])
            #histo.SetLineColor(kBlack)
        elif sample.find('DYBJetsToLL_M')!=-1:
            histo.SetFillColor(self.colors['DYBJetsToLL_M'])
            histo.SetLineColor(self.colors['DYBJetsToLL_M'])
            #histo.SetLineColor(kBlack)
        elif sample.find('DY1JetsToLL_M')!=-1 or sample.find('DY2JetsToLL_M')!=-1 or sample.find('DY3JetsToLL_M')!=-1 or sample.find('DY4JetsToLL_M')!=-1 or sample.find('DYJetsToLL_M')!=-1 :
            histo.SetFillColor(self.colors['DYNJetsToLL_M'])
            histo.SetLineColor(self.colors['DYNJetsToLL_M'])
            #histo.SetLineColor(kBlack)
        elif sample.find('BulkGraviton_ggF_ZZ_ZlepZhad_narrow')!=-1:
            histo.SetLineColor(self.colors[sample])
        elif var_name.find("Gengamma")!=-1 or var_name.find("Gennotmu")!=-1:
            histo.SetFillColor(self.colors['Z1_notLep'])
            histo.SetLineColor(self.colors['Z1_notLep'])
        elif sample.find("WZTo2L2Q")!=-1 or sample.find('WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8')!=-1:
            histo.SetFillColor(self.colors['WZTo2L2Q'])
            histo.SetLineColor(self.colors['WZTo2L2Q'])
            #histo.SetLineColor(kBlack)
        elif sample.find("ZZTo2L2Q")!=-1:
            histo.SetFillColor(self.colors['ZZTo2L2Q'])
            histo.SetLineColor(self.colors['ZZTo2L2Q'])
            #histo.SetLineColor(kBlack)
        elif sample.find("TTJets")!=-1 or sample.find("TTTo2L2Nu_TuneCUETP8M2")!=-1 or sample.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV')!=-1:
            histo.SetFillColor(self.colors['TTJets'])
            histo.SetLineColor(self.colors['TTJets'])
            #histo.SetLineColor(kBlack)
        elif sample.find("ST_")!=-1:
            histo.SetFillColor(self.colors['ST'])
            histo.SetLineColor(self.colors['ST'])
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
        #cms.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')

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
    def DrawTogether(self,histos,Region,samples,var_name,name,cat):
        #specify varible name
        titile = self.specifyVarName(var_name,cat)
        if(titile=='ERROR'):
            print "[ERROR] Please enter right varible"
            sys.exit()


        c = TCanvas(var_name,var_name,600,600)

        cms_label,lumi_label = plotHelper.MakeCMSandLumiLabel(self)
        legend = plotHelper.MakeLegend(self,'right')

        histo = {'BKG':TH1D('bkg'+var_name+'_'+Region+'_'+cat,'bkg'+var_name+'_'+Region+'_'+cat,20,0,1),
                  'SIG':TH1D('SIG'+var_name+'_'+Region+'_'+cat,'SIG'+var_name+'_'+Region+'_'+cat,20,0,1),
                  'ZV':TH1D('ZV'+var_name+'_'+Region+'_'+cat,'ZV'+var_name+'_'+Region+'_'+cat,20,0,1),
                  'TTJets':TH1D('TTJets'+var_name+'_'+Region+'_'+cat,'TTJets'+var_name+'_'+Region+'_'+cat,20,0,1)}
        for key in histo.keys():
            histo[key].Sumw2

        for sample in samples:
            if(sample.find('DYJets')!=-1):
                histo['BKG'].Add(histos[Region][sample][cat][var_name])
                print "[INFO] add bkg: "+sample
            elif((sample.find('ZZTo2L2Q')!=-1 and sample.find('GluGluHToZZTo2L2Q')==-1) or sample.find('WZTo2L2Q')!=-1):
                histo['ZV'].Add(histos[Region][sample][cat][var_name])
                print "[INFP] add ZV: "+sample
            elif(sample.find('TTJets')!=-1):
                histo['TTJets'].Add(histos[Region][sample][cat][var_name])
                print "[INFP] add TTJets_DiLep: "+sample
            else:
                histo['SIG'].Add(histos[Region][sample][cat][var_name])
                print "[INFO] add singal: "+sample
        #substract BJets for all jets
        #for sample in samples:
        #    if(sample.find('DYBJet')!=-1):
        #        histosBKG.Add(histos[sample][var_name],-1)
        #        print "[INFO] reduce DYBJets: "+sample
        for key in histo.keys():
            self.Normalize(histo[key])
            histo[key].SetLineWidth(2)
            histo[key].GetYaxis().SetTitle("Normalized to 1 ")

        #find max value of histos
        Draw_max = 0
        for sample in samples:
            temp_max = histos[Region][sample][cat][var_name].GetBinContent(histos[Region][sample][cat][var_name].GetMaximumBin())
            Draw_max +=temp_max
            #if(temp_max>Draw_max):
            #    Draw_max += temp_max

        histo['SIG'].SetMaximum(0.8)
        histo['SIG'].SetLineColor(kRed+3)
        #histosBKG.SetMaximum(Draw_max*1.1)
        histo['BKG'].SetLineColor(kGreen-1)
        histo['TTJets'].SetLineColor(kYellow - 3)
        histo['ZV'].SetLineColor(kRed + 1)

        legend.AddEntry(histo['SIG'],"ggH #rightarrow ZZ")
        #legend.AddEntry(histosSIG,"Z+Bjets", 'f')
        legend.AddEntry(histo['BKG'],"Z+jets")
        legend.AddEntry(histo['ZV'],"ZZ,WZ")
        legend.AddEntry(histo['TTJets'],'TTJets')


        #for sample in samples:
        #    if(sample=='ZZ_TuneCP5'): legend.AddEntry(histos[sample][var_name],"ZZ",'f')
        #    if(sample.find("DYJetsToLL_Pt-250To400_01")!=-1): legend.AddEntry(histos[sample][var_name],"Z + Jets",'f')
        #    if(sample.find("DYBJetsToLL_M-50_Zpt-100to200")!=-1): legend.AddEntry(histos[sample][var_name],"Z + BJets",'f')
        #    if(sample=='WZ'): legend.AddEntry(histos[sample][var_name],"WZ", 'f')
        #    if(sample=='GluGluHToZZTo2L2Q_M1000'): legend.AddEntry(histos[sample][var_name], "H(1000)", 'f')
        #    if(sample=='GluGluHToZZTo2L2Q_M1500'): legend.AddEntry(histos[sample][var_name], "H(1500)", 'f')
        #    if(sample=='GluGluHToZZTo2L2Q_M2000'): legend.AddEntry(histos[sample][var_name], "H(2000)", 'f')
        #    if(sample=='GluGluHToZZTo2L2Q_M2500'): legend.AddEntry(histos[sample][var_name], "H(2500)", 'f')
        #    if(sample=='GluGluHToZZTo2L2Q_M3000'): legend.AddEntry(histos[sample][var_name], "H(3000)", 'f')
        #    if(sample=='GluGluHToZZTo2L2Q_MAll'): legend.AddEntry(histos[sample][var_name], "ggH #rightarrow ZZ", 'f')
        #    if(sample=='QCD'): legend.AddEntry(histos[sample][var_name], "QCD", 'f')
            #histos[sample][var_name].SetMaximum(Draw_max*1.1)
            #if(samples.index(sample)==0):
            #    histos[sample][var_name].Draw('histo')
            #else:
            #    histos[sample][var_name].Draw('same histo')
        histo['SIG'].Draw('histo')
        histo['BKG'].Draw('same histo')
        histo['ZV'].Draw('same histo')
        histo['TTJets'].Draw('same histo')

        cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
        lumi_label.Draw('same')
        legend.Draw()

        #localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        plotname = self.plotspaths+"/{0}_{1}_{2}_{3}".format(titile,name,Region,cat)
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
    def DrawStack(self,histos,Region,samples,var_name,name,cat):
        #specify varible name
        titile = self.specifyVarName(var_name,cat)
        if(titile=='ERROR'):
            print "[ERROR] Please enter right varible"
            sys.exit()

        c = TCanvas(var_name,var_name,600,600)

        cms_label,lumi_label = self.MakeCMSandLumiLabel()
        legend = self.MakeLegend('right')

        #find max value of histos
        #Draw_max = 0
        #for sample in samples:
        #    temp_max = histos[sample][var_name].GetBinContent(histos[sample][var_name].GetMaximumBin())
        #    Draw_max +=temp_max

        #======================count number===============================================
        #total number
        number = {}
        sample_lists = ['DY','TT','WZorZZ','WW','ST','ggh']
        for sample_list in sample_lists:
            number[sample_list] = 0

        for sample in samples:
            if (sample.find('ZZTo2L2Q_13TeV')!=-1) or (sample.find('WZTo2L2Q_13TeV')!=-1) or (sample.find("WZ_TuneCUETP8M1_13TeV")!=-1):
                number['WZorZZ']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('DY')!=-1:
                number['DY']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('TT')!=-1 or sample.find("TTTo2L2Nu_TuneCUETP8M2")!=-1 or sample.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV')!=-1:
                number['TT']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('WW_TuneCUETP8M1_13TeV')!=-1 or sample.find('WWTo2L2Nu_13TeV-powheg')!=-1:
                number['WW']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('ST_')!=-1:
                number['ST']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('GluGluHToZZTo2L2Q_M900')!=-1:
                number['ggh']+=histos[Region][sample][cat][var_name].Integral()
        for sample_list in sample_lists:
            number[sample_list] = ('%.2f'%number[sample_list])

        #=================================sum bkg MC histos====================================================
        self.stack = THStack(titile,titile)
        backgrounds = 0.0
        temp_sample = 'nosample'
        for sample in samples:
            temp_sample = sample
            #if(sample=='Data'): legend.AddEntry(histos[Region][sample][cat][var_name],"Data",'p')
            if(sample=='ZZ_TuneCP5'): legend.AddEntry(histos[Region][sample][cat][var_name],"ZZ,WZ",'f')
            if(sample.find('ZZTo2L2Q_13TeV_00')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"ZZ,WZ[%s]"%number['WZorZZ'],'f')
            if(sample.find('WW_TuneCUETP8M1_13TeV')!=-1 or sample.find('WWTo2L2Nu_13TeV-powheg')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"WW[%s]"%number['WW'],'f')
            if(sample=="DYJets"): legend.AddEntry(histos[Region][sample][cat][var_name],"Z + Jets",'f')
            if(sample=='TTJets'): legend.AddEntry(histos[Region][sample][cat][var_name],"t#bar{t}",'f')
            if(sample.find('TTJets_DiLept_00')!=-1 or sample.find("TTTo2L2Nu_TuneCUETP8M2_00")!=-1 or sample.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV00')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"t#bar{t}[%s]"%number['TT'],'f')
            if(sample.find('ST_tW_antitop_5f_inclusiveDecays_13TeV')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"ST(s,t,w)[%s]"%number['ST'],'f')
            #if(sample=='WZ'): legend.AddEntry(histos[sample][var_name],"WZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1000'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(1000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1500'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(1500) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2000'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(2000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2500'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(2500) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M3000'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(3000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M900'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(900) #rightarrow ZZ[%s]"%number['ggh'], 'f')
            if(sample=='GluGluHToZZTo2L2Q_MAll'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH #rightarrow ZZ", 'f')
            if(sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M1000'): legend.AddEntry(histos[Region][sample][cat][var_name], "X #rightarrow ZZ", 'f')
            if(sample=='QCD'): legend.AddEntry(histos[Region][sample][cat][var_name], "QCD", 'f')
            if(sample.find("DYJetsToLL_Pt-250To400_01")!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"Z+Jets[%s]"%number['DY'],'f')
            if(sample.find("DYJetsToLL_M-50_01")!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"Z+Jets",'f')
            if(sample.find('GluGluHToZZTo2L2Q')==-1 and sample.find('Data')==-1 and sample.find('BulkGraviton_ggF_ZZ_ZlepZhad_narrow')==-1 and sample.find('SingleMuon_Run2016')==-1 and sample.find('SingleElectron_Run2016')==-1):
                self.stack.Add(histos[Region][sample][cat][var_name])
                backgrounds += histos[Region][sample][cat][var_name].Integral()
                print "[INFO] stack %s sample"%sample

        #find max value of histos
        Draw_max = 0
        for sample in samples:
            Draw_max += histos[Region][sample][cat][var_name].GetBinContent(histos[Region][sample][cat][var_name].GetMaximumBin())
            #Draw_max +=temp_max
        #Draw_max = self.stack.GetBinContent(self.stack.GetMaximumBin())

        if(var_name == 'Hmass' or var_name == 'Z1_pt' or var_name == 'GenZ1_pt'):
            self.stack.SetMaximum(10e3)
            self.stack.SetMinimum(10e-2)
        else:
            if(var_name=='SDmass_SR' or var_name=='SDmass_CR'):
                self.stack.SetMaximum(1300)
                self.stack.SetMinimum(0)
            else:
                self.stack.SetMaximum(Draw_max)
                self.stack.SetMinimum(0)


        if(var_name == 'Hmass' or var_name == 'Z1_pt' or var_name == 'GenZ1_pt'):
            pad = TPad(var_name,var_name,0,0,1,1)
            pad.Draw()
            pad.cd()
            print "[INFO] scale logY on pad"
            pad.SetLogy()

        print "[INFO] draw stack"
        self.stack.Draw('histo')
        self.stack.GetYaxis().SetTitle("Events/%s GeV"%str(histos[Region][temp_sample][cat][var_name].GetBinWidth(1)))
        #stack.GetYaxis().SetTitle("Events/%s GeV"%str(50))
        self.stack.GetYaxis().SetTitleSize(0.025)
        self.stack.GetYaxis().SetLabelSize(0.025)
        self.stack.GetXaxis().SetTitle(var_name)
        self.stack.GetXaxis().SetTitleSize(0.025)

        for sample in samples:
            if(sample.find('GluGluHToZZTo2L2Q')!=-1):
                histos[Region][temp_sample][cat][var_name].Draw('same histo')

        cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
        lumi_label.Draw('same')
        legend.Draw()

        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        plotname = self.plotspaths+"/{0}_{1}_{2}_{3}".format(titile,name,Region,cat)
        plotHelper.SavePlots(self,c,plotname)

    #================================================================================================
    #================================================================================================
    #================================================================================================
    def DrawDataMC(self,histos,Region,samples,var_name,name,cat,ifcheckIngredient):
        #specify varible name
        titile = self.specifyVarName(var_name,cat)
        if(titile=='ERROR'):
            print "[ERROR] Please enter right varible"
            sys.exit()

        #initialize a canvas to draw
        c = TCanvas(Region+'_'+titile,Region+'_'+titile,600,600)

        upper_pad = TPad("upperpad_"+titile, "upperpad_"+titile, 0,0.18, 1,1)
        upper_pad.SetBottomMargin(0.12)
        upper_pad.Draw()
        upper_pad.cd()

        cms_label,lumi_label = self.MakeCMSandLumiLabel()
        legend = self.MakeLegend('right')

        #total number
        number = {}
        sample_lists = ['data','DY','TT','WZorZZ','WW','ST','ggh']
        for sample_list in sample_lists:
            number[sample_list] = 0


        #=======================sum data histos==========================================
        nbins = histos[Region][samples[0]][cat][var_name].GetXaxis().GetNbins()
        lowEdge = histos[Region][samples[0]][cat][var_name].GetXaxis().GetBinLowEdge(1)
        upEdge = histos[Region][samples[0]][cat][var_name].GetBinLowEdge(nbins)+histos[Region][samples[0]][cat][var_name].GetBinWidth(nbins-1)
        if(var_name=='Hmass'):
            histoData = TH1D(Region+'_Data'+'_'+cat+'_'+var_name,Region+'_Data'+'_'+cat+'_'+var_name,16,array('f',[500.0,550.0,600.0,650.0,700.0,750.0,800.0,850.0,900.0,950.0,1000.0,1100.0,1300.0,1600.0,2000.0,2500.0,3500.0]))
        else:
            histoData = TH1D(Region+'_Data'+'_'+cat+'_'+var_name,Region+'_Data'+'_'+cat+'_'+var_name,nbins,lowEdge,upEdge)
        histoData.Sumw2()
        histoData.SetLineColor(kBlack)
        histoData.SetMarkerStyle(20)
        histoData.SetMarkerSize(0.8)
        histoData.SetBinErrorOption(TH1.kPoisson)
        for sample in samples:
            if(sample.find('Data')!=-1 or sample.find('SingleMuon_Run2016')!=-1 or sample.find('SingleElectron_Run2016')!=-1):
                histoData.Add(histos[Region][sample][cat][var_name])
                print '[INFO] add data histo {}_{}_{}_{}'.format(Region,sample,cat,var_name)
                print '[INFO] this number of  data  = {}'.format(histos[Region][sample][cat][var_name].Integral())
        number['data'] = histoData.Integral()
        print "[INFO] number of data in {} = {}".format(var_name,number['data'])
        #======================count number===============================================
        for sample in samples:
            if (sample.find('ZZTo2L2Q_13TeV')!=-1) or (sample.find('WZTo2L2Q_13TeV')!=-1) or (sample.find("WZ_TuneCUETP8M1_13TeV")!=-1):
                number['WZorZZ']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('DY')!=-1:
                number['DY']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('TT')!=-1 or sample.find("TTTo2L2Nu_TuneCUETP8M2")!=-1 or sample.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV')!=-1:
                number['TT']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('WW_TuneCUETP8M1_13TeV')!=-1 or sample.find('WWTo2L2Nu_13TeV-powheg')!=-1:
                number['WW']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('ST_')!=-1:
                number['ST']+=histos[Region][sample][cat][var_name].Integral()
            elif sample.find('GluGluHToZZTo2L2Q_M900')!=-1:
                number['ggh']+=histos[Region][sample][cat][var_name].Integral()
        for sample_list in sample_lists:
            number[sample_list] = ('%.2f'%number[sample_list])


        #find max value of histos
        Draw_max = 0
        #temp_max = histos[Region]['Data'][cat][var_name].GetBinContent(histos[Region]['Data'][cat][var_name].GetMaximumBin())
        temp_max = histoData.GetBinContent(histoData.GetMaximumBin())
        Draw_max = temp_max*1.5

        #=================================sum bkg MC histos====================================================
        self.stack = THStack(titile,titile)
        legend.AddEntry(histoData,"Data [%s]"%number['data'],'p')
        backgrounds = 0.0
        temp_sample = 'nosample'
        for sample in samples:
            temp_sample = sample
            #if(sample=='Data'): legend.AddEntry(histos[Region][sample][cat][var_name],"Data",'p')
            if(sample=='ZZ_TuneCP5'): legend.AddEntry(histos[Region][sample][cat][var_name],"ZZ,WZ",'f')
            if(sample.find('ZZTo2L2Q_13TeV_00')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"ZZ,WZ[%s]"%number['WZorZZ'],'f')
            if(sample.find('WW_TuneCUETP8M1_13TeV')!=-1 or sample.find('WWTo2L2Nu_13TeV-powheg')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"WW[%s]"%number['WW'],'f')
            if(sample=="DYJets"): legend.AddEntry(histos[Region][sample][cat][var_name],"Z + Jets",'f')
            if(sample=='TTJets'): legend.AddEntry(histos[Region][sample][cat][var_name],"t#bar{t}",'f')
            if(sample.find('TTJets_DiLept_00')!=-1 or sample.find("TTTo2L2Nu_TuneCUETP8M2_00")!=-1 or sample.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV00')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"t#bar{t}[%s]"%number['TT'],'f')
            if(sample.find('ST_tW_antitop_5f_inclusiveDecays_13TeV')!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"ST(s,t,w)[%s]"%number['ST'],'f')
            #if(sample=='WZ'): legend.AddEntry(histos[sample][var_name],"WZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1000'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(1000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M1500'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(1500) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2000'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(2000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M2500'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(2500) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M3000'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(3000) #rightarrow ZZ", 'f')
            if(sample=='GluGluHToZZTo2L2Q_M900'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH(900) #rightarrow ZZ[%s]"%number['ggh'], 'f')
            if(sample=='GluGluHToZZTo2L2Q_MAll'): legend.AddEntry(histos[Region][sample][cat][var_name], "ggH #rightarrow ZZ", 'f')
            if(sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M1000'): legend.AddEntry(histos[Region][sample][cat][var_name], "X #rightarrow ZZ", 'f')
            if(sample=='QCD'): legend.AddEntry(histos[Region][sample][cat][var_name], "QCD", 'f')
            if(sample.find("DYJetsToLL_Pt-250To400_01")!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"Z+Jets[%s]"%number['DY'],'f')
            if(sample.find("DYJetsToLL_M-50_01")!=-1): legend.AddEntry(histos[Region][sample][cat][var_name],"Z+Jets",'f')
            if(sample.find('GluGluHToZZTo2L2Q')==-1 and sample.find('Data')==-1 and sample.find('BulkGraviton_ggF_ZZ_ZlepZhad_narrow')==-1 and sample.find('SingleMuon_Run2016')==-1 and sample.find('SingleElectron_Run2016')==-1):
                self.stack.Add(histos[Region][sample][cat][var_name])
                backgrounds += histos[Region][sample][cat][var_name].Integral()
                print "[INFO] stack %s sample"%sample

        #if check ingredient with Z+jet smaple in leptonic channel
        for sample in samples:
            if(ifcheckIngredient==True and sample.find("DYJetsToLL")!=-1):
                if(sample.find("DYJetsToLL_Pt-250To400_01")!=-1): legend.AddEntry(histos[Region][sample][cat]['Z1_mass_ele_Gengamma'],"Z+Jets(Gen match with Gamma)",'f')
                print "[INFO] will check ingredient with Z+jet MC sim sample"
                self.AddIngredient(histos,Region,sample,var_name)

        #if(var_name == 'Hmass' or var_name == 'Z1_pt' or var_name == 'GenZ1_pt'):
        #if(var_name == 'GenZ1_pt' or var_name=='Z1_pt' or var_name == 'SDmass' or var_name == 'SDmassUncorr' or var_name == "SDmasscorr" or var_name == 'Pt'):
        if(var_name == 'GenZ1_pt' or var_name=='Z1_pt' or var_name == 'Pt'):
            self.stack.SetMaximum(10e6)
            self.stack.SetMinimum(10e-2)
            upper_pad.SetLogy()
            print "[INFO] scale logY on upper pad"
        elif(var_name== 'Hmass'):
            self.stack.SetMaximum(10e4)
            self.stack.SetMinimum(10e-2)
            upper_pad.SetLogy()
            print "[INFO] scale logY on upper pad"
        else:
            self.stack.SetMaximum(Draw_max)
            #self.stack.SetMaximum(230)
            self.stack.SetMinimum(0)

        print "[INFO] background = "+str(backgrounds)

        print "[INFO] draw stack"
        self.stack.Draw('histo')
        self.stack.GetYaxis().SetTitle("Events/%s GeV"%str(histos[Region][temp_sample][cat][var_name].GetBinWidth(1)))
        #stack.GetYaxis().SetTitle("Events/%s GeV"%str(50))
        self.stack.GetYaxis().SetTitleSize(0.025)
        self.stack.GetYaxis().SetLabelSize(0.025)
        #if(var_name=='Hmass'):
        #    stack.GetXaxis().SetTitle('m #font[12]{zz}')
        #else:
        self.stack.GetXaxis().SetTitle(titile)
        self.stack.GetXaxis().SetTitleSize(0.035)
        self.stack.GetXaxis().SetLabelSize(0.025)

        for sample in samples:
            if(sample.find('GluGluHToZZTo2L2Q')!=-1 or sample.find('BulkGraviton_ggF_ZZ_ZlepZhad_narrow')!=-1):
                histos[Region][sample][cat][var_name].Draw('same histo')
                print "[INFO] singal = "+str(histos[Region][sample][cat][var_name].Integral())

        #histos['Data'][var_name].Draw("SAME p E0 X0")
        #histos[Region]['Data'][cat][var_name].Draw("SAME p E X0")
        histoData.Draw("SAME p E X0")

        #cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
        cms_label.Draw('same')
        lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)'%str(self.lumi))
        lumi_label.Draw('same')
        legend.Draw()

        #============================draw data/mc raio plot==================================
        c.cd()
        lower_pad = TPad("lowerpad_"+titile, "lowerpad_"+titile, 0, 0, 1,0.20)
        lower_pad.SetTopMargin(0.05)
        lower_pad.SetGridy()
        lower_pad.Draw()
        lower_pad.cd()
        #ratio_plot = self.MakeRatioPlot(histos[Region]['Data'][cat][var_name],self.stack.GetStack().Last(),var_name)
        ratio_plot = self.MakeRatioPlot(histoData,self.stack.GetStack().Last(),var_name)
        ratio_plot.Draw("AP")


        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if(titile[0]=='#'):
            titile = titile.split('#')[1]
        plotname = self.plotspaths+"/{0}_{1}_{2}_{3}".format(titile,name,Region,cat)
        plotHelper.SavePlots(self,c,plotname)

    #============================================================================
    def MakeRatioPlot(self,h_data,h_MC,var_name):
        ratio_plot = TGraphAsymmErrors()
        ratio_plot.Divide(h_data, h_MC, "pois")
        ratio_plot.SetName("ratiograph_" + var_name)
        ratio_plot.SetMinimum(0.5)
        ratio_plot.SetMaximum(1.5)
        ratio_plot.SetMarkerStyle(20)
        ratio_plot.SetMarkerSize(0.5)

        ratio_plot.GetXaxis().SetRangeUser( h_data.GetXaxis().GetXmin(), h_data.GetXaxis().GetXmax() )
        ratio_plot.GetXaxis().SetLabelSize(0.1)
        ratio_plot.GetXaxis().SetTitle(var_name)
        ratio_plot.GetXaxis().SetTitleSize(0.02)
        ratio_plot.GetXaxis().SetTitleOffset(0.5)

        ratio_plot.GetYaxis().SetNdivisions(505)
        ratio_plot.GetYaxis().SetLabelSize(0.10)
        ratio_plot.GetYaxis().SetTitle("Data/MC")
        ratio_plot.GetYaxis().SetTitleSize(0.1)
        ratio_plot.GetYaxis().SetTitleOffset(0.25)

        return ratio_plot

    #==================================================================================
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

        plotname = "plot/{0}_signal_{1}".format(var_name,name)
        self.SavePlots(c,plotname)

    #==============================================================================
    def AddIngredient(self,histos,Region,sample,var_name):
        if var_name == 'Z1_mass_ele':
            self.stack.Add(histos[Region][sample]['Z1_mass_ele_Gengamma'])
        elif var_name == 'Z1_pt_ele':
            self.stack.Add(histos[Region][sample]['Z1_pt_ele_Gengamma'])
        elif var_name == 'Z1_eta_ele':
            self.stack.Add(histos[Region][sample]['Z1_eta_ele_Gengamma'])
        elif var_name == '_Z1_eta_mu':
            self.stack.Add(histos[Region][sample]['Z1_eta_mu_Gennotmu'])
        elif var_name == 'Z1_pt_mu':
            self.stack.Add(histos[Region][sample]['Z1_pt_mu_Gennotmu'])
        elif var_name == 'Z1_mass_mu':
            self.stack.Add(histos[Region][sample]['Z1_mass_mu_Gennotmu'])

    #==============================================================================

    def GetWeight(self,sample,event):
        if(sample.find('DYJetsToLL_Pt-100To250')!=-1):
            #weight = self.lumi*1000*96.8*event.eventWeight/self.sumWeights[sample]
            #weight = self.lumi*1000*96.8*event.eventWeight/81687671.0
            #weight = self.lumi*1000*96.8*event.genWeight*event.pileupWeight/81687671.0
            weight = self.lumi*1000*84.014804*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DYJetsToLL_Pt-50To100')!=-1):
            #weight = self.lumi*1000*354.3*event.eventWeight/self.sumWeights[sample]
            weight = self.lumi*1000*363.8142*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DYJetsToLL_Pt-250To400')!=-1):
            #weight = self.lumi*1000*3.765*event.eventWeight/self.sumWeights[sample]
            #weight = self.lumi*1000*3.765*event.eventWeight/20199757.0
            #weight = self.lumi*1000*3.765*event.genWeight*event.pileupWeight/20199757.0
            weight = self.lumi*1000*3.047*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DYJetsToLL_Pt-400To650')!=-1):
            weight = self.lumi*1000*0.392*event.eventWeight/self.sumWeights[sample]
            #weight = self.lumi*1000*0.5149*event.eventWeight/1863809.0
            #weight = self.lumi*1000*0.5149*event.genWeight*event.pileupWeight/1863809.0
            #weight = self.lumi*1000*0.392*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DYJetsToLL_Pt-650ToInf')!=-1):
            #weight = self.lumi*1000*0.04825*event.eventWeight/1895998.0
            #weight = self.lumi*1000*0.04825*event.genWeight*event.pileupWeight/1895998.0
            weight = self.lumi*1000*0.03636*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DYJetsToLL_M-50')!=-1):
            if(sample.find('madgraphMLM')!=-1):
                weight = self.lumi*1000*4927.0*event.eventWeight/self.sumWeights[sample]
            else:
                weight = self.lumi*1000*5941.0*event.eventWeight/self.sumWeights[sample]
            #weight = self.lumi*1000*5941.0*event.eventWeight/self.sumWeights[sample]
            #weight = self.lumi*1000*6225.4*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DY1JetsToLL_M')!=-1):
            weight = self.lumi*1000*1012.0*event.eventWeight/self.sumWeights[sample]

        elif(sample.find('DY2JetsToLL_M')!=-1):

            weight = self.lumi*1000*334.7*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DY3JetsToLL_M')!=-1):

            weight = self.lumi*1000*102.3*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DY4JetsToLL_M')!=-1):

            weight = self.lumi*1000*54.52*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('DYBJetsToLL_M')!=-1):
            weight = self.lumi*1000*70.08*event.eventWeight/self.sumWeights[sample]
        elif(sample=='TTJets'):

            weight = self.lumi*1000*722.8*event.eventWeight/10244307.0
            #weight = self.lumi*1000*722.8*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('TTJets_DiLept')!=-1):
            weight = self.lumi*1000*56.86*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('TTTo2L2Nu_TuneCUETP8M2')!=-1):
            weight = self.lumi*1000*87.3*event.eventWeight/self.sumWeights[sample]

        elif(sample.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV')!=-1):
            weight = self.lumi*1000*88.29*event.eventWeight/self.sumWeights[sample]
        elif(sample=='ZZ_TuneCP5'):
            #weight = self.lumi*1000*12.10*event.eventWeight/self.sumWeights[sample]
            weight = self.lumi*1000*12.10*event.eventWeight/1979000.0
        elif(sample.find('WZ_TuneCUETP8M1_13TeV')!=-1):
            #weight = self.lumi*1000*27.27*event.eventWeight/3885000.0
            weight = self.lumi*1000*23.43*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8')!=-1):
            #weight = self.lumi*1000*27.27*event.eventWeight/3885000.0
            weight = self.lumi*1000*4.67*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('WZTo2L2Q')!=-1):
            weight = self.lumi*1000*5.595*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('ZZTo2L2Q')!=-1 and sample.find('GluGluHToZZTo2L2Q')==-1):
            weight = self.lumi*1000*3.222*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('WW_TuneCUETP8M1_13TeV')!=-1):
            weight = self.lumi*1000*64.3*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('WWTo2L2Nu_13TeV-powheg')!=-1):
            weight = self.lumi*1000*10.48*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('ST_s')!=-1):
            weight = self.lumi*1000*3.365*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('ST_t-channel')!=-1):
            weight = self.lumi*1000*141.9*event.eventWeight/self.sumWeights[sample]
        elif(sample.find('ST_tW')!=-1):
            weight = self.lumi*1000*38.06*event.eventWeight/self.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M900'):
            weight = self.lumi*5.07*event.eventWeight/self.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M1000'):
            if(self.year=='2016Legacy'):
                #weight = self.lumi*1000*0.1129*event.eventWeight/self.sumWeights[sample]
                weight = self.lumi*1000*0.1129*event.eventWeight/200000.0
            elif(self.year=='2018Legacy'):
                weight = self.lumi*1000*0.1023*event.eventWeight/self.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M1500'):
            weight = self.lumi*1000*0.01308*event.eventWeight/self.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M2000'):
            if(self.year=='2016Legacy'):
                weight = self.lumi*1000*0.0055*event.eventWeight/self.sumWeights[sample]
            elif(self.year=='2018Legacy'):
                weight = self.lumi*1000*0.0055*event.eventWeight/self.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M2500'):
            weight = self.lumi*1000*0.002207*event.eventWeight/self.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_M3000'):
            if(self.year=='2016Legacy'):
                weight = self.lumi*1000*0.001037*event.eventWeight/self.sumWeights[sample]
            elif(self.year=='2018Legacy'):
                weight = self.lumi*1000*0.001037*event.eventWeight/self.sumWeights[sample]
        elif(sample=='GluGluHToZZTo2L2Q_MAll'):
            weight = self.lumi*1000*0.02314*event.eventWeight/self.sumWeights[sample]
        elif(sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M1000'):
            weight = self.lumi*1000*0.03883*event.eventWeight/self.sumWeights[sample]
        elif(sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M2000'):
            weight = self.lumi*1000*0.001029*event.eventWeight/self.sumWeights[sample]
        elif(sample=='BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M3000'):
            weight = self.lumi*1000*0.0000666*event.eventWeight/self.sumWeights[sample]
        elif(sample=='QCD'):
            weight = self.lumi*1000*191700*event.eventWeight/self.sumWeights[sample]
        else:
            weight=1.0




        if(self.year!='2018Legacy' and sample.find('Data')==-1 and sample.find('SingleMuon_Run2016')==-1 and sample.find('SingleElectron_Run2016')==-1):
            #print 1
            weight = weight*event.prefiringWeight

        #if(sample.find('DY1JetsToLL_M')!=-1 or sample.find('DY2JetsToLL_M')!=-1 or sample.find('DY3JetsToLL_M')!=-1 or sample.find('DY4JetsToLL_M')!=-1 or sample.find('DYBJetsToLL_M')!=-1 or (sample.find('DYJetsToLL_M')!=-1 and sample.find('madgraphMLM')!=-1)):
        return weight

    #============================================================================
    def Normalize(self,histo):
        histo.Scale(1/histo.Integral())

    #======================================================================================

    def specifyVarName(self,var_name,cat):
        if(cat == '2e'):
            if(var_name=='Z1_pt'):
                titile = "Pt_{2e} (GeV)"
            elif(var_name=='Z1_eta'):
                titile = "#eta_{2e}"
            elif(var_name=='Z1_mass'):
                titile = "M_{2e} (GeV)"
            elif(var_name=='Lep1_pt'):
                titile = "Pt_{leadingEle}"
            elif(var_name=='Lep1_eta'):
                titile = "#eta_{leadingEle}"
            elif(var_name=='Lep1_mass'):
                titile = "M_{leadingEle}"
            elif(var_name=='Lep2_pt'):
                titile = "Pt_{subleadingEle}"
            elif(var_name=='Lep2_eta'):
                titile = "#eta_{subleadingEle}"
            elif(var_name=='Lep2_mass'):
                titile = "M_{subleadingEle}"
            elif(var_name=='SDmass'):
                titile = 'M_{J with 2e} (GeV)'
            elif(var_name=='SDmassUncorr'):
                titile = 'M_{J with 2e uncorrected} (GeV)'
            elif(var_name=='SDmasscorr'):
                titile = 'M_{J with 2e corrected by PUPPIweight} (GeV)'
            elif(var_name=='Pt'):
                titile = 'Pt_{J with 2e} (GeV)'
            elif(var_name=='eta'):
                titile = '#eta_{J with 2e}'
            elif(var_name=='ZvsQCD_de'):
                titile = 'ZvsQCD_{MD with 2e}'
            elif(var_name=='particleNet_ZvsQCD_de'):
                titile = 'particleNet_{Score with 2e}'
            elif(var_name=='particleNet_ZbbvsQCD_de'):
                titile = 'particleNet_{ZbbvsQCD Score with 2e}'
            elif(var_name=='particleNet_ZBtgger_de'):
                titile = 'particleNet_{Btagger Score with 2e}'
            elif(var_name=='ZbbvsQCD_de'):
                titile = 'ZbbvsQCD_{MD with 2e}'
            elif(var_name=='tau21_DDT'):
                titile = '#tau_{21MD with 2e}'
            elif(var_name=='tau21'):
                titile = '#tau_{21 with 2e}'
            elif(var_name=='Hmass'):
                titile = 'M_{ZZ with 2e} (GeV)'
            elif(var_name=='Nmergedjets'):
                titile = 'N_[J with 2e]'
            elif(var_name=='Njets'):
                titile = 'N_[Ak4 with 2e]'
        elif(cat == '2mu'):
            if(var_name=='Z1_pt'):
                titile = "Pt_{2mu} (GeV)"
            elif(var_name=='Z1_eta'):
                titile = "#eta_{2mu}"
            elif(var_name=='Z1_mass'):
                titile = "M_{2mu} (GeV)"
            elif(var_name=='Lep1_pt'):
                titile = "Pt_{leadingEle}"
            elif(var_name=='Lep1_eta'):
                titile = "#eta_{leadingMu}"
            elif(var_name=='Lep1_mass'):
                titile = "M_{leadingMu}"
            elif(var_name=='Lep2_pt'):
                titile = "Pt_{subleadingMu}"
            elif(var_name=='Lep2_eta'):
                titile = "#eta_{subleadingMu}"
            elif(var_name=='Lep2_mass'):
                titile = "M_{subleadingMu}"
            elif(var_name=='SDmass'):
                titile = 'M_{J with 2mu} (GeV)'
            elif(var_name=='SDmassUncorr'):
                titile = 'M_{J with 2mu uncorrected} (GeV)'
            elif(var_name=='SDmasscorr'):
                titile = 'M_{J with 2mu corrected by PUPPIweight} (GeV)'
            elif(var_name=='Pt'):
                titile = 'Pt_{J with 2mu} (GeV)'
            elif(var_name=='eta'):
                titile = '#eta_{J with 2mu}'
            elif(var_name=='ZvsQCD_de'):
                titile = 'ZvsQCD_{MD with 2mu}'
            elif(var_name=='particleNet_ZvsQCD_de'):
                titile = 'particleNet_{Score with 2mu}'
            elif(var_name=='particleNet_ZbbvsQCD_de'):
                titile = 'particleNet_{ZbbvsQCD Score with 2mu}'
            elif(var_name=='particleNet_ZBtgger_de'):
                titile = 'particleNet_{Btagger Score with 2mu}'
            elif(var_name=='ZbbvsQCD_de'):
                titile = 'ZbbvsQCD_{MD with 2mu}'
            elif(var_name=='tau21_DDT'):
                titile = '#tau_{21MD with 2mu}'
            elif(var_name=='tau21'):
                titile = '#tau_{21 with 2mu}'
            elif(var_name=='Hmass'):
                titile = 'M_{ZZ with 2mu} (GeV)'
            elif(var_name=='Nmergedjets'):
                titile = 'N_[J with 2mu]'
            elif(var_name=='Njets'):
                titile = 'N_[Ak4 with 2mu]'
        elif(cat == '2lep'):
            if(var_name=='SDmasscorr'):
                titile = 'M_{J with 2leps corrected by PUPPIweight} (GeV)'
            elif(var_name=='met'):
                titile = 'MET'
            elif(var_name=='particleNet_ZvsQCD_de'):
                titile = 'particleNet_{Score with 2lep}'
            elif(var_name=='particleNet_ZBtgger_de'):
                titile = 'particleNet_{btagger with 2lep}'




        elif(var_name=='dR_lep'):
            titile = '#DeltaR(ll)'
        elif(var_name=='dR_ZZ'):
            titile = '#DeltaR(ZZ)'
        elif(var_name=='HvsSD'):
            titile = 'M_{ZZ} VS M_{Merged}'
        elif(var_name=='met'):
            titile = 'MET'
        elif(var_name=='muon_pt'):
            titile = 'Pt_{muon}'
        elif(var_name=='muon_eta'):
            titile = '#eta_{muon}'
        elif(var_name=='muon_mass'):
            titile = 'M_{muon}'
        elif(var_name=='electron_pt'):
            titile = 'Pt_{electron}'
        elif(var_name=='electron_eta'):
            titile = '#eta_{electron}'
        elif(var_name=='electron_mass'):
            titile = 'M_{electron}'
        elif(var_name=='muon1_pt'):
            titile = 'Pt_{muon2}'
        elif(var_name=='muon1_eta'):
            titile = '#eta_{muon2}'
        elif(var_name=='muon1_mass'):
            titile = 'M_{muon2}'
        elif(var_name=='electron1_pt'):
            titile = 'Pt_{electron2}'
        elif(var_name=='electron1_eta'):
            titile = '#eta_{electron2}'
        elif(var_name=='electron1_mass'):
            titile = 'M_{electron2}'
        elif(var_name=='Z1_pt_mu'):
            titile = 'Pt_{2mu}'
        elif(var_name=='Z1_eta_mu'):
            titile = '#eta_{2mu}'
        elif(var_name=='Z1_mass_mu'):
            titile = 'M_{2mu}'
        elif(var_name=='Z1_pt_ele'):
            titile = 'Pt_{2e}'
        elif(var_name=='Z1_eta_ele'):
            titile = '#eta_{2e}'
        elif(var_name=='Z1_mass_ele'):
            titile = 'M_{2e}'
        elif(var_name=='Z1_mass_ele_Gengamma'):
            titile = 'M_{2eGenGamma}'
        elif(var_name=='Z1_pt_ele_Gengamma'):
            titile = 'Pt_{2eGenGamma}'
        elif(var_name=='Z1_eta_ele_Gengamma'):
            titile = '#eta_{2eGenGamma}'
        elif(var_name=='Z1_mass_mu_Gennotmu'):
            titile = 'M_{2muGennotmu}'
        elif(var_name=='Z1_pt_mu_Gennotmu'):
            titile = 'Pt_{2muGennotmu}'
        elif(var_name=='Z1_eta_mu_Gennotmu'):
            titile = '#eta_{2muGennotmu}'
        else:
            titile = 'ERROR'
        return titile


    def SavePlots(self,c,name):
        c.SaveAs(name+".png")



    #==========================backup codes=====================================
    #==========================backup codes=====================================
    #==========================backup codes=====================================
    def readsumweight(self):
        for sample_name in self.sample_names:
            #print "[INFO] start to test sumWeights"
            #print sample_name.find('DYJetsToLL_Pt250To400')
            #if((sample_name.find('DYJetsToLL_Pt-50To100') == -1) and (sample_name.find('DYJetsToLL_Pt-100To250') == -1) and (sample_name.find('DYJetsToLL_Pt-250To400') == -1) and (sample_name.find('DYJetsToLL_Pt-400To650') == -1) and (sample_name.find('DYJetsToLL_Pt-650ToInf') == -1) and (sample_name.find('DYJetsToLL_M-50') == -1) and (sample_name.find('WZTo2L2Q') ==-1) and (sample_name.find('ZZTo2L2Q') ==-1) and (sample_name.find('TTJets_DiLept') ==-1)): continue
            if(sample_name.find('Data') != -1 and sample_name.find('SingleMuon_Run2016') != -1): continue

            if(sample_name.find('DYJetsToLL_Pt-50To100') != -1):
                print "[INFO] this is DYJetsToLL_Pt-50To100 sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYJetsToLL_Pt-50To100') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYJetsToLL_Pt-50To100 = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DYJetsToLL_Pt-100To250') != -1):
                print "[INFO] this is DYJetsToLL_Pt-100To250 sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYJetsToLL_Pt-100To250') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYJetsToLL_Pt-100To250 = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DYJetsToLL_Pt-250To400') != -1):
                print "[INFO] this is DYJetsToLL_Pt-250To400 sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYJetsToLL_Pt-250To400') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYJetsToLL_Pt-250To400 = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DYJetsToLL_Pt-400To650') != -1):
                print "[INFO] this is DYJetsToLL_Pt-400To650 sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYJetsToLL_Pt-400To650') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYJetsToLL_Pt-400To650 = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DYJetsToLL_Pt-650ToInf') != -1):
                print "[INFO] this is DYJetsToLL_Pt-650ToInf sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYJetsToLL_Pt-650ToInf') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYJetsToLL_Pt-650ToInf = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DYJetsToLL_M-50') != -1):
                if(sample_name.find('madgraphMLM')!=-1):
                    print "[INFO] this is DYJetsToLL_M-50 LO sample"
                    for sample_path in self.sample_paths[self.year]:
                        if(sample_path.find('DYJetsToLL_M')!=-1 and sample_path.find('madgraphMLM')!=-1):
                            print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                            tempfile = TFile(sample_path)
                            print "[INFO] sumWeights for DYJetsToLL_M-50 LO = "+str(self.sumWeights[sample_name])
                            print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                            self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                    print "[INFO] sumWeights for DYJetsToLL_M-50 LO = {}".format(self.sumWeights[sample_name])

                else:
                    print "[INFO] this is DYJetsToLL_M-50 NLO sample"
                    for sample_path in self.sample_paths[self.year]:
                        if(sample_path.find('DYJetsToLL_M-50') !=-1 and sample_path.find('amcatnloFXFX')!=-1):
                            print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                            tempfile = TFile(sample_path)
                            print "[INFO] sumWeights for DYJetsToLL_M-50 NLO = "+str(self.sumWeights[sample_name])
                            print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                            self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                    print "[INFO] sumWeights for DYJetsToLL_M-50 NLO = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DY1JetsToLL_M') != -1):
                print "[INFO] this is DY1JetsToLL_M sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DY1JetsToLL_M') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DY1JetsToLL_M = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DY2JetsToLL_M') != -1):
                print "[INFO] this is DY2JetsToLL_M sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DY2JetsToLL_M') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DY2JetsToLL_M = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DY3JetsToLL_M') != -1):
                print "[INFO] this is DY1JetsToLL_M sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DY3JetsToLL_M') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DY3JetsToLL_M = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DY4JetsToLL_M') != -1):
                print "[INFO] this is DY4JetsToLL_M sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DY4JetsToLL_M') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DY4JetsToLL_M = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('DYBJetsToLL_M') != -1):
                print "[INFO] this is DY1JetsToLL_M sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('DYBJetsToLL_M') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for DYBJetsToLL_M = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('WZTo2L2Q') != -1):
                print "[INFO] this is WZTo2L2Q sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('WZTo2L2Q') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for WZTo2L2Q = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for WZTo2L2Q = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('WW_TuneCUETP8M1_13TeV') != -1):
                print "[INFO] this is WW_TuneCUETP8M1_13TeV sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('WW_TuneCUETP8M1_13TeV') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for WW_TuneCUETP8M1_13TeV = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for WW_TuneCUETP8M1_13TeV = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('WWTo2L2Nu_13TeV-powheg') != -1):
                print "[INFO] this is WWTo2L2Nu_13TeV-powheg sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('WWTo2L2Nu_13TeV-powheg') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for WWTo2L2Nu_13TeV-powheg = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for WWTo2L2Nu_13TeV-powheg = {}".format(self.sumWeights[sample_name])


            if(sample_name.find('WZ_TuneCUETP8M1_13TeV') != -1):
                print "[INFO] this is WZ_TuneCUETP8M1_13TeV sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('WZ_TuneCUETP8M1_13TeV') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for WZ_TuneCUETP8M1_13TeV = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for WZ_TuneCUETP8M1_13TeV = {}".format(self.sumWeights[sample_name])


            if(sample_name.find('ZZTo2L2Q') != -1 and sample_name.find('GluGluHToZZTo2L2Q') == -1):
                print "[INFO] this is ZZTo2L2Q sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('ZZTo2L2Q') !=-1 and sample_path.find('GluGluHToZZTo2L2Q')==-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for ZZTo2L2Q = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for ZZTo2L2Q = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('TTJets_DiLept') != -1):
                print "[INFO] this is TTJets_DiLept sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('TTJets_DiLept') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for TTJets_DiLept = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for TTJets_DiLept = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('TTTo2L2Nu_TuneCUETP8M2') != -1):
                print "[INFO] this is TTTo2L2Nu_TuneCUETP8M2 sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('TTTo2L2Nu_TuneCUETP8M2') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for TTTo2L2Nu_TuneCUETP8M2 = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for TTTo2L2Nu_TuneCUETP8M2 = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV') != -1):
                print "[INFO] this is TTTo2L2Nu_TuneCP5_PSweights_13TeV sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('TTTo2L2Nu_TuneCP5_PSweights_13TeV') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for TTTo2L2Nu_TuneCP5_PSweights_13TeV = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for TTTo2L2Nu_TuneCP5_PSweights_13TeV = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('ST_s-channel') != -1):
                print "[INFO] this is ST_s-channel sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('ST_s-channel') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for ST_s-channel = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for ST_s-channel = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('ST_t-channel') != -1):
                print "[INFO] this is ST_t-channel sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('ST_t-channel') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for ST_t-channel = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for ST_t-channel = {}".format(self.sumWeights[sample_name])

            if(sample_name.find('ST_tW') != -1):
                print "[INFO] this is ST_tW sample"
                for sample_path in self.sample_paths[self.year]:
                    if(sample_path.find('ST_tW') !=-1):
                        print "[INFO] find {0:s} sample to get sumWeights, stroe in {1:s}".format(sample_name,sample_path)
                        tempfile = TFile(sample_path)
                        print "[INFO] sumWeights for ST_tW = "+str(self.sumWeights[sample_name])
                        print "[INFO] this sumWeights = "+str(tempfile.Ana.Get("sumWeights").GetBinContent(1))
                        self.sumWeights[sample_name] += tempfile.Ana.Get("sumWeights").GetBinContent(1)
                print "[INFO] sumWeights for ST_tW = {}".format(self.sumWeights[sample_name])
