import json

if __name__ == '__main__':
    with open('/home/monitor/p4app/BoostFlow/encode/tableEntries/mergeTableEntriesList.json', 'r') as f:
        mergeTableEntriesList = json.load(f)
        rows = []
        for mergeTableEntry in mergeTableEntriesList:
            row = []
            leaf = mergeTableEntry['leaf']
            for treeid, nodeIndex in mergeTableEntry['leaf_index_dict'].items():
                row.append(nodeIndex)
            row.append(leaf)
            rows.append(row)
        tree1Dict = {}
        tree2Dict = {}
        tree3Dict = {}
        tree4Dict = {}
        for row in rows:
            if row[0] not in tree1Dict:
                tree1Dict[row[0]] = []
            if row[1] not in tree2Dict:
                tree2Dict[row[1]] = []
            if row[2] not in tree3Dict:
                tree3Dict[row[2]] = []
            if row[3] not in tree4Dict:
                tree4Dict[row[3]] = []
            codeList = []
            for i in range(4):
                code = 1
                for j in range(5):
                    if i != j :
                        code = code * 100 + row[j]
                codeList.append(code)
            tree1Dict[row[0]].append(codeList[0])
            tree2Dict[row[1]].append(codeList[1])
            tree3Dict[row[2]].append(codeList[2])
            tree4Dict[row[3]].append(codeList[3])
        for value in tree1Dict.values():
            value.sort()
        for value in tree2Dict.values():
            value.sort()
        for value in tree3Dict.values():
            value.sort()
        for value in tree4Dict.values():
            value.sort()
        set1List = []
        for fNodeID,fCode in tree1Dict.items():
            for sNodeID,sCode in tree1Dict.items():
                if fNodeID != sNodeID:
                    if fCode == sCode:
                        set1List.append([fNodeID,sNodeID])
        set2List = []
        for fNodeID,fCode in tree2Dict.items():
            for sNodeID,sCode in tree2Dict.items():
                if fNodeID != sNodeID:
                    if fCode == sCode:
                        set2List.append([fNodeID,sNodeID])
        set3List = []
        for fNodeID,fCode in tree3Dict.items():
            for sNodeID,sCode in tree3Dict.items():
                if fNodeID != sNodeID:
                    if fCode == sCode:
                        set3List.append([fNodeID,sNodeID])
        set4List = []
        for fNodeID,fCode in tree4Dict.items():
            for sNodeID,sCode in tree4Dict.items():
                if fNodeID != sNodeID:
                    if fCode == sCode:
                        set4List.append([fNodeID,sNodeID])
        print(set1List)
        print(set2List)
        print(set3List)
        print(set4List)
        