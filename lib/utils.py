import uproot
import numpy as np
import boost_histogram as bh
import matplotlib.pyplot as plt
import mplhep as hep
import awkward as ak
import os

from setting import setting
##==================================================================================================================
##================================Retrive histos from root file====================================================
##==================================================================================================================
class GetHisto(setting):
    def __init__(self,year: str, cutcat: str) -> None:
        '''input: lep, resolved merged_notag or merged_tag or all'''
        super().__init__() #attribute from setting

        self.year = year
        #self.leptonic_cut_cats=['isEE','isMuMu','2lep']
        #self.regions = ['CR','SR']
        #self.tags = ['btag','untag','vbftag','all']
        self.cutcat = cutcat
        self.hist = {}
        self.inputrootfile = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root'

        if self.cutcat == 'lep':
            self.hist['lep'] = self.getlepthisto()
        elif self.cutcat=='resolved':
            self.hist['resolved'] = self.getresolvedhisto()
        elif self.cutcat=='merged_notag': 
            self.hist['merged_notag'] = self.getmergednotaghisto()
        elif self.cutcat=='merged_tag':
              self.hist['merged_tag'] = self.getmergedtaghisto()
        elif self.cutcat=='all':
            self.hist['lep'] = self.getlepthisto()
            self.hist['resolved'] = self.getresolvedhisto()
            self.hist['merged_notag'] = self.getmergednotaghisto()
            self.hist['merged_tag'] = self.getmergedtaghisto()

    def getlepthisto(self):
        '''
            input: no input
            output: hito
            function: retreive hitograms which is applied leptonic cut from root files.
        '''
        h = {}
        with uproot.open(self.inputrootfile) as f:
            for sample in self.fileset[self.year].keys():
                for cat in self.leptonic_cut_cats:
                    for varb in self.config['bininfo'].keys():
                        h[f'{sample}_{cat}_{varb}'] = f[f'{sample}/lep/{cat}/{varb}'].to_boost()
        return h


    def getresolvedhisto(self):
        '''
            input: no input
            output: hito
            function: retreive hitograms which is applied resolved cut from root files.
        '''
        h = {}
        with uproot.open(self.inputrootfile) as f:
            for sample in self.fileset[self.year].keys():
                for reg in self.regions:
                    for cat in self.leptonic_cut_cats:
                        for tag in self.tags:
                            for varb in self.config['bininfo'].keys():
                                if varb == 'mass2l2jet':
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin'].to_boost()

                                    #if f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'] and reg=='SR':
                                    temphitoname = f'DY/resolved/{reg}/{cat}/{tag}/massZZ'
                                    if reg=='SR' and (temphitoname in f.keys()):
                                        h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'].to_boost()

                                h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_boost()
        return h
    
    def getmergednotaghisto(self):
        '''
            input: no input
            output: hito
            function: retreive hitograms which is applied merged_notag cut from root files.
        '''
        h = {}
        with uproot.open(self.inputrootfile) as f:
            for sample in self.fileset[self.year].keys():
                for cat in self.leptonic_cut_cats:
                    for varb in self.config['bininfo'].keys():
                        h[f'{sample}_{cat}_{varb}'] = f[f'{sample}/merged_notag/{cat}/{varb}'].to_boost()
        return h

    def getmergedtaghisto(self):
        '''
            input: no input
            output: hito
            function: retreive hitograms which is applied merged_tag cut from root files.
        '''
        h = {}
        with uproot.open(self.inputrootfile) as f:
            for sample in self.fileset[self.year].keys():
                for reg in self.regions:
                    for cat in self.leptonic_cut_cats:
                        for tag in self.tags:
                            for varb in self.config['bininfo'].keys():
                                if varb == 'mass2lj':
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin'].to_boost()

                                    #if f[f'DY/merged_tag/{reg}/{cat}/{tag}/massZZ'] and reg=='SR':
                                    temphitoname = f'DY/resolved/{reg}/{cat}/{tag}/massZZ'
                                    if reg=='SR' and (temphitoname in f.keys()):
                                        h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f[f'DY/merged_tag/{reg}/{cat}/{tag}/massZZ'].to_boost()

                                h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'].to_boost()
        return h

#find root files in this dir
def find_this_rootfiles(dir):
    filename_list = os.listdir(dir)
    files = []
    for i, filename in enumerate(filename_list):
        if(filename.find(".root")==-1): continue
        files.append(filename)
    return files

