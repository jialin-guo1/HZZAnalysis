import awkward as ak
from coffea import processor
#from coffea.nanoevents.methods import candidate
import hist
import uproot
#from coffea.nanoevents import NanoEventsFactory, BaseSchema
from coffea.nanoevents import BaseSchema
import boost_histogram as bh

import sys
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from setting import setting

##
class CutCoffeaProcessor(processor.ProcessorABC):
    def __init__(self,):
        pass
##

class CutAllCatCoffeaProcessor(processor.ProcessorABC):
    r"""the coffea processor for make cut step"""
    def __init__(self,config = None,year = None,fileset = None, option = None):
        self.config = config
        self.year = year
        self.fileset = fileset
        self.sumWeight = 0.0
        self.leptonic_cut_cats=['isEE','isMuMu','2lep']
        self.regions = ['CR','SR','ALL','VR','SB','LSB','HSB']
        self.AlphaRegion = ['VR','SB']
        self.tags = ['btag','untag','vbftag','all']
        self.massZZ_bins = setting().massZZ_bins

        self.option = option # if option.lower() == 'masszz' then only cut on massZZ
        #self.isData = isData

    def getbininfo(self,varb):
        '''
            input: any varb exsited in config
            output: bins informations associated with bins start stop name
        '''
        bins = self.config['bininfo'][varb][0]
        start = self.config['bininfo'][varb][1]
        stop = self.config['bininfo'][varb][2]
        name = self.config['bininfo'][varb][3]

        return bins, start, stop, name

    def process(self, events):
        ####define paramters
        dataset = events.metadata['dataset']

        is_data =( dataset == 'Data')
        if(not is_data):
            #get sumWeight from rootfile
            f = uproot.open(self.fileset[dataset][0])['sumWeights']
            self.sumWeight = (f.to_boost()).sum()
            f.close()

        lumi = self.config['lumi'][self.year]
        xsec = self.config['samples_inf'][dataset][1]

        h_out = {}

        ####Gen variable setup
        varb = 'GEN_H1_mass'
        bins, start, stop, name = self.getbininfo(varb)
        h_out[varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
        h_out[varb].fill(events[varb])
        ####Leptonic cut apply and fill histo for each variable
        if self.option == None: #if option is None, then apply all cuts for leptonic
            h_out['lep'] = {}
            for cat in self.leptonic_cut_cats:
                selection = self.config['cut']['lep'][cat]
                cut = ak.numexpr.evaluate(selection,events)
                cut_event = events[cut]

                h_out['lep'][cat] = {}
                for varb in self.config['bininfo_lep'].keys():
                    if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange': continue
                    bins, start, stop, name = self.getbininfo(varb)
                    h_out['lep'][cat][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))

                    h_out['lep'][cat][varb].fill(
                        cut_event[varb],
                        weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                            ak.ones_like(cut_event.EventWeight),
                    )

        ####Resolved cut apply and fill histo for each variable
        h_out['resolved']={}
        for reg in self.regions:
            h_out['resolved'][reg] = {}
            for cat in self.leptonic_cut_cats:
                h_out['resolved'][reg][cat] = {}
                for tag in self.tags:
                    selection = self.config['cut']['resolved'][reg][cat][tag]
                    #print(selection)
                    cut = ak.numexpr.evaluate(selection,events)
                    cut_event = events[cut]
                    
                    h_out['resolved'][reg][cat][tag] = {}


                    for varb in self.config['bininfo_resolved'].keys():
                        bins = self.config['bininfo_resolved'][varb][0]
                        start = self.config['bininfo_resolved'][varb][1]
                        stop = self.config['bininfo_resolved'][varb][2]
                        name = self.config['bininfo_resolved'][varb][3]
                        #if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange': continue
                        
                        if varb=='mass2l2jet': #store massZZ related variables
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins['resolved'])
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )
                            #bin for signal fit template
                            h_out['resolved'][reg][cat][tag][f'{varb}_fit'] = hist.Hist(hist.axis.Regular(4000, 0, 4000, name = f'{varb}_fit'))
                            h_out['resolved'][reg][cat][tag][f'{varb}_fit'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight)
                            )
                            #bin for all mass range template
                            h_out['resolved'][reg][cat][tag][f'{varb}_allrange'] = hist.Hist(hist.axis.Regular(80, 0, 4000, name = f'{varb}_allrange'))
                            h_out['resolved'][reg][cat][tag][f'{varb}_allrange'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )
                            #eventweight set to one for alpha ratio process
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin_raw'] = hist.Hist(self.massZZ_bins['resolved'])
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin_raw'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )
                            #2D template
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin_2d'] = hist.Hist(self.massZZ_bins['resolved'],hist.axis.Regular(50, 0, 1))
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin_2d'].fill(
                                cut_event[varb],
                                cut_event['KD_Zjj'],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),                                
                            )
                        elif self.option == None: #store all variables only if option is None
                            h_out['resolved'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['resolved'][reg][cat][tag][varb].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )

                    if self.option == None: #store split variables only if option is None
                        for varb in self.config['bininfo_resolved_split'].keys():
                            bins = self.config['bininfo_resolved_split'][varb][0]
                            start = self.config['bininfo_resolved_split'][varb][1]
                            stop = self.config['bininfo_resolved_split'][varb][2]
                            name = self.config['bininfo_resolved_split'][varb][3]
                            h_out['resolved'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['resolved'][reg][cat][tag][varb].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )
        ####Resolved up cut apply and fill histo for each variable 
        h_out['resolved_up']={}
        for reg in self.regions:
            h_out['resolved_up'][reg] = {}
            for cat in self.leptonic_cut_cats:
                h_out['resolved_up'][reg][cat] = {}
                for tag in self.tags:
                    selection = self.config['cut']['resolved_up'][reg][cat][tag]
                    cut = ak.numexpr.evaluate(selection,events)
                    cut_event = events[cut]
                    
                    h_out['resolved_up'][reg][cat][tag] = {}
                    for varb in self.config['bininfo_resolvedup'].keys():
                        bins = self.config['bininfo_resolvedup'][varb][0]
                        start = self.config['bininfo_resolvedup'][varb][1]
                        stop = self.config['bininfo_resolvedup'][varb][2]
                        name = self.config['bininfo_resolvedup'][varb][3]
                        if varb=='mass2l2jet_up':
                            h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins['resolved'])
                            h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )

                            #eventweight set to one for alpha ratio process
                            h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin_raw'] = hist.Hist(self.massZZ_bins['resolved'])
                            h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin_raw'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )
                            #2D template
                            h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin_2d'] = hist.Hist(self.massZZ_bins['resolved'],hist.axis.Regular(50, 0, 1))
                            h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin_2d'].fill(
                                cut_event[varb],
                                cut_event['KD_Zjj_up'],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),                                
                            )
                        elif self.option == None: #store all variables only if option is None
                            h_out['resolved_up'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['resolved_up'][reg][cat][tag][varb].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )
        ####Resolved donw cut apply and fill histo for each variable 
        h_out['resolved_dn']={}
        for reg in self.regions:
            h_out['resolved_dn'][reg] = {}
            for cat in self.leptonic_cut_cats:
                h_out['resolved_dn'][reg][cat] = {}
                for tag in self.tags:
                    selection = self.config['cut']['resolved_dn'][reg][cat][tag]
                    cut = ak.numexpr.evaluate(selection,events)
                    cut_event = events[cut]
                    
                    h_out['resolved_dn'][reg][cat][tag] = {}
                    for varb in self.config['bininfo_resolveddn'].keys():
                        bins = self.config['bininfo_resolveddn'][varb][0]
                        start = self.config['bininfo_resolveddn'][varb][1]
                        stop = self.config['bininfo_resolveddn'][varb][2]
                        name = self.config['bininfo_resolveddn'][varb][3]
                        if varb=='mass2l2jet_dn':
                            h_out['resolved_dn'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins['resolved'])
                            h_out['resolved_dn'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )
                            #eventweight set to one for alpha ratio process
                            h_out['resolved_dn'][reg][cat][tag][f'{varb}_rebin_raw'] = hist.Hist(self.massZZ_bins['resolved'])
                            h_out['resolved_dn'][reg][cat][tag][f'{varb}_rebin_raw'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )
                            #2D template
                            h_out['resolved_dn'][reg][cat][tag][f'{varb}_rebin_2d'] = hist.Hist(self.massZZ_bins['resolved'],hist.axis.Regular(50, 0, 1))
                            h_out['resolved_dn'][reg][cat][tag][f'{varb}_rebin_2d'].fill(
                                cut_event[varb],
                                cut_event['KD_Zjj_dn'],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),                                
                            )

                        elif self.option == None: #store all variables only if option is None
                            h_out['resolved_dn'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['resolved_dn'][reg][cat][tag][varb].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )
         
        ####Merged cut apply and fill histo for each variable
        #frist is no net cut merged cut

        if self.option == None: #store all variables only if option is None
            h_out['merged_notag']={}
            for cat in self.leptonic_cut_cats:
                selection = self.config['cut']['merged']['notag'][cat]
                cut = ak.numexpr.evaluate(selection,events)
                cut_event = events[cut]

                h_out['merged_notag'][cat] = {}
                for varb in self.config['bininfo_merged'].keys():
                    if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange': continue

                    bins = self.config['bininfo_merged'][varb][0]
                    start = self.config['bininfo_merged'][varb][1]
                    stop = self.config['bininfo_merged'][varb][2]
                    name = self.config['bininfo_merged'][varb][3]
                    h_out['merged_notag'][cat][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                    h_out['merged_notag'][cat][varb].fill(
                        cut_event[varb],
                        weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                            ak.ones_like(cut_event.EventWeight),
                    )

        #second is merged with net cut
        h_out['merged_tag']={}
        for reg in self.regions:
            h_out['merged_tag'][reg]={}
            for cat in self.leptonic_cut_cats:
                h_out['merged_tag'][reg][cat]={}
                for tag in self.tags:
                    selection = self.config['cut']['merged']['net'][reg][cat][tag]
                    cut = ak.numexpr.evaluate(selection,events)
                    cut_event = events[cut]

                    h_out['merged_tag'][reg][cat][tag]={}
                    for varb in self.config['bininfo_merged'].keys():
                        if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange': continue
                        bins = self.config['bininfo_merged'][varb][0]
                        start = self.config['bininfo_merged'][varb][1]
                        stop = self.config['bininfo_merged'][varb][2]
                        name = self.config['bininfo_merged'][varb][3]

                        if varb=='mass2lj':
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins['merged'])
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )

                            h_out['merged_tag'][reg][cat][tag][f'{varb}_fit'] = hist.Hist(hist.axis.Regular(4000, 0, 4000, name = f'{varb}_fit'))
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_fit'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )

                            h_out['merged_tag'][reg][cat][tag][f'{varb}_allrange'] = hist.Hist(hist.axis.Regular(80, 0, 4000, name = f'{varb}_allrange'))
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_allrange'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight), 
                            )

                            #eventweight set to one for alpha ratio process
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin_raw'] = hist.Hist(self.massZZ_bins['merged'])
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin_raw'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )

                            #2D template
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin_2d'] = hist.Hist(self.massZZ_bins['merged'],hist.axis.Regular(50, 0, 1))
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin_2d'].fill(
                                cut_event[varb],
                                cut_event['KD_ZJ'],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),                                
                            )
                        elif self.option == None: #store all variables only if option is None
                            h_out['merged_tag'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['merged_tag'][reg][cat][tag][varb].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if ((not is_data) and (varb!='GEN_H1_mass')) else \
                                    ak.ones_like(cut_event.EventWeight),
                            )
                    if self.option == None: #store only split variables if option is None
                        for varb in self.config['bininfo_merged_split'].keys():
                            bins = self.config['bininfo_merged_split'][varb][0]
                            start = self.config['bininfo_merged_split'][varb][1]
                            stop = self.config['bininfo_merged_split'][varb][2]
                            name = self.config['bininfo_merged_split'][varb][3]
                            h_out['merged_tag'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['merged_tag'][reg][cat][tag][varb].fill(
                                cut_event[varb] if varb != 'ptmerged_raw' else cut_event['ptmerged'],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )
        #merged up with net cut
        h_out['merged_tag_up']={}
        for reg in self.regions:
            h_out['merged_tag_up'][reg]={}
            for cat in self.leptonic_cut_cats:
                h_out['merged_tag_up'][reg][cat]={}
                for tag in self.tags:
                    selection = self.config['cut']['merged']['net_up'][reg][cat][tag]
                    cut = ak.numexpr.evaluate(selection,events)
                    cut_event = events[cut]

                    h_out['merged_tag_up'][reg][cat][tag]={}
                    for varb in self.config['bininfo_mergedup'].keys():
                        bins = self.config['bininfo_mergedup'][varb][0]
                        start = self.config['bininfo_mergedup'][varb][1]
                        stop = self.config['bininfo_mergedup'][varb][2]
                        name = self.config['bininfo_mergedup'][varb][3]

                        if varb=='mass2lj_up':
                            h_out['merged_tag_up'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins['merged'])
                            h_out['merged_tag_up'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )

                            #eventweight set to one for alpha ratio process
                            h_out['merged_tag_up'][reg][cat][tag][f'{varb}_rebin_raw'] = hist.Hist(self.massZZ_bins['merged'])
                            h_out['merged_tag_up'][reg][cat][tag][f'{varb}_rebin_raw'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )

                            #2D template
                            h_out['merged_tag_up'][reg][cat][tag][f'{varb}_rebin_2d'] = hist.Hist(self.massZZ_bins['merged'],hist.axis.Regular(50, 0, 1))
                            h_out['merged_tag_up'][reg][cat][tag][f'{varb}_rebin_2d'].fill(
                                cut_event[varb],
                                cut_event['KD_ZJ_up'],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),                                
                            )
                        elif self.option == None: #store all variables only if option is None
                            h_out['merged_tag_up'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['merged_tag_up'][reg][cat][tag][varb].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )
        #merged dn with net cut
        h_out['merged_tag_dn']={}
        for reg in self.regions:
            h_out['merged_tag_dn'][reg]={}
            for cat in self.leptonic_cut_cats:
                h_out['merged_tag_dn'][reg][cat]={}
                for tag in self.tags:
                    selection = self.config['cut']['merged']['net_dn'][reg][cat][tag]
                    cut = ak.numexpr.evaluate(selection,events)
                    cut_event = events[cut]

                    h_out['merged_tag_dn'][reg][cat][tag]={}
                    for varb in self.config['bininfo_mergeddn'].keys():
                        bins = self.config['bininfo_mergeddn'][varb][0]
                        start = self.config['bininfo_mergeddn'][varb][1]
                        stop = self.config['bininfo_mergeddn'][varb][2]
                        name = self.config['bininfo_mergeddn'][varb][3]

                        if varb=='mass2lj_dn':
                            h_out['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins['merged'])
                            h_out['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )

                            #eventweight set to one for alpha ratio process
                            h_out['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin_raw'] = hist.Hist(self.massZZ_bins['merged'])
                            h_out['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin_raw'].fill(
                                cut_event[varb],
                                weight=ak.ones_like(cut_event.EventWeight),
                            )

                            #2D template
                            h_out['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin_2d'] = hist.Hist(self.massZZ_bins['merged'],hist.axis.Regular(50, 0, 1))
                            h_out['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin_2d'].fill(
                                cut_event[varb],
                                cut_event['KD_ZJ_dn'],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),                                
                            )
                        elif self.option == None: #store all variables only if option is None
                            h_out['merged_tag_dn'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                            h_out['merged_tag_dn'][reg][cat][tag][varb].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )

        return {
            dataset: {
                "entries": len(events),
                "h_out": h_out,
            }
        }

    def postprocess(self, accumulator):
        pass



class CutUnit():
    def __init__(self,year,varb = None) -> None:
        self.processor = CutAllCatCoffeaProcessor
        self.year = year
        self.fileset = setting().fileset[self.year]
        #self.outstr = f"{self.year}_signal"
        self.outstr = f"{self.year}"
        #print(self.fileset)
        #self.option = 'masszz'
        self.option = None

        self.futures_run = processor.Runner(
            executor = processor.FuturesExecutor(compression=None, workers=8),
            schema=BaseSchema,
        )

    def run(self):
        config = setting().config
        out = self.futures_run(self.fileset,'passedEvents',processor_instance=self.processor(config,self.year,self.fileset,self.option))

        leptonic_cut_cats=['isEE','isMuMu','2lep']
        regions = ['CR','SR','ALL','LSB','HSB'] + ['VR','SB']
        AlphaRegions = ['VR','SB']
        tags = ['btag','untag','vbftag','all']
        out_h_dir_name = 'h_out'

        out_file_name = f"hist_{self.outstr}.root" if self.option == None else f"hist_{self.outstr}_{self.option}.root"
        with uproot.recreate(out_file_name) as fw:
            for sample in self.fileset.keys():
                ##Gen Variable
                fw[f'{sample}/GEN_H1_mass'] = out[sample][out_h_dir_name]['GEN_H1_mass']
                ##store Lep cut
                if self.option == None:
                    for cat in leptonic_cut_cats:
                        for varb in config['bininfo'].keys():
                            if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange' or varb.find('_rebin')!=-1: continue
                            fw[f'{sample}/lep/{cat}/{varb}'] = out[sample][out_h_dir_name]['lep'][cat][varb]

                ##store resolved cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo_resolved'].keys():
                                if varb == 'mass2l2jet':
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][f'{varb}_rebin']
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin_2d'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][f'{varb}_rebin_2d']
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin_raw'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][f'{varb}_rebin_raw']
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_fit'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][f'{varb}_fit']
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_allrange'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][f'{varb}_allrange']
                                elif self.option == None: #store all variables only if option is None
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][varb]
                            if self.option == None: #store all variables only if option is None
                                for varb in config['bininfo_resolved_split'].keys():
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][varb]
                ##store resolved_up cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo_resolvedup'].keys():
                                if varb == 'mass2l2jet_up':
                                    fw[f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['resolved_up'][reg][cat][tag][f'{varb}_rebin']
                                    fw[f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}_rebin_2d'] = out[sample][out_h_dir_name]['resolved_up'][reg][cat][tag][f'{varb}_rebin_2d']
                                    fw[f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}_rebin_raw'] = out[sample][out_h_dir_name]['resolved_up'][reg][cat][tag][f'{varb}_rebin_raw']
                                elif self.option == None: #store all variables only if option is None
                                    fw[f'{sample}/resolved_up/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['resolved_up'][reg][cat][tag][varb]
                ##store resolved_dn cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo_resolveddn'].keys():
                                if varb == 'mass2l2jet_dn':
                                    fw[f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['resolved_dn'][reg][cat][tag][f'{varb}_rebin']
                                    fw[f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}_rebin_2d'] = out[sample][out_h_dir_name]['resolved_dn'][reg][cat][tag][f'{varb}_rebin_2d']
                                    fw[f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}_rebin_raw'] = out[sample][out_h_dir_name]['resolved_dn'][reg][cat][tag][f'{varb}_rebin_raw']
                                elif self.option == None: #store all variables only if option is None
                                    fw[f'{sample}/resolved_dn/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['resolved_dn'][reg][cat][tag][varb]
                ##store merged not net cut
                if self.option == None:
                    for cat in leptonic_cut_cats:
                        for varb in config['bininfo_merged'].keys():
                            if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange': continue
                            fw[f'{sample}/merged_notag/{cat}/{varb}'] = out[sample][out_h_dir_name]['merged_notag'][cat][varb]
                ##store merged tag cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo_merged'].keys():
                                if varb == 'mass2l2jet_allrange' or varb == 'mass2lj_allrange': continue
                                if varb == 'mass2lj':
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][f'{varb}_rebin']
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin_2d'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][f'{varb}_rebin_2d']
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin_raw'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][f'{varb}_rebin_raw']
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_fit'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][f'{varb}_fit']
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_allrange'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][f'{varb}_allrange']
                                elif self.option == None: #store all variables only if option is None
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][varb]
                            if self.option == None: #store all variables only if option is None
                                for varb in config['bininfo_merged_split'].keys():
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][varb]
                ##store merged up tag cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo_mergedup'].keys():
                                if varb == 'mass2lj_up':
                                    fw[f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['merged_tag_up'][reg][cat][tag][f'{varb}_rebin']
                                    fw[f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}_rebin_2d'] = out[sample][out_h_dir_name]['merged_tag_up'][reg][cat][tag][f'{varb}_rebin_2d']
                                    fw[f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}_rebin_raw'] = out[sample][out_h_dir_name]['merged_tag_up'][reg][cat][tag][f'{varb}_rebin_raw']
                                elif self.option == None: #store all variables only if option is None
                                    fw[f'{sample}/merged_tag_up/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['merged_tag_up'][reg][cat][tag][varb]
                ##store merged dn tag cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo_mergeddn'].keys():
                                if varb == 'mass2lj_dn':
                                    fw[f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin']
                                    fw[f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}_rebin_2d'] = out[sample][out_h_dir_name]['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin_2d']
                                    fw[f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}_rebin_raw'] = out[sample][out_h_dir_name]['merged_tag_dn'][reg][cat][tag][f'{varb}_rebin_raw']
                                elif self.option == None: #store all variables only if option is None
                                    fw[f'{sample}/merged_tag_dn/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['merged_tag_dn'][reg][cat][tag][varb]