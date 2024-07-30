# Instructions on using the workspaces
Two workspaces are provided: one with signal mass 200 GeV, width 1 GeV, the other with signal mass 3000 GeV, width 10 GeV (read from the file names).

Only 3 nuisances for luminosities are kept.

To run `combine` on these workspaces, you need `combine_v9` with CMSSW_11_3_4:
```
cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scramv1 b -j 4
```
The datacards are only with 3 luminosity uncertainties and 4 lepton energy correction uncertainties. I was intending to have only the luminosity uncertainties but somehow if the workspace doesn't contain any shape uncertainties, it fails when creating the pseudo-asimove datasets for `AsymptoticLimits`. However, if one keeps the shape uncertainties and freeze them when running `combine`, no error would occur.

The worspace is built based on the physics model in `../h4l_highmass/HighMass.py` (in principle it's not needed for running `combine` on the workspaces). There is one overal signal strength r, and a `f_vbf` representing the fraction of VBF production, which can be left floating, or frozen at 0 or 1 to have pure ggF or VBF production. The interference is multiplied by $\sqrt{r}$, or specifically $\text{sign}(r)\sqrt{|r|}$.

An example of running `AsymptoticLimits`:
```
combine -M AsymptoticLimits workspace_M3000_W10_test.root -m 3000 --setParameters f_vbf=0,f_int=1 --freezeParameters f_vbf,f_int,rate_ggHint,rate_VBFHint,CMS_res_e,CMS_res_m,CMS_scale_e,CMS_scale_m  --cminDefaultMinimizerStrategy=0 --cminFallback Minuit2,0:0.01 --cminFallback Minuit,0:0.001 --minosAlgo=stepping --X-rtd TMCSO_AdaptivePseudoAsimov=10 -n .M3000_W10_test -v 1
```
As you can see, `f_vbf` is set to be 0 (ggF production), `f_int` is set to be 1 such that we include the interference processes, and they are all frozen. The `rate_ggHint` and `rate_VBFHint` are for the negative part of the interferences, their values are always -1, and should always be frozen. Besides, shape uncertainties `CMS_res_e,CMS_res_m,CMS_scale_e,CMS_scale_m` are frozen for simplicity. It may takes ~ 1 minutes to run.

An example of running `HybridNew`:
```
combine workspace_M3000_W10_test.root -M HybridNew --frequentist --LHCmode LHC-limits --rMin 0 --rMax 1 --rAbsAcc 0 -T 500 --saveToys --saveHybridResult --cminDefaultMinimizerStrategy 0 --plot=scan_M3000_W10_test.png --setParameters f_vbf=0,f_int=1 --freezeParameters f_vbf,f_int,rate_ggHint,rate_VBFHint,CMS_res_e,CMS_res_m,CMS_scale_e,CMS_scale_m -m 3000 -n .M3000_W10_test -v 1
```
Similarly, always freeze `f_vbf,f_int,rate_ggHint,rate_VBFHint,CMS_res_e,CMS_res_m,CMS_scale_e,CMS_scale_m`. The options can be changed and debugged. Somehow it doesn't give a valid result, but it's possible to generate toys and check the test statistic with `--singlePoint`.