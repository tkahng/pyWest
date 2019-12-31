self.tol = 0.001

self.version = __revit__.Application.VersionNumber.ToString()
self.uidoc = __revit__.ActiveUIDocument
self.doc = uidoc.Document
self.currentView = uidoc.ActiveView

# variables that I have added bc of introduction of OOP structure
self.selectedLevel = None
self.allWalls = []
self.allColumns = []
self.interiorWalls = []
self.selectedLevelInst = None # introduced in self.CollectStorefrontWalls()

self.storefrontFull = []
self.storefrontPartial = []
self.selectedLevels = [] # not used in code!
self.storefrontFullLines = [] # not used in code!
self.storefrontPartialLines = [] # not used in code!
self.interiorWallsLines = [] # not used in code!
self.interiorWallsLinesEdges = []
self.selectedDoors = [] # not used in code!
self.selectedRooms = [] # not used in code!
self.selectedFloors = [] # not used in code!

self.ecModelInst = None # not used in code!
self.docEC = None # how is docEC being assigned? from Main?
self.ecTransform = None

self.allWallsEC = [] # this variable is never filled, what is it used for??? - MAYBE COLLECTION OBJECT ASKS FOR CONTAINER LIST???
self.allLevelsEC = [] # not used in code!
self.allColumnsEC = [] # this variable is never fille, what is it used for??? - MAYBE COLLECTION OBJECT ASKS FOR CONTAINER LIST???
self.wallsLinesEdgesEC = []
self.selectedLevelsEC = [] # not used in code!
self.selectedWallsEC = []
self.selectedColumnsEC = []


self.distTol = 0.5 
self.angleTol = 0.01
self.absoluteTol = 0.001

self.minPanelWidth = 1.0

# LOOK HERE! REPEATED VARIABLES...WHY???
self.docLoaded = RevitLoadECDocument() # storefront_utils.RevitLoadECDocument()
#		self.docLoaded = RevitLoadECDodument2()
self.docEC = self.docLoaded[0]
self.ecTransform = self.docLoaded[1]

self.mrTimer = Timer()