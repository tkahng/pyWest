import json
import sys
import os
import System
from System import DateTime as dt

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
import tempfile

sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\Storefront 2.panel\0 Lib")
import rpw

from SF2_Utility import *

# JSON - CAN ALSO BE ACCESSED INDEPENDENTLY
# CONFIGURATION FILES CURRENTLY IN GUI, PROBABLY SHOULD BE MOVED HERE
class DataExchange:
    def __init__(self):
        pass
        
    # replace these with my data exchange tools for consistency accross all plugins
    def JSON_SaveConfig(self, configPath):
        with open(configPath, 'w') as outfile:
            json.dump(self.currentConfig, outfile)
        return(True)

    def JSON_LoadConfig(self, configPath):
        if os.path.exists(configPath):
            with open(configPath) as readFile:
                jsonstring = readFile.read()
        else: 
            with open("{0}\\default_settings.json".format(os.path.dirname(__file__))) as readFile:
                jsonstring = readFile.read()

        jsonstring = jsonstring.replace("null", "0", 100)
        jsonData = json.loads(jsonstring)
        self.currentConfig.update(jsonData)
        return(None)    

# CONFIGURATION   
class SetConfiguration:
    """
    IT LOOKS LIKE CONFIGURATIONS ARE SHARE USING JSON FILES, READ AND WRITE
    """
    def __init__(self, selectedSystem=None, userConfigs=None):
        # from GUI
        self.familiesToLoad = {"I-Profile-Storefront-Mullion" : {"Symbol": None, "Types": {}},
                               "Empty Panel" : {"Symbol": None, "Types": {}},
                               "Solid Center Panel" : {"Symbol": None, "Types": {}},
                               "Glazed Center Panel" : {"Symbol": None, "Types": {}},
                               "Extraction-Door-Symbol" : {"Symbol": None, "Types": {}},
                               "Extraction-Desk-Symbol" : {"Symbol": None, "Types": {}},
                               "Fabrication-Error-Symbol" : {"Symbol": None, "Types": {}},
                               "Panel-Symbol-Standard" : {"Symbol": None, "Types": {}},
                               "Panel-Symbol-Custom" : {"Symbol": None, "Types": {}}}
        
        self.currentConfig = {"currentSystem":None,
                              "selectedSystem": None,
                              "postWidth":None,
                              "oneByWidth":None,
                              "headHeight":None,
                              "fullSillHeight":None,
                              "partialSillHeight":None,
                              "spacingType":None,
                              "transomHeight":None,
                              "storefrontPaneWidth":None,
                              "hasLowerInfill":None,
                              "deflectionHeadType": None,
                              "splitWallType":None,
                              "splitOffset":None,
                              "isFramed":None,
                              "profiles":None,
                              "families": self.familiesToLoad}
        
        
        # this is not called in GUI or here WHERE DOES IT BELONG?
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
                         "MODE-LH-1000-S":["L",2.98556,"SWING"]}               
        
        self.defaultConfigPath = os.path.join(tempfile.gettempdir(), "storefront_default_config.json") # this is found in SF2_GUI
        self.json_load_config = self.JSON_LoadConfig(self.defaultConfigPath) # must come after self.currentConfig
        
        self.selectedSystem = selectedSystem
        self.userConfigs = userConfigs        
        

    def Elite(self):
        # System Configurations
        self.currentConfig["currentSystem"] = "Elite"
        self.currentConfig["fullSillHeight"] = 0.0

        if "Lower Infill" in selectedSystem:
            self.currentConfig["hasLowerInfill"] = True
        else:
            self.currentConfig["hasLowerInfill"] = False

        # Regional Settings
        if "LATAM" in selectedSystem:
            self.currentConfig["transomHeight"] = 8.2021
            self.currentConfig["partialSillHeight"] = 2.49344 - (1.75/12)

        else:
            self.currentConfig["transomHeight"] = 8 + (1.75/12)
            self.currentConfig["partialSillHeight"] = 2 + (3.25/12)

        self.currentConfig["isFramed"] = True
        self.currentConfig["deflectionHeadType"] = 0

        #Used as a factor for detecting adjacent mullions for door frames
        self.currentConfig["closeMullionDetectionFactor"] = 1.0

        #To make sure that the mullion family names are correctly set
        selectedSystem = "Elite"

        # Curtain Panel Options
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"

        # Curtain Wall Settings
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = selectedSystem + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = selectedSystem + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = selectedSystem + "_Intermediate"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = selectedSystem + "_Sill"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = selectedSystem + "_Sill"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = selectedSystem + "_OneBy"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        # Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = selectedSystem + "_Post"

        # Special conditions where wall types relace the default sill to another special type
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
                                             "LH-38-S":["L",41.5/12,"SWING", "_DoorFrame", "_DoorFrame", 0, 0]}

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

    def JEB(self):
        #----------------------System Configurations----------------------#
        self.currentConfig["currentSystem"] = "JEB"
        self.currentConfig["fullSillHeight"] = 0.0
        self.currentConfig["partialSillHeight"] = 2 + (3.25/12)
        self.currentConfig["hasLowerInfill"] = False
        self.currentConfig["isFramed"] = True
        self.currentConfig["deflectionHeadType"] = 1

        #Used as a factor for detecting adjacent mullions for door frames. 
        self.currentConfig["closeMullionDetectionFactor"] = 1.0

        #----------------------Curtain Panel Options------------------------#
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"

        #----------------------Curtain Wall Settings------------------------#
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = selectedSystem + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = selectedSystem + "_Intermediate"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = selectedSystem + "_Intermediate"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = selectedSystem + "_OneBy-CableTray"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = selectedSystem + "_Sill"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = selectedSystem + "_DeflectionHead-2"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        #Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = selectedSystem + "_Post"

        #Special conditions where wall types relace the default sill to another special type. 
        self.currentConfig["specialSillConditions"] = {"Partial":"JEB_Sill-Partial"}
        self.currentConfig["specialHorizontalMullions"] = {"Power":[self.currentConfig["partialSillHeight"], "JEB_OneBy-CableTray"]}

        #----------------------Mullion Joining Configuration----------------------#
        self.currentConfig["mullionContinuousVerticalAtDoorTop"] = False
        self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsTop"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateTop"] = False
        self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = False
        self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = True

        #----------------------Door frame settings----------------------#
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

        #----------------------Standard lengths for mullions----------------------#
        self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                         "intermediate" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                         "doorframe" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                         "end" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12}}

        self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 39.28/12, "STANDARD 02" : 19.64/12}}

        #---------------------- Panel Corrections for Cutlists ----------------------#
        """
            Used to correct for simplified curtain wall models where mullions are excluded for expediency
            but results in panel sizes that need to be corrected to reflect reality
            """
        self.currentConfig["panelCorrections"] = {"horizontalEnd" :  -0.4133858/12,
                                                  "horizontalIntermediate": 0.4133858/12,
                                                  "horizontalButtJoint" : -0.0625/12, 
                                                  "verticalSill" : 0.38681102/12,
                                                  "verticalHead" : 0.551181/12}

        #---------------------- Special Cutlist Parameters ----------------------#
        """
        Each system requires different ways of exporting conditions, below controls what should be
        detected etc based on the system type
        """                                            
        self.currentConfig["cutlistDetectEndConditions"] = False

    def Extravega(self):
        #----------------------System Configurations----------------------#
        self.currentConfig["currentSystem"] = "Extravega"
        self.currentConfig["fullSillHeight"] = 0.0
        self.currentConfig["partialSillHeight"] = 2 + (3.25/12)
        self.currentConfig["hasLowerInfill"] = False
        self.currentConfig["isFramed"] = False
        self.currentConfig["deflectionHeadType"] = 1

        #Used as a factor for detecting adjacent mullions for door frames. 
        self.currentConfig["closeMullionDetectionFactor"] = 0.5

        #----------------------Curtain Panel Options------------------------#
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"

        #----------------------Curtain Wall Settings------------------------#
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = selectedSystem + "_OneBy"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = selectedSystem + "_OneBy"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = selectedSystem + "_DeflectionHead-1"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        #Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = selectedSystem + "_Post"

        #Special conditions where wall types relace the default sill to another special type. 
        self.currentConfig["specialSillConditions"] = {"Power":"Extravega_Sill-Power"}
        self.currentConfig["specialHorizontalMullions"] = {"Power":[(6.7913386/12), "Extravega_Sill-Power"]}

        #----------------------Mullion Joining Configuration----------------------#
        self.currentConfig["mullionContinuousVerticalAtDoorTop"] = True
        self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsTop"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateTop"] = False
        self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = False
        self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = True

        #----------------------Door frame settings----------------------#
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

        #----------------------Standard lengths for mullions----------------------#
        self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                         "intermediate" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                         "doorframe" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12},
                                                         "end" : {"STANDARD 01" : 97.75/12, "STANDARD 02" : 96/12, "STANDARD 03" : 84/12}}

        self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 39.28/12, "STANDARD 02" : 19.64/12}}

        #---------------------- Panel Corrections for Cutlists ----------------------#
        """
            Used to correct for simplified curtain wall models where mullions are excluded for expediency
            but results in panel sizes that need to be corrected to reflect reality
            """
        self.currentConfig["panelCorrections"] = {"horizontalEnd" :  -0.4133858/12,
                                                  "horizontalIntermediate": 0.4133858/12,
                                                  "horizontalButtJoint" : -0.0625/12, 
                                                  "verticalSill" : 0.38681102/12,
                                                  "verticalHead" : 0.551181/12}

        #---------------------- Special Cutlist Parameters ----------------------#
        """
            Each system requires different ways of exporting conditions, below controls what should be
            detected etc based on the system type
            """                                            
        self.currentConfig["cutlistDetectEndConditions"] = False

    def MODE(self):
        #----------------------System configurations----------------------#
        self.currentConfig["currentSystem"] = selectedSystem
        self.currentConfig["fullSillHeight"] = 0.0
        self.currentConfig["partialSillHeight"] = 2 + (3.25/12)
        self.currentConfig["hasLowerInfill"] = False
        self.currentConfig["isFramed"] = True
        self.currentConfig["deflectionHeadType"] = 1

        #Used as a factor for detecting adjacent mullions for door frames.
        self.currentConfig["closeMullionDetectionFactor"] = 1.0

        #----------------------Curtain Panel Options------------------------#
        self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
        self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
        self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_MODE-Center"
        self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_MODE-Offset"
        self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_MODE-Double"

        #----------------------Curtain wall settings------------------------#
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = selectedSystem + "_Intermediate-1"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = selectedSystem + "_Intermediate-1-Offset"
        self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = selectedSystem + "_Intermediate-2"
        self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = selectedSystem + "_Post"
        self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = selectedSystem + "_Intermediate-1"
        self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = selectedSystem + "_Sill-Center"
        self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = selectedSystem + "_DeflectionHead-1"
        self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_MODE-Center"
        self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
        self.currentConfig["ALLOW_AUTO_EMBED"] = 0
        self.currentConfig["FUNCTION_PARAM"] = 0
        self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
        self.currentConfig["SPACING_LAYOUT_VERT"] = 0

        #Mullion used for intersections with other storefront
        self.currentConfig["midspanIntersectionMullion"] = selectedSystem + "_Post"

        #Special conditions where wall types relace the default sill to another special type. 
        self.currentConfig["specialSillConditions"] = {"Offset":"MODE_Sill-Offset", "Double":"MODE_Sill-Double", }
        self.currentConfig["specialHorizontalMullions"] = None

        #----------------------Mullion Joining Configuration----------------------#
        self.currentConfig["mullionContinuousVerticalAtDoorTop"] = False
        self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
        self.currentConfig["mullionContinuousVerticalAtEndsTop"] = False
        self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
        self.currentConfig["mullionContinuousVerticalIntermediateTop"] = False
        self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = False
        self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = True

        #----------------------Door frame settings----------------------#
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


        #----------------------Standard lengths for mullions----------------------#
        self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 96.0/12, "STANDARD 02" : 84.0/12, "STANDARD 03" : 108/12},
                                                         "intermediate" : {"STANDARD 01" : 7.491, "STANDARD 02" : 6.491, "STANDARD 03" : 8.491},
                                                         "doorframe" : {"STANDARD 01" : 7.737, "STANDARD 02" : 6.737, "STANDARD 03" : 8.737},
                                                         "end" : {"STANDARD 01" : 96.0/12, "STANDARD 02" : 84.0/12, "STANDARD 03" : 108.0/12}}

        self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 39.28/12, "STANDARD 02" : 19.64/12}}

        #---------------------- Panel Corrections for Cutlists ----------------------#
        """
            Used to correct for simplified curtain wall models where mullions are excluded for expediency
            but results in panel sizes that need to be corrected to reflect reality
            """
        self.currentConfig["panelCorrections"] = {"horizontalEnd" :  -0.4134/12,
                                                  "horizontalIntermediate" : 0.4724/12,
                                                  "horizontalButtJoint" : -0.09375/12, 
                                                  "verticalSill" : 0.38681102/12,
                                                  "verticalHead" : 0.551181/12}

        #----------------------Cutlist Export Configuration----------------------#
        self.currentConfig["headOffsetAtEndCondition"] = 2.066929/12        #52.5mm
        self.currentConfig["headOffsetAtTBoneCondition"] = -0.0984252/12    #-2.5mm
        self.currentConfig["headOffsetAtCornerCondition"] = 4.2322835/12    #107.5mm
        self.currentConfig["headOffsetAtInlineCondition"] = 2.066929/12     #52.5mm
        self.currentConfig["headOffsetAtFourwayCondition"] = 2.066929/12    #52.5mm

        self.currentConfig["headFabAtCornerInlineCondition-Left"] = "NO-L"
        self.currentConfig["headFabAtCornerInlineCondition-Right"] = "NO-R"
        self.currentConfig["headFabAtCornerCondition-Left"] = "MI-L"
        self.currentConfig["headFabAtCornerCondition-Right"] = "MI-R"
        self.currentConfig["headFabAtEndCondition"] = "NONE"
        self.currentConfig["headFabAtInlineCondition"] = "NONE"
        self.currentConfig["headFabAtTBoneCondition"] = "NONE"

        #---------------------- Special Cutlist Parameters ----------------------#
        """
        Each system requires different ways of exporting conditions, below controls what should be
        detected etc based on the system type
        """                                            
        self.currentConfig["cutlistDetectEndConditions"] = True
        
        
# YOUNGEST CHILD
class SFLoadFamilies(DataExchange, SetConfiguration):
    def __init__(self, selectedSystem=None, userConfigs=None):
        DataExchange.__init__(self)
        SetConfiguration.__init__(self, selectedSystem, userConfigs)
        
        #if userConfigs:
            #for key in userConfigs.keys():
                #self.currentConfig[key] = userConfigs[key]
    
        #self.JSON_SaveConfig()
        
        # BROUGHT OVER FROM SF2_ENGINE.STOREFRONT2()GENERATESF()
        #systemName = SF_Form.currentConfig["currentSystem"]
        # WOULDN'T I JUST OUTPUT CONFIGURATION VARIABLE, NOT INDIVIDUAL VARIABLES?
        #storefrontPaneWidth = SF_Form.currentConfig["storefrontPaneWidth"]
        #storefrontSpacingType = SF_Form.currentConfig["spacingType"]
        #mullionDict = GetMullionTypeDict()
        #panelTypeDict = GetWindowTypeDict()
        #doorDict = SF_Form.currentConfig["systemDoors"]
        #wallTypeDict = GetWallTypeDict()
        #wallDoorHostDict = GetDoorDictByWallHost()
        
