#include "TreeLoop.h"


//construtor
TreeLoop::TreeLoop(TString inputfile){
  //df = new ROOT:
  oldfile = new TFile(inputfile);
  if(verbose){
    if(oldfile){
      cout<<"[INFO] open oldfile in "<<inputfile<<endl;
    } else{
      cout<<"[ERROR] can not open file"<<endl;
    }
  }
  //TTreeReader myreader("Ana/passedEvents",oldfile);
  myreader = new TTreeReader("Ana/passedEvents",oldfile);
  //if(verbose){
  //  if(myreader->Next()){
  //    cout<<"[INFO] setup tree reader "<<endl;
  //  } else{
  //    cout<<"[ERROR] can not setup tree reader"<<endl;
  //  }
  //}

  outfile = new TFile("testMEs_CHS.root","recreate");
  passedEventsTree_All = new TTree("passedEvents","passedEvents");

  if(verbose){cout<<"[INFO] construtor done"<<endl;}


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
  if(verbose){cout<<"[INFO] start to event loop"<<endl;}

  if(doMela){
    if(verbose){cout<<"[INFO] setup MELA"<<endl;}
  // Set the MEs
  // ME lists
  setMatrixElementListFromFile(
    "${CMSSW_BASE}/src/HZZAnalysis/ANATree/data/RecoProbabilities.me",
    "AJetsVBFProbabilities_SpinZero_JHUGen,AJetsQCDProbabilities_SpinZero_JHUGen",
    //"AJetsVBFProbabilities_SpinZero_JHUGen,AJetsQCDProbabilities_SpinZero_JHUGen,AJetsVHProbabilities_SpinZero_JHUGen,PMAVJJ_SUPERDIJETMELA",
    false
    );

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
  }else{
    if(verbose){cout<<"[INFO] skip MELA"<<endl;}
  }

  //===================start event loop==========================================
  setTree();
  if(verbose){cout<<"[INFO]============loop tree reader========================"<<endl;}
  while (myreader->Next()) {
    if(!passedTrig){
      if(verbose){cout<<"[INFO] failed pass trigger,skip to next tree loop"<<endl;}
      continue;
    }else{
      if(verbose){cout<<"[INFO] pass trigger"<<endl;}
    }

    if(verbose){
      if(lep_pt->GetSize()>0){
        cout<<"[INFO] this lep pt = "<<(*lep_pt)[0]<<endl;
      }

    }
    //initialize
    foundZ1LCandidate = false;
    foundZ2JCandidate = false;
    found4lCandidate = false;
    for (int i=0; i<2; ++i) {lep_Z1index[i]=-1;}
    for (int i=0; i<2; ++i) {jet_Z1index[i]=-1;}
    for (int i=0; i<2; ++i) {lep_Hindex[i]=-1;}

    mass2jet=0.0;
    pt2jet=0.0;
    mass2l=0.0;
    pt2l=0.0;
    mass2l2jet=0.0;
    KD_jjVBF = 0.0;


    if(verbose){cout<<"[INFO] try to find higgs candidate"<<endl;}
    findZ1LCandidate();
    findZ2JCandidata();

    if((!foundZ1LCandidate) || (!foundZ2JCandidate)){
      if(verbose){cout<<"[INFO] no higgs candidate in this event, skip to next event loop"<<endl;}
      continue;
    } //found Higg 2L2Q candidate
    if(verbose){cout<<"[INFO] higgs candidate is found in this event"<<endl;}


    if(foundZ1LCandidate && foundZ2JCandidate){
      //cout<<"[INFO] higgs candidate is found in this event"<<endl;
      //cout<<"this leading lep pt  = "<<(*lepFSR_pt)[lep_Z1index[0]]<<endl;
      if (doMela){

        //MEs
        //signal like objets
        TLorentzVector p4_ZZ_approx,selectedLep1,selectedLep2,selectedJet1,selectedJet2;
        selectedLep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
        selectedLep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
        selectedJet1.SetPtEtaPhiM((*jet_pt)[jet_Z1index[0]],(*jet_eta)[jet_Z1index[0]],(*jet_phi)[jet_Z1index[0]],(*jet_mass)[jet_Z1index[0]]);
        selectedJet2.SetPtEtaPhiM((*jet_pt)[jet_Z1index[1]],(*jet_eta)[jet_Z1index[1]],(*jet_phi)[jet_Z1index[1]],(*jet_mass)[jet_Z1index[1]]);

        p4_ZZ_approx = selectedLep1+selectedLep2+selectedJet1+selectedJet2;
        mass2l2jet = p4_ZZ_approx.M();

        SimpleParticleCollection_t daughters;
        daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1));
        daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2));
        daughters.push_back(SimpleParticle_t(0, selectedJet1));
        daughters.push_back(SimpleParticle_t(0, selectedJet2));

        //associated objets
        SimpleParticleCollection_t associated;
        int njets = jet_pt->GetSize();
        for(int i=0; i<njets; i++){

          //find jet that are not signal and put it into associated
          if(i==jet_Z1index[0] || i==jet_Z1index[1]){continue;}

          TLorentzVector thisjet;
          thisjet.SetPtEtaPhiM((*jet_pt)[i],(*jet_eta)[i],(*jet_phi)[i],(*jet_mass)[i]);
          associated.push_back(SimpleParticle_t(0, thisjet));

        }

        IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
        IvyMELAHelpers::melaHandle->setInputEvent(&daughters, &associated, nullptr, false);
        MEblock.computeMELABranches();
        MEblock.pushMELABranches();

        IvyMELAHelpers::melaHandle->resetInputEvent();

        //KD
        //retrieve MEs for KD constructing
        unordered_map<string,float> ME_Kfactor_values;
        MEblock.getBranchValues(ME_Kfactor_values);
        //unordered_map<string, float>::iterator iter;
        //for(iter = ME_Kfactor_values.begin(); iter != ME_Kfactor_values.end(); iter++){
        //  cout << "[INFO] this ME_Kfactor_values = "<<iter->first << " : " << iter->second << endl;
        //}
        //VBF
        vector<DiscriminantClasses::Type> KDtypes{DiscriminantClasses::kDjjVBF};
        unsigned int const nKDs = KDtypes.size();
        vector<DiscriminantClasses::KDspecs> KDlist;
        KDlist.reserve(nKDs);
        for (auto const& KDtype:KDtypes) KDlist.emplace_back(KDtype);
        DiscriminantClasses::constructDiscriminants(KDlist, 169*121, "JJVBFTagged");
        //Update discriminants
        for (auto& KDspec:KDlist){

          std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
          for (auto const& strKDvar:KDspec.KDvars){
            //cout<<typeid(strKDvar).name()<<endl;
            //cout<<"this strKDva = "<<strKDvar<<endl;
            //cout<<"this ME_Kfactor_values = "<<ME_Kfactor_values[static_cast<string>(strKDvar)]<<endl;
            KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
          } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.
          //float temp_KD = KDspec.KD->update(KDvars, mass2l2jet);
          //cout<<"KDvars[0] = "<<KDvars[0]<<endl;
          //cout<<"type of mass2l2jet is "<<typeid(mass2l2jet).name()<<"  value of mass2jet  = "<<mass2l2jet<<endl;
          cout<<"type of return value of KD function is :"<<typeid(KDspec.KD->update(KDvars, mass2l2jet)).name()<<"  "<<"value of KD function = "<<KDspec.KD->update(KDvars, mass2l2jet)<<endl;
          KDspec.KD->update(KDvars, mass2l2jet); // Use mZZ!
          //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
          KD_jjVBF = *(KDspec.KD);

        }
        //cout<<KDlist.size()<<endl;
        //KD_jjVBF = *(KDspecs.KD)

        for (auto& KDspec:KDlist) KDspec.resetKD();

      }

    }
    passedEventsTree_All->Fill();

  }

  outfile->cd();
  passedEventsTree_All->Write();


}

