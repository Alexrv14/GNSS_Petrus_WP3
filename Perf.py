#!/usr/bin/env python

########################################################################
# PETRUS/SRC/Perf.py:
# This is the Performances Module of PETRUS tool
#
# Project:        PETRUS
# File:           Perf.py
# Date(YY/MM/DD): 16/02/21
#
# Author: GNSS Academy
# Copyright 2021 GNSS Academy
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
from COMMON import Stats, GnssConstants
from math import sqrt
from collections import OrderedDict
from InputOutput import generateHistFile

# Performances internal functions
#-----------------------------------------------------------------------

def updateBuff(ContBuff, Status):

    # Function updating the continuity buffer per epoch

    ContBuff.pop(0)
    ContBuff.append(Status)

# End of updateBuff

def resetBuff(Status, Window):

    # Function updating the continuity buffer per epoch

    ContBuff = [0] * Window
    updateBuff(ContBuff, Status)

    return ContBuff

# End of resetBuff

# ----------------------------------------------------------------------
# Performances main functions
#-----------------------------------------------------------------------

def initializePerfInfo(Conf, Services, Rcvr, RcvrInfo, Doy, PerfInfo, VpeHistInfo):

    # Purpose: Initialize PerInfo for a given receiver for all activated service levels
    #          Initialize LPV200 VpeHistInfo for a given receiver

    # Parameters
    # ==========
    # Conf: dict
    #       Configuration information dictionary
    # Services: list
    #           List of available service levels
    # Rcvr: str
    #       Receiver acronym
    # RcvrInfo: list
    #           List containing receiver information: position, masking angle...
    # Doy: int
    #      Day of the year
    # PerInfo: dict
    #          Dictionary containing performances information per for all service levels
    # VpeHistInfo: dict
    #              Dictionary containing VPE histogram information per for LPV200 
    #              service level

    # Returns
    # =======
    # Nothing

    # Initialize internal variables
    Idx = {"FLAG": 0, "HAL": 1, "VAL": 2, "HPE95": 3, "VPE95": 4, "VPE1E7": 5, "AVAI": 6, "CONT": 7, "CINT": 8}

    # Loop over all the activated service levels
    for Service in Services:
        # If service activated
        if int(Conf[Service][Idx["FLAG"]]) == 1:
            # Initialize PerInfo dictionary
            PerfInfo[Service] = {
                "Rcvr": Rcvr,                                       # Receiver acronym
                "Lon": float(RcvrInfo[RcvrIdx["LON"]]),             # Receiver reference longitude
                "Lat": float(RcvrInfo[RcvrIdx["LAT"]]),             # Receiver reference latitude
                "Doy": Doy,                                         # Day of year
                "Service": Service,                                 # Service level
                "SamSol": 86400 // int(Conf["SAMPLING_RATE"]),      # Number of total samples processed
                "SamNoSol": 86400 // int(Conf["SAMPLING_RATE"]),    # Number of samples with no SBAS solution
                "Avail": 0,                                         # Availability percentage
                "ContRisk": 0.0,                                    # Continuity risk
                "ContBuff": [0] * int(Conf[Service][Idx["CINT"]]),  # Continuity risk buffer
                "PrevStatus": 0,                                    # Previous availability status
                "PrevSod": 0.0,                                     # Previous computed epoch
                "ContEvent": 0,                                     # Number of discontinuity events
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

            if Service == "LPV200":
                # Initialize LPV200 VpeHistInfo dictionary
                VpeHistInfo["Rcvr"] = Rcvr                          # Receiver acronym
                VpeHistInfo["Service"] = Service                    # Service level
                VpeHistInfo["BinId"] = 0                            # Bin ID
                VpeHistInfo["BinMin"] = 0.0                         # Bin minimum
                VpeHistInfo["BinMax"] = 0.0                         # Bin maximum
                VpeHistInfo["BinNumSam"] = 0                        # Bin number of samples
                VpeHistInfo["BinFreq"] = 0.0                        # Bin relative frequency
                # End of LPV200 VpeHistInfo
            
            # End of if(Service == "LPV200"):

        # End of if(Conf[Service][0] == 1)

    # End for Service in Services:

# End of initializePerfInfo:

def updatePerfEpoch(Conf, Service, PosInfo, PerfInfoSer):

    # Purpose: Update PerfInfo for a given epoch and service level

    # Parameters
    # ==========
    # Conf: dict
    #       Configuration information dictionary
    # Service: str
    #          Selected service level
    # PosInfo: dict
    #          Dictionary containing position information per epoch in PA and NPA (when activated)
    # PerfInfoSer: dict
    #              Dictionary containing performances information per service level

    # Returns
    # =======
    # Nothing

    # Initialize internal variables
    HistRes = GnssConstants.HIST_RES
    AvailStatus = 0
    Idx = {"FLAG": 0, "HAL": 1, "VAL": 2, "HPE95": 3, "VPE95": 4, "VPE1E7": 5, "AVAI": 6, "CONT": 7, "CINT": 8}
    
    # If SBAS solution has been achieved
    if PosInfo["Sol"] != 0:
        
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
        if (PosInfo["Hpl"]/Conf[Service][Idx["HAL"]]) > 1 or (PosInfo["Vpl"]/Conf[Service][Idx["VAL"]]) > 1:
            # Tag sample as non-available for selected service level
            PerfInfoSer["NotAvail"] = PerfInfoSer["NotAvail"] + 1

        elif (PosInfo["Hpl"]/Conf[Service][Idx["HAL"]]) < 1 and (PosInfo["Vpl"]/Conf[Service][Idx["VAL"]]) < 1:
            # Tag sample as available for selected service level
            AvailStatus = 1
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
            Stats.updateHist(PerfInfoSer["HpeHist"], abs(PosInfo["Hpe"]), HistRes)
            # Update VPE95 histogram
            Stats.updateHist(PerfInfoSer["VpeHist"], abs(PosInfo["Vpe"]), HistRes)

            # Update maximum HPE and VPE values
            # ----------------------------------------------------------------------
            # Get maximum HPE
            PerfInfoSer["HpeMax"] = Stats.updateMax(PerfInfoSer["HpeMax"], PosInfo["Hpe"])
            # Get maximum VPE
            PerfInfoSer["VpeMax"] = Stats.updateMax(PerfInfoSer["VpeMax"], PosInfo["Vpe"])

            # Update misleading information events
            # ----------------------------------------------------------------------
            if PosInfo["Hsi"] >= 1 or abs(PosInfo["Vsi"]) >= 1:
                if PosInfo["Hpe"] < Conf[Service][Idx["HAL"]] and abs(PosInfo["Vpe"]) < Conf[Service][Idx["VAL"]]:
                    # Tag sample as misleading information (MI)
                    PerfInfoSer["Nmi"] = PerfInfoSer["Nmi"] + 1
                elif PosInfo["Hpe"] >= Conf[Service][Idx["HAL"]] or abs(PosInfo["Vpe"]) >= Conf[Service][Idx["VAL"]]:
                    # Tag sample as hazardous misleading information (HMI)
                    PerfInfoSer["Nhmi"] = PerfInfoSer["Nhmi"] + 1

                # End of if(PosInfo["Hpe"] < Conf[Idx["HAL"]] and abs(PosInfo["Vpe"]) < Conf[Idx["VAL"]]):
            
            # End of if(PosInfo["Hsi"] >= 1 or abs(PosInfo["Vsi"]) >= 1):

        # End of if((PosInfo["Hpl"]/Conf["HAL"]) > 1 or (PosInfo["Vpl"]/Conf["VAL"]) > 1):

    # End of if (PosInfo["Sol"] != 0):
    
    # Update continuity risk
    # ---------------------------------------------------------------------- 
    # Update continuity buffer
    updateBuff(PerfInfoSer["ContBuff"], AvailStatus)
    # If jump from available to non-available status detected
    if AvailStatus == 0 and PerfInfoSer["PrevStatus"] == 1:
        # Update the number of discontinuity events 
        PerfInfoSer["ContEvent"] = PerfInfoSer["ContEvent"] + sum(PerfInfoSer["ContBuff"])
    # If data gap in performances information detected
    if PerfInfoSer["PrevSod"] != 0.0 and (PosInfo["Sod"] - PerfInfoSer["PrevSod"]) > int(Conf["SAMPLING_RATE"]):
        # Update the number of discontinuity events and reset continuity buffer
        PerfInfoSer["ContEvent"] = PerfInfoSer["ContEvent"] + sum(PerfInfoSer["ContBuff"])
        PerfInfoSer["ContBuff"] = resetBuff(AvailStatus, int(Conf[Service][Idx["CINT"]]))
    
    # Update previous availabilty status and previous computed epoch
    PerfInfoSer["PrevStatus"] = AvailStatus
    PerfInfoSer["PrevSod"] = PosInfo["Sod"]

# End of updatePerfEpoch:

def computeFinalPerf(PerfInfoSer):

    # Purpose: Compute final PerfInfo per service level

    # Parameters
    # ==========
    # PerfInfoSer: dict
    #              Dictionary containing performance information per service level

    # Returns
    # =======
    # Nothing

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
    
    # Compute continuity risk
    # ----------------------------------------------------------------------
    PerfInfoSer["ContRisk"] = PerfInfoSer["ContEvent"]/PerfInfoSer["Avail"]
    
    # Compute availability
    # ----------------------------------------------------------------------
    PerfInfoSer["Avail"] = 100 * PerfInfoSer["Avail"]/PerfInfoSer["SamSol"]

    # End of computeFinalPerf:

def computeVpeHist(fhist, PerfInfo, VpeHistInfo):

    # Purpose: Compute final VpeHistInfo per for LPV200 service level
    #          Generate the VPE output file

    # Parameters
    # ==========
    # fhist: str
    #        Path to VPE Histogram file
    # PerfInfo: dict
    #           Dictionary containing performances information for all service levels
    # VpeHistInfo: dict
    #              Dictionary containing VPE histogram information for LPV200 service level


    # Returns
    # =======
    # Nothing

    # Initialize internal variables
    BinId = 0
    HistRes = GnssConstants.HIST_RES

    # Loop over all services levels in PerfInfo
    for Service, PerfInfoSer in PerfInfo.items():
        # If service == LPV200
        if Service == "LPV200":
            # Sort VPE histogram
            SortedHist = OrderedDict({})
            for key in sorted(PerfInfoSer["VpeHist"].keys()):
                SortedHist[key] = PerfInfoSer["VpeHist"][key]

            # Loop over the bins in VpeHist
            for Bin, Samples in SortedHist.items():
                # Compute VPE histogram statistics
                VpeHistInfo["BinId"] = BinId
                VpeHistInfo["BinNumSam"] = Samples
                VpeHistInfo["BinFreq"] = VpeHistInfo["BinNumSam"]/(PerfInfoSer["SamSol"] - PerfInfoSer["NotAvail"])
                VpeHistInfo["BinMin"] = Bin
                VpeHistInfo["BinMax"] = (Bin/HistRes + (1 - HistRes))*HistRes
                # Update Bin ID
                BinId = BinId + 1
                # Generate output file
                generateHistFile(fhist, VpeHistInfo)

            # End of for(Bin, Samples in SortedHist.items()):

        # End of if(Service == "LPV200"):

    # End of computeVpeHist:
