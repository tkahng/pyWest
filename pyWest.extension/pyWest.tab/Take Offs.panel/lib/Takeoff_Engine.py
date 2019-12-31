"""
pyVersion = IronPython 2.7xx


"""
import os
import sys
import logging
import math
import _csv as csv
import json
import math

import System
from System import Array
from System.Collections.Generic import *

# imports for Windows Form
import clr
# imports for Revit API
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
import Autodesk
from Autodesk.Revit.DB import *

rpwLib = r"G:\Shared drives\Prod - BIM\05_Regional\USCI WEST\pyWest_HeavyFiles\Dependencies\revitpythonwrapper-master" # common lib folder
sys.path.append(rpwLib)
import rpw

# import partial Rhinocommon API - C# library - same api as Rhino3dm on Python 3.7xx
clr.AddReference(r"Rhino3dmIO.dll")
import Rhino as rh

import WW_RhinoRevitConversion as RRC # only run this in Python 3.7xx environment
import WW_ExternalPython as EP
import WW_DataExchange as DE

#############
## UTILITY ##
#############
class Utilities:
    def __init__(self):
        # derived parameters
        self.roomObjs = None
        self.roomLevelNames = None
    def __repr__(self):
        pass
    def CollectRooms(self):
        # FilteredElementCollector(self.doc).OfClass(SpatialElement)
        self.roomObjs = [i for i in FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Rooms) if "container" not in i.Level.Name.lower()]

        self.roomLevelNames = [i.Level.Name for i in self.roomObjs]
    def ParseLevelNamesForInt(self, levelNamesList):
        levelIntList = []
        for i in levelNamesList:
            tempList = []
            for j in i:
                if type(j) == int:
                    print(True)
                elif j == ".":
                    print(True)
    def WriteObjParameter(self):
        """
        /// <summary>
        /// Create shared parameter for Rooms category
        /// </summary>
        /// <returns>True, shared parameter exists; false, doesn't exist</returns>
        private bool CreateMyRoomSharedParameter()
        {
            // Create Room Shared Parameter Routine: -->
            // 1: Check whether the Room shared parameter("External Room ID") has been defined.
            // 2: Share parameter file locates under sample directory of this .dll module.
            // 3: Add a group named "SDKSampleRoomScheduleGroup".
            // 4: Add a shared parameter named "External Room ID" to "Rooms" category, which is visible.
            //    The "External Room ID" parameter will be used to map to spreadsheet based room ID(which is unique)

            try
            {
                // check whether shared parameter exists
                if (ShareParameterExists(RoomsData.SharedParam))
                {
                    return true;
                }

                // create shared parameter file
                String modulePath = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                String paramFile = modulePath + "\\RoomScheduleSharedParameters.txt";
                if (File.Exists(paramFile))
                {
                    File.Delete(paramFile);
                }
                FileStream fs = File.Create(paramFile);
                fs.Close();

                // cache application handle
                Autodesk.Revit.ApplicationServices.Application revitApp = m_commandData.Application.Application;

                // prepare shared parameter file
                m_commandData.Application.Application.SharedParametersFilename = paramFile;

                // open shared parameter file
                DefinitionFile parafile = revitApp.OpenSharedParameterFile();

                // create a group
                DefinitionGroup apiGroup = parafile.Groups.Create("SDKSampleRoomScheduleGroup");

                // create a visible "External Room ID" of text type.
                ExternalDefinitionCreationOptions ExternalDefinitionCreationOptions = new ExternalDefinitionCreationOptions(RoomsData.SharedParam, ParameterType.Text);
                Definition roomSharedParamDef = apiGroup.Definitions.Create(ExternalDefinitionCreationOptions);

                // get Rooms category
                Category roomCat = m_commandData.Application.ActiveUIDocument.Document.Settings.Categories.get_Item(BuiltInCategory.OST_Rooms);
                CategorySet categories = revitApp.Create.NewCategorySet();
                categories.Insert(roomCat);

                // insert the new parameter
                InstanceBinding binding = revitApp.Create.NewInstanceBinding(categories);
                m_commandData.Application.ActiveUIDocument.Document.ParameterBindings.Insert(roomSharedParamDef, binding);
                return false;
            }
            catch (Exception ex)
            {
                throw new Exception("Failed to create shared parameter: " + ex.Message);
            }
        }
        """
    def ReadObjParameter(self):
        pass

