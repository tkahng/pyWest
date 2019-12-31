"""
# trim point cloud
# isolate points on the section cut
# perform convex hull to get points on the perimeter
# use perimeter to get walls, and core
# get curves from this, somehow identify curves of core, stairs etc...
# get coordinates of interpolated curve
# export json
# read json in revit, redraw outline curve
# run usf
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
    
    class USF_Engine:
        """
        Because this was originally written to be ran from outside Revit, with inputs
        taken from the Revit user, the class reads its inputs from the 
        """
        
        def __init__(self, ptCloudArray):
            # input parameters
            self.ptCloudArray = ptCloudArray
            
            # create dataArray exchange object | standard read for getting input args | write for results of calc
            self.jsonObj = DE.JSONTools()
            self.WriteJSONresults = ShiftFilePath(os.path.abspath(__file__), 6, r"JSON Exchange")
            self.readJSONinputs = ShiftFilePath(os.path.abspath(__file__), 6, r"JSON Exchange\LU_InputArgs.json")
            
            self.ptCloudZ = None
            
            # output dataArray
    
        # SOMETHING
        @WW_Debug.Profiler
        def Method1(self):
            pass

        # RUN
        def Run_USF_Engine(self):
            pass
            return(None)
    
    
    # MAIN INVOKED BY LU_ExternalPython.py (USING SUBPROCESS MODULE)
    def Main():
        # overwrite previous estimate results
        DE.JSONTools().WriteJSON(None, self.WriteJSONresults, "USF_Results")
        
        # read json inputs - [buildingName, pointCloudPaths, materialChoice]
        self.inputArgsList = DE.JSONTools().Read_UJSON(self.readJSONinputs)
        
        # get point clouds points from Reality Capture and material | [[jsonPath, material], []]
        jsonPath = DE.JSONTools().Read_UJSON(jsonPath[0])
        ptCloudsJSON = [jsonPath for jsonPath in self.inputArgsList] #[:2] #testing at a small scale
        
        # convert python list to numpy array [n, n, n, n]
        ptCloudsJSON_array = np.array(ptCloudsJSON) # array creation is too deeply nested; why???
        
        # REALITY CAPTURE WILL HAVE TO PROVIDE SCANNER INFORMATION and BUILDING NAME IN JSON OUTPUT
        USF_Results = []
        for i, dataArray in enumerate(ptCloudsJSON_array):
            LUoutput = LU_Engine(self, ptCloudArray=None).Run_USF_Engine()
        
        # write results to a Json file
        self.jsonObj.WriteJSON("".join(LU_Results), self.WriteJSONresults, 'USF_Results')        
        
        
        #return(LUoutput)
    
    if __name__ == "__main__":
        Main()

except:
    print(traceback.format_exc())