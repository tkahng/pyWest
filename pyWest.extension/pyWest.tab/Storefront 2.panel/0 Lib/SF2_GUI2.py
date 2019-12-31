"""
:tooltip:
Module for Storefront 2.0 Engine
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork Design Technology West

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit
"""

# pyRevit metadata variables
__title__ = "Storefront 2.0 GUI"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "Find Another"
__parameters__ = []

# standard modules
import sys # noqa E402
try:
    sys.path.append(r"C:\Program Files (x86)\IronPython 2.7\Lib")
except:
    sys.path.append(r"C:\Program Files\IronPython 2.7\Lib")

import clr # noqa E402
import os # noqa E402
import pyrevit # noqa E402
import rpw # noqa E402
import System # noqa E402
import tempfile # noqa E402

from System import DateTime as dt

# windows forms modules
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
from System import Array # noqa E402
import System.Drawing # noqa E402
import System.Windows.Forms # noqa E402
from System.Drawing import * # noqa E402
from System.Windows.Forms import * # noqa E402

# Revit API modules
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402

# SF2 modules
import SF2_Families_CleanUp as SFF # noqa E402

class SF_Dialogue(Form):
    def __init__(self, doc=None, **kwargs):
        self.InitializeComponent()

        # input parameters
        self.doc = doc

        # family object to load from SF2_Families module
        self.familyObj = SFF.FamilyTools(self.doc)

        # gui options inherited from SF2_Families
        self.GUI_levelNames = kwargs.values()[0] # kwargs for keyed arguments can be anything in the future
        self.GUI_SFSystemOptions = self.familyObj.GUI_SFSystemOptions
        self.GUI_heightOptions = self.familyObj.GUI_heightOptions     
        self.GUI_divisionOptions = self.familyObj.GUI_divisionOptions      
        self.GUI_panelWidthOptions = self.familyObj.GUI_panelWidthOptions
        self.GUI_nibWallOptions = self.familyObj.GUI_nibWallOptions
        self.GUI_nibWallLengthOptions = self.familyObj.GUI_nibWallLengthOptions

        # family and file paths for families
        self.defaultConfigPath = self.familyObj.defaultConfigPath
        self.familyDirectory = self.familyObj.familyDirectory
        self.familiesToLoad = self.familyObj.currentConfig

        # derived parameters
        self.defaultSystem = None
        self.defaultHeight = None
        self.defaultDivOption = None
        self.defaultWidthOption = None
        self.defaultSplitWallOption = None
        self.defaultNibWallTypeOption = None

    def InitializeComponent(self):
        self._label0 = System.Windows.Forms.Label()
        self._checkedListBox1 = System.Windows.Forms.CheckedListBox()
        self._label1 = System.Windows.Forms.Label()
        self._label2 = System.Windows.Forms.Label()
        self._checkBox1 = System.Windows.Forms.CheckBox()
        self._button1 = System.Windows.Forms.Button()
        self._textBox1 = System.Windows.Forms.TextBox()
        self._comboBox1 = System.Windows.Forms.ComboBox()
        self._comboBox2 = System.Windows.Forms.ComboBox()
        self._comboBox4 = System.Windows.Forms.ComboBox()
        self._label3 = System.Windows.Forms.Label()
        self._comboBox5 = System.Windows.Forms.ComboBox()
        self._label4 = System.Windows.Forms.Label()
        self._textBox2 = System.Windows.Forms.TextBox()
        self._label5 = System.Windows.Forms.Label()
        self._label6 = System.Windows.Forms.Label()
        self._comboBox3 = System.Windows.Forms.ComboBox()
        self._textBox3 = System.Windows.Forms.TextBox()
        self.SuspendLayout()
        # 
        # pickLevels_Label
        # 
        self._label0.Location = System.Drawing.Point(12, 9)
        self._label0.Name = "pickLevels_Label"
        self._label0.Size = System.Drawing.Size(100, 23)
        self._label0.TabIndex = 19
        self._label0.Text = "PICK LEVELS"
        # 
        # pickLevels_checkedListBox
        # 
        self._checkedListBox1.FormattingEnabled = True
        self._checkedListBox1.Location = System.Drawing.Point(12, 35)
        self._checkedListBox1.Name = "pickLevels_checkedListBox"
        self._checkedListBox1.Size = System.Drawing.Size(245, 94)
        self._checkedListBox1.TabIndex = 18
        # 
        # label1
        # 
        self._label1.Location = System.Drawing.Point(12, 139)
        self._label1.Name = "label1"
        self._label1.Size = System.Drawing.Size(100, 23)
        self._label1.TabIndex = 0
        self._label1.Text = "PICK SYSTEM"
        self._label1.Click += self.Label1Click
        # 
        # label2
        # 
        self._label2.Location = System.Drawing.Point(12, 182)
        self._label2.Name = "label2"
        self._label2.Size = System.Drawing.Size(100, 23)
        self._label2.TabIndex = 1
        self._label2.Text = "HEAD HEIGHT"
        # 
        # checkBox1
        # 
        self._checkBox1.Location = System.Drawing.Point(12, 352)
        self._checkBox1.Name = "checkBox1"
        self._checkBox1.Size = System.Drawing.Size(185, 24)
        self._checkBox1.TabIndex = 2
        self._checkBox1.Text = "ADD NIB WALLS"
        self._checkBox1.UseVisualStyleBackColor = True
        self._checkBox1.CheckedChanged += self.CheckBox1CheckedChanged
        # 
        # button1
        # 
        self._button1.Location = System.Drawing.Point(12, 418)
        self._button1.Name = "button1"
        self._button1.Size = System.Drawing.Size(245, 23)
        self._button1.TabIndex = 3
        self._button1.Text = "GO"
        self._button1.UseVisualStyleBackColor = True
        # 
        # textBox1
        # 
        self._textBox1.Location = System.Drawing.Point(182, 382)
        self._textBox1.Name = "textBox1"
        self._textBox1.Size = System.Drawing.Size(75, 20)
        self._textBox1.TabIndex = 5
        # 
        # comboBox1
        # 
        self._comboBox1.FormattingEnabled = True
        self._comboBox1.Location = System.Drawing.Point(12, 153)
        self._comboBox1.Name = "comboBox1"
        self._comboBox1.Size = System.Drawing.Size(245, 21)
        self._comboBox1.TabIndex = 6
        # 
        # comboBox2
        # 
        self._comboBox2.FormattingEnabled = True
        self._comboBox2.Location = System.Drawing.Point(12, 198)
        self._comboBox2.Name = "comboBox2"
        self._comboBox2.Size = System.Drawing.Size(159, 21)
        self._comboBox2.TabIndex = 7
        # 
        # comboBox4
        # 
        self._comboBox4.FormattingEnabled = True
        self._comboBox4.Location = System.Drawing.Point(12, 259)
        self._comboBox4.Name = "comboBox4"
        self._comboBox4.Size = System.Drawing.Size(245, 21)
        self._comboBox4.TabIndex = 10
        # 
        # label3
        # 
        self._label3.Location = System.Drawing.Point(12, 243)
        self._label3.Name = "label3"
        self._label3.Size = System.Drawing.Size(100, 23)
        self._label3.TabIndex = 9
        self._label3.Text = "DIVISION TYPE"
        # 
        # comboBox5
        # 
        self._comboBox5.FormattingEnabled = True
        self._comboBox5.Location = System.Drawing.Point(12, 305)
        self._comboBox5.Name = "comboBox5"
        self._comboBox5.Size = System.Drawing.Size(159, 21)
        self._comboBox5.TabIndex = 12
        # 
        # label4
        # 
        self._label4.Location = System.Drawing.Point(12, 289)
        self._label4.Name = "label4"
        self._label4.Size = System.Drawing.Size(100, 23)
        self._label4.TabIndex = 11
        self._label4.Text = "DIVISION WIDTH"
        # 
        # textBox2
        # 
        self._textBox2.Location = System.Drawing.Point(182, 199)
        self._textBox2.Name = "textBox2"
        self._textBox2.Size = System.Drawing.Size(75, 20)
        self._textBox2.TabIndex = 13
        # 
        # label5
        # 
        self._label5.Location = System.Drawing.Point(12, 326)
        self._label5.Name = "label5"
        self._label5.Size = System.Drawing.Size(252, 23)
        self._label5.TabIndex = 14
        self._label5.Text = "_______________________________________________________"
        self._label5.Click += self.Label5Click
        # 
        # label6
        # 
        self._label6.Location = System.Drawing.Point(12, 220)
        self._label6.Name = "label6"
        self._label6.Size = System.Drawing.Size(252, 23)
        self._label6.TabIndex = 15
        self._label6.Text = "_______________________________________________________"
        # 
        # comboBox3
        # 
        self._comboBox3.FormattingEnabled = True
        self._comboBox3.Location = System.Drawing.Point(12, 382)
        self._comboBox3.Name = "comboBox3"
        self._comboBox3.Size = System.Drawing.Size(159, 21)
        self._comboBox3.TabIndex = 16
        # 
        # textBox3
        # 
        self._textBox3.Location = System.Drawing.Point(182, 305)
        self._textBox3.Name = "textBox3"
        self._textBox3.Size = System.Drawing.Size(75, 20)
        self._textBox3.TabIndex = 17
        # 
        # SF_Dialogue
        # 
        self.BackColor = System.Drawing.Color.FromArgb(255, 255, 255)
        self.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Center
        self.ClientSize = System.Drawing.Size(270, 457)
        self.Controls.Add(self._label0)
        self.Controls.Add(self._checkedListBox1)
        self.Controls.Add(self._textBox3)
        self.Controls.Add(self._comboBox3)
        self.Controls.Add(self._label6)
        self.Controls.Add(self._label5)
        self.Controls.Add(self._textBox2)
        self.Controls.Add(self._comboBox5)
        self.Controls.Add(self._label4)
        self.Controls.Add(self._comboBox4)
        self.Controls.Add(self._label3)
        self.Controls.Add(self._comboBox2)
        self.Controls.Add(self._comboBox1)
        self.Controls.Add(self._textBox1)
        self.Controls.Add(self._button1)
        self.Controls.Add(self._checkBox1)
        self.Controls.Add(self._label2)
        self.Controls.Add(self._label1)
        self.Name = "SF_Dialogue"
        self.Text = "Storefront 2 Beta"
        self.ResumeLayout(False)
        self.PerformLayout()

    def Label1Click(self, sender, e):
        pass

    def CheckBox1CheckedChanged(self, sender, e):
        pass

    def CheckBox2CheckedChanged(self, sender, e):
        pass

    def Label5Click(self, sender, e):
        pass

if __name__ == "__main__":
    # test, will not run if imported by another file
    formObj = SF_Dialogue()
    Application.Run(formObj)
    print(formObj.jsonPathList)
    print(formObj.selectedItem)