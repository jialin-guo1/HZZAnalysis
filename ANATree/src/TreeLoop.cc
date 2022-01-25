#include "TreeLoop.h"

using namespace std;
using namespace IvyStreamHelpers;

//construtor
TreeLoop::TreeLoop(TString inputfile){
  //df = new ROOT:
  oldfile = new TFile(inputfile);
  //TTreeReader yreader = new TTreeReader("Ana/passedEvents",oldfile);
  passedEventsTree_All = new TTree("passedEvents","passedEvents");

  TTreeReader myreader("Ana/passedEvents",oldfile);

}

//destructor
TreeLoop::~TreeLoop(){}

//==============================================================================================================//
void TreeLoop::setMatrixElementList(std::vector<std::string> const& MElist, bool const& isGen){
  IVYout << "BaseTreeLooper::setMatrixElementList: Setting " << (isGen ? "gen." : "reco.") << " matrix elements:" << endl;
  for (auto const& sme:MElist) IVYout << '\t' << sme << endl;
  if (isGen) lheMElist = MElist;
  else recoMElist = MElist;
}

//==============================================================================================================//
void TreeLoop::setMatrixElementListFromFile(std::string fname, std::string const& MElistTypes, bool const& isGen){
  if (MElistTypes==""){
    if (this->verbosity>=MiscUtils::ERROR) IVYerr << "BaseTreeLooper::setMatrixElementListFromFile: The ME list types must be specified." << endl;
    assert(0);
  }
  HostHelpers::ExpandEnvironmentVariables(fname);
  if (!HostHelpers::FileReadable(fname.data())){
    if (this->verbosity>=MiscUtils::ERROR) IVYerr << "BaseTreeLooper::setMatrixElementListFromFile: File " << fname << " is not readable." << endl;
    assert(0);
  }

  std::vector<std::string> MEtypes;
  HelperFunctions::splitOptionRecursive(MElistTypes, MEtypes, ',', true);

  // Read the file and collect the MEs
  std::vector<std::string> MElist;
  ifstream fin;
  fin.open(fname.c_str());
  if (fin.good()){
    bool acceptString = false;
    while (!fin.eof()){
      std::string str_in="";
      getline(fin, str_in);
      HelperFunctions::lstrip(str_in);
      HelperFunctions::lstrip(str_in, "\"\'");
      HelperFunctions::rstrip(str_in); HelperFunctions::rstrip(str_in, ",\"\'");

      if (str_in=="" || str_in.find('#')==0) continue;
      else if (str_in.find(']')!=std::string::npos){
        acceptString = false;
        continue;
      }

      bool isMEline = (str_in.find("Name")!=std::string::npos);
      for (auto const& MEtype:MEtypes){
        if (str_in.find(MEtype)!=std::string::npos){
          isMEline = false;
          acceptString = true;
        }
      }

      if (isMEline && acceptString){
        if (isGen && str_in.find("isGen:1")==std::string::npos){
          if (this->verbosity>=MiscUtils::ERROR) IVYerr << "BaseTreeLooper::setMatrixElementListFromFile: ME string " << str_in << " is not a gen. ME while the acquisition is done for gen. MEs!" << endl;
          continue;
        }
        MElist.push_back(str_in);
      }
    }
  }
  fin.close();

  if (!MElist.empty()) setMatrixElementList(MElist, isGen);
  else{
    //if (this->verbosity>=MiscUtils::ERROR) IVYerr << "BaseTreeLooper::setMatrixElementListFromFile: File " << fname << " does not contain any of the ME types " << MEtypes << "." << endl;
  }
}
//==============================================================================================================//
void TreeLoop::Loop(){

  bool doMela = true;
  if(doMela){
  // Set the MEs
  // ME lists
  setMatrixElementListFromFile(
    "${CMSSW_BASE}/src/HZZAnalysis/ANATree/data/RecoProbabilities.me",
    "AJetsVBFProbabilities_SpinZero_JHUGen,AJetsQCDProbabilities_SpinZero_JHUGen",
    //"AJetsVBFProbabilities_SpinZero_JHUGen,AJetsQCDProbabilities_SpinZero_JHUGen,AJetsVHProbabilities_SpinZero_JHUGen,PMAVJJ_SUPERDIJETMELA",
    false
    );

  }

  // Build the MEs if they are specified
  if (!lheMElist.empty() || !recoMElist.empty()){
  // Set up MELA (done only once inside IvyMELAHelpers)
  IvyMELAHelpers::setupMela(year, 125., MiscUtils::INFO);
  // If there are output trees, set the output trees of the MEblock.
  // Do this before building the branches.
  IVYout << "Setting up ME block output trees..." << endl;
  MEblock.addRefTree(passedEventsTree_All);
  //for (auto const& outtree_:productTreeList){
  //  IVYout << "\t- Extracting valid output trees" << endl;
  //  if (!outtree_) cout << "Output tree is NULL!" << endl;
  //  std::vector<TTree*> const& treelist_ = outtree_->getValidTrees();
  //  IVYout << "\t- Registering " << treelist_.size() << " trees" << endl;
  //  for (auto const& tree_:treelist_) MEblock.addRefTree(passedEventsTree_All);
  //  IVYout << "\t- Done" << endl;
  //}
  // Build the MEs
  IVYout << "Building the MEs..." << endl;
  if (!lheMElist.empty()) this->MEblock.buildMELABranches(lheMElist, true);
  if (!recoMElist.empty()) this->MEblock.buildMELABranches(recoMElist, false);
  }

  //===================start event loop==========================================
  //Long64_t nentries = oldtree->GetEntries();
  //for (Long64_t i=0;i<nentries; i++){
  //}
  setTree();
  while (myreader->Next()) {
    //initialize
    foundZ1LCandidate = false;
    foundZ2JCandidate = false;
    for (int i=0; i<2; ++i) {lep_Z1index[i]=-1;}

    findZ1LCandidate();
    if(foundZ1LCandidate && foundZ2JCandidate){
      if (doMela){

          TLorentzVector p4_ZZ_approx,selectedLep1,selectedLep2,selectedJet1,selectedJet2;
          selectedLep1.SetPtEtaPhiM((*lepFSR_pt)[0],(*lepFSR_eta)[0],(*lep_phi)[0],(*lepFSR_mass)[0]);
          selectedLep2.SetPtEtaPhiM((*lepFSR_pt)[1],(*lepFSR_eta)[1],(*lep_phi)[1],(*lepFSR_mass)[1]);
          selectedJet1.SetPtEtaPhiM((*jet_pt)[0],(*jet_eta)[0],(*jet_phi)[0],(*jet_mass)[0]);
          selectedJet2.SetPtEtaPhiM((*jet_pt)[1],(*jet_eta)[2],(*jet_phi)[3],(*jet_mass)[4]);

          p4_ZZ_approx = selectedLep1+selectedLep2+selectedJet1+selectedJet2;

          SimpleParticleCollection_t daughters;
          daughters.push_back(SimpleParticle_t(lepFSR_ID[0], selectedLep1));
          daughters.push_back(SimpleParticle_t(lepFSR_ID[0], selectedLep2));
          daughters.push_back(SimpleParticle_t(0, selectedJet1));
          daughters.push_back(SimpleParticle_t(0, selectedJet2));

          SimpleParticleCollection_t associated;
          for (auto const& jet:goodJets){

            TLorentzVector thisjet;
            thisjet.SetPtEtaPhiM(jet.pt(),jet.eta(),jet.phi(),jet.mass());
            associated.push_back(SimpleParticle_t(0, thisjet));

          }

          IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
          IvyMELAHelpers::melaHandle->setInputEvent(&daughters, &associated, nullptr, false);
          MEblock.computeMELABranches();
          MEblock.pushMELABranches();

          IvyMELAHelpers::melaHandle->resetInputEvent();
        }
    }
    /* code */
  }
}

