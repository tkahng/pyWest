# this module setup for pyWeWork access
from __future__ import print_function
import gspread
import google_auth
import data_uploader

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class LigthingSheetMerge:
    def __init__(self, ):
        # input parameters
        
        # derived parameters
        self.regionName = None
        
        self.FamilyName = None
        self.FamilyType = None
        self.FamilyMark = None
        self.FamilyLevel = None
        self.FamilyDescription = None
    
    def ReadGSheet(self):
        pass
    def WriteGSheet():
        pass
    def GetGSheetTabs(self):
        pass
    def Run_GSHeetTools(self):
        # go to main folder location
        #for i in main_folder_location:
            # go to each region folder
            # go to each gSheet
            # extract information from those sheets
            # append to regionGSheet
            # parse/merge/cleanup Region cluster data
            # create new region GSheet combining all project data
            # add region GSheet to main folder location
        pass

def GetAuthorization():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    
    """
    Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES) # changed the name of the json file here
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API - to do stuff?
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items: print('No files found.')
    else:
        print('Files:')
        for item in items: print(u'{0} ({1})'.format(item['name'], item['id']))      

def Main():
    # after token is created, you don't have to keep logging in - uses a pickle file
    GetAuthorization()
    
    #url_Dict = {"pacNW": r"https://docs.google.com/spreadsheets/d/1SdpMjTueNz4bwkIwszYWOO475XuGCogxsac7mh2hxAM/edit#gid=2407238",
                #"norCal": r"https://docs.google.com/spreadsheets/d/1SdpMjTueNz4bwkIwszYWOO475XuGCogxsac7mh2hxAM/edit#gid=2407238",
                #"soCal": r"https://docs.google.com/spreadsheets/d/1SdpMjTueNz4bwkIwszYWOO475XuGCogxsac7mh2hxAM/edit#gid=2407238",
                #"mntW": r"https://docs.google.com/spreadsheets/d/1SdpMjTueNz4bwkIwszYWOO475XuGCogxsac7mh2hxAM/edit#gid=2407238",
                #"texas": r"https://docs.google.com/spreadsheets/d/1SdpMjTueNz4bwkIwszYWOO475XuGCogxsac7mh2hxAM/edit#gid=2407238"}
    
    #LigthingSheetMerge(url_Dict).Run_GSHeetTools()  

if __name__ == "__main__":
    Main()