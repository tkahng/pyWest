"""
SOMETHING
"""
import traceback
import sys
import os
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
import Autodesk.Revit.UI.Selection

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))
sys.path.append(ShiftFilePath(path=os.path.abspath(__file__), branchesBack=3, append=r"0 Lib"))
#import WW_ExternalPython as WW_EP

##############################
## SUPPRESS WARNINGS/ERRORS ##
##############################
class WarningDiscard(Autodesk.Revit.DB.IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        fail_acc_list = failuresAccessor.GetFailureMessages().GetEnumerator()
        onlyWarnings = True
        for failure in fail_acc_list:
            failure_id = failure.GetFailureDefinitionId()
            failure_severity = failure.GetSeverity().ToString()
            # add failure types below
            failure_types = [BuiltInFailures.CurtainWallFailures.DanglingCurtainWallCorner,
                             BuiltInFailures.OverlapFailures.WallsOverlap,
                             BuiltInFailures.OverlapFailures.RoomSeparationLinesOverlap,
                             BuiltInFailures.OverlapFailures.SpaceSeparationLinesOverlap,
                             BuiltInFailures.OverlapFailures.WallRoomSeparationOverlap,
                             BuiltInFailures.OverlapFailures.WallAreaBoundaryOverlap,
                             BuiltInFailures.OverlapFailures.WallSpaceSeparationOverlap,
                             BuiltInFailures.CreationFailures.CannotMakeWall,
                             BuiltInFailures.CreationFailures.CannotDrawWalls,
                             BuiltInFailures.CreationFailures.CannotDrawWallsError,
                             BuiltInFailures.JoinElementsFailures.CannotKeepJoined,
                             BuiltInFailures.CurtainGridFamilyFailures.CornerMullionOverlapsOtherOnePlacedOnNeighboringRegion,
                             BuiltInFailures.CurtainGridFamilyFailures.CannotCreateCornerMullionDueAngle,
                             BuiltInFailures.CurtainGridFamilyFailures.CannotPlaceSystemMullionFamilyOnCurtainWall,
                             
                             BuiltInFailures.LinkFailures.LinkInstanceNeedsReconcile]
            # IGNORE UNRESOLVED LINKS...BUT HOW???
            if failure_id in failure_types:
                if failure_severity == "Warning":
                    failuresAccessor.DeleteWarning(failure)
                elif failure_severity == "Error":
                    failuresAccessor.ResolveFailure(failure)
                    onlyWarnings = False
        if onlyWarnings:
            return(FailureProcessingResult.Continue)
        else:
            return(FailureProcessingResult.ProceedWithCommit)
        
        #TransmittedModelOptions.KeepAsTransmitted
        
        return(True)

############################################
## EXPORT REVIT MODELS INCL. LINKS AS IFC ##
############################################
class ExportRevit:
    def __init__(self, doc, app=None, filePath=None, fileName=None, ifcOptions=None, checkOutput=False):
        # input parameters
        self.doc = doc
        self.app = app
        self.checkOutput = checkOutput
        
        if not self.filePath: self.filePath = os.path.expanduser("~\Desktop")
        else: self.filePath = filePath
        
        if not self.fileName: self.fileName = self.doc.Title
        else: self.fileName = fileName
        
        if not self.ifcOptions: self.ifcOptions = self.ArchilogicOptions() # WW default export options
        else: self.ifcOptions = ifcOptions
        
        # derived variables
        self.originalModelPath = self.doc.PathName
        self.dummyRFA = r"G:\Shared drives\Prod - BIM\07_Global Initiatives\Archilogic IFC Export\Core Files\DummyRVTFamily.rfa" # file now in shared G Drive
        self.currentViewBeforeExportLoop = None
        
        # output variables
        self.docEC_Links = []
        self.docEC_Origins = []
        
    #####################
    ## SAVE TO G DRIVE ##
    #####################
    
    #
    # EXPORT SETTINGS
    def GetExportViewId(self):
        # this will only be implemented if a default view can be added to the model
        viewId = [i.Id for i in FilteredElementCollector(self.doc).OfClass(View) if i.Name == "{3D - alvaro.lunaWW}"]
        return(viewId[0])
    
    def ArchilogicOptions(self):
        ArchL_IFC_Options = IFCExportOptions()
        ArchL_IFC_Options.FileVersion = IFCVersion.IFC2x3 # IFCVersion.IFC4
        ArchL_IFC_Options.WallAndColumnSplitting = True
        ArchL_IFC_Options.ExportBaseQuantities = True
        ArchL_IFC_Options.FilterViewId = self.GetExportViewId() # the default view will be the standard 3d view in the template
        return(ArchL_IFC_Options)
    
    def FailureProcessor(self):
        # app of current document in open loop
        app = __revit__.Application
        e = app.FailuresProcessing #+= FailureProcessor
        print(e)
        
        #hasFailure = False
        #fas = e.GetFailuresAccessor()
        #fma = fas.GetFailureMessages().ToList()
        
        #ElemntsToDelete = []
        #for fa in fma:
            #try:
                ## use the following lines to delete the warning elements
                #FailingElementIds = fa.GetFailingElementIds().ToList()
                #FailingElementId = FailingElementIds[0]
                
                #if ElemntsToDelete.Contains(FailingElementId):
                    #ElemntsToDelete.Add(FailingElementId)
                    #hasFailure = True
                    #fas.DeleteWarning(fa)
            #except:
                #if ElemntsToDelete.Count > 0:
                    #fas.DeleteElements(ElemntsToDelete)
            
            ## use the following line to disable the message supressor after the external command ends
            ## CachedUiApp.Application.FailuresProcessing -= FailureProcessor;
            #if hasFailure:
                #e.SetProcessingResult(FailureProcessingResult.ProceedWithCommit)
                #e.SetProcessingResult(FailureProcessingResult.Continue)
               
    #
    # UTILITIES / DATABASES
    def ECName(self):
        ecList = ["_ec", "ec.", "existingconditions",
                  "existing", "ec", "EC", ".EC", "-EC",
                  "existing-conditions"]
        ecStrings = [i.lower() for i in ecList]
        return(ecStrings)        
    
    def SyncWithOptions(self):
        # set options for accessing central model
        transOpts = TransactWithCentralOptions()
        
        # set options for synchronizing with central
        syncOpts = SynchronizeWithCentralOptions()
        # sync with relinquishing any checked out elements or worksets
        relinquishOpts = RelinquishOptions(True)
        syncOpts.SetRelinquishOptions(relinquishOpts)
        # do not automatically save local model after sync
        syncOpts.SaveLocalAfter = True
        syncOpts.Comment = "Changes to Workset1"
    
        try:
            self.doc.SynchronizeWithCentral(transOpts, syncOpts)
        except:
            TaskDialog.Show("Synchronize Failed") # , e.Message
    def SupressErrorsAndWarnings(self, transaction):
        # I guess this forces revit to ignore errors and warnings
        options = transaction.GetFailureHandlingOptions()
        preprocessor = WarningDiscard()
        options.SetFailuresPreprocessor(preprocessor)
        transaction.SetFailureHandlingOptions(options)
        return(None)    
    #
    # EXPORT MAIN RVT MODEL
    def ExportRVT(self):
        # record current view prior to export sequence
        uidoc = __revit__.ActiveUIDocument
        self.currentViewBeforeExportLoop = uidoc.ActiveView.Id
        print("The id is: {0}".format(self.currentViewBeforeExportLoop))
        
        t = Transaction(self.doc, 'Exporting current RVT to IFC')
        t.Start()   
        
        # export current model | Autodesk.Revit.DB.Document.Export("folder","name",options)
        self.doc.Export(self.filePath, self.fileName, self.ifcOptions)
        
        # transaction must be committed before proceeding to linked files
        t.Commit()    
    #
    # COLLECT LINKED RVT MODELS
    def CollectLinkedRVT(self, quiet=False):
        linkedInstances = FilteredElementCollector(self.doc).OfClass(RevitLinkInstance) # Autodesk.Revit.DB.
        if linkedInstances:
            for i in linkedInstances:
                if quiet == False: print("LINKED MODELS: {0}".format(str(i.Name)))
                if any(j in i.Name.lower() for j in self.ECName()): # this is new, I have never seen it before
                    self.docEC_Links.append(i.GetLinkDocument())
                    self.docEC_Origins.append(i.GetTransform().Origin) # used to line up the ec model
                    if quiet == False: print("...FOUND EC MODEL: {0}".format(str(i.Name)))
                else:
                    print(False)
            
            if self.docEC_Links and quiet == False: print("...LOADED EC MODEL")
            if not self.docEC_Links and quiet == False: print("...CHECK EC MODEL LINK BEFORE PROCEEDING")
        
        if not linkedInstances and quiet == False:
            print("...NO LINKED MODELS FOUND")
            print("...ERROR LOADING EC ELEMENTS")
    
    def ExportLinkedRVT(self):
        """
        from documentation:
        This method, if successful, changes the active document. It is not allowed to have an open transaction in the active document when calling this method. Additionally, this method may not be called from inside an event handler.
        
        also, you cannot open a file that is linked to an open file! SO LAME...
        
        AT SOME POINT GET ACTIVE VIEW ID AND OPEN DOCUMENT DIRECTLY TO IT WHEN LINK EXPORT LOOP ENDS
        """
        
        rvtLinkPaths = [i.PathName for i in self.docEC_Links]
        
        # open a dummy file in order to be able to exit the active document and export the links
        dummyModel = __revit__.OpenAndActivateDocument(self.dummyRFA)
        dummyDoc = __revit__.ActiveUIDocument.Document
        self.doc.Close(False) # close original doc to allow export of linked files        
        
        for i, rvtLink in enumerate(rvtLinkPaths):
            # WHAT IS A TRANSMITTED MODEL?
            rvtLinkObj = ModelPathUtils.ConvertUserVisiblePathToModelPath(rvtLink)
            transData = TransmissionData.ReadTransmissionData(rvtLinkObj)
            #if transData.IsDocumentTransmitted(rvtLinkObj):
            TransmittedModelOptions.KeepAsTransmitted
            transData.IsTransmitted = False
            
            exportTempModel = __revit__.OpenAndActivateDocument(rvtLink)
            exportTempDoc = __revit__.ActiveUIDocument.Document
            self.fileName = exportTempDoc.Title
            
            t = Transaction(exportTempDoc, 'Exporting linked RVT to IFC')
            t.Start()
            
            # supress warnings/errors
            #self.SupressErrorsAndWarnings(transaction=t)
            
            try:
                exportTempDoc.Export(self.filePath, "{0}".format(self.fileName), self.ifcOptions)
            except:
                print(traceback.format_exc())
            t.Commit()
        
            # reactivate original doc - must get cloud read to work first
            originalModel = __revit__.OpenAndActivateDocument(self.originalModelPath)
            
            # close opened docs
            exportTempDoc.Close(False)
        dummyDoc.Close(False)
    
    ###################
    ## MAIN (RUN ME) ##
    ###################
    def Run_IFCExport(self):
        # save to central first; also works in cloud
        self.SyncWithOptions()
        
        # collect EC model in self.doc
        self.CollectLinkedRVT()
        
        # export current model
        self.ExportRVT()
        
        # export linked EC model - transaction in code
        self.ExportLinkedRVT()
        
        # run external python engine to upload exported model to gDrive
        #scriptPath = ShiftFilePath(os.path.abspath(__file__), branchesBack=1)
        #WW_EP.ExternalPythonEngine(self, scriptPath, pyVersion="python3", jsonArgs=None).Run_Subprocess()
        
        # check if gDrive upload is successful