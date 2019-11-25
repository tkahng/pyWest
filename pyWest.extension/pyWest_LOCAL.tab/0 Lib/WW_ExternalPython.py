import sys
sys.path.append(r"C:\Program Files (x86)\IronPython 2.7\Lib")
import subprocess

class ExternalPythonEngine:
    """
    python process options: ipy (ironpython), python (python2), and python3
    """
    def __init__(self,  scriptPath, pyVersion="python3", jsonArgs=None):
        # input parameters
        self.scriptPath = scriptPath
        self.pyVersion = pyVersion
        self.jsonArgs = jsonArgs
        
        # output
        self.engineObj = None
        self.engineObj_Out = None
        self.engineObj_Err = None    
        
    def Run_Subprocess(self, SPoutput=False, SPerrors=False):
        # arguments for subprocess must be in a list
        # added PIPE for stderr allowed me to see console output in engineObj
        subprocessArgs = [self.pyVersion, self.scriptPath] 
        self.engineObj = subprocess.Popen(subprocessArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        sp_Outputs = self.engineObj.communicate()
        
        # output check
        if SPoutput == True:
            self.engineObj_Out = sp_Outputs[0] # this format means varA = function[0], varB = Function[1]
            print("{0} output is: {1}".format(self.pyVersion, self.engineObj_Out))
        if SPerrors == True:
            self.engineObj_Err = sp_Outputs[1]  
            print("errors: {0}".format(self.engineObj_Err))


def TestMain():
    #pythonFilePath = r"{0}\engineObj.py".format(libPath)
    #ExternalPythonEngine(scriptPath=None, pyVersion=None, jsonArgs=None).Run_Subprocess(SPoutput=False, SPerrors=False)
    pass

if __name__ == "__main__":
    TestMain()