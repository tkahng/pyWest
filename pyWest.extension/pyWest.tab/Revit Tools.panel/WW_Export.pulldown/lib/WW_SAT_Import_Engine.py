"""
This module is used in conjunction with the rhino export to revit
button in Rhino. You open a family template file (any? usually furniture), and select
the folder of the object which you want to import.

The Rhino export will have parsed all the elements that belonged to the same
layer, appended their fileNames with an index unique to each element, and recorded
that geometry's GUID for  in the event of an import error.
"""

# standard modules
import clr
import sys
import traceback

# revit api modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *
from Autodesk.Revit.Attributes import *
from Autodesk.Revit.UI import * # for windows form - not in original code

# SAT import module
import WW_SAT_Import_GUI as SATGUI

class ImportSAT_Rhino:
    def __init__(self, selectionType=0):
        # input parameter
        self.selectionType = selectionType
        
        # revit doc objects
        self.doc = __revit__.ActiveUIDocument.Document
        self.currentView = __revit__.ActiveUIDocument.ActiveView

    def ExtractGeometry(self, modelFilePath):
        t = Transaction(self.doc, 'Import SAT')
        t.Start()
    
        # import SAT file
        modelObjId = self.doc.Import(r"{0}".format(modelFilePath), SATImportOptions(), self.currentView)
        print(modelObjId)
        
        # extract base geometry | where is Options() from?
        geometryList = self.doc.GetElement(modelObjId).get_Geometry(Options()).GetEnumerator()
        
        for geoInstance in geometryList:
            nestedGeoList = geoInstance.GetSymbolGeometry().GetEnumerator()
            for j in nestedGeoList:
                FreeFormElement.Create(self.doc, j)
        
        # delete original imported model after extracting base geometry
        self.doc.Delete(modelObjId) 
        t.Commit()        
    
    def Run_ImportSAT_Rhino(self):
        # run windows form
        formObj = SATGUI.ImportSAT_Rhino_GUI()
        formObj.RunForm(selectionType=self.selectionType)
        
        if formObj.results:
            # loop through geometry selections and convert to revit objects
            try:
                for filePath in formObj.results:
                    print(filePath)
                    if filePath[-4:] == ".sat":
                        self.ExtractGeometry(modelFilePath=filePath)
            except:
                TaskDialog.Show("Error Importing", "Something went wrong: {0}".format(traceback.format_exc()))  
        
        else:
            sys.exit(0) # 0 == sucess 
        
       