"""
:tooltip:
Module for Storefront 2.0 Families
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork Design Technology West

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit
"""

# pyRevit metadata variables
__title__ = "Storefront 2.0 Families"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "ff31abef-b22a-4886-b819-6928a40cba46"
__parameters__ = []

# standard modules
import json # noqa E402
import sys # noqa E402
import os # noqa E402
import System # noqa E402

from System import DateTime as dt # noqa E402

# Revit API modules
import clr # noqa E402
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402
import tempfile # noqa E402
import rpw # noqa E402

# DT West modules
import SF2_Utility as SFU # noqa E402
     
###################################        
## LOAD FAMILIES DEPENDENT CLASS ##
###################################
class FamilyOptions(IFamilyLoadOptions):
    """
    IFamilyLoadOptions is an interface class, which acts weird
    The methods below are the methods the class contains, wrapped
    in this custom class, don't know why its like this
    """
    def __repr__(self):
        return("<class 'FamilyOptions'>")
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues = True
        familyInUse = True
        return(True)
    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        familyInUse = True
        return(True)

class WasInFamilyUtilities:
    def CheckConfigUpToDate(self):
        """
        Used to check the saved config file to the current working document
        if they dont match then it promps you to set the config properly for
        the current document.
        
        CHECKS WHETHER FAMILIES ARE LOADED INTO THE DOC OR NOT
        """
        # Save when the config was set.
        projectInfo = self.doc.ProjectInformation
        projectId = projectInfo.Id.IntegerValue
        projectName = None
        for p in projectInfo.Parameters:
            if p.Definition.Name == "Project Name":
                projectName = p.AsString()

        todaysDate = ("{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year))

        configProjectName = self.currentConfig["projectName"]
        configProjectId = self.currentConfig["projectId"]
        configDate = self.currentConfig["configDate"]
        
        # a nested conditional format is used here if (set of conditions) or (set of conditions)
        if ((projectName != configProjectName or projectId != configProjectId)
            or (projectId == configProjectId and todaysDate != configDate)):
            self.storefront_set_config()
        else:
            self.SFLoadFamilies(True)

class GUICalledClass:
    def __init__(self):
        # selection options used by SF_GUI
        self.GUI_SF_systemOptions = {"Elite": "Elite",
                                     "Elite - Lower Infill": "Elite - Lower Infill",
                                     "Elite - LATAM": "Elite - LATAM",
                                     "JEB": "JEB",
                                     "Extravega": "Extravega",
                                     "MODE": "MODE"
                                     }
                                
        self.GUI_SF_heightOptions = {"Elite : 7' - 1.75\"": 7 + (1.75/12),
                                     "Elite : 8' - 1.75\"": 8 + (1.75/12),
                                     "Elite : 2500mm (LATAM)" : 98.4252/12,
                                     "JEB : 2440mm - (2520mm BO Head)" : 99.2126/12,
                                     "Extravega : 2514mm - (2514mm Head) " : 98.38583/12,
                                     "MODE : 8' - 0\"" : 8.0,
                                     "Custom": "Custom" # use this to trigger custom value, or if number imput on height use that, override anything else
                                     } # Extravega has a 15mm tolerance
                            
        self.GUI_SF_divisionOptions = {"Fixed Distance": 1,
                                       "Even - Even": 0}
                                
        self.GUI_SF_panelWidthOptions = {"1000mm": 39.3701/12,
                                         "1200mm": 47.24409/12,
                                         "1375mm": 54.13386/12,
                                         "4'- 0\" (use this)": 4 + (1.75/12),
                                         "4'- 6\"": 4 + (7.75/12)
                                         }
        
        self.GUI_nibWallOptions = {"Basic Wall - Partition-Gyp": "Basic Wall - Partition-Gyp",
                                   "Basic Wall - Partition-Gyp2": "Basic Wall - Partition-Gyp2"
                                   }
        
        self.GUI_nibWallLengthOptions = {"Fixed - 6 Inches": 6.0/12,
                                         "Fixed - 12 Inches": 12.0/12,
                                         "Fixed - 150mm": 5.90551/12, 
                                         "Fixed - 300mm": 11.811/12, 
                                         "Optimized - variable": "OPTIMIZED"
                                         }              
    def CheckFamilyDict(self, checkDict, quickLoad=False):
        """
        Checks the dictionary against the document and determines if it already was loaded.
        """
        try:
            for famName, symbolAndTypes in checkDict.items():
                famFound = False
                for familyId in SFU.GetAllElements(self.doc, None, Autodesk.Revit.DB.Family):
                    family = self.doc.GetElement(familyId)
                    if famName.lower() in family.Name.lower():
                        famFound = True
                        if not quickLoad:
                            print("FAMILY: {0}...ALREADY LOADED".format(family.Name))
                        
                        # update dictionary immediatly after creating it here
                        checkDict.update(self.BuildFamilySymbol_Type_Dicts(family))
                        break
                if not famFound:
                    checkDict.update({famName: {"Symbol": None, "Types": {}}})
            return checkDict
        except Exception as inst:
            print(inst)    
    def SFLoadFamilies(self, _quickLoad):
        """ 
        THIS IS NOT ACTUALLY LOADING FAMILIES....FIGURE OUT WHAT EXACTLY IS GOING ON 
        
        Fails if correct type(symbol) does not exist in family.
        This only applies to mullions.
        
        STILL DON'T KNOW IF THIS IS DUPLICATE WORK...
        """
        familyDict = self.familiesToLoadDict
        print(self.familiesToLoadDict)
        #check if families are already loaded
        familyDict.update(self.CheckFamilyDict(familyDict, quickLoad=_quickLoad))

        # load families 
        for symbolAndTypes in familyDict.values():
            if not symbolAndTypes["Symbol"]:
                try:
                    t = Transaction(self.doc, "Load Families")
                    t.Start()
                    for famName, symbolAndTypes in familyDict.items():
                        if not symbolAndTypes["Symbol"]:
                            
                            ###################################
                            ## LOADING FAMILIES HAPPENS HERE ##
                            ###################################
                            
                            path = "{0}\{1}.rfa".format(self.familyDirectory, famName)
                            familyLoaded = clr.Reference[Autodesk.Revit.DB.Family]()
                            print("familyLoaded is {0}".format(familyLoaded))
                            loaded = self.doc.LoadFamily(path, familyLoaded)
                            
                            ##################################
                            ## IF FAMILY ALREADY IN THE DOC ##
                            ##################################
                            
                            if loaded:
                                print("FAMILY: {0}...LOADED".format(familyLoaded.Name))

                                familyLoadedSymbols = list(familyLoaded.GetFamilySymbolIds())
                                if familyLoadedSymbols:
                                    for symbolId in familyLoadedSymbols:
                                        symbol = self.doc.GetElement(symbolId)
                                        if not symbol.IsActive:
                                            symbol.Activate()
                                else:
                                    if not familyLoaded.Symbol.IsActive:
                                        familyLoaded.Symbol.Activate()  
                    t.Commit()
                
                except Exception as inst:
                    print("...PROBLEM LOADING FAMILIES")
                    print(inst)
                    t.RollBack()
                    
        familyDict.update(self.CheckFamilyDict(familyDict, quickLoad=_quickLoad))
        self.currentConfig["families"] = familyDict
        
        ###############################################
        ## MAYBE THIS CAN BE SELF.FAMILIESTOLOADDICT ##
        ###############################################
        
        return(familyDict)

##############################
## BASE CLASS A | UTILITIES ##
##############################
class FamilyUtilities:
    def __init__(self):
        pass
    def __repr__(self):
        return("<class 'FamilyUtilities'>")
    #
    # formerly called FamilySymbolAndTypesFromFamily()
    def BuildFamilySymbol_Type_Dicts(self, familyLoaded):
        """
        Takes a family and builds a dictionary of its symbol and types.
        """
        try:
            familySymbolIds = list(familyLoaded.GetFamilySymbolIds())
            familySymbolObj = self.doc.GetElement(familySymbolIds[0])
            familySymbolName = familySymbolObj.Family.Name
            if not familySymbolObj.IsActive:
                    familySymbolObj.Activate()

            # template dict
            returnDict = {familySymbolName: {"Symbol": None, "Types": {}}}

            # set family symbol
            returnDict[familySymbolName]["Symbol"] = familySymbolObj.Id.IntegerValue
            # load types if they exist into the dict
            if len(familySymbolIds)>1:
                for symbolId in familySymbolIds:
                    symbol = self.doc.GetElement(symbolId)
                    symbolName = symbol.LookupParameter("Type Name").AsString()
                    # dict.update(key:value)
                    returnDict[familySymbolName]["Types"].update({symbolName: symbolId.IntegerValue})
            else:
                # dict.update(key:value)
                returnDict[familySymbolName]["Types"].update({familySymbolName: familySymbolIds[0].IntegerValue})
            return(returnDict)
        except Exception as inst:
            SFU.OutputException(inst)
    #
    # DATA EXCHANGE
    def JSONSaveConfig(self):
        with open(self.defaultConfigPath, 'w') as outfile:
            json.dump(self.currentConfig, outfile)    
    def JSONLoadConfig(self):
        if os.path.exists(self.defaultConfigPath):
            with open(self.defaultConfigPath) as readFile:
                jsonstring = readFile.read()
        else: 
            with open(os.path.dirname(__file__) + "\\default_settings.json") as readFile:
                jsonstring = readFile.read()

        jsonstring = jsonstring.replace("null", "0", 100)
        jsonData = json.loads(jsonstring)
        self.currentConfig.update(jsonData)      

#####################################################
## BASE CLASS B | READ/WRITE FAMILY CONFIGURATIONS ##
#####################################################
class SetSFConfiguration:
    def __init__(self):
        # family setting parameters
        self.defaultConfigPath = os.path.join(tempfile.gettempdir(), "storefront_default_config.json")
        
        # derived parameters
        self.systemName = None # to be set by Run_SaveSFConfigurations()
        self.userConfigs = None # to be set by Run_SaveSFConfigurations()
        
        # types will be {type: symbolId}, symbol:symbolId} - LOOK INTO THIS
        """
        Revit API Family Types vs. Family Symbols | WHAT THE FUCK?
            SOMETHING
        """
        self.familiesToLoadDict = {"I-Profile-Storefront-Mullion" : {"Symbol": None, "Types": {}},
                                   "Empty Panel" : {"Symbol": None, "Types": {}},
                                   "Solid Center Panel" : {"Symbol": None, "Types": {}},
                                   "Glazed Center Panel" : {"Symbol": None, "Types": {}},
                                   "Extraction-Door-Symbol" : {"Symbol": None, "Types": {}},
                                   "Extraction-Desk-Symbol" : {"Symbol": None, "Types": {}},
                                   "Fabrication-Error-Symbol" : {"Symbol": None, "Types": {}},
                                   "Panel-Symbol-Standard" : {"Symbol": None, "Types": {}},
                                   "Panel-Symbol-Custom" : {"Symbol": None, "Types": {}}
                                   }        
        
        # this blank currentConfig is referenced and modified outside module then sent back...weird address this
        # SELECTED LEVELS WILL BE FILLED IF A SINGLE VIEW IS SELECTED THAT HAPPENS TO BE A PLAN
        # WHY ISNT CURRENTSYSTEM AND SELECTEDSYSTEM THE SAME THING???
        self.currentConfig = {#selectedLevels,
                              "currentSystem":None,
                              "selectedSystem": None,
                              "postWidth":None,
                              "oneByWidth":None,
                              "headHeight":None,
                              "fullSillHeight":None,
                              "partialSillHeight":None,
                              "hasLowerInfill":None,
                              "deflectionHeadType": None,
                              "nibWallType":None,
                              "nibWallLength":None,
                              "isFramed":None,
                              "profiles":None,
                              "families": self.familiesToLoadDict
                              }
        
        self.doorDict = {"74FRU":["R",74.0/12,"SLIDER"],
                         "80R":["R",80.0/12,"SLIDER"],
                         "76R":["R",76.0/12,"SLIDER"],
                         "72R":["R",72.0/12,"SLIDER"],
                         "80L":["L",80.0/12,"SLIDER"],
                         "76L":["L",76.0/12,"SLIDER"],
                         "72L":["L",72.0/12,"SLIDER"],
                         "DB-72-S":["R",75.5/12,"SLIDER"],
                         "DB-72-CR":["R",75.5/12,"SLIDER"],
                         "DB-72-MT":["R",75.5/12,"SLIDER"],
                         "RH-80":["R",80.0/12,"SLIDER"],
                         "RH-76":["R",76.0/12,"SLIDER"],
                         "RH-72":["R",72.0/12,"SLIDER"],
                         "RH-60":["R",60.0/12,"SLIDER"],
                         "RH-36":["R",39.5/12,"SWING"],
                         "RH-36S":["R",39.5/12,"SWING"],
                         "RH-37S":["R",40.5/12,"SWING"],
                         "RH-30":["R",33.5/12,"SWING"],
                         "LH-80":["L",80.0/12,"SLIDER"],
                         "LH-76":["L",76.0/12,"SLIDER"],
                         "LH-72":["L",72.0/12,"SLIDER"],
                         "LH-60":["L",60.0/12,"SLIDER"],
                         "LH-36":["L",39.5/12,"SWING"],
                         "LH-36S":["L",39.5/12,"SWING"],
                         "LH-37S":["L",40.5/12,"SWING"],
                         "LH-30":["L",33.5/12,"SWING"],
                         "CR36R":["R",39.5/12,"SWING"],
                         "CR36L":["L",39.5/12,"SWING"],
                         "MT36R":["R",39.5/12,"SWING"],
                         "MT36L":["L",39.5/12,"SWING"],
                         "72x84":["R",75.5/12,"SWING"],
                         "36x84":["R",39.5/12,"SWING"],
                         "36x80":["R",39.5/12,"SWING"],
                         "34x80":["R",37.5/12,"SWING"],
                         "34x84":["R",37.5/12,"SWING"],
                         "32x84":["R",37.5/12,"SWING"],
                         "30x84":["R",33.5/12,"SWING"],
                         "27x80":["R",30.5/12,"SWING"],
                         "Slider 6'-0\"":["R",72.0/12,"SLIDER"],
                         "36\" x 80\"":["R",39.5/12,"SWING"],
                         "36\" x 84\"":["R",39.5/12,"SWING"],
                         "30\" x 84\"":["R",33.5/12,"SWING"],
                         "72\" x 84\"":["R",75.0/12,"SWING"],
                         "RH-1900":["R",3.362861,"SLIDER"],
                         "LH-1900":["L",3.362861,"SLIDER"],
                         "MODE-RH-2000":["R",2.98556,"SLIDER"],
                         "MODE-LH-2000":["L",2.98556,"SLIDER"],
                         "RH-875-CR":["R",33.0709/12,"SWING"],
                         "RH-875-MT":["R",33.0709/12,"SWING"],
                         "RH-875-S":["R",33.0709/12,"SWING"],
                         "LH-875-CR":["L",33.0709/12,"SWING"],
                         "LH-875-MT":["L",33.0709/12,"SWING"],
                         "LH-875-S":["L",33.0709/12,"SWING"],
                         "RH-36-CR":["R",39.5/12,"SWING"],
                         "LH-36-CR":["L",39.5/12,"SWING"],
                         "RH-36-MT":["R",39.5/12,"SWING"],
                         "LH-36-MT":["L",39.5/12,"SWING"],
                         "RH-36-S":["R",39.5/12,"SWING"],
                         "LH-36-S":["L",39.5/12,"SWING"],
                         "RH-2050":["R",6.725722,"SLIDER"],
                         "LH-2050":["L",6.725722,"SLIDER"],
                         "RH-1875":["R",6.151575,"SLIDER"],
                         "LH-1875":["L",6.151575,"SLIDER"],
                         "RH-1000-MT":["R",3.28084,"SWING"],
                         "LH-1000-MT":["L",3.28084,"SWING"],
                         "RH-1000-CR":["R",3.28084,"SWING"],
                         "LH-1000-CR":["L",3.28084,"SWING"],
                         "RH-1000-S":["R",3.28084,"SWING"],
                         "LH-1000-S":["L",3.28084,"SWING"],
                         "MODE-RH-1000-MT":["R",2.98556,"SWING"],
                         "MODE-LH-1000-MT":["L",2.98556,"SWING"],
                         "MODE-RH-1000-CR":["R",2.98556,"SWING"],
                         "MODE-LH-1000-CR":["L",2.98556,"SWING"],
                         "MODE-RH-1000-S":["R",2.98556,"SWING"],
                         "MODE-LH-1000-S":["L",2.98556,"SWING"]
                         }
    def __repr__(self):
        return("<class 'SetSFConfiguration'>")    
    #
    # STOREFRONT CONFIGURATIONS
    def EliteConfigs(self):
        # System Configurations
        self.currentConfig["currentSystem"] = "Elite"
        self.currentConfig["fullSillHeight"] = 0.0

        if "Lower Infill" in self.systemName:
            self.currentConfig["hasLowerInfill"] = True
        else:
            self.currentConfig["hasLowerInfill"] = False

        # Regional Settings
        if "LATAM" in self.systemName:

            self.currentConfig["transomHeight"] = 8.2021
            self.currentConfig["partialSillHeight"] = 2.49344 - (1.75/12)

        else:
            self.currentConfig["transomHeight"] = 8 + (1.75/12)
            self.currentConfig["partialSillHeight"] = 2 + (3.25/12)

        self.currentConfig["isFramed"] = True
        self.currentConfig["deflectionHeadType"] = 0

        # Used as a factor for detecting adjacent mullions for door frames. 
        self.currentConfig["closeMullionDetectionFactor"] = 1.0

        # To make sure that the mullion family names are correctly set.
        self.systemName = "Elite"

        # Curtain Panel Options
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"

        # Curtain Wall Settings
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.systemName + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.systemName + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.systemName + "_Intermediate"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.systemName + "_Sill"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.systemName + "_Sill"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.systemName + "_OneBy"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        # Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = self.systemName + "_Post"

        # Special conditions where wall types relace the default sill to another special type. 
        self.currentConfig["specialSillConditions"] = None
        self.currentConfig["specialHorizontalMullions"] = None

        # Mullion Joining Configuration
        self.currentConfig["mullionContinuousVerticalAtDoorTop"] = True
        self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsTop"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateTop"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = True
        self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = False

        # Door frame settings
        """
        Format door info as shown below. Each door should contain its own info to build. 
        DOOR TYPE NAME":[HAND, MULLION CENTER POSTION, OPERATION TYPE, FRAME-01, FRAME-02, ADJUSTMENT-01, ADJUSTMENT-02]

        """
        self.currentConfig["systemDoors"] = {"74FRU":["R",74.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "80R":["R",80.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "76R":["R",76.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "72R":["R",72.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "80L":["L",80.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "76L":["L",76.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "72L":["L",72.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "DB-72-S":["R",75.5/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "DB-72-CR":["R",75.5/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "DB-72-MT":["R",75.5/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-80":["R",80.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-76":["R",76.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-72":["R",72.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-60":["R",60.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-36":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-36S":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-37S":["R",40.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-30":["R",33.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-80":["L",80.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-76":["L",76.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-72":["L",72.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-60":["L",60.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-36":["L",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-36S":["L",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-37S":["L",40.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-30":["L",33.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "CR36R":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "CR36L":["L",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "MT36R":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "MT36L":["L",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "72x84":["R",75.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "36x84":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "36x80":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "34x80":["R",37.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "34x84":["R",37.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "32x84":["R",37.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "30x84":["R",33.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "27x80":["R",30.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "Slider 6'-0\"":["R",72.0/12,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "36\" x 80\"":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "36\" x 84\"":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "30\" x 84\"":["R",33.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "72\" x 84\"":["R",75.0/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-36-CR":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-36-CR":["L",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-36-MT":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-36-MT":["L",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-36-S":["R",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-36-S":["L",39.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-38-CR":["R",41.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-38-CR":["L",41.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-38-MT":["R",41.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-38-MT":["L",41.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "RH-38-S":["R",41.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                             "LH-38-S":["L",41.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0]
                                             }
        
        # Standard lengths for mullions
        self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12, "STANDARD 05" : 58.5/12, "STANDARD 06" : 70.5/12, "STANDARD 07" : 82.5/12, "STANDARD 08" : 94.5/12},
                                                        "intermediate" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12, "STANDARD 05" : 58.5/12, "STANDARD 06" : 70.5/12, "STANDARD 07" : 82.5/12, "STANDARD 08" : 94.5/12},
                                                        "doorframe" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12},
                                                        "end" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12, "STANDARD 05" : 58.5/12, "STANDARD 06" : 70.5/12, "STANDARD 07" : 82.5/12, "STANDARD 08" : 94.5/12}}

        self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 36/12, "STANDARD 02" : 48/12}}

        # Panel Corrections for Cutlists
        """
        Used to correct for simplified curtain wall models where mullions are excluded for expediency
        but results in panel sizes that need to be corrected to reflect reality
        """
        self.currentConfig["panelCorrections"] = {"horizontalEnd" :  0.25/12,
                                                  "horizontalIntermediate": 0.25/12,
                                                  "horizontalButtJoint" : -0.0625/12, 
                                                  "verticalSill" : 0.25/12,
                                                  "verticalHead" : 0.25/12}

        # Special Cutlist Parameters
        """
        Each system requires different ways of exporting conditions, below controls what should be
        detected etc based on the system type
        """                                            
        self.currentConfig["cutlistDetectEndConditions"] = False
    
    def JEBConfigs(self):
        # System Configurations
        self.currentConfig["currentSystem"] = "JEB"
        self.currentConfig["fullSillHeight"] = 0.0
        self.currentConfig["partialSillHeight"] = 2 + (3.25/12)
        self.currentConfig["hasLowerInfill"] = False
        self.currentConfig["isFramed"] = True
        self.currentConfig["deflectionHeadType"] = 1

        # Used as a factor for detecting adjacent mullions for door frames. 
        self.currentConfig["closeMullionDetectionFactor"] = 1.0

        # Curtain Panel Options
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"

        # Curtain Wall Settings
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.systemName + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.systemName + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.systemName + "_Intermediate"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.systemName + "_OneBy-CableTray"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.systemName + "_Sill"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.systemName + "_DeflectionHead-2"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        # Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = self.systemName + "_Post"

        # Special conditions where wall types relace the default sill to another special type. 
        self.currentConfig["specialSillConditions"] = {"Partial":"JEB_Sill-Partial"}
        self.currentConfig["specialHorizontalMullions"] = {"Power":[self.currentConfig["partialSillHeight"], "JEB_OneBy-CableTray"]}

        # Mullion Joining Configuration
        self.currentConfig["mullionContinuousVerticalAtDoorTop"] = False
        self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsTop"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateTop"] = False
        self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = False
        self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = True

        # Door frame settings
        """
        Format door info as shown below. Each door should contain its own info to build. 
        DOOR TYPE NAME":[HAND, MULLION CENTER POSTION, OPERATION TYPE, FRAME-01, FRAME-02, ADJUSTMENT-01, ADJUSTMENT-02]

        """
        self.currentConfig["systemDoors"] ={"RH-2050":["R",6.725722,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-2050":["L",6.725722,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-1875":["R",6.151575,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-1875":["L",6.151575,"SLIDER", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-1000-MT":["R",3.28084,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-1000-MT":["L",3.28084,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-1000-CR":["R",3.28084,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-1000-CR":["L",3.28084,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-1000-S":["R",3.28084,"SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-1000-S":["L",3.28084,"SWING", "_DoorFrame", "_DoorFrame", 0, 0]}

        # Standard lengths for mullions
        self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                        "intermediate" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                        "doorframe" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                        "end" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12}}

        self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 39.28/12, "STANDARD 02" : 19.64/12}}

        # Panel Corrections for Cutlists
        """
        Used to correct for simplified curtain wall models where mullions are excluded for expediency
        but results in panel sizes that need to be corrected to reflect reality
        """
        self.currentConfig["panelCorrections"] = {"horizontalEnd" :  -0.4133858/12,
                                                    "horizontalIntermediate": 0.4133858/12,
                                                    "horizontalButtJoint" : -0.0625/12, 
                                                    "verticalSill" : 0.38681102/12,
                                                    "verticalHead" : 0.551181/12}

        # Special Cutlist Parameters
        """
        Each system requires different ways of exporting conditions, below controls what should be
        detected etc based on the system type
        """                                            
        self.currentConfig["cutlistDetectEndConditions"] = False    
    
    def ExtravegaConfigs(self):
        # System Configurations
        self.currentConfig["currentSystem"] = "Extravega"
        self.currentConfig["fullSillHeight"] = 0.0
        self.currentConfig["partialSillHeight"] = 2 + (3.25/12)
        self.currentConfig["hasLowerInfill"] = False
        self.currentConfig["isFramed"] = False
        self.currentConfig["deflectionHeadType"] = 1

        # Used as a factor for detecting adjacent mullions for door frames. 
        self.currentConfig["closeMullionDetectionFactor"] = 0.5

        # Curtain Panel Options
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"

        # Curtain Wall Settings
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.systemName + "_OneBy"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.systemName + "_OneBy"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.systemName + "_DeflectionHead-1"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        # Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = self.systemName + "_Post"

        # Special conditions where wall types relace the default sill to another special type. 
        self.currentConfig["specialSillConditions"] = {"Power":"Extravega_Sill-Power"}
        self.currentConfig["specialHorizontalMullions"] = {"Power":[(6.7913386/12), "Extravega_Sill-Power"]}

        # Mullion Joining Configuration
        self.currentConfig["mullionContinuousVerticalAtDoorTop"] = True
        self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsTop"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateTop"] = False
        self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = False
        self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = True

        # Door frame settings
        """
        Format door info as shown below. Each door should contain its own info to build. 
        DOOR TYPE NAME":[HAND, MULLION CENTER POSTION, OPERATION TYPE, FRAME-01, FRAME-02, ADJUSTMENT-01, ADJUSTMENT-02]

        """
        self.currentConfig["systemDoors"] = {"RH-875-CR" : ["R", 33.0709/12, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-875-MT" : ["R", 33.0709/12, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-875-S" : ["R", 33.0709/12, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-875-CR":["L", 33.0709/12, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-875-MT":["L", 33.0709/12, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-875-S":["L", 33.0709/12, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-1900":["R", 3.362861, "SLIDER", "_Post", "_Post-Receiver", -0.866142/12, 0],
                                            "LH-1900":["L", 3.362861, "SLIDER", "_Post-Receiver", "_Post", 0, -0.866142/12]}
        
        # Standard lengths for mullions
        self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                        "intermediate" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                        "doorframe" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                        "end" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12}}

        self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 39.28/12, "STANDARD 02" : 19.64/12}}

        # Panel Corrections for Cutlists
        """
        Used to correct for simplified curtain wall models where mullions are excluded for expediency
        but results in panel sizes that need to be corrected to reflect reality
        """
        self.currentConfig["panelCorrections"] = {"horizontalEnd" :  -0.4133858/12,
                                                    "horizontalIntermediate": 0.4133858/12,
                                                    "horizontalButtJoint" : -0.0625/12, 
                                                    "verticalSill" : 0.38681102/12,
                                                    "verticalHead" : 0.551181/12}

        # Special Cutlist Parameters
        """
        Each system requires different ways of exporting conditions, below controls what should be
        detected etc based on the system type
        """                                            
        self.currentConfig["cutlistDetectEndConditions"] = False
    
    def ModeConfigs(self):
        # System configurations
        self.currentConfig["currentSystem"] = self.systemName
        self.currentConfig["fullSillHeight"] = 0.0
        self.currentConfig["partialSillHeight"] = 2 + (3.25/12)
        self.currentConfig["hasLowerInfill"] = False
        self.currentConfig["isFramed"] = True
        self.currentConfig["deflectionHeadType"] = 1

        #Used as a factor for detecting adjacent mullions for door frames.
        self.currentConfig["closeMullionDetectionFactor"] = 1.0

        # Curtain Panel Options
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_MODE-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_MODE-Offset"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_MODE-Double"

        # Curtain wall settings
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.systemName + "_Intermediate-1"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.systemName + "_Intermediate-1-Offset"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.systemName + "_Intermediate-2"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.systemName + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.systemName + "_Intermediate-1"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.systemName + "_Sill-Center"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.systemName + "_DeflectionHead-1"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_MODE-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        # Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = self.systemName + "_Post"

        #Special conditions where wall types relace the default sill to another special type
        self.currentConfig["specialSillConditions"] = {"Offset":"MODE_Sill-Offset", "Double":"MODE_Sill-Double", }
        self.currentConfig["specialHorizontalMullions"] = None

        # Mullion Joining Configuration
        self.currentConfig["mullionContinuousVerticalAtDoorTop"] = False
        self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsTop"] = False
        self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateTop"] = False
        self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = False
        self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = True

        # Door frame settings
        """
        Format door info as shown below. Each door should contain its own info to build. 
        DOOR TYPE NAME":[HAND, MULLION CENTER POSTION, OPERATION TYPE, FRAME-01, FRAME-02, ADJUSTMENT-01, ADJUSTMENT-02]

        """
        self.currentConfig["systemDoors"] = {"RH-1000-MT" : ["R", 2.98556, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-1000-MT" : ["L", 2.98556, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-1000-CR" : ["R", 2.98556, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-1000-CR" : ["L", 2.98556, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-1000-S" : ["R", 2.98556, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "LH-1000-S" : ["L", 2.98556, "SWING", "_DoorFrame", "_DoorFrame", 0, 0],
                                            "RH-2000" : ["R", 2.98556, "SLIDER", "_DoorFrameMid", "_DoorFrame", 0.590551/12, 0],
                                            "LH-2000" : ["L", 2.98556, "SLIDER", "_DoorFrame", "_DoorFrameMid", 0, 0.590551/12]}

        
        # Standard lengths for mullions
        self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 96.0/12, "STANDARD 02" : 84.0/12, "STANDARD 03" : 108/12},
                                                        "intermediate" : {"STANDARD 01" : 7.491, "STANDARD 02" : 6.491, "STANDARD 03" : 8.491},
                                                        "doorframe" : {"STANDARD 01" : 7.737, "STANDARD 02" : 6.737, "STANDARD 03" : 8.737},
                                                        "end" : {"STANDARD 01" : 96.0/12, "STANDARD 02" : 84.0/12, "STANDARD 03" : 108.0/12}}

        self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 39.28/12, "STANDARD 02" : 19.64/12}}

        # Panel Corrections for Cutlists
        """
        Used to correct for simplified curtain wall models where mullions are excluded for expediency
        but results in panel sizes that need to be corrected to reflect reality
        """
        self.currentConfig["panelCorrections"] = {"horizontalEnd" :  -0.4134/12,
                                                    "horizontalIntermediate" : 0.4724/12,
                                                    "horizontalButtJoint" : -0.09375/12, 
                                                    "verticalSill" : 0.38681102/12,
                                                    "verticalHead" : 0.551181/12}

        # Cutlist Export Configuration
        self.currentConfig["headOffsetAtEndCondition"] = 2.066929/12        # 52.5mm
        self.currentConfig["headOffsetAtTBoneCondition"] = -0.0984252/12    # -2.5mm
        self.currentConfig["headOffsetAtCornerCondition"] = 4.2322835/12    # 107.5mm
        self.currentConfig["headOffsetAtInlineCondition"] = 2.066929/12     # 52.5mm
        self.currentConfig["headOffsetAtFourwayCondition"] = 2.066929/12    # 52.5mm

        self.currentConfig["headFabAtCornerInlineCondition-Left"] = "NO-L"
        self.currentConfig["headFabAtCornerInlineCondition-Right"] = "NO-R"
        self.currentConfig["headFabAtCornerCondition-Left"] = "MI-L"
        self.currentConfig["headFabAtCornerCondition-Right"] = "MI-R"
        self.currentConfig["headFabAtEndCondition"] = "NONE"
        self.currentConfig["headFabAtInlineCondition"] = "NONE"
        self.currentConfig["headFabAtTBoneCondition"] = "NONE"

        # Special Cutlist Parameters
        """
        Each system requires different ways of exporting conditions, below controls what should be
        detected etc based on the system type
        """                                            
        self.currentConfig["cutlistDetectEndConditions"] = True
    
    #
    # MAIN METHOD
    def Run_SaveSFConfigurations(self, systemName=None, userConfigs=None):
        """
        Each system is defined here by their profile dimensions.
        and some other system specific features. These values
        are used throughout the storefront engine by calling the
        storefront_options() class. 
        """
        # convert input variables at input to global class variables
        self.systemName = systemName
        self.userConfigs = userConfigs
        
        if self.systemName:
            if "Elite" in self.systemName:
                self.EliteConfigs()
            elif "JEB" in self.systemName:
                self.JEBConfigs()
            elif self.systemName == "Extravega":
                self.ExtravegaConfigs()
            elif self.systemName == "MODE":
                self.ModeConfigs()
            
        #Save any other configs selected previously selected by the user.
        if self.userConfigs:
            for key in self.userConfigs.keys():
                self.currentConfig[key] = self.userConfigs[key]
        
        # HOW CAN I GET NIB WALL CONFIGURATIONS TO BE WRITTEN AS WELL?
        self.JSONSaveConfig()

##################################
## BASE CLASS C | LOAD FAMILIES ##
##################################
class CreateMullion_Curtain:
    def __init__(self):
        # derived parameters
        self.selectedSystem = None
        
        self.profileDict = None
        self.wallTypeDict = None
        self.mullionDict = None
        self.panelTypeDict = None
        self.quadMullionDict = None   
    def __repr__(self):
        return("<class 'CreateMullion_Curtain'>")
    #
    # THIS IS MORE UTILITY LIKE
    def ActivateFamilySymbols(self, family):
        familyLoadedSymbols = list(family.GetFamilySymbolIds())
        if familyLoadedSymbols:
            for symbolId in familyLoadedSymbols:
                symbol = self.doc.GetElement(symbolId)
                if not symbol.IsActive:
                    symbol.Activate()
        return(None)
    #
    # ACTUAL FAMILY LOADING
    def LoadFamFromPaths(self, names, directory):
        """ 
        Loads families given a a list of family names and a directory.
        Returns a list of family Element Ids. 
        """
        familyIds = []    
        with rpw.db.Transaction("Load Family"): 
            for famName in names:
                path = "{0}\{1}".format(directory, famName)
                familyLoaded = clr.Reference[Autodesk.Revit.DB.Family]()
                
                # THIS IS THE ONLY PLACE WHERE FamilyOptions IS USED...WHAT IS IT DOING?
                loaded = self.doc.LoadFamily(path, FamilyOptions(), familyLoaded)
    
                if loaded:
                    print ("...loaded")
                    print("FAMILY: {0}...LOADED".format(familyLoaded.Name))
                    familyIds.append(familyLoaded.Id)
                    self.ActivateFamilySymbols(familyLoaded)
        return(familyIds)
    #
    # LOAD REGULAR FAMILIES AND MULLIONS
    def LoadRegularFamilies(self):
        # Load the necessary families
        #try:
            #try:
        
        # google drive stream
        self.familyDirectory = self.gDrivePath
        # get names of the families saved in google drive dir
        familiesToLoad = os.listdir(self.familyDirectory)
        self.LoadFamFromPaths(familiesToLoad, self.familyDirectory)                
            
            #except:
                ## nasuni w drive
                #self.familyDirectory = self.wDrivePath
                #familiesToLoad = os.listdir(self.familyDirectory)
                #self.LoadFamFromPaths(familiesToLoad, self.familyDirectory)                
        #except:
            #print("Families couldn't be loaded from Google Drive or Nasuni (W drive), please check network connection")
            #sys.exit()
        
        # create dictionaries of Ids of elements and elementTypes in the model
        # if empty it would imply that certain elements have not been loaded in model
        self.profileDict = SFU.GetProfileDict("I-Profile-Storefront-Mullion")
        self.wallTypeDict = SFU.GetWallTypeDict()
        self.mullionDict = SFU.GetMullionTypeDict(self.doc)
        self.panelTypeDict = SFU.GetWindowTypeDict()
        self.quadMullionDict = SFU.GetQuadMullionTypeDict()
        createMullions = {}
    #
    # CREATE MULLION TYPES    
    def CreateRectMullionTypes(self):
        mullionTypeNames = self.mullionDict.keys()
        
        # Create Rectangualr Mullions
        for profileName in self.profileDict.keys():

            # Ensure you're only creating mullion types for the selected system
            if self.selectedSystem.lower() == profileName.split("_")[0].lower():

                # Create a new mullion type from a duplicate if not in doc.
                if not any(profileName == s for s in mullionTypeNames):
                    newMullionType = self.doc.GetElement(self.mullionDict[self.mullionDict.keys()[0]]).Duplicate(profileName)
                    newMullionType.get_Parameter(BuiltInParameter.MULLION_PROFILE).Set(self.profileDict[profileName])
                    self.mullionDict[profileName] = newMullionType.Id
                # Otherwise grab it from the mullion dictionary if it exists.
                elif any(profileName == s for s in mullionTypeNames):
                    newMullionType = self.doc.GetElement(self.mullionDict[profileName])
                
                # HERE IS WHEN YOU WOULD OPEN FAMILY AND ADD TYPE WITHIN FAMILY EDITOR, REMEMBER TO CLOSE FAMILY
                else:
                    pass
                
                # Set Special parameters for Mullion Types like: Offsets
                # Default
                mullionOffset = 0

                # THIS IS TOO DIFFICULT TO MANAGE HERE, INCORPORATE IT WITHIN SF CONFIGS...
                if "MODE" in profileName:
                    if "Offset" in profileName:
                        #set the mulliontype offset to 31mm
                        mullionOffset = 0.101706
                    elif "DoorFrameMid" in profileName:
                        #set the mulliontype offset to 18.5mm
                        mullionOffset = 0.06069554

                newMullionType.get_Parameter(BuiltInParameter.MULLION_OFFSET).Set(mullionOffset)
    def CreateQuadCornerMullionTypes(self):
        # create Quad Corner Mullions
        quadMullionTypeNames = self.quadMullionDict.keys()
        for profileName in self.profileDict.keys():

            # ensure you're only creating mullion types for the selected system
            if self.selectedSystem.lower() == profileName.split("_")[0].lower():

                # any profile that ends with "_Post" will be used for the corner.
                if "post" in profileName.split("_")[1].lower():
                    if not any(profileName == s for s in quadMullionTypeNames):
                        newMullionType = self.doc.GetElement(self.quadMullionDict[self.quadMullionDict.keys()[0]]).Duplicate(profileName)
                        depth1 = 0
                        depth2 = 0

                        for p in self.doc.GetElement(self.profileDict[profileName]).Parameters:
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
                        self.quadMullionDict[profileName] = newMullionType.Id
    def CreateCurtainWallTypes(self):
        # CREATE CURTAIN WALL TYPES
        # Create curtain wall system for each system if they dont exist
        templateCW = None
        for key, value in self.wallTypeDict.items():
            wt = self.doc.GetElement(value)
            if str(wt.Kind) == "Curtain":
                templateCW = wt
                break

        curtainWallNamePrefix = "I-Storefront-"

        cwType = "{0}{1}".format(curtainWallNamePrefix, self.selectedSystem)
        if not any( cwType == s for s in self.wallTypeDict.keys()):
            newCW = templateCW.Duplicate(cwType)
        else:
            newCW = self.doc.GetElement(self.wallTypeDict[cwType])
        #newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(self.mullionDict[self.selectedSystem+"_Post"])
        newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(self.mullionDict[self.currentConfig["AUTO_MULLION_INTERIOR_VERT"]])
        newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_VERT).Set(self.quadMullionDict[self.currentConfig["AUTO_MULLION_BORDER1_VERT"]])
        newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_VERT).Set(self.quadMullionDict[self.currentConfig["AUTO_MULLION_BORDER2_VERT"]])
        newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_HORIZ).Set(self.mullionDict[self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"]])
        newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_HORIZ).Set(self.mullionDict[self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"]])
        newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"]])
        newCW.get_Parameter(BuiltInParameter.AUTO_PANEL_WALL).Set(self.panelTypeDict[self.currentConfig["AUTO_PANEL_WALL"]])
        newCW.get_Parameter(BuiltInParameter.AUTO_JOIN_CONDITION_WALL).Set(self.currentConfig["AUTO_JOIN_CONDITION_WALL"]) # vertical continuous
        newCW.get_Parameter(BuiltInParameter.ALLOW_AUTO_EMBED).Set(self.currentConfig["ALLOW_AUTO_EMBED"])
        newCW.get_Parameter(BuiltInParameter.FUNCTION_PARAM).Set(self.currentConfig["FUNCTION_PARAM"])
        newCW.get_Parameter(BuiltInParameter.SPACING_LAYOUT_HORIZ).Set(self.currentConfig["SPACING_LAYOUT_HORIZ"])
        newCW.get_Parameter(BuiltInParameter.SPACING_LAYOUT_VERT).Set(self.currentConfig["SPACING_LAYOUT_VERT"])
    def CreateMullionAndCurtainWallFamilies(self):
        # mullion dictionary is written when families are loaded
        if self.quadMullionDict.keys() and self.mullionDict.keys():
            print("LOADING CURTAIN WALLS...")
            
            # creates mullions that are needed, both rectangular and quad.
            with rpw.db.Transaction("Create Curtain Wall") as tx:
                SFU.SupressErrorsAndWarnings(tx) # i added this and the "as tx" above
                
                self.CreateRectMullionTypes()
                self.CreateQuadCornerMullionTypes()
                self.CreateCurtainWallTypes()
            
            print("...CURTAIN WALLS LOADED")
                
        # NOT ENTIRELY SURE WHAT IS GOING ON HERE...   
        else: 
            if not self.quadMullionDict.keys() or not self.mullionDict.keys():
                # legacy output:
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Please check the 'Curtain Wall Mullions' in the Project Browser and ensure you have at least (1) Quad Mullion type & (1) Rectangular Mullion type. Right click on them to create a 'New Type' if needed.")
                sys.exit()
    #
    # MAIN METHOD
    def Run_LoadFamilies(self, currentConfig):
        """
        Creates curtain wall types and loads families.
        
        THIS IS RAN AFTER SF CONFIGURATIONS HAVE BEEN MADE, GUI
        SAVES IT, AND IT EXISTS THERE, SO THOSE SETTINGS NEED TO BE FED
        BACK HERE B/C THEY WERE NEVER VARIABLES WITHIN THIS MODULE
        
        THIS COULD FUNCTION AS RUN FOR LOADING....
        """
        # convert class default
        self.currentConfig = currentConfig        
        
        self.selectedSystem = self.currentConfig["currentSystem"]
        
        print("LOADING FAMILIES...")
        self.LoadRegularFamilies()
        self.CreateMullionAndCurtainWallFamilies()
        
###################
## DERIVED CLASS ##
###################
class FamilyTools(FamilyUtilities, SetSFConfiguration, CreateMullion_Curtain, GUICalledClass):
    """
    THERE IS NO RUN, CALL CLASS THAT YOU NEED HERE
    BOTH FAMILIES WILL BE INSTANTIATED TOGETHER
    """
    def __init__(self, doc):
        # input parameters
        self.doc = doc
        
        # storefront family directory parameters - THIS IS CONVOLUTED AS FUCK THERE ARE FAMILYDIRECTORYS AND SELF.FD
        self.familyDirectory = None # this will be set in code to either the gDrive or wDrive     
        self.gDrivePath = r"G:\Shared drives\Prod - BIM\07_Global Initiatives\Storefront_2\Families"
        self.wDrivePath = None
        
        """
        Revit Wall Families used for Storefront Creation
        
        System Family: Basic Wall
        dict key: wall type
        dict value: 0 = full
                    1 = partial
        """
        self.SFWallTypeNames = {"Storefront-Full": 0,
                                "Storefront-Partial": 1,
                                "WW-Storefront-S1": 0,
                                "WW-Storefront-S1F": 1
                                }        
        
        # class inheritance / polymorphism
        FamilyUtilities.__init__(self)
        SetSFConfiguration.__init__(self)
        CreateMullion_Curtain.__init__(self)
        GUICalledClass.__init__(self)
    def __repr__(self):
        return("<class 'FamilyTools'>")    