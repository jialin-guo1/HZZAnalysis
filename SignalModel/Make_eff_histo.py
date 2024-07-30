import hist
import uproot
import awkward as ak
import sys
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from setting import setting
from logset import *

def build_eff_histos(year,config):
    p_save = "File_eff_v2"

    # input file and tree
    input_file_name = "/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggh/skimed/ggh.root"
    arr = uproot.lazy([f'{input_file_name}:passedEvents'])

    # some global variables
    region = "SR"; tags = ['btag','untag','vbftag','all']; channels = ['isEE','isMuMu','2lep']
    low_mass = 0; high_mass = 3500; n_bins = 70

    # create denominator histogram for each category
    hist_gen_mass_tot = hist.Hist(hist.axis.Regular(n_bins, low_mass, high_mass))
    hist_gen_mass_tot.fill(arr['GEN_H1_mass'])

    # create numerator histogram for each category
    hist_gen_mass = {'resolved':{},'merged':{}}
    for category in ['resolved','merged']:
        for channel in channels:
            hist_gen_mass[category][channel] = {}
            for tag in tags:
                hist_gen_mass[category][channel][tag] = hist.Hist(hist.axis.Regular(n_bins, low_mass, high_mass))

    # make cut for each channel and tag 
    for channel in channels:
        for tag in tags:
            # resolved case
            selection = config['cut'][region][channel]['resolved'][tag]
            cut = ak.numexpr.evaluate(selection, arr)
            arr_cut = arr[cut]
            hist_gen_mass['resolved'][channel][tag].fill(arr_cut['GEN_H1_mass'])

            # merged case
            selection = config['cut'][region][channel]['merged'][tag]
            cut = ak.numexpr.evaluate(selection, arr)
            arr_cut = arr[cut]
            hist_gen_mass['merged'][channel][tag].fill(arr_cut['GEN_H1_mass'])

    # save histograms
    output_file = uproot.recreate(f'{p_save}/Histos_MakeEff_{year}.root')
    output_file['gen_mass_tot'] = hist_gen_mass_tot
    for category in ['resolved','merged']:
        for channel in channels:
            for tag in tags:
                output_file[f'gen_mass_{category}_{channel}_{tag}'] = hist_gen_mass[category][channel][tag]
    output_file.close()
    logger.info(f"Efficiency histograms saved in {p_save}/Histos_MakeEff_{year}.root")

def compute_eff(year,config):
    import ROOT


    p_save = "File_eff_v2"
    input_file = ROOT.TFile(f'{p_save}/Histos_MakeEff_{year}.root','READ')
    hist_gen_mass_tot = input_file.Get('gen_mass_tot')

    # compute eff 
    tags = ['btag','untag','vbftag','all']; channels = ['isEE','isMuMu','2lep']
    # create a new file to save efficiency histograms
    output_file = ROOT.TFile(f'{p_save}/Histos_Eff_{year}.root','recreate')
    output_file.cd()
    for category in ['resolved','merged']:
        for channel in channels:
            for tag in tags:
                hist_gen_mass = input_file.Get(f'gen_mass_{category}_{channel}_{tag}')
                hist_eff = hist_gen_mass.Clone(f'eff_mass_{category}_{channel}_{tag}')
                hist_eff.Divide(hist_gen_mass_tot)
                hist_eff.SetTitle(f'eff_{category}_{channel}_{tag}')
                hist_eff.SetName(f'eff_{category}_{channel}_{tag}')
                hist_eff.Write(f"eff_{category}_{channel}_{tag}")
    output_file.Close()
    logger.info(f"Efficiency histograms saved in {p_save}/Histos_Eff_{year}.root")

if __name__ == "__main__":
    #logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    year = "2018"
    config = setting(year).config; logger.debug(f"config: {config}")

    # run build hitograms of numerator and denominator for computing efficiency
    #build_eff_histos(year, config)

    # run compute efficiency
    compute_eff(year, config)

    pass



