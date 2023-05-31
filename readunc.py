import hist

import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

class ReadUnc():
    def __init__(self,year,cutcat,varb=None) -> None:
        self.year = year
        self.cutcat = cutcat
        self.config = setting().config
        self.cat  = None
        #self.plotdir = 'plotnew'
        self.plotdir = setting().plot_store_dir_name
        self.varb = varb
        self.hits_ggh500 = None
        self.hits_ggh1000 = None
        self.hits_ggh3000 = None
        self.hits_ZH_HToBB = None
        self.plotSig = True
        
        self.catstr = {'resolved':'Resolved','merged_tag':"Merged"}
        self.lepstr = {'isEE':'eeqq','isMuMu':'mumuqq'}
        self.tagstr = {'btag':'b_tagged','untag':'untagged','vbftag':'vbf_tagged'}
        self.samplestr = {'ggh':'ggH','vbf':'qqH','zv':'vz','tt':'ttbar'}
        self.siganlstr = ['ggh1000','vbf1000']
        self.massZZstr = setting().massZZstr

        self.HM_inputs_file_path = f'/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/2l2Q_limitSettingTool/HM_inputs_{self.year}UL'

        print(f'[INFO] start to produce unce with {self.cutcat} in {self.year}')
    
    def UpdateFile(self,file,old_line,new_line):
        '''
        replace old_line by new_line in file
        '''
        file_data = ""
        with open(file,'r') as f:
            #print(f'old = {old_line}')
            for line in f:
                #if old_line == f'{line.split()[0]} {line.split()[1]} {line.split()[2]}':
                if line.find(old_line)!=-1:
                    l = line.split()
                    #print(f'{l[0]} {l[1]} {l[2]} {l[3]}')
                    if old_line == f'{l[0]} {l[1]} {l[2]} {l[3]}':
                        line = new_line+'\n'
                file_data += line
        
        with open(file,"w") as f:
            f.write(file_data)
    
    def GetUncFromUpDn(self,h_mean,h_up,h_dn):
        #print(type(h_mean))
        mean = h_mean.values().sum()

        h_mean_up  = h_mean.values() - h_up.values()
        mean_up = abs(h_mean_up).sum()

        h_mean_dn = h_mean.values() - h_dn.values()
        mean_dn = abs(h_mean_dn).sum()

        uncUp = mean_up/mean
        uncDn = mean_dn/mean

        return uncUp, uncDn

    #Get signal jes uncertainty in each tag(btag,untag,vbftag) from ggh1000 and vbf1000 sample separately
    def GetSigUnc(self,hist):
        reg = 'SR'; cat = '2lep'
        with open(f"./SigUnc_{self.cutcat}_{self.year}.txt",'w') as fout:
            for sig in self.siganlstr:
                for tag in setting().tags:
                    if tag=='all': continue
                    hist_mean = {}; hist_up = {}; hist_dn = {}
                    hist_mean[sig] = hist[self.cutcat][f'{sig}_{reg}_{cat}_{tag}_{self.massZZstr[self.cutcat]}']
                    hist_up[sig] = hist[self.cutcat][f'{sig}_{reg}_{cat}_{tag}_{self.massZZstr[self.cutcat]}_up']
                    hist_dn[sig] = hist[self.cutcat][f'{sig}_{reg}_{cat}_{tag}_{self.massZZstr[self.cutcat]}_dn']
                    uncUp, uncDn = self.GetUncFromUpDn(hist_mean[sig],hist_up[sig],hist_dn[sig])
                    print(f"[INFO] {sig} {self.year} {self.cutcat} {tag} uncUp = {uncUp} uncDn = {uncDn}")
                    fout.write(f'{sig} {self.year} {tag} uncUp = {uncUp} uncDn = {uncDn}\n')


    def PrintSplitUnc(self,hist):
        ####Set which var will be draw
        #if self.varb!= None:
        #    varbs = [self.varb]
        #elif(self.cutcat=='lep'):
        #    varbs = None
        #elif(self.cutcat=='resolved'):
        #    varbs = ['Abs', 'Abs_year', 'BBEC1', 'BBEC1_year', 'EC2', 'EC2_year', 'FlavQCD', 'HF', 'HF_year', 'RelBal', 'RelSample_year']
        #    #varbs = ['Abs']
        #elif(self.cutcat.find('merged') != -1):
        #    varbs = None
        varbs = ['Abs', 'Abs_year', 'BBEC1', 'BBEC1_year', 'EC2', 'EC2_year', 'FlavQCD', 'HF', 'HF_year', 'RelBal', 'RelSample_year']
        with open(f"./SplitJECUnc_{self.cutcat}_{self.year}.txt",'w') as fout:
            for var in varbs:
                print(f"[INFO] it is {var}")
                for reg in ['SR']:
                    for cat in setting().leptonic_cut_cats:
                        if cat=='2lep': continue
                        self.cat = cat
                        for tag in setting().tags:
                            if tag=='all': continue
                            hist_mean = {}; hist_up = {}; hist_dn = {}
                            if self.cutcat =='resolved':
                                hist_mean["DY"] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jet_1_pt'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jet_1_pt'] \
                                        +hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jet_2_pt'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jet_2_pt']
                                hist_up['DY'] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                        +hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']  
                                hist_dn['DY'] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                        +hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']
                                hist_mean['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jet_1_pt'] + hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jet_1_pt'] \
                                               +hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jet_2_pt'] + hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jet_2_pt']
                                hist_up['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                               +hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                                hist_dn['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                               +hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']
                                hist_mean['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jet_1_pt']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jet_1_pt'] \
                                             + hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jet_2_pt']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jet_2_pt']
                                hist_up['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] \
                                             + hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                                hist_dn['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] \
                                             + hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']
                                hist_mean['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jet_1_pt'] + hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jet_2_pt']
                                hist_up['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] + hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                                hist_dn['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] + hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']
                                hist_mean['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jet_1_pt'] + hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jet_2_pt']
                                hist_up['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_1_jesup_split_{var}'] + hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_2_jesup_split_{var}']
                                hist_dn['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_1_jesdn_split_{var}'] + hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_jetpt_2_jesdn_split_{var}']
                            elif self.cutcat =='merged_tag':
                                extrstr_up = 'mergedjetpt_jesup_split'
                                extrstr_dn = 'mergedjetpt_jesdn_split'
                                hist_mean["DY"] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_ptmerged_raw']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_ptmerged_raw'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_ptmerged_raw']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_ptmerged_raw']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_ptmerged_raw']
                                
                                hist_up['DY'] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_{extrstr_up}_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_{extrstr_up}_{var}'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_{extrstr_up}_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_{extrstr_up}_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_{extrstr_up}_{var}']  
                                
                                hist_dn['DY'] = hist[self.cutcat][f'DY_pt50To100_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']+hist[self.cutcat][f'DY_pt100To250_{reg}_{cat}_{tag}_{extrstr_dn}_{var}'] \
                                        +hist[self.cutcat][f'DY_pt250To400_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']+hist[self.cutcat][f'DY_pt400To650_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']+hist[self.cutcat][f'DY_pt650ToInf_{reg}_{cat}_{tag}_{extrstr_dn}_{var}'] 
                                
                                hist_mean['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_ptmerged_raw'] + hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_ptmerged_raw'] 
                                
                                hist_up['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{extrstr_up}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{extrstr_up}_{var}']
                                
                                hist_dn['tt'] = hist[self.cutcat][f'TTTo2L2Nu_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']+hist[self.cutcat][f'WWTo2L2Nu_{reg}_{cat}_{tag}_{extrstr_dn}_{var}'] \
                                
                                hist_mean['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_ptmerged_raw']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_ptmerged_raw'] 
                                            
                                hist_up['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{extrstr_up}_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{extrstr_up}_{var}']

                                hist_dn['zv'] = hist[self.cutcat][f'WZTo2Q2L_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']+hist[self.cutcat][f'ZZTo2Q2L_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']
                                
                                hist_mean['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_ptmerged_raw']
                                hist_up['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_{extrstr_up}_{var}']
                                hist_dn['ggh'] = hist[self.cutcat][f'ggh_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']

                                hist_mean['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_ptmerged_raw']
                                hist_up['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_{extrstr_up}_{var}'] 
                                hist_dn['vbf'] = hist[self.cutcat][f'vbf_{reg}_{cat}_{tag}_{extrstr_dn}_{var}']                     

                            HM_inputs_file = f'{self.HM_inputs_file_path}/{self.lepstr[cat]}_{self.catstr[self.cutcat]}_{self.tagstr[tag]}.txt'
                            for sample in ['DY','zv','tt','ggh','vbf']:
                                #print(type(hist_mean[sample]))
                                uncUp,uncDn = self.GetUncFromUpDn(hist_mean[sample],hist_up[sample],hist_dn[sample])
                                Up = (1+uncUp); Dn = 1-uncDn
                                fout.write(f'Split JEC Unc in {var}_{reg}_{cat}_{tag}_{sample} = {1+uncUp}/{1-uncDn}')
                                fout.write('\n')
                                #print(f'Split JEC Unc in {var}_{reg}_{cat}_{tag}_{sample} = {1+uncUp}/{1-uncDn}')
                                #replace in new file
                                if sample == 'DY': continue
                                new_str = f'systematic splitjec {self.samplestr[sample]} {var} {Up}/{Dn}'
                                old_str = f'systematic splitjec {self.samplestr[sample]} {var}'
                                self.UpdateFile(HM_inputs_file,old_str,new_str)

    
    def run(self,step):
        if step == 'splitjec':
            print(f'[INFO] Running {step} for {self.year} {self.cutcat}')
            bininfo = {'resolved':'bininfo_resolved_split','merged_tag': 'bininfo_merged_split'}
            hist = GetHisto(self.year,self.cutcat,f'{bininfo[self.cutcat]}').hist
            self.PrintSplitUnc(hist)
        elif step == 'sigjec':
            print(f'[INFO] Running {step} for {self.year} {self.cutcat}')
            hist = GetHisto(self.year,self.cutcat).hist
            self.GetSigUnc(hist)
