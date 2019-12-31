"""
pyVersion = IronPython 2.7xx and Python 3.7xx

These classes are compatible with both Rhino and Revit
and are meant to assist in exchanging data between
these platforms, or between any program and the OS.

Each data tool is an object with accessible
methods therein which can be linked together. There is
no main function and nothing will run without being
explicitly instantiated

Because this is meant to be used in both Python3 and
ironPython precautions must be taken in the code!
"""
# UNIVERSAL MODULES
import traceback
import sys

try:
    sys.path.append(r"C:\Program Files (x86)\IronPython 2.7\Lib")
except:
    sys.path.append(r"C:\Program Files\IronPython 2.7\Lib")
import json    

#import collections
#from collections import Sequence
from itertools import chain, count

import csv
import os

# .NET MODULES
if "2." and "IronPython" in sys.version:
    import clr
    
    #clr.AddReference('msgpack.dll')
    #import msgpack
    
    # imports for Revit API
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    from Autodesk.Revit.DB import *
    from Autodesk.Revit.UI import *    

# PYTHON 3 MODULES
elif "3." in sys.version:
    sys.path.append(r"C:\Users\aluna\AppData\Local\Programs\Python\Python37\Lib")
    import ujson
    import msgpack

class FilePathTools:
    def __init__(self):
        self.targetDirectory = None

    def CurrentFilePath(self):
        return(os.path.abspath(__file__))

    def CurrentFileDirectory(self):
        return(os.path.dirname(self.CurrentFilePath()))

    def CurrentUserDesktopPath(self):
        return(os.path.expanduser("~\Desktop"))
    
    def CurrentUser(self):
        return(os.path.expanduser("~"))

    def ShiftFilePath(self, path, branchesBack=1, append=None):
        pathReverse = path[::-1]
        newPathReverse = pathReverse.split('\\', branchesBack)[-1]
        newPath = newPathReverse[::-1]
        
        # always write append string as r"" - set as variable
        if type(append) is str: return(r"{0}\{1}".format(newPath, append))

# data prep for JSON AND CSV modules
class DataPrep:
    def __init__(self):
        pass

    def GroupNthItemList(self, data, groupSize):
        dataOut = []
        for building in data:
            count = 0
            for facadeIndex in range(len(building)):
                anotherNest = []
                facadesTempList = []

                # group facades in sub lists by looping through groupSize
                for groupIndex in range(groupSize):
                    masterIndex = (facadeIndex + groupIndex + count)
                    if masterIndex <= (len(building) - 1):
                        facadesTempList.append(building[masterIndex])
                if len(facadesTempList) > 0:
                    count += (groupSize - 1)

                    # still dont understand why this i needed...group the groups?
                    anotherNest.append(facadesTempList)
                    dataOut.append(anotherNest)
        return(dataOut)

class JSONTools:
    """
    This class works for both Python2,3 and IronPython

    fileName and filePath are separated to simply the assignment
    of creating files in specific, but common locations by allowing
    keywords that the code recognizes to create a long path string.
    This to prevent the manual copying and pasting process.
    """
    def __init__(self):
        # instantiate FilePathTools Class
        self.pathObj = FilePathTools()
    
    def WriteJSON(self, data, filePath=None, fileName=None):
        # file path operations or something
        if not fileName: fileName = "randoJSON"        
        if filePath == None: filePath = self.pathObj.CurrentUserDesktopPath()
        elif filePath == 'current': filePath = self.pathObj.CurrentFileDirectory()
        elif filePath == 'Lib': self.filePath = None
        completeFilePath = r"{0}\{1}.json".format(filePath, fileName)
        
        # write json
        with open(completeFilePath, 'w') as writePath:
            JSONdump = json.dump(data, writePath)
        
        return(JSONdump)
    
    def Write_MSGPACK(self, data, filePath=None, fileName=None):
        if fileName == None: fileName = "randoMSGPACK"
        
        if filePath == None: filePath = self.pathObj.CurrentUserDesktopPath()
        elif filePath == 'current': filePath = self.pathObj.CurrentFileDirectory()
        elif filePath == 'Lib': self.filePath = None
        
        completeFilePath = r"{0}\{1}.msgpack".format(filePath, fileName)
        
        # Write msgpack file
        with open(completeFilePath, 'w') as writePath:
            msgpack.pack(data, writePath)        

    def ReadJSON(self, filePath=None):
        if filePath == None: raise Exception("Complete path must be used!")

        with open(filePath, 'r') as read:
            dataOut = json.load(read)
        return(dataOut)
    
    def Read_UJSON(self, filePath=None):
        if filePath ==  None: raise Exception("Complete path must be used!")
        
        with open(filePath, 'r') as read:
            dataOut = ujson.load(read)
        return(dataOut)
    
    def Read_MSGPACK(self, filePath=None):
        if filePath == None: raise Exception("Complete path must be used!")
        
        with open(filePath, 'r') as read:
            dataOut = msgpack.unpack(read)
        return(dataOut)
        
           
