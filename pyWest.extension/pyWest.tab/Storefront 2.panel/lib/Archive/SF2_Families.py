import traceback
import os
import sys

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    import json
    import System
    from System import DateTime as dt

    import clr
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
    from Autodesk.Revit.UI import *
    from Autodesk.Revit.DB import *
    import tempfile # why is temp being used?

    #rpwLib = r"VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\0 Lib\revitpythonwrapper-master" # common lib folder
    #sys.path.append(ShiftFilePath(os.path.abspath(__file__), 6, rpwLib))
    sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\0 Lib\revitpythonwrapper-master")
    import rpw

    sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\Storefront 2.panel\0 Lib")
    import SF2_Utility

    # DATA EXCHANGE
    class SF_DataExchange:
        def __init__(self, configPath):
            self.configPath = configPath
        
        def json_save_config(self):
            with open(self.configPath, 'w') as outfile:
                json.dump(self.currentConfig, outfile)
            return(True)

        def json_load_config(self):
            if os.path.exists(self.configPath):
                with open(self.configPath) as readFile:
                    jsonstring = readFile.read()
            else: 
                hardCodedPath = r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\Storefront 2.panel\0 Lib"
                with open(r"{0}\default_settings.json".format(hardCodedPath)) as readFile: # os.path.dirname(__file__)
                    jsonstring = readFile.read()

            jsonstring = jsonstring.replace("null", "0", 100)
            jsonData = json.loads(jsonstring)
            self.currentConfig.update(jsonData)
            return(None)        
        
    # FAMILY AND SYSTEM OPTIONS
    class SF_Options:
        def __init__(self, userSettings=None):
            self.userSettings = userSettings
        
        def SFSystemNames(self):
            """
            This list is connected to all modules/namespaces
            that require this information including GUI form
            """
            systemNames = ['Elite',
                           'JEB',
                           'Extravega',
                           'MODE',
                           'Elite 2']
            return(systemNames)
        
        def SFFamilyNames(self):
            """
            This method contains a dictionary of storefront family
            names. In SF2_Engine if a family type exists in this dict.
            and the document then the element is made into a storefront
            system.
        
            System Family: Basic Wall
            dict key: wall type
            dict value: 0 = full
                        1 = partial
            """        
            wallTypeNames = {'Storefront-Full':0,
                             'Storefront-Partial':1,
                             'WW-Storefront-S1':0,
                             'WW-Storefront-S1F':1}
            return(wallTypeNames)
        
        def FamiliesToLoad(self):
            # USED BY THE GUI
            self.familiesToLoad = {"I-Profile-Storefront-Mullion" : {"Symbol": None, "Types": {}},
                                   "Empty Panel" : {"Symbol": None, "Types": {}},
                                   "Solid Center Panel" : {"Symbol": None, "Types": {}},
                                   "Glazed Center Panel" : {"Symbol": None, "Types": {}},
                                   "Extraction-Door-Symbol" : {"Symbol": None, "Types": {}},
                                   "Extraction-Desk-Symbol" : {"Symbol": None, "Types": {}},
                                   "Fabrication-Error-Symbol" : {"Symbol": None, "Types": {}},
                                   "Panel-Symbol-Standard" : {"Symbol": None, "Types": {}},
                                   "Panel-Symbol-Custom" : {"Symbol": None, "Types": {}}}
            return(self.familiesToLoad)
    
    
    # CONFIGURATION
    class storefront_configuration:
        """
        IT LOOKS LIKE CONFIGURATIONS ARE SHARE USING JSON FILES, READ AND WRITE

        storefront_set_config became part of the SF2_GUI
        """
        def __init__(self, system_name=None): # elimated user configs
            self.currentConfig = {"currentSystem":None,
                                  "system_name": None,
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
                                  "systemDoors":None,
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

            self.system_name = system_name
            self.userConfigs = userConfigs
        # storefront_save_config
        def Elite(self):
            # System Configurations
            self.currentConfig["currentSystem"] = "Elite"
            self.currentConfig["fullSillHeight"] = 0.0

            if "Lower Infill" in self.system_name:
                self.currentConfig["hasLowerInfill"] = True
            else:
                self.currentConfig["hasLowerInfill"] = False

            # Regional Settings
            if "LATAM" in self.system_name:
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
            system_name = "Elite"

            # Curtain Panel Options
            self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
            self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
            self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
            self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
            self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"

            # Curtain Wall Settings
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.system_name + "_Intermediate"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.system_name + "_Intermediate"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.system_name + "_Intermediate"
            self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.system_name + "_Sill"
            self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.system_name + "_Sill"
            self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.system_name + "_OneBy"
            self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
            self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
            self.currentConfig["ALLOW_AUTO_EMBED"] = 0
            self.currentConfig["FUNCTION_PARAM"] = 0
            self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
            self.currentConfig["SPACING_LAYOUT_VERT"] = 0

            # Mullion used for intersections with other storefront
            self.currentConfig["midspanIntersectionMullion"] = self.system_name + "_Post"

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
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.system_name + "_Intermediate"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.system_name + "_Intermediate"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.system_name + "_Intermediate"
            self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.system_name + "_OneBy-CableTray"
            self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.system_name + "_Sill"
            self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.system_name + "_DeflectionHead-2"
            self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
            self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
            self.currentConfig["ALLOW_AUTO_EMBED"] = 0
            self.currentConfig["FUNCTION_PARAM"] = 0
            self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
            self.currentConfig["SPACING_LAYOUT_VERT"] = 0

            #Mullion used for intersections with other storefront
            self.currentConfig["midspanIntersectionMullion"] = self.system_name + "_Post"

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
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.system_name + "_OneBy"
            self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.system_name + "_OneBy"
            self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.system_name + "_DeflectionHead-1"
            self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
            self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
            self.currentConfig["ALLOW_AUTO_EMBED"] = 0
            self.currentConfig["FUNCTION_PARAM"] = 0
            self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
            self.currentConfig["SPACING_LAYOUT_VERT"] = 0

            #Mullion used for intersections with other storefront
            self.currentConfig["midspanIntersectionMullion"] = self.system_name + "_Post"

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
            self.currentConfig["currentSystem"] = self.system_name
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
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = self.system_name + "_Intermediate-1"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = self.system_name + "_Intermediate-1-Offset"
            self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = self.system_name + "_Intermediate-2"
            self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = self.system_name + "_Post"
            self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = self.system_name + "_Intermediate-1"
            self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = self.system_name + "_Sill-Center"
            self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = self.system_name + "_DeflectionHead-1"
            self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_MODE-Center"
            self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
            self.currentConfig["ALLOW_AUTO_EMBED"] = 0
            self.currentConfig["FUNCTION_PARAM"] = 0
            self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
            self.currentConfig["SPACING_LAYOUT_VERT"] = 0

            #Mullion used for intersections with other storefront
            self.currentConfig["midspanIntersectionMullion"] = self.system_name + "_Post"

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

        def storefront_save_config(self):
            # select storefront system
            if self.system_name == 'Elite':
                self.Elite()
            elif self.system_name == 'JEB':
                self.JEB()
            elif self.system_name == 'Extravega':
                self.Extravega()
            elif self.system_name == 'MODE':
                self.MODE()

            #Save any other configs selected previously selected by the user.
            if user_configs:
                for key in user_configs.keys():
                    self.currentConfig[key] = user_configs[key]

            self.json_save_config()            

    class FamilyOption(IFamilyLoadOptions): # where does IFamilyLoadOptions come from???
        def __init__(self):
            pass

        def OnFamilyFound(self, familyInUse, overwriteParameterValues):
            overwriteParameterValues = True
            familyInUse = True
            return(True)

        def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
            familyInUse = True
            return(True)
        
        # THESE WERE ALSO MOVED FROM storefront_configuration
        # originally from storefront_system_configs.py  
        def storefront_load_families(self, _quickLoad):
            familyDict = self.familiesToLoad

            #check if families are already loaded
            familyDict.update(self.check_family_dict(familyDict, quickLoad=_quickLoad))        

            # load families 
            for symbolAndTypes in familyDict.values():
                if not symbolAndTypes["Symbol"]:
                    try:
                        t = Transaction(self.doc, "Load Families")
                        t.Start()
                        for famName, symbolAndTypes in familyDict.items():
                            if not symbolAndTypes["Symbol"]:
                                path =  "{0}{1}.rfa".format(self.familyDirectory, famName)
                                familyLoaded = clr.Reference[Autodesk.Revit.DB.Family]()
                                loaded = self.doc.LoadFamily(path, familyLoaded)
                                if loaded:
                                    print("FAMILY: {0}...LOADED".format(familyLoaded.Name))
                                    familyLoadedSymbols = [i for i in familyLoaded.GetFamilySymbolIds()]
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
                        pass

            familyDict.update(self.check_family_dict(familyDict, quickLoad=_quickLoad))
            self.currentConfig["families"] = familyDict

            return(familyDict)
        
        def family_symbol_and_types_from_family(self, familyLoaded):
            """
            Takes a family and builds a dictionary of its symbol and types.
            """
            self.doc = __revit__.ActiveUIDocument.Document
            try:
                symbolIds = list(familyLoaded.GetFamilySymbolIds())
                familySymbol = self.doc.GetElement(symbolIds[0])
                familyName = familySymbol.Family.Name
                if not familySymbol.IsActive:
                    familySymbol.Activate()

                # template dict
                returnDict = {familyName: {"Symbol": None, "Types": {}}}

                # set family symbol
                returnDict[familyName]["Symbol"] = familySymbol.Id.IntegerValue
                # load types if they exist into the dict
                if len(symbolIds)>1:
                    for symbolId in symbolIds:
                        symbol = self.doc.GetElement(symbolId)
                        symbolName = symbol.LookupParameter("Type Name").AsString()
                        returnDict[familyName]["Types"].update({symbolName: symbolId.IntegerValue})
                else:
                    returnDict[familyName]["Types"].update({familyName: symbolIds[0].IntegerValue})
                return returnDict
            except Exception as inst:
                OutputException(inst)

        def check_family_dict(self, checkDict, quickLoad=False):
            """
            Checks the dictionary against the document and determines if it already was loaded.
            """
            self.doc = __revit__.ActiveUIDocument.Document
            try:
                for famName, symbolAndTypes in checkDict.items():
                    famFound = False
                    for familyId in GetAllElements(self.doc, None, Autodesk.Revit.DB.Family):
                        family = self.doc.GetElement(familyId)
                        if famName.lower() in family.Name.lower():
                            famFound = True
                            if not quickLoad:
                                print ("FAMILY: " + family.Name + "...ALREADY LOADED")
                            checkDict.update(self.family_symbol_and_types_from_family(family))
                            break
                    if not famFound:
                        checkDict.update({famName: {"Symbol": None, "Types": {}}})
                return checkDict
            except Exception as inst:
                print(inst)        

        def check_config_uptodate(self):
            """
            Used to check the saved config file to the current working document
            if they dont match then it promps you to set the config properly for
            the current document.
            """
            # Save when the config was set.
            projectInfo = self.doc.ProjectInformation
            projectId = projectInfo.Id.IntegerValue
            projectName = None
            for p in projectInfo.Parameters:
                if p.Definition.Name == "Project Name":
                    projectName = p.AsString()

            todaysDate = str(dt.Today.Month)+"-"+str(dt.Today.Day)+"-"+str(dt.Today.Year)

            configProjectName = self.currentConfig["projectName"]
            configProjectId = self.currentConfig["projectId"]
            configDate = self.currentConfig["configDate"]

            if ((projectName != configProjectName or projectId != configProjectId)
                or (projectId == configProjectId and todaysDate != configDate)):
                self.storefront_set_config()
            else:
                self.storefront_load(True)
            return(None)        
        
    class Method3:
        def __init__(self, system_name, userConfigs):
            pass
        
        def GetMullionTypes(self):
            #-----------------------CREATE MULLION TYPES------------------------#

            #mulliontypes that will be duplicated and assigned correct profiles
            templateMullion = None
            templateQuadMullion = None

            if quadMullionDict.keys() and mullionDict.keys():
                print("LOADING MULLIONS...")
                #creates mullions that are needed, both rectangular and quad.
                with rpw.db.Transaction("Create Mullions"):

                    mullionTypeNames = mullionDict.keys()
                    #Creates Rectangualr Mullions
                    for profileName in profileDict.keys():

                        #Ensure you're only creating mullion types for the selected system
                        if self.selectedSystem.lower() == profileName.split("_")[0].lower():

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
                        if self.selectedSystem.lower() == profileName.split("_")[0].lower():

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
            else: 
                if not quadMullionDict.keys() or not mullionDict.keys():
                    Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Please check the 'Curtain Wall Mullions' in the Project Browser and ensure you have at least (1) Quad Mullion type & (1) Rectangular Mullion type. Right click on them to create a 'New Type' if needed.")
                    sys.exit()
                    

        def GetCurtaiWallTypes(self):
            if quadMullionDict.keys() and mullionDict.keys():
                print("LOADING CURTAIN WALLS...")
                #creates mullions that are needed, both rectangular and quad.
                with rpw.db.Transaction("Create Curtain Wall"):            
                    #-----------------------CREATE CURTAIN WALL TYPES------------------------#
                    # Create curtain wall system for each system if they dont exist
                    templateCW = None
                    for key, value in wallTypeDict.items():
                        wt = self.doc.GetElement(value)
                        if str(wt.Kind) == "Curtain":
                            templateCW = wt
                            break
        
                    curtainWallNamePrefix = "I-Storefront-"
        
                    cwName = selectedSystem
                    cwType = curtainWallNamePrefix+cwName
                    if not any( cwType == s for s in wallTypeDict.keys()):
                        newCW = templateCW.Duplicate(cwType)
                    else:
                        newCW = self.doc.GetElement(wallTypeDict[cwType])
        
                    #newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(mullionDict[cwName+"_Post"])
                    newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_VERT"]])
                    newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER1_VERT"]])
                    newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER2_VERT"]])
                    newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_HORIZ"]])
                    newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER1_HORIZ"]])
                    newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER2_HORIZ"]])
                    newCW.get_Parameter(BuiltInParameter.AUTO_PANEL_WALL).Set(panelTypeDict[currentConfig["AUTO_PANEL_WALL"]])
                    newCW.get_Parameter(BuiltInParameter.AUTO_JOIN_CONDITION_WALL).Set(currentConfig["AUTO_JOIN_CONDITION_WALL"]) # vertical continuous
                    newCW.get_Parameter(BuiltInParameter.ALLOW_AUTO_EMBED).Set(currentConfig["ALLOW_AUTO_EMBED"])
                    newCW.get_Parameter(BuiltInParameter.FUNCTION_PARAM).Set(currentConfig["FUNCTION_PARAM"])
                    newCW.get_Parameter(BuiltInParameter.SPACING_LAYOUT_HORIZ).Set(currentConfig["SPACING_LAYOUT_HORIZ"])
                    newCW.get_Parameter(BuiltInParameter.SPACING_LAYOUT_VERT).Set(currentConfig["SPACING_LAYOUT_VERT"])
                print("...CURTAIN WALLS LOADED")

            else: 
                if not quadMullionDict.keys() or not mullionDict.keys():
                    Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Please check the 'Curtain Wall Mullions' in the Project Browser and ensure you have at least (1) Quad Mullion type & (1) Rectangular Mullion type. Right click on them to create a 'New Type' if needed.")
                    sys.exit()

        def LoadFamilies(self, names, directory):
            """ 
            BROUGHT OVER FROM SF2_Utility

            Loads families given a a list of family names and a directory.
            Returns a list of family Element Ids. 
            """
            familyIds = []
            with rpw.db.Transaction("Load Family"): 
                for famName in names:
                    path =  directory + famName
                    familyLoaded = clr.Reference[Autodesk.Revit.DB.Family]()
                    loaded = self.doc.LoadFamily(path, self.FamilyOption(), familyLoaded)

                    if loaded:
                        print("...loaded")
                        print("FAMILY: {0}...LOADED".format(familyLoaded.Name))
                        familyIds.append(familyLoaded.Id)
                        ActivateFamilySymbols(familyLoaded)
            return(familyIds)
        
        
    #_ _ _ _ _ _ _ _ _ _YOUNGEST CHILD_ _ _ _ _ _ _ _ _ _#

    class storefront_load(storefront_configuration, FamilyOption, Method3):
        def __init__(self, doc, system_name=None, userConfigs=None, familyInUse=None, overwriteParameterValues=None):
            # polymorphic classes
            storefront_configuration.__init__(self, system_name, userConfigs)
            FamilyOption.__init__(self) # , familyInUse, overwriteParameterValues
            Method3.__init__(self, system_name, userConfigs)

            # input parameters
            self.selectedSystem = None # fix this
            self.system_name = system_name
            self.userConfigs = userConfigs

            # WHO CALLS LOAD FAMILIES
            self.doc = doc
            self.version = __revit__.Application.VersionNumber.ToString()

            # FAMILIES SAVED HERE
            self.familyDirectory = r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\Storefront 2.panel\0 Lib\Families" # ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib\Families")

        def Run_storefront_load(self):
            """
            Creates curtain wall types and loads families.
            """

            ##Load the options object
            #storefrontConfig = storefront_configuration()

            ##Selects which to load
            #storefrontConfig.storefront_set_config() # requires options from gui

            # grab the current config
            #currentConfig = storefrontConfig.currentConfig

            #self.selectedSystem= currentConfig["currentSystem"]

            #Load the necessary families
            print("LOADING FAMILIES...")
            familiesToLoadPath = os.listdir(self.familyDirectory)
            self.LoadFamilies(familiesToLoadPath, self.familyDirectory)

            # gather dicts of what exists in the project
            profileDict = SF2_Utility.GetProfileDict("I-Profile-Storefront-Mullion")
            wallTypeDict = SF2_Utility.GetWallTypeDict()
            mullionDict = SF2_Utility.GetMullionTypeDict()
            panelTypeDict = SF2_Utility.GetWindowTypeDict()
            quadMullionDict = SF2_Utility.GetQuadMullionTypeDict()
            createMullions = {}

            # create mullion types
            self.GetMullionTypes()

            # create curtain wall types
            self.GetCurtainWallTypes()
        
        def Run_Config(self):
            pass



    def TestMain():
        doc = __revit__.ActiveUIDocument.Document

        # select system_name
        system_name = "Elite"

        familyObj = storefront_load(doc)
        familyObj.Run_SFLoadFamilies()


    if __name__ == "__main__":
        TestMain()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())    