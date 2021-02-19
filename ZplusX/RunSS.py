import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
from Plot_Helper import *
from deltaR import *
from SSMethod import *
import FakeRates as FR

datafile = "/cms/user/guojl/Sample/skimed/2018_noDuplicates.root"
WZfile = "/cms/user/guojl/Sample/WZTo3LNu_TuneCP5_13TeV_filter2l.root"
#Zjetfile = "/cms/user/guojl/Sample/DY_2018.root"
#Zjetfile = "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018_filter2l.root"
Zjetfile = "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV_2018_filter2lCombine.root"
TTbarfile = "/cms/user/guojl/Sample/TTTo2L2Nu_TuneCP5_13TeV_2018_filter2l.root"
qqZZfile = "/cms/user/guojl/Sample/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_v15_ext1-v2_2018_filter2l.root"
FakeRateFile = "../RawHistos/FakeRates_SS_2018_Legacy.root"
#FakeRateFile = "/cms/user/guojl/Sample/FakeRates/FakeRates_SS_2018_Legacy.root"
OSCRfile  = "../RawHistos/CRHistos_OS_2018_Legacy.root"
SS=SSMethod(2018)

#===============================================================================
#=============produce SSCR samples==============================================
#===============================================================================
#SS.FillCRHistos(datafile,'data')
#SS.FillCRHistos(WZfile,'WZ')
#SS.FillCRHistos(TTbarfile,'TT')
#SS.FillCRHistos(qqZZfile,'qqZZ')
#SS.FillCRHistos(Zjetfile,'DY')
#SS.SaveCRHistos()

#SS.GetCRHistos()
#SS.PlotCR()

#===============================================================================
#=================calculate OS/SS ratio=========================================
#===============================================================================
#SS.Calculate_SSOS_Ratio(OSCRfile)

#================================================================================
#=================produce FakeRates==============================================
#================================================================================

SS.FillFRHistos(datafile,'data')
SS.FillFRHistos(WZfile,'WZ')
SS.SaveFRHistos(True,'Remove_NegBins_FR')

SS.GetFRHistos()
SS.SSFRproduce('data',datafile)

#================================================================================
#===========================ZX estimate==========================================
#================================================================================
#SS.FillZXHistos(FakeRateFile,datafile)
