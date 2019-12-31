import numpy as np
import sys

sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\0_PANGOLIN\0_PanelingToolsScripts\Python")
import ASGG_DataExchange as DA

def Main(*arg):
    newArray = np.array
    print(sys.version)
    print(arg)
    #for i in arg:
        #print(i)
    
    fakeOutput = [1,1,1,1]
    
    """
    THIS WILL RETURN WHATEVER, BUT ALSO CREATE
    A JSON FILE THAT WILL BE USED BY THE PROGRAM
    CALLING THIS LIBRARY TO OBTAIN THE SAME OUTPUT
    """
    dataObj = DA.JSONTools(r'C:\Users\aluna\Documents\WeWork Code\Float Volume Calculation Tool\Lib\JSON Exchange')
    print(dataObj)
    dataObj.WriteJSON('FVCT_output', fakeOutput)
    
    return(fakeOutput)

if __name__ == "__main__":
    args = sys.argv 
    #print(args)
    #sys.exit(Main(args))
    Main(args)
  