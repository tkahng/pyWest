"""
Estimate Takeoff for IT Department
"""
__author__ = 'WeWork VDC West'
__version__ = "4.0"

import traceback
import os

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    try:
        from logger import log
        log(__file__)
    except: pass # __file__ cannot be tested in shell
    
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
    
    import sys
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 3, r"0 Lib"))
    import Takeoff_Engine

    def Main():
        
        TakeoffObj = Takeoff_Engine.CalculateAllEstimates()
        TakeoffObj.Run_CalculateAllEstimates()

    if __name__ == "__main__": 
        Main()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())