#create histo from ak.Array
def get_hist(array,weights,nbins=50,xmin=None, xmax=None,mergeflowbin=True):
    if xmin is None:
        xmin = ak.min(array)
    if xmax is None:
        xmax = ak.max(array)
    bins  = bh.axis.Regular(nbins, xmin, xmax)
    hist = bh.Histogram(bins,storage=bh.storage.Weight())
    hist.fill(array,weight=weights)
    return hist

#get err from histo
def get_err(hist):
    err =  np.sqrt(hist.view(flow=False).variance)
    #err =  hist.view(flow=False).variance
    return err

#if an array has np.nan meberdata, replace it
def replace_nan(arr,isunc):
    if isunc == False:
        arr[np.isnan(arr)]=-1
    elif isunc == True:
        arr[np.isnan(arr)]=0

    return arr

#plot hist using mplhep
def plot_hist(hists, normed=False, **kwargs):
    r"""Plot the histogram in the type of boost_histogram
    """
    if not isinstance(hists, (list, tuple)):
        hists = [hists]
    content = [h.view(flow=False).value for h in hists]
    bins = hists[0].axes[0].edges
    if 'bins' in kwargs:
        bins = kwargs.pop('bins')
    if 'yerr' in kwargs:
        yerr = kwargs.pop('yerr')
    else:
        yerr = [np.sqrt(h.view(flow=False).variance) for h in hists]
    if normed:
        for i in range(len(content)):
            contsum = sum(content[i])
            content[i] /= contsum
            yerr[i] /= contsum
    if len(hists) == 1:
        content, yerr = content[0], yerr[0]
    hep.histplot(content, bins=bins, yerr=yerr, **kwargs)

#get SF for WZ ZZ and HZZ signal sample
def GetParticleNetSignalSF(array,tagger,sf_particleNet_signal):
    if tagger=='ZvsQCD':
        tag = 'particleNetZvsQCD'
    elif tagger=='btag':
        tag = 'particleNetZbbvslight'
    else:
        print("[ERROR] Please enter correctly tagger(only ZvQCD and btag are available )")
        sys.exit()
        
    sf_arr = ak.zeros_like(array['particleNetZvsQCD'])
    sf_arr = ak.to_numpy(sf_arr)
    
    wsp = {"LP":[0.90,0.94],'MP':[0.94,0.98],'HP':[0.98,1.0]}
    flavors = {'bhadron':'isbjet','chadron':'iscjet','lighthadron':'islightjet'}
    pt_ranges = {'200To400':[200,400],'400To600':[400,600],'600ToInf':[600,9999999]} 
    
    for pur in wsp.keys():
        for flavor in flavors.keys():
            for pt_range in pt_ranges.keys():
                cut = "({}>{}) & ({}<={}) & (ptmerged>={}) & (ptmerged<{}) & ({}==True)".format(tag,wsp[pur][0],tag,wsp[pur][1],pt_ranges[pt_range][0],pt_ranges[pt_range][1],flavors[flavor])
                cut_arr = ak.numexpr.evaluate(cut,array)
                sf_arr[cut_arr] = float(sf_particleNet_signal[tagger][flavor][pur][pt_range])
    sf_arr = ak.from_numpy(sf_arr)
    print("This sf_array = ",sf_arr)
    return sf_arr

def GetParticleNetbkgSF(array,tagger,cat):
    if tagger=='ZvsQCD':
        if cat == 'DY':
            sf_arr = ak.full_like(array['particleNetZvsQCD'],1.36)
        elif cat == 'TT':
            sf_arr = ak.full_like(array['particleNetZvsQCD'],0.83)
        else:
            print("[ERROR] Please enter correctly CR cat (only DY and TT are available )")
            sys.exit()
    elif tagger=='btag':
        print("[ERROR] btag SF will come soon )")
        sys.exit()
        """if cat == 'DY':
            sf_arr = ak.full_like(array['particleNetZvsQCD'],1.36)
        elif cat == 'TT':
            sf_arr = ak.full_like(array['particleNetZvsQCD'],0.83)
        else:
            print("[ERROR] Please enter correctly CR cat (only DY and TT are available )")
            sys.exit()"""
    else:
        print("[ERROR] Please enter correctly tagger(only ZvQCD and btag are available )")
        sys.exit()
        
    return sf_arr

