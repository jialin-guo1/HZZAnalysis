#include "TreeLoop.h"


//construtor
TreeLoop::TreeLoop(TString inputfile, TString outputfile){
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

  outfile = new TFile(outputfile,"recreate");
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
  int nevents_negative = 0;
  int nevents_nassociatedjets_lesstwo = 0;
  while (myreader->Next()) {
    if(!passedTrig){
      if(verbose){cout<<"[INFO] failed pass trigger,skip to next tree loop"<<endl;}
      continue;
    }else{
      if(verbose){cout<<"[INFO] pass trigger"<<endl;}
      passed_trig++;
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
    foundZ2MergedCandidata = false;
    foundmergedOnly = false;
    foundresolvedOnly = false;
    foundresolvedCombine = false;
    foundmergedCombine = false;
    passedfullmerged = false;
    passedfullresolved = false;
    for (int i=0; i<2; ++i) {lep_Z1index[i]=-1;}
    for (int i=0; i<2; ++i) {jet_Z1index[i]=-1;}
    for (int i=0; i<2; ++i) {lep_Hindex[i]=-1;}
    merged_Z1index = -1;

    mass2jet=-999.99;
    pt2jet=-999.99;
    mass2l=-999.99;
    pt2l=-999.99;
    mass2l2jet=-999.99;
    KD_jjVBF = -999.99;
    massmerged = -999.99;
    ptmerged = -999.99;
    nsubjet = -999.99;
    mass2lj = -999.99;

    particleNetZvsQCD = -999.99;

    associatedjet_pt.clear(); associatedjet_eta.clear(); associatedjet_phi.clear(); associatedjet_mass.clear();
    //initialize done


    if(verbose){cout<<"[INFO] try to find higgs candidate"<<endl;}
    findZ1LCandidate();
    findZ2JCandidata();
    findZ2MergedCandidata();

    /*
    if((!foundZ1LCandidate) || (!foundZ2JCandidate)){
      if(verbose){cout<<"[INFO] no higgs candidate in this event, skip to next event loop"<<endl;}
      continue;
    } //found Higg 2L2Q candidate
    if(verbose){cout<<"[INFO] higgs candidate is found in this event"<<endl;}
    */

    //find resovled only higgs
    if(foundZ1LCandidate && foundZ2JCandidate && !foundZ2MergedCandidata){
      passed_resovedonlyHiggs++;
      foundresolvedOnly = true;
    }
    //find merged only higgs
    if(foundZ1LCandidate && foundZ2MergedCandidata && !foundZ2JCandidate){
      passed_MergedolonlyHiggs++;
      foundmergedOnly = true;
    }
    //find combination higgs
    if(foundZ1LCandidate && foundZ2MergedCandidata && foundZ2JCandidate){
      passed_combinHiggs++;
      if(pt2l>200 && ptmerged>300){
        passed_combineMerged ++;
        foundmergedCombine = true;
      } else{
        passed_combineResolved ++;
        foundresolvedCombine = true;
      }

    }

    //full resovled higgs and do MALE
    /*
    if(foundresolvedOnly || foundresolvedCombine){
      passed_fullresolved++;
      passedfullresolved = true;

      if (doMela){
        //check number of associated jets
        int njets = jet_pt->GetSize();
        int nassociatedjets = 0;
        vector<TLorentzVector> associatedjets;
        for(int i=0; i<njets; i++){

          //find jet that are not signal and put it into associated
          if(i==jet_Z1index[0] || i==jet_Z1index[1]){continue;}
          nassociatedjets++;

          TLorentzVector thisjet;
          thisjet.SetPtEtaPhiM((*jet_pt)[i],(*jet_eta)[i],(*jet_phi)[i],(*jet_mass)[i]);
          associatedjets.push_back(thisjet);

        }
        if(nassociatedjets>=2){ //compute KD_jjVBF

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
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          double temp_leadingpt=0.0;
          for(int i=0; i<nassociatedjets; i++){
            if(associatedjets[i].Pt()>temp_leadingpt){
              temp_leadingpt = associatedjets[i].Pt();
              leading_index[0]= i;
            }
          }
          double temp_subleadingpt=0.0;
          for(int i=0; i<nassociatedjets; i++){
            if(i==leading_index[0]) continue; //do not count leading jet

            if(associatedjets[i].Pt()>temp_subleadingpt){
              temp_subleadingpt = associatedjets[i].Pt();
              leading_index[1]= i;
            }
          }
          //sort done
          for(int i=0; i<2; i++){ //put two leading jets into associated
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[i]]));
            associatedjet_pt.push_back(associatedjets[leading_index[i]].Pt());
            associatedjet_eta.push_back(associatedjets[leading_index[i]].Eta());
            associatedjet_phi.push_back(associatedjets[leading_index[i]].Phi());
            associatedjet_mass.push_back(associatedjets[leading_index[i]].M());
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
            //cout<<"type of return value of KD function is :"<<typeid(KDspec.KD->update(KDvars, mass2l2jet)).name()<<"  "<<"value of KD function = "<<KDspec.KD->update(KDvars, mass2l2jet)<<endl;
            KDspec.KD->update(KDvars, mass2l2jet); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_jjVBF = *(KDspec.KD);
            if(nassociatedjets<2){
              nevents_nassociatedjets_lesstwo++;
              //cout<<"[WARNNING] There is less than 2 associated jets in this event. There number of associated jets in this events = "<<nassociatedjets<<endl;
              //cout<<"In this event, KD = "<<KD_jjVBF<<endl;
            }
            if(KD_jjVBF<0){
              nevents_negative++;
            }

          }
          for (auto& KDspec:KDlist) KDspec.resetKD();

        }

      }

    }
    */
    //full merged higgs and do MALE
    if(foundmergedOnly){
      passed_fullmerged++;
      passedfullmerged = true;
      nsubjet = (*mergedjet_nsubjet)[merged_Z1index];

      if (doMela){
        int njets = jet_pt->GetSize();
        int nassociatedjets = 0;
        vector<TLorentzVector> associatedjets;
        for(int i=0; i<njets; i++){

          if(foundZ2JCandidate){
            if(i==jet_Z1index[0] || i==jet_Z1index[1]){continue;}
          }

          TLorentzVector thisjet;

          thisjet.SetPtEtaPhiM((*jet_pt)[i],(*jet_eta)[i],(*jet_phi)[i],(*jet_mass)[i]);
          //check this deltaR between this jet and selected merged jet

          double temp_DR = deltaR(thisjet.Eta(),thisjet.Phi(),(*mergedjet_eta)[merged_Z1index],(*mergedjet_phi)[merged_Z1index]);
          if(temp_DR<0.8) {
            continue;
          }
          nassociatedjets++;
          associatedjets.push_back(thisjet);
        }

        if(nassociatedjets>=2){ //compute KD_jjVBF

          //MEs
          //signal like objets
          TLorentzVector p4_ZZ_approx,selectedLep1,selectedLep2,selectedJet1,selectedJet2;
          selectedLep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
          selectedLep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
          selectedJet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][0],(*mergedjet_subjet_eta)[merged_Z1index][0],(*mergedjet_subjet_phi)[merged_Z1index][0],(*mergedjet_subjet_mass)[merged_Z1index][0]);
          selectedJet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index][1],(*mergedjet_subjet_phi)[merged_Z1index][1],(*mergedjet_subjet_mass)[merged_Z1index][1]);

          p4_ZZ_approx = selectedLep1+selectedLep2+selectedJet1+selectedJet2;
          mass2lj = p4_ZZ_approx.M();

          SimpleParticleCollection_t daughters;
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1));
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2));
          daughters.push_back(SimpleParticle_t(0, selectedJet1));
          daughters.push_back(SimpleParticle_t(0, selectedJet2));

          //associated objets
          SimpleParticleCollection_t associated;
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          double temp_leadingpt=0.0;
          for(int i=0; i<nassociatedjets; i++){
            if(associatedjets[i].Pt()>temp_leadingpt){
              temp_leadingpt = associatedjets[i].Pt();
              leading_index[0]= i;
            }
          }
          double temp_subleadingpt=0.0;
          for(int i=0; i<nassociatedjets; i++){
            if(i==leading_index[0]) continue; //do not count leading jet

            if(associatedjets[i].Pt()>temp_subleadingpt){
              temp_subleadingpt = associatedjets[i].Pt();
              leading_index[1]= i;
            }
          }
          //sort done
          for(int i=0; i<2; i++){ //put two leading jets into associated
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[i]]));
            associatedjet_pt.push_back(associatedjets[leading_index[i]].Pt());
            associatedjet_eta.push_back(associatedjets[leading_index[i]].Eta());
            associatedjet_phi.push_back(associatedjets[leading_index[i]].Phi());
            associatedjet_mass.push_back(associatedjets[leading_index[i]].M());
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

            KDspec.KD->update(KDvars, mass2lj); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_jjVBF = *(KDspec.KD);
            if(nassociatedjets<2){
              nevents_nassociatedjets_lesstwo++;
            }
            if(KD_jjVBF<0){
              nevents_negative++;
            }

          }
          for (auto& KDspec:KDlist) KDspec.resetKD();

        }

      }

    }



    //==========fill output tree branch==========================================
    passedEventsTree_All->Fill();

  }
  //=========================loop done==========================================
  cout<<"[INFO] there are "<<nevents_negative<<" "<<"events have negative KD value"<<endl;
  cout<<"[INFO] there are "<<nevents_nassociatedjets_lesstwo<<" "<<"events with number of associated jets less than two"<<endl;

  outfile->cd();
  passedEventsTree_All->Write();

  //print cut table infor
  cout<<"passed_trig = "<<passed_trig<<endl;
  cout<<"passed_n_2leps = "<<passed_n_2leps<<endl;
  cout<<"passed_flavor_charge = "<<passed_flavor_charge<<endl;
  cout<<"passed_lepZpt_40_25 = "<<passed_lepZpt_40_25<<endl;
  cout<<"passed_dR_lilj0point2 = "<<passed_dR_lilj0point2<<endl;
  cout<<"passed_Mll_4 = "<<passed_Mll_4<<endl;
  cout<<"passed_lepisolation = "<<passed_lepisolation<<endl;
  cout<<"passed_leptightID = "<<passed_leptightID<<endl;
  cout<<"passed_lepZmass40_180 = "<<passed_lepZmass40_180<<endl;

  cout<<"passed_n_2ak4jets = "<<passed_n_2ak4jets<<endl;
  cout<<"passed_lepclean = "<<passed_lepclean<<endl;
  cout<<"passed_jetpt30 = "<<passed_jetpt30<<endl;
  cout<<"passed_jeteta2opint4 = "<<passed_jeteta2opint4<<endl;
  cout<<"passed_dijetpt100 = "<<passed_dijetpt100<<endl;
  cout<<"passed_ak4jetZm_40_180 = "<<passed_ak4jetZm_40_180<<endl;

  cout<<"passed_resovedonlyHiggs = "<<passed_resovedonlyHiggs<<endl;

  cout<<"passed_nmergedjets_lepclean = "<<passed_nmergedjets_lepclean<<endl;
  cout<<"passed_mergedjetsPt200 = "<<passed_mergedjetsPt200<<endl;
  cout<<"passed_mergedjetEta2opint4 = "<<passed_mergedjetEta2opint4<<endl;
  cout<<"passed_mergedmass_40_180 = "<<passed_mergedmass_40_180<<endl;
  cout<<"passed_particleNetZvsQCD0opint9 = "<<passed_particleNetZvsQCD0opint9<<endl;

  cout<<"passed_MergedolonlyHiggs = "<<passed_MergedolonlyHiggs<<endl;
  cout<<"passed_combinHiggs = "<<passed_combinHiggs<<endl;
  cout<<"passed_combineMerged = "<<passed_combineMerged<<endl;
  cout<<"passed_combineResolved = "<<passed_combineResolved<<endl;


}

