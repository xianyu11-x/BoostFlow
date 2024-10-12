import switch
import feature
import socket
import csv
import scapy.all as scapy

if __name__ == '__main__':
    featureList = ['totalLength','flowDuration','maxPktLength','dstPort','minPktLength','minPktInterval','maxPktInterval']
    modelPath = '/home/monitor/p4app/BoostFlow/encode/model/model1.json'
    s = switch.switch(modelPath,featureList)
    pcapPath = '/home/monitor/p4app/BoostFlow/dataset/Friday-Afternoon.pcap'
    expiredTime = int(30 *1000000000/65536)
    lastTime = 0
    countRegSnapshot = s.featureManager.countReg.copy()
    flowIDRegSnapshot = s.featureManager.IndexReg.copy()
    with open('/home/monitor/p4app/BoostFlow/simulator/output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Collision','TotalNum', 'Used Reg Num'])
        for pkt in scapy.PcapReader(pcapPath):
            if pkt.haslayer('IP') :  
                srcIP = socket.inet_aton(pkt['IP'].src)
                dstIP = socket.inet_aton(pkt['IP'].dst)
                srcPort = 0
                dstPort = 0
                protocol = pkt['IP'].proto
                if protocol == 6 and pkt.haslayer('TCP'):
                    srcPort = pkt['TCP'].sport
                    dstPort = pkt['TCP'].dport
                elif protocol == 17 and pkt.haslayer('UDP'):
                    srcPort = pkt['UDP'].sport
                    dstPort = pkt['UDP'].dport
                else:
                    continue
                time = int(pkt.time*1000000000/65536)
                if time - lastTime > expiredTime:
                    for i in range(s.featureManager.totalReg):
                        if s.featureManager.countReg[i] == countRegSnapshot[i] and s.featureManager.IndexReg[i] == flowIDRegSnapshot[i]:
                            s.featureManager.clearReg(i)
                    countRegSnapshot = s.featureManager.countReg.copy()
                    flowIDRegSnapshot = s.featureManager.IndexReg.copy()
                    lastTime = time
                pktInfo = feature.packetInfo(srcIP,dstIP,srcPort,dstPort,protocol,time,pkt.len)
                s.process(pktInfo)
                collisionNum,totalNum = s.getCollsionInfo()
                used_reg_num = s.featureManager.getUsedRegNum()
                writer.writerow([collisionNum,totalNum, used_reg_num])
