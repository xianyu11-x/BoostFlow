import re
import copy
import numpy as np
import encode.utils as utils
#import utils
import json

def parse_tree(lines):
    node_regex = r'(\d+):\[(.*?)\] (yes|no|missing)=(\d+),(yes|no|missing)=(\d+),?(missing=(\d+))?'
    leaf_regex = r'(\d+):leaf=(-?\d+\.\d+)'
    tree_regex = r'booster\[(\d+)\]:'
    trees = {}
    tree = {}
    tree_id=0
    for line in lines:
        match = re.match(tree_regex,line)
        if match:
            tree_id=int(match.group(1))
            if tree_id > 0:
                trees[tree_id-1]=copy.deepcopy(tree)
                tree.clear()
        match = re.match(node_regex, line)
        if match:
            node_id = int(match.group(1))
            feature = match.group(2)
            true_branch = int(match.group(4))
            false_branch = int(match.group(6))
            tree[node_id] = {
                             'feature': feature,
                             'true_branch': true_branch,
                             'false_branch': false_branch,
                            }
            continue
        match = re.match(leaf_regex, line)
        if match:
            node_id = int(match.group(1))
            leaf_value = float(match.group(2))
            tree[node_id] = {'leaf': leaf_value}
            continue

    if tree_id > 0:
        trees[tree_id]=copy.deepcopy(tree)
        tree.clear()
    return trees

#按全部节点划分特征空间
def split_all_feature(trees,feature_list):
    feature_dict={}
    for feature in feature_list:
        feature_dict[feature]= []
    tree_dict = trees.values()
    for tree in tree_dict:
        for node_id in tree:
            if len(tree[node_id])>1:
                feature_name , feature_value=tree[node_id]['feature'].split('<')
                feature_dict[feature_name].append(int(feature_value))
    #feature_value_list = feature_dict.values()
    for feature_name,value_list in feature_dict.items():
        #value_list排序并除去重复元素
        value_list_1=list(set(value_list))
        value_list_1.sort()
        feature_dict[feature_name]=value_list_1
    return feature_dict

#按每颗树的节点划分特征空间
def split_tree_feature(trees,feature_list):
    tree_feature_dict={}
    #tree_dict = trees.values()
    for tree_id , tree in trees.items():
        tree_feature_dict[tree_id]={}
        for feature in feature_list:
            tree_feature_dict[tree_id][feature]=[]
        for node_id in tree:
            if len(tree[node_id])>1:
                feature_name , feature_value=tree[node_id]['feature'].split('<')
                tree_feature_dict[tree_id][feature_name].append(int(feature_value))
        for feature_name,value_list in tree_feature_dict[tree_id].items():
        #value_list排序并除去重复元素
            value_list_1=list(set(value_list))
            value_list_1.sort()
            tree_feature_dict[tree_id][feature_name]=value_list_1     
    return tree_feature_dict

#编码特征空间
def encode_feature(feature_dict,tree_feature_dict):
    encode_feature_dict={}
    for feature_name,feature_value_list in feature_dict.items():
        rows=len(tree_feature_dict)
        cols=len(feature_value_list)+1
        encode_feature_dict[feature_name]=np.zeros((rows,cols))
        for row in range(rows):
            if tree_feature_dict[row][feature_name]!=[]:
                prev_index=0
                code=1
                for split_tree_node in tree_feature_dict[row][feature_name]:
                    #在特征值列表中找到划分节点的位置
                    index=feature_value_list.index(split_tree_node)+1
                    for i in range(prev_index,index):
                        encode_feature_dict[feature_name][row][i]=code
                    prev_index=index
                    code+=1
                for i in range(prev_index,cols):
                    encode_feature_dict[feature_name][row][i]=code
    return encode_feature_dict



