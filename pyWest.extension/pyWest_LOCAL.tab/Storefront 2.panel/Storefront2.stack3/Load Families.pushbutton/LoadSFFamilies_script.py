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

import traceback
import os

try:
    import clr
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
    
    doc = __revit__.ActiveUIDocument.Document
    app = __revit__.Application
    version = __revit__.Application.VersionNumber.ToString()
    uidoc = __revit__.ActiveUIDocument
    currentView = uidoc.ActiveView
    
    user = str(System.Environment.UserName)
    
    sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\pyWestExtensions\pyWest.extension\pyWest.tab\Storefront 2.panel\0 Lib")
    import SF2_GUI
    import SF2_Utility
    
    # THIS WAS ORIGINALL IN storefront_engine
    # TREAT THIS AS YOU WOULD ENGINE, JUST CALL GUI, WHICH WILL EVENTUALLY TALK TO THE FAMILY MODULE
    def storefront_load():
        """
        Creates curtain wall types and loads families.
        """
        # SF2 instantiate gui object
        storefrontConfig = SF2_GUI.Form(doc)        
        
        # SF2 run gui
        storefrontConfig.Run_Form(printTest=False)
    
        # grab outputs from windows form
        currentConfig = storefrontConfig.currentConfig
        selectedSystem = currentConfig["currentSystem"]
        
        #Load the necessary families - THIS LOADS FAMILIES, BUT NOT THE FAMILIES I THOUGHT
        print("LOADING FAMILIES...")
        familiesToLoad = os.listdir(storefrontConfig.familyDirectory)
        SF2_Utility.LoadFamilies(familiesToLoad, storefrontConfig.familyDirectory)        
        
        #Gather dictionaries of what exists in the project
        profileDict = SF2_Utility.GetProfileDict("I-Profile-Storefront-Mullion")
        wallTypeDict = SF2_Utility.GetWallTypeDict()
        mullionDict = SF2_Utility.GetMullionTypeDict()
        panelTypeDict = SF2_Utility.GetWindowTypeDict()
        quadMullionDict = SF2_Utility.GetQuadMullionTypeDict()
        createMullions = {}
    
        #-----------------------CREATE MULLION TYPES------------------------#
    
        #mulliontypes that will be duplicated and assigned correct profiles
        templateMullion = None
        templateQuadMullion = None
    
        if quadMullionDict.keys() and mullionDict.keys():
            print("LOADING CURTAIN WALLS...")
            #creates mullions that are needed, both rectangular and quad.
            with rpw.db.Transaction("Create Curtain Wall"):
    
                mullionTypeNames = mullionDict.keys()
                #Creates Rectangualr Mullions
                for profileName in profileDict.keys():
    
                    #Ensure you're only creating mullion types for the selected system
                    if selectedSystem.lower() == profileName.split("_")[0].lower():
    
                        #Create a new mullion type if needed from a duplicate.
                        if not any(profileName == s for s in mullionTypeNames):
                            newMullionType = doc.GetElement(mullionDict[mullionDict.keys()[0]]).Duplicate(profileName)
                            newMullionType.get_Parameter(BuiltInParameter.MULLION_PROFILE).Set(profileDict[profileName])
                            mullionDict[profileName] = newMullionType.Id
    
                        #Otherwise grab it from the mullion dictionary if it exists.
                        else:
                            newMullionType = doc.GetElement(mullionDict[profileName])
    
                        #Set Special parameters for Mullion Types like: Offsets
                        #Default
                        mullionOffset = 0
    
                        if "MODE" in profileName:
                            if "Offset" in profileName:
                                #set the mulliontype offset to 31mm
                                mullionOffset = 0.101706
                            elif "DoorFrameMid" in profileName:
                                #set the mulliontype offset to 18.5mm
                                mullionOffset = 0.06069554
    
                        newMullionType.get_Parameter(BuiltInParameter.MULLION_OFFSET).Set(mullionOffset)
    
    
                #Creates Quad Corner Mullion
                quadMullionTypeNames = quadMullionDict.keys()
                for profileName in profileDict.keys():
    
                    #Ensure you're only creating mullion types for the selected system
                    if selectedSystem.lower() == profileName.split("_")[0].lower():
    
                        #Any profile that ends with "_Post" will be used for the corner.
                        if "post" in profileName.split("_")[1].lower():
                            if not any(profileName == s for s in quadMullionTypeNames):
                                newMullionType = doc.GetElement(quadMullionDict[quadMullionDict.keys()[0]]).Duplicate(profileName)
                                depth1 = 0
                                depth2 = 0
    
                                for p in doc.GetElement(profileDict[profileName]).Parameters:
                                    if p.Definition.Name == "x1":
                                        depth1 += p.AsDouble()
                                    if p.Definition.Name == "x2":
                                        depth1 += p.AsDouble()
                                    if p.Definition.Name == "y1":
                                        depth2 += p.AsDouble()
                                    if p.Definition.Name == "y2":
                                        depth2 += p.AsDouble()
                                for p in newMullionType.Parameters:
                                    if p.Definition.Name == "Depth 1":
                                        p.Set(depth1)
                                    if p.Definition.Name == "Depth 2":
                                        p.Set(depth2)
                                quadMullionDict[profileName] = newMullionType.Id
    
                #-----------------------CREATE CURTAIN WALL TYPES------------------------#
                # Create curtain wall system for each system if they dont exist
                templateCurtainWall = None
                for key, value in wallTypeDict.items():
                    wallType = doc.GetElement(value)
                    if str(wallType.Kind) == "Curtain":
                        templateCurtainWall = wallType
                        break
    
                curtainWallNamePrefix = "I-Storefront-"
    
                cwName = selectedSystem
                curtainWallType = curtainWallNamePrefix+cwName
                if not any( curtainWallType == s for s in wallTypeDict.keys()):
                    newCurtainWall = templateCurtainWall.Duplicate(curtainWallType)
                else:
                    newCurtainWall = doc.GetElement(wallTypeDict[curtainWallType])
                
                newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_VERT"]])
                newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER1_VERT"]])
                newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER2_VERT"]])
                newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_HORIZ"]])
                newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER1_HORIZ"]])
                newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER2_HORIZ"]])
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_PANEL_WALL).Set(panelTypeDict[currentConfig["AUTO_PANEL_WALL"]])
                except:
                    pass                
                newCurtainWall.get_Parameter(BuiltInParameter.AUTO_JOIN_CONDITION_WALL).Set(currentConfig["AUTO_JOIN_CONDITION_WALL"]) # vertical continuous
                newCurtainWall.get_Parameter(BuiltInParameter.ALLOW_AUTO_EMBED).Set(currentConfig["ALLOW_AUTO_EMBED"])
                newCurtainWall.get_Parameter(BuiltInParameter.FUNCTION_PARAM).Set(currentConfig["FUNCTION_PARAM"])
                newCurtainWall.get_Parameter(BuiltInParameter.SPACING_LAYOUT_HORIZ).Set(currentConfig["SPACING_LAYOUT_HORIZ"])
                newCurtainWall.get_Parameter(BuiltInParameter.SPACING_LAYOUT_VERT).Set(currentConfig["SPACING_LAYOUT_VERT"])
            print("...CURTAIN WALLS LOADED")
        
        else:
            """
            THIS WHOLE PART NEEDS TO BE FIXED. CREATE NEW TYPE WHERE FAMILY TYPE DOES NOT EXIST
            """
            if not quadMullionDict.keys() or not mullionDict.keys():
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Please check the 'Curtain Wall Mullions' in the Project Browser and ensure you have at least (1) Quad Mullion type & (1) Rectangular Mullion type. Right click on them to create a 'New Type' if needed.")
                sys.exit()  
        
        
    
    def Main():
        storefront_load()
        
    if __name__ == "__main__":
        Main()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())