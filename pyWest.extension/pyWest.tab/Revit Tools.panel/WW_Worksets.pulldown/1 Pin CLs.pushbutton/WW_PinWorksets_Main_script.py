"""
Pin/Unpin Elements in 
"Control Line" workset
"""
import traceback
import os
import sys

try:
    # imports for Revit API
    import clr
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    from Autodesk.Revit.DB import *

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