"""
Bin Estimate Takeoff for IT Department

Google Sheets Tutorial:
https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
"""
__author__ = 'WeWork VDC West'
__version__ = "4.0"

import traceback
import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    sys.path.append(r"../../lib")
    import Bins_Takeoff_Engine as BTE

    def Main():
        totalObj = BTE.BinAllocation().Run()
        
    
    if __name__ == "__main__":
        Main()

except:
    # print traceback in order to debug file
    print(traceback.format_exc())