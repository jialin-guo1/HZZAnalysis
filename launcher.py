import sys
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")

if __name__ == '__main__':
    print('\033[1;34mWelcome to HZZ2l2q Analysis\033[0m')
    print('\033[1;34mPlease tell me which analyis step you want to run. Here we have some options for you\033[0m')
    print('\033[4;35m1.makecut 2.plotMcData 3.alpha\033[0m')
    option = input()
    print('\033[1;34mThanks for you infomation, and we want to know which year you would like to do analysis\033[0m')
    print('\033[4;35m1.2016 2.2017 3.2018 4.all\033[0m')
    year = input()

    years = ['2016','2017','2018']

    #while option != 'exit':
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

    if option == 'plotMcData':
        print('\033[1;34mstart to makecut process\033[0m')
        print('\033[1;34Please kindly let me know which selection case you want to study. And only following options are avaiable:\033[0m')
        print('\033[4;35m1.lep, 2.resolved, 3.merged_notag, 4.merged_tag, 5.all\033[0m')
        cutcat = input()

        cutcats = ['lep','resolved','merged_notag','merged_tag']

        sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/Plot")
        from plotMcData import PlotUnit
        if cutcat == 'all':
            for cutcat in cutcats:
                PlotUnit(year,cutcat).run()
                
        if year=='all':
            for year in years:
                PlotUnit(year,cutcat).run()
        else:
            PlotUnit(year,cutcat).run()

    if option == 'alpha':
        print('\033[1;34mstart to Alpha Method for Z+jets background estimation process\033[0m')

        sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/BackgroundEstimation")
        from AlphaMethod import AlphaMethodUnit

        if year=='all':
            for year in years:
                AlphaMethodUnit(year).run()
        else:
            AlphaMethodUnit(year).run()



