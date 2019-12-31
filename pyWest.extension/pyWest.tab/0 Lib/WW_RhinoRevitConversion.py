"""
pyVersion = IronPython 2.7xx and Python 3.7xx

"""
import traceback
import os
import sys
import logging
import math

# exclusive IronPython modules
if "2." and "IronPython" in sys.version:
    import clr
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    import Autodesk
    from Autodesk.Revit.UI import *
    from Autodesk.Revit.DB import *
    import Autodesk.Revit.UI.Selection
    
    import System
    from System.Collections.Generic import List, IEnumerable
    from System import Array
    from System import DateTime as dt
    
    sys.path.append(r'C:\Program Files (x86)\IronPython 2.7\Lib')
    import _csv as csv
    import json
    
    rpwLib = r"G:\Shared drives\Prod - BIM\05_Regional\USCI WEST\pyWest_HeavyFiles\Dependencies\revitpythonwrapper-master" # common lib folder
    sys.path.append(rpwLib)
    import rpw
    
    # import Rhinocommon API - C# library
    clr.AddReference(r"Rhino3dmIO.dll")
    import Rhino as rh

# exclusive Python 3 modules
elif "3." in sys.version:
    """
    Rhino will be implemented using Rhino compute and 3dm,
    this will hopefully improve in the near future.
    
    Rhino3dmIO was too limited
    """
    import rhino3dm as rh
    import compute_rhino3d as rc
    import compute_rhino3d.Util as rcu
    rcu.authToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwIjoiUEtDUyM3IiwiYyI6IkFFU18yNTZfQ0JDIiwiYjY0aXYiOiJWZG5ZdVZ4NDZ3a1ArWXJOcXZKeEhnPT0iLCJiNjRjdCI6IkQwSDJYL2ZvcmNoQzJlcFgveUxlUXprbUpVZ1plQWxCUDg4S0FPWVF3eUhMdnRzQ21TYWJuSFB3NGpvL3ZQVmRDbkpMYS83ODZjYStUdENNTDFrRVQ1Qk1Gb25uNTNkTkRQVmVGaFQzcXpVN05WN0ZTNzVNVnQ5ODRnN2l0Z2haOElVMjBVY1VZVHpvZ29Tc0dLT0NSUUNPbGYxdUxSZWdUQlMvWjBLM3dPdXVwUnl5aWZaUWtMU1M4eklBbWpCYytzaUhuc09xQjlzSHFTYlE2TE92L2c9PSIsImlhdCI6MTU3NTI0MzEzN30.QRWLbcVuC1n2_FbA4JK3ZbX8CVkQtLkfZRJCM5aN_UE"

def ShiftFilePath(path, branchesBack=1, append=None):
    pathReverse = path[::-1]
    newPathBackwards = pathReverse.split('\\', branchesBack)[-1]
    newPath = newPathBackwards[::-1]

    if type(append) is str: return(r"{0}\{1}".format(newPath, append))

class Utilities:
    ##############################
    ## DIRECT OBJECT CONVERSION ##
    ##############################
    def PtConversion(self, point, revit2Rhino=True):
        # point from revit will usuall just be float coordinates
        # immediatly convert pt coordinates to float values in lists of tuples
        if revit2Rhino == True: point = rh.Geometry.Point3d(point[0], point[1], point[2])
        elif revit2Rhino == False: point = Point.Create(XYZ(point[0], point[1], point[2]))
        
        return(point)
    def CrvConversion(self, curve, revit2Rhino=True):
        # convert pt coordinates to float values in lists
        if revit2Rhino == True:
            startPt = (curve.GetEndPoint(0).X, curve.GetEndPoint(0).Y, curve.GetEndPoint(0).Z)
            endPt =   (curve.GetEndPoint(1).X, curve.GetEndPoint(1).Y, curve.GetEndPoint(1).Z)
            
            # convert revit points to rhino points
            newStartPt = self.PtConversion(startPt, revit2Rhino=True)
            newEndPt = self.PtConversion(endPt, revit2Rhino=True)
            
            newCurve = rh.Geometry.PolylineCurve((newStartPt, newEndPt))
        elif revit2Rhino == False:
            startPt = None
            endPt = None
            
            # convert rhino points to revit points
            newStartPt = self.PtConversion(startPt, revit2Rhino=False)
            newEndPt = self.PtConversion(endPt, revit2Rhino=False)
            
            newCurve = None
        #print(newCurve)
        return(newCurve)
    ####################################
    ## CONVERSIONS FROM PT EXTRACTION ##
    ####################################
    
    # revit > rhino
    def RevitVectors_2_RhinoVectors(self, vectors, *args):
        if args[0]:
            pass
        else:
            pass
        return(None)
    def RevitPlanes_2_RhinoPlanes(self, origin, xAxis, yAxis, *args):
        if args[0]:
            pass
        else:
            pass
        return(None)
    def RevitCrvPts_2_RhinoCrvs(self, pts, *args):
        """
        Because JSON data does not support revit or rhino object
        types, all geometry is reduced to float point or vector 
        coordinates and then reconstructed to the intended
        converted geometry
        
        kwarg == True reverses platform conversion Revit > Rhino | Rhino > Revit
        """
        if args[0]:
            pass
        else:
            pass
        return(None)
    def RevitSrfPts_2_RhinoSrfPts(self, pts, *args):
        if args[0]:
            pass
        else:
            pass
        return(None)        
    # rhino > revit
    def RhinoVectors_2_RevitVectors(self, vectors):
        return(self.RevitVectors_2_RhinoVectors(vectors, True))
    def RhinoPlanes_2_RevitPlanes(self, origin, xAxis, yAxis):
        return(self.RevitPlanes_2_RhinoPlanes(origin, xAxis, yAxis, True))
    def RhinoCrvPts_2_RevitCrvs(self, pts):
        return(self.RevitCrvPts2RhinoCurves(pts, True))
    def RhinoSrfPts_2_RevitSrfPts(self, pts):
        return(self.RevitSrfPts_2_RhinoSrfPts(pts, True))