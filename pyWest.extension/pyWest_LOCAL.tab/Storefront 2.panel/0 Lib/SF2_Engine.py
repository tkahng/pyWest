"""
:tooltip:
Module for Storefront logic
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork Design Technology West

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""
__author__ = 'WeWork Buildings Systems / Design Technology West'
__version__ = "2.Pre-Alpha"

import clr
import traceback

try:
    import os
    import sys
    import logging
    import System
    import math
    import _csv as csv
    import json
    import rpw

    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
    from Autodesk.Revit.UI import *
    from Autodesk.Revit.DB import *
    import Autodesk.Revit.UI.Selection

    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System.Drawing')
    from System.Windows.Forms import SaveFileDialog
    from System.Drawing import *
    from System.Drawing import Point
    from System.Windows.Forms import Application, Button, CheckBox, Form, Label
    from System.Collections.Generic import List, IEnumerable
    from System import Array
    from System import DateTime as dt

    from pyrevit import script

    # SF2 modules
    import SF2_GUI
    #import SF2_GUI2
    import SF2_Utility
    import SF2_QC
    import SF2_Families

    ########################################################
    ## STOREFRONT ELEVATION - NOT PART OF ANY INHERITANCE ##
    ########################################################
    """
    I AM STILL UNCLEAR ABOUT WHAT THIS CLASS IS BEING USED FOR

    _VARIABLE = declaring private variables, functions, methods, or classes in a module
                it will not be imported by "import module"
    __VARIABLE = variables that will get abbreviated with class name as a way of projecting
                 variables whose names might get repeated as code is expanded with additional classes
    """
    class StorefrontElevation:
        def __init__(self, _hostElementIds, _line, _superType, _id, _sillHeight, _headHeight, _systemName):	
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

    ############################
    ## SPLIT STOREFRONT WALLS ##
    ############################
    class CreateNibWalls:
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
            self.leftoverTol = 0.35  #Nib wall length

            self.gypWallList = ["Partition-Gyp", "Partition-Gyp 2",
                                "WWi-Partition-Typical-A1", "WWi-Partition-Typical-A2",
                                "WWi-Partition-Typical-A3", "WWi-Partition-Typical-A4",
                                "WWi-Partition-Typical-C1", "WWi-Partition-Typical-C2",
                                "WWi-Partition-Typical-C3", "WWi-Partition-Typical-C4",
                                "WWi-Partition-Typical-C5", "WWi-Partition-Typical-C6",
                                "WWi-Partition-Typical-D1", "WWi-Partition-Typical-D2",
                                "WWi-Partition-Typical-D3", "WWi-Partition-Typical-D4",
                                "WWi-Partition-Typical-D5", "WWi-Partition-Typical-D6"]

        def Run_CreateNibWalls(self, nibWallLength):
            # ADD THESE SAVE SETTINGS TO CONFIGURATION LATER DOWN IN THE SCRIPT
            ## user settings into a dict
            #config = {"nibWallType": wallTypesDict.keys()[wallTypesDict.values().index(gypNibWallTypeId)],
                        #"splitOffset" : splitTypes.keys()[splitTypes.values().index(selectedNibLength)]}
            ##save selected system
            #storefrontConfig.Run_SaveSFConfigurations(user_configs=config)  

            selectedSystem = self.currentConfig["currentSystem"]
            postWidth = self.currentConfig["postWidth"]
            oneByWidth = self.currentConfig["oneByWidth"]

            currentLevel = self.currentView.GenLevel
            levelName = currentLevel.Name

            gypWall = "Basic Wall - Partition-Gyp"
            self.currentConfig["nibWallType"] = gypWall       

            gypNibWallTypeId = gypWall
            selectedNibLength = nibWallLength

            # allow option to only create nib walls on user selected objects
            currentSelectedIds = self.uidoc.Selection.GetElementIds()

            if not currentSelectedIds:
                # get storefront walls from view in document
                storefrontWallIds = [i.Id for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall) if i.Name in ]
            else: storefrontWallIds = currentSelectedIds # clunky fix this

            # returns type(symbol) Id - only need one for this operation, still clunky
            gypNibWallTypeId = [i.GetTypeId() for i in FilteredElementCollector(self.doc).OfClass(Wall) if i.Name in self.gypWallList][0]

            # TESTS FOR OBTAINING WALL TYPE ID OF OBJECTS NOT CURRENTLY IN REVIT MODEL SPACE

            #wallId = ElementId(BuiltInCategory.OST_Walls)
            #element = self.doc.GetElement(wallId)
            #print(element)

            #f = self.app.Create.Filter.NewTypeFilter(Wall)
            #docWalls = self.doc.get_Elements(f)
            #print(docWalls)


            intersectionPoints = SF2_Utility.RemoveDuplicatePoints(SF2_Utility.FindWallIntersections(storefrontWallIds))

            # iterate through either selected walls or SF collected in document
            if currentSelectedIds:
                wallsToIterate = currentSelectedIds
            elif storefrontWallIds:
                wallsToIterate = storefrontWallIds
            else:
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "No Storefront walls selected or found in the view")
                pyrevit.script.exit()

            with rpw.db.Transaction("Create Nib") as tx:
                SF2_Utility.SupressErrorsAndWarnings(tx) # i added this
                
                for id in wallsToIterate:
                    # use id to get element data from revit doc
                    inst = self.doc.GetElement(id)

                    if inst.Category.Name == "Walls":
                        instName = None
                        topConstraint = None
                        unconnectedHeight = None
                        baseOffset = None
                        topOffset = None
                        botConstraint = currentLevel.Id

                        # 2 different ways of obtaining parameters (instance name) bc changes in the api
                        try:
                            instName = inst.Name.lower()
                        except:
                            for p in inst.Parameters:
                                if p.Definition.Name == "Name":
                                    instName = p.AsString().lower()

                        if "storefront" not in instName:
                            continue
                        # split storefront wall at index to create nib wall - nib matches parameters of split wall
                        else:
                            for p in inst.Parameters:
                                if p.Definition.Name == "Top Constraint":
                                    topConstraint = p.AsElementId() # element Id of top constraint object
                                if p.Definition.Name == "Unconnected Height":
                                    unconnectedHeight = p.AsDouble()
                                if p.Definition.Name == "Top Offset":
                                    topOffset = p.AsDouble()

                            # check to see which ends are naked
                            instLine = inst.Location.Curve
                            start = instLine.GetEndPoint(0)
                            end = instLine.GetEndPoint(1)
                            startOverlap = False
                            endOverlap = False
                            if intersectionPoints:
                                for point in intersectionPoints:
                                    if point.DistanceTo(start) < self.tol:
                                        startOverlap = True
                                    elif point.DistanceTo(end) < self.tol:
                                        endOverlap = True
                                    if startOverlap and endOverlap:
                                        break

                            # if only one end is touching other walls
                            if startOverlap == False or endOverlap == False:
                                nibWall = None
                                nibWalls = []
                                offset = 0
                                lengthAdjust = (0.5 * postWidth) + oneByWidth
                                length = instLine.Length - lengthAdjust
                                leftover = length%(self.standardSizes[0] + oneByWidth)
                                # var for "OPTIMIZED" calculation
                                numPanels = math.floor(length / (self.standardSizes[0] + oneByWidth))

                                # optimized nib wall split
                                if selectedNibLength == "OPTIMIZED":
                                    # if optimized split
                                    if leftover > self.leftoverTol:
                                        lastPanelSize = 0
                                        for size in self.standardSizes[1:]:
                                            if leftover - self.leftoverTol >= (size + oneByWidth):
                                                lastPanelSize = self.standardSizes[self.standardSizes.index(size)]
                                                break
                                        offset = lengthAdjust + numPanels*self.standardSizes[0] + (numPanels)*oneByWidth + lastPanelSize + int(lastPanelSize > 0)*oneByWidth
                                    else:
                                        offset = lengthAdjust + (numPanels-1)*self.standardSizes[0] + self.standardSizes[1] + (numPanels)*oneByWidth
                                # fixed nib wall split
                                else:
                                    offset = instLine.Length - selectedNibLength  

                                if startOverlap or (startOverlap == endOverlap):
                                    try:
                                        newPoint = XYZ(((end.X-start.X)*(offset/(length + lengthAdjust)))+start.X,((end.Y-start.Y)*(offset/(length + lengthAdjust)))+start.Y, start.Z)
                                        inst.Location.Curve = Line.CreateBound(start, newPoint)
                                        nibWallLine = Line.CreateBound(newPoint,end)

                                        end = newPoint

                                        nibWalls.append(Wall.Create(self.doc, nibWallLine, currentLevel.Id, False))
                                        self.doc.Regenerate()                                        
                                    except:
                                        print("Wall {0} was too short to add a nib wall".format(id))

                                if endOverlap or (startOverlap == endOverlap):
                                    try:
                                        newPoint = XYZ(((start.X-end.X)*(offset/(length + lengthAdjust)))+end.X,((start.Y-end.Y)*(offset/(length + lengthAdjust)))+end.Y, end.Z)
                                        inst.Location.Curve = Line.CreateBound(newPoint, end)                  

                                        nibWallLine = Line.CreateBound(newPoint,start)

                                        start = newPoint

                                        nibWalls.append(Wall.Create(self.doc, nibWallLine, currentLevel.Id, False))
                                        self.doc.Regenerate()
                                    except:
                                        print("Wall {0} was too short to add a nib wall".format(id))                                    

                                if nibWalls:
                                    for nibWall in nibWalls:
                                        # it seems like you create walls of whatever type then change type
                                        # but you inherit parameter settings of host wall???
                                        nibWall.WallType = self.doc.GetElement(gypNibWallTypeId)
                                        nibTopConstraint = nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId()

                                        if topConstraint.IntegerValue == botConstraint.IntegerValue:
                                            nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId(-1))
                                        else:
                                            nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(topConstraint)

                                        for p in nibWall.Parameters:
                                            if p.Definition.Name == "Location Line":
                                                p.Set(0)
                                            if p.Definition.Name == "Unconnected Height" and topConstraint.IntegerValue == -1:
                                                p.Set(unconnectedHeight)

                                        self.doc.Regenerate()
                                        if topConstraint.IntegerValue == botConstraint.IntegerValue:
                                            nibWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(topOffset)
                            else:
                                continue        

    ##########################
    ## COLLECT MOSTLY WALLS ## ADD DEFAULT VIEWS TO RUN WITHOUT BEING IN PLAN VIEW
    ##########################
    class CollectWallsColumns:
        def __init__(self, currentViewOnly=True):
            # input parameters
            self.currentViewOnly = currentViewOnly

        ###################
        ## COLLECT WALLS ##
        ###################
        def CollectSFWalls(self):
            # level of current view
            self.selectedLevelId = self.currentView.GenLevel.Id
            self.selectedLevelObj = self.doc.GetElement(self.selectedLevelId)

            # walls collected by user selection -> returns wall object
            selectionIdList = self.uidoc.Selection.GetElementIds()
            if selectionIdList: wallList = [self.doc.GetElement(id) for id in selectionIdList if self.doc.GetElement(id).Name in SF2_Families.FamilyTools(self.doc).SFWallTypeNames.keys()]

            # walls collected by code -> returns wall object
            if not selectionIdList and self.currentViewOnly == True:
                # must be in plan view, how do i manage this???
                self.wallList = [i for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall) if i.Name in SF2_Families.FamilyTools(self.doc).SFWallTypeNames.keys()] # Autodesk.Revit.DB.Wall - defines <type 'Wall'>
            if not selectionIdList and self.currentViewOnly == False:
                self.wallList = [i for i in FilteredElementCollector(self.doc).OfClass(Wall) if i.Name in SF2_Families.FamilyTools(self.doc).SFWallTypeNames.keys()]

            if self.wallList: return()
            else: raise Esception("There are no walls in the model")
        
        #######################################
        ## COLLECT COLUMNS, LEVELS, LEVEL #s ##
        #######################################
        def CollectColumns(self):
            self.allColumns = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance, currentView=True) # used eventually in build curtain wall
            self.allColumns += SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance, currentView=True) # used eventually in build curtain wall

        def CollectWallLevels(self):
            # obtain level ids then use ids to collect elements
            levelIdList = [i.LevelId for i in self.wallList]
            self.levelList = [self.doc.GetElement(id) for id in levelIdList]

        def CollectLevelNumbers(self):
            levelNameList = [i.Name for i in self.levelList]
            self.levelNumList = [list(map(float, re.findall(r'\d+', i)))[0] for i in levelNameList] # isolate level integer in string name
            # BUT WHAT IF IT IS CALLED CONTAINER, GROUND, OR SOME OTHER BULLSHIT

        #########################
        ## SORT WALLS BY LEVEL ##
        #########################
        def SortWallsByLevel(self):
            self.wallList = [i for _,i in sorted(zip(self.wallList, self.levelNumList))]

        def GroupWallsByLevel(self):
            setList = sorted(set(self.levelNumList))

            #self.self.nestedWallList = []
            for i in setList:
                tempList = []
                for j, wall in enumerate(self.wallList):
                    if self.levelNumList[j] == i:
                        tempList.append(wall)
                self.nestedWallList.append(tempList)

        ################
        ## CLASS MAIN ##
        ################
        def Run_CollectWalls(self):
            # collect all walls and columns
            self.CollectSFWalls()
            self.CollectColumns()

            # get levels of each wall
            self.CollectWallLevels()
            self.CollectLevelNumbers()

            # group walls by level
            sortedNestedWallList = self.GroupWallsByLevel()

    ########################################
    ## COLLECT / PREP SF WALLS - ORIGINAL ##
    ########################################
    class CollectSFElements:
        def __init__(self):
            # pyRevit progress bar in console window
            self.progressIndex = 0.0

            # derived parameters - CollectAllElementsInView()
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

            self.docLoaded = SF2_Utility.RevitLoadECDocument(self.doc)
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
            self.absoluteTol = 0.001
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
        def CollectAllElementsInView(self):
            self.selectedLevelId = self.currentView.GenLevel.Id
            self.selectedLevelObj = self.doc.GetElement(self.selectedLevelId)

            allColumns = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance, currentView=True)
            allColumns += SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance, currentView=True)
            
            # add SF Full and Partial lists together here instead of re-collecting everything
            self.interiorWallIds = [i.Id for i in self.viewCollector.OfClass(Wall) if i.Name in self.familyObj.SFWallTypeNames.keys()]
            
            currentSelectedIds = list(self.uidoc.Selection.GetElementIds())
            if currentSelectedIds:
                self.FilterSFWalls(currentSelectedIds)                   
            else:
                self.FilterSFWalls(self.viewCollector.OfClass(Wall))

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
            self.storefrontFullIds = SF2_Utility.FilterElementsByLevel(self.doc, self.storefrontFullIds, self.selectedLevelId)
            self.storefrontPartialIds = SF2_Utility.FilterElementsByLevel(self.doc, self.storefrontPartialIds, self.selectedLevelId)
            self.interiorWallIds = SF2_Utility.FilterElementsByLevel(self.doc, self.interiorWallIds, self.selectedLevelId)
            selectedColumns = SF2_Utility.FilterElementsByLevel(self.doc, allColumns, self.selectedLevelId)

            # collect perimeter/collision geometry from EC model
            if self.docEC:
                levelElevationEC = None 
                for p in self.selectedLevelObj.Parameters:
                    if p.Definition.Name == "Elevation":
                        levelElevationEC = p.AsDouble()
                self.selectedWallsEC = SF2_Utility.FilterElementsByLevel(self.docEC, self.allWallsEC, levelElevationEC)
                self.selectedColumnsEC = SF2_Utility.FilterElementsByLevel(self.docEC, self.allColumnsEC, levelElevationEC)
                self.wallsLinesEdgesEC = SF2_Utility.GetWallEdgeCurves(self.docEC, self.selectedWallsEC, self.ecTransform)
                self.columnsLinesEdgesEC = SF2_Utility.GetColumnEdgeCurves(self.docEC, self.selectedColumnsEC, self.ecTransform)

            # collect perimeter/collision geometry from Design model
            self.interiorWallsLinesEdges = SF2_Utility.GetWallEdgeCurves(self.doc, self.interiorWallIds, None)
            self.columnsLinesEdges = SF2_Utility.GetColumnEdgeCurves(self.doc, selectedColumns)

            levelElevation = self.selectedLevelObj.Elevation
        def Prep(self):
            self.systemName = self.currentConfig["currentSystem"]

            self.storefrontPaneWidth = self.currentConfig["storefrontPaneWidth"]
            self.storefrontSpacingType = self.currentConfig["spacingType"]

            self.mullionDict = SF2_Utility.GetMullionTypeDict(self.doc)
            self.panelTypeDict = SF2_Utility.GetWindowTypeDict()
            self.doorDict = self.currentConfig["systemDoors"]
            wallTypeDict = SF2_Utility.GetWallTypeDict()
            self.wallDoorHostDict = SF2_Utility.GetDoorDictByWallHost()

            # Ensure walltypes are loaded
            if not "I-Storefront-"+ self.systemName in wallTypeDict.keys():
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Make sure you selected/loaded the correct partition system. Check your wall types.")
                sys.exit()

            # Profile widths
            self.systemPostWidth = self.doc.GetElement(self.mullionDict[self.systemName+"_Post"]).get_Parameter(BuiltInParameter.CUST_MULLION_THICK).AsDouble()

            systemDoorFrame = self.doc.GetElement(self.mullionDict[self.systemName+"_DoorFrame"])
            systemDoorFrameWidth = systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
            systemDoorFrameWidth += systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

            systemOneBy = self.doc.GetElement(self.mullionDict[self.systemName+"_OneBy"])
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
                                    if dist < self.absoluteTol:
                                        angle = SF2_Utility.AngleThreePoints(point1b, point1a, point2b)
                                        if abs(angle-180) < self.absoluteTol:
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
        def Run_StorefrontPrep(self):
            self.CollectAllElementsInView()
            self.Prep()
            self.WrapAndChain()

    ########################################
    ## RHINO ENGINE TO REPLACE CHECKMODEL ##
    ########################################
    class ParseSFWalls_Rhino:
        """
        THE BASIC IDEA IS GET CENTERLINES, DO ALL THIS LOGIC,
        THEN USE THE CENTERLINES TO MODIFY EXISTING WALL FAMILIES
        """
        def __init__(self):
            pass

    ##############################
    ## vv CHECK MODEL FOR STUFF ##
    ##############################
    class CheckSFWalls:
        def __init__(self):
            # derived parameters
            self.distTol = 0.5 
            self.angleTol = 0.01

        def InteriorWallEdges(self):
            # check interior wall edges
            self.locLine = self.storefrontObject.HostLine
            self.locLineStart = self.locLine.GetEndPoint(0)
            self.locLineEnd = self.locLine.GetEndPoint(1)

            for intWallLine in self.interiorWallsLinesEdges:
                intersection = SF2_Utility.RevitCurveCurveIntersection(self.locLine,intWallLine)

                if intersection:
                    distToEnd = intersection.DistanceTo(self.locLineEnd) 
                    distToStart = intersection.DistanceTo(self.locLineStart) 

                    #If intersection is at the ends
                    if distToEnd < self.distTol:
                        self.storefrontObject.EndCondition = "OnGyp"
                        # If intersection is not at the surface of the edges of interior walls
                        if distToEnd > self.absoluteTol:
                            self.storefrontObject.Line = Line.CreateBound(self.locLineStart, intersection)

                    elif distToStart < self.distTol:
                        self.storefrontObject.StartCondition = "OnGyp"
                        if distToStart > self.absoluteTol:
                            self.storefrontObject.Line = Line.CreateBound(intersection, self.locLineEnd)
        def InteriorWallMidspans(self):
            # check interior wall midspans
            for intWallId in self.interiorWallIds:
                intWall = self.doc.GetElement(intWallId)
                intWallLine = intWall.Location.Curve
                intersection = SF2_Utility.RevitCurveCurveIntersection(self.locLine,intWallLine)
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
                    intersection = SF2_Utility.RevitCurveCurveIntersection(locLineFlat,obstructionLine)
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
                    intersection = SF2_Utility.RevitCurveCurveIntersection(self.locLine,neighborLocLine)

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

                        # check if intersection is at the start point or end point or middle
                        if intersection.DistanceTo(self.locLineStart) < self.tol:
                            angle = SF2_Utility.AngleThreePoints(self.locLineEnd, intersection, point1)
                            self.storefrontObject.StartNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                        elif intersection.DistanceTo(self.locLineEnd) < self.tol:
                            angle = SF2_Utility.AngleThreePoints(self.locLineStart, intersection, point1)
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
            # determine start conditions
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
                                    vect = SF2_Utility.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=conditionAngleOffset)
                                    self.locLineStart = self.locLineStart.Add(vect)
                                    self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                                elif i == 1:
                                    vect = SF2_Utility.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=conditionAngleOffset)
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
                                vect = SF2_Utility.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=self.systemPostWidth/2)
                                self.locLineStart = self.locLineStart.Add(vect)
                                self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                            elif i == 1:
                                vect = SF2_Utility.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=self.systemPostWidth/2)
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
                                vect = SF2_Utility.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=self.systemPostWidth/2)
                                self.locLineStart = self.locLineStart.Add(vect)
                                self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                            elif i == 1:
                                vect = SF2_Utility.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=self.systemPostWidth/2)
                                self.locLineEnd = self.locLineEnd.Add(vect)
                                self.storefrontObject.Line = Line.CreateBound(self.storefrontObject.Line.GetEndPoint(0), self.locLineEnd)

                        elif "Same" in  cornerTypes and "Different" in cornerTypes:
                            conditionToSet = "ForcePostAtTBone"
                            if i == 0:
                                vect = SF2_Utility.RevitTransVector(self.locLineStart, self.locLineEnd, magnitude=self.systemPostWidth/2)
                                self.locLineStart = self.locLineStart.Add(vect)
                                self.storefrontObject.Line = Line.CreateBound(self.locLineStart, self.storefrontObject.Line.GetEndPoint(1))

                            elif i == 1:
                                vect = SF2_Utility.RevitTransVector(self.locLineEnd, self.locLineStart, magnitude=self.systemPostWidth/2)
                                self.locLineEnd = self.locLineEnd.Add(vect)
                                self.storefrontObject.Line = Line.CreateBound(self.storefrontObject.Line.GetEndPoint(0), self.locLineEnd)

                    elif cornerCount == 2 and inlineCount == 1:
                        if "Same" in  cornerTypes and "Different" in cornerTypes and "Different" in inlineTypes:
                            pass

                #Logic gate to set contidions to the right ends either start of end.
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

    #############################
    ## ^^ CREATE CURTAIN WALLS ##
    #############################
    class CreateSFCurtainWalls:
        def __init__(self):
            # derived parameters
            self.storefrontObject = None
            self.locLine = None
            self.locLineEnd = None
            self.locLineStart = None            
        def Run_CreateCurtainWall(self):
            # create Curtain Wall
            with rpw.db.Transaction("Create Curtain Wall") as tx:
                SF2_Utility.SupressErrorsAndWarnings(tx)
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
                    mullionList = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5)

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

    #############################
    ## ^^ MODIFY CURTAIN WALLS ##
    #############################
    class ModifySFCurtainWalls:
        def __init__(self):
            # derived parameters
            self.minPanelWidth = 1.0
        def ModifyLowerInfillPanels(self):
            # Lower Infill Panels
            newWall_grid = self.newWall.CurtainGrid

            #Create lower infill panel and sill
            if self.currentConfig["hasLowerInfill"]:

                newWallMidPoint = self.newWall.Location.Curve.Evaluate(0.5, True)
                newWall_grid = self.newWall.CurtainGrid
                if self.storefrontObject.SuperType == "Partial":
                    with rpw.db.Transaction("Create Lower Infill Panels") as tx:
                        SF2_Utility.SupressErrorsAndWarnings(tx)
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
                            panelIds = SF2_Utility.RevitCurtainPanelsAtPoint(newWall_grid, sCurveMidpoint, detectionTolerance=0.1)
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
                            SF2_Utility.SupressErrorsAndWarnings(tx)
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
                    SF2_Utility.SupressErrorsAndWarnings(tx)
                    for gridIntersectionPoint in self.gridIntersectionPostPoints:
                        try:
                            gridInt = newWall_grid.AddGridLine(False, gridIntersectionPoint, False)
                            mullionIntList = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, gridIntersectionPoint, detectionTolerance=0.001)
                            if mullionIntList:
                                for mullion3 in mullionIntList:
                                    mullion3.Pinned = False
                                    mullion3.ChangeTypeId(self.mullionDict[self.currentConfig["midspanIntersectionMullion"]])
                        except:
                            pass
        def ModifyEnds(self):
            # Modify Ends
            with rpw.db.Transaction("Modify Ends") as tx:
                SF2_Utility.SupressErrorsAndWarnings(tx)
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
                    mullionList = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5, searchOnlySelf=True)

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
                    SF2_Utility.SupressErrorsAndWarnings(tx)
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
                    SF2_Utility.SupressErrorsAndWarnings(tx)

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

                        # door end points
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
                        checkMullion0 = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=detectionCheckDist0)
                        if not checkMullion0:
                            try:
                                grid0 = newWall_grid.AddGridLine(False, door_end0, False)
                            except:
                                pass

                            mullion0List = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=0.001)
                            if mullion0List:
                                for mullion0 in mullion0List:
                                    mullion0.Pinned = False
                                    mullion0.Lock = False
                                    mullion0.ChangeTypeId(frameMullion0)

                        self.doc.Regenerate()
                        #Check to see if a mullion exists in the spot where one would be created.
                        checkMullion1 = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=detectionCheckDist1)
                        if not checkMullion1:
                            try:
                                grid1 = newWall_grid.AddGridLine(False, door_end1, False)
                            except:
                                pass

                            mullion1List = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=0.001)
                            if mullion1List:
                                for mullion1 in mullion1List:
                                    mullion1.Pinned = False
                                    mullion1.Lock = False
                                    mullion1.ChangeTypeId(frameMullion1)

                    # empty panel
                        self.doc.Regenerate()
                        panelToChangeId = SF2_Utility.RevitCurtainPanelsAtPoint(newWall_grid, doorLocationCenter, detectionTolerance=0.2)
                        if panelToChangeId:
                            panelToChange = self.doc.GetElement(panelToChangeId[0])
                            panelToChange.Pinned = False
                            panelToChange.ChangeTypeId(self.panelTypeDict[self.currentConfig["panelEmpty"]])

                    # sill delete
                        self.doc.Regenerate()

                        filterName = self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"].split("_")[1]
                        doorSillMullions = SF2_Utility.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter=filterName)

                        for dsm in doorSillMullions:
                            dsm.Pinned = False
                            self.doc.Delete(dsm.Id)

                    # continuous head above door
                        doorFrameContinuous = self.currentConfig["mullionContinuousVerticalAtDoorTop"]
                        if not doorFrameContinuous:
                            filterName = self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"].split("_")[1]

                            # join head so its continuous
                            self.doc.Regenerate()
                            doorHeadMullions = SF2_Utility.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter="Head")
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
                            newGridPoints = SF2_Utility.RevitDividePanelEquidistant(panel, numberPanes, intermediateWidth=intermediateMullionWidth)

                    if newGridPoints:
                        with rpw.db.Transaction("Create intermediate grid lines") as tx:
                            SF2_Utility.SupressErrorsAndWarnings(tx)
                            for gridpt in newGridPoints:
                                try:
                                    grid0 = newWall_grid.AddGridLine(False, gridpt, False)
                                    mullions0List = SF2_Utility.GetVerticalMullionsAtPoint(newWall_grid, grid0.FullCurve.Origin, detectionTolerance=0.001)
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
                    SF2_Utility.SupressErrorsAndWarnings(tx) 
                    for panelId in panels:
                        panel = self.doc.GetElement(panelId)
                        panelPoint = panel.GetTransform().Origin
                        sills = SF2_Utility.GetHorizontalMullionsAtPoint(newWall_grid, panelPoint, nameFilter=currentSill)

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

    #############################
    ## ^^ SET FINAL PARAMETERS ##
    #############################
    class SetFinalSFParameters:
        def __init__(self):
            pass
        def Run_SetFinalSFParameters(self):
            # Set heights, for whatever reason differing heights before adding gridlines is an issue so set this last.
            with rpw.db.Transaction("Create Curtain Wall") as tx:
                SF2_Utility.SupressErrorsAndWarnings(tx)
                newWallSillHeight = self.storefrontObject.SillHeight
                newWallHeadHeight = self.storefrontObject.HeadHeight - self.storefrontObject.SillHeight
                self.newWall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(newWallSillHeight)
                self.newWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(newWallHeadHeight)
                self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(self.storefrontObject.SuperType)
                self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(str(self.selectedLevelId) + "-"+ str(self.storefrontObject.AssemblyID))

    #########################################
    ## ^^ DERIVED PARENT CLASS BUILD WALLS ##
    #########################################
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

        def Run_BuildSFSystem(self):
            print("RUNNING...DO NOT CLOSE WINDOW...")

            with rpw.db.TransactionGroup("Convert Wall", assimilate=True) as tg:
                #Adjust any parameters to the walltype before creation if needed.
                with rpw.db.Transaction("Adjust CW Parameters") as tx:
                    SF2_Utility.SupressErrorsAndWarnings(tx)
                    
                    wtCW = self.doc.GetElement(self.wallTypeCW)
                    if self.currentConfig["deflectionHeadType"] == 2:
                        wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-2"])
                    elif self.currentConfig["deflectionHeadType"] == 1:
                        wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-1"])

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

                    self.newWall = None

                    if str(hostElement.WallType.Kind) == "Basic":
                        self.Run_CheckSFWalls()
                        self.Run_CreateCurtainWall()
                        self.Run_ModifySFCurtainWalls()
                        self.Run_SetFinalSFParameters()
            print("STOREFRONT IS FINISHED RUNNING!")

    ##################
    ## QC SF SYSTEM ##
    ##################
    class PostSFErrorCheck:
        """
        THIS CLASS STRUCTURE IS OVERLY COMPLEX FOR JUST A CALL
        TO AN OUTSIDE MODULE BUT ITS HERE TO SERVE A PLACE HOLDER
        FOR A PRE ERROR CHECK/MODEL QC CLASS THAT WILL BE DEVELOPED
        """
        def __init__(self):
            pass
        def CheckErrors(self):
            print("...CHECKING ERRORS...")
            # WHERE IN THE F IS THIS???
            SF2_QC.SFCheckErrors().Run_SFCheckErrors()
            print("...DONE!")

    #####################
    ## SF PARENT CLASS ##
    #####################
    class GenerateSF(CreateNibWalls, CollectSFElements, 
                     ParseSFWalls_Rhino, BuildSFSystem, 
                     PostSFErrorCheck):
        """
        THE PURPOSE OF THE STOREFRONT TOOL IS TO CREATE CURTAIN
        WALL THAT IS GENERATED CORRECTLY DESPITE THE LOCATION OF THE DOOR.
        IT IS THE DOOR THAT IS PREVENTING THE BUILT IN TOOL FROM BEING ENOUGH.

        ALSO BUILT-IN TOOLS WILL NOT PARAMETICALLY DEAL WITH INTERSECTION CONDITIONS
        ON THEIR OWN (CORNERS, PERPENDICULAR, ETC...)

        IN EXISTING STOREFRONT AUTO EMBED IS OFF, HOW DOES IT WORK THEN?
        HOW CAN THE "AUTOMATICALLY EMBED" PARAMETER BE USED?

        ISSUES: THERE COULD BE 2 EC MODELS...LIKE 411 UNION...
                THIS IS A PROBLEM FOR "SF2_Utility.RevitLoadECDocument"

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
            self.mrTimer = SF2_Utility.Timer() # not used so far

            # class inheritance / polymorphism
            CreateNibWalls.__init__(self)
            CollectSFElements.__init__(self)
            ParseSFWalls_Rhino.__init__(self)
            BuildSFSystem.__init__(self) # DERIVED CLASS WITH ITS OWN INHERITANCES
            PostSFErrorCheck.__init__(self)

            # helper objects (collector)
            self.collector = FilteredElementCollector(self.doc)
            self.viewCollector = FilteredElementCollector(self.doc, self.currentView.Id)
            self.familyObj = SF2_Families.FamilyTools(self.doc)
        def Run_GenerateSF(self):
            """
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
            """
            # instantiate windows form
            SF_Form = SF2_GUI.storefront_options(self.doc)
            SF_Form.storefront_set_config()

            # set form output to derived parameter
            self.currentConfig = SF_Form.currentConfig # this is now used throughout this program

            # load families
            SF2_Families.FamilyTools(self.doc).Run_LoadFamilies(self.currentConfig)

            # create nib walls
            if SF_Form.userConfigs["createNibWall"] and str(self.currentView.ViewType) == "FloorPlan":
                self.Run_CreateNibWalls(SF_Form.userConfigs["nibWallLength"])
            else:
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Run the tool in floorplan view only!")
                pyrevit.script.exit()                

            # collect walls and sort stuff
            self.Run_StorefrontPrep()

            # build walls from collected elements - sets firing sequence for dependent classes
            self.Run_BuildSFSystem()

            # check for errors after everything has been built
            self.CheckErrors()

except:
    # print traceback in order to debug file
    print(traceback.format_exc()) 