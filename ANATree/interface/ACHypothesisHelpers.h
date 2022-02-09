#ifndef ACHYPOTHESISHELPERS_H
#define ACHYPOTHESISHELPERS_H

#include "DiscriminantClasses.h"
#include <IvyFramework/IvyDataTools/interface/HostHelpersCore.h>
#include <IvyFramework/IvyAutoMELA/interface/IvyMELAOutputStreamerExt.h>
//#include <CMS3/Dictionaries/interface/CMS3StreamHelpers.h>


using namespace std;
using namespace IvyStreamHelpers;


namespace ACHypothesisHelpers{
  enum ACHypothesis{
    kSM=0,
    kL1,
    kA2,
    kA3,
    kL1ZGs,
    nACHypotheses
  };
  enum ProductionType{
    kGG,
    kVBF,
    kHadVH,
    nProductionTypes
  };
  enum DecayType{
    kZZ4l_onshell,
    kZZ4l_offshell,
    kZZ2l2nu_offshell,
    kZW3l1nu,
    nDecayTypes
  };

  bool isOnshellDecay(DecayType dktype);

  TString getACHypothesisName(ACHypothesisHelpers::ACHypothesis hypo);
  TString getACHypothesisLabel(ACHypothesisHelpers::ACHypothesis hypo);
  TString getACHypothesisFLabel(ACHypothesisHelpers::ACHypothesis hypo);

  TString getDecayFinalStateLabel(ACHypothesisHelpers::DecayType dktype);

  std::vector<DiscriminantClasses::Type> getACHypothesisKDSet(ACHypothesisHelpers::ACHypothesis hypo, ACHypothesisHelpers::ProductionType prod_type, ACHypothesisHelpers::DecayType decay_type);
  std::vector<TString> getACHypothesisKDNameSet(ACHypothesisHelpers::ACHypothesis hypo, ACHypothesisHelpers::ProductionType prod_type, ACHypothesisHelpers::DecayType decay_type);

  float getACHypothesisMEHZZGVal(ACHypothesisHelpers::ACHypothesis hypo);
  float getACHypothesisHZZGVal(ACHypothesisHelpers::ACHypothesis hypo);

}

#endif
