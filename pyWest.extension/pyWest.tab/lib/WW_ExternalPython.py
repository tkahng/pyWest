"""
pyVersion = IronPython 2.7xx and Python 3.7xx

This will automatically create an exchange between
programs using JSON files which will contain data
and input parameters for the external program

assume Popen is a shell input: python3 script.py --> whatever input scipt asks for as variable for external app
think of this as a shell macro
"""
import sys
sys.path.append(r"C:\Program Files (x86)\IronPython 2.7\Lib")

# module for running external python processes
import subprocess
import os

# ironPython modules
if "2." and "IronPython" in sys.version:
    from _winreg import HKEY_CURRENT_USER, OpenKey, QueryValue
    
# python 2 or 3 modules
elif "3." or "2." and not "IronPython" in sys.version:
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValue

class ExternalPythonEngine:
    """
    Arguments passed to external script use sys.argv to obtain in the scipt; begins at sys.argv[1]
    
    python process options: 
        ipy (ironpython), python (python2), and python3 | these are based on shell input variables
        
    basic idea:
        #################     ####################      #####################################
        ## pyRevit app ## --> ## write JSON out ## <--> ## run external Python / read JSON ## --|
        #################     ####################      #####################################
        
             ########################      #############################################
        |--> ## write new JSON out ## <--> ## resume original pyRevit app / read JSON ##
             ########################      #############################################
    
    THIS WORKS LIKE A COMMAND LINE PROMPT, SO THAT IS WHY THE PYTHON VERSION IS SAID FIRST
    WOULDN'T BE NEEDED IF THE PROGRAM/APP IS COMPILED...WHICH ISN'T IN PYTHON.
    """
    def __init__(self,  externalScriptPath=None, pyVersion="python3", jsonArgs=None):
        # input parameters
        self.externalScriptPath = externalScriptPath
        self.pyVersion = pyVersion
        self.jsonArgs = jsonArgs
        
        # derived parameters
        # arguments for subprocess mimic shell: PS C:\ python3 script.py --> access args using sys.argv[i] in target file
        if self.jsonArgs: self.subprocessArgs = [self.pyVersion, self.externalScriptPath, self.jsonArgs]
        else: self.subprocessArgs = [self.pyVersion, self.externalScriptPath]
        
        # was Popen successfully ran?
        self.externalSuccess = None
        
        # external file name
        if self.externalScriptPath:
            self.externalPyScript_Name = self.externalScriptPath.split("\\")[-1]
        
        # output variables
        self.externalPyScript = None
        self.externalPy_In = None
        self.externalPy_Out = None
        self.externalPy_Err = None
    def Run_Subprocess(self, spPrintIn=False, spPrintOutput=False, spPrintErrors=False, useShell=False):
        if not self.externalScriptPath:
            raise Exception("This method requires the path to a scipt")
        
        # POPEN run external script - simple case - returns object
        self.externalPyScript = subprocess.Popen(self.subprocessArgs,
                                                 stdout = subprocess.PIPE, 
                                                 stderr = subprocess.PIPE,
                                                 shell = useShell)           
        
        # communication object returns a list: [output, errors]
        self.externalPy_Out, self.externalPy_Err = self.externalPyScript.communicate()
        
        # output check
        if spPrintOutput == True:
            print("{0} output: {1}".format(self.externalPyScript_Name, self.externalPy_Out))
        if spPrintErrors == True:
            print("{0} errors: {1}".format(self.externalPyScript_Name, self.externalPy_Err))
        
        # 0 means it was a sucess
        self.externalSuccess = self.externalPyScript.poll()
        return(self.externalPyScript.poll())
    def OpenWindowsProgram(self):
        # test open notepad
        #os.system("notepad") # this opens because it is accessible in the terminal
        os.system("Chrome")
    def OpenWebBrowser(self, url):
        # obtain computer's default browser
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\http\shell\open\command") as key:
            defaultBrowser = winreg.QueryValue(key, None)        
            chromePath = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        subprocess.Popen([defaultBrowser, url]) #.wait()
                
def TestMain():
    pythonFilePath = r"C:\Users\aluna\Documents\WeCode\GitRepos\pyWestRepo\pyWest2\pyWest.extension\pyWest2.tab\Take Offs.panel\0 Lib\Takeoff_Engine_Py3ext.py"
    #pythonFilePath = r"Takeoff_Engine_Py3ext.py"
    a = ExternalPythonEngine(externalScriptPath = pythonFilePath,
                                      pyVersion = "python3").Run_Subprocess(spPrintOutput=True, spPrintErrors=True, spPrintIn=True)
    
    #b = ExternalPythonEngine(externalScriptPath = pythonFilePath,
                                      #pyVersion = "python3").OpenWindowsProgram()
    
    #c = ExternalPythonEngine(externalScriptPath = pythonFilePath,
                                      #pyVersion = "python3").OpenWebBrowser("https://www.nytimes.com/", sp=True)
    print(a)
    #print(b)
    #print(c)
    

if __name__ == "__main__":
    TestMain()