##==================================================================================================================
##================================extractCutedBranch================================================================
##==================================================================================================================
def extractSpecialBranch(config,year,Sample_NameLists,Branch_List):
    arr = {}
    sumWeight = {}
    for sample in Sample_NameLists:
        print(f"This is {sample}")
        indir = config['ori_dir']+f'/{year}/'+config['samples_inf'][sample][0]+'/skimed'
        files = find_this_rootfiles(indir)
        sumWeight[sample] = 0.0

        for file in files:
            with uproot.open(f'{indir}/{file}') as f:
                this_sumWeight_h = f['sumWeights'].to_boost()
                this_sumWeight = this_sumWeight_h.sum()
                #print(f'this sum weight = {this_sumWeight}')
                sumWeight[sample] += this_sumWeight

        arr[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=Branch_List)

    return arr, sumWeight

##==================================================================================================================
##================================CutBranch=========================================================================
##==================================================================================================================
#def cutBranch(array,config,year,car):
#    arr = {}
    

##==================================================================================================================
##================================extractCutedBranch================================================================
##==================================================================================================================
def extractCutedBranch(config,year,cat):
    #load root file and read array
    bkg_array = {}
    data_array = None
    signal_array = {}
    sumWeight = {}
    filepath = config['ori_dir']+f'/{year}/'
    print(f'File path is {filepath}')
    for sample in config['Samples_lists']:
        print(f"This is {sample}")
        if sample!='Data':
            indir = config['ori_dir']+f'/{year}/'+config['samples_inf'][sample][0]+'/skimed'
            files = find_this_rootfiles(indir)
            sumWeight[sample] = 0

            for file in files:
                with uproot.open(f'{indir}/{file}') as f:
                    this_sumWeight_h = f['sumWeights'].to_boost()
                    this_sumWeight = this_sumWeight_h.sum()
                    #print(f'this sum weight = {this_sumWeight}')
                    sumWeight[sample] += this_sumWeight

            bkg_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=config['var_read_lists'])

        else:
            data_path = config['ori_dir']+f'/{year}/'+f'Data/skimed/Data{year}UL_noDuplicates.root'
            data_array = uproot.lazy([f"{data_path}:passedEvents"],filter_name=config['var_read_lists'])

    if(year!='2016APV'):
        for sample in config['signal_lists']:
            indir = config['ori_dir']+f'/{year}/'+config['samples_inf'][sample][0]+'/skimed'
            files = find_this_rootfiles(indir)

            print(f"This is {sample}")
            signal_path = config['ori_dir']+f"/{year}/"+config['samples_inf'][sample][0]+'/skimed'

            sumWeight[sample] = 0
            for file in files:
                with uproot.open(f'{indir}/{file}') as f:
                    this_sumWeight_h = f['sumWeights'].to_boost()
                    this_sumWeight = this_sumWeight_h.sum()
                    #print(f'this sum weight = {this_sumWeight}')
                    sumWeight[sample] += this_sumWeight

            signal_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=config['var_read_lists'])
    
    #=======cut=============
    if cat=='tt':
        regions = ['CR','SR']
        channels = ['ak4','net']
    else:
        channels = config['channel']
        regions = ['CR','SR']
    #regions = ['CR']
    bkg_array_cut = {}; data_array_cut = {}; signal_array_cut = {}
    for reg in regions:
        bkg_array_cut[reg] = {}; data_array_cut[reg] = {}; signal_array_cut[reg] = {}
        for channel in channels:
            bkg_array_cut[reg][channel] = {}; data_array_cut[reg][channel] = None; signal_array_cut[reg][channel] = {}
            for sample in config['Samples_lists']:
                print(f"This is {sample} in {reg} in {channel}")
                #print(f"selection text = {selection}")
                selection = config['cut'][reg][channel][cat]
                print(f"selection text = {selection}")

                if sample!='Data':
                    temp_array = bkg_array[sample]
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    #cut_array = make_cut(temp_array,region = reg, cat = cat)
                    bkg_array_cut[reg][channel][sample] = temp_array[cut_array]
                else:
                    temp_array = data_array
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    #cut_array = make_cut(temp_array,region = reg, cat = cat)
                    data_array_cut[reg][channel] = temp_array[cut_array]
            if(year!='2016APV' ):
                for sample in config['signal_lists']:
                    temp_array = signal_array[sample]
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    #cut_array = make_cut(temp_array,region = reg, cat = cat)
                    signal_array_cut[reg][channel][sample] = temp_array[cut_array]
            
    return bkg_array_cut,signal_array_cut,data_array_cut,sumWeight

