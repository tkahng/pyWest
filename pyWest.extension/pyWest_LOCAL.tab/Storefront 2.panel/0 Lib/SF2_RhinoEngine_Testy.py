import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

def CreateVector(startPt, endPt):
    """
    Create a vector between a starting point and end point
    """
    vector = rh.Geometry.Vector3d((endPt.X - startPt.X),
                                 (endPt.Y - startPt.Y),
                                 (endPt.Z - startPt.Z))
    return(vector)
def IsClose2(aVal, bList, rel_tol=None, abs_tol=None):
    for i in bList:
        if abs(aVal-i) <= max(rel_tol * max(abs(aVal), abs(i)), abs_tol):
            return(True)
def IsClose(aVal, bVal, rel_tol=None, abs_tol=None):
    if abs(aVal-bVal) <= max(rel_tol * max(abs(aVal), abs(bVal)), abs_tol):
        return(True)

#########################################
## ALIGN ALL CURVE DIRECTIONS-NEW LIST ##
#########################################

#######################################
## TEST FOR COLLINEAR CURVE SEGMENTS ##
#######################################
def CollinearIndexes(crvList=None):
    """
    Find curves that are collinear and 
    whose end points are touching. Record
    the index pairing when the conditions
    are met.
    """
    tol = 0.0001
    vecList = [CreateVector(i.PointAt(1.0), i.PointAt(0.0)) for i in crvList]
    
    recordIndexes = []
    for i in range(0, len(crvList)-1):
        for j in range(i+1, len(crvList)):
            crossProduct = rh.Geometry.Vector3d.CrossProduct(vecList[i], vecList[j])
            zeroVec = (crossProduct.X + crossProduct.Y + crossProduct.Z)
            if IsClose(zeroVec, 0.0, tol, tol) and rh.Geometry.Intersect.Intersection.CurveCurve(crvList[i], crvList[j], tol, tol):
                recordIndexes.append([i,j])
    print(recordIndexes)
    return(recordIndexes)
def RearrangeCollinearCrvsForJoin(crvList, indexList):
    def AdjustIndexes(indexList):
        """
        Loop through index list and append
        lists with matching elements
        """
        newIndex = []
        for i in range(0, len(indexList)-1):
            if indexList[i] is not None:
                for j in range(i+1, len(indexList)):
                    if indexList[j] is not None:
                        if indexList[i][1] in indexList[j]:
                            newIndex[i].append(indexList[j][0])
                            newIndex[j] = None
        return(newIndex)
    print(AdjustIndexes(indexList))
    newCrvs = []
    for i, indexPair in enumerate(AdjustIndexes(indexList)):
        if indexPair is not None:
            newCrv = rh.Geometry.Curve.JoinCurves([crvList[j] for j in indexPair])
            opt = rh.Geometry.CurveSimplifyOptions.SplitAtFullyMultipleKnots
            tol = sc.doc.ModelAbsoluteTolerance
            angTol = sc.doc.ModelAngleToleranceDegrees
            newCrv[0].Simplify(opt, tol, angTol)
            newCrvs.append(newCrv)
    print(newCrvs)
    
    # bake
    for i in newCrvs:
        for j in i:
            sc.doc.Objects.AddCurve(j)
    sc.doc.Views.Redraw()

#################
## PREP CURVES ##
#################
def PrepInputCrvs(crvList):
    # convert curves of whatever to Nurbs curves
    newCrvList = []
    for i in crvList:
        nurbsCrvs = i.ToNurbsCurve().DuplicateSegments()
        if nurbsCrvs:
            for j in nurbsCrvs:
                j.Domain = rh.Geometry.Interval(0.0, 1.0)
                newCrvList.append(j)
        else:
            i.ToNurbsCurve()
            i.Domain = rh.Geometry.Interval(0.0, 1.0)
            newCrvList.append(i)
    
    # identify collinear curve segments that
    # aren't joined and join them into one
    # larger straight curve
    recordIndexes = CollinearIndexes(crvList)
    RearrangeCollinearCrvsForJoin(crvList, recordIndexes)
    
    # split curves at perpedicular intersections
    
    
    return(newCrvList)

##########
## MAIN ##
##########
def Main():
    # collect and prep curves
    crvs = [rs.coercecurve(i) for i in rs.ObjectsByLayer("CollinearTest")]
    crvList = PrepInputCrvs(crvs)

if __name__ == "__main__":
    Main()