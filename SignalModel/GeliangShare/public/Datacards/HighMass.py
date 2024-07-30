from HiggsAnalysis.CombinedLimit.PhysicsModel import *
import fnmatch

class HighMass(PhysicsModel):
    
    def __init__(self):
        self.POIs = ""
        self.pois = []
        self.stage0 = False
        self.year = "run2"
        self.options = ""
        self.count = 0

    def setModelBuilder(self,modelBuilder):
        PhysicsModel.setModelBuilder(self,modelBuilder)
        self.modelBuilder.doModelBOnly = False

    def getYieldScale(self,bin,process):
        if not self.DC.isSignal[process]:
            return 1
        else:
            if process.startswith("ggH") and not process.startswith("ggH125"):
                muname= "r_ggH"
            elif process.startswith("gghint"):
                muname= "r_ggHint"
            elif process.startswith("VBFH") and not process.startswith("VBFH125"):
                muname= "r_VBFH"
            elif process.startswith("vbfint"):
                muname= "r_VBFHint"
            else :
                print "Process ",process," is not a signal!!!"
                return 1
        return muname

    def setPhysicsOptions(self,physOptions):
        print "Set physics options"
        for po in physOptions:
            print "Setting option %s" %po
            if "run2" in po:
                self.year= "run2"
                print "Year: run2"
            if "2016" in po:
                self.year= "2016"
                print "Year: 2016"
            if "2017" in po:
                self.year= "2017"
                print "Year: 2017"
            if "2018" in po:
                self.year= "2018"
                print "Year: 2018"
            if "doStage0" in po:
                self.stage0= True
                print "Do stage0"

    def doParametersOfInterest(self):
        self.modelBuilder.doVar("r[1,0,10]")
        self.modelBuilder.doVar("f_vbf[1,0,1]")
        self.modelBuilder.doVar("f_int[1,0,10]")
        self.modelBuilder.factory_("expr::r_ggH(\"@0*(1-@1)\",r,f_vbf)")
        self.modelBuilder.factory_("expr::r_VBFH(\"@0*@1\",r,f_vbf)")
        self.modelBuilder.factory_("expr::r_ggHint(\"sqrt(@0)*@1\",r_ggH,f_int)")
        self.modelBuilder.factory_("expr::r_VBFHint(\"sqrt(@0)*@1\",r_VBFH,f_int)")

        self.pois.append("r")
        # self.pois.append("f_vbf")

        self.POIs=",".join(self.pois)
        print "Default parameters of interest: ", self.POIs
        self.modelBuilder.doSet("POI",self.POIs)

HighMass = HighMass()
