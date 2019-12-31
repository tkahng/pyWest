import clr
import sys, traceback
import os
import logging
import System
import math

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application
version = __revit__.Application.VersionNumber.ToString()

user = str(System.Environment.UserName)

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from storefront_utils import *
from storefront_system_configs import *

class StorefrontElevation:
	def __init__(self, _hostElementIds, _line, _superType, _id, _sillHeight, _headHeight, _systemName):	
		self.AssemblyID = _id
		self.CWElementId = None
		self.EndCondition = None
		self.EndNeighbors = []
		self.EndOffset = 0
		self.EndAngledOffset = 0
		self.HostElementIds = _hostElementIds
		self.Line = _line
		self.HostLine = _line
		self.StartCondition = None
		self.StartNeighbors = []
		self.StartOffset = 0
		self.StartAngledOffset = 0
		self.SuperType = _superType
		self.SystemName = _systemName
		self.SillHeight = _sillHeight
		self.HeadHeight = _headHeight
		self.Type = None
		self.Doors = None
		self.ErrorList = []
		
