#!/usr/bin/env python
import ROOT
ROOT.gStyle.SetOptStat(False)

import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-i","--inputfiles", dest="inputfiles", default="datasetMC.txt",help="input files")
parser.add_argument("-o","--outputfiles",dest="outputfiles",default="datasetMC_dir.txt",help="output files")
args = parser.parse_args()

t = ROOT.TChain("passedEvents")
#t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/2016_noDuplicates.root")
#t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/2017_noDuplicates.root")
t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/2018_noDuplicates.root")

#if in txt
def checkline(dataline):
    N = 0
    infile = open(args.inputfiles)
    for line in infile:
        line=line.strip('\n')
        if(dataline == line):
            N += 1
    if(N==0):
        return dataline
    else:
        return "Mathed!"
Nmatch = 0
outfile = open(args.outputfiles,"w")
for ievent,event in enumerate(t):
    if(not event.passedFullSelection): continue
    if(105<event.mass4l<140):
        Run = event.Run
        LumiSect = event.LumiSect
        Event = event.Event
        mass4l = event.mass4l
        massZ1 = event.massZ1
        massZ2 = event.massZ2
        if(abs(event.lep_id[event.lep_Hindex[0]])==13 and abs(event.lep_id[event.lep_Hindex[1]])==13 and abs(event.lep_id[event.lep_Hindex[2]])==13 and abs(event.lep_id[event.lep_Hindex[3]])==13):
            cat = "4mu"
        elif(abs(event.lep_id[event.lep_Hindex[0]])==11 and abs(event.lep_id[event.lep_Hindex[1]])==11 and abs(event.lep_id[event.lep_Hindex[2]])==11 and abs(event.lep_id[event.lep_Hindex[3]])==11):
            cat = "4e"
        else:
            cat = "2e2mu"
        dataline = "{0:d}:{1:d}:{2:d}:{3:.2f}:{4:.2f}:{5:.2f}:".format(Run,LumiSect,Event,mass4l,massZ1,massZ2)
        ifmatched = checkline(dataline)
        print ifmatched
        if(ifmatched!="Mathed!"):
            outfile.write(dataline+"\n")
        else:
            Nmatch += 1

print "total number of matching = " + str(Nmatch)


outfile.close()
