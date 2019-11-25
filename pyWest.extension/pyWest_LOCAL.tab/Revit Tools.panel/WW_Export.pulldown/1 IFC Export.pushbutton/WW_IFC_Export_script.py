"""
Export Revit model as IFC
file for use in Archilogic
"""
import traceback
import os
import sys

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
    import math

    # imports for Windows Form
    import clr
    clr.AddReference("System.Drawing")
    clr.AddReference("System.Windows.Forms")

    import System.Drawing
    import System.Windows.Forms

    from System.Drawing import *
    from System.Windows.Forms import *

    # imports for Revit API
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    from Autodesk.Revit.DB import *

    dataExchangePath = ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib")
    sys.path.append(dataExchangePath)
    import Archilogic_Engine
    import Archilogic_GUI
    
    
    def Main():
        # set the active RVT doc
        doc = __revit__.ActiveUIDocument.Document # learn how this works

        ifcSavePath = os.path.expanduser("~\Desktop")
        #ifcSavePath = r"G:\Shared drives\Prod - BIM\07_Global Initiatives\Archilogic IFC Export"
        #ifcRegion = "NA PacNW"
        #ifcProjectName = "Generic Project"
        ifcFileName = doc.Title      

        # export method found in Autodesk.Revit.DB.Document.Export("folder","name",options)
        exportObj = Archilogic_Engine.ExportRevit(doc, app=None, filePath=ifcSavePath, fileName=ifcFileName, ifcOptions=None, checkOutput=True)
        exportObj.Run_IFCExport()
        
        # THIS IS UNLOADING THE EC MODEL MUST FIX THIS


    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())