from ROOT import *
import sys
import commands

#Run a script to stroe Branch name in a .txt
cmd = "python GetBranchName.py >BranchName.txt"
status, output = commands.getstatusoutput(cmd)

var_names = []
with open("BranchName.txt","r") as namefile:
    for line in namefile:
        if (line.startswith('==')): continue
        #split line by '=', to get name
        BranchName = line.split('=')[0]
        #remove space at the end of name
        BranchName = BranchName.rstrip()
        #remove space at the begin
        BranchName = BranchName.lstrip()
        var_names.append(BranchName)
        print "[INFO] Get Branch name: "+str(BranchName)

#call a TCanvas to save plots
c = TCanvas("c","c",600,600)

#open ROOT file and get tree
file = TFile("plots.root")
#check if we get the file
if(file):
    print "[INFO] Get file "
else:
    print "[ERROR] Worng file "
    sys.exit()
tree = file.Get("passedEvents")

#loop Bracnh names to draw each branch
for var_name in var_names:
    tree.Draw(var_name)
    c.SaveAs("%s.png"%var_name)
