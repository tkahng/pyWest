def json_save_config(defaultConfigPath, currentConfig):
    with open(defaultConfigPath, 'w') as outfile:
        json.dump(currentConfig, outfile)
def Elite():
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

def JEB():
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
def Extravega():
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
def MODE():
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
def storefront_save_config(self, system_name=None, user_configs=None):
    """
    Each system is defined here by their profile dimensions.
    and some other system specific features. These values
    are used throughout the storefront engine by calling the
    storefront_options() class.
    
    *
    All this method does is set the currentConfig variable
    to the exact settings that are needed for the selected
    storefront system.
    *
    
    this needs all the empty variable from families
    """
    if system_name:
        if "Elite" in system_name:
            Elite()
        elif "JEB" in system_name:
            JEB()
        elif system_name == "Extravega":
            Extravega()
        elif system_name ==  "MODE":
            MODE()
    
    #Save any other configs selected previously selected by the user.
    if user_configs:
        for key in user_configs.keys():
            self.currentConfig[key] = user_configs[key]
    
    # save the configuration written/chosen above to a json file
    self.json_save_config()
    
    
###############################################
## ARCHIVE OF STUFF I DONT THINK I WILL NEED ##
###############################################
# this is not used by anything
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
        print("LOOK AT LINE 205 OF THE CODE")
        self.storefront_load_families(True)

