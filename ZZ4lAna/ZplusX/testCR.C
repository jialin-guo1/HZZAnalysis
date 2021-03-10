#include <iostream>
#include <iomanip>
#include <cmath>
#include <fstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <stdio.h>
#include <TROOT.h>
#include <TStyle.h>
#include <TFile.h>
#include <TChain.h>
#include <TLatex.h>
#include <TMath.h>
#include "TRandom.h"
#include <TFeldmanCousins.h>
#include <TCanvas.h>
#include <TTree.h>
#include <TString.h>
#include <TH1.h>
#include <TH2.h>
#include <THStack.h>
#include <TF1.h>
#include <TGraph.h>
#include <TGraphErrors.h>
#include <TGraphAsymmErrors.h>
#include <TEfficiency.h>
#include <TLine.h>
#include <TPolyLine.h>
#include <TLegend.h>
#include <TLegendEntry.h>
#include <TLorentzVector.h>
//#include "Math/VectorUtil.h"
#include "TClonesArray.h"
#include "TEfficiency.h"
#include "TGraphErrors.h"
#include "TFrame.h"



float mass3l, mass4l, massZ1, massZ2, met, met_phi,mt;
float eventWeight, dataMCWeight, crossSection, genWeight;
    ULong64_t  Run, LumiSect, Event;
    int finalState, nVtx;
    bool passedFullSelection, passedZ1LSelection, passedZ4lZXCRSelection, passedZ4lSelection,passedZXCRSelection, passedZ4lZ1LSelection;
    vector<float> *lep_pt = 0; TBranch *b_lep_pt = 0;
    vector<float> *lep_eta = 0; TBranch *b_lep_eta = 0;
    vector<float> *lep_phi = 0; TBranch *b_lep_phi = 0;
    vector<float> *lep_mass = 0; TBranch *b_lep_mass = 0;
    int lep_Hindex[4];
    vector<int> *lep_id = 0; TBranch *b_lep_id = 0;
    vector<int> *lep_tightId = 0; TBranch *b_lep_tightId = 0;
    vector<float> *lep_RelIso = 0; TBranch *b_lep_RelIso = 0;
    vector<int> *lep_matchedR03_PdgId = 0; TBranch *b_lep_matchedR03_PdgId = 0;
    vector<int> *lep_matchedR03_MomId = 0; TBranch *b_lep_matchedR03_MomId = 0;
    vector<int> *lep_matchedR03_MomMomId = 0; TBranch *b_lep_matchedR03_MomMomId = 0;

void SetBranches(TTree *tree){
	tree->SetBranchAddress("Run",&Run);
	tree->SetBranchAddress("LumiSect",&LumiSect);
	tree->SetBranchAddress("Event",&Event);
	tree->SetBranchAddress("crossSection",&crossSection);
	tree->SetBranchAddress("eventWeight",&eventWeight);
	tree->SetBranchAddress("genWeight",&genWeight);
	tree->SetBranchAddress("dataMCWeight",&dataMCWeight);
	tree->SetBranchAddress("passedFullSelection",&passedFullSelection);
	tree->SetBranchAddress("passedZ1LSelection",&passedZ1LSelection);
	tree->SetBranchAddress("passedZ4lZ1LSelection",&passedZ4lZ1LSelection);
	tree->SetBranchAddress("passedZ4lZXCRSelection",&passedZ4lZXCRSelection);
	tree->SetBranchAddress("passedZXCRSelection",&passedZXCRSelection);
	tree->SetBranchAddress("passedZ4lSelection",&passedZ4lSelection);
	tree->SetBranchAddress("nVtx",&nVtx);
	tree->SetBranchAddress("finalState",&finalState);
	tree->SetBranchAddress("mass4l",&mass4l);
        tree->SetBranchAddress("massZ1",&massZ1);
	tree->SetBranchAddress("massZ2",&massZ2);
	tree->SetBranchAddress("lep_Hindex",lep_Hindex);
	tree->SetBranchAddress("lep_pt",&lep_pt,&b_lep_pt);
	tree->SetBranchAddress("lep_eta",&lep_eta,&b_lep_eta);
	tree->SetBranchAddress("lep_phi",&lep_phi,&b_lep_phi);
	tree->SetBranchAddress("lep_mass",&lep_mass,&b_lep_mass);
	tree->SetBranchAddress("met",&met);
	tree->SetBranchAddress("met_phi",&met_phi);
	tree->SetBranchAddress("lep_id",&lep_id,&b_lep_id);
	tree->SetBranchAddress("lep_tightId",&lep_tightId,&b_lep_tightId);
	tree->SetBranchAddress("lep_RelIsoNoFSR",&lep_RelIso,&b_lep_RelIso);
	tree->SetBranchAddress("lep_matchedR03_PdgId",&lep_matchedR03_PdgId,&b_lep_matchedR03_PdgId);
	tree->SetBranchAddress("lep_matchedR03_MomId",&lep_matchedR03_MomId,&b_lep_matchedR03_MomId);
	tree->SetBranchAddress("lep_matchedR03_MomMomId",&lep_matchedR03_MomMomId,&b_lep_matchedR03_MomMomId);

}


