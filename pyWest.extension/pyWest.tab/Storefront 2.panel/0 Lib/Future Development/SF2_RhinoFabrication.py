"""
:tooltip:
Module for Fabrication Export
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork

--------------------------------------------------------
SUMMARY:
This module reconstructs storefront panels using the Rhino API

"""

__author__ = 'WeWork Buildings Systems / Design Technology West'
__version__ = "2.Pre-Alpha"

import traceback
import os
import sys

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    import clr
    import re # for level number string parsing
    import logging
    import System
    import math

    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
    from Autodesk.Revit.UI import *
    from Autodesk.Revit.DB import *
    import Autodesk.Revit.UI.Selection

    user = str(System.Environment.UserName)

    # import Rhinocommon API - C# library
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
    clr.AddReference(r"Rhino3dmIO.dll")
    import Rhino as rh
    
    import SF2_Families
    import SF2_Report
    import SF2_GUI 
    import SF2_Utility

class StorefrontPanel:
    def __init__(self, centerLine, door=False):
        self.centerLine = centerLine # should this be just endpoints from segment or curve?