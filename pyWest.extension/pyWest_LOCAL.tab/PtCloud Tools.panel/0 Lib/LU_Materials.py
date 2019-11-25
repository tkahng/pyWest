def FloatMaterialDict():
	materials = {'LevelQuick RS': {'cost': 8.00, 
                                   'packaging': '50 lb. bag', 
                                   'coverage': 2.80},

                 'Ardex K10': {'cost': 26.00,
                               'mixing ratio': '5.25 quarts of water per bag',
                               'packaging': '50 lb. bag', 
                               'coverage': .5208},
                                
                 'Float Material C': {'cost': 26.00,
                                	  'mixing ratio': '5.25 quarts of water per bag',
                                      'packaging': '50 lb. bag', 
                                      'coverage': .5208}
                 }
	return(materials)
    
    
def TestMain():
	# the following is just a test
	print(FloatMaterialDict()['Ardex K10']['packaging'] + '\n')
	
#	#.keys(), .values()
#	for i in FloatMaterialDict().keys():
#		print(i)
#		for j in FloatMaterialDict()[i].keys():
#			print(j)
			
if __name__ == "__main__":
	TestMain()