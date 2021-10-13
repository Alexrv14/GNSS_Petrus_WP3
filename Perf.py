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

from scipy import stats
# Add path to find all modules
Common = os.path.dirname(os.path.dirname(
    os.path.abspath(sys.argv[0]))) + '/COMMON'
sys.path.insert(0, Common)
from InputOutput import RcvrIdx
from COMMON import Stats
from math import sqrt

# Performances internal functions
#-----------------------------------------------------------------------

def initializePerfInfo(Conf, Services, Rcvr, RcvrInfo, Doy, PerfInfo, VpeHistInfo):

    # Purpose: Initialize Performances Info for a given Rcvr

    # Parameters
    # ==========
    # Conf: dict
    #       Configuration dictionary
    # Services: list
    #           List of service levels
    # Rcvr: str
    #       Receiver acronym
    # RcvrInfo: list
    #           Receiver information: position, masking angle...
    # Doy: int
    #      Day of Year
    # PerInfo: dict
    #          Dictionary 
    # VpeHistInfo: dict
    #              Dictionary containing VPE histogram info per service level

    # Returns
    # =======
    # Nothing

    # Initialize internal variables
    ContWindow = 15
    Idx = {"Flag": 0, "HAL": 1, "VAL": 2, "HPE95": 3, "VPE95": 4, "VPE1E7": 5, "AVAI": 6, "CONT": 7, "CINT": 8}

    # Loop over all the activated service levels
    for Service in Services:
        # If service activated
        if Conf[Service][Idx["Flag"]] == 1:
            # Initialize PerInfo dictionary
            PerfInfo[Service] = {
                "Rcvr": Rcvr,                                       # Receiver acronym
                "Lon": float(RcvrInfo[RcvrIdx["LON"]]),             # Receiver reference longitude
                "Lat": float(RcvrInfo[RcvrIdx["LAT"]]),             # Receiver reference latitude
                "Doy": Doy,                                         # Day of year
                "Service": Service,                                 # Service level
                "SamSol": int(86400/int(Conf["SAMPLING_RATE"])),    # Number of total samples processed
                "SamNoSol": int(86400/int(Conf["SAMPLING_RATE"])),  # Number of samples with no SBAS solution
                "Avail": 0,                                         # Availability percentage
                "ContRisk": 0.0,                                    # Continuity risk
                "ContBuff": [0] * ContWindow,                       # Continuity risk buffer
                "NotAvail": 0,                                      # Number of non-available samples for the selected service level
                "NsvMin": 1000,                                     # Minimum number of satellites
                "NsvMax": 0,                                        # Maximum number of satellites    
                "HpeRms": 0.0,                                      # HPE RMS
                "VpeRms": 0.0,                                      # VPE RMS
                "Hpe95": 0.0,                                       # HPE 95% percentile
                "HpeHist": {},                                      # HPE Histogram
                "Vpe95": 0.0,                                       # VPE 95% percentile
                "VpeHist": {},                                      # VPE Histogram                       
                "HpeMax": 0.0,                                      # Maximum HPE
                "VpeMax": 0.0,                                      # Maximum VPE
                "ExtVpe": 0.0,                                      # Extrapolated VPE
                "HplMin": 1000.0,                                   # Minimum HPL
                "VplMin": 1000.0,                                   # Minimum VPL
                "HplMax": 0.0,                                      # Maximum HPL
                "VplMax": 0.0,                                      # Maximum VPL
                "HsiMax": 0.0,                                      # Maximum HSI
                "VsiMax": 0.0,                                      # Maximum VSI
                "Nmi": 0,                                           # Number of misleading information events
                "Nhmi": 0,                                          # Number of hazardous misleading information events
                "PdopMax": 0.0,                                     # Maximum PDOP
                "HdopMax": 0.0,                                     # Maximum HDOP
                "VdopMax": 0.0,                                     # Maximum VDOP
                } # End of PerfInfo[Service]

            # Initialize PerInfo dictionary
            VpeHistInfo[Service] = {
                "BinId": 0,                                         # Bin ID
                "BinMin": 0.0,                                      # Bin minimum
                "BinMax": 0.0,                                      # Bin maximum 
                "BinNumSam": 0,                                     # Number of samples
                "BinFreq": 0.0,                                     # Bin frequency
                } # End of VpeHistInfo[Service]

        # End of if(Conf[Service][0] == 1)

    # End for Service in Services:

