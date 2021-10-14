#!/usr/bin/env python

########################################################################
# PETRUS/SRC/PerfPlots.py:
# This is the PerfPlots Module of PETRUS tool
#
# Project:        PETRUS
# File:           PerfPlots.py
# Date(YY/MM/DD): 05/02/21
#
# Author: GNSS Academy
# Copyright 2021 GNSS Academy
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#
########################################################################

import sys, os
from pandas import read_csv
from InputOutput import PosIdx
sys.path.append(os.getcwd() + '/' + \
    os.path.dirname(sys.argv[0]) + '/' + 'COMMON')
from COMMON import GnssConstants
from COMMON.Plots import generatePlot
from InputOutput import HistIdx
from ConPlots import ConfPerf
import numpy as np

def initPlot(PerfFile, PlotConf, Title, Label):
    
    # Compute information from PerfFile
    PerfFileName = os.path.basename(PerfFile)
    PerfFileNameSplit = PerfFileName.split('_')
    Rcvr = PerfFileNameSplit[1]
    DatepDat = PerfFileNameSplit[2]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    # Dump information into PlotConf
    PlotConf["Title"] = "%s on Year %s DoY %s" % (Title, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/PERF/Figures/%s/' % Label + '%s_Y%sD%s.png' % (Label, Year, Doy)

def initHist(HistFile, PlotConf, Title, Label):
    
    # Compute information from HistFile
    HistFileName = os.path.basename(HistFile)
    HistFileNameSplit = HistFileName.split('_')
    Rcvr = HistFileNameSplit[1]
    DatepDat = HistFileNameSplit[2]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    # Dump information into PlotConf
    PlotConf["xLabel"] = "LPV200 VPE Histogram"

    PlotConf["Title"] = "%s %s on Year %s DoY %s" % (Rcvr, Title, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/PERF/Figures/%s/' % Label + '%s_%s_Y%sD%s.png' % (Label, Rcvr, Year, Doy)

# Plot LPV200 VPE Histogram
def plotVpeHistogram(HistFile, HistData):

    # Graph settings definition
    PlotConf = {}
    initHist(HistFile, PlotConf, "LPV200 VPE Histogram", "LPV200_VPE_HISTOGRAM")

    PlotConf["Type"] = "Hist"
    PlotConf["FigSize"] = (14.4,8.4)

    PlotConf["yLabel"] = "Relative Frequency PDF"

    PlotConf["Grid"] = True
    PlotConf["Legend"] = ["Max: " + str(max(sorted(HistData[HistIdx["BINMIN"]])))]

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    Label = 0
    PlotConf["xData"][Label] = HistData[HistIdx["BINMIN"]]
    PlotConf["yData"][Label] = HistData[HistIdx["BINFREQ"]]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def generateHistPlot(HistFile):
    
    # Purpose: generate LPV200 VPE plots regarding performances results

    # Parameters
    # ==========
    # HistFile: str
    #           Path to LPV200 VPE Histogram output file

    # Returns
    # =======
    # Nothing

    if(ConfPerf["PLOT_VPE_HISTOGRAM"] == 1):
        # Read the cols we need from HistFile file
        HistData = read_csv(HistFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[HistIdx["BINMIN"],HistIdx["BINFREQ"]])

        print( 'Plot LPV200 VPE Histogram ...')
      
        # Configure plot and call plot generation function
        plotVpeHistogram(HistFile, HistData)

