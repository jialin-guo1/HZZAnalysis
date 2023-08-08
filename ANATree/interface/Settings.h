#ifndef Settings_h
#define Settings_h
#include <iostream>
#include <string>

// options
struct Options {
    bool tree = false;
    TString infile = nullptr;
    TString outfile = nullptr;
    TString input_file_path = "${CMSSW_BASE}/src/HZZAnalysis/ANATree/testfiles/";
    TString output_file_path = "${CMSSW_BASE}/src/HZZAnalysis/fileout/";
    std::string year = "2018";
};

struct setting{
  TString outfile_path = "${CMSSW_BASE}/src/HZZAnalysis";
  double isoCutMu = 0.35;
  double isoCutEl = 0.35;
  int leadingPtCut = 40;
  int subleadingPtCut = 25;
  int dijetPtCut = 100;
  double mZ1Low = 40;
  double mZ1High = 180;
  double Zmass = 91.1876;
  bool verbose = true;
  bool doMela = true;
};


#endif
