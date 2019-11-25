# imports for Windows Form
import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

import System.Drawing
import System.Windows.Forms

from System.Drawing import *
from System.Windows.Forms import *

class WorksharingWarning(Form):
	"""
	The Form parameter in Form1 comes from System namespace
	"""
	def __init__(self):
		self.InitializeComponent()
	
	def InitializeComponent(self):
		self._textWarning = System.Windows.Forms.Label()
		self._OKbutton = System.Windows.Forms.Button()
		self.SuspendLayout()
		# 
		# textWarning
		# 
		self._textWarning.Location = System.Drawing.Point(12, 27)
		self._textWarning.Name = "textWarning"
		self._textWarning.Size = System.Drawing.Size(251, 18)
		self._textWarning.AutoSize = False
		self._textWarning.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		self._textWarning.TabIndex = 1
		self._textWarning.Text = "Revit model must be worksharing enabled!"
		# 
		# OKbutton
		# 
		self._OKbutton.Location = System.Drawing.Point(99, 63)
		self._OKbutton.Name = "OKbutton"
		self._OKbutton.Size = System.Drawing.Size(75, 23)
		self._OKbutton.TabIndex = 0
		self._OKbutton.Text = "OK"
		self._OKbutton.UseVisualStyleBackColor = True
		self._OKbutton.Click += self.EventOKbutton
		# 
		# WorksharingWarning
		# 
		self.BackColor = System.Drawing.Color.FromArgb(255, 255, 255)
		self.ClientSize = System.Drawing.Size(275, 98)
		self.Controls.Add(self._OKbutton)
		self.Controls.Add(self._textWarning)
		self.Name = "WorksharingWarning"
		self.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
		self.Text = "Revit Tools"
		self.ResumeLayout(False)


	def EventOKbutton(self, sender, e):
		self.Close()

if __name__ == "__main__":
	formObj = WorksharingWarning()
	Application.Run(formObj)
