import ROOT as ROOT
from array import array

def draw_hist(diff_histogram,reco_histogram,gen_histogram,case,mass,path):
    # Print the standard deviation for both histograms
    gen_std_dev = round(get_standard_deviation(gen_histogram),2)
    reco_std_dev = round(get_standard_deviation(reco_histogram),2)
    diff_std_dev = round(get_standard_deviation(diff_histogram), 2)

    # Draw the histograms on a canvas
    canvas = ROOT.TCanvas("canvas", "Higgs Mass Comparison", 800, 600)
    diff_histogram.Draw("hist")
    diff_histogram.SetLineColor(ROOT.kBlack)
    diff_histogram.SetLineWidth(2)
    gen_histogram.Draw('same hist')
    gen_histogram.SetLineColor(ROOT.kRed)
    gen_histogram.SetLineWidth(2)
    reco_histogram.Draw("same hist")
    reco_histogram.SetLineColor(ROOT.kBlue)
    reco_histogram.SetLineWidth(2)

    # add legend
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(gen_histogram, "GEN Higgs Mass", "l")
    legend.AddEntry(reco_histogram, "RECO Higgs Mass", "l")
    legend.AddEntry(diff_histogram, "Difference", "l")
    legend.Draw()

    # print the standard deviation on the canvas
    text = ROOT.TLatex()
    text.SetNDC()
    # round off to 2 decimal places
    text.DrawLatex(0.1, 0.8, "GEN Std Dev: {}".format(gen_std_dev))
    text.DrawLatex(0.1, 0.7, "RECO Std Dev: {}".format(reco_std_dev))
    text.DrawLatex(0.1, 0.6, "Difference Std Dev: {}".format(diff_std_dev))

    canvas.Update()
    canvas.SaveAs("{}/higgs_mass_comparison_{}_{}.png".format(path,mass,case))

def plot_diff_histogram(file_name,year,cat):
    path = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/plotJun2/"+year
    extra_str = (file_name.split("_")[2]).split(".")[0]
    file = ROOT.TFile(file_name)
    keys = file.GetListOfKeys()
    for key in keys:
        histogram_name = key.GetName()
        if "_"+cat+"_resolution" in histogram_name:
            mass = int(histogram_name.split("_")[0].lstrip("ggh"))
            histogram = key.ReadObj()
            std_dev = histogram.GetStdDev()

            # Plot the difference histogram
            canvas = ROOT.TCanvas("canvas", "Difference Histogram", 800, 600)
            histogram.Draw("hist")
            histogram.SetLineColor(ROOT.kBlack)
            histogram.SetLineWidth(2)
            histogram.SetTitle("Difference Histogram")
            histogram.GetXaxis().SetTitle("Difference [GeV]")
            histogram.GetYaxis().SetTitle("Number of Events")
            canvas.SetTitle("Difference Histogram for Mass {}".format(mass))
            canvas.SaveAs("{}/diff_histogram_{}_{}_{}.png".format(path,cat,mass,extra_str))

