"""

Pin/Unpin Elements in 
"Control Line" workset

Engine is used for the following tools:
	Pin CLs
	Unpin CLs
	Find CL Line Styles

"""

# imports for Revit API
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *

class PinningTools:
	
	def __init__(self, doc):
		self.doc = doc
	
	# COLLECT
	def CollectWorksets(self, userOnly=True):
		# collects user worksets in document
		
		if userOnly == True:
			worksetList = FilteredWorksetCollector(self.doc).OfKind(WorksetKind.UserWorkset)
		elif userOnly == False:
			worksetList = FilteredWorksetCollector(self.doc)
			
		return(worksetList)
	
	def CollectWorksetNames(self, userOnly=True):
		# filters names of collected user worksets in document
		
		worksetList = self.CollectWorksets(userOnly)
		if worksetList != None:
			worksetNames = [i.Name for i in worksetList]
			return(worksetNames)
		else:
			print("You must collect user worksets first!")
		return(None)
	
	def CollectLineStyles(self):
		# collect all line styles
		pass
	
	# FILTER
	def FilterWorksetsByName(self, worksetName):
		# obtain workset object by providing its name
		
		worksets = self.CollectWorksets()
		worksetNames = [i for i in self.CollectWorksetNames()]
		
		workset = [data for i, data in enumerate(worksets) if worksetNames[i] == worksetName][0] #why is this nested?
		return(workset)
	
	def FilterWWLineStyle_ControlLines(self):
		lineStyle = "WW-Solid-Laser-ControlLines"
	
	# ASSIGN
	def AssignNewWorkset(self, elements):
		pass
	
	# GET
	def GetElementsInWorkset(self, worksetName):
		# collects all elements belonging to a given workset
		
		elementCollector = FilteredElementCollector(self.doc)
		worksetFilter = ElementWorksetFilter(self.FilterWorksetsByName(worksetName).Id, False)
		foundElements = elementCollector.WherePasses(worksetFilter).ToElements()
		
#		print("There are {1} elements in the '{0}' workset".format(worksetName, foundElements.Count))
		return(foundElements)
	
	# PIN
	def PinUnpinElementsInWorkset(self, worksetName, unpin=False):
		# pin or unpin all elements in a given workset
		# don't know why some assignments fail

		for i in self.GetElementsInWorkset(worksetName):
			try:
				if unpin == False:
					i.Pinned = True
				elif unpin ==  True:
					i.Pinned = False
			except:
				print("Element ID: {0} cannot be pinned/unpinned".format(i.Id))
		return(None)