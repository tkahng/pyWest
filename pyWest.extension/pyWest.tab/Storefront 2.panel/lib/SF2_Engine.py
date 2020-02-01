"""
:tooltip:
Module for Storefront 2.0 Engine
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork Design Technology West

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

        
        For fabrication, the families will have to have 
        parameters that are constantly read and reported. 
        An automation script will run and generate a list
        of geometry with the assumption that what is created
        will get built, but if it gets changed by the user, 
        a second script will have to be run that signals an
        update to the storefront system.

        An idea for the future script might be to have a completly
        new family that is more intelligent and complete. - actually
        this is the only way this can be accomplished. The old system
        doesn't matter because Elite will never build it the way it is
        described above
        
        # ALSO REMEMBER THAT DOORS NEED TO BE CORRECTLY PLACED IN SF OTHERWISE THEY FAIL...
        
"""

# pyRevit metadata variables
__title__ = "Storefront 2.0 Engine"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "2404e9eb-9f9d-45e7-8e5c-ff4ca58eacb5"
__parameters__ = []

# standard modules
import clr # noqa E402
import math # noqa E402
import os # noqa E402
import re # noqa E402
import rpw # noqa E402
import sys # noqa E402
import System # noqa E402

from pyrevit import script # noqa E402

# Revit API modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402
import Autodesk.Revit.UI.Selection # noqa E402

# DT West modules
import WW_DataExchange as DE # noqa E402
import WW_ExternalPython as EP # noqa E402
import WW_Debug as DBG # noqa E402
import WW_RhinoRevitConversion as RRC # noqa E402

# SF2 modules
import SF2_GUI as SFGUI # noqa E402
import SF2_Utility as SFU # noqa E402
import SF2_QC as SFQC # noqa E402
import SF2_Families_CleanUp as SFF # noqa E402


############################################################
## TRYING TO UNDERSTAND WHAT IS GOING ON ?                ##
## SCROLL DOWN TO --> DERIVED CLASS | GENERATE STOREFRONT ##
##                                                        ##
## (class GenerateSF)                                     ##
############################################################


########################################################
## STOREFRONT ELEVATION - NOT PART OF ANY INHERITANCE ##
########################################################
"""
I AM STILL UNCLEAR ABOUT WHAT THIS CLASS IS BEING USED FOR

_VARIABLE = declaring private variables, functions, methods, or classes in a module
            it will not be imported by "import module"
__VARIABLE = variables that will get abbreviated with class name as a way of projecting
             variables whose names might get repeated as code is expanded with additional classes
             
ISSUES:
    - if configuration fails it will stall script
"""
class StorefrontElevation:
    def __init__(self, _hostElementIds, _line,
                       _superType, _id, _sillHeight, 
                       _headHeight, _systemName):
        self.AssemblyID = _id
        self.CWElementId = None
        self.EndCondition = None
        self.EndNeighbors = []
        self.EndOffset = 0
        self.EndAngledOffset = 0
        self.HostElementIds = _hostElementIds # WHAT ARE THESE STUPID UNDERSCORES FOR
        self.Line = _line
        self.HostLine = _line
        self.StartCondition = None
        self.StartNeighbors = []
        self.StartOffset = 0
        self.StartAngledOffset = 0
        self.SuperType = _superType
        self.SystemName = _systemName
        self.SillHeight = _sillHeight
        self.HeadHeight = _headHeight
        self.Type = None
        self.Doors = None
        self.ErrorList = []
    def __repr__(self):
        return("<class 'StorefrontElevation'>")

###############################################
## BASE CLASS A: COLLECT ELEMENTS FED TO GUI ##
###############################################
class Collect_PreGUI:
    """
    Must have a way of avoiding the plan view requirement
    here, perhaps get hosted level of selected wall
    """    
    def __init__(self):
        # class output variables
        self.levelObjs = []
        self.levelNames = []
        self.levelInts = []
        
        self.gypWallObjs = []
        self.gypWallNames = []
        self.gypWallUniqueNames = []
        
        # these two depend on one another bc objs cannot be serialized
        self.gypWallDict = {}
        self.gypWallDict_KEYS = {}
        
        self.loadedFamilies = []
        
        # level names to be filtered out
        # mezzanine must be included
        self.levelExclusionList = ["Container", "Roof",
                                   "CONTAINER LEVEL", "X LEVEL"]
    def __repr__(self):
        return("<class 'Collect_PreGUI'>")
    # COLLECT ELMENTS FOR GUI
    def CollectLevels(self):
        # collect levels and level properties
        # enhance the list exclusion so its not so literal
        self.levelObjs = [i for i in FilteredElementCollector(self.doc).OfClass(Level) if i.Name not in self.levelExclusionList]
        self.levelNames = [i.Name for i in self.levelObjs]
        try:
            self.levelInts = [list(map(float, re.findall(r'\d+', i)))[0] for i in self.levelNames] # <-HOW?
            
            # sort output variables
            self.levelObjs = SFU.Sort_Alist_By_Blist(self.levelObjs, self.levelInts)[0]
            self.levelNames, self.levelInts = SFU.Sort_Alist_By_Blist(self.levelNames, self.levelInts)            
        except:
            # this method does not capture instances of mezzaninne being used as a floor...address this 
            pass
    def CollectGypWalls(self):
        self.gypWallObjs = [i for i in FilteredElementCollector(self.doc).OfClass(Wall) 
                            if i.Name not in self.familyObj.SFWallTypeNames.keys()
                            and "storefront" not in i.Name.lower()] # storefront also removes curtain wall families
        
        self.gypWallTypeIds = [i.GetTypeId() for i in self.gypWallObjs]
        self.gypWallNames = [i.Name for i in self.gypWallObjs]
        self.gypWallUniqueNames = set(self.gypWallNames)
        
        # create a dict for gypWallNames: gypWallObjs -> goes to SF2_GUI as options -> selection then used in Create_NibWalls
        # set not necessary bc this loop effectively acts as set by not repeating keys
        for i,key in enumerate(self.gypWallNames):
            self.gypWallDict[key] = self.gypWallTypeIds[i]
        for i in self.gypWallDict.keys():
            self.gypWallDict_KEYS[i] = i
    # CLASS ENTRY POINT
    def Run_PreGUIMethods(self):
        # collect levels in doc
        self.CollectLevels()
        
        # collect gyp walls in doc
        self.CollectGypWalls()
        
        # create dictionary of families in the doc
        self.CollectGypWalls()

