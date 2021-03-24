#!/usr/bin/env python
import sys,os
from ROOT import *
sys.path.append("%s/lib" %os.getcwd())
from deltaR import *
gStyle.SetOptStat(False)

import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-i","--inputfiles", dest="inputfiles", default="datasetMC.txt",help="input files")
args = parser.parse_args()

#input file
infile = TFile("/cms/user/guojl/Sample/raw/"+args.inputfiles+".root")
intree = infile.Ana.Get("passedEvents")
sumWeights = infile.Ana.Get("sumWeights")
nEvents = infile.Ana.Get("nEvents")
sumWeightsPU = infile.Ana.Get("sumWeightsPU")
nVtx = infile.Ana.Get("nVtx")
nVtx_ReWeighted = infile.Ana.Get("nVtx_ReWeighted")
nInteractions = infile.Ana.Get("nInteractions")
nInteraction_ReWeighted = infile.Ana.Get("nInteraction_ReWeighted")


#outfile and sub dir
outfile = TFile("/cms/user/guojl/Sample/raw/"+args.inputfiles+"_skimed.root","recreate")
dirOutput = outfile.mkdir(args.directory)
dirOutput.cd()
sumWeights.Write()
nEvents.Write()
sumWeightsPU.Write()
nVtx.Write()
nVtx_ReWeighted.Write()
nInteractions.Write()
nInteraction_ReWeighted.Write()
outtree = intree.CloneTree(0)

npassed = 0
nentries = intree.GetEntries()
for ievent,event in enumerate(intree):
    if(ievent%100000==0):
        print "[INFO] {0:s}/{1:s}".format(str(ievent),str(nentries))
    if(evnet.mergedjet_pt.size()>=1):
        outtree.Fill()
        npassed +=1
print "[INFO] raw Entries = "+str(nentries)
print "[INFO] passed Entries = "+str(npassed)
outtree.AutoSave()
