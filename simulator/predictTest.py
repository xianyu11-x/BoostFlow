import switch
import feature
import socket
import csv
import scapy.all as scapy


def getCICTrueLabel(pktInfo:feature.packetInfo):
    if pktInfo.srcIP == "172.16.0.1" or pktInfo.dstIP == "172.16.0.1":
        return 1
    else:
        return 0



if __name__ == "__main__":
    featureList = [
        "totalLength",
        "flowDuration",
        "maxPktLength",
        "dstPort",
        "minPktLength",
        "minPktInterval",
        "maxPktInterval",
    ]
    modelPath = "/home/monitor/p4app/BoostFlow/encode/model/model1.json"
    pcapPath = "/home/monitor/p4app/BoostFlow/dataset/Friday-Afternoon.pcap"
    s = switch.switch(modelPath, featureList, 16)
    countRegSnapshot = s.featureManager.countReg.copy()
    flowIDRegSnapshot = s.featureManager.IndexReg.copy()
    expiredTime = int(30 * 1000000000 / 65536)
    lastTime = 0
    classifyNum = 0
    trueNum = 0
    for pkt in scapy.PcapReader(pcapPath):
        if pkt.haslayer("IP"):
            srcIP = socket.inet_aton(pkt["IP"].src)
            dstIP = socket.inet_aton(pkt["IP"].dst)
            srcPort = 0
            dstPort = 0
            protocol = pkt["IP"].proto
            if protocol == 6 and pkt.haslayer("TCP"):
                srcPort = pkt["TCP"].sport
                dstPort = pkt["TCP"].dport
            elif protocol == 17 and pkt.haslayer("UDP"):
                srcPort = pkt["UDP"].sport
                dstPort = pkt["UDP"].dport
            else:
                continue
            time = int(pkt.time * 1000000000 / 65536)
            if time - lastTime > expiredTime:
                for i in range(s.featureManager.totalReg):
                    if (
                        s.featureManager.countReg[i] == countRegSnapshot[i]
                        and s.featureManager.IndexReg[i] == flowIDRegSnapshot[i]
                    ):
                        s.featureManager.clearReg(i)
                countRegSnapshot = s.featureManager.countReg.copy()
                flowIDRegSnapshot = s.featureManager.IndexReg.copy()
                lastTime = time
            pktInfo = feature.packetInfo(
                srcIP, dstIP, srcPort, dstPort, protocol, time, pkt.len
            )
            flag, res = s.process(pktInfo)
            if flag == -1 :
                classifyNum+=1
            elif flag == 0 and res > 0:
                trueLabel = getCICTrueLabel(pktInfo)
                if trueLabel == res:
                    trueNum+=1
                classifyNum+=1
    print("classifyNum:",classifyNum)
    print("trueNum:",trueNum)
    print("accuracy:",trueNum/classifyNum)
