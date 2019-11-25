"""
:tooltip:
Module for storefront logic
TESTED REVIT API: 2015, 2016, 2017
:tooltip:

Copyright (c) 2016-2019 WeWork

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

ISSUES:
OLD SF2_FAMILIES REFERENCED HAS A DICTIONARY THATS MISSING IN THE OLD ONE
GUI DOES NOT SAVE PREVIOUS SETTINGS
I THINK I AM LOADING FAMILIES TWICE...
"""

__author__ = 'WeWork Buildings Systems'
__version__ = "2.XXX"

import traceback
import os
import sys

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    import clr
    import re # for level number string parsing
    import logging
    import System
    import math

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

    sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
    import _csv as csv
    import json

    user = str(System.Environment.UserName)

    rpwLib = r"VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\0 Lib\revitpythonwrapper-master" # common lib folder
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 6, rpwLib))
    import rpw

    # import Rhinocommon API - C# library
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
    clr.AddReference(r"Rhino3dmIO.dll")
    import Rhino as rh
    
    import SF2_Families
    import SF2_Report
    import SF2_GUI 
    import SF2_Utility

    #from pyrevit import script
    
    ##############
    ## NOT SURE ##
    ##############
    class StorefrontElevation:
        def __init__(self, _hostElementIds, _line, _superType, _id, _sillHeight, _headHeight, _systemName):	
            self.AssemblyID = _id
            self.CWElementId = None
            self.EndCondition = None
            self.EndNeighbors = []
            self.EndOffset = 0
            self.EndAngledOffset = 0
            self.HostElementIds = _hostElementIds
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
    
    ##############################
    ## COLLECT ORIGINAL VERSION ##
    ##############################
    class CollectWallsDeprecated:
        def __init__(self):
            # variables that I have added bc of introduction of OOP structure
            self.objLevel = None
            self.allWalls = [] # this can be avoided, simply only collect the storefront walls
            self.allColumns = []
            self.interiorWalls = []
            self.objLevelInst = None # introduced in self.CollectWallsColumns()

            self.storefrontFull = []
            self.storefrontPartial = []


            self.allWallsEC = [] # this variable is never filled, what is it used for??? - MAYBE COLLECTION OBJECT ASKS FOR CONTAINER LIST???
            self.allColumnsEC = [] # this variable is never fille, what is it used for??? - MAYBE COLLECTION OBJECT ASKS FOR CONTAINER LIST???
            self.wallsLinesEdgesEC = []
            self.selectedWallsEC = []
            self.selectedColumnsEC = []


            self.distTol = 0.5 
            self.angleTol = 0.01
            self.absoluteTol = 0.001

            self.minPanelWidth = 1.0

            self.mrTimer = SF2_Utility.Timer()

        def CollectSFwalls(self):
            """
            purpose: This method collects all walls, columns, and levels in document and EC document,
                     but mostly just parses those walls classified as storefront full and partial. 
                     Collected storefronts come from either user selection or a version of the
                     filtered element collector.

            returns: None - effective return; appends to self.storefrontFull, self.storefrontPartial,
                                                         self.allColumns, self.objLevel,
                                                         self.objLevelInst

            notes: columns and levels are collected here, they don't have variables assigned to them 
                   so if they are needed, they won't be accessible without them since the code was
                   largely procedural
            """

            # collect main level associated with view
            self.objLevel = self.currentView.GenLevel.Id # must be in a plan view!
            self.objLevelInst = self.doc.GetElement(self.objLevel)

            currentSelected = [i for i in self.uidoc.Selection.GetElementIds()]
            selectedStorefront = []


            # collect all elements of a specific type - .OST_method, not object type
            self.allWalls = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
            self.allColumns = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance, currentView=True) # used eventually in build curtain wall
            self.allColumns += SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance, currentView=True) # used eventually in build curtain wall

            # all walls in document are collected then filtered by "Storefront" - check documentation here
            #self.objLevel = SF2_Utility.FilterElementsByName(self.doc, self.allWalls,["Storefront","Storefront"], True)
            currentSelected = SF2_Utility.FilterElementsByName(self.doc, self.allWalls,["Storefront","Storefront"], True)
            
            # user selects items in model option
            # self.storefrontFull = []
            # self.storefrontPartial = []
            if currentSelected:
                for id in currentSelected:
                    inst = self.doc.GetElement(id)
                    if inst.Category.Name == "Walls":
                        instName = None
                        try:
                            instName = inst.Name.lower() # the .lower() is used to remove case sensitivity in strings
                        except:
                            for p in inst.Parameters:
                                if p.Definition.Name == "Name":
                                    instName = p.AsString().lower() # lower what the fuck
                        if "storefront" in instName:
                            if "full" in instName:
                                self.storefrontFull.append(id)
                            elif "partial" in instName:
                                self.storefrontPartial.append(id)

            # objects selected through code
            else: 
                self.storefrontFull = SF2_Utility.FilterElementsByName(self.doc, self.allWalls,["Storefront","Full"], False)
                self.storefrontPartial = SF2_Utility.FilterElementsByName(self.doc, self.allWalls,["Storefront","Partial"], False)
            if self.printTest == True:
                print([self.storefrontFull, self.storefrontPartial])
            return([self.storefrontFull, self.storefrontPartial])

        def FilterSFwalls(self, storefrontWalls):
            # filter lists by level
            self.storefrontFull = SF2_Utility.FilterElementsByLevel(self.doc, self.storefrontFull, self.objLevel)
            self.storefrontPartial = SF2_Utility.FilterElementsByLevel(self.doc, self.storefrontPartial, self.objLevel)
            self.interiorWalls = SF2_Utility.FilterElementsByLevel(self.doc, self.interiorWalls, self.objLevel)
            self.selectedColumns = SF2_Utility.FilterElementsByLevel(self.doc, self.allColumns, self.objLevel)

        def Run_CollectWallsDeprecated(self):
            SFwalls_all = self.CollectSFwalls()
            SFwalls_byLevel = self.FilterSFwalls(SFwalls_all)
            return(SFwalls_byLevel)
    
    #############
    #e COLLECT ## ADD DEFAULT VIEWS FROM WHICH TO RUN STOREFRONT, SO YOU DON'T HAVE TO BE IN A SPECIFIC VIEW
    #############
    class CollectWallsColumns:
        def __init__(self, currentViewOnly=True):
            # input parameter 
            self.currentViewOnly = currentViewOnly
            # if on 3d and current view only it will get all storefronts
            # if current view is 3d or someother thing then do all storefronts
            #try:
                #self.objLevel = self.currentView.LookupParameter("Associated Level").Id # need level associated with this ID
                #print("Level Id: {0}".format(self.objLevel))
            #except:
                ## also make this force to get all ids of levels in project that are not container, or maybe wait until walls have been filtered or something
                #raise ValueError("You must be in a plan view for self.objLevel variable to work!")
            
            # CONSIDER HAVING DEFAULT VIEWS TO USE, ONE PER LEVEL

            # class outputs
            self.wallList = [] # all walls
            self.nestedWallList = [] # walls grouped by level  
            self.storefrontFull = [] # only full SF walls
            self.storefrontPartial = [] # only partial SF walls         
            
            self.levelList = []
            self.levelNumList = []
            self.allColumns = []

            # standard tolerances
            self.distTol = 0.5 
            self.angleTol = 0.01
            self.absoluteTol = 0.001
            self.minPanelWidth = 1.0            

        ##########################
        ## COLLECT MOSTLY WALLS ##
        ##########################
        def CollectSFWalls(self):
            # walls collected by user selection -> returns wall object
            selectionIdList = self.uidoc.Selection.GetElementIds()
            if selectionIdList: wallList = [self.doc.GetElement(id) for id in selectionIdList if self.doc.GetElement(id).Name in SF2_Families.SF_Options().SFFamilyNames().keys()]

            # walls collected by code -> returns wall object
            if not selectionIdList and self.currentViewOnly == True:
                # must be in plan view, how do i manage this???
                self.wallList = [i for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall) if i.Name in SF2_Families.SF_Options().SFFamilyNames().keys()] # Autodesk.Revit.DB.Wall - defines <type 'Wall'>
            if not selectionIdList and self.currentViewOnly == False:
                self.wallList = [i for i in FilteredElementCollector(self.doc).OfClass(Wall) if i.Name in SF2_Families.SF_Options().SFFamilyNames().keys()]

            if self.wallList: return()
            else: raise Esception("There are no walls in the model")

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
            
        ########################
        ## SORT WALL BY LEVEL ##
        ########################
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

    #####################
    ## NO FUCKING IDEA ##
    #####################
    class SomeClass:
        def __init__(self):
            
            # derived variables
            self.objLevel = self.currentView.GenLevel.Id
            self.startingAssembyId = 0 # collect existing storefront curtain walls and check their Marks to ensure they incrememt       
            
            # class outputs
            self.interiorWallsLinesEdges = []
            
        def SomeBullshitIdontUnderstand(self):
            storefrontWallsInView = rpw.db.Collector(of_class='Wall', view=currentView, where=lambda x: str(x.WallType.Kind) == "Curtain")
            print(storefrontWallsInView)

            tempList = []
            for i in storefrontWallsInView:
                # WHAT THE FUCK IS THIS???
                mark = i.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
                if mark:
                    tempList.append(int(mark[mark.index("-")+1:]))
            if tempList:
                sortedList = sorted(tempList)
                self.startingAssembyId = sortedList[-1]

            tempList = []
            
            #Makes sure no stacked walls are included.
            for j in self.objLevel:
                wall = self.doc.GetElement(j)
                if not wall.IsStackedWallMember:
                    tempList.append(j)
            self.objLevel = tempList

            return([self.startingAssembyId, self.objLevel])

        def SomeECShitIdontUnderstand(self):
            # stuff from the EC model...
            if self.docEC:
                levelElevationEC = None 
                for p in self.objLevelInst.Parameters:
                    if p.Definition.Name == "Elevation":
                        levelElevationEC = p.AsDouble()

                # collect elements from EC model with the file's doc object
                self.selectedWallsEC = SF2_Utility.FilterElementsByLevel(self.docEC, self.allWallsEC, levelElevationEC)
                self.selectedColumnsEC = SF2_Utility.FilterElementsByLevel(self.docEC, self.allColumnsEC, levelElevationEC)
                self.wallsLinesEdgesEC = SF2_Utility.GetWallEdgeCurves(self.docEC, self.app, self.selectedWallsEC, self.ecTransform)
                self.columnsLinesEdgesEC = SF2_Utility.GetColumnEdgeCurves(self.docEC, self.selectedColumnsEC, self.ecTransform)

            self.interiorWallsLinesEdges = SF2_Utility.GetWallEdgeCurves(self.doc, self.app, self.objLevel, None)
            columnsLinesEdges = SF2_Utility.GetColumnEdgeCurves(self.doc, self.selectedColumns)


            levelElevation = self.objLevelInst.Elevation

            return(levelElevation)
        
        def Run_SomeClass(self):
            # run the first method
            self.SomeBullshitIdontUnderstand()
            
            # run the second method
            #self.SomeECShitIdontUnderstand()

    ##########
    ## SORT ##
    ##########
    class WallCLsOrganize:
        def __init__(self):
            
            # derived variables
            self.systemPostWidth = None
            self.wallTypeCW = None

        def AlvarosImprovedAlgorithm(self):
            pass

        def PrepElements_SHOULD_BE_MOVED_TO_RUN(self):
            #Ensure walltypes are loaded
            if not "I-Storefront-"+ systemName in wallTypeDict.keys():
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Make sure you selected/loaded the correct partition system. Check your wall types.")
                sys.exit()

            #Profile widths
            self.systemPostWidth = self.doc.GetElement(mullionDict[systemName+"_Post"]).get_Parameter(BuiltInParameter.CUST_MULLION_THICK).AsDouble()

            systemDoorFrame = self.doc.GetElement(mullionDict[systemName+"_DoorFrame"])
            systemDoorFrameWidth = systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
            systemDoorFrameWidth += systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

            systemOneBy = self.doc.GetElement(mullionDict[systemName+"_OneBy"])
            systemOneByWidth = systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
            systemOneByWidth += systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()


            self.wallTypeCW = wallTypeDict["I-Storefront-"+systemName]

            progressIndex = 0.0

        def JoinElements(self, assemblyID):
            """
            Takes walls that are inline and makes them a single
            wall element so that you dont get segmented walls that
            are supposed to be a single continuous elevation.

            AT THIS POINT IN THE CODE, STOREFRONT FULL AND PARTIAL ARE 
            CONSUMED BY A NEW LIST...IT IS NOT WHAT GETS CARRIED
            OVER TO THE BUILD METHOD......

            """
            assemblyId = self.startingAssembyId
            storefrontElevations = [] # this is what is fed into Build method
            storefrontFullAndPartial = []

            for i in self.storefrontFull:
                storefrontFullAndPartial.append([i,"Full"])
            for j in self.storefrontPartial:
                storefrontFullAndPartial.append([j,"Partial"])

            # MAKE SF OBJECTS
            for item1 in storefrontFullAndPartial:

                wallId1 = item1[0]
                wallStorefrontType1 = item1[1]

                wall1 = self.doc.GetElement(wallId1)
                wall1LocationCurve = wall1.Location.Curve

                wallDoors = []
                wallHostIds = [wallId1]

                if wallId1 in wallDoorHostDict.keys():
                    wallDoors = wallDoorHostDict[wallId1]


                # CHAIN SEARCHING
                #Find neighbors and chain them if they are in-line.
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
                                    if dist < absoluteTol:
                                        angle = AngleThreePoints(point1b, point1a, point2b)
                                        #print angle
                                        if abs(angle-180) < absoluteTol:
                                            wallHostIds += [wallId2]
                                            storefrontFullAndPartial.remove(item2)
                                            if wallId2 in wallDoorHostDict.keys():
                                                wallDoors += wallDoorHostDict[wallId2]
                                            wall1LocationCurve = Line.CreateBound(point1b, point2b)
                                            foundNeighbor = True
                                            break
                        if foundNeighbor:
                            break
                    if not foundNeighbor:
                        searchingForChain = False

                # CREATE SF OBJECT
                assemblyId += 1

                if wallStorefrontType1 == "Full":
                    sillH = SF_Form.currentConfig["fullSillHeight"]
                elif wallStorefrontType1 == "Partial":
                    if SF_Form.currentConfig["hasLowerInfill"]:
                        sillH = SF_Form.currentConfig["fullSillHeight"]
                    else:
                        sillH = SF_Form.currentConfig["partialSillHeight"]

                headH = SF_Form.currentConfig["headHeight"]
                sfe = StorefrontElevation(wallHostIds, wall1LocationCurve, wallStorefrontType1, assemblyId, sillH, headH, systemName)
                
                #Doors
                if wallDoors:
                    sfe.Doors = wallDoors
                storefrontElevations.append(sfe)

        def Run_WallCLsOrganize(self):
            pass

    #####################
    ## CREATE GEOMETRY ##
    #####################
    class BuildCurtainWall:
        def __init__(self):
            pass

            # this method is too long, needs to be broken up
        def BuildElements(self):
                # this is just a print statement on pyRevit's console; uses its api
                # to embelish it with a progress bar. it is not a 'real' form
            print("RUNNING...DO NOT CLOSE WINDOW...")

            with rpw.db.TransactionGroup("Convert Wall", assimilate=True) as tg:

                #Adjust any parameters to the walltype before creation if needed.
                with rpw.db.Transaction("Adjust CW Parameters") as tx:
                    # storefront_utils.SupressErrorsAndWarnings(transaction)
                    SupressErrorsAndWarnings(tx)


                    wtCW = self.doc.GetElement(self.wallTypeCW)
                    if SF_Form.currentConfig["deflectionHeadType"] == 2:
                        wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[systemName+"_DeflectionHead-2"])
                    elif SF_Form.currentConfig["deflectionHeadType"] == 1:
                        wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[systemName+"_DeflectionHead-1"])

                # PYREVIT PROGRESS BAR IS USED HERE
                # LOOP IS TOO MASSIVE HERE 
                for storefrontObject in storefrontElevations: 
                    #pyrevit progress bar
                    progressIndex += 1

                    output = script.get_output()
                    output.update_progress(progressIndex, len(storefrontElevations))

                    hostElement = self.doc.GetElement(storefrontObject.HostElementIds[0])
                    storefrontType = storefrontObject.SuperType

                    baseConstraint = hostElement.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()

                    locLine = storefrontObject.HostLine
                    locLineStart = locLine.GetEndPoint(0)
                    locLineEnd = locLine.GetEndPoint(1)

                    gridIntersectionPostPoints = []

                    wallHostId = storefrontObject.HostElementIds[0]
                    wtName = self.doc.GetElement(wallHostId).Name

                    newWall = None

                    if str(hostElement.WallType.Kind) == "Basic": 

                        #############################################
                        #                  Checks                   #
                        #############################################

                        #------------Interior Walls Edges------------#

                        locLine = storefrontObject.HostLine
                        locLineStart = locLine.GetEndPoint(0)
                        locLineEnd = locLine.GetEndPoint(1)

                        for intWallLine in self.interiorWallsLinesEdges:
                            intersection = RevitCurveCurveIntersection(locLine,intWallLine)

                            if intersection:
                                distToEnd = intersection.DistanceTo(locLineEnd) 
                                distToStart = intersection.DistanceTo(locLineStart) 

                                #If intersection is at the ends
                                if distToEnd < distTol:
                                    storefrontObject.EndCondition = "OnGyp"
                                    # If intersection is not at the surface of the edges of interior walls
                                    if distToEnd > absoluteTol:
                                        storefrontObject.Line = Line.CreateBound(locLineStart, intersection)

                                elif distToStart < distTol:
                                    storefrontObject.StartCondition = "OnGyp"
                                    if distToStart > absoluteTol:
                                        storefrontObject.Line = Line.CreateBound(intersection, locLineEnd)

                        #----------Interior Walls Midspans-----------#
                        for intWallId in self.objLevel:
                            intWall = self.doc.GetElement(intWallId)
                            intWallLine = intWall.Location.Curve
                            intersection = RevitCurveCurveIntersection(locLine,intWallLine)
                            if intersection:
                                distToEnd = intersection.DistanceTo(locLineEnd) 
                                distToStart = intersection.DistanceTo(locLineStart) 
                                #If intersection is at the ends
                                if distToEnd > distTol and distToStart > distTol:
                                    gridIntersectionPostPoints.append(intersection)




                        #------------------EC Walls------------------#

                        locLine = storefrontObject.HostLine
                        locLineStart = locLine.GetEndPoint(0)
                        locLineEnd = locLine.GetEndPoint(1)
                        obstructionEdges = columnsLinesEdges
                        if self.docEC:
                            obstructionEdges += columnsLinesEdgesEC
                            obstructionEdges += self.wallsLinesEdgesEC
                        if obstructionEdges:
                            for obstructionLine in obstructionEdges:
                                obstLineElevation = obstructionLine.GetEndPoint(0).Z
                                locLineStart = XYZ(locLineStart.X, locLineStart.Y, obstLineElevation)
                                locLineEnd = XYZ(locLineEnd.X, locLineEnd.Y, obstLineElevation)
                                locLineFlat = Line.CreateBound(locLineStart, locLineEnd)
                                intersection = RevitCurveCurveIntersection(locLineFlat,obstructionLine)
                                if intersection:
                                    #ERROR: Hit Existing Condition
                                    if intersection.DistanceTo(locLineEnd) < distTol:
                                        storefrontObject.EndCondition = "OnObstruction"
                                    elif intersection.DistanceTo(locLineStart) < distTol:
                                        storefrontObject.StartCondition = "OnObstruction"


                        ####-------Storefront Intersections-------####

                        locLine = storefrontObject.HostLine
                        locLineStart = locLine.GetEndPoint(0)
                        locLineEnd = locLine.GetEndPoint(1)


                        #---------------Find Neighbors---------------#
                        #print storefrontObject.HostElementIds              
                        for neighbor in storefrontElevations:

                            if neighbor != storefrontObject:
                                neighborLocLine = neighbor.HostLine
                                neighborLocLineStart = neighborLocLine.GetEndPoint(0)
                                neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
                                intersection = RevitCurveCurveIntersection(locLine,neighborLocLine)

                                if intersection:
                                    point1 = None
                                    intersectionTypeOnNeighbor = None

                                    #Check where the intersection is occuring on the neighbor
                                    if intersection.DistanceTo(neighborLocLineStart) < distTol:
                                        intersectionTypeOnNeighbor = "Start"
                                        point1 = neighborLocLineEnd
                                    elif intersection.DistanceTo(neighborLocLineEnd) < distTol:
                                        intersectionTypeOnNeighbor = "End"
                                        point1 = neighborLocLineStart
                                    else:
                                        intersectionTypeOnNeighbor = "Middle"
                                        point1 = neighborLocLineEnd

                                    #Check if intersection is at the start point or end point or middle
                                    if intersection.DistanceTo(locLineStart) < tol:
                                        angle = AngleThreePoints(locLineEnd, intersection, point1)
                                        storefrontObject.StartNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                                    elif intersection.DistanceTo(locLineEnd) < tol:
                                        angle = AngleThreePoints(locLineStart, intersection, point1)
                                        storefrontObject.EndNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                                    else:
                                        #Interesection isnt ocurring at the ends.
                                        gridIntersectionPostPoints.append(intersection)

                                        #If the intersections for both lines are on the middles for eachother.
                                        if intersectionTypeOnNeighbor == "Middle":

                                            #Split the intersecting neighbor into two segments so the walls dont overlap
                                            neighborLocLineStart = neighborLocLine.GetEndPoint(0)
                                            neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
                                            neighbor.Line = Line.CreateBound(intersection, neighborLocLineStart)
                                            neighbor.HostLine = Line.CreateBound(intersection, neighborLocLineStart)

                                            #Create another neighbor thats split
                                            newNeighborIndex = len(storefrontElevations)+1
                                            newNeighborHostElementIds = neighbor.HostElementIds
                                            newNeighborSillHeight = neighbor.SillHeight
                                            newNeighborHeadHeight = neighbor.HeadHeight
                                            splitNeighborLine = Line.CreateBound(intersection, neighborLocLineEnd)
                                            splitNeighbor = StorefrontElevation(newNeighborHostElementIds, splitNeighborLine, neighbor.SuperType, newNeighborIndex, newNeighborSillHeight, newNeighborHeadHeight, systemName)
                                            storefrontElevations.append(splitNeighbor)

                                            #Make sure that each new segment has the correct doors on each one
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

                        #-----------Determine Conditions-----------#

                        ###------------Start Condition-----------###
                        locLine = storefrontObject.HostLine
                        locLineStart = locLine.GetEndPoint(0)
                        locLineEnd = locLine.GetEndPoint(1)

                        startAndEndNeighbors = [storefrontObject.StartNeighbors, storefrontObject.EndNeighbors]

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

                                    #---Corner Test---#
                                    if abs(angle-90) < angleTol:
                                        if neighbor[1] != storefrontType:
                                            if intersectionType == "Middle":
                                                conditionToSet = "OnStorefront"
                                                cornerTypes.append("Different")
                                                cornerCount += 2
                                            elif intersectionType == "Start" or intersectionType == "End":
                                                cornerTypes.append("Different")
                                                cornerCount += 1

                                        elif neighbor[1] == storefrontType:
                                            # If the storefront is connected to the middle of another storefront
                                            # that is the of the same type, then it should join
                                            if intersectionType == "Middle":
                                                conditionToSet = "JoinStorefront"
                                                cornerTypes.append("Same")
                                                cornerCount += 2

                                            elif intersectionType == "Start" or intersectionType == "End":
                                                cornerTypes.append("Same")
                                                cornerCount += 1

                                    #---Inline Test---#
                                    elif abs(angle-180) < angleTol:
                                        if neighbor[1] != storefrontType:
                                            inlineTypes.append("Different")
                                            inlineCount += 1 
                                        elif neighbor[1] == storefrontType:
                                            inlineTypes.append("Same")
                                            #Placeholder just in case
                                            pass

                                    #---Angled Test---#
                                    elif abs(round(neighbor[2],1) % 90) > angleTol:
                                        reverse = 0
                                        if locLineStart.X > locLineEnd.X: 
                                            reverse = 180
                                        angleRadians = (neighbor[2] * (2 * math.pi)) / 360
                                        conditionAngleOffset = (0.5 * self.systemPostWidth) / math.tan((angleRadians) * 0.5)
                                        conditionToSet = "Angled"
                                        if SF_Form.currentConfig["isFramed"]:
                                            if i == 0:
                                                vect = RevitTransVector(locLineEnd, locLineStart, magnitude=conditionAngleOffset)
                                                locLineStart = locLineStart.Add(vect)
                                                storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                            elif i == 1:
                                                vect = RevitTransVector(locLineStart, locLineEnd, magnitude=conditionAngleOffset)
                                                locLineEnd = locLineEnd.Add(vect)
                                                storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)
                                        break

                                #---Compound Conditions---#
                                if cornerCount == 0 and inlineCount == 1:
                                    if "Same" in inlineTypes:
                                        pass
                                    elif "Different" in inlineTypes:
                                        if storefrontType == "Full":
                                            conditionToSet = "ForcePost"
                                        elif storefrontType == "Partial":
                                            conditionToSet = "OnStorefront"

                                elif cornerCount == 1 and inlineCount == 0:
                                    if "Same" in cornerTypes:
                                        conditionToSet = None
                                    elif "Different" in cornerTypes:
                                        if storefrontType == "Full":
                                            conditionToSet = None
                                        elif storefrontType == "Partial":
                                            conditionToSet = "OnStorefront"
                                    else: 
                                        pass

                                elif cornerCount == 1 and inlineCount == 1:
                                    if "Same" in cornerTypes:
                                        conditionToSet = "JoinStorefront"
                                        if i == 0:
                                            vect = RevitTransVector(locLineEnd, locLineStart, magnitude=self.systemPostWidth/2)
                                            locLineStart = locLineStart.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                        elif i == 1:
                                            vect = RevitTransVector(locLineStart, locLineEnd, magnitude=self.systemPostWidth/2)
                                            locLineEnd = locLineEnd.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

                                    elif "Different" in cornerTypes:
                                        conditionToSet = "OnStorefront"
                                    else: 
                                        pass

                                elif cornerCount == 2 and inlineCount == 0:
                                    if not "Different"  in  cornerTypes:
                                        conditionToSet = "JoinStorefront"
                                        if i == 0:
                                            vect = RevitTransVector(locLineEnd, locLineStart, magnitude=self.systemPostWidth/2)
                                            locLineStart = locLineStart.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                        elif i == 1:
                                            vect = RevitTransVector(locLineStart, locLineEnd, magnitude=self.systemPostWidth/2)
                                            locLineEnd = locLineEnd.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

                                    elif "Same" in  cornerTypes and "Different" in cornerTypes:
                                        conditionToSet = "ForcePostAtTBone"
                                        if i == 0:
                                            vect = RevitTransVector(locLineStart, locLineEnd, magnitude=self.systemPostWidth/2)
                                            locLineStart = locLineStart.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

                                        elif i == 1:
                                            vect = RevitTransVector(locLineEnd, locLineStart, magnitude=self.systemPostWidth/2)
                                            locLineEnd = locLineEnd.Add(vect)
                                            storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

                                elif cornerCount == 2 and inlineCount == 1:
                                    if "Same" in  cornerTypes and "Different" in cornerTypes and "Different" in inlineTypes:
                                        pass

                            #Logic gate to set contidions to the right ends either start of end.
                            if i == 0  and neighborSet:
                                storefrontObject.StartCondition = conditionToSet

                                if conditionAngleOffset:
                                    storefrontObject.StartAngledOffset = conditionAngleOffset

                            elif i == 1 and neighborSet:
                                storefrontObject.EndCondition = conditionToSet

                                if conditionAngleOffset:
                                    storefrontObject.EndAngledOffset = conditionAngleOffset

        def CreateCurtainWall(self):
            #--------------Curtain Wall-----------------#
            with rpw.db.Transaction("Create Curtain Wall") as tx:
                SupressErrorsAndWarnings(tx)
                newWallHeadHeight = storefrontObject.HeadHeight 
                newWallLine = storefrontObject.Line
                newWall = Wall.Create(self.doc, newWallLine, self.wallTypeCW, baseConstraint, newWallHeadHeight, 0, False, False)
                newWall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).Set(0)

                #Set new CW Id to storefrontObject object 
                storefrontObject.CWElementId = newWall.Id

                self.doc.Regenerate()

                if SF_Form.currentConfig["isFramed"]:
                    if storefrontObject.StartCondition == "Angled":
                        WallUtils.DisallowWallJoinAtEnd(newWall, 0)
                    if storefrontObject.EndCondition == "Angled":
                        WallUtils.DisallowWallJoinAtEnd(newWall, 1)

                conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

                #print storefrontObject.SuperType
                #print "start - " + str(storefrontObject.StartCondition)
                #print "end   - " + str(storefrontObject.EndCondition)

                for i in range(len(conditionsList)):
                    condition = conditionsList[i]
                    newWall_grid = newWall.CurtainGrid
                    newWallPoint = newWall.Location.Curve.GetEndPoint(i)
                    mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5)

                    if mullionList:
                        for mul in mullionList:
                            mul.Pinned = False

                            if condition == "OnGyp":
                                mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

                            elif condition == "OnObstruction":
                                mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

                            elif condition == "OnStorefront":
                                mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

                            elif condition == "JoinStorefront":
                                self.doc.Delete(mul.Id)

                            elif condition == "ForcePost":
                                mul.ChangeTypeId(mullionDict[systemName + "_Post"])

                            elif condition == "ForcePostAtTBone":
                                mul.ChangeTypeId(mullionDict[systemName + "_Post"])

                            elif condition == "Angled":
                                if SF_Form.currentConfig["isFramed"]:
                                    mul.ChangeTypeId(mullionDict[systemName + "_OneBy"])
                                else: 
                                    self.doc.Delete(mul.Id)
            return(True)

        def Run_BuildCurtainWall(self):
            pass

    #####################
    ## MODIFY GEOMETRY ##
    #####################
    class ModifyCurtainWall:
        def __init__(self):
            pass

        def ModifyLowerInfillPanels(self):
            #-----------Lower Infill Panels-------------#

            newWall_grid = newWall.CurtainGrid

            #Create lower infill panel and sill
            if SF_Form.currentConfig["hasLowerInfill"]:

                newWallMidPoint = newWall.Location.Curve.Evaluate(0.5, True)
                newWall_grid = newWall.CurtainGrid
                if storefrontObject.SuperType == "Partial":
                    with rpw.db.Transaction("Create Lower Infill Panels") as tx:
                        SupressErrorsAndWarnings(tx)
                        try:
                            gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + SF_Form.currentConfig["partialSillHeight"] )
                            grid0 = newWall_grid.AddGridLine(True, gridPt, False)
                        except:
                            pass

                        # Create Solid Lower Panels
                        self.doc.Regenerate()
                        newWall_grid = newWall.CurtainGrid
                        uGridIds = newWall_grid.GetVGridLineIds()
                        newWallLocationCurve = newWall.Location.Curve
                        verticalGridPoints = []

                        for uGridId in uGridIds:
                            uGrid = self.doc.GetElement(uGridId)
                            uGridOrigin = uGrid.FullCurve.Origin
                            verticalGridPoints.append(XYZ(uGridOrigin.X, uGridOrigin.Y, newWallMidPoint.Z))
                        splitCurves = RevitSplitLineAtPoints(newWallLocationCurve, verticalGridPoints)

                        for sCurve in splitCurves:
                            sCurveMidpoint = sCurve.Evaluate(0.5, True)
                            panelIds = RevitCurtainPanelsAtPoint(newWall_grid, sCurveMidpoint, detectionTolerance=0.1)
                            panelElevationTupleList = []
                            for panelId in panelIds:
                                panel = self.doc.GetElement(panelId)
                                panelElevationTupleList.append((panel,float(panel.Transform.Origin.Z)))

                            panelElevationTupleList = sorted(panelElevationTupleList, key=lambda x: x[1])

                            #Gets lowest panel and change to solid
                            try:
                                panelToChange = panelElevationTupleList[0][0]
                                panelToChange.Pinned = False
                                panelToChange.ChangeTypeId(panelTypeDict[SF_Form.currentConfig["panelLowerInfill"]])
                            except:
                                pass
            return(True)

        def ModifySpecialHorizontals(self):
            #---------------Special Horizontals---------------#
            specialHorizontals = SF_Form.currentConfig["specialHorizontalMullions"]
            if specialHorizontals:
                for key, value in specialHorizontals.items():
                    if key in wtName:
                        newWallMidPoint = newWall.Location.Curve.Evaluate(0.5, True)
                        newWall_grid = newWall.CurtainGrid
                        with rpw.db.Transaction("Create Special Horizontal") as tx:
                            SupressErrorsAndWarnings(tx)
                            try:
                                gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + value[0])
                                grid0 = newWall_grid.AddGridLine(True, gridPt, False)
                            except:
                                pass
            return(True)

        def ModifyMidspanIntersections_Post(self):
            #-----------Midspan Intersections (posts)----------#

            newWall_grid = newWall.CurtainGrid
            if gridIntersectionPostPoints:
                with rpw.db.Transaction("Create Intersection Grids") as tx:
                    SupressErrorsAndWarnings(tx)
                    for gridIntersectionPoint in gridIntersectionPostPoints:
                        try:
                            gridInt = newWall_grid.AddGridLine(False, gridIntersectionPoint, False)
                            mullionIntList = GetVerticalMullionsAtPoint(newWall_grid, gridIntersectionPoint, detectionTolerance=0.001)
                            if mullionIntList:
                                for mullion3 in mullionIntList:
                                    mullion3.Pinned = False
                                    mullion3.ChangeTypeId(mullionDict[SF_Form.currentConfig["midspanIntersectionMullion"]])
                        except:
                            pass
            return(True)

        def ModifyEnds(self):
            #-------------------Modify Ends-------------------#

            with rpw.db.Transaction("Modify Ends") as tx:
                SupressErrorsAndWarnings(tx)
                #Disallow as needed:


                if SF_Form.currentConfig["isFramed"]:
                    if storefrontObject.StartCondition == "Angled":
                        WallUtils.DisallowWallJoinAtEnd(newWall, 0)
                    if storefrontObject.EndCondition == "Angled":
                        WallUtils.DisallowWallJoinAtEnd(newWall, 1)

                self.doc.Regenerate()

                conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

                for i in range(len(conditionsList)):
                    condition = conditionsList[i]
                    newWall_grid = newWall.CurtainGrid
                    newWallPoint = newWall.Location.Curve.GetEndPoint(i)
                    mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5, searchOnlySelf=True)

                    if mullionList:
                        for mul in mullionList:
                            mul.Pinned = False

                            if condition == "OnGyp":
                                mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

                            elif condition == "OnObstruction":
                                mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

                            elif condition == "OnStorefront":
                                mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

                            elif condition == "JoinStorefront":
                                self.doc.Delete(mul.Id)

                            elif condition == "ForcePost":
                                mul.ChangeTypeId(mullionDict[systemName + "_Post"])

                            elif condition == "ForcePostAtTBone":
                                mul.ChangeTypeId(mullionDict[systemName + "_Post"])

                            elif condition == "Angled":
                                if SF_Form.currentConfig["isFramed"]:
                                    mul.ChangeTypeId(mullionDict[systemName + "_OneBy"])
                                else: 
                                    self.doc.Delete(mul.Id)
            return(True)

        def ModifyGlazingPanel(self):

            #-----------------Glazing Panel Types----------------#

            changeToPanel = None

            if "Demising" in wtName:
                changeToPanel = SF_Form.currentConfig["panelGlazedCenter"]
            elif "Offset" in wtName:
                changeToPanel = SF_Form.currentConfig["panelGlazedOffset"]
            elif "Double" in wtName:
                changeToPanel = SF_Form.currentConfig["panelGlazedDouble"]
            else:
                pass

            if changeToPanel:
                with rpw.db.Transaction("Change Glazing Types") as tx:
                    SupressErrorsAndWarnings(tx)
                    self.doc.Regenerate()
                    panels = newWall_grid.GetPanelIds()
                    for panelToChangeId in panels:
                        panelToChange = self.doc.GetElement(panelToChangeId)
                        panelToChange.Pinned = False
                        panelToChange.ChangeTypeId(panelTypeDict[changeToPanel])
            return(True)

            # this method is too long, needs to be broken up
        def ModifyDoors(self):
            #-------------------Doors------------------#

            if storefrontObject.Doors:
                newWallStartPoint = newWall.Location.Curve.GetEndPoint(0)
                newWallEndPoint = newWall.Location.Curve.GetEndPoint(1)
                doorsOnWall = storefrontObject.Doors

                with rpw.db.Transaction("Create Door Grids 0") as tx:
                    SupressErrorsAndWarnings(tx)

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
                        if doorDict.get(doorName):
                            doorDetails = doorDict[doorName]
                            doorHand = doorDetails[0]
                            doorWidth = doorDetails[1]
                            doorType = doorDetails[2]

                            frameMullion0 = mullionDict[systemName + doorDetails[3]]
                            frameMullion1 = mullionDict[systemName + doorDetails[4]]
                            extraAdjustment0 = doorDetails[5]
                            extraAdjustment1 = doorDetails[6]

                        else: 
                            #Defaults if no door is found
                            frameMullion0 = mullionDict[systemName + "_DoorFrame"]
                            frameMullion1 = mullionDict[systemName + "_DoorFrame"]

                            #Fine adjustments for mullion position
                            extraAdjustment0 = 0
                            extraAdjustment1 = 0
                            print("ISSUE: Unable to recognize door - {0}".format(doorName))


                        #Get offset widths for door frame mullions
                        fm0 = self.doc.GetElement(frameMullion0)
                        frameMullion0Width = fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
                        frameMullion0Width += fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

                        fm1 = self.doc.GetElement(frameMullion1)
                        frameMullion1Width = fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
                        frameMullion1Width += fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

                        #Accounting for mullion CUST_MULLION_THICKnesses 
                        extra0 = (frameMullion0Width * 0.5) + extraAdjustment0
                        extra1 = (frameMullion1Width * 0.5) + extraAdjustment1

                        #Vectors to move location point
                        vect0 = doorHandOrientation.Multiply(((doorWidth / 2) + extra0))
                        vect1 = doorHandOrientation.Multiply(((doorWidth / 2) + extra1) * -1)

                        #Door end points
                        door_end0 = doorLocationCenter.Add(vect0)
                        door_end1 = doorLocationCenter.Add(vect1)


                        #Detection tolerance for nearby mullions based on system
                        #required because of varying mullion sizes

                        systemDetectionFactor = SF_Form.currentConfig["closeMullionDetectionFactor"]

                        detectionCheckDist0 = frameMullion0Width * systemDetectionFactor
                        detectionCheckDist1 = frameMullion1Width * systemDetectionFactor


                        self.doc.Regenerate()
                        newWall_grid = newWall.CurtainGrid

                        #Check to see if a mullion exists in the spot where one would be created.
                        checkMullion0 = GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=detectionCheckDist0)
                        if not checkMullion0:
                            try:
                                grid0 = newWall_grid.AddGridLine(False, door_end0, False)
                            except:
                                pass

                            mullion0List = GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=0.001)
                            if mullion0List:
                                for mullion0 in mullion0List:
                                    mullion0.Pinned = False
                                    mullion0.Lock = False
                                    mullion0.ChangeTypeId(frameMullion0)

                        self.doc.Regenerate()
                        #Check to see if a mullion exists in the spot where one would be created.
                        checkMullion1 = GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=detectionCheckDist1)
                        if not checkMullion1:
                            try:
                                grid1 = newWall_grid.AddGridLine(False, door_end1, False)
                            except:
                                pass

                            mullion1List = GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=0.001)
                            if mullion1List:
                                for mullion1 in mullion1List:
                                    mullion1.Pinned = False
                                    mullion1.Lock = False
                                    mullion1.ChangeTypeId(frameMullion1)

                    #-----------------Empty Panel----------------#
                        self.doc.Regenerate()
                        panelToChangeId = RevitCurtainPanelsAtPoint(newWall_grid, doorLocationCenter, detectionTolerance=0.2)
                        if panelToChangeId:
                            panelToChange = self.doc.GetElement(panelToChangeId[0])
                            panelToChange.Pinned = False
                            panelToChange.ChangeTypeId(panelTypeDict[SF_Form.currentConfig["panelEmpty"]])

                    #-----------------Sill Delete----------------#
                        self.doc.Regenerate()

                        filterName = SF_Form.currentConfig["AUTO_MULLION_BORDER1_HORIZ"].split("_")[1]
                        doorSillMullions = SF2_Utility.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter=filterName)

                        for dsm in doorSillMullions:
                            dsm.Pinned = False
                            self.doc.Delete(dsm.Id)

                    #-------------Continuous Head Above Door--------------#

                        doorFrameContinuous = SF_Form.currentConfig["mullionContinuousVerticalAtDoorTop"]

                        if not doorFrameContinuous:

                            #filterName = SF_Form.currentConfig["AUTO_MULLION_BORDER2_HORIZ"].split("_")[1]

                            #Join head so its continuous
                            self.doc.Regenerate()
                            doorHeadMullions = SF2_Utility.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter="Head")
                            for dhm in doorHeadMullions:
                                dhm.JoinMullion()

            #-------------------Intermediates-------------------# 

            newWall_grid = newWall.CurtainGrid
            panels = newWall_grid.GetPanelIds()

            intermediateMullionWidth = 0
            if SF_Form.currentConfig["isFramed"]:

                #Select the right intermediate mullion in the project based
                #on which system is being used. 

                if "demising" in wtName.lower():
                    mulName = SF_Form.currentConfig["AUTO_MULLION_INTERIOR_VERT"]
                elif "offset" in wtName.lower():
                    mulName = SF_Form.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"]
                elif "double" in wtName.lower():
                    mulName = SF_Form.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"]
                else:
                    mulName = SF_Form.currentConfig["AUTO_MULLION_INTERIOR_VERT"]

                intermediateMullion = self.doc.GetElement(mullionDict[mulName])

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

                if "glazed" in (panel.Name + panel.Symbol.Family.Name).lower() and panelWidth > minPanelWidth:
                    newGridPoints = []
                    if storefrontSpacingType == 1:
                        newGridPoints = RevitDividePanelFixed(panel, storefrontPaneWidth, intermediateWidth=intermediateMullionWidth)
                    elif storefrontSpacingType == 0:
                        numberPanes = math.ceil(panelWidth/storefrontPaneWidth)
                        if numberPanes > 1:
                            newGridPoints = RevitDividePanelEquidistant(panel, numberPanes, intermediateWidth=intermediateMullionWidth)

                    if newGridPoints:
                        with rpw.db.Transaction("Create intermediate grid lines") as tx:
                            SupressErrorsAndWarnings(tx)
                            for gridpt in newGridPoints:
                                try:
                                    grid0 = newWall_grid.AddGridLine(False, gridpt, False)
                                    mullions0List = GetVerticalMullionsAtPoint(newWall_grid, grid0.FullCurve.Origin, detectionTolerance=0.001)
                                    for mullion0 in mullions0List:
                                        mullion0.Pinned = False
                                        if SF_Form.currentConfig["isFramed"]:
                                            mullion0.ChangeTypeId(intermediateMullion.Id)

                                            #Intermediates die into the head if mullion is "Broken"
                                            if not SF_Form.currentConfig["mullionContinuousVerticalIntermediateTop"]:
                                                mullion0.BreakMullion()
                                        else:
                                            #Delete mullion in the case that the system type is butt joined.
                                            self.doc.Delete(mullion0.Id)
                                except:
                                    pass
            return(True)

        def ModifySpecialSills(self):
            #---------------Special Sills---------------#

            newWall_grid = newWall.CurtainGrid

            updatedSill = None

            currentSill = SF_Form.currentConfig["AUTO_MULLION_BORDER1_HORIZ"]
            replacementSills = SF_Form.currentConfig["specialSillConditions"]

            if replacementSills:
                for key,value in replacementSills.items():
                    if key.lower() in wtName.lower():
                        updatedSill = mullionDict[value]

            if updatedSill:
                panels = newWall_grid.GetPanelIds()
                with rpw.db.Transaction("Update Sills") as tx:
                    SupressErrorsAndWarnings(tx) 
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
            return(True)

        def FinalParamSetters(self):
            # Set heights, for whatever reason differing heights before adding gridlines is an issue so set this last.
            with rpw.db.Transaction("Create Curtain Wall") as tx:
                SupressErrorsAndWarnings(tx)
                newWallSillHeight = storefrontObject.SillHeight
                newWallHeadHeight = storefrontObject.HeadHeight - storefrontObject.SillHeight
                newWall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(newWallSillHeight)
                newWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(newWallHeadHeight)
                newWall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(storefrontObject.SuperType)
                newWall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(str(self.objLevel) + "-"+ str(storefrontObject.AssemblyID))
            return(None)

        def Run_ModifyCurtainWall(self):
            pass


    ##################
    ## PARENT CLASS ##
    ##################
    class ParentClass(CollectWallsColumns, SomeClass, WallCLsOrganize, BuildCurtainWall, ModifyCurtainWall):
        """
        STOREFRONT 2.0
                            + SFCenterlines
                            + SFCurtainWall

        YOUNGEST CHILD----> + ParentClass(class inheritance dictated here)

        OOP NOTES:
            Namespace(file name)-->class-->properties(information about object)-->
            -->methods(actions that object performs)-->operations(math performed on object)

            object.method = property
            object.method() = action / constructor


            ENCAPSULATION
                PROPERTY IS DATA
                METHOD ACTS ON DATA

            REMEMBER: CLASS OBJECTS ARE EITHER CREATED OR MODIFIED
        """
        def __init__(self, printTest=False):
            # class inheritance / polymorphism
            CollectWallsColumns.__init__(self, currentViewOnly=False)
            #SomeClass.__init__(self)
            WallCLsOrganize.__init__(self)
            BuildCurtainWall.__init__(self)
            ModifyCurtainWall.__init__(self)
            
            # input parameters
            self.printTest = printTest

            # global parameters
            self.tol = 0.001
            self.app = __revit__.Application
            self.version = self.app.VersionNumber.ToString()
            self.uidoc = __revit__.ActiveUIDocument
            self.doc = __revit__.ActiveUIDocument.Document
            self.currentView = self.uidoc.ActiveView     

            # derived parameters
            self.docEC, self.ecTransform = SF2_Utility.RevitLoadECDocument(self.doc)

        def Run_SF2_Engine(self):
            # instantiate windows form
            SF_Form = SF2_GUI.Form(self.doc)
            SF_Form.Run_Form(printTest=True)
            
            # output from form
            formSelections = SF_Form.userSelections
            
            # load families - addSomething might need to receive guiSelection
            SF2_Families.ParentClass().Run_SF2_Families(addSomething=None)
            
            # PRE ERROR CHECK
            #SF2_Report.SFCheckModel().Run_SFvetModel(self.wallCLs)         

            # COLLECT SF WALLS
            #self.Run_CollectWalls()
            
            # RUN THAT WEIRD CLASS
            #self.Run_SomeClass()
            
            # CODE IN OPEN TRANSACTION
            #t = Transaction(self.doc, 'Generating Storefront Walls in Revit')
            #t.Start()
            #t.Commit()       

            # SECOND GUI FORM RUNS HERE

            # PARSE & SORT SF WALLS
            #self.Run_WallCLsOrganize(walls)

            # BUILD INITIAL SF GEO
            #self.Run_BuildCurtainWall()

            # MODIFY SF GEO
            #self.Run_ModifyCurtainWall()

            # POST ERROR CHECK - to be deprecated
            #print("...CHECKING ERRORS...")
            #SF2_Analysis.ErrorCheckingTools().SF_PostErrorCheck() # in overflow for now
            #print("...DONE!")

            # WRITE JSON REVIT -> CATIA
            
            # CREATE REPORT - save as json file

    ###############
    ## TEST MAIN ##
    ###############
    def TestMain():
        # this is automated or interactive
        ParentClass().Run_SF2_Engine()

    if __name__ == "__main__":
        TestMain()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())    