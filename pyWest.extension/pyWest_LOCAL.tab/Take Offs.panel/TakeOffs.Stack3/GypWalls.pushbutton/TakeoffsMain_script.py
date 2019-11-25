"""
The whole stack firing Main() is placed in a try_except pattern
in order to reveal the file and line number of any error that causes
the program to fail

REMEMBER THAT INSTANTIATED OBJECTS CAN BE CONTINOUSLY
MODIFIED BY THEIR METHODS
"""
import traceback
import os
import sys
sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')

def ShiftFilePath(path, branchesBack=1, append=None):
	pathReverse = path[::-1]
	newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
	newPath = newPathBackwards[::-1]

	if type(append) is str: return(r"{0}\{1}".format(newPath, append))
try:
	import math
	
	# imports for Windows Form
	import clr
	clr.AddReference("System.Drawing")
	clr.AddReference("System.Windows.Forms")
	
	import System.Drawing
	import System.Windows.Forms
	
	from System.Drawing import *
	from System.Windows.Forms import *
	
	# imports for Revit API
	clr.AddReference('RevitAPI')
	clr.AddReference('RevitAPIUI')
	from Autodesk.Revit.DB import *
	
	
	class GypWallEstimate():
		def __init__(self):
			self.gypWallNames = ["Partition-Gyp", "B2.1", "Chase-Pantry", "B15"]
			
			self.totalArea = None
			self.numSheets = None
			self.totalCost = None
			
			# if self.RunEstimate() is constructor, then this must be filled with properties to continue development
			
		def CollectGypWalls(self):
			# create collection object
			collectorObj = FilteredElementCollector(doc)
			selectedWalls = collectorObj.OfClass(Wall) #Autodesk.Revit.DB.Wall - defines <type 'Wall'>
			gypWalls = [wall for wall in selectedWalls if wall.Name in self.gypWallNames]
			
			return(gypWalls)
			
		def GetGypWallAreas(self):
			areaList = []
			for wall in self.CollectGypWalls():
				# outside method parses to object class' geometric properties - unlike rhino which is part of the class
				sideFaceList = HostObjectUtils.GetSideFaces(wall, ShellLayerType.Exterior)
				
				# loop into reference list for each wall to get face srf
				for face in sideFaceList:
					netFace = wall.GetGeometryObjectFromReference(face)
        			areaList.append(netFace.Area)
			self.totalArea = sum(areaList)
			return(self.totalArea)
		
		def CalculateGypWallYield(self):
			self.numSheets = round((self.GetGypWallAreas() / 32.00), 0) + 1
			return(self.numSheets)
		
		def GetGypWallCost(self, sheetPrice):
			self.totalCost = self.CalculateGypWallYield() * sheetPrice
			return(self.totalCost)
			
			
	def Main():
		# set the active Revit application and document
		app = __revit__.Application #use this to open another model?
		version = app.VersionNumber.ToString()
		uidoc = __revit__.ActiveUIDocument
		doc = __revit__.ActiveUIDocument.Document
		currentView = uidoc.ActiveView
		
		print(doc)
		
		# Gyp Wall Estimate
		gypWallObj = GypWallEstimate() #always create an object separately unless you need specific output from internal method
		gypWallObj.GetGypWallCost(sheetPrice=34.50)
		print("total area: {0}sf".format(gypWallObj.totalArea))
		print("total number of sheets: {0}".format(gypWallObj.numSheets))
		print("cost estimate: ${0}".format(gypWallObj.totalCost))
		
		# Some Other Estimate
		
	
	if __name__ == "__main__":
		Main()
	

except:
	# print traceback in order to debug file
    print(traceback.format_exc())