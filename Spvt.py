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
#----------------------------------------------------------------------
import sys, os
# Add path to find all modules
Common = os.path.dirname(os.path.dirname(
    os.path.abspath(sys.argv[0]))) + '/COMMON'
sys.path.insert(0, Common)
from collections import OrderedDict
from InputOutput import RcvrIdx
from COMMON import Coordinates
import numpy as np

# Spvt internal functions
#-----------------------------------------------------------------------

def buildResidualsVector(SatCorrInfo, PosInfo):

    # Purpose: Compute row of the residuals vector for the spvt computation

    # Get receiver and satellite position in the WGS84 reference frame
    RcvrPos = np.array(Coordinates.llh2xyz(PosInfo["Lon"], PosInfo["Lat"], PosInfo["Alt"]))
    SatPos = np.array([SatCorrInfo["SatX"], SatCorrInfo["SatY"], SatCorrInfo["SatZ"]])
    # Compute the geometrical range
    GeomRange = np.linalg.norm(np.subtract(SatPos, RcvrPos))
    # Compute the residuals
    Res = SatCorrInfo["CorrPsr"] - PosInfo["Clk"] - GeomRange

    return Res

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

def computeSpvtSolution(Conf, RcvrInfo, CorrInfo):

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
    # Rcvr: list
    #       Receiver information: position, masking angle...
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
    NumSatPa = 0
    NumSatNpa = 0
    ResVector = []
    GMatrix = []
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
            "NumSatPa": 0.0,        # Number of visible satellites in PA solution
            "HpePa": 0.0,           # HPE 
            "VpePa": 0.0,           # VPE 
            "EpePa": 0.0,           # EPE
            "NpePa": 0.0,           # NPE 
            "HplPa": 0.0,           # HPL
            "VplPa": 0.0,           # VPL
            "HsiPa": 0.0,           # Horiontal Safety Index
            "VsiPa": 0.0,           # Vertical Safety Index
            "HdopPa": 0.0,          # HDOP
            "VdopPa": 0.0,          # VDOP
            "PdopPa": 0.0,          # PDOP
            "TdopPa": 0.0,          # TDOP
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
            # If the satellite is not available
            if SatCorrInfo["Flag"] == 0:
                pass
            # If the satellite is available for PA
            elif SatCorrInfo["Flag"] == 1:
                # Update number of available satellites for PA
                NumSatPa = NumSatPa + 1
                # Compute row of the residuals vector for satellite
                ResVector.append(buildResidualsVector(SatCorrInfo, PosInfo))
                # Compute row of the geometry matrix G for satellite
                GMatrix.append(buildGMatrix(SatCorrInfo))
                # Compute diagonal element of the weighting matrix W for satellite
                Weights.append(buildWMatrix(SatCorrInfo))
            # If the satellite is only available for NPA
            elif SatCorrInfo["Flag"] == 2:
                # Update number of available satellites for NPA
                NumSatNpa = NumSatNpa + 1
    
        # Get number of visible satellites
        PosInfo["NumSatVis"] = len(CorrInfo)
        # Get number of satellites used to compute the PA solution
        PosInfo["NumSatPa"] = NumSatPa

        # Svpt computation
        # ----------------------------------------------------------
        # Compute inputs for the svpt computation
        # Get full residuals vector
        ResVector = np.reshape(ResVector,(NumSatPa,1))
        # Get full geometry matrix G
        GMatrix = np.reshape(GMatrix,(NumSatPa,4))
        # Get full weighting matrix W
        WMatrix = np.diag(Weights)
    
        # Check the number of available satellites
        # If NumSatPa is not high enough
        if NumSatPa < 4 and NumSatNpa < 4:
            PosInfo["Sol"] = 0
        elif NumSatPa < 4 and NumSatNpa > 3:
            PosInfo["Sol"] = 2
        # If NumSatPa higher or equal to four
        elif NumSatPa > 3:
            PosInfo["Sol"] = 1
        
        # End of PosInfo initialization

    # End of if(len(CorrInfo) > 0):
    
    return PosInfo
    
