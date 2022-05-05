#this script will creat a .sh file and submit it
import sys, os, pwd, re
import argparse
from Utils import *


def subIHEPjob(dir,path_subscript,runPath,excute):
    filename_list = os.listdir(dir)
    for i, filename in enumerate(filename_list):
        if(filename.find(".root")==-1): continue

        fulljobname = filename.split('/')
        jobname = fulljobname[len(fulljobname)-1]
        jobname = re.sub('.root','',jobname)
        print "this jobname is "+jobname

        jobfile = path_subscript+jobname+".sh"
        with open(jobfile,"w") as outSH:
            outSH.write("#!/bin/bash\n")
            outSH.write("/bin/hostname\n")
            outSH.write("cd {}\n".format(runPath))
            outSH.write("runMEs -p {} -i {}\n".format(dir,fulljobname[len(fulljobname)-1]))

        cmd = 'chmod 777 {}'.format(jobfile)
        output = processCmd(cmd)

        cmd = 'hep_sub {0:s}  -o /publicfs/cms/user/guojl/SubmitJobOnIHEP/sub_out/{1:s}.out -e /publicfs/cms/user/guojl/SubmitJobOnIHEP/sub_out/{2:s}.err'.format(jobfile,excute+"_"+jobname,excute+"_"+jobname)
        #cmd = 'hep_sub {0:s}  -o /publicfs/cms/user/guojl/sub_out/{1:s}.log -e /publicfs/cms/user/guojl/sub_out/{2:s}.err'.format(jobfile,args.jobname,args.jobname)
        output = processCmd(cmd)
        print output


def main():
    parser = argparse.ArgumentParser(description="A simple ttree plotter")
    parser.add_argument("-d", "--dir", dest="directory", default="MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8", help="directory stroe root input root file")
    parser.add_argument("-p", "--path", dest="path", default="/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis", help="excute run code path")
    parser.add_argument("-e", "--excute", dest="excute", default="runMEs", help="excutable file name")
    parser.add_argument("-v","--verbosity",dest="verbosity",default=True, help="True is data False is MC")
    parser.add_argument("-n","--name",dest="name",default="all", help="sample name that you want to run. only DY_pt50To100,DY_pt100To250,DY_pt400To650,DY_pt650ToInf,TTJets,TTTo2L2Nu,WW_TuneCP5,WZTo2Q2L,ZZTo2Q2L,Signal are available. if you want to run all you can skip this argument")
    args = parser.parse_args()

    ##############################################path for samples#############################################
    samples_dirs = {'DY_pt50To100':'MC/DYJetsToLL_Pt-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt100To250':'MC/DYJetsToLL_Pt-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt250To400':'MC/DYJetsToLL_Pt-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt400To650':'MC/DYJetsToLL_Pt-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt650ToInf':'MC/DYJetsToLL_Pt-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'TTJets':'MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'TTTo2L2Nu':'MC/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                    'WW_TuneCP5':'MC/WW_TuneCP5_13TeV-pythia8',
                    'WWTo2L2Nu':'MC/WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                    'WZTo2Q2L':'MC/WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'ZZTo2Q2L':'MC/ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'Signal':'MC/Signal',
                    'test':'MC/test',
                    'Data':'Data',
                    }

    path_subscript = '/cms/user/guojl/SubmitJobOnIHEP/subfiles/'
    path_subout = '/cms/user/guojl/SubmitJobOnIHEP/sub_out/'
    path_UL2016 = '/cms/user/guojl/Sample/2L2Q/UL_Legacy/2016/'

    if(args.name=='all'):
        for smaple in samples_dirs.keys():
            indir = path_UL2016+samples_dirs[smaple]
            mknewdir(indir+'/skimed')
            subIHEPjob(indir,path_subscript,args.path,args.excute)
    elif(args.name=='MC'):
        for smaple in samples_dirs.keys():
            if(smaple=='Data'): continue
            indir = path_UL2016+samples_dirs[smaple]
            mknewdir(indir+'/skimed')
            subIHEPjob(indir,path_subscript,args.path,args.excute)
    else:
        indir = path_UL2016+samples_dirs[args.name]
        mknewdir(indir+'/skimed')
        subIHEPjob(indir,path_subscript,args.path,args.excute)


if __name__ == '__main__':
    main()
