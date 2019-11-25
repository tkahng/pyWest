import sys
sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')

import subprocess as sp
import os
import traceback

class FilePathTools:
	def __init__(self):
		self.targetDirectory = None
	
	def pySafePath(self, filePath):
		return(filePath.replace("\\", "/")) # python gets confused by "\" character, replace with "/")
	
	def CurrentFilePath(self):
		return(self.pySafePath(os.path.abspath(__file__)))
	
	def CurrentFileDirectory(self):
		return(self.pySafePath(os.path.dirname(self.CurrentFilePath())))
	
	def CurrentUserDesktopPath(self):
		return(self.pySafePath(os.path.expanduser("~/Desktop")))
		
	def ConsistentFilePaths(self, branchesBack=0):
		# you cannot move branches forward, but will keep for some reason
		if branchesBack == 0:
			self.targetDirectory = self.CurrentFileDirectory()
		
		elif branchesBack != 0:
			os.chdir(self.CurrentFileDirectory())
			for i in range(branchesBack):
				os.chdir('..')
			self.targetDirectory = self.CurrentFileDirectory()
		
		return(self.pySafePath(self.targetDirectory))
		
if __name__ == "__main__":
	# TEST #
	dirObj = FilePathTools()
	a = dirObj.ConsistentFilePaths()
	b = dirObj.ConsistentFilePaths(5)
	
	print(a)
	print(b)