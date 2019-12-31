"""


Module for storefront tool menus.
TESTED REVIT API: 2015, 2016

Copyright (c) 2016-2017 WeWork

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit

"""

try:
    import clr
    import os
    import logging
    import __main__

    logger = logging.getLogger()

    # Verify these are needed.
    clr.AddReference('System')
    clr.AddReference('System.Drawing')
    clr.AddReference('System.Windows.Forms')

    #  Windows Forms Elements
    from System.Drawing import *
    from System.Drawing import Icon
    from System.Drawing import Point
    from System.Windows.Forms import *
    from System.Windows.Forms import View as winView
    from System.Windows.Forms import Form
    from System.Windows.Forms import Application, Form, CheckBox, Form, Label
    from System.Windows.Forms import DialogResult, GroupBox, FormBorderStyle
    from System.Windows.Forms import ComboBox, Button, DialogResult, SaveFileDialog

    UserName = []
    UserPass = []
    SelectedItem = []

    # create a link to the wework icon
    # just add self.Icon = icon to your form
    scriptDirectory = os.path.dirname(__main__.__file__)
    iconFilename = os.path.join(scriptDirectory, 'wework_we.ico')
    logoFilename = os.path.join(scriptDirectory, 'wework_logo.png')
    icon = Icon(iconFilename)
    logo = Bitmap(logoFilename)

    class FlexibleDropDownMenu(Form):
        """
        This menu expands and contracts based on the number of dictionaries
        that it is given. A list of headings provides labels for each dropdown
        and default values are the keys which you want to be default for each
        dropdown.
        """
        def __init__(self, dropDownDictList, dropDownHeadings, defaultValues=[], sort=True):

            topOffset = 20
            spacing = 45

            # Create the Form
            self.Name = "ListBox"
            self.Text = "pyWeWork"
            self.FormBorderStyle = FormBorderStyle.Sizable
            self.Icon = icon
            self.CenterToScreen()
            self.values = []
            self.dropDownDictList = dropDownDictList
            self.dropDownHeadings = dropDownHeadings
            self.defaultValues = defaultValues
            self.comboBoxes = []
            self.labels = []
            self.Size = Size(500, spacing*len(self.dropDownHeadings) + (topOffset + 75))

            titleFont =  Font("Arial",10, FontStyle.Bold)
            menuFont = Font("Arial",8, FontStyle.Bold)

            self.label = Label()
            self.label.Text = "SELECT PARAMETERS"
            self.label.Font = titleFont
            self.label.Location = Point(10, 10)
            self.label.AutoSize = True
            
            for index in range(len(self.dropDownDictList)):
                dropDownDict = self.dropDownDictList[index]
                if sort:
                    dictKeys = sorted(dropDownDict.keys())
                    dictValues = sorted(dropDownDict.values())
                else:
                    dictKeys = dropDownDict.keys()
                    dictValues = dropDownDict.values()
                
                self.comboBoxes.append(ComboBox())
                for item in dictKeys:
                    self.comboBoxes[index].Items.Add(item)
                self.comboBoxes[index].Location = Point(15, (spacing*index) + topOffset)
                self.comboBoxes[index].Width = 250
                if self.defaultValues:
                    selectedIndex = 0
                    for key in dictKeys:
                        defaultVal = self.defaultValues[index]
                        if dropDownDict[key] == defaultVal:
                            selectedIndex = dictKeys.index(key)
                    self.comboBoxes[index].SelectedIndex = selectedIndex
                self.labels.append(Label())
                self.labels[index].Text = self.dropDownHeadings[index]
                self.labels[index].Font = menuFont
                self.labels[index].Width = 100
                self.labels[index].AutoSize = True
                self.labels[index].Location = Point(280, (spacing*index) + topOffset + 2)
                self.Controls.Add(self.labels[index])
                self.Controls.Add(self.labels[index])
                self.Controls.Add(self.comboBoxes[index])

            self.button = Button()
            self.button.Text = "GO"
            self.button.Size = Size(0, 40)
            self.button.Dock = DockStyle.Bottom
            
            # Register event
            self.button.Click += self.ButtonClicked


            self.Controls.Add(self.button)

        def ButtonClicked(self, sender, args):
            if sender.Click:
                for index in range(len(self.dropDownDictList)):
                    dict = self.dropDownDictList[index]
                    self.values.append(dict[self.comboBoxes[index].SelectedItem])
                self.Close()

        def TestMain():
            # run form
            FlexibleDropDownMenu()

        if __name__ == "__main__":
            TestMain()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())        
