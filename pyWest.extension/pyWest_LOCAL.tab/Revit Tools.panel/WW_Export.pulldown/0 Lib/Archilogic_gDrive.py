"""
I WILL INSTANTIATE AN EXPORT IN REVIT, THEN CALL AN EXTERNAL PROCESS
THAT WILL USE pyDRIVE WRAPPER TO MOVE FILES TO GDRIVE

1 | create a new project in Google Cloud Plaform - API & Services
2 | create keys that will grant you access to gDrive using user credentials
3 | download client secrets json file from google api; rename it to client_secrets.json and save it in the same directory as this file
"""
import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os # importing os and glob to find all PDFs inside subfolder
import glob # for finding files with specific extensions?

class GDriveTools:
    """
    THIS TOOL WILL NEED TO READ THE FILE NAME OR STARGATE IN ORDER TO
    """
    
    def __init__(self, fileDirectory, gDriveDirectory=None):
        # input parameters
        self.fileDirectory = fileDirectory
        self.gDriveDirectory = gDriveDirectory
        
        # derived parameters
        self.drive = None
        
        self.clientId = r"106283127422-o9bq7hdp44n54n2spf4fcevg3tc27mc3.apps.googleusercontent.com"
        self.clientSecret = r"jweccguS_YtbrNNvn2_QeItF"

    def ConnectToGDrive(self):
        g_login = GoogleAuth()
        g_login.LocalWebserverAuth() # user using tool will have log in to gDrive with their WW account
        self.drive = GoogleDrive(g_login)
    
    def UploadFilesToGDrive(self):
        # file must be a string with a path
        with open(self.fileDirectory,"r") as file2upload:
            fileName = os.path.basename(file2upload.name)
            file_drive = self.drive.CreateFile({'title': fileName })
            print(file_drive)
        try:
            file_drive.SetContentString(file2upload.read()) # what is this for???
        except:
            pass
        file_drive.Upload()
        print("The file: " + fileName + " has been uploaded")
    
    def MoveFileInGDrive(self):
        pass

    def Run_SingleUpload(self):
        # Connecting to Google Drive with PyDrive
        self.ConnectToGDrive()

        # Uploading Files to a Drive Account
        self.UploadFilesToGDrive()
    
    def Run_MultiUpload(self):
        os.chdir(self.fileDirectory)
        for file in glob.glob("*.pdf"):
            print(file)        
    

"""
B/C PLUGIN USES SUBPROCESS TO ACCESS GDRIVE
INSTRUCTIONS WILL BE RAN FROM MAIN
"""
def Main():
    #filePath = r"/docs"
    filePath = [r"C:\Users\aluna\Desktop\TestIFCexport4_Link_0.ifc"]
    GDriveTools(fileDirectory=filePath, gDriveDirectory=None).Run_SingleUpload()


if __name__ == "__main__":
    Main()