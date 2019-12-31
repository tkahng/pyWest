"""
:tooltip:
Module for Storefront logic
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork

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
    import SF2_Utility
    import SF2_QC
    import SF2_Families
    
    ################################################################
    ## STOREFRONT ELEVATION - WHY? IDFK - NOT PART OF INHERITANCE ##
    ################################################################
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
    
    ############################
    ## SPLIT STOREFRONT WALLS ##
    ############################
    class SplitSFWalls:
        """
        SINCE THIS CLASS IS MOSTLY SELF CONTAINED, THE VARIABLES
        WITH THE SAME NAME HERE WILL NOT BE MADE .SELF CLASS
        INHERITANCE VARIABLES SO THE REST OF THE SCRIPT DOESN'T GET MESSED UP.
        THERE IS THE CHANCE TO CLEAN UP THE LOOP BY RECYCLING VARIABLES, BUT
        THE RHINO ENGINE WILL SOLVE THIS NEXT, NOT EXTENSIVELY FIXING THIS
        """
        def __init__(self):
            pass
        def storefront_split_wall(self, nibWallLength):
            """
            This has its own form...how do i merge the two?
            """
            standardSizes = [4.0, 3.0, 2.0, 1.0] #Glass sizes
            fixed_nib_wall_imperial = float(nibWallLength)/12
            fixed_nib_wall_metric = 5.90551/12
            leftoverTol = 0.35  #Nib wall length
        
            selectedSystem = self.currentConfig["currentSystem"]
            postWidth = self.currentConfig["postWidth"]
            oneByWidth = self.currentConfig["oneByWidth"]
        
            currentLevel = self.currentView.GenLevel
            levelName = currentLevel.Name
            
            
            
            # IT APPEARS THAT EVERYTHING HERE IS TO GENERATE A LIST OF WALL OPTIONS ##################################
            
            ## collect wall type information for a form to select which one to use.
            ## also select whether or not the split is fixed distance or optimized.
            #wallTypesDict = {}
            #splitTypes = SF2_Families.FamilyTools(self.doc).splitTypeOptions
        
            #selectedWallType = None
            #allWallTypes = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.WallType)
            #allWallTypes += SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_StackedWalls, Autodesk.Revit.DB.WallType)
            
            ## filter just 'Basic Wall - Partition-Gyp' walls
            #gypWalls = [i.Name for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall)]
            #print(gypWalls)
            
            #for wallTypeId in allWallTypes:
                #wallType = self.doc.GetElement(wallTypeId)
                #wallTypeFamilyName = None
                #wallTypeTypeName = None
                ##if self.version == "2016" or self.version == "2017":
                #if int(self.version) > 2015:
                    #wallTypeFamilyName = wallType.Parameter[BuiltInParameter.ALL_MODEL_FAMILY_NAME].AsString()
                    #wallTypeTypeName = wallType.Parameter[BuiltInParameter.ALL_MODEL_TYPE_NAME].AsString()
                #elif int(self.version) <= 2015:
                    #for p in wallType.Parameters:
                        #if p.Definition.Name == "Family Name":
                            #wallTypeFamilyName = p.AsString()
                        #if p.Definition.Name == "Type Name":
                            #wallTypeTypeName = p.AsString()
                            
                ## appending to dictionary here - wall Type as Key
                #wallTypesDict["{0} - {1}".format(wallTypeFamilyName, wallTypeTypeName)] = wallTypeId
                
            ##print(wallTypesDict)
            ## get default values if previously selected
            #if self.currentConfig["splitWallType"] and self.currentConfig["splitOffset"]:
                #if self.currentConfig["splitWallType"] in wallTypesDict:
                    #defaultValues = [self.currentConfig["splitWallType"], self.currentConfig["splitOffset"]]
                #else:
                    #defaultValues = [wallTypesDict.keys()[0], self.currentConfig["splitOffset"]]
            #else: 
                #pass
                ##defaultValues = [wallTypesDict.keys()[0], keys.keys()[0]]
                #defaultValues = [wallTypesDict.keys()[0], 6.0]
            
            #gypWall = "Basic Wall - Partition-Gyp"
            #self.currentConfig["splitWallType"] = gypWall
            
            #wallTypeFamilyName = "Basic Wall"
            #wallTypeTypeName = "Partition-Gyp"
            
            
            
            #print(defaultValues)
            #print(self.currentConfig["splitOffset"])
        
            ## get wall test
            #print(self.doc.GetElement("Basic Wall - Partition-Gyp"))
            
            #######################
            ## GUI TO BE REMOVED ##
            #######################
            #components = [Label('SPLIT OPTIONS'),
                          #Separator(),
                          #ComboBox("combobox1", wallTypesDict, default=defaultValues[0]),
                          #Label('NIB WALLTYPE'),
                          #ComboBox("combobox2", splitTypes, default=defaultValues[1]),
                          #Label('SPLIT METHOD'),
                          #Button('Go')]
        
            #form = FlexForm("Storefront Tools V3", components)
            #form.show()
        
            #if not form.values:
                #sys.exit()
            ##else:
            #selectedWallType = SF_Form.values["combobox1"]
            #selectedSplitOffset = float(SF_Form.values["combobox2"])
        
            
            
            ##########################################################################################################
            ##                             ##
            ## FORM SELECTION GOES HERE... ##
            ##                             ##
            #################################
            gypWall = "Basic Wall - Partition-Gyp"
            self.currentConfig["splitWallType"] = gypWall
            
            wallTypeFamilyName = "Basic Wall"
            wallTypeTypeName = "Partition-Gyp"            
            
            selectedWallType = gypWall
            selectedSplitOffset = 6.00
            
            
            ## user settings into a dict
            #config = {"splitWallType": wallTypesDict.keys()[wallTypesDict.values().index(selectedWallType)],
                      #"splitOffset" : splitTypes.keys()[splitTypes.values().index(selectedSplitOffset)]}
        
            ##save selected system
            #storefrontConfig.storefront_save_config(user_configs=config)            
            
            # get elements
            walls = SF2_Utility.GetElementsInView(BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, self.currentView.Id)
            walls = SF2_Utility.FilterElementsByLevel(self.doc, walls, currentLevel.Id)
            storefrontWalls = SF2_Utility.FilterElementsByName(self.doc, walls,["Storefront","Storefront"], invert=False)
            
            
            gypWalls = SF2_Utility.FilterElementsByName(self.doc, walls,["Basic Wall","Partition-Gyp"], invert=True)
            print("gypWall String {0}".format(gypWalls))
            selectedWallTypeId = gypWalls[0]
            selectedWallType = self.doc.GetElement(selectedWallTypeId).GetTypeId()
            print("selectedWallTypeId {0}".format(selectedWallTypeId))
            print("selectedWallType {0}".format(selectedWallType))
            
            intersectionPoints = SF2_Utility.RemoveDuplicatePoints(SF2_Utility.FindWallIntersections(walls))
            currentSelected = self.uidoc.Selection.GetElementIds()
            with rpw.db.Transaction("Create Nib") as tx: 
                for id in storefrontWalls:
                #for id in currentSelected:
                    print("storefront id in iterator {0}".format(id))
                    inst = self.doc.GetElement(id)
                    print("the instance is {0}".format(inst))
                    if inst.Category.Name == "Walls":
                        instName = None
                        topConstraint = None
                        unconnectedHeight = None
                        baseOffset = None
                        topOffset = None
                        botConstraint = currentLevel.Id
                        try:
                            instName = inst.Name.lower()
                        except:
                            for p in inst.Parameters:
                                if p.Definition.Name == "Name":
                                    instName = p.AsString().lower()
                        if "storefront" not in instName:
                            continue
                        else:
                            for p in inst.Parameters:
                                if p.Definition.Name == "Top Constraint":
                                    topConstraint = p.AsElementId()
                                if p.Definition.Name == "Unconnected Height":
                                    unconnectedHeight = p.AsDouble()
                                if p.Definition.Name == "Top Offset":
                                    topOffset = p.AsDouble()
        
                            #check to see which ends are naked
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
                            print("it got here")
                            #if only one end is touching other walls
                            if startOverlap == False or endOverlap == False:
                                nibWall = None
                                nibWalls = []
                                offset = 0
                                lengthAdjust = (0.5 * postWidth) + oneByWidth
                                length = instLine.Length - lengthAdjust
                                leftover = length%(standardSizes[0] + oneByWidth)
                                numPanels = math.floor(length / (standardSizes[0] + oneByWidth))
        
                                if selectedSplitOffset == "OPTIMIZED":
                                    #if optimized split
                                    if leftover > leftoverTol:
                                        lastPanelSize = 0
                                        for size in standardSizes[1:]:
                                            if leftover - leftoverTol >= (size + oneByWidth):
                                                lastPanelSize = standardSizes[standardSizes.index(size)]
                                                break
                                        offset = lengthAdjust + numPanels*standardSizes[0] + (numPanels)*oneByWidth + lastPanelSize + int(lastPanelSize > 0)*oneByWidth
                                    else:
                                        offset = lengthAdjust + (numPanels-1)*standardSizes[0] + standardSizes[1] + (numPanels)*oneByWidth
                                else:
                                    #if fixed distance split
                                    offset = instLine.Length - selectedSplitOffset  
        
                                if startOverlap or (startOverlap == endOverlap):
                                    newPoint = XYZ(((end.X-start.X)*(offset/(length + lengthAdjust)))+start.X,((end.Y-start.Y)*(offset/(length + lengthAdjust)))+start.Y, start.Z)
                                    inst.Location.Curve = Line.CreateBound(start, newPoint)
                                    nibWallLine = Line.CreateBound(newPoint,end)
        
                                    end = newPoint
        
                                    nibWalls.append(Wall.Create(self.doc, nibWallLine, currentLevel.Id, False))
                                    self.doc.Regenerate()
        
                                if endOverlap or (startOverlap == endOverlap):
                                    newPoint = XYZ(((start.X-end.X)*(offset/(length + lengthAdjust)))+end.X,((start.Y-end.Y)*(offset/(length + lengthAdjust)))+end.Y, end.Z)
                                    inst.Location.Curve = Line.CreateBound(newPoint, end)                  
        
                                    nibWallLine = Line.CreateBound(newPoint,start)
        
                                    start = newPoint
        
                                    nibWalls.append(Wall.Create(self.doc, nibWallLine, currentLevel.Id, False))
                                    self.doc.Regenerate()
                                print("nib walls: {0}".format(nibWalls))
                                if nibWalls:
                                    for nibWall in nibWalls:
                                        print(selectedWallType)
                                        nibWall.WallType = self.doc.GetElement(selectedWallType)
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
                                print("It finished but nothing happened")
                            else:
                                print("What the hell happened?")
                                continue        
    
    ##########################
    ## COLLECT MOSTLY WALLS ## ADD DEFAULT VIEWS TO RUN WITHOUT BEING IN PLAN VIEW
    ##########################
    class CollectWallsColumns:
        def __init__(self, currentViewOnly=True):
            # input parameter - for future functionality
            self.currentViewOnly = currentViewOnly

        ##########################
        ## COLLECT MOSTLY WALLS ##
        ##########################
        def CollectSFWalls(self):
            # level of current view
            self.selectedLevel = self.currentView.GenLevel.Id
            self.selectedLevelInst = self.doc.GetElement(self.selectedLevel)
            
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
    
    ########################################
    ## COLLECT / PREP SF WALLS - ORIGINAL ##
    ########################################
    class storefront_generate:
        def __init__(self):
            pass
        def CollectAllElementsInView(self):
            self.selectedLevel = self.currentView.GenLevel.Id # THIS RANDOMLY FAILS...WHY
            self.selectedLevelInst = self.doc.GetElement(self.selectedLevel)
    
            currentSelected = list(self.uidoc.Selection.GetElementIds())
            selectedStorefront = []
    
            allWalls = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True) # boolean is currentView only
            allColumns = SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance, currentView=True)
            allColumns += SF2_Utility.GetAllElements(self.doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance, currentView=True)
    
            self.interiorWalls = SF2_Utility.FilterElementsByName(self.doc, allWalls,["Storefront","Storefront"], True)
    
            if currentSelected:
                for i in currentSelected:
                    inst = self.doc.GetElement(i)
                    if inst.Category.Name == "Walls":
                        instName = None
                        try:
                            instName = inst.Name.lower()
                        except:
                            for p in inst.Parameters:
                                if p.Definition.Name == "Name":
                                    instName = p.AsString().lower()
                        if "storefront" in instName:
                            if "full" in instName:
                                self.storefrontFull.append(i)
                            elif "partial" in instName:
                                self.storefrontPartial.append(i)
            else:
    
                self.storefrontFull = SF2_Utility.FilterElementsByName(self.doc, allWalls,["Storefront","Full"], False)
                self.storefrontPartial = SF2_Utility.FilterElementsByName(self.doc, allWalls,["Storefront","Partial"], False)
    
            # this might be used to track each assembly - possibly for fabrication?
            # collect existing storefront curtain walls and check their Marks to ensure they incrememt. 
            # so that mark numbers can be consecutive?
            self.startingAssembyId = 0
            storefrontWallsInView = rpw.db.Collector(of_class='Wall', view=self.currentView, where=lambda x: str(x.WallType.Kind) == "Curtain")
            
            ## SPLIT HERE IN ORDER
            ## TO COLLECT WALLS ONLY ONCE
            
            tempList = []
            for storefrontInView in storefrontWallsInView:
                mark = storefrontInView.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
                if mark:
                    tempList.append(int(mark[mark.index("-")+1:]))
            if tempList:
                sortedList = sorted(tempList)
                self.startingAssembyId = sortedList[-1]
    
    
            tempList = []
            # makes sure no stacked walls are included.
            for wallId in self.interiorWalls:
                wall = self.doc.GetElement(wallId)
                if not wall.IsStackedWallMember:
                    tempList.append(wallId)
            self.interiorWalls = tempList
    
            #Sort lists by level
            self.storefrontFull = SF2_Utility.FilterElementsByLevel(self.doc, self.storefrontFull, self.selectedLevel)
            self.storefrontPartial = SF2_Utility.FilterElementsByLevel(self.doc, self.storefrontPartial, self.selectedLevel)
            self.interiorWalls = SF2_Utility.FilterElementsByLevel(self.doc, self.interiorWalls, self.selectedLevel)
            selectedColumns = SF2_Utility.FilterElementsByLevel(self.doc, allColumns, self.selectedLevel)
    
            if self.docEC:
                levelElevationEC = None 
                for p in self.selectedLevelInst.Parameters:
                    if p.Definition.Name == "Elevation":
                        levelElevationEC = p.AsDouble()
                self.selectedWallsEC = SF2_Utility.FilterElementsByLevel(self.docEC, self.allWallsEC, levelElevationEC)
                self.selectedColumnsEC = SF2_Utility.FilterElementsByLevel(self.docEC, self.allColumnsEC, levelElevationEC)
                self.wallsLinesEdgesEC = SF2_Utility.GetWallEdgeCurves(self.docEC, self.selectedWallsEC, self.ecTransform)
                self.columnsLinesEdgesEC = SF2_Utility.GetColumnEdgeCurves(self.docEC, self.selectedColumnsEC, self.ecTransform)
    
            self.interiorWallsLinesEdges = SF2_Utility.GetWallEdgeCurves(self.doc, self.interiorWalls, None)
            self.columnsLinesEdges = SF2_Utility.GetColumnEdgeCurves(self.doc, selectedColumns)
    
            levelElevation = self.selectedLevelInst.Elevation
        def Prep(self):
            #############################################
            #                  Prep                    #
            #############################################
            self.systemName = self.currentConfig["currentSystem"]
    
            self.storefrontPaneWidth = self.currentConfig["storefrontPaneWidth"]
            self.storefrontSpacingType = self.currentConfig["spacingType"]
    
            self.mullionDict = SF2_Utility.GetMullionTypeDict(self.doc)
            self.panelTypeDict = SF2_Utility.GetWindowTypeDict()
            self.doorDict = self.currentConfig["systemDoors"]
            wallTypeDict = SF2_Utility.GetWallTypeDict()
            self.wallDoorHostDict = SF2_Utility.GetDoorDictByWallHost()
    
            #Ensure walltypes are loaded
            if not "I-Storefront-"+ self.systemName in wallTypeDict.keys():
                Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Make sure you selected/loaded the correct partition system. Check your wall types.")
                sys.exit()
    
            #TODO: verify mullions in project, if not then run the load tool.
    
            #Profile widths - THIS HAS FAILED WHEN FAMILIES WEREN'T LOADED, BUT IT DIDN'T TRIGGER THAT THE FAMILIES WEREN'T LOADED
            self.systemPostWidth = self.doc.GetElement(self.mullionDict[self.systemName+"_Post"]).get_Parameter(BuiltInParameter.CUST_MULLION_THICK).AsDouble()
    
            systemDoorFrame = self.doc.GetElement(self.mullionDict[self.systemName+"_DoorFrame"])
            systemDoorFrameWidth = systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
            systemDoorFrameWidth += systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()
    
            systemOneBy = self.doc.GetElement(self.mullionDict[self.systemName+"_OneBy"])
            systemOneByWidth = systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
            systemOneByWidth += systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()
    
    
            self.wallTypeCW = wallTypeDict["I-Storefront-"+self.systemName]
    
            self.progressIndex = 0.0
        def WrapAndChain(self):
            #############################################
            #              Wrap & Chain                #
            #############################################
            """
                Takes walls that are inline and makes them a single
                wall element so that you dont get segmented walls that
                are supposed to be a single continuous elevation.
                """
            assemblyId = self.startingAssembyId
            self.storefrontElevations = []
            storefrontFullAndPartial = []
    
            for wallId in self.storefrontFull:
                storefrontFullAndPartial.append([wallId,"Full"])
            for wallId in self.storefrontPartial:
                storefrontFullAndPartial.append([wallId,"Partial"])
    
            #--------------Make SF Objects---------------#
            for item1 in storefrontFullAndPartial:
    
                wallId1 = item1[0]
                wallStorefrontType1 = item1[1]
    
                wall1 = self.doc.GetElement(wallId1)
                wall1LocationCurve = wall1.Location.Curve
    
                wallDoors = []
                wallHostIds = [wallId1]
    
                if wallId1 in self.wallDoorHostDict.keys():
                    wallDoors = self.wallDoorHostDict[wallId1]
    
    
                #--------------Chain Searching--------------#
    
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
                                    if dist < self.absoluteTol:
                                        angle = SF2_Utility.AngleThreePoints(point1b, point1a, point2b)
                                        #print angle
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
    
                #--------------Create SF Object--------------#
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
                #Doors
                if wallDoors:
                    sfe.Doors = wallDoors
                self.storefrontElevations.append(sfe)
        def Run_StorefrontPrep(self):
            self.CollectAllElementsInView()
            self.Prep()
            self.WrapAndChain()
    
    ##########################################
    ## BUILD WALL                           ##
    ## the following classes are depenents: ##
    ##     CheckModel()                     ##
    ##     CreateCurtainWalls()             ##
    ##     ModifyCurtainWalls()             ##
    ##     SetFinalParameters()             ##
    class BuildWall: #########################
        def __init__(self):
            # derived parameters
            self.gridIntersectionPostPoints = []
            self.baseConstraint = None
            self.newWall = None
            self.wtName = None
            self.storefrontType = None
            
        def Run_BuildWall(self):
            
            print("RUNNING...DO NOT CLOSE WINDOW...")

            with rpw.db.TransactionGroup("Convert Wall", assimilate=True) as tg:
                #Adjust any parameters to the walltype before creation if needed.
                with rpw.db.Transaction("Adjust CW Parameters") as tx:
                    
                    # this is coming from utilities module
                    SF2_Utility.SupressErrorsAndWarnings(tx)
                    wtCW = self.doc.GetElement(self.wallTypeCW)
                    if self.currentConfig["deflectionHeadType"] == 2:
                        wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-2"])
                    elif self.currentConfig["deflectionHeadType"] == 1:
                        wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-1"])
                
                # what data type is storefrontObject? - easy answer in C#
                for storefrontObject in self.storefrontElevations:
                    # convert iterator to class variable
                    self.storefrontObject = storefrontObject
                    #############################################
                    #                  Build                   #
                    #############################################
                    #pyrevit progress bar
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
                        self.Run_CheckModel()
                        self.Run_CreateCurtainWall()
                        self.Run_ModifyCurtainWalls()
                        self.Run_SetFinalParameters()
    
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
    
    ###########################
    ## CHECK MODEL FOR STUFF ##
    ###########################
    class CheckModel:
        def __init__(self):
            pass
        def InteriorWallEdges(self):
            #############################################
            #                  Checks                   #
            #############################################

            #------------Interior Wall Edges------------#

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
            #----------Interior Wall Midspans-----------#
            for intWallId in self.interiorWalls:
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
            #------------------EC Walls------------------#
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
            ####-------Storefront Intersections-------####

            self.locLine = self.storefrontObject.HostLine
            self.locLineStart = self.locLine.GetEndPoint(0)
            self.locLineEnd = self.locLine.GetEndPoint(1)
        def FindNeighbors(self):
            #---------------Find Neighbors---------------#
            #print self.storefrontObject.HostElementIds              
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

                        #Check if intersection is at the start point or end point or middle
                        if intersection.DistanceTo(self.locLineStart) < self.tol:
                            angle = SF2_Utility.AngleThreePoints(self.locLineEnd, intersection, point1)
                            self.storefrontObject.StartNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                        elif intersection.DistanceTo(self.locLineEnd) < self.tol:
                            angle = SF2_Utility.AngleThreePoints(self.locLineStart, intersection, point1)
                            self.storefrontObject.EndNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                        else:
                            #Interesection isnt ocurring at the ends.
                            self.gridIntersectionPostPoints.append(intersection)

                            #If the intersections for both lines are on the middles for eachother.
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
        def DetermineConditions(self):
            #-----------Determine Conditions-----------#

            ###------------Start Condition-----------###
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

                        #---Corner Test---#
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

                        #---Inline Test---#
                        elif abs(angle-180) < self.angleTol:
                            if neighbor[1] != self.storefrontType:
                                inlineTypes.append("Different")
                                inlineCount += 1 
                            elif neighbor[1] == self.storefrontType:
                                inlineTypes.append("Same")
                                #Placeholder just in case
                                pass

                        #---Angled Test---#
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

                    #---Compound Conditions---#
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
        def Run_CheckModel(self):
            self.InteriorWallEdges()
            self.InteriorWallMidspans()
            self.ECWalls()
            self.StorefrontIntersections()
            self.FindNeighbors()
            self.DetermineConditions()
    
    #########################
    ## CREATE CURTAIN WALL ##
    #########################
    class CreateCurtainWalls:
        def __init__(self):
            pass
        def Run_CreateCurtainWall(self):
            #--------------Curtain Wall-----------------#
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
    
    class ModifyCurtainWalls:
        def __init__(self):
            pass
        def ModifyLowerInfillPanels(self):
            #############################################
            #              Modifications                #
            #############################################
            #-----------Lower Infill Panels-------------#

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
            #---------------Special Horizontals---------------#
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
            #-----------Midspan Intersections (posts)----------#
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
            #-------------------Modify Ends-------------------#
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
            #-----------------Glazing Panel Types----------------#
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
            #-------------------Doors------------------#
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
                            print "ISSUE: Unable to recognize door - " + doorName

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

                        systemDetectionFactor = self.currentConfig["closeMullionDetectionFactor"]

                        detectionCheckDist0 = frameMullion0Width * systemDetectionFactor
                        detectionCheckDist1 = frameMullion1Width * systemDetectionFactor


                        self.doc.Regenerate()
                        newWall_grid = self.newWall.CurtainGrid

                        #Check to see if a mullion exists in the spot where one would be created.
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

                    #-----------------Empty Panel----------------#
                        self.doc.Regenerate()
                        panelToChangeId = SF2_Utility.RevitCurtainPanelsAtPoint(newWall_grid, doorLocationCenter, detectionTolerance=0.2)
                        if panelToChangeId:
                            panelToChange = self.doc.GetElement(panelToChangeId[0])
                            panelToChange.Pinned = False
                            panelToChange.ChangeTypeId(self.panelTypeDict[self.currentConfig["panelEmpty"]])

                    #-----------------Sill Delete----------------#
                        self.doc.Regenerate()

                        filterName = self.currentConfig["AUTO_MULLION_BORDER1_HORIZ"].split("_")[1]
                        doorSillMullions = SF2_Utility.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter=filterName)

                        for dsm in doorSillMullions:
                            dsm.Pinned = False
                            self.doc.Delete(dsm.Id)

                    #-------------Continuous Head Above Door--------------#
                        doorFrameContinuous = self.currentConfig["mullionContinuousVerticalAtDoorTop"]
                        if not doorFrameContinuous:
                            #filterName = self.currentConfig["AUTO_MULLION_BORDER2_HORIZ"].split("_")[1]

                            #Join head so its continuous
                            self.doc.Regenerate()
                            doorHeadMullions = SF2_Utility.GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter="Head")
                            for dhm in doorHeadMullions:
                                dhm.JoinMullion()
        def ModifyIntermediates(self):
            #-------------------Intermediates-------------------# 
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
            #---------------Special Sills---------------#
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
        def Run_ModifyCurtainWalls(self):
            self.ModifyLowerInfillPanels()
            self.ModifySpecialHorizontals()
            self.ModifyMidspanIntersections()
            self.ModifyEnds()
            self.ModifyGlazingPanelTypes()
            self.ModifyDoors()
            self.ModifyIntermediates()
            self.SpecialSills()
    
    ##########################
    ## SET FINAL PARAMETERS ##
    ##########################   
    class SetFinalParameters:
        def __init__(self):
            pass
        def Run_SetFinalParameters(self):
            # Set heights, for whatever reason differing heights before adding gridlines is an issue so set this last.
            with rpw.db.Transaction("Create Curtain Wall") as tx:
                SF2_Utility.SupressErrorsAndWarnings(tx)
                newWallSillHeight = self.storefrontObject.SillHeight
                newWallHeadHeight = self.storefrontObject.HeadHeight - self.storefrontObject.SillHeight
                self.newWall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(newWallSillHeight)
                self.newWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(newWallHeadHeight)
                self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(self.storefrontObject.SuperType)
                self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(str(self.selectedLevel) + "-"+ str(self.storefrontObject.AssemblyID))
        
    ##################
    ## QC SF SYSTEM ##
    ##################
    class PostErrorCheck:
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
            SF2_QC.storefront_check_errors().Run_storefront_check_errors()
            print("...DONE!")
    
    #####################
    ## SF PARENT CLASS ##
    #####################
    class GenerateSF(SplitSFWalls, storefront_generate, 
                     BuildWall, CheckModel, ParseSFWalls_Rhino, 
                     CreateCurtainWalls, ModifyCurtainWalls,
                     SetFinalParameters, PostErrorCheck):
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
            # input parameters - comes from SF2_GUI
            self.currentConfig = None
            
            # current view being lost workaround
            
            # class inheritance / polymorphism
            SplitSFWalls.__init__(self)
            storefront_generate.__init__(self)
            BuildWall.__init__(self)
            CheckModel.__init__(self)
            ParseSFWalls_Rhino.__init__(self)
            CreateCurtainWalls.__init__(self)
            ModifyCurtainWalls.__init__(self)
            SetFinalParameters.__init__(self)
            PostErrorCheck.__init__(self)
            
            # global parameters
            self.user = str(System.Environment.UserName)
    
            self.tol = 0.001
    
            self.doc = __revit__.ActiveUIDocument.Document
            self.app = __revit__.Application
            self.version = __revit__.Application.VersionNumber.ToString()
            self.uidoc = __revit__.ActiveUIDocument
            self.currentView = __revit__.ActiveUIDocument.ActiveView
    
            self.storefrontFull = []
            self.storefrontPartial = []
            self.selectedLevels = []
            self.storefrontFullLines = []
            self.storefrontPartialLines = []
            self.interiorWallsLines = []
            self.interiorWallsLinesEdges = []
            self.selectedDoors = []
            self.selectedRooms = []
            self.selectedFloors = []
    
            self.ecModelInst = None
            self.docEC = None
            self.ecTransform = None
    
            self.allWallsEC = []
            self.allLevelsEC = []
            self.allColumnsEC = []
            self.wallsLinesEdgesEC = []
            self.selectedLevelsEC = []
            self.selectedWallsEC = []
            self.selectedColumnsEC = []
    
            self.distTol = 0.5 
            self.angleTol = 0.01
            self.absoluteTol = 0.001
    
            self.minPanelWidth = 1.0
    
            self.docLoaded = SF2_Utility.RevitLoadECDocument(self.doc)
            self.docEC = self.docLoaded[0]
            self.ecTransform = self.docLoaded[1]
    
            self.mrTimer = SF2_Utility.Timer()
            
            # CollectAllElementsInView() outputs
            self.startingAssembyId = None
            self.interiorWalls = None
            self.columnsLinesEdges = None
            self.columnsLinesEdgesEC = None
            self.selectedLevel = None
            
            # Prep() outputs
            self.wallTypeCW = None
            self.wallDoorHostDict = None
            self.storefrontConfig = None # this is gui object and eventual user selections
            self.systemName = None
            self.progressIndex = None
            self.mullionDict = None
            self.doorDict = None
            self.panelTypeDict = None
            self.storefrontSpacingType = None
            self.storefrontPaneWidth = None
            self.systemPostWidth = None
            
            # WrapAndChain() outputs
            self.storefrontElevations = []
            
            # parameters for build curtain wall sequence
            self.storefrontObject = None
            self.locLine = None
            self.locLineEnd = None
            self.locLineStart = None
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
            #SF2_Families.FamilyTools(self.doc).Run_LoadFamilies(self.currentConfig)
            
            # save current view because it gets lost when families load...
            #self.selectedLevel = self.currentView.GenLevel.Id # THIS RANDOMLY FAILS...WHY
            #self.selectedLevelInst = self.doc.GetElement(self.selectedLevel)            
            
            # create nib walls
            if SF_Form.userConfigs["splitWalls"]:
                self.storefront_split_wall(SF_Form.userConfigs["splitWallLength"])
            #if str(currentView.ViewType) == "FloorPlan" :
                #storefront_split_wall()
            #else:
                #Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Run the tool in floorplan view only!")
                #pyrevit.script.exit()            
            
            # collect walls and sort stuff
            #self.Run_StorefrontPrep()
            
            # build walls from collected elements - sets firing sequence for dependent classes
            #self.Run_BuildWall()
            
            # check for errors after everything has been built
            #self.CheckErrors()

except:
    # print traceback in order to debug file
    print(traceback.format_exc()) 