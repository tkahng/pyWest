class BuildWall2:
    def __init__(self):
        # originall from the run in this class
        self.gridIntersectionPostPoints = []
        self.baseConstraint = None
        self.newWall = None
        self.wtName = None
        self.storefrontType = None

        # outputs from checker
    def Checker(self, storefrontObject):
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
                if distToEnd < self.distTol:
                    storefrontObject.EndCondition = "OnGyp"
                    # If intersection is not at the surface of the edges of interior walls
                    if distToEnd > self.absoluteTol:
                        storefrontObject.Line = Line.CreateBound(locLineStart, intersection)

                elif distToStart < self.distTol:
                    storefrontObject.StartCondition = "OnGyp"
                    if distToStart > self.absoluteTol:
                        storefrontObject.Line = Line.CreateBound(intersection, locLineEnd)

        #----------Interior Walls Midspans-----------#
        for intWallId in self.interiorWalls:
            intWall = self.doc.GetElement(intWallId)
            intWallLine = intWall.Location.Curve
            intersection = RevitCurveCurveIntersection(locLine,intWallLine)
            if intersection:
                distToEnd = intersection.DistanceTo(locLineEnd) 
                distToStart = intersection.DistanceTo(locLineStart) 
                #If intersection is at the ends
                if distToEnd > self.distTol and distToStart > self.distTol:
                    self.gridIntersectionPostPoints.append(intersection)




        #------------------EC Walls------------------#

        locLine = storefrontObject.HostLine
        locLineStart = locLine.GetEndPoint(0)
        locLineEnd = locLine.GetEndPoint(1)
        obstructionEdges = self.columnsLinesEdges
        if self.docEC:
            obstructionEdges += self.columnsLinesEdgesEC
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
                    if intersection.DistanceTo(locLineEnd) < self.distTol:
                        storefrontObject.EndCondition = "OnObstruction"
                    elif intersection.DistanceTo(locLineStart) < self.distTol:
                        storefrontObject.StartCondition = "OnObstruction"


        ####-------Storefront Intersections-------####

        locLine = storefrontObject.HostLine
        locLineStart = locLine.GetEndPoint(0)
        locLineEnd = locLine.GetEndPoint(1)


        #---------------Find Neighbors---------------#
        #print storefrontObject.HostElementIds              
        for neighbor in self.storefrontElevations:

            if neighbor != storefrontObject:
                neighborLocLine = neighbor.HostLine
                neighborLocLineStart = neighborLocLine.GetEndPoint(0)
                neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
                intersection = RevitCurveCurveIntersection(locLine,neighborLocLine)

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
                    if intersection.DistanceTo(locLineStart) < self.tol:
                        angle = AngleThreePoints(locLineEnd, intersection, point1)
                        storefrontObject.StartNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

                    elif intersection.DistanceTo(locLineEnd) < self.tol:
                        angle = AngleThreePoints(locLineStart, intersection, point1)
                        storefrontObject.EndNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

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
                        if locLineStart.X > locLineEnd.X: 
                            reverse = 180
                        angleRadians = (neighbor[2] * (2 * math.pi)) / 360
                        conditionAngleOffset = (0.5 * self.systemPostWidth) / math.tan((angleRadians) * 0.5)
                        conditionToSet = "Angled"
                        if self.storefrontConfig.currentConfig["isFramed"]:
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

    def Creation(self, storefrontObject):
        #############################################
        #                 Creation                  #
        #############################################

        #--------------Curtain Wall-----------------#
        with rpw.db.Transaction("Create Curtain Wall") as tx:
            SupressErrorsAndWarnings(tx)
            newWallHeadHeight = storefrontObject.HeadHeight 
            newWallLine = storefrontObject.Line
            self.newWall = Wall.Create(self.doc, newWallLine, self.wallTypeCW, self.baseConstraint, newWallHeadHeight, 0, False, False)
            self.newWall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).Set(0)

            #Set new CW Id to storefrontObject object 
            storefrontObject.CWElementId = self.newWall.Id

            self.doc.Regenerate()

            if self.storefrontConfig.currentConfig["isFramed"]:
                if storefrontObject.StartCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 0)
                if storefrontObject.EndCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 1)

            conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

            for i in range(len(conditionsList)):
                condition = conditionsList[i]
                newWall_grid = self.newWall.CurtainGrid
                newWallPoint = self.newWall.Location.Curve.GetEndPoint(i)
                mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5)

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
                            if self.storefrontConfig.currentConfig["isFramed"]:
                                mul.ChangeTypeId(self.mullionDict[self.systemName + "_OneBy"])
                            else: 
                                self.doc.Delete(mul.Id)
    def ModifyLowerInfillPanels(self, storefrontObject):
        #############################################
        #              Modifications                #
        #############################################
        #-----------Lower Infill Panels-------------#

        newWall_grid = self.newWall.CurtainGrid

        #Create lower infill panel and sill
        if self.storefrontConfig.currentConfig["hasLowerInfill"]:

            newWallMidPoint = self.newWall.Location.Curve.Evaluate(0.5, True)
            newWall_grid = self.newWall.CurtainGrid
            if storefrontObject.SuperType == "Partial":
                with rpw.db.Transaction("Create Lower Infill Panels") as tx:
                    SupressErrorsAndWarnings(tx)
                    try:
                        gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + self.storefrontConfig.currentConfig["partialSillHeight"] )
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
                            panelToChange.ChangeTypeId(self.panelTypeDict[self.storefrontConfig.currentConfig["panelLowerInfill"]])
                        except:
                            pass
    def ModifySpecialHorizontals(self, storefrontObject):
        #---------------Special Horizontals---------------#
        specialHorizontals = self.storefrontConfig.currentConfig["specialHorizontalMullions"]
        if specialHorizontals:
            for key, value in specialHorizontals.items():
                if key in self.wtName:
                    newWallMidPoint = self.newWall.Location.Curve.Evaluate(0.5, True)
                    newWall_grid = self.newWall.CurtainGrid
                    with rpw.db.Transaction("Create Special Horizontal") as tx:
                        SupressErrorsAndWarnings(tx)
                        try:
                            gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + value[0])
                            grid0 = newWall_grid.AddGridLine(True, gridPt, False)
                        except:
                            pass
    def ModifyMidspanIntersectionPosts(self, storefrontObject):
        #-----------Midspan Intersections (posts)----------#
        newWall_grid = self.newWall.CurtainGrid
        if self.gridIntersectionPostPoints:
            with rpw.db.Transaction("Create Intersection Grids") as tx:
                SupressErrorsAndWarnings(tx)
                for gridIntersectionPoint in self.gridIntersectionPostPoints:
                    try:
                        gridInt = newWall_grid.AddGridLine(False, gridIntersectionPoint, False)
                        mullionIntList = GetVerticalMullionsAtPoint(newWall_grid, gridIntersectionPoint, detectionTolerance=0.001)
                        if mullionIntList:
                            for mullion3 in mullionIntList:
                                mullion3.Pinned = False
                                mullion3.ChangeTypeId(self.mullionDict[self.storefrontConfig.currentConfig["midspanIntersectionMullion"]])
                    except:
                        pass

    def ModifyEnds(self, storefrontObject):
        #-------------------Modify Ends-------------------#
        with rpw.db.Transaction("Modify Ends") as tx:
            SupressErrorsAndWarnings(tx)
            #Disallow as needed:

            if self.storefrontConfig.currentConfig["isFramed"]:
                if storefrontObject.StartCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 0)
                if storefrontObject.EndCondition == "Angled":
                    WallUtils.DisallowWallJoinAtEnd(self.newWall, 1)

            self.doc.Regenerate()

            conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

            for i in range(len(conditionsList)):
                condition = conditionsList[i]
                newWall_grid = self.newWall.CurtainGrid
                newWallPoint = self.newWall.Location.Curve.GetEndPoint(i)
                mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5, searchOnlySelf=True)

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
                            if self.storefrontConfig.currentConfig["isFramed"]:
                                mul.ChangeTypeId(self.mullionDict[self.systemName + "_OneBy"])
                            else: 
                                self.doc.Delete(mul.Id)
    def ModifyGlazingPanelTypes(self, storefrontObject):
        #-----------------Glazing Panel Types----------------#
        changeToPanel = None

        if "Demising" in self.wtName:
            changeToPanel = self.storefrontConfig.currentConfig["panelGlazedCenter"]
        elif "Offset" in self.wtName:
            changeToPanel = self.storefrontConfig.currentConfig["panelGlazedOffset"]
        elif "Double" in self.wtName:
            changeToPanel = self.storefrontConfig.currentConfig["panelGlazedDouble"]
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
                    panelToChange.ChangeTypeId(self.panelTypeDict[changeToPanel])
    def ModifyDoors(self, storefrontObject):
        #-------------------Doors------------------#
        if storefrontObject.Doors:
            newWallStartPoint = self.newWall.Location.Curve.GetEndPoint(0)
            newWallEndPoint = self.newWall.Location.Curve.GetEndPoint(1)
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

                    systemDetectionFactor = self.storefrontConfig.currentConfig["closeMullionDetectionFactor"]

                    detectionCheckDist0 = frameMullion0Width * systemDetectionFactor
                    detectionCheckDist1 = frameMullion1Width * systemDetectionFactor


                    self.doc.Regenerate()
                    newWall_grid = self.newWall.CurtainGrid

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
                        panelToChange.ChangeTypeId(self.panelTypeDict[self.storefrontConfig.currentConfig["panelEmpty"]])
                #-----------------Sill Delete----------------#
                    self.doc.Regenerate()

                    filterName = self.storefrontConfig.currentConfig["AUTO_MULLION_BORDER1_HORIZ"].split("_")[1]
                    doorSillMullions = GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter=filterName)

                    for dsm in doorSillMullions:
                        dsm.Pinned = False
                        self.doc.Delete(dsm.Id)
                #-------------Continuous Head Above Door--------------#
                    doorFrameContinuous = self.storefrontConfig.currentConfig["mullionContinuousVerticalAtDoorTop"]
                    if not doorFrameContinuous:
                        #filterName = self.storefrontConfig.currentConfig["AUTO_MULLION_BORDER2_HORIZ"].split("_")[1]

                        #Join head so its continuous
                        self.doc.Regenerate()
                        doorHeadMullions = GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter="Head")
                        for dhm in doorHeadMullions:
                            dhm.JoinMullion()
        #-------------------Intermediates-------------------# 
        newWall_grid = self.newWall.CurtainGrid
        panels = newWall_grid.GetPanelIds()

        intermediateMullionWidth = 0
        if self.storefrontConfig.currentConfig["isFramed"]:

            #Select the right intermediate mullion in the project based
            #on which system is being used. 

            if "demising" in self.wtName.lower():
                mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT"]
            elif "offset" in self.wtName.lower():
                mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"]
            elif "double" in self.wtName.lower():
                mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"]
            else:
                mulName = self.storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT"]

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
                                    if self.storefrontConfig.currentConfig["isFramed"]:
                                        mullion0.ChangeTypeId(intermediateMullion.Id)

                                        #Intermediates die into the head if mullion is "Broken"
                                        if not self.storefrontConfig.currentConfig["mullionContinuousVerticalIntermediateTop"]:
                                            mullion0.BreakMullion()
                                    else:
                                        #Delete mullion in the case that the system type is butt joined.
                                        self.doc.Delete(mullion0.Id)
                            except:
                                pass

        #---------------Special Sills---------------#
        newWall_grid = self.newWall.CurtainGrid

        updatedSill = None

        currentSill = self.storefrontConfig.currentConfig["AUTO_MULLION_BORDER1_HORIZ"]
        replacementSills = self.storefrontConfig.currentConfig["specialSillConditions"]

        if replacementSills:
            for key,value in replacementSills.items():
                if key.lower() in self.wtName.lower():
                    updatedSill = self.mullionDict[value]

        if updatedSill:
            panels = newWall_grid.GetPanelIds()
            with rpw.db.Transaction("Update Sills") as tx:
                SupressErrorsAndWarnings(tx) 
                for panelId in panels:
                    panel = self.doc.GetElement(panelId)
                    panelPoint = panel.GetTransform().Origin
                    sills = GetHorizontalMullionsAtPoint(newWall_grid, panelPoint, nameFilter=currentSill)

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
    def SetFinalParameters(self, storefrontObject):
        #############################################
        #            Final Param Setters            #
        #############################################
        # Set heights, for whatever reason differing heights before adding gridlines is an issue so set this last.
        with rpw.db.Transaction("Create Curtain Wall") as tx:
            SupressErrorsAndWarnings(tx)
            newWallSillHeight = storefrontObject.SillHeight
            newWallHeadHeight = storefrontObject.HeadHeight - storefrontObject.SillHeight
            self.newWall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(newWallSillHeight)
            self.newWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(newWallHeadHeight)
            self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(storefrontObject.SuperType)
            self.newWall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(str(self.selectedLevel) + "-"+ str(storefrontObject.AssemblyID))
    def Run_BuildWall2(self):
        print "RUNNING...DO NOT CLOSE WINDOW..."
        with rpw.db.TransactionGroup("Convert Wall", assimilate=True) as tg:

            #Adjust any parameters to the walltype before creation if needed.
            with rpw.db.Transaction("Adjust CW Parameters") as tx:

                # this is coming from utilities module
                SupressErrorsAndWarnings(tx)
                wtCW = self.doc.GetElement(self.wallTypeCW)
                if self.storefrontConfig.currentConfig["deflectionHeadType"] == 2:
                    wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-2"])
                elif self.storefrontConfig.currentConfig["deflectionHeadType"] == 1:
                    wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(self.mullionDict[self.systemName+"_DeflectionHead-1"])

            # FROM HERE ON OUT IT IS ONE GIANT FUCKING LOOP
            for storefrontObject in self.storefrontElevations:
                #############################################
                #                  Build                   #
                #############################################
                #pyrevit progress bar
                self.progressIndex += 1
                output = script.get_output()

                output.update_progress(self.progressIndex, len(self.storefrontElevations))

                hostElement = self.doc.GetElement(storefrontObject.HostElementIds[0])
                self.storefrontType = storefrontObject.SuperType

                self.baseConstraint = hostElement.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()

                locLine = storefrontObject.HostLine
                locLineStart = locLine.GetEndPoint(0)
                locLineEnd = locLine.GetEndPoint(1)

                #self.gridIntersectionPostPoints = [] # duplicate in __init__

                wallHostId = storefrontObject.HostElementIds[0]
                self.wtName = self.doc.GetElement(wallHostId).Name

                self.newWall = None
                ###########################
                ## FUCK THIS CONDITIONAL ##
                ###########################
                if str(hostElement.WallType.Kind) == "Basic":
                    self.Checker(storefrontObject)
                    self.Creation(storefrontObject)
                    self.Modification(storefrontObject)
                    self.SetFinalParameters(storefrontObject)