def plot_std_dev_vs_mass_weighted(file_name, year, cat):
    path = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/SignalModel/plotJun2/"+year
    file = ROOT.TFile(file_name)
    keys = file.GetListOfKeys()
    masses = {'unweight':[],'weighted':[]}
    std_devs = {'unweight':[],'weighted':[]}
    std_devs_error = {'unweight':[],'weighted':[]}

    for key in keys:
        histogram_name = key.GetName()
        print(histogram_name)
        if ("_"+cat+"_resolution_2lep" in histogram_name) and ("_weighted" not in histogram_name):
            #append *_resolution_2lep.root
            #mass = int(histogram_name.split("_")[0].lstrip("ggh"))
            mass = int(histogram_name.split("_")[0].lstrip("sig"))
            histogram = key.ReadObj()
            std_dev = histogram.GetStdDev()
            std_dev_error = histogram.GetStdDevError()

            masses['unweight'].append(mass)
            std_devs['unweight'].append(std_dev)
            std_devs_error['unweight'].append(std_dev_error)


            #append *_resolution_2lep_.root_weighted.root
            histogram_name_weighted = histogram_name+"_weighted"
            histogram_weighted = file.Get(histogram_name_weighted)
            std_dev_weighted = histogram_weighted.GetStdDev()
            std_dev_weighted_error = histogram_weighted.GetStdDevError()

            masses['weighted'].append(mass)
            std_devs['weighted'].append(std_dev_weighted)
            std_devs_error['weighted'].append(std_dev_weighted_error)
    
    print(masses)
    print(std_devs)
    
    # Plot the standard deviation vs mass
    MultiGraph = ROOT.TMultiGraph()
    colorList = [ROOT.EColor.kGreen,ROOT.EColor.kBlue,ROOT.EColor.kRed,ROOT.EColor.kYellow+2,ROOT.EColor.kRed,ROOT.EColor.kMagenta,ROOT.EColor.kBlue,ROOT.EColor.kCyan]
    if cat == "resolved":
        leg = ROOT.TLegend(.55, .2, .85, .4)
    else:
        leg = ROOT.TLegend(.2, .65, .5, .85)
    #plot unweight 
    #graph = ROOT.TGraph(len(masses['unweight']), array('d', masses['unweight']), array('d', std_devs['unweight']))
    #make TGraphAsymmErrors 
    #create an array of zeros for the x error
    x_error = array('d', [0.0]*len(masses['unweight']))
    graph = ROOT.TGraphAsymmErrors(len(masses['unweight']), array('d', masses['unweight']), array('d', std_devs['unweight']), x_error, x_error, array('d', std_devs_error['unweight']), array('d', std_devs_error['unweight']))
    graph.SetLineColor(ROOT.EColor.kGreen)
    graph.SetMarkerColor(ROOT.EColor.kGreen)
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.5)
    leg.AddEntry(graph, "unweight", "p")
    MultiGraph.Add(graph,"PL")
    #plot weighted
    #graph = ROOT.TGraph(len(masses['weighted']), array('d', masses['weighted']), array('d', std_devs['weighted']))
    #make TGraphAsymmErrors
    #create an array of zeros for the x error
    x_error = array('d', [0.0]*len(masses['weighted']))
    graph = ROOT.TGraphAsymmErrors(len(masses['weighted']), array('d', masses['weighted']), array('d', std_devs['weighted']), x_error, x_error, array('d', std_devs_error['weighted']), array('d', std_devs_error['weighted']))
    graph.SetLineColor(ROOT.EColor.kRed)
    graph.SetMarkerColor(ROOT.EColor.kRed)
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.5)
    leg.AddEntry(graph, "weighted", "p")
    MultiGraph.Add(graph,"PL")

    #plot all channel
    canvas = ROOT.TCanvas("canvas", "Standard Deviation vs Mass", 800, 600)
    MultiGraph.Draw("AP")
    MultiGraph.SetTitle("Standard Deviation vs Mass")
    MultiGraph.GetXaxis().SetTitle("Mass of Higgs [GeV]")
    MultiGraph.GetYaxis().SetTitle("Standard Deviation [GeV]")
    leg.Draw()
    canvas.SetTitle("Standard Deviation vs Mass for {}".format(cat))
    canvas.SaveAs("{}/std_dev_vs_mass_{}_{}_weighted.png".format(path,cat,year))


