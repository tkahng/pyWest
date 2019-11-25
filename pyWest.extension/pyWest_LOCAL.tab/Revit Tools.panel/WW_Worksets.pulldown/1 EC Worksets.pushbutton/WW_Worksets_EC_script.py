"""

Create default worksets for
WeWork EC models 

"""

import sys
sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
import os
import traceback

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
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

    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
    import WW_Worksets_Engine as WSE

    def Main():
        WSE.WorksetTools().Run_WW_Worksets_Script(EC=True)
        return(True)

    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())