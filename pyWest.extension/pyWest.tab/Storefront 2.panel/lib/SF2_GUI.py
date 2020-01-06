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

from System import DateTime as dt # noqa E402

# Revit API modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402

# SF2 modules
import SF2_Families_CleanUp as SFF # noqa E402

#####################
## STOREFRONT FORM ##
#####################
class SF_Form:
    def __init__(self, doc, **kwargs):
        # input parameters
        self.doc = doc
        
        # input kwarg parameters
        if kwargs.items():
            for i, (key, value) in enumerate(kwargs.items()): 
                if key == "levelNames":
                    self.GUI_levelNames = kwargs.values()[i] # kwargs for keyed arguments can be anything in the future
                    print(self.GUI_levelNames)
                if key == "gypWallOptions":
                    #                         SF2_Engine.gypWallDict
                    self.GUI_nibWallOptions = kwargs.values()[i]
                if key == "loadedFamilies":
                    self.GUI_loadedFamilies = kwargs.values()[i]
        
        # family object to load from SF2_Families module
        self.familyObj = SFF.FamilyTools(self.doc)
        
        # gui options inherited from SF2_Families
        self.GUI_SF_systemOptions = self.familyObj.GUI_SF_systemOptions
        self.GUI_SF_heightOptions = self.familyObj.GUI_SF_heightOptions     
        self.GUI_SF_divisionOptions = self.familyObj.GUI_SF_divisionOptions      
        self.GUI_SF_panelWidthOptions = self.familyObj.GUI_SF_panelWidthOptions
        self.GUI_nibWallLengthOptions = self.familyObj.GUI_nibWallLengthOptions        
        
        # default options for GUI dropdowns
        self.components = None
        
        self.defaultSystem = None
        self.defaultHeight = None
        self.defaultDivOption = None
        self.defaultWidthOption = None
        self.defaultNibWallOption = None
        self.defaultNibWallLengthOption = None
        
        ############################
        ## SetFormOutputs outputs ##
        ############################
        self.selectedSystem = None
        self.headHeight = None
        self.partialHeadHeight = None
    
        self.spacingType = None
        self.storefrontPaneWidth = None
        self.createNibWall = None
        self.nibWallType = None
        self.nibWallLength = None
        
        # inherit empty self.currentConfig dict to begin writing data to it in this module
        # default, or last selected settings
        self.currentConfig = self.familyObj.currentConfig
        
        # outputs - used seperately from json files that are written, more flexible
        self.userConfigs = None        
        
        # loads previously saved currentConfig!
        # if an error points to this location, comment this out, run again to save another json
        # file, then uncomment this again and start over...
        self.familyObj.JSONLoadConfig()
        
    def SetDefaultFormValues(self):
        """
        DEFAULT OPTIONS FOR GUI. IF NO SELF.DEFAULT 
        VALUES EXIST THEN COMPONENT DEFAULT IS USED
        """
        
        # set default storefront system
        if not self.currentConfig["selectedSystem"] in self.GUI_SF_systemOptions.values():
            self.defaultSystem = self.GUI_SF_systemOptions.keys()[0]
        else:
            self.defaultSystem = self.GUI_SF_systemOptions.keys()[self.GUI_SF_systemOptions.values().index(self.currentConfig["selectedSystem"])]
        
        # set default storefront height
        if not self.currentConfig["headHeight"] in self.GUI_SF_heightOptions.values():
            self.defaultHeight = self.GUI_SF_heightOptions.keys()[0]
        else: 
            self.defaultHeight = self.GUI_SF_heightOptions.keys()[self.GUI_SF_heightOptions.values().index(self.currentConfig["headHeight"])]
        
        
        
        
        # FIX THIS 
        # set defualt storefront panel division method
        if not self.currentConfig["spacingType"] in self.GUI_SF_divisionOptions.values():
            self.defaultDivOption = self.GUI_SF_divisionOptions.keys()[0]
        else:
            self.defaultDivOption = self.GUI_SF_divisionOptions.keys()[self.GUI_SF_divisionOptions.values().index(self.currentConfig["spacingType"])]
            
            
            
            
        
        # set default storefront panel width 
        if not self.currentConfig["storefrontPaneWidth"] in self.GUI_SF_panelWidthOptions.values():
            self.defaultWidthOption = self.GUI_SF_panelWidthOptions.keys()[0]
        else:
            self.defaultWidthOption = self.GUI_SF_panelWidthOptions.keys()[self.GUI_SF_panelWidthOptions.values().index(self.currentConfig["storefrontPaneWidth"])]
        
        # set default nib wall type
        if not self.currentConfig["nibWallType"] in self.GUI_nibWallOptions.values():
            self.defaultNibWallOption = self.GUI_nibWallOptions.keys()[0]
        else:
            self.defaultNibWallOption = self.GUI_nibWallOptions.keys()[self.GUI_nibWallOptions.values().index(self.currentConfig["nibWallType"])]
       
        # set default nib wall length
        if not self.currentConfig["nibWallLength"] in self.GUI_nibWallLengthOptions.values():
            self.defaultNibWallLengthOption = self.GUI_nibWallLengthOptions.keys()[0]
        else:
            self.defaultNibWallLengthOption = self.GUI_nibWallLengthOptions.keys()[self.GUI_nibWallLengthOptions.values().index(self.currentConfig["nibWallLength"])]
            
    def SetFormComponents(self):
        from rpw.ui.forms import Button, CheckBox, ComboBox, Label, Separator, TextBox # why does this have to be inside method?
        
        # set form buttons, text boxes, etc... | TextBox(componentName, defaultValue) is an option for manual entry
        # dropdown transomHeightOptions from above is not currently being used
        self.components = [#Label('CHOOSE FLOORS'),
                           #CheckBox("checkbox1", "something", default=True),
                           
                           Separator(),
                           Label('PICK SYSTEM'),
                           ComboBox("combobox1", self.GUI_SF_systemOptions , default=self.defaultSystem),
                      
                           Label('HEAD HEIGHT'),
                           ComboBox("combobox2", self.GUI_SF_heightOptions, default=self.defaultHeight),
                      
                           Label('DIVISION TYPE'),
                           ComboBox("combobox4", self.GUI_SF_divisionOptions, default=self.defaultDivOption),
                      
                           Label('DIVISION WIDTH'),
                           ComboBox("combobox5", self.GUI_SF_panelWidthOptions, default=self.defaultWidthOption),
                      
                           Separator(),
                           CheckBox("checkbox1", "NIB WALL SPLIT", default=True),
                           CheckBox("checkbox2", "NIB WALL SPLIT ONLY", default=False),
                           ComboBox("combobox6", self.GUI_nibWallOptions, default=self.defaultNibWallOption),
                           ComboBox("combobox7", self.GUI_nibWallLengthOptions, default=self.defaultNibWallLengthOption),
                      
                           Separator(),
                           Button('Go')
                           ]
    
    def SetFormOutputs(self, form):
        if not form.values:
            # better than sys.exit()
            pyrevit.script.exit()
        
        else:
            self.selectedSystem = form.values["combobox1"]
            self.headHeight = float(form.values["combobox2"])
            self.partialHeadHeight = float(form.values["combobox2"])
            
            self.spacingType = form.values["combobox4"]
            self.storefrontPaneWidth = float(form.values["combobox5"])
            self.createNibWall = form.values["checkbox1"]
            self.createNibWallOnly = form.values["checkbox2"]
            self.nibWallType = form.values["combobox6"]
            
            if form.values["combobox7"] == "OPTIMIZED":
                self.nibWallLength = form.values["combobox7"]
            else:
                self.nibWallLength = float(form.values["combobox7"])
    
    def WriteSFConfigs(self):
        # Save when the config was set.
        projectInfo = self.doc.ProjectInformation
        projectId = projectInfo.Id
        
        # project name
        for p in projectInfo.Parameters:
            if p.Definition.Name == "Project Name":
                projectName = p.AsString()
            else: projectName = None

        todaysDate = "{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year)        
        
        self.userConfigs = {"projectName": projectName,
                            "projectId": projectId.IntegerValue,
                            "configDate": todaysDate,
                            "families": self.GUI_loadedFamilies,
                       
                            "selectedSystem": self.selectedSystem,
                            "headHeight": self.headHeight,
                            "partialHeadHeight": self.partialHeadHeight,
                       
                            "spacingType": self.spacingType,
                            "storefrontPaneWidth": self.storefrontPaneWidth,
                            
                            "createNibWall": self.createNibWall,
                            "createNibWallOnly": self.createNibWallOnly,
                            "nibWallType": self.nibWallType,
                            "nibWallLength": self.nibWallLength
                            }
        
        # convert userConfigs to currentConfigs + all other currentConfig settings
        self.familyObj.Run_SaveSFCurrentConfig(self.selectedSystem, self.userConfigs)
    
    def SF_GetUserConfigs(self):
        from rpw.ui.forms import FlexForm
        # set form options
        self.SetDefaultFormValues()
        
        # create form object and add elements to it
        self.SetFormComponents()
        
        # Create Menu
        form = FlexForm("STOREFRONT 2", self.components)
        form.show()
        
        # set form outputs
        self.SetFormOutputs(form)
        
        # write SF configuration to be used by SF2_Engine
        self.WriteSFConfigs()
    
