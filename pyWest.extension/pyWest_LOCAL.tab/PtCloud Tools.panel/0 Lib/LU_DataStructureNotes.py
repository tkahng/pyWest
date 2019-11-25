"""
LEVELUP DATA STRUCTURE and PROCESS

DATA HARVEST
_point cloud model isolated for floor
_point coordinates exported as .txt (cyclone/recap pro) or .json (rhino)
_total ReCap deliverables:
____3d building laser scan per level volume
____10x decimated 3d building laser scan per level volume
____10x decimated isolated floor laser scan per level
____.txt or .json export of point coordinates per floor
_________each file saved as: "CONTINENT_CITY_BUILDING NAME_LEVEL #"
_____________in Rhino this will be done with a script using layer names
_____________in cyclone/recap pro this will be input manually at each export
_____________how can i leverage Stargate Id?
_________how can this step be automated and protected from errors?

LEVELUP CALCULATION
_raw point data loaded into script
_building/floor informaiton derived from file name
____this needs to be automated
"""

# 1 | DATA FROM RHINO OR CYCLONE/RECAP PRO
levelUpInputDict = {"TIME STAMPED ANALYSIS" : {"Points" : [],
                                                "BuildingMetadata" : {"StargateId" : 000,
                                                                      "Continent" : "NA",
                                                                      "City" : "SEA",
                                                                      "BuildingName" : "Something",
                                                                      "Floor Number" : {0},
                                                                      "Scanner" : "Scanner Name / value"}},      
                    "TIME STAMPED ANALYSIS" : {"Points" : [],
                                                "BuildingMetadata" : {"StargateId" : 000,
                                                                      "Continent" : "NA",
                                                                      "City" : "SEA",
                                                                      "BuildingName" : "Something",
                                                                      "Floor Number" : {0},
                                                                      "Scanner" : "Scanner Name / value"}}
                   }

# 2 | DATA FROM RHINO OR CYCLONE/RECAP PRO
levelUpInputDict = {"TIME STAMPED ANALYSIS" : {"Points" : [],
                                                "Float Material" : "Something",
                                                "BuildingMetadata" : {"StargateId" : 000,
                                                                      "Continent" : "NA",
                                                                      "City" : "SEA",
                                                                      "BuildingName" : "Something",
                                                                      "Floor Number" : {0},
                                                                      "Scanner" : "Scanner Name / value"}},      
                    "TIME STAMPED ANALYSIS" : {"Points" : [],
                                                "Float Material" : "Something",
                                                "BuildingMetadata" : {"StargateId" : 000,
                                                                      "Continent" : "NA",
                                                                      "City" : "SEA",
                                                                      "BuildingName" : "Something",
                                                                      "Floor Number" : {0},
                                                                      "Scanner" : "Scanner Name / value"}}

# THERE IS AN EXPORT FROM RHINO OF JUST THE POINTS. THEN THERE IS AN EXPORT FROM LEVEL UP TOOL TO THE ENGINE THAT SAYS WHERE TO READ THE POINTS. THE POINTS ARE THEN LOADED INTO MEMORY AND RAN BY THE ENGINE. RHINO MUST HAVE THE POINTS PROPERLY ORGANIZED IN CODE. THE ORIGNAL EXPORT CODE EITHER BY NAME OR CONTENTS IS WHAT GIVE THE ENGINE THE DATA IT NEEDS. 





