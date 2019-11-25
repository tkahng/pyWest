"""
Refactored version of the original
Storefront Tool. Serves as the basis for
Storefront 2.0 Tool. Will be gradually
subsumed by the new version.
"""
__author__ = 'WeWork Design Technology West'
__version__ = "4.0"

import traceback
import os
#from logger import log
#log(__file__) # __file__ cannot be tested in shell

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
    import sys
    sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
    import SF2_Engine

    def Main():
        SF2_Engine.GenerateSF().Run_GenerateSF()

    if __name__ == "__main__": 
        Main()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())