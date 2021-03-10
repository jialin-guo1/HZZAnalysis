from ROOT import *
import os,sys
sys.path.append("%s/../lib" %os.getcwd())
from plotHelper import *

ZZfilename  = "/cms/user/guojl/Sample/ZZ_TuneCP5_13TeV-pythia8_RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2.root"
ZZfile = TFile("ZZfilename")
ZZtree = ZZfile.Ana.Get("passedEvents")
