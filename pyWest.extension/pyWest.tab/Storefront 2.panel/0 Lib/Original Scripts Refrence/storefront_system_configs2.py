
import json
import sys
import os
import System
from System import DateTime as dt

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from storefront_utils import *
import SF2_Families2

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
import tempfile

import rpw

##############
## GUI FORM ##
##############
class storefront_options:
    def __init__(self, doc):
        # input parameters
        self.doc = doc
        
        # family object to load from SF2_Families module
        self.familyObj = FamilyStuff()
        
        # file paths
        self.defaultConfigPath = self.familyObj.defaultConfigPath
        self.familyDirectory = self.familyObj.familyDirectory
        
        self.familiesToLoad = self.familyObj.currentConfig
        
        # THIS IS THE MAIN OUTPUT THAT IS USED BY SF2_ENGINE
        self.currentConfig = self.familyObj.currentConfig # default, or last selected settings
        
        self.familyObj.json_load_config()

        self.availableSystems = self.familyObj.availableSystems
        self.heightOptions = self.familyObj.heightOptions     
        self.divisionOptions = self.familyObj.divisionOptions()      
        self.panelWidthOptions = self.familyObj.panelWidthOptions
        self.splitTypeOptions = self.familyObj.splitTypeOptions
        self.doorDict = self.familyObj.doorDict
    def storefront_set_config(self):
        """
        Set configurations and load families.
        
        THIS IS ALSO IDENTICAL TO STOREFRONT GUI, SO IT WILL BE REPLACED BY THAT...
        """

        # Create Menu

        from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm

        systemOptions = self.availableSystems   
        heightOptions = self.heightOptions
        divisionTypeOptions = self.divisionOptions
        widthOptions = self.panelWidthOptions

        # make sure default values are set
        if not self.currentConfig["selectedSystem"] in systemOptions.values():
            defaultSystem = systemOptions.keys()[0]
        else:
            defaultSystem = systemOptions.keys()[systemOptions.values().index(self.currentConfig["selectedSystem"])]

        if not self.currentConfig["headHeight"] in heightOptions.values():
            defaultHeight = heightOptions.keys()[0]
        else: 
            defaultHeight = heightOptions.keys()[heightOptions.values().index(self.currentConfig["headHeight"])]

        if not self.currentConfig["spacingType"] in divisionTypeOptions.values():
            defaultDivOption = divisionTypeOptions.keys()[0]
        else:
            defaultDivOption = divisionTypeOptions.keys()[divisionTypeOptions.values().index(self.currentConfig["spacingType"])]

        if not self.currentConfig["storefrontPaneWidth"] in widthOptions.values():
            defaultWidthOption = widthOptions.keys()[0]
        else:
            defaultWidthOption = widthOptions.keys()[widthOptions.values().index(self.currentConfig["storefrontPaneWidth"])]

        components = [Label('PICK SYSTEM'),
                    ComboBox("combobox1", systemOptions, default=defaultSystem),
                    Label('HEAD HEIGHT'),
                    ComboBox("combobox2", heightOptions, default=defaultHeight),
                    Label('DIVISION TYPE'),
                    ComboBox("combobox3", divisionTypeOptions, default=defaultDivOption),
                    Label('DIVISION WIDTH'),
                    ComboBox("combobox4", widthOptions, default=defaultWidthOption),
                    Separator(),
                    Button('Go')]

        form = FlexForm("Storefront Tools V3", components)
        form.show()

        if not form.values:
            sys.exit()
        else:
            selectedSystem = form.values["combobox1"]
            headHeight = float(form.values["combobox2"])
            partialHeadHeight = float(form.values["combobox2"])
            spacingType = form.values["combobox3"]
            storefrontPaneWidth = float(form.values["combobox4"])

        # Load familes
        loadedFamilies = self.familyObj.storefront_load_families(True)

        # Save when the config was set.
        projectInfo = self.locLineStart.ProjectInformation
        projectId = projectInfo.Id
        projectName = None
        for p in projectInfo.Parameters:
            if p.Definition.Name == "Project Name":
                projectName = p.AsString()

        todaysDate = "{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year)

        userConfigs = {"projectName": projectName,
                        "projectId": projectId.IntegerValue,
                        "configDate": todaysDate,
                        "headHeight": headHeight,
                        "storefrontPaneWidth" : storefrontPaneWidth,
                        "spacingType" : spacingType,
                        "families": loadedFamilies,
                        "selectedSystem": selectedSystem}
        
        # THIS IS THE MAIN FORM OUTPUT
        self.familyObj.storefront_save_config(selectedSystem, userConfigs)
       
    
