"""
# namespace.class().method() | namespace.class().variable

the methods in this script require inputs and are not just self.variables
because the loop is handled in the class and not just dealing with a  
single element


LEVEL UP CAN ALSO BE USED FOR AUTOMATIC USF GENERATOR BY LEVERAGING A CONVEX HULL ALGORITHM
"""

import traceback

# TRY/EXCEPT TO SHOW ERROR IN REVIT
try:
    import numpy as np # linear algebra library for arrays
    from scipy import stats # statistical library for arrays
    import math
    import sys
    import array
    import os
    
    def ShiftFilePath(path, branchesBack=1, append=None):
        pathReverse = path[::-1]
        newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
        newPath = newPathBackwards[::-1]
    
        if type(append) is str: return(r"{0}\{1}".format(newPath, append))    
    
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 3, r"0 Lib"))
    import WW_DataExchange as DE
    import WW_Debug # contains profiler to test execution time
    
    import LU_Utilities as LU_U
    import LU_Materials as LU_M
    
    class LU_Engine:
        """
        Because this was originally written to be ran from outside Revit, with inputs
        taken from the Revit user, the class reads its inputs from the 
        """
        
        def __init__(self, ptCloudArray=None, materialChoice="Ardex K10", scanVendor="WeWork", scanner="ScannerA", buildingMetadata=None):
            # input parameters
            self.ptCloudArray = ptCloudArray
            if not self.ptCloudArray: raise Exception("No point cloud array was found at instantiation") 
            
            self.materialChoice = materialChoice
            self.scanVendor = scanVendor
            self.scanner = scanner
            self.buildingMetadata = buildingMetadata
            if not self.buildingMetadata: self.buildingMetadata = "NA_CHI_800 Wells St_0"            
            
            # derived material parameters
            self.materialMetadata = LU_M.FloatMaterialDict()[self.materialChoice]
            self.materialCost = self.materialMetadata['cost']
            self.materialCoverage = self.materialMetadata['coverage']
            
            # derived scanner parameters
            self.scannerDensity = LU_U.ScanRadiusDB()[self.scanVendor][self.scanner]['Density']
            
            # derived building metadata
            buildingDataObj = LU_U.FileNameParser(self.buildingMetadata)
            self.continent = buildingDataObj.continent
            self.city = buildingDataObj.city
            self.buildingName = buildingDataObj.buildingName
            self.floorNum = buildingDataObj.floorNum            
            
            # output dataArray
            self.ptCloudZ = None
            self.ptCloudZHeights = None
            self.levelElevationHeight = None            
            
            self.totalVolume = None
            self.numBags = None
            self.totalCost = None
    
        # CALCULATE VOLUME
        @WW_Debug.Profiler
        def CalcVolume(self, levelOverride=False):
            """
            This method uses arrays and is vectorized
    
            Vectorization: is the process of converting an algorithm from operating on a
                           single value at a time to operating on a set of values (vector)
                           at one time. Often in 1:1 operations between 2 arrays with values
                           at matching indices.
            """
            # calculate mode to determine floor level | .mode(array[row, column]) [return index]| [:all rows, column] - returns array of just z values
            self.ptCloudZ = self.ptCloudArray[:,2]
            self.levelElevationHeight = stats.mode(self.ptCloudZ)[0]  
            
            # array of heights
            self.ptCloudZHeights = np.subtract(self.levelElevationHeight, self.ptCloudZ) # if positive: depression; if negative: undulation
            
            # array of radius and pi
            rSqr = self.scannerDensity
            self.levelElevationHeight = np.array(rSqr * math.pi)
            
            # multi step multiplication
            volumes = np.multiply(self.levelElevationHeight, self.ptCloudZHeights)
    
            # sum values for total volume
            self.totalVolume = np.sum(volumes) / 1728 # convert to ft3
            return(self.totalVolume)
        
        # CALCULATE MATERIAL QUANTITY
        def CalcMaterialQty(self, margin=1.10):
            self.numBags = round((round((self.totalVolume / self.materialCoverage), 0) + 1) * margin, 0)
            return(self.numBags)
        
        # CALCULATE MATERIAL COST
        def CalcMaterialCost(self):
            self.totalCost = self.numBags * self.materialCost
            return(self.totalCost)

        # RUN
        def Run_LU_Engine(self):
            # collect the volume result of each chosen point cloud
            floatVolume = self.CalcVolume(levelOverride=False)
            
            # material costs
            self.CalcMaterialQty(margin=1.10)
            
            
            # this gets sent to pretty print or whatever
            LU_Results.append(self.PrettyOutput(printOut=False))
            
            return(None)
    
    
    # MAIN INVOKED BY LU_ExternalPython.py (USING SUBPROCESS MODULE)
    # READ INPUTS FOR JSON PATHS, THEN READ JSON PATHS FOR POINT COORDINATES AND MATERIAL
    def Main():
        jsonObj = DE.JSONTools()
        LU_ResultsPath = ShiftFilePath(os.path.abspath(__file__), 0, r"JSON Exchange")
        LU_InputsPath = ShiftFilePath(os.path.abspath(__file__), 0, r"JSON Exchange\LU_InputArgs.json")        
        
        # overwrite previous estimate results
        jsonObj.WriteJSON(None, LU_ResultsPath, "LU_Results")
        
        # read json inputs - [pointCloudPaths, materialChoice, buildingMetadata]
        inputArgsList = jsonObj.Read_UJSON(LU_InputsPath)
        
        # read points from paths in inputArgsList and chosen material | [[jsonPath, material], []]
        ptCloudsJSON = [jsonObj.Read_UJSON(i[0]) for i in inputArgsList] #[:2] # testing at a small scale
        floatMaterials = [jsonObj.Read_UJSON(i[1])  for i in inputArgsList]
        #metadata = [jsonObj.Read_UJSON(i[2])  for i in inputArgsList]
        
        # convert python list to numpy array [n, n, n, n]
        ptCloudsJSON_array = np.array(ptCloudsJSON) # array creation is too deeply nested; why???
        
        # REALITY CAPTURE WILL HAVE TO PROVIDE SCANNER INFORMATION and BUILDING NAME IN JSON OUTPUT
        fakebuildingMetadata = "NA_SEA_411 Union P1_3"
        LU_Results = []
        for i, dataArray in enumerate(ptCloudsJSON_array):
            # BUILDING METADATA ALSO NEEDS TO HAVE SCANNER INFORMATION
            LUoutput = LU_Engine(self, ptCloudArray=dataArray, scanVendor="WeWork", scanner="ScannerA", buildingMetadata=metaData[i]).Run_LU_Engine() # --> writes LU_Results.json
        
        # write results to a Json file
        jsonObj.WriteJSON("".join(LU_Results), LU_ResultsPath, 'LU_Results')        
        
        
        #return(LUoutput)
    
    if __name__ == "__main__":
        Main()

except:
    print(traceback.format_exc())