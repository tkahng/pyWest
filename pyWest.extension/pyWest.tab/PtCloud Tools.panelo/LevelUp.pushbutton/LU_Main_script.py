"""
pyVersion = IronPython 2.7xx

This Tool is intended to provide an estimate of the volume required to fill
the top surface of a floor plate in order to make it level. That volume in 
turn will be used to estimate the amount of leveling compound that needs to be
purchased by the GC.
"""
import traceback
import os
import sys

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    sys.path.append(r"C:\Program Files (x86)\IronPython 2.7\Lib")
    import subprocess as sp
    
    # imports for Windows Form
    import clr
    clr.AddReference("System.Drawing")
    clr.AddReference("System.Windows.Forms")
    import System.Drawing
    import System.Windows.Forms
    from System.Drawing import *
    from System.Windows.Forms import *

    dataExchangePath = ShiftFilePath(os.path.abspath(__file__), 3, r"0 Lib")
    sys.path.append(dataExchangePath)
    import WW_DataExchange as DE
    import WW_ExternalPython as WW_EP
    
    libPath = ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib")
    sys.path.append(libPath)
    import LU_GUI
    import LU_GUI_Results as LU_R
    
    checkPy = sys.version
    if int(checkPy[0]) == 3:    
        from importlib import reload # this process is new to Python 3
        reload(LU_GUI)
        reload(LU_R)
        reload(WW_EP)
    else:
        reload(LU_GUI)
        reload(LU_R)
        reload(WW_EP)

    def Main(printOut=False, export=False):
        # GUI
        firstForm = LU_GUI.LU_Form()
        Application.Run(firstForm)
        
        if not firstForm:
            sys.exit()

        # collect json pc and material choice
        ptCloudPathList = firstForm.jsonPathList
        materialChoice = firstForm.selectedMaterial
        
        # collect project metadata from json file name
        # CAN I JUST ADD META DATA TO FILE AND ALLOW INPUT TO JUST USE FOR CALCULATION

        # save json - external engine uses this file
        filePath = r"{0}\JSON Exchange".format(libPath)
        inputArgsList = [[path, materialChoice] for i,path in enumerate(ptCloudPathList)]
        dataObj = DE.JSONTools()
        dataObj.WriteJSON(inputArgsList, filePath, "LU_InputArgs")
        
        # run external python engine - this script gets suspended while it waits for the results of the external script
        LU_EnginePath = ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib\LU_Engine.py")
        WW_EP.ExternalPythonEngine(scriptPath=LU_EnginePath, pyVersion="python3").Run_Subprocess(SPoutput=True, SPerrors=True)

        # read results from json file - written by external python engine
        output = dataObj.ReadJSON(r"{0}\JSON Exchange\LU_Results.json".format(libPath))

        # GUI - display results from External Python Engine
        secondForm = LU_R.LU_Form_Results(output)
        Application.Run(secondForm)       

        return(output)


    if __name__ == "__main__":
        Main()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())