###################################################
## BASE CLASS B: COLLECT DOC ELEMENTS - ORIGINAL ##
###################################################
class CollectSFElements:
    def __init__(self):
        # pyRevit progress bar in console window
        self.progressIndex = 0.0
        
        # derived parameters - CollectNeededElements()
        self.storefrontFullIds = []
        self.storefrontPartialIds = []
        self.selectedLevels = []
        self.storefrontFullLines = []
        self.storefrontPartialLines = []
        self.interiorWallsLines = []
        self.interiorWallsLinesEdges = []
        self.startingAssembyId = None
        self.interiorWallIds = None
        self.columnsLinesEdges = None
        self.columnsLinesEdgesEC = None
        self.selectedLevelId = None

        self.docLoaded = SFU.RevitLoadECDocument(self.doc)
        self.docEC = self.docLoaded[0]
        self.ecTransform = self.docLoaded[1]            

        self.allWallsEC = []
        self.allLevelsEC = []
        self.allColumnsEC = []
        self.wallsLinesEdgesEC = []
        self.selectedLevelsEC = []
        self.selectedWallsEC = []
        self.selectedColumnsEC = [] 

        # derived parameters - Prep()
        self.wallTypeCW = None
        self.wallDoorHostDict = None
        self.storefrontConfig = None # this is gui object and eventual user selections
        self.systemName = None
        self.mullionDict = None
        self.doorDict = None
        self.panelTypeDict = None
        self.storefrontSpacingType = None
        self.storefrontPaneWidth = None
        self.systemPostWidth = None

        # derived parameters - WrapAndChain()
        self.storefrontElevations = []
    
    def __repr__(self):
        return("<class 'CollectSFElements'>")
    
    # UTILITIES
    def FilterSFWalls(self, sfWallObjs):
        # this will filter user selection or collected SF walls
        # into either a full or partial SF list to be used throughout
        for i,data in enumerate(sfWallObjs):
            # Autodesk.Revit.DB.ElementId
            if type(data) is ElementId:
                obj = self.doc.GetElement(data)
            else: obj = data
            if obj.Name in self.familyObj.SFWallTypeNames.keys() and self.familyObj.SFWallTypeNames[obj.Name] == 0:
                self.storefrontFullIds.append(obj.Id)
            elif obj.Name in self.familyObj.SFWallTypeNames.keys() and self.familyObj.SFWallTypeNames[obj.Name] == 1:
                self.storefrontPartialIds.append(obj.Id)
    
    # MAIN STUFF
    def CollectNeededElements(self):
        ## save this
        #if userSelectedIds: 
            #self.interiorWallIds = [self.doc.GetElement(id) for id in userSelectedIds 
                                    #if self.doc.GetElement(id).Name in SFF.FamilyTools(self.doc).SFWallTypeNames.keys()]        
        
        
        
        
        if self.selectionType == "userSelection":
            # this will get used in the selection class
            currentSelectedObjs = [self.doc.GetElement(i) for i in self.userSelectedIds]
            self.storefrontWallIds = self.userSelectedIds
            
            userSelectedIdsLevelIds = []
        
        elif self.selectionType == "planViewSelection":
            # get storefront walls from view in document
            self.storefrontWallIds = [i.Id for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall)
                                      if i.Name in SFF.FamilyTools(self.doc).SFWallTypeNames]
            
        elif self.selectionType == "levelSelection":
            pass        
        
        # once the appropriate walls are placed in the correct locations the script can run as before. last hurdle is the point where full and partial sfs are parsed.
        
        
        
        
        # collect plan view level and levelId
        self.selectedLevelId = self.currentView.GenLevel.Id
        self.selectedLevelObj = self.doc.GetElement(self.selectedLevelId)

        allColumns = SFU.GetAllElements(self.doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance, currentView=True)
        allColumns += SFU.GetAllElements(self.doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance, currentView=True)
        
        # collect all SF walls in view
        self.interiorWallIds = [i.Id for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall) if i.Name in self.familyObj.SFWallTypeNames.keys()]
        
        userSelectedIds = list(self.uidoc.Selection.GetElementIds())
        if userSelectedIds:
            self.FilterSFWalls(userSelectedIds)                   
        else:
            self.FilterSFWalls(FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall))

        # this might be used to track each assembly - possibly for fabrication?
        # collect existing storefront curtain walls and check their Marks to ensure they incrememt. 
        # so that mark numbers can be consecutive?
        self.startingAssembyId = 0
        storefrontWallsInView = rpw.db.Collector(of_class='Wall', view=self.currentView, where=lambda x: str(x.WallType.Kind) == "Curtain")


        tempList = []
        for storefrontInView in storefrontWallsInView:
            mark = storefrontInView.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
            if mark:
                tempList.append(int(mark[mark.index("-")+1:]))
        if tempList:
            sortedList = sorted(tempList)
            self.startingAssembyId = sortedList[-1]

        # makes sure no stacked walls are included.    
        tempList = []
        for wallId in self.interiorWallIds:
            wall = self.doc.GetElement(wallId)
            if not wall.IsStackedWallMember:
                tempList.append(wallId)
        self.interiorWallIds = tempList

        # Sort lists by level
        self.storefrontFullIds = SFU.FilterElementsByLevel(self.doc, self.storefrontFullIds, self.selectedLevelId)
        self.storefrontPartialIds = SFU.FilterElementsByLevel(self.doc, self.storefrontPartialIds, self.selectedLevelId)
        self.interiorWallIds = SFU.FilterElementsByLevel(self.doc, self.interiorWallIds, self.selectedLevelId)
        selectedColumns = SFU.FilterElementsByLevel(self.doc, allColumns, self.selectedLevelId)

        # collect perimeter/collision geometry from EC model
        if self.docEC:
            levelElevationEC = None 
            for p in self.selectedLevelObj.Parameters:
                if p.Definition.Name == "Elevation":
                    levelElevationEC = p.AsDouble()
            self.selectedWallsEC = SFU.FilterElementsByLevel(self.docEC, self.allWallsEC, levelElevationEC)
            self.selectedColumnsEC = SFU.FilterElementsByLevel(self.docEC, self.allColumnsEC, levelElevationEC)
            self.wallsLinesEdgesEC = SFU.GetWallEdgeCurves(self.docEC, self.selectedWallsEC, self.ecTransform)
            self.columnsLinesEdgesEC = SFU.GetColumnEdgeCurves(self.docEC, self.selectedColumnsEC, self.ecTransform)

        # collect perimeter/collision geometry from Design model
        self.interiorWallsLinesEdges = SFU.GetWallEdgeCurves(self.doc, self.interiorWallIds, None)
        self.columnsLinesEdges = SFU.GetColumnEdgeCurves(self.doc, selectedColumns)

        levelElevation = self.selectedLevelObj.Elevation
    
    def Prep(self):
        self.systemName = self.currentConfig["currentSystem"]

        self.storefrontPaneWidth = self.currentConfig["storefrontPaneWidth"]
        self.storefrontSpacingType = self.currentConfig["spacingType"]

        self.mullionDict = SFU.GetMullionTypeDict(self.doc)
        self.panelTypeDict = SFU.GetWindowTypeDict()
        self.doorDict = self.currentConfig["systemDoors"]
        wallTypeDict = SFU.GetWallTypeDict()
        self.wallDoorHostDict = SFU.GetDoorDictByWallHost()

        # Ensure walltypes are loaded
        if not "I-Storefront-"+ self.systemName in wallTypeDict.keys():
            Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Make sure you selected/loaded the correct partition system. Check your wall types.")
            sys.exit()

        # Profile widths
        self.systemPostWidth = self.doc.GetElement(self.mullionDict["{0}_Post".format(self.systemName)]).get_Parameter(BuiltInParameter.CUST_MULLION_THICK).AsDouble()

        systemDoorFrame = self.doc.GetElement(self.mullionDict["{0}_DoorFrame".format(self.systemName)])
        systemDoorFrameWidth = systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
        systemDoorFrameWidth += systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

        systemOneBy = self.doc.GetElement(self.mullionDict["{0}_OneBy".format(self.systemName)])
        systemOneByWidth = systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
        systemOneByWidth += systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

        self.wallTypeCW = wallTypeDict["I-Storefront-"+self.systemName]

    def WrapAndChain(self):
        """
        Takes walls that are inline and makes them a single
        wall element so that you dont get segmented walls that
        are supposed to be a single continuous elevation.
        """
        assemblyId = self.startingAssembyId
        self.storefrontElevations = []
        storefrontFullAndPartial = []

        for wallId in self.storefrontFullIds:
            storefrontFullAndPartial.append([wallId,"Full"])
        for wallId in self.storefrontPartialIds:
            storefrontFullAndPartial.append([wallId,"Partial"])

        # Make SF Objects
        for item1 in storefrontFullAndPartial:
            wallId1 = item1[0]
            wallStorefrontType1 = item1[1]

            wall1 = self.doc.GetElement(wallId1)
            wall1LocationCurve = wall1.Location.Curve

            wallDoors = []
            wallHostIds = [wallId1]

            if wallId1 in self.wallDoorHostDict.keys():
                wallDoors = self.wallDoorHostDict[wallId1]

            ## PROFILE THIS SECTION ##########################################################################

            # Chain Searching
            # Find neighbors and chain them if they are in-line.
            searchingForChain = True
            while searchingForChain:
                foundNeighbor = False
                wall1Start = wall1LocationCurve.GetEndPoint(0)
                wall1End = wall1LocationCurve.GetEndPoint(1)
                wall1Endpoints = [wall1Start, wall1End]

                for item2 in storefrontFullAndPartial:
                    wallId2 = item2[0]
                    wallStorefrontType2 = item2[1]

                    if wallId1 != wallId2 and wallStorefrontType1 == wallStorefrontType2:
                        wall2 = self.doc.GetElement(wallId2)
                        wall2LocationCurve = wall2.Location.Curve
                        wall2Start = wall2LocationCurve.GetEndPoint(0)
                        wall2End = wall2LocationCurve.GetEndPoint(1)
                        wall2Endpoints = [wall2Start, wall2End]
                        for i in range(len(wall1Endpoints)):
                            point1a = wall1Endpoints[i]
                            point1b = wall1Endpoints[i-1]
                            for j in range(len(wall2Endpoints)):
                                point2a = wall2Endpoints[j]
                                point2b = wall2Endpoints[j-1]
                                dist = point1a.DistanceTo(point2a)
                                if dist < self.tol:
                                    angle = SFU.AngleThreePoints(point1b, point1a, point2b)
                                    if abs(angle-180) < self.tol:
                                        wallHostIds += [wallId2]
                                        storefrontFullAndPartial.remove(item2)
                                        if wallId2 in self.wallDoorHostDict.keys():
                                            wallDoors += self.wallDoorHostDict[wallId2]
                                        wall1LocationCurve = Line.CreateBound(point1b, point2b)
                                        foundNeighbor = True
                                        break
                    if foundNeighbor:
                        break
                if not foundNeighbor:
                    searchingForChain = False

            ## PROFILE THIS SECTION ##########################################################################

            # Create SF Object
            assemblyId += 1

            if wallStorefrontType1 == "Full":
                sillH = self.currentConfig["fullSillHeight"]
            elif wallStorefrontType1 == "Partial":
                if self.currentConfig["hasLowerInfill"]:
                    sillH = self.currentConfig["fullSillHeight"]
                else:
                    sillH = self.currentConfig["partialSillHeight"]

            headH = self.currentConfig["headHeight"]
            sfe = StorefrontElevation(wallHostIds, wall1LocationCurve, wallStorefrontType1, assemblyId, sillH, headH, self.systemName)
            
            # Doors
            if wallDoors:
                sfe.Doors = wallDoors
            self.storefrontElevations.append(sfe)
    
    # MAIN CLASS ENTRY POINT
    def Run_StorefrontPrep(self):
        self.CollectNeededElements()
        self.Prep()
        self.WrapAndChain()
        
