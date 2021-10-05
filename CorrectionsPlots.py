#!/usr/bin/env python

########################################################################
# PETRUS/SRC/CorrectionPlots.py:
# This is the CorrectionsPlots Module of PETRUS tool
#
#  Project:        PETRUS
#  File:           CorrectionPlots.py
#  Date(YY/MM/DD): 05/02/21
#
#  Author: GNSS Academy
#  Copyright 2021 GNSS Academy
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#
########################################################################

from collections import OrderedDict
from math import sqrt
import sys, os
from pandas import unique
from pandas import read_csv
from InputOutput import CorrIdx, SatIdx, RcvrIdx
sys.path.append(os.getcwd() + '/' + \
    os.path.dirname(sys.argv[0]) + '/' + 'COMMON')
from COMMON import GnssConstants, Iono
from COMMON.Plots import generatePlot
from COMMON.Coordinates import xyz2llh
import numpy as np
from ConPlots import ConfCorr
import matplotlib.pyplot as plt

def initPlot(CorrFile, PlotConf, Title, Label):
    
    # Compute information from PreproObsFile
    CorrFileName = os.path.basename(CorrFile)
    CorrFileNameSplit = CorrFileName.split('_')
    Rcvr = CorrFileNameSplit[1]
    DatepDat = CorrFileNameSplit[2]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    # Dump information into PlotConf
    PlotConf["xLabel"] = "Hour of Day %s" % Doy

    PlotConf["Title"] = "%s from %s on Year %s"\
        " DoY %s" % (Title, Rcvr, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/CORR/Figures/%s/' % Label + \
        '%s_%s_Y%sD%s.png' % (Label, Rcvr, Year, Doy)

def initPlotB(CorrFile, PlotConf, Title, Label):
    
    # Compute information from PreproObsFile
    CorrFileName = os.path.basename(CorrFile)
    CorrFileNameSplit = CorrFileName.split('_')
    Rcvr = CorrFileNameSplit[1]
    DatepDat = CorrFileNameSplit[2]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    # Dump information into PlotConf
    PlotConf["Title"] = "%s from %s on Year %s"\
        " DoY %s" % (Title, Rcvr, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/CORR/Figures/%s/' % Label + \
        '%s_%s_Y%sD%s.png' % (Label, Rcvr, Year, Doy)

def roundRcvr(RcvrInfo):

    # Function rounding the position of the receiver

    Lon = int(RcvrInfo[RcvrIdx["LON"]]) // 5 
    Lat = int(RcvrInfo[RcvrIdx["LAT"]]) // 5

    # Compute rounded longitude
    if (int(RcvrInfo[RcvrIdx["LON"]]) % 5) > 2:
        RcvrLon = 5*Lon + 5
    else:
        RcvrLon = 5*Lon
    # Compute rounded latitude
    if (int(RcvrInfo[RcvrIdx["LAT"]]) % 5) > 2:
        RcvrLat = 5*Lat + 5
    else:
        RcvrLat = 5*Lat

    return RcvrLon, RcvrLat

# Plot Monitored Satellite Tracks
def plotSatTracks(CorrFile, CorrData, RcvrInfo):

    # Graph settings definition
    PlotConf = {}
    initPlotB(CorrFile, PlotConf, "Monitored Satellites Tracks", "SATS_TRACKS_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (16.8,15.2)

    PlotConf["Background"] = ["Rcvr"]

    RcvrLon, RcvrLat = roundRcvr(RcvrInfo)
    if RcvrLat > 55:
        PlotConf["LonMin"] = -180
        PlotConf["LonMax"] = 180
        PlotConf["LatMin"] = (RcvrLat - 70)
        PlotConf["LatMax"] = (RcvrLat + 10) if RcvrLat < 80 else 90
    else:
        PlotConf["LonMin"] = (RcvrLon - 115) 
        PlotConf["LonMax"] = (RcvrLon + 115) 
        PlotConf["LatMin"] = (RcvrLat - 70)
        PlotConf["LatMax"] = (RcvrLat + 35) 
    PlotConf["LonStep"] = 15
    PlotConf["LatStep"] = 10

    PlotConf["yTicks"] = range(PlotConf["LatMin"],PlotConf["LatMax"]+1,10)
    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]

    PlotConf["xTicks"] = range(PlotConf["LonMin"],PlotConf["LonMax"]+1,15)
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True
    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75
    PlotConf["BackMarker"] = "X"
    PlotConf["BackLineWidth"] = 30.0
    PlotConf["ColorMarker"] = "darkgreen"

    # Processing data to be plotted
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    x = CorrData[CorrIdx["SAT-X"]][FilterCond].to_numpy()
    y = CorrData[CorrIdx["SAT-Y"]][FilterCond].to_numpy()
    z = CorrData[CorrIdx["SAT-Z"]][FilterCond].to_numpy()
    Longitude = np.zeros(len(x))
    Latitude = np.zeros(len(x))

    for index in range(len(x)):
        Longitude[index], Latitude[index], h = xyz2llh(x[index], y[index], z[index])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Labels = ["Tracks", "Rcvr"]
    for Label in Labels:
        if Label == "Rcvr":
            PlotConf["xData"][Label] = np.array([RcvrInfo[RcvrIdx["LON"]]])
            PlotConf["yData"][Label] = np.array([RcvrInfo[RcvrIdx["LAT"]]])
        else:
            PlotConf["xData"][Label] = Longitude
            PlotConf["yData"][Label] = Latitude
            PlotConf["zData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot LTC Corrections
def plotLtcCorr(CorrFile, CorrData, SatData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "LTC Corrections", "LTC_CORRECTIONS_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (12.4,8.6)
    PlotConf["Background"] = ["LTC-X","LTC-Y","LTC-Z","LTC-B","FC"]

    PlotConf["yLabel"] = "Fast and Long Term Corrections [m]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = True
    PlotConf["Legend"] = ["ENTtoGPS","LTC-X","LTC-Y","LTC-Z","LTC-B","FC"]

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 1.5
    PlotConf["BackMarker"] = '.'
    PlotConf["BackLineWidth"] = 0.75

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    for Label in PlotConf["Legend"]:
        if Label == "ENTtoGPS":
            PlotConf["xData"][Label] = CorrData[CorrIdx["SOD"]][FilterCond] / GnssConstants.S_IN_H
            PlotConf["yData"][Label] = CorrData[CorrIdx[Label]][FilterCond]
        else:
            PlotConf["xData"][Label] = SatData[SatIdx["SOD"]] / GnssConstants.S_IN_H
            PlotConf["yData"][Label] = SatData[SatIdx[Label]]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot ENT-GPS Offset
def plotEntGps(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "ENT - GPS Offset", "ENT_GPS_OFFSET_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "ENT-GPS Offset [m]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.75

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["SOD"]][FilterCond] / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = CorrData[CorrIdx["ENTtoGPS"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma FLT
def plotSigmaFlt(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Sigma FLT", "SIGMA_FLT_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Sigma FLT [m]"

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,100,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["SFLT"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot UIVD
def plotUivd(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "UIVD", "UIVD_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "UIVD [m]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Processing data to be plotted
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Sod = CorrData[CorrIdx["SOD"]][FilterCond].to_numpy()
    Elev = CorrData[CorrIdx["ELEV"]][FilterCond].to_numpy()
    Uisd = CorrData[CorrIdx["UISD"]][FilterCond].to_numpy()
    Uivd = np.zeros(len(Sod))
    
    for index in range(len(Uivd)):
        Uivd[index] = Uisd[index]/Iono.computeIonoMappingFunction(Elev[index])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = Sod / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = Uivd
    PlotConf["zData"][Label] = Elev

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot UISD
def plotUisd(CorrFile, CorrData, RcvrInfo):

    # Graph settings definition
    PlotConf = {}
    initPlotB(CorrFile, PlotConf, "UISD", "UISD_at_IPP")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (16.8,15.2)

    RcvrLon, RcvrLat = roundRcvr(RcvrInfo)
    PlotConf["LonMin"] = (RcvrLon - 25)
    PlotConf["LonMax"] = (RcvrLon + 25)
    PlotConf["LatMin"] = (RcvrLat - 15)
    PlotConf["LatMax"] = (RcvrLat + 15) if RcvrLat < 75 else 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yTicks"] = range(PlotConf["LatMin"],PlotConf["LatMax"]+1,10)
    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]

    PlotConf["xTicks"] = range(PlotConf["LonMin"],PlotConf["LonMax"]+1,15)
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True
    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "UISD [m]"
    PlotConf["ColorBarMax"] = int(max(CorrData[CorrIdx["UISD"]])) + 1
    PlotConf["ColorBarMin"] = int(min(CorrData[CorrIdx["UISD"]]))
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["IPPLON"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["IPPLAT"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["UISD"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma UIRE
def plotSigmaUire(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Sigma UIRE", "SIGMA_UIRE_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Sigma UIRE [m]"

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,100,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["SUIRE"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot STD
def plotStd(CorrFile, CorrData, RcvrInfo):

    # Graph settings definition
    PlotConf = {}
    initPlotB(CorrFile, PlotConf, "STD", "STD_at_RCVR")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (16.8,15.2)

    RcvrLon, RcvrLat = roundRcvr(RcvrInfo)
    PlotConf["LonMin"] = (RcvrLon - 25)
    PlotConf["LonMax"] = (RcvrLon + 25)
    PlotConf["LatMin"] = (RcvrLat - 15)
    PlotConf["LatMax"] = (RcvrLat + 15) if RcvrLat < 75 else 90
    PlotConf["LonStep"] = 5
    PlotConf["LatStep"] = 5

    PlotConf["yTicks"] = range(PlotConf["LatMin"],PlotConf["LatMax"]+1,10)
    PlotConf["yLim"] = [PlotConf["LatMin"], PlotConf["LatMax"]]

    PlotConf["xTicks"] = range(PlotConf["LonMin"],PlotConf["LonMax"]+1,15)
    PlotConf["xLim"] = [PlotConf["LonMin"], PlotConf["LonMax"]]

    PlotConf["Grid"] = True
    PlotConf["Map"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "STD [m]"
    PlotConf["ColorBarMax"] = int(max(CorrData[CorrIdx["STD"]])) + 1
    PlotConf["ColorBarMin"] = int(min(CorrData[CorrIdx["STD"]]))
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["IPPLON"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["IPPLAT"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["STD"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma TROPO
def plotSigmaTropo(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Sigma TROPO", "SIGMA_TROPO_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Sigma TROPO [m]"

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,100,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["STROPO"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma Multipath
def plotSigmaMulti(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Sigma Multipath", "SIGMA_MULTI_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Sigma Multipath [m]"

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,100,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["SMP"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma Noise + Divergence
def plotSigmaNoise(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Sigma Noise + Divergence", "SIGMA_NOISE_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Sigma Noise + Divergence [m]"

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,100,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["SNOISEDIV"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma Airborne
def plotSigmaAir(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Sigma Airborne", "SIGMA_AIR_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Sigma Airborne [m]"

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,100,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["SAIR"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma UERE
def plotSigmaUere(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Sigma UERE", "SIGMA_UERE_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Sigma UERE [m]"

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,100,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["ELEV"]][FilterCond]
    PlotConf["yData"][Label] = CorrData[CorrIdx["SUERE"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Receiver Clock
def plotRcvrClock(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Receiver Clock", "RCVR_CLOCK_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Receiver Clock [m]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.75

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["SOD"]][FilterCond] / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = CorrData[CorrIdx["RCVR-CLK"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Pseudo-Range Residuals
def plotRes(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlot(CorrFile, PlotConf, "Pseudo-Range Residuals", "RES_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Pseudo-Range Residuals [m]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = True

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.75

    # Colorbar definition
    PrnList = sorted(unique(CorrData[CorrIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    FilterCond = CorrData[CorrIdx["FLAG"]] == 1
    Label = 0
    PlotConf["xData"][Label] = CorrData[CorrIdx["SOD"]][FilterCond] / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = CorrData[CorrIdx["PSR-RES"]][FilterCond]
    PlotConf["zData"][Label] = CorrData[CorrIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Sigma UERE Statistics
def plotSigmaUereStats(CorrFile, CorrData):

    # Graph settings definition
    PlotConf = {}
    initPlotB(CorrFile, PlotConf, "Sigma UERE Statistics", "SIGMA_UERE_STATS")

    PlotConf["Type"] = "Bars"
    PlotConf["FigSize"] = (14.4,8.4)

    PlotConf["yLabel"] = "Sigma UERE [m]"
    
    PlotConf["xLim"] = [0.5,32.5]

    PlotConf["Grid"] = True
    PlotConf["Legend"] = ["Max", "95%", "RMS", "Min"]

    PlotConf["BarWidth"] = 0.5

    # Prepare data to be plotted
    MaxUere = []
    MinUere = []
    RMSUere = []
    ConUere = []

    FilterCond1 = CorrData[CorrIdx["FLAG"]] == 1
    # Loop over all satellites
    for Prn in range(1,33,1):
        FilterCond2 = CorrData[CorrIdx["PRN"]] == Prn
        SigmaUereSat = CorrData[CorrIdx["SUERE"]][FilterCond2][FilterCond1].to_numpy()
        # Check if the satellite is in view
        if len(SigmaUereSat) > 0:
            # Compute maximum Sigma UERE
            MaxUere.append(max(SigmaUereSat))
            # Compute minimum sigma UERE
            MinUere.append(min(SigmaUereSat))
            # Compute RMS 
            NSigma = 0
            for Sigma in SigmaUereSat:
                NSigma = NSigma + Sigma**2
            RMSUere.append(sqrt(NSigma/len(SigmaUereSat)))
            # Compute 95% confidence interval for Sigma UERE
            ConfInter = np.percentile(SigmaUereSat, 95)
            ConUere.append(ConfInter)
        else:
            MaxUere.append(0.0)
            MinUere.append(0.0)
            RMSUere.append(0.0)
            ConUere.append(0.0)

    PlotData = OrderedDict({})
    PlotData["Max"] = np.around(MaxUere, decimals = 2)
    PlotData["Min"] = np.around(MinUere, decimals = 2)
    PlotData["RMS"] = np.around(RMSUere, decimals = 2)
    PlotData["95%"] = np.around(ConUere, decimals = 2)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    Labels = ["Max", "95%", "RMS", "Min"]
    for Label in Labels:
        PlotConf["xData"][Label] = np.arange(1,33,1)
        PlotConf["yData"][Label] = PlotData[Label]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def generateCorrPlots(CorrFile, SatFile, RcvrInfo):
    
    # Purpose: generate output plots regarding Preprocessing results

    # Parameters
    # ==========
    # CorrFile: str
    #           Path to CORR output file
    # SatFile: str
    #          Path to SAT input file
    # RcvrInfo: List
    #           List containing information on the receiver

    # Returns
    # =======
    # Nothing
    
    # Monitored Satellite Tracks
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SAT_TRACKS"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["SAT-X"],CorrIdx["SAT-Y"],CorrIdx["SAT-Z"],CorrIdx["ELEV"],CorrIdx["FLAG"]])

        print( 'Plot Monitored Satellites Tracks vs Time ...')
      
        # Configure plot and call plot generation function
        plotSatTracks(CorrFile, CorrData, RcvrInfo)

    # LTC Corrections
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_LTC"] == 1):
        # Read the cols we need from SatFile file
        SatData = read_csv(SatFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[SatIdx["SOD"],SatIdx["LTC-X"],SatIdx["LTC-Y"],SatIdx["LTC-Z"],SatIdx["LTC-B"],SatIdx["FC"]])

        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["SOD"],CorrIdx["ENTtoGPS"],CorrIdx["FLAG"]])

        print( 'Plot LTC corrections vs Time ...')
      
        # Configure plot and call plot generation function
        plotLtcCorr(CorrFile, CorrData, SatData)

    # ENT-GPS Offset
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_ENT_GPS"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["SOD"],CorrIdx["ENTtoGPS"],CorrIdx["FLAG"]])

        print( 'Plot ENT-GPS Offset vs Time ...')
      
        # Configure plot and call plot generation function
        plotEntGps(CorrFile, CorrData)

    # Sigma FLT
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_FLT"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["ELEV"],CorrIdx["SFLT"],CorrIdx["FLAG"]])

        print( 'Plot Sigma FLT vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotSigmaFlt(CorrFile, CorrData)

    # UIVD
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_UIVD"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["SOD"],CorrIdx["ELEV"],CorrIdx["UISD"],CorrIdx["FLAG"]])

        print( 'Plot UIVD vs Time ...')
      
        # Configure plot and call plot generation function
        plotUivd(CorrFile, CorrData)

    # UISD
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_UISD"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["IPPLON"],CorrIdx["IPPLAT"],CorrIdx["UISD"],CorrIdx["FLAG"]])

        print( 'Plot UISD vs Time ...')
      
        # Configure plot and call plot generation function
        plotUisd(CorrFile, CorrData, RcvrInfo)

    # Sigma UIRE
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_UIRE"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["ELEV"],CorrIdx["SUIRE"],CorrIdx["FLAG"]])

        print( 'Plot Sigma UIRE vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotSigmaUire(CorrFile, CorrData)

    # STD
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_STD"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["IPPLON"],CorrIdx["IPPLAT"],CorrIdx["STD"],CorrIdx["FLAG"]])

        print( 'Plot STD vs Time ...')
      
        # Configure plot and call plot generation function
        plotStd(CorrFile, CorrData, RcvrInfo)
    
    # Sigma TROPO
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_TROPO"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["ELEV"],CorrIdx["STROPO"],CorrIdx["FLAG"]])

        print( 'Plot Sigma TROPO vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotSigmaTropo(CorrFile, CorrData)
    
    # Sigma Multipath
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_MULTI"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["ELEV"],CorrIdx["SMP"],CorrIdx["FLAG"]])

        print( 'Plot Sigma Multipath vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotSigmaMulti(CorrFile, CorrData)
    
    # Sigma Noise + Divergence
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_NOISE"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["ELEV"],CorrIdx["SNOISEDIV"],CorrIdx["FLAG"]])

        print( 'Plot Sigma Noise + Divergence vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotSigmaNoise(CorrFile, CorrData)
    
    # Sigma AIR
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_AIR"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["ELEV"],CorrIdx["SAIR"],CorrIdx["FLAG"]])

        print( 'Plot Sigma Airborne vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotSigmaAir(CorrFile, CorrData)
    
    # Sigma UERE
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_UERE"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["ELEV"],CorrIdx["SUERE"],CorrIdx["FLAG"]])

        print( 'Plot Sigma UERE vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotSigmaUere(CorrFile, CorrData)
    
    # Receiver Clock
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_RCVR_CLK"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["SOD"],CorrIdx["RCVR-CLK"],CorrIdx["FLAG"]])

        print( 'Plot Receiver Clock vs Time ...')
      
        # Configure plot and call plot generation function
        plotRcvrClock(CorrFile, CorrData)
    
    # Residuals
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_RES"] == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["SOD"],CorrIdx["PRN"],CorrIdx["PSR-RES"],CorrIdx["FLAG"]])

        print( 'Plot Pseudo-Range Residuals vs Time ...')
      
        # Configure plot and call plot generation function
        plotRes(CorrFile, CorrData)
    
    # Sigma UERE Statistics
    # ----------------------------------------------------------
    if(ConfCorr["PLOT_SIGMA_UERE_STATS"]  == 1):
        # Read the cols we need from CorrFile file
        CorrData = read_csv(CorrFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[CorrIdx["PRN"],CorrIdx["SUERE"],CorrIdx["FLAG"]])

        print( 'Plot Sigma UERE Statistics ...')
      
        # Configure plot and call plot generation function
        plotSigmaUereStats(CorrFile, CorrData)