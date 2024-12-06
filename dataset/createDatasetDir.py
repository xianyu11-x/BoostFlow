import scapy.all as scapy
import pandas as pd
import os
#读取pcap文件，并按源IP、源端口、目的IP、目的端口和协议作为流标识，将每个流的前x个数据包按时间顺序存储在字典中
def read_pcap(pcap_file,x) -> dict:
    i=0
    flow  = {}
    for pkt in scapy.PcapReader(pcap_file):
        if pkt.haslayer('IP') and pkt['IP'].len > 0:
            src_ip = pkt['IP'].src
            dst_ip = pkt['IP'].dst
            proto = pkt['IP'].proto
            src_port=0
            dst_port=0
            if proto == 6:
                if pkt.haslayer('TCP'):
                    src_port = pkt['TCP'].sport
                    dst_port = pkt['TCP'].dport
            elif proto == 17:
                if pkt.haslayer('UDP'):
                    src_port = pkt['UDP'].sport
                    dst_port = pkt['UDP'].dport
            else:
                continue
            flow_id = dst_ip + '-' + src_ip + '-' + str(dst_port) + '-' + str(src_port) + '-' + str(proto)
            if flow_id not in flow.keys():
                flow[flow_id] = {}
                initFeature(flow[flow_id],pkt)
            if flow[flow_id]['pkt_num'] < x:
                updateFeature(flow[flow_id],pkt)
                i+=1
            if i == 10000 :
                print("read 10000 packets")
                i=0
    print("read all packets")
    return flow

def initFeature(flowInfo,pkt):
    flowInfo['total_length'] = 0
    flowInfo['pkt_num'] = 0
    flowInfo['max_pkt_length'] = 0
    flowInfo['min_pkt_length'] = 9999999
    flowInfo['min_pkt_interval'] = 9999999
    flowInfo['max_pkt_interval'] = 0
    flowInfo['dst_port'] = 0
    flowInfo['flow_duration'] = 0
    flowInfo['last_time'] = pkt.time

def updateFeature(flowInfo,pkt):
    pkt_len=pkt['IP'].len
    flowInfo['total_length'] += pkt_len
    if len(pkt) > flowInfo['max_pkt_length']:
        flowInfo['max_pkt_length'] = pkt_len
    if len(pkt) < flowInfo['min_pkt_length']:
        flowInfo['min_pkt_length'] = pkt_len
    pkt_interval = pkt.time - flowInfo['last_time']
    flowInfo['flow_duration']+=pkt_interval
    if flowInfo['pkt_num'] >0:
        if pkt_interval < flowInfo['min_pkt_interval']:
            flowInfo['min_pkt_interval'] = pkt_interval
        if pkt_interval > flowInfo['max_pkt_interval']:
            flowInfo['max_pkt_interval'] = pkt_interval
    proto = pkt['IP'].proto
    if proto == 6:
        if pkt.haslayer('TCP'):
            flowInfo['dst_port'] = pkt['TCP'].dport
    elif proto == 17:
        if pkt.haslayer('UDP'):
            flowInfo['dst_port'] = pkt['UDP'].dport
    flowInfo['last_time'] = pkt.time
    flowInfo['pkt_num'] += 1

#将字典中的流特征保存在csv文件中
def save_feature(flowsList,featureList, csv_file,featureIndexList=['Total Length of Fwd Packets',' Flow Duration',' Max Packet Length',' Destination Port',' Min Packet Length',' Flow IAT Min',' Flow IAT Max','Packet Num']):
    with open(csv_file, 'w') as f:
        f.write('FlowId,'+','.join(featureIndexList) + ',Label\n')
        for flow in flowsList:
            for key in flow.keys():
                f.write(key+','+','.join([str(flow[key][x]) for x in featureList]) + ',0\n')

#删除csv文件中 Flow IAT Max为0的行
def cleanFlow(csvPath,pktNum):
    df = pd.read_csv(csvPath)
    df = df[df[' Flow IAT Max'] != 0]
    df = df[df['Packet Num'] == pktNum]
    #把df中 Flow Duration、 Flow IAT Min、 Flow IAT Max列的值先乘以1000000000后右移16位转换为整数
    df[' Flow Duration'] = df[' Flow Duration'].apply(lambda x: int(x*1000000000/65536))
    df[' Flow IAT Min'] = df[' Flow IAT Min'].apply(lambda x: int(x*1000000000/65536))
    df[' Flow IAT Max'] = df[' Flow IAT Max'].apply(lambda x: int(x*1000000000/65536))
    #把df中 Flow Duration、 Flow IAT Min、 Flow IAT Max列中大于1048575的值转换位1048575
    df[' Flow Duration'] = df[' Flow Duration'].apply(lambda x: 1048575 if x > 1048575 else x)
    df[' Flow IAT Min'] = df[' Flow IAT Min'].apply(lambda x: 1048575 if x > 1048575 else x)
    df[' Flow IAT Max'] = df[' Flow IAT Max'].apply(lambda x: 1048575 if x > 1048575 else x)
    df.to_csv(csvPath, index=False)
    

def TON_iotIPLabel():
    ipList = []
    strIPPrefix = "192.168.1.3"
    for i in range(10):
        ipList.append(strIPPrefix + str(i))
    return ipList


def CICIDS2017_friLabel():
    ipList = ['172.16.0.1']
    return ipList

def findLabel(dstIp,srcIp,ipList):
    #ipList = ['192.168.1.165','192.168.1.223','192.168.1.248','192.168.1.227','192.168.1.241','192.168.1.129','192.168.1.239','192.168.1.119','192.168.1.163','192.168.1.118']
    ipset = set(ipList)
    if dstIp in ipset or srcIp in ipset:
        return 1
    else:
        return 0    
    

def setLabel(unLabeledCsvPath):
    df1=pd.read_csv(unLabeledCsvPath)
    df1['Label']=df1['Label'].apply(lambda x: 0)
    for i in range(len(df1)):
        flowIdList=df1.loc[i]['FlowId'].split('-')
        dstIp=flowIdList[0]
        srcIp=flowIdList[1]
        label = findLabel(dstIp,srcIp,CICIDS2017_friLabel())
        #if dstIp=='172.16.0.1' or srcIp=='172.16.0.1' or srcIp == '205.174.165.73' or dstIp == '205.174.165.73':
        #修改df1中该行对应Label列的值
        df1.loc[i,('Label')]=label
    df1.to_csv(unLabeledCsvPath, index=False)

if __name__ == '__main__':
    dataSetName = 'CICIDS2017-Fri'
    pcapPathDir = "./pcap/"+dataSetName
    #获取pcapPathDir目录下面的所有pcap文件列表
    pcapFileList = os.listdir(pcapPathDir)
    pcapFiles = [file for file in pcapFileList if file.endswith('.pcap')]
    #pcap_path='./pcap/iot-29.pcap'
    # #pcap_path='./smallFlows.pcap'
    flowList = []
    for pcapFile in pcapFiles:
        print("processing pcap file: ",pcapFile)
        flow = read_pcap(pcapPathDir+'/'+pcapFile,4)
        flowList.append(flow)
    featureList=['total_length','flow_duration','max_pkt_length','dst_port','min_pkt_length','min_pkt_interval','max_pkt_interval','pkt_num']
    save_feature(flowList,featureList, './origindata/'+dataSetName+'.csv')
    cleanFlow('./origindata/'+dataSetName+'.csv',4)
    setLabel('./origindata/'+dataSetName+'.csv')
    # setLabel('./origindata/Friday-Afternoon.csv','./origindata/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv')