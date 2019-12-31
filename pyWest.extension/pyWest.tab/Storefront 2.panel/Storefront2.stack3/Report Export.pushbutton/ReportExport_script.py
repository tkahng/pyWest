"""
Creates storefront reports
"""

__author__ = 'WeWork Product Development'
__version__ = "3.0"

import sys
import clr
import os
import csv

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, IFailuresPreprocessor, BuiltInFailures, UV

uidoc = __revit__.ActiveUIDocument
version = __revit__.Application.VersionNumber.ToString()
currentView = uidoc.ActiveView

sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\Storefront_2.panel\Lib\SFR_Lib")
from SF_Refactored_analysis import *

SFAnalysisTools().storefront_report()