def plot_std_dev_vs_mass(file_name, year, cat,if_allchannel=False):
    channels = ['isEE','isMuMu','2lep']
    file = ROOT.TFile(file_name)

    keys = file.GetListOfKeys()

    masses = {}
    std_devs = {}
    for channel in channels:
        masses[channel] = []
        std_devs[channel] = []

    # Loop over the keys to find histograms matching the pattern
    for channel in channels:
        for key in keys:
            histogram_name = key.GetName()
            if "_"+cat+"_resolution_"+channel in histogram_name:
                #mass = int(histogram_name.split("_")[0].lstrip("sig"))
                mass = int(histogram_name.split("_")[0].lstrip("ggh"))
                masses[channel].append(mass)

                histogram = key.ReadObj()
                std_dev = histogram.GetStdDev()
                std_devs[channel].append(std_dev)
    
    # Plot the standard deviation vs mass
    MultiGraph = ROOT.TMultiGraph()
    colorList = [ROOT.EColor.kGreen,ROOT.EColor.kBlue,ROOT.EColor.kRed,ROOT.EColor.kYellow+2,ROOT.EColor.kRed,ROOT.EColor.kMagenta,ROOT.EColor.kBlue,ROOT.EColor.kCyan]
    if cat == "resolved":
        leg = ROOT.TLegend( .55, .2, .85, .4 )
    else:
        leg = ROOT.TLegend( .2, .65, .5, .85)
    for i,channel in enumerate(channels):
        graph = ROOT.TGraph(len(masses[channel]), array('d', masses[channel]), array('d', std_devs[channel]))
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(1.5)
        graph.SetMarkerColor(colorList[i])
        leg.AddEntry(graph,channel,"p")
        #graph.SetTitle("Standard Deviation vs Mass of Higgs")
        #graph.GetXaxis().SetTitle("Mass of Higgs [GeV]")
        #graph.GetYaxis().SetTitle("Standard Deviation")
        MultiGraph.Add(graph,'PL')

    canvas = ROOT.TCanvas("canvas", "Standard Deviation vs Mass of Higgs", 800, 600)
    MultiGraph.Draw("AP")
    MultiGraph.GetXaxis().SetTitle("Mass of Higgs [GeV]")
    MultiGraph.GetYaxis().SetTitle("Standard Deviation")
    MultiGraph.SetTitle("Standard Deviation vs Mass of Higgs in "+cat)
    #MultiGraph.SetTitleSize(0.025)
    leg.Draw()
    #graph.Draw("AP")
    canvas.SetTitle("Standard Deviation vs Mass of Higgs in "+cat)
    canvas.SaveAs("std_dev_vs_mass_"+cat+year+"_individule.png")

    file.Close()


#plot std dev vs mass with systematics
def plot_std_dev_vs_mass_sys(file_name,year,cat,if_allchannel=False):
    channels = ['isEE','isMuMu','2lep'] if if_allchannel else ['2lep']
    file = ROOT.TFile(file_name)

    keys = file.GetListOfKeys()

    masses = {}
    std_devs = {}
    std_devs_error = {}
    
    for channel in channels:
        masses[channel] = []
        std_devs[channel] = []
        std_devs_error[channel] = []

    # Loop over the keys to find histograms matching the pattern
    for channel in channels:
        for key in keys:
            histogram_name = key.GetName()
            if "_"+cat+"_resolution_"+channel in histogram_name:
                #mass = int(histogram_name.split("_")[0].lstrip("ggh"))
                mass = int(histogram_name.split("_")[0].lstrip("sig"))
                masses[channel].append(mass)

                histogram = key.ReadObj()

                std_dev = histogram.GetStdDev()
                std_devs[channel].append(std_dev)

                std_dev_error = histogram.GetStdDevError()
                std_devs_error[channel].append(std_dev_error)
    
    # Plot the standard deviation vs mass
    MultiGraph = ROOT.TMultiGraph()
    colorList = [ROOT.EColor.kGreen,ROOT.EColor.kBlue,ROOT.EColor.kRed,ROOT.EColor.kYellow+2,ROOT.EColor.kRed,ROOT.EColor.kMagenta,ROOT.EColor.kBlue,ROOT.EColor.kCyan]
    if cat == "resolved":
        leg = ROOT.TLegend( .55, .2, .85, .4 )
    else:
        leg = ROOT.TLegend( .2, .65, .5, .85)
    for i,channel in enumerate(channels):
        #graph = ROOT.TGraph(len(masses[channel]), array('d', masses[channel]), array('d', std_devs[channel]))
        #make TGraphAsymmErrors 
        #create an array of zeros for the x error
        x_error = array('d',[0.0]*len(masses[channel]))
        graph = ROOT.TGraphAsymmErrors(len(masses[channel]), array('d', masses[channel]), array('d', std_devs[channel]), x_error, x_error, array('d', std_devs_error[channel]), array('d', std_devs_error[channel]))
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(1.0)
        graph.SetMarkerColor(colorList[i])
        leg.AddEntry(graph,channel,"p")
        #graph.SetTitle("Standard Deviation vs Mass of Higgs")
        #graph.GetXaxis().SetTitle("Mass of Higgs [GeV]")
        #graph.GetYaxis().SetTitle("Standard Deviation")
        MultiGraph.Add(graph,'PL')

    canvas = ROOT.TCanvas("canvas", "Standard Deviation vs Mass of Higgs", 800, 600)
    MultiGraph.Draw("AP")
    MultiGraph.GetXaxis().SetTitle("Mass of Higgs [GeV]")
    MultiGraph.GetYaxis().SetTitle("Standard Deviation")
    MultiGraph.SetTitle("Standard Deviation vs Mass of Higgs in "+cat)
    #MultiGraph.SetTitleSize(0.025)
    leg.Draw()
    #graph.Draw("AP")
    canvas.SetTitle("Standard Deviation vs Mass of Higgs in "+cat)
    canvas.SaveAs("std_dev_vs_mass_"+cat+year+"_individule.png")

    file.Close()



