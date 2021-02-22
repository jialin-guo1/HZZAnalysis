#!/usr/bin/env python
import os
import argparse
parser = argparse.ArgumentParser(description="reduce files from a list")
parser.add_argument("-i","--inputfiles", dest="inputfiles", default="datasetMC.txt",help="input files")
args = parser.parse_args()

outfile = open(args.inputfiles+"_noDuplicates.txt","w")
nDuplicates=0
lines = []
for line in open(args.inputfiles+".txt"):
    if(line not in lines):
        lines.append(line)
        outfile.write(line)
        print "[INFO] found line: %s"%line.strip('\n')
    else:
        nDuplicates+=1
        print "[INFO] found duplicate: %s"%line.strip('\n')
print "[INFO] number of duplicates  = "+str(nDuplicates)
outfile.close()