//=================find two lepton==============================================
void TreeLoop::findZ1LCandidate(){
  if(verbose){cout<<"[INFO] loop leptons in this event"<<endl;}
  unsigned int Nlep = lepFSR_pt->GetSize();
  if(Nlep<2){return;}
  passed_n_2leps++;
  if(verbose){cout<<"[INFO] found at least tow leptons"<<endl;}

  // First, make all Z candidates including any FSR photons
  int n_Zs=0;
  vector<int> Z_Z1L_lepindex1;
  vector<int> Z_Z1L_lepindex2;

  //variables for cut table
  bool pass_flavor_charge = false;

  for(unsigned int i=0; i<Nlep; i++){

    for(unsigned int j=i+1; j<Nlep; j++){


      // same flavor opposite charge
      if(((*lep_id)[i]+(*lep_id)[j])!=0) continue;
      pass_flavor_charge = true;

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
  if(pass_flavor_charge) passed_flavor_charge++;

  //variables for cut table
  bool pass_lepZpt_40_25 = false;
  bool pass_dR_lilj0point2 = false;
  bool pass_Mll_4 = false;
  bool pass_lepisolation = false;
  bool pass_leptightID = false;
  bool pass_lepZmass40_180 = false;
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
    pass_lepZpt_40_25 = true;

    // Check dR(li,lj)>0.02 for any i,j
    vector<double> alldR;
    alldR.push_back(deltaR(lep_i1.Eta(),lep_i1.Phi(),lep_i2.Eta(),lep_i2.Phi()));
    if (*min_element(alldR.begin(),alldR.end())<0.02) continue;
    pass_dR_lilj0point2 = true;

    // Check M(l+,l-)>4.0 GeV for any OS pair
    // Do not include FSR photons
    vector<double> allM;
    TLorentzVector i1i2;
    i1i2 = (lep_i1_nofsr)+(lep_i2_nofsr);
    allM.push_back(i1i2.M());
    if (*min_element(allM.begin(),allM.end())<4.0) {continue;}
    pass_Mll_4 = true;

    // Check isolation cut (without FSR ) for Z1 leptons
    if ((*lep_RelIsoNoFSR)[Z1_lepindex[0]]>((abs((*lep_id)[Z1_lepindex[0]])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed
    if ((*lep_RelIsoNoFSR)[Z1_lepindex[1]]>((abs((*lep_id)[Z1_lepindex[1]])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed
    pass_lepisolation = true;
    // Check tight ID cut for Z1 leptons
    if (!((*lep_tightId)[Z1_lepindex[0]])) continue; // checking tight lepton ID
    if (!((*lep_tightId)[Z1_lepindex[1]])) continue; // checking tight lepton ID
    pass_leptightID = true;

    if ( (Z1.M() < mZ1Low) || (Z1.M() > mZ1High) ) continue;
    pass_lepZmass40_180 = true;
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

  if(pass_lepZpt_40_25) passed_lepZpt_40_25++;
  if(pass_dR_lilj0point2) passed_dR_lilj0point2++;
  if(pass_Mll_4) passed_Mll_4++;
  if(pass_lepisolation) passed_lepisolation++;
  if(pass_leptightID) passed_leptightID++;
  if(pass_lepZmass40_180) passed_lepZmass40_180++;
  if(foundZ1LCandidate) passed_lepZ++;


  if(verbose){
    if(foundZ1LCandidate){cout<<"[INFO] found leptoinc Z candidate."<<endl;}
    else{cout<<"[INFO] no leptoinc Z candidate in this evnets"<<endl;}
  }


}

//==================find two resovled jets=========================================
void TreeLoop::findZ2JCandidata(){
  if(verbose){cout<<"[INFO] loop jets in this events"<<endl;}
  unsigned int Njets = jet_pt->GetSize();
  if(Njets<2){ return; } //found at least two jets
  passed_n_2ak4jets++;
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


  //variables for cut table
  bool pass_jetpt30 = false;
  bool pass_jeteta2opint4 = false;
  bool pass_lepclean = false;
  bool pass_dijetpt100 = false;
  bool pass_ak4jetZm_40_180 = false;

  // Consider all Z candidates
  double minZ1DeltaM=9999.9;
  double temp_pt = 0.0;

  for (int i=0; i<n_Zs; i++){

    int i1 = Z_Z2J_jetindex1[i]; int i2 = Z_Z2J_jetindex2[i];
    int this_jetindex[2] = {i1,i2};

    TLorentzVector jet_i1, jet_i2;
    jet_i1.SetPtEtaPhiM((*jet_pt)[i1],(*jet_eta)[i1],(*jet_phi)[i1],(*jet_mass)[i1]);
    jet_i2.SetPtEtaPhiM((*jet_pt)[i2],(*jet_eta)[i2],(*jet_phi)[i2],(*jet_mass)[i2]);

    TLorentzVector Zi;
    Zi = jet_i1+jet_i2;

    TLorentzVector Z1 = Zi;
    double Z1DeltaM = abs(Zi.M()-Zmass);

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
        tempDeltaR=deltaR((*jet_eta)[this_jetindex[i]],(*jet_phi)[this_jetindex[i]],thisLep.Eta(),thisLep.Phi());
        if (tempDeltaR<0.4){
          isclean_jet = false;
        }
      }
    }
    if(!isclean_jet){continue;}
    pass_lepclean = true;

    //sort jet in terms of Pt order
    int Z2_jetindex[2] = {0,0};
    if (jet_i1.Pt()>jet_i2.Pt()) { Z2_jetindex[0] = i1;  Z2_jetindex[1] = i2; }
    else { Z2_jetindex[0] = i2;  Z2_jetindex[1] = i1; }

    //check each jet pt and eta
    if(jet_i1.Pt()<30 || jet_i2.Pt()<30) {continue;}
    pass_jetpt30 = true;
    if(abs(jet_i1.Eta()>2.4) || abs(jet_i2.Eta()>2.4)) {continue;}
    pass_jeteta2opint4 = true;

    //check dijet pt
    if(Zi.Pt()<dijetPtCut){ continue;}
    pass_dijetpt100 = true;

    //check loose dijet mass for 40-180Gev
    if(Zi.M()<mZ1Low || Zi.M()>mZ1High){ continue;}
    pass_ak4jetZm_40_180 = true;
    /*
    if ( Z1DeltaM<=minZ1DeltaM ) {

      minZ1DeltaM = Z1DeltaM;

      jet_Z1index[0] = Z2_jetindex[0];
      jet_Z1index[1] = Z2_jetindex[1];

      mass2jet = Zi.M();
      pt2jet = Zi.Pt();

      //if (verbose) cout<<" new best Z1L candidate: massZ1: "<<massZ1<<" (mass3l: "<<mass3l<<")"<<endl;
      foundZ2JCandidate=true;
    }
    */
    //select as di-jet pt order
    if(Zi.Pt()>temp_pt){
      temp_pt = Zi.Pt();

      jet_Z1index[0] = Z2_jetindex[0];
      jet_Z1index[1] = Z2_jetindex[1];

      mass2jet = Zi.M();
      pt2jet = Zi.Pt();

      foundZ2JCandidate=true;

    }
  }

  if(pass_jetpt30) passed_jetpt30++;
  if(pass_jeteta2opint4) passed_jeteta2opint4++;
  if(pass_lepclean) passed_lepclean++;
  if(pass_dijetpt100) passed_dijetpt100++;
  if(pass_ak4jetZm_40_180) passed_ak4jetZm_40_180++;
}

//==================find mergedjets==================================================
void TreeLoop::findZ2MergedCandidata(){
  int nmergedjets = mergedjet_pt->GetSize();

  //cut table
  bool pass_nmergedjets = false;
  bool pass_mergedjetsPt200 = false;
  bool pass_mergedjetEta2opint4 = false;
  bool pass_mergedmass_40_180 = false;
  bool pass_particleNetZvsQCD0opint9 = false;
  if(nmergedjets<1) return;
  pass_nmergedjets = true;
  if(pass_nmergedjets) passed_nmergedjets_lepclean++;

  float this_pt = 0.0;
  for(int i=0; i<nmergedjets; i++){
    if((*mergedjet_pt)[i]<200) continue;
    pass_mergedjetsPt200 = true;

    if(abs((*mergedjet_eta)[i])>2.4) continue;
    pass_mergedjetEta2opint4 = true;

    if((*mergedjet_subjet_softDropMass)[i]<mZ1Low || (*mergedjet_subjet_softDropMass)[i]>mZ1High) continue;
    pass_mergedmass_40_180 = true;

    float temp_particleNetZvsQCD = (*mergedjet_Net_Xbb_de)[i]+(*mergedjet_Net_Xcc_de)[i]+(*mergedjet_Net_Xqq_de)[i];
    if(temp_particleNetZvsQCD<0.9) continue;
    //cout<<"this passed ZvsQCD = "<<temp_particleNetZvsQCD<<endl;
    pass_particleNetZvsQCD0opint9 = true;

    foundZ2MergedCandidata = true;
    if((*mergedjet_pt)[i]>this_pt){
      this_pt = (*mergedjet_pt)[i];
      ptmerged = this_pt;
      massmerged = (*mergedjet_subjet_softDropMass)[i];
      merged_Z1index = i;
      particleNetZvsQCD = temp_particleNetZvsQCD;
    }

  }

  if(pass_mergedjetsPt200) passed_mergedjetsPt200++;
  if(pass_mergedjetEta2opint4) passed_mergedjetEta2opint4++;
  if(pass_mergedmass_40_180) passed_mergedmass_40_180++;
  if(pass_particleNetZvsQCD0opint9) passed_particleNetZvsQCD0opint9++;
  //cout<<"this passed_particleNetZvsQCD0opint9 = "<<passed_particleNetZvsQCD0opint9<<endl;

}


//=====================findHZZ4Lcandidate============================================
/*
void TreeLoop::find4lCandidate(){

  cout<<"nothing in this function"<<endl;

  const double Zmass = 91.1876;

  unsigned int Nlep = lepFSR_pt.size();
  if(Nlep<4) return;
  if (verbose) cout<<Nlep<<" leptons in total"<<endl;

  // First, make all Z candidates including any FSR photons
  int n_Zs=0;
  vector<int> Z_lepindex1;
  vector<int> Z_lepindex2;
  vector<float> Z_pt, Z_eta, Z_phi, Z_mass, Z_noFSR_pt, Z_noFSR_eta, Z_noFSR_mass;

  for(unsigned int i=0; i<Nlep; i++){

      //if (!(lep_tightId[i])) continue; // checking tight lepton ID
      //if (lep_RelIsoNoFSR[i]>((abs(lep_id[i])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed
      for(unsigned int j=i+1; j<Nlep; j++){
          //if (!(lep_tightId[j])) continue; // checking tight lepton ID
          //if (lep_RelIsoNoFSR[j]>((abs(lep_id[j])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed

          // same flavor opposite charge
          if((lep_id[i]+lep_id[j])!=0) continue;

          TLorentzVector li, lj;
          li.SetPtEtaPhiM((*lep_pt)[i],(*lep_pt)[i],(*lep_phi)[i],(*lep_mass)[i]);
          lj.SetPtEtaPhiM((*lep_pt)[j],(*lep_pt)[j],(*lep_phi)[j],(*lep_mass)[j]);

          TLorentzVector lifsr, ljfsr;
          lifsr.SetPtEtaPhiM((*lepFSR_pt)[i],(*lepFSR_eta)[i],(*lepFSR_phi)[i],(*lepFSR_mass)[i]);
          ljfsr.SetPtEtaPhiM((*lepFSR_pt)[j],(*lepFSR_eta)[j],(*lepFSR_phi)[j],(*lepFSR_mass)[j]);

          TLorentzVector liljfsr = lifsr+ljfsr;

          if (verbose) {
              cout<<"OSSF pair: i="<<i<<" id1="<<lep_id[i]<<" j="<<j<<" id2="<<lep_id[j]<<" pt1: "<<lifsr.Pt()<<" pt2: "<<ljfsr.Pt()<<" M: "<<liljfsr.M()<<endl;
          }

          TLorentzVector Z, Z_noFSR;
          Z = lifsr+ljfsr;
          Z_noFSR = li+lj;

          if (verbose) cout<<"this Z mass: "<<Z.M()<<" mZ2Low: "<<mZ2Low<<endl;

          if (Z.M()>0.0) {
              n_Zs++;
              Z_pt.push_back(Z.Pt());
              Z_eta.push_back(Z.Eta());
              Z_phi.push_back(Z.Phi());
              Z_mass.push_back(Z.M());
              Z_noFSR_pt.push_back(Z_noFSR.Pt());
              Z_noFSR_eta.push_back(Z_noFSR.Eta());
              Z_noFSR_phi.push_back(Z_noFSR.Phi());
              Z_noFSR_mass.push_back(Z_noFSR.M());
              Z_lepindex1.push_back(i);
              Z_lepindex2.push_back(j);
              if (verbose) cout<<" add Z_lepindex1: "<<i<<" Z_lepindex2: "<<j<<endl;
          }

      } // lep i
  } // lep j

  if (verbose) cout<<"found four leptons"<<endl;

  bool properLep_ID = false; int Nmm = 0; int Nmp = 0; int Nem = 0; int Nep = 0;
  for(int i = 0; i<Nlep; i++){
    if((*lep_id)[i]==-13) Nmm = Nmm+1;
    if((*lep_id)[i]==13) Nmp = Nmp+1;
    if((*lep_id)[i]==-11) Nem = Nem+1;
    if((*lep_id)[i]==11) Nep = Nep+1;
  }
  if(Nmm>=2 && Nmp>=2) properLep_ID = true; //4mu
  if(Nem>=2 && Nep>=2) properLep_ID = true; //4e
  if(Nmm>0 && Nmp>0 && Nem>0 && Nep>0) properLep_ID = true; //2e2mu
  // four proper charge flavor combination
  if(!properLep_ID) return;

  // Consider all ZZ candidates
  double minZ1DeltaM_SR=9999.9; double minZ1DeltaM_CR=99999.9;
  double maxZ2SumPt_SR=0.0; double maxZ2SumPt_CR=0.0;
  double max_D_bkg_kin_SR=0.0; double max_D_bkg_kin_CR=0.0;
  bool foundSRCandidate=false;

  for (int i=0; i<n_Zs; i++) {
      for (int j=i+1; j<n_Zs; j++) {

          int i1 = Z_lepindex1[i]; int i2 = Z_lepindex2[i];
          int j1 = Z_lepindex1[j]; int j2 = Z_lepindex2[j];

          if (i1 == j1 || i1 == j2 || i2 == j1 || i2 == j2) continue; // if there common leptons

          TLorentzVector lep_i1, lep_i2, lep_j1, lep_j2;
          lep_i1.SetPtEtaPhiM((*lepFSR_pt)[i1],(*lepFSR_eta)[i1],(*lepFSR_phi)[i1],(*lepFSR_mass)[i1]);
          lep_i2.SetPtEtaPhiM((*lepFSR_pt)[i2],(*lepFSR_eta)[i2],(*lepFSR_phi)[i2],(*lepFSR_mass)[i2]);
          lep_j1.SetPtEtaPhiM((*lepFSR_pt)[j1],(*lepFSR_eta)[j1],(*lepFSR_phi)[j1],(*lepFSR_mass)[j1]);
          lep_j2.SetPtEtaPhiM((*lepFSR_pt)[j2],(*lepFSR_eta)[j2],(*lepFSR_phi)[j2],(*lepFSR_mass)[j2]);

          TLorentzVector lep_i1_nofsr, lep_i2_nofsr, lep_j1_nofsr, lep_j2_nofsr;
          lep_i1_nofsr.SetPtEtaPhiM((*lep_pt)[i1],(*lep_pt)[i1],(*lep_phi)[i1],(*lep_mass)[i1]);
          lep_i2_nofsr.SetPtEtaPhiM((*lep_pt)[i2],(*lep_pt)[i2],(*lep_phi)[i2],(*lep_mass)[i2]);
          lep_j1_nofsr.SetPtEtaPhiM((*lep_pt)[j1],(*lep_pt)[j1],(*lep_phi)[j1],(*lep_mass)[j1]);
          lep_j2_nofsr.SetPtEtaPhiM((*lep_pt)[j2],(*lep_pt)[j2],(*lep_phi)[j2],(*lep_mass)[j2]);

          TLorentzVector Zi, Zj;
          Zi.SetPtEtaPhiM(Z_pt[i],Z_eta[i],Z_phi[i],Z_mass[i]);
          Zj.SetPtEtaPhiM(Z_pt[j],Z_eta[j],Z_phi[j],Z_mass[j]);

          if (verbose) {cout<<"ZZ candidate Zi->M() "<<Zi.M()<<" Zj->M() "<<Zj.M()<<endl;}

          TLorentzVector Z1, Z2;
          int Z1index, Z2index;
          int Z1_lepindex[2] = {0,0};
          int Z2_lepindex[2] = {0,0};
          double Z1DeltaM, Z2SumPt;

          if (abs(Zi.M()-Zmass)<abs(Zj.M()-Zmass)) {
              Z1index = i; Z2index = j;
              Z1 = Zi; Z2 = Zj;
              if (lep_i1.Pt()>lep_i2.Pt()) { Z1_lepindex[0] = i1;  Z1_lepindex[1] = i2; }
              else { Z1_lepindex[0] = i2;  Z1_lepindex[1] = i1; }
              if (lep_j1.Pt()>lep_j2.Pt()) { Z2_lepindex[0] = j1;  Z2_lepindex[1] = j2; }
              else { Z2_lepindex[0] = j2;  Z2_lepindex[1] = j1; }
              Z1DeltaM = abs(Zi.M()-Zmass);
              Z2SumPt = lep_j1_nofsr.Pt()+lep_j2_nofsr.Pt();
              //                 if(isMuonZi) isMuon = true;
              //                 else isMuon = false;
          }
          else {
              Z1index = j; Z2index = i;
              Z1 = Zj; Z2 = Zi;
              if (lep_j1.Pt()>lep_j2.Pt()) { Z1_lepindex[0] = j1;  Z1_lepindex[1] = j2; }
              else { Z1_lepindex[0] = j2;  Z1_lepindex[1] = j1; }
              if (lep_i1.Pt()>lep_i2.Pt()) { Z2_lepindex[0] = i1;  Z2_lepindex[1] = i2; }
              else { Z2_lepindex[0] = i2;  Z2_lepindex[1] = i1; }
              Z1DeltaM = abs(Zj.M()-Zmass);
              Z2SumPt = lep_i1_nofsr.Pt()+lep_i2_nofsr.Pt();
              //                 if(isMuonZj) isMuon = true;
              //                 else isMuon = false;
          }

          // Check isolation cut (without FSR ) for Z1 leptons
          if ((*lep_RelIsoNoFSR)[Z1_lepindex[0]]>((abs(lep_id[Z1_lepindex[0]])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed
          if ((*lep_RelIsoNoFSR)[Z1_lepindex[1]]>((abs(lep_id[Z1_lepindex[1]])==11) ? isoCutEl : isoCutMu)) continue; // checking iso with FSR removed
          // Check tight ID cut for Z1 leptons
          if (!((*lep_tightId)[Z1_lepindex[0]])) continue; // checking tight lepton ID
          if (!((*lep_tightId)[Z1_lepindex[1]])) continue; // checking tight lepton ID

          // Check Leading and Subleading pt Cut
          vector<double> allPt;
          allPt.push_back(lep_i1_nofsr.Pt()); allPt.push_back(lep_i2_nofsr.Pt());
          allPt.push_back(lep_j1_nofsr.Pt()); allPt.push_back(lep_j2_nofsr.Pt());
          std::sort(allPt.begin(), allPt.end());
          if (verbose) cout<<" leading pt: "<<allPt[3]<<" cut: "<<leadingPtCut<<" subleadingPt: "<<allPt[2]<<" cut: "<<subleadingPtCut<<endl;
          if (allPt[3]<leadingPtCut || allPt[2]<subleadingPtCut ) continue;

          // Check dR(li,lj)>0.02 for any i,j
          vector<double> alldR;
          alldR.push_back(deltaR(lep_i1_nofsr.Eta(),lep_i1_nofsr.Phi(),lep_i2_nofsr.Eta(),lep_i2_nofsr.Phi()));
          alldR.push_back(deltaR(lep_i1_nofsr.Eta(),lep_i1_nofsr.Phi(),lep_j1_nofsr.Eta(),lep_j1_nofsr.Phi()));
          alldR.push_back(deltaR(lep_i1_nofsr.Eta(),lep_i1_nofsr.Phi(),lep_j2_nofsr.Eta(),lep_j2_nofsr.Phi()));
          alldR.push_back(deltaR(lep_i2_nofsr.Eta(),lep_i2_nofsr.Phi(),lep_j1_nofsr.Eta(),lep_j1_nofsr.Phi()));
          alldR.push_back(deltaR(lep_i2_nofsr.Eta(),lep_i2_nofsr.Phi(),lep_j2_nofsr.Eta(),lep_j2_nofsr.Phi()));
          alldR.push_back(deltaR(lep_j1_nofsr.Eta(),lep_j1_nofsr.Phi(),lep_j2_nofsr.Eta(),lep_j2_nofsr.Phi()));
          if (verbose) cout<<" minDr: "<<*min_element(alldR.begin(),alldR.end())<<endl;
          if (*min_element(alldR.begin(),alldR.end())<0.02) continue;

          // Check M(l+,l-)>4.0 GeV for any OS pair
          // Do not include FSR photons
          vector<double> allM;
          TLorentzVector i1i2;
          TLorentzVector _4l_temp;
          i1i2 = (lep_i1_nofsr)+(lep_i2_nofsr); allM.push_back(i1i2.M());
          TLorentzVector j1j2;
          j1j2 = (lep_j1_nofsr)+(lep_j2_nofsr); allM.push_back(j1j2.M());
          _4l_temp = Z1 + Z2;

          if (lep_id[i1]*lep_id[j1]<0) {
              TLorentzVector i1j1;
              i1j1 = (lep_i1_nofsr)+(lep_j1_nofsr); allM.push_back(i1j1.M());
              TLorentzVector i2j2;
              i2j2 = (lep_i2_nofsr)+(lep_j2_nofsr); allM.push_back(i2j2.M());
          } else {
              TLorentzVector i1j2;
              i1j2 = (lep_i1_nofsr)+(lep_j2_nofsr); allM.push_back(i1j2.M());
              TLorentzVector i2j1;
              i2j1 = (lep_i2_nofsr)+(lep_j1_nofsr); allM.push_back(i2j1.M());
          }
          if (verbose) cout<<" min m(l+l-): "<<*min_element(allM.begin(),allM.end())<<endl;
          if (*min_element(allM.begin(),allM.end())<4.0) {passedQCDcut=false; continue;}

          // Check the "smart cut": !( |mZa-mZ| < |mZ1-mZ| && mZb<12)
          // only for 4mu or 4e ZZ candidates
          bool passSmartCut=true;

          if ( abs(lep_id[i1])==abs(lep_id[j1])) {
              TLorentzVector Za, Zb;
              if (lep_id[i1]==lep_id[j1]) {
                  Za = (lep_i1)+(lep_j2);
                  Zb = (lep_i2)+(lep_j1);
              } else {
                  Za = (lep_i1)+(lep_j1);
                  Zb = (lep_i2)+(lep_j2);
              }
              if ( abs(Za.M()-Zmass)<abs(Zb.M()-Zmass) ) {
                  if (verbose) cout<<"abs(Za.M()-Zmass)-abs(Z1.M()-Zmass): "<<abs(Za.M()-Zmass)-abs(Z1.M()-Zmass)<<" Zb.M(): "<<Zb.M()<<endl;
                  if ( abs(Za.M()-Zmass)<abs(Z1.M()-Zmass) && Zb.M()<mZ2Low ) passSmartCut=false;
              }
              else {
                  if (verbose) cout<<"abs(Zb.M()-Zmass)-abs(Z1.M()-Zmass): "<<abs(Zb.M()-Zmass)-abs(Z1.M()-Zmass)<<" Za.M(): "<<Za.M()<<endl;
                  if ( abs(Zb.M()-Zmass)<abs(Z1.M()-Zmass) && Za.M()<mZ2Low ) passSmartCut=false;
              }

          }
          if (!passSmartCut) continue;

          if (verbose) cout<<" massZ1: "<<Z1.M()<<" massZ2: "<<Z2.M()<<endl;
          if ( (Z1.M() < mZ1Low) || (Z1.M() > mZ1High) || (Z2.M() < mZ2Low) || (Z2.M() > mZ2High) ) continue;

          if (verbose) cout<<" mass4l: "<<_4l_temp.M()<<endl;
          if ( _4l_temp.M() < m4lLowCut ) continue;

          // Signal region if Z2 leptons are both tight ID Iso
          bool signalRegion=true;
          if ((*lep_RelIsoNoFSR)[Z2_lepindex[0]]>((abs(lep_id[Z2_lepindex[0]])==11) ? isoCutEl : isoCutMu)) signalRegion=false; // checking iso with FSR removed
          if ((*lep_RelIsoNoFSR)[Z2_lepindex[1]]>((abs(lep_id[Z2_lepindex[1]])==11) ? isoCutEl : isoCutMu)) signalRegion=false; // checking iso with FSR removed
          if (!(lep_tightId[Z2_lepindex[0]])) signalRegion=false; // checking tight lepton ID
          if (!(lep_tightId[Z2_lepindex[1]])) signalRegion=false; // checking tight lepton ID
}
*/

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

  mergedjet_pt = new TTreeReaderArray<float>(*myreader,"mergedjet_pt");
  mergedjet_eta = new TTreeReaderArray<float>(*myreader,"mergedjet_eta");
  mergedjet_phi = new TTreeReaderArray<float>(*myreader,"mergedjet_phi");
  mergedjet_subjet_softDropMass = new TTreeReaderArray<float>(*myreader,"mergedjet_subjet_softDropMass");
  mergedjet_Net_Xbb_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_Xbb_de");
  mergedjet_Net_Xcc_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_Xcc_de");
  mergedjet_Net_Xqq_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_Xqq_de");
  mergedjet_nsubjet = new TTreeReaderArray<int>(*myreader,"mergedjet_nsubjet");
  mergedjet_subjet_pt = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_pt");
  mergedjet_subjet_eta = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_eta");
  mergedjet_subjet_phi = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_phi");
  mergedjet_subjet_mass = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_mass");

  passedEventsTree_All->Branch("mass2jet",&mass2jet);
  passedEventsTree_All->Branch("pt2jet",&pt2jet);
  passedEventsTree_All->Branch("mass2l",&mass2l);
  passedEventsTree_All->Branch("pt2l",&pt2l);
  passedEventsTree_All->Branch("mass2l2jet",&mass2l2jet);
  passedEventsTree_All->Branch("mass2lj",&mass2lj);
  passedEventsTree_All->Branch("KD_jjVBF",&KD_jjVBF);
  passedEventsTree_All->Branch("KD_jVBF",&KD_jVBF);
  passedEventsTree_All->Branch("particleNetZvsQCD",&particleNetZvsQCD);
  passedEventsTree_All->Branch("massmerged",&massmerged);
  passedEventsTree_All->Branch("ptmerged",&ptmerged);
  passedEventsTree_All->Branch("nsubjet",&nsubjet);
  passedEventsTree_All->Branch("passedfullmerged",&passedfullmerged);
  passedEventsTree_All->Branch("passedfullresolved",&passedfullresolved);
  passedEventsTree_All->Branch("associatedjet_pt",&associatedjet_pt);
  passedEventsTree_All->Branch("associatedjet_eta",&associatedjet_eta);
  passedEventsTree_All->Branch("associatedjet_phi",&associatedjet_phi);
  passedEventsTree_All->Branch("associatedjet_mass",&associatedjet_mass);

}
