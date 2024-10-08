import bfrt_grpc.client as gc
import sys
import encode as parser
import numpy as np
import copy
import re
# import signal
#import dbClient as dbc
import ipaddress

def reset():
    grpc_client.clear_all_tables()
    
def quit():
    print("quit......")
    grpc_client.__del__()
    sys.exit()


def preLoadEntries(path):
    with open(path) as f:
        lines = f.readlines()
    feature_list=['feature0','feature1','feature2','feature3','feature4','feature5','feature6']
    maxBitsList=[16,20,16,16,16,20,20]
    featureTableEntriesDict,treeTableEntriesDict,mergeTableEntriesList=parser.get_para(lines,feature_list,maxBitsList)
    return featureTableEntriesDict,treeTableEntriesDict,mergeTableEntriesList

def addEncodeTableEntries(target,table_list,featureTableEntriesDict):
    k=0
    for feature,feature_value_list in featureTableEntriesDict.items():
        for feature_value in feature_value_list:
            keyName=feature
            actionName='SwitchIngress.SetCode'+k.__str__()
            keyValue=int(feature_value['value'],2)
            keyMask=int(feature_value['mask'],2)
            priority=int(feature_value['priority'])
            encodeValue=int(feature_value['encodeValue'])
            key=table_list[k].make_key([gc.KeyTuple(keyName,value=keyValue, mask=keyMask),gc.KeyTuple('$MATCH_PRIORITY', priority)])
            data=table_list[k].make_data([gc.DataTuple('allEncode',encodeValue)],actionName)
            table_list[k].entry_add(target,[key],[data])
        k+=1
    return

def addDttableEntries(target,table_list,treeTableEntriesDict):
    for i in range(len(table_list)):
        for treeTableEntrie in treeTableEntriesDict[i]:
            keyList=[]
            for j in range(len(treeTableEntrie['key'])-1):
                keyName='ig_md.'+treeTableEntrie['key'][j]['keyName']+'encode'+str(i+1)
                keyValue=int(treeTableEntrie['key'][j]['value'],2)
                keyMask=int(treeTableEntrie['key'][j]['mask'],2)
                keyList.append(gc.KeyTuple(keyName,value=keyValue,mask=keyMask))
            priority=int(treeTableEntrie['key'][-1]['priority'])  
            keyList.append(gc.KeyTuple('$MATCH_PRIORITY',priority))                          
            table_list[i].entry_add(target,
                                [table_list[i].make_key(keyList)],
                                [table_list[i].make_data([gc.DataTuple('res', int(treeTableEntrie['value']))],'SwitchIngress.setTreeRes'+str(i+1))]
                                )

def addClassifyTableEntries(target,classify_table,mergeTableEntriesList):
    for mergeTableEntries in mergeTableEntriesList:
        key_list=[]
        for key_name,key_value in mergeTableEntries['leaf_index_dict'].items():
            key_list.append(gc.KeyTuple('ig_md.resTree'+str(key_name+1),value=key_value))
        classify_table.entry_add(target,
                                [classify_table.make_key(key_list)],
                                [classify_table.make_data([gc.DataTuple('res',int(mergeTableEntries['leaf']))],'SwitchIngress.set_merge_res')]
                                )

