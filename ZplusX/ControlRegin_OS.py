import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
from Plot_Helper import *
from deltaR import *
from SSMethod import *

gROOT.SetBatch(True)

def main():
        save_dir = 'plot'
        analyzer_cfg = AC.Analyzer_Config('inclusive')
        ntuples = LoadNtuples(analyzer_cfg)
        print "get ntuples done "
        print "start test ntuple"
        print "number of events after loading = " +str(ntuples['DY'].GetEntries())

        cat_names = ['4e', '4mu', '2mu2e', '2e2mu']
        plot_cfg = PC.Plot_Config(analyzer_cfg)

        #declare hito
        histos = {}
        for cat_name in cat_names:
            histos[cat_name] = {}
        for sample in analyzer_cfg.samp_names:
            histos['4e'][sample] = ROOT.TH1D(sample+'4e',sample+'4e',40,70,800)
            histos['4mu'][sample] = ROOT.TH1D(sample+'4mu',sample+'4mu',40,70,800)
            histos['2mu2e'][sample] = ROOT.TH1D(sample+'2mu2e',sample+'2mu2e',40,70,800)
            histos['2e2mu'][sample] = ROOT.TH1D(sample+'2e2mu',sample+'2e2mu',40,70,800)

        #loop over samples and events
        print " will start loop samples = "+str(analyzer_cfg.samp_names)
        for sample in analyzer_cfg.samp_names:
            print " enter the loop of samples = " + sample
            ntup = ntuples[sample]
            #print "type of ntup = "+str(type(ntup))
            #print "get ntuple"
            #print ntuples[sample].GetEntries()
            for ievent,event in enumerate(ntup):
                if(sample=='DY'):
                    weight = 59.7*1000*6104*event.eventWeight/event.crossSection/130939680.0
                elif(sample=='WZ'):
                    weight = 59.7*1000*4.67*event.eventWeight/event.crossSection/3110669.0
                elif(sample=='TT'):
                    weight = 59.7*1000*4.67*event.eventWeight/event.crossSection/32584720.0
                elif(sample=='qqZZ'):
                    weight = 59.7*1000*4.67*event.eventWeight*event.k_qqZZ_qcd_M*event.k_qqZZ_ewk/event.crossSection/18896902.0
                else:
                    weight = 1.0
                #print "enter the loop of events"
                if(not event.passedZXCRSelection): continue
                if(event.lep_id[event.lep_Hindex[0]]+event.lep_id[event.lep_Hindex[1]]!=0 or event.lep_id[event.lep_Hindex[2]]+event.lep_id[event.lep_Hindex[3]]!=0):continue
                if(event.nZXCRFailedLeptons==2):
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==11):
                        histos['4e'][sample].Fill(event.mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==13):
                        histos['4mu'][sample].Fill(event.mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==11 and event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==13):
                        histos['2e2mu'][sample].Fill(event.mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==13 and event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==11):
                        histos['2mu2e'][sample].Fill(event.mass4l,weight)

        #set histoStyles
        for cat_name in cat_names:
            for sample in analyzer_cfg.samp_names:
                plot_cfg.SetHistStyles(histos[cat_name][sample], sample,cat_name)

        # save stack plots and make ratio plots
        lumi_label = MakeLumiLabel(plot_cfg.lumi)
        cms_label  = MakeCMSDASLabel()

        for cat_name in cat_names:
            stacks = MakeStack(histos[cat_name], analyzer_cfg, cat_name)
            scaled_data = MakeDataLabel(histo[cat_name]['data'],cat_name)
            legend = MakeLegend(plot_cfg, histos[cat_name], scaled_data)

            canv = CreateCanvas(cat_name)
            DrawOnCanv(canv, cat_name, plot_cfg, stacks, histos[cat_name], scaled_data,legend, lumi_label, cms_label)
            SaveCanvPic(canv, save_dir, cat_name)

main()