#深度优先遍历树节点，获取从根节点到叶子节点的所有路径
def dfs_tree(tree,node_id,tree_feature_dict,node_path):
    global all_node_path
    global leaf_index
    if len(tree[node_id])>1:
        node=tree[node_id]['feature'].split('<')
        left=tree[node_id]['true_branch']
        right=tree[node_id]['false_branch']
        feature_value_list=tree_feature_dict[node[0]]
        index=feature_value_list.index(int(node[1]))+1
        tempr=node_path[node[0]]['right']
        node_path[node[0]]['right']=index
        left_path=copy.deepcopy(node_path)
        dfs_tree(tree,left,tree_feature_dict,left_path)
        node_path[node[0]]['right']=tempr
        templ=node_path[node[0]]['left']
        node_path[node[0]]['left']=index+1
        right_path=copy.deepcopy(node_path)
        dfs_tree(tree,right,tree_feature_dict,right_path)
        node_path[node[0]]['left']=templ
    else :
        all_node_path[node_id]={}
        all_node_path[node_id]['leaf']=tree[node_id]['leaf']
        all_node_path[node_id]['leaf_index']=leaf_index
        leaf_index+=1
        all_node_path[node_id]['path']=copy.deepcopy(node_path)
        return
    return


#获取所有树的所有节点的路径列表
def get_all_node_path_list(trees,feature_list,tree_feature_dict,encode_feature_dict):
    all_node_path_list=[]
    for tree_id,tree in trees.items():
        global all_node_path
        node_path={}
        for feature in feature_list:
            node_path[feature]={'left':1,'right':int(encode_feature_dict[feature][tree_id][-1])}
            #node_path[feature]={'left':1,'right':15}
        all_node_path={}
        global leaf_index
        leaf_index = 0
        dfs_tree(tree,0,tree_feature_dict[tree_id],node_path)
        all_node_path_list.append(copy.deepcopy(all_node_path))
    return all_node_path_list

#将叶子节点的值转换位补码表示
def leaf_to_complement(all_node_path_list):
    for all_node_path in all_node_path_list: 
        for node_id , node_dict in all_node_path.items():
            leaf=int(node_dict['leaf']*1000000000)
            #把leaf转换为20位的补码表示
            leaf=bin(leaf & 0xffffffff)[2:]
            node_dict['leaf']=leaf
    return all_node_path_list

def clean_unused_feature(all_node_path_list,encode_feature_dict):
    i=0
    for all_node_path in all_node_path_list:
        for node_id,node_dict in all_node_path.items():
            for feature_name,feature_value in node_dict['path'].items():
                if feature_value['left']==1 and feature_value['right']==int(encode_feature_dict[feature_name][i][-1]):
                    feature_value['left'] = 0
                    feature_value['right'] = 0
        i=i+1
    return all_node_path_list

def getFeatureTableEntries(feature_dict,encode_feature_dict,maxBitsDict):
    k=0
    featureTableEntriesDict={}
    for featureName,featureValueList in feature_dict.items():
        featureTableEntriesDict[featureName]=[]
        featureValueList.insert(0,0)
        featureValueList.append(1<<maxBitsDict[featureName])
        priority = 0
        for i in range(1,len(featureValueList)):
            #actionName='SwitchIngress.SetCode'+k.__str__()
            rows= encode_feature_dict[featureName].shape[0]
            encodeValue=int(0)
            for j in range(rows,0,-1):
                encodeValue*=16 #每个特征值占用位数为4位
                encodeValue += encode_feature_dict[featureName][j-1][i-1] 
            startNumList,addNumList = utils.rangeToTernary(0,featureValueList[i])
            for startNum,addNum in zip(startNumList,addNumList):
                if(startNum+addNum>=featureValueList[i-1]):
                    temp={}
                    temp['value']=bin(startNum)
                    temp['mask']=utils.get_mask(maxBitsDict[featureName],addNum)
                    temp['priority']=priority
                    #temp['actionName']=actionName
                    temp['encodeValue']=encodeValue
                    featureTableEntriesDict[featureName].append(temp)
                    priority+=1
        k+=1
    return featureTableEntriesDict

def getTreeTableEntries(all_node_path_list):
    treeTableEntriesDict={}
    for i in range(len(all_node_path_list)):
        treeTableEntriesDict[i]=[]
        global dtPriority
        dtPriority=0
        for node_path in all_node_path_list[i].values():
                value=node_path['leaf_index']
                #value有str转成2进制
                path=node_path['path']
                keys_list=[]
                for key_name,key_value in path.items():
                    key_list=[]
                    if key_value['left'] == 0 and key_value['right'] == 0:
                        temp={}
                        temp['keyName']=key_name
                        temp['value']=bin(0)
                        temp['mask']='0b0'
                        key_list.append(temp)
                    else:
                        startNumList,addNumList = utils.rangeToTernary(key_value['left'],key_value['right']+1)
                        for startNum,addNum in zip(startNumList,addNumList):
                            temp={}
                            temp['keyName']=key_name
                            temp['value']=bin(startNum)
                            temp['mask']=utils.get_mask(4,addNum)
                            key_list.append(temp)
                    keys_list.append(key_list)
                #使用一个列表储存keys_list的所有组合
                global all_key_list
                all_key_list=[]
                setKeyPath(keys_list,0)
                #key_list.append(gc.KeyTuple('$MATCH_PRIORITY', j))
                #j+=1
                for key_list in all_key_list:
                    temp={}
                    temp['key']=key_list
                    temp['value']=value
                    #temp['action']='SwitchIngress.set_classification_res_'+str(i+1)
                    treeTableEntriesDict[i].append(temp)
    return treeTableEntriesDict