def addAllTableEntry():
    if bfrt_info.p4_name!='p4_flowManagement_3':
        print("error p4 program")
    else:
        print("connect")
        ingress_port=0
        sid=5
        egress_port=5
        featureTableEntriesDict,treeTableEntriesDict,mergeTableEntriesList=preLoadEntries('./encode/split3.txt')
        feature0_table=bfrt_info.table_get("SwitchIngress.table_feature0")
        feature1_table=bfrt_info.table_get("SwitchIngress.table_feature1")
        feature2_table=bfrt_info.table_get("SwitchIngress.table_feature2")
        feature3_table=bfrt_info.table_get("SwitchIngress.table_feature3")
        feature4_table=bfrt_info.table_get("SwitchIngress.table_feature4")
        feature5_table=bfrt_info.table_get("SwitchIngress.table_feature5")
        feature6_table=bfrt_info.table_get("SwitchIngress.table_feature6")
        feature_table_list=[feature0_table,feature1_table,feature2_table,feature3_table,feature4_table,feature5_table,feature6_table]
        dt_1_table=bfrt_info.table_get("SwitchIngress.dt_1_tb")
        dt_2_table=bfrt_info.table_get("SwitchIngress.dt_2_tb")
        dt_3_table=bfrt_info.table_get("SwitchIngress.dt_3_tb")
        dt_4_table=bfrt_info.table_get("SwitchIngress.dt_4_tb")
        dt_list=[dt_1_table,dt_2_table,dt_3_table,dt_4_table]
        merge_table=bfrt_info.table_get("SwitchIngress.merge_tb")
        target=gc.Target(device_id=0, pipe_id=0xffff)
        try:
            addEncodeTableEntries(target,feature_table_list,featureTableEntriesDict)
            addDttableEntries(target,dt_list,treeTableEntriesDict)
            addClassifyTableEntries(target,merge_table,mergeTableEntriesList)
            resp=dt_1_table.entry_get(target,flags={"from_hw":True})
            table_entry_num=0
            for data, key in resp:
                table_entry_num+=1
            print("table entry num: ",table_entry_num)
            table_entry_num=0
            resp=dt_2_table.entry_get(target,flags={"from_hw":True})
            for data, key in resp:
                table_entry_num+=1
            print("table entry num: ",table_entry_num)
            table_entry_num=0
            resp=dt_3_table.entry_get(target,flags={"from_hw":True})
            for data, key in resp:
                table_entry_num+=1
            print("table entry num: ",table_entry_num)
            table_entry_num=0
            resp=dt_4_table.entry_get(target,flags={"from_hw":True})
            for data, key in resp:
                table_entry_num+=1
            print("table entry num: ",table_entry_num)
        except gc.BfruntimeRpcException as e:
            raise e
        finally:
            pass


def delAllTableEntry():
    if bfrt_info.p4_name!='p4_flowManagement_2':
        print("error p4 program")
    else:
        print("connect")
        target=gc.Target(device_id=0, pipe_id=0xffff)
        checkNewFlowTable=bfrt_info.table_get("SwitchIngress.checkNewFlow_tb")
        table_feature0=bfrt_info.table_get("SwitchIngress.table_feature0")
        table_feature1=bfrt_info.table_get("SwitchIngress.table_feature1")
        table_feature2=bfrt_info.table_get("SwitchIngress.table_feature2")
        table_feature3=bfrt_info.table_get("SwitchIngress.table_feature3")
        table_feature4=bfrt_info.table_get("SwitchIngress.table_feature4")
        table_feature5=bfrt_info.table_get("SwitchIngress.table_feature5")
        table_feature6=bfrt_info.table_get("SwitchIngress.table_feature6")
        dt_1_table=bfrt_info.table_get("SwitchIngress.dt_1_tb")
        dt_2_table=bfrt_info.table_get("SwitchIngress.dt_2_tb")
        dt_3_table=bfrt_info.table_get("SwitchIngress.dt_3_tb")
        dt_4_table=bfrt_info.table_get("SwitchIngress.dt_4_tb")
        classify_table=bfrt_info.table_get("SwitchIngress.merge_tb")
        try:
            table_feature0.entry_del(target)
            table_feature1.entry_del(target)
            table_feature2.entry_del(target)
            table_feature3.entry_del(target)
            table_feature4.entry_del(target)
            table_feature5.entry_del(target)
            table_feature6.entry_del(target)
            dt_1_table.entry_del(target)
            dt_2_table.entry_del(target)
            dt_3_table.entry_del(target)
            dt_4_table.entry_del(target)
            classify_table.entry_del(target)
            checkNewFlowTable.entry_del(target)
        except gc.BfruntimeRpcException as e:
            raise e
        finally:
            pass


def getInfo():
    if bfrt_info.p4_name!='p4_flowManagement_2':
        print("error p4 program")
    else:
        print("connect")
        target=gc.Target(device_id=0, pipe_id=0xffff)
        tableList=bfrt_info.table_name_list_get()
        #匹配tableList中前缀为pipe.SwitchIngress的表
        tableList=[table for table in tableList if re.match('pipe.SwitchIngress.reg',table)]
        for table in tableList:
            table=bfrt_info.table_get(table)
            resp=table.entry_get(target,flags={"from_hw":True})
            i=0
            for data, key in resp:
                #将数据写入.txt文件
                with open('./tableEntries/'+str(i)+'.txt','a') as f:
                    f.write("data: "+data.to_dict().__str__()+"\n")
                    f.write("\n")
                    i=i+1
        tableList2=[table for table in tableList if re.match('pipe.SwitchIngress.checkNew',table)]
        for table in tableList2:
            table=bfrt_info.table_get(table)
            resp=table.entry_get(target,flags={"from_hw":True})
            i=0
            for data, key in resp:
                #将数据写入.txt文件
                print(data)
            
