# imports for Windows Form
import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import *

class LU_Form_Results(Form):
    def __init__(self, stringResults):
        # output from main as initial input
        self.stringResults = stringResults

        self.InitializeComponent()

    def InitializeComponent(self):
					self._label1 = System.Windows.Forms.Label()
					self._exportButton = System.Windows.Forms.Button()
					self._closeButton = System.Windows.Forms.Button()
					self.SuspendLayout()
					# 
					# label1
					# 
					self._label1.AutoSize = True
					self._label1.Location = System.Drawing.Point(27, 9)
					self._label1.MaximumSize = System.Drawing.Size(367, 0)
					self._label1.Name = "label1"
					self._label1.Size = System.Drawing.Size(0, 13)
					self._label1.TabIndex = 2
					self._label1.Text = self.stringResults
					# 
					# exportButton
					# 
					self._exportButton.Location = System.Drawing.Point(238, 94)
					self._exportButton.Name = "exportButton"
					self._exportButton.Size = System.Drawing.Size(75, 23)
					self._exportButton.TabIndex = 1
					self._exportButton.Text = "Export"
					self._exportButton.UseVisualStyleBackColor = True
					# 
					# closeButton
					# 
					self._closeButton.Location = System.Drawing.Point(319, 94)
					self._closeButton.Name = "closeButton"
					self._closeButton.Size = System.Drawing.Size(75, 23)
					self._closeButton.TabIndex = 0
					self._closeButton.Text = "Close"
					self._closeButton.UseVisualStyleBackColor = True
					self._closeButton.Click += self.EventCloseButton
					# 
					# LU_Form_Results
					# 
					self.BackColor = System.Drawing.Color.FromArgb(255, 255, 255)
					self.ClientSize = System.Drawing.Size(431, 138)
					self.Controls.Add(self._label1)
					self.Controls.Add(self._exportButton)
					self.Controls.Add(self._closeButton)
					self.Name = "LU_Form_Results"
					self.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
					self.Text = "LevelUp - Results"
					self.ResumeLayout(False)
					self.PerformLayout()

    def EventCloseButton(self, sender, e):
        # closes windows form
        self.Close()


if __name__ == "__main__":
    # test, will not run if imported by another file
    text = """
    Hello
    World!
    """
    
    Application.Run(LU_Form_Results(text))