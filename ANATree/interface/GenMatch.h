#ifndef GENMATCH_H
#define GENMATCH_H

#include <vector>
#include <string>
#include <typeinfo>
#include "DataFormats/Math/interface/deltaR.h"
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"
#include "TFile.h"
#include "TString.h"
#include "Settings.h"

using namespace std;

class GenMatch
{
public:
  GenMatch(TString inputfile,TString outputfile);
  ~GenMatch();

  void Loop();

protected:
  //input file
  TFile *oldfile;
  TTree *oldtree;
  TTreeReader *myreader;
  // Output file, Saved Events Trees
  TFile *outfile;
  TTree *passedEventsTree_All;

};

#endif
