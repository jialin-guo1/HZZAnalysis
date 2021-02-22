#!/usr/bin/env python
from ROOT import *
gStyle.SetOptStat(False)

import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-i","--inputfiles", dest="inputfiles", default="datasetMC.txt",help="input files")
args = parser.parse_args()

infile = TFile(args.inputfiles+".root")
intree = infile.Ana.Get("passedEvents")

outfile = TFile(args.inputfiles+"_noDuplicates.root","recreate")
outtree = intree.CloneTree(0)

runlumieventSet=[]
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
