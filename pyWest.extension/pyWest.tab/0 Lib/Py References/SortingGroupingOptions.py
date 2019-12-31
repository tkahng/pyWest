# SORT WALL LIST BY LEVEL LIST
def SortListbyList(listA, listB):
    return([x for _,x in sorted(zip(listB, listA))])

wallLevels = [16,17,16,15,15,15]
walls = ['wall', 'wall1', 'wall2', 'wall3', 'wall4', 'wall5']
sortedWalls = SortListbyList(walls, wallLevels)
print(sortedWalls)

# GROUP SORTED LIST BY LEVEL
def groupLists(listA, listB):
    setList = sorted(set(listB))
    listOut = []
    for i in setList:
        tempList = []
        for j, wall in enumerate(listA):
            if listB[j] == i:
                tempList.append(wall)
        listOut.append(tempList)
    return(listOut)

print(groupLists(sortedWalls, wallLevels))