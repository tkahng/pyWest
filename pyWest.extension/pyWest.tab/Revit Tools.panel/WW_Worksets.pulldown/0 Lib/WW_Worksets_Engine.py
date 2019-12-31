"""
(workset name, is workset visible)
"""
import traceback

# imports for Revit API
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *

import WW_Worksets_PopUp as popUP

class WorksetTools:
    def __init__(self):
        self.worksets = None
        self.worksetsEC = None
        
        # set the active Revit application and document
        self.doc = __revit__.ActiveUIDocument.Document
        
        self.collectedArchElements = []
        self.collectedInteriorElements = []
    
    # COLLECT
    def CollectLevels(self):
        # make all point cloud worksets visible == False by default
        self.levels = FilteredElementCollector(self.doc).OfClass(Level)
        levelTuples = [("Link-PC-{0}".format(i.Name), False) for i in self.levels]

        return(levelTuples)
    
    def CollectArchitectureElements(self):
        collector = FilteredElementCollector(self.doc)
        self.walls = collector.OfClass(Wall)
        #self.columns = collector.OfClass(Column)
        
        self.collectedArchElements.extend([self.walls])
        return(self.collectedArchElements)
    
    def CollectInteriorElements(self):
        collector = FilteredElementCollector(self.doc)
        self.furnitureSystems = collector.OfCategory(BuiltInCategory.OST_FurnitureSystems)
        print(self.furnitureSystems)
        self.furniture = collector.OfCategory(BuiltInCategory.OST_Furniture)
        for i in self.furnitureSystems:
            print(i)
        
        self.collectedInteriorElements.extend([self.furnitureSystems, self.furniture])
        return(self.collectedInteriorElements)
    
    # WORKSET DATABASES
    def EC_Worksets(self):
        self.worksetsEC = [("Architecture", True), ("Structure", True),
                           ("Link-CAD", True), ("WW-Control Lines", True)
                          ]
        # add workset for each level in constructed model
        self.worksetsEC.extend(self.CollectLevels())

        return(self.worksetsEC)

    def Project_Worksets(self):
        self.worksets = [("Link-EC", True), ("Link-CAD", False),
                         ("Link-MEP", False), ("Ghosted Desks", False), 
                         ("WW-Control Lines", False), ("WW-Arch", True),
                         ("WW-Interior", True), ("WW-Casework", True)
                        ]
        return(self.worksets)
    
    # UTILITIES
    def ChangeClassObjWorksets(self, elements, worksetId):
        t = Transaction(self.doc, "Moving Elments to the {0} workset".format(worksetId))
        t.Start()
        for i in elements:
            for j in i:
                wsId = j.WorksetId
                wsParam = j.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM) # this is the workset parameter
                print(wsParam.Definition)
                try:
                    wsParam.Set(worksetId)
                except:
                    print(traceback.format_exc())
        t.Commit()    

    # RUN METHODS 
    def Run_WW_Worksets_Script(self, EC=False):
        if self.doc.IsWorkshared == True:
            # consider using while open or whatever here
            t = Transaction(self.doc, 'Creating Worksets')
            t.Start()
            
            # choose either project or ec workset batch
            if EC == True: defaultWorksets = self.EC_Worksets()
            else: defaultWorksets = self.Project_Worksets()
            
            for worksetTuple in defaultWorksets:
                if WorksetTable.IsWorksetNameUnique(self.doc, worksetTuple[0]) == True:
                    newWorkset = Workset.Create(self.doc, worksetTuple[0])
                    visibility = WorksetDefaultVisibilitySettings.GetWorksetDefaultVisibilitySettings(self.doc)
                    visibility.SetWorksetVisibility(newWorkset.Id, worksetTuple[1])

            t.Commit()

        elif doc.IsWorkshared == False:
            # pop up window requiring document to be worksharing enabled
            Application.Run(popUP.WorksharingWarning()) # namespace.class() - just runs not method how???
    
    
    def Run_WW_Worksets_Elements_script(self):
        # collect architecture elements
        wwArchWs = [i for i in FilteredWorksetCollector(self.doc).OfKind(WorksetKind.UserWorkset) if i.Name == "WW-Arch"][0] # fix this to be a dictionary
        wwArchWsId = wwArchWs.Id.IntegerValue
        self.ChangeClassObjWorksets(self.CollectArchitectureElements(), wwArchWsId)
        
        # collect interior elements
        #wwIntWs = [i for i in FilteredWorksetCollector(self.doc).OfKind(WorksetKind.UserWorkset) if i.Name == "WW-Interior"][0]
        #print(wwIntWs.Name)
        #wwIntWsId = wwIntWs.Id.IntegerValue
        #self.CollectInteriorElements()
        #self.ChangeClassObjWorksets(self.CollectInteriorElements(), wwIntWsId)
        
        ## collect level elements
        #wwLevelWs = [i for i in FilteredWorksetCollector(self.doc).OfKind(WorksetKind.UserWorkset) if i.Name == "Shared Views, Levels, Grids"][0]
        #wwLevelWsId = wwLevelWs.Id.IntegerValue
        #self.ChangeClassObjWorksets(self.CollectLevels(), wwLevelWsId)
        

def TestMain():
    #WorksetTools().CollectLevels()
    WorksetTools().EC_Worksets()


if __name__ == "__main__":
    TestMain()