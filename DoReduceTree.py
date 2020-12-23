import sys, os, pwd, commands


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
filenamesInput = "/cms/user/guojl/Sample/2016_noDuplicates.root"
filenameOutput = "/cms/user/guojl/Sample/skimed/2016_noDuplicates.root"
tree = "passedEvents"
#directory = ""
removelist = "*"

#cmd = "python reduceTree.py"+" "+filenamesInput+" "+filenameOutput+" "+"-t"+" "+tree+" "+"-d"+directory+" "+"-r"+" "+removelist+" "+"-k"+" "+keeplist
cmd = "python reduceTree.py"+" "+filenamesInput+" "+filenameOutput+" "+"-t"+" "+"\"%s\""%tree+" "+"-r"+" "+"\"%s\""%removelist+" "+"-k"+" "+"\"%s\""%keeplist
print cmd
processCmd(cmd)
