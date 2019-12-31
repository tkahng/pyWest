"""
:tooltip:
EXPORT A SCHEDULE FROM A LIST OF REVIT MODELS
:tooltip:

Copyright (c) 2019 WeWork

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit
"""

__author__ = 'WeWork Buildings Systems'
__version__ = "2.XXX"

import traceback
import os
import sys

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    #######################
    ## MODULES TO IMPORT ##
    #######################
    import os
    import sys
    import time
    import clr
    import re # for level number string parsing
    import logging
    import System
    import math
    #import helpers
    from datetime import datetime 

    from utils import get_schedule_values, get_sheet_key, subprocess_cmd  
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
    from Autodesk.Revit.UI import *
    from Autodesk.Revit.DB import *
    import Autodesk.Revit.UI.Selection

    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System.Drawing')
    from System.Windows.Forms import SaveFileDialog
    from System.Drawing import *
    from System.Drawing import Point
    from System.Windows.Forms import Application, Button, CheckBox, Form, Label
    from System.Collections.Generic import List, IEnumerable
    from System import Array
    from System import DateTime as dt

    sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
    import _csv as csv
    import json

    user = str(System.Environment.UserName)
    
    # helper functions for logging, template revit version checking
    #helpers.get_revit_version(block_access=False)
    #helpers.check_template_version(block_access=False)
    #helpers.log_custom_attributes()
    
    cwd = os.path.dirname(__file__)
    parent = os.path.dirname
    uploader_script = os.path.join(parent(cwd), "lib", "data_uploader.py")
    start = time.time()    

    rpwLib = r"VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\0 Lib\revitpythonwrapper-master" # common lib folder
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 6, rpwLib))
    import rpw
    from rpw import doc, uidoc, DB, UI

    ######################
    ## EXPORT SCHEDULES ##
    #EE###################   
    class ExportScheduleTools:
        def __init__(self):
            pass
        
        def ExportSchedules(self):
            try:
                allSchedules = FilteredElementCollector(self.newModelCurrent).OfClass(ViewSchedule).ToElements()
                selected_schedules = [i for i in allSchedules if i.Name == self.scheduleToExport]
                
                # GUI GET RID OF THIS
                # Prompt for Sheet URL
                #url_param = doc.ProjectInformation.LookupParameter("GoogleSheet")
                #if url_param:
                    #url = url_param.AsString()
                #if not url_param:
                    #value = rpw.ui.forms.TextInput("Paste the Sheet URL", default="https://...")
                    #url = value
                
                url = r"https://docs.google.com/spreadsheets/d/1ph1gMTpT48Lwn-4farmMQozNnfMmvdemTYk2djp-k9Y/edit#gid=0"
                key = get_sheet_key(url)
                if not key:
                    UI.TaskDialog.Show("DriveUpload", "Invalid URL")
                    sys.exit()
                
                # Process Schedules
                schedules_data = []
                name_string = ""
                for schedule in selected_schedules:
                    temp_folder = os.path.expandvars("%temp%\\")
                    now = datetime.now()
                    now_str = now.strftime("%Y-%m-%d_%H%M%S")
                    filename = "Revit_{}".format(now_str)
                    full_filepath = os.path.join(temp_folder, filename)
                    schedules_data.extend(get_schedule_values(schedule))
                print(schedules_data)
                
                if not schedules_data:
                    UI.TaskDialog.Show("DriveUpload", "Check with Gui. This shouldn't happen")
                else:
                    import pickle
                
                    with open(full_filepath, "wb") as fp:
                        pickle.dump(schedules_data, fp)
                
                    python = "python.exe"
                    
                    #python_path = os.path.join(parent(parent(parent(parent(cwd)))), "Lib", "Python35", python)
                    python_path = r"C:\Users\aluna\AppData\Roaming\pyRevitExtensions\pyDesign.extension\pyDesign.tab\Lib\Python35\python.exe"
                    
                    if not os.path.exists(python_path):
                        rpw.ui.forms.Alert(python_path, header="Python Not Found")
                
                    process, out, errmsg = subprocess_cmd(
                        '{python} {script} {key} "{path}"'.format(
                            python=python_path, script=uploader_script, key=key, path=full_filepath
                        )
                    )
                
                    failed = process.returncode
                    end = time.time()
                    if errmsg:
                        print(errmsg)
                    else:
                        print("Success! Run time {}s.".format(end - start))
            except:
                print("What the fuck!")
        
        def Run_ExportScheduleTools(self):
            self.ExportSchedules()

    #######################
    ## OPEN REVIT MODELS ##
    #######################
    class OpenRVTTools:
        def __init__(self):
            # derived parameters
            self.newModel = None
            self.newModelCurrent = None
            self.originalModel = None       
            
            # LOCAL SHIT
            # LOOK FOR A WAY TO IGNORE WARNING WHEN OPENING SO YOU DON'T HAVE TO CLICK OR ANYTHING!!!
            # derived inputs
            #self.openOptions = OpenOptions()
            #self.openOptions.DetachFromCentralOption = DetachFromCentralOption.DetachAndDiscardWorksets
            
            # CLOUD SHIT
            #self.openFromCloud = IOpenFromCloudCallback
            #self.openFromCloud = cloudinterdace()
            #self.openFromCloud = DefaultOpenFromCloudCallback

        def OpenRVT_Local(self):            
            for i, rvtLink in enumerate(self.filePaths):
                self.newModel = __revit__.OpenAndActivateDocument(rvtLink)
                self.newModelCurrent = __revit__.ActiveUIDocument.Document
                
                t = Transaction(self.newModelCurrent, 'Exporting schedule from RVT')
                t.Start()  
                try:
                    # export the required schedules
                    self.Run_ExportScheduleTools()
            
                except:
                    print(traceback.format_exc())
                t.Commit()
                
                # reactivate original doc - must get cloud read to work first
                self.originalModel = __revit__.OpenAndActivateDocument(self.originalModelPath)                
                
                # close opened docs
                self.newModelCurrent.Close(False)
        def OpenRVT_Cloud(self):
            for i, rvtLink in enumerate(self.filePaths):
                # you get the GUIDs from Forge API
                #rvtLink = ModelPathUtils.ConvertUserVisiblePathToModelPath(rvtLink)
                #rvtLink = ModelPathUtils.ConvertCloudGUIDsToCloudPath(projectId, modelId)
                print(rvtLink)
                
                #newModel = __revit__.OpenAndActivateDocument(rvtLink, self.openOptions, True, self.openFromCloud) # file in the cloud
                #newModelCurrent = __revit__.ActiveUIDocument.Document
                #t = Transaction(newModelCurrent, 'Exporting schedule from RVT')
                #t.Start()  
                #try:
                    ## export the required schedules
                    #self.Run_ExportScheduleTools()
            
                #except:
                    #print(traceback.format_exc())
                #t.Commit()
                
                ## reactivate original doc - must get cloud read to work first
                #originalModel = __revit__.OpenAndActivateDocument(self.originalModelPath, self.openOptions, True, self.openFromCloud)                
                
                ## close opened docs
                #newModelCurrent.Close(False)         
            
        def Run_OpenRVT_Local(self):
            # revit version might not be correct how do you correct for this?
            try:
                # open rvt docs in file paths
                self.OpenRVT_Local()
            except:
                print(traceback.format_exc()) 
    
    ##################
    ## PARENT CLASS ##
    ##################   
    class ParentClass(ExportScheduleTools, OpenRVTTools):
        def __init__(self, filePaths):
            # class inheritance
            ExportScheduleTools.__init__(self)
            OpenRVTTools.__init__(self)
            
            # global variables
            self.tol = 0.001           
            
            # these will have to also be current for each opened file
            self.app = __revit__.Application
            self.version = self.app.VersionNumber.ToString()
            self.uidoc = __revit__.ActiveUIDocument
            self.doc = __revit__.ActiveUIDocument.Document
            self.currentView = self.uidoc.ActiveView
            
            # input parameters
            self.filePaths = filePaths
            # derived parameters
            self.scheduleToExport = "WW-Project-USF"             
            
            # local model variables
            self.originalModelPath = self.doc.PathName
            
            # cloud model variables
            #self.cloudPath = self.doc.GetCloudModelPath()
            #self.projectId = self.cloudPath.GetModelGUID()
            #self.modelId = self.cloudPath.GetProjectGUID() 
        
        def Run_ParentClass(self):
            self.Run_OpenRVT_Local()
        

    #---------------------------------------------------------------------------------------------
    def TestMain():
        rvtLinks = [r"BIM 360://NA SEA 411 Union St - P1/SEA_411 Union_P1.rvt"]
        
        # this is automated or interactive
        ParentClass(rvtLinks).Run_ParentClass()

    if __name__ == "__main__":
        TestMain()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())    