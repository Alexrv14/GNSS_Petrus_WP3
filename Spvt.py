#!/usr/bin/env python

########################################################################
# PETRUS/SRC/Spvt.py:
# This is the SPVT Module of PETRUS tool
#
#  Project:        PETRUS
#  File:           Spvt.py
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
# ----------------------------------------------------------------------

import sys, os
# Add path to find all modules
Common = os.path.dirname(os.path.dirname(
    os.path.abspath(sys.argv[0]))) + '/COMMON'
sys.path.insert(0, Common)
from collections import OrderedDict
from InputOutput import RcvrIdx
from COMMON import GnssConstants
from COMMON.Wlsq import wlsqComputation
import numpy as np

# Spvt internal functions
# ----------------------------------------------------------------------

def buildWMatrix(SatCorrInfo):

    # Purpose: Compute diagonal element of the weighting matrix W for the spvt computation

    # Compute the diagonal element of the weighting matrix W
    Weight = 1/(SatCorrInfo["SigmaUere"])**2

    return Weight

def buildGMatrix(SatCorrInfo):

    # Purpose: Compute row of the geometry matrix G in the ENU reference frame for the spvt computation

    # Convert degrees to radians
    DegtoRad = np.pi / 180.0
    
    # Compute row of geometry matrix G
    XComp = - (np.cos(SatCorrInfo["Elevation"]*DegtoRad)*np.sin(SatCorrInfo["Azimuth"]*DegtoRad))
    YComp = - (np.cos(SatCorrInfo["Elevation"]*DegtoRad)*np.cos(SatCorrInfo["Azimuth"]*DegtoRad))
    ZComp = - (np.sin(SatCorrInfo["Elevation"]*DegtoRad))
    BComp = 1

    return XComp, YComp, ZComp, BComp

def computeDops(GMatrix, PosInfo):

    # Purpose: Compute the DOP matrix Q in the ENU reference frame for the spvt computation, as well as 
    # the HDOP, VDOP, PDOP and TDOP

    # Compute the DOP matrix
    QMatrix = np.linalg.inv(np.dot(GMatrix.T, GMatrix))
    QDiag = np.diag(QMatrix)

    # Compute the DOPS
    PosInfo["Hdop"] = np.sqrt(QDiag[0] + QDiag[1])
    PosInfo["Vdop"] = np.sqrt(QDiag[2])
    PosInfo["Pdop"] = np.sqrt(QDiag[0] + QDiag[1] + QDiag[2])
    PosInfo["Tdop"] = np.sqrt(QDiag[3])

def buildSMatrix(GMatrix, WMatrix):

    # Purpose: Compute the S matrix in the ENU reference frame for the svpt computation

    SMatrix = np.linalg.multi_dot([np.linalg.inv(np.linalg.multi_dot([GMatrix.T, WMatrix, GMatrix])), GMatrix.T, WMatrix])

    return SMatrix

def computeProtectionLevels(GMatrix, WMatrix, PosInfo, Mode):

    # Purpose: Compute the protection levels in the ENU reference frame

    # Compute the D Matrix
    DMatrix = np.linalg.inv(np.linalg.multi_dot([GMatrix.T, WMatrix, GMatrix]))
    DDiag1 = np.diag(DMatrix)
    DDiag2 = np.diag(DMatrix, k = 1)

    # Compute the protection levels 
    if Mode == "PA":
        PosInfo["Hpl"] = np.sqrt(((DDiag1[0] + DDiag1[1])/2) + np.sqrt(((DDiag1[0] - DDiag1[1])/2)**2 + DDiag2[0]**2))*GnssConstants.MOPS_KH_PA
        PosInfo["Vpl"] = np.sqrt(DDiag1[2])*GnssConstants.MOPS_KV_PA
    elif Mode == "NPA":
        PosInfo["Hpl"] = np.sqrt(((DDiag1[0] + DDiag1[1])/2) + np.sqrt(((DDiag1[0] - DDiag1[1])/2)**2 + DDiag2[0]**2))*GnssConstants.MOPS_KH_NPA
        PosInfo["Vpl"] = np.sqrt(DDiag1[2])*GnssConstants.MOPS_KV_NPA

# Spvt main function
# -----------------------------------------------------------------------

