#!/usr/bin/env python

########################################################################
# PETRUS/SRC/Preprocessing.py:
# This is the Inputs (conf and input files) Module of PETRUS tool
#
#  Project:        PETRUS
#  File:           Preprocessing.py
#  Date(YY/MM/DD): 01/02/21
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
from collections import OrderedDict

# Preprocessing plots configuration flags
ConfPrepro = OrderedDict({})
ConfPrepro["PLOT_VIS"] = 0
ConfPrepro["PLOT_NSAT"] = 0
ConfPrepro["PLOT_POLAR"] = 0
ConfPrepro["PLOT_SATS_FLAGS"] = 0
ConfPrepro["PLOT_C1_C1SMOOTHED_T"] = 0
ConfPrepro["PLOT_C1_C1SMOOTHED_E"] = 0
ConfPrepro["PLOT_C1_RATE"] = 0
ConfPrepro["PLOT_L1_RATE"] = 0
ConfPrepro["PLOT_C1_RATE_STEP"] = 0
ConfPrepro["PLOT_L1_RATE_STEP"] = 0
ConfPrepro["PLOT_VTEC"] = 0
ConfPrepro["PLOT_AATR_INDEX"] = 0

# Correction plots configuration flags
ConfCorr = OrderedDict({})
ConfCorr["PLOT_SAT_TRACKS"] = 0
ConfCorr["PLOT_LTC"] = 0
ConfCorr["PLOT_ENT_GPS"] = 0
ConfCorr["PLOT_SIGMA_FLT"] = 0
ConfCorr["PLOT_UIVD"] = 0
ConfCorr["PLOT_UISD"] = 0
ConfCorr["PLOT_SIGMA_UIRE"] = 0
ConfCorr["PLOT_STD"] = 0
ConfCorr["PLOT_SIGMA_TROPO"] = 0
ConfCorr["PLOT_SIGMA_MULTI"] = 0
ConfCorr["PLOT_SIGMA_NOISE"] = 0
ConfCorr["PLOT_SIGMA_AIR"] = 0
ConfCorr["PLOT_SIGMA_UERE"] = 0
ConfCorr["PLOT_SIGMA_UERE_STAT"] = 0
ConfCorr["PLOT_RCVR_CLK"] = 0
ConfCorr["PLOT_RES"] = 0
ConfCorr["PLOT_SIGMA_UERE_STATS"] = 0