//=================find two lepton==============================================
void TreeLoop::findZ1LCandidate(){
  if(verbose){cout<<"[INFO] loop leptons in this event"<<endl;}
  unsigned int Nlep = lepFSR_pt->GetSize();
  if(Nlep<2){return;}
  if(verbose){cout<<"[INFO] found at least tow leptons"<<endl;}

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
  if(verbose){cout<<"[INFO] find leptons pairs"<<endl;}

  // Consider all Z candidates
  double minZ1DeltaM=9999.9;

  if(verbose){cout<<"[INFO] checkout all leptons pairs if is Z candidate"<<endl;}
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
    if(verbose){cout<<"[INFO] found Z1 leptons pairs candidate"<<endl;}

    //if (verbose) cout<<"good Z1L candidate, Z1DeltaM: "<<Z1DeltaM<<" minZ1DeltaM: "<<minZ1DeltaM<<endl;
    // Check if this candidate has the best Z1 and highest scalar sum of Z2 lepton pt

    if ( Z1DeltaM<=minZ1DeltaM ) {


      minZ1DeltaM = Z1DeltaM;

      lep_Z1index[0] = Z1_lepindex[0];
      lep_Z1index[1] = Z1_lepindex[1];

      mass2l = Z1.M();
      pt2l = Z1.Pt();

      //if (verbose) cout<<" new best Z1L candidate: massZ1: "<<massZ1<<" (mass3l: "<<mass3l<<")"<<endl;
      foundZ1LCandidate=true;
    }
  }

  if(verbose){

    if(foundZ1LCandidate){cout<<"[INFO] found leptoinc Z candidate."<<endl;}
    else{cout<<"[INFO] no leptoinc Z candidate in this evnets"<<endl;}
  }


}

