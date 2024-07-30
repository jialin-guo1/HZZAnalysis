# import packages
import uproot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplhep as hep
import awkward as ak
import os
import sys
import hist

import vector
vector.register_awkward()

# set cms plot style
use_helvet = True  ## true: use helvetica for plots, make sure the system have the font installed
if use_helvet:
    CMShelvet = hep.style.CMS
    CMShelvet['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.style.use(CMShelvet)
else:
    plt.style.use(hep.style.CMS)

sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from setting import setting

#config_path = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL_alphavalidate_110to135.yml"
year = '2016preAPV'; process = 'vz'
import yaml
config_path = f"/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/cards/config_UL{year}.yml"
with open( config_path) as f:
    config = yaml.safe_load(f)

#make cut
def make_cut(selection,arr):
    r'''
    input: selection, arr as ak.Aarry()
    output: cuted arr with selection
    '''
    cut  = ak.numexpr.evaluate(selection,arr)
    return arr[cut]

channels = ['isEE','isMuMu']
tags = ['untag','vbftag','btag']
channel_map = {'isMuMu':"mumuqq", 'isEE':'eeqq'}
tag_map = {'untag':'untagged','vbftag':'vbf_tagged','btag':'b_tagged'}
cat_map = {'resolved':'Resolved','merged':'Merged'}
out_dir = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/txtfiles/HM_inputs_{year}UL'


#samples = ['DY_pt50To100','DY_pt100To250','DY_pt250To400','DY_pt400To650','DY_pt650ToInf','TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L','WWTo1L1Nu2Q','tZq','ZZTo2L2Nu','WZTo1L1Nu2Q','ggh1000','ggh500','sig','ggh2000']
#samples = ['DY_pt50To100','DY_pt100To250','DY_pt250To400','DY_pt400To650','DY_pt650ToInf','TTTo2L2Nu','WWTo2L2Nu','WZTo2Q2L','ZZTo2Q2L','tZq','ggh1000','sig']
#samples = ['TTTo2L2Nu','tZq']
#samples = ['ggh125','ggh400','ggh450','ggh500','ggh550','ggh600','ggh700','ggh750','ggh800','ggh900','ggh1000','ggh2000','ggh2500','ggh3000',]
#samples = ['DY_pt50To100','DY_pt100To250','DY_pt250To400','DY_pt400To650','DY_pt650ToInf']
samples = ['WWTo2L2Nu','ZZTo2Q2L','WZTo2Q2L']
#samples = ['qqH']
arr = {}
sumweight = {}
n_events = {}
#for sample in samples:
#    #arr[sample] = uproot.lazy([f"{setting().fileset[year][sample][0]}:passedEvents"],filter_name = ['jet*','found*','KD*','Met','mass*','isMuMu','isEE'])
#    #arr[sample] = uproot.lazy([f"{setting().fileset[year][sample][0]}:passedEvents"])
#    #arr[sample] = uproot.lazy([f"/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/{process}/skimed/ggh.root:passedEvents"])
#    arr[sample] = uproot.lazy([f"/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}/MC/vbf/skimed/vbf.root:passedEvents"])
#    #arr[sample] = uproot.lazy([f"/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggh/skimed/ggh.root:passedEvents"])
#    
#    #f = uproot.open(f"/cms/user/guojl/Sample/2L2Q/UL_Legacy/{year}//MC/{process}/skimed/VBF_HToZZTo2L2Q_M1000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v1_0.root")['sumWeights']
#    #f = uproot.open(f"/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggh/skimed/ggh.root")['sumWeights']
#    #sumweight[sample] = (f.to_boost()).sum()
#
#    #f = uproot.open(setting().fileset[year][sample][0])['sumWeights']
#    #sumweight[sample] = (f.to_boost()).sum()
#
#    #f = uproot.open(setting().fileset[year][sample][0])['nEvents']
#    #n_events[sample] = (f.to_boost()).sum()
#
#    f.close()


filelists = [f"{setting().fileset[year][sample][0]}:passedEvents" for sample in samples]
arr[process] = uproot.lazy(filelists)

masszz = {'resolved':'mass2l2jet','merged':'mass2lj'}
lumi = config['lumi']['2018']
bins = 60; start = 0; stop = 3000

for channel in channels:
    arr_cut = {}
    for tag in tags:
        arr_cut[tag] = {}
        for case in ['resolved','merged']:
            selection = config['cut']['SR'][channel][case][tag]
            arr_cut[tag][case] = make_cut(selection,arr[process])

            #fill hist
            h = {}
            h['mean'] = hist.Hist(hist.axis.Regular(bins, start, stop))
            h['up'] = hist.Hist(hist.axis.Regular(bins, start, stop))
            h['down'] = hist.Hist(hist.axis.Regular(bins, start, stop))

            xsec = config['samples_inf']['ggh'][1]
            h['mean'].fill(
                arr_cut[tag][case][masszz[case]],
                #weight = ak.numexpr.evaluate(f'EventWeight*{lumi}*1000/{sumweight["ggh"]}',arr_cut[case])
                weight = ak.numexpr.evaluate(f'EventWeight',arr_cut[tag][case])
            )
            h['up'].fill(
                arr_cut[tag][case][masszz[case]],
                #weight = ak.numexpr.evaluate(f'EventWeight_up*{lumi}*1000/{sumweight["ggh"]}',arr_cut[case])
                weight = ak.numexpr.evaluate(f'EventWeight_up',arr_cut[tag][case])
            )
            h['down'].fill(
                arr_cut[tag][case][masszz[case]],
                #weight = ak.numexpr.evaluate(f'EventWeight_dn*{lumi}*1000*{xsec}/{sumweight["ggh"]}',arr_cut[case])
                weight = ak.numexpr.evaluate(f'EventWeight_dn',arr_cut[tag][case])
            )

            #plot
            h['mean'].plot1d(density=False,label='mean')
            h['up'].plot1d(density=False,label='up')
            h['down'].plot1d(density=False,label='down')

            plt.xlabel('M(2l2q) [GeV]')
            plt.ylabel('Events')
            plt.legend()

            plt.title(f'Estimate M(2l2q) distribution in SR in {channel_map[channel]} channel with {tag} category in {case}',fontsize=20)

            #add difference of up and down with showing a text in plot
            n_mean = h['mean'].values().sum()
            n_up = h['up'].values().sum()
            n_down = h['down'].values().sum()

            diff_up = abs(n_up-n_mean)/n_mean
            diff_down = abs(n_down-n_mean)/n_mean

            #crab the max value of y-axis
            max_y = max(h['mean'].values())

            plt.text(1500, max_y*0.7, f'uncertainty in two {channel_map[channel]} channel in {case} in {tag}', fontsize=20,color = 'red')
            plt.text(1500, max_y*0.65,f"= +{diff_up:.4f}/-{diff_down:.4f} in {process} process", fontsize=20,color='red')

            #print the text
            print(f'uncertainty in two {channel_map[channel]} channel in {case} in {tag} = +{diff_up:.9f}/-{diff_down:.9f} in {process} process')

            #save plot
            if os.path.exists(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/papercomments/plots/{year}') == False: # check if the directory exists
                os.mkdir(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/papercomments/plots/{year}')
            
            plt.savefig(f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/papercomments/plots/{year}/massZZ_{process}_{case}_{channel_map[channel]}_{tag}.png')
            plt.close()

            r'''
            write uncertainty to the txt file
            if the file name include eeqq then write the uncertainty following "## Electron systematics ##" in the file
            if the file name include mumuqq then write the uncertainty following "## Muon systematics ##" in the file
            the uncertainty line for eeqq should be "systematic elec_full {process} {diff_up:.9f}/{diff_down:.9f}"
            the uncertainty line for mumuqq should be "systematic muon_full {process} {diff_up:.9f}/{diff_down:.9f}"
            if the uncertainty line is already in the file, then replace the line with the new uncertainty, else add the line to the following line of the "## Electron systematics ##" or "## Muon systematics ##"
            the file should be closed after writing the uncertainty
            '''
            filename = f'{out_dir}/{channel_map[channel]}_{cat_map[case]}_{tag_map[tag]}.txt'
            #Determine the type of uncertainty based on the filemane
            if 'eeqq' in filename:
                uncertainty_type = 'elec_full'
                systematics_header = '## Electron systematics ##'
            elif 'mumuqq' in filename:
                uncertainty_type = 'muon_full'
                systematics_header = '## Muon systematics ##'
            else:
                raise ValueError(f'Invalid filename: {filename}')
            
            #Format the new unceratinty line
            new_line = f'systematic {uncertainty_type} {process} {1+diff_up:.9f}/{1-diff_down:.9f}'

            # Read the existing lines in the file
            print(f'Writing uncertainty to file: {filename}')
            with open(filename, 'r') as infile:
                lines = infile.readlines()

            # Try to replace the existing uncertainty line, if it exists
            found_line = False
            for i, line in enumerate(lines):
                if line.startswith(f'systematic {uncertainty_type} {process}'):
                    lines[i] = new_line + '\n'
                    found_line = True
                    #break
                if line.startswith(f'systematic {uncertainty_type}') and line.split(" ")[2].isdigit():
                    # If the uncertainty line is not contained the process name, then delete the line
                    del lines[i]

            if found_line == False:
                # If the uncertainty line is not found, then add it after the header
                for i, line in enumerate(lines):
                    if line.startswith(systematics_header):
                        lines.insert(i+1, new_line + '\n')
                        break

            # Write the new lines to the file
            with open(filename, 'w') as outfile:
                outfile.writelines(lines)

