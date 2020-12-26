import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
from Plot_Helper import *
from deltaR import *
from SSMethod import *

gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(False)

def main():
        save_dir = 'plot'
        analyzer_cfg = AC.Analyzer_Config('inclusive')
        ntuples = LoadNtuples(analyzer_cfg)
        print "get ntuples done "
        print "start test ntuple"
        print "number of events after loading = " +str(ntuples['DY'].GetEntries())

        cat_names = ['4e2P2F', '4mu2P2F', '2mu2e2P2F', '2e2mu2P2F','4e3P1F', '4mu3P1F', '2mu2e3P1F', '2e2mu3P1F']
        plot_cfg = PC.Plot_Config(analyzer_cfg)

        #declare hito
        histos = {}
        for cat_name in cat_names:
            histos[cat_name] = {}
        for sample in analyzer_cfg.samp_names:
            histos['4e2P2F'][sample] = ROOT.TH1D(sample+'4e2P2F',sample+'4e2P2F',40,70,870)
            histos['4mu2P2F'][sample] = ROOT.TH1D(sample+'4mu2P2F',sample+'4mu2P2F',40,70,870)
            histos['2mu2e2P2F'][sample] = ROOT.TH1D(sample+'2mu2e2P2F',sample+'2mu2e2P2F',40,70,870)
            histos['2e2mu2P2F'][sample] = ROOT.TH1D(sample+'2e2mu2P2F',sample+'2e2mu2P2F',40,70,870)
            histos['4e3P1F'][sample] = ROOT.TH1D(sample+'4e3P1F',sample+'4e3P1F',40,70,870)
            histos['4mu3P1F'][sample] = ROOT.TH1D(sample+'4mu3P1F',sample+'4mu3P1F',40,70,870)
            histos['2mu2e3P1F'][sample] = ROOT.TH1D(sample+'2mu2e3P1F',sample+'2mu2e3P1F',40,70,870)
            histos['2e2mu3P1F'][sample] = ROOT.TH1D(sample+'2e2mu3P1F',sample+'2e2mu3P1F',40,70,870)

        #loop over samples and events
        passedCR = 0
        passedID = 0
        twoFailed = 0
        oneFailed = 0
        print " will start loop samples = "+str(analyzer_cfg.samp_names)
        for sample in analyzer_cfg.samp_names:
            print " enter the loop of samples = " + sample
            ntup = ntuples[sample]
            #print "type of ntup = "+str(type(ntup))
            #print "get ntuple"
            #print ntuples[sample].GetEntries()
            for ievent,event in enumerate(ntup):
                if(ievent==10000): break
                if(sample=='DY'):
                    #weight = 35.9*1000*6104*event.eventWeight/event.crossSection/81781072.0
                    weight = 59.7*1000*6225.4*event.eventWeight/130939680.0
                    #weight = 59.7*1000*6225.4*event.eventWeight/event.crossSection/130939680.0
                elif(sample=='WZ'):
                    #weight = 59.7*1000*4.67*event.eventWeight/event.crossSection/3110669.0
                    weight = 59.7*1000*4.67*event.eventWeight/3110669.0
                elif(sample=='TT'):
                    #weight = 59.7*1000*87.31*event.eventWeight/event.crossSection/32584720.0
                    weight = 59.7*1000*87.31*event.eventWeight/32584720.0
                elif(sample=='qqZZ'):
                    weight = 59.7*1000*1.256*event.eventWeight*event.k_qqZZ_qcd_M*event.k_qqZZ_ewk/event.crossSection/18896902.0
                else:
                    weight = 1.0
                #print "enter the loop of events"
                if(not event.passedZXCRSelection): continue
                passedCR += 1
                if(event.lep_id[event.lep_Hindex[0]]*event.lep_id[event.lep_Hindex[1]]>0 or event.lep_id[event.lep_Hindex[2]]+event.lep_id[event.lep_Hindex[3]]>0):continue
                passedID += 1
                l1 = ROOT.TLorentzVector()
                l2 = ROOT.TLorentzVector()
                l3 = ROOT.TLorentzVector()
                l4 = ROOT.TLorentzVector()
                l1.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[3]])
                l2.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[3]])
                l3.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[3]])
                l4.SetPtEtaPhiM(event.lepFSR_pt[event.lep_Hindex[0]],event.lepFSR_eta[event.lep_Hindex[1]],event.lepFSR_phi[event.lep_Hindex[2]],event.lepFSR_mass[event.lep_Hindex[3]])
                mass4l = (l1+l2+l3+l4).M()
                if(event.nZXCRFailedLeptons==2):
                    twoFailed +=1
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==11):
                        histos['4e2P2F'][sample].Fill(mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==13):
                        histos['4mu2P2F'][sample].Fill(mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==11 and event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==13):
                        histos['2e2mu2P2F'][sample].Fill(mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==13 and event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==11):
                        histos['2mu2e2P2F'][sample].Fill(mass4l,weight)
                if(event.nZXCRFailedLeptons==1):
                    oneFailed +=1
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==11):
                        histos['4e3P1F'][sample].Fill(mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==13):
                        histos['4mu3P1F'][sample].Fill(mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==11 and event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==13):
                        histos['2e2mu3P1F'][sample].Fill(mass4l,weight)
                    if(event.lep_id[event.lep_Hindex[0]]==event.lep_id[event.lep_Hindex[1]]==13 and event.lep_id[event.lep_Hindex[2]]==event.lep_id[event.lep_Hindex[3]]==11):
                        histos['2mu2e3P1F'][sample].Fill(mass4l,weight)

        print"passedCR="+str(passedCR)
        print"passedID="+str(passedID)
        print"twoFailed="+str(twoFailed)
        print"oneFailed="+str(oneFailed)
        #set histoStyles
        for cat_name in cat_names:
            for sample in analyzer_cfg.samp_names:
                plot_cfg.SetHistStyles(histos[cat_name][sample], sample,cat_name)

        # save stack plots and make ratio plots
        lumi_label = MakeLumiLabel(plot_cfg.lumi)
        cms_label  = MakeCMSDASLabel()

        for cat_name in cat_names:
            stacks = MakeStack(histos[cat_name], analyzer_cfg, cat_name)
            scaled_data = MakeDataLabel(stacks['data'],cat_name)
            legend = MakeLegend(plot_cfg, histos[cat_name])

            canv = CreateCanvas(cat_name)
            DrawOnCanv(canv, cat_name, plot_cfg, stacks, histos[cat_name], scaled_data,legend, lumi_label, cms_label)
            save_name = cat_name+"OS2018"
            SaveCanvPic(canv, save_dir, save_name)

main()