class CSVTools:
    """
    data assumes data is single column, if more than one column then you can make iterable
    """
    def __init__(self, fileName=None, filePath=None):
        # instantiate FilePathTools Class
        self.pathObj = FilePathTools()        

        self.fileName = fileName
        self.filePath = filePath

        # default file write locations and keyword options
        if self.fileName == None: self.fileName = "randoCSV"

        if self.filePath == None: self.filePath = FilePathTools().CurrentUserDesktopPath()
        elif self.filePath == 'current': self.filePath == FilePathTools().CurrentFileDirectory()
        elif self.filePath == 'Lib': self.filePath = None        

    def ReadCSV(self, row=True, cellStart=None, cellEnd=None):
        # cellStart = (row#, column#)

        # assume fileName contiains full path, unless files are saved in same location
        with open(self.fileName, mode='r') as csvFile:
            # read rows
            if row == True:
                csvReader = csv.reader(csvFile, delimiter=',')
                csvData = [i for i in csvReader]

            # read columns
            elif row == False:
                csvReader = csv.reader(csvFile, delimiter=',')
                csvData = [i for i in zip(*csvReader)]

        return(csvData)

    def WriteCSV(self, data, row=True, cellStart=None, cellEnd=None):
        # cellStart = (row#, column#)

        completeFilePath = "{0}/{1}.csv".format(self.filePath, self.fileName)

        with open(completeFilePath, mode='w') as csvFile:
            writerObj = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # write row
            if row == True:
                for i in data:
                    writerObj.writerow(i)

            # write column
            elif row == False:
                data2 =  zip(data)
                for i in data2:
                    writerObj.writerow([i])
        return(None)

    def WriteCSV2(self, data, cellStart=None, cellEnd=None):
        # cellStart = (row#, column#)
        print('hello world')
        inPath = "{0}/{1}.csv".format(self.filePath, 'in')
        outPath = "{0}/{1}.csv".format(self.filePath, 'out')

        in_file = open(inPath, mode='r')
        reader = csv.reader(in_file)

        myList = list(reader)
        in_file.close()

        print(myList)

        #myList[2][0] = 'cat'
        #myNewList = open(outPath, mode='w', newline='')
        #writer = csv.writer(myNewList)
        #writer.writerows(myList)
        #myNewList.close()           

class SQLTools:
    """
    This class only works in Python 2 & 3. Not implimented for ironPython.
    Please call subprocess to use within Rhino or Revit. 
    """
    def __init__(self):
        import sqlite3
        pass

    def WriteDB(self):
        pass

    def UpdateDB(self):
        pass    

    def ReadDB(self):
        pass


