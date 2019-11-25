"""

# namespace.class().method() | namespace.class().variable

the methods in this script require inputs and are not just self.variables
because the loop is handled in the class and not just dealing with a  
single element

"""
import traceback

# TRY/EXCEPT TO SHOW ERROR IN REVIT
try:
    import numpy as np # linear algebra library for arrays
    from scipy import stats # statical library for arrays
    import math
    import time
    import sys
    import array
    
    import FV_Materials as FV_M
    sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\0 Lib")
    import WW_DataExchange as DE


    class FV_Engine:
        def __init__(self, test=False, **kwargs):
            self.test = test
            self.kwargs = kwargs         
            
            # optional **kwargs for access outside Revit
            if kwargs:
                pass
            
            # subprocess called from Revit
            else:
                # create data exchange object | standard read for getting input args | write for results of calc
                self.jsonObj = DE.JSONTools()
                self.writeJSONresults = r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\PtCloudTools.panel\Lib\JSON Exchange"
                if self.test == True:
                    self.readJSONinputs = r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\PtCloudTools.panel\Lib\JSON Exchange\FV_InputArgs.json" # same inputs for now until further development
                elif self.test == False:
                    self.readJSONinputs = r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\PtCloudTools.panel\Lib\JSON Exchange\FV_InputArgs.json"
            
            self.ptCloudZ = None
            
            # output data
            self.totalVolume = None
            self.numBags = None
            self.totalCost = None
    
            self.timeToComplete = None # output var for testing 

        # UTILITY
        def PrintOut(self, floorResults, buildingName='testBuilding'):  
            title = "{0} Float Volume Analyis and Estimate".format(buildingName)
    
            firstLine = 'Total number of bags: {0}'.format(self.numBags)
            secondLine = 'Total material cost: ${0}'.format(self.totalCost) 
    
            print(title)
            print(firstLine)
            print(secondLine)
    
        def ScanRadiusDB(self, scanQuality):
            # radius squared for vectorization
            scanRadius = [0.010, 0.250, .0025, 0.5]
            squaredOutput = scanRadius[scanQuality] ** 2
            
            return(squaredOutput)
    
        # CALCULATE
        def CalculateVolume(self, ptCloudArray, scanQuality=0, printTime=False):
            """
            This method uses arrays and is vectorized
    
            Vectorization: is the process of converting an algorithm from operating on a
                           single value at a time to operating on a set of values (vector)
                           at one time. Often in 1:1 operations between 2 arrays with values
                           at matching indices.
            """
            startTime = time.time()
            
            # calculate mode to determine floor level | .mode(array[row, column]) [return index]| [:all rows, column] - returns array of just z values
            self.ptCloudZ = ptCloudArray[:,2]
            floorLevelHeight = stats.mode(ptCloudZ)[0]  
            
            # array of heights
            ptCloudZHeights = np.subtract(ptCloudZ, floorLevelHeight)
            
            # array of radius and pi
            rSqr = self.ScanRadiusDB(scanQuality)
            floorLevelHeight = np.array(rSqr * math.pi)
            
            # multi step multiplication
            volumes = np.multiply(floorLevelHeight, ptCloudZHeights)
    
            # sum values for total volume
            self.totalVolume = np.sum(volumes)
            endTime = time.time()
    
            self.timeToComplete = "Numpy computation Time: {0} secs".format(round((endTime - startTime), 4))
            if printTime == True:
                print(self.timeToComplete)
    
            return(self.totalVolume)
        
        # ESTIMATE
        def LevelingCompoundEstimate(self, compoundVolume, floatMaterial, margin=1.10):
            # cost and material yield should be consistently formatted - too deeply nested
            cost = floatMaterial['cost']
            materialYield = floatMaterial['yield']
    
            self.numBags = round((round((compoundVolume / materialYield), 0) + 1) * margin, 0)
            self.totalCost = self.numBags * cost
    
            if self.numBags != None and self.totalCost != None:
                return([self.numBags, self.totalCost])
    
            else:
                return(None)

        # CLASS MAIN
        def RunFV(self):
            # overwrite whatever json file exists to ensure if the script fails you don't get an old result
            self.jsonObj.WriteJSON(None, self.writeJSONresults, "FV_Results")
            
            # outside input
            if self.kwargs:
                ptCloudsJSON = None
                self.floatMaterials = None
            
            # subprocess called from Revit
            else:
                # read json inputs
                self.inputArgsList = self.jsonObj.ReadJSON(self.readJSONinputs)                
        
                # get point clouds points from Reality Capture and material | [[jsonPath, material], []]
                ptCloudsJSON = [self.jsonObj.ReadJSON(jsonPath[0]) for jsonPath in self.inputArgsList] #[:2] #testing at a small scale
                self.floatMaterials = [FV_M.MaterialCostDictionary()[mat[1]] for mat in self.inputArgsList]
        
            # creat arrays of the python lists [n, n, n, n]
            self.ptCloudsJSON_array = np.array(ptCloudsJSON) # array creation is too deeply nested; why???     
            #print(len(self.ptCloudsJSON_array[0])) # check array size
            
            FV_Results = []
            for i, data in enumerate(self.ptCloudsJSON_array):
                # collect the volume result of each chosen point cloud
                floatVolume = self.CalculateVolume(data, scanQuality=0, printTime=True)
                # material costs
                FV_Results.append(self.LevelingCompoundEstimate(floatVolume, self.floatMaterials[i], margin=1.10))
    
            # write results to a Json file
            self.jsonObj.WriteJSON(FV_Results, self.writeJSONresults, 'FV_Results')
    
            return(FV_Results)
    
    # MAIN INVOKED BY SUBPROCESS
    def Main():
        FVoutput = FV_Engine(False).RunFV()
        return(FVoutput)
    
    if __name__ == "__main__":
        Main()

except:
    print(traceback.format_exc())