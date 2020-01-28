import clr

# windows forms modules
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
from System import Array # noqa E402
import System.Drawing # noqa E402
import System.Windows.Forms # noqa E402
from System.Drawing import * # noqa E402
from System.Windows.Forms import * # noqa E402

class Form1(Form):
	def __init__(self):
		self.InitializeComponent()
	
	def InitializeComponent(self):
		self._button1 = System.Windows.Forms.Button()
		self.SuspendLayout()
		# 
		# button1
		# 
		self._button1.Location = System.Drawing.Point(76, 74)
		self._button1.Name = "button1"
		self._button1.Size = System.Drawing.Size(75, 23)
		self._button1.TabIndex = 0
		self._button1.Text = "button1"
		self._button1.UseVisualStyleBackColor = True
		# 
		# Form1
		# 
		self.ClientSize = System.Drawing.Size(284, 261)
		self.Controls.Add(self._button1)
		self.Name = "Form1"
		self.Text = "Form1"
		self.ResumeLayout(False)

if __name__ == "__main__":
    # test, will not run if imported by another file
    formObj = Form1()
    Application.Run(formObj)