def setcheckNewFlowTable():
    if bfrt_info.p4_name!='p4_flowManagement_2':
        print("error p4 program")
    else:
        print("connect")
        target=gc.Target(device_id=0, pipe_id=0xffff)
        checkNewFlowTable=bfrt_info.table_get("SwitchIngress.checkNewFlow_tb")
        key=checkNewFlowTable.make_key([gc.KeyTuple("hdr.ipv4.src_addr",value=gc.ipv4_to_bytes("192.168.10.50")),gc.KeyTuple("hdr.ipv4.dst_addr",value=gc.ipv4_to_bytes("192.168.10.12")),gc.KeyTuple("ig_md.hdr_srcport",value=22),gc.KeyTuple("ig_md.hdr_dstport",value=35396),gc.KeyTuple("hdr.ipv4.protocol",value=6)])
        data=checkNewFlowTable.make_data([gc.DataTuple('flag',1)],"SwitchIngress.setClassifiedFlag")
        checkNewFlowTable.entry_add(target,[key],[data])

def addTableEntryToFlowFilter(data_dict):
        target = gc.Target(device_id=0, pipe_id=0xffff)
        checkNewFlowTable = bfrt_info.table_get("SwitchIngress.checkNewFlow_tb")
        key = checkNewFlowTable.make_key([gc.KeyTuple("hdr.ipv4.src_addr",value=data_dict['src_addr']),gc.KeyTuple("hdr.ipv4.dst_addr",value=data_dict['dst_addr']),gc.KeyTuple("ig_md.hdr_srcport",value=data_dict['src_port']),gc.KeyTuple("ig_md.hdr_dstport",value=data_dict['dst_port']),gc.KeyTuple("hdr.ipv4.protocol",value=data_dict['protocol'])])
        data = checkNewFlowTable.make_data([gc.DataTuple('flag',data_dict['final_res'])],"SwitchIngress.setClassifiedFlag")
        checkNewFlowTable.entry_add(target,[key],[data])
   

def receive_digest():
    print("receive_digest......")
    # signal.signal(signal.SIGINT, quit)                                
    # signal.signal(signal.SIGTERM, quit)
    while True:
        digest = None
        try:
            digest = grpc_client.digest_get()
        except KeyboardInterrupt:
             break
        except Exception as e:
            if 'Digest list not received' not in str(e):
                print('Unexpected error receiving digest - [%s]', e)
        
        if digest:
            data_list = learn_filter.make_data_list(digest)
            if not data_list or len(data_list) == 0:
                data_list = learn_filter.make_data_list(digest)
            for data_item in data_list:
                data_dict = data_item.to_dict()
                try:
                    addTableEntryToFlowFilter(data_dict)
                    #print(data_dict)
                    print("receive one digest pkt ......")
                    src_addr = str(ipaddress.ip_address(data_dict['src_addr']))
                    dst_addr = str(ipaddress.ip_address(data_dict['dst_addr']))
                    #db.setClassifyResult(data_dict,src_addr, dst_addr)
                    #db.setFeature(data_dict)
                except Exception as e:
                    print('Unexpected error adding table entry - [%s]', e)    


if __name__ == '__main__':
    grpc_client=gc.ClientInterface(grpc_addr="172.23.20.70:50052",client_id=0,device_id=0)
    bfrt_info=grpc_client.bfrt_info_get(p4_name=None)
    grpc_client.bind_pipeline_config(p4_name=bfrt_info.p4_name)
    learn_filter = bfrt_info.learn_get("digest_a")
    # url = "http://218.199.84.19:8088"
    # token = "B1gnlW_Qhet5JNdijU1N3cGmxDlCzNQNKZkhKPIyqajXV5QBWOP8LkPWARc-20V0VR-yK6rtlwcQC064O7Pofw=="  # 对于InfluxDB 1.8，token通常是 username:password
    # org = "my-org"  # 对于InfluxDB 1.8，组织可以使用任意值，但通常使用 "-"
    # bucket = "classdb"
    # db = dbc.dbClient(url,token,org,bucket)
    if len(sys.argv) != 2:
        print('error')
    elif sys.argv[1] == 'add':
        print('add entries')
        addAllTableEntry()
    elif sys.argv[1] == 'del':
        print('del entries')
        delAllTableEntry()
    elif sys.argv[1] == 'get':
        print('get info entries')
        getInfo()
    elif sys.argv[1] == 'setFlow':
        print('set flow entries')
        setcheckNewFlowTable()
    elif sys.argv[1] == 'reset':
        print('reset')
        reset()
    else : 
        print('error')
    #接受digest数据包
    receive_digest() 