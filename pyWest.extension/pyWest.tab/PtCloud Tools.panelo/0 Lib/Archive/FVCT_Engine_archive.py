import numpy as np
import math

import sys
sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\0_Panels\0_PanelingToolsScripts\Python")
import ASGG_DataExchange as DA
import time

import rhino3dm as rh
import compute_rhino3d as cr
from compute_rhino3d import NurbsSurface #must be declared explicitly; weird glitch
from compute_rhino3d import Mesh


#intersection = cr.Intersection.
#cr.Brep.GetVolume(polySrf)
class FVCT_Engine:
    def __init__(self, ptCloudJson):
        self.ptCloudJson = ptCloudJson
        
        # container list for python tuples
        self.ptCloud = None
    
    def JSONListToTuple(self):
        self.ptCloud = [tuple(i) for i in self.ptCloudJson]
        return(self.ptCloud)
    
    def PythonLoopVolumeTest(self):
        start = time.time()
        areas = [self.CylinderVolume(4.000, 6.000) for i in range(0, 8000000)]
        sumAreas = sum(areas)
        end = time.time()
        
        print("Python computation Time: {0} secs".format(round((end - start), 4)))
        
        return(sumAreas)
         
    def NumpyVolumeCalculation_Deprecated(self):
        start = time.time()
        
        # create numpy array - 1d array bc structure is not nested
        dType = [('x', float), ('y', float), ('z', float)]
        
        # create numpy array - 2d array [[x,y,z], [x,y,z], etc]
        ptCloudArray = np.array(self.JSONListToTuple(), dtype=dType)
    
        # get min max z coordinates
        ptCloudArraySorted = np.sort(ptCloudArray, order='z')  
        #ptCloudArraySorted = ptCloudArray[ptCloudArray[:,1].argsort()]
        print(ptCloudArraySorted)
        print()
        
        
        #_min = ptCloudArray.min(order='z')
        #_max = ptCloudArray.max(order='z')
        #print(_min)
        #print(_max)        
        
        #sum areasa
        sumAreas = None
        end = time.time()
        
        print("Numpy computation Time: {0} secs".format(round((end - start), 4)))
        return(sumAreas)
    
    def NumpyVolumeCalculation(self):
        start = time.time()
        
        ptCloudArray = np.array(self.ptCloudJson)
        
        #ptCloudSorted = np.sort(ptCloudArray.view('f8, f8, f8'), order='f2', axis=0).view(np.float)
        #print(ptCloudSorted)
        
        _min = np.min(ptCloudArray[:, 2])
        _max = np.max(ptCloudArray[:, 2])
        
        print(_min, _max)
        
        for i in np.nditer(ptCloudArray):
            print(i)
        
        #sum areasa
        sumAreas = None
        end = time.time()
        
        print("Numpy computation Time: {0} secs".format(round((end - start), 4)))
        return(sumAreas)        
        
    def MaterialCostDictionary(self):
        materials = {'LevelQuick RS': {'cost': 20.00, 'size': 50.00, 'yield': 2.80},
                     'Test Material': {'cost': 20.00, 'size': 50.00, 'yield': 2.80},
                    }
        return(materials)
    def QuantityPriceBreak(self):
        pass
    def MaterialCosting(self, sumArea, currentPrice):
        pass
    def ConvertToPoints(self, coordinateList):
        ptList = []
        for i in coordinateList:
            if i != None:
                ptList.append(rh.Point3d(i[0],i[1],i[2]))
        return(ptList)
    def CylinderVolume(self, radius, height):
        return(math.pi * (radius**2) * height)

def Main():
    """
    rather than creating a geometric model, why not a analytical model that
    adds hypothetical volumes to each point (arbitrary radius and height = maxHeight - zValue) 
    and calculates total volumes accross the entire field of points
    
    
    ptsArray *= cylinder volume
    
    1 get points
    2 get min and max z point coordinates
    3 calculate point height from level height
    3a solve level from points by getting the most common height after points have been rounded?
    4a 
    
    # create points
    #pts = ConvertToPoints(ptCloud)
    
    # why not class().method()??? - must figure out
    #cr.Mesh.CreatePatch(pts)
    """
    
    # get point clouds points from Reality Capture - coordinates must be placed in tuple, not list!
    ptCloud = DA.JSONTools().ReadJSON("C:/Users/aluna/Desktop/test.json")
    
    # convert JSON list to tuple for numpy array
    volumeObj = FVCT_Engine(ptCloud)
    
    # test python calculation time - 9 secs
    volumeObj.PythonLoopVolumeTest()
    
    # test numpy calculation time - 
    volumeObj.NumpyVolumeCalculation()
    

    

if __name__ == "__main__":
    Main()