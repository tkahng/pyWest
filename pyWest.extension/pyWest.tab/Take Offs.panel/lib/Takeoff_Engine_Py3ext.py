"""
pyVersion = Python 3.7xx


"""
import os
import sys
import logging
import math
import _csv as csv
import json
import math

import rhino3dm as rh
import compute_rhino3d as rc

import WW_RhinoRevitConversion as RRC # only run this in Python 3.7xx environment
import WW_ExternalPython as EP
import WW_DataExchange as DE

class RoomData_IT_ExternalOperations:
    def __init__(self):
        self.jsonFileName = "{0}__TO__OriginalFile".format(os.path.basename(__file__).split(".")[0])
    def RoomBoundCL(self, rhinoCrvs):
        """
        this must be run from Python 3.7xx
        
        The mathmatical basis for this can be found here:
        https://www.designingbuildings.co.uk/wiki/Measurement
    
        cl is centerline
        """
        # centerline = internalGirth + numCorners * ((2*wallWidth)/2)
        # internalGirth =  
        
        pt = rh.Point3d(0,0,0)
        print(pt)
        print(pt.X)
        print(type(pt))
        
        pts = [rh.Point3d(i,j,0) for i in range(3) for j in range(3)]
        print(pts)
        crv = rh.NurbsCurve.Create(False, 1, pts)
        print(crv)
        
        ## what elements would only have a single boundary segment
        #for nestedCrvList in rhinoCrvs:
            #for crvList in nestedCrvList:
                ## this should work like this: rh.Geometry.Curve.JoinCurves(crvList)
                #joinedCrv = rc.Curve.JoinCurves(crvList)
                #print(joinedCrv)
                #for i in crvList:
                    #print(i)
        
        clLength = 98945.59
        DE.JSONTools().WriteJSON(clLength, "{0}\JSON_talk\\".format(os.path.dirname(__file__)), self.jsonFileName)

def Main():
    externalArguments = sys.argv[1]
    
    # external operations for RoomData_IT().EstimateCableTrays()
    if externalArguments == "EstimateCableTrays":
        # read 
        crvPts = DE.JSONTools().ReadJSON("{0}\JSON_talk\Takeoff_Engine__TO__Takeoff_Engine_Py3ext.json".format(os.path.dirname(__file__)))
        print(crvPts)
        
        # reconstruct curves
        rhinoCrvs = RRC
        
        roomDataObj = RoomData_IT_ExternalOperations()
        roomDataObj.RoomBoundCL(rhinoCrvs=rhinoCrvs)
        
    # external operations for something else
    elif externalArguments == None:
        print("input args are not working")
        

if __name__ == "__main__":
    Main()