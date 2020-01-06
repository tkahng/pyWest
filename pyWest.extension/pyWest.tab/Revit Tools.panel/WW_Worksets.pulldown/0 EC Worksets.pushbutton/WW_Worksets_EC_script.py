"""

Create default worksets for
WeWork EC models 

"""

import sys
sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
import os
import traceback

try:
    ## imports for Windows Form
    #import clr
    #clr.AddReference("System.Drawing")
    #clr.AddReference("System.Windows.Forms")

    #import System.Drawing
    #import System.Windows.Forms

    #from System.Drawing import *
    #from System.Windows.Forms import *

    ## imports for Revit API
    #import clr
    #clr.AddReference('RevitAPI')
    #clr.AddReference('RevitAPIUI')
    #from Autodesk.Revit.DB import *

    import WW_Worksets_Engine as WSE

    def Main():
        WSE.WorksetTools().Run_WW_Worksets_Script(EC=True)
        return(True)

    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())