#======================================================================================================================================================
#======================================================================================================================================================
# #====================================================================================================================================================== 
#plot_std_dev_vs_mass("Hist_resolution2016.root", "2016", "resolved")
#plot_std_dev_vs_mass("Hist_resolution2017.root", "2017", "resolved")
#plot_std_dev_vs_mass("Hist_resolution2018_split.root", "2018", "resolved")

#plot_std_dev_vs_mass_sys("FilesDeltaM/Hist_resolution2018_split.root", "2018", "resolved",if_allchannel=True)
#plot_std_dev_vs_mass_sys("FilesDeltaM/Hist_resolution2018_split.root", "2018", "merged",if_allchannel=True)

#plot_std_dev_vs_mass_sys("FilesDeltaM/Hist_resolution2018_individule.root", "2018", "resolved",if_allchannel=True)
#plot_std_dev_vs_mass_sys("FilesDeltaM/Hist_resolution2018_individule.root", "2018", "merged",if_allchannel=True)

#plot_std_dev_vs_mass("Hist_resolution2018_individule.root", "2018", "resolved")
#plot_std_dev_vs_mass("Hist_resolution2016.root", "2016", "merged")
#plot_std_dev_vs_mass("Hist_resolution2017.root", "2017", "merged")
#plot_std_dev_vs_mass("Hist_resolution2018_split.root", "2018", "merged")
#plot_std_dev_vs_mass("Hist_resolution2018_individule.root", "2018", "merged")
plot_std_dev_vs_mass_weighted("Hist_resolution2018_split_width003.root", "2018", "resolved")
plot_std_dev_vs_mass_weighted("Hist_resolution2018_split_width003.root", "2018", "merged")

#plot_diff_histogram("Hist_resolution2018_lookat900Gev.root", "2018", "resolved")
#plot_diff_histogram("Hist_resolution2018_lookat900Gev.root", "2018", "merged")
#plot_diff_histogram("Hist_resolution2018_lookat1500Gev.root", "2018", "resolved")
#plot_diff_histogram("Hist_resolution2018_lookat1500Gev.root", "2018", "merged")
#plot_diff_histogram("Hist_resolution2018_lookat2500Gev.root", "2018", "resolved")
#plot_diff_histogram("Hist_resolution2018_lookat2500Gev.root", "2018", "merged")
#plot_diff_histogram("FilesDeltaM/Hist_resolution2018_individual_normalize_reco.root", "2018", "merged")
#plot_diff_histogram("FilesDeltaM/Hist_resolution2018_individual_normalize_reco.root", "2018", "resolved")
