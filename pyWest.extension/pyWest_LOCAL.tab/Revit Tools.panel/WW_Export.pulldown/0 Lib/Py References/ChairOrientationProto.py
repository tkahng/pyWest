from Rhino import Geometry as rg
import rhinoscriptsyntax as rs
import scriptcontext as sc
import math as m

import sys
sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\0 Lib")
import WW_DataExchange as DE

class Chair:
    def __init__(self, chair, CL):
        # properties
        self.chair = chair
        self.CL = CL

def CollectChairs():
    # collect chairs + CLs
    chair0 = rs.coercebrep(rs.ObjectsByLayer("chair0"))
    chair0_CL = rs.coercecurve(rs.ObjectsByLayer("chair0_CL"))
    chair1 = rs.coercebrep(rs.ObjectsByLayer("chair1"))
    chair1_CL = rs.coercecurve(rs.ObjectsByLayer("chair1_CL"))
    
    # create chair objects
    chair0_Obj = Chair(chair0, chair0_CL)
    chair1_Obj = Chair(chair1, chair1_CL)
    
    return([chair0_Obj, chair1_Obj])

def Curve2Vector(chairCL):
    # create a vector from an input line/curve
    startPt = chairCL.PointAtNormalizedLength(0)
    endPt = chairCL.PointAtNormalizedLength(1)
    
    vector = rg.Vector3d((endPt.X - startPt.X),
                         (endPt.Y - startPt.Y),
                         (endPt.Z - startPt.Z))
    return(vector)

def GetAnglesBtwnVectors(referenceVector):
    worldX = rg.Plane.WorldXY.XAxis
    angle = rg.Vector3d.VectorAngle(worldX, referenceVector)
    return(angle)

def RotationTest(chairCL, rotationAngle, bake=True):
    cl_Center_t = chairCL.NormalizedLengthParameter(.5)[1]
    cl_Center_pt = chairCL.PointAtNormalizedLength(.5)
    
    rotationNormal = rg.Plane.WorldXY.Normal
    chairCL.Rotate(-rotationAngle + (-m.pi), rotationNormal, cl_Center_pt) # modifies object, if you need new curve create copy
    
    if bake == True:
        sc.doc.Objects.AddCurve(chairCL)
        sc.doc.Views.Redraw()

def Main():
    # collect chairs
    chairs = CollectChairs()
    
    # obtain chair CL vectors
    chair_Vectors = [Curve2Vector(i.CL) for i in chairs]
    
    # measure vector transformation i <> WorldX axis -> radians
    transformationList = [GetAnglesBtwnVectors(i) for i in chair_Vectors]
    
    [RotationTest(crv.CL, transformationList[i]) for i,crv in enumerate(chairs)]

if __name__ == "__main__":
    Main()