//==================find two resovled jets======================================
void TreeLoop::findZ2JCandidata(){
  if(verbose){cout<<"[INFO] loop jets in this events"<<endl;}
  unsigned int Njets = jet_pt->GetSize();
  if(Njets<2){ return; } //found at least two jets
  if(verbose){cout<<"[INFO] find at least two jets. number of jets = "<<Njets<<" in this events"<<endl;}


  int n_Zs=0;
  vector<int> Z_Z2J_jetindex1;
  vector<int> Z_Z2J_jetindex2;
  for(unsigned int i=0; i<Njets; i++){
    for(unsigned int j=i+1; j<Njets; j++){

      TLorentzVector jet_i1, jet_i2;
      jet_i1.SetPtEtaPhiM((*jet_pt)[i],(*jet_eta)[i],(*jet_phi)[i],(*jet_mass)[i]);
      jet_i2.SetPtEtaPhiM((*jet_pt)[j],(*jet_eta)[j],(*jet_phi)[j],(*jet_mass)[j]);

      TLorentzVector Zjet;
      Zjet = jet_i1+jet_i2;

      if (Zjet.M()>0.0) {
        n_Zs++;
        Z_Z2J_jetindex1.push_back(i);
        Z_Z2J_jetindex2.push_back(j);
      }
    } //jet 1
  }//jet 2

  // Consider all Z candidates
  double minZ1DeltaM=9999.9;

  for (int i=0; i<n_Zs; i++){

    int i1 = Z_Z2J_jetindex1[i]; int i2 = Z_Z2J_jetindex2[i];

    TLorentzVector jet_i1, jet_i2;
    jet_i1.SetPtEtaPhiM((*jet_pt)[i1],(*jet_eta)[i1],(*jet_phi)[i1],(*jet_mass)[i1]);
    jet_i2.SetPtEtaPhiM((*jet_pt)[i2],(*jet_eta)[i2],(*jet_phi)[i2],(*jet_mass)[i2]);

    TLorentzVector Zi;
    Zi = jet_i1+jet_i2;

    TLorentzVector Z1 = Zi;
    double Z1DeltaM = abs(Zi.M()-Zmass);

    //sort jet in terms of Pt order
    int Z2_jetindex[2] = {0,0};
    if (jet_i1.Pt()>jet_i2.Pt()) { Z2_jetindex[0] = i1;  Z2_jetindex[1] = i2; }
    else { Z2_jetindex[0] = i2;  Z2_jetindex[1] = i1; }

    //check each jet pt and eta
    if(jet_i1.Pt()<30 || jet_i2.Pt()<30) {continue;}
    if(abs(jet_i1.Eta()>2.4) || abs(jet_i2.Eta()>2.4)) {continue;}

    //all jet must not overlap with tight leptons
    bool isclean_jet = true;
    unsigned int thisNjets = 2;
    unsigned int Nleptons = lep_pt->GetSize();
    for(unsigned int i=0; i<thisNjets; i++){
      for (unsigned int j=0; j<Nleptons; j++){

        bool passed_idiso=true;
        if (abs((*lep_id)[j])==13 && (*lep_RelIsoNoFSR)[j]>isoCutMu) passed_idiso=false;
        if (abs((*lep_id)[j])==11 && (*lep_RelIsoNoFSR)[j]>isoCutEl) passed_idiso=false;
        if (!((*lep_tightId)[j])) passed_idiso=false;
        //for (int l=0; l<4; l++) {
        //    if ((int)i==lep_Hindex[l]) cand_lep=true;
        //}
        //if (!(passed_idiso || cand_lep)) continue;
        if (!passed_idiso) continue;
        TLorentzVector thisLep;
        thisLep.SetPtEtaPhiM((*lep_pt)[j],(*lep_eta)[j],(*lep_phi)[j],(*lep_mass)[j]);

        double tempDeltaR=999.0;
        tempDeltaR=deltaR((*jet_eta)[i],(*jet_phi)[i],thisLep.Eta(),thisLep.Phi());
        if (tempDeltaR<0.4){
          isclean_jet = false;
        }
      }
    }
    if(!isclean_jet){continue;}

    //check dijet pt
    if(Zi.Pt()<dijetPtCut){ continue;}

    //check loose dijet mass for 40-180Gev
    if(Zi.M()<mZ1Low || Zi.M()>mZ1High){ continue;}

    if ( Z1DeltaM<=minZ1DeltaM ) {

      minZ1DeltaM = Z1DeltaM;

      jet_Z1index[0] = Z2_jetindex[0];
      jet_Z1index[1] = Z2_jetindex[1];

      mass2jet = Zi.M();
      pt2jet = Zi.Pt();

      //if (verbose) cout<<" new best Z1L candidate: massZ1: "<<massZ1<<" (mass3l: "<<mass3l<<")"<<endl;
      foundZ2JCandidate=true;
    }
  }
}


