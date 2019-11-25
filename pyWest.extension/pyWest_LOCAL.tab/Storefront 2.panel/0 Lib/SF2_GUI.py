
import json
import sys
import os
import System
from System import DateTime as dt

#sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import SF2_Utility
import SF2_Families

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
import tempfile

import rpw
import pyrevit

##############
## GUI FORM ##
##############
class storefront_options:
    def __init__(self, doc):
        # input parameters
        self.doc = doc
        
        # family object to load from SF2_Families module
        self.familyObj = SF2_Families.FamilyTools(self.doc)
        
        # file paths
        self.defaultConfigPath = self.familyObj.defaultConfigPath
        self.familyDirectory = self.familyObj.familyDirectory
        
        self.familiesToLoad = self.familyObj.currentConfig
        
        # THIS IS THE MAIN OUTPUT THAT IS USED BY SF2_ENGINE
        self.currentConfig = self.familyObj.currentConfig # default, or last selected settings
        
        # WHAT IS USING THIS???
        self.familyObj.JSONLoadConfig()

        self.availableSystems = self.familyObj.availableSystems
        self.heightOptions = self.familyObj.heightOptions     
        self.transomHeightOptions = self.familyObj.transomHeightOptions
        self.divisionOptions = self.familyObj.divisionOptions      
        self.panelWidthOptions = self.familyObj.panelWidthOptions
        self.nibWallDict = self.familyObj.nibWallDict
        self.nibWallLength = self.familyObj.nibWallLength
        self.doorDict = self.familyObj.doorDict
        
        # outputs - used seperately from json files that are written, more flexible
        self.userConfigs = None
    
    def storefront_set_config(self):
        """
        Set configurations and load families.
        
        THIS IS ALSO IDENTICAL TO STOREFRONT GUI, SO IT WILL BE REPLACED BY THAT...
        """
        from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm, CheckBox, TextBox

        # set default storefront system
        if not self.currentConfig["selectedSystem"] in self.availableSystems.values():
            defaultSystem = self.availableSystems .keys()[0]
        else:
            defaultSystem = self.availableSystems .keys()[self.availableSystems.values().index(self.currentConfig["selectedSystem"])]
        # set default storefront height
        if not self.currentConfig["headHeight"] in self.heightOptions.values():
            defaultHeight = self.heightOptions.keys()[0]
        else: 
            defaultHeight = self.heightOptions.keys()[self.heightOptions.values().index(self.currentConfig["headHeight"])]
        # set default storefront transum height
        if not self.currentConfig["transomHeight"] in self.transomHeightOptions.values():
            defaultTransomHeight = self.transomHeightOptions.keys()[0]
        else:
            defaultTransomHeight = self.transumHeightOptions.keys()[self.transumHeightOptions.values().index(self.currentConfig["transomHeight"])]
        # set defualt storefront panel division method
        if not self.currentConfig["spacingType"] in self.divisionOptions.values():
            defaultDivOption = self.divisionOptions.keys()[0]
        else:
            defaultDivOption = self.divisionOptions.keys()[self.divisionOptions.values().index(self.currentConfig["spacingType"])]
        # set default storefront panel width 
        if not self.currentConfig["storefrontPaneWidth"] in self.panelWidthOptions.values():
            defaultWidthOption = self.panelWidthOptions.keys()[0]
        else:
            defaultWidthOption = self.panelWidthOptions.keys()[self.panelWidthOptions.values().index(self.currentConfig["storefrontPaneWidth"])]
        # set default nib wall type
        if not self.currentConfig["nibWallType"] in self.nibWallDict.values():
            defaultSplitWallOption = self.nibWallDict.keys()[0]
        else:
            defaultSplitWallOption = self.nibWallDict.keys()[self.nibWallDict.values().index(self.currentConfig["nibWallType"])]
        # set default nib wall length
        if not self.currentConfig["splitOffset"] in self.nibWallLength.values():
            defaultNibWallTypeOption = self.nibWallLength.keys()[0]
        else:
            defaultNibWallTypeOption = self.nibWallLength.keys()[self.nibWallLength.values().index(self.currentConfig["splitOffset"])]
        
        # set form buttons, text boxes, etc... | TextBox(componentName, defaultValue) is an option for manual entry
        # dropdown transomHeightOptions from above is not currently being used
        components = [Label('PICK SYSTEM'),
                      ComboBox("combobox1", self.availableSystems , default=defaultSystem),
                      
                      Label('HEAD HEIGHT'),
                      ComboBox("combobox2", self.heightOptions, default=defaultHeight),
                      
                      CheckBox("checkbox1", "Transom (decimal input)", default=False),
                      TextBox("textbox1", default="12.00 inches"),
                      
                      Label('DIVISION TYPE'),
                      ComboBox("combobox4", self.divisionOptions, default=defaultDivOption),
                      
                      Label('DIVISION WIDTH'),
                      ComboBox("combobox5", self.panelWidthOptions, default=defaultWidthOption),
                      
                      Separator(),
                      CheckBox("checkbox2", "Nib Wall Split", default=True),
                      ComboBox("combobox6", self.nibWallDict, default=defaultSplitWallOption),
                      ComboBox("combobox7", self.nibWallLength, default=defaultNibWallTypeOption),
                      
                      Separator(),
                      Button('Go')
                      ]

        # Create Menu
        form = FlexForm("STOREFRONT 2 BETA", components)
        form.show()

        if not form.values:
            # better than sys.exit()
            pyrevit.script.exit()
        else:
            selectedSystem = form.values["combobox1"]
            headHeight = float(form.values["combobox2"])
            partialHeadHeight = float(form.values["combobox2"])
            createTransom = form.values["checkbox1"]
            
            # filter out inputs with a text character - expand to other types of units
            try:
                transomHeight = float(form.values["textbox1"])
            except:
                transomHeight = float(form.values["textbox1"].split(" inches")[0])
        
            spacingType = form.values["combobox4"]
            storefrontPaneWidth = float(form.values["combobox5"])
            createNibWall = form.values["checkbox2"]
            nibWallType = form.values["combobox6"]
            if form.values["combobox7"] == "OPTIMIZED":
                nibWallLength = form.values["combobox7"]
            else:
                nibWallLength = float(form.values["combobox7"])

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
                       
                            "createTransom": createTransom,
                            "transomHeight": transomHeight,
                       
                            "spacingType": spacingType,
                            "storefrontPaneWidth": storefrontPaneWidth,
                            
                            "createNibWall": createNibWall,
                            "nibWallType": nibWallType,
                            "nibWallLength": nibWallLength
                            }
        
        # IS THIS SAVING WHAT WILL GET LOADED NEXT TIME?
        self.familyObj.Run_SaveSFConfigurations(selectedSystem, self.userConfigs)
       
    
