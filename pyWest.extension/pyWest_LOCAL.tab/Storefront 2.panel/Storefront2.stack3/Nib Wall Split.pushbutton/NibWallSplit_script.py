"""
Splits storefront walls that have free ends or touching
the EC model to have a typical GYP wall at the end.

"""

__author__ = 'WeWork Buildings Systems'
__version__ = "3.0"

import sys
import clr
import os

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

version = __revit__.Application.VersionNumber.ToString()
uidoc = __revit__.ActiveUIDocument
currentView = uidoc.ActiveView

sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\Storefront_2.panel\Lib\SFR_Lib")
from SF_Refactored_analysis import *


if str(currentView.ViewType) == "FloorPlan" :
    SFAnalysisTools().storefront_split_wall()
else:
    Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Run the tool in floorplan view only!")
    pyrevit.script.exit()

#__window__.Close()
