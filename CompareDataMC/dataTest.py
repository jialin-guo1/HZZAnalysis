#!/usr/bin/env python
import ROOT
ROOT.gStyle.SetOptStat(False)

t = ROOT.TChain("passedEvents")
#t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2016/2016_noDuplicates.root")
#t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2017/2017_noDuplicates.root")
t.Add("/afs/cern.ch/work/g/guoj/XToZZ_FullRunII/Data2018/2018_noDuplicates_new.root")

Data = ROOT.TH1D("Data","result(RuII)",50,70,170)
Data.GetYaxis().SetTitle("Events / 2 GeV")
Data.SetMarkerStyle(20)
Data.SetMarkerColor(ROOT.kBlack)
Data.SetMarkerSize(1.2)
Data.SetLineColor(ROOT.kBlack)
Data.SetLineWidth(1)
Data.SetFillColor(ROOT.kRed)
c = ROOT.TCanvas()

#check binWidth
axis = Data.GetXaxis()
print " bin Width = " + str(axis.GetBinWidth(axis.FindBin(100)))

#chek bin value of each bin
nMass = 0
for ievent,event in enumerate(t):
#    if(not event.passedFullSelection): continue
#    if ievent == 100: break
    Data.Fill(event.H_FSR)
    if(event.H_FSR>70):
        nMass += 1
print "RunII mass window number = " +str(nMass)
#print "2017 mass window number = " +str(nMass)


axis = Data.GetXaxis()
massWindow = 0
for value in range(106,142):
    bin_number = axis.FindBin(value)
#    print " Get {0:d} bin number ".format(value) + str(bin_number)
    print " Bin {0:d} Cneter Value = ".format(value) + str(Data.GetBinContent(bin_number))
    massWindow += Data.GetBinContent(bin_number)
#print "RunII mass window = " + str(massWindow)
#print "RunII mass window number = " +str(Data.Integral())

#print "Bin numbers = " + str(Data.FindBin(100))
#print "Bin 110 Content = " + str(Data.GetBinContent(Data.FindBin(110)))
#print "Bin 100 Content = " + str(Data.GetBinContent(Data.FindBin(100)))


Data.Draw("E1")
Data.Draw("same")

c.SaveAs("Run2018massWindow.png")
