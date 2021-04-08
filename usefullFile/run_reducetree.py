#!/usr/bin/env python
import sys, os, pwd, commands

import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-i", "--inputpath", dest="inputpath", default="/cms/user/guojl/Sample/raw/crab_QCD_Pt-150to3000_TuneCP5_FlatPower7_13TeV_pythia8_RunIISummer19UL18MiniAOD-106X/210402_012917/0000/", help="List of input files")
parser.add_argument("-o", "--outpupath", dest="outputfile", default="/cms/user/guojl/Sample/", help="output path for store skimed root file")
parser.add_argument("-n", "--nameOfscript", dest="nameOfscript", default="reduce2l2qTree.py", help="the script that you want to run")
args = parser.parse_args()

# define function for processing the external os commands
def processCmd(cmd, quite = 0):
    #    print cmd
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
        return "ERROR!!! "+output
    else:
        return output

#define function for checking if is a rootfile
def ifROOT(line):
    line=line.strip('\n')
    if line[-4:] != "root":
        return False

#go to store file and get name of root file to generate input and out put file name
#cmd = "cd {}".format(args.inputpath)
#output = processCmd(cmd)
#print output

outputfile = os.popen('ls  '+str(args.inputpath))
print outputfile

for line in outputfile:
    line=line.strip('\n')
    #if(ifROOT(line)==False): continue
    filename = line.split('.root')[0]
    print "[INFO] get root file {}".format(filename)
    cmd = 'python {} -i {} -p {}'.format(args.nameOfscript,filename,args.inputpath)
    output = processCmd(cmd)
    print output
