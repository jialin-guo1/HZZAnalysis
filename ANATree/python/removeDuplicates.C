#include <iostream>
#include <set>
#include <TString.h>
#include <TFile.h>
#include <TTree.h>

void removeDuplicates() {
    TString prefix = "/cms/user/guojl/Sample/2L2Q/UL_Legacy/2018/Data/skimed/Data2018UL";
    TString filename = prefix+".root";

    std::cout<<filename<<std::endl;

    TFile *oldfile = new TFile(filename);
    //oldfile->cd("Ana");
    //TTree *oldtree = (TTree*)oldfile->Get("Ana/passedEvents");

    //TTree *oldtree = (TTree*)gDirectory->Get("passedEvents");
    TTree *oldtree = (TTree*)oldfile->Get("passedEvents");

    Long64_t nentries = oldtree->GetEntries();
    std::cout<<nentries<<" total entries."<<std::endl;
    ULong64_t run, lumiSect, event;
    bool passedZ4lSelection;
    //oldtree->SetBranchAddress("Run",&Run);
    //oldtree->SetBranchAddress("LumiSect",&LumiSect);
    //oldtree->SetBranchAddress("Event",&Event);

    oldtree->SetBranchAddress("run",&run);
    oldtree->SetBranchAddress("lumiSect",&lumiSect);
    oldtree->SetBranchAddress("event",&event);

    //Create a new file + a clone of old tree in new file
    TFile *newfile = new TFile(
            prefix+"_noDuplicates.root"
            ,"recreate");
    TTree *newtree = oldtree->CloneTree(0);

    std::set<TString> runlumieventSet;
    //std::set<int> runlumieventSet;
    int nremoved = 0;
    Long64_t sizeofset = 0;
    for (Long64_t i=0;i<nentries; i++) {
        if (i%100000==0) {
          std::cout<<i<<"/"<<nentries<<std::endl;
          sizeofset = sizeof(runlumieventSet);
          //std::cout<<"size of set = "<<sizeofset<<std::endl;
          //std::cout<<std::endl;
        }
        oldtree->GetEntry(i);

        TString s_Run  = std::to_string(run);
        TString s_Lumi = std::to_string(lumiSect);
        TString s_Event = std::to_string(event);
        TString runlumievent = s_Run+":"+s_Lumi+":"+s_Event;

        if (runlumieventSet.find(runlumievent)==runlumieventSet.end()) {
            runlumieventSet.insert(runlumievent);
            newtree->Fill();
        } else {
            nremoved++;
        }
        //if (passedZ4lSelection) newtree->Fill();
    }

    std::cout<<nremoved<<" duplicates."<<std::endl;
    newtree->Print();
    newtree->AutoSave();
    //delete oldfile;
    delete newfile;
}