void TreeLoop::setTree(){

  lep_id = new TTreeReaderArray<int>(*myreader, "lep_id");
  lepFSR_pt = new TTreeReaderArray<double>(*myreader, "lepFSR_pt");
  lepFSR_eta  = new TTreeReaderArray<double>(*myreader, "lepFSR_eta");
  lepFSR_phi = new TTreeReaderArray<double>(*myreader, "lepFSR_phi");
  lepFSR_mass  = new TTreeReaderArray<double>(*myreader, "lepFSR_mass");
  lep_pt = new TTreeReaderArray<double>(*myreader, "lep_pt");
  lep_eta  = new TTreeReaderArray<double>(*myreader, "lep_eta");
  lep_phi = new TTreeReaderArray<double>(*myreader, "lep_phi");
  lep_mass  = new TTreeReaderArray<double>(*myreader, "lep_mass");
  lep_tightId = new TTreeReaderArray<int>(*myreader, "lep_tightId");
  lep_RelIsoNoFSR = new TTreeReaderArray<double>(*myreader, "lep_RelIsoNoFSR");

  jet_pt = new TTreeReaderArray<double>(*myreader, "jet_pt");
  jet_eta = new TTreeReaderArray<double>(*myreader, "jet_eta");
  jet_phi = new TTreeReaderArray<double>(*myreader, "jet_phi");
  jet_mass = new TTreeReaderArray<double>(*myreader, "jet_mass");
}