################################################################
## BASE CLASS B: COLLECT DOC ELEMENTS - FUTURE IMPLEMENTATION ##
################################################################
class Collect_Elements:
    def __init__(self, selectionType):
        """
        Must have a way of avoiding the plan view requirement
        here, perhaps get hosted level of selected wall
        """
        
        # input parameters
        self.selectionType = selectionType
        
        # wall outputs
        self.allWallIds = None
        
        self.userSelectedIds = None # this was used to test selection type but needed later on...
        
        # pyRevit progress bar in console window
        self.progressIndex = 0.0
    
        # derived parameters - CollectNeededElements()
        self.storefrontFullIds = []
        self.storefrontPartialIds = []
        self.selectedLevels = []
        self.storefrontFullLines = []
        self.storefrontPartialLines = []
        self.interiorWallsLines = []
        self.interiorWallsLinesEdges = []
        self.startingAssembyId = None
        self.interiorWallIds = None
        self.columnsLinesEdges = None
        self.columnsLinesEdgesEC = None
        self.selectedLevelId = None
    
        self.docLoaded = SFU.RevitLoadECDocument(self.doc)
        self.docEC = self.docLoaded[0]
        self.ecTransform = self.docLoaded[1]            
    
        self.allWallsEC = []
        self.allLevelsEC = []
        self.allColumnsEC = []
        self.wallsLinesEdgesEC = []
        self.selectedLevelsEC = []
        self.selectedWallsEC = []
        self.selectedColumnsEC = []         
        
    # COLLECT ELEMENTS
    def CollectAllWalls(self):
        # this method is used for finding intersections among walls for nib wall creation
        
        # collect all wall ids
        self.allWallIds = SFU.GetElementsInView(BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, self.currentView.Id)
        
        # filter self.allWallIds to contain only those in current plan view
        self.allWallIds = [i for i in SFU.FilterElementsByLevel(self.doc, self.allWallIds, self.currentLevel.Id)]        
    def CollectSFWalls(self):
        if self.selectionType == "userSelection":
            # this will get used in the selection class
            currentSelectedObjs = [self.doc.GetElement(i) for i in self.userSelectedIds]
            self.storefrontWallIds = self.userSelectedIds
            
            userSelectedIdsLevelIds = []
        
        elif self.selectionType == "planViewSelection":
            # get storefront walls from view in document
            self.storefrontWallIds = [i.Id for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall)
                                      if i.Name in SFF.FamilyTools(self.doc).SFWallTypeNames]
            
        elif self.selectionType == "levelSelection":
            pass        
        
        
        
        
        
        
        
        self.interiorWallIds = [self.doc.GetElement(id) for id in self.userSelectedIds 
                                if self.doc.GetElement(id).Name in SFF.FamilyTools(self.doc).SFWallTypeNames.keys()]        
        
        
        # A) walls collected by user selection -> returns wall id
        userSelectedIds = [i for i in self.uidoc.Selection.GetElementIds()] # GetElementIds is a .net enumerator
        if userSelectedIds:
            currentSelectedObjs = [self.doc.GetElement(i) for i in userSelectedIds]
            userSelectedIdsLevelIds = []
        
        
        if not userSelectedIds:
            # get storefront walls from view in document
            self.storefrontWallIds = [i.Id for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall)
                                      if i.Name in SFF.FamilyTools(self.doc).SFWallTypeNames]
        else:
            self.storefrontWallIds = userSelectedIds
        
        
        if userSelectedIds: 
            self.interiorWallIds = [self.doc.GetElement(id) for id in userSelectedIds 
                                    if self.doc.GetElement(id).Name in SFF.FamilyTools(self.doc).SFWallTypeNames.keys()]
            

        # walls collected by code -> returns wall object -> Autodesk.Revit.DB.Wall - defines <type 'Wall'>
        if not userSelectedIds and self.currentViewOnly == True:
            # level of current view
            self.selectedLevelId = self.currentView.GenLevel.Id
            self.selectedLevelObj = self.doc.GetElement(self.selectedLevelId)            
            
            self.interiorWallIds = [i for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall)
                                    if i.Name in SFF.FamilyTools(self.doc).SFWallTypeNames.keys()]
        elif not userSelectedIds and self.currentViewOnly == False:
            self.interiorWallIds = [i for i in FilteredElementCollector(self.doc).OfClass(Wall)
                                    if i.Name in SFF.FamilyTools(self.doc).SFWallTypeNames.keys()]

        # check to make sure there are SF walls in the model
        if self.interiorWallIds: return()
        else: raise Esception("There are no walls in the model")
    def CollectColumns(self):
        self.allColumns = SFU.GetAllElements(self.doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance, currentView=True) # used eventually in build curtain wall
        self.allColumns += SFU.GetAllElements(self.doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance, currentView=True) # used eventually in build curtain wall

    def CollectWallLevels(self):
        # obtain level ids then use ids to collect elements
        levelIdList = [i.LevelId for i in self.interiorWallIds]
        self.levelList = [self.doc.GetElement(id) for id in levelIdList]        
    def CollectWallColumnEdges(self):
        # collect perimeter/collision geometry from EC model
        if self.docEC:
            levelElevationEC = None 
            for p in self.selectedLevelObj.Parameters:
                if p.Definition.Name == "Elevation":
                    levelElevationEC = p.AsDouble()
            
            self.selectedWallsEC = SFU.FilterElementsByLevel(self.docEC, self.allWallsEC, levelElevationEC)
            self.selectedColumnsEC = SFU.FilterElementsByLevel(self.docEC, self.allColumnsEC, levelElevationEC)
            
            self.wallsLinesEdgesEC = SFU.GetWallEdgeCurves(self.docEC, self.selectedWallsEC, self.ecTransform)
            self.columnsLinesEdgesEC = SFU.GetColumnEdgeCurves(self.docEC, self.selectedColumnsEC, self.ecTransform)

        # collect perimeter/collision geometry from Design model
        self.interiorWallsLinesEdges = SFU.GetWallEdgeCurves(self.doc, self.interiorWallIds, None)
        self.columnsLinesEdges = SFU.GetColumnEdgeCurves(self.doc, selectedColumns)        
    def CollectLoadedFamilies(self):
        # IS THIS DOUBLE LOADING?
        # Load familes - its not a load, load but I will clarify this later
        self.loadedFamilies = self.familyObj.SFLoadFamilies(True)
        #print(type(self.loadedFamilies))
        #print(self.loadedFamilies)        
    # SORT/FILTER ELEMENTS
    def SortWallsByLevel(self):
        self.interiorWallIds = [i for _,i in sorted(zip(self.interiorWallIds, self.levelNumList))]
    def GroupWallsByLevel(self):
        setList = sorted(set(self.levelNumList))

        #self.self.nestedWallList = []
        for i in setList:
            tempList = []
            for j, wall in enumerate(self.interiorWallIds):
                if self.levelNumList[j] == i:
                    tempList.append(wall)
            self.nestedWallList.append(tempList)    
    # CLASS ENTRY POINT
    def Run_CollectWalls(self):
        # collect all walls and columns
        self.CollectSFWalls()
        self.CollectColumns()

        # get levels of each wall
        self.CollectWallLevels()
        self.CollectLevelNumbers()

        # group walls by level
        sortedNestedWallList = self.GroupWallsByLevel()

