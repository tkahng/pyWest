"""
TESTED IN REVIT 2017

This script effectively explodes geometry
by extracting the base surfaces from the
geometry and adding them back to the document

namespace ImportSAT_Rhino
public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)

OOP:
method(): action; method: property
"""
import traceback
import os

try:
    # imports for Windows Form
    import clr
    clr.AddReference("System.Drawing")
    clr.AddReference("System.Windows.Forms")
    from System import Array # convert .net arrays to python lists
    import System.Drawing
    import System.Windows.Forms
    from System.Drawing import *
    from System.Windows.Forms import *

    # imports for Revit API
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    from Autodesk.Revit.DB import *
    from Autodesk.Revit.Attributes import *
    from Autodesk.Revit.UI import * # for windows form - not in original code


    class ImportSAT_Rhino:
        def __init__(self, doc):
            self.doc = doc

            # UI object
            self.openFileDialog = None

            # default SAT import options
            self.satImportOptions = SATImportOptions()

        def UI_Revit_Archive(self):
            # this form is derived from Revit's classes
            self.openFileDialog = openFileDialog("SAT file (*.sat)|*.sat")
            # in C# closer to: self.openFileDialog.Title("Select SAT file to import")
            self.openFileDialog.Title = "Select SAT file to import"
            self.openFileDialog.Show()

            """
            # get form outputs
            selectedModelPath = self.openFileDialog.GetSelectedModelPath()
            self.openFileDialog.Dispose()
            for i in selectedModelPath:
                satImportPaths = ModelPathUtils.ConvertModelPathToUserVisiblePath(i)
            """

        def UI(self):
            # windows form: open file dialog
            self.openFileDialog = System.Windows.Forms.OpenFileDialog() # create file open dialog object
            self.openFileDialog.Filter = "SAT file (*.sat)|*.sat"
            self.openFileDialog.InitialDirectory = os.path.expanduser("~\Desktop")
            self.openFileDialog.Multiselect = True
            self.openFileDialog.ShowDialog()

        def Run_ImportSAT_Rhino(self):
            # run windows form
            self.UI()

            currentView = FilteredElementCollector(self.doc).OfClass(View).ToElements()[0] # view that model will be in??? shouldn't matter but it does

            # get form outputs
            if DialogResult.OK:
                satImportPaths = [i for i in self.openFileDialog.FileNames]
            try:
                for i in satImportPaths:
                    t = Transaction(self.doc, 'Import SAT')
                    t.Start()

                    # import SAT file
                    elementId = self.doc.Import(r"{0}".format(i), self.satImportOptions, currentView)
                    
                    # extract base geometry - where is Options() form again? 
                    geometryList = self.doc.GetElement(elementId).get_Geometry(Options()).GetEnumerator()
                    for geoInstance in geometryList:
                        nestedGeoList = geoInstance.GetSymbolGeometry().GetEnumerator() # what was this get_SymbolGeometry in C#; is a problem with decompiling???
                        for j in nestedGeoList:
                            FreeFormElement.Create(self.doc, j)
                    
                    # delete original imported model after extracting base geometry
                    self.doc.Delete(elementId) 
                    t.Commit()

            except:
                TaskDialog.Show("Error Importing", "Something went wrong: {0}".format(traceback.format_exc()))

    def Main():
        # set the active Revit application and document
        doc = __revit__.ActiveUIDocument.Document

        # Run_ImportSAT_Rhino import class
        importObj = ImportSAT_Rhino(doc)
        importObj.Run_ImportSAT_Rhino()

    if __name__ == "__main__":
        Main()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())    