void initNewLiteTree(TTree* newtree, bool isMC=false){

    newtree->Branch("Run",&Run,"Run/l");
    newtree->Branch("Event",&Event,"Event/l");
    newtree->Branch("LumiSect",&LumiSect,"LumiSect/l");
    newtree->Branch("nVtx",&nVtx,"nVtx/I");
    newtree->Branch("passedFullSelection",&passedFullSelection,"passedFullSelection/O");
    newtree->Branch("passedZ4lSelection",&passedZ4lSelection,"passedZ4lSelection/O");
    newtree->Branch("passedZXCRSelection",&passedZXCRSelection,"passedZXCRSelection/O");
    newtree->Branch("passedZ4lZXCRSelection",&passedZXCRSelection,"passedZ4lZXCRSelection/O");
    newtree->Branch("passedZ4lZ1LSelection",&passedZ4lZ1LSelection,"passedZ4lZ1LSelection/O");

    newtree->Branch("finalState",&finalState,"finalState/I");
    newtree->Branch("dataMCWeight",&dataMCWeight,"dataMCWeight/F");
    newtree->Branch("genWeight",&genWeight,"genWeight/F");
    newtree->Branch("crossSection",&crossSection,"crossSection/F");

    newtree->Branch("lep_id",&lep_id);
    newtree->Branch("lep_pt",&lep_pt);
    newtree->Branch("lep_eta",&lep_eta);
    newtree->Branch("lep_phi",&lep_phi);
    newtree->Branch("lep_mass",&lep_mass);
    newtree->Branch("lep_tightId",&lep_tightId);
    newtree->Branch("lep_RelIso",&lep_RelIso);
    newtree->Branch("lep_RelIsoNoFSR",&lep_RelIso);
    newtree->Branch("lep_Hindex",lep_Hindex);

    if (isMC) {
        newtree->Branch("lep_matchedR03_PdgId",&lep_matchedR03_PdgId);
        newtree->Branch("lep_matchedR03_MomId",&lep_matchedR03_MomId);
        newtree->Branch("lep_matchedR03_MomMomId",&lep_matchedR03_MomMomId);
    };
    newtree->Branch("mass4l",&mass4l,"mass4l/F");
    newtree->Branch("massZ1",&massZ1,"massZ1/F");
    newtree->Branch("massZ2",&massZ2,"massZ2/F");
    newtree->Branch("met",&met,"met/F");
    newtree->Branch("met_phi",&met_phi,"met_phi/F");
}


