#include "TreeLoop.h"

//construtor
TreeLoop::TreeLoop(TString inputfile, TString outputfile, string year, string melafile){

  if(strstr(inputfile,"MuonEG") || strstr(inputfile,"DoubleMuon") || strstr(inputfile,"SingleMuon") || strstr(inputfile,"SingleElectron") || strstr(inputfile,"DoubleEG") || strstr(inputfile,"EGamma")){
    isData = true;
    cout<<"This is Data process"<<endl;
  }else{
    isMC = true;
    cout<<"This is MC process"<<endl;
    if(inputfile.Contains("GluGluHToZZTo2L2Q") || inputfile.Contains("VBF_HToZZTo2L2Q")){
      SetCrossSection(inputfile);
      std::cout << "Cross Section Value: " << xsec << std::endl;
    }
  }

  //tempyear = static_cast<int>(year);
  //set up splited jes uncertainty source
  tempyear = stoi(year); //convert string to int
  if(tempyear==2016){
    jecUncFile_ = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/ANATree/data/RegroupedV2_Summer16_07Aug2017_V11_MC_UncertaintySources_AK4PFchs.txt";
    uncSources.push_back("Total");
    uncSources.push_back("Absolute"); uncSources.push_back("Absolute_2016");
    uncSources.push_back("BBEC1"); uncSources.push_back("BBEC1_2016");
    uncSources.push_back("EC2"); uncSources.push_back("EC2_2016");
    uncSources.push_back("FlavorQCD");
    uncSources.push_back("HF"); uncSources.push_back("HF_2016");
    uncSources.push_back("RelativeBal");
    uncSources.push_back("RelativeSample_2016");
    ////['Absolute', 'Absolute_2016', 'BBEC1', 'BBEC1_2016', 'EC2', 'EC2_2016', 'FlavorQCD', 'HF', 'HF_2016', 'RelativeBal', 'RelativeSample_2016']='total'
  }else if(tempyear==2017){
    jecUncFile_ = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/ANATree/data/RegroupedV2_Fall17_17Nov2017_V32_MC_UncertaintySources_AK4PFchs.txt";
    uncSources.push_back("Total");
    uncSources.push_back("Absolute"); uncSources.push_back("Absolute_2017");
    uncSources.push_back("BBEC1"); uncSources.push_back("BBEC1_2017");
    uncSources.push_back("EC2"); uncSources.push_back("EC2_2017");
    uncSources.push_back("FlavorQCD");
    uncSources.push_back("HF"); uncSources.push_back("HF_2017");
    uncSources.push_back("RelativeBal");
    uncSources.push_back("RelativeSample_2017"); 
    //['Absolute', 'Absolute_2017', 'BBEC1', 'BBEC1_2017', 'EC2', 'EC2_2017', 'FlavorQCD', 'HF', 'HF_2017', 'RelativeBal', 'RelativeSample_2017'] + 'Total'
  }else if(tempyear==2018){
    jecUncFile_ = "/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/ANATree/data/RegroupedV2_Autumn18_V19_MC_UncertaintySources_AK4PFchs.txt";
    uncSources.push_back("Total");
    uncSources.push_back("Absolute"); uncSources.push_back("Absolute_2018");
    uncSources.push_back("BBEC1"); uncSources.push_back("BBEC1_2018");
    uncSources.push_back("EC2"); uncSources.push_back("EC2_2018");
    uncSources.push_back("FlavorQCD");
    uncSources.push_back("HF"); uncSources.push_back("HF_2018");
    uncSources.push_back("RelativeBal");
    uncSources.push_back("RelativeSample_2018");
    //['Absolute', 'Absolute_2018', 'BBEC1', 'BBEC1_2018', 'EC2', 'EC2_2018', 'FlavorQCD', 'HF', 'HF_2018', 'RelativeBal', 'RelativeSample_2018'] + 'Total'
  }

  //jecsplit
  if(isMC){
    for(unsigned s_unc = 0; s_unc < uncSources.size(); s_unc++){
      JetCorrectorParameters ak4corrParams = JetCorrectorParameters(jecUncFile_, uncSources[s_unc]);
      JetCorrectorParameters ak8corrParams = JetCorrectorParameters(jecUncFile_, uncSources[s_unc]);
      ak4splittedUncerts_.push_back(new JetCorrectionUncertainty(ak4corrParams));
      ak8splittedUncerts_.push_back(new JetCorrectionUncertainty(ak8corrParams));
      cout<<"uncSources["<<s_unc<<"]"<<uncSources[s_unc]<<endl;
      cout<<"ak4splittedUncerts_["<<s_unc<<"]"<<ak4splittedUncerts_[s_unc]<<endl;
    }
  }
  
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
  TH1F *temph = (TH1F*)oldfile->Get("Ana/sumWeights");
  SumWeight = temph->GetBinContent(1);

  CrossSectionWeight = 1000*xsec/SumWeight;

  TH1F *nEvents = (TH1F*)oldfile->Get("Ana/nEvents");
  nentries = nEvents->GetBinContent(1);

  outfile = new TFile(outputfile,"recreate");
  passedEventsTree_All = new TTree("passedEvents","passedEvents");

  //set up mela
  if(doMela){
    if(verbose){cout<<"[INFO] setup MELA using "<< melafile <<endl;}
    cout<<"[INFO] setup MELA using "<< melafile <<endl;
    SetMEsFile(melafile);
  }else{
    if(verbose){cout<<"[INFO] skip MELA"<<endl;}
  }

  if(verbose){cout<<"[INFO] construtor done"<<endl;}

}

//destructor
TreeLoop::~TreeLoop(){}