##########################################
## BASE CLASS C: SPLIT STOREFRONT WALLS ##
##########################################
class Create_NibWalls:
    """
    SINCE THIS CLASS IS MOSTLY SELF CONTAINED, THE VARIABLES
    WITH THE SAME NAME HERE WILL NOT BE MADE .SELF CLASS
    INHERITANCE VARIABLES SO THE REST OF THE SCRIPT DOESN'T GET MESSED UP.
    THERE IS THE CHANCE TO CLEAN UP THE LOOP BY RECYCLING VARIABLES, BUT
    THE RHINO ENGINE WILL SOLVE THIS NEXT, NOT EXTENSIVELY FIXING THIS
    
    KNOWN ISSUES:
        THIS IS CREATING NIB WALLS ON FREESTANDING WALLS
    """
    def __init__(self):
        # glass sizes
        self.standardSizes = [4.0, 3.0, 2.0, 1.0]
        self.fixedNibWall_imperial = 6/12
        self.fixedNibWall_metric = 5.90551/12
        self.leftoverTol = 0.35  # Nib wall length
        
        # something
        self.selectedSystem = None
        self.selectedPostWidth = None
        self.selectedOneByWidth = None
        self.selectedNibWallLength = None
        self.gypNibWallTypeId = None
        
        self.currentLevel = self.currentView.GenLevel
        
        # something else
        self.instName = None
        self.topConstraint = None
        self.unconnectedHeight = None
        self.topOffset = None
        self.botConstraint = None       
        
        self.storefrontWallIds = None
        self.intersectionPoints = None
    def __repr__(self):
        return("<class 'Create_NibWalls'>")   
    def BigMethod(self, SFobj):
        for p in SFobj.Parameters:
            if p.Definition.Name == "Top Constraint":
                self.topConstraint = p.AsElementId() # element Id of top constraint object
            if p.Definition.Name == "Unconnected Height":
                self.unconnectedHeight = p.AsDouble()
            if p.Definition.Name == "Top Offset":
                self.topOffset = p.AsDouble()

        # check to see which ends are naked
        SFobjCrv = SFobj.Location.Curve
        SFobjCrv_StartPt = SFobjCrv.GetEndPoint(0)
        SFobjCrv_EndPt = SFobjCrv.GetEndPoint(1)
        startOverlap = False
        endOverlap = False
        
        if self.intersectionPoints:
            # compare intersection points with end points of wall,
            # when they match then an intersection at the wall end is confirmed
            for point in self.intersectionPoints:
                if point.DistanceTo(SFobjCrv_StartPt) < self.tol:
                    startOverlap = True
                elif point.DistanceTo(SFobjCrv_EndPt) < self.tol:
                    endOverlap = True
                if startOverlap and endOverlap:
                    break

        # if only one SFobjCrv_EndPt is touching other walls
        if startOverlap == False or endOverlap == False:
            nibWall = None
            nibWalls = []
            offset = 0
            lengthAdjust = (0.5 * self.selectedPostWidth) + self.selectedOneByWidth
            length = SFobjCrv.Length - lengthAdjust
            leftover = length%(self.standardSizes[0] + self.selectedOneByWidth)

            # calculate offset
            # optimized nib wall split
            if self.selectedNibWallLength == "OPTIMIZED":
                
                numPanels_optimized = math.floor(length / (self.standardSizes[0] + self.selectedOneByWidth))                
                
                # if optimized split
                if leftover > self.leftoverTol:
                    lastPanelSize = 0
                    for size in self.standardSizes[1:]:
                        if leftover - self.leftoverTol >= (size + self.selectedOneByWidth):
                            lastPanelSize = self.standardSizes[self.standardSizes.index(size)]
                            break
                    offset = lengthAdjust + numPanels_optimized*self.standardSizes[0] + (numPanels_optimized)*self.selectedOneByWidth + lastPanelSize + int(lastPanelSize > 0)*self.selectedOneByWidth
                else:
                    offset = lengthAdjust + (numPanels_optimized-1)*self.standardSizes[0] + self.standardSizes[1] + (numPanels_optimized)*self.selectedOneByWidth
            
            # fixed nib wall split
            else: offset = SFobjCrv.Length - self.selectedNibWallLength  
        
            if startOverlap or (startOverlap == endOverlap):
                try:
                    # create new SF and Nib walls
                    newPoint = XYZ(((SFobjCrv_EndPt.X-SFobjCrv_StartPt.X)*(offset/(length + lengthAdjust)))+SFobjCrv_StartPt.X,((SFobjCrv_EndPt.Y-SFobjCrv_StartPt.Y)*(offset/(length + lengthAdjust)))+SFobjCrv_StartPt.Y, SFobjCrv_StartPt.Z)
                    SFobj.Location.Curve = Line.CreateBound(SFobjCrv_StartPt, newPoint)
                    nibWallLine = Line.CreateBound(newPoint,SFobjCrv_EndPt)
    
                    SFobjCrv_EndPt = newPoint
    
                    nibWalls.append(Wall.Create(self.doc, nibWallLine, self.currentLevel.Id, False))
                    self.doc.Regenerate()                                        
                except:
                    print("Wall {0} was too short to add a nib wall".format(id))
    
            if endOverlap or (startOverlap == endOverlap):
                try:
                    # create new SF and Nib walls
                    newPoint = XYZ(((SFobjCrv_StartPt.X-SFobjCrv_EndPt.X)*(offset/(length + lengthAdjust)))+SFobjCrv_EndPt.X,((SFobjCrv_StartPt.Y-SFobjCrv_EndPt.Y)*(offset/(length + lengthAdjust)))+SFobjCrv_EndPt.Y, SFobjCrv_EndPt.Z)
                    SFobj.Location.Curve = Line.CreateBound(newPoint, SFobjCrv_EndPt)                  
    
                    nibWallLine = Line.CreateBound(newPoint,SFobjCrv_StartPt)
    
                    SFobjCrv_StartPt = newPoint
    
                    nibWalls.append(Wall.Create(self.doc, nibWallLine, self.currentLevel.Id, False))
                    self.doc.Regenerate()
                except:
                    print("Wall {0} was too short to add a nib wall".format(id))                                    
    
            if nibWalls:
                # this will have to be adjusted bc not view dependent
                self.botConstraint = self.currentLevel.Id
                
                for nibWall in nibWalls:
                    # it seems like you create walls of whatever type then change type
                    # but you inherit parameter settings of host wall???
                    nibWall.WallType = self.doc.GetElement(self.gypNibWallTypeId)
                    nibTopConstraint = nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId()
    
                    if self.topConstraint.IntegerValue == self.botConstraint.IntegerValue:
                        nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId(-1))
                    else:
                        nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(self.topConstraint)
    
                    for p in nibWall.Parameters:
                        if p.Definition.Name == "Location Line":
                            p.Set(0)
                        if p.Definition.Name == "Unconnected Height" and self.topConstraint.IntegerValue == -1:
                            p.Set(self.unconnectedHeight)
    
                    self.doc.Regenerate()
                    if self.topConstraint.IntegerValue == self.botConstraint.IntegerValue:
                        nibWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(self.topOffset)
    
    def Run_CreateNibWalls(self):
        # find intersections between all walls in model/model level
        self.intersectionPoints = SFU.RemoveDuplicatePoints(SFU.FindWallIntersections(self.allWallIds))        
        
        # this class takes the recently saved currentConfigs to get data about how to create nib walls
        self.selectedSystem = self.currentConfig["currentSystem"]
        self.selectedPostWidth = self.currentConfig["postWidth"]
        self.selectedOneByWidth = self.currentConfig["oneByWidth"]
        self.selectedNibWallLength = self.currentConfig["nibWallLength"]
        # you can't serialize objs so dct of keys calls a dict that is always written in this module with objs as values for the same key indexes
        self.gypNibWallTypeId = self.gypWallDict[self.currentConfig["nibWallType"]]         
        
        if not self.storefrontWallIds:
            Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "No Storefront walls selected or found in the view")
            pyrevit.script.exit()

        t = Transaction(self.doc, "Create Nib")
        t.Start()
        for id in self.storefrontWallIds:
            # use id to get element data from revit doc
            SFobj = self.doc.GetElement(id)

            if SFobj.Category.Name == "Walls":
                # 2 different ways of obtaining parameters (instance name) bc changes in the api
                try:
                    self.instName = SFobj.Name.lower()
                except:
                    for p in SFobj.Parameters:
                        if p.Definition.Name == "Name":
                            self.instName = p.AsString().lower()

                if "storefront" not in self.instName:
                    continue
                # split storefront wall at index to create nib wall - nib matches parameters of split wall
                else:
                    self.BigMethod(SFobj)
            else: continue            
        t.Commit()      

################################
## BASE CLASS D: RHINO ENGINE ##
################################
class ParseSFWalls_Rhino:
    """
    THE BASIC IDEA IS GET CENTERLINES, DO ALL THIS LOGIC,
    THEN USE THE CENTERLINES TO MODIFY EXISTING WALL FAMILIES
    """
    def __init__(self):
        pass
    def __repr__(self):
        return("<class 'ParseSFWalls_Rhino'>")

