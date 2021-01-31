import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
from Plot_Helper import *
from deltaR import *
from OSMethod import *
import FakeRates as FR

datafile = "/cms/user/guojl/Sample/skimed/2018_noDuplicates.root"
WZfile = "/cms/user/guojl/Sample/WZTo3LNu_TuneCP5_13TeV_filter2l.root"
#Zjetfile = "/cms/user/guojl/Sample/DY_2018.root"
#Zjetfile = "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018_filter2l.root"
Zjetfile = "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV_2018_filter2lCombine.root"
TTbarfile = "/cms/user/guojl/Sample/TTTo2L2Nu_TuneCP5_13TeV_2018_filter2l.root"
qqZZfile = "/cms/user/guojl/Sample/qqZZ_2018.root"
FakeRateFile = "/cms/user/guojl/CMSSW_10_6_12/src/HToZZ4lRepeat/RawHistos/FakeRates_SS_2018_Legacy.root"
OS=OSMethod(2018)

#===============================================================================
#=============produce SSCR samples==============================================
#===============================================================================
OS.FillCRHistos(datafile,'data')
OS.FillCRHistos(WZfile,'WZ')
OS.FillCRHistos(TTbarfile,'TT')
OS.FillCRHistos(qqZZfile,'qqZZ')
OS.FillCRHistos(Zjetfile,'DY')
OS.SaveCRHistos()

OS.GetCRHistos()
OS.PlotCR()
