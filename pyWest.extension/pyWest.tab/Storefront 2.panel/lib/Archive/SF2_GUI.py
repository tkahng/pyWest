"""
:tooltip:
Module for Storefront 2.0 Engine
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork Design Technology West

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit
"""

# pyRevit metadata variables
__title__ = "Storefront 2.0 GUI"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "Find Another"
__parameters__ = []

# standard modules
import clr # noqa E402
import os # noqa E402
import pyrevit # noqa E402
import rpw # noqa E402
import sys # noqa E402
import System # noqa E402
import tempfile # noqa E402

from System import DateTime as dt

# Revit API modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

# SF2 modules
import SF2_Families_CleanUp as SFF

#####################
## STOREFRONT FORM ##
#####################
class SF_Form:
    def __init__(self, doc, **kwargs):
        # input parameters
        self.doc = doc
        
        # family object to load from SF2_Families module
        self.familyObj = SFF.FamilyTools(self.doc)
        
        # file paths
        self.defaultConfigPath = self.familyObj.defaultConfigPath
        self.familyDirectory = self.familyObj.familyDirectory
        
        self.familiesToLoad = self.familyObj.currentConfig
        
        # THIS IS THE MAIN OUTPUT THAT IS USED BY SF2_ENGINE
        self.currentConfig = self.familyObj.currentConfig # default, or last selected settings
        
        # WHAT IS USING THIS???
        self.familyObj.JSONLoadConfig()

        self.GUI_levelNames = kwargs.values()[0] # kwargs for keyed arguments can be anything in the future
        self.GUI_SFSystemOptions = self.familyObj.GUI_SFSystemOptions
        self.GUI_heightOptions = self.familyObj.GUI_heightOptions     
        self.GUI_divisionOptions = self.familyObj.GUI_divisionOptions      
        self.GUI_panelWidthOptions = self.familyObj.GUI_panelWidthOptions
        self.GUI_nibWallOptions = self.familyObj.GUI_nibWallOptions
        self.GUI_nibWallLengthOptions = self.familyObj.GUI_nibWallLengthOptions
        
        # outputs - used seperately from json files that are written, more flexible
        self.userConfigs = None
    
    def SF_GetUserConfigs(self):
        """
        Set configurations and load families.
        
        THIS IS ALSO IDENTICAL TO STOREFRONT GUI, SO IT WILL BE REPLACED BY THAT...
        """
        from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm, CheckBox, TextBox

        # set default storefront system
        if not self.currentConfig["selectedSystem"] in self.GUI_SFSystemOptions.values():
            defaultSystem = self.GUI_SFSystemOptions .keys()[0]
        else:
            defaultSystem = self.GUI_SFSystemOptions .keys()[self.GUI_SFSystemOptions.values().index(self.currentConfig["selectedSystem"])]
        # set default storefront height
        if not self.currentConfig["headHeight"] in self.GUI_heightOptions.values():
            defaultHeight = self.GUI_heightOptions.keys()[0]
        else: 
            defaultHeight = self.GUI_heightOptions.keys()[self.GUI_heightOptions.values().index(self.currentConfig["headHeight"])]
        # set default storefront transum height
        #if not self.currentConfig["transomHeight"] in self.transomHeightOptions.values():
            #defaultTransomHeight = self.transomHeightOptions.keys()[0]
        #else:
            #defaultTransomHeight = self.transumHeightOptions.keys()[self.transumHeightOptions.values().index(self.currentConfig["transomHeight"])]
        # set defualt storefront panel division method
        if not self.currentConfig["spacingType"] in self.GUI_divisionOptions.values():
            defaultDivOption = self.GUI_divisionOptions.keys()[0]
        else:
            defaultDivOption = self.GUI_divisionOptions.keys()[self.GUI_divisionOptions.values().index(self.currentConfig["spacingType"])]
        # set default storefront panel width 
        if not self.currentConfig["storefrontPaneWidth"] in self.GUI_panelWidthOptions.values():
            defaultWidthOption = self.GUI_panelWidthOptions.keys()[0]
        else:
            defaultWidthOption = self.GUI_panelWidthOptions.keys()[self.GUI_panelWidthOptions.values().index(self.currentConfig["storefrontPaneWidth"])]
        # set default nib wall type
        if not self.currentConfig["nibWallType"] in self.GUI_nibWallOptions.values():
            defaultSplitWallOption = self.GUI_nibWallOptions.keys()[0]
        else:
            defaultSplitWallOption = self.GUI_nibWallOptions.keys()[self.GUI_nibWallOptions.values().index(self.currentConfig["nibWallType"])]
        # set default nib wall length
        if not self.currentConfig["splitOffset"] in self.GUI_nibWallLengthOptions.values():
            defaultNibWallTypeOption = self.GUI_nibWallLengthOptions.keys()[0]
        else:
            defaultNibWallTypeOption = self.GUI_nibWallLengthOptions.keys()[self.GUI_nibWallLengthOptions.values().index(self.currentConfig["splitOffset"])]
        
        # set form buttons, text boxes, etc... | TextBox(componentName, defaultValue) is an option for manual entry
        # dropdown transomHeightOptions from above is not currently being used
        components = [Label('PICK SYSTEM'),
                      ComboBox("combobox1", self.GUI_SFSystemOptions , default=defaultSystem),
                      
                      Label('HEAD HEIGHT'),
                      ComboBox("combobox2", self.GUI_heightOptions, default=defaultHeight),
                      
                      #CheckBox("checkbox1", "Transom (decimal input)", default=False),
                      #TextBox("textbox1", default="12.00 inches"),
                      
                      Label('DIVISION TYPE'),
                      ComboBox("combobox4", self.GUI_divisionOptions, default=defaultDivOption),
                      
                      Label('DIVISION WIDTH'),
                      ComboBox("combobox5", self.GUI_panelWidthOptions, default=defaultWidthOption),
                      
                      Separator(),
                      CheckBox("checkbox2", "Nib Wall Split", default=True),
                      ComboBox("combobox6", self.GUI_nibWallOptions, default=defaultSplitWallOption),
                      ComboBox("combobox7", self.GUI_nibWallLengthOptions, default=defaultNibWallTypeOption),
                      
                      Separator(),
                      Button('Go')
                      ]

        # Create Menu
        form = FlexForm("STOREFRONT 2", components)
        form.show()

        if not form.values:
            # better than sys.exit()
            pyrevit.script.exit()
        else:
            selectedSystem = form.values["combobox1"]
            headHeight = float(form.values["combobox2"])
            partialHeadHeight = float(form.values["combobox2"])
            #createTransom = form.values["checkbox1"]
            
            # filter out inputs with a text character - expand to other types of units
            #try:
                #transomHeight = float(form.values["textbox1"])
            #except:
                #transomHeight = float(form.values["textbox1"].split(" inches")[0])
        
            spacingType = form.values["combobox4"]
            storefrontPaneWidth = float(form.values["combobox5"])
            createNibWall = form.values["checkbox2"]
            nibWallType = form.values["combobox6"]
            if form.values["combobox7"] == "OPTIMIZED":
                GUI_nibWallLengthOptions = form.values["combobox7"]
            else:
                GUI_nibWallLengthOptions = float(form.values["combobox7"])
        
        # IS THIS DOUBLE LOADING?
        # Load familes - its not a load, load but I will clarify this later
        loadedFamilies = self.familyObj.SFLoadFamilies(True)

        # Save when the config was set.
        projectInfo = self.doc.ProjectInformation
        projectId = projectInfo.Id
        projectName = None
        for p in projectInfo.Parameters:
            if p.Definition.Name == "Project Name":
                projectName = p.AsString()

        todaysDate = "{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year)
        
        # can also be used as class outputs directly in code
        self.userConfigs = {"projectName": projectName,
                            "projectId": projectId.IntegerValue,
                            "configDate": todaysDate,
                            "families": loadedFamilies,
                       
                            "selectedSystem": selectedSystem,
                            "headHeight": headHeight,
                            "partialHeadHeight": partialHeadHeight,
                       
                            #"createTransom": createTransom,
                            #"transomHeight": transomHeight,
                       
                            "spacingType": spacingType,
                            "storefrontPaneWidth": storefrontPaneWidth,
                            
                            "createNibWall": createNibWall,
                            "nibWallType": nibWallType,
                            "nibWallLength": GUI_nibWallLengthOptions
                            }
        
        # IS THIS SAVING WHAT WILL GET LOADED NEXT TIME?
        self.familyObj.Run_SaveSFConfigurations(selectedSystem, self.userConfigs)
       
    
