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
    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System.Drawing')
    from System.Windows.Forms import SaveFileDialog
    from System.Drawing import *
    from System.Drawing import Point
    from System.Windows.Forms import Application, Button, CheckBox, Form, Label
    from System.Collections.Generic import List, IEnumerable
    from System import Array    
    
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
    from Autodesk.Revit.UI import *
    from Autodesk.Revit.DB import *
    import tempfile

    rpwLib = r"pyWestExtensions\pyWest.extension\pyWest.tab\0 Lib\revitpythonwrapper-master" # common lib folder
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 6, rpwLib))
    import rpw
    from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
    
    import SF2_Utility
    reload(SF2_Utility)

    #######################
    ## MAIN FAMILY CLASS ##
    #######################
    class Families:      
        #######################
        ## JSON SAVE METHODS ##
        #######################
        def json_save_config(self): # this is only used by storefront_save_config()
            with open(self.defaultConfigPath, 'w') as outfile:
                json.dump(self.currentConfig, outfile)
        def json_load_config(self): # this is only used by SF2_Families Parent Class
    
            if os.path.exists(self.defaultConfigPath):
                with open(self.defaultConfigPath) as readFile:
                    jsonstring = readFile.read()
            else: 
                with open(os.path.dirname(__file__) + "\\default_settings.json") as readFile:
                    jsonstring = readFile.read()
    
            jsonstring = jsonstring.replace("null", "0", 100)
            jsonData = json.loads(jsonstring)
            self.currentConfig.update(jsonData) # update is a python dictionary function
        ############################        
        ## METHODS USED BY SF_GUI ##
        ############################
        def storefront_load_families(self, _quickLoad): # this is only used by SF_GUI and check_config_uptodate()
            """ 
            Loads families into a family dictionary.
            If quickLoad = True, it will only search for families and not load.
            This is useful assuming the families were loaded already.
            Otherwise families will be searched and loaded.
            """
            familyDict = self.familiesToLoad
    
            #check if families are already loaded
            familyDict.update(self.check_family_dict(familyDict, quickLoad=_quickLoad))
    
            # load families 
            for symbolAndTypes in familyDict.values():
                if not symbolAndTypes["Symbol"]:
                    t = Transaction(self.doc, "Load Families")
                    try:
                        t.Start()
                        for famName, symbolAndTypes in familyDict.items():
                            if not symbolAndTypes["Symbol"]:
                                #path =  self.familyDirectory + famName + ".rfa"
                                path = "{0}\{1}.rfa".format(self.familyDirectory, famName)
                                familyLoaded = clr.Reference[Autodesk.Revit.DB.Family]()
                                loaded = self.doc.LoadFamily(path, familyLoaded)
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
                        t.RollBack() # this is undo
                        pass
            familyDict.update(self.check_family_dict(familyDict, quickLoad=_quickLoad))
            self.currentConfig["families"] = familyDict
            return(familyDict)        
        def storefront_save_config(self, system_name=None, user_configs=None): # this is only used by SF_GUI - missleading it writes the currentConfig
            """
            Each system is defined here by their profile dimensions.
            and some other system specific features. These values
            are used throughout the storefront engine by calling the
            storefront_options() class. 
            
            """
            if system_name:
    
                
                if "Elite" in system_name: 
    
                    #----------------------System Configurations----------------------#
                    self.currentConfig["currentSystem"] = "Elite"
                    self.currentConfig["fullSillHeight"] = 0.0
    
                    if "Lower Infill" in system_name:
                        self.currentConfig["hasLowerInfill"] = True
                    else:
                        self.currentConfig["hasLowerInfill"] = False
    
                    #Regional Settings
    
                    if "LATAM" in system_name:
    
                        self.currentConfig["transomHeight"] = 8.2021
                        self.currentConfig["partialSillHeight"] = 2.49344 - (1.75/12)
    
                    else:
                        self.currentConfig["transomHeight"] = 8 + (1.75/12)
                        self.currentConfig["partialSillHeight"] = 2 + (3.25/12)
    
    
                    self.currentConfig["isFramed"] = True
                    self.currentConfig["deflectionHeadType"] = 0
    
                    #Used as a factor for detecting adjacent mullions for door frames. 
                    self.currentConfig["closeMullionDetectionFactor"] = 1.0
    
                    #To make sure that the mullion family names are correctly set.
                    system_name = "Elite"
    
                    #----------------------Curtain Panel Options------------------------#
                    self.currentConfig["panelEmpty"] = "Empty Panel-Empty Panel"
                    self.currentConfig["panelhasLowerInfill"] ="Solid Center Panel-Solid Center Panel"
                    self.currentConfig["panelGlazedCenter"] = "Glazed-Panel_Generic-Center"
                    self.currentConfig["panelGlazedOffset"] = "Glazed-Panel_Generic-Center"
                    self.currentConfig["panelGlazedDouble"] = "Glazed-Panel_Generic-Center"
    
                    #----------------------Curtain Wall Settings------------------------#
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = system_name + "_Intermediate"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = system_name + "_Intermediate"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = system_name + "_Intermediate"
                    self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = system_name + "_Sill"
                    self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = system_name + "_Sill"
                    self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = system_name + "_OneBy"
                    self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
                    self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
                    self.currentConfig["ALLOW_AUTO_EMBED"] = 0
                    self.currentConfig["FUNCTION_PARAM"] = 0
                    self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
                    self.currentConfig["SPACING_LAYOUT_VERT"] = 0
    
                    #Mullion used for intersections with other storefront
                    self.currentConfig["midspanIntersectionMullion"] = system_name + "_Post"
    
                    #Special conditions where wall types relace the default sill to another special type. 
                    self.currentConfig["specialSillConditions"] = None
                    self.currentConfig["specialHorizontalMullions"] = None
    
                    #----------------------Mullion Joining Configuration----------------------#
                    self.currentConfig["mullionContinuousVerticalAtDoorTop"] = True
                    self.currentConfig["mullionContinuousVerticalAtDoorBottom"] = True
                    self.currentConfig["mullionContinuousVerticalAtEndsTop"] = True
                    self.currentConfig["mullionContinuousVerticalAtEndsBottom"] = True
                    self.currentConfig["mullionContinuousVerticalIntermediateTop"] = True
                    self.currentConfig["mullionContinuousVerticalIntermediateBottom"] = True
                    self.currentConfig["mullionContinuousHorizontalHeadAtDoor"] = False
    
                    #----------------------Door frame settings----------------------#
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
                    
                    #----------------------Standard lengths for mullions----------------------#
    
                    self.currentConfig["systemStandardVerticals"] = {"post" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12, "STANDARD 05" : 58.5/12, "STANDARD 06" : 70.5/12, "STANDARD 07" : 82.5/12, "STANDARD 08" : 94.5/12},
                                                                    "intermediate" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12, "STANDARD 05" : 58.5/12, "STANDARD 06" : 70.5/12, "STANDARD 07" : 82.5/12, "STANDARD 08" : 94.5/12},
                                                                    "doorframe" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12},
                                                                    "end" : {"STANDARD 01" : 85.75/12, "STANDARD 02" : 97.75/12, "STANDARD 03" : 109.75/12, "STANDARD 04" : 121.75/12, "STANDARD 05" : 58.5/12, "STANDARD 06" : 70.5/12, "STANDARD 07" : 82.5/12, "STANDARD 08" : 94.5/12}}
    
                    self.currentConfig["systemStandardHorizontals"] = {"sill" : {"STANDARD 01" : 36/12, "STANDARD 02" : 48/12}}
    
                    #---------------------- Panel Corrections for Cutlists ----------------------#
                    """
                    Used to correct for simplified curtain wall models where mullions are excluded for expediency
                    but results in panel sizes that need to be corrected to reflect reality
                    """
                    self.currentConfig["panelCorrections"] = {"horizontalEnd" :  0.25/12,
                                                                "horizontalIntermediate": 0.25/12,
                                                                "horizontalButtJoint" : -0.0625/12, 
                                                                "verticalSill" : 0.25/12,
                                                                "verticalHead" : 0.25/12}
    
                    #---------------------- Special Cutlist Parameters ----------------------#
                    """
                    Each system requires different ways of exporting conditions, below controls what should be
                    detected etc based on the system type
                    """                                            
                    self.currentConfig["cutlistDetectEndConditions"] = False
    
                
                elif "JEB" in system_name:
    
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
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = system_name + "_Intermediate"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = system_name + "_Intermediate"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = system_name + "_Intermediate"
                    self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = system_name + "_OneBy-CableTray"
                    self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = system_name + "_Sill"
                    self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = system_name + "_DeflectionHead-2"
                    self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
                    self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
                    self.currentConfig["ALLOW_AUTO_EMBED"] = 0
                    self.currentConfig["FUNCTION_PARAM"] = 0
                    self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
                    self.currentConfig["SPACING_LAYOUT_VERT"] = 0
    
                    #Mullion used for intersections with other storefront
                    self.currentConfig["midspanIntersectionMullion"] = system_name + "_Post"
    
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
    
    
    
                elif system_name ==  "Extravega": 
    
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
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = system_name + "_OneBy"
                    self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = system_name + "_OneBy"
                    self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = system_name + "_DeflectionHead-1"
                    self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_Generic-Center"
                    self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
                    self.currentConfig["ALLOW_AUTO_EMBED"] = 0
                    self.currentConfig["FUNCTION_PARAM"] = 0
                    self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
                    self.currentConfig["SPACING_LAYOUT_VERT"] = 0
    
                    #Mullion used for intersections with other storefront
                    self.currentConfig["midspanIntersectionMullion"] = system_name + "_Post"
    
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
    
                elif system_name ==  "MODE": 
    
                    #----------------------System configurations----------------------#
                    self.currentConfig["currentSystem"] = system_name
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
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT"] = system_name + "_Intermediate-1"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"] = system_name + "_Intermediate-1-Offset"
                    self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"] = system_name + "_Intermediate-2"
                    self.currentConfig["AUTO_MULLION_BORDER1_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_BORDER2_VERT"] = system_name + "_Post"
                    self.currentConfig["AUTO_MULLION_INTERIOR_HORIZ"] = system_name + "_Intermediate-1"
                    self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"] = system_name + "_Sill-Center"
                    self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"] = system_name + "_DeflectionHead-1"
                    self.currentConfig["AUTO_PANEL_WALL"] = "Glazed-Panel_MODE-Center"
                    self.currentConfig["AUTO_JOIN_CONDITION_WALL"] = 1
                    self.currentConfig["ALLOW_AUTO_EMBED"] = 0
                    self.currentConfig["FUNCTION_PARAM"] = 0
                    self.currentConfig["SPACING_LAYOUT_HORIZ"] = 0
                    self.currentConfig["SPACING_LAYOUT_VERT"] = 0
    
                    #Mullion used for intersections with other storefront
                    self.currentConfig["midspanIntersectionMullion"] = system_name + "_Post"
    
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
    
                
            #Save any other configs selected previously selected by the user.
            if user_configs:
                for key in user_configs.keys():
                    self.currentConfig[key] = user_configs[key]
            
            self.json_save_config()
        
        def family_symbol_and_types_from_family(self, familyLoaded): # this is only used by check_family_dict()
            """
            Takes a family and builds a dictionary of its symbol and types.
            """
            doc = __revit__.ActiveUIDocument.Document
            try:
                symbolIds = list(familyLoaded.GetFamilySymbolIds())
                familySymbol = doc.GetElement(symbolIds[0])
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
                        symbol = doc.GetElement(symbolId)
                        symbolName = symbol.LookupParameter("Type Name").AsString()
                        returnDict[familyName]["Types"].update({symbolName: symbolId.IntegerValue})
                else:
                    returnDict[familyName]["Types"].update({familyName: symbolIds[0].IntegerValue})
                return returnDict
            except Exception as inst:
                OutputException(inst)
    
        def check_family_dict(self, checkDict, quickLoad=False): # this is only used by storefront_load_families()
            """
            Checks the dictionary against the document and determines if it already was loaded.
            """
            doc = __revit__.ActiveUIDocument.Document
            try:
                for famName, symbolAndTypes in checkDict.items():
                    famFound = False
                    for familyId in SF2_Utility.GetAllElements(doc, None, Autodesk.Revit.DB.Family):
                        family = doc.GetElement(familyId)
                        if famName.lower() in family.Name.lower():
                            famFound = True
                            if not quickLoad:
                                print("FAMILY: " + family.Name + "...ALREADY LOADED")
                            checkDict.update(self.family_symbol_and_types_from_family(family))
                            break
                    if not famFound:
                        checkDict.update({famName: {"Symbol": None, "Types": {}}})
                return checkDict
            except Exception as inst:
                print(inst)          
        ###############################
        ## METHODS USED BY SF_Engine ##
        ###############################
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
        ##############################
        ## ACTUAL FAMILY LOADING??? ##
        ##############################
        def LoadFamilies(self, names, directory):
            """ 
            Loads families given a a list of family names and a directory.
            Returns a list of family Element Ids. 
            """
            familyIds = []
            with rpw.db.Transaction("Load Family"): 
                for famName in names:
                    path =  directory + famName
                    familyLoaded = clr.Reference[Autodesk.Revit.DB.Family]()
                    try:
                        loaded = self.doc.LoadFamily(path, FamilyOptions(), familyLoaded)
                        if loaded:
                            print("...loaded")
                            print("FAMILY: {0}...LOADED".format(familyLoaded.Name))
                            familyIds.append(familyLoaded.Id)
                            self.ActivateFamilySymbols(familyLoaded)
                    except:
                        print("{0} family did not load".format(famName))                  
            
            return(familyIds)
        def ActivateFamilySymbols(self, family):
            familyLoadedSymbols = list(family.GetFamilySymbolIds())
            if familyLoadedSymbols:
                for symbolId in familyLoadedSymbols:
                    symbol = self.doc.GetElement(symbolId)
                    if not symbol.IsActive:
                        symbol.Activate()
            return(None)        
        ##########################
        ## CURTAIN WALL METHODS ##
        ##########################
        def LoadCurtainWalls(self, currentConfig, selectedSystem, profileDict, wallTypeDict, mullionDict, panelTypeDict, quadMullionDict):
            # THIS WAS ABLE TO MOSTLY RUN WITHOUT SELECTEDSYSTEM ASSIGNED....FAMILIES ARE LOADED OUTSIDE OF HERE? THE OTHER JUNK MAYBE
            
            # THESE ARE NOT USED!
            #mulliontypes that will be duplicated and assigned correct profiles
            templateMullion = None
            templateQuadMullion = None            
            
            print("LOADING CURTAIN WALLS...")
            #creates mullions that are needed, both rectangular and quad.
            with rpw.db.Transaction("Create Curtain Wall"):
                mullionTypeNames = mullionDict.keys()
                print("Mullion Type Names: {0}".format(mullionTypeNames))
                
                #Creates Rectangualr Mullions
                for profileName in profileDict.keys():
                    #Ensure you're only creating mullion types for the selected system
                    if selectedSystem.lower() == profileName.split("_")[0].lower():
                        #Create a new mullion type if needed from a duplicate.
                        if not any(profileName == s for s in mullionTypeNames):
                            newMullionType = self.doc.GetElement(mullionDict[mullionDict.keys()[0]]).Duplicate(profileName)
                            newMullionType.get_Parameter(BuiltInParameter.MULLION_PROFILE).Set(profileDict[profileName])
                            mullionDict[profileName] = newMullionType.Id
    
                        #Otherwise grab it from the mullion dictionary if it exists.
                        else:
                            newMullionType = self.doc.GetElement(mullionDict[profileName])
    
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
                                newMullionType = self.doc.GetElement(quadMullionDict[quadMullionDict.keys()[0]]).Duplicate(profileName)
                                depth1 = 0
                                depth2 = 0
    
                                for p in self.doc.GetElement(profileDict[profileName]).Parameters:
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
                    wallType = self.doc.GetElement(value)
                    if str(wallType.Kind) == "Curtain":
                        templateCurtainWall = wallType
                        break
    
                curtainWallNamePrefix = "I-Storefront-"
    
                cwName = selectedSystem
                print("Curtain Wall System: {0}".format(cwName))
                curtainWallType = curtainWallNamePrefix+cwName
                if not any( curtainWallType == s for s in wallTypeDict.keys()):
                    newCurtainWall = templateCurtainWall.Duplicate(curtainWallType)
                else:
                    newCurtainWall = self.doc.GetElement(wallTypeDict[curtainWallType])
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_VERT"]])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER1_VERT"]])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER2_VERT"]])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_HORIZ"]])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER1_HORIZ"]])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER2_HORIZ"]])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_PANEL_WALL).Set(panelTypeDict[currentConfig["AUTO_PANEL_WALL"]])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.AUTO_JOIN_CONDITION_WALL).Set(currentConfig["AUTO_JOIN_CONDITION_WALL"]) # vertical continuous
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.ALLOW_AUTO_EMBED).Set(currentConfig["ALLOW_AUTO_EMBED"])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.FUNCTION_PARAM).Set(currentConfig["FUNCTION_PARAM"])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.SPACING_LAYOUT_HORIZ).Set(currentConfig["SPACING_LAYOUT_HORIZ"])
                except:
                    pass
                try:
                    newCurtainWall.get_Parameter(BuiltInParameter.SPACING_LAYOUT_VERT).Set(currentConfig["SPACING_LAYOUT_VERT"])
                except:
                    pass
            print("...CURTAIN WALLS LOADED")
        def CorrectMissingCurtainWallTypes(self):
            """
            THIS WHOLE PART NEEDS TO BE FIXED. CREATE NEW TYPE WHERE FAMILY TYPE DOES NOT EXIST
            """
            if not quadMullionDict.keys() or not mullionDict.keys():
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Please check the 'Curtain Wall Mullions' in the Project Browser and ensure you have at least (1) Quad Mullion type & (1) Rectangular Mullion type. Right click on them to create a 'New Type' if needed.")
                sys.exit()            
    
    ###################################
    ## THIS DOES SOMETHING BUT WHAT? ##
    ###################################
    # this is only used by LoadFamilies()
    class FamilyOptions(IFamilyLoadOptions):
        """
        IFamilyLoadOptions comes from the RevitAPI
        """
        def OnFamilyFound(self, familyInUse, overwriteParameterValues):
            overwriteParameterValues = True
            familyInUse = True
            return(True)
        def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
            familyInUse = True
            return(True)
    
    ##################
    ## PARENT CLASS ##
    ##################
    class ParentClass(Families, FamilyOptions):
        def __init__(self):
            """
            The input parameter for this parent class is defaulted
            to None b/c in the GUI module access to family options are
            needed and the since the storefrontConfig is provided by the
            GUI we need to avoid circular logic.
            """
            # global parameters
            self.doc = __revit__.ActiveUIDocument.Document
            self.app = __revit__.Application
            self.version = __revit__.Application.VersionNumber.ToString()
            self.uidoc = __revit__.ActiveUIDocument
            self.currentView = self.uidoc.ActiveView
            
            # derived parameters
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
                                  "transomHeight":None,
                                  "hasLowerInfill":None,
                                  "deflectionHeadType": None,
                                  "splitWallType":None,
                                  "splitOffset":None,
                                  "isFramed":None,
                                  "profiles":None,
                                  "families": self.familiesToLoad,
                                  "spacingType":None,
                                  "storefrontPaneWidth":None}
            self.availableSystems = {"Elite":"Elite",
                                     "Elite - Lower Infill":"Elite - Lower Infill",
                                     "Elite - LATAM":"Elite - LATAM",
                                     "JEB":"JEB",
                                     "Extravega":"Extravega",
                                     "MODE":"MODE"}
            self.heightOptions = {"Elite : 7' - 1.75''": 7 + (1.75/12),
                                  "Elite : 8' - 1.75''": 8 + (1.75/12),
                                  "Elite : 2500mm (LATAM)" : 98.4252/12,
                                  "JEB : 2440mm - (2520mm BO Head)" : 99.2126/12,
                                  "Extravega : 2514mm - (2514mm Head) " : 98.38583/12,
                                  "MODE : 8' - 0''" : 8.0} 
                                  # Extravega has a 15mm tolerance
            self.divisionOptions = {"Fixed Distance": 1,
                                    "Even - Even": 0}
            self.panelWidthOptions = {"1000mm": 39.3701/12,
                                      "1200mm": 47.24409/12,
                                      "1375mm": 54.13386/12,
                                      "4'- 0''": 4 + (1.75/12),
                                      "4'- 6''": 4 + (7.75/12)}            
            
            
            
            self.defaultConfigPath = os.path.join(tempfile.gettempdir(), "storefront_default_config.json")
            self.familyDirectory = r"C:\Users\aluna\Documents\WeWork Code\pyWestExtensions\pyWest.extension\pyWest.tab\Storefront 2.panel\0 Lib\Families"
            self.splitTypeOptions = {"Fixed - 6 Inches": 6.0/12,
                                     "Fixed - 12 Inches": 12.0/12,
                                     "Fixed - 150mm": 5.90551/12, 
                                     "Fixed - 300mm": 11.811/12, 
                                     "Optimized - variable": "OPTIMIZED"}
            
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
            
            # load storefront configurations if they exist, otherwise write the file
            self.json_load_config()
            print("json_load_config is : {0}".format(self.json_load_config))
            
            # instantiate classes in this file - order of operations mattters
            Families.__init__(self)
            FamilyOptions.__init__(self)
            
        def Run_SF2_Families(self, addSomething=None):
            """
            Creates curtain wall types and loads families.
            
            Running this will force the running of all the methods and stuff above...
            
            CURRENTCONFIG HERE MIGHT BE A FUCKING PROBLEM
            """
            # grab outputs from windows form
            currentConfig = self.currentConfig
            selectedSystem = currentConfig["currentSystem"]
            
            ##################################################################################################################################
            ## THIS IS FAILING HARD, FIND OUT WHY ############################################################################################
            ##################################################################################################################################
            #Load the necessary families - THIS LOADS FAMILIES, BUT NOT THE FAMILIES I THOUGHT
            print("LOADING FAMILIES...")
            self.familiesToLoad = os.listdir(self.familyDirectory)
            print(self.familiesToLoad)
            #self.LoadFamilies(self.familiesToLoad, self.familyDirectory)        
            
            # gather dictionaries of what exists in the project
            # (objects are collected then placed in dictionaries)
            profileDict = SF2_Utility.GetProfileDict("I-Profile-Storefront-Mullion")
            wallTypeDict = SF2_Utility.GetWallTypeDict()
            mullionDict = SF2_Utility.GetMullionTypeDict(self.doc)
            panelTypeDict = SF2_Utility.GetWindowTypeDict()
            quadMullionDict = SF2_Utility.GetQuadMullionTypeDict()
            createMullions = {}
            
            ##################################################################################################################################
            ## SO IS THIS EVERYTHING IS FN BROKEN ############################################################################################
            ##################################################################################################################################            
            # create mullion types
            if quadMullionDict.keys() and mullionDict.keys():
                self.LoadCurtainWalls(currentConfig, selectedSystem, mullionDict, wallTypeDict, mullionDict, panelTypeDict, quadMullionDict)
            else:
                self.CorrectMissingCurtainWallTypes()

except:
    # print traceback in order to debug file
    print(traceback.format_exc()) 