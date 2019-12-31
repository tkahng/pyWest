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

    rpwLib = r"VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\0 Lib\revitpythonwrapper-master" # common lib folder
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 6, rpwLib))
    import rpw
    from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
    
    import SF2_Families # saves storefront configs
    import SF2_Utility
    reload(SF2_Families)  
    reload(SF2_Utility)
    

    class Form:
        """
        Generates curtain wall on top of 
        existing basic walls.

        Storefront configurations are loaded from SF2_SystemConfigs
        Storefront families are loaded from SF2_Families
        """
        def __init__(self, doc):
            # input parameters
            self.doc = doc
                      
            # form options
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
                                  "MODE : 8' - 0''" : 8.0} # Extravega has a 15mm tolerance         

            self.divisionOptions = {"Fixed Distance": 1,
                                    "Even - Even": 0}

            self.panelWidthOptions = {"1000mm": 39.3701/12,
                                      "1200mm": 47.24409/12,
                                      "1375mm": 54.13386/12,
                                      "4'- 0''": 4 + (1.75/12),
                                      "4'- 6''": 4 + (7.75/12)}

            self.splitTypeOptions = {"Fixed - 6 Inches": 6.0/12,
                                     "Fixed - 12 Inches": 12.0/12,
                                     "Fixed - 150mm": 5.90551/12, 
                                     "Fixed - 300mm": 11.811/12, 
                                     "Optimized - variable": "OPTIMIZED"}            
            
            # form selection outputs
            self.selectedSystem = None
            self.headHeight = None
            self.partialHeadHeight = None
            self.spacingType = None
            self.storefrontPaneWidth = None
            self.components = None
            self.userConfigs = None # this is a dict
            self.userSettings = None

            self.projectInfo = self.doc.ProjectInformation
            self.projectId = self.projectInfo.Id
            self.projectName = None
            for p in projectInfo.Parameters:
                if p.Definition.Name == "Project Name":
                    projectName = p.AsString()            
            
            self.todaysDate = "{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year)          
        
        def PRINTout(self):
            for i in self.userSettings:
                print("{0} : {1}".format(i, self.userSettings[i]))
        
        def SelectedSettings():
            # this dictionary if fed to family selection method and appropriate
            # parameters for the family are set based on user selection
            self.userSettings = {"selectedSystem" : self.selectedSystem,
                                 "headHeight" : self.headHeight,
                                 "partialHeadHeight" : self.partialHeadHeight,
                                 "spacingType" : self.spacingType,
                                 "storefrontPaneWidth" : self.storefrontPaneWidth,
                                 "components" : self.components,
                                 "userConfigs" : self.userConfigs,
                                 "currentConfig" : self.currentConfig,
             
                                 "projectInfo" : self.projectInfo,
                                 "projectId" : self.projectId,
                                 "projectName" : self.projectName,
                                 "todaysDate" : self.todaysDate}
            
        def CreateForm(self):
            # Create Menu
            systemOptions = self.availableSystems
            heightOptions = self.heightOptions
            divisionTypeOptions = self.divisionOptions
            widthOptions = self.panelWidthOptions
            
            # Make sure default values are set
            if not self.configObj.currentConfig["selectedSystem"] in systemOptions.values():
                defaultSystem = systemOptions.keys()[0]
            else:
                defaultSystem = systemOptions.keys()[systemOptions.values().index(self.configObj.currentConfig["selectedSystem"])]

            if not self.configObj.currentConfig["headHeight"] in heightOptions.values():
                defaultHeight = heightOptions.keys()[0]
            else: 
                defaultHeight = heightOptions.keys()[heightOptions.values().index(self.configObj.currentConfig["headHeight"])]

            if not self.configObj.currentConfig["spacingType"] in divisionTypeOptions.values():
                defaultDivOption = divisionTypeOptions.keys()[0]
            else:
                defaultDivOption = divisionTypeOptions.keys()[divisionTypeOptions.values().index(self.configObj.currentConfig["spacingType"])]

            if not self.configObj.currentConfig["storefrontPaneWidth"] in widthOptions.values():
                defaultWidthOption = widthOptions.keys()[0]
            else:
                defaultWidthOption = widthOptions.keys()[widthOptions.values().index(self.configObj.currentConfig["storefrontPaneWidth"])]

            self.components = [Label('PICK SYSTEM'),
                               ComboBox("combobox1", systemOptions, default=defaultSystem),
                               Label('HEAD HEIGHT'),
                               ComboBox("combobox2", heightOptions, default=defaultHeight),
                               Label('DIVISION TYPE'),
                               ComboBox("combobox3", divisionTypeOptions, default=defaultDivOption),
                               Label('DIVISION WIDTH'),
                               ComboBox("combobox4", widthOptions, default=defaultWidthOption),
                               Separator(),
                               Button('Go')]        
            
        def Run_Form(self, printTest=False):
            # create form - instantiates outputs through user selection
            self.CreateForm()
            
            form = FlexForm("Storefront Tools Refactored", self.components)
            form.show()

            # exit if no selection
            if not form.values:
                sys.exit()
            
            # form output if selection accepted
            else:
                self.selectedSystem = form.values["combobox1"]
                self.headHeight = float(form.values["combobox2"])
                self.partialHeadHeight = float(form.values["combobox2"])
                self.spacingType = form.values["combobox3"]
                self.storefrontPaneWidth = float(form.values["combobox4"])
                # MAKE SURE TO OUTPUT THE DATA NECESSARY TO KNOW WHICH FAMILIES TO LOAD
                
                if printTest == True:
                    self.PRINTout()
            
            # GUI HAS TO RUN CONFIGS AND LOAD STOREFRONT SETTINGS...IT CAN LIVE IN FAMILIES WHICH THEN LOADS THE FAMILIES THEMSELVES...
            self.userConfigs = {"projectName": self.projectName,
                                "projectId": self.projectId.IntegerValue,
                                "configDate": self.todaysDate,
                                "headHeight": self.headHeight,
                                "storefrontPaneWidth" : self.storefrontPaneWidth,
                                "spacingType" : self.spacingType,
                                "families": loadedFamilies,
                                "selectedSystem": selectedSystem}
            
            # run youngest child from SF2_SystemConfigs - MAYBE NOT THIS RIGHT NOW, BUT SOMETHING ELSE HERE
            self.configObj = SF2_Families.storefront_configuration(system_name=self.selectedSystem, userConfigs=self.userConfigs)
            self.storefront_save_config(selectedSystem, userConfigs)              

            return(None)


    def TestMain():
        #app = __revit__.Application
        #uidoc = __revit__.ActiveUIDocument
        doc = __revit__.ActiveUIDocument.Document
        
        form = Form(doc).RunForm(printTest=True)

    if __name__ == "__main__":
        TestMain()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())    