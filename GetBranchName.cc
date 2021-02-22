{

  TFile *file = TFile::Open("plots.root");
  TTree*tree=(TTree*)file->Get("passedEvents");
  TObjArray *contours  = tree->GetListOfBranches();
  int Nbranch = contours->GetSize();
  vector<TString> names;
  for(int i=0; i<=Nbranch; i++){
    names.push_back(contours->At(i)->GetName());
    cout<<names[i]<<endl;
  }


}