def computeSpvtSolution(Conf, RcvrInfo, CorrInfo, Mode):

    # Purpose: Compute the svpt solution

    # More in detail, this function handles the following tasks:

    #       *  Build the Geometry matrix G in XYZ and ENU
    #       *  Build D as DOP-Matrix and PDOP
    #       *  Build the weighting W matrix
    #       *  Build the S matrix 
    #       *  Build the residuals vector as input for the WLSQ filter
    #       *  Call the iterative WLSQ filter
    #       *  Estimate the receiver position in the WGS84 reference frame
    #       *  Estimate the receiver clock Bias
    #       *  Estimate the receiver position in the ENU reference frame
    #       *  Compute the position errors in the ENU reference frame
    #       *  Compute the horizontal HPE and vertical VPE position erros
    #       *  Compute the protection levels HPL and VPL 
    #       *  Compute the DOP values: HDOP, VDOP, PDOP, TDOP

    # Attention: Several simplifications will be applied:

    #       * It is assumed that the satellite position remains constant throughout the iterative process
    #       * It is assumed that the corrections (Iono, Tropo...) remain constant throughout the iterative process
    #       * The first receiver clock guess is set to zero
    #       * The first receiver position matches the exact receiver position 

    # Parameters
    # ==========
    # Conf: dict
    #       Configuration dictionary
    # RcvrInfo: list
    #           Receiver information: position, masking angle...
    # CorrInfo: dict
    #           Corrected information for current epoch per satellite
    #           CorrInfo["G01"]["C1"]

    # Returns
    # =======
    # PosInfo: dict
    #          Spvt outputs for Rcvr on current epoch: Latitude, longitude...

    # Initialize output
    PosInfo = OrderedDict({})

    # Initialize some variables
    NumSatSol = 0
    GMatrixRows = []
    Weights = []

    # Check if corrected information is available at current epoch
    if len(CorrInfo) > 0:
        PosInfo = {
            "Sod": 0.0,             # Second of day
            "Doy": 0,               # Day of year
            "Lon": 0.0,             # Receiver estimated longitude
            "Lat": 0.0,             # Receiver estimated latitude
            "Alt": 0.0,             # Receiver estimated altitude
            "Clk": 0.0,             # Receiver estimated clock
            "Sol": 0,               # 0: No solution 1: PA Sol 2: NPA Sol
            "NumSatVis": 0.0,       # Number of visible satellites
            "NumSatSol": 0.0,       # Number of visible satellites in solution
            "Hpe": 0.0,             # HPE 
            "Vpe": 0.0,             # VPE 
            "Epe": 0.0,             # EPE
            "Npe": 0.0,             # NPE 
            "Hpl": 0.0,             # HPL
            "Vpl": 0.0,             # VPL
            "Hsi": 0.0,             # Horiontal Safety Index
            "Vsi": 0.0,             # Vertical Safety Index
            "Hdop": 0.0,            # HDOP
            "Vdop": 0.0,            # VDOP
            "Pdop": 0.0,            # PDOP
            "Tdop": 0.0,            # TDOP
        } # End of PosInfo

        # Get SoD and DoY
        PosInfo["Sod"] = CorrInfo[list(CorrInfo.keys())[0]]["Sod"]
        PosInfo["Doy"] = CorrInfo[list(CorrInfo.keys())[0]]["Doy"]
        # Get receiver coordinates first guess in the ENU reference frame
        PosInfo["Lon"] = float(RcvrInfo[RcvrIdx["LON"]])
        PosInfo["Lat"] = float(RcvrInfo[RcvrIdx["LAT"]])
        PosInfo["Alt"] = float(RcvrInfo[RcvrIdx["ALT"]])

        # Loop over all satellites in CorrInfo dictionary
        for SatCorrInfo in CorrInfo.values():
            # If the satellite is available for PA
            if SatCorrInfo["Flag"] == 1:
                # Update number of available satellites for PA
                NumSatSol = NumSatSol + 1
                # Compute row of the geometry matrix G for satellite
                GMatrixRows.append(buildGMatrix(SatCorrInfo))
                # Compute diagonal element of the weighting matrix W for satellite
                Weights.append(buildWMatrix(SatCorrInfo))
            # If the satellite is only available for NPA and NPA mode is activated
            if SatCorrInfo["Flag"] == 2 and Mode == "NPA":
                # Update number of available satellites for NPA
                NumSatSol = NumSatSol + 1
                # Compute row of the geometry matrix G for satellite
                GMatrixRows.append(buildGMatrix(SatCorrInfo))
                # Compute diagonal element of the weighting matrix W for satellite
                Weights.append(buildWMatrix(SatCorrInfo))
    
        # End of for SatCorrInfo in CorrInfo.values():
        
        # Get number of visible satellites
        PosInfo["NumSatVis"] = len(CorrInfo)
        # Get number of satellites used to compute the solution
        PosInfo["NumSatSol"] = NumSatSol

        # Svpt computation
        # ----------------------------------------------------------------------
        # Compute inputs required for the computation
        # Get full geometry matrix G
        GMatrix = np.reshape(GMatrixRows,(NumSatSol,4))
        # Get full weighting matrix W
        WMatrix = np.diag(Weights)

        # Check the number of available satellites for computing the solution
        if NumSatSol >= GnssConstants.MIN_NUM_SATS_PVT:
            # Compute DOPS
            computeDops(GMatrix, PosInfo)
            if PosInfo["Pdop"] < float(Conf["PDOP_MAX"]):
                # Compute the S matrix
                SMatrix = buildSMatrix(GMatrix, WMatrix)
                # Call WLSQ function
                wlsqComputation(Conf, CorrInfo, PosInfo, SMatrix, Mode)
                # Compute protection levels
                computeProtectionLevels(GMatrix, WMatrix, PosInfo, Mode)
                # Compute safety indexes
                PosInfo["Hsi"] = PosInfo["Hpe"]/PosInfo["Hpl"]
                PosInfo["Vsi"] = PosInfo["Vpe"]/PosInfo["Vpl"]
                # Update intermediate performances

            # End of if(PosInfo["Pdop"] < float(Conf["PDOP_MAX"])):
        
        # End if(NumSatSol >= GnssConstants.MIN_NUM_SATS_PVT):
    
    return PosInfo

    # End of computespvtsolution:
    
    ########################################################################
    # END OF SVPT FUNCTIONS MODULE
    ########################################################################
