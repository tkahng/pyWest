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
try:
    jsonPath = r"C:\Program Files (x86)\IronPython 2.7\Lib"
except:
    jsonPath = r"C:\Program Files\IronPython 2.7\Lib"
sys.path.append(jsonPath)
import json
import traceback
import os


import SF2_Utility
import SF2_Families

class SF_Dialogue(Form):
        def __init__(self):
                self.InitializeComponent()

                # input parameters
                self.doc = doc

                # family object to load from SF2_Families module
                self.familyObj = SF2_Families.FamilyStuff(self.doc)

                # file paths
                self.defaultConfigPath = self.familyObj.defaultConfigPath
                self.familyDirectory = self.familyObj.familyDirectory

                self.familiesToLoad = self.familyObj.currentConfig

                # THIS IS THE MAIN OUTPUT THAT IS USED BY SF2_ENGINE
                self.currentConfig = self.familyObj.currentConfig # default, or last selected settings

                # WHAT IS USING THIS???
                self.familyObj.json_load_config()

                self.availableSystems = self.familyObj.availableSystems
                self.heightOptions = self.familyObj.heightOptions     
                self.divisionOptions = self.familyObj.divisionOptions      
                self.panelWidthOptions = self.familyObj.panelWidthOptions
                self.splitTypeOptions = self.familyObj.splitTypeOptions
                self.doorDict = self.familyObj.doorDict

        def InitializeComponent(self):
                self._label1 = System.Windows.Forms.Label()
                self._label2 = System.Windows.Forms.Label()
                self._checkBox1 = System.Windows.Forms.CheckBox()
                self._button1 = System.Windows.Forms.Button()
                self._checkBox2 = System.Windows.Forms.CheckBox()
                self._textBox1 = System.Windows.Forms.TextBox()
                self._comboBox1 = System.Windows.Forms.ComboBox()
                self._comboBox2 = System.Windows.Forms.ComboBox()
                self._comboBox4 = System.Windows.Forms.ComboBox()
                self._label3 = System.Windows.Forms.Label()
                self._comboBox5 = System.Windows.Forms.ComboBox()
                self._label4 = System.Windows.Forms.Label()
                self._textBox2 = System.Windows.Forms.TextBox()
                self._label5 = System.Windows.Forms.Label()
                self.SuspendLayout()
                # 
                # label1
                # 
                self._label1.Location = System.Drawing.Point(12, 9)
                self._label1.Name = "label1"
                self._label1.Size = System.Drawing.Size(100, 23)
                self._label1.TabIndex = 0
                self._label1.Text = "PICK SYSTEM"
                self._label1.Click += self.Label1Click
                # 
                # label2
                # 
                self._label2.Location = System.Drawing.Point(12, 52)
                self._label2.Name = "label2"
                self._label2.Size = System.Drawing.Size(100, 23)
                self._label2.TabIndex = 1
                self._label2.Text = "HEAD HEIGHT"
                # 
                # checkBox1
                # 
                self._checkBox1.Location = System.Drawing.Point(12, 229)
                self._checkBox1.Name = "checkBox1"
                self._checkBox1.Size = System.Drawing.Size(185, 24)
                self._checkBox1.TabIndex = 2
                self._checkBox1.Text = "ADD NIB WALLS"
                self._checkBox1.UseVisualStyleBackColor = True
                self._checkBox1.CheckedChanged += self.CheckBox1CheckedChanged
                # 
                # button1
                # 
                self._button1.Location = System.Drawing.Point(182, 306)
                self._button1.Name = "button1"
                self._button1.Size = System.Drawing.Size(75, 23)
                self._button1.TabIndex = 3
                self._button1.Text = "GO"
                self._button1.UseVisualStyleBackColor = True
                # 
                # checkBox2
                # 
                self._checkBox2.Location = System.Drawing.Point(12, 100)
                self._checkBox2.Name = "checkBox2"
                self._checkBox2.Size = System.Drawing.Size(117, 24)
                self._checkBox2.TabIndex = 4
                self._checkBox2.Text = "TRANSOM"
                self._checkBox2.UseVisualStyleBackColor = True
                self._checkBox2.CheckedChanged += self.CheckBox2CheckedChanged
                # 
                # textBox1
                # 
                self._textBox1.Location = System.Drawing.Point(182, 231)
                self._textBox1.Name = "textBox1"
                self._textBox1.Size = System.Drawing.Size(75, 20)
                self._textBox1.TabIndex = 5
                # 
                # comboBox1
                # 
                self._comboBox1.FormattingEnabled = True
                self._comboBox1.Location = System.Drawing.Point(12, 23)
                self._comboBox1.Name = "comboBox1"
                self._comboBox1.Size = System.Drawing.Size(245, 21)
                self._comboBox1.TabIndex = 6
                # 
                # comboBox2
                # 
                self._comboBox2.FormattingEnabled = True
                self._comboBox2.Location = System.Drawing.Point(12, 68)
                self._comboBox2.Name = "comboBox2"
                self._comboBox2.Size = System.Drawing.Size(245, 21)
                self._comboBox2.TabIndex = 7
                # 
                # comboBox4
                # 
                self._comboBox4.FormattingEnabled = True
                self._comboBox4.Location = System.Drawing.Point(12, 153)
                self._comboBox4.Name = "comboBox4"
                self._comboBox4.Size = System.Drawing.Size(245, 21)
                self._comboBox4.TabIndex = 10
                # 
                # label3
                # 
                self._label3.Location = System.Drawing.Point(12, 137)
                self._label3.Name = "label3"
                self._label3.Size = System.Drawing.Size(100, 23)
                self._label3.TabIndex = 9
                self._label3.Text = "DIVISION TYPE"
                # 
                # comboBox5
                # 
                self._comboBox5.FormattingEnabled = True
                self._comboBox5.Location = System.Drawing.Point(12, 199)
                self._comboBox5.Name = "comboBox5"
                self._comboBox5.Size = System.Drawing.Size(245, 21)
                self._comboBox5.TabIndex = 12
                # 
                # label4
                # 
                self._label4.Location = System.Drawing.Point(12, 183)
                self._label4.Name = "label4"
                self._label4.Size = System.Drawing.Size(100, 23)
                self._label4.TabIndex = 11
                self._label4.Text = "DIVISION WIDTH"
                # 
                # textBox2
                # 
                self._textBox2.Location = System.Drawing.Point(182, 100)
                self._textBox2.Name = "textBox2"
                self._textBox2.Size = System.Drawing.Size(75, 20)
                self._textBox2.TabIndex = 13
                # 
                # label5
                # 
                self._label5.Location = System.Drawing.Point(12, 275)
                self._label5.Name = "label5"
                self._label5.Size = System.Drawing.Size(252, 23)
                self._label5.TabIndex = 14
                self._label5.Text = "_______________________________________________________"
                self._label5.Click += self.Label5Click
                # 
                # SF_Dialogue
                # 
                self.Controls.Add(self._label5)
                self.Controls.Add(self._textBox2)
                self.Controls.Add(self._comboBox5)
                self.Controls.Add(self._label4)
                self.Controls.Add(self._comboBox4)
                self.Controls.Add(self._label3)
                self.Controls.Add(self._comboBox2)
                self.Controls.Add(self._comboBox1)
                self.Controls.Add(self._textBox1)
                self.Controls.Add(self._checkBox2)
                self.Controls.Add(self._button1)
                self.Controls.Add(self._checkBox1)
                self.Controls.Add(self._label2)
                self.Controls.Add(self._label1)
                self.ClientSize = System.Drawing.Size(270, 340)
                self.Name = "SF_Dialogue"
                self.Text = "Storefront 2 Beta"
                self.BackColor = System.Drawing.Color.FromArgb(255, 255, 255)
                self.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Center
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

        def storefront_set_config(self):
                """
                Set configurations and load families.

                THIS IS ALSO IDENTICAL TO STOREFRONT GUI, SO IT WILL BE REPLACED BY THAT...
                """
                # make sure default values are set
                if not self.currentConfig["selectedSystem"] in self.availableSystems .values():
                        defaultSystem = self.availableSystems .keys()[0]
                else:
                        defaultSystem = self.availableSystems .keys()[self.availableSystems .values().index(self.currentConfig["selectedSystem"])]
        
                if not self.currentConfig["headHeight"] in self.heightOptions.values():
                        defaultHeight = self.heightOptions.keys()[0]
                else: 
                        defaultHeight = self.heightOptions.keys()[self.heightOptions.values().index(self.currentConfig["headHeight"])]
        
                if not self.currentConfig["spacingType"] in self.divisionOptions.values():
                        defaultDivOption = self.divisionOptions.keys()[0]
                else:
                        defaultDivOption = self.divisionOptions.keys()[self.divisionOptions.values().index(self.currentConfig["spacingType"])]
        
                if not self.currentConfig["storefrontPaneWidth"] in self.panelWidthOptions.values():
                        defaultWidthOption = self.panelWidthOptions.keys()[0]
                else:
                        defaultWidthOption = self.panelWidthOptions.keys()[self.panelWidthOptions.values().index(self.currentConfig["storefrontPaneWidth"])]
        
                selectedSystem = form.values["combobox1"]
                headHeight = float(form.values["combobox2"])
                partialHeadHeight = float(form.values["combobox2"])
                spacingType = form.values["combobox3"]
                storefrontPaneWidth = float(form.values["combobox4"])
        
                # Load familes
                loadedFamilies = self.familyObj.storefront_load_families(True)
        
                # Save when the config was set.
                projectInfo = self.doc.ProjectInformation
                projectId = projectInfo.Id
                projectName = None
                for p in projectInfo.Parameters:
                        if p.Definition.Name == "Project Name":
                                projectName = p.AsString()
        
                todaysDate = "{0}-{1}-{2}".format(dt.Today.Month, dt.Today.Day, dt.Today.Year)
        
                userConfigs = {"projectName": projectName,
                               "projectId": projectId.IntegerValue,
                               "configDate": todaysDate,
                               "headHeight": headHeight,
                               "storefrontPaneWidth" : storefrontPaneWidth,
                               "spacingType" : spacingType,
                               "families": loadedFamilies,
                               "selectedSystem": selectedSystem}
        
                # IS THIS SAVING WHAT WILL GET LOADED NEXT TIME?
                self.familyObj.storefront_save_config(selectedSystem, userConfigs)


if __name__ == "__main__":
        # test, will not run if imported by another file
        formObj = SF_Dialogue()
        Application.Run(formObj)
        print(formObj.jsonPathList)
        print(formObj.selectedItem)