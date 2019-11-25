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
"""
These tools are intended to revert a revit model
that has been given to Wework by a landlord back
to its original state before views, sheets, or planes
while also keeping intact the geometry that was created.
This will allow us to recreate the document

ALL OF THESE ARE NOW DANGEROUS WITH TRANSACTION IN
MAIN IT PREVENTS THE SAVE STATE. MODIFICATIONS
CANNOT BE REVERESED

### CLEAN UP SHOULD JUST BE A SINGLE BUTTON THAT 
FIXES PROEJCT TO HOW WE WOULD LIKE IT SET UP
WW PARAMETERS, VIEWS, AND SUCH ###
"""

class RevitCleanupTools:
    def __init__(self, doc):
        self.doc = doc

        # built in objects
        self.collector = FilteredElementCollector(self.doc)

        # derived outputs
        self.allViewIDs = None
        self.allSheetIDs = None
        self.unhostedPlaneIDs = None
        self.allRVTLinkIDs = None

    # COLLECT
    def CollectViews(self):
        # collect views
        #views3D = self.collector.OfClass(View3D)
        #viewsDrafting = self.collector.OfClass(ViewDrafting)
        #viewsPlan = self.collector.OfClass(ViewPlan)
        #viewsSection = self.collector.OfClass(ViewSection)
        allViews = self.collector.OfClass(View) # already elements

        # just i would separate to element
        self.allViewIDs = [i.Id for i in allViews]
        for i in allViews:
            print(i.Name)

        return(self.allViewIDs)

    def CollectSheets(self):
        # THIS IS INCLUDED IN VIEWS!
        allSheets = self.collector.OfClass(ViewSheet)
        self.allSheetIDs = [i.Id for i in allSheets]

        return(self.allSheetIDs)

    def CollectUnhostedPlanes(self):
        # collection rules - very complex to me; simplify?
        bip = BuiltInParameter.DATUM_TEXT
        provider = ParameterValueProvider(ElementId(bip))
        evaluator = FilterStringEquals()
        rule = FilterStringRule(provider, evaluator, "", False)
        filter = ElementParameterFilter(rule)

        # collect reference planes
        allUnhostedPlanes = self.collector.OfClass(ReferencePlane).WherePasses(filter)
        self.allUnhostedPlaneIDs = [i.Id for i in allUnhostedPlanes]

        return(self.allUnhostedPlaneIDs)

    def CollectRVTLinks(self):
        # collect all RVT links
        allRVTLinks = self.collector.OfCategory(BuiltInCategory.OST_RvtLinks)
        self.allRVTLinkIDs = [i.Id for i in allRVTLinks]

        return(self.allRVTLinkIDs)

    def CollectUnusedFamilies(self):
        pass

    # DELETE
    def DeleteViews(self):
        # DANGEROUS - CANNOT BE UNDONE!

        self.CollectViews() # instantiate view object
        for id in self.allViewIDs:
            try:
                self.doc.Delete(id)
            except:
                print('Cannot delete view')
        return(None)

    def DeleteSheets(self):
        self.CollectSheets()
        for id in self.allSheetIDs:
            try:
                self.doc.Delete(id)
            except:
                print('Cannot delete sheet')
        return(None)

    def DeleteUnhostedPlanes(self):
        self.CollectUnhostedPlanes()
        for id in self.allUnhostedPlaneIDs:
            try:
                self.doc.Delete(id)
            except:
                print('Cannot delete plane')
        return(None)

    def DeleteRVTLinks(self):
        # DANGEROUS - CANNOT BE UNDONE!

        self.CollectRVTLinks()
        for id in self.allRVTLinkIDs:
            try:
                self.doc.Delete(id)
            except:
                print('Cannot delete Revit Link')
        return(None)


# this function is for testing purposes only
def TestMain():
    # set the active Revit application and document
    doc = __revit__.ActiveUIDocument.Document

    object = CleanupTools(doc).DeleteRVTLinks()
    print(object)

if __name__ == "__main__":
    TestMain()