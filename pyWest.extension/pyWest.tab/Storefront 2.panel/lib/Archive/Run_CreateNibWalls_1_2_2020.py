def Run_CreateNibWalls2(self):
    # this class takes the recently saved currentConfigs to get data about how to create nib walls
    selectedSystem = self.currentConfig["currentSystem"]
    selectedPostWidth = self.currentConfig["postWidth"]
    selectedOneByWidth = self.currentConfig["oneByWidth"]
    gypNibWallTypeId = self.gypWallDict[self.currentConfig["nibWallType"]] # you can't serialize objs so dct of keys calls a dict that is always written in this module with objs as values for the same key indexes
    selectedNibWallLength = self.currentConfig["nibWallLength"]
    
    currentLevel = self.currentView.GenLevel
    levelName = currentLevel.Name        
    ####################################################
    ## REDUNDENT - SAME PROCESS AS COLLECTION CLASSES ##
    ####################################################
    # allow option to only create nib walls on user selected objects
    currentSelectedIds = self.uidoc.Selection.GetElementIds()

    if not currentSelectedIds:
        # get storefront walls from view in document
        storefrontWallIds = [i.Id for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall)
                             if i.Name in SFF.FamilyTools(self.doc).SFWallTypeNames]
    else: storefrontWallIds = currentSelectedIds # clunky fix this
    ####################################################
    ## REDUNDENT - SAME PROCESS AS COLLECTION CLASSES ##
    ####################################################
    intersectionPoints = SFU.RemoveDuplicatePoints(SFU.FindWallIntersections(storefrontWallIds))
    
    if not storefrontWallIds:
        Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "No Storefront walls selected or found in the view")
        pyrevit.script.exit()

    with rpw.db.Transaction("Create Nib") as tx:
        SFU.SupressErrorsAndWarnings(tx) # i added this
        
        for id in storefrontWallIds:
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
                        lengthAdjust = (0.5 * selectedPostWidth) + selectedOneByWidth
                        length = instLine.Length - lengthAdjust
                        leftover = length%(self.standardSizes[0] + selectedOneByWidth)
                        # var for "OPTIMIZED" calculation
                        numPanels = math.floor(length / (self.standardSizes[0] + selectedOneByWidth))

                        # optimized nib wall split
                        if selectedNibWallLength == "OPTIMIZED":
                            # if optimized split
                            if leftover > self.leftoverTol:
                                lastPanelSize = 0
                                for size in self.standardSizes[1:]:
                                    if leftover - self.leftoverTol >= (size + selectedOneByWidth):
                                        lastPanelSize = self.standardSizes[self.standardSizes.index(size)]
                                        break
                                offset = lengthAdjust + numPanels*self.standardSizes[0] + (numPanels)*selectedOneByWidth + lastPanelSize + int(lastPanelSize > 0)*selectedOneByWidth
                            else:
                                offset = lengthAdjust + (numPanels-1)*self.standardSizes[0] + self.standardSizes[1] + (numPanels)*selectedOneByWidth
                        # fixed nib wall split
                        else: offset = instLine.Length - selectedNibWallLength  
                        
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