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

class MakeResolutionCoffeaProcessor(processor.ProcessorABC):
    def __init__(self,config = None,year = None,fileset = None):
        self.config = config
        self.year = year
        self.fileset = fileset
        self.sumWeight = 0.0
        #self.leptonic_cut_cats=['isEE','isMuMu','2lep']
        self.leptonic_cut_cats='2lep'
        #self.regions = ['CR','SR','ALL']
        self.regions = 'SR'
        #self.tags = ['btag','untag','vbftag','all']
        self.tags = 'all'
        self.massZZ_bins = setting().massZZ_bins
        self.gen_higss_str = 'GEN_H1_mass'
        self.varb = {'resolved':'mass2l2jet','merged':'mass2lj'}
        #self.isData = isData

    def getbininfo(self,dataset):
        '''
            input: any varb exsited in config
            output: bins informations associated with bins start stop name
        '''
        mean = int(dataset[3:])
        start = mean-500
        stop = mean+500
        bins = 100

        return mean,start,stop,bins
    
    def process(self,events):
        dataset = events.metadata['dataset']
        mean,start,stop,bins = self.getbininfo(dataset)

        h_out = {}
        
        h_out['resolved'] = {}
        selection = self.config['cut']['resolved'][self.regions][self.leptonic_cut_cats][self.tags]
        cut = ak.numexpr.evaluate(selection,events)
        cut_event = events[cut]

        h_out['resolved'] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
        h_out['resolved'].fill(
            cut_event[self.varb['resolved']]-cut_event[self.gen_higss_str]+mean,
            weight = ak.ones_like(cut_event[self.varb['resolved']])
        )

        h_out['merged'] = {}
        selection = self.config['cut']['merged']['net'][self.regions][self.leptonic_cut_cats][self.tags]
        cut = ak.numexpr.evaluate(selection,events)
        cut_event = events[cut]

        h_out['merged'] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
        h_out['merged'].fill(
            cut_event[self.varb['merged']]-cut_event[self.gen_higss_str]+mean,
            weight = ak.ones_like(cut_event[self.varb['merged']])
        )
    
        return {
            dataset:{
                "h_out":h_out
            }
        }
    
    def postprocess(self, accumulator):
        pass

