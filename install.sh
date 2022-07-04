source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700

scramv1 project CMSSW CMSSW_10_6_26
cd CMSSW_10_6_26/src/
cmsenv

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