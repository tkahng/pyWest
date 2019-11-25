"""
Refactored version of the original
Storefront Tool. Serves as the basis for
Storefront 2.0 Tool. Will be gradually
subsumed by the new version.
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
    
    import clr
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
    from Autodesk.Revit.UI import *
    from Autodesk.Revit.DB import *
    import Autodesk.Revit.UI.Selection    
    
    import sys
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
    import SF2_RhinoRevitConversion as RRC
    import SF2_Families as SFF

    def TestMain():
        # parameters used by all classes/methods
        tol = 0.001
    
        app = __revit__.Application
        version = app.VersionNumber.ToString()
        uidoc = __revit__.ActiveUIDocument
        doc = __revit__.ActiveUIDocument.Document
        currentView = uidoc.ActiveView     
        
        wallList = [i for i in FilteredElementCollector(doc, currentView.Id).OfClass(Wall) if i.Name in SFF.SF_Options().SFFamilyNames().keys()]
        
        # loop through floor - just large collection here
        newRevitCurves = []
        #for walls in wallList:
        # instantiate conversion class
        conversionObj = RRC.Revit2Rhino_Walls(wallList)            
        conversionObj.Run_Revit2Rhino_Walls()
    
    if __name__ == "__main__":
        TestMain()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())