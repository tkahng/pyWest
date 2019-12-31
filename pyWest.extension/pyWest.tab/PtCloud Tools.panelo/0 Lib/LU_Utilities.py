# UTILITIES

class ScannerLibrary:
    def __init__(self):
        self.scanRadius = [0.276, 0.315, 0.355, 0.394, 0.500]
        self.scanSettings = None
        
    def ScanRadiusDB(self, vendor='WeWork', scanner='ScannerA'):
        # radius squared for vectorization
        scanSettings = {'WeWork' : {{'Scanner A' : {'Density' : 0.394}},
                                    {'Scanner B' : {'Density' : 0.394}}},
                        
                        'Contractor A' : {{'Scanner A' : {'Density' : 0.394}},
                                          {'Scanner B' : {'Density' : 0.394}}}
                       }
        squaredOutput = scanRadius[vendor][scanner]['Density'] ** 2
        
        return(squaredOutput)

class FileNameParser:
    def __init__(self, fileName):
        # input parameters
        self.fileName = fileName
        
        # output parameters
        self.continent = None
        self.city = None
        self.buildingName = None
        self.floorNum = None
    
    def ParseFileName(self):
        splitStringList = self.fileName.split('_')
        self.continent, self.city, self.buildingName, self.floorNum = splitStringList

def PrettyOutput(self, buildingName, totalVolume, numBags, totalCost, printOut=True):  
    outputMessage = """
    {0} Float Volume Analyis and Estimate
    
    Total float volume: {1}ft3
    Total number of bags: {2}
    Total material cost: ${3}
    
    """.format(buildingName, abs(round(totalVolume,2)), abs(numBags), abs(round(totalCost,2)))
    
    if printOut == True:
        print(outputMessage)
    return(outputMessage)



def TestMain():
    ## ScannerLibrary
    #scannerQuality = ScannerLibrary().ScanRadiusDB()
    #print(scannerQuality)
    
    # FileNameParser
    testFileName = r'NA_Denver_Tabor Center_10'
    fileObj = FileNameParser(testFileName)
    fileObj.ParseFileName()
    print(fileObj.continent, fileObj.city, fileObj.buildingName, fileObj.floorNum)

if __name__ == "__main__":
    TestMain()