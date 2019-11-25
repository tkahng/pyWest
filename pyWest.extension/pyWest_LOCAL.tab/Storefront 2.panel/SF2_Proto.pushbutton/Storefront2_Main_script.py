import traceback

try:
    import sys
    sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
    import os

    """
	The whole stack firing Main() is placed in a try_except pattern
	in order to reveal the file and line number of any error that causes
	the program to fail

	REMEMBER THAT INSTANTIATED OBJECTS CAN BE CONTINOUSLY
	MODIFIED BY THEIR METHODS
	"""

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

    # imports for Storefront2 dependencies
    sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\Storefront 2.panel\0 Lib\SF2_Prototypes")
    #import Storefront2_Engine as SFE
    #import Storefront2_GUI as SFGUI
    #import Storefront2_Utilities as SFU
    
    sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\Storefront 2.panel\0 Lib")
    import SF2_Families    
    # reload is for preproduction / testing purposes
    #reload(SFE)
    #reload(SFGUI)
    #reload(SFU)
    #reload(SF2_Families)

    class CollectSFwalls:
        """
        The intention of this new code is to make the collection of walls
        as versatile as possible. Rather than hard coding the names of 
        storefront/random wall type, it always creates a list of walls
        within the document and groups elements to those names, per level.
        Mapping this to a single location containing the cannonical Storefront
        names should make future expansion much easier.
        """
        def __init__(self, currentViewOnly=True):
            # DELETE: THESE WILL BE INHERITED FROM YOUNGEST CHILD
            self.app = __revit__.Application #use this to open another model?
            self.version = self.app.VersionNumber.ToString()
            self.uidoc = __revit__.ActiveUIDocument
            self.doc = __revit__.ActiveUIDocument.Document
            self.currentView = self.uidoc.ActiveView
            
            # input parameter - can avoid level parsing by reading view level
            self.currentViewOnly = currentViewOnly
            
            # standard tolerances
            self.distTol = 0.5 
            self.angleTol = 0.01
            self.absoluteTol = 0.001
            self.minPanelWidth = 1.0            
        
        def GetSFWalls(self):
            # walls collected by user selection -> returns wall object
            selectionIdList = self.uidoc.Selection.GetElementIds()
            if selectionIdList: wallList = [self.doc.GetElement(id) for id in selectionIdList if self.doc.GetElement(id).Name in SF2_Families.SFFamilyNames()]
            
            # walls collected by code -> returns wall object
            if not selectionIdList and self.currentViewOnly == True:
                wallList = [i for i in FilteredElementCollector(self.doc, self.currentView.Id).OfClass(Wall) if i.Name in SF2_Families.SFFamilyNames()] # Autodesk.Revit.DB.Wall - defines <type 'Wall'>
            if not selectionIdList and self.currentViewOnly == False:
                wallList = [i for i in FilteredElementCollector(self.doc).OfClass(Wall) if i.Name in SF2_Families.SFFamilyNames()]
            
            if wallList: return(wallList)
            else: raise Esception("There are no walls in the model")
            
        def GetUniqueWallNames(self, wallList):
            # get and parse unique wall names
            wallNameList = [wall.Name for wall in wallList]
            uniqueWallNames = set(wallNameList)
            return(uniqueWallNames)
        
        def GetLevelsOfEachWall(self, wallList):
            # try this: IntersectWith(FilteredElementCollector(self.doc).OfClass(Level))
            levelIdList = [i.LevelId for i in wallList]
            levelList = [self.doc.GetElement(id) for id in levelIdList]
            levelNameList = [i.Name for i in levelList]
            return(levelList)
    
        def PairUniqueWallsToUniqueLevels(self):
            storefrontWalls = [wall for wall in wallList if wall.Name in SFF.Families().SFWallNames()] # HOW SHOULD THIS BE USED???
        
        def SortPairedWallList(self):
            pass     
        
        def Run_CollectWalls(self):
            # collect all walls
            sfWalls = self.GetSFWalls()
            
            # get unique wall names
            wallNameList = self.GetUniqueWallNames(sfWalls)
            
            # get levels of each wall
            levelList = self.GetLevelsOfEachWall(sfWalls)
            
            # filter walls by type, and level
            
            # pair unique wall names with unique levels
            if self.currentViewOnly == True:
                pass #skip this step s            
            
            # sort lists of lists based on level number
            
            # collect storefront walls of name/type within list of past and present options
            
            return(['nested wall collection'])
                        
    
    def TestMain():
        # COLLECT SF WALLS
        CollectSFwalls(currentViewOnly=True).Run_CollectWalls()
        
        ## Run_CollectWalls ENGINE
        #t = Transaction(doc, 'Generating Storefront Walls in Revit')
        #t.Start()

        ## Run_CollectWalls storefront on sf walls - check SFE for notes	
        #SFE.Storefront2(doc, wallList).GenerateSF()

        #t.Commit()

        # create report; save as json file


        # design to fabrication


    if __name__ == "__main__":
        TestMain()


except:
    # print traceback in order to debug file
    print(traceback.format_exc())