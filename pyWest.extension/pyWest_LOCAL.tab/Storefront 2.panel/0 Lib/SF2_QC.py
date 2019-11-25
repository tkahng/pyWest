"""
:tooltip:
Module for storefront logic
TESTED REVIT API: 2015, 2016, 2017
:tooltip:

Copyright (c) 2016-2018 WeWork

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__author__ = 'WeWork Buildings Systems'
__version__ = "1.0"

import clr
import sys, traceback
import os
import sys
import logging
import System
import math
import _csv as csv
import json
import rpw


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

from pyrevit import script

user = str(System.Environment.UserName)

#sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import SF2_Utility
import SF2_Engine
import SF2_Families
import SF2_GUI

class SFCheckErrors:
    """
    Checks errors for mullions and panels
    """
    def __init__(self):
        # global parameters
        self.doc = __revit__.ActiveUIDocument.Document
        self.app = __revit__.Application
        self.version = __revit__.Application.VersionNumber.ToString()
        self.uidoc = __revit__.ActiveUIDocument
        self.currentView = self.uidoc.ActiveView
    def PointsAndErrors(self, mullions_list, errorName, cat_or_ids):
        """adds to lists of points and errors"""
        errorsToFlag = []
        compList =[]
        for m in mullions_list:
            mElem = self.doc.GetElement(m)
            if m not in compList:
                intersectingMulls = SF2_Utility.FindIntersectingMullions(mElem, cat_or_ids)
                if list(intersectingMulls):
                    mullPt = mElem.Location.Point
                    errorsToFlag.append([mullPt, errorName])
                    for mm in list(intersectingMulls):
                        compList.append(mm.Id)
        return(errorsToFlag)
    def MullionClash(self):
        errorsToFlag = []

        selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id

        allMullions = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_CurtainWallMullions, Autodesk.Revit.DB.FamilyInstance, currentView=True)
        allWalls = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)

        allWalls = SF2_Utility.FilterElementsByName(self.doc, allWalls, ["Storefront","Storefront"], True)

        errorsToFlag += self.PointsAndErrors(allMullions, "Mullion-Mullion Intersects", BuiltInCategory.OST_CurtainWallMullions)
        errorsToFlag += self.PointsAndErrors(allMullions, "Mullion-Panel Intersects", BuiltInCategory.OST_CurtainWallPanels)
        if allWalls:
            errorsToFlag += self.PointsAndErrors(allMullions, "Mullion-Wall Intersects", allWalls)
        return(errorsToFlag)

    def PanelClash(self):
        errorsToFlag = []

        allPanels = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Windows, Autodesk.Revit.DB.FamilyInstance, currentView=True)
        allPanels = SF2_Utility.FilterDemolishedElements(self.doc, allPanels)

        panelMinWidth = 0.45
        panelMaxWidth = 5.0
        panelMaxHeight = 8.14

        ### ITERATE OVER PANEL LIST ###
        for p in allPanels:
            famInst = self.doc.GetElement(p)

            pan_height = famInst.Parameter[BuiltInParameter.FAMILY_HEIGHT_PARAM].AsDouble()
            pan_width = famInst.Parameter[BuiltInParameter.FAMILY_WIDTH_PARAM].AsDouble()

            if "empty" not in famInst.Name.lower():
                if pan_width < panelMinWidth:
                    errorsToFlag.append([famInst.GetTransform().Origin, "Small Panel"])
                elif pan_width > panelMaxWidth:
                    errorsToFlag.append([famInst.GetTransform().Origin, "Wide Panel"])
                elif pan_height > panelMaxHeight:
                    errorsToFlag.append([famInst.GetTransform().Origin, "Tall Panel"])
            else:
                pass
        return(errorsToFlag)

    def ECWallClash(self):
        errorsToFlag = []
        columnsLinesEdgesEC = []
        wallsLinesEdgesEC = []


        docLoaded = SF2_Utility.RevitLoadECDocument(self.doc, quiet=True)
        if docLoaded[0]:
            docEC = docLoaded[0]
            ecTransform = docLoaded[1]

            selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id

            selectedLevelInst = self.doc.GetElement(selectedLevel)
            levelElevationEC = None 
            for p in selectedLevelInst.Parameters:
                if p.Definition.Name == "Elevation":
                    levelElevationEC = p.AsDouble()

            allWallsEC  = SF2_Utility.GetAllElements(docEC, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
            allColumnsEC = SF2_Utility.GetAllElements(docEC, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
            allColumnsEC += SF2_Utility.GetAllElements(docEC, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)

            selectedWallsEC = SF2_Utility.FilterElementsByLevel(docEC, allWallsEC, levelElevationEC)
            selectedColumnsEC = SF2_Utility.FilterElementsByLevel(docEC, allColumnsEC, levelElevationEC)

            wallsLinesEdgesEC = SF2_Utility.GetWallEdgeCurves(docEC, selectedWallsEC, ecTransform)
            columnsLinesEdgesEC = SF2_Utility.GetColumnEdgeCurves(docEC, selectedColumnsEC, ecTransform)

        allWalls = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
        storefrontWalls = SF2_Utility.FilterElementsByName(self.doc, allWalls,["Storefront","Storefront"], False)
        storefrontWalls = SF2_Utility.FilterWallsByKind(self.doc, storefrontWalls, "Basic")

        obstructionEdges = columnsLinesEdgesEC
        obstructionEdges += wallsLinesEdgesEC

        if obstructionEdges:
            for sfWallId in storefrontWalls:
                sfWall = self.doc.GetElement(sfWallId)
                locLine = sfWall.Location.Curve
                locLineStart = locLine.GetEndPoint(0)
                locLineEnd = locLine.GetEndPoint(1)

                for obstructionLine in obstructionEdges:
                    obstLineElevation = obstructionLine.GetEndPoint(0).Z
                    locLineStart = XYZ(locLineStart.X, locLineStart.Y, obstLineElevation)
                    locLineEnd = XYZ(locLineEnd.X, locLineEnd.Y, obstLineElevation)
                    locLineFlat = Line.CreateBound(locLineStart, locLineEnd)
                    intersection = SF2_Utility.RevitCurveCurveIntersection(locLineFlat,obstructionLine)

                    if intersection:
                        # ERROR: Hit Existing Condition
                        errorsToFlag.append([intersection, "Hit EC"])
        return(errorsToFlag)
    def Run_SFCheckErrors(self):
        famTypeDict = SF2_Utility.GetFamilyTypeDict("Fabrication-Error-Symbol")
    
        # Clear existing error notations
        errorNotations = list(SF2_Utility.GetElementsInView(BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, self.currentView.Id))
        errorNotations = SF2_Utility.FilterElementsByName(self.doc, errorNotations,["Fabrication","Error-Symbol"], False)
        if errorNotations:
            with rpw.db.Transaction("Place Errors"):
                for error in errorNotations:
                    self.doc.Delete(error)
                    
        allErrors = []
        allErrors += self.ECWallClash()
        allErrors += self.MullionClash()
        allErrors += self.PanelClash()
    
        errorSymbolId = famTypeDict["Fabrication-Error-Symbol"]
    
        if allErrors:
            with rpw.db.Transaction("Error Check"):
                SF2_Utility.RevitPlaceErrorsInView(self.currentView, allErrors, errorSymbolId)            