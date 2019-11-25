import os, zipfile

def UnzipFiles(dirName=None):
    if dirName:
        dir_name = 'C:\\SomeDirectory'
        extension = ".zip"
        
        os.chdir(dir_name) # change directory from working dir to dir with files
        
        for item in os.listdir(dir_name): # loop through items in dir
            if item.endswith(extension): # check for ".zip" extension
                file_name = os.path.abspath(item) # get full path of files
                zip_ref = zipfile.ZipFile(file_name) # create zipfile object
                zip_ref.extractall(dir_name) # extract file to dir
                zip_ref.close() # close file
                os.remove(file_name) # delete zipped file

def Main():
    # GUI
    # select directory
    dirName = None
    
    UnzipFiles(dirName)

if __name__ == "__main__":
    UnzipFiles()