//==============================================================================================================//
void TreeLoop::Loop(){
  if(verbose){cout<<"[INFO] start to event loop"<<endl;}

  //if(doMela){
  //  if(verbose){cout<<"[INFO] setup MELA"<<endl;}
  //  SetMEsFile();
//
  //}else{
  //  if(verbose){cout<<"[INFO] skip MELA"<<endl;}
  //}

  //===================start event loop==========================================
  setTree();
  //KDZjj========================================================================
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_Zjj "<<endl;
  vector<DiscriminantClasses::Type> KDtypes_Zjj{DiscriminantClasses::KDZjj};
  unsigned int const nKDs_Zjj = KDtypes_Zjj.size();
  if(verbose) cout<<"[INFO] constuct Discriminant list for KD_Zjj "<<endl;
  vector<DiscriminantClasses::KDspecs> KDlist_Zjj;
  KDlist_Zjj.reserve(nKDs_Zjj);
  for (auto const& KDtype:KDtypes_Zjj) KDlist_Zjj.emplace_back(KDtype);
  if(verbose) cout<<"[INFO] call constuct class for KD_Zjj"<<endl;
  DiscriminantClasses::constructDiscriminants(KDlist_Zjj, 169*121, "JJVBFTagged");
  //KDZjj_up
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_Zjj_up "<<endl;
  vector<DiscriminantClasses::Type> KDtypes_Zjj_up{DiscriminantClasses::KDZjj};
  unsigned int const nKDs_Zjj_up = KDtypes_Zjj_up.size();
  if(verbose) cout<<"[INFO] constuct Discriminant list for KD_Zjj_up "<<endl;
  vector<DiscriminantClasses::KDspecs> KDlist_Zjj_up;
  KDlist_Zjj_up.reserve(nKDs_Zjj_up);
  for (auto const& KDtype:KDtypes_Zjj_up) KDlist_Zjj_up.emplace_back(KDtype);
  if(verbose) cout<<"[INFO] call constuct class for KD_Zjj"<<endl;
  DiscriminantClasses::constructDiscriminants(KDlist_Zjj_up, 169*121, "JJVBFTagged");
  //KDZjj_dn
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_Zjj_dn "<<endl;
  vector<DiscriminantClasses::Type> KDtypes_Zjj_dn{DiscriminantClasses::KDZjj};
  unsigned int const nKDs_Zjj_dn = KDtypes_Zjj_dn.size();
  if(verbose) cout<<"[INFO] constuct Discriminant list for KD_Zjj_dn "<<endl;
  vector<DiscriminantClasses::KDspecs> KDlist_Zjj_dn;
  KDlist_Zjj_dn.reserve(nKDs_Zjj_dn);
  for (auto const& KDtype:KDtypes_Zjj_dn) KDlist_Zjj_dn.emplace_back(KDtype);
  if(verbose) cout<<"[INFO] call constuct class for KD_Zjj_dn"<<endl;
  DiscriminantClasses::constructDiscriminants(KDlist_Zjj_dn, 169*121, "JJVBFTagged");
  //KD_ZJ========================================================================
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_ZJ "<<endl;
  vector<DiscriminantClasses::Type> KDtypes_ZJ{DiscriminantClasses::KDZjj};
  unsigned int const nKDs_ZJ = KDtypes_ZJ.size();
  if(verbose) cout<<"[INFO] constuct Discriminant list for KD_ZJ "<<endl;
  vector<DiscriminantClasses::KDspecs> KDlist_ZJ;
  KDlist_ZJ.reserve(nKDs_ZJ);
  for (auto const& KDtype:KDtypes_ZJ) KDlist_ZJ.emplace_back(KDtype);
  if(verbose) cout<<"[INFO] call constuct class for KD_ZJ"<<endl;
  DiscriminantClasses::constructDiscriminants(KDlist_ZJ, 169*121, "JJVBFTagged");
  //up
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_ZJ_up "<<endl;
  vector<DiscriminantClasses::Type> KDtypes_ZJ_up{DiscriminantClasses::KDZjj};
  unsigned int const nKDs_ZJ_up = KDtypes_ZJ_up.size();
  if(verbose) cout<<"[INFO] constuct Discriminant list for KD_ZJ_up "<<endl;
  vector<DiscriminantClasses::KDspecs> KDlist_ZJ_up;
  KDlist_ZJ_up.reserve(nKDs_ZJ_up);
  for (auto const& KDtype:KDtypes_ZJ_up) KDlist_ZJ_up.emplace_back(KDtype);
  if(verbose) cout<<"[INFO] call constuct class for KD_ZJ_up"<<endl;
  DiscriminantClasses::constructDiscriminants(KDlist_ZJ_up, 169*121, "JJVBFTagged");
  //dn
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_ZJ_dn "<<endl;
  vector<DiscriminantClasses::Type> KDtypes_ZJ_dn{DiscriminantClasses::KDZjj};
  unsigned int const nKDs_ZJ_dn = KDtypes_ZJ_dn.size();
  if(verbose) cout<<"[INFO] constuct Discriminant list for KD_ZJ_dn "<<endl;
  vector<DiscriminantClasses::KDspecs> KDlist_ZJ_dn;
  KDlist_ZJ_dn.reserve(nKDs_ZJ_dn);
  for (auto const& KDtype:KDtypes_ZJ_dn) KDlist_ZJ_dn.emplace_back(KDtype);
  if(verbose) cout<<"[INFO] call constuct class for KD_ZJ_dn"<<endl;
  DiscriminantClasses::constructDiscriminants(KDlist_ZJ_dn, 169*121, "JJVBFTagged");

  //KD_jjVBF========================================================================
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_VBF"<<endl;
  vector<DiscriminantClasses::Type> KDtypes{DiscriminantClasses::kDjjVBF};
  unsigned int const nKDs = KDtypes.size();
  vector<DiscriminantClasses::KDspecs> KDlist;
  KDlist.reserve(nKDs);
  for (auto const& KDtype:KDtypes) KDlist.emplace_back(KDtype);
  DiscriminantClasses::constructDiscriminants(KDlist, 169*121, "JJVBFTagged");

  //KD_jVBf for resolved case========================================================================
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_jVBF"<<endl;
  vector<DiscriminantClasses::Type> KDtypes_jVBF{DiscriminantClasses::kDjVBF};
  unsigned int const nKDs_jVBF = KDtypes_jVBF.size();
  vector<DiscriminantClasses::KDspecs> KDlist_jVBF;
  KDlist_jVBF.reserve(nKDs_jVBF);
  for (auto const& KDtype:KDtypes_jVBF) KDlist_jVBF.emplace_back(KDtype);
  DiscriminantClasses::constructDiscriminants(KDlist_jVBF, 169*121, "JJVBFTagged");

  //KD_JJVBF========================================================================
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_JJVBF"<<endl;
  vector<DiscriminantClasses::Type> KDtypes_JJVBF{DiscriminantClasses::kDjjVBF};
  unsigned int const nKDs_JJVBF = KDtypes_JJVBF.size();
  vector<DiscriminantClasses::KDspecs> KDlist_JJVBF;
  KDlist_JJVBF.reserve(nKDs_JJVBF);
  for (auto const& KDtype:KDtypes_JJVBF) KDlist_JJVBF.emplace_back(KDtype);
  DiscriminantClasses::constructDiscriminants(KDlist_JJVBF, 169*121, "JJVBFTagged");
  //KD_JVBF========================================================================
  if(verbose) cout<<"[INFO] constuct DiscriminantClasses objet for KD_JVBF"<<endl;
  vector<DiscriminantClasses::Type> KDtypes_JVBF{DiscriminantClasses::kDjVBF};
  unsigned int const nKDs_JVBF = KDtypes_JVBF.size();
  vector<DiscriminantClasses::KDspecs> KDlist_JVBF;
  KDlist_JVBF.reserve(nKDs_JVBF);
  for (auto const& KDtype:KDtypes_JVBF) KDlist_JVBF.emplace_back(KDtype);
  DiscriminantClasses::constructDiscriminants(KDlist_JVBF, 169*121, "JJVBFTagged");

  //jecsplit
  if(isMC){
    for(unsigned s_unc = 0; s_unc < uncSources.size(); s_unc++){
      JetCorrectorParameters ak4corrParams = JetCorrectorParameters(jecUncFile_, uncSources[s_unc]);
      JetCorrectorParameters ak8corrParams = JetCorrectorParameters(jecUncFile_, uncSources[s_unc]);
      ak4splittedUncerts_.push_back(new JetCorrectionUncertainty(ak4corrParams));
      ak8splittedUncerts_.push_back(new JetCorrectionUncertainty(ak8corrParams));
      cout<<"uncSources["<<s_unc<<"]"<<uncSources[s_unc]<<endl;
      cout<<"ak4splittedUncerts_["<<s_unc<<"]"<<ak4splittedUncerts_[s_unc]<<endl;
    }
  }

  if(verbose){cout<<"[INFO]============loop tree reader========================"<<endl;}
  int nevents_negative = 0;
  int npassed_resolved = 0;
  int times_calculation_KD_jjVBF = 0;
  int n_negative_KD_jjVBF_resolved  = 0;
  int n_events_associatedjets_lesstwo_resolved = 0;

  int n_times_calculation_KD_jVBF_resolved = 0;
  int n_associatedjets_0_resolved = 0;
  int n_negative_KD_jVBF_resolved = 0;

  int n_passed_merged = 0;
  int n_negative_KD_VBF_merged = 0;
  int n_negative_KD_jjVBF_merged = 0;
  int n_times_calculation_KD_jjVBF_merged = 0;
  int n_events_associatedjets_lesstwo_merged = 0;

  int n_times_calculation_KD_jVBF_merged = 0;
  int n_associatedjets_0_merged = 0;
  int n_negative_KD_jVBF_merged = 0;


  int ievent = 0;
  //loop
  while (myreader->Next()) {
    ievent++;
    if(ievent%10000==0){
      cout<<ievent<<"/"<<nentries<<std::endl;
    }
    if(ievent==20000){break;} //test for 50000 events

    initialize(); // initialize all menber datas

    //setup GEN variables excipt for VBF variables
    if(isMC){
      if(verbose) cout<<"[INFO] start GEN analysis"<<endl;
      SetGen();
      if(verbose) cout<<"[INFO] GEN analysis done"<<endl;
    }

    if(!(*(*passedTrig))){
      if(verbose){cout<<"[INFO] failed pass trigger,skip to next tree loop"<<endl;}
      continue;
    }else{
      if(verbose){cout<<"[INFO] pass trigger"<<endl;}
      passed_trig++;
    }

    if(verbose){
      if(lep_pt->GetSize()>0){
        if(verbose) cout<<"[INFO] this lep pt = "<<(*lep_pt)[0]<<endl;
      }

    }

    Met = *(*met);
    Met_phi = *(*met_phi);

    //save then number of ak4 jets and ak8 jets
    n_jets = jet_pt->GetSize();
    n_mergedjets = mergedjet_pt->GetSize();

    if(verbose){cout<<"[INFO] try to find higgs candidate"<<endl;}
    findZ1LCandidate();
    findZ2JCandidata();
    findZ2MergedCandidata();
    if(verbose){cout<<"[INFO] find higgs candidate done"<<endl;}
    /*
    if((!foundZ1LCandidate) || (!foundZ2JCandidate)){
      if(verbose){cout<<"[INFO] no higgs candidate in this event, skip to next event loop"<<endl;}
      continue;
    } //found Higg 2L2Q candidate
    if(verbose){cout<<"[INFO] higgs candidate is found in this event"<<endl;}
    */

    if(isMC){
      if(verbose) cout<<"[INFO] start VBF GEN analysis"<<endl;
      SetVBFGen();
      if(verbose) cout<<"[INFO] VBF GEN analysis done"<<endl;
    }

    //at least have a leptoinc Z in evnets
    if(!found2lepCandidate) continue;
    run = *(*Run);
    event = *(*Event);
    lumiSect = *(*LumiSect);

    EventWeight = *(*eventWeight)*(*lep_dataMC)[lep_Z1index[0]]*(*lep_dataMC)[lep_Z1index[1]];
    GenWeight = *(*genWeight);
    PileupWeight = *(*pileupWeight);
    PrefiringWeight = *(*prefiringWeight);
    
    if(abs((*lep_id)[lep_Z1index[0]])==13 && abs((*lep_id)[lep_Z1index[1]])==13){ isMuMu = true;}
    if(abs((*lep_id)[lep_Z1index[0]])==11 && abs((*lep_id)[lep_Z1index[1]])==11){ isEE = true;}

    if(foundZ2MergedCandidata && isMC){
      int nbhadron = (*mergedjet_nbHadrons)[merged_Z1index];
      int nchadron = (*mergedjet_ncHadrons)[merged_Z1index];

      if(nbhadron>=1){ isbjet = true; }
      else if(nchadron>=1 && nbhadron==0){ iscjet = true; }
      else if(nbhadron==0 && nchadron==0) { islightjet = true;}

    }

    if(foundZ2MergedCandidata) {
      passed_MergedolonlyHiggs++;
      foundZ2JCandidate=false;
      foundZ2JCandidate_up=false;
      foundZ2JCandidate_dn=false;
    }
    else{passed_resovedonlyHiggs++;}

    //================================
    //====resolved category============
    //================================
    if(foundZ2JCandidate){
      //split JEC UnCertainty
      vector<float> jes_unc_split {};
      vector<float> pt_jesup_split {};
      vector<float> pt_jesdn_split {};
      float singleContr_jes_unc = 0;
      if(isMC){

        for(unsigned s_unc = 0; s_unc < uncSources.size(); s_unc++){
			    singleContr_jes_unc = 0;
			    ak4splittedUncerts_[s_unc]->setJetEta((*jet_eta)[jet_Z1index[0]]);
			    ak4splittedUncerts_[s_unc]->setJetPt((*jet_pt)[jet_Z1index[0]]);
			    singleContr_jes_unc = ak4splittedUncerts_[s_unc]->getUncertainty(true); 
			    jes_unc_split.push_back(singleContr_jes_unc);
			    pt_jesup_split.push_back( (*jet_pt)[jet_Z1index[0]] * (1.0 + singleContr_jes_unc));
			    pt_jesdn_split.push_back( (*jet_pt)[jet_Z1index[0]] * (1.0 - singleContr_jes_unc));
        }
      }else{
        jes_unc_split.push_back(-999.);
			  pt_jesup_split.push_back(-999.);
			  pt_jesdn_split.push_back(-999.);
      }
      jet_1_jesunc_split_Total=jes_unc_split[0]; 
      jet_1_jesunc_split_Abs=jes_unc_split[1]; 
      jet_1_jesunc_split_Abs_year=jes_unc_split[2]; 
      jet_1_jesunc_split_BBEC1=jes_unc_split[3]; 
      jet_1_jesunc_split_BBEC1_year=jes_unc_split[4];
      jet_1_jesunc_split_EC2=jes_unc_split[5]; 
      jet_1_jesunc_split_EC2_year=jes_unc_split[6]; 
      jet_1_jesunc_split_FlavQCD=jes_unc_split[7]; 
      jet_1_jesunc_split_HF=jes_unc_split[8]; 
      jet_1_jesunc_split_HF_year=jes_unc_split[9];
      jet_1_jesunc_split_RelBal=jes_unc_split[10]; 
      jet_1_jesunc_split_RelSample_year=jes_unc_split[11];

      jetpt_1_jesup_split_Total=pt_jesup_split[0]; 
      jetpt_1_jesup_split_Abs=pt_jesup_split[1]; 
      jetpt_1_jesup_split_Abs_year=pt_jesup_split[2]; 
      jetpt_1_jesup_split_BBEC1=pt_jesup_split[3]; 
      jetpt_1_jesup_split_BBEC1_year=pt_jesup_split[4];
      jetpt_1_jesup_split_EC2=pt_jesup_split[5]; 
      jetpt_1_jesup_split_EC2_year=pt_jesup_split[6]; 
      jetpt_1_jesup_split_FlavQCD=pt_jesup_split[7]; 
      jetpt_1_jesup_split_HF=pt_jesup_split[8]; 
      jetpt_1_jesup_split_HF_year=pt_jesup_split[9];
      jetpt_1_jesup_split_RelBal=pt_jesup_split[10]; 
      jetpt_1_jesup_split_RelSample_year=pt_jesup_split[11];
	    //dn	
      jetpt_1_jesdn_split_Total=pt_jesdn_split[0]; 
      jetpt_1_jesdn_split_Abs=pt_jesdn_split[1]; 
      jetpt_1_jesdn_split_Abs_year=pt_jesdn_split[2]; 
      jetpt_1_jesdn_split_BBEC1=pt_jesdn_split[3]; 
      jetpt_1_jesdn_split_BBEC1_year=pt_jesdn_split[4];
      jetpt_1_jesdn_split_EC2=pt_jesdn_split[5]; 
      jetpt_1_jesdn_split_EC2_year=pt_jesdn_split[6]; 
      jetpt_1_jesdn_split_FlavQCD=pt_jesdn_split[7]; 
      jetpt_1_jesdn_split_HF=pt_jesdn_split[8]; 
      jetpt_1_jesdn_split_HF_year=pt_jesdn_split[9];
      jetpt_1_jesdn_split_RelBal=pt_jesdn_split[10]; 
      jetpt_1_jesdn_split_RelSample_year=pt_jesdn_split[11];

      ////jet 2
      jes_unc_split.clear();
      pt_jesup_split.clear();
      pt_jesdn_split.clear();
      singleContr_jes_unc = 0;
      if(isMC){

        for(unsigned s_unc = 0; s_unc < uncSources.size(); s_unc++){
			    singleContr_jes_unc = 0;
			    ak4splittedUncerts_[s_unc]->setJetEta((*jet_eta)[jet_Z1index[1]]);
			    ak4splittedUncerts_[s_unc]->setJetPt((*jet_pt)[jet_Z1index[1]]);
			    singleContr_jes_unc = ak4splittedUncerts_[s_unc]->getUncertainty(true); 
			    jes_unc_split.push_back(singleContr_jes_unc);
			    pt_jesup_split.push_back( (*jet_pt)[jet_Z1index[1]] * (1.0 + singleContr_jes_unc));
			    pt_jesdn_split.push_back( (*jet_pt)[jet_Z1index[1]] * (1.0 - singleContr_jes_unc));
        }
      }else{
        jes_unc_split.push_back(-999.);
			  pt_jesup_split.push_back(-999.);
			  pt_jesdn_split.push_back(-999.);
      }
      jet_2_jesunc_split_Total=jes_unc_split[0]; 
      jet_2_jesunc_split_Abs=jes_unc_split[1]; 
      jet_2_jesunc_split_Abs_year=jes_unc_split[2]; 
      jet_2_jesunc_split_BBEC1=jes_unc_split[3]; 
      jet_2_jesunc_split_BBEC1_year=jes_unc_split[4];
      jet_2_jesunc_split_EC2=jes_unc_split[5]; 
      jet_2_jesunc_split_EC2_year=jes_unc_split[6]; 
      jet_2_jesunc_split_FlavQCD=jes_unc_split[7]; 
      jet_2_jesunc_split_HF=jes_unc_split[8]; 
      jet_2_jesunc_split_HF_year=jes_unc_split[9];
      jet_2_jesunc_split_RelBal=jes_unc_split[10]; 
      jet_2_jesunc_split_RelSample_year=jes_unc_split[11];

      jetpt_2_jesup_split_Total=pt_jesup_split[0]; 
      jetpt_2_jesup_split_Abs=pt_jesup_split[1]; 
      jetpt_2_jesup_split_Abs_year=pt_jesup_split[2]; 
      jetpt_2_jesup_split_BBEC1=pt_jesup_split[3]; 
      jetpt_2_jesup_split_BBEC1_year=pt_jesup_split[4];
      jetpt_2_jesup_split_EC2=pt_jesup_split[5]; 
      jetpt_2_jesup_split_EC2_year=pt_jesup_split[6]; 
      jetpt_2_jesup_split_FlavQCD=pt_jesup_split[7];
      jetpt_2_jesup_split_HF=pt_jesup_split[8]; 
      jetpt_2_jesup_split_HF_year=pt_jesup_split[9];
      jetpt_2_jesup_split_RelBal=pt_jesup_split[10]; 
      jetpt_2_jesup_split_RelSample_year=pt_jesup_split[11];
	    //dn	
      jetpt_2_jesdn_split_Total=pt_jesdn_split[0]; 
      jetpt_2_jesdn_split_Abs=pt_jesdn_split[1]; 
      jetpt_2_jesdn_split_Abs_year=pt_jesdn_split[2]; 
      jetpt_2_jesdn_split_BBEC1=pt_jesdn_split[3]; 
      jetpt_2_jesdn_split_BBEC1_year=pt_jesdn_split[4];
      jetpt_2_jesdn_split_EC2=pt_jesdn_split[5]; 
      jetpt_2_jesdn_split_EC2_year=pt_jesdn_split[6]; 
      jetpt_2_jesdn_split_FlavQCD=pt_jesdn_split[7]; 
      jetpt_2_jesdn_split_HF=pt_jesdn_split[8]; 
      jetpt_2_jesdn_split_HF_year=pt_jesdn_split[9];
      jetpt_2_jesdn_split_RelBal=pt_jesdn_split[10]; 
      jetpt_2_jesdn_split_RelSample_year=pt_jesdn_split[11];


      TLorentzVector p4_ZZ, Lep1, Lep2, Jet1,Jet2;
      Lep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
      Lep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
      Jet1.SetPtEtaPhiM((*jet_pt)[jet_Z1index[0]],(*jet_eta)[jet_Z1index[0]],(*jet_phi)[jet_Z1index[0]],(*jet_mass)[jet_Z1index[0]]);
      Jet2.SetPtEtaPhiM((*jet_pt)[jet_Z1index[1]],(*jet_eta)[jet_Z1index[1]],(*jet_phi)[jet_Z1index[1]],(*jet_mass)[jet_Z1index[1]]);

      p4_ZZ = Lep1 + Lep2 + Jet1 + Jet2;
      mass2l2jet = p4_ZZ.M(); //mass2l2jet_up = p4_ZZ_up.M(); mass2l2jet_dn = p4_ZZ_dn.M();

      TLorentzVector Jet1_mass_bais, Jet2_mass_bais;
      Jet1_mass_bais.SetPtEtaPhiM((*jet_pt)[jet_Z1index_mass_bais[0]],(*jet_eta)[jet_Z1index_mass_bais[0]],(*jet_phi)[jet_Z1index_mass_bais[0]],(*jet_mass)[jet_Z1index_mass_bais[0]]);
      Jet2_mass_bais.SetPtEtaPhiM((*jet_pt)[jet_Z1index_mass_bais[1]],(*jet_eta)[jet_Z1index_mass_bais[1]],(*jet_phi)[jet_Z1index_mass_bais[1]],(*jet_mass)[jet_Z1index_mass_bais[1]]);

      mass2l2jet_mass_bais = (Lep1 + Lep2 + Jet1_mass_bais + Jet2_mass_bais).M();
      //cout<<"this mass2l2jet = "<< mass2l2jet<<endl;

      if(foundZ1LCandidate){
        npassed_resolved++;
        if (doMela){
          //check number of associated jets
          int njets = jet_pt->GetSize();
          int nassociatedjets = 0;
          vector<TLorentzVector> associatedjets;
          for(int i=0; i<njets; i++){

            //find jet that are not signal and put it into associated
            if(i==jet_Z1index[0] || i==jet_Z1index[1]){continue;}

            TLorentzVector thisjet;
            thisjet.SetPtEtaPhiM((*jet_pt)[i],(*jet_eta)[i],(*jet_phi)[i],(*jet_mass)[i]);
            
            nassociatedjets++;
            associatedjets.push_back(thisjet);
            associatedjetsjj_index.push_back(i);
          }

          TLorentzVector selectedLep1,selectedLep2,selectedJet1,selectedJet2;
          selectedLep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
          selectedLep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
          selectedJet1.SetPtEtaPhiM((*jet_pt)[jet_Z1index[0]],(*jet_eta)[jet_Z1index[0]],(*jet_phi)[jet_Z1index[0]],(*jet_mass)[jet_Z1index[0]]);
          selectedJet2.SetPtEtaPhiM((*jet_pt)[jet_Z1index[1]],(*jet_eta)[jet_Z1index[1]],(*jet_phi)[jet_Z1index[1]],(*jet_mass)[jet_Z1index[1]]);

          SimpleParticleCollection_t daughters;
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1));
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2));
          daughters.push_back(SimpleParticle_t(0, selectedJet1));
          daughters.push_back(SimpleParticle_t(0, selectedJet2));

          //cout<<" fill daughters done "<<endl;

          //associated objets
          SimpleParticleCollection_t associated;
          //sort associatedjets as pt order
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          if(nassociatedjets>0){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_leadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(associatedjets[i].Pt()>temp_leadingpt){
                temp_leadingpt = associatedjets[i].Pt();
                leading_index[0]= i;
              }
            }
            //push_back the leading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[0]]));
            //cout<<"associatedjet1: px="<<associatedjets[leading_index[0]].Px()<<" Py="<<associatedjets[leading_index[0]].Py()<<" Pz="<<associatedjets[leading_index[0]].Pz()<<" E="<<associatedjets[leading_index[0]].E()<<endl;
            //store variables for associate jet
            associatedjetjj_pt.push_back(associatedjets[leading_index[0]].Pt());
            associatedjetjj_eta.push_back(associatedjets[leading_index[0]].Eta());
            associatedjetjj_phi.push_back(associatedjets[leading_index[0]].Phi());
            associatedjetjj_mass.push_back(associatedjets[leading_index[0]].M());
          }
          if(nassociatedjets>1){
            if(verbose) cout<<"[INFO] second associatedjets"<<endl;
            double temp_subleadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(i==leading_index[0]) continue; //do not count leading jet
              if(associatedjets[i].Pt()>temp_subleadingpt){
                temp_subleadingpt = associatedjets[i].Pt();
                leading_index[1]= i;
              }
            }
            //push_back the subleading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[1]]));
            //compute delta eta between two associated jets
            time_associatedjetjj_eta = associatedjets[leading_index[0]].Eta()*associatedjets[leading_index[1]].Eta();
            //cout<<"associatedjet2: px="<<associatedjets[leading_index[1]].Px()<<" Py="<<associatedjets[leading_index[1]].Py()<<" Pz="<<associatedjets[leading_index[1]].Pz()<<" E="<<associatedjets[leading_index[1]].E()<<endl;
            //store variables for associate jet
            associatedjetjj_pt.push_back(associatedjets[leading_index[1]].Pt());
            associatedjetjj_eta.push_back(associatedjets[leading_index[1]].Eta());
            associatedjetjj_phi.push_back(associatedjets[leading_index[1]].Phi());
            associatedjetjj_mass.push_back(associatedjets[leading_index[1]].M());

            //match to turth 
            if(isMC){
              if((associatedjetsjj_index[leading_index[0]] == match1_recoindex || associatedjetsjj_index[leading_index[0]] == match2_recoindex) && (associatedjetsjj_index[leading_index[1]] == match1_recoindex || associatedjetsjj_index[leading_index[1]] == match2_recoindex)){
                passedmatchtruthVBF_jj=true;
              }
            }

          }
          if(verbose) cout<<"[INFO] associatedjet set done"<<endl;

          //if(verbose) cout<<"[INFO] associatedjet set done"<<endl;

          //cout<<" fill VBF jet done "<<endl;

          IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
          IvyMELAHelpers::melaHandle->setInputEvent(&daughters, &associated, nullptr, false);
          MEblock.computeMELABranches();
          MEblock.pushMELABranches();

          IvyMELAHelpers::melaHandle->resetInputEvent();

          //KD
          //retrieve MEs for KD constructing
          unordered_map<string,float> ME_Kfactor_values;
          MEblock.getBranchValues(ME_Kfactor_values);

          //KDZjj=========================================================================
          //Update discriminants
          if(verbose) cout<<"[INFO] Get Discriminant for KD_Zjj "<<endl;
          for (auto& KDspec:KDlist_Zjj){
            std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
            for (auto const& strKDvar:KDspec.KDvars){
              KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
            } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

            KDspec.KD->update(KDvars, mass2l2jet); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_Zjj = *(KDspec.KD);
            if(verbose) cout<<"[INFO] This KD_Zjj = "<<KD_Zjj<<endl;
          }

          //KDjjVBF=========================================================================
          if(nassociatedjets>=2){ //compute KD_jjVBF
            times_calculation_KD_jjVBF ++;
            if(verbose) cout<<"[INFO] found at least two nassociatedjets"<<endl;
            passedNassociated_jj = true;
            //Update discriminants
            for (auto& KDspec:KDlist){
              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2l2jet); // Use mZZ!
              //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
              KD_jjVBF = *(KDspec.KD);

              if(KD_jjVBF<0){
                //cout<< "WARNING: KD_jjVBF = "<<KD_jjVBF<<endl;
                nevents_negative++;
                n_negative_KD_jjVBF_resolved ++;
              }
          
            }
          } else if(nassociatedjets==1){
            //KDjVBF=========================================================================
            if(verbose) cout<<"[INFO] found at least one nassociatedjets"<<endl;
            //Update discriminants
            for (auto& KDspec:KDlist_jVBF){
              n_times_calculation_KD_jVBF_resolved ++;
              n_events_associatedjets_lesstwo_resolved ++;

              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2l2jet); // Use mZZ!
              //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
              KD_jVBF = *(KDspec.KD);
              if(verbose) cout<<"[INFO] This KD_jVBF = "<<KD_jVBF<<endl;
              //cout<<"KD_jVBF = "<<KD_jVBF<<endl;
            }
            //count how many events have negative KD
            if(KD_jVBF<0){
              nevents_negative++;
              n_negative_KD_jVBF_resolved ++;
            }

          } else{
            //count how many events have nassociatedjets = 0 
            n_associatedjets_0_resolved ++;
          }
        }
      }
    }
    //=============find resolved up higgs===============
    if(foundZ2JCandidate_up && isMC){
      TLorentzVector p4_ZZ_up, Jet1_up, Jet2_up, Lep1, Lep2;
      Jet1_up.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_up[0]],(*jet_jesup_eta)[jet_Z1index_up[0]],(*jet_jesup_phi)[jet_Z1index_up[0]],(*jet_jesup_mass)[jet_Z1index_up[0]]);
      Jet2_up.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_up[1]],(*jet_jesup_eta)[jet_Z1index_up[1]],(*jet_jesup_phi)[jet_Z1index_up[1]],(*jet_jesup_mass)[jet_Z1index_up[1]]);
      Lep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
      Lep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
      //Jet1_dn.SetPtEtaPhiM((*jet_jesdn_pt)[jet_Z1index[0]],(*jet_jesdn_eta)[jet_Z1index[0]],(*jet_jesdn_phi)[jet_Z1index[0]],(*jet_jesdn_mass)[jet_Z1index[0]]);
      //Jet2_dn.SetPtEtaPhiM((*jet_jesdn_pt)[jet_Z1index[1]],(*jet_jesdn_eta)[jet_Z1index[1]],(*jet_jesdn_phi)[jet_Z1index[1]],(*jet_jesdn_mass)[jet_Z1index[1]]);
      p4_ZZ_up = Lep1+Lep2+Jet1_up+Jet2_up;
      //p4_ZZ_dn = Lep1+Lep2+Jet1_dn+Jet2_dn;
      mass2l2jet_up = p4_ZZ_up.M();

      if(foundZ1LCandidate){
        if (doMela){
          //check number of associated jets
          int njets_up = jet_jesup_pt->GetSize();
          int nassociatedjets_up = 0;
          vector<TLorentzVector> associatedjets_up;
          for(int i=0; i<njets_up; i++){

            //find jet that are not signal and put it into associated
            if(i==jet_Z1index_up[0] || i==jet_Z1index_up[1]){continue;}

            TLorentzVector thisjet;
            thisjet.SetPtEtaPhiM((*jet_jesup_pt)[i],(*jet_jesup_eta)[i],(*jet_jesup_phi)[i],(*jet_jesup_mass)[i]);
            
            nassociatedjets_up++;
            associatedjets_up.push_back(thisjet);
          }

          TLorentzVector selectedLep1_up,selectedLep2_up,selectedJet1_up,selectedJet2_up;
          selectedLep1_up.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
          selectedLep2_up.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
          selectedJet1_up.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_up[0]],(*jet_jesup_eta)[jet_Z1index_up[0]],(*jet_jesup_phi)[jet_Z1index_up[0]],(*jet_jesup_mass)[jet_Z1index_up[0]]);
          selectedJet2_up.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_up[1]],(*jet_jesup_eta)[jet_Z1index_up[1]],(*jet_jesup_phi)[jet_Z1index_up[1]],(*jet_jesup_mass)[jet_Z1index_up[1]]);

          SimpleParticleCollection_t daughters_up;
          daughters_up.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1_up));
          daughters_up.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2_up));
          daughters_up.push_back(SimpleParticle_t(0, selectedJet1_up));
          daughters_up.push_back(SimpleParticle_t(0, selectedJet2_up));

          //cout<<" fill daughters done "<<endl;

          //associated objets
          SimpleParticleCollection_t associated_up;
          //sort associatedjets as pt order
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          if(nassociatedjets_up>0){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_leadingpt=0.0;
            for(int i=0; i<nassociatedjets_up; i++){
              if(associatedjets_up[i].Pt()>temp_leadingpt){
                temp_leadingpt = associatedjets_up[i].Pt();
                leading_index[0]= i;
              }
            }
            //push_back the leading jet
            associated_up.push_back(SimpleParticle_t(0, associatedjets_up[leading_index[0]]));
            //cout<<"associatedjet1: px="<<associatedjets[leading_index[0]].Px()<<" Py="<<associatedjets[leading_index[0]].Py()<<" Pz="<<associatedjets[leading_index[0]].Pz()<<" E="<<associatedjets[leading_index[0]].E()<<endl;
          }
          if(nassociatedjets_up>1){
            if(verbose) cout<<"[INFO] second associatedjets"<<endl;
            double temp_subleadingpt=0.0;
            for(int i=0; i<nassociatedjets_up; i++){
              if(i==leading_index[0]) continue; //do not count leading jet
              if(associatedjets_up[i].Pt()>temp_subleadingpt){
                temp_subleadingpt = associatedjets_up[i].Pt();
                leading_index[1]= i;
              }
            }
            //push_back the subleading jet
            associated_up.push_back(SimpleParticle_t(0, associatedjets_up[leading_index[1]]));
            //compute delta eta between two associated jets
            //time_associatedjetjj_eta = associatedjets[leading_index[0]].Eta()*associatedjets[leading_index[1]].Eta();
            ////cout<<"associatedjet2: px="<<associatedjets[leading_index[1]].Px()<<" Py="<<associatedjets[leading_index[1]].Py()<<" Pz="<<associatedjets[leading_index[1]].Pz()<<" E="<<associatedjets[leading_index[1]].E()<<endl;

          }


          IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
          IvyMELAHelpers::melaHandle->setInputEvent(&daughters_up, &associated_up, nullptr, false);
          MEblock.computeMELABranches();
          MEblock.pushMELABranches();

          IvyMELAHelpers::melaHandle->resetInputEvent();

          //KD
          //retrieve MEs for KD constructing
          unordered_map<string,float> ME_Kfactor_values;
          MEblock.getBranchValues(ME_Kfactor_values);

          //KDZjj=========================================================================
          //Update discriminants
          if(verbose) cout<<"[INFO] Get Discriminant for KD_Zjj_up "<<endl;
          for (auto& KDspec:KDlist_Zjj_up){
            std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
            for (auto const& strKDvar:KDspec.KDvars){
              KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
            } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

            KDspec.KD->update(KDvars, mass2l2jet_up); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_Zjj_up = *(KDspec.KD);
            if(verbose) cout<<"[INFO] This KD_Zjj_up = "<<KD_Zjj_up<<endl;
          }

          if(nassociatedjets_up>=2){ //compute KD_jjVBF
            //cout<<" nassociatedjets>=2 "<<endl;
            if(verbose) cout<<"[INFO] found at least two nassociatedjets"<<endl;
            passedNassociated_jj = true;
            //Update discriminants
            for (auto& KDspec:KDlist){
              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2l2jet_up); // Use mZZ!
              //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
              KD_jjVBF_up = *(KDspec.KD);          
            }
          }
        }
      }
    }

    //=============find resolved dn higgs===============
    if(foundZ2JCandidate_dn && isMC){
      TLorentzVector p4_ZZ_dn, Jet1_dn, Jet2_dn, Lep1, Lep2;
      Jet1_dn.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_dn[0]],(*jet_jesup_eta)[jet_Z1index_dn[0]],(*jet_jesup_phi)[jet_Z1index_dn[0]],(*jet_jesup_mass)[jet_Z1index_dn[0]]);
      Jet2_dn.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_dn[1]],(*jet_jesup_eta)[jet_Z1index_dn[1]],(*jet_jesup_phi)[jet_Z1index_dn[1]],(*jet_jesup_mass)[jet_Z1index_dn[1]]);
      Lep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
      Lep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
      //Jet1_dn.SetPtEtaPhiM((*jet_jesdn_pt)[jet_Z1index[0]],(*jet_jesdn_eta)[jet_Z1index[0]],(*jet_jesdn_phi)[jet_Z1index[0]],(*jet_jesdn_mass)[jet_Z1index[0]]);
      //Jet2_dn.SetPtEtaPhiM((*jet_jesdn_pt)[jet_Z1index[1]],(*jet_jesdn_eta)[jet_Z1index[1]],(*jet_jesdn_phi)[jet_Z1index[1]],(*jet_jesdn_mass)[jet_Z1index[1]]);
      p4_ZZ_dn = Lep1+Lep2+Jet1_dn+Jet2_dn;
      //p4_ZZ_dn = Lep1+Lep2+Jet1_dn+Jet2_dn;
      mass2l2jet_dn = p4_ZZ_dn.M();

      if(foundZ1LCandidate){
        if (doMela){
          //check number of associated jets
          int njets_dn = jet_jesup_pt->GetSize();
          int nassociatedjets_dn = 0;
          vector<TLorentzVector> associatedjets_dn;
          for(int i=0; i<njets_dn; i++){

            //find jet that are not signal and put it into associated
            if(i==jet_Z1index_dn[0] || i==jet_Z1index_dn[1]){continue;}

            TLorentzVector thisjet;
            thisjet.SetPtEtaPhiM((*jet_jesup_pt)[i],(*jet_jesup_eta)[i],(*jet_jesup_phi)[i],(*jet_jesup_mass)[i]);
            
            nassociatedjets_dn++;
            associatedjets_dn.push_back(thisjet);
          }

          TLorentzVector selectedLep1_dn,selectedLep2_dn,selectedJet1_dn,selectedJet2_dn;
          selectedLep1_dn.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
          selectedLep2_dn.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
          selectedJet1_dn.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_dn[0]],(*jet_jesup_eta)[jet_Z1index_dn[0]],(*jet_jesup_phi)[jet_Z1index_dn[0]],(*jet_jesup_mass)[jet_Z1index_dn[0]]);
          selectedJet2_dn.SetPtEtaPhiM((*jet_jesup_pt)[jet_Z1index_dn[1]],(*jet_jesup_eta)[jet_Z1index_dn[1]],(*jet_jesup_phi)[jet_Z1index_dn[1]],(*jet_jesup_mass)[jet_Z1index_dn[1]]);

          SimpleParticleCollection_t daughters_dn;
          daughters_dn.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1_dn));
          daughters_dn.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2_dn));
          daughters_dn.push_back(SimpleParticle_t(0, selectedJet1_dn));
          daughters_dn.push_back(SimpleParticle_t(0, selectedJet2_dn));

          //cout<<" fill daughters done "<<endl;

          //associated objets
          SimpleParticleCollection_t associated_dn;
          //sort associatedjets as pt order
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          if(nassociatedjets_dn>0){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_leadingpt=0.0;
            for(int i=0; i<nassociatedjets_dn; i++){
              if(associatedjets_dn[i].Pt()>temp_leadingpt){
                temp_leadingpt = associatedjets_dn[i].Pt();
                leading_index[0]= i;
              }
            }
            //push_back the leading jet
            associated_dn.push_back(SimpleParticle_t(0, associatedjets_dn[leading_index[0]]));
            //cout<<"associatedjet1: px="<<associatedjets[leading_index[0]].Px()<<" Py="<<associatedjets[leading_index[0]].Py()<<" Pz="<<associatedjets[leading_index[0]].Pz()<<" E="<<associatedjets[leading_index[0]].E()<<endl;
          }
          if(nassociatedjets_dn>1){
            if(verbose) cout<<"[INFO] second associatedjets"<<endl;
            double temp_subleadingpt=0.0;
            for(int i=0; i<nassociatedjets_dn; i++){
              if(i==leading_index[0]) continue; //do not count leading jet
              if(associatedjets_dn[i].Pt()>temp_subleadingpt){
                temp_subleadingpt = associatedjets_dn[i].Pt();
                leading_index[1]= i;
              }
            }
            //push_back the subleading jet
            associated_dn.push_back(SimpleParticle_t(0, associatedjets_dn[leading_index[1]]));
            //compute delta eta between two associated jets
            //time_associatedjetjj_eta = associatedjets[leading_index[0]].Eta()*associatedjets[leading_index[1]].Eta();
            ////cout<<"associatedjet2: px="<<associatedjets[leading_index[1]].Px()<<" Py="<<associatedjets[leading_index[1]].Py()<<" Pz="<<associatedjets[leading_index[1]].Pz()<<" E="<<associatedjets[leading_index[1]].E()<<endl;

          }


          IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
          IvyMELAHelpers::melaHandle->setInputEvent(&daughters_dn, &associated_dn, nullptr, false);
          MEblock.computeMELABranches();
          MEblock.pushMELABranches();

          IvyMELAHelpers::melaHandle->resetInputEvent();

          //KD
          //retrieve MEs for KD constructing
          unordered_map<string,float> ME_Kfactor_values;
          MEblock.getBranchValues(ME_Kfactor_values);

          //KDZjj=========================================================================
          //Update discriminants
          if(verbose) cout<<"[INFO] Get Discriminant for KD_Zjj_dn "<<endl;
          for (auto& KDspec:KDlist_Zjj_dn){
            std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
            for (auto const& strKDvar:KDspec.KDvars){
              KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
            } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

            KDspec.KD->update(KDvars, mass2l2jet_dn); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_Zjj_dn = *(KDspec.KD);
            if(verbose) cout<<"[INFO] This KD_Zjj_dn = "<<KD_Zjj_dn<<endl;
          }

          if(nassociatedjets_dn>=2){ //compute KD_jjVBF
            //cout<<" nassociatedjets>=2 "<<endl;
            if(verbose) cout<<"[INFO] found at least two nassociatedjets"<<endl;
            passedNassociated_jj = true;
            //Update discriminants
            for (auto& KDspec:KDlist){
              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2l2jet_dn); // Use mZZ!
              //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
              KD_jjVBF_dn = *(KDspec.KD);          
            }
          }
        }
      }
    }

    //================================
    //====Merged category============
    //================================
    if(foundZ2MergedCandidata){
      //split JEC UnCertainty
      vector<float> jes_unc_split {};
      vector<float> pt_jesup_split {};
      vector<float> pt_jesdn_split {};
      float singleContr_jes_unc = 0;
      if(isMC){

        for(unsigned s_unc = 0; s_unc < uncSources.size(); s_unc++){
			    singleContr_jes_unc = 0;
			    ak8splittedUncerts_[s_unc]->setJetEta((*mergedjet_eta)[merged_Z1index]);
			    ak8splittedUncerts_[s_unc]->setJetPt((*mergedjet_pt)[merged_Z1index]);
			    singleContr_jes_unc = ak8splittedUncerts_[s_unc]->getUncertainty(true); 
			    jes_unc_split.push_back(singleContr_jes_unc);
			    pt_jesup_split.push_back( (*mergedjet_pt)[merged_Z1index] * (1.0 + singleContr_jes_unc));
			    pt_jesdn_split.push_back( (*mergedjet_pt)[merged_Z1index] * (1.0 - singleContr_jes_unc));
        }
      }else{
        jes_unc_split.push_back(-999.);
			  pt_jesup_split.push_back(-999.);
			  pt_jesdn_split.push_back(-999.);
      }
      mergedjet_jesunc_split_Total=jes_unc_split[0]; 
      mergedjet_jesunc_split_Abs=jes_unc_split[1]; 
      mergedjet_jesunc_split_Abs_year=jes_unc_split[2]; 
      mergedjet_jesunc_split_BBEC1=jes_unc_split[3]; 
      mergedjet_jesunc_split_BBEC1_year=jes_unc_split[4];
      mergedjet_jesunc_split_EC2=jes_unc_split[5]; 
      mergedjet_jesunc_split_EC2_year=jes_unc_split[6]; 
      mergedjet_jesunc_split_FlavQCD=jes_unc_split[7]; 
      mergedjet_jesunc_split_HF=jes_unc_split[8]; 
      mergedjet_jesunc_split_HF_year=jes_unc_split[9];
      mergedjet_jesunc_split_RelBal=jes_unc_split[10]; 
      mergedjet_jesunc_split_RelSample_year=jes_unc_split[11];

      mergedjetpt_jesup_split_Total=pt_jesup_split[0]; 
      mergedjetpt_jesup_split_Abs=pt_jesup_split[1]; 
      mergedjetpt_jesup_split_Abs_year=pt_jesup_split[2]; 
      mergedjetpt_jesup_split_BBEC1=pt_jesup_split[3]; 
      mergedjetpt_jesup_split_BBEC1_year=pt_jesup_split[4];
      mergedjetpt_jesup_split_EC2=pt_jesup_split[5]; 
      mergedjetpt_jesup_split_EC2_year=pt_jesup_split[6]; 
      mergedjetpt_jesup_split_FlavQCD=pt_jesup_split[7]; 
      mergedjetpt_jesup_split_HF=pt_jesup_split[8]; 
      mergedjetpt_jesup_split_HF_year=pt_jesup_split[9];
      mergedjetpt_jesup_split_RelBal=pt_jesup_split[10]; 
      mergedjetpt_jesup_split_RelSample_year=pt_jesup_split[11];
	    //dn	
      mergedjetpt_jesdn_split_Total=pt_jesdn_split[0]; 
      mergedjetpt_jesdn_split_Abs=pt_jesdn_split[1]; 
      mergedjetpt_jesdn_split_Abs_year=pt_jesdn_split[2]; 
      mergedjetpt_jesdn_split_BBEC1=pt_jesdn_split[3]; 
      mergedjetpt_jesdn_split_BBEC1_year=pt_jesdn_split[4];
      mergedjetpt_jesdn_split_EC2=pt_jesdn_split[5]; 
      mergedjetpt_jesdn_split_EC2_year=pt_jesdn_split[6]; 
      mergedjetpt_jesdn_split_FlavQCD=pt_jesdn_split[7]; 
      mergedjetpt_jesdn_split_HF=pt_jesdn_split[8]; 
      mergedjetpt_jesdn_split_HF_year=pt_jesdn_split[9];
      mergedjetpt_jesdn_split_RelBal=pt_jesdn_split[10]; 
      mergedjetpt_jesdn_split_RelSample_year=pt_jesdn_split[11];

      nsubjet = (*mergedjet_nsubjet)[merged_Z1index];

      TLorentzVector p4_ZZ,Lep1,Lep2,Jet1,Jet2,Mergedjet;
      Lep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
      Lep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
      Jet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][0],(*mergedjet_subjet_eta)[merged_Z1index][0],(*mergedjet_subjet_phi)[merged_Z1index][0],(*mergedjet_subjet_mass)[merged_Z1index][0]);
      Jet2.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index][1],(*mergedjet_subjet_phi)[merged_Z1index][1],(*mergedjet_subjet_mass)[merged_Z1index][1]);
      Mergedjet.SetPtEtaPhiM((*mergedjet_pt)[merged_Z1index],(*mergedjet_eta)[merged_Z1index],(*mergedjet_phi)[merged_Z1index],(*mergedjet_subjet_softDropMass)[merged_Z1index]);

      p4_ZZ = Lep1+Lep2+Mergedjet;
      mass2lj = p4_ZZ.M();


      if(foundZ1LCandidate){
        n_passed_merged ++;
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
            DR_merged_asccoiacted.push_back(temp_DR);
            if(temp_DR<0.8) {
              continue;
            }

            nassociatedjets++;
            associatedjets.push_back(thisjet);
            associatedjetsJ_index.push_back(i);
          }

          //compute KD_JJVBF and KD_Zjj
          //MEs
          //signal like objets
          TLorentzVector selectedLep1,selectedLep2,selectedJet1,selectedJet2;
          selectedLep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
          selectedLep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
          selectedJet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][0],(*mergedjet_subjet_eta)[merged_Z1index][0],(*mergedjet_subjet_phi)[merged_Z1index][0],(*mergedjet_subjet_mass)[merged_Z1index][0]);
          selectedJet2.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index][1],(*mergedjet_subjet_phi)[merged_Z1index][1],(*mergedjet_subjet_mass)[merged_Z1index][1]);


          SimpleParticleCollection_t daughters;
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1));
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2));
          daughters.push_back(SimpleParticle_t(0, selectedJet1));
          daughters.push_back(SimpleParticle_t(0, selectedJet2));

          if(verbose){
            cout<<"Lep1: px="<<selectedLep1.Px()<<" Py="<<selectedLep1.Py()<<" Pz="<<selectedLep1.Pz()<<" E="<<selectedLep1.E()<<endl;
            cout<<"Lep2: px="<<selectedLep2.Px()<<" Py="<<selectedLep2.Py()<<" Pz="<<selectedLep2.Pz()<<" E="<<selectedLep2.E()<<endl;
            cout<<"jet1: px="<<selectedJet1.Px()<<" Py="<<selectedJet1.Py()<<" Pz="<<selectedJet1.Pz()<<" E="<<selectedJet1.E()<<endl;
            cout<<"jet2: px="<<selectedJet2.Px()<<" Py="<<selectedJet2.Py()<<" Pz="<<selectedJet2.Pz()<<" E="<<selectedJet2.E()<<endl;
          }

          //associated objets
          if(verbose) cout<<"[INFO] push signal and associated candidate"<<endl;
          SimpleParticleCollection_t associated;
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          if(nassociatedjets>0){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_leadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(associatedjets[i].Pt()>temp_leadingpt){
                temp_leadingpt = associatedjets[i].Pt();
                leading_index[0]= i;
              }
            }
            //push_back the leading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[0]]));
            //cout<<"associatedjet1: px="<<associatedjets[leading_index[0]].Px()<<" Py="<<associatedjets[leading_index[0]].Py()<<" Pz="<<associatedjets[leading_index[0]].Pz()<<" E="<<associatedjets[leading_index[0]].E()<<endl;
            //store variables for associate jet
            associatedjetJ_pt.push_back(associatedjets[leading_index[0]].Pt());
            associatedjetJ_eta.push_back(associatedjets[leading_index[0]].Eta());
            associatedjetJ_phi.push_back(associatedjets[leading_index[0]].Phi());
            associatedjetJ_mass.push_back(associatedjets[leading_index[0]].M());
          }
          if(nassociatedjets>1){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_subleadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(i==leading_index[0]) continue; //do not count leading jet
              if(associatedjets[i].Pt()>temp_subleadingpt){
                temp_subleadingpt = associatedjets[i].Pt();
                leading_index[1]= i;
              }
            }
            //push_back the subleading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[1]]));
            //compute delta eta between two associated jets
            time_associatedjetJ_eta = associatedjets[leading_index[0]].Eta()*associatedjets[leading_index[1]].Eta();
            //cout<<"associatedjet2: px="<<associatedjets[leading_index[1]].Px()<<" Py="<<associatedjets[leading_index[1]].Py()<<" Pz="<<associatedjets[leading_index[1]].Pz()<<" E="<<associatedjets[leading_index[1]].E()<<endl;
            //store variables for associate jet
            associatedjetJ_pt.push_back(associatedjets[leading_index[1]].Pt());
            associatedjetJ_eta.push_back(associatedjets[leading_index[1]].Eta());
            associatedjetJ_phi.push_back(associatedjets[leading_index[1]].Phi());
            associatedjetJ_mass.push_back(associatedjets[leading_index[1]].M());

            if(isMC){
              if((associatedjetsJ_index[leading_index[0]] == match1_recoindex || associatedjetsJ_index[leading_index[0]] == match2_recoindex) && (associatedjetsJ_index[leading_index[1]] == match1_recoindex || associatedjetsJ_index[leading_index[1]] == match2_recoindex)){
                passedmatchtruthVBF_J=true;
              }
            }

          }

          if(verbose) cout<<"[INFO] Set Mela CandidateDecayMode,InputEvent and computeMELABranche "<<endl;
          IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
          IvyMELAHelpers::melaHandle->setInputEvent(&daughters, &associated, nullptr, false);
          MEblock.computeMELABranches();
          MEblock.pushMELABranches();
          IvyMELAHelpers::melaHandle->resetInputEvent();

          //KD
          //retrieve MEs for KD constructing
          if(verbose) cout<<"[INFO] retrieve MEs for KD constructing "<<endl;
          unordered_map<string,float> ME_Kfactor_values;
          MEblock.getBranchValues(ME_Kfactor_values);
          //unordered_map<string, float>::iterator iter;
          //for(iter = ME_Kfactor_values.begin(); iter != ME_Kfactor_values.end(); iter++){
          //  cout << "[INFO] this ME_Kfactor_values = "<<iter->first << " : " << iter->second << endl;
          //}
          
          //KDZjj=========================================================================
          //Update discriminants
          if(verbose) cout<<"[INFO] Get Discriminant for KD_ZJ "<<endl;
          for (auto& KDspec:KDlist_ZJ){
            std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
            for (auto const& strKDvar:KDspec.KDvars){
              //cout<<typeid(strKDvar).name()<<endl;
              //cout<<"this strKDva in Zjj= "<<strKDvar<<endl;
              //cout<<"this ME_Kfactor_values = "<<ME_Kfactor_values[static_cast<string>(strKDvar)]<<endl;
              KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
            } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

            KDspec.KD->update(KDvars, mass2lj); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_ZJ = *(KDspec.KD);
            //
            KD_ZJ_up = *(KDspec.KD);
            KD_ZJ_dn = *(KDspec.KD);
            if(verbose) cout<<"[INFO] This KD_ZJ = "<<KD_ZJ<<endl;
          }

          if(nassociatedjets>=2){ //compute KD_JJVBF
            n_times_calculation_KD_jjVBF_merged ++;
            passedNassociated_J = true;
            //KD_JJVBF========================================================================
            //Update discriminants
            if(verbose) cout<<"[INFO] Get Discriminant for KD_JJVBF"<<endl;
            for (auto& KDspec:KDlist_JJVBF){
              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                //cout<<typeid(strKDvar).name()<<endl;
                //cout<<"this strKDva = "<<strKDvar<<endl;
                //cout<<"this ME_Kfactor_values = "<<ME_Kfactor_values[static_cast<string>(strKDvar)]<<endl;
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2lj); // Use mZZ!
              //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
              KD_JJVBF = *(KDspec.KD);
              KD_JVBF_up = *(KDspec.KD);
              KD_JVBF_dn = *(KDspec.KD);

              if(KD_JJVBF<0){
                n_negative_KD_VBF_merged ++;
                n_negative_KD_jjVBF_merged++;
              }
            }
          }else if(nassociatedjets==1){
            //KD_JVBF========================================================================
            n_events_associatedjets_lesstwo_merged++;
            n_times_calculation_KD_jVBF_merged ++;
            //Update discriminants
            if(verbose) cout<<"[INFO] Get Discriminant for KD_JVBF"<<endl;
            for (auto& KDspec:KDlist_JVBF){
              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2lj); // Use mZZ!
              KD_JVBF = *(KDspec.KD);

              if(KD_JVBF<0){
                n_negative_KD_VBF_merged ++;
                n_negative_KD_jVBF_merged++;
              }
            }
          }else{
            n_associatedjets_0_merged++;
          }

          if(verbose){
            cout<<"[INFO] domela in merged case done"<<endl;
          }
        }

      }
    }

    //=============find merged up higgs===============
    if(foundZ2MergedCandidata_up && isMC){
      //nsubjet = (*mergedjet_nsubjet)[merged_Z1index];

      TLorentzVector p4_ZZ,Lep1,Lep2,Mergedjet;
      Lep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
      Lep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
      //Jet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][0],(*mergedjet_subjet_eta)[merged_Z1index][0],(*mergedjet_subjet_phi)[merged_Z1index][0],(*mergedjet_subjet_mass)[merged_Z1index][0]);
      //Jet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index][1],(*mergedjet_subjet_phi)[merged_Z1index][1],(*mergedjet_subjet_mass)[merged_Z1index][1]);
      Mergedjet.SetPtEtaPhiM((*mergedjet_jesup_pt)[merged_Z1index_up],(*mergedjet_jesup_eta)[merged_Z1index_up],(*mergedjet_jesup_phi)[merged_Z1index_up],(*mergedjet_jesup_mass)[merged_Z1index_up]);

      p4_ZZ = Lep1+Lep2+Mergedjet;
      mass2lj_up = p4_ZZ.M();

      /* Will be un-comments once subjet jes index problem solved
      if(foundZ1LCandidate){
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
            double temp_DR = deltaR(thisjet.Eta(),thisjet.Phi(),(*mergedjet_jesup_eta)[merged_Z1index_up],(*mergedjet_jesup_phi)[merged_Z1index_up]);
            DR_merged_asccoiacted.push_back(temp_DR);
            if(temp_DR<0.8) {
              continue;
            }

            nassociatedjets++;
            associatedjets.push_back(thisjet);
          }

          //compute KD_JJVBF and KD_Zjj
          //MEs
          //signal like objets
          TLorentzVector selectedLep1,selectedLep2,selectedJet1,selectedJet2;
          selectedLep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
          selectedLep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
          //selectedJet1.SetPtEtaPhiM((*mergedjet_jesup_pt)[merged_Z1index_up],(*mergedjet_jesup_eta)[merged_Z1index_up],(*mergedjet_jesup_phi)[merged_Z1index_up],(*mergedjet_jesup_mass)[merged_Z1index_up]);
          //selectedJet2.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index][1],(*mergedjet_subjet_phi)[merged_Z1index][1],(*mergedjet_subjet_mass)[merged_Z1index][1]);
          selectedJet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index_up][0],(*mergedjet_subjet_eta)[merged_Z1index_up][0],(*mergedjet_subjet_phi)[merged_Z1index_up][0],(*mergedjet_subjet_mass)[merged_Z1index_up][0]);
          selectedJet2.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index_up][1],(*mergedjet_subjet_eta)[merged_Z1index_up][1],(*mergedjet_subjet_phi)[merged_Z1index_up][1],(*mergedjet_subjet_mass)[merged_Z1index_up][1]);
          //selectedJet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][0],(*mergedjet_subjet_eta)[merged_Z1index_up][0],(*mergedjet_subjet_phi)[merged_Z1index_up][0],(*mergedjet_subjet_mass)[merged_Z1index_up][0]);
          //selectedJet2.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index_up][1],(*mergedjet_subjet_phi)[merged_Z1index_up][1],(*mergedjet_subjet_mass)[merged_Z1index_up][1]);
          //selectedJet2.SetPtEtaPhiM(0.0,0.0,0.0,0.0);

          SimpleParticleCollection_t daughters;
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1));
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2));
          daughters.push_back(SimpleParticle_t(0, selectedJet1));
          daughters.push_back(SimpleParticle_t(0, selectedJet2));

          //associated objets
          if(verbose) cout<<"[INFO] push signal and associated candidate"<<endl;
          SimpleParticleCollection_t associated;
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          if(nassociatedjets>0){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_leadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(associatedjets[i].Pt()>temp_leadingpt){
                temp_leadingpt = associatedjets[i].Pt();
                leading_index[0]= i;
              }
            }
            //push_back the leading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[0]]));
          }
          if(nassociatedjets>1){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_subleadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(i==leading_index[0]) continue; //do not count leading jet
              if(associatedjets[i].Pt()>temp_subleadingpt){
                temp_subleadingpt = associatedjets[i].Pt();
                leading_index[1]= i;
              }
            }
            //push_back the subleading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[1]]));
          }

          if(verbose) cout<<"[INFO] Set Mela CandidateDecayMode,InputEvent and computeMELABranche "<<endl;
          IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
          IvyMELAHelpers::melaHandle->setInputEvent(&daughters, &associated, nullptr, false);
          MEblock.computeMELABranches();
          MEblock.pushMELABranches();
          IvyMELAHelpers::melaHandle->resetInputEvent();

          //KD
          //retrieve MEs for KD constructing
          if(verbose) cout<<"[INFO] retrieve MEs for KD constructing "<<endl;
          unordered_map<string,float> ME_Kfactor_values;
          MEblock.getBranchValues(ME_Kfactor_values);
          
          //KDZjj=========================================================================
          //Update discriminants
          if(verbose) cout<<"[INFO] Get Discriminant for KD_ZJ_up "<<endl;
          for (auto& KDspec:KDlist_ZJ_up){
            std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
            for (auto const& strKDvar:KDspec.KDvars){
              KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
            } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

            KDspec.KD->update(KDvars, mass2lj_up); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_ZJ_up = *(KDspec.KD);
            if(verbose) cout<<"[INFO] This KD_ZJ = "<<KD_ZJ<<endl;
          }

          if(nassociatedjets>=2){ //compute KD_JJVBF

            passedNassociated_J = true;
            //KD_JJVBF========================================================================
            //Update discriminants
            if(verbose) cout<<"[INFO] Get Discriminant for KD_VBF"<<endl;
            for (auto& KDspec:KDlist_JJVBF){
              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2lj_up); // Use mZZ!
              KD_JVBF_up = *(KDspec.KD);
            }

          }
        }

      }
      */
    }

    //=============find merged up higgs===============
    if(foundZ2MergedCandidata_dn && isMC){
      //nsubjet = (*mergedjet_nsubjet)[merged_Z1index];

      TLorentzVector p4_ZZ,Lep1,Lep2,Mergedjet;
      Lep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
      Lep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
      //Jet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][0],(*mergedjet_subjet_eta)[merged_Z1index][0],(*mergedjet_subjet_phi)[merged_Z1index][0],(*mergedjet_subjet_mass)[merged_Z1index][0]);
      //Jet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index][1],(*mergedjet_subjet_phi)[merged_Z1index][1],(*mergedjet_subjet_mass)[merged_Z1index][1]);
      Mergedjet.SetPtEtaPhiM((*mergedjet_jesdn_pt)[merged_Z1index_dn],(*mergedjet_jesdn_eta)[merged_Z1index_dn],(*mergedjet_jesdn_phi)[merged_Z1index_dn],(*mergedjet_jesdn_mass)[merged_Z1index_dn]);

      p4_ZZ = Lep1+Lep2+Mergedjet;
      mass2lj_dn = p4_ZZ.M();

      /*Will be un-comments once subjet jes index problem solved
      if(foundZ1LCandidate){
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
            double temp_DR = deltaR(thisjet.Eta(),thisjet.Phi(),(*mergedjet_jesup_eta)[merged_Z1index_up],(*mergedjet_jesup_phi)[merged_Z1index_up]);
            DR_merged_asccoiacted.push_back(temp_DR);
            if(temp_DR<0.8) {
              continue;
            }

            nassociatedjets++;
            associatedjets.push_back(thisjet);
          }

          //compute KD_JJVBF and KD_Zjj
          //MEs
          //signal like objets
          TLorentzVector selectedLep1,selectedLep2,selectedJet1,selectedJet2;
          selectedLep1.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[0]],(*lepFSR_eta)[lep_Z1index[0]],(*lep_phi)[lep_Z1index[0]],(*lepFSR_mass)[lep_Z1index[0]]);
          selectedLep2.SetPtEtaPhiM((*lepFSR_pt)[lep_Z1index[1]],(*lepFSR_eta)[lep_Z1index[1]],(*lep_phi)[lep_Z1index[1]],(*lepFSR_mass)[lep_Z1index[1]]);
          //selectedJet1.SetPtEtaPhiM((*mergedjet_jesdn_pt)[merged_Z1index_dn],(*mergedjet_jesdn_eta)[merged_Z1index_dn],(*mergedjet_jesdn_phi)[merged_Z1index_dn],(*mergedjet_jesdn_mass)[merged_Z1index_dn]);
          //selectedJet2.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index][1],(*mergedjet_subjet_eta)[merged_Z1index][1],(*mergedjet_subjet_phi)[merged_Z1index][1],(*mergedjet_subjet_mass)[merged_Z1index][1]);
          selectedJet1.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index_dn][0],(*mergedjet_subjet_eta)[merged_Z1index_dn][0],(*mergedjet_subjet_phi)[merged_Z1index_dn][0],(*mergedjet_subjet_mass)[merged_Z1index_dn][0]);
          selectedJet2.SetPtEtaPhiM((*mergedjet_subjet_pt)[merged_Z1index_dn][1],(*mergedjet_subjet_eta)[merged_Z1index_dn][1],(*mergedjet_subjet_phi)[merged_Z1index_dn][1],(*mergedjet_subjet_mass)[merged_Z1index_dn][1]);
          //selectedJet2.SetPtEtaPhiM(0.0,0.0,0.0,0.0);

          SimpleParticleCollection_t daughters;
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[0]], selectedLep1));
          daughters.push_back(SimpleParticle_t((*lep_id)[lep_Z1index[1]], selectedLep2));
          daughters.push_back(SimpleParticle_t(0, selectedJet1));
          daughters.push_back(SimpleParticle_t(0, selectedJet2));

          //associated objets
          if(verbose) cout<<"[INFO] push signal and associated candidate"<<endl;
          SimpleParticleCollection_t associated;
          //sort associatedjets as pt order
          int leading_index[2]={0,0};
          if(nassociatedjets>0){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_leadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(associatedjets[i].Pt()>temp_leadingpt){
                temp_leadingpt = associatedjets[i].Pt();
                leading_index[0]= i;
              }
            }
            //push_back the leading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[0]]));
          }
          if(nassociatedjets>1){
            if(verbose) cout<<"[INFO] first associatedjets"<<endl;
            double temp_subleadingpt=0.0;
            for(int i=0; i<nassociatedjets; i++){
              if(i==leading_index[0]) continue; //do not count leading jet
              if(associatedjets[i].Pt()>temp_subleadingpt){
                temp_subleadingpt = associatedjets[i].Pt();
                leading_index[1]= i;
              }
            }
            //push_back the subleading jet
            associated.push_back(SimpleParticle_t(0, associatedjets[leading_index[1]]));
          }

          if(verbose) cout<<"[INFO] Set Mela CandidateDecayMode,InputEvent and computeMELABranche "<<endl;
          IvyMELAHelpers::melaHandle->setCandidateDecayMode(TVar::CandidateDecay_ZZ);
          IvyMELAHelpers::melaHandle->setInputEvent(&daughters, &associated, nullptr, false);
          MEblock.computeMELABranches();
          MEblock.pushMELABranches();
          IvyMELAHelpers::melaHandle->resetInputEvent();

          //KD
          //retrieve MEs for KD constructing
          if(verbose) cout<<"[INFO] retrieve MEs for KD constructing "<<endl;
          unordered_map<string,float> ME_Kfactor_values;
          MEblock.getBranchValues(ME_Kfactor_values);
          
          //KDZjj=========================================================================
          //Update discriminants
          if(verbose) cout<<"[INFO] Get Discriminant for KD_ZJ_up "<<endl;
          for (auto& KDspec:KDlist_ZJ_dn){
            std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
            for (auto const& strKDvar:KDspec.KDvars){
              KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
            } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

            KDspec.KD->update(KDvars, mass2lj_dn); // Use mZZ!
            //cout<<"value of KD for this evnet  = "<<*(KDspec.KD)<<endl;
            KD_ZJ_dn = *(KDspec.KD);
            if(verbose) cout<<"[INFO] This KD_ZJ = "<<KD_ZJ<<endl;
          }

          if(nassociatedjets>=2){ //compute KD_JJVBF

            passedNassociated_J = true;
            //KD_JJVBF========================================================================
            //Update discriminants
            if(verbose) cout<<"[INFO] Get Discriminant for KD_VBF"<<endl;
            for (auto& KDspec:KDlist_JJVBF){
              std::vector<float> KDvars; KDvars.reserve(KDspec.KDvars.size());
              for (auto const& strKDvar:KDspec.KDvars){
                KDvars.push_back(ME_Kfactor_values[static_cast<string>(strKDvar)]);
              } // ME_Kfactor_values here is just a map of TString->float. You should have something equivalent.

              KDspec.KD->update(KDvars, mass2lj_dn); // Use mZZ!
              KD_JVBF_dn = *(KDspec.KD);
            }

          }
        }

      }
      */
    }
    /*
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
    if(foundresolvedOnly || foundresolvedCombine){
      if(verbose) cout<<"[INFO] this is resovled higgs"<<endl;
      passed_fullresolved++;
      passedfullresolved = true;
      //cout<<"passedfullresolved"<<endl;
    }

    //full merged higgs and do MALE
    if(foundmergedOnly || foundmergedCombine ){
      if(verbose) cout<<"[INFO] this is merged higgs"<<endl;
      passed_fullmerged++;
      passedfullmerged = true;

      //DR
      if(isMC){
        if(passedRecoquarkMatch){
          double this1_DR = 0.0;
          this1_DR = deltaR((*mergedjet_eta)[merged_Z1index],(*mergedjet_phi)[merged_Z1index],Reco_quark1_match_eta,Reco_quark1_match_phi);
          DR_merged_VBF1_matched = this1_DR;

          double this2_DR = 0.0;
          this2_DR = deltaR((*mergedjet_eta)[merged_Z1index],(*mergedjet_phi)[merged_Z1index],Reco_quark2_match_eta,Reco_quark2_match_phi);
          DR_merged_VBF2_matched = this2_DR;
        }
      }
    }
    */

    //SetVBFGen(); set Gen and match atfer reco-jet selected
    //==========fill output tree branch==========================================
    passedEventsTree_All->Fill();

    if(verbose){
      cout<<"[INFO] loop this evnet done"<<endl;
      cout<<"================================="<<endl;
      cout<<"================================="<<endl;
      cout<<"================================="<<endl;
    } 

  }
  //=========================loop done==========================================
  if(verbose) cout<<"[INFO] Clean DiscriminantClasses"<<endl;
  for (auto& KDspec:KDlist) KDspec.resetKD();
  if(verbose) cout<<"[INFO] KD_VBF done"<<endl;

  if(verbose) cout<<"[INFO] Clean DiscriminantClasses"<<endl;
  for (auto& KDspec:KDlist_JJVBF) KDspec.resetKD();
  if(verbose) cout<<"[INFO] KD_JJVBF done"<<endl;

  if(verbose) cout<<"[INFO] Clean DiscriminantClasses"<<endl;
  for (auto& KDspec:KDlist_Zjj) KDspec.resetKD();
  if(verbose) cout<<"[INFO] KD_Zjj done"<<endl;

  if(verbose) cout<<"[INFO] Clean DiscriminantClasses"<<endl;
  for (auto& KDspec:KDlist_ZJ) KDspec.resetKD();
  if(verbose) cout<<"[INFO] KD_ZJ done"<<endl;

  cout<<"[INFO] there are "<<npassed_resolved<<" "<<"events have passed full resolved selection"<<endl;
  cout<<"[INFP] there are "<<times_calculation_KD_jjVBF<<" "<<"times calculation KD_jjVBF in resolved case"<<endl;
  cout<<"[INFO] there are "<<n_negative_KD_jjVBF_resolved<<" "<<"events have negative KD_jjVBF value in resolved case"<<endl;
  cout<<"[INFO] there are "<<n_events_associatedjets_lesstwo_resolved<<" "<<"events with number of associated jets less than two in resolved case"<<endl;
  cout<<"[INFO] there are "<<n_times_calculation_KD_jVBF_resolved<<" "<<"times calculation KD_jVBF in resolved case"<<endl;
  cout<<"[INFO] there are "<<n_associatedjets_0_resolved<<" "<<"events with number of associated jets equal to zero in resolved case"<<endl;
  cout<<"[INFO] there are "<<n_negative_KD_jVBF_resolved<<" "<<"events have negative KD_jVBF value in resolved case"<<endl;
  cout<<"[INFO] there are "<<nevents_negative<<" "<< "events have negative KD in resolved case"<<endl;

  cout<<"[INFO] there are "<<n_passed_merged<<" "<<"events have passed full merged selection"<<endl;
  cout<<"[INFP] there are "<<n_times_calculation_KD_jjVBF_merged<<" "<<"times calculation KD_jjVBF in merged case"<<endl;
  cout<<"[INFO] there are "<<n_negative_KD_jjVBF_merged<<" "<<"events have negative KD_jjVBF value in merged case"<<endl;
  cout<<"[INFO] there are "<<n_events_associatedjets_lesstwo_merged<<"events with number of associated jets less than two in merged case"<<endl;
  cout<<"[INFO] there are "<<n_times_calculation_KD_jVBF_merged<<" "<<"times calculation KD_jVBF in merged case"<<endl;
  cout<<"[INFO] there are "<<n_associatedjets_0_merged<<" "<<"events with number of associated jets equal to zero in merged case"<<endl;
  cout<<"[INFO] there are "<<n_negative_KD_jVBF_merged<<" "<<"events have negative KD_jVBF value in merged case"<<endl;
  cout<<"[INFO] there are "<<n_negative_KD_VBF_merged<<" "<< "events have negative KD in merged case"<<endl;

  cout<<"[INFO] there are "<<n_match_vbfquarks_to_recojet<<" "<< "events with vbf quarks match to reco jets in all events in resolved case"<<endl;

  outfile->cd();
  //passedEventsTree_All->Write();
  TH1F h("sumWeights","sum Weights of Sample",2,0,2);
  h.SetBinContent(1,SumWeight);

  //store total number of events in a histogram for further reference
  TH1F h_0("nEvents","nEvents",1,0,1);
  h_0.SetBinContent(1,nentries);
  //
  TH1F h_1("cutflow","cutflow",23,0,23);
  h_1.SetBinContent(1,ievent); h_1.GetXaxis()->SetBinLabel(1,"nEvents");
  h_1.SetBinContent(2,passed_trig); h_1.GetXaxis()->SetBinLabel(2,"passed_trig");
  h_1.SetBinContent(3,passed_n_2leps); h_1.GetXaxis()->SetBinLabel(3,"passed_n_2leps");
  h_1.SetBinContent(4,passed_flavor_charge); h_1.GetXaxis()->SetBinLabel(4,"passed_flavor_charge");
  h_1.SetBinContent(5,passed_lepZpt_40_25); h_1.GetXaxis()->SetBinLabel(5,"passed_lepZpt_40_25");
  h_1.SetBinContent(6,passed_dR_lilj0point2); h_1.GetXaxis()->SetBinLabel(6,"passed_dR_lilj0point2");
  h_1.SetBinContent(7,passed_Mll_4); h_1.GetXaxis()->SetBinLabel(7,"passed_Mll_4");
  h_1.SetBinContent(8,passed_lepisolation); h_1.GetXaxis()->SetBinLabel(8,"passed_lepisolation");
  h_1.SetBinContent(9,passed_leptightID); h_1.GetXaxis()->SetBinLabel(9,"passed_leptightID");
  h_1.SetBinContent(10,passed_lepZmass40_180); h_1.GetXaxis()->SetBinLabel(10,"passed_lepZmass40_180");
  h_1.SetBinContent(11,passed_lepZ); h_1.GetXaxis()->SetBinLabel(11,"passed_lepZ");

  h_1.SetBinContent(12,passed_n_2ak4jets); h_1.GetXaxis()->SetBinLabel(12,"passed_n_2ak4jets");
  h_1.SetBinContent(13,passed_lepclean); h_1.GetXaxis()->SetBinLabel(13,"passed_lepclean");
  h_1.SetBinContent(14,passed_jetpt30); h_1.GetXaxis()->SetBinLabel(14,"passed_jetpt30");
  h_1.SetBinContent(15,passed_jeteta2opint4); h_1.GetXaxis()->SetBinLabel(15,"passed_jeteta2opint4");
  h_1.SetBinContent(16,passed_dijetpt100); h_1.GetXaxis()->SetBinLabel(16,"passed_dijetpt100");
  h_1.SetBinContent(17,passed_ak4jetZm_40_180); h_1.GetXaxis()->SetBinLabel(17,"passed_ak4jetZm_40_180");
  h_1.SetBinContent(18,passed_resovedonlyHiggs); h_1.GetXaxis()->SetBinLabel(18,"passed_resovedonlyHiggs");


  h_1.SetBinContent(18,passed_nmergedjets_lepclean); h_1.GetXaxis()->SetBinLabel(18,"passed_nmergedjets_lepclean");
  h_1.SetBinContent(19,passed_mergedjetsPt200); h_1.GetXaxis()->SetBinLabel(19,"passed_mergedjetsPt200");
  h_1.SetBinContent(20,passed_mergedjetEta2opint4); h_1.GetXaxis()->SetBinLabel(20,"passed_mergedjetEta2opint4");
  h_1.SetBinContent(21,passed_mergedmass_40_180); h_1.GetXaxis()->SetBinLabel(21,"passed_mergedmass_40_180");
  h_1.SetBinContent(22,passed_particleNetZvsQCD0opint9); h_1.GetXaxis()->SetBinLabel(22,"passed_particleNetZvsQCD0opint9");
  h_1.SetBinContent(23,passed_MergedolonlyHiggs); h_1.GetXaxis()->SetBinLabel(23,"passed_MergedolonlyHiggs");

  outfile->Write();

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
//=======================================================================================================
//=======================================================================================================
//=======================================================================================================
//=================find two lepton=======================================================================
void TreeLoop::findZ1LCandidate(){
  if(verbose){cout<<"[INFO] loop leptons in this event"<<endl;}
  unsigned int Nlep = lepFSR_pt->GetSize();
  if(Nlep<2){return;}
  //passed_n_2leps++;
  Nleptons = Nlep;
  if(verbose){cout<<"[INFO] found at least tow leptons"<<endl;}

  // First, make all Z candidates including any FSR photons
  int n_Zs=0;
  vector<int> Z_Z1L_lepindex1;
  vector<int> Z_Z1L_lepindex2;

  //up 1%
  int n_Zs_1p=0;
  vector<int> Z_Z1L_lepindex1_1p;
  vector<int> Z_Z1L_lepindex2_1p;

  //down 1%
  int n_Zs_1m=0;
  vector<int> Z_Z1L_lepindex1_1m;
  vector<int> Z_Z1L_lepindex2_1m;

  //check if n tight lepton==2
  for(unsigned int i=0; i<Nlep; i++){
    if ((*lep_tightId)[i]){ Ntightleptons+=1;}
  }
  if(Ntightleptons!=2){return;}
  passed_n_2leps++;

  //variables for cut table
  bool pass_flavor_charge = false;
  //flavor and charge cut
  for(unsigned int i=0; i<Nlep; i++){
    for(unsigned int j=i+1; j<Nlep; j++){
      // same flavor opposite charge for Z+jet CR. different sgin with different flavor for TTjet CR
      if( (((*lep_id)[i]+(*lep_id)[j])!=0) && ((((*lep_id)[i]*(*lep_id)[j])>0) || (abs((*lep_id)[i])==abs((*lep_id)[j]))) ) continue;
      pass_flavor_charge = true;

      TLorentzVector li, lj;
      li.SetPtEtaPhiM((*lep_pt)[i],(*lep_eta)[i],(*lep_phi)[i],(*lep_mass)[i]);
      lj.SetPtEtaPhiM((*lep_pt)[j],(*lep_eta)[j],(*lep_phi)[j],(*lep_mass)[j]);

      TLorentzVector lifsr, ljfsr;
      lifsr.SetPtEtaPhiM((*lepFSR_pt)[i],(*lepFSR_eta)[i],(*lepFSR_phi)[i],(*lepFSR_mass)[i]);
      ljfsr.SetPtEtaPhiM((*lepFSR_pt)[j],(*lepFSR_eta)[j],(*lepFSR_phi)[j],(*lepFSR_mass)[j]);

      TLorentzVector Z, Z_noFSR;
      Z = lifsr+ljfsr;
      Z_noFSR = li+lj;

      // float lepton pt 1%
      //up 1%
      TLorentzVector li_1p, lj_1p;
      li_1p.SetPtEtaPhiM((*lep_pt)[i]*1.01,(*lep_eta)[i],(*lep_phi)[i],(*lep_mass)[i]);
      lj_1p.SetPtEtaPhiM((*lep_pt)[j]*1.01,(*lep_eta)[j],(*lep_phi)[j],(*lep_mass)[j]);

      TLorentzVector lifsr_1p, ljfsr_1p;
      lifsr_1p.SetPtEtaPhiM((*lepFSR_pt)[i]*1.01,(*lepFSR_eta)[i],(*lepFSR_phi)[i],(*lepFSR_mass)[i]);
      ljfsr_1p.SetPtEtaPhiM((*lepFSR_pt)[j]*1.01,(*lepFSR_eta)[j],(*lepFSR_phi)[j],(*lepFSR_mass)[j]);

      TLorentzVector Z_1p, Z_noFSR_1p;
      Z_1p = lifsr_1p+ljfsr_1p;
      Z_noFSR_1p = li_1p+lj_1p;

      //down 1%
      TLorentzVector li_1m, lj_1m;
      li_1m.SetPtEtaPhiM((*lep_pt)[i]*0.99,(*lep_eta)[i],(*lep_phi)[i],(*lep_mass)[i]);
      lj_1m.SetPtEtaPhiM((*lep_pt)[j]*0.99,(*lep_eta)[j],(*lep_phi)[j],(*lep_mass)[j]);

      TLorentzVector lifsr_1m, ljfsr_1m;
      lifsr_1m.SetPtEtaPhiM((*lepFSR_pt)[i]*0.99,(*lepFSR_eta)[i],(*lepFSR_phi)[i],(*lepFSR_mass)[i]);
      ljfsr_1m.SetPtEtaPhiM((*lepFSR_pt)[j]*0.99,(*lepFSR_eta)[j],(*lepFSR_phi)[j],(*lepFSR_mass)[j]);

      TLorentzVector Z_1m, Z_noFSR_1m;
      Z_1m = lifsr_1m+ljfsr_1m;
      Z_noFSR_1m = li_1m+lj_1m;
      

      if (Z.M()>0.0) {
        n_Zs++;
        Z_Z1L_lepindex1.push_back(i);
        Z_Z1L_lepindex2.push_back(j);
      }

      //up 1%
      if (Z_1p.M()>0.0) {
        n_Zs_1p++;
        Z_Z1L_lepindex1_1p.push_back(i);
        Z_Z1L_lepindex2_1p.push_back(j);
      }
      //down 1%
      if (Z_1m.M()>0.0) {
        n_Zs_1m++;
        Z_Z1L_lepindex1_1m.push_back(i);
        Z_Z1L_lepindex2_1m.push_back(j);
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

  //if(Ntightleptons!=2){return;}
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

    if(Z1.Pt()<100) continue;

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
      lep_1_pt = (*lepFSR_pt)[lep_Z1index[0]];
      lep_1_eta = (*lepFSR_eta)[lep_Z1index[0]];
      lep_1_phi = (*lepFSR_phi)[lep_Z1index[0]];
      lep_1_mass = (*lepFSR_mass)[lep_Z1index[0]];
      lep_2_pt = (*lepFSR_pt)[lep_Z1index[1]];
      lep_2_eta = (*lepFSR_eta)[lep_Z1index[1]];
      lep_2_phi = (*lepFSR_phi)[lep_Z1index[1]];
      lep_2_mass = (*lepFSR_mass)[lep_Z1index[1]];

      //if (verbose) cout<<" new best Z1L candidate: massZ1: "<<massZ1<<" (mass3l: "<<mass3l<<")"<<endl;
      found2lepCandidate = true;
      if( ((*lep_id)[lep_Z1index[0]]+(*lep_id)[lep_Z1index[1]])==0 ) foundZ1LCandidate=true;
      if( (((*lep_id)[lep_Z1index[0]]*(*lep_id)[lep_Z1index[1]])<0) && (abs((*lep_id)[lep_Z1index[0]])!=abs((*lep_id)[lep_Z1index[1]])) ) foundTTCRCandidate = true;
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

  //1% up
  for (int i=0; i<n_Zs_1p; i++) {

    int i1 = Z_Z1L_lepindex1_1p[i]; int i2 = Z_Z1L_lepindex2_1p[i];

    TLorentzVector lep_i1, lep_i2;
    lep_i1.SetPtEtaPhiM((*lepFSR_pt)[i1]*1.01,(*lepFSR_eta)[i1],(*lepFSR_phi)[i1],(*lepFSR_mass)[i1]);
    lep_i2.SetPtEtaPhiM((*lepFSR_pt)[i2]*1.01,(*lepFSR_eta)[i2],(*lepFSR_phi)[i2],(*lepFSR_mass)[i2]);

    TLorentzVector lep_i1_nofsr, lep_i2_nofsr;
    lep_i1_nofsr.SetPtEtaPhiM((*lep_pt)[i1]*1.01,(*lep_eta)[i1],(*lep_phi)[i1],(*lep_mass)[i1]);
    lep_i2_nofsr.SetPtEtaPhiM((*lep_pt)[i2]*1.01,(*lep_eta)[i2],(*lep_phi)[i2],(*lep_mass)[i2]);

    TLorentzVector Zi;
    Zi = lep_i1+lep_i2;

    TLorentzVector Z1 = Zi;
    double Z1DeltaM = abs(Zi.M()-Zmass);
    int Z1_lepindex[2] = {0,0};
    if(lep_i1.Pt()>lep_i2.Pt()){ Z1_lepindex[0] = i1;  Z1_lepindex[1] = i2; }
    else{ Z1_lepindex[0] = i2;  Z1_lepindex[1] = i1; }

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

    if(Z1.Pt()<100) continue;

    if ( (Z1.M() < mZ1Low) || (Z1.M() > mZ1High) ) continue;

    if (Z1DeltaM<=minZ1DeltaM) {

      minZ1DeltaM = Z1DeltaM;

      lep_1_pt_up = ((*lepFSR_pt)[Z1_lepindex[0]])*1.01;
      lep_1_eta_up = (*lepFSR_eta)[Z1_lepindex[0]];
      lep_1_phi_up = (*lepFSR_phi)[Z1_lepindex[0]];
      lep_1_mass_up = (*lepFSR_mass)[Z1_lepindex[0]];
      lep_2_pt_up = (*lepFSR_pt)[Z1_lepindex[1]]*1.01;
      lep_2_eta_up = (*lepFSR_eta)[Z1_lepindex[1]];
      lep_2_phi_up = (*lepFSR_phi)[Z1_lepindex[1]];
      lep_2_mass_up = (*lepFSR_mass)[Z1_lepindex[1]];

      if( ((*lep_id)[Z1_lepindex[0]]+(*lep_id)[Z1_lepindex[1]])==0 ) foundZ1LCandidate_up=true;
    }

  }

  // 1% down
  for (int i=0; i<n_Zs_1m; i++){
      
      int i1 = Z_Z1L_lepindex1_1m[i]; int i2 = Z_Z1L_lepindex2_1m[i];
  
      TLorentzVector lep_i1, lep_i2;
      lep_i1.SetPtEtaPhiM((*lepFSR_pt)[i1]*0.99,(*lepFSR_eta)[i1],(*lepFSR_phi)[i1],(*lepFSR_mass)[i1]);
      lep_i2.SetPtEtaPhiM((*lepFSR_pt)[i2]*0.99,(*lepFSR_eta)[i2],(*lepFSR_phi)[i2],(*lepFSR_mass)[i2]);

      TLorentzVector lep_i1_nofsr, lep_i2_nofsr;
      lep_i1_nofsr.SetPtEtaPhiM((*lep_pt)[i1]*0.99,(*lep_eta)[i1],(*lep_phi)[i1],(*lep_mass)[i1]);
      lep_i2_nofsr.SetPtEtaPhiM((*lep_pt)[i2]*0.99,(*lep_eta)[i2],(*lep_phi)[i2],(*lep_mass)[i2]);

      TLorentzVector Zi;
      Zi = lep_i1+lep_i2;

      TLorentzVector Z1 = Zi;
      double Z1DeltaM = abs(Zi.M()-Zmass);
      int Z1_lepindex[2] = {0,0};
      if(lep_i1.Pt()>lep_i2.Pt()){ Z1_lepindex[0] = i1;  Z1_lepindex[1] = i2; }
      else{ Z1_lepindex[0] = i2;  Z1_lepindex[1] = i1; }

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

      if(Z1.Pt()<100) continue;

      if ( (Z1.M() < mZ1Low) || (Z1.M() > mZ1High) ) continue;

      if (Z1DeltaM<=minZ1DeltaM) {

        minZ1DeltaM = Z1DeltaM;

        lep_1_pt_dn = (*lepFSR_pt)[Z1_lepindex[0]]*0.99;
        lep_1_eta_dn = (*lepFSR_eta)[Z1_lepindex[0]];
        lep_1_phi_dn = (*lepFSR_phi)[Z1_lepindex[0]];
        lep_1_mass_dn = (*lepFSR_mass)[Z1_lepindex[0]];
        lep_2_pt_dn = (*lepFSR_pt)[Z1_lepindex[1]]*0.99;
        lep_2_eta_dn = (*lepFSR_eta)[Z1_lepindex[1]];
        lep_2_phi_dn = (*lepFSR_phi)[Z1_lepindex[1]];
        lep_2_mass_dn = (*lepFSR_mass)[Z1_lepindex[1]];

        if( ((*lep_id)[Z1_lepindex[0]]+(*lep_id)[Z1_lepindex[1]])==0 ) foundZ1LCandidate_dn=true;
      }

  }

}

//==================find two resovled jets=========================================
void TreeLoop::findZ2JCandidata(){
  if(verbose){cout<<"[INFO] loop jets in this events"<<endl;}

  //variables for cut table
  bool pass_jetpt30 = false;
  bool pass_jeteta2opint4 = false;
  bool pass_lepclean = false;
  bool pass_dijetpt100 = false;
  bool pass_ak4jetZm_40_180 = false;

  // Consider all Z candidates
  double minZ1DeltaM=9999.9;
  unsigned int Njets = jet_pt->GetSize();
  if(Njets<2){ return; } //found at least two jets
  passed_n_2ak4jets++;
  if(verbose){cout<<"[INFO] find at least two jets. number of jets = "<<Njets<<" in this events"<<endl;}

  int n_Zs=0;
  vector<int> Z_Z2J_jetindex1;
  vector<int> Z_Z2J_jetindex2;
  if(Njets>=2){
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

    double temp_pt = 0.0;
    if(verbose) cout<<"[INFO] start to check each ak4 pair"<<endl;
    for (int i=0; i<n_Zs; i++){

      int i1 = Z_Z2J_jetindex1[i]; int i2 = Z_Z2J_jetindex2[i];
      //int this_jetindex[2] = {i1,i2};

      TLorentzVector jet_i1, jet_i2;
      jet_i1.SetPtEtaPhiM((*jet_pt)[i1],(*jet_eta)[i1],(*jet_phi)[i1],(*jet_mass)[i1]);
      jet_i2.SetPtEtaPhiM((*jet_pt)[i2],(*jet_eta)[i2],(*jet_phi)[i2],(*jet_mass)[i2]);


      TLorentzVector Zi;
      Zi = jet_i1+jet_i2;

      TLorentzVector Z1 = Zi;
      double Z1DeltaM = abs(Zi.M()-Zmass);

      //all jet must not overlap with tight leptons
      /*
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
      */
      pass_lepclean = true;

      //sort jet in terms of Pt order
      int Z2_jetindex[2] = {0,0};
      if (jet_i1.Pt()>jet_i2.Pt()) { Z2_jetindex[0] = i1;  Z2_jetindex[1] = i2; }
      else { Z2_jetindex[0] = i2;  Z2_jetindex[1] = i1; }

      //check each jet pt and eta
      if(jet_i1.Pt()<30 || jet_i2.Pt()<30) {continue;}
      pass_jetpt30 = true;
      if(abs(jet_i1.Eta())>2.4 || abs(jet_i2.Eta())>2.4) {continue;}
      pass_jeteta2opint4 = true;

      //check dijet pt
      if(Zi.Pt()<dijetPtCut){ continue;}
      pass_dijetpt100 = true;

      //check loose dijet mass for 40-180Gev
      if(Zi.M()<mZ2Low || Zi.M()>mZ2High){ continue;}
      pass_ak4jetZm_40_180 = true;
      
      if ( Z1DeltaM<=minZ1DeltaM ) {

        minZ1DeltaM = Z1DeltaM;

        jet_Z1index_mass_bais[0] = Z2_jetindex[0];
        jet_Z1index_mass_bais[1] = Z2_jetindex[1];

        mass2jet_mass_bais = Zi.M();
        pt2jet_mass_bais = Zi.Pt();

        //if (verbose) cout<<" new best Z1L candidate: massZ1: "<<massZ1<<" (mass3l: "<<mass3l<<")"<<endl;
        foundZ2JCandidate=true;
      }
      

      //select as di-jet pt order
      if(Zi.Pt()>temp_pt){
        temp_pt = Zi.Pt();

        jet_Z1index[0] = Z2_jetindex[0];
        jet_Z1index[1] = Z2_jetindex[1];

        jet_1_btag = (*jet_isbtag)[Z2_jetindex[0]];
        jet_2_btag = (*jet_isbtag)[Z2_jetindex[1]];


        jet_1_deepbtag = (*jet_deepBtag)[Z2_jetindex[0]];
        jet_2_deepbtag = (*jet_deepBtag)[Z2_jetindex[1]];

        if(isMC){
          //cout<<"(*jet_hadronFlavour)[Z2_jetindex[0]] = " <<(*jet_hadronFlavour)[Z2_jetindex[0]]<<endl;
          //cout<<"(*jet_hadronFlavour)[Z2_jetindex[1]] = " <<(*jet_hadronFlavour)[Z2_jetindex[1]]<<endl;

          jet_1_hadronflavor = (*jet_hadronFlavour)[Z2_jetindex[0]];
          jet_2_hadronflavor = (*jet_hadronFlavour)[Z2_jetindex[1]];
          jet_1_partonflavor = (*jet_partonFlavour)[Z2_jetindex[0]];
          jet_2_partonflavor = (*jet_partonFlavour)[Z2_jetindex[1]];
        }

        mass2jet = Zi.M(); //mass2jet_up = Zi_up.M(); mass2jet_dn = Zi_dn.M();
        pt2jet = Zi.Pt(); //pt2jet_up = Zi_up.Pt(); pt2jet_dn = Zi_dn.Pt();

        jet_1_pt = (*jet_pt)[Z2_jetindex[0]];
        jet_2_pt = (*jet_pt)[Z2_jetindex[1]];

        jet_1_eta = (*jet_eta)[Z2_jetindex[0]];
        jet_2_eta = (*jet_eta)[Z2_jetindex[1]];

        jet_1_phi = (*jet_phi)[Z2_jetindex[0]];
        jet_2_phi = (*jet_phi)[Z2_jetindex[1]];

        jet_1_mass = (*jet_mass)[Z2_jetindex[0]];
        jet_2_mass = (*jet_mass)[Z2_jetindex[1]];



        foundZ2JCandidate=true;
        if(verbose) cout<<"[INFO] find resovled jet candidates"<<endl;

      }
    }
  }
  if(pass_jetpt30) passed_jetpt30++;
  if(pass_jeteta2opint4) passed_jeteta2opint4++;
  if(pass_lepclean) passed_lepclean++;
  if(pass_dijetpt100) passed_dijetpt100++;
  if(pass_ak4jetZm_40_180) passed_ak4jetZm_40_180++;
  //=============JES UP and donw===============
  if(isMC){
    unsigned int Njets_up = jet_jesup_pt->GetSize();
    int n_Zs_up=0;
    vector<int> Z_Z2Jup_jetindex1;
    vector<int> Z_Z2Jup_jetindex2;
    if(Njets_up>=2){
      for(unsigned int i=0; i<Njets_up; i++){
        for(unsigned int j=i+1; j<Njets_up; j++){

          TLorentzVector jet_i1_up, jet_i2_up;
          jet_i1_up.SetPtEtaPhiM((*jet_jesup_pt)[i],(*jet_jesup_eta)[i],(*jet_jesup_phi)[i],(*jet_jesup_mass)[i]);
          jet_i2_up.SetPtEtaPhiM((*jet_jesup_pt)[j],(*jet_jesup_eta)[j],(*jet_jesup_phi)[j],(*jet_jesup_mass)[j]);

          TLorentzVector Zjet_up;
          Zjet_up = jet_i1_up+jet_i2_up;

          if (Zjet_up.M()>0.0) {
            n_Zs_up++;
            Z_Z2Jup_jetindex1.push_back(i);
            Z_Z2Jup_jetindex2.push_back(j);
          }
        } //jet 1
      }//jet 2 

      double temp_pt_up = 0.0;
      for (int i=0; i<n_Zs_up; i++){

        int i1 = Z_Z2Jup_jetindex1[i]; int i2 = Z_Z2Jup_jetindex2[i];
        //int this_jetindex[2] = {i1,i2};
        TLorentzVector jet_i1_up, jet_i2_up;
        jet_i1_up.SetPtEtaPhiM((*jet_jesup_pt)[i1],(*jet_jesup_eta)[i1],(*jet_jesup_phi)[i1],(*jet_jesup_mass)[i1]);
        jet_i2_up.SetPtEtaPhiM((*jet_jesup_pt)[i2],(*jet_jesup_eta)[i2],(*jet_jesup_phi)[i2],(*jet_jesup_mass)[i2]);
        //jet_i1_dn.SetPtEtaPhiM((*jet_jesdn_pt)[i1],(*jet_jesdn_eta)[i1],(*jet_jesdn_phi)[i1],(*jet_jesdn_mass)[i1]);
        //jet_i2_dn.SetPtEtaPhiM((*jet_jesdn_pt)[i2],(*jet_jesdn_eta)[i2],(*jet_jesdn_phi)[i2],(*jet_jesdn_mass)[i2]);


        TLorentzVector Zi_up; //Zi_dn;
        Zi_up = jet_i1_up+jet_i2_up;
        //Zi_dn = jet_i1_dn+jet_i2_dn;

        TLorentzVector Z1_up = Zi_up;

        //sort jet in terms of Pt order
        int Z2_jetindex[2] = {0,0};
        if (jet_i1_up.Pt()>jet_i2_up.Pt()) { Z2_jetindex[0] = i1;  Z2_jetindex[1] = i2; }
        else { Z2_jetindex[0] = i2;  Z2_jetindex[1] = i1; }

        //check each jet pt and eta
        if(jet_i1_up.Pt()<30 || jet_i2_up.Pt()<30) {continue;}
        if(abs(jet_i1_up.Eta())>2.4 || abs(jet_i2_up.Eta())>2.4) {continue;}

        //check dijet pt
        if(Zi_up.Pt()<dijetPtCut){ continue;}

        //check loose dijet mass for 40-180Gev
        if(Zi_up.M()<mZ2Low || Zi_up.M()>mZ2High){ continue;}
        //select as di-jet pt order
        if(Zi_up.Pt()>temp_pt_up){
          temp_pt_up = Zi_up.Pt();

          jet_Z1index_up[0] = Z2_jetindex[0];
          jet_Z1index_up[1] = Z2_jetindex[1];

          jet_1_btag_up = (*jet_isbtag)[Z2_jetindex[0]];
          jet_2_btag_up = (*jet_isbtag)[Z2_jetindex[1]];

          jet_1_deepbtag_up = (*jet_deepBtag)[Z2_jetindex[0]];
          jet_2_deepbtag_up = (*jet_deepBtag)[Z2_jetindex[1]];

          jet_1_pt_up = (*jet_jesup_pt)[Z2_jetindex[0]]; jet_1_eta_up = (*jet_jesup_eta)[Z2_jetindex[0]]; jet_1_phi_up = (*jet_jesup_phi)[Z2_jetindex[0]]; jet_1_mass_up = (*jet_jesup_mass)[Z2_jetindex[0]];
          //jet_1_pt_dn = (*jet_jesdn_pt)[Z2_jetindex[0]]; jet_1_eta_dn = (*jet_jesdn_eta)[Z2_jetindex[0]]; jet_1_phi_dn = (*jet_jesdn_phi)[Z2_jetindex[0]]; jet_1_mass_dn = (*jet_jesdn_mass)[Z2_jetindex[0]];
          jet_2_pt_up = (*jet_jesup_pt)[Z2_jetindex[1]]; jet_2_eta_up = (*jet_jesup_eta)[Z2_jetindex[1]]; jet_2_phi_up = (*jet_jesup_phi)[Z2_jetindex[1]]; jet_2_mass_up = (*jet_jesup_mass)[Z2_jetindex[1]];
          //jet_2_pt_dn = (*jet_jesdn_pt)[Z2_jetindex[1]]; jet_2_eta_dn = (*jet_jesdn_eta)[Z2_jetindex[1]]; jet_2_phi_dn = (*jet_jesdn_phi)[Z2_jetindex[1]]; jet_2_mass_dn = (*jet_jesdn_mass)[Z2_jetindex[1]];

          mass2jet_up = Zi_up.M(); //mass2jet_dn = Zi_dn.M();
          pt2jet_up = Zi_up.Pt(); //pt2jet_dn = Zi_dn.Pt();

          foundZ2JCandidate_up=true;

        }
      }
    }
  
    //=============Down=====
    unsigned int Njets_dn = jet_jesdn_pt->GetSize();
    int n_Zs_dn=0;
    vector<int> Z_Z2Jdn_jetindex1;
    vector<int> Z_Z2Jdn_jetindex2;
    if(Njets_dn>=2){
      for(unsigned int i=0; i<Njets_dn; i++){
        for(unsigned int j=i+1; j<Njets_dn; j++){

          TLorentzVector jet_i1_dn, jet_i2_dn;
          jet_i1_dn.SetPtEtaPhiM((*jet_jesdn_pt)[i],(*jet_jesdn_eta)[i],(*jet_jesdn_phi)[i],(*jet_jesdn_mass)[i]);
          jet_i2_dn.SetPtEtaPhiM((*jet_jesdn_pt)[j],(*jet_jesdn_eta)[j],(*jet_jesdn_phi)[j],(*jet_jesdn_mass)[j]);

          TLorentzVector Zjet_dn;
          Zjet_dn = jet_i1_dn+jet_i2_dn;

          if (Zjet_dn.M()>0.0) {
            n_Zs_dn++;
            Z_Z2Jdn_jetindex1.push_back(i);
            Z_Z2Jdn_jetindex2.push_back(j);
          }
        } //jet 1
      }//jet 2 

      double temp_pt_dn = 0.0;
      for (int i=0; i<n_Zs_dn; i++){

        int i1 = Z_Z2Jdn_jetindex1[i]; int i2 = Z_Z2Jdn_jetindex2[i];
        //int this_jetindex[2] = {i1,i2};
        TLorentzVector jet_i1_dn, jet_i2_dn;
        jet_i1_dn.SetPtEtaPhiM((*jet_jesdn_pt)[i1],(*jet_jesdn_eta)[i1],(*jet_jesdn_phi)[i1],(*jet_jesdn_mass)[i1]);
        jet_i2_dn.SetPtEtaPhiM((*jet_jesdn_pt)[i2],(*jet_jesdn_eta)[i2],(*jet_jesdn_phi)[i2],(*jet_jesdn_mass)[i2]);


        TLorentzVector Zi_dn;
        Zi_dn = jet_i1_dn+jet_i2_dn;

        TLorentzVector Z1_dn = Zi_dn;

        //sort jet in terms of Pt order
        int Z2_jetindex[2] = {0,0};
        if (jet_i1_dn.Pt()>jet_i2_dn.Pt()) { Z2_jetindex[0] = i1;  Z2_jetindex[1] = i2; }
        else { Z2_jetindex[0] = i2;  Z2_jetindex[1] = i1; }

        //check each jet pt and eta
        if(jet_i1_dn.Pt()<30 || jet_i2_dn.Pt()<30) {continue;}
        if(abs(jet_i1_dn.Eta())>2.4 || abs(jet_i2_dn.Eta())>2.4) {continue;}

        //check dijet pt
        if(Zi_dn.Pt()<dijetPtCut){ continue;}

        //check loose dijet mass for 40-180Gev
        if(Zi_dn.M()<mZ2Low || Zi_dn.M()>mZ2High){ continue;}
        //select as di-jet pt order
        if(Zi_dn.Pt()>temp_pt_dn){
          temp_pt_dn = Zi_dn.Pt();

          jet_Z1index_dn[0] = Z2_jetindex[0];
          jet_Z1index_dn[1] = Z2_jetindex[1];

          jet_1_btag_dn = (*jet_isbtag)[Z2_jetindex[0]];
          jet_2_btag_dn = (*jet_isbtag)[Z2_jetindex[1]];

          jet_1_deepbtag = (*jet_deepBtag)[Z2_jetindex[0]];
          jet_2_deepbtag = (*jet_deepBtag)[Z2_jetindex[1]];

          jet_1_pt_dn = (*jet_jesdn_pt)[Z2_jetindex[0]]; jet_1_eta_dn = (*jet_jesdn_eta)[Z2_jetindex[0]]; jet_1_phi_dn = (*jet_jesdn_phi)[Z2_jetindex[0]]; jet_1_mass_dn = (*jet_jesdn_mass)[Z2_jetindex[0]];
          jet_2_pt_dn = (*jet_jesdn_pt)[Z2_jetindex[1]]; jet_2_eta_dn = (*jet_jesdn_eta)[Z2_jetindex[1]]; jet_2_phi_dn = (*jet_jesdn_phi)[Z2_jetindex[1]]; jet_2_mass_dn = (*jet_jesdn_mass)[Z2_jetindex[1]];

          mass2jet_dn = Zi_dn.M();
          pt2jet_dn = Zi_dn.Pt();

          foundZ2JCandidate_dn=true;

        }
      }
    }
  }

}

//==================find mergedjets==================================================
void TreeLoop::findZ2MergedCandidata(){
  if(verbose) cout<<"[INFO] loop mergedjets in this event"<<endl;

  int nmergedjets = mergedjet_pt->GetSize();
  if(verbose) cout<<"nmergedjets = "<<nmergedjets<<endl;

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
    if(verbose) cout<<"(*mergedjet_pt)[i] = "<<(*mergedjet_pt)[i]<<endl;
    if((*mergedjet_pt)[i]<200) continue;
    pass_mergedjetsPt200 = true;

    if(verbose) cout<<"(*mergedjet_eta)[i] = "<<(*mergedjet_eta)[i]<<endl;
    if(abs((*mergedjet_eta)[i])>2.4) continue;
    pass_mergedjetEta2opint4 = true;

    if(verbose) cout<<"*mergedjet_subjet_softDropMass)[i] = "<<(*mergedjet_subjet_softDropMass)[i]<<endl;
    if((*mergedjet_subjet_softDropMass)[i]<mZ2Low || (*mergedjet_subjet_softDropMass)[i]>mZ2High) continue;
    pass_mergedmass_40_180 = true;

    if(verbose) cout<<"(*mergedjet_Net_Xbb_de)[i] = "<<(*mergedjet_Net_Xbb_de)[i]<<endl;
    if(verbose) cout<<"(*mergedjet_Net_Xcc_de)[i] = "<<(*mergedjet_Net_Xcc_de)[i]<<endl;
    if(verbose) cout<<"(*mergedjet_Net_Xqq_de)[i] = "<<(*mergedjet_Net_Xqq_de)[i]<<endl;
    float temp_particleNetZvsQCD = (*mergedjet_Net_Xbb_de)[i]+(*mergedjet_Net_Xcc_de)[i]+(*mergedjet_Net_Xqq_de)[i];
    float temp_particleNetZbbvslight = (*mergedjet_Net_Xbb_de)[i]/temp_particleNetZvsQCD;
    float temp_particleNetXbbvsQCD = (*mergedjet_Net_Xbb_de)[i]/((*mergedjet_Net_Xbb_de)[i]+(*mergedjet_Net_QCDbb_de)[i]+(*mergedjet_Net_QCDcc_de)[i]+(*mergedjet_Net_QCDother_de)[i]+(*mergedjet_Net_QCDb_de)[i]+(*mergedjet_Net_QCDc_de)[i]);
    if(temp_particleNetZvsQCD>=0.9) pass_particleNetZvsQCD0opint9 = true;
    //cout<<"this passed ZvsQCD = "<<temp_particleNetZvsQCD<<endl;
    //pass_particleNetZvsQCD0opint9 = true;

    foundZ2MergedCandidata = true;
    if((*mergedjet_pt)[i]>this_pt){
      this_pt = (*mergedjet_pt)[i];
      ptmerged = this_pt;
      etamerged = (*mergedjet_eta)[i];
      phimerged = (*mergedjet_phi)[i];
      massmerged = (*mergedjet_subjet_softDropMass)[i];
      merged_Z1index = i;
      particleNetZvsQCD = temp_particleNetZvsQCD;
      particleNetZbbvslight = temp_particleNetZbbvslight;
      particleNetXbbvsQCD = temp_particleNetXbbvsQCD;
      if(verbose) cout<<"found merged jet candidates"<<endl;
    }
  }

  if(pass_mergedjetsPt200) passed_mergedjetsPt200++;
  if(pass_mergedjetEta2opint4) passed_mergedjetEta2opint4++;
  if(pass_mergedmass_40_180) passed_mergedmass_40_180++;
  if(pass_particleNetZvsQCD0opint9) passed_particleNetZvsQCD0opint9++;

  if(isMC){
    //=====up
    int nmergedjets_up = mergedjet_jesup_pt->GetSize();
    if(nmergedjets_up>0){
      float this_pt_up = 0.0;
      for(int i=0; i<nmergedjets_up; i++){
        if((*mergedjet_jesup_pt)[i]<200) continue;
        if(abs((*mergedjet_jesup_eta)[i])>2.4) continue;
        if((*mergedjet_jesup_mass)[i]<mZ2Low || (*mergedjet_jesup_mass)[i]>mZ2High) continue;
        float temp_particleNetZvsQCD_up = (*mergedjet_Net_Xbb_de)[i]+(*mergedjet_Net_Xcc_de)[i]+(*mergedjet_Net_Xqq_de)[i];
        float temp_particleNetZbbvslight_up = (*mergedjet_Net_Xbb_de)[i]/temp_particleNetZvsQCD_up;
        float temp_particleNetXbbvsQCD_up = (*mergedjet_Net_Xbb_de)[i]/((*mergedjet_Net_Xbb_de)[i]+(*mergedjet_Net_QCDbb_de)[i]+(*mergedjet_Net_QCDcc_de)[i]+(*mergedjet_Net_QCDother_de)[i]+(*mergedjet_Net_QCDb_de)[i]+(*mergedjet_Net_QCDc_de)[i]);
        foundZ2MergedCandidata_up = true;
        if((*mergedjet_jesup_pt)[i]>this_pt_up){
          this_pt_up = (*mergedjet_jesup_pt)[i];
          ptmerged_up = this_pt_up;
          massmerged_up = (*mergedjet_jesup_mass)[i];
          merged_Z1index_up = i;
          particleNetZvsQCD_up = temp_particleNetZvsQCD_up;
          particleNetZbbvslight_up = temp_particleNetZbbvslight_up;
          particleNetXbbvsQCD_up = temp_particleNetXbbvsQCD_up;
        }
      }
    }
    //===dn
    int nmergedjets_dn = mergedjet_jesdn_pt->GetSize();
    if(nmergedjets_dn>0){
      float this_pt_dn = 0.0;
      for(int i=0; i<nmergedjets_dn; i++){
        if((*mergedjet_jesdn_pt)[i]<200) continue;
        if(abs((*mergedjet_jesdn_eta)[i])>2.4) continue;
        if((*mergedjet_jesdn_mass)[i]<mZ2Low || (*mergedjet_jesdn_mass)[i]>mZ2High) continue;
        float temp_particleNetZvsQCD_dn = (*mergedjet_Net_Xbb_de)[i]+(*mergedjet_Net_Xcc_de)[i]+(*mergedjet_Net_Xqq_de)[i];
        float temp_particleNetZbbvslight_dn = (*mergedjet_Net_Xbb_de)[i]/temp_particleNetZvsQCD_dn;
        float temp_particleNetXbbvsQCD_dn = (*mergedjet_Net_Xbb_de)[i]/((*mergedjet_Net_Xbb_de)[i]+(*mergedjet_Net_QCDbb_de)[i]+(*mergedjet_Net_QCDcc_de)[i]+(*mergedjet_Net_QCDother_de)[i]+(*mergedjet_Net_QCDb_de)[i]+(*mergedjet_Net_QCDc_de)[i]);
        foundZ2MergedCandidata_dn = true;
        if((*mergedjet_jesdn_pt)[i]>this_pt_dn){
          this_pt_dn = (*mergedjet_jesdn_pt)[i];
          ptmerged_dn = this_pt_dn;
          massmerged_dn = (*mergedjet_jesdn_mass)[i];
          merged_Z1index_dn = i;
          particleNetZvsQCD_dn = temp_particleNetZvsQCD_dn;
          particleNetZbbvslight_dn = temp_particleNetZbbvslight_dn;
          particleNetXbbvsQCD_dn = temp_particleNetXbbvsQCD_dn;
        }
      }
    }
  }
  //cout<<"this passed_particleNetZvsQCD0opint9 = "<<passed_particleNetZvsQCD0opint9<<endl;

}

//======================GEN=======================================================
void TreeLoop::SetGen(){
  //cout<<"[INFO] start to set GEN variables"<<endl;
  //higgs mass
  int nGEN_higgs = GENH_mass->GetSize();
  if(nGEN_higgs>0){
    for(int i=0; i<nGEN_higgs; i++){
      if( (*GENH_status)[i]==22 && (*GENH_isHard)[i]){
        GEN_H1_mass = (*GENH_mass)[i];
        GEN_H1_pt = (*GENH_pt)[i];
        GEN_H1_eta = (*GENH_eta)[i];
        GEN_H1_phi = (*GENH_phi)[i];
      }
      else{ continue; }
    }
  }
  //cout<<"[INFO] GEN_H1_mass = "<<GEN_H1_mass<<endl;
}

//======================GEN VBF=======================================================
void TreeLoop::SetVBFGen(){
  //VBF quark
  int nGEN_VBF  = GEN_VBF_pt->GetSize();
  if(nGEN_VBF>1){
    GEN_associated1_pt = (*GEN_VBF_pt)[0];
    GEN_associated1_eta = (*GEN_VBF_eta)[0];
    GEN_associated1_phi = (*GEN_VBF_phi)[0];
    GEN_associated1_mass = (*GEN_VBF_mass)[0];
    GEN_associated2_pt = (*GEN_VBF_pt)[1];
    GEN_associated2_eta = (*GEN_VBF_eta)[1];
    GEN_associated2_phi = (*GEN_VBF_phi)[1];
    GEN_associated2_mass = (*GEN_VBF_mass)[1];
    GEN_associated12_Deta = GEN_associated1_eta-GEN_associated2_eta;

    TLorentzVector GEN_associated1,GEN_associated2;
    GEN_associated1.SetPtEtaPhiM(GEN_associated1_mass,GEN_associated1_eta,GEN_associated1_phi,GEN_associated1_mass);
    GEN_associated2.SetPtEtaPhiM(GEN_associated2_mass,GEN_associated2_eta,GEN_associated2_phi,GEN_associated2_mass);
    GEN_associated12_mass = (GEN_associated1+GEN_associated2).M();

    //match VBF quark to GEN_jet
    int nGEN_jet = GENjet_pt->GetSize();
    int match1 = 0;
    int match2 = 0;
    int match1_index = -1;
    int match2_index = -1;
    for(int i=0; i<nGEN_jet; i++){
      double this1_dr;
      this1_dr = deltaR((*GENjet_eta)[i],(*GENjet_phi)[i],GEN_associated1_eta,GEN_associated1_phi);
      if(this1_dr<0.4){
        match1++;
        match1_index = i;
      }

      double this2_dr;
      this2_dr = deltaR((*GENjet_eta)[i],(*GENjet_phi)[i],GEN_associated2_eta,GEN_associated2_phi);
      if(this2_dr<0.4){
        match2++;
        match2_index = i;
      }
    }
    if(match1>1){
      if(verbose) cout<<"[!!!!] match1 = "<<match1<<endl;
    }
    if(match2>1){
      if(verbose) cout<<"[!!!!] match2 = "<<match2<<endl;
    }
    if(match1!=0 && match2!=0){
      passedGenquarkMatch = true;
      if(match1_index==match2_index){
        if(verbose) cout<<"[!!!!!] match to same gen jet"<<endl;
      }
    }

    if(passedGenquarkMatch){
      n_match_vbfquarks_to_genjet ++;
      GEN_quark1_match_pt = (*GENjet_pt)[match1_index];
      GEN_quark1_match_eta = (*GENjet_eta)[match1_index];
      GEN_quark1_match_phi = (*GENjet_phi)[match1_index];
      GEN_quark1_match_mass = (*GENjet_mass)[match1_index];

      GEN_quark2_match_pt = (*GENjet_pt)[match2_index];
      GEN_quark2_match_eta = (*GENjet_eta)[match2_index];
      GEN_quark2_match_phi = (*GENjet_phi)[match2_index];
      GEN_quark2_match_mass = (*GENjet_mass)[match2_index];

      TLorentzVector match1_GENjet, match2_GENjet;
      match1_GENjet.SetPtEtaPhiM(GEN_quark1_match_pt,GEN_quark1_match_eta,GEN_quark1_match_phi,GEN_quark1_match_mass);
      match2_GENjet.SetPtEtaPhiM(GEN_quark2_match_pt,GEN_quark2_match_eta,GEN_quark2_match_phi,GEN_quark2_match_mass);
      GEN_quark12_match_mass = (match1_GENjet+match2_GENjet).M();
    }

    //match VBF quark to reco-jet
    int njet = jet_pt->GetSize();
    int match1_reco = 0;
    int match2_reco = 0;
    for(int i=0; i<njet; i++){
      double this1_dr;
      this1_dr = deltaR((*jet_eta)[i],(*jet_phi)[i],GEN_associated1_eta,GEN_associated1_phi);
      if(this1_dr<0.4){
        match1_reco++;
        match1_recoindex = i;
      }

      double this2_dr;
      this2_dr = deltaR((*jet_eta)[i],(*jet_phi)[i],GEN_associated2_eta,GEN_associated2_phi);
      if(this2_dr<0.4){
        match2_reco++;
        match2_recoindex = i;
      }
    }
    if(match1_reco>1){
      if(verbose) cout<<"[!!!!] match1 reco = "<<match1_reco<<endl;
    }
    if(match2_reco>1){
      if(verbose) cout<<"[!!!!] match2 reco= "<<match2_reco<<endl;
    }
    if(match1_reco!=0 && match2_reco!=0){
      passedRecoquarkMatch = true;
      if(match1_recoindex==match2_recoindex){
        if(verbose) cout<<"[!!!!!] match to same gen quark"<<endl;
      }
    }

    if(passedRecoquarkMatch){
      n_match_vbfquarks_to_recojet ++;
      Reco_quark1_match_pt = (*jet_pt)[match1_recoindex];
      Reco_quark1_match_eta = (*jet_eta)[match1_recoindex];
      Reco_quark1_match_phi = (*jet_phi)[match1_recoindex];
      Reco_quark1_match_mass = (*jet_mass)[match1_recoindex];

      Reco_quark2_match_pt = (*jet_pt)[match2_recoindex];
      Reco_quark2_match_eta = (*jet_eta)[match2_recoindex];
      Reco_quark2_match_phi = (*jet_phi)[match2_recoindex];
      Reco_quark2_match_mass = (*jet_mass)[match2_recoindex];

      Reco_quark12_match_DEta = abs(Reco_quark1_match_eta-Reco_quark2_match_eta);

      TLorentzVector match1_Recojet, match2_Recojet;
      match1_Recojet.SetPtEtaPhiM(Reco_quark1_match_pt,Reco_quark1_match_eta,Reco_quark1_match_phi,Reco_quark1_match_mass);
      match2_Recojet.SetPtEtaPhiM(Reco_quark2_match_pt,Reco_quark2_match_eta,Reco_quark2_match_phi,Reco_quark2_match_mass);
      Reco_quark12_match_mass = (match1_Recojet+match2_Recojet).M();
    }

  }

  //match Z quark to reco-jet




  //match Z quark to selected reco-jet
  /*
  if(foundmergedOnly){
    int n_GENZ = GEN_Zq_pt->GetSize();
    for(int i=0; i<n_GENZ; i++){
      double this_DR = deltaR((*GEN_Zq_eta)[i],(*GEN_Zq_phi)[i],(*mergedjet_eta)[merged_Z1index],(*mergedjet_phi)[merged_Z1index]);
      DR_merged_GenZ.push_back(this_DR);
      if(this_DR<0.8){
        DR_merged_GenZ_matched.push_back(this_DR);
        matched_merged_GEN_Z = true;
      }
    }

    for(int i=0; i<n_GENZ; i++){
      double this_DR = deltaR((*GEN_Zq_eta)[i],(*GEN_Zq_phi)[i],associatedjet_eta[0],associatedjet_phi[0]);
      DR_associatedjet1_GenZ.push_back(this_DR);
      if(this_DR<0.4){
        DR_associatedjet1_GenZ_matched.push_back(this_DR);
        matched_associatedjet1_GEN_Z = true;
      }
    }

    for(int i=0; i<n_GENZ; i++){
      double this_DR = deltaR((*GEN_Zq_eta)[i],(*GEN_Zq_phi)[i],associatedjet_eta[1],associatedjet_phi[1]);
      DR_associatedjet2_GenZ.push_back(this_DR);
      if(this_DR<0.4){
        DR_associatedjet2_GenZ_matched.push_back(this_DR);
        matched_associatedjet2_GEN_Z = true;
      }
    }

    if(matched_associatedjet2_GEN_Z && matched_associatedjet1_GEN_Z){
      matched_associatedjet_GEN_Z = true;
    }else if((!matched_associatedjet1_GEN_Z && matched_associatedjet2_GEN_Z) || (matched_associatedjet1_GEN_Z && !matched_associatedjet2_GEN_Z)){
      matched_associatedjetone_GEN_Z = true;
    }


  }

  if(foundresolvedOnly){
    int n_GENZ = GEN_Zq_pt->GetSize();
    for(int i=0; i<n_GENZ; i++){
      double this_DR = deltaR((*GEN_Zq_eta)[i],(*GEN_Zq_phi)[i],(*jet_eta)[jet_Z1index[0]],(*jet_phi)[jet_Z1index[0]]);
      DR_resovled1_GenZ.push_back(this_DR);

      if(this_DR<0.4){
        DR_resovled1_GenZ_matched.push_back(this_DR);
        matched_resovled1_GEN_Z = true;
      }
    }

    for(int i=0; i<n_GENZ; i++){
      double this_DR = deltaR((*GEN_Zq_eta)[i],(*GEN_Zq_phi)[i],(*jet_eta)[jet_Z1index[1]],(*jet_phi)[jet_Z1index[1]]);
      DR_resovled2_GenZ.push_back(this_DR);

      if(this_DR<0.4){
        DR_resovled2_GenZ_matched.push_back(this_DR);
        matched_resovled2_GEN_Z = true;
      }
    }

    if(matched_resovled2_GEN_Z && matched_resovled1_GEN_Z){
      matched_resovled_GEN_Z = true;
    }else if((!matched_resovled2_GEN_Z && matched_resovled1_GEN_Z) || (matched_resovled2_GEN_Z && !matched_resovled1_GEN_Z)){
      matched_resovledone_GEN_Z = true;
    }

  }
  */

}

//=========================set MEs from file==========================================
void TreeLoop::SetMEsFile(std::string melafile){// Set the MEs
  // ME lists
  setMatrixElementListFromFile(
    //"${CMSSW_BASE}/src/HZZAnalysis/ANATree/data/RecoProbabilities_2000.me",
    melafile,
    //"AJetsVBFProbabilities_SpinZero_JHUGen,AJetsQCDProbabilities_SpinZero_JHUGen",
    "AJetsVBFProbabilities_SpinZero_JHUGen,AJetsQCDProbabilities_SpinZero_JHUGen,DecayProbabilities_SpinZero_JHUGen,LHE_DecayProbabilities_MCFM,LHE_PropagatorRewgt",
    //"AJetsVBFProbabilities_SpinZero_JHUGen,AJetsQCDProbabilities_SpinZero_JHUGen,AJetsVHProbabilities_SpinZero_JHUGen,PMAVJJ_SUPERDIJETMELA",
    //false
    true
  );

  // Build the MEs if they are specified
  if (!lheMElist.empty() || !recoMElist.empty()){
    // Set up MELA (done only once inside IvyMELAHelpers)
    //IvyMELAHelpers::setupMela(tempyear, 125., MiscUtils::INFO);
    IvyMELAHelpers::setupMela(tempyear, 125., MiscUtils::ERROR);
    //IvyMELAHelpers::setupMela(year, 125., MiscUtils::DEBUG_VERBOSE);
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
}

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
  lep_dataMC = new TTreeReaderArray<float>(*myreader,"lep_dataMC");
  lep_pterr = new TTreeReaderArray<double>(*myreader,"lep_pterr");
  passedTrig = new TTreeReaderValue<bool>(*myreader,"passedTrig");

  eventWeight = new TTreeReaderValue<float>(*myreader,"eventWeight");
  genWeight = new TTreeReaderValue<float>(*myreader,"genWeight");
  pileupWeight = new TTreeReaderValue<float>(*myreader,"pileupWeight");
  prefiringWeight = new TTreeReaderValue<float>(*myreader,"prefiringWeight");
  Run = new TTreeReaderValue<ULong64_t>(*myreader,"Run");
  Event = new TTreeReaderValue<ULong64_t>(*myreader,"Event");
  LumiSect = new TTreeReaderValue<ULong64_t>(*myreader,"LumiSect");


  jet_pt = new TTreeReaderArray<double>(*myreader, "jet_pt");
  jet_eta = new TTreeReaderArray<double>(*myreader, "jet_eta");
  jet_phi = new TTreeReaderArray<double>(*myreader, "jet_phi");
  jet_mass = new TTreeReaderArray<double>(*myreader, "jet_mass");
  jet_isbtag = new TTreeReaderArray<int>(*myreader,"jet_isbtag");
  jet_deepBtag = new TTreeReaderArray<float>(*myreader,"jet_deepBtag");
  jet_hadronFlavour = new TTreeReaderArray<int>(*myreader,"jet_hadronFlavour");
  jet_partonFlavour = new TTreeReaderArray<int>(*myreader,"jet_partonFlavour");

  jet_jesup_pt = new TTreeReaderArray<double>(*myreader,"jet_jesup_pt");
  jet_jesup_eta = new TTreeReaderArray<double>(*myreader,"jet_jesup_eta");
  jet_jesup_phi = new TTreeReaderArray<double>(*myreader,"jet_jesup_phi");
  jet_jesup_mass = new TTreeReaderArray<double>(*myreader,"jet_jesup_mass");
  jet_jesdn_pt = new TTreeReaderArray<double>(*myreader,"jet_jesdn_pt");
  jet_jesdn_eta = new TTreeReaderArray<double>(*myreader,"jet_jesdn_eta");
  jet_jesdn_phi = new TTreeReaderArray<double>(*myreader,"jet_jesdn_phi");
  jet_jesdn_mass = new TTreeReaderArray<double>(*myreader,"jet_jesdn_mass");

  jet_jerup_pt = new TTreeReaderArray<double>(*myreader,"jet_jerup_pt");
  jet_jerup_eta = new TTreeReaderArray<double>(*myreader,"jet_jerup_eta");
  jet_jerup_phi = new TTreeReaderArray<double>(*myreader,"jet_jerup_phi");
  jet_jerup_mass = new TTreeReaderArray<double>(*myreader,"jet_jerup_mass");
  jet_jerdn_pt = new TTreeReaderArray<double>(*myreader,"jet_jerdn_pt");
  jet_jerdn_eta = new TTreeReaderArray<double>(*myreader,"jet_jerdn_eta");
  jet_jerdn_phi = new TTreeReaderArray<double>(*myreader,"jet_jerdn_phi");
  jet_jerdn_mass = new TTreeReaderArray<double>(*myreader,"jet_jerdn_mass");

  mergedjet_jerup_pt = new TTreeReaderArray<float>(*myreader,"mergedjet_jerup_pt");
  mergedjet_jerdn_pt = new TTreeReaderArray<float>(*myreader,"mergedjet_jerdn_pt");
  mergedjet_jer_pterr = new TTreeReaderArray<float>(*myreader,"mergedjet_jer_pterr");
  mergedjet_jer_phierr = new TTreeReaderArray<float>(*myreader,"mergedjet_jer_phierr");

  if(isMC){
    cout<<"read merged jes from file"<<endl;
    mergedjet_jesup_pt = new TTreeReaderArray<float>(*myreader,"mergedjet_jesup_pt");
    mergedjet_jesup_eta = new TTreeReaderArray<float>(*myreader,"mergedjet_jesup_eta");
    mergedjet_jesup_phi = new TTreeReaderArray<float>(*myreader,"mergedjet_jesup_phi");
    mergedjet_jesup_mass = new TTreeReaderArray<float>(*myreader,"mergedjet_jesup_mass");
    mergedjet_jesdn_pt = new TTreeReaderArray<float>(*myreader,"mergedjet_jesdn_pt");
    mergedjet_jesdn_eta = new TTreeReaderArray<float>(*myreader,"mergedjet_jesdn_eta");
    mergedjet_jesdn_phi = new TTreeReaderArray<float>(*myreader,"mergedjet_jesdn_phi");
    mergedjet_jesdn_mass = new TTreeReaderArray<float>(*myreader,"mergedjet_jesdn_mass");
  }

  mergedjet_pt = new TTreeReaderArray<float>(*myreader,"mergedjet_pt");
  mergedjet_eta = new TTreeReaderArray<float>(*myreader,"mergedjet_eta");
  mergedjet_phi = new TTreeReaderArray<float>(*myreader,"mergedjet_phi");
  mergedjet_subjet_softDropMass = new TTreeReaderArray<float>(*myreader,"mergedjet_subjet_softDropMass");
  mergedjet_Net_Xbb_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_Xbb_de");
  mergedjet_Net_Xcc_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_Xcc_de");
  mergedjet_Net_Xqq_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_Xqq_de");
  mergedjet_Net_QCDbb_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_QCDbb_de");
  mergedjet_Net_QCDcc_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_QCDcc_de");
  mergedjet_Net_QCDother_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_QCDother_de");
  mergedjet_Net_QCDb_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_QCDb_de");
  mergedjet_Net_QCDc_de = new TTreeReaderArray<float>(*myreader,"mergedjet_Net_QCDc_de");
  mergedjet_nsubjet = new TTreeReaderArray<int>(*myreader,"mergedjet_nsubjet");
  mergedjet_subjet_pt = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_pt");
  mergedjet_subjet_eta = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_eta");
  mergedjet_subjet_phi = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_phi");
  mergedjet_subjet_mass = new TTreeReaderArray<vector<float>>(*myreader,"mergedjet_subjet_mass");
  mergedjet_nbHadrons = new TTreeReaderArray<int>(*myreader,"mergedjet_nbHadrons");
  mergedjet_ncHadrons = new TTreeReaderArray<int>(*myreader,"mergedjet_ncHadrons");

  met = new TTreeReaderValue<float>(*myreader,"met");
  met_phi = new TTreeReaderValue<float>(*myreader,"met_phi");


  GEN_Zq_pt = new TTreeReaderArray<double>(*myreader,"GEN_Zq_pt");
  GEN_Zq_eta = new TTreeReaderArray<double>(*myreader,"GEN_Zq_eta");
  GEN_Zq_phi = new TTreeReaderArray<double>(*myreader,"GEN_Zq_phi");
  GEN_Zq_mass = new TTreeReaderArray<double>(*myreader,"GEN_Zq_mass");

  GEN_q_pt = new TTreeReaderArray<double>(*myreader,"GEN_q_pt");
  GEN_q_eta = new TTreeReaderArray<double>(*myreader,"GEN_q_eta");
  GEN_q_phi = new TTreeReaderArray<double>(*myreader,"GEN_q_phi");
  GEN_q_mass = new TTreeReaderArray<double>(*myreader,"GEN_q_mass");

  GENjet_pt = new TTreeReaderArray<double>(*myreader,"GENjet_pt");
  GENjet_eta = new TTreeReaderArray<double>(*myreader,"GENjet_eta");
  GENjet_phi = new TTreeReaderArray<double>(*myreader,"GENjet_phi");
  GENjet_mass = new TTreeReaderArray<double>(*myreader,"GENjet_mass");

  GEN_Zq_id = new TTreeReaderArray<int>(*myreader,"GEN_Zq_id");
  GEN_q_id = new TTreeReaderArray<int>(*myreader,"GEN_q_id");
  GEN_q_status = new TTreeReaderArray<int>(*myreader,"GEN_q_status");
  GEN_q_Momid = new TTreeReaderArray<int>(*myreader,"GEN_q_Momid");
  GEN_q_MomMomid = new TTreeReaderArray<int>(*myreader,"GEN_q_MomMomid");
  GEN_q_nDaughters = new TTreeReaderArray<int>(*myreader,"GEN_q_nDaughters");

  GEN_qdau_id = new TTreeReaderArray<vector<int>>(*myreader,"GEN_qdau_id");
  GEN_qdau_status = new TTreeReaderArray<vector<int>>(*myreader,"GEN_qdau_status");

  GEN_qdau_pt = new TTreeReaderArray<vector<double>>(*myreader,"GEN_qdau_pt");
  GEN_qdau_eta = new TTreeReaderArray<vector<double>>(*myreader,"GEN_qdau_eta");
  GEN_qdau_phi = new TTreeReaderArray<vector<double>>(*myreader,"GEN_qdau_phi");
  GEN_qdau_mass = new TTreeReaderArray<vector<double>>(*myreader,"GEN_qdau_mass");
  GEN_VBF_pt = new TTreeReaderArray<double>(*myreader,"GEN_VBF_pt");
  GEN_VBF_eta = new TTreeReaderArray<double>(*myreader,"GEN_VBF_eta");
  GEN_VBF_phi = new TTreeReaderArray<double>(*myreader,"GEN_VBF_phi");
  GEN_VBF_mass = new TTreeReaderArray<double>(*myreader,"GEN_VBF_mass");

  GENH_status = new TTreeReaderArray<double>(*myreader,"GENH_status");
  GENH_isHard = new TTreeReaderArray<int>(*myreader,"GENH_isHard");
  GENH_mass = new TTreeReaderArray<double>(*myreader,"GENH_mass");
  GENH_pt = new TTreeReaderArray<double>(*myreader,"GENH_pt");
  GENH_eta = new TTreeReaderArray<double>(*myreader,"GENH_eta");
  GENH_phi = new TTreeReaderArray<double>(*myreader,"GENH_phi");

  passedEventsTree_All->Branch("lep_1_pt",&lep_1_pt);
  passedEventsTree_All->Branch("lep_1_phi",&lep_1_phi);
  passedEventsTree_All->Branch("lep_1_mass",&lep_1_mass);
  passedEventsTree_All->Branch("lep_2_pt",&lep_2_pt);
  passedEventsTree_All->Branch("lep_1_eta",&lep_1_eta);
  passedEventsTree_All->Branch("lep_2_eta",&lep_2_eta);
  passedEventsTree_All->Branch("lep_2_phi",&lep_2_phi);
  passedEventsTree_All->Branch("lep_2_mass",&lep_2_mass);
  passedEventsTree_All->Branch("lep_1_pt_up",&lep_1_pt_up);
  passedEventsTree_All->Branch("lep_1_eta_up",&lep_1_eta_up);
  passedEventsTree_All->Branch("lep_1_phi_up",&lep_1_phi_up);
  passedEventsTree_All->Branch("lep_1_mass_up",&lep_1_mass_up);
  passedEventsTree_All->Branch("lep_2_pt_up",&lep_2_pt_up);
  passedEventsTree_All->Branch("lep_2_eta_up",&lep_2_eta_up);
  passedEventsTree_All->Branch("lep_2_phi_up",&lep_2_phi_up);
  passedEventsTree_All->Branch("lep_2_mass_up",&lep_2_mass_up);
  passedEventsTree_All->Branch("lep_1_pt_dn",&lep_1_pt_dn);
  passedEventsTree_All->Branch("lep_1_eta_dn",&lep_1_eta_dn);
  passedEventsTree_All->Branch("lep_1_phi_dn",&lep_1_phi_dn);
  passedEventsTree_All->Branch("lep_1_mass_dn",&lep_1_mass_dn);
  passedEventsTree_All->Branch("lep_2_pt_dn",&lep_2_pt_dn);
  passedEventsTree_All->Branch("lep_2_eta_dn",&lep_2_eta_dn);
  passedEventsTree_All->Branch("lep_2_phi_dn",&lep_2_phi_dn);
  passedEventsTree_All->Branch("lep_2_mass_dn",&lep_2_mass_dn);
  passedEventsTree_All->Branch("Nleptons",&Nleptons);
  passedEventsTree_All->Branch("Ntightleptons",&Ntightleptons);


  passedEventsTree_All->Branch("mass2jet",&mass2jet);
  passedEventsTree_All->Branch("mass2jet_mass_bais",&mass2jet_mass_bais);
  passedEventsTree_All->Branch("mass2jet_up",&mass2jet_up);
  passedEventsTree_All->Branch("mass2jet_dn",&mass2jet_dn);
  passedEventsTree_All->Branch("pt2jet",&pt2jet);
  passedEventsTree_All->Branch("pt2jet_mass_bais",&pt2jet_mass_bais);
  passedEventsTree_All->Branch("pt2jet_up",&pt2jet_up);
  passedEventsTree_All->Branch("pt2jet_dn",&pt2jet_dn);
  passedEventsTree_All->Branch("mass2l",&mass2l);
  passedEventsTree_All->Branch("pt2l",&pt2l);
  passedEventsTree_All->Branch("mass2l2jet",&mass2l2jet);
  passedEventsTree_All->Branch("mass2l2jet_mass_bais",&mass2l2jet_mass_bais);
  passedEventsTree_All->Branch("mass2l2jet_up",&mass2l2jet_up);
  passedEventsTree_All->Branch("mass2l2jet_dn",&mass2l2jet_dn);
  passedEventsTree_All->Branch("n_jets",&n_jets);
  passedEventsTree_All->Branch("n_mergedjets",&n_mergedjets);

  passedEventsTree_All->Branch("mass2lj",&mass2lj);
  passedEventsTree_All->Branch("mass2lj_up",&mass2lj_up);
  passedEventsTree_All->Branch("mass2lj_dn",&mass2lj_dn);
  passedEventsTree_All->Branch("KD_jjVBF",&KD_jjVBF);
  passedEventsTree_All->Branch("KD_jjVBF_up",&KD_jjVBF_up);
  passedEventsTree_All->Branch("KD_jjVBF_dn",&KD_jjVBF_dn);
  passedEventsTree_All->Branch("KD_jVBF",&KD_jVBF);
  passedEventsTree_All->Branch("KD_JJVBF",&KD_JJVBF);
  passedEventsTree_All->Branch("KD_JVBF_up",&KD_JVBF_up);
  passedEventsTree_All->Branch("KD_JVBF_dn",&KD_JVBF_dn);
  passedEventsTree_All->Branch("KD_JVBF",&KD_JVBF);
  passedEventsTree_All->Branch("KD_ZJ",&KD_ZJ);
  passedEventsTree_All->Branch("KD_ZJ_up",&KD_ZJ_up);
  passedEventsTree_All->Branch("KD_ZJ_dn",&KD_ZJ_dn);
  passedEventsTree_All->Branch("KD_Zjj",&KD_Zjj);
  passedEventsTree_All->Branch("KD_Zjj_up",&KD_Zjj_up);
  passedEventsTree_All->Branch("KD_Zjj_dn",&KD_Zjj_dn);
  passedEventsTree_All->Branch("particleNetZvsQCD",&particleNetZvsQCD);
  passedEventsTree_All->Branch("particleNetZvsQCD_up",&particleNetZvsQCD_up);
  passedEventsTree_All->Branch("particleNetZvsQCD_dn",&particleNetZvsQCD_dn);
  passedEventsTree_All->Branch("particleNetZbbvslight",&particleNetZbbvslight);
  passedEventsTree_All->Branch("particleNetZbbvslight_up",&particleNetZbbvslight_up);
  passedEventsTree_All->Branch("particleNetZbbvslight_dn",&particleNetZbbvslight_dn);
  passedEventsTree_All->Branch("particleNetXbbvsQCD",&particleNetXbbvsQCD);
  passedEventsTree_All->Branch("particleNetXbbvsQCD_up",&particleNetXbbvsQCD_up);
  passedEventsTree_All->Branch("particleNetXbbvsQCD_dn",&particleNetXbbvsQCD_dn);
  passedEventsTree_All->Branch("massmerged",&massmerged);
  passedEventsTree_All->Branch("massmerged_up",&massmerged_up);
  passedEventsTree_All->Branch("massmerged_dn",&massmerged_dn);
  passedEventsTree_All->Branch("ptmerged",&ptmerged);
  passedEventsTree_All->Branch("ptmerged_up",&ptmerged_up);
  passedEventsTree_All->Branch("ptmerged_dn",&ptmerged_dn);
  passedEventsTree_All->Branch("etamerged",&etamerged);
  passedEventsTree_All->Branch("phimerged",&phimerged);
  passedEventsTree_All->Branch("nsubjet",&nsubjet);
  passedEventsTree_All->Branch("foundZ1LCandidate",&foundZ1LCandidate);
  passedEventsTree_All->Branch("foundZ1LCandidate_up",&foundZ1LCandidate_up);
  passedEventsTree_All->Branch("foundZ1LCandidate_dn",&foundZ1LCandidate_dn);
  passedEventsTree_All->Branch("foundZ2JCandidate",&foundZ2JCandidate);
  passedEventsTree_All->Branch("foundZ2JCandidate_up",&foundZ2JCandidate_up);
  passedEventsTree_All->Branch("foundZ2JCandidate_dn",&foundZ2JCandidate_dn);
  passedEventsTree_All->Branch("foundZ2MergedCandidata",&foundZ2MergedCandidata);
  passedEventsTree_All->Branch("foundZ2MergedCandidata_up",&foundZ2MergedCandidata_up);
  passedEventsTree_All->Branch("foundZ2MergedCandidata_dn",&foundZ2MergedCandidata_dn);
  passedEventsTree_All->Branch("passedfullmerged",&passedfullmerged);
  passedEventsTree_All->Branch("passedfullresolved",&passedfullresolved);
  passedEventsTree_All->Branch("passedNassociated_jj",&passedNassociated_jj);
  passedEventsTree_All->Branch("passedNassociated_J",&passedNassociated_J);
  passedEventsTree_All->Branch("found2lepCandidate",&found2lepCandidate);
  passedEventsTree_All->Branch("foundTTCRCandidate",&foundTTCRCandidate);
  passedEventsTree_All->Branch("isEE",&isEE);
  passedEventsTree_All->Branch("isMuMu",&isMuMu);

  passedEventsTree_All->Branch("EventWeight",&EventWeight);
  passedEventsTree_All->Branch("GenWeight",&GenWeight);
  passedEventsTree_All->Branch("PileupWeight",&PileupWeight);
  passedEventsTree_All->Branch("PrefiringWeight",&PrefiringWeight);
  passedEventsTree_All->Branch("SumWeight",&SumWeight);
  passedEventsTree_All->Branch("CrossSectionWeight",&CrossSectionWeight);
  passedEventsTree_All->Branch("run",&run,"run/l");
  passedEventsTree_All->Branch("event",&event,"event/l");
  passedEventsTree_All->Branch("lumiSect",&lumiSect,"lumiSect/l");

  passedEventsTree_All->Branch("Met",&Met);
  passedEventsTree_All->Branch("Met_phi",&Met_phi);


  passedEventsTree_All->Branch("lep_Z1index",&lep_Z1index,"lep_Z1index[2]/I");
  passedEventsTree_All->Branch("jet_Z1index",&jet_Z1index,"jet_Z1index[2]/I");
  passedEventsTree_All->Branch("jet_Z1index_up",&jet_Z1index_up,"jet_Z1index_up[2]/I");
  passedEventsTree_All->Branch("jet_Z1index_dn",&jet_Z1index_dn,"jet_Z1index_dn[2]/I");
  passedEventsTree_All->Branch("merged_Z1index",&merged_Z1index);
  passedEventsTree_All->Branch("merged_Z1index_up",&merged_Z1index_up);
  passedEventsTree_All->Branch("merged_Z1index_dn",&merged_Z1index_dn);

  passedEventsTree_All->Branch("associatedjetjj_pt",&associatedjetjj_pt);
  passedEventsTree_All->Branch("associatedjetjj_eta",&associatedjetjj_eta);
  passedEventsTree_All->Branch("associatedjetjj_phi",&associatedjetjj_phi);
  passedEventsTree_All->Branch("associatedjetjj_mass",&associatedjetjj_mass);
  passedEventsTree_All->Branch("associatedjetsjj_index",&associatedjetsjj_index);
  passedEventsTree_All->Branch("associatedjetJ_pt",&associatedjetJ_pt);
  passedEventsTree_All->Branch("associatedjetJ_eta",&associatedjetJ_eta);
  passedEventsTree_All->Branch("associatedjetJ_phi",&associatedjetJ_phi);
  passedEventsTree_All->Branch("associatedjetJ_mass",&associatedjetJ_mass);
  passedEventsTree_All->Branch("associatedjetsJ_index",&associatedjetsJ_index);


  passedEventsTree_All->Branch("isbjet",&isbjet);
  passedEventsTree_All->Branch("iscjet",&iscjet);
  passedEventsTree_All->Branch("islightjet",&islightjet);
  passedEventsTree_All->Branch("jet_1_btag",&jet_1_btag);
  passedEventsTree_All->Branch("jet_1_btag_up",&jet_1_btag_up);
  passedEventsTree_All->Branch("jet_1_btag_dn",&jet_1_btag_dn);
  passedEventsTree_All->Branch("jet_2_btag",&jet_2_btag);
  passedEventsTree_All->Branch("jet_2_btag_up",&jet_2_btag_up);
  passedEventsTree_All->Branch("jet_2_btag_dn",&jet_2_btag_dn);
  passedEventsTree_All->Branch("jet_1_deepbtag",&jet_1_deepbtag);
  passedEventsTree_All->Branch("jet_1_deepbtag_up",&jet_1_deepbtag_up);
  passedEventsTree_All->Branch("jet_1_deepbtag_dn",&jet_1_deepbtag_dn);
  passedEventsTree_All->Branch("jet_2_deepbtag",&jet_2_deepbtag);
  passedEventsTree_All->Branch("jet_2_deepbtag_up",&jet_2_deepbtag_up);
  passedEventsTree_All->Branch("jet_2_deepbtag_dn",&jet_2_deepbtag_dn);
  passedEventsTree_All->Branch("jet_1_hadronflavor",&jet_1_hadronflavor);
  passedEventsTree_All->Branch("jet_2_hadronflavor",&jet_2_hadronflavor);
  passedEventsTree_All->Branch("jet_1_partonflavor",&jet_1_partonflavor);
  passedEventsTree_All->Branch("jet_2_partonflavor",&jet_2_partonflavor);
  passedEventsTree_All->Branch("jet_1_pt",&jet_1_pt);
  passedEventsTree_All->Branch("jet_2_pt",&jet_2_pt);
  passedEventsTree_All->Branch("jet_1_eta",&jet_1_eta);
  passedEventsTree_All->Branch("jet_2_eta",&jet_2_eta);
  passedEventsTree_All->Branch("jet_1_phi",&jet_1_phi);
  passedEventsTree_All->Branch("jet_2_phi",&jet_2_phi);
  passedEventsTree_All->Branch("jet_1_mass",&jet_1_mass);
  passedEventsTree_All->Branch("jet_2_mass",&jet_2_mass);
  passedEventsTree_All->Branch("jet_1_pt_up",&jet_1_pt_up);
  passedEventsTree_All->Branch("jet_1_eta_up",&jet_1_eta_up);
  passedEventsTree_All->Branch("jet_1_phi_up",&jet_1_phi_up);
  passedEventsTree_All->Branch("jet_1_mass_up",&jet_1_mass_up);
  passedEventsTree_All->Branch("jet_1_pt_dn",&jet_1_pt_dn);
  passedEventsTree_All->Branch("jet_1_eta_dn",&jet_1_eta_dn);
  passedEventsTree_All->Branch("jet_1_phi_dn",&jet_1_phi_dn);
  passedEventsTree_All->Branch("jet_1_mass_dn",&jet_1_mass_dn);
  passedEventsTree_All->Branch("jet_2_pt_up",&jet_2_pt_up);
  passedEventsTree_All->Branch("jet_2_eta_up",&jet_2_eta_up);
  passedEventsTree_All->Branch("jet_2_phi_up",&jet_2_phi_up);
  passedEventsTree_All->Branch("jet_2_mass_up",&jet_2_mass_up);
  passedEventsTree_All->Branch("jet_2_pt_dn",&jet_2_pt_dn);
  passedEventsTree_All->Branch("jet_2_eta_dn",&jet_2_eta_dn);
  passedEventsTree_All->Branch("jet_2_phi_dn",&jet_2_phi_dn);
  passedEventsTree_All->Branch("jet_2_mass_dn",&jet_2_mass_dn);

  passedEventsTree_All->Branch("jet_1_jesunc_split_Total",         &jet_1_jesunc_split_Total);
  passedEventsTree_All->Branch("jet_1_jesunc_split_Abs",           &jet_1_jesunc_split_Abs);
  passedEventsTree_All->Branch("jet_1_jesunc_split_Abs_year",      &jet_1_jesunc_split_Abs_year);
  passedEventsTree_All->Branch("jet_1_jesunc_split_BBEC1",         &jet_1_jesunc_split_BBEC1);
  passedEventsTree_All->Branch("jet_1_jesunc_split_BBEC1_year",    &jet_1_jesunc_split_BBEC1_year);
  passedEventsTree_All->Branch("jet_1_jesunc_split_EC2",           &jet_1_jesunc_split_EC2);
  passedEventsTree_All->Branch("jet_1_jesunc_split_EC2_year",      &jet_1_jesunc_split_EC2_year);
  passedEventsTree_All->Branch("jet_1_jesunc_split_FlavQCD",       &jet_1_jesunc_split_FlavQCD);
  passedEventsTree_All->Branch("jet_1_jesunc_split_HF",            &jet_1_jesunc_split_HF);
  passedEventsTree_All->Branch("jet_1_jesunc_split_HF_year",       &jet_1_jesunc_split_HF_year);
  passedEventsTree_All->Branch("jet_1_jesunc_split_RelBal",        &jet_1_jesunc_split_RelBal);
  passedEventsTree_All->Branch("jet_1_jesunc_split_RelSample_year",&jet_1_jesunc_split_RelSample_year);
  passedEventsTree_All->Branch("jet_2_jesunc_split_Total",         &jet_2_jesunc_split_Total);
  passedEventsTree_All->Branch("jet_2_jesunc_split_Abs",           &jet_2_jesunc_split_Abs);
  passedEventsTree_All->Branch("jet_2_jesunc_split_Abs_year",      &jet_2_jesunc_split_Abs_year);
  passedEventsTree_All->Branch("jet_2_jesunc_split_BBEC1",         &jet_2_jesunc_split_BBEC1);
  passedEventsTree_All->Branch("jet_2_jesunc_split_BBEC1_year",    &jet_2_jesunc_split_BBEC1_year);
  passedEventsTree_All->Branch("jet_2_jesunc_split_EC2",           &jet_2_jesunc_split_EC2);
  passedEventsTree_All->Branch("jet_2_jesunc_split_EC2_year",      &jet_2_jesunc_split_EC2_year);
  passedEventsTree_All->Branch("jet_2_jesunc_split_FlavQCD",       &jet_2_jesunc_split_FlavQCD);
  passedEventsTree_All->Branch("jet_2_jesunc_split_HF",            &jet_2_jesunc_split_HF);
  passedEventsTree_All->Branch("jet_2_jesunc_split_HF_year",       &jet_2_jesunc_split_HF_year);
  passedEventsTree_All->Branch("jet_2_jesunc_split_RelBal",        &jet_2_jesunc_split_RelBal);
  passedEventsTree_All->Branch("jet_2_jesunc_split_RelSample_year",&jet_2_jesunc_split_RelSample_year);

  passedEventsTree_All->Branch("jetpt_1_jesup_split_Total",         &jetpt_1_jesup_split_Total);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_Abs",           &jetpt_1_jesup_split_Abs);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_Abs_year",      &jetpt_1_jesup_split_Abs_year);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_BBEC1",         &jetpt_1_jesup_split_BBEC1);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_BBEC1_year",    &jetpt_1_jesup_split_BBEC1_year);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_EC2",           &jetpt_1_jesup_split_EC2);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_EC2_year",      &jetpt_1_jesup_split_EC2_year);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_FlavQCD",       &jetpt_1_jesup_split_FlavQCD);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_HF",            &jetpt_1_jesup_split_HF);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_HF_year",       &jetpt_1_jesup_split_HF_year);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_RelBal",        &jetpt_1_jesup_split_RelBal);
  passedEventsTree_All->Branch("jetpt_1_jesup_split_RelSample_year",&jetpt_1_jesup_split_RelSample_year);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_Total",         &jetpt_1_jesdn_split_Total);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_Abs",           &jetpt_1_jesdn_split_Abs);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_Abs_year",      &jetpt_1_jesdn_split_Abs_year);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_BBEC1",         &jetpt_1_jesdn_split_BBEC1);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_BBEC1_year",    &jetpt_1_jesdn_split_BBEC1_year);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_EC2",           &jetpt_1_jesdn_split_EC2);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_EC2_year",      &jetpt_1_jesdn_split_EC2_year);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_FlavQCD",       &jetpt_1_jesdn_split_FlavQCD);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_HF",            &jetpt_1_jesdn_split_HF);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_HF_year",       &jetpt_1_jesdn_split_HF_year);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_RelBal",        &jetpt_1_jesdn_split_RelBal);
  passedEventsTree_All->Branch("jetpt_1_jesdn_split_RelSample_year",&jetpt_1_jesdn_split_RelSample_year);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_Total",         &jetpt_2_jesup_split_Total);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_Abs",           &jetpt_2_jesup_split_Abs);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_Abs_year",      &jetpt_2_jesup_split_Abs_year);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_BBEC1",         &jetpt_2_jesup_split_BBEC1);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_BBEC1_year",    &jetpt_2_jesup_split_BBEC1_year);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_EC2",           &jetpt_2_jesup_split_EC2);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_EC2_year",      &jetpt_2_jesup_split_EC2_year);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_FlavQCD",       &jetpt_2_jesup_split_FlavQCD);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_HF",            &jetpt_2_jesup_split_HF);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_HF_year",       &jetpt_2_jesup_split_HF_year);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_RelBal",        &jetpt_2_jesup_split_RelBal);
  passedEventsTree_All->Branch("jetpt_2_jesup_split_RelSample_year",&jetpt_2_jesup_split_RelSample_year);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_Total",         &jetpt_2_jesdn_split_Total);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_Abs",           &jetpt_2_jesdn_split_Abs);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_Abs_year",      &jetpt_2_jesdn_split_Abs_year);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_BBEC1",         &jetpt_2_jesdn_split_BBEC1);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_BBEC1_year",    &jetpt_2_jesdn_split_BBEC1_year);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_EC2",           &jetpt_2_jesdn_split_EC2);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_EC2_year",      &jetpt_2_jesdn_split_EC2_year);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_FlavQCD",       &jetpt_2_jesdn_split_FlavQCD);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_HF",            &jetpt_2_jesdn_split_HF);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_HF_year",       &jetpt_2_jesdn_split_HF_year);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_RelBal",        &jetpt_2_jesdn_split_RelBal);
  passedEventsTree_All->Branch("jetpt_2_jesdn_split_RelSample_year",&jetpt_2_jesdn_split_RelSample_year);

  passedEventsTree_All->Branch("mergedjet_jesunc_split_Total",         &mergedjet_jesunc_split_Total);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_Abs",           &mergedjet_jesunc_split_Abs);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_Abs_year",      &mergedjet_jesunc_split_Abs_year);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_BBEC1",         &mergedjet_jesunc_split_BBEC1);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_BBEC1_year",    &mergedjet_jesunc_split_BBEC1_year);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_EC2",           &mergedjet_jesunc_split_EC2);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_EC2_year",      &mergedjet_jesunc_split_EC2_year);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_FlavQCD",       &mergedjet_jesunc_split_FlavQCD);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_HF",            &mergedjet_jesunc_split_HF);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_HF_year",       &mergedjet_jesunc_split_HF_year);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_RelBal",        &mergedjet_jesunc_split_RelBal);
  passedEventsTree_All->Branch("mergedjet_jesunc_split_RelSample_year",&mergedjet_jesunc_split_RelSample_year);

  passedEventsTree_All->Branch("mergedjetpt_jesup_split_Total",         &mergedjetpt_jesup_split_Total);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_Abs",           &mergedjetpt_jesup_split_Abs);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_Abs_year",      &mergedjetpt_jesup_split_Abs_year);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_BBEC1",         &mergedjetpt_jesup_split_BBEC1);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_BBEC1_year",    &mergedjetpt_jesup_split_BBEC1_year);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_EC2",           &mergedjetpt_jesup_split_EC2);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_EC2_year",      &mergedjetpt_jesup_split_EC2_year);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_FlavQCD",       &mergedjetpt_jesup_split_FlavQCD);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_HF",            &mergedjetpt_jesup_split_HF);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_HF_year",       &mergedjetpt_jesup_split_HF_year);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_RelBal",        &mergedjetpt_jesup_split_RelBal);
  passedEventsTree_All->Branch("mergedjetpt_jesup_split_RelSample_year",&mergedjetpt_jesup_split_RelSample_year);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_Total",         &mergedjetpt_jesdn_split_Total);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_Abs",           &mergedjetpt_jesdn_split_Abs);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_Abs_year",      &mergedjetpt_jesdn_split_Abs_year);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_BBEC1",         &mergedjetpt_jesdn_split_BBEC1);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_BBEC1_year",    &mergedjetpt_jesdn_split_BBEC1_year);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_EC2",           &mergedjetpt_jesdn_split_EC2);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_EC2_year",      &mergedjetpt_jesdn_split_EC2_year);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_FlavQCD",       &mergedjetpt_jesdn_split_FlavQCD);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_HF",            &mergedjetpt_jesdn_split_HF);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_HF_year",       &mergedjetpt_jesdn_split_HF_year);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_RelBal",        &mergedjetpt_jesdn_split_RelBal);
  passedEventsTree_All->Branch("mergedjetpt_jesdn_split_RelSample_year",&mergedjetpt_jesdn_split_RelSample_year);

  passedEventsTree_All->Branch("GEN_H1_pt",&GEN_H1_pt);
  passedEventsTree_All->Branch("GEN_H1_eta",&GEN_H1_eta);
  passedEventsTree_All->Branch("GEN_H1_phi",&GEN_H1_phi);
  passedEventsTree_All->Branch("GEN_H1_mass",&GEN_H1_mass);
  //passedEventsTree_All->Branch("GEN_H2_pt",&GEN_H2_pt);
  //passedEventsTree_All->Branch("GEN_H2_eta",&GEN_H2_eta);
  //passedEventsTree_All->Branch("GEN_H2_phi",&GEN_H2_phi);
  //passedEventsTree_All->Branch("GEN_H2_mass",&GEN_H2_mass);
  passedEventsTree_All->Branch("GEN_DR_H1_Mom",&GEN_DR_H1_Mom);
  passedEventsTree_All->Branch("GEN_DR_H2_Mom",&GEN_DR_H2_Mom);

  passedEventsTree_All->Branch("GEN_H1_Mom_pt",&GEN_H1_Mom_pt);
  passedEventsTree_All->Branch("GEN_H1_Mom_eta",&GEN_H1_Mom_eta);
  passedEventsTree_All->Branch("GEN_H1_Mom_phi",&GEN_H1_Mom_phi);
  passedEventsTree_All->Branch("GEN_H1_Mom_mass",&GEN_H1_Mom_mass);
  passedEventsTree_All->Branch("GEN_H2_Mom_pt",&GEN_H2_Mom_pt);
  passedEventsTree_All->Branch("GEN_H2_Mom_eta",&GEN_H2_Mom_eta);
  passedEventsTree_All->Branch("GEN_H2_Mom_phi",&GEN_H2_Mom_phi);
  passedEventsTree_All->Branch("GEN_H2_Mom_mass",&GEN_H2_Mom_mass);

  passedEventsTree_All->Branch("GEN_H1_Bro_pt",&GEN_H1_Bro_pt);
  passedEventsTree_All->Branch("GEN_H1_Bro_eta",&GEN_H1_Bro_eta);
  passedEventsTree_All->Branch("GEN_H1_Bro_phi",&GEN_H1_Bro_phi);
  passedEventsTree_All->Branch("GEN_H1_Bro_mass",&GEN_H1_Bro_mass);
  passedEventsTree_All->Branch("GEN_DR_H1_Bro",&GEN_DR_H1_Bro);
  passedEventsTree_All->Branch("GEN_DR_H1Mom_Bro",&GEN_DR_H1Mom_Bro);
  passedEventsTree_All->Branch("GEN_H2_Bro_pt",&GEN_H1_Bro_pt);
  passedEventsTree_All->Branch("GEN_H2_Bro_eta",&GEN_H2_Bro_eta);
  passedEventsTree_All->Branch("GEN_H2_Bro_phi",&GEN_H2_Bro_phi);
  passedEventsTree_All->Branch("GEN_H2_Bro_mass",&GEN_H2_Bro_mass);
  passedEventsTree_All->Branch("GEN_DR_H2_Bro",&GEN_DR_H2_Bro);
  passedEventsTree_All->Branch("GEN_DR_H2Mom_Bro",&GEN_DR_H2Mom_Bro);
  passedEventsTree_All->Branch("GEN_DR_Bro12",&GEN_DR_Bro12);
  passedEventsTree_All->Branch("GEN_DEta_H1_Bro",&GEN_DEta_H1_Bro);
  passedEventsTree_All->Branch("GEN_DEta_H1Mom_Bro",&GEN_DEta_H1Mom_Bro);
  passedEventsTree_All->Branch("GEN_DEta_H2_Bro",&GEN_DEta_H2_Bro);
  passedEventsTree_All->Branch("GEN_DEta_H2Mom_Bro",&GEN_DEta_H2Mom_Bro);
  passedEventsTree_All->Branch("GEN_DEta_Bro12",&GEN_DEta_Bro12);
  passedEventsTree_All->Branch("passedGENH",&passedGENH);

  passedEventsTree_All->Branch("DR_merged_GenZ",&DR_merged_GenZ);
  passedEventsTree_All->Branch("matched_merged_GEN_Z",&matched_merged_GEN_Z);
  passedEventsTree_All->Branch("DR_merged_GenZ_matched",&DR_merged_GenZ_matched);
  passedEventsTree_All->Branch("DR_resovled1_GenZ",&DR_resovled1_GenZ);
  passedEventsTree_All->Branch("DR_resovled2_GenZ",&DR_resovled2_GenZ);
  passedEventsTree_All->Branch("DR_resovled2_GenZ_matched",&DR_resovled2_GenZ_matched);
  passedEventsTree_All->Branch("DR_resovled1_GenZ_matched",&DR_resovled1_GenZ_matched);
  passedEventsTree_All->Branch("matched_resovled1_GEN_Z",&matched_resovled1_GEN_Z);
  passedEventsTree_All->Branch("matched_resovled2_GEN_Z",&matched_resovled2_GEN_Z);
  passedEventsTree_All->Branch("matched_resovled_GEN_Z",&matched_resovled_GEN_Z);
  passedEventsTree_All->Branch("matched_resovledone_GEN_Z",&matched_resovledone_GEN_Z);

  passedEventsTree_All->Branch("matched_associatedjet1_GEN_Z",&matched_associatedjet1_GEN_Z);
  passedEventsTree_All->Branch("matched_associatedjet2_GEN_Z",&matched_associatedjet2_GEN_Z);
  passedEventsTree_All->Branch("matched_associatedjet_GEN_Z",&matched_associatedjet_GEN_Z);
  passedEventsTree_All->Branch("matched_associatedjetone_GEN_Z",&matched_associatedjetone_GEN_Z);
  passedEventsTree_All->Branch("DR_associatedjet1_GenZ",&DR_associatedjet1_GenZ);
  passedEventsTree_All->Branch("DR_associatedjet2_GenZ",&DR_associatedjet2_GenZ);
  passedEventsTree_All->Branch("DR_associatedjet1_GenZ_matched",&DR_associatedjet1_GenZ_matched);
  passedEventsTree_All->Branch("DR_associatedjet2_GenZ_matched",&DR_associatedjet2_GenZ_matched);

  //VBF
  passedEventsTree_All->Branch("GEN_associated1_pt",&GEN_associated1_pt);
  passedEventsTree_All->Branch("GEN_associated1_eta",&GEN_associated1_eta);
  passedEventsTree_All->Branch("GEN_associated1_phi",&GEN_associated1_phi);
  passedEventsTree_All->Branch("GEN_associated1_mass",&GEN_associated1_mass);
  passedEventsTree_All->Branch("GEN_associated2_pt",&GEN_associated2_pt);
  passedEventsTree_All->Branch("GEN_associated2_eta",&GEN_associated2_eta);
  passedEventsTree_All->Branch("GEN_associated2_phi",&GEN_associated2_phi);
  passedEventsTree_All->Branch("GEN_associated2_mass",&GEN_associated2_mass);
  passedEventsTree_All->Branch("GEN_associated12_mass",&GEN_associated12_mass);
  passedEventsTree_All->Branch("GEN_associated12_Deta",&GEN_associated12_Deta);

  passedEventsTree_All->Branch("GEN_quark1_match_pt",&GEN_quark1_match_pt);
  passedEventsTree_All->Branch("GEN_quark1_match_eta",&GEN_quark1_match_eta);
  passedEventsTree_All->Branch("GEN_quark1_match_phi",&GEN_quark1_match_phi);
  passedEventsTree_All->Branch("GEN_quark1_match_mass",&GEN_quark1_match_mass);
  passedEventsTree_All->Branch("GEN_quark2_match_pt",&GEN_quark2_match_pt);
  passedEventsTree_All->Branch("GEN_quark2_match_eta",&GEN_quark2_match_eta);
  passedEventsTree_All->Branch("GEN_quark2_match_phi",&GEN_quark2_match_phi);
  passedEventsTree_All->Branch("GEN_quark2_match_mass",&GEN_quark2_match_mass);
  passedEventsTree_All->Branch("GEN_quark12_match_mass",&GEN_quark12_match_mass);
  passedEventsTree_All->Branch("passedGenquarkMatch",&passedGenquarkMatch);

  passedEventsTree_All->Branch("Reco_quark1_match_pt",&Reco_quark1_match_pt);
  passedEventsTree_All->Branch("Reco_quark1_match_eta",&Reco_quark1_match_eta);
  passedEventsTree_All->Branch("Reco_quark1_match_phi",&Reco_quark1_match_phi);
  passedEventsTree_All->Branch("Reco_quark1_match_mass",&Reco_quark1_match_mass);
  passedEventsTree_All->Branch("Reco_quark2_match_pt",&Reco_quark2_match_pt);
  passedEventsTree_All->Branch("Reco_quark2_match_eta",&Reco_quark2_match_eta);
  passedEventsTree_All->Branch("Reco_quark2_match_phi",&Reco_quark2_match_phi);
  passedEventsTree_All->Branch("Reco_quark2_match_mass",&Reco_quark2_match_mass);
  passedEventsTree_All->Branch("Reco_quark12_match_mass",&Reco_quark12_match_mass);
  passedEventsTree_All->Branch("Reco_quark12_match_DEta",&Reco_quark12_match_DEta);
  passedEventsTree_All->Branch("passedRecoquarkMatch",&passedRecoquarkMatch);
  passedEventsTree_All->Branch("match2_recoindex",&match2_recoindex);
  passedEventsTree_All->Branch("match1_recoindex",&match1_recoindex);
  passedEventsTree_All->Branch("DR_merged_VBF1_matched",&DR_merged_VBF1_matched);
  passedEventsTree_All->Branch("DR_merged_VBF2_matched",&DR_merged_VBF2_matched);
  passedEventsTree_All->Branch("DR_merged_asccoiacted",&DR_merged_asccoiacted);
  passedEventsTree_All->Branch("DR_selectedleps_asccoiacted",&DR_selectedleps_asccoiacted);
  passedEventsTree_All->Branch("passedmatchtruthVBF_jj",&passedmatchtruthVBF_jj);
  passedEventsTree_All->Branch("passedmatchtruthVBF_J",&passedmatchtruthVBF_J);
  passedEventsTree_All->Branch("time_associatedjetjj_eta",&time_associatedjetjj_eta);
  passedEventsTree_All->Branch("time_associatedjetJ_eta",&time_associatedjetJ_eta);




}

