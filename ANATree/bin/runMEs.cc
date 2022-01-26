#include <iostream>
//Auto MELA
#include "IvyBase.h"
#include <IvyFramework/IvyAutoMELA/interface/IvyMELAHelpers.h>
#include <IvyFramework/IvyAutoMELA/interface/IvyMELAOutputStreamerExt.h>
#include <IvyFramework/IvyDataTools/interface/HostHelpersCore.h>
#include "TString.h"
#include "TreeLoop.h"

int main(int argc, char** argv){
  using namespace std;
  using namespace IvyStreamHelpers;

  TreeLoop *lp = new TreeLoop("${CMSSW_BASE}/src/HZZAnalysis/ANATree/testfiles/test.root");
  lp->Loop();
  //TreeLoop loop("${CMSSW_BASE}/src/HZZAnalysis/ANATree/testfile/test.root");


  cout<<"haha"<<endl;
  return 0;
}
