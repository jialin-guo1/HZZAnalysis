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
    else:
        outpath = "/cms/user/guojl/Sample/2L2Q/UL_Legacy/{}/Data/".format(args.year)
        os.chdir(run_hadd_script_path)
        cmd = 'python haddFile_new.py -y {} -i {} -o {}'.format(args.year,path,outpath)
        print "cmd = " + cmd
        os.system(cmd)

def HaddSkimedFiles(sample,rootstr,samples_path,isData):
    if not isData:
        #cd to root dir
        path = '{}/skimed'.format(samples_path+"MC/"+rootstr)
        os.chdir(path)
        os.system('pwd')

        #hadd all files
        if rootstr == 'ggh':
            cmd = "hadd -f {}/{}.root GluGluHToZZTo2L2Q*.root".format(path,sample)
        elif rootstr == 'vbf':
            cmd = "hadd -f {}/{}.root VBF_HToZZTo2L2Q_M*.root".format(path,sample)
        elif rootstr == 'sig':
            cmd = "hadd -f {}/{}.root *.root".format(path,sample)
        else:
            cmd = "hadd -f {}/{}.root {}*.root".format(path,sample,rootstr)
        os.system(cmd)
        print "cmd = " + cmd

        #rm root files
        if rootstr != 'ggh' and rootstr != 'vbf' and rootstr != 'sig':
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
    parser.add_argument("-s","--step",dest="step",default='step2', help="step1 means hadd files from Raw miniaod files as each 10G. step2 means hadd files. Default: step 2")
    parser.add_argument("-y","--year",dest="year",default='2016', help="year to run or run for all three year. Options: 2016, 2016APV, 2017,2018,all")
    parser.add_argument("-d","--dataset",dest="dataset",default='MC', help="MC or dataset to run step one. Options: data,mc,all ")
    parser.add_argument("-threads","--threads",dest="threads",default="4", help="threads of process. Defalut 4")
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
                'ggh400':'GluGluHToZZTo2L2Q_M400_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh450':'GluGluHToZZTo2L2Q_M450_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'ggh500':'GluGluHToZZTo2L2Q_M500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
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
                'vbf400':'VBF_HToZZTo2L2Q_M400_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf450':'VBF_HToZZTo2L2Q_M450_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf500':'VBF_HToZZTo2L2Q_M500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf550':'VBF_HToZZTo2L2Q_M550_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf600':'VBF_HToZZTo2L2Q_M600_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf700':'VBF_HToZZTo2L2Q_M700_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf750':'VBF_HToZZTo2L2Q_M750_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf800':'VBF_HToZZTo2L2Q_M800_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf900':'VBF_HToZZTo2L2Q_M900_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf1000':'VBF_HToZZTo2L2Q_M1000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf1500':'VBF_HToZZTo2L2Q_M1500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf2000':'VBF_HToZZTo2L2Q_M2000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf2500':'VBF_HToZZTo2L2Q_M2500_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                'vbf3000':'VBF_HToZZTo2L2Q_M3000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8',
                #'ggh':'MC/ggh',
                #'vbf':'MC/vbf',
                #'test':'MC/test',
                'Data':'Data',
                }
    samples_dirs_step2 = {'DY_pt50To100':'DYJetsToLL_LHEFilterPtZ-50To100_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt100To250':'DYJetsToLL_LHEFilterPtZ-100To250_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt250To400':'DYJetsToLL_LHEFilterPtZ-250To400_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt400To650':'DYJetsToLL_LHEFilterPtZ-400To650_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DY_pt650ToInf':'DYJetsToLL_LHEFilterPtZ-650ToInf_MatchEWPDG20_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                ##'TTJets':'MC/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                #'TTTo2L2Nu':'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                ##'WW_TuneCP5':'MC/WW_TuneCP5_13TeV-pythia8',
                #'WWTo2L2Nu':'WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                #'WZTo2Q2L':'WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                #'ZZTo2Q2L':'ZZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                #'ggh':'ggh',
                #'vbf':'vbf',
                #'sig':'sig',
                ##'test':'MC/test',
                #'Data':'Data',
                }
    data_dir = {}
    data_dir['2018'] = ['DoubleMuon','EGamma','MuonEG','SingleMuon']
    data_dir['2016'] = ['DoubleEG','DoubleMuon','MuonEG','SingleElectron','SingleMuon']
    data_dir['2016preAPV'] = ['DoubleEG','DoubleMuon','MuonEG','SingleElectron','SingleMuon']
    data_dir['2017'] = ['DoubleEG','DoubleMuon','MuonEG','SingleElectron','SingleMuon']
    samples_path = '/cms/user/guojl/Sample/2L2Q/UL_Legacy/{}/'.format(args.year)
    #============================================================================================================================================

    import multiprocessing
    if args.step =='step1':
        if args.dataset =='mc':
            for sample in samples_dirs.keys():
                if sample is not 'Data':
                    sub_process = multiprocessing.Process(target=HaddRawMiniaodFiles,args=(samples_dirs[sample], False))
                    sub_process.start() 
        elif args.dataset =='data':
            for sample in data_dir[args.year]:
                sub_process = multiprocessing.Process(target=HaddRawMiniaodFiles,args=(sample, True))
                sub_process.start()
        
        elif args.dataset =='sig':
            for sample in samples_dirs.keys():
                if sample.find('ggh')!=-1 or sample.find('vbf')!=-1:
                    sub_process = multiprocessing.Process(target=HaddRawMiniaodFiles,args=(samples_dirs[sample], False))
                    sub_process.start() 
        elif args.dataset =='all':
            for sample in samples_dirs.keys():
                if sample is not 'Data':
                    sub_process = multiprocessing.Process(target=HaddRawMiniaodFiles,args=(samples_dirs[sample], False))
                    sub_process.start()
            for sample in data_dir[args.year]:
                sub_process = multiprocessing.Process(target=HaddRawMiniaodFiles,args=(sample, True))
                sub_process.start()
        else:
            sample = args.dataset
            sub_process = multiprocessing.Process(target=HaddRawMiniaodFiles,args=(sample, False))
            sub_process.start()

    
    if args.step == 'step2':
        for sample in samples_dirs_step2.keys():
            if sample !='Data':
                #rootstr = (samples_dirs[sample].split('/'))[1]
                rootstr = samples_dirs_step2[sample]
                ## Submit a multiprocess job
                #pool.apply_async(HaddSkimedFiles, args=(sample, rootstr,samples_path,False))
                HaddSkimedFiles(sample, rootstr,samples_path,False)
            else:
                rootstr = 'Data'
                HaddSkimedFiles(sample, rootstr,samples_path,True)
                #pool.apply_async(HaddSkimedFiles, args=(sample, rootstr,samples_path,True))


    
