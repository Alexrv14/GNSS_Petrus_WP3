#!/usr/bin/env python

########################################################################
# PETRUS/SRC/Perf.py:
# This is the Performances Module of PETRUS tool
#
#  Project:        PETRUS
#  File:           Perf.py
#  Date(YY/MM/DD): 16/02/21
#
#  Author: GNSS Academy
#  Copyright 2021 GNSS Academy
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#
########################################################################

# Import External and Internal functions and Libraries
#----------------------------------------------------------------------
import sys, os
# Add path to find all modules
Common = os.path.dirname(os.path.dirname(
    os.path.abspath(sys.argv[0]))) + '/COMMON'
sys.path.insert(0, Common)
from InputOutput import RcvrIdx
import numpy as np

# Performances internal functions
#-----------------------------------------------------------------------

def initializePerfInfo(Conf, Services, Rcvr, RcvrInfo, Doy, PerfInfo):

    # Purpose: Initialize Performances Info for a given Rcvr

    # Parameters
    # ==========
    # Conf: dict
    #       Configuration dictionary
    # Rcvr: str
    #       Receiver acronym
    # RcvrInfo: list
    #           Receiver information: position, masking angle...
    # Doy: int
    #      Day of Year
    # Doy: int
    #      Day of Year
    # Services: list
    #           List of service levels

    # Returns
    # =======
    # Nothing

    # Initialize internal variables
    ContWindow = 15

    # Loop over all the activated service levels
    for Service in Services:
        # If service activated
        if Conf[Service][0] == 1:
            # Initialize PerInfo dictionary
            PerfInfo[Service] = {
                "Rcvr": Rcvr,                               # Receiver acronym
                "Lon": float(RcvrInfo[RcvrIdx["LON"]]),     # Receiver reference longitude
                "Lat": float(RcvrInfo[RcvrIdx["LAT"]]),     # Receiver reference latitude
                "Doy": Doy,                                 # Day of year
                "Service": Service,                         # Service level
                "SamSol": 0,                                # Number of total samples 
                "SamNoSol": 0,                              # Number of samples with no SBAS solution
                "Avail": 0.0,                               # Availability percentage
                "ContRisk": 0.0,                            # Continuity risk
                "NotAvail": 0,                              # Number of non-available samples for the selected service level
                "NsvMin": 0,                                # Minimum number of satellites
                "NsvMax": 0,                                # Maximum number of satellites    
                "HpeRms": 0.0,                              # HPE RMS
                "VpeRms": 0.0,                              # VPE RMS
                "Hpe95": [],                                # HPE 95% percentile
                "Vpe95": [],                                # VPE 95% percentile                        
                "HpeMax": 0.0,                              # Maximum HPE
                "VpeMax": 0.0,                              # Maximum VPE
                "ExtVpe": 0.0,                              # Extrapolated VPE
                "HplMin": 0.0,                              # Minimum HPL
                "VplMin": 0.0,                              # Minimum VPL
                "HplMax": 0.0,                              # Maximum HPL
                "VplMax": 0.0,                              # Maximum VPL
                "HsiMax": 0.0,                              # Maximum HSI
                "VsiMax": 0.0,                              # Maximum VSI
                "Nmi": 0,                                   # Number of misleading information events
                "Nhmi": 0,                                  # Number of hazardous misleading information events
                "PdopMax": 0.0,                             # Maximum PDOP
                "HdopMax": 0.0,                             # Maximum HDOP
                "VdopMax": 0.0,                             # Maximum VDOP
                "Buff": [0] * ContWindow                    # Continuity buffer
                } # End of PerfInfo[Service]

        # End of if(Conf[Service][0] == 1)

    # End of PerfInfo

# End of initializePerfInfo:


