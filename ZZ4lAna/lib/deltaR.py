import numpy as np
import math

def deltaR( eta1, phi1, eta2, phi2):
    if abs(phi1-phi2)>np.pi:
        dR = math.sqrt((2.*np.pi - abs(phi1 - phi2)) * (2.*np.pi - abs(phi1 - phi2)) + (eta1 - eta2) * (eta1 - eta2))
    else:
        dR = math.sqrt((phi1 - phi2) * (phi1 - phi2) + (eta1 - eta2) * (eta1 - eta2))
    return dR