###########
## DESKS ##
###########
class DeskTools:
    def __init__(self):
        # global parameters/variables
        self.deskDict = {"1_Person-Office-Desk": {"nested": False,
                                                  "level" : None},
                         "Enterprise_Amazon_desk": {"nested": False,
                                                    "level" : None},
                         "PXi-OfficeDesk": {"nested": False,
                                            "level" : None},
                         "WWi-OfficeDesks-Multiple": {"nested": True,
                                                      "level" : None},
                         "WWi-OfficeDesk-Column": {"nested": True,
                                                   "level" : None}
                         }
        self.ITRoomDicts = {"Family": {"Serve-IT_Room-Front_Array-Prototype": {"nested": True},
                                       "Serve-IT_Room-Prototype-v2"         : {"nested": True}
                                            },
                            "Room"  : {"names": ["IT"]
                                            }
                                 }
        self.PrinterKnookDict = {}
    def __repr__(self):
        pass    
    def CollectDesks(self):
        """
        there is a difference between FamilyInstance and FamilySymbol
        FamilyInstance Class - is any kind of family no just furniture systems, 
        which is why OfCategory good to use

        comparing data types - i.GetType().Name | if this already symbol this won't work
        this is a family object
        Symbol is not a class obj, but Family is as is FamilyInstance and FamilySymbol
        """

        furnitureSysObjs = [i for i in FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_FurnitureSystems) if i.GetType() != FamilySymbol and i.Symbol.Family.Name in self.deskDict and "container" not in self.doc.GetElement(i.LevelId).Name.lower()]
        deskObjs = [i.Symbol.Family for i in furnitureSysObjs]
        deskObjLevelObjs = [self.doc.GetElement(i.LevelId).Name for i in furnitureSysObjs]

        print(deskObjs)
        print(deskObjLevelObjs)
    def CollectQtyPrinterKnooks(self):
        # use room collection from utilities
        pass
    def CollectQtyITrooms(self):
        self.CollectRooms()

        # cross check a given family and room program, use room collection from utilities
        ITroomObjs = [j for i in self.roomObjs for j in list(i.GetParameters("Name")) if j.AsString() in self.ITRoomDicts["Room"]["names"]]

        self.qtyITRooms = len(ITroomObjs)
        print(self.qtyITRooms)

###################
## AUDIO / VIDEO ##
###################
class AudioVideoTools:
    def __init__(self):
        # derived parameters
        self.roomObjs = []

        # room name lists
        self.conferenceRoomNames = ["Conference Room", "WWLO", "CONF ROOM"]
        self.eventSpaceNames = []
    def __repr__(self):
        pass
    def CollectConferenceRooms(self):
        self.CollectRooms()

        # cross check a given family and room program, use room collection from utilities
        conferenceRoomObjs = [j for i in self.roomObjs for j in list(i.GetParameters("Name")) if j.AsString() in self.conferenceRoomNames]

        print(conferenceRoomObjs)
    def CollectEventSpace(self):
        # find into about projectors + screens; room calculation point
        pass
    def GetSFofFloorNotInOffice(self): # do this
        pass
    def QTYofOfficeWithMoreThan10(self):
        # this is for card readers
        pass

    def Run_IT_Budget(self):
        self.CollectDesks()

class RoomData_IT:
    def __init__(self):
        # main class output
        self.roomDataDict = {}
        
        # for isolating non office spaces
        self.programTypes = ["CIRCULATE"]

        # derived parameters
        self.floors = None
        self.floorNames = None
        self.uniqueFloorNames = None
        self.floorLevelIds = None
        self.floorLevelObjs = None
        
        # instantiate JSON object
        self.jsonExchange = DE.JSONTools()
    def __repr__(self):
        return("Room Data Class")
    def CollectUSF(self):
        # collect areas with usf in the name; there should only be one in our current template
        areaObjs = [i for i in FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Areas) if "usf" in i.AreaScheme.Name.lower()]
        for i in areaObjs:
            levelObj = i.Level
            levelName = levelObj.Name
            area = i.Area
            self.roomDataDict["{0}".format(levelName)] = {"USF": area}
    def CollectFinishedFloors(self):
        # MDF - main distribution facility - count
        # IDF - intermidiate distribution facility - count

        self.floors = [i for i in FilteredElementCollector(self.doc).OfClass(Floor)]
        self.floorNames = [i.Name for i in self.floors]
        self.uniqueFloorNames = set(self.floorNames)
        self.floorLevelIds = [i.LevelId for i in self.floors]
        self.floorLevelObjs = [self.doc.GetElement(i) for i in self.floorLevelIds]
        print(uniqueFloorNames)
        #print(self.floorLevelObjs)
        #print(self.floorLevelIds)
        return()
    def EstimateCableTrays(self):
        # get method name in script
        # use this to autoname json file for external programs
        
        def ReduceCrvSegsToPts(segments):
            # nestedBoundarySegmentList --> segmentList --> segment
            # for i                         for j           for k        
            ptList = []
            for nestedSegList in segments:
                #print("This rooms contains {0} nested elements".format(len(nestedSegList)))
                tempNestedSegList = []
                for segList in nestedSegList:
                    tempSegList = []
                    #print("BoundarySegment List contains {0} elements".format(len(segList)))
                    #print(segList)
                    #print(type(segList))
                    for segment in segList:
                        #print(type(segment))
                        crv = segment.GetCurve()
                        
                        startPt = (crv.GetEndPoint(0).X, crv.GetEndPoint(0).Y, crv.GetEndPoint(0).Z)
                        endPt =   (crv.GetEndPoint(1).X, crv.GetEndPoint(1).Y, crv.GetEndPoint(1).Z)
                        crvPts = (startPt, endPt)
                        
                        tempSegList.append(crvPts)
                    tempNestedSegList.append(tempSegList)
                ptList.append(tempNestedSegList)
            #print(len(ptList))
            #print(ptList)
            
            return(ptList)
            
        # Cable Trays - linear figure byproduct of SqF of corridor
        self.CollectRooms()

        # collect data | assume single value in parameter list
        circulationRoomObjs = [i for i in self.roomObjs for j in list(i.GetParameters("ProgramType")) if j.AsString() in self.programTypes]
        circulationRoomNames = [j.AsString() for i in circulationRoomObjs for j in list(i.GetParameters("Name"))]
        circulationRoomLevels = [i.Level.Name for i in circulationRoomObjs]
        #print(circulationRoomNames)
        #print(circulationRoomLevels)

        # curve segments in nested lists [roomobject[list[crvSegments]]]
        circulationRoomSegObjs = [i.GetBoundarySegments(SpatialElementBoundaryOptions()) for i in circulationRoomObjs]
        #print(len(circulationRoomSegObjs))
        
        # json file name | currentFileName<>targetFileName
        jsonFileName = "{0}__TO__{1}".format(os.path.basename(__file__).split(".")[0], self.extensionFileName.split(".")[0])
        
        # write JSON revit objects - conversion to simple must be done here
        ptConversionData = ReduceCrvSegsToPts(circulationRoomSegObjs)
        self.jsonExchange.WriteJSON(         data = ptConversionData, 
                                         filePath = self.jsonFolderLocation, 
                                         fileName = jsonFileName)
        
        # send revit geometric data to external rhino python file to calculate in rhino api
        # in external script use sys.argv[i] to obtain arguments sent from here | separated by spaces, not commas
        # shell=True works better in revit because the cmd window is supressed
        externalPyArgs = ["EstimateCableTrays cat"]
        EP.ExternalPythonEngine(externalScriptPath = self.engineExtensionPath,
                                         pyVersion = "python3",
                                          jsonArgs = externalPyArgs).Run_Subprocess(spPrintOutput=True, 
                                                                                    spPrintErrors=True,
                                                                                         useShell=True)
        # read results from json file - written by external python engine
        #externalPythonOutput = self.jsonExchange.ReadJSON(r"{0}\centerlineLength.json".format(self.jsonFolderLocation))
        #print(externalPythonOutput)
        
