#ifndef TREELOOP_H
#define TREELOOP_H

#include <vector>
#include <string>
#include <typeinfo>
#include "IvyBase.h"
#include "DataFormats/Math/interface/deltaR.h"
#include <IvyFramework/IvyAutoMELA/interface/IvyMELAHelpers.h>
#include <IvyFramework/IvyDataTools/interface/HostHelpersCore.h>
#include "TTreeReader.h"
#include "TTreeReaderValue.h"
#include "TTreeReaderArray.h"
#include "TFile.h"
#include "TString.h"
#include "DiscriminantClasses.h"
//#include <ROOT/RDataFrame.hxx>

using namespace std;
using namespace IvyStreamHelpers;

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
  void find4lCandidate();


protected:
  int year= 2016;
  //TString treeName = "Ana/passedEvents";
  // ME lists
  std::vector<std::string> lheMElist;
  std::vector<std::string> recoMElist;
  IvyMELAHelpers::GMECBlock MEblock;
  std::map<TString,float> ME_Kfactor_values;

  //input file
  TFile *oldfile;
  TTree *oldtree;
  TTreeReader *myreader;
  // Output file, Saved Events Trees
  TFile *outfile;
  TTree *passedEventsTree_All;


  //menber object
  bool foundZ1LCandidate;
  bool foundZ2JCandidate;
  bool found4lCandidate;

  int lep_Z1index[2];
  int jet_Z1index[2];
  int lep_Hindex[4];

  double mass2jet, pt2jet;
  double mass2l, pt2l;
  double mass2l2jet;

  //KD
  float KD_jjVBF;

  TTreeReaderArray<int> *lep_id, *lep_tightId;
  TTreeReaderArray<double> *lepFSR_pt, *lepFSR_eta, *lepFSR_phi, *lepFSR_mass;
  TTreeReaderArray<double> *lep_pt, *lep_eta, *lep_phi, *lep_mass;
  TTreeReaderArray<double> *jet_pt, *jet_eta, *jet_phi, *jet_mass;
  TTreeReaderArray<float> *lep_RelIsoNoFSR;
  TTreeReaderValue<bool> *passedTrig;

  //Setting(those setting will be moved to a independent class later)
  double isoCutMu = 0.35, isoCutEl = 0.35;
  int leadingPtCut = 40;
  int subleadingPtCut = 25;
  int dijetPtCut = 100;
  double mZ1Low = 40;
  double mZ1High = 180;
  double Zmass = 91.1876;
  bool verbose = false;
  bool doMela = true;



};

#endif
