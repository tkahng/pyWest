import math

from Rhino import Geometry as rg
import rhinoscriptsyntax as rs
import scriptcontext as sc

class Utilities:
    def __init__(self):
        pass
    
    ####################
    ## BAKE UTILITIES ##
    ####################
    def BakePoints2(self, ptList):
        for i in ptList:
            sc.doc.Objects.AddPoint(i)
        sc.doc.Views.Redraw()
    
    def BakePoints(self, ptList):
        for i in ptList:
            for j in i:
                if j != None:
                    sc.doc.Objects.AddPoint(j)
        sc.doc.Views.Redraw()
    
    def BakeCrvs(self, crvList):
        for i in crvList:
            sc.doc.Objects.AddCurve(i)
        sc.doc.Views.Redraw()
    
    def VisualizeSorting(self, crvList):
        rs.EnableRedraw(False)
        for i,crv in enumerate(crvList):
            midPt = crv.PointAt((crv.Domain[1] - crv.Domain[0])/2 + crv.Domain[0])
            rs.AddTextDot(i, midPt)
    
    
    ###############
    ## UTILITIES ##
    ###############
    def RemoveDuplicates(self, originalFunction):
        def WrapperFunction(*args, **kwargs):
            outList = []
            setList = set()
            for val in originalFunction(*args, **kwargs):
                if not val in setList:
                    outList.append(val)
                    setList.add(val)
            return(outList)
    
    def RemoveDuplicatesWithinPartnerLists(self, someList, mapList):
        # describe logic here #
        outList = []
        setList = set()
        for i,val in enumerate(someList):
            if not val in setList and mapList[i] != mapList[i-1]:
                outList.append(val)
                setList.add(val)
            elif val in setList and mapList[i] != mapList[i-1]:
                outList.append(val)
        self.interParams = mapList
        self.indexes = outList
        return(self.interParams)
    
    def SortListAndMapPartnerList(self, listA, listB, reverse=False):
        # i is assumed to be [0] in tuple, unless specified i[1]
        sortedLists = zip(*sorted(zip(listA, listB), key=lambda i: i, reverse=reverse))
        sortedUnpacked = [i for i in sortedLists]
        
        self.indexes = list(sortedUnpacked[0])
        self.interParams = list(sortedUnpacked[1])
    
    def SortCrvsByXY(self, crvList, reverse=False):
        # CONSIDER AVERAGING POINTS ALONG 0.0, 0.5, 1.0
        
        # assume all building is in the +X +Y coordinate plane
        centroids = [i.PointAt(0.5) for i in crvList]
        
        sortedLists = zip(*sorted(zip(crvList, centroids), key=lambda i: (i[1][0], i[1][1]), reverse=reverse))
        sortedUnpacked = [i for i in sortedLists]
        
        self.wallCL_List = list(sortedUnpacked[0])
        
    def IsClose(self, aVal, bValList, rel_tol=None, abs_tol=None):
        for bVal in bValList:
            if abs(aVal-bVal) <= max(rel_tol * max(abs(aVal), abs(bVal)), abs_tol):
                return(True)


class Convert_Revit2Rhino:
    def __init__(self):
        pass


class WallCLPrep:
    def __init__(self, wallCL_List):
        # input parameters
        self.wallCL_List = wallCL_List
        
        # derived variables
        self.segmentWallList = []
        
        self.toSplitOrNotToSplit = [] # not so clever...
        self.indexes = []
        self.interPoints = []
        self.interParams = []
        
        self.IsCrvBisected = []
        self.newWallCL_List = []
        
        # global variables
        self.tol = 0.0001
    
    #################
    ## PREP CURVES ##
    #################
    def PrepInputCrvs(self):
        # convert to nurbs curves then explode and reparameterize
        # use these domains to identify parameters on curves which will need to be split
        for i in self.wallCL_List:
            nurbsCrvs = i.ToNurbsCurve().DuplicateSegments()
            if nurbsCrvs:
                for j in nurbsCrvs:
                    j.Domain = rg.Interval(0.0, 1.0)
                    self.segmentWallList.append(j)
            else:
                i.ToNurbsCurve()
                i.Domain = rg.Interval(0.0, 1.0)
                self.segmentWallList.append(i)
        return(self.segmentWallList)
    
    # UNIQUE INTERSECTIONS
    def FindIntersForSplitting_Pts(self):
        for i in range(0, len(self.segmentWallList)-1):
            for j in range(i+1, len(self.segmentWallList)):
                inter = rg.Intersect.Intersection.CurveCurve(
                self.segmentWallList[i],
                self.segmentWallList[j], 
                self.tol, self.tol)
                if inter:
                    end_t_values = [0.0, 1.0]
                    for k in inter:
                        if k.ParameterA and k.ParameterB not in end_t_values:
                            self.interPoints.append([k.PointA, k.PointB])
                        elif k.ParameterA not in end_t_values:
                            self.interPoints.append([k.PointA, None])
                        elif k.ParameterB not in end_t_values:
                            self.interPoints.append([None, k.PointB])
                else:
                    self.interPoints.append([None, None])
        return(self.interPoints)
    def FindIntersForSplitting(self):
        # identify CLs that are bisected by another CL to split
        for i in range(0, len(self.segmentWallList)): 
            for j in range(i+1, len(self.segmentWallList)):
                inter = rg.Intersect.Intersection.CurveCurve(
                self.segmentWallList[i],
                self.segmentWallList[j], 
                self.tol, self.tol)
                if inter:
                    # filter out start and end parameter intersections
                    end_t_values = [0.0, 1.0] 
                    for k in inter:
                        if not self.IsClose(k.ParameterA, end_t_values, self.tol, self.tol) and not self.IsClose(k.ParameterB, end_t_values, self.tol, self.tol):
                            self.interParams.extend([k.ParameterA, k.ParameterB])
                            self.indexes.extend([i,j])
                        elif not self.IsClose(k.ParameterA, end_t_values, self.tol, self.tol) and self.IsClose(k.ParameterB, end_t_values, self.tol, self.tol):
                            self.interParams.append(k.ParameterA)
                            self.indexes.append(i)
                        elif self.IsClose(k.ParameterA, end_t_values, self.tol, self.tol) and not self.IsClose(k.ParameterB, end_t_values, self.tol, self.tol):
                            self.interParams.append(k.ParameterB)
                            self.indexes.append(j)
        # remove duplicate intersections and sort indexes w/ map
        self.RemoveDuplicatesWithinPartnerLists(self.indexes, self.interParams)
        self.SortListAndMapPartnerList(self.indexes, self.interParams)
        
        # reverse lists to avoid altering index order of original CL list
        self.interParams.reverse()
        self.indexes.reverse()
    def SplitBisectedCLs(self):
        for i,index in enumerate(self.indexes):
            split = self.segmentWallList[index].Split(self.interParams[i])
            if split:
                splitCrvs = [i for i in split]
                splitCrvs.reverse()
                for crvSegment in splitCrvs:
                    self.segmentWallList.insert(index+1, crvSegment)
            self.segmentWallList.pop(index)
    
    def FindECIntersections(self):
        # this is to create nib walls
        pass
    
    def Run_WallCLPrep(self):
        # sort input centerlines
        self.SortCrvsByXY(self.wallCL_List)
        
        # clean up incoming crv data / explode joined curves to reveal segements
        self.PrepInputCrvs()
        
        # find intersections between curves
        self.FindIntersForSplitting()
        
        # split bisected centerlines
        self.SplitBisectedCLs()