class MakeResolution(MakeResolutionCoffeaProcessor):
    def __init__(self, config=setting().config, year=None, fileset=None):

        super().__init__(config, year, fileset)

        self.massList = setting().massList
        self.fileset = setting().sigfileset[year]['sig']
        #self.fileset = setting().sigfileset[year]['ggh500']
        self.h_out = {}

    #getbininfo
    def getbininfo(self,mass):
        '''
            input: any varb exsited in config
            output: bins informations associated with bins start stop name
        '''
        mean = mass
        start = mean-500
        stop = mean+500
        bins = 100
        
        return mean,start,stop,bins

    def writeoutfile(self):
        with uproot.recreate(f"SignalModel/Hist_resolution{self.year}.root") as fw:
        #with uproot.recreate(f"SignalModel/Hist_resolution{self.year}_sig500.root") as fw:
            for mass in self.massList:
                fw[f"sig{mass}_resolved_resolution"] = self.h_out['resolved'][mass]
                fw[f"sig{mass}_resolved_reco"] = self.h_out['resolved'][f"{mass}_reco"]
                fw[f"sig{mass}_resolved_gen"] = self.h_out['resolved'][f"{mass}_gen"]
                fw[f"sig{mass}_merged_resolution"] = self.h_out['merged'][mass]
                fw[f"sig{mass}_merged_reco"] = self.h_out['merged'][f"{mass}_reco"]
                fw[f"sig{mass}_merged_gen"] = self.h_out['merged'][f"{mass}_gen"]


    def run(self):
        #events = uproot.open(self.fileset[0])['passedEvents']
        events = uproot.lazy([f"{self.fileset[0]}:passedEvents"])
        self.h_out['resolved'] = {}
        self.h_out['merged'] = {}
        for mass in self.massList:
            mean, start, stop, bins = self.getbininfo(mass)
            width = mass*0.03 if mass < 1000 else mass*0.05
            massLow = mass-width; massHigh = mass+width

            #cut on resolved case
            #selection = f"{self.config['cut']['resolved'][self.regions][self.leptonic_cut_cats][self.tags]} & (mass2l2jet>{massLow}) & (mass2l2jet<{massHigh})"
            #add gen Higgs mass cut
            selection = f"{self.config['cut']['resolved'][self.regions][self.leptonic_cut_cats][self.tags]} & (GEN_H1_mass>{massLow}) & (GEN_H1_mass<{massHigh})"
            cut = ak.numexpr.evaluate(selection,events)
            cut_event = events[cut]
            #save resolution histogram
            self.h_out['resolved'][mass] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
            self.h_out['resolved'][mass].fill(
                cut_event[self.varb['resolved']]-cut_event[self.gen_higss_str]+mean,
                weight = ak.ones_like(cut_event[self.varb['resolved']])
            )
            #self.h_out['resolved'][mass].fill(
            #    cut_event[self.varb['resolved']]-cut_event[self.gen_higss_str],
            #    weight = ak.ones_like(cut_event[self.varb['resolved']])
            #)

            #save reconstruction level histogram
            self.h_out['resolved'][f"{mass}_reco"] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
            self.h_out['resolved'][f"{mass}_reco"].fill(
                cut_event[self.varb['resolved']],
                weight = ak.ones_like(cut_event[self.varb['resolved']])
            )
            #save generator level histogram
            self.h_out['resolved'][f"{mass}_gen"] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
            self.h_out['resolved'][f"{mass}_gen"].fill(
                cut_event[self.gen_higss_str],
                weight = ak.ones_like(cut_event[self.gen_higss_str])
            )

            #cut on merged case
            #selection = f"{self.config['cut']['merged']['net'][self.regions][self.leptonic_cut_cats][self.tags]} & (mass2lj>{massLow}) & (mass2lj<{massHigh})"
            #add gen Higgs mass cut
            selection = f"{self.config['cut']['merged']['net'][self.regions][self.leptonic_cut_cats][self.tags]} & (GEN_H1_mass>{massLow}) & (GEN_H1_mass<{massHigh})"
            cut = ak.numexpr.evaluate(selection,events)
            cut_event = events[cut]

            #save resolution histogram
            self.h_out['merged'][mass] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
            self.h_out['merged'][mass].fill(
                cut_event[self.varb['merged']]-cut_event[self.gen_higss_str]+mean,
                weight = ak.ones_like(cut_event[self.varb['merged']])
            )
            #save reconstruction level histogram
            self.h_out['merged'][f"{mass}_reco"] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
            self.h_out['merged'][f"{mass}_reco"].fill(
                cut_event[self.varb['merged']],
                weight = ak.ones_like(cut_event[self.varb['merged']])
            )
            #save generator level histogram
            self.h_out['merged'][f"{mass}_gen"] = hist.Hist(hist.axis.Regular(bins=bins, start=start, stop=stop))
            self.h_out['merged'][f"{mass}_gen"].fill(
                cut_event[self.gen_higss_str],
                weight = ak.ones_like(cut_event[self.gen_higss_str])
            )

        
        self.writeoutfile()



#older version
class MakeResolutionUnit():
    def __init__(self,year) -> None:
        self.processor = MakeResolutionCoffeaProcessor
        self.year = year
        self.fileset = setting().sigfileset[self.year]
        #self.outstr = f"{self.year}_signal"
        self.outstr = f"{self.year}"
        #print(self.fileset)

        self.futures_run = processor.Runner(
            executor = processor.FuturesExecutor(compression=None, workers=8),
            schema=BaseSchema,
        )
    
    def run(self):
        reg = 'SR'
        cat = '2lep'
        tag = 'all'
        config = setting().config
        out = self.futures_run(self.fileset,'passedEvents',processor_instance=self.processor(config,self.year,self.fileset))
        out_h_dir_name = 'h_out'
        with uproot.recreate(f"SignalModel/Hist_resolution{self.outstr}.root") as fw:
            for sample in self.fileset.keys():
                fw[f"{sample}_resolved_resolution"] = out[sample][out_h_dir_name]['resolved']
                fw[f"{sample}_merged_resolution"] = out[sample][out_h_dir_name]['merged']


