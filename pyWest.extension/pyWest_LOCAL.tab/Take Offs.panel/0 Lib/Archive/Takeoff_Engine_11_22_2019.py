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
import Autodesk
from Autodesk.Revit.DB import *

##################################
## I DON'T FUCKING KNOW ANYMORE ##
##################################
class RandomShit:
    def CollectAllRoomFamilyParameters(self):
        # are rooms families or family systems? and the are their types within them? - why do they not have types
        FamilyInstanceFilter = ElementClassFilter(Autodesk.Revit.DB.SpatialElement)
        #AllIds = [i for i in FilteredElementCollector(self.doc).WherePasses(FamilyInstanceFilter) if type(i) == Autodesk.Revit.DB.Architecture.Room and i.Level.Name != "CONTAINER LEVEL"]
        #AllIds = FilteredElementCollector(self.doc).WherePasses(FamilyInstanceFilter)
        AllIds = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType() 
        
        AllFamilyInstances = [i for i in FilteredElementCollector(self.doc).WherePasses(FamilyInstanceFilter).ToElements() if type(i) == Autodesk.Revit.DB.Architecture.Room and i.Level.Name != "CONTAINER LEVEL"]
        #for i in AllFamilyInstances:
            #print(i)
    
        famtypeitr = AllIds.GetElementIdIterator()
        
        #for id in AllIds:
            #for j in id:
                #print(j.Parameter('ProgramType'))
            #family = self.doc.GetElement(id)            
            
            #param = family.Parameter('ProgramType') # needs to be GUID
            #print(param)
            #param.Set(2*inc)
            #inc = inc + 1
        
        paramList = []
        for familyInstance in AllFamilyInstances[:1]:
            try: familySymbol = familyInstance.Symbol
            except: familySymbol = None
            
            if familySymbol: family = familySymbol.Family
            else: family = None

            # Add Instance Parameter names to list
            for param in familyInstance.Parameters:
                paramList.append(param.Definition.Name)
        
            # Add Type Parameter names to list
            if familySymbol:
                for param in familySymbol.Parameters:
                    paramList.append(param.Definition.Name)
        
            # Add Family Type Parameter names to list
            if family:
                for param in family.Parameters:
                    paramList.append(param.Definition.Name)
            
            print(paramList)
    
    def CollectArea_Areas(self):
        areaObj = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements() # needs to be the actual object
        areaNames = [i.Name for i in areaObj]
        areaArea = [i.Area for i in areaObj] # new object with new methods and properties aftern instantiation
        for i,j in enumerate(areaArea):
            print("{0}: {1}".format(areaNames[i], j))
    
    def SetNewFamilyParameter(self):
        pass 

###########################
## GYPSUM WALL ESTIMATES ##
###########################
class GypEstimate:
    """
    This is an estimate for gyp walls in the project
    """
    def __init__(self):
        pass
    def CollectGypWalls(self):
        pass
    
    def GetGypWallAreas(self):
        pass
    
    def CalculateGypWallPanelEstimate(self):
        pass
    
    def CalculateGypWallCost(self):
        pass
    
    def Run_GypEstimate(self):
        pass

###########
## DESKS ##
###########
class DeskTools:
    def __init__(self):
        # global parameters/variables
        self.deskDict = {"1_Person-Office-Desk": {"nested": False
                                                  }, 
                         "Enterprise_Amazon_desk": {"nested": False
                                                    },
                         "PXi-OfficeDesk": {"nested": False
                                            },
                         "WWi-OfficeDesks-Multiple": {"nested": True
                                                      },
                         "WWi-OfficeDesk-Column": {"nested": True
                                                   }
                         }
    def CollectDesks(self):
        # filter out by CONTAINER LEVEL and family name
        furnitureSystemList = [i for i in self.collector.OfCategory(BuiltInCategory.OST_FurnitureSystems)]
        print(furnitureSystemList)
        print(len(furnitureSystemList))
    def CollectQtyPrinterKnooks(self):
        pass
    
    def CollectQtyITrooms(self):
        pass

###################
## AUDIO / VIDEO ##
###################
class AudioVideoTools:
    def __init__(self):
        pass
    def CollectConferenceRooms(self):
        possibleRoomNames = ["Conference Room",
                             "WWLO"
                            ]
    
    def CollectEventSpace(self):
        # find into about projectors + screens; room calculation point
        
        pass
    
    ##############
    ## SECURITY ##
    ##############
    def GetSFofFloorNotInOffice(self):
        pass
    
    def QTYofOfficeWithMoreThan10(self):
        # this is for card readers
        pass
    
    def Run_IT_Budget(self):
        self.CollectDesks()

#########################
## IT BUDGET ESTIMATES ##
#########################
class IT_Budget(DeskTools, AudioVideoTools):
    """
    This is an estimate for IT budgets that uses...
    
    TRY THIS ON 830 HOLIDAY(Classic); 288 E BROADWAY(HQ)
    TEST ON PROJECTS 2755 CANYON, BOULDER CO; 6060 SILVER AVE, VANCOUVER BC
    
    Do families report number of cables and outlet per office
    
    Need to figure out csv tool and connect to google sheets
    """
    def __init__(self, projectNum=1, tierNum=1, WWproductType="Classic"):
        # input parameters
        self.projectNum = projectNum # P1 has more upfront costs than subsequent Ps...
        self.tierNum = tierNum # copper vs fiber
        self.WWproductType = WWproductType

        # output parameters
        self.usf = None
        self.levels = None
        self.floors = None
        
        # inherited classes
        DeskTools.__init__(self)
        AudioVideoTools.__(self)
    
    ############################
    ## INFORMATION TECHNOLOGY ##
    ############################
    def CollectUSF(self):
        pass
    
    def CollectFinishedFloors(self):
        # MDF - main distribution facility - count
        # IDF - intermidiate distribution facility - count
        # Cable Trays - linear figure byproduct of SqF of corridor
        
        self.floors = [i for i in FilteredElementCollector(self.doc).OfClass(Floor)]
        self.floorNames = [i.Name for i in self.floors]
        self.floorLevelIds = [i.LevelId for i in self.floors]
        print(self.floorNames)
        print(self.floorLevelIds)

##################    
## PARENT CLASS ##
##################
class QTOTools(GypEstimate, IT_Budget):
    def __init__(self):
        # class inheritance / polymorphism
        GypEstimate.__init__(self)
        IT_Budget.__init__(self, projectNum=1, tierNum=1, WWproductType="Classic")
        
        # input parameters - revit doc objects
        self.app = __revit__.Application
        self.version = self.app.VersionNumber.ToString()
        self.uidoc = __revit__.ActiveUIDocument
        self.doc = __revit__.ActiveUIDocument.Document
        self.currentView = self.uidoc.ActiveView
        
        # derived parameters
        self.collector = FilteredElementCollector(self.doc)
        self.viewCollector = FilteredElementCollector(self.doc, self.currentView.Id)
        
        # universally needed objects
        #self.levelList = [(i, i.Name) for i in FilteredElementCollector(self.doc).OfClass(Level) if i.Name != "CONTAINER LEVEL"]

        # FAMILY PARSING
        
        # linked models
        self.allRVTLinks = FilteredElementCollector(self.doc).OfClass(RevitLinkInstance) # Autodesk.Revit.DB. LINK INSTANCE
        self.allRVTLinks2 = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_RvtLinks) # LINK TYPE
        self.allRVTLinkIDs = [i.Id for i in self.allRVTLinks]
    
    def Run_CalculateAllEstimates(self):
        # generate estimate for IT budget
        self.Run_IT_Budget()
        
    