//=====================findHZZ4Lcandidate============================================
void TreeLoop::find4lCandidate(){
  cout<<"nothing in this function"<<endl;
}

//=========================set input and output tree==================================
void TreeLoop::setTree(){
  if(verbose){cout<<"[INFO] set input tree variables"<<endl;}
  //oldfile->cd();
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
  lep_RelIsoNoFSR = new TTreeReaderArray<float>(*myreader, "lep_RelIsoNoFSR");
  passedTrig = new TTreeReaderValue<bool>(*myreader,"passedTrig");

  jet_pt = new TTreeReaderArray<double>(*myreader, "jet_pt");
  jet_eta = new TTreeReaderArray<double>(*myreader, "jet_eta");
  jet_phi = new TTreeReaderArray<double>(*myreader, "jet_phi");
  jet_mass = new TTreeReaderArray<double>(*myreader, "jet_mass");

  passedEventsTree_All->Branch("mass2jet",&mass2jet);
  passedEventsTree_All->Branch("pt2jet",&pt2jet);
  passedEventsTree_All->Branch("mass2l",&mass2l);
  passedEventsTree_All->Branch("pt2l",&pt2l);
  passedEventsTree_All->Branch("mass2l2jet",&mass2l2jet);
  passedEventsTree_All->Branch("KD_jjVBF",&KD_jjVBF);


}
