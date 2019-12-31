import json
import sys
import os
import System
from System import DateTime as dt

sys.path.append(os.path.dirname(os.path.realpath(__file__))) # these files and the one referenced below should be in the same directory
from SF_Refactored_utils import *

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
import tempfile # where the fuck does this come from?
print("this is the printout for tempfile: {0}".format(tempfile))

sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\Storefront 2.panel\0 Lib\revitpythonwrapper-master")
import rpw


class storefront_options:
    """
    IT LOOKS LIKE CONFIGURATIONS ARE SHARE USING JSON FILES, READ AND WRITE
    """
    def __init__(self):
        pass

    def storefront_save_config(self, system_name=None, user_configs=None):
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

    def storefront_load_families(self, _quickLoad):
        """ 
        #Loads families into a family dictionary.
        #If quickLoad = True, it will only search for families and not load.
        #This is useful assuming the families were loaded already.
        #Otherwise families will be searched and loaded.
        """
        doc = __revit__.ActiveUIDocument.Document
        version = __revit__.Application.VersionNumber.ToString()
        
        # WHERE ARE THE FAMILIES?
        familyDirectory = os.path.dirname(os.path.realpath(__file__)).replace("lib","families\\")
        familyDict = self.familiesToLoad

        #check if families are already loaded
        familyDict.update(self.check_family_dict(familyDict, quickLoad=_quickLoad))

        # load families 
        for symbolAndTypes in familyDict.values():
            if not symbolAndTypes["Symbol"]:
                try:
                    t = Transaction(doc, "Load Families")
                    t.Start()
                    for famName, symbolAndTypes in familyDict.items():
                        if not symbolAndTypes["Symbol"]:
                            path =  familyDirectory + famName + ".rfa"
                            familyLoaded = clr.Reference[Autodesk.Revit.DB.Family]()
                            loaded = doc.LoadFamily(path, familyLoaded)
                            if loaded:
                                print("FAMILY: {0}...LOADED".format(familyLoaded.Name))

                                familyLoadedSymbols = list(familyLoaded.GetFamilySymbolIds())
                                if familyLoadedSymbols:
                                    for symbolId in familyLoadedSymbols:
                                        symbol = doc.GetElement(symbolId)
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

    def check_family_dict(self, checkDict, quickLoad=False):
        """
        Checks the dictionary against the document and determines if it already was loaded.
        """
        doc = __revit__.ActiveUIDocument.Document
        try:
            for famName, symbolAndTypes in checkDict.items():
                famFound = False
                for familyId in GetAllElements(doc, None, Autodesk.Revit.DB.Family):
                    family = doc.GetElement(familyId)
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
        projectInfo = doc.ProjectInformation
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
            self.storefront_load_families(True)
        return(True)

    # replace these with my data exchange tools for consistency accross all plugins
    def json_save_config(self):
        with open(self.defaultConfigPath, 'w') as outfile:
            json.dump(self.currentConfig, outfile)
        return(True)

    def json_load_config(self):
        if os.path.exists(self.defaultConfigPath):
            with open(self.defaultConfigPath) as readFile:
                jsonstring = readFile.read()
        else: 
            with open(os.path.dirname(__file__) + "\\default_settings.json") as readFile:
                jsonstring = readFile.read()

        jsonstring = jsonstring.replace("null", "0", 100)
        jsonData = json.loads(jsonstring)
        self.currentConfig.update(jsonData)
        return(True)