"""
class BuildWall:
    def __init__(self):
        pass
    def Build(self):
        #############################################
            #                  Build                   #
        #############################################
        print "RUNNING...DO NOT CLOSE WINDOW..."

        with rpw.db.TransactionGroup("Convert Wall", assimilate=True) as tg:

            #Adjust any parameters to the walltype before creation if needed.
            with rpw.db.Transaction("Adjust CW Parameters") as tx:
                SupressErrorsAndWarnings(tx)


                wtCW = self.doc.GetElement(self.wallTypeCW)
                if self.storefrontConfig.currentConfig["deflectionHeadType"] == 2:
                    wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-2"])
                elif self.storefrontConfig.currentConfig["deflectionHeadType"] == 1:
                    wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-1"])

            for storefrontObject in self.storefrontElevations:
                #pyrevit progress bar
                self.progressIndex += 1
                output = script.get_output()

                output.update_progress(self.progressIndex, len(self.storefrontElevations))

                hostElement = self.doc.GetElement(storefrontObject.HostElementIds[0])
                storefrontType = storefrontObject.SuperType

                baseConstraint = hostElement.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()

                locLine = storefrontObject.HostLine
                locLineStart = locLine.GetEndPoint(0)
                locLineEnd = locLine.GetEndPoint(1)

                gridIntersectionPostPoints = []

                wallHostId = storefrontObject.HostElementIds[0]
                wtName = self.doc.GetElement(wallHostId).Name

                newWall = None

                if str(hostElement.WallType.Kind) == "Basic":
                    #############################################
                    #                  Checks                   #
                    #############################################

                    #------------Interior Walls Edges------------#

                    locLine = storefrontObject.HostLine
                    locLineStart = locLine.GetEndPoint(0)
                    locLineEnd = locLine.GetEndPoint(1)

                    for intWallLine in self.interiorWallsLinesEdges:
                        intersection = RevitCurveCurveIntersection(locLine,intWallLine)

                        if intersection:
                            distToEnd = intersection.DistanceTo(locLineEnd) 
                            distToStart = intersection.DistanceTo(locLineStart) 

                            #If intersection is at the ends
                            if distToEnd < self.distTol:
                                storefrontObject.EndCondition = "OnGyp"
                                # If intersection is not at the surface of the edges of interior walls
                                if distToEnd > self.absoluteTol:
                                    storefrontObject.Line = Line.CreateBound(locLineStart, intersection)

                            elif distToStart < self.distTol:
                                storefrontObject.StartCondition = "OnGyp"
                                if distToStart > self.absoluteTol:
                                    storefrontObject.Line = Line.CreateBound(intersection, locLineEnd)

                    #----------Interior Walls Midspans-----------#
                    for intWallId in self.interiorWalls:
                        intWall = self.doc.GetElement(intWallId)
                        intWallLine = intWall.Location.Curve
                        intersection = RevitCurveCurveIntersection(locLine,intWallLine)
                        if intersection:
                            distToEnd = intersection.DistanceTo(locLineEnd) 
                            distToStart = intersection.DistanceTo(locLineStart) 
                            #If intersection is at the ends
                            if distToEnd > self.distTol and distToStart > self.distTol:
                                gridIntersectionPostPoints.append(intersection)




                    #------------------EC Walls------------------#

                    locLine = storefrontObject.HostLine
                    locLineStart = locLine.GetEndPoint(0)
                    locLineEnd = locLine.GetEndPoint(1)
                    obstructionEdges = self.columnsLinesEdges
                    if self.docEC:
                        obstructionEdges += self.columnsLinesEdgesEC
                        obstructionEdges += self.wallsLinesEdgesEC
                    if obstructionEdges:
                        for obstructionLine in obstructionEdges:
                            obstLineElevation = obstructionLine.GetEndPoint(0).Z
                            locLineStart = XYZ(locLineStart.X, locLineStart.Y, obstLineElevation)
                            locLineEnd = XYZ(locLineEnd.X, locLineEnd.Y, obstLineElevation)
                            locLineFlat = Line.CreateBound(locLineStart, locLineEnd)
                            intersection = RevitCurveCurveIntersection(locLineFlat,obstructionLine)
                            if intersection:
                                #ERROR: Hit Existing Condition
                                if intersection.DistanceTo(locLineEnd) < self.distTol:
                                    storefrontObject.EndCondition = "OnObstruction"
                                elif intersection.DistanceTo(locLineStart) < self.distTol:
                                    storefrontObject.StartCondition = "OnObstruction"


                    ####-------Storefront Intersections-------####

                    locLine = storefrontObject.HostLine
                    locLineStart = locLine.GetEndPoint(0)
                    locLineEnd = locLine.GetEndPoint(1)


                    #---------------Find Neighbors---------------#
                    #print storefrontObject.HostElementIds              
                    for neighbor in self.storefrontElevations:

                        if neighbor != storefrontObject:
                            neighborLocLine = neighbor.HostLine
                            neighborLocLineStart = neighborLocLine.GetEndPoint(0)
                            neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
                            intersection = RevitCurveCurveIntersection(locLine,neighborLocLine)

                            if intersection:
                                point1 = None
                                intersectionTypeOnNeighbor = None

                                #Check where the intersection is occuring on the neighbor
                                if intersection.DistanceTo(neighborLocLineStart) < self.distTol:
                                    intersectionTypeOnNeighbor = "Start"
                                    point1 = neighborLocLineEnd
                                elif intersection.DistanceTo(neighborLocLineEnd) < self.distTol:
                                    intersectionTypeOnNeighbor = "End"
                                    point1 = neighborLocLineStart
                                else:
                                    intersectionTypeOnNeighbor = "Middle"
                                    point1 = neighborLocLineEnd

                                #Check if intersection is at the start point or end point or middle
                                if intersection.DistanceTo(locLineStart) < self.tol:
                                    angle = AngleThreePoints(locLineEnd, intersection, point1)
                                    storefrontObject.StartNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                                elif intersection.DistanceTo(locLineEnd) < self.tol:
                                    angle = AngleThreePoints(locLineStart, intersection, point1)
                                    storefrontObject.EndNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                                else:
                                    #Interesection isnt ocurring at the ends.
                                    gridIntersectionPostPoints.append(intersection)

                                    #If the intersections for both lines are on the middles for eachother.
                                    if intersectionTypeOnNeighbor == "Middle":

                                        #Split the intersecting neighbor into two segments so the walls dont overlap
                                        neighborLocLineStart = neighborLocLine.GetEndPoint(0)
                                        neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
                                        neighbor.Line = Line.CreateBound(intersection, neighborLocLineStart)
                                        neighbor.HostLine = Line.CreateBound(intersection, neighborLocLineStart)

                                        #Create another neighbor thats split
                                        newNeighborIndex = len(self.storefrontElevations)+1
                                        newNeighborHostElementIds = neighbor.HostElementIds
                                        newNeighborSillHeight = neighbor.SillHeight
                                        newNeighborHeadHeight = neighbor.HeadHeight
                                        splitNeighborLine = Line.CreateBound(intersection, neighborLocLineEnd)
                                        splitNeighbor = StorefrontElevation(newNeighborHostElementIds, splitNeighborLine, neighbor.SuperType, newNeighborIndex, newNeighborSillHeight, newNeighborHeadHeight, self.systemName)
                                        self.storefrontElevations.append(splitNeighbor)

                                        #Make sure that each new segment has the correct doors on each one
                                        if neighbor.Doors:
                                            doorsOnNeighbor = neighbor.Doors
                                            tempList1 = []
                                            tempList2 = []
                                            for neighborDoorId in doorsOnNeighbor:
                                                neighborDoor = self.doc.GetElement(neighborDoorId)
                                                doorPoint = neighborDoor.Location.Point
                                                if RevitPointOnLine2D(doorPoint, neighbor.Line):
                                                    tempList1.append(neighborDoorId)
                                                else:
                                                    tempList2.append(neighborDoorId)
                                            neighbor.Doors = tempList1
                                            splitNeighbor.Doors = tempList2

                    #-----------Determine Conditions-----------#

                    ###------------Start Condition-----------###
                    locLine = storefrontObject.HostLine
                    locLineStart = locLine.GetEndPoint(0)
                    locLineEnd = locLine.GetEndPoint(1)

                    startAndEndNeighbors = [storefrontObject.StartNeighbors, storefrontObject.EndNeighbors]

                    for i in range(len(startAndEndNeighbors)):

                        neighborSet = startAndEndNeighbors[i]
                        cornerCount = 0
                        inlineCount = 0
                        cornerTypes = []
                        inlineTypes = []
                        conditionAngleOffset = None
                        conditionToSet = None

                        if neighborSet:

                            for neighbor in neighborSet:
                                angle = neighbor[2]
                                intersectionType = neighbor[3]
                                intersection = neighbor[4]

                                #---Corner Test---#
                                if abs(angle-90) < self.angleTol:
                                    if neighbor[1] != storefrontType:
                                        if intersectionType == "Middle":
                                            conditionToSet = "OnStorefront"
                                            cornerTypes.append("Different")
                                            cornerCount += 2
                                        elif intersectionType == "Start" or intersectionType == "End":
                                            cornerTypes.append("Different")
                                            cornerCount += 1

                                    elif neighbor[1] == storefrontType:
                                        # If the storefront is connected to the middle of another storefront
                                        # that is the of the same type, then it should join
                                        if intersectionType == "Middle":
                                            conditionToSet = "JoinStorefront"
                                            cornerTypes.append("Same")
                                            cornerCount += 2

                                        elif intersectionType == "Start" or intersectionType == "End":
                                            cornerTypes.append("Same")
                                            cornerCount += 1

                                #---Inline Test---#
                                elif abs(angle-180) < self.angleTol:
                                    if neighbor[1] != storefrontType:
                                        inlineTypes.append("Different")
                                        inlineCount += 1 
                                    elif neighbor[1] == storefrontType:
                                        inlineTypes.append("Same")
                                        #Placeholder just in case
                                        pass

                                #---Angled Test---#
                                elif abs(round(neighbor[2],1) % 90) > self.angleTol:
                                    reverse = 0
                                    if locLineStart.X > locLineEnd.X: 
                                        reverse = 180
                                    angleRadians = (neighbor[2] * (2 * math.pi)) / 360
                                    conditionAngleOffset = (0.5 * self.systemPostWidth) / math.tan((angleRadians) * 0.5)
                                    conditionToSet = "Angled"
                                    if self.storefrontConfig.currentConfig["isFramed"]:
                                        if i == 0:
                                            vect = RevitTransVector(locLineEnd, locLineStart, magnitude=conditionAngleOffset)
                                            locLineStart = locLineStart.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                        elif i == 1:
                                            vect = RevitTransVector(locLineStart, locLineEnd, magnitude=conditionAngleOffset)
                                            locLineEnd = locLineEnd.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)
                                    break

                            #---Compound Conditions---#
                            if cornerCount == 0 and inlineCount == 1:
                                if "Same" in inlineTypes:
                                    pass
                                elif "Different" in inlineTypes:
                                    if storefrontType == "Full":
                                        conditionToSet = "ForcePost"
                                    elif storefrontType == "Partial":
                                        conditionToSet = "OnStorefront"

                            elif cornerCount == 1 and inlineCount == 0:
                                if "Same" in cornerTypes:
                                    conditionToSet = None
                                elif "Different" in cornerTypes:
                                    if storefrontType == "Full":
                                        conditionToSet = None
                                    elif storefrontType == "Partial":
                                        conditionToSet = "OnStorefront"
                                else: 
                                    pass

                            elif cornerCount == 1 and inlineCount == 1:
                                if "Same" in cornerTypes:
                                    conditionToSet = "JoinStorefront"
                                    if i == 0:
                                        vect = RevitTransVector(locLineEnd, locLineStart, magnitude=self.systemPostWidth/2)
                                        locLineStart = locLineStart.Add(vect)
                                        storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                    elif i == 1:
                                        vect = RevitTransVector(locLineStart, locLineEnd, magnitude=self.systemPostWidth/2)
                                        locLineEnd = locLineEnd.Add(vect)
                                        storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

                                elif "Different" in cornerTypes:
                                    conditionToSet = "OnStorefront"
                                else: 
                                    pass

                            elif cornerCount == 2 and inlineCount == 0:
                                if not "Different"  in  cornerTypes:
                                    conditionToSet = "JoinStorefront"
                                    if i == 0:
                                        vect = RevitTransVector(locLineEnd, locLineStart, magnitude=self.systemPostWidth/2)
                                        locLineStart = locLineStart.Add(vect)
                                        storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                    elif i == 1:
                                        vect = RevitTransVector(locLineStart, locLineEnd, magnitude=self.systemPostWidth/2)
                                        locLineEnd = locLineEnd.Add(vect)
                                        storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

                                elif "Same" in  cornerTypes and "Different" in cornerTypes:
                                    conditionToSet = "ForcePostAtTBone"
                                    if i == 0:
                                        vect = RevitTransVector(locLineStart, locLineEnd, magnitude=self.systemPostWidth/2)
                                        locLineStart = locLineStart.Add(vect)
                                        storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                    elif i == 1:
                                        vect = RevitTransVector(locLineEnd, locLineStart, magnitude=self.systemPostWidth/2)
                                        locLineEnd = locLineEnd.Add(vect)
                                        storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

                            elif cornerCount == 2 and inlineCount == 1:
                                if "Same" in  cornerTypes and "Different" in cornerTypes and "Different" in inlineTypes:
                                    pass

                        #Logic gate to set contidions to the right ends either start of end.
                        if i == 0  and neighborSet:
                            storefrontObject.StartCondition = conditionToSet

                            if conditionAngleOffset:
                                storefrontObject.StartAngledOffset = conditionAngleOffset

                        elif i == 1 and neighborSet:
                            storefrontObject.EndCondition = conditionToSet

                            if conditionAngleOffset:
                                storefrontObject.EndAngledOffset = conditionAngleOffset


                    #############################################
                    #                 Creation                  #
                    #############################################

                    #--------------Curtain Wall-----------------#
                    with rpw.db.Transaction("Create Curtain Wall") as tx:
                        SupressErrorsAndWarnings(tx)
                        newWallHeadHeight = storefrontObject.HeadHeight 
                        newWallLine = storefrontObject.Line
                        newWall = Wall.Create(self.doc, newWallLine, self.wallTypeCW, baseConstraint, newWallHeadHeight, 0, False, False)
                        newWall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).Set(0)

                        #Set new CW Id to storefrontObject object 
                        storefrontObject.CWElementId = newWall.Id

                        self.doc.Regenerate()

                        if self.storefrontConfig.currentConfig["isFramed"]:
                            if storefrontObject.StartCondition == "Angled":
                                WallUtils.DisallowWallJoinAtEnd(newWall, 0)
                            if storefrontObject.EndCondition == "Angled":
                                WallUtils.DisallowWallJoinAtEnd(newWall, 1)

                        conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

                        #print storefrontObject.SuperType
                        #print "start - " + str(storefrontObject.StartCondition)
                        #print "end   - " + str(storefrontObject.EndCondition)

                        for i in range(len(conditionsList)):
                            condition = conditionsList[i]
                            newWall_grid = newWall.CurtainGrid
                            newWallPoint = newWall.Location.Curve.GetEndPoint(i)
                            mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5)

                            if mullionList:
                                for mul in mullionList:
                                    mul.Pinned = False

                                    if condition == "OnGyp":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])

                                    elif condition == "OnObstruction":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])

                                    elif condition == "OnStorefront":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])

                                    elif condition == "JoinStorefront":
                                        self.doc.Delete(mul.Id)

                                    elif condition == "ForcePost":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_Post"])

                                    elif condition == "ForcePostAtTBone":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_Post"])

                                    elif condition == "Angled":
                                        if self.storefrontConfig.currentConfig["isFramed"]:
                                            mul.ChangeTypeId(self.mullionDict[self.systemName + "_OneBy"])
                                        else: 
                                            self.doc.Delete(mul.Id)



                    #############################################
                    #              Modifications                #
                    #############################################


                    #-----------Lower Infill Panels-------------#

                    newWall_grid = newWall.CurtainGrid

                    #Create lower infill panel and sill
                    if self.storefrontConfig.currentConfig["hasLowerInfill"]:

                        newWallMidPoint = newWall.Location.Curve.Evaluate(0.5, True)
                        newWall_grid = newWall.CurtainGrid
                        if storefrontObject.SuperType == "Partial":
                            with rpw.db.Transaction("Create Lower Infill Panels") as tx:
                                SupressErrorsAndWarnings(tx)
                                try:
                                    gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + self.storefrontConfig.currentConfig["partialSillHeight"] )
                                    grid0 = newWall_grid.AddGridLine(True, gridPt, False)
                                except:
                                    pass

                                # Create Solid Lower Panels
                                self.doc.Regenerate()
                                newWall_grid = newWall.CurtainGrid
                                uGridIds = newWall_grid.GetVGridLineIds()
                                newWallLocationCurve = newWall.Location.Curve
                                verticalGridPoints = []

                                for uGridId in uGridIds:
                                    uGrid = self.doc.GetElement(uGridId)
                                    uGridOrigin = uGrid.FullCurve.Origin
                                    verticalGridPoints.append(XYZ(uGridOrigin.X, uGridOrigin.Y, newWallMidPoint.Z))
                                splitCurves = RevitSplitLineAtPoints(newWallLocationCurve, verticalGridPoints)

                                for sCurve in splitCurves:
                                    sCurveMidpoint = sCurve.Evaluate(0.5, True)
                                    panelIds = RevitCurtainPanelsAtPoint(newWall_grid, sCurveMidpoint, detectionTolerance=0.1)
                                    panelElevationTupleList = []
                                    for panelId in panelIds:
                                        panel = self.doc.GetElement(panelId)
                                        panelElevationTupleList.append((panel,float(panel.Transform.Origin.Z)))

                                    panelElevationTupleList = sorted(panelElevationTupleList, key=lambda x: x[1])

                                    #Gets lowest panel and change to solid
                                    try:
                                        panelToChange = panelElevationTupleList[0][0]
                                        panelToChange.Pinned = False
                                        panelToChange.ChangeTypeId(self.panelTypeDict[self.storefrontConfig.currentConfig["panelLowerInfill"]])
                                    except:
                                        pass


                    #---------------Special Horizontals---------------#
                    specialHorizontals = self.storefrontConfig.currentConfig["specialHorizontalMullions"]
                    if specialHorizontals:
                        for key, value in specialHorizontals.items():
                            if key in wtName:
                                newWallMidPoint = newWall.Location.Curve.Evaluate(0.5, True)
                                newWall_grid = newWall.CurtainGrid
                                with rpw.db.Transaction("Create Special Horizontal") as tx:
                                    SupressErrorsAndWarnings(tx)
                                    try:
                                        gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + value[0])
                                        grid0 = newWall_grid.AddGridLine(True, gridPt, False)
                                    except:
                                        pass

                    #-----------Midspan Intersections (posts)----------#

                    newWall_grid = newWall.CurtainGrid
                    if gridIntersectionPostPoints:
                        with rpw.db.Transaction("Create Intersection Grids") as tx:
                            SupressErrorsAndWarnings(tx)
                            for gridIntersectionPoint in gridIntersectionPostPoints:
                                try:
                                    gridInt = newWall_grid.AddGridLine(False, gridIntersectionPoint, False)
                                    mullionIntList = GetVerticalMullionsAtPoint(newWall_grid, gridIntersectionPoint, detectionTolerance=0.001)
                                    if mullionIntList:
                                        for mullion3 in mullionIntList:
                                            mullion3.Pinned = False
                                            mullion3.ChangeTypeId(self.mullionDict[self.storefrontConfig.currentConfig["midspanIntersectionMullion"]])
                                except:
                                    pass


                    #-------------------Modify Ends-------------------#

                    with rpw.db.Transaction("Modify Ends") as tx:
                        SupressErrorsAndWarnings(tx)
                        #Disallow as needed:


                        if self.storefrontConfig.currentConfig["isFramed"]:
                            if storefrontObject.StartCondition == "Angled":
                                WallUtils.DisallowWallJoinAtEnd(newWall, 0)
                            if storefrontObject.EndCondition == "Angled":
                                WallUtils.DisallowWallJoinAtEnd(newWall, 1)

                        self.doc.Regenerate()

                        conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

                        #print storefrontObject.SuperType
                        #print "start - " + str(storefrontObject.StartCondition)
                        #print "end   - " + str(storefrontObject.EndCondition)

                        for i in range(len(conditionsList)):
                            condition = conditionsList[i]
                            newWall_grid = newWall.CurtainGrid
                            newWallPoint = newWall.Location.Curve.GetEndPoint(i)
                            mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5, searchOnlySelf=True)

                            if mullionList:
                                for mul in mullionList:
                                    mul.Pinned = False

                                    if condition == "OnGyp":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])

                                    elif condition == "OnObstruction":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])

                                    elif condition == "OnStorefront":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])

                                    elif condition == "JoinStorefront":
                                        self.doc.Delete(mul.Id)

                                    elif condition == "ForcePost":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_Post"])

                                    elif condition == "ForcePostAtTBone":
                                        mul.ChangeTypeId(self.mullionDict[self.systemName + "_Post"])

                                    elif condition == "Angled":
                                        if self.storefrontConfig.currentConfig["isFramed"]:
                                            mul.ChangeTypeId(self.mullionDict[self.systemName + "_OneBy"])
                                        else: 
                                            self.doc.Delete(mul.Id)



                    #-----------------Glazing Panel Types----------------#

                    changeToPanel = None

                    if "Demising" in wtName:
                        changeToPanel = self.storefrontConfig.currentConfig["panelGlazedCenter"]
                    elif "Offset" in wtName:
                        changeToPanel = self.storefrontConfig.currentConfig["panelGlazedOffset"]
                    elif "Double" in wtName:
                        changeToPanel = self.storefrontConfig.currentConfig["panelGlazedDouble"]
                    else:
                        pass

                    if changeToPanel:
                        with rpw.db.Transaction("Change Glazing Types") as tx:
                            SupressErrorsAndWarnings(tx)
                            self.doc.Regenerate()
                            panels = newWall_grid.GetPanelIds()
                            for panelToChangeId in panels:
                                panelToChange = self.doc.GetElement(panelToChangeId)
                                panelToChange.Pinned = False
                                panelToChange.ChangeTypeId(self.panelTypeDict[changeToPanel])




                    #-------------------Doors------------------#

                    if storefrontObject.Doors:
                        newWallStartPoint = newWall.Location.Curve.GetEndPoint(0)
                        newWallEndPoint = newWall.Location.Curve.GetEndPoint(1)
                        doorsOnWall = storefrontObject.Doors

                        with rpw.db.Transaction("Create Door Grids 0") as tx:
                            SupressErrorsAndWarnings(tx)

                            for doorId in doorsOnWall:

                                #Location info
                                door = self.doc.GetElement(doorId)
                                doorName = door.Name
                                doorLocationCenter = door.Location.Point
                                doorLocationRotation = door.Location.Rotation
                                doorHandOrientation = door.HandOrientation

                                #Defaults
                                doorHand = "R"
                                doorWidth = 1.0
                                doorType = "SWING"

                                #Get specific door info based on registered doors in the config.
                                if self.doorDict.get(doorName):

                                    doorDetails = self.doorDict[doorName]
                                    doorHand = doorDetails[0]
                                    doorWidth = doorDetails[1]
                                    doorType = doorDetails[2]

                                    frameMullion0 = self.mullionDict[self.systemName + doorDetails[3]]
                                    frameMullion1 = self.mullionDict[self.systemName + doorDetails[4]]
                                    extraAdjustment0 = doorDetails[5]
                                    extraAdjustment1 = doorDetails[6]

                                else: 

                                    #Defaults if no door is found
                                    frameMullion0 = self.mullionDict[self.systemName + "_DoorFrame"]
                                    frameMullion1 = self.mullionDict[self.systemName + "_DoorFrame"]

                                    #Fine adjustments for mullion position
                                    extraAdjustment0 = 0
                                    extraAdjustment1 = 0
                                    print "ISSUE: Unable to recognize door - " + doorName


                                #Get offset widths for door frame mullions
                                fm0 = self.doc.GetElement(frameMullion0)
                                frameMullion0Width = fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
                                frameMullion0Width += fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

                                fm1 = self.doc.GetElement(frameMullion1)
                                frameMullion1Width = fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
                                frameMullion1Width += fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

                                #Accounting for mullion CUST_MULLION_THICKnesses 
                                extra0 = (frameMullion0Width * 0.5) + extraAdjustment0
                                extra1 = (frameMullion1Width * 0.5) + extraAdjustment1

                                #Vectors to move location point
                                vect0 = doorHandOrientation.Multiply(((doorWidth / 2) + extra0))
                                vect1 = doorHandOrientation.Multiply(((doorWidth / 2) + extra1) * -1)

                                #Door end points
                                door_end0 = doorLocationCenter.Add(vect0)
                                door_end1 = doorLocationCenter.Add(vect1)


                                #Detection tolerance for nearby mullions based on system
                                #required because of varying mullion sizes

                                systemDetectionFactor = self.storefrontConfig.currentConfig["closeMullionDetectionFactor"]

                                detectionCheckDist0 = frameMullion0Width * systemDetectionFactor
                                detectionCheckDist1 = frameMullion1Width * systemDetectionFactor


                                self.doc.Regenerate()
                                newWall_grid = newWall.CurtainGrid

                                #Check to see if a mullion exists in the spot where one would be created.
                                checkMullion0 = GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=detectionCheckDist0)
                                if not checkMullion0:
                                    try:
                                        grid0 = newWall_grid.AddGridLine(False, door_end0, False)
                                    except:
                                        pass

                                    mullion0List = GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=0.001)
                                    if mullion0List:
                                        for mullion0 in mullion0List:
                                            mullion0.Pinned = False
                                            mullion0.Lock = False
                                            mullion0.ChangeTypeId(frameMullion0)

                                self.doc.Regenerate()
                                #Check to see if a mullion exists in the spot where one would be created.
                                checkMullion1 = GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=detectionCheckDist1)
                                if not checkMullion1:
                                    try:
                                        grid1 = newWall_grid.AddGridLine(False, door_end1, False)
                                    except:
                                        pass

                                    mullion1List = GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=0.001)
                                    if mullion1List:
                                        for mullion1 in mullion1List:
                                            mullion1.Pinned = False
                                            mullion1.Lock = False
                                            mullion1.ChangeTypeId(frameMullion1)

                            #-----------------Empty Panel----------------#
                                self.doc.Regenerate()
                                panelToChangeId = RevitCurtainPanelsAtPoint(newWall_grid, doorLocationCenter, detectionTolerance=0.2)
                                if panelToChangeId:
                                    panelToChange = self.doc.GetElement(panelToChangeId[0])
                                    panelToChange.Pinned = False
                                    panelToChange.ChangeTypeId(self.panelTypeDict[self.storefrontConfig.currentConfig["panelEmpty"]])

                            #-----------------Sill Delete----------------#
                                self.doc.Regenerate()

                                filterName = self.storefrontConfig.currentConfig["AUTO_MULLION_BORDER1_HORIZ"].split("_")[1]
                                doorSillMullions = GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter=filterName)

                                for dsm in doorSillMullions:
                                    dsm.Pinned = False
                                    self.doc.Delete(dsm.Id)

                            #-------------Continuous Head Above Door--------------#

                                doorFrameContinuous = self.storefrontConfig.currentConfig["mullionContinuousVerticalAtDoorTop"]

                                if not doorFrameContinuous:

                                    #filterName = self.storefrontConfig.currentConfig["AUTO_MULLION_BORDER2_HORIZ"].split("_")[1]

                                    #Join head so its continuous
                                    self.doc.Regenerate()
                                    doorHeadMullions = GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter="Head")
                                    for dhm in doorHeadMullions:
                                        dhm.JoinMullion()

                    #-------------------Intermediates-------------------# 

                    newWall_grid = newWall.CurtainGrid
                    panels = newWall_grid.GetPanelIds()

                    intermediateMullionWidth = 0
                    if self.storefrontConfig.currentConfig["isFramed"]:

                        #Select the right intermediate mullion in the project based
                        #on which system is being used. 

                        if "demising" in wtName.lower():
                            mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT"]
                        elif "offset" in wtName.lower():
                            mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"]
                        elif "double" in wtName.lower():
                            mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"]
                        else:
                            mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT"]

                        intermediateMullion = self.doc.GetElement(self.mullionDict[mulName])

                        #Get the sizes of the intermediate
                        try:
                            intermediateMullionWidth = intermediateMullion.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()
                            intermediateMullionWidth += intermediateMullion.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
                        except:
                            for p in intermediateMullion.Parameters:
                                if p.Definition.Name == "Width on side 1":
                                    intermediateMullionWidth += p.AsDouble()
                                if p.Definition.Name == "Width on side 2":
                                    intermediateMullionWidth += p.AsDouble()

                    #For each panel, check the widths and divide them
                    #according to the rules selected by the user.                 
                    for panelId in panels:
                        panel = self.doc.GetElement(panelId)
                        panelWidth = panel.get_Parameter(BuiltInParameter.CURTAIN_WALL_PANELS_WIDTH).AsDouble()

                        if "glazed" in (panel.Name + panel.Symbol.Family.Name).lower() and panelWidth > self.minPanelWidth:
                            newGridPoints = []
                            if self.storefrontSpacingType == 1:
                                newGridPoints = RevitDividePanelFixed(panel, self.storefrontPaneWidth, intermediateWidth=intermediateMullionWidth)
                            elif self.storefrontSpacingType == 0:
                                numberPanes = math.ceil(panelWidth/self.storefrontPaneWidth)
                                if numberPanes > 1:
                                    newGridPoints = RevitDividePanelEquidistant(panel, numberPanes, intermediateWidth=intermediateMullionWidth)

                            if newGridPoints:
                                with rpw.db.Transaction("Create intermediate grid lines") as tx:
                                    SupressErrorsAndWarnings(tx)
                                    for gridpt in newGridPoints:
                                        try:
                                            grid0 = newWall_grid.AddGridLine(False, gridpt, False)
                                            mullions0List = GetVerticalMullionsAtPoint(newWall_grid, grid0.FullCurve.Origin, detectionTolerance=0.001)
                                            for mullion0 in mullions0List:
                                                mullion0.Pinned = False
                                                if self.storefrontConfig.currentConfig["isFramed"]:
                                                    mullion0.ChangeTypeId(intermediateMullion.Id)

                                                    #Intermediates die into the head if mullion is "Broken"
                                                    if not self.storefrontConfig.currentConfig["mullionContinuousVerticalIntermediateTop"]:
                                                        mullion0.BreakMullion()
                                                else:
                                                    #Delete mullion in the case that the system type is butt joined.
                                                    self.doc.Delete(mullion0.Id)
                                        except:
                                            pass

                    #---------------Special Sills---------------#

                    newWall_grid = newWall.CurtainGrid

                    updatedSill = None

                    currentSill = self.storefrontConfig.currentConfig["AUTO_MULLION_BORDER1_HORIZ"]
                    replacementSills = self.storefrontConfig.currentConfig["specialSillConditions"]

                    if replacementSills:
                        for key,value in replacementSills.items():
                            if key.lower() in wtName.lower():
                                updatedSill = self.mullionDict[value]

                    if updatedSill:
                        panels = newWall_grid.GetPanelIds()
                        with rpw.db.Transaction("Update Sills") as tx:
                            SupressErrorsAndWarnings(tx) 
                            for panelId in panels:
                                panel = self.doc.GetElement(panelId)
                                panelPoint = panel.GetTransform().Origin
                                sills = GetHorizontalMullionsAtPoint(newWall_grid, panelPoint, nameFilter=currentSill)

                                sillElevationTupleList = []
                                for sill in sills:
                                    sillElevationTupleList.append((sill,float(sill.LocationCurve.Origin.Z)))

                                sillElevationTupleList = sorted(sillElevationTupleList, key=lambda x: x[1])

                                try:
                                    sillToChange = sillElevationTupleList[0][0]
                                    sillToChange.Pinned = False
                                    sillToChange.ChangeTypeId(updatedSill)
                                except:
                                    pass                       

                    #############################################
                    #            Final Param Setters            #
                    #############################################
                    # Set heights, for whatever reason differing heights before adding gridlines is an issue so set this last.
                    with rpw.db.Transaction("Create Curtain Wall") as tx:
                        SupressErrorsAndWarnings(tx)
                        newWallSillHeight = storefrontObject.SillHeight
                        newWallHeadHeight = storefrontObject.HeadHeight - storefrontObject.SillHeight
                        newWall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(newWallSillHeight)
                        newWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(newWallHeadHeight)
                        newWall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(storefrontObject.SuperType)
                        newWall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(str(self.selectedLevel) + "-"+ str(storefrontObject.AssemblyID))
    def Run_BuildWall(self):
        self.Build()
"""
