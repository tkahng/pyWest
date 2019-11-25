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

    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System.Drawing')
    from System.Windows.Forms import SaveFileDialog
    from System.Drawing import *
    from System.Drawing import Point
    from System.Windows.Forms import Application, Button, CheckBox, Form, Label
    from System.Collections.Generic import List, IEnumerable
    from System import Array
    from System import DateTime as dt

    sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
    import _csv as csv
    import json

    user = str(System.Environment.UserName)

    rpwLib = r"VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\0 Lib\revitpythonwrapper-master" # common lib folder
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 6, rpwLib))
    import rpw

    # import Rhinocommon API - C# library
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
    clr.AddReference(r"Rhino3dmIO.dll")
    import Rhino as rh
    
    import SF2_Families

    #from pyrevit import script
    class Revit2Rhino_Walls:
        def __init__(self, wallList):
            # input parameters
            self.wallList = wallList
            
            # derived parameters
            self.CL_List = []
        
        def GetWallCLEndPts(self):
            self.CL_List = [i.Location for i in self.wallList]
            print(self.CL_List)
            
            # immediatly convert pt coordinates to float values in lists of tuples
            endPts = [[(i.Curve.GetEndPoint(0).X, i.Curve.GetEndPoint(0).Y, i.Curve.GetEndPoint(0).Z),
                       (i.Curve.GetEndPoint(1).X, i.Curve.GetEndPoint(1).Y, i.Curve.GetEndPoint(1).Z)][0] for i in self.CL_List]
            print(endPts)
            
            #h = [i.LookUpParameter("Height").AsDouble for i in self.wallList]
        
        def Run_Revit2Rhino_Walls(self):
            self.GetWallCLEndPts()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())    