def setKeyPath(keys_list,index,key_list=[]):
    global all_key_list
    global dtPriority
    if index==len(keys_list):
        temp_list=copy.deepcopy(key_list)
        temp={}
        temp['priority']=dtPriority
        temp_list.append(temp)
        dtPriority+=1
        all_key_list.append(temp_list)
        return
    for key in keys_list[index]:
        temp_list=copy.deepcopy(key_list)
        temp_list.append(key)
        setKeyPath(keys_list,index+1,temp_list)


def findFeatureRangeValue(featureName,featureIndex,feature_dict,encode_feature_dict,tree_id,side):
    featureValueList=feature_dict[featureName]
    featureEncodeList=encode_feature_dict[featureName][tree_id]
    npFeatureEncodeList=np.array(featureEncodeList)
    indexList=np.where(npFeatureEncodeList==featureIndex)[0]
    if side == 'left':
        return featureValueList[indexList[0]]
    elif side == 'right':
        return featureValueList[indexList[-1]+1]-1


def getFeatureRange(feature_dict,encode_feature_dict,all_node_path_list):
    for i in range(len(all_node_path_list)):
        for node_path in all_node_path_list[i].values():
            path=node_path['path']
            node_path['feature_range']={}
            for key_name,key_value in path.items():
                node_path['feature_range'][key_name]={}
                if key_value['left'] == 0 and key_value['right'] == 0:
                    node_path['feature_range'][key_name]['left']=0
                    node_path['feature_range'][key_name]['right']=feature_dict[key_name][-1]-1
                else:
                    node_path['feature_range'][key_name]['left']=findFeatureRangeValue(key_name,key_value['left'],feature_dict,encode_feature_dict,i,'left')
                    node_path['feature_range'][key_name]['right']=findFeatureRangeValue(key_name,key_value['right'],feature_dict,encode_feature_dict,i,'right')
    return all_node_path_list

def updateFeatureRange(TreesNodeFeatureRange,node_dictFeatureRange):
    temp={}
    flag = True
    for key_name,key_value in TreesNodeFeatureRange.items():
        temp[key_name]={}
        temp[key_name]['left']=max(key_value['left'],node_dictFeatureRange[key_name]['left'])
        temp[key_name]['right']=min(key_value['right'],node_dictFeatureRange[key_name]['right'])
        if temp[key_name]['left']>temp[key_name]['right']:
            flag=False
            break
    return flag,temp


def mergeTree(TreesNodeList,all_node_path,tree_id):
    NewTreesList=[]
    if TreesNodeList == []:
        for node_dict in all_node_path.values():
            temp={}
            temp['leaf']=node_dict['leaf']
            temp['feature_range']=node_dict['feature_range']
            temp['leaf_index_dict']={}
            temp['leaf_index_dict'][tree_id]=node_dict['leaf_index']
            NewTreesList.append(temp)
    else :
        for node_dict in all_node_path.values():
            for TreesNode in TreesNodeList:
                temp={}
                temp['leaf']=node_dict['leaf']+TreesNode['leaf']
                flag,temp['feature_range']=updateFeatureRange(TreesNode['feature_range'],node_dict['feature_range'])
                temp['leaf_index_dict']=copy.deepcopy(TreesNode['leaf_index_dict'])
                temp['leaf_index_dict'][tree_id]=node_dict['leaf_index']
                if flag:
                    NewTreesList.append(temp)
    return NewTreesList
               