void testCR()
{
  std::cout<<"Hello"<<std::endl;
  TString processFileName = "/cms/user/guojl/Sample/skimed/2018_noDuplicates.root" ;
  TChain* zxTree = new TChain("passedEvents");
  zxTree->Add(processFileName);
  Long64_t nentries = zxTree->GetEntries();
  std::cout<<nentries<<std::endl;
  SetBranches(zxTree);
  zxTree->LoadTree(0);

  float  var_plotHigh = 870.0;
  float var_plotLow = 70.0;
  float  var_nBins = 40;
  TH1D *h1D_m4l_2P2F_2e2mu = new TH1D("h1D_m4l_2P2F_2e2mu","h1D_m4l_2P2F_2e2mu",var_nBins, var_plotLow, var_plotHigh); h1D_m4l_2P2F_2e2mu->Sumw2();
  TH1D *h1D_m4l_2P2F_2mu2e = new TH1D("h1D_m4l_2P2F_2mu2e","h1D_m4l_2P2F_2mu2e",var_nBins, var_plotLow, var_plotHigh); h1D_m4l_2P2F_2mu2e->Sumw2();
  TH1D *h1D_m4l_2P2F_4e = new TH1D("h1D_m4l_2P2F_4e","h1D_m4l_2P2F_4e",var_nBins, var_plotLow, var_plotHigh); h1D_m4l_2P2F_4e->Sumw2();
  TH1D *h1D_m4l_2P2F_4mu = new TH1D("h1D_m4l_2P2F_4mu","h1D_m4l_2P2F_4mu",var_nBins, var_plotLow, var_plotHigh); h1D_m4l_2P2F_4mu->Sumw2();


  for(int iEvt=0; iEvt < nentries; iEvt++){
      zxTree->GetEntry(iEvt);
      if(iEvt%50000==0) cout <<massZ1<< "   event: " << iEvt << "/" << nentries << endl;
      if (passedZXCRSelection)
        {
	    int lep_tight[4];
            float lep_iso[4];
            int idL[4];

            for(unsigned int k = 0; k <= 3; k++) {
                lep_tight[k] = lep_tightId->at(lep_Hindex[k]);
                lep_iso[k]= lep_RelIso->at(lep_Hindex[k]);
                idL[k] = lep_id->at(lep_Hindex[k]);
            }
            int nFailedLeptonsZ1 = !(lep_tight[0] && ((abs(idL[0])==11) || (abs(idL[0])==13 && lep_iso[0]<0.35))) + !(lep_tight[1] && ((abs(idL[1])==11) || (abs(idL[1])==13 && lep_iso[1]<0.35)));
            int nFailedLeptonsZ2 = !(lep_tight[2] && ((abs(idL[2])==11) || (abs(idL[2])==13 && lep_iso[2]<0.35))) + !(lep_tight[3] && ((abs(idL[3])==11) || (abs(idL[3])==13 && lep_iso[3]<0.35)));

            int nFailedLeptons   = nFailedLeptonsZ1 + nFailedLeptonsZ2;
            bool CR_2P2F_2e2mu_combination = (((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==48) && (passedZXCRSelection) && (nFailedLeptons == 2));
            bool CR_2P2F_4e  = (((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==44) && (passedZXCRSelection) && (nFailedLeptons == 2));
            bool CR_2P2F_4mu = (((abs(idL[0])+abs(idL[1])+abs(idL[2])+abs(idL[3]))==52) && (passedZXCRSelection) && (nFailedLeptons == 2));


            if  ( CR_2P2F_2e2mu_combination && ((abs(idL[2])+abs(idL[3]))== 26) ) h1D_m4l_2P2F_2e2mu->Fill(mass4l,1);
            if  ( CR_2P2F_2e2mu_combination && ((abs(idL[2])+abs(idL[3]))== 22) ) h1D_m4l_2P2F_2mu2e->Fill(mass4l,1);
            if  ( CR_2P2F_4e )  h1D_m4l_2P2F_4e->Fill(mass4l,1);
            if  ( CR_2P2F_4mu ) h1D_m4l_2P2F_4mu->Fill(mass4l,1);
   	}
      else continue;
      }

  TCanvas *c1 = new TCanvas("c1", "myPlots",0,75,600,600);
  gStyle->SetOptFit(1);
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  c1->Range(-102.5,-10.38415,847.5,69.4939);
  c1->SetFillColor(0);
  c1->SetBorderMode(0);
  c1->SetBorderSize(2);
  c1->SetTickx(1);
  c1->SetTicky(1);
  c1->SetLeftMargin(0.18);
  c1->SetRightMargin(0.05);
  c1->SetTopMargin(0.05);
  c1->SetBottomMargin(0.13);
  c1->SetFrameFillStyle(0);
  c1->SetFrameBorderMode(0);
  c1->SetFrameFillStyle(0);
  c1->SetFrameBorderMode(0);

  h1D_m4l_2P2F_2e2mu->Draw("e1");
  c1->SaveAs("test_2P2F_2e2mu.pdf");

  h1D_m4l_2P2F_2mu2e->Draw("e1");
  c1->SaveAs("test_2P2F_2mu2e.pdf");

  h1D_m4l_2P2F_4e->Draw("e1");
  c1->SaveAs("test_2P2F_4e.pdf");

  h1D_m4l_2P2F_4mu->Draw("e1");
  c1->SaveAs("test_2P2F_4mu.pdf");


}
