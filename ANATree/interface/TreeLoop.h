#ifndef TREELOOP_H
#define TREELOOP_H

#include <vector>
#include <string>
#include "IvyBase.h"
#include "DataFormats/Math/interface/deltaR.h"
#include <IvyFramework/IvyAutoMELA/interface/IvyMELAHelpers.h>
#include <IvyFramework/IvyDataTools/interface/HostHelpersCore.h>
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"
#include "TFile.h"
#include "TString.h"
//#include <ROOT/RDataFrame.hxx>

class TreeLoop : public IvyBase
//class TreeLoop
{
public:
  TreeLoop(TString inputfile);
  ~TreeLoop();

  void setMatrixElementList(std::vector<std::string> const& MElist, bool const& isGen);
  void setMatrixElementListFromFile(std::string fname, std::string const& MElistTypes, bool const& isGen); // MElistTypes is comman-separated
  void Loop();
  void setTree();
  void findZ1LCandidate();
  void findZ2JCandidata();


protected:
  int year= 2016;
  //TString treeName = "Ana/passedEvents";
  // ME lists
  std::vector<std::string> lheMElist;
  std::vector<std::string> recoMElist;
  IvyMELAHelpers::GMECBlock MEblock;

  //input file
  TFile *oldfile;
  TTree *oldtree;
  TTreeReader *myreader;
  // Output tree, Saved Events Trees
  TTree *passedEventsTree_All;

  //menber object
  bool foundZ1LCandidate;
  bool foundZ2JCandidate;

  int lep_Z1index[2];

  TTreeReaderArray<int> *lep_id, *lep_tightId;
  TTreeReaderArray<double> *lepFSR_pt, *lepFSR_eta, *lepFSR_phi, *lepFSR_mass, *lep_RelIsoNoFSR;
  TTreeReaderArray<double> *lep_pt, *lep_eta, *lep_phi, *lep_mass;
  TTreeReaderArray<double> *jet_pt, *jet_eta, *jet_phi, *jet_mass;




};

#endif