//========================initialize=======================
void TreeLoop::initialize(){
  //initialize
  foundZ1LCandidate = false;
  foundZ1LCandidate_up = false;
  foundZ1LCandidate_dn = false;
  foundZ2JCandidate = false;
  foundZ2JCandidate_up = false;
  foundZ2JCandidate_dn = false;
  found4lCandidate = false;
  foundZ2MergedCandidata = false;
  foundZ2MergedCandidata_up = false;
  foundZ2MergedCandidata_dn = false;
  foundmergedOnly = false;
  foundresolvedOnly = false;
  foundresolvedCombine = false;
  foundmergedCombine = false;
  found2lepCandidate = false;
  foundTTCRCandidate = false;
  passedfullmerged = false;
  passedfullresolved = false;
  passedNassociated_jj = false;
  passedNassociated_J = false;
  isEE = false; isMuMu = false;
  for (int i=0; i<2; ++i) {lep_Z1index[i]=-1;}
  for (int i=0; i<2; ++i) {jet_Z1index[i]=-1;}
  for (int i=0; i<2; ++i) {jet_Z1index_up[i]=-1;}
  for (int i=0; i<2; ++i) {jet_Z1index_dn[i]=-1;}
  for (int i=0; i<2; ++i) {lep_Hindex[i]=-1;}
  for (int i=0; i<2; ++i) {jet_Z1index_mass_bais[i]=-1;}
  merged_Z1index = -1; merged_Z1index_up = -1; merged_Z1index_dn = -1;

  EventWeight = 1.0; GenWeight = 1.0; PileupWeight = 1.0; PrefiringWeight = 1.0;
  lep_1_pt = -999.0; lep_1_eta = -999.0; lep_1_phi = -999; lep_2_eta = -999.0; lep_2_pt = -999.0; lep_2_phi = -999.0;
  lep_1_mass = -999.0; lep_2_mass = -999.0;
  lep_1_pt_up = -999.0; lep_1_eta_up = -999.0; lep_1_phi_up = -999; lep_2_eta_up = -999.0; lep_2_pt_up = -999.0; lep_2_phi_up = -999.0;
  lep_1_mass_up = -999.0; lep_2_mass_up = -999.0;
  lep_1_pt_dn = -999.0; lep_1_eta_dn = -999.0; lep_1_phi_dn = -999; lep_2_eta_dn = -999.0; lep_2_pt_dn = -999.0; lep_2_phi_dn = -999.0;
  lep_1_mass_dn = -999.0; lep_2_mass_dn = -999.0;
  Nleptons = -999; Ntightleptons = 0;
  mass2jet=-999.99; mass2jet_up=-999.99; mass2jet_dn=-999.99;
  pt2jet=-999.99; pt2jet_up=-999.00; pt2jet_dn=-999.99;
  mass2jet_mass_bais=-999.99; pt2jet_mass_bais=-999.99; mass2l2jet_mass_bais=-999.99;
  mass2l=-999.99;
  pt2l=-999.99;
  mass2l2jet=-999.99;
  mass2l2jet_dn = -999.99;
  mass2l2jet_up = -999.99;
  KD_jjVBF = -999.9; KD_jjVBF_up = -999.99; KD_jjVBF_dn = -999.99;
  KD_jVBF = -999.9;
  KD_JJVBF = -999.99; KD_JVBF_up = -999.99; KD_JVBF_dn = -999.99;
  KD_JVBF = -999.99;
  KD_ZJ = -999.99; KD_ZJ_dn = -999.99; KD_ZJ_up = -999.99;
  KD_Zjj = -999.99; KD_Zjj_up = -999.99; KD_Zjj_dn = -999.99;
  massmerged = -999.99; massmerged_up = -999.99; massmerged_dn = -999.99;
  ptmerged = -999.99; ptmerged_up = -999.99; ptmerged_dn = -999.99;
  etamerged = -999.99;
  phimerged = -999.99;
  nsubjet = -999.99;
  mass2lj = -999.99;
  mass2lj_up = -999.99;
  mass2lj_dn = -999.00;

  n_jets = 0; n_mergedjets = 0;

  jet_1_btag=-999; jet_2_btag=-999; jet_1_hadronflavor=-999; jet_1_partonflavor=-999;
  jet_1_deepbtag = -999; jet_1_deepbtag_up = -999; jet_1_deepbtag_dn = -999;
  jet_2_deepbtag = -999; jet_2_deepbtag_up = -999; jet_2_deepbtag_dn = -999;
  jet_1_btag_up = -999; jet_1_btag_dn=-999; jet_2_btag_up = -999; jet_2_btag_dn=-999;
  jet_2_hadronflavor=-999; jet_2_partonflavor=-999;
  jet_1_pt = -999.99;  jet_2_pt = -999.99;
  jet_1_eta = -999.99; jet_2_eta = -999.99;
  jet_1_phi = -999.99; jet_2_phi = -999.99;
  jet_1_mass = -999.99; jet_2_mass = -999.99;
  jet_1_pt_up=-999.99; jet_1_pt_dn=-999.99;
  jet_1_eta_up=-999.99; jet_1_eta_dn=-999.99;
  jet_1_phi_up=-999.00; jet_1_phi_dn=-999.99;
  jet_1_mass_up=-999.99; jet_1_mass_dn=-999.99;
  jet_2_pt_up=-999.99;   jet_2_pt_dn=-999.99;
  jet_2_eta_up=-999.99;  jet_2_eta_dn=-999.99;
  jet_2_phi_up=-999.00;  jet_2_phi_dn=-999.99;
  jet_2_mass_up=-999.99; jet_2_mass_dn=-999.99;


  particleNetZvsQCD = -999.99; particleNetZvsQCD_up = -999.99; particleNetZvsQCD_dn = -999.99;
  particleNetZbbvslight = -999.99; particleNetZbbvslight_up = -999.99; particleNetZbbvslight_dn = -999.99;
  particleNetXbbvsQCD = -999.9; particleNetXbbvsQCD_up = -999.9; particleNetXbbvsQCD_dn = -999.9;

  passedGENH = false;
  isbjet = false; iscjet = false; islightjet = false;

  Met = 0.0; Met_phi = 0.0;
  GEN_H1_pt=-999.0; GEN_H1_eta=-999.0; GEN_H1_phi=-999.0; GEN_H1_mass=-999.0;
  GEN_H2_pt=-999.0; GEN_H2_eta=-999.0; GEN_H2_phi=-999.0; GEN_H2_mass=-999.0;
  GEN_DR_H1_Mom = -999.0; GEN_DR_H2_Mom=-999.0;
  GEN_H1_Mom_pt=-999.0; GEN_H1_Mom_eta=-999.0; GEN_H1_Mom_phi=-999.0; GEN_H1_Mom_mass=-999.0;
  GEN_H2_Mom_pt=-999.0; GEN_H2_Mom_eta=-999.0; GEN_H2_Mom_phi=-999.0; GEN_H2_Mom_mass=-999.0;

  GEN_H1_Bro_pt.clear(); GEN_H1_Bro_eta.clear(); GEN_H1_Bro_phi.clear(); GEN_H1_Bro_mass.clear(); GEN_DR_H1_Bro.clear(); GEN_DR_H1Mom_Bro.clear();
  GEN_H2_Bro_pt.clear(); GEN_H2_Bro_eta.clear(); GEN_H2_Bro_phi.clear(); GEN_H2_Bro_mass.clear(); GEN_DR_H2_Bro.clear(); GEN_DR_H2Mom_Bro.clear();
  GEN_DR_Bro12.clear();
  GEN_DEta_H1_Bro.clear(); GEN_DEta_H1Mom_Bro.clear(); GEN_DEta_H2_Bro.clear(); GEN_DEta_H2Mom_Bro.clear();
  GEN_DEta_Bro12.clear();
  DR_merged_GenZ.clear(); DR_merged_GenZ_matched.clear(); DR_resovled2_GenZ_matched.clear(); DR_resovled1_GenZ_matched.clear();
  DR_resovled1_GenZ.clear(); DR_resovled2_GenZ.clear();
  DR_associatedjet1_GenZ.clear(); DR_associatedjet2_GenZ.clear(); DR_associatedjet1_GenZ_matched.clear(); DR_associatedjet2_GenZ_matched.clear();
  matched_merged_GEN_Z = false; matched_resovled1_GEN_Z=false; matched_resovled2_GEN_Z = false; matched_resovled_GEN_Z = false; matched_resovledone_GEN_Z=false;
  matched_associatedjet1_GEN_Z = false; matched_associatedjet2_GEN_Z = false; matched_associatedjet_GEN_Z = false; matched_associatedjetone_GEN_Z = false;
  associatedjetjj_pt.clear(); associatedjetjj_eta.clear(); associatedjetjj_phi.clear(); associatedjetjj_mass.clear();
  associatedjetJ_pt.clear(); associatedjetJ_eta.clear(); associatedjetJ_phi.clear(); associatedjetJ_mass.clear();
  associatedjetsjj_index.clear(); associatedjetsJ_index.clear();
  

  //VBF
  GEN_associated1_pt=-999.0; GEN_associated1_eta=-999.0; GEN_associated1_phi=-999.0; GEN_associated1_mass=-999.0;
  GEN_associated2_pt=-999.0; GEN_associated2_eta=-999.0; GEN_associated2_phi=-999.0; GEN_associated2_mass=-999.0;
  GEN_associated12_mass=-999.0; GEN_associated12_Deta=-999.0;


  GEN_quark1_match_pt=-999.0; GEN_quark1_match_eta=-999.0; GEN_quark1_match_phi=-999.0; GEN_quark1_match_mass=-999.0;
  GEN_quark2_match_pt=-999.0; GEN_quark2_match_eta=-999.0; GEN_quark2_match_phi=-999.0; GEN_quark2_match_mass=-999.0;
  GEN_quark12_match_mass=-999.0;
  passedGenquarkMatch=false;

  Reco_quark1_match_pt=-999.0; Reco_quark1_match_eta=-999.0; Reco_quark1_match_phi=-999.0; Reco_quark1_match_mass=-999.0;
  Reco_quark2_match_pt=-999.0; Reco_quark2_match_eta=-999.0; Reco_quark2_match_phi=-999.0; Reco_quark2_match_mass=-999.0;
  Reco_quark12_match_mass=-999.0;
  passedRecoquarkMatch = false;
  match2_recoindex=-999; match1_recoindex=-999;
  Reco_quark12_match_DEta=-999.9;
  DR_merged_VBF1_matched = -999.9; DR_merged_VBF2_matched=-999.0;
  DR_merged_asccoiacted.clear();
  DR_selectedleps_asccoiacted.clear();
  passedmatchtruthVBF_jj = false;
  passedmatchtruthVBF_J = false;
  time_associatedjetjj_eta = -999.0;
  time_associatedjetJ_eta = -999.0;
  //initialize done

}

//========================Set Cross Section=================================
void TreeLoop::SetCrossSection(TString inputfile){
    std::ifstream file("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/ANATree/CrossSection.txt"); // Open the text file

    if (file.is_open()) { // Check if the file is successfully opened
        std::string line;
        //split TString inputfile by "/" and get the last one
        TString delimiter_input = "/";
        TObjArray *parts = inputfile.Tokenize(delimiter_input); // split inputfile by "/"
        //Get the last part after splitting 
        TString extractedPart = ((TObjString *)(parts->At(parts->GetLast())))->String();
        std::cout << "Input File name after splitting = "<<extractedPart << std::endl;

        TString targetString = extractedPart;

        std::string delimiter = " ";
        while (std::getline(file, line)) {
            // Check if the target string is present in the current line
            if (line.find(targetString) != std::string::npos) {
                // Extract the associated value
                size_t pos = line.find(delimiter);
                std::string value = line.substr(pos + delimiter.length());
                xsec = std::stof(value);
                break; // Stop further processing if the target is found
            }
        }

        file.close(); // Close the file
    } else {
        std::cout << "Failed to open the file." << std::endl;
    }
}