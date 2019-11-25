"""

*args is used here because this script is designed to be called directly 
and as an external session from an ironpython / python2 script.

"""

import numpy as np # linear algebra/fast array library
from scipy import stats # statical library; usinng to calculate floor level based on mode
import math # standard math operations
import time
import rhino3dm as rh
import sys

import FVCT_Materials as FVCT_M

sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\0_PANGOLIN\0_PanelingToolsScripts\Python")
import ASGG_DataExchange as DA

class FVCT_Engine:
    def __init__(self, jsonFilePath=None, materialChoice=None, *args):
        # if args from the outside, then jsonFilePath is getting a list of all arguments
        # must be parsed        
        
        self.dataObj = DA.JSONTools() # namespace.class().method() | namespace.class().variable
        
        # required parameters
        if type(jsonFilePath) is not list:
            self.jsonFilePath = jsonFilePath
            self.materialChoice = materialChoice
        
        # i am not even using args, how do i use args???
        elif type(jsonFilePath) is list:
            self.jsonFilePath = jsonFilePath[1]
            self.materialChoice = jsonFilePath[2]

        # derived variables
        self.ptCloudJson = None

        # cost method variables
        self.numBags = None
        self.totalCost = None

    #____________________________UTILITIES__________________________________________
    def CylinderVolume(self, radius, height):
        return(math.pi * (radius**2) * height)    

    #____________________________DEPRECATED / OLD REFERENCE_________________________
    def NumpyOverflowForReference(self):
        # np.sort(numpyArray.view('string with types at each location in sublist'), order='column is f0,1,2 etc', axis=0).view(np.type)
        ptCloudSorted = np.sort(ptCloudArray.view('f8, f8, f8'), order='f2', axis=0).view(np.float)
        print(ptCloudSorted)        

        for i in np.nditer(ptCloudArray, op_flags=['readwrite'], flags=['external_loop'], order='C'):
            height = _max - i[2]
            print(height)
            volumes[:] = self.CylinderVolume(2.000, height)

        #_min = np.min(ptCloudArray[:, 2])
        #_max = np.max(ptCloudArray[:, 2])        

    #____________________________VOLUME CALCULATION_________________________________
    def PythonLoopVolumeTest(self):
        start = time.time()
        _min = min(self.ptCloudJson)
        _max = max(self.ptCloudJson)
        print(_min, _max)

        areas = [self.CylinderVolume(4.000, 6.000) for i in self.ptCloudJson]
        sumAreas = sum(areas)
        end = time.time()

        print("Python computation Time: {0} secs".format(round((end - start), 4)))

        return(sumAreas)

    def CalculateVolume(self):
        """
        HOW DO I VECTORIZE THIS TO MAKE IT FASTER???

        ALSO THIS SHOULD HAVE SEPARATE VOLUME OUTPUTS:
        A FILLED IN VOLUME AND A SHAVED VOLUME!!!
        """
        def PrintOut():
            print(floorLevelHeight is list)
            print(floorLevelHeight)
            print(volumes.shape)
            print(round(sumAreas,2))
            print("Numpy computation Time: {0} secs".format(round((end - start), 4)))

        start = time.time()

        # create a numpy array from the json list data
        ptCloudArray = np.array(self.ptCloudJson)
        #print(ptCloudArray)
        
        # calculate mode to determine floor level | .mode(array[row, column]) [return index]| [:all rows, column]
        floorLevelHeight = stats.mode(ptCloudArray[:,2])[0]
        #print(floorLevelHeight)

        # create empty array to be filled in by loop
        # determine how this can be vectorized
        volumes = np.empty([ptCloudArray.shape[0], 1], dtype=float) #[rows, columns]

        # THIS SHOULD BE MADE FASTER!!!
        for index, pt in np.ndenumerate(ptCloudArray):
            # filter only Z pt values
            if index[1] == 2:
                height = abs(floorLevelHeight - pt) #obtain absolute value
                volumes[index[0]] = self.CylinderVolume(.250, height)

        #sum areas
        sumAreas = np.sum(volumes)
        end = time.time()

        return(sumAreas)

    #____________________________MATERIAL ESTIMATE__________________________________
    def LevelingCompoundEstimate(self, compoundVolume, margin=1.10, fancyPrint=False):
        def PrintFancy():
            print('Total number of bags: {0}'.format(self.numBags))
            print('Total material cost: ${0}'.format(self.totalCost))

        # cost and material yield should be consistently formatted
        cost = self.floatMaterial['cost']
        materialYield = self.floatMaterial['yield']

        # 
        self.numBags = round((round((compoundVolume / materialYield), 0) + 1) * margin, 0)
        self.totalCost = self.numBags * cost

        if fancyPrint == True:
            PrintFancy()

        if self.numBags != None and self.totalCost != None:
            return('Total number of bags: {0}\nTotal material cost: ${1}'.format(self.numBags, self.totalCost))
            
        else:
            return(False)


    #____________________________MAIN METHOD________________________________________
    def RunEstimate(self, fancyPrint=False):
        # get point clouds points from Reality Capture and material
        self.ptCloudJson = DA.JSONTools().ReadJSON(self.jsonFilePath)#[:2] #testing at a small scale
        self.floatMaterial = FVCT_M.MaterialCostDictionary()[self.materialChoice]
        
        # calculate volume
        floatVolume = round(self.CalculateVolume(), 3)

        # material costs
        estimateOutput = self.LevelingCompoundEstimate(floatVolume, margin=1.10, fancyPrint=fancyPrint)
        #print(estimateOutput)
        
        # write results to a Json file
        dataObj = DA.JSONTools("C:/Users/aluna/Documents/WeWork Code/Float Volume Calculation Tool/Lib/JSON Exchange")
        dataObj.WriteJSON('FVCT_Results', estimateOutput)

        return(estimateOutput)
    def RunEstimate(self, fancyPrint=False):
        pass

def TestMain():
    ptCloudPath = "C:/Users/aluna/Desktop/FVCT_Test.json"
    materialChoice = "LevelQuick RS"
    #FVCToutput = FVCT_Engine(ptCloudPath, materialChoice).CalculateVolume()
    FVCToutput = FVCT_Engine(ptCloudPath, materialChoice).RunEstimate(False)
    print(FVCToutput)

def Main():
    inputArgs = DA.JSONTools().ReadJSON(filePaths)
    
    # inputArgs = [[x,y,z], i, j]
    for i, ptCloud in enumerate(inputArgs[0]):
        material = inputArgs[1]
    
    # read json file with parameters for 
    pass


if __name__ == "__main__":
    #figure out what exactly is happening here...
    args = sys.argv
    
    # instantiate object
    FVCToutput = FVCT_Engine(args).RunEstimate(True)
    
    # Test
    #TestMain()
    
    #Main()



