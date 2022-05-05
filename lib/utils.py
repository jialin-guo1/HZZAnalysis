import numpy as np
import boost_histogram as bh
import matplotlib.pyplot as plt
import mplhep as hep
import awkward as ak
import os

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



        



    

