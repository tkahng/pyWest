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
    
    from pyrevit import script
    
    sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
    import _csv as csv
    import json
    
    doc = __revit__.ActiveUIDocument.Document
    app = __revit__.Application
    version = __revit__.Application.VersionNumber.ToString()
    uidoc = __revit__.ActiveUIDocument
    currentView = uidoc.ActiveView
    
    user = str(System.Environment.UserName)
    
    rpwLib = r"VDCwestExtensions\pyVDCwest.extension\VDCwest.tab\0 Lib\revitpythonwrapper-master" # common lib folder
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 6, rpwLib))
    import rpw
    
    import SF2_Engine
    import SF2_Utility
    
    from pyrevit import script


    # PRE ERROR CHECK
    class SFCheckModel:
        def __init__(self, wallCLs):
            self.wallCLs = wallCLs # wall centerlines from engine are needed

        def PsuedoCode(self):
            # collect storefront settings from user
            # collect storefront walls from document
            # translate storefront walls to centerlines
            # convert centerlines to rhino objects
            # create nested lists of Revit end points
            # use Rhino api to create new lines from revit line endpoints
            # PRECHECK VERY IMPORTANT! vet model with Rhino lines

            # whatever doesnt check out gets converted back to Revit lines - what to do with original
            # i need a way to create a custom temp filter after problematic geometry is identified

            # new storefront algorithm to divide for mullions/panels; reconcile door
            # then run storefront as normal - 

            # storefront should write a json file in a default location with meta data of the most current storefront design

            # longterm take 3d geometry and create a pipeline to fabrication
            return(True)

        def Run_SFvetModel(self):
            pass
        

    # POST ERROR CHECK
    class ErrorCheckingTools:
        def storefront_fixer(self):
            """
            For fixing particular issues related to 
            storefront modeling for fabrication
            """
    
    
            print("CREATING REPORT...PLEASE WAIT...")
            PrintBreakLine()
            currentView = uidoc.ActiveView
    
            oneByWidth = 1.75/12
            tol = 0.001
    
            storefrontConfig = storefront_options()
    
            systemName = None
    
    
            mullionDict = GetMullionTypeDict()
            panelTypeDict = GetWindowTypeDict()
            doorDict = storefrontConfig.doorDict
    
    
            from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
            # Select the report type
            components = [Label('Specify System'),
                                  ComboBox("combobox1", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
                                                    Separator(),
                                                    Button('Go')]
    
            form = FlexForm("Storefront Report", components)
            form.show()
    
            if not form.values:
                sys.exit()
            else:
                systemName = form.values["combobox1"]
                if not systemName.lower() in storefrontConfig.currentConfig["currentSystem"].lower():
                    storefrontConfig.storefront_set_config()
                    systemName = storefrontConfig.currentConfig["currentSystem"]
                    storefrontConfig.storefront_save_config()
    
    
            allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
                                                          view=currentView, 
                                                                                                    where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))
    
            allStorefrontPanels  = []
            allStorefrontMullions = []
    
            for sfwall in allStorefrontWalls:
                for sfMullionsId in sfwall.CurtainGrid.GetMullionIds():
                    allStorefrontMullions.append(doc.GetElement(sfMullionsId))
    
                for panelId in sfwall.CurtainGrid.GetPanelIds():
                    allStorefrontPanels.append(doc.GetElement(panelId))
    
    
            with rpw.db.Transaction("Storfront Fixer"):
    
                for sfmullion in allStorefrontMullions:
    
                    mullionLength = sfmullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
    
                    if mullionLength > 0 and sfmullion.LocationCurve:
    
                        mullionName = sfmullion.Name.lower()
                        mullionRoom = sfmullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
                        mullionPoint = sfmullion.Location.Point
                        mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)
    
                        mullionCurve = sfmullion.LocationCurve
                        mullionCenter = mullionCurve.Evaluate(0.5, True)
    
                        if "post" in mullionName or "wallstart" in mullionName:
    
                            #Intermediate posts"
                            #if not storefrontConfig.currentConfig["mullionContinuousVerticalIntermediateTop"]:
                            sfmullion.JoinMullion()
                            doc.Regenerate()
                            mullionLengthAfter = sfmullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
                            if mullionLengthAfter > mullionLength:
                                output = script.get_output()
                                clickable_link = output.linkify(sfmullion.Id)
                                print "fixed: " + mullionName + " // " + str(mullionLength) + " to " + str(mullionLengthAfter) + " // -->" + clickable_link
    
                            # print out  all errors
    
                        if "door" in mullionName:
                            sfmullion.JoinMullion()
    
                        if "intermediate" in mullionName:
                            sfmullion.BreakMullion()
    
    
                for sfwall in allStorefrontWalls:
    
                    sfGrid = sfwall.CurtainGrid
    
                    for panelId in sfGrid.GetPanelIds():
    
                        panel = doc.GetElement(panelId)
    
    
                        panelWidth = panel.get_Parameter(BuiltInParameter.WINDOW_WIDTH).AsDouble()
                        panelHeight = panel.get_Parameter(BuiltInParameter.WINDOW_HEIGHT).AsDouble()
    
                        if (panelWidth > 0) and (panelHeight > 0):
    
                            condition = None
                            varient01 = None
                            varient02 = None
    
                            panelType = panel.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
                            panelSizeName = str(panelWidth) + " x " + str(panelHeight)
    
                            #Get panel point and flatten
                            panelPoint = panel.GetTransform().Origin
                            panelPoint = XYZ(panelPoint.X, panelPoint.Y, 0)
    
                            #Join or break the head mullions based on the system config
                            if "empty" in panelType.lower():
                                doorHeads = GetHorizontalMullionsAtPoint(sfGrid, panelPoint, nameFilter= "head")
    
                                if storefrontConfig.currentConfig["mullionContinuousHorizontalHeadAtDoor"]:
                                    if doorHeads:
                                        for mull in doorHeads:
                                            mull.JoinMullion()
                                            print "fixed: " + mull.Name
                                else:
                                    if doorHeads:
                                        for mull in doorHeads:
                                            mull.BreakMullion()
    
            # added return to allow IDE function collapse
            return(True)
    
        # 172 LINES OF CODE
        def storefront_preflight(self):
    
            ecModelInst = None
            docEC = None
            wallErrorList = {}
            doorErrorList = {}
            toSelect = []
            toSelectEC = []
            selection = uidoc.Selection
            storefrontConfig = storefront_options()
    
            try:
                linkedInstances = SF2_Utility.GetRevitLinkInstances()
                if linkedInstances:
                    for modelInst in linkedInstances:
                        if ("_ec" in modelInst.Name.lower()
                                                or "ec." in  modelInst.Name.lower()
                                                            or "existingconditions" in  modelInst.Name.lower()
                                                            or "existing" in  modelInst.Name.lower()):
                            ecModelInst = modelInst
                            docEC = ecModelInst.GetLinkDocument()
                    if not docEC:
                        wallErrorList["EC ERROR"] = "EC model is not linked, please check."
                    else:
                        print("EC MODEL FOUND")
                else:
                    wallErrorList["EC ERROR"] = "No linked models found"
            except Exception as inst:           
                print("...ERROR LOADING EC ELEMENTS")
                OutputException(inst)
    
            PrintBreakLine()
    
            # Check EC Document
            try:
                if docEC:
                    allLevelsEC = GetAllElements(docEC, BuiltInCategory.OST_Levels, Autodesk.Revit.DB.Level)
    
                    # check walls
                    allWallsEC  = GetAllElements(docEC, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
                    wallCheckEC = CheckElementConstraints(docEC,allWallsEC)
                    if wallCheckEC:
                        wallErrorList["EC WALL ERRORS"] = wallCheckEC
                        print str(len(wallCheckEC)) + " - Wall Issues in EC"
    
                    # check columns
                    allColumnsEC = GetAllElements(docEC, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
                    allColumnsEC += GetAllElements(docEC, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)
                    columnCheckEC = CheckElementConstraints(docEC,allColumnsEC)
                    if columnCheckEC:
                        wallErrorList["EC COLUMN ERRORS"] = columnCheckEC
                        print str(len(columnCheckEC)) + " - Column Issues in EC"
                        #walls that span or are unconnected
    
            except Exception as inst:
                OutputException(inst)
    
            # Check Active Document
            try:
                allLevels = GetAllElements(doc, BuiltInCategory.OST_Levels, Autodesk.Revit.DB.Level)
    
                # check walls
                allWalls  = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
                wallCheck = CheckElementConstraints(doc,allWalls)
                if wallCheck:
                    wallErrorList["WALL ERRORS"] = wallCheck
                    print str(len(wallCheck)) + " - Wall Issues in Acive Doc"
    
                # check columns
                allColumns = GetAllElements(doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
                allColumns += GetAllElements(doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)
                columnCheck = CheckElementConstraints(doc,allColumns)
                if columnCheck:
                    wallErrorList["COLUMN ERRORS"] = columnCheck
                    print str(len(columnCheck)) + " - Column Issues in Active Doc"
                    #walls that span or are unconnected
    
            except Exception as inst:
                OutputException(inst)   
    
            # check doors
            availableDoors = storefrontConfig.doorDict
            doorErrorList["DOOR ERRORS"] = []
            allDoors = GetAllElements(doc, BuiltInCategory.OST_Doors, Autodesk.Revit.DB.FamilyInstance)
            allDoors = FilterDemolishedElements(doc, allDoors)
    
            for doorId in allDoors:
                door = doc.GetElement(doorId)
                hostWallId = None
                for p in door.Parameters:
                    if p.Definition.Name == "Host Id":
                        hostWallId = p.AsElementId()
                # check if door is hosted on storefront
                if hostWallId:
                    hostWall = doc.GetElement(hostWallId)
                    if hostWall:
                        if "storefront" in hostWall.Name.lower():
                            #check if door exists in list of recognized doors
                            doorName =  door.Name
                            inList = False
                            for name in availableDoors.keys():
                                if doorName in name:
                                    inList = True
                            if not inList:
                                doorErrorList["DOOR ERRORS"] += [doorId]
    
            # print out door issue deail
            if doorErrorList["DOOR ERRORS"]:
                for doorId in doorErrorList["DOOR ERRORS"]:
                    door = doc.GetElement(doorId)
                    doorName = door.Name
                    doorLevel = None
                    for p in door.Parameters:
                        if p.Definition.Name == "Level":
                            doorLevel = p.AsValueString()
                    print("Unrecognized Door Issue // {0} // : {1}".format(str(doorName), str(doorLevel)))
    
            print("{0} - Door Issues in Active Doc".format(str(len(doorErrorList["DOOR ERRORS"]))))

            # add door errors to list
            #toSelect += errorList["DOOR ERRORS"]
    
            PrintBreakLine()
    
            # output the caught wall and column issues
            for key in wallErrorList.keys():
    
                if type(wallErrorList[key]) == list:
    
                    for inst in wallErrorList[key]:
                        elementCategory = None
                        familyName = None
                        typeName = None
                        topConstraint = None
    
                        if type(inst) == ElementId: 
                            inst = doc.GetElement(inst)
                            print "THIS" 
                            print inst
                        for p in inst.Parameters:
                            if p.Definition.Name == "Base Constraint" or p.Definition.Name == "Base Level":
                                baseConstraint = p.AsValueString()
                            if p.Definition.Name == "Top Constraint" or p.Definition.Name == "Top Level":
                                topConstraint = p.AsValueString()
                            if p.Definition.Name == "Category":
                                elementCategory = p.AsValueString()
    
                        prefix = ""
                        whichDoc = ""
    
                        if topConstraint and "Unconnected" in topConstraint:
                            prefix = "Unconnected "
                        elif topConstraint:
                            prefix = "Spanning "
                        if "EC" in key:
                            whichDoc = "-- EC DOC"
                        else:
                            whichDoc = "-- ACTIVE DOC"
    
                        # print out  all errors
                        output = script.get_output()
                        clickable_link = output.linkify(inst.Id)
                        print prefix + str(elementCategory) + " Issue // " + str(inst.Name) + " // : " + str(baseConstraint) + " --> " + str(topConstraint) + " // " + whichDoc + "-->" + clickable_link
    
                else:
                    print wallErrorList[key]
                    PrintBreakLine()
                PrintBreakLine()
            print ""
    
            # added return to allow IDE function collapse
            return(True)
    
        # 266 LINES OF CODE
        def storefront_annotate(self):
            """Annotates a view with storefront.
            """
    
            print("CREATING ANNOTATIONS")
            PrintBreakLine()
    
            currentView = uidoc.ActiveView
            storefrontFrames = []
            annotationNotes = []
    
            standardTol = 0.01
    
    
            #Form input
            from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
    
            components = [Label('Select System'),
                                  ComboBox("combobox1", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
                                                    ComboBox("combobox2", {"Custom/Standard": "CS", "Glass Sizes": "GS"}),
                                                    Separator(),
                                                    Button('Go')]
    
            form = FlexForm("Storefront Annotate", components)
            form.show()
    
            if not form.values:
                sys.exit()
            else: 
                systemName = form.values["combobox1"]
                annoType = form.values["combobox2"]
    
    
            #Load config
            storefrontConfig = storefront_options()
    
            if not systemName.lower() in storefrontConfig.currentConfig["currentSystem"].lower():
                storefrontConfig.storefront_set_config()
                systemName = storefrontConfig.currentConfig["currentSystem"]
                storefrontConfig.storefront_save_config()
    
            famTypeDict = GetFamilyTypeDict("Panel-Symbol-Custom")
            famTypeDict.update(GetFamilyTypeDict("Panel-Symbol-Standard"))
    
            #Load standard sizes
            systemStandardHorizontals = storefrontConfig.currentConfig["systemStandardHorizontals"]
            sillStandards = systemStandardHorizontals["sill"]
    
            #collect notest in the view if there are any
            annotationNotes = list(SF2_Utility.GetElementsInView(BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, currentView.Id))
            annotationNotes = FilterElementsByName(doc, annotationNotes,["Panel","Symbol"], False)
    
            #collect walls and mullions
            allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
                                                  view=currentView, 
                                                  where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))
    
            allStorefrontMullions = []
    
            #Collect mullions
            for sfwall in allStorefrontWalls:
                for sfMullionsId in sfwall.CurtainGrid.GetMullionIds():
                    allStorefrontMullions.append(doc.GetElement(sfMullionsId))
    
            annotationsList = []
    
            # Toggle: if theres annotations in the view already, then delete them.
    
            if annoType == "CS":
    
                if annotationNotes:
                    with rpw.db.Transaction("Clear Annotations"):
                        DeleteElementsInView(currentView.Id, BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, "Panel-Symbol-Custom")
                        DeleteElementsInView(currentView.Id, BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, "Panel-Symbol-Standard")
    
    
                # Toggle: if there is NOT annotations in the view, then create them
                else:
                    for sfMullion in allStorefrontMullions:
    
                        sfMullionName = sfMullion.Name
    
                        if sfMullion.LocationCurve:
    
                            sfMullionLength = sfMullion.LocationCurve.Length
    
                            if "sill" in sfMullionName.lower():
                                placementPoint = sfMullion.LocationCurve.Evaluate(0.5, True)
                                text = ""
                                notesymbol = None
    
                                for key, standardLength in sillStandards.items():
                                    if abs(sfMullionLength - standardLength) < standardTol:
                                        text = "STANDARD"
                                        notesymbol = doc.GetElement(famTypeDict["Panel-Symbol-Standard"])
                                        break
                                    else:
                                        text = "CUSTOM"
                                        notesymbol = doc.GetElement(famTypeDict["Panel-Symbol-Custom"])
    
                                annotationsList.append([placementPoint, text, notesymbol])
    
                    #Place annotations	
                    with rpw.db.Transaction("Clear Annotations"):
                        for annot in annotationsList:
                            point = annot[0]
                            sym = annot[2]
                            annotInst = doc.Create.NewFamilyInstance(point, sym, currentView)
                            for p in annotInst.Parameters:
                                if p.Definition.Name == "label_text":
                                    p.Set(annot[1])
    
    
            #Creates glass width tags on a plan
            if annoType == "GS":
    
                junctionPoints = []
                intermediatePoints = []
    
                glassTagList = []
    
    
                for mullion in allStorefrontMullions:
    
                    mullionLength = mullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
    
                    if mullionLength > 0 and mullion.LocationCurve:
    
                        mullionName = mullion.Name.lower()
                        mullionRoom = mullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
                        mullionPoint = mullion.Location.Point
                        mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)
    
                        if "post" in mullionName:
                            junctionPoints.append([mullionPoint, mullionName])
    
                        if "wallstart" in mullionName:
                            junctionPoints.append([mullionPoint, mullionName])
    
                        if "door" in mullionName:
                            junctionPoints.append([mullionPoint, mullionName])
    
                        if "intermediate" in mullionName:
                            intermediatePoints.append([mullionPoint, mullionName])
    
    
    
                for storefrontElevation in allStorefrontWalls:
    
                    panelIds = storefrontElevation.CurtainGrid.GetPanelIds()
    
                    linearGlass = storefrontElevation.Location.Curve.Length
    
                    storefrontElevationID = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
                    storefrontSuperType = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
    
                    #Panels
                    for panelId in panelIds:
    
                        panel = doc.GetElement(panelId)
                        panelWidth = panel.get_Parameter(BuiltInParameter.WINDOW_WIDTH).AsDouble()
                        panelHeight = panel.get_Parameter(BuiltInParameter.WINDOW_HEIGHT).AsDouble()
    
                        if (panelWidth > 0) and (panelHeight > 0):
    
                            condition = None
                            varient01 = None
                            varient02 = None
    
                            panelFamily = panel.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
                            panelType = panel.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
                            panelSF = panelWidth * panelHeight
                            panelSizeName = str(panelWidth) + " x " + str(panelHeight)
    
                            #Get panel point and flatten
                            panelPoint = panel.GetTransform().Origin
                            panelPoint = XYZ(panelPoint.X, panelPoint.Y, 0)
    
                            panelRoomID = panel.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
    
                            #Default panel position
                            panelPositions = []
    
                            # Checking end conditions against junctions (post, wallstart, and door frames)
                            juntionsAndDoorFrames = junctionPoints
    
    
                            if "glazed" in panelFamily.lower():
    
                                numFoundEndConditions = 0
    
                                #CORRECT PANEL WIDTH + HEIGHT FOR ACTUAL SIZES
                                # Add correction for differences between modeling and reality
    
                                glassWidthCorrection = 0
                                glassHeightCorrection = 0
    
                                #Ends
                                for i in range(len(juntionsAndDoorFrames)):
                                    testPoint = juntionsAndDoorFrames[i][0]
                                    testMullionName = juntionsAndDoorFrames[i][1]
                                    testDist1 = testPoint.DistanceTo(panelPoint)
    
                                    if testDist1 < ((panelWidth/2) + (2.1/12)):
                                        glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]
                                        numFoundEndConditions += 1 #Found an end condition
                                        #print storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]
    
                                #Intermediates
                                for i in range(len(intermediatePoints)):
                                    testPoint = intermediatePoints[i][0]
                                    testMullionName = intermediatePoints[i][1]
                                    testDist2 = testPoint.DistanceTo(panelPoint)
    
                                    if testDist2 < ((panelWidth/2) + (1.8/2)):
                                        glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]
                                        numFoundEndConditions += 1 #Found an end condition
                                        #print storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]
    
                                #Butt joints
                                numButtJoints = 2 - numFoundEndConditions #Glass has 2 ends, if above conditions arent detected, its assumed a butt joint is found
                                glassWidthCorrection += (numButtJoints * storefrontConfig.currentConfig["panelCorrections"]["horizontalButtJoint"])
    
                                #print numButtJoints
    
    
                                #Head and Sill pockets
                                glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalSill"]
                                glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalHead"]
    
                                #create list of glass size tags
                                glassTagList.append([panelPoint,(panelWidth + glassWidthCorrection)])
    
    
                #place glass tags
                tagFamTypeDict = GetFamilyTypeDict("Panel-Symbol-Standard")
                tagSym = doc.GetElement(tagFamTypeDict["Panel-Symbol-Standard"])
    
    
                #Set units and format options to convert decimal feet to inche fractional
                formatUnits = doc.GetUnits()
                fvo = FormatValueOptions()
                fo = FormatOptions(DisplayUnitType.DUT_FRACTIONAL_INCHES)
                fo.Accuracy = .0625
                fvo.SetFormatOptions(fo)
    
                #Place annotations	
                with rpw.db.Transaction("Tag Glass"):
                    for tag in glassTagList:
                        point = tag[0]
                        #tag = size[2]
    
                        sizeInches = UnitFormatUtils.Format(formatUnits, UnitType.UT_Length, tag[1], False, False, fvo)
    
                        annotInst = doc.Create.NewFamilyInstance(point, tagSym, currentView)
                        for p in annotInst.Parameters:
                            if p.Definition.Name == "label_text":
                                p.Set(sizeInches)
    
    
    
            print("FINISHED")
            # added return to allow IDE function collapse
            return(True)
    
        # 250 LINES OF CODE
        def storefront_dimension(self):
            """Creates dimension strings on
            a storefront laser layout view.
            """
    
            from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
    
            currentView = uidoc.ActiveView
            theta = math.pi*0.5
            axis_z = Autodesk.Revit.DB.Line.CreateBound(XYZ(0,0,0),XYZ(0,0,1))
            searchDist = 4
            offsetDim = 1
    
            #Get the linear dimension types in the doc to select from
            allDimensionTypes = GetAllElements(doc, None, Autodesk.Revit.DB.DimensionType)
            linearDimensionTypes = {}
    
            autodimOptions = {"Laser Layout": "Laser Layout", "Partition Plan" : "Partition Plan"}
    
            for elemId in allDimensionTypes:
                dT = doc.GetElement(elemId)
                if "Linear" in dT.FamilyName:
                    dTName = dT.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
                    linearDimensionTypes[dTName] = dT
    
    
            #Select dimension settings
            components = [Label('Dimension Distance From Datums'),
                                  ComboBox("combobox1", {"4'-0''": 4.0, "8'-0''": 8.0}),
                                                    Label('Dimension Type'),
                                                    ComboBox("combobox2", linearDimensionTypes),
                                                    Label('Dimension Function'),
                                                    ComboBox("combobox3", autodimOptions),
                                                    Label('System'),
                                                    ComboBox("combobox4", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
                                                    Separator(),
                                                    Button('Go')]
    
            form = FlexForm("Storefront Auto Dim", components)
            form.show()
    
            if not form.values:
                sys.exit()
            else: 
                searchDist = form.values["combobox1"]
                selectedDimType = form.values["combobox2"]
                autodimOption = form.values["combobox3"]
                systemName = form.values["combobox4"]
    
            if autodimOption == "Laser Layout":
    
                #Get walls for datum lines to measure to
                allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
                #storefrontWalls = FilterElementsByName(doc, allWalls, ["Storefront","Storefront"], False)
    
                with rpw.db.Transaction("Auto Dim Lines"):
                    # Gather all the lines to filter and delete the ones we dont want.
                    allLines = list(SF2_Utility.GetElementsInView(BuiltInCategory.OST_Lines, Autodesk.Revit.DB.CurveElement, currentView.Id))
    
                    for lineId1 in allLines:
                        line1 = doc.GetElement(lineId1)
                        lineName = line1.LineStyle.Name
    
                        if ("Full" in lineName or "Partial" in lineName) and line1.GeometryCurve.IsBound:
                            refArray = ReferenceArray()
                            lineReference =line1.GeometryCurve
    
                            line1StartPoint = lineReference.GetEndPoint(0)
                            line1EndPoint = lineReference.GetEndPoint(1)
    
                            x1 = line1EndPoint.X - line1StartPoint.X
                            y1 = line1EndPoint.Y - line1StartPoint.Y
    
                            vect1Norm = XYZ(y1 * -1, x1, 0).Normalize()
                            vect1 = vect1Norm.Multiply(offsetDim)
    
                            point1 = line1StartPoint.Add(vect1)
                            point2 = line1EndPoint.Add(vect1)
    
                            dimLine = Autodesk.Revit.DB.Line.CreateBound(point1, point2)
    
                            refArray.Append(lineReference.GetEndPointReference(0)) 
                            refArray.Append(lineReference.GetEndPointReference(1))
                            newDim = doc.Create.NewDimension(currentView, dimLine, refArray)
                            newDim.DimensionType = selectedDimType
    
    
                        elif "control" in lineName.lower() and line1.GeometryCurve.IsBound:
    
                            for wallId in allWalls:
                                wall = doc.GetElement(wallId)
                                if "Basic" in str(wall.WallType.Kind):
                                    line2 = wall.Location.Curve
    
                                    #Crazy way to get the wall centerline as a Reference object
                                    unique = wall.UniqueId
                                    refString = System.String.Format("{0}:{1}:{2}",unique,-9999,1)
                                    wall_centre = Reference.ParseFromStableRepresentation(doc,refString)
    
                                    line2StartPoint = line2.Evaluate(0, True)
                                    line2Midpoint = line2.Evaluate(0.5, True)
    
                                    x1 = line2Midpoint.X - line2StartPoint.X
                                    y1 = line2Midpoint.Y - line2StartPoint.Y
                                    z1 = line2Midpoint.Z
    
                                    vect1Norm = XYZ(x1,y1,0).Normalize()
                                    vect1 = vect1Norm.Multiply(searchDist)
    
                                    #Create the vectors
                                    vect2 = XYZ(vect1.Y * -1, vect1.X, vect1.Z)
                                    vect3 = XYZ(vect1.Y, vect1.X * -1, vect1.Z)
    
                                    #Add them to the midpoints
                                    point1 = line2Midpoint.Add(vect2)
                                    point2 = line2Midpoint.Add(vect3)
    
    
                                    #Create the line that will be used to test intersections with datum lines
                                    testLine = Autodesk.Revit.DB.Line.CreateBound(point1, point2)
    
                                    #Create the datum line at the same z level as the test intersection lines
                                    line1GC = line1.GeometryCurve
                                    datumPoint1 = line1GC.GetEndPoint(0)
                                    datumPoint2 = line1GC.GetEndPoint(1)
    
                                    datumPoint1 = XYZ(datumPoint1.X, datumPoint1.Y, line2Midpoint.Z)
                                    datumPoint2 = XYZ(datumPoint2.X, datumPoint2.Y, line2Midpoint.Z)
    
                                    flattenedDatumLine = Autodesk.Revit.DB.Line.CreateBound(datumPoint1, datumPoint2)
    
                                    intersection = RevitCurveCurveIntersection(flattenedDatumLine, testLine)
    
                                    if intersection:
    
                                        #Adjust the position parameter based on distance away
                                        #from the datum line so they are easier to read
    
                                        posFactor = (line2Midpoint.DistanceTo(intersection)/searchDist) * (line2StartPoint.DistanceTo(line2Midpoint)/2)
                                        adjustVect = vect1Norm.Multiply(posFactor)
    
                                        p1 = line2Midpoint.Add(adjustVect)
                                        p2 = intersection.Add(adjustVect)
    
                                        if p1.DistanceTo(p2) > app.ShortCurveTolerance:
                                            dimLine = Autodesk.Revit.DB.Line.CreateBound(p1, p2)
                                            refArray = ReferenceArray()
                                            #lineReference =line1.GeometryCurve
                                            refArray.Append(line1.GeometryCurve.Reference)
                                            refArray.Append(wall_centre)
                                            newDim = doc.Create.NewDimension(currentView, dimLine, refArray)
                                            newDim.DimensionType = selectedDimType
    
            elif autodimOption == "Partition Plan":
    
                """
                            Creates sill dimensions for partition install plans
                            """ 
    
                allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
                                                                  view=currentView, 
                                                                                                    where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))
    
                allStorefrontPanels  = []
                allStorefrontMullions = []
    
                #Collect mullions
                for sfwall in allStorefrontWalls:
                    for sfMullionsId in sfwall.CurtainGrid.GetMullionIds():
                        allStorefrontMullions.append(doc.GetElement(sfMullionsId))
    
                with rpw.db.Transaction("Auto Dim Sills"):
    
                    for sfMullion in allStorefrontMullions:
    
                        if "sill" in sfMullion.Name.lower() and sfMullion.LocationCurve:
    
                            mullionDirection = sfMullion.LocationCurve.Direction
    
                            refArray = ReferenceArray()
                            edgeCurve = None
    
                            options = app.Create.NewGeometryOptions()
                            options.IncludeNonVisibleObjects = True
                            options.ComputeReferences = True
    
                            faces = []
                            perpFace = None
    
                            mullionGeo = sfMullion.get_Geometry(options)
    
                            for item in list(mullionGeo):
                                geometry = list(item.GetInstanceGeometry())
                                for geo in geometry:
                                    if type(geo) == Autodesk.Revit.DB.Solid:
                                        if list(geo.Faces.GetEnumerator()):
                                            faces = list(geo.Faces.GetEnumerator()) 
                                if faces:
                                    break
    
                            for face in faces:
    
                                faceDirection = face.FaceNormal
    
    
                                if abs(90-((faceDirection.AngleTo(mullionDirection)*360)/ (2*math.pi))) < 0.01 and faceDirection.Z == 1 :
                                    #print "found face"
    
                                    edgeloops = list(face.EdgeLoops)[0]
                                    edgesFound = 0
    
                                    for edge in edgeloops:
    
                                        #if abs(edge.AsCurve().Direction.Z) == 1:
                                        if abs(180-((edge.AsCurve().Direction.AngleTo(mullionDirection)*360)/ (2*math.pi))) < 0.01:
    
                                            edgeCurve = Autodesk.Revit.DB.Line.CreateBound(edge.AsCurve().GetEndPoint(0), edge.AsCurve().GetEndPoint(1))
    
                                            edgesFound += 1
                                            break
                                    break
    
                            if edgesFound >= 1:
    
                                line1 = sfMullion.LocationCurve
    
                                line1StartPoint = line1.GetEndPoint(0)
                                line1EndPoint = line1.GetEndPoint(1)
    
                                x1 = line1EndPoint.X - line1StartPoint.X
                                y1 = line1EndPoint.Y - line1StartPoint.Y
    
                                vect1Norm = XYZ(y1 * -1, x1, 0).Normalize()
                                vect1 = vect1Norm.Multiply(offsetDim)
    
                                point1 = line1StartPoint.Add(vect1)
                                point2 = line1EndPoint.Add(vect1)
    
                                dimLine = Autodesk.Revit.DB.Line.CreateBound(point1, point2)
    
                                if edgeCurve:
                                    dummyDetail = doc.Create.NewDetailCurve(currentView, edgeCurve)
    
                                    refArray.Append(dummyDetail.GeometryCurve.GetEndPointReference(0)) 
                                    refArray.Append(dummyDetail.GeometryCurve.GetEndPointReference(1))
    
                                    newDim = doc.Create.NewDimension(currentView, dimLine, refArray)
                                    newDim.DimensionType = selectedDimType
    
            # added return to allow IDE function collapse
            return(True)
    
        # 149 LINES OF CODE
        def SF_PostErrorCheck(self):
            """Checks errors for mullions and panels
            """
    
            currentView = uidoc.ActiveView
            famTypeDict = GetFamilyTypeDict("Fabrication-Error-Symbol")
    
            # Clear existing error notations
            errorNotations = list(SF2_Utility.GetElementsInView(BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, currentView.Id))
            errorNotations = FilterElementsByName(doc, errorNotations,["Fabrication","Error-Symbol"], False)
            if errorNotations:
                with rpw.db.Transaction("Place Errors"):
                    for error in errorNotations:
                        doc.Delete(error)
    
    
            def PointsAndErrors(mullions_list, errorName, cat_or_ids):
                """adds to lists of points and errors"""
                errorsToFlag = []
                compList =[]
                for m in mullions_list:
                    mElem = doc.GetElement(m)
                    if m not in compList:
                        intersectingMulls = FindIntersectingMullions(mElem, cat_or_ids)
                        if list(intersectingMulls):
                            mullPt = mElem.Location.Point
                            errorsToFlag.append([mullPt, errorName])
                            for mm in list(intersectingMulls):
                                compList.append(mm.Id)
                return errorsToFlag
    
            def MullionClash():
    
                errorsToFlag = []
    
                selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id
    
                allMullions = GetAllElements(doc, BuiltInCategory.OST_CurtainWallMullions, Autodesk.Revit.DB.FamilyInstance, currentView=True)
                allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
    
                allWalls = FilterElementsByName(doc, allWalls, ["Storefront","Storefront"], True)
    
                errorsToFlag += PointsAndErrors(allMullions, "Mullion-Mullion Intersects", BuiltInCategory.OST_CurtainWallMullions)
                errorsToFlag += PointsAndErrors(allMullions, "Mullion-Panel Intersects", BuiltInCategory.OST_CurtainWallPanels)
                if allWalls:
                    errorsToFlag += PointsAndErrors(allMullions, "Mullion-Wall Intersects", allWalls)
    
                return errorsToFlag
    
            def PanelClash():
    
    
                errorsToFlag = []
    
                allPanels = GetAllElements(doc, BuiltInCategory.OST_Windows, Autodesk.Revit.DB.FamilyInstance, currentView=True)
                allPanels = FilterDemolishedElements(doc, allPanels)
    
                panelMinWidth = 0.45
                panelMaxWidth = 5.0
                panelMaxHeight = 8.14
    
                ### ITERATE OVER PANEL LIST ###
                for p in allPanels:
                    famInst = doc.GetElement(p)
    
                    pan_height = famInst.Parameter[BuiltInParameter.FAMILY_HEIGHT_PARAM].AsDouble()
                    pan_width = famInst.Parameter[BuiltInParameter.FAMILY_WIDTH_PARAM].AsDouble()
    
                    if "empty" not in famInst.Name.lower():
                        if pan_width < panelMinWidth:
                            errorsToFlag.append([famInst.GetTransform().Origin, "Small Panel"])
                        elif pan_width > panelMaxWidth:
                            errorsToFlag.append([famInst.GetTransform().Origin, "Wide Panel"])
                        elif pan_height > panelMaxHeight:
                            errorsToFlag.append([famInst.GetTransform().Origin, "Tall Panel"])
                    else:
                        pass
    
                return errorsToFlag
    
            def ECWallClash():
    
                errorsToFlag = []
                columnsLinesEdgesEC = []
                wallsLinesEdgesEC = []
    
    
                docLoaded = RevitLoadECDocument(quiet=True)
                if docLoaded[0]:
                    docEC = docLoaded[0]
                    ecTransform = docLoaded[1]
    
                    selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id
    
                    selectedLevelInst = doc.GetElement(selectedLevel)
                    levelElevationEC = None 
                    for p in selectedLevelInst.Parameters:
                        if p.Definition.Name == "Elevation":
                            levelElevationEC = p.AsDouble()
    
                    allWallsEC  = GetAllElements(docEC, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
                    allColumnsEC = GetAllElements(docEC, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
                    allColumnsEC += GetAllElements(docEC, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)
    
                    selectedWallsEC = FilterElementsByLevel(docEC, allWallsEC, levelElevationEC)
                    selectedColumnsEC = FilterElementsByLevel(docEC, allColumnsEC, levelElevationEC)
    
                    wallsLinesEdgesEC = SF2_Utility.GetWallEdgeCurves(docEC, selectedWallsEC, ecTransform)
                    columnsLinesEdgesEC = SF2_Utility.GetColumnEdgeCurves(docEC, selectedColumnsEC, ecTransform)
    
                allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
                storefrontWalls = FilterElementsByName(doc, allWalls,["Storefront","Storefront"], False)
                storefrontWalls = FilterWallsByKind(doc, storefrontWalls, "Basic")
    
                obstructionEdges = columnsLinesEdgesEC
                obstructionEdges += wallsLinesEdgesEC
    
                if obstructionEdges:
                    for sfWallId in storefrontWalls:
                        sfWall = doc.GetElement(sfWallId)
                        locLine = sfWall.Location.Curve
                        locLineStart = locLine.GetEndPoint(0)
                        locLineEnd = locLine.GetEndPoint(1)
    
                        for obstructionLine in obstructionEdges:
                            obstLineElevation = obstructionLine.GetEndPoint(0).Z
                            locLineStart = XYZ(locLineStart.X, locLineStart.Y, obstLineElevation)
                            locLineEnd = XYZ(locLineEnd.X, locLineEnd.Y, obstLineElevation)
                            locLineFlat = Line.CreateBound(locLineStart, locLineEnd)
                            intersection = RevitCurveCurveIntersection(locLineFlat,obstructionLine)
    
                            if intersection:
                                #ERROR: Hit Existing Condition
                                errorsToFlag.append([intersection, "Hit EC"])
    
                return errorsToFlag
    
            allErrors = []
            allErrors += ECWallClash()
            allErrors += MullionClash()
            allErrors += PanelClash()
    
            errorSymbolId = famTypeDict["Fabrication-Error-Symbol"]
    
            if allErrors:
                with rpw.db.Transaction("Error Check"):
                    RevitPlaceErrorsInView(currentView, allErrors, errorSymbolId)
    
            # added return to allow IDE function collapse
            return(True)
    
        # 1,389 LINES OF CODE
        def storefront_report(self):
    
            """Reporting tool that prepares an export
    
                    reportType = "material" or "cut"
                    Material report is just a take-off
                    Cut report is a full cu
                    tlist.
                    """
    
    
            print("CREATING REPORT...PLEASE WAIT...")
            SF2_Utility.PrintBreakLine()
            currentView = uidoc.ActiveView
            try:
                levelName = currentView.GenLevel.Name
            except:
                pass
            try:
                levelElevation = currentView.GenLevel.Elevation
            except:
                pass
            glassList = []
            storefrontFrames = []
    
            oneByWidth = 1.75/12
            tol = 0.001
    
            storefrontConfig = storefront_options()
    
            systemName = None
    
    
            mullionDict = GetMullionTypeDict()
            panelTypeDict = GetWindowTypeDict()
            doorDict = storefrontConfig.doorDict
    
    
            from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
            # Select the report type
            components = [Label('Pick Report Type:'),
                                  ComboBox("combobox1", {"Estimation - Take Off": "takeoff", "Fabrication - Cut List": "cutlist"}),
                                                    Label('Specify System'),
                                                    ComboBox("combobox2", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
                                                    Separator(),
                                                    Button('Go')]
    
            form = FlexForm("Storefront Report", components)
            form.show()
    
            if not form.values:
                sys.exit()
            else:
                reportType = form.values["combobox1"]
                systemName = form.values["combobox2"]
    
    
                if not systemName.lower() in storefrontConfig.currentConfig["currentSystem"].lower():
                    storefrontConfig.storefront_set_config()
                    systemName = storefrontConfig.currentConfig["currentSystem"]
                    storefrontConfig.storefront_save_config()
    
    
            currentSelected = list(uidoc.Selection.GetElementIds())
            allStorefrontWalls = []
    
            if currentSelected:
                for id in currentSelected:
                    inst = doc.GetElement(id)
                    if inst.Category.Name == "Walls":
                        instName = None
                        try:
                            instName = inst.Name.lower()
                        except:
                            for p in inst.Parameters:
                                if p.Definition.Name == "Name":
                                    instName = p.AsString().lower()
                        if systemName.lower() in instName.lower() and str(inst.WallType.Kind) == "Curtain":
                            allStorefrontWalls.append(inst)
            else:
                allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
                                                                  view=currentView, 
                                                                                                    where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))
    
            #Gather elements in view
            #cutlist specific
    
    
            allStorefrontMullions = []
    
            #allStorefrontMullions = list(rpw.db.Collector(of_class='FamilyInstance', of_category='OST_CurtainWallMullions',
            #										level=currentView.GenLevel, 
            #										where=lambda x: (systemName.lower() in x.Name.lower())).unwrap())
    
            for sfwall in allStorefrontWalls:
                sfMullionsIds = sfwall.CurtainGrid.GetMullionIds()
                for sfMullionsId in sfMullionsIds:
                    allStorefrontMullions.append(doc.GetElement(sfMullionsId))
    
    
    
    
            allDoors = rpw.db.Collector(of_class='FamilyInstance', of_category='OST_Doors')
    
            allStorefrontBasicWalls = rpw.db.Collector(of_class='Wall', 
                                                               view=currentView, 
                                                                                                    where=lambda x: (str(x.WallType.Kind) == "Basic") and ("storefront" in x.Name.lower()))
    
            allAreas = rpw.db.Collector(of_class='SpatialElement', of_category='OST_Areas',
                                                view=currentView)
    
            allWalls = rpw.db.Collector(of_class='Wall')
    
            allFamInstances = rpw.db.Collector(of_class='FamilyInstance', of_category='OST_SpecialityEquipment')
            projectInfo = doc.ProjectInformation
            projectName = projectInfo.get_Parameter(BuiltInParameter.PROJECT_NAME).AsString()
    
            if not projectName:
                projectName = "UNNAMED PROJECT"
    
            todaysDate = str(dt.Today.Month)+"/"+str(dt.Today.Day)+"/"+str(dt.Today.Year)
            currentUser = doc.Application.Username
    
            try:
                systemStandardHorizontals = storefrontConfig.currentConfig["systemStandardHorizontals"]
            except:
                pass
            try:
                systemStandardVerticals = storefrontConfig.currentConfig["systemStandardVerticals"]
            except:
                pass
            try:
                detectEndConditions = storefrontConfig.currentConfig["cutlistDetectEndConditions"]
            except:
                pass
    
            print("...GATHERING DATA")
    
            fullPosts = 0
            PartialPosts = 0
    
            conditionsArray = [["ELEMENT", "SYSTEM", "CONDITION", "VARIENT 01", "VARIENT 02", "AREA", "ROOM", "LENGTH", "WIDTH", "COMMENT"]]
    
            linearFull = 0
            linearDoors = 0
            linearPartial = 0
            linearOther = 0
    
            linearBasicFull = 0
            linearBasicDoors = 0
            linearBasicPartial = 0
            linearBasicOther = 0
    
            areaGlass = 0
            areaGlassStandard = 0
            countGlass = 0
    
            areaInfillPanel = 0
            countInfillPanel = 0
    
            fullPostPoints = []
            partialPostPoints = []
            partialSillHeight = 0
            fullHeadHeight = 0
    
            glassExportDict = {}
            solidExportDict = {}
            mullionExportDict = {}
            doorExportDict = {}
    
            allWallsSummary = {}
            allDoorsSummary = {}
            allSpecialObjectSummary = {}
    
            junctionPoints = []
            doorFramePoints = []
            intermediatePoints = []
    
            areaBoundaryPoints = {}
    
            standardTol = 0.01
    
        # Creates list of boundary points that will test for element inclusion
            for anArea in allAreas:
                areaName = anArea.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
                areaBoundaryPoints[areaName] = GetArea2DBoundaryPoints(anArea)
    
        # Walls - Collects list of wall types and lengths inthe model for a general report.
            wallTypeAntiKeywords = ["finish", "furring", "gyp", "artwork", "chase", "toilet"]
    
            for wall in allWalls:
                walltype = wall.Name
                if not any(x in walltype.lower() for x in wallTypeAntiKeywords):
                    wallLevel = doc.GetElement(wall.LevelId).Name
    
                    if wallLevel not in allWallsSummary.keys():
                        allWallsSummary[wallLevel] = {}
    
                    if walltype not in allWallsSummary[wallLevel].keys():
                        allWallsSummary[wallLevel][walltype] = [str(wall.WallType.Kind), wall.Location.Curve.Length]
                    else:
                        allWallsSummary[wallLevel][walltype][1] += wall.Location.Curve.Length
    
    
        # Doors - Collects list of doors in the model for a general report
    
            doorHostKeywords = ["storefront", "partition", "glass", "frameless"]
            doorHostAntiKeywords = ["toilet", "gyp"]
    
            for door in allDoors:
                door = rpw.db.Element(door)
                if door.Host:
                    doorHost = str(door.Host.Name) + " - " + str(door.Host.WallType.Kind)
    
                    if any(x in doorHost.lower() for x in doorHostKeywords) and not any(x in doorHost.lower() for x in doorHostAntiKeywords):
    
                        doorFamilyName = door.get_family(wrapped=True).name
                        doorTypeName = door.get_symbol(wrapped=True).name
    
                        if doc.GetElement(door.LevelId):
                            doorLevel = doc.GetElement(door.LevelId).Name
                            doorWidth = door.Symbol.get_Parameter(BuiltInParameter.DOOR_WIDTH).AsValueString()
                            doorHasCardReader = 0
    
                            doorTypeComments = door.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_COMMENTS).AsString()
    
                            doorToRoom = door.ToRoom[doc.GetElement(door.CreatedPhaseId)]
                            doorFromRoom = door.FromRoom[doc.GetElement(door.CreatedPhaseId)]
                            doorRooms = [doorToRoom, doorFromRoom]
    
                            for i in range(len(doorRooms)):
                                #Make sure room is not None.
                                room1 = doorRooms[i]
                                room2 = doorRooms[i-1]
                                if room1:
                                    #Make sure that the door is not an internal office door.
                                    try:
                                        if room1.Id == room2.Id:
                                            continue
                                    except:
                                        pass
    
                                    roomName = room1.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
                                    deskCount = room1.LookupParameter("DeskCount_Room")
                                    if deskCount:
                                        deskCount = deskCount.AsInteger()
                                        if deskCount > 9:
                                            doorHasCardReader = 1
    
    
                            if doorLevel not in allDoorsSummary.keys():
                                allDoorsSummary[doorLevel] = {}
    
                            if doorTypeName not in allDoorsSummary[doorLevel].keys():
                                allDoorsSummary[doorLevel][doorTypeName] = [str(doorFamilyName), doorTypeComments, doorHost, doorWidth, doorHasCardReader, 1]
                            else:
                                allDoorsSummary[doorLevel][doorTypeName][5] += 1
                                allDoorsSummary[doorLevel][doorTypeName][4] += doorHasCardReader
    
        # Specialty Items - Collects list of specialty items for a general report
            specialItemsKeywords = ["whiteboard", "clarus", "glassboard"]
    
            for famInstance in allFamInstances:
                fi = rpw.db.Element(famInstance)
                try:
                    fiFamilyName = fi.get_family(wrapped=True).name
                    fiTypeName = fi.get_symbol(wrapped=True).name
                    fiTypeComments = fi.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_COMMENTS).AsString()
    
                    found = False
    
                    for search in specialItemsKeywords:
                        if search in fiFamilyName.lower():
                            found = True
                            break
    
                    if found:
    
                        fiLevelId = fi.get_Parameter(BuiltInParameter.FAMILY_LEVEL_PARAM).AsElementId()
    
                        if fiLevelId.IntegerValue == -1:
                            fiLevelId = fi.Room[doc.GetElement(fi.CreatedPhaseId)].LevelId
    
                        fiLevel = doc.GetElement(fiLevelId).Name
    
                        fiNameConcat = fiTypeName + " - " + fiFamilyName
    
                        if fiLevel not in allSpecialObjectSummary.keys():
                            allSpecialObjectSummary[fiLevel] = {}
    
                        if fiNameConcat not in allSpecialObjectSummary[fiLevel].keys():
                            allSpecialObjectSummary[fiLevel][fiNameConcat] = [str(fiFamilyName), fiTypeComments, 1]
                        else:
                            allSpecialObjectSummary[fiLevel][fiNameConcat][2] += 1
                except Exception as e:
                    continue
    
            #COLLECT DOOR INFORMATION
    
            for door in allDoors:
                door = rpw.db.Element(door)
                doorFamilyName = door.get_family(wrapped=True).name
                doorTypeName = door.get_symbol(wrapped=True).name
                doorHost = door.Host
                doorDesignOption = door.DesignOption
    
                if door.Id and doorHost:
    
                    if doorDesignOption:
                        if not doorDesignOption.IsPrimary:
                            continue
                    doorEntry = {door.Id.IntegerValue  : {"DoorFamily": doorFamilyName,
                                                                          "HostId": doorHost.Id.IntegerValue}}
    
                    if doorTypeName in doorExportDict.keys():
                        doorExportDict[doorTypeName].update(doorEntry)
                    else:
                        doorExportDict[doorTypeName] = doorEntry
    
    
            # CREATE CUT LIST EXPORT 
            if reportType == "cutlist":
    
                # MULLIONS AND PANELS INHERIT ROOM NUMBERS
                for storefrontWall in allStorefrontWalls:
                    InheritRoomLocation(storefrontWall)
    
    
                #STANDARD LENGTHS FOR CONDITIONS
                sillStandards = systemStandardHorizontals["sill"]
                postStandards = systemStandardVerticals["post"]
                wallstartStandards = systemStandardVerticals["post"]
                doorframeStandards = systemStandardVerticals["doorframe"]
                intermediateStandards = systemStandardVerticals["intermediate"]
                endStandards = systemStandardVerticals["end"]
    
                # CONDITIONS
                for mullion in allStorefrontMullions:
    
                    mullionLength = mullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
    
                    if mullionLength > 0 and mullion.LocationCurve:
    
                        mullionName = mullion.Name.lower()
                        mullionRoom = mullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
                        mullionPoint = mullion.Location.Point
                        mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)
    
                        mullionCurve = mullion.LocationCurve
                        mullionCenter = mullionCurve.Evaluate(0.5, True)
    
                        mullionArea = None
    
                        condition = None
                        varient01 = None
                        varient02 = None
                        conditionComment = None
    
                        # Find which area the condition occurs
                        for areaName, areaPoints in areaBoundaryPoints.items():
                            if PointInPolygon(mullionPoint, areaPoints):
                                mullionArea = areaName
    
                        # ----------------------------- VERTICALS -----------------------------
    
                        # POST Intersections: 2 Way, 3 Way, 4 Way
                        if "post" in mullionName:
    
                            postIntersections = []
                            junctionPoints.append([mullionPoint, mullionName])
                            #Flatten mullion point and set to 0
    
                            testCircle = Ellipse.Create(mullionPoint, 1, 1,XYZ(1.0,0.0,0.0),XYZ(0.0,1.0,0.0),0.0,10.0)
    
                            for storefrontElevation in allStorefrontWalls:
                                storefrontLine = storefrontElevation.Location.Curve
                                sfStart = storefrontLine.GetEndPoint(0)
                                sfEnd = storefrontLine.GetEndPoint(1)
    
                                #Flatten the wall curve for intersection test
                                flatStart = XYZ(sfStart.X, sfStart.Y, 0)
                                flatEnd = XYZ(sfEnd.X, sfEnd.Y, 0)
                                storefrontLintFlat = Line.CreateBound(flatStart, flatEnd)
    
                                #Checks for neighboring intersecting curtain wall
                                intersections = RevitCircleCurveIntersection(storefrontLintFlat, testCircle, filterIntersectionType="Overlap")
    
                                if intersections:
                                    for intersection in intersections:
                                        postIntersections.append(storefrontElevation.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET))
    
                            if postIntersections:
    
                                #If any walls are partial height infered by base offset parameter
                                condition = "POST"
    
                                numIntersection = len(postIntersections)
    
                                varient01 = str(numIntersection) + " WAY"
    
                                #Search for standard lengths in the system config
    
                                for key, standardLength in postStandards.items():
                                    if abs(mullionLength - standardLength) < standardTol:
                                        varient02 = key
                                        break
                                    else:
                                        varient02 = "CUSTOM"
    
                                #Comments
                                if "mode" in systemName.lower():
                                    conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"
    
    
                        # WALL STARTS
                        elif "wallstart" in mullionName:
                            condition = "WALLSTART"
                            varient01 = "1 WAY"
                            junctionPoints.append([mullionPoint, mullionName])
    
                            #Search for standard lengths in the system config
    
                            for key, standardLength in wallstartStandards.items():
                                if abs(mullionLength - standardLength) < standardTol:
                                    varient02 = key
                                    break
                                else:
                                    varient02 = "CUSTOM"
    
                            if "mode" in systemName.lower():
                                conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"
    
    
                        elif "door" in mullionName:
                            condition = "DOORFRAME"
                            doorFramePoints.append([mullionPoint, mullionName])
    
                            varient01 = "TYPICAL"
    
                            for key, standardLength in doorframeStandards.items():
                                if abs(mullionLength - standardLength) < standardTol:
                                    varient02 = key
                                    break
                                else:
                                    varient02 = "CUSTOM"
    
    
                        # INTERMEDIATES
                        elif "intermediate" in mullionName:
                            condition = "INTERMEDIATE"
                            intermediatePoints.append([mullionPoint, mullionName])
    
                            if "double" in mullionName or "intermediate-2" in mullionName:
                                varient01 = "DOUBLE"
                            else: 
                                varient01 = "SINGLE"
    
                            #Search for standard lengths in the system config
    
                            for key, standardLength in intermediateStandards.items():
                                if abs(mullionLength - standardLength) < standardTol:
                                    varient02 = key
                                    break
                                else:
                                    varient02 = "CUSTOM"
    
    
                        # ----------------------------- HORIZONTALS -----------------------------
    
                        elif "sill" in mullionName:
    
                            #Threshold for sill on floor or intermediate sill
    
                            if (mullionCenter.Z-levelElevation) > 2.0:
                                condition = "SILL INTERMEDIATE"
                            else: 
                                condition = "SILL"
    
                            if "double" in mullionName:
                                varient01 = "DOUBLE"
                            else: 
                                varient01 = "SINGLE"
    
                            for key, standardLength in sillStandards.items():
                                if abs(mullionLength - standardLength) < standardTol:
                                    varient02 = key
                                    break
                                else:
                                    varient02 = "CUSTOM"
    
                        if condition:
    
                            conditionEntry = [mullion.Id.IntegerValue,
                                                                      systemName,
                                                                                            condition,
                                                                                            varient01,
                                                                                            varient02,
                                                                                            mullionArea,
                                                                                            mullionRoom, 
                                                                                            mullionLength,
                                                                                            None,
                                                                                            conditionComment]
                            conditionsArray.append(conditionEntry)
    
                allStorefrontMullionsTemp = allStorefrontMullions
    
                headList = []
    
                for mullion in allStorefrontMullionsTemp:
    
                    mullionLength = mullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
    
                    if mullionLength > 0 and mullion.LocationCurve:
    
                        mullionName = mullion.Name.lower()
                        mullionRoom = mullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
                        mullionPoint = mullion.Location.Point
                        mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)
                        mullionArea = None
    
                        mullionCurve = mullion.LocationCurve
                        mullionCenter = mullionCurve.Evaluate(0.5, True)
                        mullionCenter = XYZ(mullionCenter.X, mullionCenter.Y, 0)
    
                        storefrontHostHeight = mullion.Host.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
    
                        condition = None
                        varient01 = None
                        varient02 = None
    
                        # Find which area the condition occurs
                        for areaName, areaPoints in areaBoundaryPoints.items():
                            if PointInPolygon(mullionPoint, areaPoints):
                                mullionArea = areaName
    
    
                        mullionElevation = mullion.GetTransform().Origin.Z
    
                        # ----------------------------- ENDS -----------------------------
    
                        # Use sills to find end conditions and test lengths	
                        if detectEndConditions:
                            if "sill" in mullionName:
    
                                # Check against junctions (wallstarts and posts)
                                for i in range(len(junctionPoints)):
                                    testPoint = junctionPoints[i][0]
                                    testDist = testPoint.DistanceTo(mullionCenter)
                                    if testDist < ((mullionLength/2) + 0.33):
    
                                        condition = "END"
                                        varient01 = None
                                        varient02 = None
                                        conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"
    
                                        if "offset" in  mullionName.lower():
                                            varient01 = "OFFSET"
                                        elif "center" in  mullionName.lower():
                                            varient01 = "CENTER"
                                        elif "double" in  mullionName.lower():
                                            varient01 = "DOUBLE"
    
                                        for key, standardLength in endStandards.items():
                                            if abs(storefrontHostHeight - standardLength) < standardTol:
                                                varient02 = key
                                                break
                                            else:
                                                varient02 = "CUSTOM"
    
                                        conditionEntry = [mullion.Id.IntegerValue,
                                                                                              systemName,
                                                                                                            condition,
                                                                                                            varient01,
                                                                                                            varient02,
                                                                                                            mullionArea,
                                                                                                            mullionRoom, 
                                                                                                            storefrontHostHeight,
                                                                                                            None,
                                                                                                            conditionComment]
                                        conditionsArray.append(conditionEntry)
    
                                # Check against door frames
                                for i in range(len(doorFramePoints)): 
                                    doorFrameName = doorFramePoints[i][1]
                                    testPoint = doorFramePoints[i][0]
                                    testDist = testPoint.DistanceTo(mullionCenter)
    
                                    # Check if the centerpoint of the panel is within tolerance 
                                    # to an end conditions
                                    if testDist < ((mullionLength/2) + 0.33):
    
                                        condition = "END"
                                        varient01 = None
                                        varient02 = None
                                        conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"
    
                                        if "offset" in  mullionName.lower():
                                            if ("mid" in doorFrameName) and ("door" in doorFrameName):
                                                varient01 = "CENTER"
                                            else:
                                                varient01 = "OFFSET"
                                        elif "center" in  mullionName.lower():
                                            varient01 = "CENTER"
                                        elif "double" in  mullionName.lower():
                                            varient01 = "DOUBLE"
    
                                        else:
                                            print doorFrameName
    
                                        for key, standardLength in endStandards.items():
                                            if abs(storefrontHostHeight - standardLength) < standardTol:
                                                varient02 = key
                                                break
                                            else:
                                                varient02 = "CUSTOM"
    
                                        conditionEntry = [mullion.Id.IntegerValue,
                                                                                                      systemName,
                                                                                                            condition,
                                                                                                            varient01,
                                                                                                            varient02,
                                                                                                            mullionArea,
                                                                                                            mullionRoom, 
                                                                                                            storefrontHostHeight,
                                                                                                            None,
                                                                                                            conditionComment]
                                        conditionsArray.append(conditionEntry)
    
    
                        # ----------------------------- HEADS -----------------------------
    
                        # Search for head mullions and chain together if they are continuous
                        if "head" in mullionName:
                            searchingForChain = True
                            searchTol = 0.01
                            while searchingForChain:
    
                                foundNeighbor = False
                                mullion1Start = mullionCurve.GetEndPoint(0)
                                mullion1End = mullionCurve.GetEndPoint(1)
                                mullion1Endpoints = [mullion1Start, mullion1End]
    
                                for mullion2 in allStorefrontMullionsTemp:
    
                                    if "head" in mullion2.Name.lower() and mullion2 != mullion:
                                        mullion2Curve = mullion2.LocationCurve
                                        mullion2Start = mullion2Curve.GetEndPoint(0)
                                        mullion2End = mullion2Curve.GetEndPoint(1)
                                        mullion2Endpoints = [mullion2Start, mullion2End]
    
                                        for i in range(len(mullion1Endpoints)):
                                            point1a = mullion1Endpoints[i]
                                            point1b = mullion1Endpoints[i-1]
                                            for j in range(len(mullion2Endpoints)):
                                                point2a = mullion2Endpoints[j]
                                                point2b = mullion2Endpoints[j-1]
                                                dist = point1a.DistanceTo(point2a)
                                                if dist < searchTol:
                                                    angle = AngleThreePoints(point1b, point1a, point2b)
                                                    #print angle
                                                    if abs(angle-180) < searchTol:
                                                        allStorefrontMullions.remove(mullion2)
                                                        mullionCurve = Line.CreateBound(point1b, point2b)
    
                                                        foundNeighbor = True
                                                        break
                                    if foundNeighbor:
                                        break
                                if not foundNeighbor:
                                    searchingForChain = False
    
                            headList.append([mullionCurve, mullion.Id, mullionRoom, mullionArea ])
    
                            condition = "HEAD"
                            varient01 = "TYPICAL"
                            varient02 = "CUSTOM"
    
    
                            conditionEntry = [mullion.Id.IntegerValue,
                                                                      systemName,
                                                                                                    condition,
                                                                                                    varient01,
                                                                                                    varient02,
                                                                                                    mullionArea,
                                                                                                    mullionRoom, 
                                                                                                    mullionCurve.Length,
                                                                                                    None,
                                                                                                    conditionComment]
                            conditionsArray.append(conditionEntry)
    
                # ----------------------------- DEFLECTION HEADS -----------------------------
    
                startHeadToMaintainInline = []
                headToMaintainInline = []
    
                startAndEndIntersections = []
    
                for head1 in headList:
                    mullionCurve = head1[0]				
    
                    mullionStart = mullionCurve.GetEndPoint(0)
                    mullionStart = XYZ(mullionStart.X, mullionStart.Y, 0)
    
                    mullionEnd = mullionCurve.GetEndPoint(1)
                    mullionEnd = XYZ(mullionEnd.X, mullionEnd.Y, 0)
    
                    mullionEndpoints = [mullionStart, mullionEnd]
    
                    endIntersections = []
                    startIntersections = []
    
                    headToMaintainInline.append(False)
    
    
                    #print "---------------------------"
                    #print head1[1]
    
                    for i in range(len(mullionEndpoints)):
                        pt1 = mullionEndpoints[i]
                        pt2 = mullionEndpoints[i-1]
    
                        startNeighbors = []
                        endNeighbors = []
    
                        #print str(i) + " -----"
    
                        for head2 in headList:
    
                            if head1 != head2:
                                mullion2Curve = head2[0]
    
                                mullion2Start = mullion2Curve.GetEndPoint(0)
                                mullion2Start = XYZ(mullion2Start.X, mullion2Start.Y, 0)
    
                                mullion2End = mullion2Curve.GetEndPoint(1)
                                mullion2End = XYZ(mullion2End.X, mullion2End.Y, 0)
    
                                mullion2Endpoints = [mullion2Start, mullion2End]
    
    
                                for j in range(len(mullion2Endpoints)):
                                    pt3 = mullion2Endpoints[j]
                                    pt4 = mullion2Endpoints[j-1]
    
                                    testDist = pt1.DistanceTo(pt3)
    
                                    #searches for nearby heads at inline and corners
                                    if testDist < 0.4:
    
                                        #found a neighbor
    
                                        vect1 = XYZ(pt2.X - pt1.X, pt2.Y - pt1.Y, pt2.Z - pt1.Z)
                                        vect2 = XYZ(pt4.X - pt3.X, pt4.Y - pt3.Y, pt4.Z - pt3.Z)
                                        testAngle = ((vect1.AngleTo(vect2)*360)/ (2*math.pi))
    
                                        refVector = XYZ(1,0,0)
    
                                        dot = (vect1.X * vect2.X) + (vect1.Y * vect2.Y)
                                        det = (vect1.X * vect2.Y) + (vect1.Y * vect2.X)
                                        testAngle2 = (math.atan2(det,dot)*360)/ (2*math.pi)
    
                                        refdot = (vect1.X * refVector.X) + (vect1.Y * refVector.Y)
                                        refdet = (vect1.X * refVector.Y) + (vect1.Y * refVector.X)
                                        refAngle = round((math.atan2(refdet,refdot)*360)/ (2*math.pi),3)
    
                                        #print testAngle2
                                        #print refAngle	
                                        #flipping because the vector angle flips based on orientation
    
                                        if (abs(refAngle) > 135 or abs(refAngle) < 45) or refAngle == -135 or refAngle == 45:
                                            testAngle2 = testAngle2*-1
    
    
                                        if i == 0:
                                            startIntersections.append([testAngle, headList.index(head2), testAngle2])
                                            #startNeighbors.append([testAngle, headList.index(headCurve2)])
                                            #print "Start: " + str(testAngle)
    
                                        elif i == 1:
                                            endIntersections.append([testAngle, headList.index(head2), testAngle2])
                                            #print "End: " + str(testAngle)
    
    
    
                                        #endIntersections.append("", testAngle)
    
                    startAndEndIntersections.append([startIntersections, endIntersections])
    
                for head1 in headList:	
    
                    #-------------Junction testing and offset setting------------------
                    headCurveIndex = headList.index(head1)
                    curveIntersections = startAndEndIntersections[headCurveIndex]
    
                    startAndEndOffsets = [0,0]
                    conditionComment = ""
    
                    #print "----------------------------------"
                    #print head1[1]
    
                    for index in range(len(curveIntersections)):
    
                        intersectionSet = curveIntersections[index]
                        offsetAmount = 0
                        fabComments = []
    
    
                        #listToMaintainInline = startAndEndToMaintainInline[index]
                        if len(intersectionSet) == 0:
                            offsetAmount = storefrontConfig.currentConfig["headOffsetAtEndCondition"]
                            fabComments.append(storefrontConfig.currentConfig["headFabAtEndCondition"])
                        #Corner/Inline
    
                        elif len(intersectionSet) == 1:
    
                            ang = intersectionSet[0][0]
                            rotAng = intersectionSet[0][2]
                            #Corner
    
                            if abs(abs(ang) - 90) < 1.0:
                                offsetAmount = storefrontConfig.currentConfig["headOffsetAtCornerCondition"]
    
                                if rotAng < 0:
                                    fabComments.append(storefrontConfig.currentConfig["headFabAtCornerCondition-Right"])
                                else:
                                    fabComments.append(storefrontConfig.currentConfig["headFabAtCornerCondition-Left"])
    
                            #Inline
                            elif abs(abs(ang) - 180) < 1.0:
                                offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]
                                fabComments.append(storefrontConfig.currentConfig["headFabAtInlineCondition"])
                            else:
                                print "odd angle"
                                if rotAng < 0:
                                    fabComments.append("ODD-RIGHT")
                                else:
                                    fabComments.append("ODD-LEFT")
    
                        #TBone/Inline+Corner
                        elif len(intersectionSet) > 1:
                            inlineCount = 0
                            cornerCount = 0
                            cornersList = []
                            oddCount = 0
    
                            #Build condition counts to evaluate
                            for intNeighbor in intersectionSet:
                                ang = intNeighbor[0]
    
                                #Corner
                                if abs(abs(ang) - 90) < 1.0:
                                    cornerCount += 1
                                    cornersList.append(intNeighbor[2])
                                #Inline
                                elif abs(abs(ang) - 180) < 1.0:
                                    inlineCount += 1
                                else:
                                    oddCount += 1
    
    
                            #Evaluate condition counts
    
                            # Corner & Inline
                            if inlineCount == 1 and cornerCount == 1 and oddCount == 0:
                                offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]
    
                                # add fab comments for these cordners
                                for rotAng in cornersList:
                                    if rotAng < 0:
                                        fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Right"])
                                    else:
                                        fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Left"])
    
    
                            # Corner & Corner (TBone)
                            elif inlineCount == 0 and cornerCount == 2 and oddCount == 0:
                                offsetAmount = storefrontConfig.currentConfig["headOffsetAtTBoneCondition"]
                                fabComments.append(storefrontConfig.currentConfig["headFabAtTBoneCondition"])
    
                            # Inline & Corner & Corner (4Way)
                            elif inlineCount == 1 and cornerCount == 2 and oddCount == 0:
    
                                #check corner neighbors to see if they have an inline to maintain
                                setNeighborToMaintainInline = False
    
                                selfToMaintainInline = headToMaintainInline[headCurveIndex]
    
                                #fist check if the current curve should maintain inline
    
                                # If already should maintain inline, set the offset
                                if selfToMaintainInline:
                                    offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]
    
                                    # add fabs at corners if needed
                                    for rotAng in cornersList:
                                        if rotAng < 0:
                                            fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Right"])
                                        else:
                                            fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Left"])
    
                                else: 
    
                                    #check neighbors in the intersection set
                                    for neighborToCheck in intersectionSet:
                                        neighborAngle = neighborToCheck[0]
                                        neighborIndex = neighborToCheck[1]
    
                                        #if they are corners, see if they already should maintain inline
                                        if abs(abs(neighborAngle) - 90) < 1.0: 
    
                                            #if they do, consider the current offset a TBone 
                                            if headToMaintainInline[neighborIndex]:
                                                offsetAmount = storefrontConfig.currentConfig["headOffsetAtTBoneCondition"]
                                                fabComments.append(storefrontConfig.currentConfig["headFabAtTBoneCondition"])
                                                break
    
                                            #otherwise consider an inline and set the self and neighbor to True
                                            else:
                                                offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]
                                                headToMaintainInline[headCurveIndex] = True
                                                setNeighborToMaintainInline = True
                                                #print "set self to True"
    
                                                # add fabs at corners if needed
                                                fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Right"])
                                                fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Left"])
    
                                                for neighborToCheck2 in intersectionSet:
                                                    neighborAngle2 = neighborToCheck2[0]
                                                    neighborIndex2 = neighborToCheck2[1]
    
                                                    if abs(abs(neighborAngle2) - 180) < 1.0: 
                                                        headToMaintainInline[neighborIndex2] = True
                                                        #print "set my neighbor to True"
                                                break
    
    
    
                            # Inline with Odd corner
                            elif inlineCount == 1 and oddCount > 0:
                                offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]
    
                            # Odd corners requires 
                            elif inlineCount == 0 and oddCount > 0:
                                manualDimension = "Drop error marker and notify user"
                                print "odd multi corner"
    
                        #Set the offset
                        startAndEndOffsets[index] = offsetAmount
                        if index == 1:
                            conditionComment += " | "
                        conditionComment += (" + ".join(str(e) for e in fabComments))
    
    
    
    
    
    
                    headLength = sum(startAndEndOffsets) + head1[0].Length
    
                    condition = "DEFLECTION BASE"
                    varient01 = "TYPICAL"
                    varient02 = "CUSTOM"
    
    
                    conditionEntry = [head1[1],
                                                      systemName,
                                                                                    condition,
                                                                                    varient01,
                                                                                    varient02,
                                                                                    head1[3],
                                                                                    head1[2], 
                                                                                    headLength,
                                                                                    None,
                                                                                    conditionComment]
                    conditionsArray.append(conditionEntry)
    
    
    
    
                    #----------------------Cutlist Export Configuration----------------------#
                    """
                                    self.currentConfig["headOffsetAtEndCondition"] = 2.066929/12        #52.5mm
                                    self.currentConfig["headOffsetAtTBoneCondition"] = -0.0984252/12    #-2.5mm
                                    self.currentConfig["headOffsetAtCornerCondition"] = 4.2322835/12    #107.5mm
                                    self.currentConfig["headOffsetAtInlineCondition"] = 2.066929/12     #52.5mm
                                    self.currentConfig["headOffsetAtFourwayCondition"] = 2.066929/12    #52.5mm
                                    """
    
    
    
                #TODO: Use empty panels to find closest door on storefront and create condition entry 
                #TODO: Get deflection head condition per storefront centerline length
    
                """
                            if allDoorsSummary:
                                    #["LEVEL", "REVIT FAMILY", "REVIT TYPE", "REVIT TYPE COMMENTS", "HOST WALLTYPE", "WIDTH", "CARD READER - COUNT", "TOTAL - COUNT"])
                                    conditionsArray = [["ELEMENT", "SYSTEM", "CONDITION", "VARIENT 01", "VARIENT 02", "AREA", "ROOM", "LENGTH", "WIDTH", "COMMENT"]]
                                    for doorLev in sorted(allDoorsSummary.keys()):
                                            if levelName.lower() in doorLev.lower():
                                                    for doorTypeName in sorted(allDoorsSummary[doorLev].keys()):
                                                            doorFamName = allDoorsSummary[doorLev][doorTypeName][0]
                                                            dtc = allDoorsSummary[doorLev][doorTypeName][1]
                                                            dh = allDoorsSummary[doorLev][doorTypeName][2]
                                                            dw = allDoorsSummary[doorLev][doorTypeName][3]
                                                            dcr = allDoorsSummary[doorLev][doorTypeName][4]
                                                            dc = allDoorsSummary[doorLev][doorTypeName][5]
    
                                                            conditionEntry = [None,
                                                                                                    systemName,
                                                                                                    doorFamName,
                                                                                                    doorTypeName,
                                                                                                    None,
                                                                                                    None,
                                                                                                    None, 
                                                                                                    storefrontHostHeight,
                                                                                                    None,
                                                                                                    conditionComment]
    
                                                            conditionsArray.append([doorLev, doorFamName, doorTypeName, dtc, dh, dw, str(dcr), str(dc)])
    
                            """
    
                for storefrontElevation in allStorefrontWalls:
    
                    panelIds = storefrontElevation.CurtainGrid.GetPanelIds()
                    #mullionIds = storefrontElevation.CurtainGrid.GetMullionIds()
    
                    linearGlass = storefrontElevation.Location.Curve.Length
    
                    storefrontElevationID = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
                    storefrontSuperType = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
    
    
    
    
                    #Panels
                    for panelId in panelIds:
    
                        panel = doc.GetElement(panelId)
                        panelWidth = panel.get_Parameter(BuiltInParameter.WINDOW_WIDTH).AsDouble()
                        panelHeight = panel.get_Parameter(BuiltInParameter.WINDOW_HEIGHT).AsDouble()
    
                        if (panelWidth > 0) and (panelHeight > 0):
    
                            condition = None
                            varient01 = None
                            varient02 = None
    
                            panelFamily = panel.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
                            panelType = panel.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
                            panelSF = panelWidth * panelHeight
                            panelSizeName = str(panelWidth) + " x " + str(panelHeight)
    
                            #Get panel point and flatten
                            panelPoint = panel.GetTransform().Origin
                            panelPoint = XYZ(panelPoint.X, panelPoint.Y, 0)
    
                            panelRoomID = panel.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
    
                            # Find which area the condition occurs
                            panelArea = None
                            for areaName, areaPoints in areaBoundaryPoints.items():
                                if PointInPolygon(panelPoint, areaPoints):
                                    panelArea = areaName
    
                            #Default panel position
                            panelPositions = []
    
                            # Checking end conditions against junctions (post, wallstart, and door frames)
                            juntionsAndDoorFrames = junctionPoints + doorFramePoints
    
                            if "glazed" in panelFamily.lower():
                                #print "-----------------------------"
                                #print panel.Id
    
                                condition = "GLASS"
    
                                if "double" in panelType.lower():
                                    varient01 = "DOUBLE"
                                else:
                                    varient01 = "SINGLE"
    
                                varient02 = "CUSTOM"
    
    
                                panelComment = "EXACT GLASS SIZE! - INCLUDES AMOUNT IN POCKET "
    
    
                                numFoundEndConditions = 0
    
                                #CORRECT PANEL WIDTH + HEIGHT FOR ACTUAL SIZES
                                # Add correction for differences between modeling and reality
    
                                glassWidthCorrection = 0
                                glassHeightCorrection = 0
    
                                #Ends
                                for i in range(len(juntionsAndDoorFrames)):
                                    testPoint = juntionsAndDoorFrames[i][0]
                                    testMullionName = juntionsAndDoorFrames[i][1]
                                    testDist1 = testPoint.DistanceTo(panelPoint)
    
                                    if testDist1 < ((panelWidth/2) + (2.1/12)):
                                        glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]
                                        numFoundEndConditions += 1 #Found an end condition
                                        #print storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]
    
                                #Intermediates
                                for i in range(len(intermediatePoints)):
                                    testPoint = intermediatePoints[i][0]
                                    testMullionName = intermediatePoints[i][1]
                                    testDist2 = testPoint.DistanceTo(panelPoint)
    
                                    if testDist2 < ((panelWidth/2) + (1.8/2)):
                                        glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]
                                        numFoundEndConditions += 1 #Found an end condition
                                        #print storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]
    
                                #Butt joints
                                numButtJoints = 2 - numFoundEndConditions #Glass has 2 ends, if above conditions arent detected, its assumed a butt joint is found
                                glassWidthCorrection += (numButtJoints * storefrontConfig.currentConfig["panelCorrections"]["horizontalButtJoint"])
    
                                #print numButtJoints
    
    
                                #Head and Sill pockets
                                glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalSill"]
                                glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalHead"]
    
    
                                conditionEntry = [panelId.IntegerValue,
                                                                              systemName,
                                                                                            condition,
                                                                                            varient01,
                                                                                            varient02,
                                                                                            panelArea,
                                                                                            panelRoomID, 
                                                                                            panelWidth + glassWidthCorrection,
                                                                                            panelHeight + glassHeightCorrection,
                                                                                            panelComment]
                                conditionsArray.append(conditionEntry)
    
    
    
    
                print("...SAVE REPORT")
                save_file = SaveFileDialog()
                save_file.FileName  = (projectName + "_CUTLIST REPORT_" + todaysDate.replace("/","")) + ".csv"
                print(save_file.FileName)
                save_file.Filter = "CSV files (*.csv)|*.csv|Excel Files|*.xls;*.xlsx;*.xlsm"
                save_file.ShowDialog()
    
    
                try:
                    writeList = []
                    writeList.append(["PROJECT NAME", "REPORT AUTHOR", "REPORT DATE"])
                    writeList.append([projectName, currentUser, todaysDate])
    
                    writeList.append([" "])
                    writeList.append([" "])
                    writeList.append(["CONDITIONS"])
    
    
                    with open(save_file.FileName, 'w') as f:
                        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                        for row in conditionsArray:
                            writer.writerow(row)
                        #  Writing to csv
                    os.startfile(save_file.FileName)
                except Exception as inst:
                    OutputException(inst)
    
    
    
    
            if reportType == "takeoff":
    
                print "...SAVE REPORT"
                save_file = SaveFileDialog()
                save_file.FileName  = (projectName + "_MATERIAL REPORT_" + todaysDate.replace("/","")) + ".csv"
                print save_file.FileName
                save_file.Filter = "CSV files (*.csv)|*.csv|Excel Files|*.xls;*.xlsx;*.xlsm"
                save_file.ShowDialog()
    
    
                try:
                    writeList = []
                    writeList.append(["PROJECT NAME", "REPORT AUTHOR", "REPORT DATE"])
                    writeList.append([projectName, currentUser, todaysDate])
    
                    """
                                    writeList.append(["STOREFRONT TYPE","LINEAR FT"])
                                    writeList.append(["Full Height w/ Glass:",linearFull])
                                    writeList.append(["Full Height @ Door:",linearDoors])
                                    writeList.append(["Partial Height:",linearPartial])
                                    writeList.append([" "])
    
    
                                    #ProfileSummary
                                    writeList.append(["PROFILE TYPE","LINEAR FT", "COUNT"])
                                    for mullionType in mullionExportDict.keys():
                                            linearMullion = 0
                                            countMullion = 0
                                            for entry in mullionExportDict[mullionType].keys():
                                                    linearMullion += mullionExportDict[mullionType][entry]["Length"]
                                                    countMullion += 1
                                            writeList.append([mullionType, linearMullion, countMullion])
                                    writeList.append([" "])
    
                                    #Glass Summary
                                    writeList.append(["OTHER","SQUARE FT", "COUNT"])
                                    writeList.append(["Glass:",areaGlass, countGlass])
                                    writeList.append(["Infill Panel:",areaInfillPanel, countInfillPanel])
                                    writeList.append([" "])
    
                                    #Door Summary
                                    writeList.append(["DOOR TYPE", "DOOR FAMILY", "COUNT"])
                                    for doorType in doorExportDict.keys():
                                            doorCount = 0
                                            doorFamilyName = None
                                            for entry in doorExportDict[doorType].keys():
                                                    doorCount += 1
                                                    doorFamilyName = doorExportDict[doorType][entry]["DoorFamily"]
                                            writeList.append([doorType, doorFamilyName, doorCount])
                                    writeList.append([" "])
                                    writeList.append([" "])
                                    """
    
    
                    if allWallsSummary:
                        writeList.append([" "])
                        writeList.append([" "])
                        writeList.append(["WALLS"])
                        writeList.append(["LEVEL", "REVIT WALL TYPE", "REVIT WALL KIND", "LINEAR FT (INCLUDES DOOR WIDTH)"])
                        writeList.append([" "])
                        for wallLev in sorted(allWallsSummary.keys()):
                            if "container" not in wallLev.lower():
                                writeList.append([" "])
                                for wallType in sorted(allWallsSummary[wallLev].keys()):
                                    wallKind = allWallsSummary[wallLev][wallType][0]
                                    wallLength = allWallsSummary[wallLev][wallType][1]
                                    writeList.append([wallLev, wallType, wallKind, str(wallLength)])
    
                    if allDoorsSummary:
                        writeList.append([" "])
                        writeList.append([" "])
                        writeList.append(["DOORS"])
                        writeList.append(["LEVEL", "REVIT FAMILY", "REVIT TYPE", "REVIT TYPE COMMENTS", "HOST WALLTYPE", "WIDTH", "CARD READER - COUNT", "TOTAL - COUNT"])
                        for doorLev in sorted(allDoorsSummary.keys()):
                            if "container" not in doorLev.lower():
                                writeList.append([" "])
                                for doorTypeName in sorted(allDoorsSummary[doorLev].keys()):
                                    doorFamName = allDoorsSummary[doorLev][doorTypeName][0]
                                    dtc = allDoorsSummary[doorLev][doorTypeName][1]
                                    dh = allDoorsSummary[doorLev][doorTypeName][2]
                                    dw = allDoorsSummary[doorLev][doorTypeName][3]
                                    dcr = allDoorsSummary[doorLev][doorTypeName][4]
                                    dc = allDoorsSummary[doorLev][doorTypeName][5]
                                    writeList.append([doorLev, doorFamName, doorTypeName, dtc, dh, dw, str(dcr), str(dc)])
    
                    if allSpecialObjectSummary:
                        writeList.append([" "])
                        writeList.append([" "])
                        writeList.append(["SPECIALTY ITEMS"])
                        writeList.append(["LEVEL", "REVIT FAMILY", "REVIT TYPE", "REVIT TYPE COMMENTS", "TOTAL - COUNT"])
                        for fiLevel in sorted(allSpecialObjectSummary.keys()):
                            if "container" not in fiLevel.lower():
                                writeList.append([" "])
                                for fiTypeName in sorted(allSpecialObjectSummary[fiLevel].keys()):
                                    fiFamilyName = allSpecialObjectSummary[fiLevel][fiTypeName][0]
                                    fiTypeComments = allSpecialObjectSummary[fiLevel][fiTypeName][1]
                                    fiCount = allSpecialObjectSummary[fiLevel][fiTypeName][2]
                                    writeList.append([fiLevel, fiFamilyName, fiTypeName, fiTypeComments, str(fiCount)])
    
    
                    with open(save_file.FileName, 'w') as f:
                        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                        for row in writeList:
                            writer.writerow(row)
                        #  Writing to csv
                    os.startfile(save_file.FileName)
                except Exception as inst:
                    OutputException(inst)
    
    
            """
                    elif reportType == "cutlist":
    
                            profileDict = GetProfileDict("I-Profile-Storefront-Mullion")
    
                            #Storefront Conditions
                            ##  Office Front Singe
                            ##  Office Front Double 
                            ##  Cross Wall Single
                            ##  Cross Wall Double
                            ##  4 Way
                            ##  3 way
                            ##  2 Way
                            ##  Wall Start
                            ##  Sliding Door
                            ##  Swing Door
    
                            #collect posts & wall starts
                            #get their center points
                            #detect intersection onto other curtain wall locaiton lines
                            #collect intersection and walltype data
                            #compare to map of intersection types and tally them up
    
    
    
                            try:
                                    print "...SAVE CUTLIST"
                                    save_file = SaveFileDialog()
                                    save_file.FileName  = (projectName + "_" + levelName + "_CUT LIST_" + todaysDate.replace("/","")) + ".csv"
                                    print save_file.FileName
                                    save_file.Filter = "CSV files (*.csv)|*.csv|Excel Files|*.xls;*.xlsx;*.xlsm"
                                    save_file.ShowDialog()
                            except:
                                    pass
    
                            writeList = []
                            writeList.append(["PROJECT NAME", "LEVEL NAME", "REPORT AUTHOR", "REPORT DATE"])
                            writeList.append([projectName, levelName, currentUser, todaysDate])
    
                            # Iterate through the dictionary and create cutlist for verticals
                            writeList.append([" "])
                            writeList.append(["VERTICALS"])
                            writeList.append(["PROFILE TYPE","PART NUMBER", "CUT LENGTH", "COUNT"])
    
                            # Write posts here.
                            #writeList.append(["Post","1501 x 2 (solid)", frameHeadHeight, int(len(fullPostPoints)/2)])
                            #writeList.append(["Post","1501 x 2 (solid)", frameHeadHeight-frameSillHeight, int(len(partialPostPoints)/2)])
    
                            # Write the rest of ther vertical here
                            for key in profileDict.keys():
                                    uniqueLengths = [[],[]]
                                    for i in range(len(profileDict[key][1])):
                                            partNumber = profileDict[key][0]
                                            length = profileDict[key][1][i]
                                            assemId = profileDict[key][2][i]
                                            frameId = profileDict[key][3][i]
    
                                            if "Head" not in key and "Sill" not in key and "Post" not in key:
                                                    if length not in uniqueLengths[0]:
                                                            uniqueLengths[0].append(length)
                                                            uniqueLengths[1].append(1)
                                                    else:
                                                            uniqueLengths[1][uniqueLengths[0].index(length)] += 1
                                    for i in range(len(uniqueLengths[0])):
                                            writeList.append([key, partNumber, uniqueLengths[0][i], uniqueLengths[1][i]])
    
    
                            # Iterate through the dictionary and create cutlist for horizontals
                            writeList.append([" "])
                            writeList.append(["HORIZONTALS "])
                            writeList.append(["PROFILE TYPE","PART NUMBER", "CUT LENGTH", "ASSEMBLY ID", "FRAME ID", "NOTE"])
                            for key in profileDict.keys():
                                    for i in range(len(profileDict[key][1])):
                                            if "Head" in key or "Sill" in key:
                                                    partNumber = profileDict[key][0]
                                                    length = profileDict[key][1][i]
                                                    assemId = profileDict[key][2][i]
                                                    frameId = profileDict[key][3][i]
                                                    note = profileDict[key][4][i]
                                                    writeList.append([key, partNumber, length, assemId, frameId, note])
    
                            writeList.append([" "])
                            writeList.append(["GLASS "])
                            writeList.append(["X DIM","Y DIM", "AREA", "ASSEMBLY ID", "FRAME ID", "NOTE"])
                            for glass in glassList:
                                    writeList.append(glass)
    
                            try:
                                    with open(save_file.FileName, 'w') as f:
                                            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                                            for row in writeList:
                                                    writer.writerow(row)
                            except Exception as inst:
                                    OutputException(inst)
                            try:
                                    # initialize writing to csv
                                    os.startfile(save_file.FileName)
                            except Exception as inst:
                                    OutputException(inst)
                    print "FINISHED"
                    """
    
            # added return to allow IDE function collapse
            return(True)
    
        # 168 LINES OF CODE - HOW WAS THIS USED???
        def storefront_extract(self):
            #TODO:  Implement rpw transactions, collectors, and filters. 
    
            version = __revit__.Application.VersionNumber.ToString()
    
            storefrontFull = []
            storefrontPartial = []
            selectedLevels = []
            storefrontFullLines = []
            storefrontPartialLines = []
            interiorWallsLines = []
    
            doc = __revit__.ActiveUIDocument.Document
    
            storefrontViewTypeName = "Laser Layout"
            storefrontViewUse = "Laser Layout"
            storefrontViewScale = 96
    
            subCatIdList = []
            lineSubCatsToEnsure = [["WW_StorefrontFull",Autodesk.Revit.DB.Color(0,60,175),8],
                                           ["WW_StorefrontPartial",Autodesk.Revit.DB.Color(0,200,0),8],
                                                               ["WW_InteriorWall",Autodesk.Revit.DB.Color(100,100,100),4],
                                                               ["WW_InteriorWallEdge",Autodesk.Revit.DB.Color(200,100,100),3],
                                                               ["WW_RoomBoundary",Autodesk.Revit.DB.Color(255,0,0),2],
                                                               ["WW_FloorEdge",Autodesk.Revit.DB.Color(100,100,100),2],
                                                               ["WW_ExistingConditions",Autodesk.Revit.DB.Color(50,50,50),5],
                                                               ["WW_DeskOutlines",Autodesk.Revit.DB.Color(0,60,175),2],
                                                               ["WW_StorefrontMullions",Autodesk.Revit.DB.Color(0,60,175),2],
                                                               ["WW_ControlLines",Autodesk.Revit.DB.Color(255,0,0),5]]
    
            # Load configuration object  ---------------------------------------------------------------
            storefrontConfig = storefront_options()
            storefrontConfig.storefront_load_families(True)
    
            # Get family dict object
            familyDict = storefrontConfig.currentConfig["families"]
    
            # Get elements from ec model ---------------------------------------------------------------
            selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id
    
    
            # Get all the elements needed in main doc ---------------------------------------------------------------
            allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
            allViews = GetAllElements(doc, BuiltInCategory.OST_Views, Autodesk.Revit.DB.View)
            allViewPlans = GetAllElements(doc, BuiltInCategory.OST_Views, Autodesk.Revit.DB.ViewPlan)
    
            # Filter by name ---------------------------------------------------------------
            storefrontFull = FilterElementsByName(doc, allWalls,["Storefront","Full"], False)
            storefrontPartial = FilterElementsByName(doc, allWalls,["Storefront","Partial"], False)
            interiorWalls = FilterElementsByName(doc, allWalls,["Storefront","Storefront"], True)
            laserViewPlan = FilterElementsByName(doc, allViewPlans,["Laser","Layout"], False)
    
            if not laserViewPlan:
                laserViewPlan = FilterElementsByName(doc, allViewPlans,["Working","Working"], False)
    
            # Makes sure no stacked walls are included  ---------------------------------------------------------------
            tempList = []
            for wallId in interiorWalls:
                wall = doc.GetElement(wallId)
                if not wall.IsStackedWallMember:
                    tempList.append(wallId)
            interiorWalls = tempList
    
            #Extract curves from elements ---------------------------------------------------------------
    
            storefrontFullLines = SF2_Utility.GetWallLocationCurves(doc, storefrontFull)
            storefrontPartialLines = SF2_Utility.GetWallLocationCurves(doc, storefrontPartial)
            interiorWallsLines = SF2_Utility.GetWallLocationCurves(doc, interiorWalls)
    
            #Split curves as they are intersected ---------------------------------------------------------------
    
            allLines  = storefrontFullLines + storefrontPartialLines + interiorWallsLines
    
            temp = []
            for line in storefrontFullLines:
                intersections = []
                for testLine in allLines:
                    if testLine != line:
                        intersection = RevitCurveCurveIntersection(line, testLine, filterIntersectionType="Overlap")
                        if intersection:
                            intersections.append(intersection)
    
                temp += RevitSplitLineAtPoints(line, intersections)
            storefrontFullLines = temp
    
            temp = []
            for line in storefrontPartialLines:
                intersections = []
                for testLine in allLines:
                    if testLine != line:
                        intersection = RevitCurveCurveIntersection(line, testLine, filterIntersectionType="Overlap")
                        if intersection:
                            intersections.append(intersection)
    
                temp += RevitSplitLineAtPoints(line, intersections)
            storefrontPartialLines = temp
    
            #Setup line syles  ---------------------------------------------------------------
            subCatIdList = SetupLineStyles(lineSubCatsToEnsure)
            existingViewsFound = False
    
            levelInst = doc.GetElement(selectedLevel)
            levelName = None
            for p in levelInst.Parameters:
                if p.Definition.Name == "Name":
                    levelName = p.AsString()
    
            #Check if theres an existing view  ---------------------------------------------------------------
            for viewId in allViews:
                viewInDoc = doc.GetElement(viewId)
                if levelName + " Laser Layout" == viewInDoc.Name:
                    existingViewsFound = True
                    viewToUpdate = viewId
                    break
    
            if existingViewsFound:
                with rpw.db.Transaction("Clear Laser Layout View"):
                    print("{0}...CLEARING VIEW...".format(levelName))
                    DeleteElementsInView(viewToUpdate, BuiltInCategory.OST_Lines, optionalKeyword="Detail Lines")
                    #DeleteElementsInView(viewToUpdate, BuiltInCategory.OST_DetailComponents)
                    #DeleteElementsInView(viewToUpdate, BuiltInCategory.OST_GenericAnnotation)
    
    
            #Make/Update view ---------------------------------------------------------------
            with rpw.db.Transaction("Make Laser Layout View"):
                viewFamilyTypes = FilteredElementCollector(doc).OfClass(ViewFamilyType)
                viewTypeToMake = None
                foundViewFamilyType = False #default
    
                #check to see if a viewfamilytype already exists
                vftName = None
                for vft in viewFamilyTypes:
                    if version == "2016" or version == "2017":
                        vftName = vft.Parameter[BuiltInParameter.ALL_MODEL_TYPE_NAME].AsString()
                    elif version == "2015":
                        for p in vft.Parameters:
                            if p.Definition.Name == "Type Name":
                                vftName = p.AsString()
    
                    if storefrontViewTypeName == vftName:
                        viewTypeToMake = vft
                        foundViewFamilyType = True
                        break
    
                # if not make one
                if not foundViewFamilyType:
                    for i in viewFamilyTypes:
                        if i.ViewFamily == ViewFamily.FloorPlan:
                            viewTypeToMake = i.Duplicate(storefrontViewTypeName)
                            break
                if levelName:
                    if not existingViewsFound:
                        print("{0}...CREATING VIEW...".format(levelName))
                        planViewMake = ViewPlan.Create(doc, viewTypeToMake.Id, selectedLevel)
                        planViewMake.Name = levelName + " Laser Layout"
                        viewToUpdate = planViewMake.Id
                        planViewMake.ViewTemplateId = doc.GetElement(laserViewPlan[0]).ViewTemplateId
    
                    print("{0}...CREATING LAYOUT...".format(levelName))
                    #Draw curves in view
                    DrawCurvesInView(viewToUpdate, storefrontFullLines, subCatIdList[0])
                    DrawCurvesInView(viewToUpdate, storefrontPartialLines, subCatIdList[1])
                    DrawCurvesInView(viewToUpdate, interiorWallsLines, subCatIdList[2])
    
                    print("{0}...DONE".format(levelName))
    
            # added return to allow IDE function collapse
            return(True)
    
        # 209 LINES OF CODE - this is nib wall code, should it be integrated?
        def storefront_split_wall(self):
    
            from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm, Console
    
            tol = 0.1
            standardSizes = [4.0, 3.0, 2.0, 1.0] #Glass sizes
            fixed_nib_wall_imperial = 6.0/12
            fixed_nib_wall_metric = 5.90551/12
            leftoverTol = 0.35  #Nib wall length
    
            storefrontConfig = storefront_options()
            currentConfig = storefrontConfig.currentConfig
            selectedSystem = currentConfig["currentSystem"]
            postWidth = currentConfig["postWidth"]
            oneByWidth = currentConfig["oneByWidth"]
    
    
            currentView = uidoc.ActiveView
            currentLevel = currentView.GenLevel
            levelName = currentLevel.Name
    
            # collect wall type information for a form to select which one to use.
            # also select whether or not the split is fixed distance or optimized.
            wallTypesList = {}
            splitTypes = storefrontConfig.splitTypeOptions
    
            selectedWallType = None
            allWallTypes = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.WallType)
            allWallTypes += GetAllElements(doc, BuiltInCategory.OST_StackedWalls, Autodesk.Revit.DB.WallType)
            for wallTypeId in allWallTypes:
                wallType = doc.GetElement(wallTypeId)
                wallTypeFamilyName = None
                wallTypeTypeName = None
                if version == "2016" or version == "2017":
                    wallTypeFamilyName = wallType.Parameter[BuiltInParameter.ALL_MODEL_FAMILY_NAME].AsString()
                    wallTypeTypeName = wallType.Parameter[BuiltInParameter.ALL_MODEL_TYPE_NAME].AsString()
                elif version == "2015":
                    for p in wallType.Parameters:
                        if p.Definition.Name == "Family Name":
                            wallTypeFamilyName = p.AsString()
                        if p.Definition.Name == "Type Name":
                            wallTypeTypeName = p.AsString()
                wallTypesList[wallTypeFamilyName + " - " + wallTypeTypeName] = wallTypeId
    
    
            # get default values if previously selected
            if currentConfig["splitWallType"] and currentConfig["splitOffset"]:
                if currentConfig["splitWallType"] in wallTypesList:
                    defaultValues = [currentConfig["splitWallType"], currentConfig["splitOffset"]]
                else:
                    defaultValues = [wallTypesList.keys()[0], currentConfig["splitOffset"]]
            else: 
                defaultValues = [wallTypesList.keys()[0], keys.keys()[0]]
    
            components = [Label('SPLIT OPTIONS'),
                                  Separator(),
                                                    ComboBox("combobox1", wallTypesList, default=defaultValues[0]),
                                                    Label('NIB WALLTYPE'),
                                                    ComboBox("combobox2", splitTypes, default=defaultValues[1]),
                                                    Label('SPLIT METHOD'),
                                                    Button('Go')]
    
            form = FlexForm("Storefront Tools V3", components)
            form.show()
    
            if not form.values:
                sys.exit()
            else:
                selectedWallType = form.values["combobox1"]
                selectedSplitOffset = float(form.values["combobox2"])
    
            # user settings into a dict
            config = {"splitWallType": wallTypesList.keys()[wallTypesList.values().index(selectedWallType)],
                              "splitOffset" : splitTypes.keys()[splitTypes.values().index(selectedSplitOffset)]}
    
            #save selected system
            storefrontConfig.storefront_save_config(user_configs=config)
    
            #get elements
            walls = SF2_Utility.GetElementsInView(BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView.Id)
            walls = FilterElementsByLevel(doc, walls, currentLevel.Id)
            storefrontWalls = FilterElementsByName(doc, walls,["Storefront","Storefront"], False)
            gypWalls = FilterElementsByName(doc, walls,["Storefront","Storefront"], True)
    
            #allWalls = storefrontWalls + gypWalls
            intersectionPoints = RemoveDuplicatePoints(FindWallIntersections(walls))
            currentSelected = uidoc.Selection.GetElementIds()
            with rpw.db.Transaction("Create Nib") as tx: 
                for id in currentSelected:
                    inst = doc.GetElement(id)
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
                                    if point.DistanceTo(start) < tol:
                                        startOverlap = True
                                    elif point.DistanceTo(end) < tol:
                                        endOverlap = True
                                    if startOverlap and endOverlap:
                                        break
    
    
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
    
                                    nibWalls.append(Wall.Create(doc, nibWallLine, currentLevel.Id, False))
                                    doc.Regenerate()
    
                                if endOverlap or (startOverlap == endOverlap):
                                    newPoint = XYZ(((start.X-end.X)*(offset/(length + lengthAdjust)))+end.X,((start.Y-end.Y)*(offset/(length + lengthAdjust)))+end.Y, end.Z)
                                    inst.Location.Curve = Line.CreateBound(newPoint, end)                  
    
                                    nibWallLine = Line.CreateBound(newPoint,start)
    
                                    start = newPoint
    
                                    nibWalls.append(Wall.Create(doc, nibWallLine, currentLevel.Id, False))
                                    doc.Regenerate()
    
                                if nibWalls:
    
                                    for nibWall in nibWalls:
                                        nibWall.WallType = doc.GetElement(selectedWallType)
                                        nibTopConstraint = nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId()
    
    
                                        #nibWall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(topOffset)
                                        if topConstraint.IntegerValue == botConstraint.IntegerValue:
                                            nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId(-1))
                                        else:
                                            nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(topConstraint)
    
    
                                        for p in nibWall.Parameters:
                                            if p.Definition.Name == "Location Line":
                                                p.Set(0)
                                            if p.Definition.Name == "Unconnected Height" and topConstraint.IntegerValue == -1:
                                                p.Set(unconnectedHeight)
    
                                        doc.Regenerate()
                                        if topConstraint.IntegerValue == botConstraint.IntegerValue:
                                            nibWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(topOffset)
    
    
    
    
    
                            else:
                                continue
    
            # added return to allow IDE function collapse
            return(True)
        def storefront_check_errors():
            """Checks errors for mullions and panels
            """
        
            currentView = uidoc.ActiveView
            famTypeDict = GetFamilyTypeDict("Fabrication-Error-Symbol")
        
            # Clear existing error notations
            errorNotations = list(GetElementsInView(BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, currentView.Id))
            errorNotations = FilterElementsByName(doc, errorNotations,["Fabrication","Error-Symbol"], False)
            if errorNotations:
                with rpw.db.Transaction("Place Errors"):
                    for error in errorNotations:
                        doc.Delete(error)
        
        
            def PointsAndErrors(mullions_list, errorName, cat_or_ids):
                """adds to lists of points and errors"""
                errorsToFlag = []
                compList =[]
                for m in mullions_list:
                    mElem = doc.GetElement(m)
                    if m not in compList:
                        intersectingMulls = FindIntersectingMullions(mElem, cat_or_ids)
                        if list(intersectingMulls):
                            mullPt = mElem.Location.Point
                            errorsToFlag.append([mullPt, errorName])
                            for mm in list(intersectingMulls):
                                compList.append(mm.Id)
                return errorsToFlag
        
            def MullionClash():
        
                errorsToFlag = []
        
                selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id
        
                allMullions = GetAllElements(doc, BuiltInCategory.OST_CurtainWallMullions, Autodesk.Revit.DB.FamilyInstance, currentView=True)
                allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
        
                allWalls = FilterElementsByName(doc, allWalls, ["Storefront","Storefront"], True)
        
                errorsToFlag += PointsAndErrors(allMullions, "Mullion-Mullion Intersects", BuiltInCategory.OST_CurtainWallMullions)
                errorsToFlag += PointsAndErrors(allMullions, "Mullion-Panel Intersects", BuiltInCategory.OST_CurtainWallPanels)
                if allWalls:
                    errorsToFlag += PointsAndErrors(allMullions, "Mullion-Wall Intersects", allWalls)
        
                return errorsToFlag
        
            def PanelClash():
        
        
                errorsToFlag = []
        
                allPanels = GetAllElements(doc, BuiltInCategory.OST_Windows, Autodesk.Revit.DB.FamilyInstance, currentView=True)
                allPanels = FilterDemolishedElements(doc, allPanels)
        
                panelMinWidth = 0.45
                panelMaxWidth = 5.0
                panelMaxHeight = 8.14
        
                ### ITERATE OVER PANEL LIST ###
                for p in allPanels:
                    famInst = doc.GetElement(p)
        
                    pan_height = famInst.Parameter[BuiltInParameter.FAMILY_HEIGHT_PARAM].AsDouble()
                    pan_width = famInst.Parameter[BuiltInParameter.FAMILY_WIDTH_PARAM].AsDouble()
        
                    if "empty" not in famInst.Name.lower():
                        if pan_width < panelMinWidth:
                            errorsToFlag.append([famInst.GetTransform().Origin, "Small Panel"])
                        elif pan_width > panelMaxWidth:
                            errorsToFlag.append([famInst.GetTransform().Origin, "Wide Panel"])
                        elif pan_height > panelMaxHeight:
                            errorsToFlag.append([famInst.GetTransform().Origin, "Tall Panel"])
                    else:
                        pass
        
                return errorsToFlag
        
            def ECWallClash():
        
                errorsToFlag = []
                columnsLinesEdgesEC = []
                wallsLinesEdgesEC = []
        
        
                docLoaded = RevitLoadECDocument(quiet=True)
                if docLoaded[0]:
                    docEC = docLoaded[0]
                    ecTransform = docLoaded[1]
        
                    selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id
        
                    selectedLevelInst = doc.GetElement(selectedLevel)
                    levelElevationEC = None 
                    for p in selectedLevelInst.Parameters:
                        if p.Definition.Name == "Elevation":
                            levelElevationEC = p.AsDouble()
        
                    allWallsEC  = GetAllElements(docEC, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
                    allColumnsEC = GetAllElements(docEC, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
                    allColumnsEC += GetAllElements(docEC, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)
        
                    selectedWallsEC = FilterElementsByLevel(docEC, allWallsEC, levelElevationEC)
                    selectedColumnsEC = FilterElementsByLevel(docEC, allColumnsEC, levelElevationEC)
        
                    wallsLinesEdgesEC = GetWallEdgeCurves(docEC, selectedWallsEC, ecTransform)
                    columnsLinesEdgesEC = GetColumnEdgeCurves(docEC, selectedColumnsEC, ecTransform)
        
                allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
                storefrontWalls = FilterElementsByName(doc, allWalls,["Storefront","Storefront"], False)
                storefrontWalls = FilterWallsByKind(doc, storefrontWalls, "Basic")
        
                obstructionEdges = columnsLinesEdgesEC
                obstructionEdges += wallsLinesEdgesEC
        
                if obstructionEdges:
                    for sfWallId in storefrontWalls:
                        sfWall = doc.GetElement(sfWallId)
                        locLine = sfWall.Location.Curve
                        locLineStart = locLine.GetEndPoint(0)
                        locLineEnd = locLine.GetEndPoint(1)
        
                        for obstructionLine in obstructionEdges:
                            obstLineElevation = obstructionLine.GetEndPoint(0).Z
                            locLineStart = XYZ(locLineStart.X, locLineStart.Y, obstLineElevation)
                            locLineEnd = XYZ(locLineEnd.X, locLineEnd.Y, obstLineElevation)
                            locLineFlat = Line.CreateBound(locLineStart, locLineEnd)
                            intersection = RevitCurveCurveIntersection(locLineFlat,obstructionLine)
        
                            if intersection:
                                #ERROR: Hit Existing Condition
                                errorsToFlag.append([intersection, "Hit EC"])
        
                return errorsToFlag
        
            allErrors = []
            allErrors += ECWallClash()
            allErrors += MullionClash()
            allErrors += PanelClash()
        
            errorSymbolId = famTypeDict["Fabrication-Error-Symbol"]
        
            if allErrors:
                with rpw.db.Transaction("Error Check"):
                    RevitPlaceErrorsInView(currentView, allErrors, errorSymbolId)    

except:
    # print traceback in order to debug file
    print(traceback.format_exc())
