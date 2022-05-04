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
  void SetVBFGen();
  void initialize();
  void SetMEsFile();


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

  //=================================================================================================
  //===============================output Tree branch================================================
  //=================================================================================================
  //menber object
  bool foundZ1LCandidate;
  bool foundZ2JCandidate;
  bool foundZ2MergedCandidata;
  bool found4lCandidate;
  bool found2lepCandidate;
  bool foundTTCRCandidate;

  bool foundresolvedOnly;
  bool foundmergedOnly;
  bool foundresolvedCombine;
  bool foundmergedCombine;
  bool passedfullresolved;
  bool passedfullmerged;
  bool passedNassociated;
  bool isEE;
  bool isMuMu;

  bool passedGENH;

  float EventWeight, GenWeight, PileupWeight, PrefiringWeight,SumWeight;

  ULong64_t run,event,lumiSect;

  int lep_Z1index[2];
  int jet_Z1index[2];
  int lep_Hindex[4];
  int merged_Z1index;

  double mass2jet, pt2jet;
  double mass2l, pt2l;
  double massmerged, ptmerged;
  float mass2l2jet, mass2lj;
  int nsubjet;

  float particleNetZvsQCD, particleNetZbbvslight;

  vector<double>  associatedjet_pt,associatedjet_eta,associatedjet_phi,associatedjet_mass;
  vector<int> associatedjets_index;

  float Met,Met_phi;

  //out Gen branchs
  bool isbjet,iscjet,islightjet;
  double GEN_H1_pt,GEN_H1_eta,GEN_H1_phi,GEN_H1_mass,GEN_H2_pt,GEN_H2_eta,GEN_H2_phi,GEN_H2_mass,GEN_DR_H1_Mom,GEN_DR_H2_Mom;
  double GEN_H1_Mom_pt,GEN_H1_Mom_eta,GEN_H1_Mom_phi,GEN_H1_Mom_mass,GEN_H2_Mom_pt,GEN_H2_Mom_eta,GEN_H2_Mom_phi,GEN_H2_Mom_mass;

  vector<double> GEN_H1_Bro_pt,GEN_H1_Bro_eta,GEN_H1_Bro_phi,GEN_H1_Bro_mass,GEN_DR_H1_Bro,GEN_DR_H1Mom_Bro;
  vector<double> GEN_H2_Bro_pt,GEN_H2_Bro_eta,GEN_H2_Bro_phi,GEN_H2_Bro_mass,GEN_DR_H2_Bro,GEN_DR_H2Mom_Bro,GEN_DR_Bro12;
  vector<double> GEN_DEta_H1_Bro,GEN_DEta_H1Mom_Bro,GEN_DEta_H2_Bro,GEN_DEta_H2Mom_Bro,GEN_DEta_Bro12;
  vector<double> DR_merged_GenZ,DR_merged_GenZ_matched,DR_resovled1_GenZ,DR_resovled2_GenZ,DR_resovled2_GenZ_matched,DR_resovled1_GenZ_matched;
  vector<double> DR_associatedjet1_GenZ,DR_associatedjet2_GenZ,DR_associatedjet1_GenZ_matched,DR_associatedjet2_GenZ_matched;

  bool matched_merged_GEN_Z,matched_resovled1_GEN_Z,matched_resovled2_GEN_Z,matched_resovled_GEN_Z,matched_resovledone_GEN_Z;
  bool matched_associatedjet1_GEN_Z,matched_associatedjet2_GEN_Z,matched_associatedjet_GEN_Z,matched_associatedjetone_GEN_Z;

  //VBF quarks
  double GEN_associated1_pt,GEN_associated1_eta,GEN_associated1_phi,GEN_associated1_mass;
  double GEN_associated2_pt,GEN_associated2_eta,GEN_associated2_phi,GEN_associated2_mass;
  double GEN_associated12_mass,GEN_associated12_Deta;

  double GEN_quark1_match_pt,GEN_quark1_match_eta,GEN_quark1_match_phi,GEN_quark1_match_mass;
  double GEN_quark2_match_pt,GEN_quark2_match_eta,GEN_quark2_match_phi,GEN_quark2_match_mass;
  double GEN_quark12_match_mass;
  bool passedGenquarkMatch;

  double Reco_quark1_match_pt,Reco_quark1_match_eta,Reco_quark1_match_phi,Reco_quark1_match_mass;
  double Reco_quark2_match_pt,Reco_quark2_match_eta,Reco_quark2_match_phi,Reco_quark2_match_mass;
  double Reco_quark12_match_mass, Reco_quark12_match_DEta;
  bool passedRecoquarkMatch;
  int match2_recoindex, match1_recoindex;

  double DR_merged_VBF1_matched, DR_merged_VBF2_matched;
  vector<double> DR_merged_asccoiacted;
  vector<double> DR_selectedleps_asccoiacted;
  bool passedmatchtruthVBF;
  double time_associatedjet_eta;

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

  //=================================================================================================================
  //=====================================read from input file========================================================
  //=================================================================================================================
  TTreeReaderArray<int> *lep_id, *lep_tightId;
  TTreeReaderArray<int> *mergedjet_nsubjet;
  TTreeReaderArray<double> *lepFSR_pt, *lepFSR_eta, *lepFSR_phi, *lepFSR_mass;
  TTreeReaderArray<double> *lep_pt, *lep_eta, *lep_phi, *lep_mass;
  TTreeReaderArray<double> *jet_pt, *jet_eta, *jet_phi, *jet_mass;
  TTreeReaderArray<float> *lep_RelIsoNoFSR, *mergedjet_pt, *mergedjet_eta, *mergedjet_phi, *mergedjet_subjet_softDropMass;
  TTreeReaderArray<float> *mergedjet_Net_Xbb_de, *mergedjet_Net_Xcc_de, *mergedjet_Net_Xqq_de;
  TTreeReaderArray<vector<float>> *mergedjet_subjet_pt, *mergedjet_subjet_eta, *mergedjet_subjet_phi,*mergedjet_subjet_mass;
  TTreeReaderValue<bool> *passedTrig;
  TTreeReaderValue<float> *eventWeight, *genWeight, *pileupWeight, *prefiringWeight;
  TTreeReaderValue<ULong64_t> *Run, *Event, *LumiSect;
  TTreeReaderValue<float> *met, *met_phi;

  //GEN
  TTreeReaderArray<double> *GEN_Zq_pt, *GEN_Zq_eta, *GEN_Zq_phi, *GEN_Zq_mass, *GEN_q_pt, *GEN_q_eta, *GEN_q_phi, *GEN_q_mass, *GENjet_pt, *GENjet_eta, *GENjet_phi, *GENjet_mass;
  TTreeReaderArray<int> *GEN_Zq_id, *GEN_q_id, *GEN_q_status, *GEN_q_Momid, *GEN_q_MomMomid, *GEN_q_nDaughters;
  TTreeReaderArray<vector<int>> *GEN_qdau_id, *GEN_qdau_status;
  TTreeReaderArray<vector<double>> *GEN_qdau_pt, *GEN_qdau_eta, *GEN_qdau_phi, *GEN_qdau_mass;
  TTreeReaderArray<double> *GEN_VBF_pt, *GEN_VBF_eta, *GEN_VBF_phi, *GEN_VBF_mass;
  TTreeReaderArray<float> *lep_dataMC;
  TTreeReaderArray<int> *mergedjet_nbHadrons, *mergedjet_ncHadrons;


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
  bool isMC = false;
  bool isData = false;



};

#endif
