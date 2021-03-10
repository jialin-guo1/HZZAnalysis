#!/usr/bin/env python
from ROOT import *
gStyle.SetOptStat(False)

import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-i","--inputfiles", dest="inputfiles", default="datasetMC.txt",help="input files")
args = parser.parse_args()

inputfilename = "/cms/user/guojl/Sample/raw/"+args.inputfiles+".root"
inputfile = TFile(inputfilename)
inputTree = inputfile.Ana.Get("passedEvents")
outfile = open(args.inputfiles+".txt","w")

totalEntries = inputTree.GetEntries()
print "[INFO] total entries  = "+str(inputTree.GetEntries())
for ievent,event in enumerate(inputTree):
    if(ievent%100000==0):
        print "[INFO] {0:s}/{1:s}".format(str(ievent),str(totalEntries))
    Run = str(event.Run)
    LumiSect = str(event.LumiSect)
    Event = str(event.Event)
    dataline ="{0:s}:{1:s}:{2:s}".format(Run,LumiSect,Event)
    outfile.write(dataline+"\n")

outfile.close()
