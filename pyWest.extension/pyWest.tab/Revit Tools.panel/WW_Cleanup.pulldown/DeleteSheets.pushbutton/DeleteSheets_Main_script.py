"""
The whole stack firing Main() is placed in a try_except pattern
in order to reveal the file and line number of any error that causes
the program to fail

REMEMBER THAT INSTANTIATED OBJECTS CAN BE CONTINOUSLY
MODIFIED BY THEIR METHODS
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

    import CleanupModel_Engine

    """
    DANGEROUS - CANNOT BE UNDONE!
    """

    def Main():
        # set the active Revit application and document
        doc = __revit__.ActiveUIDocument.Document

        t = Transaction(doc, 'Deleting all sheets from the document')
        t.Start()

        # delete sheets
        CleanupModel_Engine.RevitCleanupTools(doc).DeleteSheets()

        t.Commit()


    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())