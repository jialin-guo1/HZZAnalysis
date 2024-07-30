import ROOT

f_input = ROOT.TFile("/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/MC/ggZZ4l.root","READ")
pass_tree = f_input.Get("ZZTree/candTree")
fail_tree = f_input.Get("ZZTree/candTree_failed")

# create a histogram for the ggZZ line shape
#h = ROOT.TH1F("h","ggZZ line shape",70,0,3500)
h = ROOT.TH1F("h","ggZZ line shape",350,0,3500)

# fill GenHMass branch from pass and fail trees into the histogram
pass_tree.Draw("GenHMass>>h","genHEPMCweight*PUWeight*KFactor_QCD_ggZZ_Nominal")
fail_tree.Draw("GenHMass>>h","genHEPMCweight*PUWeight*KFactor_QCD_ggZZ_Nominal")

# smooth the histogram
h.Smooth(1)

# Clone the histogram to a new histogram
h_clone = h.Clone()

# normalize the clone histogram
h_clone.Scale(1./h_clone.Integral())

# convert the histogram to RooHistPdf
#x = ROOT.RooRealVar("x","x",0,3500)
#h_pdf = ROOT.RooDataHist("h_pdf","h_pdf",ROOT.RooArgList(x),h)
#h_pdf = ROOT.RooHistPdf("h_pdf","h_pdf",ROOT.RooArgSet(x),h_pdf)

# plot the clone histogram
c = ROOT.TCanvas()
h_clone.Draw()
c.SaveAs("ggZZ_lineshape.png")

# save the clone, original histograms and pdf into a root file
f_output = ROOT.TFile("ggZZ_lineshape.root","RECREATE")
h.Write("ggZZ_lineshape_hist")
h_clone.Write("ggZZ_lineshape_norm_hist")
#h_pdf.Write("ggZZ_lineshape_pdf")
f_output.Close()