##########################################
## BASE CLASS E1: CHECK MODEL FOR STUFF ##
##########################################
class CheckSFWalls:
    def __init__(self):
        # derived parameters
        
        #############################
        ## FIX TOLERANCE ISSUE     ##
        ## fails bc lines to small ##
        ## but tolerance was large ##
        #############################
        
        self.distTol = 0.05
        self.angleTol = 0.01
    def __repr__(self):
        return("<class 'CheckSFWalls'>")
    def InteriorWallEdges(self):
        # check interior wall edges
        self.locLine = self.storefrontObject.HostLine
        self.locLineStart = self.locLine.GetEndPoint(0)
        self.locLineEnd = self.locLine.GetEndPoint(1)

        for intWallLine in self.interiorWallsLinesEdges:
            intersection = SFU.RevitCurveCurveIntersection(self.locLine,intWallLine)

            if intersection:
                distToEnd = intersection.DistanceTo(self.locLineEnd) 
                distToStart = intersection.DistanceTo(self.locLineStart) 

                #If intersection is at the ends
                if distToEnd < self.distTol:
                    self.storefrontObject.EndCondition = "OnGyp"
                    # If intersection is not at the surface of the edges of interior walls
                    if distToEnd > self.tol:
                        self.storefrontObject.Line = Line.CreateBound(self.locLineStart, intersection)

                elif distToStart < self.distTol:
                    self.storefrontObject.StartCondition = "OnGyp"
                    if distToStart > self.tol:
                        self.storefrontObject.Line = Line.CreateBound(intersection, self.locLineEnd)
    def InteriorWallMidspans(self):
        # check interior wall midspans
        for intWallId in self.interiorWallIds:
            intWall = self.doc.GetElement(intWallId)
            intWallLine = intWall.Location.Curve
            intersection = SFU.RevitCurveCurveIntersection(self.locLine,intWallLine)
            if intersection:
                distToEnd = intersection.DistanceTo(self.locLineEnd) 
                distToStart = intersection.DistanceTo(self.locLineStart) 
                #If intersection is at the ends
                if distToEnd > self.distTol and distToStart > self.distTol:
                    self.gridIntersectionPostPoints.append(intersection)
    def ECWalls(self):
        # check EC walls
        self.locLine = self.storefrontObject.HostLine
        self.locLineStart = self.locLine.GetEndPoint(0)
        self.locLineEnd = self.locLine.GetEndPoint(1)
        obstructionEdges = self.columnsLinesEdges
        if self.docEC:
            obstructionEdges += self.columnsLinesEdgesEC
            obstructionEdges += self.wallsLinesEdgesEC
        if obstructionEdges:
            for obstructionLine in obstructionEdges:
                obstLineElevation = obstructionLine.GetEndPoint(0).Z
                self.locLineStart = XYZ(self.locLineStart.X, self.locLineStart.Y, obstLineElevation)
                self.locLineEnd = XYZ(self.locLineEnd.X, self.locLineEnd.Y, obstLineElevation)
                locLineFlat = Line.CreateBound(self.locLineStart, self.locLineEnd)
                intersection = SFU.RevitCurveCurveIntersection(locLineFlat,obstructionLine)
                if intersection:
                    #ERROR: Hit Existing Condition
                    if intersection.DistanceTo(self.locLineEnd) < self.distTol:
                        self.storefrontObject.EndCondition = "OnObstruction"
                    elif intersection.DistanceTo(self.locLineStart) < self.distTol:
                        self.storefrontObject.StartCondition = "OnObstruction"
    def StorefrontIntersections(self):
        # check storefront intersections
        self.locLine = self.storefrontObject.HostLine
        self.locLineStart = self.locLine.GetEndPoint(0)
        self.locLineEnd = self.locLine.GetEndPoint(1)
    def FindNeighbors(self):
        # find neighbors
        for neighbor in self.storefrontElevations:
            if neighbor != self.storefrontObject:
                neighborLocLine = neighbor.HostLine
                neighborLocLineStart = neighborLocLine.GetEndPoint(0)
                neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
                intersection = SFU.RevitCurveCurveIntersection(self.locLine,neighborLocLine)

                if intersection:
                    point1 = None
                    intersectionTypeOnNeighbor = None

                    #Check where the intersection is occuring on the neighbor
                    if intersection.DistanceTo(neighborLocLineStart) < self.distTol:
                        intersectionTypeOnNeighbor = "Start"
                        point1 = neighborLocLineEnd
                    elif intersection.DistanceTo(neighborLocLineEnd) < self.distTol:
                        intersectionTypeOnNeighbor = "End"
                        point1 = neighborLocLineStart
                    else:
                        intersectionTypeOnNeighbor = "Middle"
                        point1 = neighborLocLineEnd

                    # check if intersection is at the SFobjCrv_StartPt point or SFobjCrv_EndPt point or middle
                    if intersection.DistanceTo(self.locLineStart) < self.tol:
                        angle = SFU.AngleThreePoints(self.locLineEnd, intersection, point1)
                        self.storefrontObject.StartNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                    elif intersection.DistanceTo(self.locLineEnd) < self.tol:
                        angle = SFU.AngleThreePoints(self.locLineStart, intersection, point1)
                        self.storefrontObject.EndNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                    else:
                        # interesection isnt ocurring at the ends.
                        self.gridIntersectionPostPoints.append(intersection)

                        # if the intersections for both lines are on the middles for eachother.
                        if intersectionTypeOnNeighbor == "Middle":

                            #Split the intersecting neighbor into two segments so the walls dont overlap
                            neighborLocLineStart = neighborLocLine.GetEndPoint(0)
                            neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
                            neighbor.Line = Line.CreateBound(intersection, neighborLocLineStart)
                            neighbor.HostLine = Line.CreateBound(intersection, neighborLocLineStart)

                            #Create another neighbor thats split
                            newNeighborIndex = len(self.storefrontElevations)+1
                            newNeighborHostElementIds = neighbor.HostElementIds
                            newNeighborSillHeight = neighbor.SillHeight
                            newNeighborHeadHeight = neighbor.HeadHeight
                            splitNeighborLine = Line.CreateBound(intersection, neighborLocLineEnd)
                            splitNeighbor = StorefrontElevation(newNeighborHostElementIds, splitNeighborLine, neighbor.SuperType, newNeighborIndex, newNeighborSillHeight, newNeighborHeadHeight, self.systemName)
                            self.storefrontElevations.append(splitNeighbor)

                            # make sure that each new segment has the correct doors on each one
                            if neighbor.Doors:
                                doorsOnNeighbor = neighbor.Doors
                                tempList1 = []
                                tempList2 = []
                                for neighborDoorId in doorsOnNeighbor:
                                    neighborDoor = self.doc.GetElement(neighborDoorId)
                                    doorPoint = neighborDoor.Location.Point
                                    if RevitPointOnLine2D(doorPoint, neighbor.Line):
                                        tempList1.append(neighborDoorId)
                                    else:
                                        tempList2.append(neighborDoorId)
                                neighbor.Doors = tempList1
                                splitNeighbor.Doors = tempList2
    def DetermineConditions(self):
        # determine SFobjCrv_StartPt conditions
        self.locLine = self.storefrontObject.HostLine
        self.locLineStart = self.locLine.GetEndPoint(0)
        self.locLineEnd = self.locLine.GetEndPoint(1)

        startAndEndNeighbors = [self.storefrontObject.StartNeighbors, self.storefrontObject.EndNeighbors]

        for i in range(len(startAndEndNeighbors)):
            neighborSet = startAndEndNeighbors[i]
            cornerCount = 0
            inlineCount = 0
            cornerTypes = []
            inlineTypes = []
            conditionAngleOffset = None
            conditionToSet = None
            if neighborSet:
                for neighbor in neighborSet:
                    angle = neighbor[2]
                    intersectionType = neighbor[3]
                    intersection = neighbor[4]

                    # corner test
                    if abs(angle-90) < self.angleTol:
                        if neighbor[1] != self.storefrontType:
                            if intersectionType == "Middle":
                                conditionToSet = "OnStorefront"
                                cornerTypes.append("Different")
                                cornerCount += 2
                            elif intersectionType == "Start" or intersectionType == "End":
                                cornerTypes.append("Different")
                                cornerCount += 1

                        elif neighbor[1] == self.storefrontType:
                            # If the storefront is connected to the middle of another storefront
                            # that is the of the same type, then it should join
                            if intersectionType == "Middle":
                                conditionToSet = "JoinStorefront"
                                cornerTypes.append("Same")
                                cornerCount += 2

                            elif intersectionType == "Start" or intersectionType == "End":
                                cornerTypes.append("Same")
                                cornerCount += 1

                    # inline test
                    elif abs(angle-180) < self.angleTol:
                        if neighbor[1] != self.storefrontType:
                            inlineTypes.append("Different")
                            inlineCount += 1 
                        elif neighbor[1] == self.storefrontType:
                            inlineTypes.append("Same")
                            #Placeholder just in case
                            pass

                    # angled test
                    elif abs(round(neighbor[2],1) % 90) > self.angleTol:
                        reverse = 0
                        if self.locLineStart.X > self.locLineEnd.X: 
                            reverse = 180
                        angleRadians = (neighbor[2] * (2 * math.pi)) / 360
                        conditionAngleOffset = (0.5 * self.systemPostWidth) / math.tan((angleRadians) * 0.5)
                        conditionToSet = "Angled"
                        if self.currentConfig["isFramed"]:
                            if i == 0:
                                vect = SFU.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=conditionAngleOffset)
                                self.locLineStart = self.locLineStart.Add(vect)
                                self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                            elif i == 1:
                                vect = SFU.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=conditionAngleOffset)
                                self.locLineEnd = self.locLineEnd.Add(vect)
                                self.storefrontObject.Line = Line.CreateBound(self.storefrontObject.Line.GetEndPoint(0), self.locLineEnd)
                        break

                # compound conditions
                if cornerCount == 0 and inlineCount == 1:
                    if "Same" in inlineTypes:
                        pass
                    elif "Different" in inlineTypes:
                        if self.storefrontType == "Full":
                            conditionToSet = "ForcePost"
                        elif self.storefrontType == "Partial":
                            conditionToSet = "OnStorefront"

                elif cornerCount == 1 and inlineCount == 0:
                    if "Same" in cornerTypes:
                        conditionToSet = None
                    elif "Different" in cornerTypes:
                        if self.storefrontType == "Full":
                            conditionToSet = None
                        elif self.storefrontType == "Partial":
                            conditionToSet = "OnStorefront"
                    else: 
                        pass

                elif cornerCount == 1 and inlineCount == 1:
                    if "Same" in cornerTypes:
                        conditionToSet = "JoinStorefront"
                        if i == 0:
                            vect = SFU.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=self.systemPostWidth/2)
                            self.locLineStart = self.locLineStart.Add(vect)
                            self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                        elif i == 1:
                            vect = SFU.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=self.systemPostWidth/2)
                            self.locLineEnd = self.locLineEnd.Add(vect)
                            self.storefrontObject.Line = Line.CreateBound(self.storefrontObject.Line.GetEndPoint(0), self.locLineEnd)

                    elif "Different" in cornerTypes:
                        conditionToSet = "OnStorefront"
                    else: 
                        pass

                elif cornerCount == 2 and inlineCount == 0:
                    if not "Different"  in  cornerTypes:
                        conditionToSet = "JoinStorefront"
                        if i == 0:
                            vect = SFU.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=self.systemPostWidth/2)
                            self.locLineStart = self.locLineStart.Add(vect)
                            self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                        elif i == 1:
                            vect = SFU.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=self.systemPostWidth/2)
                            self.locLineEnd = self.locLineEnd.Add(vect)
                            self.storefrontObject.Line = Line.CreateBound(self.storefrontObject.Line.GetEndPoint(0), self.locLineEnd)

                    elif "Same" in  cornerTypes and "Different" in cornerTypes:
                        conditionToSet = "ForcePostAtTBone"
                        if i == 0:
                            vect = SFU.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=self.systemPostWidth/2)
                            self.locLineStart = self.locLineStart.Add(vect)
                            self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                        elif i == 1:
                            vect = SFU.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=self.systemPostWidth/2)
                            self.locLineEnd = self.locLineEnd.Add(vect)
                            self.storefrontObject.Line = Line.CreateBound(self.storefrontObject.Line.GetEndPoint(0), self.locLineEnd)

                elif cornerCount == 2 and inlineCount == 1:
                    if "Same" in  cornerTypes and "Different" in cornerTypes and "Different" in inlineTypes:
                        pass

            #Logic gate to set contidions to the right ends either SFobjCrv_StartPt of SFobjCrv_EndPt.
            if i == 0  and neighborSet:
                self.storefrontObject.StartCondition = conditionToSet

                if conditionAngleOffset:
                    self.storefrontObject.StartAngledOffset = conditionAngleOffset

            elif i == 1 and neighborSet:
                self.storefrontObject.EndCondition = conditionToSet

                if conditionAngleOffset:
                    self.storefrontObject.EndAngledOffset = conditionAngleOffset
    def Run_CheckSFWalls(self):
        self.InteriorWallEdges()
        self.InteriorWallMidspans()
        self.ECWalls()
        self.StorefrontIntersections()
        self.FindNeighbors()
        self.DetermineConditions()

