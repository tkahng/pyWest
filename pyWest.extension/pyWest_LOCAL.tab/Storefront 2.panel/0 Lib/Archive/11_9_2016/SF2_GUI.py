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
    
    import SF2_Families
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
            
            # instantiate family module classes - gains access to every method and variable
            self.familyObj = SF2_Families.ParentClass()
            
            # derived parameters
            self.currentConfig = self.familyObj.currentConfig
            self.formWindowName = "Storefront 2.0 - BETA"
            
            # form options
            self.availableSystems = self.familyObj.availableSystems
            self.heightOptions = self.familyObj.heightOptions         
            self.divisionOptions = self.familyObj.divisionOptions
            self.panelWidthOptions = self.familyObj.panelWidthOptions
            
            # form selection outputs
            self.selectedSystem = None
            self.headHeight = None
            self.partialHeadHeight = None
            self.spacingType = None
            self.storefrontPaneWidth = None
            self.components = None
            self.userSelections = None
            
        ###############
        ## UTILITIES ##
        ###############
        def PRINTout(self):
            if self.userSelections:
                for i in self.userSelections:
                    print("{0} : {1}".format(i, self.userSelections[i]))
        #############
        ## OUTPUTS ##
        #############
        def SelectedSettings(self):
            # this dictionary if fed to family selection method and appropriate
            # parameters for the family are set based on user selection
            self.userSelections = {"selectedSystem" : self.selectedSystem,
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
        
        ##########################
        ## DEFINE FORM ELEMENTS ##
        ##########################
        def DefineFormComponents(self):
            # establish form options - define this more clearly
            systemOptions = self.availableSystems
            heightOptions = self.heightOptions
            divisionTypeOptions = self.divisionOptions
            widthOptions = self.panelWidthOptions
            
            # establish default form settings
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
            
            # create form buttons, labels, etc.
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
        ################
        ## CLASS MAIN ##
        ################
        def Run_Form(self, printTest=False):
            # create form - instantiates outputs through user selection
            self.DefineFormComponents()
            form = FlexForm(self.formWindowName, self.components) # method(windowName, buttonsAndStuff)
            form.show()

            # exit if no selection
            if not form.values:
                sys.exit()
            
            # get form output from user selection
            else:
                self.selectedSystem = form.values["combobox1"]
                self.headHeight = float(form.values["combobox2"])
                self.partialHeadHeight = float(form.values["combobox2"])
                self.spacingType = form.values["combobox3"]
                self.storefrontPaneWidth = float(form.values["combobox4"])
                
                self.projectInfo = self.doc.ProjectInformation
                self.projectId = self.projectInfo.Id
                self.projectName = None
                for p in self.projectInfo.Parameters:
                    if p.Definition.Name == "Project Name":
                        projectName = p.AsString()
                
                
                #############################################################################################################
                # load families / write families to dictionary that is outputed
                loadedFamilies = self.familyObj.storefront_load_families(True)
                
                self.todaysDate = "{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year)   
                self.userConfigs = {"projectName": self.projectName,
                                    "projectId": self.projectId.IntegerValue,
                                    "configDate": self.todaysDate,
                                    "headHeight": self.headHeight,
                                    "storefrontPaneWidth" : self.storefrontPaneWidth,
                                    "spacingType" : self.spacingType,
                                    "families": loadedFamilies,
                                    "selectedSystem": self.selectedSystem}               
                
                # creates self.userSelections...
                self.SelectedSettings()
                
                if printTest == True:
                    self.PRINTout()
            
            # save storefront configuration
            self.familyObj.storefront_save_config(self.selectedSystem, self.userConfigs)

            return(None)

    
    ###############
    ## TEST MAIN ##
    ###############
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