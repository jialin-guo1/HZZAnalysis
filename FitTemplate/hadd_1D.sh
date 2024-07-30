cd Files
for year in 2016postAPV
    do
    for channel in 2e 2mu 2l
        do
        hadd -f Template1D_spin0_${channel}_${year}.root Template1D_spin0_${channel}_resolved_${year}.root Template1D_spin0_${channel}_merged_${year}.root

        mv Template1D_spin0_${channel}_${year}.root /cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/FitTemplate/Files/outfiles
        done
    done