class GRASSHOPPERTools:
    def __init__(self):
        pass

    def DEPRECATED(self, raggedList):
        # Grasshopper imports
        import clr
        clr.AddReference("Grasshopper")
        from Grasshopper import DataTree
        from Grasshopper.Kernel.Data import GH_Path

        from System import Array
        from System import Object


        rl = raggedList
        result = DataTree[object]()
        for i in range(len(rl)):
            temp = []
            for j in range(len(rl[i])):
                temp.append(rl[i][j])
            #print i, " - ",temp
            path = GH_Path(i)
            result.AddRange(temp, path)
        return(result)

    def NestedListToDataTree(self, input, none_and_holes=True, source=[0]):
        # Grasshopper imports
        import clr
        clr.AddReference("Grasshopper")
        from Grasshopper import DataTree
        from Grasshopper.Kernel.Data import GH_Path

        from System import Array
        from System import Object

        def proc(input,tree,track):
            path = GH_Path(Array[int](track))
            if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
            for i,item in enumerate(input):
                if hasattr(item, '__iter__'): # if list or tuple
                    track.append(i); proc(item,tree,track); track.pop()
                else:
                    if none_and_holes: tree.Insert(item,path,i)
                    elif item is not None: tree.Add(item,path)
        if input is not None: t=DataTree[object]();proc(input,t,source[:]);return t

    def DataTreeToNestedList(self, aTree):
        # Grasshopper imports
        import clr
        clr.AddReference("Grasshopper")
        from Grasshopper import DataTree
        from Grasshopper.Kernel.Data import GH_Path

        from System import Array
        from System import Object


        theList = []
        for i in range(aTree.BranchCount ):
            thisListPart = []
            thisBranch = aTree.Branch(i)
            for j in range(len(thisBranch)):
                thisListPart.append( thisBranch[j] )
            theList.append(thisListPart)
        return(theList)

class ListTools:
    def __init__(self):
        pass

        #def ListDepth(self, dataList):
        #dataList = iter(dataList)
        #try:
        #for level in count():
            #dataList = chain([next(dataList)], dataList)
            #dataList = chain.from_iterable(s for s in dataList if isinstance(s, Sequence))

        ## do not recognize the formatting after except
        #except StopIteration:
        #return(level)
        ## yield from is not ironpython safe???
        #def MissingNumbersInSequence(numList, start, end):
        ## very advanced formatting, is this recursion?
        #if end - start <= 1: 
        #if numList[end] - numList[start] > 1:
            #yield from range(numList[start] + 1, numList[end])
        #return

        #index = start + (end - start) // 2

        ## is the lower half consecutive?
        #consecutive_low =  numList[index] == numList[start] + (index - start)
        #if not consecutive_low:
        #yield from MissingNumbersInSequence(numList, start, index)

        ## is the upper part consecutive?
        #consecutive_high =  numList[index] == numList[end] - (end - index)
        #if not consecutive_high:
        #yield from MissingNumbersInSequence(numList, index, end)

        return(False)

class RangeDict(dict):
    def __getitem__(self, item):
        if type(item) != range: # or xrange in Python 2
            for key in self:
                if item in key:
                    return(self[key])
        else:
            return(super().__getitem__(item))

def frange(start, stop=None, step=None):
    # use float number in range() function
    
    # if stop and step argument is null set start=0.0 and step=1.0
    if stop == None:
        stop = start + 0.0
        start = 0.0
    
    if step == None:
        step = 1.0
        
    while True:
        if step > 0 and start >= stop:
            break
        elif step < 0 and start <= stop:
            break
        yield("{0}".format(start))
        start = start + step

def frange2(x, y, jump):
    while x < y:
        yield x
        x += jump    

def TestMain():
    ### csv write
    ###data = ['cat', 'dog', 'rabbit', 'dolphin', 7]
    ###csvWriteData = CSVTools().WriteCSV(data, False)
    ###print(csvWriteData)

    ###csvWriteData2 = CSVTools().WriteCSV2(data)
    ###print(csvWriteData2)    

    ###csvFilePath = r"C:\Users\aluna\Downloads\Memorial Weekend - Sheet1.csv"
    ###csvReadData = CSVTools(csvFilePath).ReadCSV(False)
    ###print(csvReadData)
    
    #aDict = {frange2(1.0,3.0,.1): "dog",
             #frange2(3.0,float(sys.maxsize), .1) : "CAT"
            #}
    
    #rangObj = RangeDict(aDict)
    #print(rangObj[2.999])
    
    print(FilePathTools().CurrentUser())
    
    pass
    

if __name__ == "__main__":
    TestMain()