# End of initializePerfInfo:

def updatePerfEpoch(Conf, PosInfo, PerfInfoSer):

    # Purpose: Update Performances Info for a given epoch

    # Parameters
    # ==========
    # Conf: list
    #       List containing information associated to the service level
    # PosInfo: dict
    #          Dictionary containing POS info per epoch in PA and NPA (when activated)
    # PerfInfoSer: dict
    #              Dictionary containing PERF info per service level

    # Returns
    # =======
    # Nothing

    # Initialize internal variables
    HistRes = 0.001
    Idx = {"Flag": 0, "HAL": 1, "VAL": 2, "HPE95": 3, "VPE95": 4, "VPE1E7": 5, "AVAI": 6, "CONT": 7, "CINT": 8}
  
    # If SBAS solution is available
    # ----------------------------------------------------------------------
    if PosInfo["Sol"] == 1:
        # Update total number of samples with no SBAS solution
        # ----------------------------------------------------------------------
        PerfInfoSer["SamNoSol"] = PerfInfoSer["SamNoSol"] - 1

        # Update number of satellites used in SBAS solution
        # ----------------------------------------------------------------------
        # Get minimum number of satellites
        PerfInfoSer["NsvMin"] = Stats.updateMin(PerfInfoSer["NsvMin"], PosInfo["NumSatSol"])
        # Get maximum number of satellites
        PerfInfoSer["NsvMax"] = Stats.updateMax(PerfInfoSer["NsvMax"], PosInfo["NumSatSol"])

        # Update HPL and VPL values
        # ----------------------------------------------------------------------
        # Get minimum HPL
        PerfInfoSer["HplMin"] = Stats.updateMin(PerfInfoSer["HplMin"], PosInfo["Hpl"])
        # Get minimum VPL
        PerfInfoSer["VplMin"] = Stats.updateMin(PerfInfoSer["VplMin"], PosInfo["Vpl"])
        # Get maximum HPL
        PerfInfoSer["HplMax"] = Stats.updateMax(PerfInfoSer["HplMax"], PosInfo["Hpl"])
        # Get maximum VPL
        PerfInfoSer["VplMax"] = Stats.updateMax(PerfInfoSer["VplMax"], PosInfo["Vpl"])
    
        # Update HSI and VSI values
        # ----------------------------------------------------------------------
        # Get maximum HSI
        PerfInfoSer["HsiMax"] = Stats.updateMax(PerfInfoSer["HsiMax"], abs(PosInfo["Hsi"]))
        # Get maximum VSI
        PerfInfoSer["VsiMax"] = Stats.updateMax(PerfInfoSer["VsiMax"], abs(PosInfo["Vsi"]))

        # Update DOPS
        # ----------------------------------------------------------------------
        # Get maximum PDOP
        PerfInfoSer["PdopMax"] = Stats.updateMax(PerfInfoSer["PdopMax"], PosInfo["Pdop"])
        # Get maximum HDOP
        PerfInfoSer["HdopMax"] = Stats.updateMax(PerfInfoSer["HdopMax"], PosInfo["Hdop"])
        # Get maximum VDOP
        PerfInfoSer["VdopMax"] = Stats.updateMax(PerfInfoSer["VdopMax"], PosInfo["Vdop"])

        # Update availability
        # ----------------------------------------------------------------------
        if (PosInfo["Hpl"]/Conf[Idx["HAL"]]) > 1 or (PosInfo["Vpl"]/Conf[Idx["VAL"]]) > 1:
            # Tag sample as non-available for selected service level
            PerfInfoSer["NotAvail"] = PerfInfoSer["NotAvail"] + 1
        
        elif (PosInfo["Hpl"]/Conf[Idx["HAL"]]) < 1 and (PosInfo["Vpl"]/Conf[Idx["VAL"]]) < 1:
            # Tag sample as available for selected service level
            PerfInfoSer["Avail"] = PerfInfoSer["Avail"] + 1

            # Update HPE and VPE RMS
            # ----------------------------------------------------------------------
            # Get new contribution of HPE RMS
            PerfInfoSer["HpeRms"] = PerfInfoSer["HpeRms"] + PosInfo["Hpe"]**2
            # Get new contribution of VPE RMS
            PerfInfoSer["VpeRms"] = PerfInfoSer["VpeRms"] + PosInfo["Vpe"]**2

            # Update HPE and VPE histograms 
            # ---------------------------------------------------------------------- 
            # Update HPE95 histogram
            Stats.updateHist(PerfInfoSer["HpeHist"], PosInfo["Hpe"], HistRes)
            # Update VPE95 histogram
            Stats.updateHist(PerfInfoSer["VpeHist"], PosInfo["Vpe"], HistRes)

            # Update maximum HPE and VPE values
            # ----------------------------------------------------------------------
            # Get maximum HPE
            PerfInfoSer["HpeMax"] = Stats.updateMax(PerfInfoSer["HpeMax"], PosInfo["Hpe"])
            # Get maximum VPE
            PerfInfoSer["VpeMax"] = Stats.updateMax(PerfInfoSer["VpeMax"], PosInfo["Vpe"])

        # End of if((PosInfo["Hpl"]/Conf["HAL"]) > 1 or (PosInfo["Vpl"]/Conf["VAL"]) > 1):

        # Update continuity risk
        # ---------------------------------------------------------------------- 

    # End of if (PosInfo["Sol"] == 0):