##==================================================================================================================
##================================extractCutedBranch for catgory====================================================
##==================================================================================================================
def extractCutedCatBranch(config,year,cat):
    tags = ['btag','untag','vbftag']
    #load root file and read array
    bkg_array = {}
    data_array = None
    signal_array = {}
    sumWeight = {}
    filepath = config['ori_dir']+f'/{year}/'
    print(f'File path is {filepath}')
    for sample in config['Samples_lists']:
        print(f"This is {sample}")
        if sample!='Data':
            indir = config['ori_dir']+f'/{year}/'+config['samples_inf'][sample][0]+'/skimed'
            files = find_this_rootfiles(indir)
            sumWeight[sample] = 0

            for file in files:
                with uproot.open(f'{indir}/{file}') as f:
                    this_sumWeight_h = f['sumWeights'].to_boost()
                    this_sumWeight = this_sumWeight_h.sum()
                    #print(f'this sum weight = {this_sumWeight}')
                    sumWeight[sample] += this_sumWeight

            bkg_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=config['var_read_lists'])

        else:
            data_path = config['ori_dir']+f'/{year}/'+f'Data/skimed/Data{year}UL_noDuplicates.root'
            data_array = uproot.lazy([f"{data_path}:passedEvents"],filter_name=config['var_read_lists'])

    if(year!='2016APV' and year!='2017'):
        for sample in config['signal_lists']:
            indir = config['ori_dir']+f'/{year}/'+config['samples_inf'][sample][0]+'/skimed'
            files = find_this_rootfiles(indir)

            print(f"This is {sample}")
            signal_path = config['ori_dir']+f"/{year}/"+config['samples_inf'][sample][0]+'/skimed'

            sumWeight[sample] = 0
            for file in files:
                with uproot.open(f'{indir}/{file}') as f:
                    this_sumWeight_h = f['sumWeights'].to_boost()
                    this_sumWeight = this_sumWeight_h.sum()
                    #print(f'this sum weight = {this_sumWeight}')
                    sumWeight[sample] += this_sumWeight

            signal_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=config['var_read_lists'])
    
    #=======cut=============
    if cat=='tt':
        regions = ['CR','SR']
        channels = ['ak4','net']
    else:
        channels = config['channel']
        regions = ['CR','SR']
    #regions = ['CR']
    bkg_array_cut = {}; data_array_cut = {}; signal_array_cut = {}
    for reg in regions:
        bkg_array_cut[reg] = {}; data_array_cut[reg] = {}; signal_array_cut[reg] = {}
        for channel in channels:
            bkg_array_cut[reg][channel] = {}; data_array_cut[reg][channel] = {}; signal_array_cut[reg][channel] = {}
            for tag in tags:
                bkg_array_cut[reg][channel][tag] = {}; data_array_cut[reg][channel][tag] = None; signal_array_cut[reg][channel][tag] = {}
                for sample in config['Samples_lists']:
                    print(f"This is {sample} in {reg} in {channel}")
                    #print(f"selection text = {selection}")
                    selection = config['cut'][reg][channel][cat][tag]
                    print(f"selection text = {selection}")

                    if sample!='Data':
                        temp_array = bkg_array[sample]
                        cut_array = ak.numexpr.evaluate(selection,temp_array)
                        #cut_array = make_cut(temp_array,region = reg, cat = cat)
                        bkg_array_cut[reg][channel][tag][sample] = temp_array[cut_array]
                    else:
                        temp_array = data_array
                        cut_array = ak.numexpr.evaluate(selection,temp_array)
                        #cut_array = make_cut(temp_array,region = reg, cat = cat)
                        data_array_cut[reg][channel][tag] = temp_array[cut_array]
                if(year!='2016APV' and year!='2017'):
                    for sample in config['signal_lists']:
                        temp_array = signal_array[sample]
                        cut_array = ak.numexpr.evaluate(selection,temp_array)
                        #cut_array = make_cut(temp_array,region = reg, cat = cat)
                        signal_array_cut[reg][channel][tag][sample] = temp_array[cut_array]
            
    return bkg_array_cut,signal_array_cut,data_array_cut,sumWeight
