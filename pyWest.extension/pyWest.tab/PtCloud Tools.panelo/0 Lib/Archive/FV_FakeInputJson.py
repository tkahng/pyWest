# write a fake Json file for point cloud estimate
import sys
sys.path.append(r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\0 Lib")
import WW_DataExchange as DE

data = [[r"C:\Users\aluna\Desktop\Tabor_10.json", r"LevelQuick RS"], [r"C:\Users\aluna\Desktop\Tabor_13.json", r"LevelQuick RS"],
        [r"C:\Users\aluna\Desktop\Tabor_14.json", r"LevelQuick RS"], [r"C:\Users\aluna\Desktop\Tabor_15.json", r"LevelQuick RS"]]

filePath = r"C:\Users\aluna\Documents\WeWork Code\VDCwestExtensions\pyVDCWest.extension\VDCwest.tab\PtCloud Tools.panel\0 Lib\JSON Exchange"
jsonObj = DE.JSONTools()
jsonObj.WriteJSON(data=data, filePath=filePath, fileName="FV_InputArgs", inMemory=False)