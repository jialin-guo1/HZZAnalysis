#ifndef TREELOOP_H
#define TREELOOP_H

#include <vector>
#include <cmath>
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

#include "FWCore/ParameterSet/interface/FileInPath.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"

using namespace std;
using namespace IvyStreamHelpers;

class TreeLoop : public IvyBase
//class TreeLoop
{
public:
  TreeLoop(TString inputfile,TString outputfile, string year, string melafile);
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
  void SetGen();
  void initialize();
  void SetMEsFile(string melafile);
  void SetCrossSection(TString inputfile);


protected:
  int tempyear= 2016;
  string jecUncFile_ = "";
  vector<string> uncSources {};
  vector<JetCorrectionUncertainty*> ak4splittedUncerts_;
  vector<JetCorrectionUncertainty*> ak8splittedUncerts_;
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
  bool foundZ1LCandidate, foundZ1LCandidate_up, foundZ1LCandidate_dn;
  bool foundZ2JCandidate, foundZ2JCandidate_up, foundZ2JCandidate_dn;
  bool foundZ2MergedCandidata, foundZ2MergedCandidata_up, foundZ2MergedCandidata_dn;
  bool found4lCandidate;
  bool found2lepCandidate;
  bool foundTTCRCandidate;

  bool foundresolvedOnly;
  bool foundmergedOnly;
  bool foundresolvedCombine;
  bool foundmergedCombine;
  bool passedfullresolved;
  bool passedfullmerged;
  bool passedNassociated_jj;
  bool passedNassociated_J;
  bool isEE;
  bool isMuMu;

  bool passedGENH;

  float EventWeight, GenWeight, PileupWeight, PrefiringWeight,SumWeight, CrossSectionWeight=1.0;
  float EventWeight_up, EventWeight_dn;
  float xsec = 1.0;
  Long64_t nentries;

  ULong64_t run,event,lumiSect;

  double lep_1_pt, lep_1_eta, lep_1_phi, lep_1_mass;
  double lep_2_pt, lep_2_eta, lep_2_phi, lep_2_mass;

  double lep_1_pt_up, lep_1_eta_up, lep_1_phi_up, lep_1_mass_up;
  double lep_2_pt_up, lep_2_eta_up, lep_2_phi_up, lep_2_mass_up;

  double lep_1_pt_dn, lep_1_eta_dn, lep_1_phi_dn, lep_1_mass_dn;
  double lep_2_pt_dn, lep_2_eta_dn, lep_2_phi_dn, lep_2_mass_dn;

  int lep_Z1index[2];
  int jet_Z1index[2], jet_Z1index_up[2], jet_Z1index_dn[2];
  int jet_Z1index_mass_bais[2];
  int lep_Hindex[4];
  int Nleptons, Ntightleptons;
  int n_jets, n_mergedjets;
  int jet_1_btag, jet_1_btag_up, jet_1_btag_dn;
  int jet_2_btag, jet_2_btag_up, jet_2_btag_dn;
  float jet_1_deepbtag, jet_1_deepbtag_up, jet_1_deepbtag_dn;
  float jet_2_deepbtag, jet_2_deepbtag_up, jet_2_deepbtag_dn;
  int jet_1_hadronflavor, jet_1_partonflavor;
  int jet_2_hadronflavor, jet_2_partonflavor;
  int merged_Z1index, merged_Z1index_up, merged_Z1index_dn;
  double jet_1_pt, jet_1_eta, jet_1_phi, jet_1_mass;
  double jet_2_pt, jet_2_eta, jet_2_phi, jet_2_mass;
  double jet_1_pt_up, jet_1_eta_up, jet_1_phi_up, jet_1_mass_up;
  double jet_2_pt_up, jet_2_eta_up, jet_2_phi_up, jet_2_mass_up;
  double jet_1_pt_dn, jet_1_eta_dn, jet_1_phi_dn, jet_1_mass_dn;
  double jet_2_pt_dn, jet_2_eta_dn, jet_2_phi_dn, jet_2_mass_dn;

  double jet_1_jesunc_split_Total,    jet_1_jesunc_split_Abs,        jet_1_jesunc_split_Abs_year; 
  double jet_1_jesunc_split_BBEC1,    jet_1_jesunc_split_BBEC1_year, jet_1_jesunc_split_EC2; 
  double jet_1_jesunc_split_EC2_year, jet_1_jesunc_split_FlavQCD,    jet_1_jesunc_split_HF; 
  double jet_1_jesunc_split_HF_year,  jet_1_jesunc_split_RelBal,     jet_1_jesunc_split_RelSample_year;
  double jet_2_jesunc_split_Total,    jet_2_jesunc_split_Abs,        jet_2_jesunc_split_Abs_year; 
  double jet_2_jesunc_split_BBEC1,    jet_2_jesunc_split_BBEC1_year, jet_2_jesunc_split_EC2; 
  double jet_2_jesunc_split_EC2_year, jet_2_jesunc_split_FlavQCD,    jet_2_jesunc_split_HF; 
  double jet_2_jesunc_split_HF_year,  jet_2_jesunc_split_RelBal,     jet_2_jesunc_split_RelSample_year;

  double jetpt_1_jesup_split_Total,      jetpt_1_jesup_split_Abs, jetpt_1_jesup_split_Abs_year, jetpt_1_jesup_split_BBEC1;
  double jetpt_1_jesup_split_BBEC1_year, jetpt_1_jesup_split_EC2, jetpt_1_jesup_split_EC2_year;
  double jetpt_1_jesup_split_FlavQCD,    jetpt_1_jesup_split_HF,  jetpt_1_jesup_split_HF_year,  jetpt_1_jesup_split_RelBal;
  double jetpt_1_jesup_split_RelSample_year;
  double jetpt_2_jesup_split_Total,      jetpt_2_jesup_split_Abs, jetpt_2_jesup_split_Abs_year, jetpt_2_jesup_split_BBEC1;
  double jetpt_2_jesup_split_BBEC1_year, jetpt_2_jesup_split_EC2, jetpt_2_jesup_split_EC2_year;
  double jetpt_2_jesup_split_FlavQCD,    jetpt_2_jesup_split_HF,  jetpt_2_jesup_split_HF_year,  jetpt_2_jesup_split_RelBal;
  double jetpt_2_jesup_split_RelSample_year;

  double jetpt_1_jesdn_split_Total,      jetpt_1_jesdn_split_Abs, jetpt_1_jesdn_split_Abs_year, jetpt_1_jesdn_split_BBEC1;
  double jetpt_1_jesdn_split_BBEC1_year, jetpt_1_jesdn_split_EC2, jetpt_1_jesdn_split_EC2_year;
  double jetpt_1_jesdn_split_FlavQCD,    jetpt_1_jesdn_split_HF,  jetpt_1_jesdn_split_HF_year,  jetpt_1_jesdn_split_RelBal;
  double jetpt_1_jesdn_split_RelSample_year;
  double jetpt_2_jesdn_split_Total,      jetpt_2_jesdn_split_Abs, jetpt_2_jesdn_split_Abs_year, jetpt_2_jesdn_split_BBEC1;
  double jetpt_2_jesdn_split_BBEC1_year, jetpt_2_jesdn_split_EC2, jetpt_2_jesdn_split_EC2_year;
  double jetpt_2_jesdn_split_FlavQCD,    jetpt_2_jesdn_split_HF,  jetpt_2_jesdn_split_HF_year,  jetpt_2_jesdn_split_RelBal;
  double jetpt_2_jesdn_split_RelSample_year;
  vector<int> jet_btag;


  double mergedjet_jesunc_split_Total,    mergedjet_jesunc_split_Abs,        mergedjet_jesunc_split_Abs_year; 
  double mergedjet_jesunc_split_BBEC1,    mergedjet_jesunc_split_BBEC1_year, mergedjet_jesunc_split_EC2; 
  double mergedjet_jesunc_split_EC2_year, mergedjet_jesunc_split_FlavQCD,    mergedjet_jesunc_split_HF; 
  double mergedjet_jesunc_split_HF_year,  mergedjet_jesunc_split_RelBal,     mergedjet_jesunc_split_RelSample_year;

  double mergedjetpt_jesup_split_Total,    mergedjetpt_jesup_split_Abs,        mergedjetpt_jesup_split_Abs_year; 
  double mergedjetpt_jesup_split_BBEC1,    mergedjetpt_jesup_split_BBEC1_year, mergedjetpt_jesup_split_EC2; 
  double mergedjetpt_jesup_split_EC2_year, mergedjetpt_jesup_split_FlavQCD,    mergedjetpt_jesup_split_HF; 
  double mergedjetpt_jesup_split_HF_year,  mergedjetpt_jesup_split_RelBal,     mergedjetpt_jesup_split_RelSample_year;

  double mergedjetpt_jesdn_split_Total,    mergedjetpt_jesdn_split_Abs,        mergedjetpt_jesdn_split_Abs_year; 
  double mergedjetpt_jesdn_split_BBEC1,    mergedjetpt_jesdn_split_BBEC1_year, mergedjetpt_jesdn_split_EC2; 
  double mergedjetpt_jesdn_split_EC2_year, mergedjetpt_jesdn_split_FlavQCD,    mergedjetpt_jesdn_split_HF; 
  double mergedjetpt_jesdn_split_HF_year,  mergedjetpt_jesdn_split_RelBal,     mergedjetpt_jesdn_split_RelSample_year;

  double mass2jet_up, mass2jet_dn, pt2jet_up, pt2jet_dn;
  double mass2jet, pt2jet;
  double mass2jet_mass_bais, pt2jet_mass_bais, mass2l2jet_mass_bais;
  double mass2l, pt2l;
  double massmerged,massmerged_up, massmerged_dn;
  double ptmerged, ptmerged_up, ptmerged_dn;
  double etamerged, phimerged;
  float mass2l2jet, mass2lj;
  float mass2l2jet_up, mass2l2jet_dn, mass2lj_up, mass2lj_dn;
  int nsubjet;

  float particleNetZvsQCD, particleNetZvsQCD_up, particleNetZvsQCD_dn;
  float particleNetZbbvslight, particleNetZbbvslight_up, particleNetZbbvslight_dn;
  float particleNetXbbvsQCD, particleNetXbbvsQCD_up, particleNetXbbvsQCD_dn;

  vector<double>  associatedjetjj_pt,associatedjetjj_eta,associatedjetjj_phi,associatedjetjj_mass;
  vector<double>  associatedjetJ_pt,associatedjetJ_eta,associatedjetJ_phi,associatedjetJ_mass;
  vector<int> associatedjetsjj_index, associatedjetsJ_index;

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
  int n_match_vbfquarks_to_recojet = 0;
  int n_match_vbfquarks_to_genjet = 0;

  double DR_merged_VBF1_matched, DR_merged_VBF2_matched;
  vector<double> DR_merged_asccoiacted;
  vector<double> DR_selectedleps_asccoiacted;
  bool passedmatchtruthVBF_jj;
  bool passedmatchtruthVBF_J;
  double time_associatedjetjj_eta;
  double time_associatedjetJ_eta;

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
  float KD_jjVBF, KD_jjVBF_up, KD_jjVBF_dn;
  float KD_jVBF;
  float KD_JJVBF, KD_JVBF_up, KD_JVBF_dn;
  float KD_JVBF;
  float KD_ZJ, KD_ZJ_up, KD_ZJ_dn;
  float KD_Zjj, KD_Zjj_up, KD_Zjj_dn;


  //=================================================================================================================
  //=====================================read from input file========================================================
  //=================================================================================================================
  TTreeReaderArray<int> *lep_id, *lep_tightId;
  TTreeReaderArray<int> *mergedjet_nsubjet;
  TTreeReaderArray<double> *lepFSR_pt, *lepFSR_eta, *lepFSR_phi, *lepFSR_mass, *lep_pterr;
  TTreeReaderArray<double> *lep_pt, *lep_eta, *lep_phi, *lep_mass;
  TTreeReaderArray<double> *jet_pt, *jet_eta, *jet_phi, *jet_mass;
  TTreeReaderArray<int> *jet_isbtag;
  TTreeReaderArray<float> *jet_deepBtag;
  TTreeReaderArray<float> *jet_bTagEffi;
  TTreeReaderArray<float> *lep_RelIsoNoFSR, *mergedjet_pt, *mergedjet_eta, *mergedjet_phi, *mergedjet_subjet_softDropMass;
  TTreeReaderArray<float> *mergedjet_Net_Xbb_de, *mergedjet_Net_Xcc_de, *mergedjet_Net_Xqq_de;
  TTreeReaderArray<float> *mergedjet_Net_QCDbb_de, *mergedjet_Net_QCDcc_de, *mergedjet_Net_QCDother_de, *mergedjet_Net_QCDb_de, *mergedjet_Net_QCDc_de;
  TTreeReaderArray<vector<float>> *mergedjet_subjet_pt, *mergedjet_subjet_eta, *mergedjet_subjet_phi,*mergedjet_subjet_mass;
  TTreeReaderValue<bool> *passedTrig;
  TTreeReaderValue<float> *eventWeight, *genWeight, *pileupWeight, *prefiringWeight;
  TTreeReaderValue<ULong64_t> *Run, *Event, *LumiSect;
  TTreeReaderValue<float> *met, *met_phi;
  //jer and jec
  TTreeReaderArray<float> *mergedjet_jerup_pt,*mergedjet_jerdn_pt, *mergedjet_jer_pterr, *mergedjet_jer_phierr;
  TTreeReaderArray<float> *mergedjet_jesup_pt,*mergedjet_jesup_eta,*mergedjet_jesup_phi,*mergedjet_jesup_mass;
  TTreeReaderArray<float> *mergedjet_jesdn_pt,*mergedjet_jesdn_eta,*mergedjet_jesdn_phi,*mergedjet_jesdn_mass;
  TTreeReaderArray<double> *jet_jesup_pt, *jet_jesup_eta, *jet_jesup_phi, *jet_jesup_mass, *jet_jesdn_pt, *jet_jesdn_eta, *jet_jesdn_phi, *jet_jesdn_mass;
  TTreeReaderArray<double> *jet_jerup_pt, *jet_jerup_eta, *jet_jerup_phi, *jet_jerup_mass, *jet_jerdn_pt, *jet_jerdn_eta, *jet_jerdn_phi, *jet_jerdn_mass;

  //GEN
  TTreeReaderArray<double> *GEN_Zq_pt, *GEN_Zq_eta, *GEN_Zq_phi, *GEN_Zq_mass, *GEN_q_pt, *GEN_q_eta, *GEN_q_phi, *GEN_q_mass, *GENjet_pt, *GENjet_eta, *GENjet_phi, *GENjet_mass;
  TTreeReaderArray<int> *GEN_Zq_id, *GEN_q_id, *GEN_q_status, *GEN_q_Momid, *GEN_q_MomMomid, *GEN_q_nDaughters;
  TTreeReaderArray<vector<int>> *GEN_qdau_id, *GEN_qdau_status;
  TTreeReaderArray<vector<double>> *GEN_qdau_pt, *GEN_qdau_eta, *GEN_qdau_phi, *GEN_qdau_mass;
  TTreeReaderArray<double> *GEN_VBF_pt, *GEN_VBF_eta, *GEN_VBF_phi, *GEN_VBF_mass;
  TTreeReaderArray<float> *lep_dataMC, *lep_dataMCErr;
  TTreeReaderArray<int> *mergedjet_nbHadrons, *mergedjet_ncHadrons;
  TTreeReaderArray<int> *jet_hadronFlavour, *jet_partonFlavour;
  TTreeReaderArray<double> *GENH_status, *GENH_mass, *GENH_pt, *GENH_eta, *GENH_phi;
  TTreeReaderArray<int> *GENH_isHard;


  //Setting(those setting will be moved to a independent class later)
  double isoCutMu = 0.35, isoCutEl = 0.35;
  int leadingPtCut = 40;
  int subleadingPtCut = 25;
  int dijetPtCut = 100;
  double mZ1Low = 60.0;
  double mZ1High = 120;
  double mZ2Low = 40;
  double mZ2High = 180;
  double m4lLowCut = 70.0;
  double Zmass = 91.1876;
  bool verbose = false;
  bool doMela = true;
  bool isMC = false;
  bool isData = false;



};

#endif
