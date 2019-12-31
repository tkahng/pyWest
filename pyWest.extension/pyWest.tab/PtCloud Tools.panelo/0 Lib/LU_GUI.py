"""

you are creating form objects, then
modifying form object properties

at some point consider bringing all forms for
this script into this file

"""

# imports for Windows Form
import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
from System import Array # convert .net arrays to python lists
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import *

import sys
sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\PtCloudTools.panel\Lib")
import LU_Materials as LUM

class LU_Form(Form):
    def __init__(self):
        self.InitializeComponent() # outside list must come from here

        # custom outputs - don't know if this functionality is built in...
        self.jsonPathList = None
        self.selectedMaterial = None

    def InitializeComponent(self):
    	self.materials = LUM.FloatMaterialDict()
        self._openFileDialog = System.Windows.Forms.OpenFileDialog()
        self._jsonBrowse = System.Windows.Forms.Button()
        self._calculateButton = System.Windows.Forms.Button()
        self._closeButton = System.Windows.Forms.Button()
        self._jsonLabel = System.Windows.Forms.Label()
        self._materialLabel = System.Windows.Forms.Label()
        self._materialDropdown = System.Windows.Forms.ComboBox()
        self.SuspendLayout()
        # 
        # openFileDialog
        # 
        self._openFileDialog.Filter = "Json files (*.json)|*.json|All files (*.*)|*.*"
        self._openFileDialog.InitialDirectory = r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\PtCloud Tools.panel\0 Lib\JSON Exchange\TEST PtCloud JSONs"
        self._openFileDialog.Multiselect = True
        self._openFileDialog.RestoreDirectory = True
        # 
        # jsonBrowse
        # 
        self._jsonBrowse.Location = System.Drawing.Point(12, 12)
        self._jsonBrowse.Name = "jsonBrowse"
        self._jsonBrowse.Size = System.Drawing.Size(75, 23)
        self._jsonBrowse.TabIndex = 2
        self._jsonBrowse.Text = "JSON"
        self._jsonBrowse.UseVisualStyleBackColor = True
        self._jsonBrowse.UseWaitCursor = False
        self._jsonBrowse.Click += self.EventJSONBrowse
        # 
        # calculateButton
        # 
        self._calculateButton.Location = System.Drawing.Point(238, 94)
        self._calculateButton.Name = "calculateButton"
        self._calculateButton.Size = System.Drawing.Size(75, 23)
        self._calculateButton.TabIndex = 1
        self._calculateButton.Text = "Calculate"
        self._calculateButton.UseVisualStyleBackColor = True
        self._calculateButton.UseWaitCursor = False
        self._calculateButton.Click += self.EventCalculateButton
        # 
        # closeButton
        # 
        self._closeButton.Location = System.Drawing.Point(319, 94)
        self._closeButton.Name = "closeButton"
        self._closeButton.Size = System.Drawing.Size(75, 23)
        self._closeButton.TabIndex = 0
        self._closeButton.Text = "Close"
        self._closeButton.UseVisualStyleBackColor = True
        self._closeButton.UseWaitCursor = False
        self._closeButton.Click += self.EventCloseButton
        # 
        # jsonLabel
        # 
        self._jsonLabel.Location = System.Drawing.Point(139, 12)
        self._jsonLabel.Name = "jsonLabel"
        self._jsonLabel.Size = System.Drawing.Size(267, 23)
        self._jsonLabel.TabIndex = 3
        self._jsonLabel.Text = "No Point Cloud Selected"
        self._jsonLabel.UseWaitCursor = False
        # 
        # materialLabel
        # 
        self._materialLabel.Location = System.Drawing.Point(12, 55)
        self._materialLabel.Name = "materialLabel"
        self._materialLabel.Size = System.Drawing.Size(301, 13)
        self._materialLabel.TabIndex = 6
        self._materialLabel.Text = "Float Material"
        self._materialLabel.UseWaitCursor = False
        # 
        # materialDropdown
        # 
        self._materialDropdown.FormattingEnabled = True
        self._materialDropdown.Location = System.Drawing.Point(12, 71)
        self._materialDropdown.Name = "materialDropdown"
        self._materialDropdown.Size = System.Drawing.Size(121, 21)
        self._materialDropdown.TabIndex = 8
        self._materialDropdown.UseWaitCursor = False
        
        for i in self.materials.keys(): self._materialDropdown.Items.Add(i)
        
        self._calculateButton.Click += self.EventMaterialDropdown # not method but object, why???
        # 
        # LU_Form
        # 
        self.BackColor = System.Drawing.Color.FromArgb(255, 255, 255)
        self.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Center
        self.ClientSize = System.Drawing.Size(431, 138)
        self.Controls.Add(self._materialDropdown)
        self.Controls.Add(self._materialLabel)
        self.Controls.Add(self._jsonLabel)
        self.Controls.Add(self._closeButton)
        self.Controls.Add(self._calculateButton)
        self.Controls.Add(self._jsonBrowse)
        self.Text = "Level UP"
        self.UseWaitCursor = False
        self.ResumeLayout(False)


    # EVENT HANDLERS - if/else has broken preview
    def EventJSONBrowse(self, sender, e):
        # save dialog selection on pressing ok/calculate button
        if self._openFileDialog.ShowDialog() == DialogResult.OK:
        	if len(self._openFileDialog.FileNames) == 1:
        		self._jsonLabel.Text = "1 Json file selected"
        	elif len(self._openFileDialog.FileNames) > 1:
        		self._jsonLabel.Text = "{0} Json files selected".format(len(self._openFileDialog.FileNames))
        	self.jsonPathList = [i for i in self._openFileDialog.FileNames]
    
    def EventMaterialDropdown(self, sender, e):
    	selectedIndex = self._materialDropdown.SelectedIndex
        self.selectedMaterial = self._materialDropdown.SelectedItem

    def EventCalculateButton(self, sender, e):
    	# closes windows form
        self.Close()

    def EventCloseButton(self, sender, e):
        # closes windows form
        self.Close()        


if __name__ == "__main__":
    # test, will not run if imported by another file
    formObj = LU_Form()
    Application.Run(formObj)
    print(formObj.jsonPathList)
    print(formObj.selectedItem)