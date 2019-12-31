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
    
    
    def Main():
        pass


    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())