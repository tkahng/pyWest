# pyRevit metadata variables
__title__ = "Storefront 2.0 Families"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "find new one"
__parameters__ = []

# standard modules
import json # noqa E402
import sys # noqa E402
import os # noqa E402
import System # noqa E402

from System import DateTime as dt # noqa E402

# Revit API modules
import clr # noqa E402
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk # noqa E402
from Autodesk.Revit.UI import * # noqa E402
from Autodesk.Revit.DB import * # noqa E402
import tempfile # noqa E402
import rpw # noqa E402

# DT West modules
import SF2_Utility # noqa E402

class FamilyConfig:
    def __init__(self):
        self.familySavePath = r""
        self.familyDict = {}

class FamilyLoadProcess:
    """
    Only one family at a time is processed
    """
    def __init__(self):
        pass
    def IsFamilyLoaded(self, familyName):
        pass
    def CheckFamilyTypes(self):
        pass
    def OpenFamily(self):
        pass
    def LoadFamily(self):
        pass
    def Run_FamilyLoadProcess(self):
        pass
        # does family exist in doc?
        
        # if False, load family
        
        # does family have correct type?
        
        # if False, does it have any type?
            # if True, use duplicate method to create required familyTypes
                # write types with parameters
            # if False, open family editor of family in question to create required types
                # write types with parameters

class DerivedClass(FamilyConfig, FamilyLoadProcess):
    def __init__(self):
        FamilyConfig.__init__(self)
        FamilyLoadProcess.__init__(self)

def TestMain():
    familyObj = DerivedClass()
    FamilyObj.Run_FamilyLoadProcess()

if __name__ == "__main__":
    TestMain()