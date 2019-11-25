"""

This Tool is intended to provide an e	stimate of the volume required to fill
the top surface of a floor plate in order to make it level. That volume in 
turn will be used to estimate the amount of leveling compound that needs to be
purchased by the GC.

"""

import sys
sys.path.append(r"C:\Program Files (x86)\IronPython 2.7\Lib")
import subprocess as sp
import os
import traceback

try:
	# imports for Windows Form
	import clr
	clr.AddReference("System.Drawing")
	clr.AddReference("System.Windows.Forms")
	
	import System.Drawing
	import System.Windows.Forms
	
	from System.Drawing import *
	from System.Windows.Forms import *
	
	sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\0_PANGOLIN\0_PanelingToolsScripts\Python")
	import ASGG_DataExchange as DA
	
	filePath = "C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\PtCloudTools.panel\Lib"
	sys.path.append(r"{0}".format(filePath))
	import FVCT_GUI
	import FVCT_GUI_Results as FVCT_R
			
	def Main():
		firstForm = FVCT_GUI.FVCT_Form()
		Application.Run(firstForm)
		
		# get point clouds points from Reality Capture
		ptCloudPathList = firstForm.jsonPathList
		materialChoice = "LevelQuick RS" # only one at a time
		
		# create json here have the script automatically read file in certain location
		inputArgsList = [[path, materialChoice] for i,path in enumerate(ptCloudPathList)]
		dataObj = DA.JSONTools()
		dataObj.WriteJSON(filePath, "FVCTInputArgs", inputArgsList)
		
		# figure out how to close program early at 'event cancel'
		
		# python process options: ipy (ironpython), python (python2), and python3 - numpy works on python2&3
		scriptFilePath = "{0}\FVCT_Python3Engine.py".format(filePath)
		args = ["python3", "{0}".format(scriptFilePath)]
		externalProgram = sp.Popen(args, stdout=sp.PIPE)
		out, err = externalProgram.communicate() # this format means varA = function[0], varB = Function[1]
		
		# get return from external program
		output = dataObj.ReadJSON(r"C:\Users\aluna\Documents\WeWork Code\Float Volume Calculation Tool\Lib\JSON Exchange\FVCT_Results.json")
		print(output)
		
		# display new dialog box
		Application.Run(FVCT_R.FVCT_Form_Results(str(output)))
			
		return(output)
	
	if __name__ == "__main__":
		Main()

except:
	# print traceback in order to debug file
    print(traceback.format_exc())