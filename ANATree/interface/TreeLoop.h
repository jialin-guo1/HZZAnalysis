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
  TreeLoop(TString inputfile,TString outputfile);
  ~TreeLoop();

  void setMatrixElementList(std::vector<std::string> const& MElist, bool const& isGen);
  void setMatrixElementListFromFile(std::string fname, std::string const& MElistTypes, bool const& isGen); // MElistTypes is comman-separated
  void Loop();
  void setTree();
  void findZ1LCandidate();
  void findZ2JCandidata();
  void find4lCandidate();
  void findZ2MergedCandidata();


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
  // Output file, Saved Events Trees
  TFile *outfile;
  TTree *passedEventsTree_All;


  //menber object
  bool foundZ1LCandidate;
  bool foundZ2JCandidate;
  bool foundZ2MergedCandidata;
  bool found4lCandidate;

  bool foundresolvedOnly;
  bool foundmergedOnly;
  bool foundresolvedCombine;
  bool foundmergedCombine;
  bool passedfullresolved;
  bool passedfullmerged;

  int lep_Z1index[2];
  int jet_Z1index[2];
  int lep_Hindex[4];
  int merged_Z1index;

  double mass2jet, pt2jet;
  double mass2l, pt2l;
  double massmerged, ptmerged;
  float mass2l2jet, mass2lj;
  int nsubjet;

  vector<double>  associatedjet_pt,associatedjet_eta,associatedjet_phi,associatedjet_mass;


  float particleNetZvsQCD;

  //cut table
  int passed_trig = 0;
  int passed_n_2leps = 0;
  int passed_flavor_charge = 0;
  int passed_lepZpt_40_25 = 0;
  int passed_dR_lilj0point2 = 0;
  int passed_Mll_4 = 0;
  int passed_lepisolation = 0;
  int passed_leptightID = 0;
  int passed_lepZmass40_180 = 0;
  int passed_lepZ = 0;

  int passed_n_2ak4jets = 0;
  int passed_jetpt30 = 0;
  int passed_jeteta2opint4 = 0;
  int passed_lepclean = 0;
  int passed_dijetpt100 = 0;
  int passed_ak4jetZm_40_180 = 0;

  int passed_nmergedjets_lepclean = 0;
  int passed_mergedjetsPt200 = 0;
  int passed_mergedjetEta2opint4 = 0;
  int passed_mergedmass_40_180 = 0;
  int passed_particleNetZvsQCD0opint9 = 0;

  int passed_resovedonlyHiggs = 0;
  int passed_MergedolonlyHiggs = 0;
  int passed_combinHiggs = 0;
  int passed_combineMerged = 0;
  int passed_combineResolved = 0;
  int passed_fullmerged = 0;
  int passed_fullresolved = 0;



  //KD
  float KD_jjVBF;
  float KD_jVBF;

  TTreeReaderArray<int> *lep_id, *lep_tightId;
  TTreeReaderArray<int> *mergedjet_nsubjet;
  TTreeReaderArray<double> *lepFSR_pt, *lepFSR_eta, *lepFSR_phi, *lepFSR_mass;
  TTreeReaderArray<double> *lep_pt, *lep_eta, *lep_phi, *lep_mass;
  TTreeReaderArray<double> *jet_pt, *jet_eta, *jet_phi, *jet_mass;
  TTreeReaderArray<float> *lep_RelIsoNoFSR, *mergedjet_pt, *mergedjet_eta, *mergedjet_phi, *mergedjet_subjet_softDropMass;
  TTreeReaderArray<float> *mergedjet_Net_Xbb_de, *mergedjet_Net_Xcc_de, *mergedjet_Net_Xqq_de;
  TTreeReaderArray<vector<float>> *mergedjet_subjet_pt, *mergedjet_subjet_eta, *mergedjet_subjet_phi,*mergedjet_subjet_mass;
  TTreeReaderValue<bool> *passedTrig;

  //Setting(those setting will be moved to a independent class later)
  double isoCutMu = 0.35, isoCutEl = 0.35;
  int leadingPtCut = 40;
  int subleadingPtCut = 25;
  int dijetPtCut = 100;
  double mZ1Low = 40.0;
  double mZ1High = 180;
  double mZ2Low = 12.0;
  double mZ2High = 120.0;
  double m4lLowCut = 70.0;
  double Zmass = 91.1876;
  bool verbose = false;
  bool doMela = true;



};

#endif
