#!/usr/bin/env python
from ROOT import *
gStyle.SetOptStat(False)

import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-i","--inputfiles", dest="inputfiles", default="datasetMC.txt",help="input files")
args = parser.parse_args()

def checkline(line):
    N = 0
    infile = open(args.inputfiles+"_noDuplicates.txt")
    for line in infile:
        line=line.strip('\n')
        if(dataline == line):
                line.replace(line,'\n')
                return True
            else:
                return False

inputfilename  = args.inputfiles+".root"
inputfile = TFile(inputfilename)
inputTree = inputfile.Ana.Get("passedEvents")

outfile = TFile(args.inputfiles+"_noDuplicates.root","recreate")
outTree = inputTree.CloneTree(0)

nremoved = 0
nentries = inputTree.GetEntries()
for ievt in range(nentries):
    inputTree.GetEntry(ievt)
    if(ievent%100000==0):
        print "[INFO] {0:s}/{1:s}".format(str(ievt),str(nentries))
    Run = str(inputTree.Run)
    LumiSect = str(inputTree.LumiSect)
    Event = str(inputTree.Event)
    dataline ="{0:s}:{1:s}:{2:s}".format(Run,LumiSect,Event)
    ifmatched = checkline(dataline)
    if(ifmatched):
        outTree.Fill()
    else:
        nremoved+=1
        print "[INFO] Found duplicate event: %s"%dataline
