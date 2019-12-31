"""
:tooltip:
Module for Rename Elements Engine
rename stuff, rename portions of view, sheet, or room names
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork Design Technology West

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit
"""

# pyRevit metadata variables
__title__ = "Rename Elements Engine"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "find new"
__parameters__ = []

# standard modules
import clr # noqa E402
import math # noqa E402
import os # noqa E402
import re # noqa E402
import rpw # noqa E402
import sys # noqa E402
import System # noqa E402

from pyrevit import script # noqa E402

# Revit API modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402
import Autodesk.Revit.UI.Selection # noqa E402

# rename elements modules
import RenameElements_GUI as REGUI

class CollectElements:
    def __init__(self):
        # CollectViews output
        self.allViewObjs = None
        
        # CollectSheets output
        self.allSheetObjs = None
        
        # CollectRooms output
        self.allRoomObjs = None
    
    def CollectViews(self):
        self.allViewObjs = [i for i in FilteredElementCollector(self.doc).OfClass(View)
                            if self.searchString in i.Name]
        names = [i.Name for i in self.allViewObjs] # not really needed
        return(self.allViewObjs)

    def CollectSheets(self):
        self.allSheetObjs = [i for i in FilteredElementCollector(self.doc).OfClass(ViewSheet)]
        return(self.allSheetObjs)
    
    def CollectRooms(self):
        # FilteredElementCollector(self.doc).OfClass(SpatialElement)
        self.allRoomObjs = [i for i in FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Rooms) 
                            if "container" not in i.Level.Name.lower()]     
        return(self.allRoomObjs)

class RenameElements:
    def __init__(self):
        pass
    
    def RenameViews(self):
        t = Transaction(self.doc, "Renaming views")
        t.Start()
        for obj in self.allViewObjs:
            try:
                obj.Name = obj.Name.replace(self.searchString, self.targetString)
            except: pass
        t.Commit()
    
    def RenameSheets(self):
        t = Transaction(self.doc, "Renaming sheets")
        t.Start()
        for obj in self.allSheetObjs:
            try:
                newNumber = obj.get_Parameter(BuiltInParameter.SHEET_NUMBER).Set(obj.SheetNumber.Replace(self.searchString, self.targetString))
                print(newNumber)
            except: pass
        t.Commit()
    
    def RenameRooms(self):
        t = Transaction(self.doc, "Renaming rooms")
        t.Start()
        for obj in self.allRoomObjs:
            try:
                obj.Name = obj.Name.replace(self.searchString, self.targetString)
            except: pass
        t.Commit()           

class DerivedClass(CollectElements, RenameElements):
    def __init__(self, searchString=None, targetString=None):
        # default input parameters, to be updated by GUI selection
        self.searchString = searchString
        self.targetString = targetString
        
        # revit doc parameters
        self.doc = __revit__.ActiveUIDocument.Document
        self.app = __revit__.Application
        self.version = __revit__.Application.VersionNumber.ToString()
        self.uidoc = __revit__.ActiveUIDocument
        self.currentView = __revit__.ActiveUIDocument.ActiveView
        
        # class inheritance / polymorphism
        CollectElements.__init__(self)
    
    def Run_RenameElements(self):
        # generate GUI
        formObj = REGUI.RE_Form()
        formObj.Run_Form()
        
        # convert default none values to string outputs based on form selection
        self.searchString = formObj.searchString
        self.targetString = formObj.targetString
        
        if formObj.viewsBoolean:
            self.CollectViews()
            self.RenameViews()
        
        if formObj.sheetsBoolean:
            self.CollectSheets()
            self.RenameSheets()