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
    import math
    import clr
    
    # imports for Revit API
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    from Autodesk.Revit.DB import *
    
    import sys
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 3, r"0 Lib"))
    import Takeoff_Engine

    def Main():
        # PSUEDO CODE
        # main controls gui
        # main calls engine
        # engine calculates, some methods need external help, transfer through JSON
        # within engine call external instructions for rhino/revit conversion - PYTHON 3 BASED
        # within that it calls ww_rhinoRevit conversion - PYTHON 3 BASED
        # JSON output here is read and engine uses it to finish operation
        # whatever is done to revit objects with written estimates
        # output is given to gui
        
        ITtestObj = Takeoff_Engine.QTOTools()
        #ITtestObj.CollectUSF()
        # ITtestObj.DeskTools - you can't double call classes only methods within them - HOW DO YOU CALL THIS?
        #ITtestObj.CollectDesks()
        #ITtestObj.CollectFinishedFloors()
        #ITtestObj.CollectConferenceRooms()
        #ITtestObj.CollectQtyITrooms()
        #ITtestObj.CollectConferenceRooms()
        ITtestObj.EstimateCableTrays()
        
    if __name__ == "__main__": 
        Main()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())