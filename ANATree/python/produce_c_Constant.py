from ROOT import *

outpath = '/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/ANATree/data/RecoMEConstants/'
#outpath = './'
outfile = TFile(outpath+"gConstant_Zjj.root",'recreate')

fun_c = TF1("c_func","0.035*(3.05+(0.0005*x)-(2.73/(1.+exp((x-2500.)/258.26))))",0,12000)

xmin = 0.0; xmax = 12000.0
sp_tgfinal_ZZ_SM_over_tgfinal_Zjj = TSpline3("spline",xmin,xmax,fun_c,1000000)

sp_tgfinal_ZZ_SM_over_tgfinal_Zjj.Write()
outfile.Write()
