import traceback
import sys

sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\pyWestExtensions\pyWest.extension\pyWest_LOCAL.tab\Take Offs.panel\0 Lib")
import Takeoff_Engine
reload(Takeoff_Engine)

try:
    ITestObj = Takeoff_Engine.QTOTools()
    collectDesks = ITestObj.CollectUSF()
    print(ITestObj.DeskTools)

except:
    # print traceback in order to debug file
    print(traceback.format_exc())