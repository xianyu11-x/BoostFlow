import scapy.all as scapy

#读取pcap文件，并按源IP、源端口、目的IP、目的端口和协议作为流标识，将流中的数据包按时间顺序存储在字典中
def read_pcap(pcap_file) -> dict:
    flow = {}
    for pkt in scapy.PcapReader(pcap_file):
        if pkt.haslayer('IP'):
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
            flow_id = src_ip + '_' + str(src_port) + '_' + dst_ip + '_' + str(dst_port) + '_' + str(proto)
            if flow_id not in flow.keys():
                flow[flow_id] = []
            flow[flow_id].append(pkt)
    print("read all packets")
    return flow

#遍历字典中的流，将每个流前3个数据包总长度、流持续时间、最大数据包长度、目的端口、最小数据包长度、最小数据包间隔时间和最大数据包间隔时间作为值，将流标签作为键，保存在字典中。
def get_feature(flow) -> dict:
    feature = {}
    for key in flow.keys():
        pkt_list = flow[key]
        total_length = 0
        max_pkt_length = 0
        min_pkt_length = 9999999
        min_pkt_interval = 9999999
        max_pkt_interval = 0
        for i in range(min(len(pkt_list),3)):
            total_length += len(pkt_list[i])
            if len(pkt_list[i]) > max_pkt_length:
                max_pkt_length = len(pkt_list[i])
            if len(pkt_list[i]) < min_pkt_length:
                min_pkt_length = len(pkt_list[i])
            if i > 0:
                pkt_interval = pkt_list[i].time - pkt_list[i-1].time
                if pkt_interval < min_pkt_interval:
                    min_pkt_interval = pkt_interval
                if pkt_interval > max_pkt_interval:
                    max_pkt_interval = pkt_interval
        flow_duration = pkt_list[-1].time - pkt_list[0].time
        proto = pkt_list[0]['IP'].proto
        if proto == 6:
            dst_port = pkt_list[0]['TCP'].dport
        elif proto == 17:
            dst_port = pkt_list[0]['UDP'].dport
        feature[key] = [total_length, flow_duration, max_pkt_length, dst_port, min_pkt_length, min_pkt_interval, max_pkt_interval]
    return feature

#将字典中的流特征保存在csv文件中
def save_feature(feature, csv_file,featureIndexList=['Total Length of Fwd Packets',' Flow Duration',' Max Packet Length',' Destination Port',' Min Packet Length',' Flow IAT Min',' Flow IAT Max']):
    with open(csv_file, 'w') as f:
        f.write(','.join(featureIndexList) + ',Label\n')
        for key in feature.keys():
            f.write(','.join([str(x) for x in feature[key]]) + ',1\n')


if __name__ == '__main__':
    pcap_path='./pcap/Friday-WorkingHours.pcap'
    flow = read_pcap(pcap_path)
    feature = get_feature(flow)
    save_feature(feature, './origindata/Friday-WorkingHours.csv')