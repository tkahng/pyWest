"""
Open Revit model in order
to export a specific schedule
"""
import traceback
import os
import sys

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

    import RVTExportSchedules_Engine as RVTE
    
    ##############################
    # COLLECT FILE PATHS         #
    ##############################    
    def TestFilePaths(local=True):
        if local == True:
            filePaths = [r"C:\Users\aluna\Desktop\TEST REVIT FILES\SEA 316 Florentia St P1.rvt",
                         r"C:\Users\aluna\Desktop\TEST REVIT FILES\VAN_288 E Broadway_HQ.rvt"]
            
        else:
            # TEST BIM 360 PATHS
            filePaths = [r"BIM 360://NA SEA 411 Union St - P1/SEA_411 Union_P1.rvt"]
        
        return(filePaths)
    
    def Main():
        # collect RVT links
        RVTFilePaths = TestFilePaths(local=True)        
        
        # export method found in Autodesk.Revit.DB.Document.Export("folder","name",options)
        RVTE.ParentClass(RVTFilePaths).Run_ParentClass()
        

    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())