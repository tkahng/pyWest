import os
import sys
import logging
import System
import math
import _csv as csv
import json
try:
    import rpw
except:
    pass

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
    def __repr__(self):
        return("<DeskTools Object>")
    
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
class ITBudget(DeskTools, AudioVideoTools):
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
        
        # class inheritance / polymorphism
        DeskTools.__init__(self)
        AudioVideoTools.__init__(self)
    
    ############################
    ## INFORMATION TECHNOLOGY ##
    ############################
    def CollectUSF(self):
        #area_values = defaultdict(int)
        #other_schemes_found = 0
    
        # Store aggregate area values by level
        # OST_AreaSchemes	
        # OST_Areas
        areas = self.collector.OfCategory(BuiltInCategory.OST_Areas)
        print(areas)
        for area_element in areas:
            print(area_element)
        #for area_element in rpw.db.Collector(of_category="OST_Areas"):
            #print(area_element)
            #level = area_element.Level
            #area = db.Area(area_element)
            #if area.is_bounded and area.is_placed:
                #if "2327702" in str(area.parameters["Area Scheme Id"].value):
                    #try:
                        #area_value = area.parameters["Area"].value
                        #area_values[level.Name] += area_value
                        #print("Found Area: {0}:{1}".format(level.Name, area_value))
                    #except:
                        #pass
                #else:
                    #other_schemes_found += 1
            #else:
                #print("Area Ignored. Please check for unplaced or unplaced areas.")
    
        #print(
            #str(other_schemes_found)
            #+ " non-USF Area Schemes found. Confirm this is correct"  # noqa
        #)
        #print("=" * 20)
    
        ## Use stored values to set level USF parameter
        #for level in db.Collector(of_category="OST_Levels", is_not_type=True):
            #print("Setting Areas for Level: {}".format(level.Name))
            #level = db.Element(level)
            #area = area_values[level.Name]
            #with db.Transaction("Set USF on Levels"):
                #try:
                    #if found_new_template is True:
                        #level.parameters["WW-USF"].value = area
                    #else:
                        #level.parameters["USF"].value = area
                        #level.parameters["NYSF"].value = area * 0.75
                    #print("USF: {}".format(area))
                    #print("=" * 20)
                #except Exception as errmsg:
                    #helpers.log_exception(errmsg)
                    #helpers.log_stacktrace()    
    
    def CollectFinishedFloors(self):
        # MDF - main distribution facility - count
        # IDF - intermidiate distribution facility - count
        # Cable Trays - linear figure byproduct of SqF of corridor
        
        self.floors = [i for i in FilteredElementCollector(self.doc).OfClass(Floor)]
        self.floorNames = [i.Name for i in self.floors]
        self.floorLevelIds = [i.LevelId for i in self.floors]
        print(self.floorNames)
        print(self.floorLevelIds)
    def Run_ITBudget(self):
        pass

##################    
## PARENT CLASS ##
##################
class QTOTools(ITBudget):
    def __init__(self):
        # THESE ARE ATTRIBUTES
        # LOOK INTO THE @property decorator
        
        # input parameters - revit doc objects
        self.app = __revit__.Application
        self.version = self.app.VersionNumber.ToString()
        self.uidoc = __revit__.ActiveUIDocument
        self.doc = __revit__.ActiveUIDocument.Document
        self.currentView = self.uidoc.ActiveView
        
        # derived parameters
        self.collector = FilteredElementCollector(self.doc)
        self.viewCollector = FilteredElementCollector(self.doc, self.currentView.Id)
        
        # linked models
        self.allRVTLinks = self.collector.OfClass(RevitLinkInstance) # Autodesk.Revit.DB. LINK INSTANCE
        self.allRVTLinks2 = self.collector.OfCategory(BuiltInCategory.OST_RvtLinks) # LINK TYPE
        self.allRVTLinkIDs = [i.Id for i in self.allRVTLinks]
        
        # class inheritance / polymorphism
        ITBudget.__init__(self)        
    
    def Run_CalculateAllEstimates(self):
        # generate estimate for IT budget
        self.Run_IT_Budget()
        
    