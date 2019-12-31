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
__title__ = "Rename Elements GUI"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "Find Another"
__parameters__ = []

# standard modules
import clr # noqa E402
import os # noqa E402
import pyrevit # noqa E402
import rpw # noqa E402
import sys # noqa E402
import System # noqa E402
import tempfile # noqa E402

from System import DateTime as dt # noqa E402

##########################
## RENAME ELEMENTS FORM ##
##########################
class RE_Form:
    def __init__(self, **kwargs):
        pass

    def SetFormComponents(self):
        from rpw.ui.forms import Button, CheckBox, Label, Separator, TextBox # why does this have to be inside method?
        self.components = [CheckBox("checkbox1", "VIEWS", default=False),
                           CheckBox("checkbox2", "SHEETS", default=False),
                           CheckBox("checkbox3", "ROOMS", default=False),
                           
                           Label("SEARCH TEXT"),
                           TextBox("textbox1"),
                           
                           Label("TARGET TEXT"),
                           TextBox("textbox2"),
                      
                           Separator(),
                           Button('Go')
                           ]  
        
    def SetFormOutputs(self, form):
        if not form.values:
            # better than sys.exit()
            pyrevit.script.exit()
        
        else:
            #print(form.values)
            self.viewsBoolean = form.values["checkbox1"]
            self.sheetsBoolean = form.values["checkbox2"]
            self.roomsBoolean = form.values["checkbox3"]
            self.searchString = form.values["textbox1"]
            self.targetString = form.values["textbox2"]
    
    def Run_Form(self):
        from rpw.ui.forms import FlexForm
        # create form object and add elements to it
        self.SetFormComponents()
        
        # Create Menu
        form = FlexForm("RENAME ELEMENTS", self.components)
        form.show()
        
        # set form outputs
        self.SetFormOutputs(form)