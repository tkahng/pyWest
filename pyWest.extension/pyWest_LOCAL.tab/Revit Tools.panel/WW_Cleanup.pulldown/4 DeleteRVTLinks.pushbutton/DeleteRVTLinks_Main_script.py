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
	
	sys.path.append(ShiftFilePath(os.path.abspath(__file__), 2, r"0 Lib"))
	import CleanupModel_Engine

	
	def Main():
		# set the active Revit application and document
		doc = __revit__.ActiveUIDocument.Document
		
		t = Transaction(doc, 'Deleting all RVT Links from the document')
		t.Start()
		
		# delete RVT links
		CleanupModel_Engine.RevitCleanupTools(doc).DeleteRVTLinks()
		
		t.Commit()
	
	if __name__ == "__main__":
		Main()
	

except:
	# print traceback in order to debug file
	print(traceback.format_exc())