#########################################
## BASE CLASS E2: CREATE CURTAIN WALLS ##
#########################################
class CreateSFCurtainWalls:
    def __init__(self):
        # derived parameters
        self.storefrontObject = None
        self.locLine = None
        self.locLineEnd = None
        self.locLineStart = None
    def __repr__(self):
        return("<class 'CreateSFCurtainWalls'>")
    def Run_CreateCurtainWall(self):
        # create Curtain Wall
        with rpw.db.Transaction("Create Curtain Wall") as tx:
            SFU.SupressErrorsAndWarnings(tx)
            newWallHeadHeight = self.storefrontObject.HeadHeight 
            newWallLine = self.storefrontObject.Line
            self.newWall = Wall.Create(self.doc, newWallLine, self.wallTypeCW, self.baseConstraint, newWallHeadHeight, 0, False, False)
            self.newWall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).Set(0)

            #Set new CW Id to self.storefrontObject object 
            self.storefrontObject.CWElementId = self.newWall.Id

            self.doc.Regenerate()

            if self.currentConfig["isFramed"]:
                if self.storefrontObject.StartCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 0)
                if self.storefrontObject.EndCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 1)

            conditionsList = [self.storefrontObject.StartCondition, self.storefrontObject.EndCondition]

            for i in range(len(conditionsList)):
                condition = conditionsList[i]
                newWall_grid = self.newWall.CurtainGrid
                newWallPoint = self.newWall.Location.Curve.GetEndPoint(i)
                mullionList = SFU.GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5)

                if mullionList:
                    for mul in mullionList:
                        mul.Pinned = False
                        if condition == "OnGyp":
                            mul.ChangeTypeId(self.mullionDict["{0}_WallStart".format(self.systemName)])
                        elif condition == "OnObstruction":
                            mul.ChangeTypeId(self.mullionDict["{0}_WallStart".format(self.systemName)])
                        elif condition == "OnStorefront":
                            mul.ChangeTypeId(self.mullionDict["{0}_WallStart".format(self.systemName)])
                        elif condition == "JoinStorefront":
                            self.doc.Delete(mul.Id)
                        elif condition == "ForcePost":
                            mul.ChangeTypeId(self.mullionDict["{0}_Post".format(self.systemName)])
                        elif condition == "ForcePostAtTBone":
                            mul.ChangeTypeId(self.mullionDict["{0}_Post".format(self.systemName)])
                        elif condition == "Angled":
                            if self.currentConfig["isFramed"]:
                                mul.ChangeTypeId(self.mullionDict["{0}_OneBy".format(self.systemName)])
                            else: 
                                self.doc.Delete(mul.Id)

