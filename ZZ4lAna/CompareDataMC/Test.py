from ROOT import *
from array import array


file=TFile("/cms/user/guojl/Sample/skimed/2016_noDuplicates.root")
tree=file.Get("passedEvents")
#nbins=8
#xbins=array('f',[100.,200.,300.,400.,500.,1000.,2000.,3000,3500.])
#h=TH1D("h","h",nbins,xbins)
h=TH1D("h","h",680,100,3500)
#c=TCanvas("c","c",800,600)
c=TCanvas("c","c",650,500)
c.SetLogx()
#c.SetLogy()

for ievent, event in enumerate(tree):
    if(not event.passedFullSelection): continue
    h.Fill(event.mass4l)

xaxis = h.GetXaxis()
xaxis.SetLabelOffset(99)
#bins = []
#for i in range(100,3500,5):
#    nbin=xaxis.FindBin(i)
#    bins.append(nbin)
#    xaxis.SetBinLabel(nbin,str(i))
h.Draw("p E1 X0")
x_low = 100
x_up =3500
step = 10
latex={}
label_margin = -0.40
for i in range(100,3500,step):
    if(i==200 or i==300 or i==400 or i==500 or i==1000 or i==2000 or i==3000):
        i_x = i
        latex[i] = TLatex(i_x,label_margin,"%.0f"%i_x)
        latex[i].SetTextAlign(23)
        latex[i].SetTextFont (42)
        latex[i].SetTextSize (0.04)
        latex[i].Draw()

c.SaveAs("plot/test.png")
