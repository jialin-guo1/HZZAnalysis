import sys
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
import os

if __name__ == '__main__':
    print('\033[1;34mWelcome to HZZ2l2q Analysis\033[0m')
    print('\033[1;34mPlease tell me which analyis step you want to run. Here we have some options for you\033[0m')
    print('\033[4;35m1.makecut 2.plotMcData 3.plotsplitunce 4.alpha 5.make2dtemplate 6.readunc 7.significant 8.makereso 9.btageff\033[0m')
    option = input()
    #ask to type option again if the input is not in the list
    while option not in ['makecut','plotMcData','plotsplitunce','alpha','make2dtemplate','readunc','significant','makereso']:
        print('\033[1;34mPlease type the option again\033[0m')
        print('\033[4;35m1.makecut 2.plotMcData 3.plotsplitunce 4.alpha 5.make2dtemplate 6.readunc 7.significant 8.makereso\033[0m')
        option = input()
    
    print('\033[1;34mThanks for you infomation, and we want to know which year you would like to do analysis\033[0m')
    print('\033[4;35m1.2016 2.2016preAPV 3.2016postAPV 4.2017 5.2018 6.all\033[0m')
    year = input()
    #ask to type year again if the input is not in the list
    while year not in ['2016','2016preAPV','2016postAPV','2017','2018','all']:
        print('\033[1;34mPlease type the year again\033[0m')
        print('\033[4;35m1.2016 2.2016preAPV 3.2016postAPV 4.2017 5.2018 6.all\033[0m')
        year = input()

    #years = ['2016','2016preAPV','2016postAPV','2017','2018']
    years = ['2016','2017','2018']

    #================================================
    #makecut process
    if option == 'makecut':
        print('\033[1;34mstart to makecut process\033[0m')
    
        from makecut import CutUnit
        if year == 'all':
            for year in years:
                CutUnit(year).run()
        else:
            CutUnit(year).run()
        #runProcess = CutUnit(year)
        #runProcess.run()
    
    #================================================
    #plotMcData process
    if option == '2' or option == 'plotMcData':
        print('\033[1;34mstart to makecut process\033[0m')
        print('\033[1;34Please kindly let me know which selection case you want to study. And only following options are avaiable:\033[0m')
        print('\033[4;35m1.lep, 2.resolved, 3.merged_notag, 4.merged_tag, 5.all\033[0m')
        cutcat = input()
        #ask to type cutcat again if the input is not in the list
        while cutcat not in ['lep','resolved','merged_notag','merged_tag','all']:
            print('\033[1;34mPlease type the cutcat again\033[0m')
            print('\033[4;35m1.lep, 2.resolved, 3.merged_notag, 4.merged_tag, 5.all\033[0m')
            cutcat = input()
        
        years = ['2016preAPV','2016postAPV','2017','2018']

        print('\033[4;35mDO you have specific variable to draw? if YES, please type the name of variable, if NO, please tpye no\033[0m')
        varb = input()

        cutcats = ['lep','resolved','merged_notag','merged_tag']

        sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot")
        from plotMcData import PlotUnit
        if varb == 'no':
            
            if cutcat == 'all':
                for cutcat in cutcats:
                    PlotUnit(year,cutcat).run()

            if year=='all':
                for year in years:
                    PlotUnit(year,cutcat).run()
            else:
                PlotUnit(year,cutcat).run()
        else:
            print(f'start to draw {varb} only')
            if cutcat == 'all':
                for cutcat in cutcats:
                    PlotUnit(year,cutcat,varb).run()

            if year=='all':
                for year in years:
                    PlotUnit(year,cutcat,varb).run()
            else:
                PlotUnit(year,cutcat,varb).run()
    
    #================================================
    #plotsplitunce process
    if option == 'plotsplitunce' or option == '3':
        print('\033[1;34mstart to makecut process\033[0m')
        print('\033[1;34mPlease kindly let me know which selection case you want to study. And only following options are avaiable:\033[0m')
        print('\033[4;35m1.resolved, 2.merged_tag, 5.all\033[0m')
        cutcat = input()
        sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot")
        from plotMcData import PlotUpDn
        if year=='all':
            for year in years:
                PlotUpDn(year,cutcat).run()
        else:
            PlotUpDn(year,cutcat).run()

    #================================================
    #alpha process
    if option == 'alpha':
        print('\033[1;34mstart to Alpha Method for Z+jets background estimation process\033[0m')

        sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation")
        from AlphaMethod import AlphaMethodUnit

        if year=='all':
            for year in years:
                AlphaMethodUnit(year).run()
        else:
            AlphaMethodUnit(year).run()

    #================================================
    #make2dtemplate process
    if option == 'make2dtemplate':
        print('\033[1;34mstart to make 2D template process\033[0m')
        print('\033[1;34Please kindly let me know which selection case you want to study. And only following options are avaiable:\033[0m')
        print('\033[4;35m1.resolved 2.merged_tag, 3.all\033[0m')
        cutcat = input()

        cutcats = ['resolved','merged_tag']
        if cutcat == 'all':
            for cutcat in cutcats:
                print('\033[1;34mThis is {} process\033[0m'.format(cutcat))
                os.chdir("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/FitTemplate")
                cmd = f'python make_2DtemplateNew.py -y {year} -c {cutcat}'
                os.system(cmd)
        else:
            print('\033[1;34mThis is {} process\033[0m'.format(cutcat))
            os.chdir("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/FitTemplate")
            cmd = f'python make_2DtemplateNew.py -y {year} -c {cutcat}'
            os.system(cmd)
    
    #================================================
    #readunc process
    if option== 'readunc':
        print('\033[1;34mFor now, there is only Split JEC Uncertainty in resolved case can be read\033[0m')
        print('\033[1;34mPlease kindly let me know which selection case you want to study. And only following options are avaiable:\033[0m')
        print('\033[4;35m1.resolved 2.merged_tag, 3.all\033[0m')
        cutcat = input()
        print('\033[1;34mPlease kindly let me know which step you want to run. And only following options are avaiable:\033[0m')
        print('\033[4;35m1.splitjec 2.sigjec, 3.all\033[0m')
        step = input()
        from readunc import ReadUnc
        if year == 'all' and cutcat == 'all':
            for year in years:
                for cutcat in ['resolved','merged_tag']:
                    ReadUnc(year,cutcat).run(step)
        elif year != 'all' and cutcat == 'all':
            for cutcat in ['resolved','merged_tag']:
                ReadUnc(year,cutcat).run(step)
        elif year == 'all' and cutcat != 'all':
            for year in years:
                ReadUnc(year,cutcat).run(step)
        elif year != 'all' and cutcat != 'all':
            ReadUnc(year,cutcat).run(step)
    
    #================================================
    #significant scan process
    if option == 'significant':
        from significant import FinalSigScan
        FinalSigScan('2018','resolved').run()
    
    
    #================================================
    #make resolution process
    if option == 'makereso':
        print('\033[1;34mstart to MakeResolution process\033[0m')

        sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel")
        from MakeResolution import MakeResolutionUnit, MakeResolution
        if year == 'all':
            for year in years:
                #MakeResolutionUnit(year).run()
                MakeResolution(year=year).run()
        else:
            #MakeResolutionUnit(year).run()
            MakeResolution(year=year).run()

    
    #================================================
    if option == 'btageff':
        print('\033[1;34mstart to BtagEff process\033[0m')
        sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BtagEff")
        from BtagEff import BtagEffUnit
        BtagEffUnit(year).run()    
        


