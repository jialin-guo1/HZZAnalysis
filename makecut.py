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

class CutCoffeaProcessor(processor.ProcessorABC):
    r"""the coffea processor for make cut step"""
    def __init__(self,config = None,year = None,fileset = None):
        self.config = config
        self.year = year
        self.fileset = fileset
        self.sumWeight = 0.0
        self.leptonic_cut_cats=['isEE','isMuMu','2lep']
        self.regions = ['CR','SR']
        self.tags = ['btag','untag','vbftag','all']
        self.massZZ_bins = setting().massZZ_bins

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

        ####Leptonic cut apply and fill histo for each variable
        h_out['lep'] = {}
        for cat in self.leptonic_cut_cats:
            selection = self.config['cut']['lep'][cat]
            cut = ak.numexpr.evaluate(selection,events)
            cut_event = events[cut]

            h_out['lep'][cat] = {}
            for varb in self.config['bininfo'].keys():
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
                    cut = ak.numexpr.evaluate(selection,events)
                    cut_event = events[cut]
                    
                    h_out['resolved'][reg][cat][tag] = {}
                    for varb in self.config['bininfo'].keys():
                        bins = self.config['bininfo'][varb][0]
                        start = self.config['bininfo'][varb][1]
                        stop = self.config['bininfo'][varb][2]
                        name = self.config['bininfo'][varb][3]
                        if varb=='mass2l2jet':
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins)
                            h_out['resolved'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            ) 
                        h_out['resolved'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                        h_out['resolved'][reg][cat][tag][varb].fill(
                            cut_event[varb],
                            weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                ak.ones_like(cut_event.EventWeight),
                        )

        #####Resolved up cut apply and fill histo for each variable 
        #h_out['resolved_up']={}
        #for reg in self.regions:
        #    h_out['resolved_up'][reg] = {}
        #    for cat in self.leptonic_cut_cats:
        #        h_out['resolved_up'][reg][cat] = {}
        #        for tag in self.tags:
        #            selection = self.config['cut']['resolved_up'][reg][cat][tag]
        #            cut = ak.numexpr.evaluate(selection,events)
        #            cut_event = events[cut]
        #            
        #            h_out['resolved_up'][reg][cat][tag] = {}
        #            for varb in self.config['bininfo'].keys():
        #                bins = self.config['bininfo'][varb][0]
        #                start = self.config['bininfo'][varb][1]
        #                stop = self.config['bininfo'][varb][2]
        #                name = self.config['bininfo'][varb][3]
        #                if varb=='mass2l2jet':
        #                    h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins)
        #                    h_out['resolved_up'][reg][cat][tag][f'{varb}_rebin'].fill(
        #                        cut_event[varb],
        #                        weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
        #                            ak.ones_like(cut_event.EventWeight),
        #                    ) 
        #                h_out['resolved_up'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
        #                h_out['resolved_up'][reg][cat][tag][varb].fill(
        #                    cut_event[varb],
        #                    weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
        #                        ak.ones_like(cut_event.EventWeight),
        #                )
       # 
        ####Merged cut apply and fill histo for each variable
        #frist is no net cut merged cut
        h_out['merged_notag']={}
        for cat in self.leptonic_cut_cats:
            selection = self.config['cut']['merged']['notag'][cat]
            cut = ak.numexpr.evaluate(selection,events)
            cut_event = events[cut]

            h_out['merged_notag'][cat] = {}
            for varb in self.config['bininfo'].keys():
                bins = self.config['bininfo'][varb][0]
                start = self.config['bininfo'][varb][1]
                stop = self.config['bininfo'][varb][2]
                name = self.config['bininfo'][varb][3]
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
                    for varb in self.config['bininfo'].keys():
                        bins = self.config['bininfo'][varb][0]
                        start = self.config['bininfo'][varb][1]
                        stop = self.config['bininfo'][varb][2]
                        name = self.config['bininfo'][varb][3]

                        if varb=='mass2lj':
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin'] = hist.Hist(self.massZZ_bins)
                            h_out['merged_tag'][reg][cat][tag][f'{varb}_rebin'].fill(
                                cut_event[varb],
                                weight=ak.numexpr.evaluate(f'EventWeight*{lumi}*1000*{xsec}/{self.sumWeight}',cut_event) if not is_data else \
                                    ak.ones_like(cut_event.EventWeight),
                            )
        
                        h_out['merged_tag'][reg][cat][tag][varb] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop, name=name))
                        h_out['merged_tag'][reg][cat][tag][varb].fill(
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

    def __init__(self,year) -> None:
        self.processor = CutCoffeaProcessor
        self.year = year
        self.fileset = setting().fileset[self.year]
        #print(self.fileset)

        self.futures_run = processor.Runner(
            executor = processor.FuturesExecutor(compression=None, workers=8),
            schema=BaseSchema,
        )

    def run(self):
        config = setting().config
        out = self.futures_run(self.fileset,'passedEvents',processor_instance=self.processor(config,self.year,self.fileset))

        leptonic_cut_cats=['isEE','isMuMu','2lep']
        regions = ['CR','SR']
        tags = ['btag','untag','vbftag','all']
        out_h_dir_name = 'h_out'
        with uproot.recreate(f"hist_{self.year}.root") as fw:
            for sample in self.fileset.keys():
                ##store Lep cut
                for cat in leptonic_cut_cats:
                    for varb in config['bininfo'].keys():
                        fw[f'{sample}/lep/{cat}/{varb}'] = out[sample][out_h_dir_name]['lep'][cat][varb]

                ##store resolved cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo'].keys():
                                if varb == 'mass2l2jet':
                                    fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][f'{varb}_rebin']
                                fw[f'{sample}/resolved/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['resolved'][reg][cat][tag][varb]
                ##store merged not net cut
                for cat in leptonic_cut_cats:
                    for varb in config['bininfo'].keys():
                        fw[f'{sample}/merged_notag/{cat}/{varb}'] = out[sample][out_h_dir_name]['merged_notag'][cat][varb]
                ##store merged tag cut
                for reg in regions:
                    for cat in leptonic_cut_cats:
                        for tag in tags:
                            for varb in config['bininfo'].keys():
                                if varb == 'mass2lj':
                                    fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}_rebin'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][f'{varb}_rebin']
                                fw[f'{sample}/merged_tag/{reg}/{cat}/{tag}/{varb}'] = out[sample][out_h_dir_name]['merged_tag'][reg][cat][tag][varb]