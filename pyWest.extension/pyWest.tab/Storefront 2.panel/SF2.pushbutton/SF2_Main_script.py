"""
:tooltip:
Module for initializin Storefront 2.0
TESTED REVIT API: 2017, 2019
:tooltip:

Copyright (c) 2016-2019 WeWork Design Technology West

--------------------------------------------------------
PyRevit Notice:
Copyright (c) 2014-2016 Ehsan Iran-Nejad
pyRevit: repository at https://github.com/eirannejad/pyRevit
"""

# pyRevit metadata variables
__title__ = "Storefront 2.0"
__author__ = "WeWork Design Technology West - Alvaro Luna"
__helpurl__ = "google.com"
__min_revit_ver__ = 2017
__max_revit_ver__ = 2019
__version__ = "2.0"

# WW private global variables | https://www.uuidgenerator.net/version4
__uiud__ = "045ff863-7897-44ba-b728-535eeac05bf4"
__parameters__ = []

# standard modules
import os # noqa E402
import sys # noqa E402
import traceback # noqa E402

#from logging import log # noqa E402
#log(__file__)

# SF2 modules
import SF2_Engine as SFE # noqa E402

try:
    #@helpers.log_analytics
    def Main():
        SFE.GenerateSF().Run_GenerateSF()

    if __name__ == "__main__": 
        Main()
except:
    # print traceback in order to debug file
    print(traceback.format_exc())