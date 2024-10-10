import crcmod

class packetInfo:
    def __init__(self,srcIP=0,dstIP=0,srcPort=0,dstPort=0,protocol=0,timestamp = 0,pktLen = 1) -> None:
        self.srcIP = srcIP
        self.dstIP = dstIP
        self.srcPort = srcPort
        self.dstPort = dstPort
        self.protocol = protocol
        self.timestamp = timestamp
        self.pktLen = pktLen

class featureMethods:
    def __init__(self) -> None:
        self.MethodDict= {
            'totalLength':self.totalLength,
            'flowDuration':self.flowDuration,
            'maxPktLength':self.maxPktLength,
            'minPktLength':self.minPktLength,
            'minPktInterval':self.minPktInterval,
            'maxPktInterval':self.maxPktInterval,
            'dstPort':self.dstPort
        }
    
    def totalLength(self,featureDict,pktInfo):
        return featureDict['totalLength'] + pktInfo.pktLen

    def flowDuration(self,featureDict,pktInfo):
        return featureDict['flowDuration'] + pktInfo.timestamp - featureDict['timestamp']

    def maxPktLength(self,featureDict,pktInfo):
        if featureDict['count'] == 1:
            return pktInfo.pktLen
        return max(featureDict['maxPktLength'],pktInfo.pktLen)
    
    def minPktLength(self,featureDict,pktInfo):
        if featureDict['count'] == 1:
            return pktInfo.pktLen
        return min(featureDict['minPktLength'],pktInfo.pktLen)
    
    def minPktInterval(self,featureDict,pktInfo):
        if featureDict['count'] == 1:
            return 1<<16
        return min(featureDict['minPktInterval'],pktInfo.timestamp - featureDict['timestamp'])
    
    def maxPktInterval(self,featureDict,pktInfo):
        if featureDict['count'] == 1:
            return 0
        return max(featureDict['maxPktInterval'],pktInfo.timestamp - featureDict['timestamp'])
    
    def dstPort(self,featureDict,pktInfo):
        return pktInfo.dstPort
    
    def getMethods(self,nameList):
        methodDict = {}
        for name in nameList:
            methodDict[name] = self.MethodDict[name]
        return methodDict
    
    
class featureManagemnet:
    def __init__(self,featureMethodDict:dict,featureLists:list,bitsLen=16,maxPktCount = 4) -> None:
        self.bitsLen = bitsLen
        self.IndexReg = [0]*(1<<bitsLen)
        self.countReg = [0]*(1<<bitsLen)
        self.timestampReg = [0]*(1<<bitsLen)
        self.featureDict = {}
        self.maxPktCount = maxPktCount
        self.featureMethodDict = featureMethodDict
        for feature in featureLists:
            self.featureDict[feature] = [0]*(1<<bitsLen)
    
    def update(self,pktInfo=packetInfo()):
        update_flag = False
        flow_id = self.CRC32([pktInfo.srcIP,pktInfo.dstIP,pktInfo.srcPort,pktInfo.dstPort,pktInfo.protocol])
        reg_id = self.CRC16([pktInfo.srcIP,pktInfo.dstIP,pktInfo.srcPort,pktInfo.dstPort,pktInfo.protocol])
        if self.IndexReg[reg_id] == 0:
            update_flag = True
            self.IndexReg[reg_id] = flow_id
            self.countReg[reg_id] = 1
            self.timestampReg[reg_id] = pktInfo.timestamp
            self.calFeature(reg_id,pktInfo)            
            # for i in range(len(self.featureDict)):
            #     self.featureDict[i][reg_id] = pktInfo.pktLen
        else:
            if self.IndexReg[reg_id] == flow_id:
                update_flag = True
                self.countReg[reg_id] += 1
                self.calFeature(reg_id,pktInfo)
                self.timestampReg[reg_id] = pktInfo.timestamp
                # for i in range(len(self.featureDict)):
                #     self.featureDict[i][reg_id] += pktInfo.pktLen
            elif self.countReg[reg_id] == self.maxPktCount:
                update_flag  = True
                self.clearReg(reg_id)
                self.IndexReg[reg_id] = flow_id
                self.countReg[reg_id] = 1
                self.timestampReg[reg_id] = pktInfo.timestamp
                self.calFeature(reg_id,pktInfo)
                # for i in range(len(self.featureDict)):
                #     self.featureDict[i][reg_id] = pktInfo.pktLen
        return update_flag,flow_id,reg_id
    
    def CRC32(self,data):
        input_data =""
        for i in data:
            input_data += str(i)
        crc32_func = crcmod.predefined.mkPredefinedCrcFun('crc-32')
        return crc32_func(bytes(input_data,encoding='utf-8'))
    
    def CRC16(self,data):
        input_data =""
        for i in data:
            input_data += str(i)
        crc16_func = crcmod.predefined.mkPredefinedCrcFun('crc-16')
        return crc16_func(bytes(input_data,encoding='utf-8'))
    
    
    def clearReg(self,reg_id):
        self.IndexReg[reg_id] = 0
        self.countReg[reg_id] = 0
        self.timestampReg[reg_id] = 0
        for name,feature in self.featureDict.items():
            feature[reg_id] = 0
    
    def calFeature(self,reg_id,pktInfo):
        for name,method in self.featureMethodDict.items():
            self.featureDict[name][reg_id] = method(self.getFeature(reg_id),pktInfo)
    
    def getCount(self,reg_id):
        return self.countReg[reg_id]
    
    def getTimestamp(self,reg_id):
        return self.timestampReg[reg_id]
    
    def getFeature(self,reg_id):
        pktFeature = {}
        pktFeature['count'] = self.countReg[reg_id]
        pktFeature['timestamp'] = self.timestampReg[reg_id]
        for name,feature in self.featureDict.items():
            pktFeature[name] = feature[reg_id]
        return pktFeature 
