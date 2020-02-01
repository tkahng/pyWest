"""

client secret JSON in tool folder
"""
# gSheet API
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas
import pprint

class BinAllocation:
    def __init__(self):
        # credentials
        self.client = None
        
        # bin totals
        self.trash_3_5 = 0
        self.trash_7 = 0
        self.trash_10 = 0
        
        self.recycle_3_5 = 0
        self.recycle_7 = 0
        self.recycle_10 = 0
        
        self.standardSilverULine = 0
        
        self.output = None
        
    def AuthGSheet(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(r"../../lib/client_secret.json", scope)
        self.client = gspread.authorize(creds)
        
    def ReadRow(self, startCell, endCell):
        pass
    
    def ReadColumn(self, startCell, endCell):
        pass
    
    def WriteRow(self, startCell, endCell):
        pass
    
    def WriteColumn(self, startCell, endCell):
        pass
    
    def CountBins(self):
        if self.deskCount:
            if 'conference' in list(self.deskCount.keys())[0]:
                print(list(self.deskCount.keys())[0])
                self.standardSilverULine += 1
                self.recycle_3_5 += 1
            
            elif 'classroom' or 'board' in list(self.deskCount.keys())[0]:
                self.standardSilverULine += 1
                self.recycle_7 += 1
                
            elif 2 >= self.deskCount.values() >= 1:
                self.trash_3_5 += 1
                self.recycle_3_5 += 1
                
            elif 8 >= self.deskCount.values() >= 3:
                self.trash_7 += 1
                self.recycle_7 += 1
            
            elif 15 >= self.deskCount.values() >= 9:
                self.trash_10 += 1
                self.recycle_10 += 1
                
            elif 60 >= self.deskCount.values() >= 16:
                self.trash_10 += 2
                self.recycle_10 += 2
                
            elif 99 >= self.deskCount.values() >= 61:
                self.trash_10 += 3
                self.recycle_10 += 3
            
            elif 160 >= self.deskCount.values() >= 100:
                self.trash_10 += 4
                self.recycle_10 += 4
            
            elif 230 >= self.deskCount.values() >= 161:
                self.trash_10 += 5
                self.recycle_10 += 5
            
            elif self.deskCount.values() > 230:
                self.trash_10 += 6
                self.recycle_10 += 6
        
        self.output = """self.trash_3_5 = {0}
self.trash_7 = {1}
self.trash_10 = {2}
        
self.recycle_3_5 = {3}
self.recycle_7 = {4}
self.recycle_10 = {5}
        
self.standardSilverULine = {6}""".format(self.trash_3_5,
                                         self.trash_7,
                                         self.trash_10,
                                         self.recycle_3_5,
                                         self.recycle_7,
                                         self.recycle_10,
                                         self.standardSilverULine)
        print(self.output)
    
    def Run(self):
        # get Google Sheet API credentials/authorization
        self.AuthGSheet()
        
        sheet = self.client.open("410 N Scotsdale").sheet1
        print(sheet)
        
        listOfHatches = sheet.get_all_records()
        pprint.pprint(listOfHatches)        
              