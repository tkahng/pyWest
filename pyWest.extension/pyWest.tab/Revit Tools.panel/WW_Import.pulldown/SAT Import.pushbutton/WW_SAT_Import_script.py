"""
TESTED IN REVIT 2017

This script effectively explodes geometry
by extracting the base surfaces from the
geometry and adding them back to the document

namespace ImportSAT_Rhino
public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)

OOP:
method(): action; method: property
"""

# WW Import module
import WW_SAT_Import_Engine as WWSIE

def Main():
    WWSIE.ImportSAT_Rhino(1).Run_ImportSAT_Rhino()

if __name__ == "__main__":
    Main()