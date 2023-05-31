import uproot
import numpy as np
import boost_histogram as bh
import hist
import matplotlib.pyplot as plt
import mplhep as hep
import awkward as ak
import os

from setting import setting
##==================================================================================================================
##================================Retrive histos from root file====================================================
##==================================================================================================================
class GetHisto(setting):
    def __init__(self,year: str, cutcat: str, binlists=None, invarb=None, option = None) -> None:
        '''input: lep, resolved merged_notag or merged_tag or all'''
        super().__init__() #attribute from setting
        self.binlists = binlists
        self.invarb = invarb
        self.year = year
        #self.leptonic_cut_cats=['isEE','isMuMu','2lep']
        #self.regions = ['CR','SR','ALL']
        #self.tags = ['btag','untag','vbftag','all']
        self.cutcat = cutcat
        self.hist = {}
        if option == 'masszz': #read masszz root file
            self.inputrootfile = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}_masszz.root'
        else:
            self.inputrootfile = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/hist_{self.year}.root'
        print(f'[INFO] get histo from {self.inputrootfile}')

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
                    for varb in self.config['bininfo_lep'].keys():
                        #h[f'{sample}_{cat}_{varb}'] = f[f'{sample}/lep/{cat}/{varb}'].to_boost()
                        h[f'{sample}_{cat}_{varb}'] = f[f'{sample}/lep/{cat}/{varb}'].to_hist()
        return h

    def getresolvedhisto(self):
        '''
            input: no input
            output: hito
            function: retreive hitograms which is applied resolved cut from root files.
        '''
        h = {}
        if(self.binlists==None and self.invarb==None):
            print(f'[INFO] get histo from {self.inputrootfile} with all resolved variables')
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                for varb in self.config['bininfo_resolved'].keys():
                                    if varb == 'mass2l2jet':
                                        #h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin'].to_boost()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin'].to_hist()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin_2d'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin_2d'].to_hist()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_up_rebin_2d'] = f[f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}_up_rebin_2d'].to_hist()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_dn_rebin_2d'] = f[f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}_dn_rebin_2d'].to_hist()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_allrange'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_allrange'].to_hist()

                                        #if f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'] and reg=='SR':
                                        temphitoname = f'DY/resolved/{reg}/{cat}/{tag}/massZZ;1'
                                        if reg=='SR' and (temphitoname in f.keys()):
                                            #h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f[f'DY/resolved/{reg}/{cat}/{tag}/massZZ'].to_boost()
                                            h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f[f'DY_resolved_{reg}_{cat}_{tag}_massZZ'].to_hist()

                                    #h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_boost()
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_hist()
                                for varb in self.config['bininfo_resolvedup']:
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}'].to_hist()
                                for varb in self.config['bininfo_resolveddn']:
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}'].to_hist()
                                for varb in self.config['bininfo_resolved_split'].keys():
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_hist()
        elif(self.binlists==None and self.invarb!=None):
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                varb = self.invarb
                                h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_hist()
        elif(self.binlists!=None and self.invarb==None):
            print(f'[INFO] get histo from {self.inputrootfile} with {self.binlists} variables in resolved')
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                for varb in self.config[self.binlists].keys():
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'].to_hist()
        return h
    
    def getmergednotaghisto(self):
        '''
            input: no input
            output: hito
            function: retreive hitograms which is applied merged_notag cut from root files.
        '''
        h = {}
        if(self.binlists==None and self.invarb==None):
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for cat in self.leptonic_cut_cats:
                        for varb in self.config['bininfo'].keys():
                            if varb.find('mass2l2jet')!=-1 or varb=='mass2lj_allrange': continue
                            h[f'{sample}_{cat}_{varb}'] = f[f'{sample}/merged_notag/{cat}/{varb}'].to_hist()
        elif(self.binlists==None and self.invarb!=None):
            print(f'[INFO] only get {self.invarb} in merged no tag ')
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for cat in self.leptonic_cut_cats:
                        varb = self.invarb
                        h[f'{sample}_{cat}_{varb}'] = f[f'{sample}/merged_notag/{cat}/{varb}'].to_hist()

        return h

    def getmergedtaghisto(self):
        '''
            input: no input
            output: hito
            function: retreive hitograms which is applied merged_tag cut from root files.
        '''
        h = {}
        if(self.binlists==None and self.invarb==None):
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                for varb in self.config['bininfo'].keys():
                                    if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange': continue
                                    if varb == 'mass2lj':
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin'].to_boost()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_allrange'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_allrange'].to_boost()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_rebin_2d'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin_2d'].to_boost()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_up_rebin_2d'] = f[f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}_up_rebin_2d'].to_boost()
                                        h[f'{sample}_{reg}_{cat}_{tag}_{varb}_dn_rebin_2d'] = f[f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}_dn_rebin_2d'].to_boost()

                                        #if f[f'DY/merged_tag/{reg}/{cat}/{tag}/massZZ'] and reg=='SR':
                                        temphitoname = f'DY/merged_tag/{reg}/{cat}/{tag}/massZZ;1'
                                        if reg=='SR' and (temphitoname in f.keys()):
                                            h[f'DY_{reg}_{cat}_{tag}_massZZ'] = f[f'DY/merged_tag/{reg}/{cat}/{tag}/massZZ'].to_boost()

                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'].to_boost()
                                for varb in self.config['bininfo_mergedup'].keys():
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}'].to_hist()
                                for varb in self.config['bininfo_mergeddn'].keys():
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}'].to_hist()
        elif(self.binlists!=None and self.invarb==None):
            print(f'[INFO] get histo from {self.inputrootfile} with {self.binlists} variables in merged_tag')
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                for varb in self.config[self.binlists].keys():
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'].to_hist()
        elif(self.binlists!=None and self.invarb!=None):
            print(f'[INFO] only get {self.invarb} in merged tag ')
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                varb = self.invarb
                                h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'].to_hist()
        elif(self.binlists==None and self.invarb!=None):
            print(f'[INFO] only get {self.invarb} in merged tag ')
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                varb = self.invarb
                                h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'].to_hist()

        else:
            with uproot.open(self.inputrootfile) as f:
                for sample in self.fileset[self.year].keys():
                    for reg in self.regions:
                        for cat in self.leptonic_cut_cats:
                            for tag in self.tags:
                                for varb in self.config[self.binlists].keys():
                                    h[f'{sample}_{reg}_{cat}_{tag}_{varb}'] = f[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'].to_hist()
        return h



##==================================================================================================================
##================================Make cut and return array====================================================
##==================================================================================================================
def MakeCut(events,selection)-> ak.Array:
    cut = ak.numexpr.evaluate(selection,events)
    cut_event = events[cut]
    return cut_event

def get_bh(array, bins=10, xmin=None, xmax=None, underflow=False, overflow=False, mergeflowbin=True, normed=False,
            weights=None, **kwargs):
    r"""Plot histogram from input array.

    Arguments:
        array (np.ndarray, ak.Aarray): input array.
        bins (int, list or tuple of numbers, np.ndarray, bh.axis): bins
        weights (None, or np.ndarray): weights
        # normed (bool): deprecated.

    Returns:
        hist (boost_histogram.Histogram)
    """
    if isinstance(bins, int):
        if xmin is None:
            xmin = array.min()
        if xmax is None:
            xmax = array.max()
        width = 1.*(xmax-xmin)/bins
        if mergeflowbin and underflow:
            xmin += width
            bins -= 1
        if mergeflowbin and underflow:
            xmax -= width
            bins -= 1
        bins = bh.axis.Regular(bins, xmin, xmax, underflow=underflow, overflow=overflow)
    elif isinstance(bins, (list, tuple, np.ndarray)):
        if mergeflowbin and underflow:
            bins = bins[1:]
        if mergeflowbin and overflow:
            bins = bins[:-1]
        bins = bh.axis.Variable(bins, underflow=underflow, overflow=overflow)

    hist = bh.Histogram(bins, storage=bh.storage.Weight())
    if weights is None:
        #weights = np.ones_like(array)
        weights = ak.ones_like(array)
    hist.fill(array, weight=weights)
    return hist

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

#get bin info from boot_histogram object, edge, xmin , xmax, nbins sperately
def GetBinInfoFromBH(hist):
    r'''
        Get bin info from boot_histogram object, return a dict with keys: edge, xmin , xmax, nbins
        intput: hist (boost_histogram.Histogram) or hist.Histogram
        output: bininfo : edge, nbins, xmin , xmax, nbins sperately
    '''
    edge = hist.axes[0].edges
    xmin = hist.axes[0].edges[0]
    xmax= hist.axes[0].edges[-1]
    nbins= hist.axes[0].size
    return edge, nbins ,xmin ,xmax


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


#crate boost_histogram object from ROOT histogram
def CreateBoostHistoFromROOT(hist):
    r'''
       input: ROOT histogram
       output: boost_histogram object
    '''
    # Extract the number of bins, minimum value, and maximum value from the ROOT histogram
    n_bins = hist.GetNbinsX()
    x_min = hist.GetXaxis().GetXmin()
    x_max = hist.GetXaxis().GetXmax()
    # Create bin edges array
    bin_edges = [hist.GetBinLowEdge(i) for i in range(1, n_bins + 2)]
    # Create an empty boost_histogram object
    boost_hist = bh.Histogram(bh.axis.Variable(bin_edges))
    # Fill the boost_histogram object with bin contents
    for i in range(1, n_bins + 1):
        bin_content = hist.GetBinContent(i)
        boost_hist[hist.GetBinLowEdge(i)] = bin_content
    return boost_hist

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

def getbininfo(varb):
    '''
        input: any varb exsited in config
        output: bins informations associated with bins start stop name
    '''
    bins = setting().config['bininfo'][varb][0]
    start = setting().config['bininfo'][varb][1]
    stop = setting().config['bininfo'][varb][2]
    name = setting().config['bininfo'][varb][3]
    return bins, start, stop, name
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

            #bkg_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=config['var_read_lists'])
            bkg_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"])

        else:
            data_path = config['ori_dir']+f'/{year}/'+f'Data/skimed/Data{year}UL_noDuplicates.root'
            #data_array = uproot.lazy([f"{data_path}:passedEvents"],filter_name=config['var_read_lists'])
            data_array = uproot.lazy([f"{data_path}:passedEvents"])

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

            #signal_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"],filter_name=config['var_read_lists'])
            signal_array[sample] = uproot.lazy([f"{indir}/*.root:passedEvents"])
    
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


##==================================================================================================================
##================================extractCutedBranch for region====================================================
##==================================================================================================================
def extractCutedRegionBranch(conig,year,reg,case,samplelist = setting().sample_list,cats = setting().leptonic_cut_cats,tags = setting().tags):
    tags = ['btag','untag','vbftag']
    #load root file and read array
    bkg_array = {}
    data_array = None
    signal_array = {}
    sumWeight = {}
    #loop sample list to read array
    for sample in samplelist:
        print(f"[INFO] This is {sample}")
        if sample!='Data':
            #get sumWeight
            f = uproot.open(setting().fileset[sample][0])['sumWeights']
            sumWeight[sample] = (f.to_boost()).sum()
            f.close()

            #get array
            bkg_array[sample] = uproot.lazy([f"{setting().fileset[sample][0]}:passedEvents"])
        else:
            data_array = uproot.lazy([f"{setting().fileset[sample][0]}:passedEvents"])
    
    #=======cut=============
    #define out put array
    bkg_array_cut = {}; data_array_cut = {}
    for cat in cats:
        bkg_array_cut[cat] = {}; data_array_cut[cat] = {}
        for tag in tags:

            print(f"[INFO] This is {cat} in {tag}")
            #selection = setting().cut[reg][cat][tag]
            selection = config['cut'][reg][cat][tag]
            print(f"[INFO] selection text = {selection}")

            for sample in samplelist:
                if sample!='Data':
                    temp_array = bkg_array[sample]
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    bkg_array_cut[reg][cat][tag][sample] = temp_array[cut_array]
                else:
                    temp_array = data_array
                    cut_array = ak.numexpr.evaluate(selection,temp_array)
                    data_array_cut[reg][cat][tag] = temp_array[cut_array]

