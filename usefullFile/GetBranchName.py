from ROOT import *
file  = TFile("plots.root")
tree = file.Get("passedEvents")
tree.Show()