#########################################
## BASE CLASS E3: MODIFY CURTAIN WALLS ##
#########################################
class ModifySFCurtainWalls:
    def __init__(self):
        # derived parameters
        self.minPanelWidth = 1.0
    def __repr__(self):
        return("<class 'ModifySFCurtainWalls'>")
    def ModifyLowerInfillPanels(self):
        # Lower Infill Panels
        newWall_grid = self.newWall.CurtainGrid

        #Create lower infill panel and sill
        if self.currentConfig["hasLowerInfill"]:

            newWallMidPoint = self.newWall.Location.Curve.Evaluate(0.5, True)
            newWall_grid = self.newWall.CurtainGrid
            if self.storefrontObject.SuperType == "Partial":
                with rpw.db.Transaction("Create Lower Infill Panels") as tx:
                    SFU.SupressErrorsAndWarnings(tx)
                    try:
                        gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + self.currentConfig["partialSillHeight"] )
                        grid0 = newWall_grid.AddGridLine(True, gridPt, False)
                    except:
                        pass

                    # Create Solid Lower Panels
                    self.doc.Regenerate()
                    newWall_grid = self.newWall.CurtainGrid
                    uGridIds = newWall_grid.GetVGridLineIds()
                    newWallLocationCurve = self.newWall.Location.Curve
                    verticalGridPoints = []

                    for uGridId in uGridIds:
                        uGrid = self.doc.GetElement(uGridId)
                        uGridOrigin = uGrid.FullCurve.Origin
                        verticalGridPoints.append(XYZ(uGridOrigin.X, uGridOrigin.Y, newWallMidPoint.Z))
                    splitCurves = RevitSplitLineAtPoints(newWallLocationCurve, verticalGridPoints)

                    for sCurve in splitCurves:
                        sCurveMidpoint = sCurve.Evaluate(0.5, True)
                        panelIds = SFU.RevitCurtainPanelsAtPoint(newWall_grid, sCurveMidpoint, detectionTolerance=0.1)
                        panelElevationTupleList = []
                        for panelId in panelIds:
                            panel = self.doc.GetElement(panelId)
                            panelElevationTupleList.append((panel,float(panel.Transform.Origin.Z)))

                        panelElevationTupleList = sorted(panelElevationTupleList, key=lambda x: x[1])

                        #Gets lowest panel and change to solid
                        try:
                            panelToChange = panelElevationTupleList[0][0]
                            panelToChange.Pinned = False
                            panelToChange.ChangeTypeId(self.panelTypeDict[self.currentConfig["panelLowerInfill"]])
                        except:
                            pass
    def ModifySpecialHorizontals(self):
        # Special Horizontals
        specialHorizontals = self.currentConfig["specialHorizontalMullions"]
        if specialHorizontals:
            for key, value in specialHorizontals.items():
                if key in self.wtName:
                    newWallMidPoint = self.newWall.Location.Curve.Evaluate(0.5, True)
                    newWall_grid = self.newWall.CurtainGrid
                    with rpw.db.Transaction("Create Special Horizontal") as tx:
                        SFU.SupressErrorsAndWarnings(tx)
                        try:
                            gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + value[0])
                            grid0 = newWall_grid.AddGridLine(True, gridPt, False)
                        except:
                            pass
    def ModifyMidspanIntersections(self):
        # Midspan Intersections (posts)
        newWall_grid = self.newWall.CurtainGrid
        if self.gridIntersectionPostPoints:
            with rpw.db.Transaction("Create Intersection Grids") as tx:
                SFU.SupressErrorsAndWarnings(tx)
                for gridIntersectionPoint in self.gridIntersectionPostPoints:
                    try:
                        gridInt = newWall_grid.AddGridLine(False, gridIntersectionPoint, False)
                        mullionIntList = SFU.GetVerticalMullionsAtPoint(newWall_grid, gridIntersectionPoint, detectionTolerance=0.001)
                        if mullionIntList:
                            for mullion3 in mullionIntList:
                                mullion3.Pinned = False
                                mullion3.ChangeTypeId(self.mullionDict[self.currentConfig["midspanIntersectionMullion"]])
                    except:
                        pass
    def ModifyEnds(self):
        # Modify Ends
        with rpw.db.Transaction("Modify Ends") as tx:
            SFU.SupressErrorsAndWarnings(tx)
            #Disallow as needed:

            if self.currentConfig["isFramed"]:
                if self.storefrontObject.StartCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 0)
                if self.storefrontObject.EndCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 1)

            self.doc.Regenerate()

            conditionsList = [self.storefrontObject.StartCondition, self.storefrontObject.EndCondition]

            for i in range(len(conditionsList)):
                condition = conditionsList[i]
                newWall_grid = self.newWall.CurtainGrid
                newWallPoint = self.newWall.Location.Curve.GetEndPoint(i)
                mullionList = SFU.GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5, searchOnlySelf=True)

                if mullionList:
                    for mul in mullionList:
                        mul.Pinned = False

                        if condition == "OnGyp":
                            mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])
                        elif condition == "OnObstruction":
                            mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])
                        elif condition == "OnStorefront":
                            mul.ChangeTypeId(self.mullionDict[self.systemName + "_WallStart"])
                        elif condition == "JoinStorefront":
                            self.doc.Delete(mul.Id)
                        elif condition == "ForcePost":
                            mul.ChangeTypeId(self.mullionDict[self.systemName + "_Post"])
                        elif condition == "ForcePostAtTBone":
                            mul.ChangeTypeId(self.mullionDict[self.systemName + "_Post"])
                        elif condition == "Angled":
                            if self.currentConfig["isFramed"]:
                                mul.ChangeTypeId(self.mullionDict[self.systemName + "_OneBy"])
                            else: 
                                self.doc.Delete(mul.Id)
    def ModifyGlazingPanelTypes(self):
        # Glazing Panel Types
        changeToPanel = None

        if "Demising" in self.wtName:
            changeToPanel = self.currentConfig["panelGlazedCenter"]
        elif "Offset" in self.wtName:
            changeToPanel = self.currentConfig["panelGlazedOffset"]
        elif "Double" in self.wtName:
            changeToPanel = self.currentConfig["panelGlazedDouble"]
        else:
            pass

        if changeToPanel:
            with rpw.db.Transaction("Change Glazing Types") as tx:
                SFU.SupressErrorsAndWarnings(tx)
                self.doc.Regenerate()
                panels = newWall_grid.GetPanelIds()
                for panelToChangeId in panels:
                    panelToChange = self.doc.GetElement(panelToChangeId)
                    panelToChange.Pinned = False
                    panelToChange.ChangeTypeId(self.panelTypeDict[changeToPanel])
    def ModifyDoors(self):
        # modify doors
        if self.storefrontObject.Doors:
            newWallStartPoint = self.newWall.Location.Curve.GetEndPoint(0)
            newWallEndPoint = self.newWall.Location.Curve.GetEndPoint(1)
            doorsOnWall = self.storefrontObject.Doors

            with rpw.db.Transaction("Create Door Grids 0") as tx:
                SFU.SupressErrorsAndWarnings(tx)

                for doorId in doorsOnWall:
                    #Location info
                    door = self.doc.GetElement(doorId)
                    doorName = door.Name
                    doorLocationCenter = door.Location.Point
                    doorLocationRotation = door.Location.Rotation
                    doorHandOrientation = door.HandOrientation

                    #Defaults
                    doorHand = "R"
                    doorWidth = 1.0
                    doorType = "SWING"

                    #Get specific door info based on registered doors in the config.
                    if self.doorDict.get(doorName):
                        doorDetails = self.doorDict[doorName]
                        doorHand = doorDetails[0]
                        doorWidth = doorDetails[1]
                        doorType = doorDetails[2]

                        frameMullion0 = self.mullionDict[self.systemName + doorDetails[3]]
                        frameMullion1 = self.mullionDict[self.systemName + doorDetails[4]]
                        extraAdjustment0 = doorDetails[5]
                        extraAdjustment1 = doorDetails[6]

                    else: 
                        #Defaults if no door is found
                        frameMullion0 = self.mullionDict[self.systemName + "_DoorFrame"]
                        frameMullion1 = self.mullionDict[self.systemName + "_DoorFrame"]

                        #Fine adjustments for mullion position
                        extraAdjustment0 = 0
                        extraAdjustment1 = 0
                        print("ISSUE: Unable to recognize door - {0}".format(doorName)) 

                    # get offset widths for door frame mullions
                    fm0 = self.doc.GetElement(frameMullion0)
                    frameMullion0Width = fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
                    frameMullion0Width += fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

                    fm1 = self.doc.GetElement(frameMullion1)
                    frameMullion1Width = fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
                    frameMullion1Width += fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

                    # accounting for mullion CUST_MULLION_THICKnesses 
                    extra0 = (frameMullion0Width * 0.5) + extraAdjustment0
                    extra1 = (frameMullion1Width * 0.5) + extraAdjustment1

                    # vectors to move location point
                    vect0 = doorHandOrientation.Multiply(((doorWidth / 2) + extra0))
                    vect1 = doorHandOrientation.Multiply(((doorWidth / 2) + extra1) * -1)

                    # door SFobjCrv_EndPt points
                    door_end0 = doorLocationCenter.Add(vect0)
                    door_end1 = doorLocationCenter.Add(vect1)


                    # detection tolerance for nearby mullions based on system
                    # required because of varying mullion sizes

                    systemDetectionFactor = self.currentConfig["closeMullionDetectionFactor"]

                    detectionCheckDist0 = frameMullion0Width * systemDetectionFactor
                    detectionCheckDist1 = frameMullion1Width * systemDetectionFactor

                    self.doc.Regenerate()
                    newWall_grid = self.newWall.CurtainGrid

                    # check to see if a mullion exists in the spot where one would be created.
                    checkMullion0 = SFU.GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=detectionCheckDist0)
                    if not checkMullion0:
                        try:
                            grid0 = newWall_grid.AddGridLine(False, door_end0, False)
                        except:
                            pass

                        mullion0List = SFU.GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=0.001)
                        if mullion0List:
                            for mullion0 in mullion0List:
                                mullion0.Pinned = False
                                mullion0.Lock = False
                                mullion0.ChangeTypeId(frameMullion0)

                    self.doc.Regenerate()
                    #Check to see if a mullion exists in the spot where one would be created.
                    checkMullion1 = SFU.GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=detectionCheckDist1)
                    if not checkMullion1:
                        try:
                            grid1 = newWall_grid.AddGridLine(False, door_end1, False)
                        except:
                            pass

                        mullion1List = SFU.GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=0.001)
                        if mullion1List:
                            for mullion1 in mullion1List:
                                mullion1.Pinned = False
                                mullion1.Lock = False
                                mullion1.ChangeTypeId(frameMullion1)

                # empty panel
                    self.doc.Regenerate()
                    panelToChangeId = SFU.RevitCurtainPanelsAtPoint(newWall_grid, doorLocationCenter, detectionTolerance=0.2)
                    if panelToChangeId:
                        panelToChange = self.doc.GetElement(panelToChangeId[0])
                        panelToChange.Pinned = False
                        panelToChange.ChangeTypeId(self.panelTypeDict[self.currentConfig["panelEmpty"]])

                # sill delete
                    self.doc.Regenerate()

                    filterName = self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"].split("_")[1]
                    doorSillMullions = SFU.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter=filterName)

                    for dsm in doorSillMullions:
                        dsm.Pinned = False
                        self.doc.Delete(dsm.Id)

                # continuous head above door
                    doorFrameContinuous = self.currentConfig["mullionContinuousVerticalAtDoorTop"]
                    if not doorFrameContinuous:
                        filterName = self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"].split("_")[1]

                        # join head so its continuous
                        self.doc.Regenerate()
                        doorHeadMullions = SFU.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter="Head")
                        for dhm in doorHeadMullions:
                            dhm.JoinMullion()
    def ModifyIntermediates(self):
        # modify intermediates
        newWall_grid = self.newWall.CurtainGrid
        panels = newWall_grid.GetPanelIds()

        intermediateMullionWidth = 0
        if self.currentConfig["isFramed"]:

            #Select the right intermediate mullion in the project based
            #on which system is being used. 

            if "demising" in self.wtName.lower():
                mulName = self.currentConfig["AUTO_MULLION_INTERIOR_VERT"]
            elif "offset" in self.wtName.lower():
                mulName = self.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"]
            elif "double" in self.wtName.lower():
                mulName = self.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"]
            else:
                mulName = self.currentConfig["AUTO_MULLION_INTERIOR_VERT"]

            intermediateMullion = self.doc.GetElement(self.mullionDict[mulName])

            #Get the sizes of the intermediate
            try:
                intermediateMullionWidth = intermediateMullion.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()
                intermediateMullionWidth += intermediateMullion.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
            except:
                for p in intermediateMullion.Parameters:
                    if p.Definition.Name == "Width on side 1":
                        intermediateMullionWidth += p.AsDouble()
                    if p.Definition.Name == "Width on side 2":
                        intermediateMullionWidth += p.AsDouble()

        #For each panel, check the widths and divide them
        #according to the rules selected by the user.                 
        for panelId in panels:
            panel = self.doc.GetElement(panelId)
            panelWidth = panel.get_Parameter(BuiltInParameter.CURTAIN_WALL_PANELS_WIDTH).AsDouble()

            if "glazed" in (panel.Name + panel.Symbol.Family.Name).lower() and panelWidth > self.minPanelWidth:
                newGridPoints = []
                if self.storefrontSpacingType == 1:
                    newGridPoints = RevitDividePanelFixed(panel, self.storefrontPaneWidth, intermediateWidth=intermediateMullionWidth)
                elif self.storefrontSpacingType == 0:
                    numberPanes = math.ceil(panelWidth/self.storefrontPaneWidth)
                    if numberPanes > 1:
                        newGridPoints = SFU.RevitDividePanelEquidistant(panel, numberPanes, intermediateWidth=intermediateMullionWidth)

                if newGridPoints:
                    with rpw.db.Transaction("Create intermediate grid lines") as tx:
                        SFU.SupressErrorsAndWarnings(tx)
                        for gridpt in newGridPoints:
                            try:
                                grid0 = newWall_grid.AddGridLine(False, gridpt, False)
                                mullions0List = SFU.GetVerticalMullionsAtPoint(newWall_grid, grid0.FullCurve.Origin, detectionTolerance=0.001)
                                for mullion0 in mullions0List:
                                    mullion0.Pinned = False
                                    if self.currentConfig["isFramed"]:
                                        mullion0.ChangeTypeId(intermediateMullion.Id)

                                        #Intermediates die into the head if mullion is "Broken"
                                        if not self.currentConfig["mullionContinuousVerticalIntermediateTop"]:
                                            mullion0.BreakMullion()
                                    else:
                                        #Delete mullion in the case that the system type is butt joined.
                                        self.doc.Delete(mullion0.Id)
                            except:
                                pass
    def SpecialSills(self):
        # special sills
        newWall_grid = self.newWall.CurtainGrid

        updatedSill = None

        currentSill = self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"]
        replacementSills = self.currentConfig["specialSillConditions"]

        if replacementSills:
            for key,value in replacementSills.items():
                if key.lower() in self.wtName.lower():
                    updatedSill = self.mullionDict[value]

        if updatedSill:
            panels = newWall_grid.GetPanelIds()
            with rpw.db.Transaction("Update Sills") as tx:
                SFU.SupressErrorsAndWarnings(tx) 
                for panelId in panels:
                    panel = self.doc.GetElement(panelId)
                    panelPoint = panel.GetTransform().Origin
                    sills = SFU.GetHorizontalMullionsAtPoint(newWall_grid, panelPoint, nameFilter=currentSill)

                    sillElevationTupleList = []
                    for sill in sills:
                        sillElevationTupleList.append((sill,float(sill.LocationCurve.Origin.Z)))

                    sillElevationTupleList = sorted(sillElevationTupleList, key=lambda x: x[1])

                    try:
                        sillToChange = sillElevationTupleList[0][0]
                        sillToChange.Pinned = False
                        sillToChange.ChangeTypeId(updatedSill)
                    except:
                        pass                       
    def Run_ModifySFCurtainWalls(self):
        self.ModifyLowerInfillPanels()
        self.ModifySpecialHorizontals()
        self.ModifyMidspanIntersections()
        self.ModifyEnds()
        self.ModifyGlazingPanelTypes()
        self.ModifyDoors()
        self.ModifyIntermediates()
        self.SpecialSills()

#########################################
## BASE CLASS E4: SET FINAL PARAMETERS ##
#########################################
class SetFinalSFParameters:
    def __init__(self):
        pass
    def __repr__(self):
        return("<class 'SetFinalSFParameters'>")
    def Run_SetFinalSFParameters(self):
        # Set heights, for whatever reason differing heights before adding gridlines is an issue so set this last.
        with rpw.db.Transaction("Create Curtain Wall") as tx:
            SFU.SupressErrorsAndWarnings(tx)
            newWallSillHeight = self.storefrontObject.SillHeight
            newWallHeadHeight = self.storefrontObject.HeadHeight - self.storefrontObject.SillHeight
            self.newWall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(newWallSillHeight)
            self.newWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(newWallHeadHeight)
            self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(self.storefrontObject.SuperType)
            self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("{0}-{1}".format(self.selectedLevelId, self.storefrontObject.AssemblyID))