def getMergeTableEntries(all_node_path_list):
    mergeTableEntriesList=[]
    trees = len(all_node_path_list)
    TreesNodeList=[]
    for i in range(trees):
        TreesNodeList=mergeTree(TreesNodeList,all_node_path_list[i],i)
    for TreesNode in TreesNodeList:
        temp={}
        if TreesNode['leaf'] >= 0:
            temp['leaf']=2
        else :
            temp['leaf']=1
        temp['leaf_index_dict']=TreesNode['leaf_index_dict']
        mergeTableEntriesList.append(temp)
    return mergeTableEntriesList

def checkNode(checkNodeDict,all_node_path):
    # checkNodeDict={}
    # checkNodeDict['feature0']=5
    # checkNodeDict['feature1']=6
    # checkNodeDict['feature2']=0
    # checkNodeDict['feature3']=5
    # checkNodeDict['feature4']=0
    # checkNodeDict['feature5']=3
    # checkNodeDict['feature6']=1
    for node in all_node_path.values():
        flag = True
        for nodeFeatureName , nodeFeatureRange in node['path'].items():
            if nodeFeatureRange['left'] ==0 and nodeFeatureRange['right'] ==0:
                continue
            elif checkNodeDict[nodeFeatureName] >= nodeFeatureRange['left'] and checkNodeDict[nodeFeatureName] <= nodeFeatureRange['right']:
                continue
            else:
                flag = False
                break
        if flag :
            print(node)
            return True
    return False
    


def get_para(lines,feature_list,maxBitsList):
    maxBitsDict={}
    for featureName , maxBits in zip(feature_list,maxBitsList):
        maxBitsDict[featureName]=maxBits
    trees = parse_tree(lines)
    feature_dict=split_all_feature(trees,feature_list)
    tree_feature_dict=split_tree_feature(trees,feature_list)
    encode_feature_dict=encode_feature(feature_dict,tree_feature_dict)
    featureTableEntriesDict=getFeatureTableEntries(feature_dict,encode_feature_dict,maxBitsDict)
    all_node_path_list=get_all_node_path_list(trees,feature_list,tree_feature_dict,encode_feature_dict)
    #print(all_node_path_list)
    all_node_path_list=clean_unused_feature(all_node_path_list,encode_feature_dict)
    #all_node_path_list=leaf_to_complement(all_node_path_list)
    all_node_path_list=getFeatureRange(feature_dict,encode_feature_dict,all_node_path_list)
    treeTableEntriesDict=getTreeTableEntries(all_node_path_list)
    mergeTableEntriesList=getMergeTableEntries(all_node_path_list)
    #print(all_node_path_list[1])              
    return featureTableEntriesDict,treeTableEntriesDict,mergeTableEntriesList

if __name__ == "__main__":
    with open('./split3.txt') as f: 
        lines = f.readlines()
    feature_list=['feature0','feature1','feature2','feature3','feature4','feature5','feature6']
    maxBitsList=[16,20,16,16,16,20,20]
    # maxBitsDict={}
    # for featureName , maxBits in zip(feature_list,maxBitsList):
    #     maxBitsDict[featureName]=maxBits
    featureTableEntriesDict,treeTableEntries,mergeTableEntriesList=get_para(lines,feature_list,maxBitsList)
    totalEntries = 0
    for featureName,featureTableEntries in featureTableEntriesDict.items():
        #打印featureName+featureTableEntries的长度
        totalEntries+=len(featureTableEntries)
        print(featureName,len(featureTableEntries))
    for TreeId,treeTableEntries in treeTableEntries.items():
        #打印TreeId+treeTableEntries的长度
        totalEntries+=len(treeTableEntries)
        print(TreeId,len(treeTableEntries))
    print(len(mergeTableEntriesList))
    totalEntries+=len(mergeTableEntriesList)
    print(totalEntries)
    # with open('featureTableEntriesDict.json', 'w') as f:
    #     json.dump(featureTableEntriesDict, f)

    # # 将 treeTableEntries 的值写入文件
    # with open('treeTableEntries.json', 'w') as f:
    #     json.dump(treeTableEntries, f)

    # # 将 mergeTableEntriesList 的值写入文件
    # with open('mergeTableEntriesList.json', 'w') as f:
    #     json.dump(mergeTableEntriesList, f)    
    # for entries in treeTableEntries[1]:
    #     if entries["value"] == 11:
    #         print(entries)
    # print(feature_dict)
    # print(all_node_path_list)
    # for all_node_path in all_node_path_list:
    #     print(all_node_path)
    #     print('next')
