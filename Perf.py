#!/usr/bin/env python

########################################################################
# PETRUS/SRC/Corrections.py:
# This is the Performances Module of PETRUS tool
#
#  Project:        PETRUS
#  File:           Corrections.py
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
import numpy as np

# Performances internal functions
#-----------------------------------------------------------------------