class DivideCLs:
    def __init__(self):
        pass
    
    def DivideCrvJustificationMod(self, crvList, divLength, justification=2, offsetValue=0, bake=False):
        """
        Point Division Types:
            [0 + Value] = custom value from start
            [C + Value] = custom value from center +-
            [R + Value] = custom value from end
            
        MUST INCLUDE A WAY TO ADJUST OR CLAMP ENDS INDEPENDENTLY TO ACHIEVE CORNERS
        """
        totalParameters = []
        for crv in crvList:
            crvLength = crv.GetLength()
            
            # calculate the number of division segements that fit on curve
            divisionCount = int(round((crvLength/divLength),0) - 1)
            
            # HOW DO YOU DEAL WITH 0 DIVISION LENGTHS?
            
            # difference between total divided length and curve length
            lengthDifference = crvLength - (divLength * divisionCount)
            
            # manage point and parameter offsets here
            # have to figure out how to manage list inputs
            if justification == 0:
                self.startModification = offsetValue
            elif justification == 1:
                self.startModification = lengthDifference + offsetValue
            elif justification == 2:
            	# + towards curve end
                # - towards curve start
                self.startModification = (lengthDifference/2) + offsetValue
            elif justification == 4:
                crv.Reverse()
                self.startModification = offsetValue
            elif justification == 6:
                pass
                # call point justification method from here, return startmodification
                self.DivideCrvJustificationModPt(crv, pt, divLength, fillStart=True, bake=True)
            
            self.startModification = {0 : offsetValue,
                                      1 : lengthDifference + offsetValue,
                                      2 : (lengthDifference/2) + offsetValue}
                                      
            
            lengthList = [i for i in rs.frange(self.startModification[justification], crvLength, divLength)]
            
            # calculate parameters and points
            parameters = [crv.LengthParameter(len)[1] for len in lengthList]
            totalParameters.append(parameters)
        
        print(len(totalParameters))
        
        if bake ==  True:
            points = [crv.PointAt(t) for tList in totalParameters for t in tList]
            
            for pt in points:
                sc.doc.Objects.AddPoint(pt)
            sc.doc.Views.Redraw()
            
            return(points)
        
        else:
            return(parameters)
    
    def Run_DivideCLs(self):
        # run curve division
        self.DivideCrvJustificationMod(self.segmentWallList, 1, 1, True, True)


class Doors:
    def __init__(self):
        pass


class ParentClass(Utilities, Convert_Revit2Rhino, WallCLPrep, DivideCLs, Doors):
    def __init__(self, wallCL_List):
        # instantiate classes in this file
        Utilities.__init__(self)
        Convert_Revit2Rhino.__init__(self)
        WallCLPrep.__init__(self, wallCL_List)
        DivideCLs.__init__(self)
        Doors.__init__(self)
    
    def Run_SF2_RhinoEngine(self):
        # prep wall centerlines
        self.Run_WallCLPrep()
        
        self.FindIntersForSplitting_Pts()
        self.VisualizeSorting(self.segmentWallList)
        self.BakePoints(self.interPoints)
        self.BakeCrvs(self.segmentWallList)
        
        # divide Crvs
        self.Run_DivideCLs()
        
        # determine continguous curves
        # IS THERE A WAY TO TAKE THE INTERSECTION INDICES AND 
        
        # how to deal with domain of door along curve if door


"""
WALL PREP WILL HAVE TO TAKE INTO ACCOUNT
DOOR AND DOOR WIDTH IN ORDER TO CHECK
WHETHER THE MODEL IS MODELLED CORRECTLY
"""

def Main():
    # collect crvs
    wallCL_List = [rs.coercecurve(i) for i in rs.ObjectsByLayer("Crvs")]
    
    # prepare wall centerlines for divisions
    ParentClass(wallCL_List).Run_SF2_RhinoEngine()

if __name__ == "__main__":
    Main()