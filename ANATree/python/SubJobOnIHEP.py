#this script will creat a .sh file and submit it
import sys, os, pwd, re
import argparse
from Utils import *


def subIHEPjob(dir,path_subscript,runPath,excute,year):
    filename_list = os.listdir(dir)
    for i, filename in enumerate(filename_list):
        if(filename.find(".root")==-1): continue

        fulljobname = filename.split('/') #split the path and get the last element, Note: this line does not work in current situation
        jobname = fulljobname[len(fulljobname)-1] #get the last element of the list
        jobname = re.sub('.root','',jobname+"_"+year)
        print "this jobname is "+jobname

        #if this is GluGluHToZZTo2L2Q or VBFHToZZTo2L2Q sample, we need to crab the mass point and add it to the runMEs command with -m option
        #i.e from GluGluHToZZTo2L2Q_M800_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root get 800
        if 'GluGluHToZZTo2L2Q' in jobname:
            mass = jobname.split('_')[1]
            mass = mass.replace('M','')
        elif 'VBF_HToZZTo2L2Q' in jobname:
            mass = jobname.split('_')[2]
            mass = mass.replace('M','')
        else:
            mass = None
        

        jobfile = path_subscript+jobname+".sh"
        with open(jobfile,"w") as outSH:
            outSH.write("#!/bin/bash\n")
            outSH.write("/bin/hostname\n")
            outSH.write("cd {}\n".format(runPath))
            if mass is not None:
                outSH.write("runMEs -p {} -i {} -y {} -m {}\n".format(dir,fulljobname[len(fulljobname)-1],year,mass))
            else:
                outSH.write("runMEs -p {} -i {} -y {} \n".format(dir,fulljobname[len(fulljobname)-1],year))

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
    parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
    parser.add_argument("-n","--name",dest="name",default="all", help="sample name that you want to run. only DY_pt50To100,DY_pt100To250,DY_pt400To650,DY_pt650ToInf,TTJets,TTTo2L2Nu,WW_TuneCP5,WZTo2Q2L,ZZTo2Q2L,Signal are available. if you want to run all you can skip this argument")
    args = parser.parse_args()

    ##############################################path for samples#############################################
    samples_dirs = {'DY_pt50To100':'MC/DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt100To250':'MC/DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt250To400':'MC/DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt400To650':'MC/DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt650ToInf':'MC/DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    #'TTJets':'MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'TTTo2L2Nu':'MC/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                    #'WW_TuneCP5':'MC/WW_TuneCP5_13TeV-pythia8',
                    'WWTo2L2Nu':'MC/WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                    'WZTo2Q2L':'MC/WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'ZZTo2Q2L':'MC/ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'ZZTo2L2Nu':'MC/ZZTo2L2Nu_TuneCP5_13TeV_powheg_pythia8',
                    'tZq':"MC/tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-amcatnlo-pythia8",
                    'WZTo1L1Nu2Q':'MC/WZTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'WWTo1L1Nu2Q':'MC/WWTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    #'ZH_HToBB':'MC/ZH_HToBB_ZToLL_M-125_TuneCP5_13TeV-powheg-pythia8',
                    #'ZH_HToCC':'MC/ZH_HToCC_ZToLL_M-125_TuneCP5_13TeV-powheg-pythia8',
                    #'ZH_HToGG':'MC/ZH_HToGG_ZToAll_M125_TuneCP5_13TeV-powheg-pythia8',
                    'ggh':'MC/ggh',
                    #'ggh125':'MC/ggh125',
                    #'ggh300':'MC/ggh300',
                    #'ggh350':'MC/ggh350',
                    #'ggh400':'MC/ggh400',
                    #'ggh450':'MC/ggh450',
                    #'ggh500':'MC/ggh500',
                    #'ggh550':'MC/ggh550',
                    #'ggh600':'MC/ggh600',
                    #'ggh700':'MC/ggh700',
                    #'ggh800':'MC/ggh800',
                    #'ggh900':'MC/ggh900',
                    #'ggh1000':'MC/ggh1000',
                    #'ggh1500':'MC/ggh1500',
                    #'ggh3000':'MC/ggh3000',
                    #'ggh2500':'MC/ggh2500',
                    'vbf':'MC/vbf',
                    #'test':'MC/test',
                    'Data':'Data',
                    }
    
    samples_zjet = {'DY_pt50To100':'MC/DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt100To250':'MC/DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt250To400':'MC/DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt400To650':'MC/DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    'DY_pt650ToInf':'MC/DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                    }

    path_subscript = '/cms/user/guojl/SubmitJobOnIHEP/subfiles/'
    path_subout = '/cms/user/guojl/SubmitJobOnIHEP/sub_out/'
    path_UL2016 = '/cms/user/guojl/Sample/2L2Q/UL_Legacy/2016/'

    #read which year to run
    if(args.year=='all'):
        years = ['2016','2016APV','2017','2018']
    else:
        years = [args.year]
    
    #loop year list to submit job
    for year in years:
        path_sample = '/cms/user/guojl/Sample/2L2Q/UL_Legacy/'+year+'/'
        if(args.name=='all'):
            for smaple in samples_dirs.keys():
                indir = path_sample+samples_dirs[smaple]
                if(os.path.exists(indir)):
                    mknewdir(indir+'/skimed')
                    subIHEPjob(indir,path_subscript,args.path,args.excute,year)
                else:
                    continue
        elif(args.name=='MC'):
            for smaple in samples_dirs.keys():
                if(smaple=='Data'): continue
                indir = path_sample+samples_dirs[smaple]
                if(os.path.exists(indir)):
                    mknewdir(indir+'/skimed')
                    subIHEPjob(indir,path_subscript,args.path,args.excute,year)
                else:
                    continue
        elif(args.name=='zjet'):
            for sample in samples_zjet.keys():
                indir = path_sample+samples_zjet[sample]
                if(os.path.exists(indir)):
                    mknewdir(indir+'/skimed')
                    subIHEPjob(indir,path_subscript,args.path,args.excute,year)
                else:
                    continue
        else:
            print "[INFO] this is {}".format(args.name)
            indir = path_sample+samples_dirs[args.name]
            if(os.path.exists(indir)):
                mknewdir(indir+'/skimed')
                subIHEPjob(indir,path_subscript,args.path,args.excute,year)
            else:
                sys.exit()


if __name__ == '__main__':
    main()
