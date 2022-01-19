#ifndef TREELOOP_H
#define TREELOOP_H

#include <vector>
#include <string>
#include "IvyBase.h"
#include <IvyFramework/IvyAutoMELA/interface/IvyMELAHelpers.h>
#include <IvyFramework/IvyDataTools/interface/HostHelpersCore.h>

class TreeLoop : public IvyBase
{
public:
  TreeLoop();
  ~TreeLoop();

  void setMatrixElementList(std::vector<std::string> const& MElist, bool const& isGen);
  void setMatrixElementListFromFile(std::string fname, std::string const& MElistTypes, bool const& isGen); // MElistTypes is comman-separated

protected:
  // ME lists
  std::vector<std::string> lheMElist;
  std::vector<std::string> recoMElist;
  IvyMELAHelpers::GMECBlock MEblock;

  // Output tree, Saved Events Trees
  TTree *passedEventsTree_All;


};

#endif
