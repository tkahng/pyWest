"""
:tooltip:
GUI Module for Storefront 2.0
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2020 WeWork Design Technology West
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

class Form1(Form):
    def __init__(self, doc, **kwargs):

        # input parameters
        self.doc = doc

        # input kwarg parameters
        if kwargs.items():
            for i, (key, value) in enumerate(kwargs.items()): 
                if key == "levelNames":
                    self.GUI_levelNames = kwargs.values()[i] # kwargs for keyed arguments can be anything in the future
                    print(self.GUI_levelNames)
                if key == "gypWallOptions":
                    #                         SF2_Engine.gypWallDict
                    self.GUI_nibWallOptions = kwargs.values()[i]
                if key == "loadedFamilies":
                    self.GUI_loadedFamilies = kwargs.values()[i]

        # family object to load from SF2_Families module
        self.familyObj = SFF.FamilyTools(self.doc)

        # gui options inherited from SF2_Families
        self.GUI_SF_systemOptions = self.familyObj.GUI_SF_systemOptions
        self.GUI_SF_heightOptions = self.familyObj.GUI_SF_heightOptions     
        self.GUI_SF_divisionOptions = self.familyObj.GUI_SF_divisionOptions      
        self.GUI_SF_panelWidthOptions = self.familyObj.GUI_SF_panelWidthOptions
        self.GUI_nibWallLengthOptions = self.familyObj.GUI_nibWallLengthOptions        

        # default options for GUI dropdowns
        self.components = None

        self.defaultSystem = None
        self.defaultHeight = None
        self.defaultDivOption = None
        self.defaultWidthOption = None
        self.defaultNibWallOption = None
        self.defaultNibWallLengthOption = None

        ############################
        ## SetFormOutputs outputs ##
        ############################
        self.selectedSystem = None
        self.headHeight = None
        self.partialHeadHeight = None

        self.spacingType = None
        self.storefrontPaneWidth = None
        self.createNibWall = None
        self.nibWallType = None
        self.nibWallLength = None

        # inherit empty self.currentConfig dict to begin writing data to it in this module
        # default, or last selected settings
        self.currentConfig = self.familyObj.currentConfig

        # outputs - used seperately from json files that are written, more flexible
        self.userConfigs = None        

        # loads previously saved currentConfig!
        # if an error points to this location, comment this out, run again to save another json
        # file, then uncomment this again and start over...
        self.familyObj.JSONLoadConfig()
        self.InitializeComponent()
    def InitializeComponent(self):
        resources = System.Resources.ResourceManager("Form1", System.Reflection.Assembly.GetEntryAssembly())
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
        self._comboBox3 = System.Windows.Forms.ComboBox()
        self._textBox3 = System.Windows.Forms.TextBox()
        self._checkBox2 = System.Windows.Forms.CheckBox()
        self._label7 = System.Windows.Forms.Label()
        self.SuspendLayout()
        # 
        # label0
        # 
        self._label0.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, 0)
        self._label0.Location = System.Drawing.Point(23, 110)
        self._label0.Name = "label0"
        self._label0.Size = System.Drawing.Size(100, 14)
        self._label0.TabIndex = 19
        self._label0.Text = "PICK LEVELS"
        # 
        # checkedListBox1
        # 
        self._checkedListBox1.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._checkedListBox1.FormattingEnabled = True
        self._checkedListBox1.Location = System.Drawing.Point(23, 136)
        self._checkedListBox1.Name = "checkedListBox1"
        self._checkedListBox1.Size = System.Drawing.Size(245, 76)
        self._checkedListBox1.Sorted = True
        self._checkedListBox1.TabIndex = 18
        # 
        # label1
        # 
        self._label1.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, 0)
        self._label1.Location = System.Drawing.Point(23, 221)
        self._label1.Name = "label1"
        self._label1.Size = System.Drawing.Size(116, 15)
        self._label1.TabIndex = 0
        self._label1.Text = "SELECT SYSTEM"
        self._label1.Click += self.Label1Click
        # 
        # label2
        # 
        self._label2.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._label2.Location = System.Drawing.Point(23, 270)
        self._label2.Name = "label2"
        self._label2.Size = System.Drawing.Size(100, 21)
        self._label2.TabIndex = 1
        self._label2.Text = "Head Height"
        # 
        # checkBox1
        # 
        self._checkBox1.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._checkBox1.Location = System.Drawing.Point(23, 46)
        self._checkBox1.Name = "checkBox1"
        self._checkBox1.Size = System.Drawing.Size(117, 26)
        self._checkBox1.TabIndex = 2
        self._checkBox1.Text = "Add Nib Walls"
        self._checkBox1.UseVisualStyleBackColor = True
        self._checkBox1.CheckedChanged += self.CheckBox1CheckedChanged
        # 
        # button1
        # 
        self._button1.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, 0)
        self._button1.Location = System.Drawing.Point(23, 429)
        self._button1.Name = "button1"
        self._button1.Size = System.Drawing.Size(245, 23)
        self._button1.TabIndex = 3
        self._button1.Text = "GO"
        self._button1.UseVisualStyleBackColor = True
        # 
        # textBox1
        # 
        self._textBox1.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._textBox1.Location = System.Drawing.Point(193, 79)
        self._textBox1.Name = "textBox1"
        self._textBox1.Size = System.Drawing.Size(75, 23)
        self._textBox1.TabIndex = 5
        # 
        # comboBox1
        # 
        self._comboBox1.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._comboBox1.FormattingEnabled = True
        self._comboBox1.Location = System.Drawing.Point(23, 239)
        self._comboBox1.Name = "comboBox1"
        self._comboBox1.Size = System.Drawing.Size(245, 23)
        self._comboBox1.TabIndex = 6
        # 
        # comboBox2
        # 
        self._comboBox2.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._comboBox2.FormattingEnabled = True
        self._comboBox2.Location = System.Drawing.Point(23, 286)
        self._comboBox2.Name = "comboBox2"
        self._comboBox2.Size = System.Drawing.Size(159, 23)
        self._comboBox2.TabIndex = 7
        # 
        # comboBox4
        # 
        self._comboBox4.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._comboBox4.FormattingEnabled = True
        self._comboBox4.Location = System.Drawing.Point(23, 340)
        self._comboBox4.Name = "comboBox4"
        self._comboBox4.Size = System.Drawing.Size(245, 23)
        self._comboBox4.TabIndex = 10
        # 
        # label3
        # 
        self._label3.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._label3.Location = System.Drawing.Point(23, 324)
        self._label3.Name = "label3"
        self._label3.Size = System.Drawing.Size(100, 13)
        self._label3.TabIndex = 9
        self._label3.Text = "Division Type"
        # 
        # comboBox5
        # 
        self._comboBox5.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._comboBox5.FormattingEnabled = True
        self._comboBox5.Location = System.Drawing.Point(23, 386)
        self._comboBox5.Name = "comboBox5"
        self._comboBox5.Size = System.Drawing.Size(159, 23)
        self._comboBox5.TabIndex = 12
        # 
        # label4
        # 
        self._label4.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._label4.Location = System.Drawing.Point(23, 370)
        self._label4.Name = "label4"
        self._label4.Size = System.Drawing.Size(100, 13)
        self._label4.TabIndex = 11
        self._label4.Text = "Division Width"
        # 
        # textBox2
        # 
        self._textBox2.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._textBox2.Location = System.Drawing.Point(193, 287)
        self._textBox2.Name = "textBox2"
        self._textBox2.Size = System.Drawing.Size(75, 23)
        self._textBox2.TabIndex = 13
        # 
        # comboBox3
        # 
        self._comboBox3.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._comboBox3.FormattingEnabled = True
        self._comboBox3.Location = System.Drawing.Point(23, 79)
        self._comboBox3.Name = "comboBox3"
        self._comboBox3.Size = System.Drawing.Size(159, 23)
        self._comboBox3.TabIndex = 16
        # 
        # textBox3
        # 
        self._textBox3.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._textBox3.Location = System.Drawing.Point(193, 386)
        self._textBox3.Name = "textBox3"
        self._textBox3.Size = System.Drawing.Size(75, 23)
        self._textBox3.TabIndex = 17
        # 
        # checkBox2
        # 
        self._checkBox2.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, 0)
        self._checkBox2.Location = System.Drawing.Point(23, 24)
        self._checkBox2.Name = "checkBox2"
        self._checkBox2.Size = System.Drawing.Size(116, 26)
        self._checkBox2.TabIndex = 20
        self._checkBox2.Text = "Nib Walls Only"
        self._checkBox2.UseVisualStyleBackColor = True
        # 
        # label7
        # 
        self._label7.Font = System.Drawing.Font("Karla", 9.749999, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, 0)
        self._label7.Location = System.Drawing.Point(23, 8)
        self._label7.Name = "label7"
        self._label7.Size = System.Drawing.Size(100, 13)
        self._label7.TabIndex = 21
        self._label7.Text = "NIB WALLS"
        # 
        # Form1
        # 
        self.BackColor = System.Drawing.Color.FromArgb(255, 255, 255)
        self.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Center
        self.ClientSize = System.Drawing.Size(294, 471)
        self.Controls.Add(self._label7)
        self.Controls.Add(self._checkBox2)
        self.Controls.Add(self._label0)
        self.Controls.Add(self._checkedListBox1)
        self.Controls.Add(self._textBox3)
        self.Controls.Add(self._comboBox3)
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
        self.Icon = resources.GetObject("$this.Icon")
        self.Name = "Form1"
        self.Text = "Storefront 2"
        self.Load += self.SF_DialogueLoad
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

    def SF_DialogueLoad(self, sender, e):
        pass

#if __name__ == "__main__":
#    # test, will not run if imported by another file
#    formObj = Form1()
#    Application.Run(formObj)
#    print(formObj.jsonPathList)
#    print(formObj.selectedItem)

