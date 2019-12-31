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

# pyRevit metadata variables
__title__ = "Storefront 2.0 QC"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "find a new one"
__parameters__ = []

import clr # noqa E402
import os # noqa E402
import rpw # noqa E402
import sys # noqa E402
import System # noqa E402

from pyrevit import script # noqa E402

# .net windows modules
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
from System.Windows.Forms import SaveFileDialog # noqa E402
from System.Drawing import * # noqa E402
from System.Drawing import Point # noqa E402

# Revit API modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402
import Autodesk.Revit.UI.Selection # noqa E402

# SF2 modules
import SF2_Utility as SFU # noqa E402

# global variables
user = str(System.Environment.UserName)

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
                intersectingMulls = SFU.FindIntersectingMullions(mElem, cat_or_ids)
                if list(intersectingMulls):
                    mullPt = mElem.Location.Point
                    errorsToFlag.append([mullPt, errorName])
                    for mm in list(intersectingMulls):
                        compList.append(mm.Id)
        return(errorsToFlag)
    def MullionClash(self):
        errorsToFlag = []

        selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id

        allMullions = SFU.GetAllElements(self.doc, BuiltInCategory.OST_CurtainWallMullions, Autodesk.Revit.DB.FamilyInstance, currentView=True)
        allWalls = SFU.GetAllElements(self.doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)

        allWalls = SFU.FilterElementsByName(self.doc, allWalls, ["Storefront","Storefront"], True)

        errorsToFlag += self.PointsAndErrors(allMullions, "Mullion-Mullion Intersects", BuiltInCategory.OST_CurtainWallMullions)
        errorsToFlag += self.PointsAndErrors(allMullions, "Mullion-Panel Intersects", BuiltInCategory.OST_CurtainWallPanels)
        if allWalls:
            errorsToFlag += self.PointsAndErrors(allMullions, "Mullion-Wall Intersects", allWalls)
        return(errorsToFlag)

    def PanelClash(self):
        errorsToFlag = []

        allPanels = SFU.GetAllElements(self.doc, BuiltInCategory.OST_Windows, Autodesk.Revit.DB.FamilyInstance, currentView=True)
        allPanels = SFU.FilterDemolishedElements(self.doc, allPanels)

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


        docLoaded = SFU.RevitLoadECDocument(self.doc, quiet=True)
        if docLoaded[0]:
            docEC = docLoaded[0]
            ecTransform = docLoaded[1]

            selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id

            selectedLevelInst = self.doc.GetElement(selectedLevel)
            levelElevationEC = None 
            for p in selectedLevelInst.Parameters:
                if p.Definition.Name == "Elevation":
                    levelElevationEC = p.AsDouble()

            allWallsEC  = SFU.GetAllElements(docEC, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
            allColumnsEC = SFU.GetAllElements(docEC, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
            allColumnsEC += SFU.GetAllElements(docEC, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)

            selectedWallsEC = SFU.FilterElementsByLevel(docEC, allWallsEC, levelElevationEC)
            selectedColumnsEC = SFU.FilterElementsByLevel(docEC, allColumnsEC, levelElevationEC)

            wallsLinesEdgesEC = SFU.GetWallEdgeCurves(docEC, selectedWallsEC, ecTransform)
            columnsLinesEdgesEC = SFU.GetColumnEdgeCurves(docEC, selectedColumnsEC, ecTransform)

        allWalls = SFU.GetAllElements(self.doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
        storefrontWalls = SFU.FilterElementsByName(self.doc, allWalls,["Storefront","Storefront"], False)
        storefrontWalls = SFU.FilterWallsByKind(self.doc, storefrontWalls, "Basic")

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
                    intersection = SFU.RevitCurveCurveIntersection(locLineFlat,obstructionLine)

                    if intersection:
                        # ERROR: Hit Existing Condition
                        errorsToFlag.append([intersection, "Hit EC"])
        return(errorsToFlag)
    def Run_SFCheckErrors(self):
        famTypeDict = SFU.GetFamilyTypeDict("Fabrication-Error-Symbol")
    
        # Clear existing error notations
        errorNotations = list(SFU.GetElementsInView(BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, self.currentView.Id))
        errorNotations = SFU.FilterElementsByName(self.doc, errorNotations,["Fabrication","Error-Symbol"], False)
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
                SFU.RevitPlaceErrorsInView(self.currentView, allErrors, errorSymbolId)            