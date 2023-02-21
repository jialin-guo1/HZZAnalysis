import os,sys
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")



def HaddRawMiniaodFiles(path,isData):
    run_hadd_script_path = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib"
    if not isData:
        outpath = "/cms/user/guojl/Sample/2L2Q/UL_Legacy/{}/MC/".format(args.year)
        os.chdir(run_hadd_script_path)
        cmd = 'python haddFile_new.py -y {} -i {} -o {}'.format(args.year,path,outpath)
        print "cmd = " + cmd
        os.system(cmd)

def HaddSkimedFiles(sample,rootstr,samples_path,isData):
    if not isData:
        #cd to root dir
        #cmd = 'cd {}/skimed'.format(samples_path+"MC/"+rootstr)
        path = '{}/skimed'.format(samples_path+"MC/"+rootstr)
        os.chdir(path)
        #os.system(cmd)
        #print "cmd = " + cmd
        #check pwd
        os.system('pwd')

        #hadd all files
        cmd = "hadd -f {}/{}.root {}*.root".format(path,sample,rootstr)
        os.system(cmd)
        print "cmd = " + cmd

        #rm root files
        cmd = "rm {}*.root".format(rootstr)
        os.system(cmd)
        print "cmd = " + cmd
    else:
        #cmd = 'cd {}/skimed'.format(samples_path+"Data")
        path = '{}/skimed'.format(samples_path+"Data")
        os.chdir(path)
        os.system('pwd')
        #os.system(cmd)
        #print "cmd = " + cmd

        #hadd all files
        cmd = "hadd -f {}/Data{}UL.root *{}*.root".format(path,args.year,'Run')
        os.system(cmd)
        print "cmd = " + cmd

        #rm root files
        cmd = "rm *{}*.root".format('Run')
        os.system(cmd)
        print "cmd = " + cmd

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="A simple ttree plotter")
    parser.add_argument("-s","--step",dest="step",default='step2', help="step1 means hadd files from Raw miniaod files as each 10G. step2 means hadd files")
    parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
    parser.add_argument("-threads","--threads",dest="threads",default="4", help="threads of process")
    args = parser.parse_args()

    #============================================================================================================================================
    #samples_dirs = {'DY_pt50To100':'MC/DYJetsToLL_Pt-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            'DY_pt100To250':'MC/DYJetsToLL_Pt-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            'DY_pt250To400':'MC/DYJetsToLL_Pt-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            'DY_pt400To650':'MC/DYJetsToLL_Pt-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            'DY_pt650ToInf':'MC/DYJetsToLL_Pt-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            'TTJets':'MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            #'TTTo2L2Nu':'MC/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
    #            #'WW_TuneCP5':'MC/WW_TuneCP5_13TeV-pythia8',
    #            'WWTo2L2Nu':'MC/WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
    #            'WZTo2Q2L':'MC/WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            'ZZTo2Q2L':'MC/ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
    #            #'ggh':'MC/ggh',
    #            #'vbf':'MC/vbf',
    #            #'test':'MC/test',
    #            'Data':'Data',
    #            }
    samples_dirs = {'DY_pt50To100':'DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt100To250':'DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt250To400':'DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt400To650':'DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt650ToInf':'DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                #'TTJets':'MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'TTTo2L2Nu':'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                #'WW_TuneCP5':'MC/WW_TuneCP5_13TeV-pythia8',
                'WWTo2L2Nu':'WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                'WZTo2Q2L':'WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'ZZTo2Q2L':'ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'ggh550':'GluGluHToZZTo2L2Q_M550_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh600':'GluGluHToZZTo2L2Q_M600_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh700':'GluGluHToZZTo2L2Q_M700_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh750':'GluGluHToZZTo2L2Q_M750_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh800':'GluGluHToZZTo2L2Q_M800_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh900':'GluGluHToZZTo2L2Q_M900_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh1000':'GluGluHToZZTo2L2Q_M1000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh1500':'GluGluHToZZTo2L2Q_M1500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh2500':'GluGluHToZZTo2L2Q_M2500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh3000':'GluGluHToZZTo2L2Q_M3000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf500':'VBF_HToZZTo2L2Q_M500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf700':'VBF_HToZZTo2L2Q_M700_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf1500':'VBF_HToZZTo2L2Q_M1500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf2000':'VBF_HToZZTo2L2Q_M2000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf2500':'VBF_HToZZTo2L2Q_M2500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                #'ggh':'MC/ggh',
                #'vbf':'MC/vbf',
                #'test':'MC/test',
                'Data':'Data',
                }
    samples_path = '/cms/user/guojl/Sample/2L2Q/UL_Legacy/{}/'.format(args.year)
    #============================================================================================================================================

    import multiprocessing
    if args.step =='step1':
        for sample in samples_dirs.keys():
            if sample is not 'Data':
                sub_process = multiprocessing.Process(target=HaddRawMiniaodFiles,args=(samples_dirs[sample], False))
                sub_process.start()

    
    if args.step == 'step2':
        for sample in samples_dirs.keys():
            if sample !='Data':
                rootstr = (samples_dirs[sample].split('/'))[1]
                ## Submit a multiprocess job
                #pool.apply_async(HaddSkimedFiles, args=(sample, rootstr,samples_path,False))
                HaddSkimedFiles(sample, rootstr,samples_path,False)
            else:
                rootstr = 'Data'
                HaddSkimedFiles(sample, rootstr,samples_path,True)
                #pool.apply_async(HaddSkimedFiles, args=(sample, rootstr,samples_path,True))


    
