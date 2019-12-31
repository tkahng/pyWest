"""
Pin/Unpin Elements in 
"Control Line" workset
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
    # imports for Revit API
    import clr
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    from Autodesk.Revit.DB import *

    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
    import Pin_Worksets_Engine as PW

    def Main():
        doc = __revit__.ActiveUIDocument.Document

        worksetName = 'WW-Control Lines'

        t = Transaction(doc, 'Pin Workset Elements')
        t.Start()

        PW.PinningTools(doc).PinUnpinElementsInWorkset(worksetName, unpin=False) # pin

        t.Commit()

        return(None)

    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())    