#!/usr/bin/env python
import sys, os, pwd, commands
import argparse
parser = argparse.ArgumentParser(description="A simple ttree plotter")
parser.add_argument("-i", "--inputfiles", dest="inputfiles", default="Sync_1031_2018_ttH_v2.root", help="List of input files")
parser.add_argument("-o", "--outputfile", dest="outputfile", default="plots.root", help="Output file containing plots")
parser.add_argument("-t", "--ttree", dest="ttree", default="Ana/passedEvents", help="TTree Name")
parser.add_argument("-v","--verbosity",dest="verbosity",default=True, help="True is data False is MC")
args = parser.parse_args()

print args.verbosity
isData = args.verbosity
print isData
if(isData==True):
    print "start to deal with DATA"
else:
    print "start to deal with MC"
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

keeplist  = "lep_id lep_pt lep_eta lep_phi lep_mass lepFSR_pt lepFSR_eta lepFSR_phi lepFSR_mass lep_Hindex lep_pterr lep_pterrold lep_ecalEnergy lep_isEB lep_isEE lep_tightId lep_Sip lep_RelIsoNoFSR passedFullSelection passedZ1LSelection passedZXCRSelection nZXCRFailedLeptons eventWeight mass4l k_ggZZ k_qqZZ_qcd_dPhi k_qqZZ_qcd_M k_qqZZ_ewk k_qqZZ_qcd_Pt crossSection EventCat Run Event LumiSect"
filenamesInput = "/cms/user/guojl/Sample/{}".format(args.inputfiles)
filenameOutput = "/cms/user/guojl/Sample/skimed/{}".format(args.outputfile)
tree = "passedEvents"
if(isData!=True):
    directory = "Ana/"
#directory = ""
removelist = "*"
if(isData!=True):
    cmd = "python reduceTree.py"+" "+filenamesInput+" "+filenameOutput+" "+"-t"+" "+"\"%s\""%tree+" "+"-d"+" "+"\"%s\""%directory+" "+"-r"+" "+"\"%s\""%removelist+" "+"-k"+" "+"\"%s\""%keeplist

else:
    cmd = "python reduceTree.py"+" "+filenamesInput+" "+filenameOutput+" "+"-t"+" "+"\"%s\""%tree+" "+"-r"+" "+"\"%s\""%removelist+" "+"-k"+" "+"\"%s\""%keeplist
#cmd = "python reduceTree.py"+" "+filenamesInput+" "+filenameOutput+" "+"-t"+" "+tree+" "+"-d"+directory+" "+"-r"+" "+removelist+" "+"-k"+" "+keeplist
#cmd = "python reduceTree.py"+" "+filenamesInput+" "+filenameOutput+" "+"-t"+" "+"\"%s\""%tree+" "+"-r"+" "+"\"%s\""%removelist+" "+"-k"+" "+"\"%s\""%keeplist
print cmd
output = processCmd(cmd)
print output
