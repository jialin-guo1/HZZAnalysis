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
WZfile = "/cms/user/guojl/Sample/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18MiniAOD-102X_2018_filter2l_new.root"
#Zjetfile = "/cms/user/guojl/Sample/DY_2018.root"
#Zjetfile = "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_2018_filter2l.root"
Zjetfile = "/cms/user/guojl/Sample/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8_2018filter2l_new.root"
TTbarfile = "/cms/user/guojl/Sample/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new.root"
qqZZfile = "/cms/user/guojl/Sample/ZZTo4L_TuneCP5_13TeV_powheg_pythia8_RunIIAutumn18MiniAOD-102X_2018filter2l_new.root"
FakeRateFile = "../RawHistos/FakeRates_OS_2018_Legacy.root"
OS=OSMethod(2018)

#===============================================================================
#=============produce OSCR samples==============================================
#===============================================================================
#OS.FillCRHistos(datafile,'data')
#OS.FillCRHistos(WZfile,'WZ')
#OS.FillCRHistos(TTbarfile,'TT')
#OS.FillCRHistos(qqZZfile,'qqZZ')
#OS.FillCRHistos(Zjetfile,'DY')
#OS.FillCRHistosTest(datafile,'data')
#OS.FillCRHistosTest(WZfile,'WZ')
#OS.FillCRHistosTest(TTbarfile,'TT')
#OS.FillCRHistosTest(qqZZfile,'qqZZ')
#OS.FillCRHistosTest(Zjetfile,'DY')
#OS.SaveCRHistos()



#OS.GetCRHistos()
#OS.PlotCR()
#===============================================================================
#=====================FakeRates=================================================
#===============================================================================
OS.FillFRHistos(datafile,'data')
OS.FillFRHistos(WZfile,'WZ')
OS.SaveFRHistos(True,'Remove_NegBins_FR')

OS.GetFRHistos()
OS.OSFRproduce('data')

#===============================================================================
#========================ZX=====================================================
#===============================================================================
#OS.MakeHistogramsZX_test(FakeRateFile,datafile,qqZZfile)
#OS.SaveZXHistos()
