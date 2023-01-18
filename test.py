import uproot 
import boost_histogram as bh
import matplotlib.pyplot as plt
import matplotlib as mpl
import mplhep as hep
import awkward as ak
import pandas as pd
import numpy as np
import seaborn as sns

#===========================================load self.config file====================================================================
import sys,os
sys.path.append("/cms/user/guojl/ME_test/CMSSW_10_6_26/src/HZZAnalysis/lib")
from utils import *
from setting import setting

year = '2016'; cutcat = 'resolved'

h  = GetHisto(year,cutcat).hist
print(h[cutcat][cutcat])