# End of updatePerfEpoch:

def computeFinalPerf(PerfInfoSer):

    # Purpose: Compute final Performances Info for receiver

    # Parameters
    # ==========
    # Conf: list
    #       List containing information associated to the service level
    # PerfInfoSer: dict
    #              Dictionary containing PERF info per service level

    # Returns
    # =======
    # Nothing

    # Initialize internal variables
    Idx = {"Flag": 0, "HAL": 1, "VAL": 2, "HPE95": 3, "VPE95": 4, "VPE1E7": 5, "AVAI": 6, "CONT": 7, "CINT": 8}

    # Compute final number of non-available samples
    # ----------------------------------------------------------------------
    PerfInfoSer["NotAvail"] = PerfInfoSer["NotAvail"] + PerfInfoSer["SamNoSol"]
    
    # Compute final HPE and VPE RMS
    # ----------------------------------------------------------------------
    # Compute HPE RMS
    PerfInfoSer["HpeRms"] = sqrt(PerfInfoSer["HpeRms"]/PerfInfoSer["Avail"])
    # Compute VPE RMS
    PerfInfoSer["VpeRms"] = sqrt(PerfInfoSer["VpeRms"]/PerfInfoSer["Avail"])
    
    # Compute final HPE95 and VPE95 values
    # ----------------------------------------------------------------------
    # Compute final HPE95
    Cdf, Sigmas = Stats.computeCdfFromHistogram(PerfInfoSer["HpeHist"], PerfInfoSer["Avail"])
    PerfInfoSer["Hpe95"] = Stats.computePercentile(Cdf, 95)
    # Compute final VPE95
    Cdf, Sigmas = Stats.computeCdfFromHistogram(PerfInfoSer["VpeHist"], PerfInfoSer["Avail"])
    PerfInfoSer["Vpe95"] = Stats.computePercentile(Cdf, 95)
    
    # Compute final extrapolated VPE value
    # ----------------------------------------------------------------------
    ThresholdBin = Stats.computePercentile(Cdf, 60)
    PerfInfoSer["ExtVpe"] = 5.33 * Stats.computeOverbound(Sigmas, ThresholdBin)
    
    # Compute availability
    # ----------------------------------------------------------------------
    PerfInfoSer["Avail"] = 100 * PerfInfoSer["Avail"]/PerfInfoSer["SamSol"]

    # Compute continuity
    # ----------------------------------------------------------------------

    
    # End of computeFinalPerf: