# standard python modules
import clr
import os

# windows form modules
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
from System import Array # convert .net arrays to python lists
import System.Drawing
import System.Windows.Forms
import System.IO # for Directory obj
from System.Drawing import *
from System.Windows.Forms import *
from System.IO import *

class ImportSAT_Rhino_GUI:
    def __init__(self):
        # UI object
        self.openFileDialog = System.Windows.Forms.OpenFileDialog()
        self.openFolderDialog = System.Windows.Forms.FolderBrowserDialog()
        
        # last opened directory
        # read some json file
        
        # form output
        self.results = None
    
    def SelectFolder(self):
        self.openFolderDialog.ShowDialog()
        result = Directory.GetFiles(self.openFolderDialog.SelectedPath)
        return(result)

    def SelectFiles(self):
        # windows form: open file dialog
        self.openFileDialog.Filter = "SAT file (*.sat)|*.sat"
        # in C# closer to: self.openFileDialog.Title("Select SAT file to import")
        self.openFileDialog.Title = "Select SAT file to import"
        
        # read json file of last opened directory
        
        # open from that location if it exists
        self.openFileDialog.InitialDirectory = os.path.expanduser("~\Desktop")
        self.openFileDialog.Multiselect = True
        
        # open windows form
        self.openFileDialog.ShowDialog()
    
    def RunForm(self, selectionType=0):
        if selectionType == 0:
            self.SelectFiles()
            
            # get form outputs
            if DialogResult.OK:
                self.results = [i for i in self.openFileDialog.FileNames]            
       
        elif selectionType == 1:
            folderContents = self.SelectFolder()
            
            if DialogResult.OK:
                self.results = [i for i in folderContents]
                #System.Windows.Forms.MessageBox.Show("Files found: {0}".format(folderContents.Length.ToString()), "Message")            