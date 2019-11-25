"""
:tooltip:
Module for storefront logic
TESTED REVIT API: 2015, 2016, 2017
:tooltip:

Copyright (c) 2016-2018 WeWork

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

__author__ = 'WeWork Buildings Systems'
__version__ = "1.0"

import clr
import sys, traceback
import os
import sys
import logging
import System
import math
import _csv as csv
import json
import rpw


clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
import Autodesk.Revit.UI.Selection

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
from System.Windows.Forms import SaveFileDialog
from System.Drawing import *
from System.Drawing import Point
from System.Windows.Forms import Application, Button, CheckBox, Form, Label
from System.Collections.Generic import List, IEnumerable
from System import Array
from System import DateTime as dt

from pyrevit import script

doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application
version = __revit__.Application.VersionNumber.ToString()
uidoc = __revit__.ActiveUIDocument
currentView = uidoc.ActiveView

user = str(System.Environment.UserName)


sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from storefront_utils import *
from storefront_class_cw import *
from storefront_system_configs import *

def storefront_fixer():
	"""
	For fixing particular issues related to 
	storefront modeling for fabrication
	"""

	
	print "CREATING REPORT...PLEASE WAIT..."
	PrintBreakLine()
	currentView = uidoc.ActiveView
	#levelName = currentView.GenLevel.Name
	#levelElevation = currentView.GenLevel.Elevation

	oneByWidth = 1.75/12
	tol = 0.001

	storefrontConfig = storefront_options()
	
	systemName = None


	mullionDict = GetMullionTypeDict()
	panelTypeDict = GetWindowTypeDict()
	doorDict = storefrontConfig.doorDict


	from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
	# Select the report type
	components = [Label('Specify System'),
					ComboBox("combobox1", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
					Separator(),
					Button('Go')]

	form = FlexForm("Storefront Report", components)
	form.show()

	if not form.values:
		sys.exit()
	else:
		systemName = form.values["combobox1"]


		if not systemName.lower() in storefrontConfig.currentConfig["currentSystem"].lower():
			storefrontConfig.storefront_set_config()
			systemName = storefrontConfig.currentConfig["currentSystem"]
			storefrontConfig.storefront_save_config()


	allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
											view=currentView, 
											where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))

	allStorefrontPanels  = []
	allStorefrontMullions = []

	for sfwall in allStorefrontWalls:

		for sfMullionsId in sfwall.CurtainGrid.GetMullionIds():
			allStorefrontMullions.append(doc.GetElement(sfMullionsId))

		for panelId in sfwall.CurtainGrid.GetPanelIds():
			allStorefrontPanels.append(doc.GetElement(panelId))


	with rpw.db.Transaction("Storfront Fixer"):

		for sfmullion in allStorefrontMullions:

			mullionLength = sfmullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()

			if mullionLength > 0 and sfmullion.LocationCurve:

				mullionName = sfmullion.Name.lower()
				mullionRoom = sfmullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
				mullionPoint = sfmullion.Location.Point
				mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)

				mullionCurve = sfmullion.LocationCurve
				mullionCenter = mullionCurve.Evaluate(0.5, True)

				if "post" in mullionName or "wallstart" in mullionName:
					
					#Intermediate posts"
					#if not storefrontConfig.currentConfig["mullionContinuousVerticalIntermediateTop"]:
					sfmullion.JoinMullion()
					doc.Regenerate()
					mullionLengthAfter = sfmullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
					if mullionLengthAfter > mullionLength:
						output = script.get_output()
						clickable_link = output.linkify(sfmullion.Id)
						print "fixed: " + mullionName + " // " + str(mullionLength) + " to " + str(mullionLengthAfter) + " // -->" + clickable_link

					# print out  all errors
			
				if "door" in mullionName:
					sfmullion.JoinMullion()

				if "intermediate" in mullionName:
					sfmullion.BreakMullion()


		for sfwall in allStorefrontWalls:

			sfGrid = sfwall.CurtainGrid

			for panelId in sfGrid.GetPanelIds():

				panel = doc.GetElement(panelId)


				panelWidth = panel.get_Parameter(BuiltInParameter.WINDOW_WIDTH).AsDouble()
				panelHeight = panel.get_Parameter(BuiltInParameter.WINDOW_HEIGHT).AsDouble()

				if (panelWidth > 0) and (panelHeight > 0):

					condition = None
					varient01 = None
					varient02 = None

					panelType = panel.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
					panelSizeName = str(panelWidth) + " x " + str(panelHeight)

					#Get panel point and flatten
					panelPoint = panel.GetTransform().Origin
					panelPoint = XYZ(panelPoint.X, panelPoint.Y, 0)

					#Join or break the head mullions based on the system config
					if "empty" in panelType.lower():
						doorHeads = GetHorizontalMullionsAtPoint(sfGrid, panelPoint, nameFilter= "head")

						if storefrontConfig.currentConfig["mullionContinuousHorizontalHeadAtDoor"]:
							if doorHeads:
								for mull in doorHeads:
									mull.JoinMullion()
									print "fixed: " + mull.Name
						else:
							if doorHeads:
								for mull in doorHeads:
									mull.BreakMullion()
									print "fixed: " + mull.Name




def storefront_preflight():
	
	ecModelInst = None
	docEC = None
	wallErrorList = {}
	doorErrorList = {}
	toSelect = []
	toSelectEC = []
	selection = uidoc.Selection
	storefrontConfig = storefront_options()
	
	try:
		linkedInstances = GetRevitLinkInstances()
		if linkedInstances:
			for modelInst in linkedInstances:
				if ("_ec" in modelInst.Name.lower()
						or "ec." in  modelInst.Name.lower()
						or "existingconditions" in  modelInst.Name.lower()
						or "existing" in  modelInst.Name.lower()):
					ecModelInst = modelInst
					docEC = ecModelInst.GetLinkDocument()
			if not docEC:
				wallErrorList["EC ERROR"] = "EC model is not linked, please check."
			else:
				print "EC MODEL FOUND"
		else:
			wallErrorList["EC ERROR"] = "No linked models found"
	except Exception as inst:           
		print "...ERROR LOADING EC ELEMENTS"
		OutputException(inst)
		
	PrintBreakLine()
	
	
	# Check EC Document
	try:
		if docEC:
			allLevelsEC = GetAllElements(docEC, BuiltInCategory.OST_Levels, Autodesk.Revit.DB.Level)
			
			# check walls
			allWallsEC  = GetAllElements(docEC, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
			wallCheckEC = CheckElementConstraints(docEC,allWallsEC)
			if wallCheckEC:
				wallErrorList["EC WALL ERRORS"] = wallCheckEC
				print str(len(wallCheckEC)) + " - Wall Issues in EC"
				
			# check columns
			allColumnsEC = GetAllElements(docEC, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
			allColumnsEC += GetAllElements(docEC, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)
			columnCheckEC = CheckElementConstraints(docEC,allColumnsEC)
			if columnCheckEC:
				wallErrorList["EC COLUMN ERRORS"] = columnCheckEC
				print str(len(columnCheckEC)) + " - Column Issues in EC"
				#walls that span or are unconnected
				
	except Exception as inst:
		OutputException(inst)
		
	# Check Active Document
	try:
		allLevels = GetAllElements(doc, BuiltInCategory.OST_Levels, Autodesk.Revit.DB.Level)
		
		# check walls
		allWalls  = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
		wallCheck = CheckElementConstraints(doc,allWalls)
		if wallCheck:
			wallErrorList["WALL ERRORS"] = wallCheck
			print str(len(wallCheck)) + " - Wall Issues in Acive Doc"
			
		# check columns
		allColumns = GetAllElements(doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
		allColumns += GetAllElements(doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)
		columnCheck = CheckElementConstraints(doc,allColumns)
		if columnCheck:
			wallErrorList["COLUMN ERRORS"] = columnCheck
			print str(len(columnCheck)) + " - Column Issues in Active Doc"
			#walls that span or are unconnected
				
	except Exception as inst:
		OutputException(inst)   
		
	# check doors
	availableDoors = storefrontConfig.doorDict
	doorErrorList["DOOR ERRORS"] = []
	allDoors = GetAllElements(doc, BuiltInCategory.OST_Doors, Autodesk.Revit.DB.FamilyInstance)
	allDoors = FilterDemolishedElements(doc, allDoors)
	
	for doorId in allDoors:
		door = doc.GetElement(doorId)
		hostWallId = None
		for p in door.Parameters:
			if p.Definition.Name == "Host Id":
				hostWallId = p.AsElementId()
		# check if door is hosted on storefront
		if hostWallId:
			hostWall = doc.GetElement(hostWallId)
			if hostWall:
				if "storefront" in hostWall.Name.lower():
					#check if door exists in list of recognized doors
					doorName =  door.Name
					inList = False
					for name in availableDoors.keys():
						if doorName in name:
							inList = True
					if not inList:
						doorErrorList["DOOR ERRORS"] += [doorId]
					
	# print out door issue deail
	if doorErrorList["DOOR ERRORS"]:
		for doorId in doorErrorList["DOOR ERRORS"]:
			door = doc.GetElement(doorId)
			doorName = door.Name
			doorLevel = None
			for p in door.Parameters:
				if p.Definition.Name == "Level":
					doorLevel = p.AsValueString()
			print "Unrecognized Door Issue // " + str(doorName) + "// : " + str(doorLevel)
	
	print str(len(doorErrorList["DOOR ERRORS"])) + " - Door Issues in Active Doc"
	
	# add door errors to list
	#toSelect += errorList["DOOR ERRORS"]
	
	PrintBreakLine()
	
	# output the caught wall and column issues
	for key in wallErrorList.keys():

		if type(wallErrorList[key]) == list:
			
			for inst in wallErrorList[key]:
				elementCategory = None
				familyName = None
				typeName = None
				topConstraint = None

				if type(inst) == ElementId: 
					inst = doc.GetElement(inst)
					print "THIS" 
					print inst
				for p in inst.Parameters:
					if p.Definition.Name == "Base Constraint" or p.Definition.Name == "Base Level":
						baseConstraint = p.AsValueString()
					if p.Definition.Name == "Top Constraint" or p.Definition.Name == "Top Level":
						topConstraint = p.AsValueString()
					if p.Definition.Name == "Category":
						elementCategory = p.AsValueString()
				
				prefix = ""
				whichDoc = ""

				if topConstraint and "Unconnected" in topConstraint:
					prefix = "Unconnected "
				elif topConstraint:
					prefix = "Spanning "
				if "EC" in key:
					whichDoc = "-- EC DOC"
				else:
					whichDoc = "-- ACTIVE DOC"
						
				# print out  all errors
				output = script.get_output()
				clickable_link = output.linkify(inst.Id)
				print prefix + str(elementCategory) + " Issue // " + str(inst.Name) + " // : " + str(baseConstraint) + " --> " + str(topConstraint) + " // " + whichDoc + "-->" + clickable_link
				
		else:
			print wallErrorList[key]
			PrintBreakLine()
		PrintBreakLine()
	print ""

def storefront_load():
	"""
	Creates curtain wall types and loads families.
	"""

	#Load the options opbject
	storefrontConfig = storefront_options()

	#Selects which to load
	storefrontConfig.storefront_set_config()

	#Grab the current config
	currentConfig = storefrontConfig.currentConfig

	selectedSystem = currentConfig["currentSystem"]
	
	#Load the necessary families
	familyDirectory = os.path.dirname(os.path.realpath(__file__)).replace("lib","families\\")
	
	print "LOADING FAMILIES..."
	familiesToLoad = os.listdir(familyDirectory)
	LoadFamilies(familiesToLoad, familyDirectory)


	#Gather dicts of what exists in the project
	profileDict = GetProfileDict("I-Profile-Storefront-Mullion")
	wallTypeDict = GetWallTypeDict()
	mullionDict = GetMullionTypeDict()
	panelTypeDict = GetWindowTypeDict()
	quadMullionDict = GetQuadMullionTypeDict()
	createMullions = {}

	#-----------------------CREATE MULLION TYPES------------------------#

	#mulliontypes that will be duplicated and assigned correct profiles
	templateMullion = None
	templateQuadMullion = None

	if quadMullionDict.keys() and mullionDict.keys():
		print "LOADING CURTAIN WALLS..."
		#creates mullions that are needed, both rectangular and quad.
		with rpw.db.Transaction("Create Curtain Wall"):

			mullionTypeNames = mullionDict.keys()
			#Creates Rectangualr Mullions
			for profileName in profileDict.keys():

				#Ensure you're only creating mullion types for the selected system
				if selectedSystem.lower() == profileName.split("_")[0].lower():

					#Create a new mullion type if needed from a duplicate.
					if not any(profileName == s for s in mullionTypeNames):
						newMullionType = doc.GetElement(mullionDict[mullionDict.keys()[0]]).Duplicate(profileName)
						newMullionType.get_Parameter(BuiltInParameter.MULLION_PROFILE).Set(profileDict[profileName])
						mullionDict[profileName] = newMullionType.Id

					#Otherwise grab it from the mullion dictionary if it exists.
					else:
						newMullionType = doc.GetElement(mullionDict[profileName])

					#Set Special parameters for Mullion Types like: Offsets
					#Default
					mullionOffset = 0

					if "MODE" in profileName:
						if "Offset" in profileName:
							#set the mulliontype offset to 31mm
							mullionOffset = 0.101706
						elif "DoorFrameMid" in profileName:
							#set the mulliontype offset to 18.5mm
							mullionOffset = 0.06069554

					newMullionType.get_Parameter(BuiltInParameter.MULLION_OFFSET).Set(mullionOffset)
					

			#Creates Quad Corner Mullion
			quadMullionTypeNames = quadMullionDict.keys()
			for profileName in profileDict.keys():

				#Ensure you're only creating mullion types for the selected system
				if selectedSystem.lower() == profileName.split("_")[0].lower():

					#Any profile that ends with "_Post" will be used for the corner.
					if "post" in profileName.split("_")[1].lower():
						if not any(profileName == s for s in quadMullionTypeNames):
							newMullionType = doc.GetElement(quadMullionDict[quadMullionDict.keys()[0]]).Duplicate(profileName)
							depth1 = 0
							depth2 = 0

							for p in doc.GetElement(profileDict[profileName]).Parameters:
								if p.Definition.Name == "x1":
									depth1 += p.AsDouble()
								if p.Definition.Name == "x2":
									depth1 += p.AsDouble()
								if p.Definition.Name == "y1":
									depth2 += p.AsDouble()
								if p.Definition.Name == "y2":
									depth2 += p.AsDouble()
							for p in newMullionType.Parameters:
								if p.Definition.Name == "Depth 1":
									p.Set(depth1)
								if p.Definition.Name == "Depth 2":
									p.Set(depth2)
							quadMullionDict[profileName] = newMullionType.Id

			#-----------------------CREATE CURTAIN WALL TYPES------------------------#
			# Create curtain wall system for each system if they dont exist
			templateCW = None
			for key, value in wallTypeDict.items():
				wt = doc.GetElement(value)
				if str(wt.Kind) == "Curtain":
					templateCW = wt
					break

			curtainWallNamePrefix = "I-Storefront-"

			cwName = selectedSystem
			cwType = curtainWallNamePrefix+cwName
			if not any( cwType == s for s in wallTypeDict.keys()):
				newCW = templateCW.Duplicate(cwType)
			else:
				newCW = doc.GetElement(wallTypeDict[cwType])

			#newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(mullionDict[cwName+"_Post"])
			newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_VERT"]])
			newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER1_VERT"]])
			newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_VERT).Set(quadMullionDict[currentConfig["AUTO_MULLION_BORDER2_VERT"]])
			newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_INTERIOR_HORIZ"]])
			newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER1_HORIZ"]])
			newCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[currentConfig["AUTO_MULLION_BORDER2_HORIZ"]])
			newCW.get_Parameter(BuiltInParameter.AUTO_PANEL_WALL).Set(panelTypeDict[currentConfig["AUTO_PANEL_WALL"]])
			newCW.get_Parameter(BuiltInParameter.AUTO_JOIN_CONDITION_WALL).Set(currentConfig["AUTO_JOIN_CONDITION_WALL"]) # vertical continuous
			newCW.get_Parameter(BuiltInParameter.ALLOW_AUTO_EMBED).Set(currentConfig["ALLOW_AUTO_EMBED"])
			newCW.get_Parameter(BuiltInParameter.FUNCTION_PARAM).Set(currentConfig["FUNCTION_PARAM"])
			newCW.get_Parameter(BuiltInParameter.SPACING_LAYOUT_HORIZ).Set(currentConfig["SPACING_LAYOUT_HORIZ"])
			newCW.get_Parameter(BuiltInParameter.SPACING_LAYOUT_VERT).Set(currentConfig["SPACING_LAYOUT_VERT"])

			
		print "...CURTAIN WALLS LOADED"
	else: 
		if not quadMullionDict.keys() or not mullionDict.keys():
			Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Please check the 'Curtain Wall Mullions' in the Project Browser and ensure you have at least (1) Quad Mullion type & (1) Rectangular Mullion type. Right click on them to create a 'New Type' if needed.")
			sys.exit()
		
	#__window__.Close()

def storefront_annotate():
	"""Annotates a view with storefront.
	"""

	print "CREATING ANNOTATIONS"
	PrintBreakLine()

	currentView = uidoc.ActiveView
	storefrontFrames = []
	annotationNotes = []

	standardTol = 0.01


	#Form input
	from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm

	components = [Label('Select System'),
					ComboBox("combobox1", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
					ComboBox("combobox2", {"Custom/Standard": "CS", "Glass Sizes": "GS"}),
					Separator(),
					Button('Go')]

	form = FlexForm("Storefront Annotate", components)
	form.show()

	if not form.values:
		sys.exit()
	else: 
		systemName = form.values["combobox1"]
		annoType = form.values["combobox2"]


	#Load config
	storefrontConfig = storefront_options()

	if not systemName.lower() in storefrontConfig.currentConfig["currentSystem"].lower():
		storefrontConfig.storefront_set_config()
		systemName = storefrontConfig.currentConfig["currentSystem"]
		storefrontConfig.storefront_save_config()
	
	famTypeDict = GetFamilyTypeDict("Panel-Symbol-Custom")
	famTypeDict.update(GetFamilyTypeDict("Panel-Symbol-Standard"))

	#Load standard sizes
	systemStandardHorizontals = storefrontConfig.currentConfig["systemStandardHorizontals"]
	sillStandards = systemStandardHorizontals["sill"]
	


	#collect notest in the view if there are any
	annotationNotes = list(GetElementsInView(BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, currentView.Id))
	annotationNotes = FilterElementsByName(doc, annotationNotes,["Panel","Symbol"], False)

	#collect walls and mullions
	allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
											view=currentView, 
											where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))

	allStorefrontMullions = []

	#Collect mullions
	for sfwall in allStorefrontWalls:
		for sfMullionsId in sfwall.CurtainGrid.GetMullionIds():
			allStorefrontMullions.append(doc.GetElement(sfMullionsId))

	annotationsList = []

	# Toggle: if theres annotations in the view already, then delete them.

	if annoType == "CS":

		if annotationNotes:
			with rpw.db.Transaction("Clear Annotations"):
				DeleteElementsInView(currentView.Id, BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, "Panel-Symbol-Custom")
				DeleteElementsInView(currentView.Id, BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, "Panel-Symbol-Standard")


		# Toggle: if there is NOT annotations in the view, then create them
		else:

			for sfMullion in allStorefrontMullions:

				sfMullionName = sfMullion.Name

				if sfMullion.LocationCurve:

					sfMullionLength = sfMullion.LocationCurve.Length

					if "sill" in sfMullionName.lower():
						placementPoint = sfMullion.LocationCurve.Evaluate(0.5, True)
						text = ""
						notesymbol = None

						for key, standardLength in sillStandards.items():
							if abs(sfMullionLength - standardLength) < standardTol:
								text = "STANDARD"
								notesymbol = doc.GetElement(famTypeDict["Panel-Symbol-Standard"])
								break
							else:
								text = "CUSTOM"
								notesymbol = doc.GetElement(famTypeDict["Panel-Symbol-Custom"])

						annotationsList.append([placementPoint, text, notesymbol])
				
			#Place annotations	
			with rpw.db.Transaction("Clear Annotations"):
				for annot in annotationsList:
					point = annot[0]
					sym = annot[2]
					annotInst = doc.Create.NewFamilyInstance(point, sym, currentView)
					for p in annotInst.Parameters:
						if p.Definition.Name == "label_text":
							p.Set(annot[1])


	#Creates glass width tags on a plan
	if annoType == "GS":

		junctionPoints = []
		intermediatePoints = []

		glassTagList = []


		for mullion in allStorefrontMullions:

			mullionLength = mullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()

			if mullionLength > 0 and mullion.LocationCurve:

				mullionName = mullion.Name.lower()
				mullionRoom = mullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
				mullionPoint = mullion.Location.Point
				mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)

				if "post" in mullionName:
					junctionPoints.append([mullionPoint, mullionName])

				if "wallstart" in mullionName:
					junctionPoints.append([mullionPoint, mullionName])

				if "door" in mullionName:
					junctionPoints.append([mullionPoint, mullionName])

				if "intermediate" in mullionName:
					intermediatePoints.append([mullionPoint, mullionName])



		for storefrontElevation in allStorefrontWalls:

			panelIds = storefrontElevation.CurtainGrid.GetPanelIds()

			linearGlass = storefrontElevation.Location.Curve.Length

			storefrontElevationID = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
			storefrontSuperType = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()

			#Panels
			for panelId in panelIds:

				panel = doc.GetElement(panelId)
				panelWidth = panel.get_Parameter(BuiltInParameter.WINDOW_WIDTH).AsDouble()
				panelHeight = panel.get_Parameter(BuiltInParameter.WINDOW_HEIGHT).AsDouble()

				if (panelWidth > 0) and (panelHeight > 0):

					condition = None
					varient01 = None
					varient02 = None

					panelFamily = panel.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
					panelType = panel.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
					panelSF = panelWidth * panelHeight
					panelSizeName = str(panelWidth) + " x " + str(panelHeight)

					#Get panel point and flatten
					panelPoint = panel.GetTransform().Origin
					panelPoint = XYZ(panelPoint.X, panelPoint.Y, 0)

					panelRoomID = panel.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()

					#Default panel position
					panelPositions = []

					# Checking end conditions against junctions (post, wallstart, and door frames)
					juntionsAndDoorFrames = junctionPoints


					if "glazed" in panelFamily.lower():
						
						numFoundEndConditions = 0

						#CORRECT PANEL WIDTH + HEIGHT FOR ACTUAL SIZES
						# Add correction for differences between modeling and reality

						glassWidthCorrection = 0
						glassHeightCorrection = 0

						#Ends
						for i in range(len(juntionsAndDoorFrames)):
							testPoint = juntionsAndDoorFrames[i][0]
							testMullionName = juntionsAndDoorFrames[i][1]
							testDist1 = testPoint.DistanceTo(panelPoint)

							if testDist1 < ((panelWidth/2) + (2.1/12)):
								glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]
								numFoundEndConditions += 1 #Found an end condition
								#print storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]

						#Intermediates
						for i in range(len(intermediatePoints)):
							testPoint = intermediatePoints[i][0]
							testMullionName = intermediatePoints[i][1]
							testDist2 = testPoint.DistanceTo(panelPoint)

							if testDist2 < ((panelWidth/2) + (1.8/2)):
								glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]
								numFoundEndConditions += 1 #Found an end condition
								#print storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]

						#Butt joints
						numButtJoints = 2 - numFoundEndConditions #Glass has 2 ends, if above conditions arent detected, its assumed a butt joint is found
						glassWidthCorrection += (numButtJoints * storefrontConfig.currentConfig["panelCorrections"]["horizontalButtJoint"])

						#print numButtJoints


						#Head and Sill pockets
						glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalSill"]
						glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalHead"]
						
						#create list of glass size tags
						glassTagList.append([panelPoint,(panelWidth + glassWidthCorrection)])

		
		#place glass tags
		tagFamTypeDict = GetFamilyTypeDict("Panel-Symbol-Standard")
		tagSym = doc.GetElement(tagFamTypeDict["Panel-Symbol-Standard"])


		#Set units and format options to convert decimal feet to inche fractional
		formatUnits = doc.GetUnits()
		fvo = FormatValueOptions()
		fo = FormatOptions(DisplayUnitType.DUT_FRACTIONAL_INCHES)
		fo.Accuracy = .0625
		fvo.SetFormatOptions(fo)

		#Place annotations	
		with rpw.db.Transaction("Tag Glass"):
			for tag in glassTagList:
				point = tag[0]
				#tag = size[2]
				
				sizeInches = UnitFormatUtils.Format(formatUnits, UnitType.UT_Length, tag[1], False, False, fvo)

				annotInst = doc.Create.NewFamilyInstance(point, tagSym, currentView)
				for p in annotInst.Parameters:
					if p.Definition.Name == "label_text":
						p.Set(sizeInches)



	print "FINISHED"

def storefront_dimension():
	"""Creates dimension strings on
	a storefront laser layout view.
	"""

	from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm

	currentView = uidoc.ActiveView
	theta = math.pi*0.5
	axis_z = Autodesk.Revit.DB.Line.CreateBound(XYZ(0,0,0),XYZ(0,0,1))
	searchDist = 4
	offsetDim = 1

	#Get the linear dimension types in the doc to select from
	allDimensionTypes = GetAllElements(doc, None, Autodesk.Revit.DB.DimensionType)
	linearDimensionTypes = {}

	autodimOptions = {"Laser Layout": "Laser Layout", "Partition Plan" : "Partition Plan"}

	for elemId in allDimensionTypes:
		dT = doc.GetElement(elemId)
		if "Linear" in dT.FamilyName:
			dTName = dT.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
			linearDimensionTypes[dTName] = dT


	#Select dimension settings
	components = [Label('Dimension Distance From Datums'),
					ComboBox("combobox1", {"4'-0''": 4.0, "8'-0''": 8.0}),
					Label('Dimension Type'),
					ComboBox("combobox2", linearDimensionTypes),
					Label('Dimension Function'),
					ComboBox("combobox3", autodimOptions),
					Label('System'),
					ComboBox("combobox4", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
					Separator(),
					Button('Go')]

	form = FlexForm("Storefront Auto Dim", components)
	form.show()

	if not form.values:
		sys.exit()
	else: 
		searchDist = form.values["combobox1"]
		selectedDimType = form.values["combobox2"]
		autodimOption = form.values["combobox3"]
		systemName = form.values["combobox4"]

	if autodimOption == "Laser Layout":

		#Get walls for datum lines to measure to
		allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
		#storefrontWalls = FilterElementsByName(doc, allWalls, ["Storefront","Storefront"], False)

		with rpw.db.Transaction("Auto Dim Lines"):
			# Gather all the lines to filter and delete the ones we dont want.
			allLines = list(GetElementsInView(BuiltInCategory.OST_Lines, Autodesk.Revit.DB.CurveElement, currentView.Id))

			for lineId1 in allLines:
				line1 = doc.GetElement(lineId1)
				lineName = line1.LineStyle.Name
				
				if ("Full" in lineName or "Partial" in lineName) and line1.GeometryCurve.IsBound:
					refArray = ReferenceArray()
					lineReference =line1.GeometryCurve

					line1StartPoint = lineReference.GetEndPoint(0)
					line1EndPoint = lineReference.GetEndPoint(1)

					x1 = line1EndPoint.X - line1StartPoint.X
					y1 = line1EndPoint.Y - line1StartPoint.Y

					vect1Norm = XYZ(y1 * -1, x1, 0).Normalize()
					vect1 = vect1Norm.Multiply(offsetDim)

					point1 = line1StartPoint.Add(vect1)
					point2 = line1EndPoint.Add(vect1)

					dimLine = Autodesk.Revit.DB.Line.CreateBound(point1, point2)

					refArray.Append(lineReference.GetEndPointReference(0)) 
					refArray.Append(lineReference.GetEndPointReference(1))
					newDim = doc.Create.NewDimension(currentView, dimLine, refArray)
					newDim.DimensionType = selectedDimType
				
				
				elif "control" in lineName.lower() and line1.GeometryCurve.IsBound:

					for wallId in allWalls:
						wall = doc.GetElement(wallId)
						if "Basic" in str(wall.WallType.Kind):
							line2 = wall.Location.Curve

							#Crazy way to get the wall centerline as a Reference object
							unique = wall.UniqueId
							refString = System.String.Format("{0}:{1}:{2}",unique,-9999,1)
							wall_centre = Reference.ParseFromStableRepresentation(doc,refString)

							line2StartPoint = line2.Evaluate(0, True)
							line2Midpoint = line2.Evaluate(0.5, True)

							x1 = line2Midpoint.X - line2StartPoint.X
							y1 = line2Midpoint.Y - line2StartPoint.Y
							z1 = line2Midpoint.Z

							vect1Norm = XYZ(x1,y1,0).Normalize()
							vect1 = vect1Norm.Multiply(searchDist)

							#Create the vectors
							vect2 = XYZ(vect1.Y * -1, vect1.X, vect1.Z)
							vect3 = XYZ(vect1.Y, vect1.X * -1, vect1.Z)

							#Add them to the midpoints
							point1 = line2Midpoint.Add(vect2)
							point2 = line2Midpoint.Add(vect3)

							
							#Create the line that will be used to test intersections with datum lines
							testLine = Autodesk.Revit.DB.Line.CreateBound(point1, point2)
							 
							#Create the datum line at the same z level as the test intersection lines
							line1GC = line1.GeometryCurve
							datumPoint1 = line1GC.GetEndPoint(0)
							datumPoint2 = line1GC.GetEndPoint(1)

							datumPoint1 = XYZ(datumPoint1.X, datumPoint1.Y, line2Midpoint.Z)
							datumPoint2 = XYZ(datumPoint2.X, datumPoint2.Y, line2Midpoint.Z)

							flattenedDatumLine = Autodesk.Revit.DB.Line.CreateBound(datumPoint1, datumPoint2)

							intersection = RevitCurveCurveIntersection(flattenedDatumLine, testLine)

							if intersection:

								#Adjust the position parameter based on distance away
								#from the datum line so they are easier to read

								posFactor = (line2Midpoint.DistanceTo(intersection)/searchDist) * (line2StartPoint.DistanceTo(line2Midpoint)/2)
								adjustVect = vect1Norm.Multiply(posFactor)

								p1 = line2Midpoint.Add(adjustVect)
								p2 = intersection.Add(adjustVect)
								
								if p1.DistanceTo(p2) > app.ShortCurveTolerance:
									dimLine = Autodesk.Revit.DB.Line.CreateBound(p1, p2)
									refArray = ReferenceArray()
									#lineReference =line1.GeometryCurve
									refArray.Append(line1.GeometryCurve.Reference)
									refArray.Append(wall_centre)
									newDim = doc.Create.NewDimension(currentView, dimLine, refArray)
									newDim.DimensionType = selectedDimType

	elif autodimOption == "Partition Plan":

		"""
		Creates sill dimensions for partition install plans
		""" 

		allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
											view=currentView, 
											where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))

		allStorefrontPanels  = []
		allStorefrontMullions = []

		#Collect mullions
		for sfwall in allStorefrontWalls:
			for sfMullionsId in sfwall.CurtainGrid.GetMullionIds():
				allStorefrontMullions.append(doc.GetElement(sfMullionsId))

		with rpw.db.Transaction("Auto Dim Sills"):

			for sfMullion in allStorefrontMullions:
				
				if "sill" in sfMullion.Name.lower() and sfMullion.LocationCurve:

					mullionDirection = sfMullion.LocationCurve.Direction

					refArray = ReferenceArray()
					edgeCurve = None

					options = app.Create.NewGeometryOptions()
					options.IncludeNonVisibleObjects = True
					options.ComputeReferences = True

					faces = []
					perpFace = None

					mullionGeo = sfMullion.get_Geometry(options)

					for item in list(mullionGeo):
						geometry = list(item.GetInstanceGeometry())
						for geo in geometry:
							if type(geo) == Autodesk.Revit.DB.Solid:
								if list(geo.Faces.GetEnumerator()):
									faces = list(geo.Faces.GetEnumerator()) 
						if faces:
							break

					for face in faces:

						faceDirection = face.FaceNormal


						if abs(90-((faceDirection.AngleTo(mullionDirection)*360)/ (2*math.pi))) < 0.01 and faceDirection.Z == 1 :
							#print "found face"
						
							edgeloops = list(face.EdgeLoops)[0]
							edgesFound = 0

							for edge in edgeloops:
								
								#if abs(edge.AsCurve().Direction.Z) == 1:
								if abs(180-((edge.AsCurve().Direction.AngleTo(mullionDirection)*360)/ (2*math.pi))) < 0.01:

									edgeCurve = Autodesk.Revit.DB.Line.CreateBound(edge.AsCurve().GetEndPoint(0), edge.AsCurve().GetEndPoint(1))

									edgesFound += 1
									break
							break

					if edgesFound >= 1:
					
						line1 = sfMullion.LocationCurve

						line1StartPoint = line1.GetEndPoint(0)
						line1EndPoint = line1.GetEndPoint(1)

						x1 = line1EndPoint.X - line1StartPoint.X
						y1 = line1EndPoint.Y - line1StartPoint.Y

						vect1Norm = XYZ(y1 * -1, x1, 0).Normalize()
						vect1 = vect1Norm.Multiply(offsetDim)

						point1 = line1StartPoint.Add(vect1)
						point2 = line1EndPoint.Add(vect1)

						dimLine = Autodesk.Revit.DB.Line.CreateBound(point1, point2)

						if edgeCurve:
							dummyDetail = doc.Create.NewDetailCurve(currentView, edgeCurve)

							refArray.Append(dummyDetail.GeometryCurve.GetEndPointReference(0)) 
							refArray.Append(dummyDetail.GeometryCurve.GetEndPointReference(1))

							newDim = doc.Create.NewDimension(currentView, dimLine, refArray)
							newDim.DimensionType = selectedDimType



def storefront_check_errors():
	"""Checks errors for mullions and panels
	"""

	currentView = uidoc.ActiveView
	famTypeDict = GetFamilyTypeDict("Fabrication-Error-Symbol")

	# Clear existing error notations
	errorNotations = list(GetElementsInView(BuiltInCategory.OST_GenericAnnotation, Autodesk.Revit.DB.FamilyInstance, currentView.Id))
	errorNotations = FilterElementsByName(doc, errorNotations,["Fabrication","Error-Symbol"], False)
	if errorNotations:
		with rpw.db.Transaction("Place Errors"):
			for error in errorNotations:
				doc.Delete(error)


	def PointsAndErrors(mullions_list, errorName, cat_or_ids):
		"""adds to lists of points and errors"""
		errorsToFlag = []
		compList =[]
		for m in mullions_list:
			mElem = doc.GetElement(m)
			if m not in compList:
				intersectingMulls = FindIntersectingMullions(mElem, cat_or_ids)
				if list(intersectingMulls):
					mullPt = mElem.Location.Point
					errorsToFlag.append([mullPt, errorName])
					for mm in list(intersectingMulls):
						compList.append(mm.Id)
		return errorsToFlag

	def MullionClash():

		errorsToFlag = []

		selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id

		allMullions = GetAllElements(doc, BuiltInCategory.OST_CurtainWallMullions, Autodesk.Revit.DB.FamilyInstance, currentView=True)
		allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)

		allWalls = FilterElementsByName(doc, allWalls, ["Storefront","Storefront"], True)

		errorsToFlag += PointsAndErrors(allMullions, "Mullion-Mullion Intersects", BuiltInCategory.OST_CurtainWallMullions)
		errorsToFlag += PointsAndErrors(allMullions, "Mullion-Panel Intersects", BuiltInCategory.OST_CurtainWallPanels)
		if allWalls:
			errorsToFlag += PointsAndErrors(allMullions, "Mullion-Wall Intersects", allWalls)

		return errorsToFlag

	def PanelClash():


		errorsToFlag = []
		
		allPanels = GetAllElements(doc, BuiltInCategory.OST_Windows, Autodesk.Revit.DB.FamilyInstance, currentView=True)
		allPanels = FilterDemolishedElements(doc, allPanels)

		panelMinWidth = 0.45
		panelMaxWidth = 5.0
		panelMaxHeight = 8.14

		### ITERATE OVER PANEL LIST ###
		for p in allPanels:
			famInst = doc.GetElement(p)

			pan_height = famInst.Parameter[BuiltInParameter.FAMILY_HEIGHT_PARAM].AsDouble()
			pan_width = famInst.Parameter[BuiltInParameter.FAMILY_WIDTH_PARAM].AsDouble()

			if "empty" not in famInst.Name.lower():
				if pan_width < panelMinWidth:
					errorsToFlag.append([famInst.GetTransform().Origin, "Small Panel"])
				elif pan_width > panelMaxWidth:
					errorsToFlag.append([famInst.GetTransform().Origin, "Wide Panel"])
				elif pan_height > panelMaxHeight:
					errorsToFlag.append([famInst.GetTransform().Origin, "Tall Panel"])
			else:
				pass
		
		return errorsToFlag

	def ECWallClash():

		errorsToFlag = []
		columnsLinesEdgesEC = []
		wallsLinesEdgesEC = []


		docLoaded = RevitLoadECDocument(quiet=True)
		if docLoaded[0]:
			docEC = docLoaded[0]
			ecTransform = docLoaded[1]

			selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id

			selectedLevelInst = doc.GetElement(selectedLevel)
			levelElevationEC = None 
			for p in selectedLevelInst.Parameters:
				if p.Definition.Name == "Elevation":
					levelElevationEC = p.AsDouble()

			allWallsEC  = GetAllElements(docEC, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall)
			allColumnsEC = GetAllElements(docEC, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance)
			allColumnsEC += GetAllElements(docEC, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance)

			selectedWallsEC = FilterElementsByLevel(docEC, allWallsEC, levelElevationEC)
			selectedColumnsEC = FilterElementsByLevel(docEC, allColumnsEC, levelElevationEC)

			wallsLinesEdgesEC = GetWallEdgeCurves(docEC, selectedWallsEC, ecTransform)
			columnsLinesEdgesEC = GetColumnEdgeCurves(docEC, selectedColumnsEC, ecTransform)

		allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
		storefrontWalls = FilterElementsByName(doc, allWalls,["Storefront","Storefront"], False)
		storefrontWalls = FilterWallsByKind(doc, storefrontWalls, "Basic")

		obstructionEdges = columnsLinesEdgesEC
		obstructionEdges += wallsLinesEdgesEC

		if obstructionEdges:
			for sfWallId in storefrontWalls:
				sfWall = doc.GetElement(sfWallId)
				locLine = sfWall.Location.Curve
				locLineStart = locLine.GetEndPoint(0)
				locLineEnd = locLine.GetEndPoint(1)

				for obstructionLine in obstructionEdges:
					obstLineElevation = obstructionLine.GetEndPoint(0).Z
					locLineStart = XYZ(locLineStart.X, locLineStart.Y, obstLineElevation)
					locLineEnd = XYZ(locLineEnd.X, locLineEnd.Y, obstLineElevation)
					locLineFlat = Line.CreateBound(locLineStart, locLineEnd)
					intersection = RevitCurveCurveIntersection(locLineFlat,obstructionLine)

					if intersection:
						#ERROR: Hit Existing Condition
						errorsToFlag.append([intersection, "Hit EC"])

		return errorsToFlag

	allErrors = []
	allErrors += ECWallClash()
	allErrors += MullionClash()
	allErrors += PanelClash()

	errorSymbolId = famTypeDict["Fabrication-Error-Symbol"]

	if allErrors:
		with rpw.db.Transaction("Error Check"):
			RevitPlaceErrorsInView(currentView, allErrors, errorSymbolId)

def storefront_report():

	"""Reporting tool that prepares an export

	reportType = "material" or "cut"
	Material report is just a take-off
	Cut report is a full cu
	tlist.
	"""

	
	print "CREATING REPORT...PLEASE WAIT..."
	PrintBreakLine()
	currentView = uidoc.ActiveView
	levelName = currentView.GenLevel.Name
	levelElevation = currentView.GenLevel.Elevation

	glassList = []
	storefrontFrames = []

	oneByWidth = 1.75/12
	tol = 0.001

	storefrontConfig = storefront_options()
	
	systemName = None


	mullionDict = GetMullionTypeDict()
	panelTypeDict = GetWindowTypeDict()
	doorDict = storefrontConfig.doorDict


	from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm
	# Select the report type
	components = [Label('Pick Report Type:'),
					ComboBox("combobox1", {"Estimation - Take Off": "takeoff", "Fabrication - Cut List": "cutlist"}),
					Label('Specify System'),
					ComboBox("combobox2", {"Elite": "Elite", "MODE": "MODE", "Extravega": "Extravega"}),
					Separator(),
					Button('Go')]

	form = FlexForm("Storefront Report", components)
	form.show()

	if not form.values:
		sys.exit()
	else:
		reportType = form.values["combobox1"]
		systemName = form.values["combobox2"]


		if not systemName.lower() in storefrontConfig.currentConfig["currentSystem"].lower():
			storefrontConfig.storefront_set_config()
			systemName = storefrontConfig.currentConfig["currentSystem"]
			storefrontConfig.storefront_save_config()
			

	currentSelected = list(uidoc.Selection.GetElementIds())
	allStorefrontWalls = []

	if currentSelected:
		for id in currentSelected:
			inst = doc.GetElement(id)
			if inst.Category.Name == "Walls":
				instName = None
				try:
					instName = inst.Name.lower()
				except:
					for p in inst.Parameters:
						if p.Definition.Name == "Name":
							instName = p.AsString().lower()
				if systemName.lower() in instName.lower() and str(inst.WallType.Kind) == "Curtain":
					allStorefrontWalls.append(inst)
	else:
		allStorefrontWalls = rpw.db.Collector(of_class='Wall', 
											view=currentView, 
											where=lambda x: (str(x.WallType.Kind) == "Curtain") and (systemName.lower() in x.Name.lower()))

	#Gather elements in view
	#cutlist specific
	

	allStorefrontMullions = []

	#allStorefrontMullions = list(rpw.db.Collector(of_class='FamilyInstance', of_category='OST_CurtainWallMullions',
	#										level=currentView.GenLevel, 
	#										where=lambda x: (systemName.lower() in x.Name.lower())).unwrap())

	for sfwall in allStorefrontWalls:
		sfMullionsIds = sfwall.CurtainGrid.GetMullionIds()
		for sfMullionsId in sfMullionsIds:
			allStorefrontMullions.append(doc.GetElement(sfMullionsId))




	allDoors = rpw.db.Collector(of_class='FamilyInstance', of_category='OST_Doors')

	allStorefrontBasicWalls = rpw.db.Collector(of_class='Wall', 
											view=currentView, 
											where=lambda x: (str(x.WallType.Kind) == "Basic") and ("storefront" in x.Name.lower()))

	allAreas = rpw.db.Collector(of_class='SpatialElement', of_category='OST_Areas',
											view=currentView)

	allWalls = rpw.db.Collector(of_class='Wall')

	allFamInstances = rpw.db.Collector(of_class='FamilyInstance', of_category='OST_SpecialityEquipment')
	projectInfo = doc.ProjectInformation
	projectName = projectInfo.get_Parameter(BuiltInParameter.PROJECT_NAME).AsString()

	if not projectName:
		projectName = "UNNAMED PROJECT"

	todaysDate = str(dt.Today.Month)+"/"+str(dt.Today.Day)+"/"+str(dt.Today.Year)
	currentUser = doc.Application.Username

	systemStandardHorizontals = storefrontConfig.currentConfig["systemStandardHorizontals"]
	systemStandardVerticals = storefrontConfig.currentConfig["systemStandardVerticals"]
	detectEndConditions = storefrontConfig.currentConfig["cutlistDetectEndConditions"]

	print "...GATHERING DATA"

	fullPosts = 0
	PartialPosts = 0

	conditionsArray = [["ELEMENT", "SYSTEM", "CONDITION", "VARIENT 01", "VARIENT 02", "AREA", "ROOM", "LENGTH", "WIDTH", "COMMENT"]]

	linearFull = 0
	linearDoors = 0
	linearPartial = 0
	linearOther = 0

	linearBasicFull = 0
	linearBasicDoors = 0
	linearBasicPartial = 0
	linearBasicOther = 0

	areaGlass = 0
	areaGlassStandard = 0
	countGlass = 0
	
	areaInfillPanel = 0
	countInfillPanel = 0
	
	fullPostPoints = []
	partialPostPoints = []
	partialSillHeight = 0
	fullHeadHeight = 0

	glassExportDict = {}
	solidExportDict = {}
	mullionExportDict = {}
	doorExportDict = {}

	allWallsSummary = {}
	allDoorsSummary = {}
	allSpecialObjectSummary = {}

	junctionPoints = []
	doorFramePoints = []
	intermediatePoints = []

	areaBoundaryPoints = {}

	standardTol = 0.01

# Creates list of boundary points that will test for element inclusion
	for anArea in allAreas:
		areaName = anArea.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
		areaBoundaryPoints[areaName] = GetArea2DBoundaryPoints(anArea)

# Walls - Collects list of wall types and lengths inthe model for a general report.
	wallTypeAntiKeywords = ["finish", "furring", "gyp", "artwork", "chase", "toilet"]

	for wall in allWalls:
		walltype = wall.Name
		if not any(x in walltype.lower() for x in wallTypeAntiKeywords):
			wallLevel = doc.GetElement(wall.LevelId).Name

			if wallLevel not in allWallsSummary.keys():
				allWallsSummary[wallLevel] = {}

			if walltype not in allWallsSummary[wallLevel].keys():
				allWallsSummary[wallLevel][walltype] = [str(wall.WallType.Kind), wall.Location.Curve.Length]
			else:
				allWallsSummary[wallLevel][walltype][1] += wall.Location.Curve.Length


# Doors - Collects list of doors in the model for a general report

	doorHostKeywords = ["storefront", "partition", "glass", "frameless"]
	doorHostAntiKeywords = ["toilet", "gyp"]

	for door in allDoors:
		door = rpw.db.Element(door)
		if door.Host:
			doorHost = str(door.Host.Name) + " - " + str(door.Host.WallType.Kind)

			if any(x in doorHost.lower() for x in doorHostKeywords) and not any(x in doorHost.lower() for x in doorHostAntiKeywords):

				doorFamilyName = door.get_family(wrapped=True).name
				doorTypeName = door.get_symbol(wrapped=True).name
				
				if doc.GetElement(door.LevelId):
					doorLevel = doc.GetElement(door.LevelId).Name
					doorWidth = door.Symbol.get_Parameter(BuiltInParameter.DOOR_WIDTH).AsValueString()
					doorHasCardReader = 0

					doorTypeComments = door.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_COMMENTS).AsString()

					doorToRoom = door.ToRoom[doc.GetElement(door.CreatedPhaseId)]
					doorFromRoom = door.FromRoom[doc.GetElement(door.CreatedPhaseId)]
					doorRooms = [doorToRoom, doorFromRoom]

					for i in range(len(doorRooms)):
						#Make sure room is not None.
						room1 = doorRooms[i]
						room2 = doorRooms[i-1]
						if room1:
							#Make sure that the door is not an internal office door.
							try:
								if room1.Id == room2.Id:
									continue
							except:
								pass

							roomName = room1.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
							deskCount = room1.LookupParameter("DeskCount_Room")
							if deskCount:
								deskCount = deskCount.AsInteger()
								if deskCount > 9:
									doorHasCardReader = 1


					if doorLevel not in allDoorsSummary.keys():
						allDoorsSummary[doorLevel] = {}

					if doorTypeName not in allDoorsSummary[doorLevel].keys():
						allDoorsSummary[doorLevel][doorTypeName] = [str(doorFamilyName), doorTypeComments, doorHost, doorWidth, doorHasCardReader, 1]
					else:
						allDoorsSummary[doorLevel][doorTypeName][5] += 1
						allDoorsSummary[doorLevel][doorTypeName][4] += doorHasCardReader

# Specialty Items - Collects list of specialty items for a general report
	specialItemsKeywords = ["whiteboard", "clarus", "glassboard"]

	for famInstance in allFamInstances:
		fi = rpw.db.Element(famInstance)
		try:
			fiFamilyName = fi.get_family(wrapped=True).name
			fiTypeName = fi.get_symbol(wrapped=True).name
			fiTypeComments = fi.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_COMMENTS).AsString()

			found = False

			for search in specialItemsKeywords:
				if search in fiFamilyName.lower():
					found = True
					break

			if found:

				fiLevelId = fi.get_Parameter(BuiltInParameter.FAMILY_LEVEL_PARAM).AsElementId()

				if fiLevelId.IntegerValue == -1:
					fiLevelId = fi.Room[doc.GetElement(fi.CreatedPhaseId)].LevelId
				
				fiLevel = doc.GetElement(fiLevelId).Name

				fiNameConcat = fiTypeName + " - " + fiFamilyName

				if fiLevel not in allSpecialObjectSummary.keys():
					allSpecialObjectSummary[fiLevel] = {}

				if fiNameConcat not in allSpecialObjectSummary[fiLevel].keys():
					allSpecialObjectSummary[fiLevel][fiNameConcat] = [str(fiFamilyName), fiTypeComments, 1]
				else:
					allSpecialObjectSummary[fiLevel][fiNameConcat][2] += 1
		except Exception as e:
			continue

	#COLLECT DOOR INFORMATION

	for door in allDoors:
		door = rpw.db.Element(door)
		doorFamilyName = door.get_family(wrapped=True).name
		doorTypeName = door.get_symbol(wrapped=True).name
		doorHost = door.Host
		doorDesignOption = door.DesignOption

		if door.Id and doorHost:

			if doorDesignOption:
				if not doorDesignOption.IsPrimary:
					continue
			doorEntry = {door.Id.IntegerValue  : {"DoorFamily": doorFamilyName,
								"HostId": doorHost.Id.IntegerValue}}

			if doorTypeName in doorExportDict.keys():
				doorExportDict[doorTypeName].update(doorEntry)
			else:
				doorExportDict[doorTypeName] = doorEntry


	# CREATE CUT LIST EXPORT 
	if reportType == "cutlist":

		# MULLIONS AND PANELS INHERIT ROOM NUMBERS
		for storefrontWall in allStorefrontWalls:
			InheritRoomLocation(storefrontWall)


		#STANDARD LENGTHS FOR CONDITIONS
		sillStandards = systemStandardHorizontals["sill"]
		postStandards = systemStandardVerticals["post"]
		wallstartStandards = systemStandardVerticals["post"]
		doorframeStandards = systemStandardVerticals["doorframe"]
		intermediateStandards = systemStandardVerticals["intermediate"]
		endStandards = systemStandardVerticals["end"]

		# CONDITIONS
		for mullion in allStorefrontMullions:

			mullionLength = mullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()

			if mullionLength > 0 and mullion.LocationCurve:

				mullionName = mullion.Name.lower()
				mullionRoom = mullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
				mullionPoint = mullion.Location.Point
				mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)

				mullionCurve = mullion.LocationCurve
				mullionCenter = mullionCurve.Evaluate(0.5, True)

				mullionArea = None

				condition = None
				varient01 = None
				varient02 = None
				conditionComment = None

				# Find which area the condition occurs
				for areaName, areaPoints in areaBoundaryPoints.items():
					if PointInPolygon(mullionPoint, areaPoints):
						mullionArea = areaName

				# ----------------------------- VERTICALS -----------------------------

				# POST Intersections: 2 Way, 3 Way, 4 Way
				if "post" in mullionName:
					
					postIntersections = []
					junctionPoints.append([mullionPoint, mullionName])
					#Flatten mullion point and set to 0

					testCircle = Ellipse.Create(mullionPoint, 1, 1,XYZ(1.0,0.0,0.0),XYZ(0.0,1.0,0.0),0.0,10.0)

					for storefrontElevation in allStorefrontWalls:
						storefrontLine = storefrontElevation.Location.Curve
						sfStart = storefrontLine.GetEndPoint(0)
						sfEnd = storefrontLine.GetEndPoint(1)

						#Flatten the wall curve for intersection test
						flatStart = XYZ(sfStart.X, sfStart.Y, 0)
						flatEnd = XYZ(sfEnd.X, sfEnd.Y, 0)
						storefrontLintFlat = Line.CreateBound(flatStart, flatEnd)

						#Checks for neighboring intersecting curtain wall
						intersections = RevitCircleCurveIntersection(storefrontLintFlat, testCircle, filterIntersectionType="Overlap")

						if intersections:
							for intersection in intersections:
								postIntersections.append(storefrontElevation.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET))
					
					if postIntersections:

						#If any walls are partial height infered by base offset parameter
						condition = "POST"

						numIntersection = len(postIntersections)

						varient01 = str(numIntersection) + " WAY"

						#Search for standard lengths in the system config

						for key, standardLength in postStandards.items():
							if abs(mullionLength - standardLength) < standardTol:
								varient02 = key
								break
							else:
								varient02 = "CUSTOM"

						#Comments
						if "mode" in systemName.lower():
							conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"
						
				
				# WALL STARTS
				elif "wallstart" in mullionName:
					condition = "WALLSTART"
					varient01 = "1 WAY"
					junctionPoints.append([mullionPoint, mullionName])

					#Search for standard lengths in the system config

					for key, standardLength in wallstartStandards.items():
						if abs(mullionLength - standardLength) < standardTol:
							varient02 = key
							break
						else:
							varient02 = "CUSTOM"

					if "mode" in systemName.lower():
							conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"

					
				elif "door" in mullionName:
					condition = "DOORFRAME"
					doorFramePoints.append([mullionPoint, mullionName])

					varient01 = "TYPICAL"

					for key, standardLength in doorframeStandards.items():
						if abs(mullionLength - standardLength) < standardTol:
							varient02 = key
							break
						else:
							varient02 = "CUSTOM"

					
				# INTERMEDIATES
				elif "intermediate" in mullionName:
					condition = "INTERMEDIATE"
					intermediatePoints.append([mullionPoint, mullionName])

					if "double" in mullionName or "intermediate-2" in mullionName:
						varient01 = "DOUBLE"
					else: 
						varient01 = "SINGLE"

					#Search for standard lengths in the system config

					for key, standardLength in intermediateStandards.items():
						if abs(mullionLength - standardLength) < standardTol:
							varient02 = key
							break
						else:
							varient02 = "CUSTOM"
				

				# ----------------------------- HORIZONTALS -----------------------------

				elif "sill" in mullionName:

					#Threshold for sill on floor or intermediate sill
					
					if (mullionCenter.Z-levelElevation) > 2.0:
						condition = "SILL INTERMEDIATE"
					else: 
						condition = "SILL"
					
					if "double" in mullionName:
						varient01 = "DOUBLE"
					else: 
						varient01 = "SINGLE"

					for key, standardLength in sillStandards.items():
						if abs(mullionLength - standardLength) < standardTol:
							varient02 = key
							break
						else:
							varient02 = "CUSTOM"

				if condition:

					conditionEntry = [mullion.Id.IntegerValue,
										systemName,
										condition,
										varient01,
										varient02,
										mullionArea,
										mullionRoom, 
										mullionLength,
										None,
										conditionComment]
					conditionsArray.append(conditionEntry)

		allStorefrontMullionsTemp = allStorefrontMullions

		headList = []

		for mullion in allStorefrontMullionsTemp:

			mullionLength = mullion.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()

			if mullionLength > 0 and mullion.LocationCurve:

				mullionName = mullion.Name.lower()
				mullionRoom = mullion.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()
				mullionPoint = mullion.Location.Point
				mullionPoint = XYZ(mullionPoint.X,mullionPoint.Y, 0)
				mullionArea = None

				mullionCurve = mullion.LocationCurve
				mullionCenter = mullionCurve.Evaluate(0.5, True)
				mullionCenter = XYZ(mullionCenter.X, mullionCenter.Y, 0)

				storefrontHostHeight = mullion.Host.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()

				condition = None
				varient01 = None
				varient02 = None

				# Find which area the condition occurs
				for areaName, areaPoints in areaBoundaryPoints.items():
					if PointInPolygon(mullionPoint, areaPoints):
						mullionArea = areaName

				
				mullionElevation = mullion.GetTransform().Origin.Z

				# ----------------------------- ENDS -----------------------------

				# Use sills to find end conditions and test lengths	
				if detectEndConditions:
					if "sill" in mullionName:

						# Check against junctions (wallstarts and posts)
						for i in range(len(junctionPoints)):
							testPoint = junctionPoints[i][0]
							testDist = testPoint.DistanceTo(mullionCenter)
							if testDist < ((mullionLength/2) + 0.33):
								
								condition = "END"
								varient01 = None
								varient02 = None
								conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"

								if "offset" in  mullionName.lower():
									varient01 = "OFFSET"
								elif "center" in  mullionName.lower():
									varient01 = "CENTER"
								elif "double" in  mullionName.lower():
									varient01 = "DOUBLE"

								for key, standardLength in endStandards.items():
									if abs(storefrontHostHeight - standardLength) < standardTol:
										varient02 = key
										break
									else:
										varient02 = "CUSTOM"

								conditionEntry = [mullion.Id.IntegerValue,
												systemName,
												condition,
												varient01,
												varient02,
												mullionArea,
												mullionRoom, 
												storefrontHostHeight,
												None,
												conditionComment]
								conditionsArray.append(conditionEntry)

						# Check against door frames
						for i in range(len(doorFramePoints)): 
								doorFrameName = doorFramePoints[i][1]
								testPoint = doorFramePoints[i][0]
								testDist = testPoint.DistanceTo(mullionCenter)

								# Check if the centerpoint of the panel is within tolerance 
								# to an end conditions
								if testDist < ((mullionLength/2) + 0.33):

									condition = "END"
									varient01 = None
									varient02 = None
									conditionComment = "SEE SYSTEM CONDITIONS FOR ACTUAL LENGTH"
								
									if "offset" in  mullionName.lower():
										if ("mid" in doorFrameName) and ("door" in doorFrameName):
											varient01 = "CENTER"
										else:
											varient01 = "OFFSET"
									elif "center" in  mullionName.lower():
										varient01 = "CENTER"
									elif "double" in  mullionName.lower():
										varient01 = "DOUBLE"

									else:
										print doorFrameName

									for key, standardLength in endStandards.items():
										if abs(storefrontHostHeight - standardLength) < standardTol:
											varient02 = key
											break
										else:
											varient02 = "CUSTOM"

									conditionEntry = [mullion.Id.IntegerValue,
												systemName,
												condition,
												varient01,
												varient02,
												mullionArea,
												mullionRoom, 
												storefrontHostHeight,
												None,
												conditionComment]
									conditionsArray.append(conditionEntry)


				# ----------------------------- HEADS -----------------------------

				# Search for head mullions and chain together if they are continuous
				if "head" in mullionName:
					searchingForChain = True
					searchTol = 0.01
					while searchingForChain:

						foundNeighbor = False
						mullion1Start = mullionCurve.GetEndPoint(0)
						mullion1End = mullionCurve.GetEndPoint(1)
						mullion1Endpoints = [mullion1Start, mullion1End]

						for mullion2 in allStorefrontMullionsTemp:

							if "head" in mullion2.Name.lower() and mullion2 != mullion:
								mullion2Curve = mullion2.LocationCurve
								mullion2Start = mullion2Curve.GetEndPoint(0)
								mullion2End = mullion2Curve.GetEndPoint(1)
								mullion2Endpoints = [mullion2Start, mullion2End]

								for i in range(len(mullion1Endpoints)):
									point1a = mullion1Endpoints[i]
									point1b = mullion1Endpoints[i-1]
									for j in range(len(mullion2Endpoints)):
										point2a = mullion2Endpoints[j]
										point2b = mullion2Endpoints[j-1]
										dist = point1a.DistanceTo(point2a)
										if dist < searchTol:
											angle = AngleThreePoints(point1b, point1a, point2b)
											#print angle
											if abs(angle-180) < searchTol:
												allStorefrontMullions.remove(mullion2)
												mullionCurve = Line.CreateBound(point1b, point2b)

												foundNeighbor = True
												break
							if foundNeighbor:
								break
						if not foundNeighbor:
							searchingForChain = False

					headList.append([mullionCurve, mullion.Id, mullionRoom, mullionArea ])

					condition = "HEAD"
					varient01 = "TYPICAL"
					varient02 = "CUSTOM"


					conditionEntry = [mullion.Id.IntegerValue,
											systemName,
											condition,
											varient01,
											varient02,
											mullionArea,
											mullionRoom, 
											mullionCurve.Length,
											None,
											conditionComment]
					conditionsArray.append(conditionEntry)

		# ----------------------------- DEFLECTION HEADS -----------------------------

		startHeadToMaintainInline = []
		headToMaintainInline = []

		startAndEndIntersections = []

		for head1 in headList:
			mullionCurve = head1[0]				

			mullionStart = mullionCurve.GetEndPoint(0)
			mullionStart = XYZ(mullionStart.X, mullionStart.Y, 0)

			mullionEnd = mullionCurve.GetEndPoint(1)
			mullionEnd = XYZ(mullionEnd.X, mullionEnd.Y, 0)

			mullionEndpoints = [mullionStart, mullionEnd]
			
			endIntersections = []
			startIntersections = []

			headToMaintainInline.append(False)


			#print "---------------------------"
			#print head1[1]

			for i in range(len(mullionEndpoints)):
				pt1 = mullionEndpoints[i]
				pt2 = mullionEndpoints[i-1]

				startNeighbors = []
				endNeighbors = []

				#print str(i) + " -----"

				for head2 in headList:

					if head1 != head2:
						mullion2Curve = head2[0]

						mullion2Start = mullion2Curve.GetEndPoint(0)
						mullion2Start = XYZ(mullion2Start.X, mullion2Start.Y, 0)

						mullion2End = mullion2Curve.GetEndPoint(1)
						mullion2End = XYZ(mullion2End.X, mullion2End.Y, 0)

						mullion2Endpoints = [mullion2Start, mullion2End]
						

						for j in range(len(mullion2Endpoints)):
							pt3 = mullion2Endpoints[j]
							pt4 = mullion2Endpoints[j-1]

							testDist = pt1.DistanceTo(pt3)

							#searches for nearby heads at inline and corners
							if testDist < 0.4:

								#found a neighbor
						
								vect1 = XYZ(pt2.X - pt1.X, pt2.Y - pt1.Y, pt2.Z - pt1.Z)
								vect2 = XYZ(pt4.X - pt3.X, pt4.Y - pt3.Y, pt4.Z - pt3.Z)
								testAngle = ((vect1.AngleTo(vect2)*360)/ (2*math.pi))

								refVector = XYZ(1,0,0)
								
								dot = (vect1.X * vect2.X) + (vect1.Y * vect2.Y)
								det = (vect1.X * vect2.Y) + (vect1.Y * vect2.X)
								testAngle2 = (math.atan2(det,dot)*360)/ (2*math.pi)

								refdot = (vect1.X * refVector.X) + (vect1.Y * refVector.Y)
								refdet = (vect1.X * refVector.Y) + (vect1.Y * refVector.X)
								refAngle = round((math.atan2(refdet,refdot)*360)/ (2*math.pi),3)

								#print testAngle2
								#print refAngle	
								#flipping because the vector angle flips based on orientation
								
								if (abs(refAngle) > 135 or abs(refAngle) < 45) or refAngle == -135 or refAngle == 45:
									testAngle2 = testAngle2*-1
								
								
								if i == 0:
									startIntersections.append([testAngle, headList.index(head2), testAngle2])
									#startNeighbors.append([testAngle, headList.index(headCurve2)])
									#print "Start: " + str(testAngle)

								elif i == 1:
									endIntersections.append([testAngle, headList.index(head2), testAngle2])
									#print "End: " + str(testAngle)



								#endIntersections.append("", testAngle)

			startAndEndIntersections.append([startIntersections, endIntersections])

		for head1 in headList:	

			#-------------Junction testing and offset setting------------------
			headCurveIndex = headList.index(head1)
			curveIntersections = startAndEndIntersections[headCurveIndex]
			
			startAndEndOffsets = [0,0]
			conditionComment = ""

			#print "----------------------------------"
			#print head1[1]

			for index in range(len(curveIntersections)):

				intersectionSet = curveIntersections[index]
				offsetAmount = 0
				fabComments = []


				#listToMaintainInline = startAndEndToMaintainInline[index]
				if len(intersectionSet) == 0:
					offsetAmount = storefrontConfig.currentConfig["headOffsetAtEndCondition"]
					fabComments.append(storefrontConfig.currentConfig["headFabAtEndCondition"])
				#Corner/Inline

				elif len(intersectionSet) == 1:
					
					ang = intersectionSet[0][0]
					rotAng = intersectionSet[0][2]
					#Corner

					if abs(abs(ang) - 90) < 1.0:
						offsetAmount = storefrontConfig.currentConfig["headOffsetAtCornerCondition"]

						if rotAng < 0:
							fabComments.append(storefrontConfig.currentConfig["headFabAtCornerCondition-Right"])
						else:
							fabComments.append(storefrontConfig.currentConfig["headFabAtCornerCondition-Left"])

					#Inline
					elif abs(abs(ang) - 180) < 1.0:
						offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]
						fabComments.append(storefrontConfig.currentConfig["headFabAtInlineCondition"])
					else:
						print "odd angle"
						if rotAng < 0:
							fabComments.append("ODD-RIGHT")
						else:
							fabComments.append("ODD-LEFT")

				#TBone/Inline+Corner
				elif len(intersectionSet) > 1:
					inlineCount = 0
					cornerCount = 0
					cornersList = []
					oddCount = 0

					#Build condition counts to evaluate
					for intNeighbor in intersectionSet:
						ang = intNeighbor[0]

						#Corner
						if abs(abs(ang) - 90) < 1.0:
							cornerCount += 1
							cornersList.append(intNeighbor[2])
						#Inline
						elif abs(abs(ang) - 180) < 1.0:
							inlineCount += 1
						else:
							oddCount += 1


					#Evaluate condition counts

					# Corner & Inline
					if inlineCount == 1 and cornerCount == 1 and oddCount == 0:
						offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]

						# add fab comments for these cordners
						for rotAng in cornersList:
							if rotAng < 0:
								fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Right"])
							else:
								fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Left"])


					# Corner & Corner (TBone)
					elif inlineCount == 0 and cornerCount == 2 and oddCount == 0:
						offsetAmount = storefrontConfig.currentConfig["headOffsetAtTBoneCondition"]
						fabComments.append(storefrontConfig.currentConfig["headFabAtTBoneCondition"])

					# Inline & Corner & Corner (4Way)
					elif inlineCount == 1 and cornerCount == 2 and oddCount == 0:

						#check corner neighbors to see if they have an inline to maintain
						setNeighborToMaintainInline = False

						selfToMaintainInline = headToMaintainInline[headCurveIndex]
						
						#fist check if the current curve should maintain inline

						# If already should maintain inline, set the offset
						if selfToMaintainInline:
							offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]

							# add fabs at corners if needed
							for rotAng in cornersList:
								if rotAng < 0:
									fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Right"])
								else:
									fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Left"])

						else: 

							#check neighbors in the intersection set
							for neighborToCheck in intersectionSet:
								neighborAngle = neighborToCheck[0]
								neighborIndex = neighborToCheck[1]

								#if they are corners, see if they already should maintain inline
								if abs(abs(neighborAngle) - 90) < 1.0: 

									#if they do, consider the current offset a TBone 
									if headToMaintainInline[neighborIndex]:
										offsetAmount = storefrontConfig.currentConfig["headOffsetAtTBoneCondition"]
										fabComments.append(storefrontConfig.currentConfig["headFabAtTBoneCondition"])
										break
																		
									#otherwise consider an inline and set the self and neighbor to True
									else:
										offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]
										headToMaintainInline[headCurveIndex] = True
										setNeighborToMaintainInline = True
										#print "set self to True"

										# add fabs at corners if needed
										fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Right"])
										fabComments.append(storefrontConfig.currentConfig["headFabAtCornerInlineCondition-Left"])

										for neighborToCheck2 in intersectionSet:
											neighborAngle2 = neighborToCheck2[0]
											neighborIndex2 = neighborToCheck2[1]

											if abs(abs(neighborAngle2) - 180) < 1.0: 
												headToMaintainInline[neighborIndex2] = True
												#print "set my neighbor to True"
										break

						

					# Inline with Odd corner
					elif inlineCount == 1 and oddCount > 0:
						offsetAmount = storefrontConfig.currentConfig["headOffsetAtInlineCondition"]

					# Odd corners requires 
					elif inlineCount == 0 and oddCount > 0:
						manualDimension = "Drop error marker and notify user"
						print "odd multi corner"

				#Set the offset
				startAndEndOffsets[index] = offsetAmount
				if index == 1:
					conditionComment += " | "
				conditionComment += (" + ".join(str(e) for e in fabComments))
				
				




			headLength = sum(startAndEndOffsets) + head1[0].Length

			condition = "DEFLECTION BASE"
			varient01 = "TYPICAL"
			varient02 = "CUSTOM"


			conditionEntry = [head1[1],
									systemName,
									condition,
									varient01,
									varient02,
									head1[3],
									head1[2], 
									headLength,
									None,
									conditionComment]
			conditionsArray.append(conditionEntry)




			#----------------------Cutlist Export Configuration----------------------#
			"""
			self.currentConfig["headOffsetAtEndCondition"] = 2.066929/12        #52.5mm
			self.currentConfig["headOffsetAtTBoneCondition"] = -0.0984252/12    #-2.5mm
			self.currentConfig["headOffsetAtCornerCondition"] = 4.2322835/12    #107.5mm
			self.currentConfig["headOffsetAtInlineCondition"] = 2.066929/12     #52.5mm
			self.currentConfig["headOffsetAtFourwayCondition"] = 2.066929/12    #52.5mm
			"""

				

		#TODO: Use empty panels to find closest door on storefront and create condition entry 
		#TODO: Get deflection head condition per storefront centerline length

		"""
		if allDoorsSummary:
			#["LEVEL", "REVIT FAMILY", "REVIT TYPE", "REVIT TYPE COMMENTS", "HOST WALLTYPE", "WIDTH", "CARD READER - COUNT", "TOTAL - COUNT"])
			conditionsArray = [["ELEMENT", "SYSTEM", "CONDITION", "VARIENT 01", "VARIENT 02", "AREA", "ROOM", "LENGTH", "WIDTH", "COMMENT"]]
			for doorLev in sorted(allDoorsSummary.keys()):
				if levelName.lower() in doorLev.lower():
					for doorTypeName in sorted(allDoorsSummary[doorLev].keys()):
						doorFamName = allDoorsSummary[doorLev][doorTypeName][0]
						dtc = allDoorsSummary[doorLev][doorTypeName][1]
						dh = allDoorsSummary[doorLev][doorTypeName][2]
						dw = allDoorsSummary[doorLev][doorTypeName][3]
						dcr = allDoorsSummary[doorLev][doorTypeName][4]
						dc = allDoorsSummary[doorLev][doorTypeName][5]

						conditionEntry = [None,
											systemName,
											doorFamName,
											doorTypeName,
											None,
											None,
											None, 
											storefrontHostHeight,
											None,
											conditionComment]

						conditionsArray.append([doorLev, doorFamName, doorTypeName, dtc, dh, dw, str(dcr), str(dc)])

		"""
		
		for storefrontElevation in allStorefrontWalls:

			panelIds = storefrontElevation.CurtainGrid.GetPanelIds()
			#mullionIds = storefrontElevation.CurtainGrid.GetMullionIds()

			linearGlass = storefrontElevation.Location.Curve.Length

			storefrontElevationID = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
			storefrontSuperType = storefrontElevation.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()


			

			#Panels
			for panelId in panelIds:

				panel = doc.GetElement(panelId)
				panelWidth = panel.get_Parameter(BuiltInParameter.WINDOW_WIDTH).AsDouble()
				panelHeight = panel.get_Parameter(BuiltInParameter.WINDOW_HEIGHT).AsDouble()

				if (panelWidth > 0) and (panelHeight > 0):

					condition = None
					varient01 = None
					varient02 = None

					panelFamily = panel.get_Parameter(BuiltInParameter.ELEM_FAMILY_PARAM).AsValueString()
					panelType = panel.get_Parameter(BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
					panelSF = panelWidth * panelHeight
					panelSizeName = str(panelWidth) + " x " + str(panelHeight)

					#Get panel point and flatten
					panelPoint = panel.GetTransform().Origin
					panelPoint = XYZ(panelPoint.X, panelPoint.Y, 0)

					panelRoomID = panel.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString()

					# Find which area the condition occurs
					panelArea = None
					for areaName, areaPoints in areaBoundaryPoints.items():
						if PointInPolygon(panelPoint, areaPoints):
							panelArea = areaName

					#Default panel position
					panelPositions = []

					# Checking end conditions against junctions (post, wallstart, and door frames)
					juntionsAndDoorFrames = junctionPoints + doorFramePoints

					if "glazed" in panelFamily.lower():
						#print "-----------------------------"
						#print panel.Id

						condition = "GLASS"

						if "double" in panelType.lower():
							varient01 = "DOUBLE"
						else:
							varient01 = "SINGLE"

						varient02 = "CUSTOM"


						panelComment = "EXACT GLASS SIZE! - INCLUDES AMOUNT IN POCKET "

						
						numFoundEndConditions = 0

						#CORRECT PANEL WIDTH + HEIGHT FOR ACTUAL SIZES
						# Add correction for differences between modeling and reality

						glassWidthCorrection = 0
						glassHeightCorrection = 0

						#Ends
						for i in range(len(juntionsAndDoorFrames)):
							testPoint = juntionsAndDoorFrames[i][0]
							testMullionName = juntionsAndDoorFrames[i][1]
							testDist1 = testPoint.DistanceTo(panelPoint)

							if testDist1 < ((panelWidth/2) + (2.1/12)):
								glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]
								numFoundEndConditions += 1 #Found an end condition
								#print storefrontConfig.currentConfig["panelCorrections"]["horizontalEnd"]

						#Intermediates
						for i in range(len(intermediatePoints)):
							testPoint = intermediatePoints[i][0]
							testMullionName = intermediatePoints[i][1]
							testDist2 = testPoint.DistanceTo(panelPoint)

							if testDist2 < ((panelWidth/2) + (1.8/2)):
								glassWidthCorrection += storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]
								numFoundEndConditions += 1 #Found an end condition
								#print storefrontConfig.currentConfig["panelCorrections"]["horizontalIntermediate"]

						#Butt joints
						numButtJoints = 2 - numFoundEndConditions #Glass has 2 ends, if above conditions arent detected, its assumed a butt joint is found
						glassWidthCorrection += (numButtJoints * storefrontConfig.currentConfig["panelCorrections"]["horizontalButtJoint"])

						#print numButtJoints


						#Head and Sill pockets
						glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalSill"]
						glassHeightCorrection += storefrontConfig.currentConfig["panelCorrections"]["verticalHead"]
						

						conditionEntry = [panelId.IntegerValue,
										systemName,
										condition,
										varient01,
										varient02,
										panelArea,
										panelRoomID, 
										panelWidth + glassWidthCorrection,
										panelHeight + glassHeightCorrection,
										panelComment]
						conditionsArray.append(conditionEntry)



		
		print "...SAVE REPORT"
		save_file = SaveFileDialog()
		save_file.FileName  = (projectName + "_CUTLIST REPORT_" + todaysDate.replace("/","")) + ".csv"
		print save_file.FileName
		save_file.Filter = "CSV files (*.csv)|*.csv|Excel Files|*.xls;*.xlsx;*.xlsm"
		save_file.ShowDialog()


		try:
			writeList = []
			writeList.append(["PROJECT NAME", "REPORT AUTHOR", "REPORT DATE"])
			writeList.append([projectName, currentUser, todaysDate])

			writeList.append([" "])
			writeList.append([" "])
			writeList.append(["CONDITIONS"])

			
			with open(save_file.FileName, 'w') as f:
				writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
				for row in conditionsArray:
					writer.writerow(row)
				#  Writing to csv
			os.startfile(save_file.FileName)
		except Exception as inst:
			OutputException(inst)




	if reportType == "takeoff":

		print "...SAVE REPORT"
		save_file = SaveFileDialog()
		save_file.FileName  = (projectName + "_MATERIAL REPORT_" + todaysDate.replace("/","")) + ".csv"
		print save_file.FileName
		save_file.Filter = "CSV files (*.csv)|*.csv|Excel Files|*.xls;*.xlsx;*.xlsm"
		save_file.ShowDialog()


		try:
			writeList = []
			writeList.append(["PROJECT NAME", "REPORT AUTHOR", "REPORT DATE"])
			writeList.append([projectName, currentUser, todaysDate])

			"""
			writeList.append(["STOREFRONT TYPE","LINEAR FT"])
			writeList.append(["Full Height w/ Glass:",linearFull])
			writeList.append(["Full Height @ Door:",linearDoors])
			writeList.append(["Partial Height:",linearPartial])
			writeList.append([" "])

			
			#ProfileSummary
			writeList.append(["PROFILE TYPE","LINEAR FT", "COUNT"])
			for mullionType in mullionExportDict.keys():
				linearMullion = 0
				countMullion = 0
				for entry in mullionExportDict[mullionType].keys():
					linearMullion += mullionExportDict[mullionType][entry]["Length"]
					countMullion += 1
				writeList.append([mullionType, linearMullion, countMullion])
			writeList.append([" "])

			#Glass Summary
			writeList.append(["OTHER","SQUARE FT", "COUNT"])
			writeList.append(["Glass:",areaGlass, countGlass])
			writeList.append(["Infill Panel:",areaInfillPanel, countInfillPanel])
			writeList.append([" "])

			#Door Summary
			writeList.append(["DOOR TYPE", "DOOR FAMILY", "COUNT"])
			for doorType in doorExportDict.keys():
				doorCount = 0
				doorFamilyName = None
				for entry in doorExportDict[doorType].keys():
					doorCount += 1
					doorFamilyName = doorExportDict[doorType][entry]["DoorFamily"]
				writeList.append([doorType, doorFamilyName, doorCount])
			writeList.append([" "])
			writeList.append([" "])
			"""


			if allWallsSummary:
				writeList.append([" "])
				writeList.append([" "])
				writeList.append(["WALLS"])
				writeList.append(["LEVEL", "REVIT WALL TYPE", "REVIT WALL KIND", "LINEAR FT (INCLUDES DOOR WIDTH)"])
				writeList.append([" "])
				for wallLev in sorted(allWallsSummary.keys()):
					if "container" not in wallLev.lower():
						writeList.append([" "])
						for wallType in sorted(allWallsSummary[wallLev].keys()):
							wallKind = allWallsSummary[wallLev][wallType][0]
							wallLength = allWallsSummary[wallLev][wallType][1]
							writeList.append([wallLev, wallType, wallKind, str(wallLength)])

			if allDoorsSummary:
				writeList.append([" "])
				writeList.append([" "])
				writeList.append(["DOORS"])
				writeList.append(["LEVEL", "REVIT FAMILY", "REVIT TYPE", "REVIT TYPE COMMENTS", "HOST WALLTYPE", "WIDTH", "CARD READER - COUNT", "TOTAL - COUNT"])
				for doorLev in sorted(allDoorsSummary.keys()):
					if "container" not in doorLev.lower():
						writeList.append([" "])
						for doorTypeName in sorted(allDoorsSummary[doorLev].keys()):
							doorFamName = allDoorsSummary[doorLev][doorTypeName][0]
							dtc = allDoorsSummary[doorLev][doorTypeName][1]
							dh = allDoorsSummary[doorLev][doorTypeName][2]
							dw = allDoorsSummary[doorLev][doorTypeName][3]
							dcr = allDoorsSummary[doorLev][doorTypeName][4]
							dc = allDoorsSummary[doorLev][doorTypeName][5]
							writeList.append([doorLev, doorFamName, doorTypeName, dtc, dh, dw, str(dcr), str(dc)])

			if allSpecialObjectSummary:
				writeList.append([" "])
				writeList.append([" "])
				writeList.append(["SPECIALTY ITEMS"])
				writeList.append(["LEVEL", "REVIT FAMILY", "REVIT TYPE", "REVIT TYPE COMMENTS", "TOTAL - COUNT"])
				for fiLevel in sorted(allSpecialObjectSummary.keys()):
					if "container" not in fiLevel.lower():
						writeList.append([" "])
						for fiTypeName in sorted(allSpecialObjectSummary[fiLevel].keys()):
							fiFamilyName = allSpecialObjectSummary[fiLevel][fiTypeName][0]
							fiTypeComments = allSpecialObjectSummary[fiLevel][fiTypeName][1]
							fiCount = allSpecialObjectSummary[fiLevel][fiTypeName][2]
							writeList.append([fiLevel, fiFamilyName, fiTypeName, fiTypeComments, str(fiCount)])

			
			with open(save_file.FileName, 'w') as f:
				writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
				for row in writeList:
					writer.writerow(row)
				#  Writing to csv
			os.startfile(save_file.FileName)
		except Exception as inst:
			OutputException(inst)


	"""
	elif reportType == "cutlist":

		profileDict = GetProfileDict("I-Profile-Storefront-Mullion")

		#Storefront Conditions
		##  Office Front Singe
		##  Office Front Double 
		##  Cross Wall Single
		##  Cross Wall Double
		##  4 Way
		##  3 way
		##  2 Way
		##  Wall Start
		##  Sliding Door
		##  Swing Door

		#collect posts & wall starts
		#get their center points
		#detect intersection onto other curtain wall locaiton lines
		#collect intersection and walltype data
		#compare to map of intersection types and tally them up
		

		
		try:
			print "...SAVE CUTLIST"
			save_file = SaveFileDialog()
			save_file.FileName  = (projectName + "_" + levelName + "_CUT LIST_" + todaysDate.replace("/","")) + ".csv"
			print save_file.FileName
			save_file.Filter = "CSV files (*.csv)|*.csv|Excel Files|*.xls;*.xlsx;*.xlsm"
			save_file.ShowDialog()
		except:
			pass

		writeList = []
		writeList.append(["PROJECT NAME", "LEVEL NAME", "REPORT AUTHOR", "REPORT DATE"])
		writeList.append([projectName, levelName, currentUser, todaysDate])

		# Iterate through the dictionary and create cutlist for verticals
		writeList.append([" "])
		writeList.append(["VERTICALS"])
		writeList.append(["PROFILE TYPE","PART NUMBER", "CUT LENGTH", "COUNT"])

		# Write posts here.
		#writeList.append(["Post","1501 x 2 (solid)", frameHeadHeight, int(len(fullPostPoints)/2)])
		#writeList.append(["Post","1501 x 2 (solid)", frameHeadHeight-frameSillHeight, int(len(partialPostPoints)/2)])

		# Write the rest of ther vertical here
		for key in profileDict.keys():
			uniqueLengths = [[],[]]
			for i in range(len(profileDict[key][1])):
				partNumber = profileDict[key][0]
				length = profileDict[key][1][i]
				assemId = profileDict[key][2][i]
				frameId = profileDict[key][3][i]

				if "Head" not in key and "Sill" not in key and "Post" not in key:
					if length not in uniqueLengths[0]:
						uniqueLengths[0].append(length)
						uniqueLengths[1].append(1)
					else:
						uniqueLengths[1][uniqueLengths[0].index(length)] += 1
			for i in range(len(uniqueLengths[0])):
				writeList.append([key, partNumber, uniqueLengths[0][i], uniqueLengths[1][i]])


		# Iterate through the dictionary and create cutlist for horizontals
		writeList.append([" "])
		writeList.append(["HORIZONTALS "])
		writeList.append(["PROFILE TYPE","PART NUMBER", "CUT LENGTH", "ASSEMBLY ID", "FRAME ID", "NOTE"])
		for key in profileDict.keys():
			for i in range(len(profileDict[key][1])):
				if "Head" in key or "Sill" in key:
					partNumber = profileDict[key][0]
					length = profileDict[key][1][i]
					assemId = profileDict[key][2][i]
					frameId = profileDict[key][3][i]
					note = profileDict[key][4][i]
					writeList.append([key, partNumber, length, assemId, frameId, note])

		writeList.append([" "])
		writeList.append(["GLASS "])
		writeList.append(["X DIM","Y DIM", "AREA", "ASSEMBLY ID", "FRAME ID", "NOTE"])
		for glass in glassList:
			writeList.append(glass)

		try:
			with open(save_file.FileName, 'w') as f:
				writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
				for row in writeList:
					writer.writerow(row)
		except Exception as inst:
			OutputException(inst)
		try:
			# initialize writing to csv
			os.startfile(save_file.FileName)
		except Exception as inst:
			OutputException(inst)
	print "FINISHED"
	"""

def storefront_extract():

	#TODO:  Implement rpw transactions, collectors, and filters. 

	version = __revit__.Application.VersionNumber.ToString()

	storefrontFull = []
	storefrontPartial = []
	selectedLevels = []
	storefrontFullLines = []
	storefrontPartialLines = []
	interiorWallsLines = []

	doc = __revit__.ActiveUIDocument.Document

	storefrontViewTypeName = "Laser Layout"
	storefrontViewUse = "Laser Layout"
	storefrontViewScale = 96

	subCatIdList = []
	lineSubCatsToEnsure = [["WW_StorefrontFull",Autodesk.Revit.DB.Color(0,60,175),8],
						   ["WW_StorefrontPartial",Autodesk.Revit.DB.Color(0,200,0),8],
						   ["WW_InteriorWall",Autodesk.Revit.DB.Color(100,100,100),4],
						   ["WW_InteriorWallEdge",Autodesk.Revit.DB.Color(200,100,100),3],
						   ["WW_RoomBoundary",Autodesk.Revit.DB.Color(255,0,0),2],
						   ["WW_FloorEdge",Autodesk.Revit.DB.Color(100,100,100),2],
						   ["WW_ExistingConditions",Autodesk.Revit.DB.Color(50,50,50),5],
						   ["WW_DeskOutlines",Autodesk.Revit.DB.Color(0,60,175),2],
						   ["WW_StorefrontMullions",Autodesk.Revit.DB.Color(0,60,175),2],
						   ["WW_ControlLines",Autodesk.Revit.DB.Color(255,0,0),5]]

	# Load configuration object  ---------------------------------------------------------------
	storefrontConfig = storefront_options()
	storefrontConfig.storefront_load_families(True)

	# Get family dict object
	familyDict = storefrontConfig.currentConfig["families"]

	# Get elements from ec model ---------------------------------------------------------------
	selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id
	

	# Get all the elements needed in main doc ---------------------------------------------------------------
	allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
	allViews = GetAllElements(doc, BuiltInCategory.OST_Views, Autodesk.Revit.DB.View)
	allViewPlans = GetAllElements(doc, BuiltInCategory.OST_Views, Autodesk.Revit.DB.ViewPlan)

	# Filter by name ---------------------------------------------------------------
	storefrontFull = FilterElementsByName(doc, allWalls,["Storefront","Full"], False)
	storefrontPartial = FilterElementsByName(doc, allWalls,["Storefront","Partial"], False)
	interiorWalls = FilterElementsByName(doc, allWalls,["Storefront","Storefront"], True)
	laserViewPlan = FilterElementsByName(doc, allViewPlans,["Laser","Layout"], False)

	if not laserViewPlan:
		laserViewPlan = FilterElementsByName(doc, allViewPlans,["Working","Working"], False)

	# Makes sure no stacked walls are included  ---------------------------------------------------------------
	tempList = []
	for wallId in interiorWalls:
		wall = doc.GetElement(wallId)
		if not wall.IsStackedWallMember:
			tempList.append(wallId)
	interiorWalls = tempList
	
	#Extract curves from elements ---------------------------------------------------------------

	storefrontFullLines = GetWallLocationCurves(doc, storefrontFull)
	storefrontPartialLines = GetWallLocationCurves(doc, storefrontPartial)
	interiorWallsLines = GetWallLocationCurves(doc, interiorWalls)

	#Split curves as they are intersected ---------------------------------------------------------------

	allLines  = storefrontFullLines + storefrontPartialLines + interiorWallsLines

	temp = []
	for line in storefrontFullLines:
		intersections = []
		for testLine in allLines:
			if testLine != line:
				intersection = RevitCurveCurveIntersection(line, testLine, filterIntersectionType="Overlap")
				if intersection:
					intersections.append(intersection)

		temp += RevitSplitLineAtPoints(line, intersections)
	storefrontFullLines = temp

	temp = []
	for line in storefrontPartialLines:
		intersections = []
		for testLine in allLines:
			if testLine != line:
				intersection = RevitCurveCurveIntersection(line, testLine, filterIntersectionType="Overlap")
				if intersection:
					intersections.append(intersection)

		temp += RevitSplitLineAtPoints(line, intersections)
	storefrontPartialLines = temp

	#Setup line syles  ---------------------------------------------------------------
	subCatIdList = SetupLineStyles(lineSubCatsToEnsure)
	existingViewsFound = False

	levelInst = doc.GetElement(selectedLevel)
	levelName = None
	for p in levelInst.Parameters:
		if p.Definition.Name == "Name":
			levelName = p.AsString()

	#Check if theres an existing view  ---------------------------------------------------------------
	for viewId in allViews:
		viewInDoc = doc.GetElement(viewId)
		if levelName + " Laser Layout" == viewInDoc.Name:
			existingViewsFound = True
			viewToUpdate = viewId
			break
		 
	if existingViewsFound:
		with rpw.db.Transaction("Clear Laser Layout View"):
			print levelName + "...CLEARING VIEW..."
			DeleteElementsInView(viewToUpdate, BuiltInCategory.OST_Lines, optionalKeyword="Detail Lines")
			#DeleteElementsInView(viewToUpdate, BuiltInCategory.OST_DetailComponents)
			#DeleteElementsInView(viewToUpdate, BuiltInCategory.OST_GenericAnnotation)
	

	#Make/Update view ---------------------------------------------------------------
	with rpw.db.Transaction("Make Laser Layout View"):
		viewFamilyTypes = FilteredElementCollector(doc).OfClass(ViewFamilyType)
		viewTypeToMake = None
		foundViewFamilyType = False #default

		#check to see if a viewfamilytype already exists
		vftName = None
		for vft in viewFamilyTypes:
			if version == "2016" or version == "2017":
				vftName = vft.Parameter[BuiltInParameter.ALL_MODEL_TYPE_NAME].AsString()
			elif version == "2015":
				for p in vft.Parameters:
					if p.Definition.Name == "Type Name":
						vftName = p.AsString()

			if storefrontViewTypeName == vftName:
				viewTypeToMake = vft
				foundViewFamilyType = True
				break

		# if not make one
		if not foundViewFamilyType:
			for i in viewFamilyTypes:
				if i.ViewFamily == ViewFamily.FloorPlan:
					viewTypeToMake = i.Duplicate(storefrontViewTypeName)
					break
		if levelName:
			if not existingViewsFound:
				print levelName + "...CREATING VIEW..."
				planViewMake = ViewPlan.Create(doc, viewTypeToMake.Id, selectedLevel)
				planViewMake.Name = levelName + " Laser Layout"
				viewToUpdate = planViewMake.Id
				planViewMake.ViewTemplateId = doc.GetElement(laserViewPlan[0]).ViewTemplateId
			
			print levelName + "...CREATING LAYOUT..."
			#Draw curves in view
			DrawCurvesInView(viewToUpdate, storefrontFullLines, subCatIdList[0])
			DrawCurvesInView(viewToUpdate, storefrontPartialLines, subCatIdList[1])
			DrawCurvesInView(viewToUpdate, interiorWallsLines, subCatIdList[2])

			print levelName + "...DONE"
			
def storefront_split_wall():

	from rpw.ui.forms import Label, ComboBox, Separator, Button, FlexForm, Console

	tol = 0.1
	standardSizes = [4.0, 3.0, 2.0, 1.0] #Glass sizes
	fixed_nib_wall_imperial = 6.0/12
	fixed_nib_wall_metric = 5.90551/12
	leftoverTol = 0.35  #Nib wall length
	
	storefrontConfig = storefront_options()
	currentConfig = storefrontConfig.currentConfig
	selectedSystem = currentConfig["currentSystem"]
	postWidth = currentConfig["postWidth"]
	oneByWidth = currentConfig["oneByWidth"]
	

	currentView = uidoc.ActiveView
	currentLevel = currentView.GenLevel
	levelName = currentLevel.Name

	# collect wall type information for a form to select which one to use.
	# also select whether or not the split is fixed distance or optimized.
	wallTypesList = {}
	splitTypes = storefrontConfig.splitTypeOptions
					
	selectedWallType = None
	allWallTypes = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.WallType)
	allWallTypes += GetAllElements(doc, BuiltInCategory.OST_StackedWalls, Autodesk.Revit.DB.WallType)
	for wallTypeId in allWallTypes:
		wallType = doc.GetElement(wallTypeId)
		wallTypeFamilyName = None
		wallTypeTypeName = None
		if version == "2016" or version == "2017":
			wallTypeFamilyName = wallType.Parameter[BuiltInParameter.ALL_MODEL_FAMILY_NAME].AsString()
			wallTypeTypeName = wallType.Parameter[BuiltInParameter.ALL_MODEL_TYPE_NAME].AsString()
		elif version == "2015":
			for p in wallType.Parameters:
				if p.Definition.Name == "Family Name":
					wallTypeFamilyName = p.AsString()
				if p.Definition.Name == "Type Name":
					wallTypeTypeName = p.AsString()
		wallTypesList[wallTypeFamilyName + " - " + wallTypeTypeName] = wallTypeId


	# get default values if previously selected
	if currentConfig["splitWallType"] and currentConfig["splitOffset"]:
		if currentConfig["splitWallType"] in wallTypesList:
			defaultValues = [currentConfig["splitWallType"], currentConfig["splitOffset"]]
		else:
			defaultValues = [wallTypesList.keys()[0], currentConfig["splitOffset"]]
	else: 
		defaultValues = [wallTypesList.keys()[0], keys.keys()[0]]

	components = [Label('SPLIT OPTIONS'),
					Separator(),
					ComboBox("combobox1", wallTypesList, default=defaultValues[0]),
					Label('NIB WALLTYPE'),
					ComboBox("combobox2", splitTypes, default=defaultValues[1]),
					Label('SPLIT METHOD'),
					Button('Go')]

	form = FlexForm("Storefront Tools V3", components)
	form.show()

	if not form.values:
		sys.exit()
	else:
		selectedWallType = form.values["combobox1"]
		selectedSplitOffset = float(form.values["combobox2"])

	# user settings into a dict
	config = {"splitWallType": wallTypesList.keys()[wallTypesList.values().index(selectedWallType)],
					"splitOffset" : splitTypes.keys()[splitTypes.values().index(selectedSplitOffset)]}
	
	#save selected system
	storefrontConfig.storefront_save_config(user_configs=config)
	
	#get elements
	walls = GetElementsInView(BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView.Id)
	walls = FilterElementsByLevel(doc, walls, currentLevel.Id)
	storefrontWalls = FilterElementsByName(doc, walls,["Storefront","Storefront"], False)
	gypWalls = FilterElementsByName(doc, walls,["Storefront","Storefront"], True)

	#allWalls = storefrontWalls + gypWalls
	intersectionPoints = RemoveDuplicatePoints(FindWallIntersections(walls))
	currentSelected = uidoc.Selection.GetElementIds()
	with rpw.db.Transaction("Create Nib") as tx: 
		for id in currentSelected:
			inst = doc.GetElement(id)
			if inst.Category.Name == "Walls":
				instName = None
				topConstraint = None
				unconnectedHeight = None
				baseOffset = None
				topOffset = None
				botConstraint = currentLevel.Id
				try:
					instName = inst.Name.lower()
				except:
					for p in inst.Parameters:
						if p.Definition.Name == "Name":
							instName = p.AsString().lower()
				if "storefront" not in instName:
					continue
				else:
					for p in inst.Parameters:
						if p.Definition.Name == "Top Constraint":
							topConstraint = p.AsElementId()
						if p.Definition.Name == "Unconnected Height":
							unconnectedHeight = p.AsDouble()
						if p.Definition.Name == "Top Offset":
							topOffset = p.AsDouble()
					
					#check to see which ends are naked
					instLine = inst.Location.Curve
					start = instLine.GetEndPoint(0)
					end = instLine.GetEndPoint(1)
					startOverlap = False
					endOverlap = False
					if intersectionPoints:
						for point in intersectionPoints:
							if point.DistanceTo(start) < tol:
								startOverlap = True
							elif point.DistanceTo(end) < tol:
								endOverlap = True
							if startOverlap and endOverlap:
								break
					

					#if only one end is touching other walls
					if startOverlap == False or endOverlap == False:
						nibWall = None
						nibWalls = []
						offset = 0
						lengthAdjust = (0.5 * postWidth) + oneByWidth
						length = instLine.Length - lengthAdjust
						leftover = length%(standardSizes[0] + oneByWidth)
						numPanels = math.floor(length / (standardSizes[0] + oneByWidth))
						
						if selectedSplitOffset == "OPTIMIZED":
							#if optimized split
							if leftover > leftoverTol:
								lastPanelSize = 0
								for size in standardSizes[1:]:
									if leftover - leftoverTol >= (size + oneByWidth):
										lastPanelSize = standardSizes[standardSizes.index(size)]
										break
								offset = lengthAdjust + numPanels*standardSizes[0] + (numPanels)*oneByWidth + lastPanelSize + int(lastPanelSize > 0)*oneByWidth
							else:
								offset = lengthAdjust + (numPanels-1)*standardSizes[0] + standardSizes[1] + (numPanels)*oneByWidth
						else:
							#if fixed distance split
							offset = instLine.Length - selectedSplitOffset  
						

						if startOverlap or (startOverlap == endOverlap):
							newPoint = XYZ(((end.X-start.X)*(offset/(length + lengthAdjust)))+start.X,((end.Y-start.Y)*(offset/(length + lengthAdjust)))+start.Y, start.Z)
							inst.Location.Curve = Line.CreateBound(start, newPoint)
							nibWallLine = Line.CreateBound(newPoint,end)

							end = newPoint

							nibWalls.append(Wall.Create(doc, nibWallLine, currentLevel.Id, False))
							doc.Regenerate()

						if endOverlap or (startOverlap == endOverlap):
							newPoint = XYZ(((start.X-end.X)*(offset/(length + lengthAdjust)))+end.X,((start.Y-end.Y)*(offset/(length + lengthAdjust)))+end.Y, end.Z)
							inst.Location.Curve = Line.CreateBound(newPoint, end)                  

							nibWallLine = Line.CreateBound(newPoint,start)

							start = newPoint

							nibWalls.append(Wall.Create(doc, nibWallLine, currentLevel.Id, False))
							doc.Regenerate()

						if nibWalls:

							for nibWall in nibWalls:
								nibWall.WallType = doc.GetElement(selectedWallType)
								nibTopConstraint = nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId()
								

								#nibWall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(topOffset)
								if topConstraint.IntegerValue == botConstraint.IntegerValue:
									nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId(-1))
								else:
									nibWall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(topConstraint)


								for p in nibWall.Parameters:
									if p.Definition.Name == "Location Line":
										p.Set(0)
									if p.Definition.Name == "Unconnected Height" and topConstraint.IntegerValue == -1:
										p.Set(unconnectedHeight)

								doc.Regenerate()
								if topConstraint.IntegerValue == botConstraint.IntegerValue:
									nibWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(topOffset)



													

					else:
						continue

def storefront_generate():
	"""
	Generates curtain wall on top of 
	existing basic walls.
	"""

	from pyrevit import script

	tol = 0.001

	version = __revit__.Application.VersionNumber.ToString()
	uidoc = __revit__.ActiveUIDocument
	doc = uidoc.Document
	currentView = uidoc.ActiveView

	storefrontFull = []
	storefrontPartial = []
	selectedLevels = []
	storefrontFullLines = []
	storefrontPartialLines = []
	interiorWallsLines = []
	interiorWallsLinesEdges = []
	selectedDoors = []
	selectedRooms = []
	selectedFloors = []

	ecModelInst = None
	docEC = None
	ecTransform = None

	allWallsEC = []
	allLevelsEC = []
	allColumnsEC = []
	wallsLinesEdgesEC = []
	selectedLevelsEC = []
	selectedWallsEC = []
	selectedColumnsEC = []
	wallsLinesEdgesEC = []


	distTol = 0.5 
	angleTol = 0.01
	absoluteTol = 0.001

	minPanelWidth = 1.0

	docLoaded = RevitLoadECDocument()
	docEC = docLoaded[0]
	ecTransform = docLoaded[1]

	mrTimer = Timer()


	######################################################################
	#                 Collects all elements in a view                    #
	######################################################################

	selectedLevel = __revit__.ActiveUIDocument.ActiveView.GenLevel.Id
	selectedLevelInst = doc.GetElement(selectedLevel)

	currentSelected = list(uidoc.Selection.GetElementIds())
	selectedStorefront = []

	allWalls = GetAllElements(doc, BuiltInCategory.OST_Walls, Autodesk.Revit.DB.Wall, currentView=True)
	allColumns = GetAllElements(doc, BuiltInCategory.OST_Columns, Autodesk.Revit.DB.FamilyInstance, currentView=True)
	allColumns += GetAllElements(doc, BuiltInCategory.OST_StructuralColumns, Autodesk.Revit.DB.FamilyInstance, currentView=True)

	interiorWalls = FilterElementsByName(doc, allWalls,["Storefront","Storefront"], True)

	if currentSelected:
		for id in currentSelected:
			inst = doc.GetElement(id)
			if inst.Category.Name == "Walls":
				instName = None
				try:
					instName = inst.Name.lower()
				except:
					for p in inst.Parameters:
						if p.Definition.Name == "Name":
							instName = p.AsString().lower()
				if "storefront" in instName:
					if "full" in instName:
						storefrontFull.append(id)
					elif "partial" in instName:
						storefrontPartial.append(id)
	else:

		storefrontFull = FilterElementsByName(doc, allWalls,["Storefront","Full"], False)
		storefrontPartial = FilterElementsByName(doc, allWalls,["Storefront","Partial"], False)
	
	#Collect existing storefront curtain walls and check their Marks to ensure they incrememt. 
	startingAssembyId = 0
	storefrontWallsInView = rpw.db.Collector(of_class='Wall', 
											view=currentView, 
											where=lambda x: str(x.WallType.Kind) == "Curtain")
	tempList = []
	for storefrontInView in storefrontWallsInView:
		mark = storefrontInView.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()
		if mark:
			tempList.append(int(mark[mark.index("-")+1:]))
	if tempList:
		sortedList = sorted(tempList)
		startingAssembyId = sortedList[-1]


	tempList = []
	#Makes sure no stacked walls are included.
	for wallId in interiorWalls:
		wall = doc.GetElement(wallId)
		if not wall.IsStackedWallMember:
			tempList.append(wallId)
	interiorWalls = tempList


	#Sort lists by level
	storefrontFull = FilterElementsByLevel(doc, storefrontFull, selectedLevel)
	storefrontPartial = FilterElementsByLevel(doc, storefrontPartial, selectedLevel)
	interiorWalls = FilterElementsByLevel(doc, interiorWalls, selectedLevel)
	selectedColumns = FilterElementsByLevel(doc, allColumns, selectedLevel)

	if docEC:
		levelElevationEC = None 
		for p in selectedLevelInst.Parameters:
			if p.Definition.Name == "Elevation":
				levelElevationEC = p.AsDouble()
		selectedWallsEC = FilterElementsByLevel(docEC, allWallsEC, levelElevationEC)
		selectedColumnsEC = FilterElementsByLevel(docEC, allColumnsEC, levelElevationEC)
		wallsLinesEdgesEC = GetWallEdgeCurves(docEC, selectedWallsEC, ecTransform)
		columnsLinesEdgesEC = GetColumnEdgeCurves(docEC, selectedColumnsEC, ecTransform)

	interiorWallsLinesEdges = GetWallEdgeCurves(doc, interiorWalls, None)
	columnsLinesEdges = GetColumnEdgeCurves(doc, selectedColumns)


	levelElevation = selectedLevelInst.Elevation

	#############################################
	 #                  Prep                    #
	#############################################       

	# Load configuration object
	storefrontConfig = storefront_options()
	storefrontConfig.storefront_set_config()

	systemName = storefrontConfig.currentConfig["currentSystem"]

	storefrontPaneWidth = storefrontConfig.currentConfig["storefrontPaneWidth"]
	storefrontSpacingType = storefrontConfig.currentConfig["spacingType"]

	mullionDict = GetMullionTypeDict()
	panelTypeDict = GetWindowTypeDict()
	#doorDict = storefrontConfig.doorDict
	doorDict = storefrontConfig.currentConfig["systemDoors"]
	wallTypeDict = GetWallTypeDict()
	wallDoorHostDict = GetDoorDictByWallHost()

	#Ensure walltypes are loaded
	if not "I-Storefront-"+ systemName in wallTypeDict.keys():
		Autodesk.Revit.UI.TaskDialog.Show ("ERROR", "Make sure you selected/loaded the correct partition system. Check your wall types.")
		sys.exit()

	
	#TODO: verify mullions in project, if not then run the load tool.

	#Profile widths
	systemPostWidth = doc.GetElement(mullionDict[systemName+"_Post"]).get_Parameter(BuiltInParameter.CUST_MULLION_THICK).AsDouble()

	systemDoorFrame = doc.GetElement(mullionDict[systemName+"_DoorFrame"])
	systemDoorFrameWidth = systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
	systemDoorFrameWidth += systemDoorFrame.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

	systemOneBy = doc.GetElement(mullionDict[systemName+"_OneBy"])
	systemOneByWidth = systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
	systemOneByWidth += systemOneBy.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()


	wallTypeCW = wallTypeDict["I-Storefront-"+systemName]

	progressIndex = 0.0

	#############################################
	 #              Wrap & Chain                #
	#############################################
	"""
	Takes walls that are inline and makes them a single
	wall element so that you dont get segmented walls that
	are supposed to be a single continuous elevation.
	"""
	assemblyId = startingAssembyId
	storefrontElevations = []
	storefrontFullAndPartial = []

	for wallId in storefrontFull:
		storefrontFullAndPartial.append([wallId,"Full"])
	for wallId in storefrontPartial:
		storefrontFullAndPartial.append([wallId,"Partial"])

	#--------------Make SF Objects---------------#
	for item1 in storefrontFullAndPartial:

		wallId1 = item1[0]
		wallStorefrontType1 = item1[1]

		wall1 = doc.GetElement(wallId1)
		wall1LocationCurve = wall1.Location.Curve
		
		wallDoors = []
		wallHostIds = [wallId1]

		if wallId1 in wallDoorHostDict.keys():
			wallDoors = wallDoorHostDict[wallId1]
		

		#--------------Chain Searching--------------#

		#Find neighbors and chain them if they are in-line.
		searchingForChain = True
		while searchingForChain:

			foundNeighbor = False
			wall1Start = wall1LocationCurve.GetEndPoint(0)
			wall1End = wall1LocationCurve.GetEndPoint(1)
			wall1Endpoints = [wall1Start, wall1End]

			for item2 in storefrontFullAndPartial:

				wallId2 = item2[0]
				wallStorefrontType2 = item2[1]

				if wallId1 != wallId2 and wallStorefrontType1 == wallStorefrontType2:
					wall2 = doc.GetElement(wallId2)
					wall2LocationCurve = wall2.Location.Curve
					wall2Start = wall2LocationCurve.GetEndPoint(0)
					wall2End = wall2LocationCurve.GetEndPoint(1)
					wall2Endpoints = [wall2Start, wall2End]
					for i in range(len(wall1Endpoints)):
						point1a = wall1Endpoints[i]
						point1b = wall1Endpoints[i-1]
						for j in range(len(wall2Endpoints)):
							point2a = wall2Endpoints[j]
							point2b = wall2Endpoints[j-1]
							dist = point1a.DistanceTo(point2a)
							if dist < absoluteTol:
								angle = AngleThreePoints(point1b, point1a, point2b)
								#print angle
								if abs(angle-180) < absoluteTol:
									wallHostIds += [wallId2]
									storefrontFullAndPartial.remove(item2)
									if wallId2 in wallDoorHostDict.keys():
										wallDoors += wallDoorHostDict[wallId2]
									wall1LocationCurve = Line.CreateBound(point1b, point2b)
									foundNeighbor = True
									break
				if foundNeighbor:
					break
			if not foundNeighbor:
				searchingForChain = False

		#--------------Create SF Object--------------#
		assemblyId += 1

		if wallStorefrontType1 == "Full":
			sillH = storefrontConfig.currentConfig["fullSillHeight"]
		elif wallStorefrontType1 == "Partial":
			if storefrontConfig.currentConfig["hasLowerInfill"]:
				sillH = storefrontConfig.currentConfig["fullSillHeight"]
			else:
				sillH = storefrontConfig.currentConfig["partialSillHeight"]


		headH = storefrontConfig.currentConfig["headHeight"]
		sfe = StorefrontElevation(wallHostIds, wall1LocationCurve, wallStorefrontType1, assemblyId, sillH, headH, systemName)
		#Doors
		if wallDoors:
			sfe.Doors = wallDoors
		storefrontElevations.append(sfe)


	#############################################
	 #                  Build                   #
	#############################################

	print "RUNNING...DO NOT CLOSE WINDOW..."

	with rpw.db.TransactionGroup("Convert Wall", assimilate=True) as tg:

		#Adjust any parameters to the walltype before creation if needed.
		with rpw.db.Transaction("Adjust CW Parameters") as tx:
			SupressErrorsAndWarnings(tx)

			
			wtCW = doc.GetElement(wallTypeCW)
			if storefrontConfig.currentConfig["deflectionHeadType"] == 2:
				wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[systemName+"_DeflectionHead-2"])
			elif storefrontConfig.currentConfig["deflectionHeadType"] == 1:
				wtCW.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mullionDict[systemName+"_DeflectionHead-1"])

		for storefrontObject in storefrontElevations: 


			#pyrevit progress bar
			progressIndex += 1
			output = script.get_output()

			output.update_progress(progressIndex, len(storefrontElevations))

			hostElement = doc.GetElement(storefrontObject.HostElementIds[0])
			storefrontType = storefrontObject.SuperType

			baseConstraint = hostElement.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()

			locLine = storefrontObject.HostLine
			locLineStart = locLine.GetEndPoint(0)
			locLineEnd = locLine.GetEndPoint(1)

			gridIntersectionPostPoints = []

			wallHostId = storefrontObject.HostElementIds[0]
			wtName = doc.GetElement(wallHostId).Name

			newWall = None

			if str(hostElement.WallType.Kind) == "Basic": 

				#############################################
				#                  Checks                   #
				#############################################

			   #------------Interior Walls Edges------------#

				locLine = storefrontObject.HostLine
				locLineStart = locLine.GetEndPoint(0)
				locLineEnd = locLine.GetEndPoint(1)

				for intWallLine in interiorWallsLinesEdges:
					intersection = RevitCurveCurveIntersection(locLine,intWallLine)

					if intersection:
						distToEnd = intersection.DistanceTo(locLineEnd) 
						distToStart = intersection.DistanceTo(locLineStart) 

						#If intersection is at the ends
						if distToEnd < distTol:
							storefrontObject.EndCondition = "OnGyp"
							# If intersection is not at the surface of the edges of interior walls
							if distToEnd > absoluteTol:
								storefrontObject.Line = Line.CreateBound(locLineStart, intersection)

						elif distToStart < distTol:
							storefrontObject.StartCondition = "OnGyp"
							if distToStart > absoluteTol:
								storefrontObject.Line = Line.CreateBound(intersection, locLineEnd)

				#----------Interior Walls Midspans-----------#
				for intWallId in interiorWalls:
					intWall = doc.GetElement(intWallId)
					intWallLine = intWall.Location.Curve
					intersection = RevitCurveCurveIntersection(locLine,intWallLine)
					if intersection:
						distToEnd = intersection.DistanceTo(locLineEnd) 
						distToStart = intersection.DistanceTo(locLineStart) 
						#If intersection is at the ends
						if distToEnd > distTol and distToStart > distTol:
							gridIntersectionPostPoints.append(intersection)




				#------------------EC Walls------------------#

				locLine = storefrontObject.HostLine
				locLineStart = locLine.GetEndPoint(0)
				locLineEnd = locLine.GetEndPoint(1)
				obstructionEdges = columnsLinesEdges
				if docEC:
					obstructionEdges += columnsLinesEdgesEC
					obstructionEdges += wallsLinesEdgesEC
				if obstructionEdges:
					for obstructionLine in obstructionEdges:
						obstLineElevation = obstructionLine.GetEndPoint(0).Z
						locLineStart = XYZ(locLineStart.X, locLineStart.Y, obstLineElevation)
						locLineEnd = XYZ(locLineEnd.X, locLineEnd.Y, obstLineElevation)
						locLineFlat = Line.CreateBound(locLineStart, locLineEnd)
						intersection = RevitCurveCurveIntersection(locLineFlat,obstructionLine)
						if intersection:
							#ERROR: Hit Existing Condition
							if intersection.DistanceTo(locLineEnd) < distTol:
								storefrontObject.EndCondition = "OnObstruction"
							elif intersection.DistanceTo(locLineStart) < distTol:
								storefrontObject.StartCondition = "OnObstruction"

				
				####-------Storefront Intersections-------####

				locLine = storefrontObject.HostLine
				locLineStart = locLine.GetEndPoint(0)
				locLineEnd = locLine.GetEndPoint(1)


				#---------------Find Neighbors---------------#
				#print storefrontObject.HostElementIds              
				for neighbor in storefrontElevations:

					if neighbor != storefrontObject:
						neighborLocLine = neighbor.HostLine
						neighborLocLineStart = neighborLocLine.GetEndPoint(0)
						neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
						intersection = RevitCurveCurveIntersection(locLine,neighborLocLine)
						
						if intersection:
							point1 = None
							intersectionTypeOnNeighbor = None

							#Check where the intersection is occuring on the neighbor
							if intersection.DistanceTo(neighborLocLineStart) < distTol:
								intersectionTypeOnNeighbor = "Start"
								point1 = neighborLocLineEnd
							elif intersection.DistanceTo(neighborLocLineEnd) < distTol:
								intersectionTypeOnNeighbor = "End"
								point1 = neighborLocLineStart
							else:
								intersectionTypeOnNeighbor = "Middle"
								point1 = neighborLocLineEnd

							#Check if intersection is at the start point or end point or middle
							if intersection.DistanceTo(locLineStart) < tol:
								angle = AngleThreePoints(locLineEnd, intersection, point1)
								storefrontObject.StartNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

							elif intersection.DistanceTo(locLineEnd) < tol:
								angle = AngleThreePoints(locLineStart, intersection, point1)
								storefrontObject.EndNeighbors.append([neighbor.AssemblyID, neighbor.SuperType, angle, intersectionTypeOnNeighbor, intersection])

							else:
								#Interesection isnt ocurring at the ends.
								gridIntersectionPostPoints.append(intersection)

								#If the intersections for both lines are on the middles for eachother.
								if intersectionTypeOnNeighbor == "Middle":

									#Split the intersecting neighbor into two segments so the walls dont overlap
									neighborLocLineStart = neighborLocLine.GetEndPoint(0)
									neighborLocLineEnd = neighborLocLine.GetEndPoint(1)
									neighbor.Line = Line.CreateBound(intersection, neighborLocLineStart)
									neighbor.HostLine = Line.CreateBound(intersection, neighborLocLineStart)

									#Create another neighbor thats split
									newNeighborIndex = len(storefrontElevations)+1
									newNeighborHostElementIds = neighbor.HostElementIds
									newNeighborSillHeight = neighbor.SillHeight
									newNeighborHeadHeight = neighbor.HeadHeight
									splitNeighborLine = Line.CreateBound(intersection, neighborLocLineEnd)
									splitNeighbor = StorefrontElevation(newNeighborHostElementIds, splitNeighborLine, neighbor.SuperType, newNeighborIndex, newNeighborSillHeight, newNeighborHeadHeight, systemName)
									storefrontElevations.append(splitNeighbor)

									#Make sure that each new segment has the correct doors on each one
									if neighbor.Doors:
										doorsOnNeighbor = neighbor.Doors
										tempList1 = []
										tempList2 = []
										for neighborDoorId in doorsOnNeighbor:
											neighborDoor = doc.GetElement(neighborDoorId)
											doorPoint = neighborDoor.Location.Point
											if RevitPointOnLine2D(doorPoint, neighbor.Line):
												tempList1.append(neighborDoorId)
											else:
												tempList2.append(neighborDoorId)
										neighbor.Doors = tempList1
										splitNeighbor.Doors = tempList2
				
				#-----------Determine Conditions-----------#

				###------------Start Condition-----------###
				locLine = storefrontObject.HostLine
				locLineStart = locLine.GetEndPoint(0)
				locLineEnd = locLine.GetEndPoint(1)

				startAndEndNeighbors = [storefrontObject.StartNeighbors, storefrontObject.EndNeighbors]

				for i in range(len(startAndEndNeighbors)):

					neighborSet = startAndEndNeighbors[i]
					cornerCount = 0
					inlineCount = 0
					cornerTypes = []
					inlineTypes = []
					conditionAngleOffset = None
					conditionToSet = None

					if neighborSet:

						for neighbor in neighborSet:
							angle = neighbor[2]
							intersectionType = neighbor[3]
							intersection = neighbor[4]

							#---Corner Test---#
							if abs(angle-90) < angleTol:
								if neighbor[1] != storefrontType:
									if intersectionType == "Middle":
										conditionToSet = "OnStorefront"
										cornerTypes.append("Different")
										cornerCount += 2
									elif intersectionType == "Start" or intersectionType == "End":
										cornerTypes.append("Different")
										cornerCount += 1

								elif neighbor[1] == storefrontType:
									# If the storefront is connected to the middle of another storefront
									# that is the of the same type, then it should join
									if intersectionType == "Middle":
										conditionToSet = "JoinStorefront"
										cornerTypes.append("Same")
										cornerCount += 2

									elif intersectionType == "Start" or intersectionType == "End":
										cornerTypes.append("Same")
										cornerCount += 1

							#---Inline Test---#
							elif abs(angle-180) < angleTol:
								if neighbor[1] != storefrontType:
									inlineTypes.append("Different")
									inlineCount += 1 
								elif neighbor[1] == storefrontType:
									inlineTypes.append("Same")
									#Placeholder just in case
									pass

							#---Angled Test---#
							elif abs(round(neighbor[2],1) % 90) > angleTol:
								reverse = 0
								if locLineStart.X > locLineEnd.X: 
									reverse = 180
								angleRadians = (neighbor[2] * (2 * math.pi)) / 360
								conditionAngleOffset = (0.5 * systemPostWidth) / math.tan((angleRadians) * 0.5)
								conditionToSet = "Angled"
								if storefrontConfig.currentConfig["isFramed"]:
									if i == 0:
										vect = RevitTransVector(locLineEnd, locLineStart, magnitude=conditionAngleOffset)
										locLineStart = locLineStart.Add(vect)
										storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

									elif i == 1:
										vect = RevitTransVector(locLineStart, locLineEnd, magnitude=conditionAngleOffset)
										locLineEnd = locLineEnd.Add(vect)
										storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)
								break

						#---Compound Conditions---#
						if cornerCount == 0 and inlineCount == 1:
							if "Same" in inlineTypes:
								pass
							elif "Different" in inlineTypes:
								if storefrontType == "Full":
									conditionToSet = "ForcePost"
								elif storefrontType == "Partial":
									conditionToSet = "OnStorefront"

						elif cornerCount == 1 and inlineCount == 0:
							if "Same" in cornerTypes:
								conditionToSet = None
							elif "Different" in cornerTypes:
								if storefrontType == "Full":
									conditionToSet = None
								elif storefrontType == "Partial":
									conditionToSet = "OnStorefront"
							else: 
								pass

						elif cornerCount == 1 and inlineCount == 1:
							if "Same" in cornerTypes:
								conditionToSet = "JoinStorefront"
								if i == 0:
									vect = RevitTransVector(locLineEnd, locLineStart, magnitude=systemPostWidth/2)
									locLineStart = locLineStart.Add(vect)
									storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

								elif i == 1:
									vect = RevitTransVector(locLineStart, locLineEnd, magnitude=systemPostWidth/2)
									locLineEnd = locLineEnd.Add(vect)
									storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

							elif "Different" in cornerTypes:
								conditionToSet = "OnStorefront"
							else: 
								pass

						elif cornerCount == 2 and inlineCount == 0:
							if not "Different"  in  cornerTypes:
								conditionToSet = "JoinStorefront"
								if i == 0:
									vect = RevitTransVector(locLineEnd, locLineStart, magnitude=systemPostWidth/2)
									locLineStart = locLineStart.Add(vect)
									storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

								elif i == 1:
									vect = RevitTransVector(locLineStart, locLineEnd, magnitude=systemPostWidth/2)
									locLineEnd = locLineEnd.Add(vect)
									storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

							elif "Same" in  cornerTypes and "Different" in cornerTypes:
								conditionToSet = "ForcePostAtTBone"
								if i == 0:
									vect = RevitTransVector(locLineStart, locLineEnd, magnitude=systemPostWidth/2)
									locLineStart = locLineStart.Add(vect)
									storefrontObject.Line = Line.CreateBound(locLineStart, storefrontObject.Line.GetEndPoint(1))

								elif i == 1:
									vect = RevitTransVector(locLineEnd, locLineStart, magnitude=systemPostWidth/2)
									locLineEnd = locLineEnd.Add(vect)
									storefrontObject.Line = Line.CreateBound(storefrontObject.Line.GetEndPoint(0), locLineEnd)

						elif cornerCount == 2 and inlineCount == 1:
							if "Same" in  cornerTypes and "Different" in cornerTypes and "Different" in inlineTypes:
								pass

					#Logic gate to set contidions to the right ends either start of end.
					if i == 0  and neighborSet:
						storefrontObject.StartCondition = conditionToSet
						
						if conditionAngleOffset:
							storefrontObject.StartAngledOffset = conditionAngleOffset
				   
					elif i == 1 and neighborSet:
						storefrontObject.EndCondition = conditionToSet
						
						if conditionAngleOffset:
							storefrontObject.EndAngledOffset = conditionAngleOffset


				#############################################
				#                 Creation                  #
				#############################################

				#--------------Curtain Wall-----------------#
				with rpw.db.Transaction("Create Curtain Wall") as tx:
					SupressErrorsAndWarnings(tx)
					newWallHeadHeight = storefrontObject.HeadHeight 
					newWallLine = storefrontObject.Line
					newWall = Wall.Create(doc, newWallLine, wallTypeCW, baseConstraint, newWallHeadHeight, 0, False, False)
					newWall.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).Set(0)

					#Set new CW Id to storefrontObject object 
					storefrontObject.CWElementId = newWall.Id

					doc.Regenerate()
					
					if storefrontConfig.currentConfig["isFramed"]:
						if storefrontObject.StartCondition == "Angled":
							WallUtils.DisallowWallJoinAtEnd(newWall, 0)
						if storefrontObject.EndCondition == "Angled":
							WallUtils.DisallowWallJoinAtEnd(newWall, 1)

					conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

					#print storefrontObject.SuperType
					#print "start - " + str(storefrontObject.StartCondition)
					#print "end   - " + str(storefrontObject.EndCondition)
					
					for i in range(len(conditionsList)):
						condition = conditionsList[i]
						newWall_grid = newWall.CurtainGrid
						newWallPoint = newWall.Location.Curve.GetEndPoint(i)
						mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5)

						if mullionList:
							for mul in mullionList:
								mul.Pinned = False

								if condition == "OnGyp":
									mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

								elif condition == "OnObstruction":
									mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

								elif condition == "OnStorefront":
									mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

								elif condition == "JoinStorefront":
									doc.Delete(mul.Id)

								elif condition == "ForcePost":
									mul.ChangeTypeId(mullionDict[systemName + "_Post"])

								elif condition == "ForcePostAtTBone":
									mul.ChangeTypeId(mullionDict[systemName + "_Post"])

								elif condition == "Angled":
									if storefrontConfig.currentConfig["isFramed"]:
										mul.ChangeTypeId(mullionDict[systemName + "_OneBy"])
									else: 
										doc.Delete(mul.Id)
				


				#############################################
				#              Modifications                #
				#############################################
				
				
				#-----------Lower Infill Panels-------------#

				newWall_grid = newWall.CurtainGrid

				#Create lower infill panel and sill
				if storefrontConfig.currentConfig["hasLowerInfill"]:

					newWallMidPoint = newWall.Location.Curve.Evaluate(0.5, True)
					newWall_grid = newWall.CurtainGrid
					if storefrontObject.SuperType == "Partial":
						with rpw.db.Transaction("Create Lower Infill Panels") as tx:
							SupressErrorsAndWarnings(tx)
							try:
								gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + storefrontConfig.currentConfig["partialSillHeight"] )
								grid0 = newWall_grid.AddGridLine(True, gridPt, False)
							except:
								pass

							# Create Solid Lower Panels
							doc.Regenerate()
							newWall_grid = newWall.CurtainGrid
							uGridIds = newWall_grid.GetVGridLineIds()
							newWallLocationCurve = newWall.Location.Curve
							verticalGridPoints = []

							for uGridId in uGridIds:
								uGrid = doc.GetElement(uGridId)
								uGridOrigin = uGrid.FullCurve.Origin
								verticalGridPoints.append(XYZ(uGridOrigin.X, uGridOrigin.Y, newWallMidPoint.Z))
							splitCurves = RevitSplitLineAtPoints(newWallLocationCurve, verticalGridPoints)

							for sCurve in splitCurves:
								sCurveMidpoint = sCurve.Evaluate(0.5, True)
								panelIds = RevitCurtainPanelsAtPoint(newWall_grid, sCurveMidpoint, detectionTolerance=0.1)
								panelElevationTupleList = []
								for panelId in panelIds:
									panel = doc.GetElement(panelId)
									panelElevationTupleList.append((panel,float(panel.Transform.Origin.Z)))
								
								panelElevationTupleList = sorted(panelElevationTupleList, key=lambda x: x[1])

								#Gets lowest panel and change to solid
								try:
									panelToChange = panelElevationTupleList[0][0]
									panelToChange.Pinned = False
									panelToChange.ChangeTypeId(panelTypeDict[storefrontConfig.currentConfig["panelLowerInfill"]])
								except:
									pass


				#---------------Special Horizontals---------------#
				specialHorizontals = storefrontConfig.currentConfig["specialHorizontalMullions"]
				if specialHorizontals:
					for key, value in specialHorizontals.items():
						if key in wtName:
							newWallMidPoint = newWall.Location.Curve.Evaluate(0.5, True)
							newWall_grid = newWall.CurtainGrid
							with rpw.db.Transaction("Create Special Horizontal") as tx:
								SupressErrorsAndWarnings(tx)
								try:
									gridPt = XYZ(newWallMidPoint.X, newWallMidPoint.Y, newWallMidPoint.Z + value[0])
									grid0 = newWall_grid.AddGridLine(True, gridPt, False)
								except:
									pass

				#-----------Midspan Intersections (posts)----------#

				newWall_grid = newWall.CurtainGrid
				if gridIntersectionPostPoints:
					with rpw.db.Transaction("Create Intersection Grids") as tx:
						SupressErrorsAndWarnings(tx)
						for gridIntersectionPoint in gridIntersectionPostPoints:
							try:
								gridInt = newWall_grid.AddGridLine(False, gridIntersectionPoint, False)
								mullionIntList = GetVerticalMullionsAtPoint(newWall_grid, gridIntersectionPoint, detectionTolerance=0.001)
								if mullionIntList:
									for mullion3 in mullionIntList:
										mullion3.Pinned = False
										mullion3.ChangeTypeId(mullionDict[storefrontConfig.currentConfig["midspanIntersectionMullion"]])
							except:
								pass

							  
				#-------------------Modify Ends-------------------#
				
				with rpw.db.Transaction("Modify Ends") as tx:
					SupressErrorsAndWarnings(tx)
					#Disallow as needed:


					if storefrontConfig.currentConfig["isFramed"]:
						if storefrontObject.StartCondition == "Angled":
							WallUtils.DisallowWallJoinAtEnd(newWall, 0)
						if storefrontObject.EndCondition == "Angled":
							WallUtils.DisallowWallJoinAtEnd(newWall, 1)

					doc.Regenerate()

					conditionsList = [storefrontObject.StartCondition, storefrontObject.EndCondition]

					#print storefrontObject.SuperType
					#print "start - " + str(storefrontObject.StartCondition)
					#print "end   - " + str(storefrontObject.EndCondition)
					
					for i in range(len(conditionsList)):
						condition = conditionsList[i]
						newWall_grid = newWall.CurtainGrid
						newWallPoint = newWall.Location.Curve.GetEndPoint(i)
						mullionList = GetVerticalMullionsAtPoint(newWall_grid, newWallPoint, detectionTolerance=0.5, searchOnlySelf=True)

						if mullionList:
							for mul in mullionList:
								mul.Pinned = False

								if condition == "OnGyp":
									mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

								elif condition == "OnObstruction":
									mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

								elif condition == "OnStorefront":
									mul.ChangeTypeId(mullionDict[systemName + "_WallStart"])

								elif condition == "JoinStorefront":
									doc.Delete(mul.Id)

								elif condition == "ForcePost":
									mul.ChangeTypeId(mullionDict[systemName + "_Post"])

								elif condition == "ForcePostAtTBone":
									mul.ChangeTypeId(mullionDict[systemName + "_Post"])

								elif condition == "Angled":
									if storefrontConfig.currentConfig["isFramed"]:
										mul.ChangeTypeId(mullionDict[systemName + "_OneBy"])
									else: 
										doc.Delete(mul.Id)



				#-----------------Glazing Panel Types----------------#
				
				changeToPanel = None

				if "Demising" in wtName:
					changeToPanel = storefrontConfig.currentConfig["panelGlazedCenter"]
				elif "Offset" in wtName:
					changeToPanel = storefrontConfig.currentConfig["panelGlazedOffset"]
				elif "Double" in wtName:
					changeToPanel = storefrontConfig.currentConfig["panelGlazedDouble"]
				else:
					pass

				if changeToPanel:
					with rpw.db.Transaction("Change Glazing Types") as tx:
						SupressErrorsAndWarnings(tx)
						doc.Regenerate()
						panels = newWall_grid.GetPanelIds()
						for panelToChangeId in panels:
							panelToChange = doc.GetElement(panelToChangeId)
							panelToChange.Pinned = False
							panelToChange.ChangeTypeId(panelTypeDict[changeToPanel])




				#-------------------Doors------------------#
				
				if storefrontObject.Doors:
					newWallStartPoint = newWall.Location.Curve.GetEndPoint(0)
					newWallEndPoint = newWall.Location.Curve.GetEndPoint(1)
					doorsOnWall = storefrontObject.Doors

					with rpw.db.Transaction("Create Door Grids 0") as tx:
						SupressErrorsAndWarnings(tx)

						for doorId in doorsOnWall:

							#Location info
							door = doc.GetElement(doorId)
							doorName = door.Name
							doorLocationCenter = door.Location.Point
							doorLocationRotation = door.Location.Rotation
							doorHandOrientation = door.HandOrientation

							#Defaults
							doorHand = "R"
							doorWidth = 1.0
							doorType = "SWING"

							#Get specific door info based on registered doors in the config.
							if doorDict.get(doorName):

								doorDetails = doorDict[doorName]
								doorHand = doorDetails[0]
								doorWidth = doorDetails[1]
								doorType = doorDetails[2]

								frameMullion0 = mullionDict[systemName + doorDetails[3]]
								frameMullion1 = mullionDict[systemName + doorDetails[4]]
								extraAdjustment0 = doorDetails[5]
								extraAdjustment1 = doorDetails[6]

							else: 

								#Defaults if no door is found
								frameMullion0 = mullionDict[systemName + "_DoorFrame"]
								frameMullion1 = mullionDict[systemName + "_DoorFrame"]

								#Fine adjustments for mullion position
								extraAdjustment0 = 0
								extraAdjustment1 = 0
								print "ISSUE: Unable to recognize door - " + doorName


							#Get offset widths for door frame mullions
							fm0 = doc.GetElement(frameMullion0)
							frameMullion0Width = fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
							frameMullion0Width += fm0.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

							fm1 = doc.GetElement(frameMullion1)
							frameMullion1Width = fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
							frameMullion1Width += fm1.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()

							#Accounting for mullion CUST_MULLION_THICKnesses 
							extra0 = (frameMullion0Width * 0.5) + extraAdjustment0
							extra1 = (frameMullion1Width * 0.5) + extraAdjustment1

							#Vectors to move location point
							vect0 = doorHandOrientation.Multiply(((doorWidth / 2) + extra0))
							vect1 = doorHandOrientation.Multiply(((doorWidth / 2) + extra1) * -1)

							#Door end points
							door_end0 = doorLocationCenter.Add(vect0)
							door_end1 = doorLocationCenter.Add(vect1)


							#Detection tolerance for nearby mullions based on system
							#required because of varying mullion sizes

							systemDetectionFactor = storefrontConfig.currentConfig["closeMullionDetectionFactor"]

							detectionCheckDist0 = frameMullion0Width * systemDetectionFactor
							detectionCheckDist1 = frameMullion1Width * systemDetectionFactor
	

							doc.Regenerate()
							newWall_grid = newWall.CurtainGrid

							#Check to see if a mullion exists in the spot where one would be created.
							checkMullion0 = GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=detectionCheckDist0)
							if not checkMullion0:
								try:
									grid0 = newWall_grid.AddGridLine(False, door_end0, False)
								except:
									pass

								mullion0List = GetVerticalMullionsAtPoint(newWall_grid, door_end0, detectionTolerance=0.001)
								if mullion0List:
									for mullion0 in mullion0List:
										mullion0.Pinned = False
										mullion0.Lock = False
										mullion0.ChangeTypeId(frameMullion0)

							doc.Regenerate()
							#Check to see if a mullion exists in the spot where one would be created.
							checkMullion1 = GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=detectionCheckDist1)
							if not checkMullion1:
								try:
									grid1 = newWall_grid.AddGridLine(False, door_end1, False)
								except:
									pass

								mullion1List = GetVerticalMullionsAtPoint(newWall_grid, door_end1, detectionTolerance=0.001)
								if mullion1List:
									for mullion1 in mullion1List:
										mullion1.Pinned = False
										mullion1.Lock = False
										mullion1.ChangeTypeId(frameMullion1)

						#-----------------Empty Panel----------------#
							doc.Regenerate()
							panelToChangeId = RevitCurtainPanelsAtPoint(newWall_grid, doorLocationCenter, detectionTolerance=0.2)
							if panelToChangeId:
								panelToChange = doc.GetElement(panelToChangeId[0])
								panelToChange.Pinned = False
								panelToChange.ChangeTypeId(panelTypeDict[storefrontConfig.currentConfig["panelEmpty"]])

						#-----------------Sill Delete----------------#
							doc.Regenerate()

							filterName = storefrontConfig.currentConfig["AUTO_MULLION_BORDER1_HORIZ"].split("_")[1]
							doorSillMullions = GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter=filterName)

							for dsm in doorSillMullions:
								dsm.Pinned = False
								doc.Delete(dsm.Id)

						#-------------Continuous Head Above Door--------------#

							doorFrameContinuous = storefrontConfig.currentConfig["mullionContinuousVerticalAtDoorTop"]

							if not doorFrameContinuous:
								
								#filterName = storefrontConfig.currentConfig["AUTO_MULLION_BORDER2_HORIZ"].split("_")[1]

								#Join head so its continuous
								doc.Regenerate()
								doorHeadMullions = GetHorizontalMullionsAtPoint(newWall_grid, doorLocationCenter, nameFilter="Head")
								for dhm in doorHeadMullions:
									dhm.JoinMullion()
	 
				#-------------------Intermediates-------------------# 

				newWall_grid = newWall.CurtainGrid
				panels = newWall_grid.GetPanelIds()

				intermediateMullionWidth = 0
				if storefrontConfig.currentConfig["isFramed"]:

					#Select the right intermediate mullion in the project based
					#on which system is being used. 

					if "demising" in wtName.lower():
						mulName = storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT"]
					elif "offset" in wtName.lower():
						mulName = storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT_OFFSET"]
					elif "double" in wtName.lower():
						mulName = storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT_DOUBLE"]
					else:
						mulName = storefrontConfig.currentConfig["AUTO_MULLION_INTERIOR_VERT"]

					intermediateMullion = doc.GetElement(mullionDict[mulName])

					#Get the sizes of the intermediate
					try:
						intermediateMullionWidth = intermediateMullion.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH1).AsDouble()
						intermediateMullionWidth += intermediateMullion.get_Parameter(BuiltInParameter.CUST_MULLION_WIDTH2).AsDouble()
					except:
						for p in intermediateMullion.Parameters:
							if p.Definition.Name == "Width on side 1":
								intermediateMullionWidth += p.AsDouble()
							if p.Definition.Name == "Width on side 2":
								intermediateMullionWidth += p.AsDouble()

				#For each panel, check the widths and divide them
				#according to the rules selected by the user.                 
				for panelId in panels:
					panel = doc.GetElement(panelId)
					panelWidth = panel.get_Parameter(BuiltInParameter.CURTAIN_WALL_PANELS_WIDTH).AsDouble()

					if "glazed" in (panel.Name + panel.Symbol.Family.Name).lower() and panelWidth > minPanelWidth:
						newGridPoints = []
						if storefrontSpacingType == 1:
							newGridPoints = RevitDividePanelFixed(panel, storefrontPaneWidth, intermediateWidth=intermediateMullionWidth)
						elif storefrontSpacingType == 0:
							numberPanes = math.ceil(panelWidth/storefrontPaneWidth)
							if numberPanes > 1:
								newGridPoints = RevitDividePanelEquidistant(panel, numberPanes, intermediateWidth=intermediateMullionWidth)

						if newGridPoints:
							with rpw.db.Transaction("Create intermediate grid lines") as tx:
								SupressErrorsAndWarnings(tx)
								for gridpt in newGridPoints:
									try:
										grid0 = newWall_grid.AddGridLine(False, gridpt, False)
										mullions0List = GetVerticalMullionsAtPoint(newWall_grid, grid0.FullCurve.Origin, detectionTolerance=0.001)
										for mullion0 in mullions0List:
											mullion0.Pinned = False
											if storefrontConfig.currentConfig["isFramed"]:
												mullion0.ChangeTypeId(intermediateMullion.Id)

												#Intermediates die into the head if mullion is "Broken"
												if not storefrontConfig.currentConfig["mullionContinuousVerticalIntermediateTop"]:
													mullion0.BreakMullion()
											else:
												#Delete mullion in the case that the system type is butt joined.
												doc.Delete(mullion0.Id)
									except:
										pass

				#---------------Special Sills---------------#
				
				newWall_grid = newWall.CurtainGrid

				updatedSill = None

				currentSill = storefrontConfig.currentConfig["AUTO_MULLION_BORDER1_HORIZ"]
				replacementSills = storefrontConfig.currentConfig["specialSillConditions"]

				if replacementSills:
					for key,value in replacementSills.items():
						if key.lower() in wtName.lower():
							updatedSill = mullionDict[value]

				if updatedSill:
					panels = newWall_grid.GetPanelIds()
					with rpw.db.Transaction("Update Sills") as tx:
						SupressErrorsAndWarnings(tx) 
						for panelId in panels:
							panel = doc.GetElement(panelId)
							panelPoint = panel.GetTransform().Origin
							sills = GetHorizontalMullionsAtPoint(newWall_grid, panelPoint, nameFilter=currentSill)

							sillElevationTupleList = []
							for sill in sills:
								sillElevationTupleList.append((sill,float(sill.LocationCurve.Origin.Z)))
								
							sillElevationTupleList = sorted(sillElevationTupleList, key=lambda x: x[1])

							try:
								sillToChange = sillElevationTupleList[0][0]
								sillToChange.Pinned = False
								sillToChange.ChangeTypeId(updatedSill)
							except:
								pass                       
				 
				#############################################
				#            Final Param Setters            #
				#############################################
				# Set heights, for whatever reason differing heights before adding gridlines is an issue so set this last.
				with rpw.db.Transaction("Create Curtain Wall") as tx:
					SupressErrorsAndWarnings(tx)
					newWallSillHeight = storefrontObject.SillHeight
					newWallHeadHeight = storefrontObject.HeadHeight - storefrontObject.SillHeight
					newWall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(newWallSillHeight)
					newWall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(newWallHeadHeight)
					newWall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(storefrontObject.SuperType)
					newWall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(str(selectedLevel) + "-"+ str(storefrontObject.AssemblyID))



	print "...CHECKING ERRORS..."

	storefront_check_errors()

	print "...DONE!"