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
"""

# pyRevit metadata variables
__title__ = "Storefront 2.0 Utility"
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
import logging # noqa E402
import math # noqa E402
import os # noqa E402
import rpw # noqa E402
import string # noqa E402
import sys # noqa E402
import System # noqa E402
import time # noqa E402
import traceback # noqa E402
import types # noqa E402

from rpw.utils.logger import logger # noqa E402

# .net windows modules
clr.AddReference('MathNet.Spatial')
clr.AddReference('System.Collections')
import MathNet.Spatial # noqa E402

from System.Collections.Generic import List # noqa E402
from System import DateTime as dt # noqa E402

# Revit API modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402
from Autodesk.Revit.DB import Transaction, IFailuresPreprocessor, BuiltInFailures, UV # noqa E402

# global variables
app = __revit__.Application # use this to open another model?
version = app.VersionNumber.ToString()
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
currentView = uidoc.ActiveView
user = str(System.Environment.UserName)

class Timer(object):
    "Time and TimeIt Decorator"
    def __init__(self):
        self.start_time = time.time()
        self.last = time.time()

    def stop(self):
        end_time = time.time()
        duration = end_time - self.start_time
        return duration
    def interval(self, message=None):
        end_time = time.time()
        interval = end_time - self.last
        self.last = end_time
        if message:
            print("{0} - Time: {1}".format(message, str(interval)))
        return interval

    @staticmethod
    def time_function(name):
        def wrapper(func):
            def wrap(*ags, **kwargs):
                print("START: {0}".format(name))
                t = Timer()
                rv = func(*ags, **kwargs)
                duration = t.stop()
                print("Done: {0} sec".format(duration))
                return rv
            return wrap
        return wrapper

def OutputException(inst):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(type(inst))    # the exception instance
    print(inst.args)     # arguments stored in .args
    print(inst)
    traceback.print_tb(exc_traceback, limit=3, file=sys.stdout)

    dataLines = "Error: {0}".format(str(inst))
    dataLines += "Error Args: {0}".format(str(inst.args))

    sys.exit("STOP")

def CreateLogger(name, verbosity):
    try:
        VERBOSE = verbosity  # True to Keep Window Open
        LOG_LEVEL = logging.ERROR
        LOG_LEVEL = logging.INFO
        if VERBOSE:
            LOG_LEVEL = logging.DEBUG
        logging.basicConfig(level=LOG_LEVEL)
        logger = logging.getLogger(name)
    except Exception as inst:
        OutputException(inst)
        pass
    return logger

def WriteToLogFile(entryTitle=None, data=None):

    doc = __revit__.ActiveUIDocument.Document
    currentView = uidoc.ActiveView
    path = "B:\\Python\\Logs\\pyFabrication\\"
    todaysDate = str(dt.Today.Month)+"/"+str(dt.Today.Day)+"/"+str(dt.Today.Year)
    currentUser = doc.Application.Username
    currentViewType = currentView.ViewType
    projectInfo = doc.ProjectInformation
    projectName = None
    for p in projectInfo.Parameters:
        if p.Definition.Name == "Project Name":
            projectName = p.AsString()
    with open(path+"logfile_storefront.txt","a") as file:
        file.write("Date:%s,Action:%s,User:%s,Project:%s,View:%s,%s\n" %( todaysDate, entryTitle, currentUser, projectName, currentViewType, data),) 
        file.close()

    return(True)

###################
## GET FUNCTIONS ##
###################
def GetAllElements(document, someCategory=None, someClass=None, currentView=False):
    """ 
    Grabs all elements of given category and class
    and returns it it as a collector.
    """
    try:
        if not document:
            document = __revit__.ActiveUIDocument.Document
        if currentView:
            collector = FilteredElementCollector(document, __revit__.ActiveUIDocument.ActiveView.Id)
        else:
            collector = FilteredElementCollector(document)
        if someCategory:
            collector.OfCategory(someCategory)
        if someClass:
            collector.OfClass(someClass)
        familyIter = collector.GetElementIdIterator()
        familyIter.Reset()
        return(list(familyIter))
    except Exception as inst:
        OutputException(inst)
        pass

def GetElementsInView(someCategory,someClass,aView):
    """ Grabs all elements of given category and class
        and returns it it as a collector.
    """
    try:
        collector = FilteredElementCollector(doc,aView)
        if someCategory:
            collector.OfCategory(someCategory)
        collector.OfCategory(someCategory)
        if someClass:
            collector.OfClass(someClass)
        familyIter = collector.GetElementIdIterator()
        return familyIter
    except Exception as inst:
        OutputException(inst)
        pass

def GetWallLocationCurves(document, elemIDlist):
        # elemIDlist data structure:
        # [[wall list level A], [wall list level B], [wall list levelB]]
    try:
        locationCrvList = []
        for i in elemIDlist:
            wall = document.GetElement(i)
            returnList.append(wall.Location.Curve)
        return(locationCrvList)

    except Exception as inst:
        OutputException(inst)
        pass

def GetWallEdgeCurves(document, someIterList, transform):
    try:
        returnList = []
        bo_options = app.Create.NewGeometryOptions()
        vector = None
        if transform:
            vector = Autodesk.Revit.DB.Transform.CreateTranslation(transform)

        if document:
            for instId in someIterList:
                inst = document.GetElement(instId)
                geo = inst.get_Geometry(bo_options)
                faces = []
                #print type(inst.Location.Curve)
                if type(inst.Location.Curve) == Arc:
                    for solid in geo:
                        solid_face = solid.Faces
                        for s in solid_face:
                            if type(s) == Autodesk.Revit.DB.PlanarFace:
                                faces.append(s)
                    try:
                        if faces:
                            edgeloops = faces[1].EdgeLoops
                            for loop in edgeloops:
                                for edge in loop:
                                    #Sprint edge, "-", list(loop).index(edge), "-", type(edge), type(edge.AsCurve())
                                    if type(edge.AsCurve()) == Arc:
                                        verts = list(edge.Tessellate())
                                        for i in range(len(verts)-1):

                                            if verts[i].DistanceTo(verts[i+1]) > app.ShortCurveTolerance:

                                                approxEdge = Line.CreateBound(verts[i],verts[i+1])
                                                if transform:
                                                    returnList.append(approxEdge.CreateTransformed(vector))
                                                else:
                                                    returnList.append(approxEdge)
                                    else:
                                        if transform:
                                            returnList.append(edge.AsCurve().CreateTransformed(vector))
                                        else:
                                            returnList.append(edge.AsCurve())
                    except Exception as inst:
                        OutputException(inst)
                        pass

                elif type(inst.Location.Curve) == Autodesk.Revit.DB.Line:
                    for f in geo:
                        solid_face = []
                        try:
                            solid_face = f.Faces
                        except: 
                            #print(inst.Name)
                            pass
                        for s in solid_face:
                            faces.append(s)
                    try:
                        if faces:
                            edgeloops = faces[2].EdgeLoops
                            for loop in edgeloops:
                                for edge in loop:
                                    if transform:
                                        returnList.append(edge.AsCurve().CreateTransformed(vector))
                                    else:
                                        returnList.append(edge.AsCurve())
                    except Exception as inst:
                        OutputException(inst)
                        pass 

        return(returnList)

    except Exception as inst:
        OutputException(inst)
        pass

def GetRoomBoundaryCurves(document, someIterList):
    try:
        returnList = []
        boptions = Autodesk.Revit.DB.SpatialElementBoundaryOptions()
        for instId in someIterList:
            inst = document.GetElement(instId)
            roomName = None
            for p in inst.Parameters:
                #print p.Definition.Name
                if p.Definition.Name == 'Name':
                    roomName = p.AsString()
            if roomName:
                boundsegs = inst.GetBoundarySegments(boptions)
                for bound in boundsegs:
                    for seg in bound:
                        if __revit__.Application.VersionNumber.ToString() == "2017":
                            returnList.append(seg.GetCurve())
                        else:
                            returnList.append(seg.Curve)
        return(returnList)
    except Exception as inst:
        OutputException(inst)
        pass

def GetFloorBoundaryCurves(document, someIterList):
    try:
        returnList = []
        bo_options = app.Create.NewGeometryOptions()
        for instId in someIterList:
            inst = document.GetElement(instId)
            floor_geo = inst.get_Geometry(bo_options)
            faces = []
            for f in floor_geo:
                solid_face = f.Faces
                for s in solid_face:
                    faces.append(s)
            edgeloops = faces[1].EdgeLoops
            for loop in edgeloops:
                for edge in loop:
                    returnList.append(edge.AsCurve())
        return returnList
    except Exception as inst:
        OutputException(inst)
        pass

def GetColumnEdgeCurves(document, someIterList, transform=None):
    try:
        returnList = []
        bo_options = app.Create.NewGeometryOptions()
        vector = None
        loc = None
        if not document:
            print someIterList
            for theId in someIterList:
                item = doc.GetElement(theId)
                if item.Name: 
                    print item.Name

        if transform:
            vector = Autodesk.Revit.DB.Transform.CreateTranslation(transform)
        for instId in someIterList:
            geo = None
            inst = document.GetElement(instId)
            geo = inst.get_Geometry(bo_options)
            faces = []

            #loc = inst.Location.Point
            #instLevel = document.GetElement(inst.LevelId)
            #loc = Autodesk.Revit.DB.XYZ(loc.X,loc.Y,instLevel.Elevation)

            if geo != None:
                for solid in geo:
                    if type(solid) == Autodesk.Revit.DB.Solid and len(list(solid.Faces)) > 0:
                        if solid.Faces[0].ComputeNormal(UV(0,0)).Z == -1:
                            edgeloop = list(solid.Faces[0].EdgeLoops)
                            for loop in edgeloop:
                                for edge in loop:
                                    if transform:
                                        returnList.append(edge.AsCurve().CreateTransformed(vector))
                                    else:
                                        returnList.append(edge.AsCurve())
                    elif type(solid) == Autodesk.Revit.DB.GeometryInstance:
                        subGeo = solid.GetInstanceGeometry()
                        for subSolid in subGeo:

                            if type(subSolid) == Autodesk.Revit.DB.Solid and len(list(subSolid.Faces)) > 0:
                                try:
                                    if subSolid.Faces[0].FaceNormal.Z == -1:
                                        edgeloop = list(subSolid.Faces[0].EdgeLoops)
                                        for loop in edgeloop:
                                            for edge in loop:
                                                if transform:
                                                    returnList.append(edge.AsCurve().CreateTransformed(vector))
                                                else:
                                                    returnList.append(edge.AsCurve())
                                except:
                                    continue

        return returnList
    except Exception as inst:
        OutputException(inst)
        pass

def GetRevitLinkInstances(document):
    # look in RevitLoadECDocument()
    pass

def GetLowerSolid(aSolid, locPoint):
    """
    Gets the lower solid based on a point for the plane
    and a normal direction. 
    """
    normal = Autodesk.Revit.DB.XYZ(0.0,0.0,1.0)
    origin = Autodesk.Revit.DB.XYZ(locPoint.X,locPoint.Y,locPoint.Z+4)
    plane  = Autodesk.Revit.DB.Plane.CreateByNormalAndOrigin(normal,origin)
    intersectSolid = Autodesk.Revit.DB.BooleanOperationsUtils.CutWithHalfSpace(aSolid,plane)
    if intersectSolid:
        return intersectSolid
    else: 
        return None
    return(True)

def GetWallTypeDict():
    #gets all wall types
    wallTypeDict = {}
    wallTypeIds = GetAllElements(doc, None, Autodesk.Revit.DB.WallType)
    for wallTypeId in wallTypeIds:
        wallType = doc.GetElement(wallTypeId)
        wallTypeKind = str(wallType.Kind)
        wallTypeName = None
        for p in wallType.Parameters:
            if p.Definition.Name == "Type Name":
                wallTypeName = p.AsString()
        wallTypeDict[wallTypeName] = wallTypeId
    return wallTypeDict

def GetDoorDictByWallHost():
    wallDoorHostDict = {}
    doorIds = GetAllElements(doc, BuiltInCategory.OST_Doors, Autodesk.Revit.DB.FamilyInstance)
    for doorId in doorIds:
        door = doc.GetElement(doorId)
        hostWallId = door.get_Parameter(BuiltInParameter.HOST_ID_PARAM).AsElementId()

        if not hostWallId in wallDoorHostDict.keys():
            wallDoorHostDict[hostWallId] = [doorId]
        else:
            wallDoorHostDict[hostWallId].append(doorId)
    return wallDoorHostDict

def GetFamilyTypeDict(name):
    #loads all families to search through
    familiyIds = GetAllElements(doc, None, Autodesk.Revit.DB.Family)

    #collect profiles from loaded family
    familyDict = {}
    for i in familiyIds:
        familyObj = doc.GetElement(i)
        if name.lower() == familyObj.Name.lower():
            for symbolId in familyObj.GetFamilySymbolIds():
                symbol = doc.GetElement(symbolId)
                symbolName = None
                for p in symbol.Parameters:
                    if p.Definition.Name == "Type Name":
                        symbolName = p.AsString()
                familyDict[symbolName] = symbol.Id
    if familyDict.keys():
        return familyDict
    else:
        return None
    return(True)

def GetProfileDict(name):
    #loads all families to search through
    familiyIds = GetAllElements(doc, None, Autodesk.Revit.DB.Family)

    #collect profiles from loaded family
    profileDict = {}
    for i in familiyIds:
        familyObj = doc.GetElement(i)
        if name.lower() in familyObj.Name.lower():

            for symbolId in familyObj.GetFamilySymbolIds():
                symbol = doc.GetElement(symbolId)
                symbolName = None
                for p in symbol.Parameters:
                    if p.Definition.Name == "Type Name":
                        symbolName = p.AsString()
                if not symbol.IsActive:
                    symbol.Activate()
                profileDict[symbolName] = symbol.Id
    if profileDict.keys():
        return(profileDict)
    else:
        return(None)

def GetMullionTypeDict(doc):
    """
    Checks to see if mullions have not yet been made
    If not existing, creates new mullions based on profile dict.
    """
    mullionDict = {}
    familiyIds = GetAllElements(doc, None, Autodesk.Revit.DB.Family)
    for i in familiyIds:
        familyObj = doc.GetElement(i)
        if "rectangular mullion" in  familyObj.Name.lower():
            for mullionTypeId in familyObj.GetFamilySymbolIds():
                mullionType = doc.GetElement(mullionTypeId)
                mullionTypeName =  mullionType.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
                mullionTypeProfileId =  mullionType.get_Parameter(BuiltInParameter.MULLION_PROFILE).AsElementId()
                if "rectangular" in  mullionTypeName.lower():
                    mullionDict["Template"] = mullionTypeId
                mullionDict[mullionTypeName] = mullionTypeId
    return(mullionDict)

def GetQuadMullionTypeDict():
    quadMullionDict = {}
    familiyIds = GetAllElements(doc, None, Autodesk.Revit.DB.Family)
    for i in familiyIds:
        familyObj = doc.GetElement(i)
        if "quad corner" in familyObj.Name.lower():
            for mullionTypeId in familyObj.GetFamilySymbolIds():
                mullionType = doc.GetElement(mullionTypeId)
                mullionTypeName = None
                for p in mullionType.Parameters:
                    if p.Definition.Name == "Type Name":
                        mullionTypeName = p.AsString()
                    if p.Definition.Name == "Profile":
                        mullionTypeProfileId = p.AsElementId()
                if "quad" in  mullionTypeName.lower():
                    quadMullionDict["Template"] = mullionType.Id
                quadMullionDict[mullionTypeName] = mullionType.Id
    return(quadMullionDict)

def GetPanelTypeDict():
    """
    Checks to see if mullions have not yet been made
    If not existing, creates new mullions based on profile dict.
    """
    panelTypeDict = {}
    familyIds = GetAllElements(doc, BuiltInCategory.OST_CurtainWallPanels, Autodesk.Revit.DB.FamilySymbol)
    for i in familyIds:
        panel = doc.GetElement(i)
        for p in panel.Parameters:
            if p.Definition.Name == "Type Name":
                panelTypeName = p.AsString()
        panelTypeDict[panel.Family.Name + '-' + panelTypeName] = i
    return(panelTypeDict)

def GetWindowTypeDict():
    """
    Checks to see if mullions have not yet been made
    If not existing, creates new mullions based on profile dict.
    """
    windowTypeDict = {}
    familyIds = GetAllElements(doc, BuiltInCategory.OST_Windows, Autodesk.Revit.DB.FamilySymbol)
    for i in familyIds:
        window = doc.GetElement(i)
        for p in window.Parameters:
            if p.Definition.Name == "Type Name":
                windowTypeName = p.AsString()
        windowTypeDict[window.Family.Name + '-' + windowTypeName] = i
    return(windowTypeDict)

def GetVerticalMullionsAtPoint(curtaingrid, point, detectionTolerance=0.01, searchOnlySelf=False):
    returnMullions = None
    selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id

    def SearchVerticalMullions(mullionIds):
        foundMullions = []
        for mulId in mullionIds:
            mullion = doc.GetElement(mulId)
            mullionLocCurve = mullion.LocationCurve
            if mullionLocCurve:
                if abs(mullionLocCurve.Direction.Z) == 1:
                    mullionOrigin = mullion.GetTransform().Origin
                    mullionPoint = XYZ(mullionOrigin.X, mullionOrigin.Y, point.Z)
                    if mullionPoint.DistanceTo(point) < detectionTolerance:
                        foundMullions.append(mullion)
        return(foundMullions)

    if curtaingrid:
        gridMullionIds = curtaingrid.GetMullionIds()
        returnMullions = SearchVerticalMullions(gridMullionIds)

    if not returnMullions and not searchOnlySelf:
        allMullionIds = GetAllElements(doc, BuiltInCategory.OST_CurtainWallMullions, Autodesk.Revit.DB.FamilyInstance, currentView=True)
        allMullionIds = FilterElementsByLevel(doc, allMullionIds, selectedLevel)
        returnMullions = SearchVerticalMullions(allMullionIds)
    else:
        return(returnMullions)

    return(returnMullions)

def GetHorizontalMullionsAtPoint(curtaingrid, point, nameFilter=None):
    mullionIds = curtaingrid.GetMullionIds()
    returnMullions = []
    for mulId in mullionIds:
        mullion = doc.GetElement(mulId)
        mullionName = mullion.Name
        if mullion.LocationCurve:
            mullionCurve = mullion.LocationCurve 
            if abs(mullionCurve.Direction.Z) < 1:
                mullionOrigin = mullion.GetTransform().Origin
                testPoint = XYZ(point.X, point.Y, mullionOrigin.Z)
                intersects = RevitPointOnLine2D(testPoint, mullionCurve)
                if intersects:
                    if nameFilter:
                        if nameFilter.lower() in mullionName.lower():
                            returnMullions.append(mullion)
                    else:
                        returnMullions.append(mullion)

    return(returnMullions)

def GetMullionCurves(mullion):
    mullionCurves = []
    options = app.Create.NewGeometryOptions()
    options.IncludeNonVisibleObjects = True
    options.ComputeReferences = True

    if abs(mullion.LocationCurve.Direction.Z) >= 1:
        mullionGeo = mullion.get_Geometry(options)

        for item in list(mullionGeo):
            geometry = list(item.GetInstanceGeometry())
            faces = []
            for geo in geometry:
                if type(geo) == Autodesk.Revit.DB.Line:
                    panelCurve = geo
                    break
                elif type(geo) == Autodesk.Revit.DB.Solid:
                    if list(geo.Faces.GetEnumerator()):
                        faces = list(geo.Faces.GetEnumerator())

            if faces:
                edgeloopArrayArray = faces[1].EdgeLoops
                edgeloop = list(edgeloopArrayArray)[0]
                for edge in edgeloop:
                    mullionCurves.append(edge.AsCurve())
                break

    return(mullionCurves)

def GetArea2DBoundaryPoints(areaBoundary):
    try:
        returnList = []
        boptions = Autodesk.Revit.DB.SpatialElementBoundaryOptions()
        inst = areaBoundary

        areaName = None
        for p in inst.Parameters:
            #print p.Definition.Name
            if p.Definition.Name == 'Name':
                areaName = p.AsString()
        if areaName:
            boundsegs = inst.GetBoundarySegments(boptions)
            for bound in boundsegs:
                for seg in bound:
                    if __revit__.Application.VersionNumber.ToString() == "2017":
                        returnList.append(seg.GetCurve().GetEndPoint(0))
                    else:
                        returnList.append(seg.Curve.GetEndPoint(0))

        return(returnList)
    except Exception as inst:
        OutputException(inst)
        pass

######################
## FILTER FUNCTIONS ##
######################
def FilterElementsByLevel(document,someIterList, levelIn):
    """ 
    Takes list of elements and compares its level with
    a given level.
    """
    try:
        tol = 0.1
        filteredIterList = []
        levelElevation = None
        levelName = None
        if not document:
            document = __revit__.ActiveUIDocument.Document
        if type(someIterList) == FilteredElementIdIterator:
            someIterList.Reset()
        if type(levelIn) == ElementId:
            level = doc.GetElement(levelIn)
            for p in level.Parameters:
                if p.Definition.Name == "Name":
                    all = string.maketrans('','')
                    nodigs = all.translate(all, string.digits)
                    levelName = str(p.AsString().translate(all, nodigs))
                    if not levelName:
                        levelName = p.AsString()
        elif type(levelIn) == float:
            levelElevation = levelIn

        #get elementlevel and  
        for instId in someIterList:
            inst = document.GetElement(instId)
            instLevId = inst.LevelId
            if document.GetElement(instLevId):
                elementLevel = document.GetElement(instLevId)
                elementLevelName = elementLevel.Name
                elementLevelHeight = None
                for p in elementLevel.Parameters:
                    if p.Definition.Name == "Elevation":
                        elementLevelHeight = p.AsDouble()
                if levelName and levelName.lower() in elementLevelName.lower():
                    filteredIterList.append(instId)
                elif levelElevation  and abs(elementLevelHeight - levelElevation) < tol:
                    filteredIterList.append(instId)
        return filteredIterList
    except Exception as inst:
        OutputException(inst)
        pass

def FilterElementsByBaseOffset(document,someIterList, offsetThres):
    """ Filters out elements that are greater than the offset thresh because it 
    clears that threshold. 
    """
    try:
        filteredIterList = []
        if type(someIterList) == FilteredElementIdIterator:
            someIterList.Reset()

        if not document:
            document = __revit__.ActiveUIDocument.Document

        for instId in someIterList:
            inst = document.GetElement(instId)
            baseOffset = None
            for p in inst.Parameters:
                if p.Definition.Name == "Base Offset":
                    baseOffset = p.AsDouble()
                    break
            if baseOffset != None:
                if baseOffset < offsetThres:
                    filteredIterList.append(instId)
                else:
                    continue
        return filteredIterList
    except Exception as inst:
        OutputException(inst)
        pass

def FilterElementsByName(document, someIterList,keyWordPair, invert): # candidate for deletion
    """ 
    Takes list and checks the elements name, if it passes
    then its added to the return list. 
    """
    try:
        filteredIterList = []

        if not document:
            document = __revit__.ActiveUIDocument.Document

        if type(someIterList) == FilteredElementIdIterator:
            someIterList.Reset()
        for instId in someIterList:
            inst = document.GetElement(instId)
            instName = None
            try:
                instName = inst.Symbol.Family.Name
            except:
                for p in inst.Parameters:
                    if p.Definition.Name == "Name":
                        instName = p.AsString()
            if not instName:
                try:
                    instName = inst.Name
                except Exception as inst:
                    OutputException(inst)
                    pass
            if not invert:
                if keyWordPair[0].lower() in instName.lower() and keyWordPair[1].lower() in instName.lower():
                    filteredIterList.append(instId)
            else:
                if keyWordPair[0].lower() not in instName.lower() and keyWordPair[1].lower() not in instName.lower():
                    filteredIterList.append(instId)
        return filteredIterList #returns the ids
    except Exception as inst:
        OutputException(inst)
        pass

def FilterWallsByKind(document, walls, kindString):
    returnList = []

    if not document:
        document = __revit__.ActiveUIDocument.Document

    for wallId in walls:
        wall = document.GetElement(wallId)
        wallKind = str(wall.WallType.Kind)
        if kindString == wallKind:
            returnList.append(wallId)
    return(returnList)

def FilterDemolishedElements(document, someIterList):
    """
    Filters a list of revit elements
    and removes any that will be demo
    """

    if not document:
        document = __revit__.ActiveUIDocument.Document

    returnList = []
    for id in someIterList:
        item = document.GetElement(id)
        if item:
            phase = document.GetElement(item.DemolishedPhaseId)
            if not phase:
                returnList.append(id)

    return returnList

def FilterElementsByPhase(document, someIterList, phaseKeyword):
    """Filters a list of revit elements
        by a keyword in the name of the phase element
    """
    allPhases = GetAllElements(document, BuiltInCategory.OST_Phases, Autodesk.Revit.DB.Phase)
    matchedPhase = None
    returnList = []
    for id in allPhases:
        phase = document.GetElement(id)
        if phase:
            if phaseKeyWord.lower() in (phase.Name.AsString()).lower():
                matchedPhase = id
                break
    for id in someIterList:
        item = document.GetElement(id)
        if item.CreatedPhaseId:
            if item.CreatedPhaseId == matchedPhase:
                returnList.append(id)

    return(returnList)

####################
## VIEW FUNCTIONS ##
####################
def PlaceOrientationErrorsInView(aView,orientErrorList,symbol):
    try:

        if type(symbol) == Autodesk.Revit.DB.ElementId:
            symbol = doc.GetElement(symbol)
        try:
            symbol.Activate()
        except:
            pass

        currentView = doc.GetElement(aView)
        placementCurve = None
        for error in orientErrorList:
            if type(error[0]) == rg.LineCurve or type(error[0]) == rg.Line:
                startPt = error[0].PointAtStart
                endPt = error[0].PointAtEnd
                placementCurve = Line.CreateBound(XYZ(startPt[0],startPt[1],0), XYZ(endPt[0],endPt[1],0))
            errorInst = doc.Create.NewFamilyInstance(placementCurve, symbol, currentView)
            for p in errorInst.Parameters:
                if p.Definition.Name == "label_text":
                    p.Set(error[1]) 
    except Exception as inst:
        OutputException(inst)
        pass

def PlaceErrorsInView(aView,errorList,symbol):
    if not symbol.IsActive:
        symbol.Activate()
    try:
        currentView = doc.GetElement(aView)
        for error in errorList:
            point = RRConvertPoints(error[0], "ToRevit")
            errorInst = doc.Create.NewFamilyInstance(point, symbol, currentView)
            for p in errorInst.Parameters:
                if p.Definition.Name == "label_text":
                    p.Set(error[1]) 
    except Exception as inst:
        OutputException(inst)
        pass

def RevitPlaceErrorsInView(aView, errorTupleList, symbolId):
    symbolElem = doc.GetElement(symbolId)
    if not symbolElem.IsActive:
        symbolElem.Activate()
    try:
        currentView = aView
        for errorTuple in errorTupleList:
            errorInst = doc.Create.NewFamilyInstance(errorTuple[0], symbolElem, currentView)
            for p in errorInst.Parameters:
                if p.Definition.Name == "label_text":
                    p.Set(errorTuple[1])
    except Exception as inst:
        OutputException(inst)
        pass

def DeleteElementsInView(aView, someCategory=None, someClass=None, optionalKeyword=None):
    try:
        collector = FilteredElementCollector(doc,aView)
        if someCategory:
            collector.OfCategory(someCategory)
        if someClass:
            collector.OfClass(someClass)

        for item in collector:
            if optionalKeyword:
                try: 
                    if optionalKeyword.lower() in item.Name.lower():
                        doc.Delete(item.Id)
                except: 
                    pass
                try: 
                    if optionalKeyword.lower() in item.Symbol.Family.Name.lower():
                        doc.Delete(item.Id)
                except: 
                    pass

            else:
                doc.Delete(item.Id)

    except Exception as inst:
        OutputException(inst)
        pass

def DrawCurvesInView(aView,curveList,aLineStyle):
    currentCurve = None
    minTolerance = 0.01
    curveZ = 0.0

    try:
        viewElement = doc.GetElement(aView)
        if viewElement.ViewType == "FloorPlan":
            curveZ = viewElement.GenLevel.Elevation

        for curve in curveList:
            currentCurve = curveList.index(curve)
            end = curve.GetEndPoint(1)
            start = curve.GetEndPoint(0)
            midpoint = curve.Evaluate(0.5,True)
            flatEnd =  XYZ(end.X, end.Y, curveZ)
            flatMid = XYZ(midpoint.X, midpoint.Y, curveZ)
            flatStart = XYZ(start.X, start.Y, curveZ)
            flatCurve = None
            if flatStart.DistanceTo(flatEnd) > app.ShortCurveTolerance:
                if type(curve) == Autodesk.Revit.DB.Arc:
                    flatCurve = Arc.Create(start,end,midpoint)
                elif type(curve) == Autodesk.Revit.DB.Line:
                    flatCurve = Line.CreateBound(flatStart, flatEnd)
                else:
                    print "...ISSUE DRAWING CURVE"
                newDetailLine = doc.Create.NewDetailCurve(viewElement,flatCurve)
                if aLineStyle != None:
                    newDetailLine.LineStyle = aLineStyle.GetGraphicsStyle(GraphicsStyleType.Projection)
            else:
                print "...REMOVED A TINY CURVE"
    except Exception as inst:
        if currentCurve:
            print curveList[currentCurve].Length
            #print "Curve - " + str(currentCurve) +" in " + str(aLineStyle.Name) + " out of " + str(len(curveList))
        OutputException(inst)
        pass

def DrawDoorsInView(aView, doorList, doorSym, doorDict):
    try:
        if type(doorSym) == Autodesk.Revit.DB.FamilySymbol:
            if not doorSym.IsActive:
                doorSym.Activate()
        elif type(doorSym) == Autodesk.Revit.DB.ElementId:
            doorSym = doc.GetElement(doorSym)

        viewElement = doc.GetElement(aView)
        for doorId in doorList:
            door = doc.GetElement(doorId)
            foundDoor = False
            if door:
                doorName =  door.Name
                doorPoint = door.Location.Point
                doorRotation = door.Location.Rotation
                doorMirrored = door.Mirrored
                doorHandFlipped = door.HandFlipped
                doorFacingFlipped = door.FacingFlipped
                doorHand = None
                for key,value in doorDict.items():
                    if key.lower() in doorName.lower():
                        doorName = key
                        doorHand = value[0]
                        doorWidth = value[1]
                        doorType = value[2]
                        foundDoor = True
                        break

            if foundDoor:
                famInst = doc.Create.NewFamilyInstance(doorPoint, doorSym,viewElement)
                for p in famInst.Parameters:
                    if p.Definition.Name == "doorWidth":
                        p.Set(doorWidth)
                    elif p.Definition.Name == "doorName":
                        p.Set(doorName)
                    elif p.Definition.Name == "doorHand":
                        p.Set(doorHand)
                    elif p.Definition.Name == "doorType":
                        p.Set(doorType) 
                    elif p.Definition.Name == "isSwing":
                        if doorType == "SWING":
                            p.Set(1)
                        if doorType == "SLIDER":
                            p.Set(0)
                    elif p.Definition.Name == "doorHandFlipped":
                        p.Set(doorHandFlipped)
                    elif p.Definition.Name == "doorMirrored":
                        p.Set(doorMirrored)
                    elif p.Definition.Name == "doorFacingFlipped":
                        p.Set(doorFacingFlipped)

                axis = Autodesk.Revit.DB.Line.CreateBound(doorPoint,XYZ(doorPoint.X,doorPoint.Y,doorPoint.Z+1.0))
                Autodesk.Revit.DB.ElementTransformUtils.RotateElement(doc,famInst.Id,axis,doorRotation)
            else:
                print "Could not find: " + doorName + " in list"
    except Exception as inst:
        OutputException(inst)
        pass

def DrawDesksInView(aView, deskList, deskSym):

    try:
        if type(deskSym) == Autodesk.Revit.DB.FamilySymbol:
            if not deskSym.IsActive:
                deskSym.Activate()
        elif type(deskSym) == Autodesk.Revit.DB.ElementId:
            deskSym = doc.GetElement(deskSym)

        viewElement = doc.GetElement(aView)
        for deskId in deskList:
            desk = doc.GetElement(deskId)
            deskPoint = desk.Location.Point
            deskRotation = desk.Location.Rotation
            if desk.Mirrored:
                deskRotation += math.pi

            famInst = doc.Create.NewFamilyInstance(deskPoint, deskSym, viewElement)

            axis = Autodesk.Revit.DB.Line.CreateBound(deskPoint,XYZ(deskPoint.X,deskPoint.Y,deskPoint.Z+1.0))
            Autodesk.Revit.DB.ElementTransformUtils.RotateElement(doc,famInst.Id,axis,deskRotation)

    except Exception as inst:
        OutputException(inst)




############################
## INTERSECTION FUNCTIONS ##
############################
def DrawCirclesAtIntersections(aView, pointList):
    try:
        viewElement = doc.GetElement(aView)
        rad = 0.25
        for point in pointList:
            ellipse = Ellipse.Create(point, rad,rad,XYZ(1.0,0.0,0.0),XYZ(0.0,1.0,0.0),0.0,10.0)
            circle = doc.Create.NewDetailCurve(viewElement,ellipse)
    except Exception as inst:
        OutputException(inst)
        pass

def FindWallIntersections(wallList):
    try:
        intersectionList =[]
        returnList = []
        for wall1 in wallList:
            for wall2 in wallList:
                if wall1 is not wall2:
                    line1 = doc.GetElement(wall1).Location.Curve
                    line2 = doc.GetElement(wall2).Location.Curve
                    out = clr.Reference[Autodesk.Revit.DB.IntersectionResultArray]()
                    inter = line1.Intersect(line2, out)
                    if inter == SetComparisonResult.Overlap or inter == SetComparisonResult.Subset:
                        intersectionList.append(out.Item[0].XYZPoint)
        for item in intersectionList:
            if item not in returnList:
                returnList.append(item)
        return(returnList)
    except Exception as inst:
        OutputException(inst)
        pass
def RevitCurveCurveIntersection(curve1,curve2, filterIntersectionType=None):
    returnPoint = None
    out = clr.Reference[Autodesk.Revit.DB.IntersectionResultArray]()
    inter = curve1.Intersect(curve2, out)
    if inter == SetComparisonResult.Overlap or inter == SetComparisonResult.Subset:
        if not filterIntersectionType:
            returnPoint = out.Item[0].XYZPoint
        elif filterIntersectionType == "Overlap" and inter == SetComparisonResult.Overlap:
            returnPoint = out.Item[0].XYZPoint
        elif filterIntersectionType == "Subset" and inter == SetComparisonResult.Subset:
            returnPoint = out.Item[0].XYZPoint
    return(returnPoint)
def RevitCircleCurveIntersection(curve1,curve2, filterIntersectionType=None):
    returnPoints = []
    out = clr.Reference[Autodesk.Revit.DB.IntersectionResultArray]()
    inter = curve1.Intersect(curve2, out)
    if inter == SetComparisonResult.Overlap or inter == SetComparisonResult.Subset:
        if not filterIntersectionType:
            for i in range(out.Size):
                returnPoints.append(out.Item[i].XYZPoint)
        elif filterIntersectionType == "Overlap" and inter == SetComparisonResult.Overlap:
            for i in range(out.Size):
                returnPoints.append(out.Item[i].XYZPoint)
        elif filterIntersectionType == "Subset" and inter == SetComparisonResult.Subset:
            for i in range(out.Size):
                returnPoints.append(out.Item[i].XYZPoint)
    return(returnPoints)
def RevitCurvesListIntersect(curves):
    intersectionList =[]
    returnList = []
    for curve1 in curves:
        for curve2 in curves:
            if curve1 is not curve2:
                intersection = RevitCurveCurveIntersection(curve1, curve2)
                if intersection:
                    intersectionList.append(intersection)
    for item in intersectionList:
        if item not in returnList:
            returnList.append(item)
    return(returnList)
###################################
## WARNING ELIMINATION FUNCTIONS ##
###################################
class WarningDiscard(Autodesk.Revit.DB.IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        fail_acc_list = failuresAccessor.GetFailureMessages().GetEnumerator()
        onlyWarnings = True
        for failure in fail_acc_list:
            failure_id = failure.GetFailureDefinitionId()
            failure_severity = failure.GetSeverity().ToString()
            #add failure types below
            failure_types = [BuiltInFailures.CurtainWallFailures.DanglingCurtainWallCorner,
                             BuiltInFailures.OverlapFailures.WallsOverlap,
                             BuiltInFailures.OverlapFailures.RoomSeparationLinesOverlap,
                             BuiltInFailures.OverlapFailures.SpaceSeparationLinesOverlap,
                             BuiltInFailures.OverlapFailures.WallRoomSeparationOverlap,
                             BuiltInFailures.OverlapFailures.WallAreaBoundaryOverlap,
                             BuiltInFailures.OverlapFailures.WallSpaceSeparationOverlap,
                             BuiltInFailures.CreationFailures.CannotMakeWall,
                             BuiltInFailures.CreationFailures.CannotDrawWalls,
                             BuiltInFailures.CreationFailures.CannotDrawWallsError,
                             BuiltInFailures.JoinElementsFailures.CannotKeepJoined,
                             BuiltInFailures.CurtainGridFamilyFailures.CornerMullionOverlapsOtherOnePlacedOnNeighboringRegion,
                             BuiltInFailures.CurtainGridFamilyFailures.CannotCreateCornerMullionDueAngle,
                             BuiltInFailures.CurtainGridFamilyFailures.CannotPlaceSystemMullionFamilyOnCurtainWall]

            if failure_id in failure_types:
                if failure_severity == "Warning":
                    failuresAccessor.DeleteWarning(failure)
                elif failure_severity == "Error":
                    failuresAccessor.ResolveFailure(failure)
                    onlyWarnings = False
        if onlyWarnings:
            return(FailureProcessingResult.Continue)
        else:
            return(FailureProcessingResult.ProceedWithCommit)
        return(True)
def SupressErrorsAndWarnings(transaction):
    # I guess this forces revit to ignore errors and warnings
    options = transaction.GetFailureHandlingOptions()
    preprocessor = WarningDiscard()
    options.SetFailuresPreprocessor(preprocessor)
    transaction.SetFailureHandlingOptions(options)
    return(None)
###############
## SOMETHING ##
###############
def SetupLineStyles(lineSubcategories):
    #requires incoming in the format of [[string name, color, lineweight value]]
    lineCat = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Lines)
    subCatList = lineCat.SubCategories
    subCatIdList = []
    try:
        t = Transaction(doc, "UpdateSubCats")
        t.Start()
        for subCatToEnsure in lineSubcategories:
            found = False
            for subCat in subCatList:
                if subCatToEnsure[0] == str(subCat.Name):
                    found = True
                    subCatIdList.append(subCat)#append existing subcat
                    subCat.LineColor = subCatToEnsure[1] #sets color
                    subCat.SetLineWeight(subCatToEnsure[2] , GraphicsStyleType.Projection)#set line weight
            if not found:
                newSubCat = doc.Settings.Categories.NewSubcategory(lineCat,subCatToEnsure[0]) #creates the subcat
                newSubCat.LineColor = subCatToEnsure[1] #sets color
                newSubCat.SetLineWeight(subCatToEnsure[2] , GraphicsStyleType.Projection)#set line weight
                subCatIdList.append(newSubCat)#append newly created subcat
        t.Commit()
        return subCatIdList
    except Exception as inst:
        OutputException(inst)
        pass
    finally:
        t.Dispose()

def CheckElementConstraints(document, someIterList):
    badElements = []
    try:
        levelDict = {}
        sortedLevelNames = None
        allLevels = GetAllElements(document, BuiltInCategory.OST_Levels, Autodesk.Revit.DB.Level)
        for levelId in allLevels:
            level = document.GetElement(levelId)
            levelDict[level.Name] = level.Elevation

        sortedLevelNames = sorted(levelDict, key=levelDict.get)

    except Exception as inst:
        OutputException(inst)
        pass

    try:
        for instId in someIterList:
            inst = document.GetElement(instId)
            baseConstraint = None
            topConstraint = None
            for p in inst.Parameters:
                if p.Definition.Name == "Base Constraint" or p.Definition.Name == "Base Level":
                    baseConstraint = p.AsValueString()
                if p.Definition.Name == "Top Constraint" or p.Definition.Name == "Top Level":
                    topConstraint = p.AsValueString()
            try:
                if topConstraint and baseConstraint:
                    # check to see if the topConstraint is the level above the bottom. 
                    if not sortedLevelNames[sortedLevelNames.index(baseConstraint)+1] in topConstraint and ("CONTAINER" not in baseConstraint):
                        # spanning floors
                        badElements.append(inst)

                else:
                    # unconnected top
                    if "CONTAINER" not in baseConstraint:
                        badElements.append(inst)
            except:
                pass

    except Exception as inst:
        OutputException(inst)
        pass
    return(badElements)

def MovePoint(fromPoint, toPoint, dist):
    move = rg.Vector3d(toPoint[0]-fromPoint[0], toPoint[1]-fromPoint[1], toPoint[2]-fromPoint[2])
    move.Unitize()
    move = rg.Vector3d.Multiply(move, dist)
    return(rg.Point3d.Add(fromPoint,move))

def PrintBreakLine():
    print("----------------------------------------")

###############
## SOMETHING ##
###############
def RevitPointOnLine2D(point1, line):
    lineStart = line.GetEndPoint(0)
    lineEnd = line.GetEndPoint(1)
    vect = XYZ(lineEnd.Y - lineStart.Y, lineEnd.X - lineStart.X, lineEnd.Z - lineStart.Z)
    vect = vect.Normalize()
    point2 = point1.Add(vect)


    intersectLine = Line.CreateBound(point1, point2)
    return(RevitCurveCurveIntersection(line, intersectLine) != None)

###############
## SOMETHING ##
###############
def AngleThreePoints(point1,point2,point3):
    vect1 = XYZ(point1.X - point2.X, point1.Y - point2.Y, point1.Z - point2.Z)
    vect2 = XYZ(point3.X - point2.X, point3.Y - point2.Y, point3.Z - point2.Z)
    angle = ((vect1.AngleTo(vect2)*360)/ (2*math.pi))
    return(angle)

def RevitTransVector(pointTo, pointFrom, magnitude=None):
    vect1 = XYZ(pointTo.X - pointFrom.X, pointTo.Y - pointFrom.Y, pointTo.Z - pointFrom.Z)
    if magnitude:
        vect1 = vect1.Normalize()
        vect1 = vect1.Multiply(magnitude)
    return(vect1)

def RevitCurtainPanelsAtPoint(curtaingrid, point, detectionTolerance=0.001):
    wallPanels = curtaingrid.GetPanelIds()
    options = app.Create.NewGeometryOptions()
    options.IncludeNonVisibleObjects = True
    options.ComputeReferences = True

    foundPanels = []

    for panelId in wallPanels:
        panel = doc.GetElement(panelId)
        panelGeo = panel.get_Geometry(options)
        panelCurve = None
        panelMidpoint = None

        for item in list(panelGeo):
            geometry = list(item.GetInstanceGeometry())
            faces = []
            for geo in geometry:
                if type(geo) == Autodesk.Revit.DB.Line:
                    panelCurve = geo
                    break
                elif type(geo) == Autodesk.Revit.DB.Solid:
                    if list(geo.Faces.GetEnumerator()):
                        faces = list(geo.Faces.GetEnumerator()) 
            if faces:
                edgeloopArrayArray = faces[1].EdgeLoops
                edgeArray = list(edgeloopArrayArray)[0]
                edge1Midpoint = edgeArray[1].AsCurve().Evaluate(0.5, True)
                edge2Midpoint = edgeArray[3].AsCurve().Evaluate(0.5, True)

                edge3Midpoint = Line.CreateBound(edge1Midpoint, edge2Midpoint).Evaluate(0.5, True)
                panelMidpoint = XYZ(edge3Midpoint.X, edge3Midpoint.Y, point.Z)
                break

        if panelMidpoint:
            detectionDist = point.DistanceTo(panelMidpoint)
            if detectionDist < detectionTolerance:
                foundPanels.append(panelId)

    return(foundPanels)

def RevitCurtainPanelCurve(panel):
    panelCurve = None
    options = app.Create.NewGeometryOptions()
    options.IncludeNonVisibleObjects = True
    options.ComputeReferences = True

    panelGeo = panel.get_Geometry(options)

    for item in list(panelGeo):
        geometry = list(item.GetInstanceGeometry())
        faces = []
        for geo in geometry:
            if type(geo) == Autodesk.Revit.DB.Line:
                panelCurve = geo
                break
            elif type(geo) == Autodesk.Revit.DB.Solid:
                if list(geo.Faces.GetEnumerator()):
                    faces = list(geo.Faces.GetEnumerator()) 
        if faces:
            edgeloopArrayArray = faces[1].EdgeLoops
            edgeArray = list(edgeloopArrayArray)[0]
            edge1Midpoint = edgeArray[1].AsCurve().Evaluate(0.5, True)
            edge2Midpoint = edgeArray[3].AsCurve().Evaluate(0.5, True)
            edge1Midpoint = XYZ(edge1Midpoint.X, edge1Midpoint.Y, edge1Midpoint.Z)
            edge2Midpoint = XYZ(edge2Midpoint.X, edge2Midpoint.Y, edge2Midpoint.Z)
            panelCurve = Line.CreateBound(edge1Midpoint, edge2Midpoint)
            break
    return(panelCurve)

def RevitDividePanelEquidistant(panel, divs, intermediateWidth=0):
    line = RevitCurtainPanelCurve(panel)
    panelWidth = (line.Length - ((divs - 1) * intermediateWidth)) / divs
    listPoints = []
    for d in range(int(divs - 1)):
        param = (panelWidth * (d + 1)) + ((d + 0.5) * intermediateWidth)
        listPoints.append(line.Evaluate(param, False))
    return(listPoints)

def RevitDividePanelFixed(panel, width, intermediateWidth=0, minPanelWidth=1):
    listPoints = []
    line = RevitCurtainPanelCurve(panel)
    numPanels = math.floor(line.Length/width)
    adjustment = 0
    if numPanels == 0:
        return listPoints

    leftover = line.Length - (numPanels * width)

    if leftover >= minPanelWidth:
        adjustment = 0
    else:
        adjustment = -1

    for d in range((int(numPanels)+adjustment)):
        param = (width * (d+1))
        listPoints.append(line.Evaluate(param, False))
    return(listPoints)

def RevitSplitLineAtPoints(lineToSplit, splitPoints):
    splitParams = [0]
    splitCurves = []
    lineToSplitStart = lineToSplit.GetEndPoint(0)
    for point in splitPoints:
        if RevitPointOnLine2D(point, lineToSplit):
            dist = point.DistanceTo(lineToSplitStart)/lineToSplit.Length
            splitParams.append(point.DistanceTo(lineToSplitStart)/lineToSplit.Length)
    splitParams.append(1)
    splitParams.sort()
    for i in range(len(splitParams)-1):
        p1 = splitParams[i]
        p2 = splitParams[i+1]
        pt1 = lineToSplit.Evaluate(p1, True)
        pt2 = lineToSplit.Evaluate(p2, True)
        if pt1.DistanceTo(pt2) > app.ShortCurveTolerance:
            lineSeg = Line.CreateBound(pt1, pt2)
            splitCurves.append(lineSeg)

    return(splitCurves)

###############
## SOMETHING ##
###############
def FindIntersectingMullions(mull_instance, comparison_group):
    """inputs mullion element and a category OR list of ids to gather elements to compare to"""
    if isinstance(comparison_group, BuiltInCategory):
        intersectionCollector = FilteredElementCollector(mull_instance.Document).WhereElementIsNotElementType()
        intersectionCollector.OfCategory(comparison_group).OfClass(Autodesk.Revit.DB.FamilyInstance)
    elif isinstance(comparison_group, list):
        intersectionCollector = FilteredElementCollector(mull_instance.Document, List[ElementId](comparison_group)).WhereElementIsNotElementType()
    else:
        pass

    excludedElems = List[ElementId]([mull_instance.Id])
    exclusionFilt = ExclusionFilter(excludedElems)
    intersectionCollector.WherePasses(exclusionFilt)

    intersectionFilt = ElementIntersectsElementFilter(mull_instance)
    intersectionCollector.WherePasses(intersectionFilt)

    return(intersectionCollector.ToElements())

def RevitDividePanelEquidistant(panel,divs,intermediateWidth=0):
    line = RevitCurtainPanelCurve(panel)
    panelWidth = (line.Length-((divs-1)*intermediateWidth))/divs
    listPoints = []
    for d in range(int(divs-1)):
        param = (panelWidth*(d+1)) + ((d + 0.5)*intermediateWidth)
        listPoints.append(line.Evaluate(param, False))
    return(listPoints)

###############
## SOMETHING ##
###############
def RemoveDuplicatePoints(incomingPoints):
    tol = 0.001
    if incomingPoints:
        returnList = [incomingPoints[0]]
        for point1 in incomingPoints:
            foundDuplicate = False
            for point2 in returnList:
                if point1.DistanceTo(point2) < tol:
                    foundDuplicate = True
            if not foundDuplicate:
                returnList.append(point1)
        return returnList
    else:
        return(None)

def InheritRoomLocation(storefrontWall):
    targetRoomNames = ["office", "conference", "meeting", "lounge", "av", "scrum", "conf", "small", "large", "medium", "micro", "brain", "class", "board", "exec", "po", "conv", "show"]
    phase = list(doc.Phases)[-1] 

    storefrontPanels = storefrontWall.CurtainGrid.GetPanelIds()
    storefrontMullions = storefrontWall.CurtainGrid.GetMullionIds()

    panelPoints = {}

    with rpw.db.Transaction("Create Curtain Wall") as tx:
        SupressErrorsAndWarnings(tx)

        for panelId in storefrontPanels:

            rooms = {}
            fromRoom = None
            toRoom = None
            roomNumber = None

            panel = doc.GetElement(panelId)

            panelPoint = panel.GetTransform().Origin
            panelPoints[panel.Id] = XYZ(panelPoint.X, panelPoint.Y, 0)

            fromRoomSize = 0
            toRoomSize = 0

            try:
                fromRoom = panel.FromRoom[phase]
            except:
                pass
            try:
                toRoom = panel.ToRoom[phase]
            except:
                pass

            if fromRoom:
                rooms.update({fromRoom.Id : fromRoom.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()})
                fromRoomSize = fromRoom.Area
            if toRoom:
                rooms.update({toRoom.Id : toRoom.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()})
                toRoomSize = toRoom.Area

            for roomId, roomName in rooms.items():

                if any (targetRoom in roomName.lower() for targetRoom in targetRoomNames):
                    roomNumber = doc.GetElement(roomId).get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()
                    break

            if not roomNumber:
                if (fromRoomSize < toRoomSize and fromRoom and toRoom) or (fromRoom and not toRoom):
                    roomNumber = doc.GetElement(fromRoom.Id).get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()
                elif (fromRoomSize > toRoomSize and fromRoom and toRoom) or (toRoom and not fromRoom):
                    roomNumber = doc.GetElement(toRoom.Id).get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()
                else:
                    roomNumber = None

            if roomNumber:
                panel.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(roomNumber)

        for mullionId in storefrontMullions:
            mullion = doc.GetElement(mullionId)
            mullionName = mullion.Name

            if mullion.LocationCurve:
                mullionCurve = mullion.LocationCurve 
                mullionPoint = mullionCurve.Evaluate(0.5,True)
                mullionPoint = XYZ(mullionPoint.X, mullionPoint.Y, 0)

                currentClosestPanel = [None, 1000]

                for panelId, panelPoint in panelPoints.items():
                    testPanel = doc.GetElement(panelId)
                    distToMullion = panelPoint.DistanceTo(mullionPoint)
                    if distToMullion < currentClosestPanel[1]:
                        currentClosestPanel = [panelId, distToMullion]

                closestPanel = doc.GetElement(currentClosestPanel[0])
                closestRoomName = closestPanel.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
                if closestRoomName:
                    mullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(closestRoomName)

    return(True)

def CurtainwallInheritRoomID(curtainwall):
    result = False
    return(result)

def StandardizeMullionSpacing(curtainwall):
    result = False
    return(result)

def PointInPolygon(point, boundaryPts):
    #Uses Math.Net
    result = False
    boundaryPoints = []
    for p in boundaryPts:
        boundaryPoints.append(MathNet.Spatial.Euclidean.Point2D(p.X,p.Y))

    point = MathNet.Spatial.Euclidean.Point2D(point.X,point.Y)
    polygon2D = MathNet.Spatial.Euclidean.Polygon2D(boundaryPoints)

    return(polygon2D.EnclosesPoint(point))

###########################
## ALVARO "IMPROVEMENTS" ##
###########################
def ECName():
    ec = ["_ec", "ec.", "existingconditions",
          "existing", "ec", "EC", ".EC", "-EC"]
    ecStrings = [i.lower() for i in ec]
    return(ecStrings)    

def RevitLoadECDocument(document, quiet=False):
    """
    THIS WILL EVENTUALLY HAVE TO ACCOMODATE
    MULTIPLE EC MODELS LIKE THE FACADE AND 
    CORE MODELS ON SEA_411 UNION_P1 OR
    WHATEVER
    """
    docEC_Future = []
    ecOrigin_Future = []
    
    docEC = None
    ecOrigin = None

    linkedInstances = FilteredElementCollector(document).OfClass(RevitLinkInstance) # Autodesk.Revit.DB.
    if linkedInstances:
        for i in linkedInstances:
            if not quiet: print("LINKED MODELS: {0}".format(str(i.Name)))
            if any(j in i.Name.lower() for j in ECName()):
                # future state - to be developed later with changes reconcild in SF2_Engine
                docEC_Future.append(i.GetLinkDocument())
                # used to line up the ec model
                ecOrigin_Future.append(i.GetTransform().Origin) 
                
                ecModelInst = i
                # used to line up the ec model
                ecTransform = i.GetTransform().Origin                
                
                if quiet == False: print("...FOUND EC MODEL: {0}".format(str(i.Name)))
                docEC = ecModelInst.GetLinkDocument()

        if docEC and quiet == False: print("...LOADED EC MODEL")
        if not docEC and quiet == False: print("...CHECK EC MODEL LINK BEFORE PROCEEDING")

    if not linkedInstances and quiet == False:
        print("...NO LINKED MODELS FOUND")
        print("...ERROR LOADING EC ELEMENTS")

    return([docEC, ecOrigin])
#######################
## SORTING FUNCTIONS ##
#######################
def Sort_Alist_By_Blist(Alist, Blist):
    """
    This will sort the first input list (Alist) by the
    values of the second input list(Blist). Only the second
    list needs to be a sortable data type (float, int, etc...)
    
    inputs:
        Alist - list of any data type
        Blist - list of qunatifiable data type
    
    returns:
        [sorted_Alist, sorted_Blist]
    """
    nestedSortedList = zip(*sorted(zip(Alist, Blist), key=lambda i: i, reverse=False))
    return(nestedSortedList)