void TreeLoop::findZ1LCandidate(){

  const double Zmass = 91.1876;

  unsigned int Nlep = lepFSR_pt->GetSize();

  // First, make all Z candidates including any FSR photons
  int n_Zs=0;
  vector<int> Z_Z1L_lepindex1;
  vector<int> Z_Z1L_lepindex2;

  for(unsigned int i=0; i<Nlep; i++){

    for(unsigned int j=i+1; j<Nlep; j++){


      // same flavor opposite charge
      if(((*lep_id)[i]+(*lep_id)[j])!=0) continue;

      TLorentzVector li, lj;
      li.SetPtEtaPhiM((*lep_pt)[i],(*lep_eta)[i],(*lep_phi)[i],(*lep_mass)[i]);
      lj.SetPtEtaPhiM((*lep_pt)[j],(*lep_eta)[j],(*lep_phi)[j],(*lep_mass)[j]);

      TLorentzVector lifsr, ljfsr;
      lifsr.SetPtEtaPhiM((*lepFSR_pt)[i],(*lepFSR_eta)[i],(*lepFSR_phi)[i],(*lepFSR_mass)[i]);
      ljfsr.SetPtEtaPhiM((*lepFSR_pt)[j],(*lepFSR_eta)[j],(*lepFSR_phi)[j],(*lepFSR_mass)[j]);

      TLorentzVector liljfsr = lifsr+ljfsr;

      TLorentzVector Z, Z_noFSR;
      Z = lifsr+ljfsr;
      Z_noFSR = li+lj;

      if (Z.M()>0.0) {
        n_Zs++;
        Z_Z1L_lepindex1.push_back(i);
        Z_Z1L_lepindex2.push_back(j);
      }
    } // lep i
  } // lep j

  // Consider all Z candidates
  double minZ1DeltaM=9999.9;
  int leadingPtCut = 40;
  int subleadingPtCut = 25;
  double isoCutEl = 0.35;
  double isoCutMu = 0.35;
  double mZ1Low = 40;
  double mZ1High = 180;


  for (int i=0; i<n_Zs; i++) {

    int i1 = Z_Z1L_lepindex1[i]; int i2 = Z_Z1L_lepindex2[i];

    TLorentzVector lep_i1, lep_i2;
    lep_i1.SetPtEtaPhiM((*lepFSR_pt)[i1],(*lepFSR_eta)[i1],(*lepFSR_phi)[i1],(*lepFSR_mass)[i1]);
    lep_i2.SetPtEtaPhiM((*lepFSR_pt)[i2],(*lepFSR_eta)[i2],(*lepFSR_phi)[i2],(*lepFSR_mass)[i2]);

    TLorentzVector lep_i1_nofsr, lep_i2_nofsr;
    lep_i1_nofsr.SetPtEtaPhiM((*lep_pt)[i1],(*lep_eta)[i1],(*lep_phi)[i1],(*lep_mass)[i1]);
    lep_i2_nofsr.SetPtEtaPhiM((*lep_pt)[i2],(*lep_eta)[i2],(*lep_phi)[i2],(*lep_mass)[i2]);

    TLorentzVector Zi;
    Zi = lep_i1+lep_i2;

    TLorentzVector Z1 = Zi;
    double Z1DeltaM = abs(Zi.M()-Zmass);
    int Z1_lepindex[2] = {0,0};
    if (lep_i1.Pt()>lep_i2.Pt()) { Z1_lepindex[0] = i1;  Z1_lepindex[1] = i2; }
    else { Z1_lepindex[0] = i2;  Z1_lepindex[1] = i1; }

    // Check Leading and Subleading pt Cut
    vector<double> allPt;
    allPt.push_back(lep_i1.Pt()); allPt.push_back(lep_i2.Pt());
    std::sort(allPt.begin(), allPt.end());
    if (allPt[1]<leadingPtCut || allPt[0]<subleadingPtCut ) continue;

    // Check dR(li,lj)>0.02 for any i,j
    vector<double> alldR;
    alldR.push_back(deltaR(lep_i1.Eta(),lep_i1.Phi(),lep_i2.Eta(),lep_i2.Phi()));
    if (*min_element(alldR.begin(),alldR.end())<0.02) continue;

    // Check M(l+,l-)>4.0 GeV for any OS pair
    // Do not include FSR photons
    vector<double> allM;
    TLorentzVector i1i2;
    i1i2 = (lep_i1_nofsr)+(lep_i2_nofsr);
    allM.push_back(i1i2.M());
    if (*min_element(allM.begin(),allM.end())<4.0) {continue;}

    // Check isolation cut (without FSR ) for Z1 leptons
    if ((*lep_RelIsoNoFSR)[Z1_lepindex[0]]>((abs((*lep_id)[Z1_lepindex[0]])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed
    if ((*lep_RelIsoNoFSR)[Z1_lepindex[1]]>((abs((*lep_id)[Z1_lepindex[1]])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed
    // Check tight ID cut for Z1 leptons
    if (!((*lep_tightId)[Z1_lepindex[0]])) continue; // checking tight lepton ID
    if (!((*lep_tightId)[Z1_lepindex[1]])) continue; // checking tight lepton ID

    if ( (Z1.M() < mZ1Low) || (Z1.M() > mZ1High) ) continue;

    //if (verbose) cout<<"good Z1L candidate, Z1DeltaM: "<<Z1DeltaM<<" minZ1DeltaM: "<<minZ1DeltaM<<endl;
    // Check if this candidate has the best Z1 and highest scalar sum of Z2 lepton pt

    if ( Z1DeltaM<=minZ1DeltaM ) {


      minZ1DeltaM = Z1DeltaM;

      TLorentzVector Z1L;
      Z1L = Z1+lep_j1;


      lep_Z1index[0] = Z1_lepindex[0];
      lep_Z1index[1] = Z1_lepindex[1];

      //if (verbose) cout<<" new best Z1L candidate: massZ1: "<<massZ1<<" (mass3l: "<<mass3l<<")"<<endl;
      foundZ1LCandidate=true;
    }
  }

}

void TreeLoop::findZ2JCandidata(){

  unsigned int Njets = jet_pt->GetSize();

  int n_Zs=0;
  vector<int> Z_Z2J_jetindex1;
  vector<int> Z_Z2J_jetindex1;
  for(unsigned int i=0; i<Njets; i++){
    for(unsigned int j=i+1; j<Njets; j++){

      TLorentzVector jet_i1, jet_i2;
      jet_i1.SetPtEtaPhiM((*jet_pt)[i1],(*jet_eta)[i1],(*jet_phi)[i1],(*jet_mass)[i1]);
      jet_i2.SetPtEtaPhiM((*jet_pt)[i2],(*jet_eta)[i2],(*jet_phi)[i2],(*jet_mass)[i2]);

      TLorentzVector Zi;
      Zi = jet_i1+jet_i2;

      if (Z.M()>0.0) {
        n_Zs++;
        Z_Z2J_jetindex1.push_back(i);
        Z_Z2J_jetindex2.push_back(j);
      }
    } //jet 1
  }//jet 2

  for (int i=0; i<n_Zs; i++){
    int i1 = Z_Z2J_jetindex1[i]; int i2 = Z_Z2J_jetindex2[i];

    TLorentzVector jet_i1, jet_i2;
    lep_i1.SetPtEtaPhiM((*jet_pt)[i1],(*jet_eta)[i1],(*jet_phi)[i1],(*jet_mass)[i1]);
    lep_i2.SetPtEtaPhiM((*jet_pt)[i2],(*jet_eta)[i2],(*jet_phi)[i2],(*jet_mass)[i2]);

    TLorentzVector Zi;
    Zi = lep_i1+lep_i2;


  }



}
