import ROOT
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
import Analyzer_Configs as AC
import Plot_Configs     as PC
from Plot_Helper import *
from deltaR import *
from SSMethod import *

datafile = "/cms/user/guojl/Sample/skimed/2018_noDuplicates.root"
WZfile = "/cms/user/guojl/Sample/skimed/WZ_2018.root"
SS=SSMethod()

#===============================================================================
#=============produce SSCR samples==============================================
#===============================================================================

SS.FillFRHistos(datafile,'data')
SS.FillFRHistos(WZfile,'WZ')


#SS.GetFRHistos('2018')
SS.SSFRproduce('2018','data')
