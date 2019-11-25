import sys
import os

class WinDirTools:
    """
    This library can be used to create, rename, and delete
    folders in a windows environment. You can do this to 
    the standard folders or GStream if it is installed.
    """
    def __init__(self, saveLocation="ifc"):
        if saveLocation == "ifc":
            self.ifcMainDir = r"G:\Shared drives\Prod - BIM\07_Global Initiatives\Archilogic IFC Export"
    def CreateDir(self, dirPath):
        if type(dirPath) is list:
            if not os.path.exists(i):
                for i in dirPath:
                    os.mkdir(i)
        else:
            if not os.path.exists(dirPath):
                os.mkdir(dirPath)
    def RenameDir(self, oldDirPath, newDirPath):
        if os.path.exists(oldDirPath):
            os.rename(oldDirPath, newDirPath)
            print("'{0}' is renamed to '{1}'".format(oldDirPath, newDirPath))
    def DelDir(self, dirPath):
        if os.path.exists(dirPath):
            os.rmdir(dirPath)
    def TraverseDirRecursively(self, dirPath):
        # NOT QUITE SURE WHAT THIS IS FOR...
        rootdir = "c:\\temp"
        for root, dirs, files in os.walk(rootdir):
            print("{0} has {1} files".format(root, len(files)))
            
def CreateFakeFile():
    with open(filename, "w") as f:
        f.write("FOOBAR") 

def TestMain():
    """
    how do i want this tool to work? I want to be able to have
    a user run the tool, then have it automatically create a 
    continent folder (if it doesn't already exist), a city folder [...],
    a building folder [...] and place the exports within there. 
    """
    
    
    # folders to create
    testFolderNames = ["Folder {0}".format(i) for i in range(11)]
    
    gStreamObj = WinDirTools(saveLocation="ifc")
    gStreamObj.CreateDir(fullDirNames)

if __name__ == "__main__":
    TestMain()