#########################
## IT BUDGET ESTIMATES ##
#########################
class ITBudget(DeskTools, AudioVideoTools, RoomData_IT):
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
        RoomData_IT.__init__(self)
    def __repr__(self):
        pass
    def Run_ITBudget(self):
        # run the stuff

        # export the stuff
        pass

##################    
## PARENT CLASS ##
##################
"""
Instantiate all QTO classes by calling this class.
It will open all variables and data up for use. 

* YOU ALSO NEED IT TO USE THE REVIT DOC OBJS *

In the future this will be used to merge the outputs
of all QTO categories in order to creat one single
QTO tool
"""
class QTOTools(Utilities, ITBudget):
    def __init__(self):
        # ATTRIBUTES / PROPERTIES
        # LOOK INTO THE @property decorator

        # revit doc objects
        # __revit__ = Autodesk.Revit.Application | predefined by RevitPythonShell
        #             Autodesk.Revit.UI.ExternalCommandData()
        self.app = __revit__.Application
        self.version = self.app.VersionNumber.ToString()
        self.uidoc = __revit__.ActiveUIDocument
        self.doc = __revit__.ActiveUIDocument.Document
        self.currentView = self.uidoc.ActiveView
        self.projectName = self.doc.Title

        # universal variables
        self.collector = FilteredElementCollector(self.doc) # this is not working as a shared self.variable
        self.viewCollector = FilteredElementCollector(self.doc, self.currentView.Id)
        self.tol = 0.0001
        
        # check if JSON_talk folder exists in directory, if not create it
        self.jsonSavePath = r"{0}\JSON_talk".format(os.path.dirname(__file__))
        if os.path.exists(self.jsonSavePath):
            self.jsonFolderLocation = self.jsonSavePath # JSON file locations - saved in this file's directory
        else:
            # create JSON folder
            os.mkdir(self.jsonSavePath)
            self.jsonFolderLocation = self.jsonSavePath
        
        # Python 3.7xx engine extension for rhino geometry operations
        self.extensionFileName = "Takeoff_Engine_Py3ext.py"
        self.engineExtensionPath = r"{0}\{1}".format(os.path.dirname(__file__), self.extensionFileName)

        # instantiate Rhino<>Revit Conversion
        self.conversionObj = RRC.Utilities()        

        # linked models
        self.allRVTLinks = self.collector.OfClass(RevitLinkInstance) # Autodesk.Revit.DB. LINK INSTANCE
        self.allRVTLinks2 = self.collector.OfCategory(BuiltInCategory.OST_RvtLinks) # LINK TYPE
        self.allRVTLinkIDs = [i.Id for i in self.allRVTLinks]
        
        # class inheritance / polymorphism
        Utilities.__init__(self)
        ITBudget.__init__(self)
    def __repr__(self):
        pass
    def Run_CalculateAllEstimates(self):
        # generate estimate for IT budget
        self.Run_IT_Budget()