################################################
## BASE CLASS E & DERIVED CLASS | BUILD WALLS ##
################################################
class BuildSFSystem(CheckSFWalls, CreateSFCurtainWalls,
                    ModifySFCurtainWalls, SetFinalSFParameters):
    def __init__(self):
        # derived parameters
        self.gridIntersectionPostPoints = []
        self.baseConstraint = None
        self.newWall = None
        self.wtName = None
        self.storefrontType = None

        # class inheritance / polymorphism
        CheckSFWalls.__init__(self)
        CreateSFCurtainWalls.__init__(self)
        ModifySFCurtainWalls.__init__(self)
        SetFinalSFParameters.__init__(self)            
    def __repr__(self):
        return("<class 'BuildSFSystem'>")
    def Run_BuildSFSystem(self):
        print("RUNNING...DO NOT CLOSE WINDOW...")

        with rpw.db.TransactionGroup("Convert Wall", assimilate=True) as tg:
            #Adjust any parameters to the walltype before creation if needed.
            with rpw.db.Transaction("Adjust CW Parameters") as tx:
                SFU.SupressErrorsAndWarnings(tx)
                
                wtCW = self.doc.GetElement(self.wallTypeCW)
                if self.currentConfig["deflectionHeadType"] == 2:
                    wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict["{0}_DeflectionHead-2".format(self.systemName)])
                elif self.currentConfig["deflectionHeadType"] == 1:
                    wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict["{0}_DeflectionHead-1".format(self.systemName)])

            # Build Storefront
            for storefrontObject in self.storefrontElevations:
                # convert iterator to class variable
                self.storefrontObject = storefrontObject

                # pyrevit progress bar
                self.progressIndex += 1
                output = script.get_output()

                output.update_progress(self.progressIndex, len(self.storefrontElevations))

                hostElement = self.doc.GetElement(self.storefrontObject.HostElementIds[0])
                self.storefrontType = self.storefrontObject.SuperType

                self.baseConstraint = hostElement.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()

                self.locLine = self.storefrontObject.HostLine
                self.locLineStart = self.locLine.GetEndPoint(0)
                self.locLineEnd = self.locLine.GetEndPoint(1)

                wallHostId = self.storefrontObject.HostElementIds[0]
                self.wtName = self.doc.GetElement(wallHostId).Name
                
                # this geometry will be entry point from rhino engine
                self.newWall = None

                if str(hostElement.WallType.Kind) == "Basic":
                    self.Run_CheckSFWalls()
                    self.Run_CreateCurtainWall()
                    self.Run_ModifySFCurtainWalls()
                    self.Run_SetFinalSFParameters()
        print("STOREFRONT IS FINISHED RUNNING!")

################################
## BASE CLASS F: QC SF SYSTEM ##
################################
class PostSFErrorCheck:
    """
    This class structure is overly complex for just calling an
    oustide module but it is here to serve as a placeholder
    for an eventual pre-error model/checker QC class that will
    be developed at a later point.
    """
    def __init__(self):
        pass
    def __repr__(self):
        return("<class 'PostSFErrorCheck'>")
    def CheckErrors(self):
        print("...CHECKING ERRORS...")
        SFQC.SFCheckErrors().Run_SFCheckErrors()
        print("...DONE! YOU MAY CLOSE THIS WINDOW")

#############################################
## TRYING TO UNDERSTAND WHAT IS GOING ON ? ##
## START HERE !                            ##
##                                         ##
## DERIVED CLASS | GENERATE STOREFRONT     ##
#############################################
class GenerateSF(Collect_PreGUI, Create_NibWalls, 
                 CollectSFElements, ParseSFWalls_Rhino, 
                 BuildSFSystem, PostSFErrorCheck):
    """
    THE PURPOSE OF THE STOREFRONT TOOL IS TO CREATE CURTAIN
    WALL THAT IS GENERATED CORRECTLY DESPITE THE LOCATION OF THE DOOR.
    IT IS THE DOOR THAT IS PREVENTING THE BUILT IN TOOL FROM BEING ENOUGH.

    ALSO BUILT-IN TOOLS WILL NOT PARAMETICALLY DEAL WITH INTERSECTION CONDITIONS
    ON THEIR OWN (CORNERS, PERPENDICULAR, ETC...)

    IN EXISTING STOREFRONT AUTO EMBED IS OFF, HOW DOES IT WORK THEN?
    HOW CAN THE "AUTOMATICALLY EMBED" PARAMETER BE USED?

    ISSUES: THERE COULD BE 2 EC MODELS...LIKE 411 UNION...
            THIS IS A PROBLEM FOR "SFU.RevitLoadECDocument"

            MUST ENSURE CONVERSION FROM INCHES TO FEET AND IMPERIAL
            TO METRIC WHEN A GIVEN SYSTEM IS SELECTED...
    """
    def __init__(self):
        """
        Generates curtain wall on top of 
        existing basic walls.
        """
        # revit doc parameters
        self.doc = __revit__.ActiveUIDocument.Document
        self.app = __revit__.Application
        self.version = __revit__.Application.VersionNumber.ToString()
        self.uidoc = __revit__.ActiveUIDocument
        self.currentView = __revit__.ActiveUIDocument.ActiveView

        # immediately needed global parameters
        self.currentConfig = None

        # pyRevit progress bar in console window
        self.progressIndex = 0.0

        # global parameters
        self.user = str(System.Environment.UserName)
        self.tol = 0.001
        self.mrTimer = SFU.Timer() # not used so far
        self.selectionType = None
        
        # helper family methods
        # instantiates family modules to SFobjCrv_StartPt 
        # extracting data from it in this script - nothing created yet
        self.familyObj = SFF.FamilyTools(self.doc)   

        # class inheritance / polymorphism
        Collect_PreGUI.__init__(self)
        Create_NibWalls.__init__(self)
        CollectSFElements.__init__(self)
        ParseSFWalls_Rhino.__init__(self)
        
        # [...] derived class w/ its own inheritances
        BuildSFSystem.__init__(self)
        
        PostSFErrorCheck.__init__(self)
    
    def __repr__(self):
        return("<class 'GenerateSF'>")
    
    def TaskDialogue(self):
        mainDialog = TaskDialog("Storefront 2")
        mainDialog.MainInstruction = "WHOA! HANLON YOU MESSED UP"
        mainDialog.MainContent = "Make sure you either select a SF wall, run this tool in a plan view, or select at least one level from the list"

        # Set common buttons and default button. If no CommonButton or CommandLink is added,
        # task dialog will show a Close button by default
        mainDialog.CommonButtons = TaskDialogCommonButtons.Close
        mainDialog.DefaultButton = TaskDialogResult.Close

        mainDialog.Show()        
    
    def Run_GenerateSF(self):
        # instantiate variables that need to be fed to GUI
        self.Run_PreGUIMethods()
        
        # instantiate rpw form | what system will be created and what families are loaded
        formObj = SFGUI.SF_Form(self.doc, 
                                gypWallOptions=self.gypWallDict_KEYS,
                                loadedFamilies=self.loadedFamilies)
        formObj.SF_GetuserSelection()
        #Application.Run(formObj) 
   
        # how configs get used: currentConfigs are written by selections made by user configs
        # current configs are saved as json and referenced at SFobjCrv_StartPt of project
        # this is a separate json file that is read 
        self.currentConfig = formObj.currentConfig
        
        # test for/collect user selection
        self.userSelectedIds = [i for i in self.uidoc.Selection.GetElementIds()
                                if i.Name in SFF.FamilyTools(self.doc).SFWallTypeNames.keys()]        
        
        
        # A) USER MADE A SELECTION - ESTABLISH SELECTION TYPE
        if self.userSelectedIds and not formObj.userSelection["selectedLevels"]:
            self.selectionType = "userSelection"     
        # B) NO USER SELECTION OR LEVEL SELECTION BUT USER IN PLAN VIEW
        elif not self.userSelectedIds and not formObj.userSelection["selectedLevels"] and str(self.currentView.ViewType) == "FloorPlan":
            self.selectionType = "planViewSelection"
        # C) USER SELECTED LEVELS FROM GUI OPTION LIST
        elif formObj.userSelection["selectedLevels"]:
            self.selectionType = "levelSelection"
        # D) NO APPROPRIATE SELECTION MADE
        else:
            self.TaskDialogue()
         
         
        # run whole script - current currentConfig file fed back to family module
        if formObj.userSelection["createNibWallOnly"] == False:
            
            # load families
            SFF.FamilyTools(self.doc).Run_LoadFamilies(self.currentConfig)
    
            # create nib walls
            if formObj.userSelection["createNibWall"]:
                if str(self.currentView.ViewType) == "FloorPlan":
                    self.Run_CreateNibWalls() # shouldn't this be current config? saved userSelection from form become currentConfig?
                else:
                    Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Run the tool in floorplan view only!")
                    pyrevit.script.exit()                
    
            # collect walls and sort stuff
            self.Run_StorefrontPrep()
    
            # build walls from collected elements - sets firing sequence for dependent classes
            self.Run_BuildSFSystem()
    
            # check for errors after everything has been built
            self.CheckErrors()
        
        # only run nib walls
        elif formObj.userSelection["createNibWallOnly"] == True:
            if str(self.currentView.ViewType) == "FloorPlan":
                
                # GET SELECTION TYPE
                
                self.Run_CreateNibWalls()
            else:
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Run the tool in floorplan view only!")
                pyrevit.script.exit()
                """