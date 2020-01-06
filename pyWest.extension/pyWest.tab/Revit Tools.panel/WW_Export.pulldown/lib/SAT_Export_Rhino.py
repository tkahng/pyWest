# imports for Windows Form
import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
from System import Array # convert .net arrays to python lists
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import *

class Form1(Form):
    def __init__(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        resources = System.Resources.ResourceManager("Form1", System.Reflection.Assembly.GetEntryAssembly())
        self._pictureBox1 = System.Windows.Forms.PictureBox()
        self._pictureBox1.BeginInit()
        self.SuspendLayout()
        # 
        # pictureBox1
        # 
        self._pictureBox1.Image = resources.GetObject(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\Revit Tools.panel\WW_Export.pulldown\Rhino_VDCw.png")
        self._pictureBox1.Location = System.Drawing.Point(74, 59)
        self._pictureBox1.Name = "pictureBox1"
        self._pictureBox1.Size = System.Drawing.Size(255, 66)
        self._pictureBox1.TabIndex = 0
        self._pictureBox1.TabStop = False
        # 
        # Form1
        # 
        self.BackColor = System.Drawing.Color.White
        self.ClientSize = System.Drawing.Size(400, 200)
        self.Controls.Add(self._pictureBox1)
        self.Font = System.Drawing.Font("Roboto", 8.25, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, 0)
        self.Name = "Form1"
        self.Text = "VDC.w"
        self._pictureBox1.EndInit()
        self.ResumeLayout(False)


if __name__ == "__main__":
    # test, will not run if imported by another file
    Application.Run(Form1())
