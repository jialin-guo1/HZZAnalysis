# This is HZZAnalysis based on Ntuple

## To install V2
```shell
wget https://github.com/jialin-guo1/HZZAnalysis/blob/master/install.sh
chmod +x install.sh
./install.sh
```
## To Run Siganl Model Only
### NOTE: By running this install, you will be not able to run skimming proccess
### 1.Install
```shell
wget https://github.com/jialin-guo1/HZZAnalysis/blob/master/install_SigMod.sh
chmod +x install_SigMod.sh
./install_SigMod.sh
```
### 2.To reshape signal model 
```shell
cd $CMSSW_BASE/src/HZZAnalysis/SignalModel
python MakeShape_v2.py -y 2018 -s sig
```
### 3.To Fit SignalModel
```shell
python FitShape.py -y 2018
```
### all files what you need are already there

## To install
### Setup CMSSW env
```shell
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_6_26
cd CMSSW_10_6_26
cmsenv
```
### include packages
```shell
git clone git@github.com:JHUGen/JHUGenMELA.git
cd JHUGenMELA
./setup.sh -j 8
cd ..

git clone git@github.com:MELALabs/MelaAnalytics.git
cd MelaAnalytics
./setup.sh -j 8
cd ..

git clone git@github.com:IvyFramework/IvyDataTools.git IvyFramework/IvyDataTools
git clone git@github.com:IvyFramework/IvyAutoMELA.git IvyFramework/IvyAutoMELA
git clone git@github.com:jialin-guo1/HZZAnalysis.git
scram b -j 8 
