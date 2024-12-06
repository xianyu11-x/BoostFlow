import feature
import treemodel
import xgboost as xgb
import pandas as pd

class switch:
    def __init__(self,modelPath,featureList:list,bitsLen=16,maxPktCount = 4) -> None:
        self.filter = {}
        allMethods = feature.featureMethods()
        self.featureList = ['totalLength','flowDuration','maxPktLength','minPktLength','minPktInterval','maxPktInterval','dstPort']
        methodDict = allMethods.getMethods(featureList)
        self.featureManager = feature.featureManagemnet(methodDict,featureList,bitsLen,maxPktCount)
        self.totalNum = 0
        self.collsionNum = 0
        self.trees = treemodel.TreeModel('xgboost',modelPath)
        
    def process(self,pkt:feature.packetInfo):
        flow_id = str(pkt.srcIP) + '_' + str(pkt.srcPort) + '_' + str(pkt.dstIP) + '_' + str(pkt.dstPort) + '_' + str(pkt.protocol)
        if flow_id in self.filter:
            self.filter[flow_id]['count'] += 1
            self.totalNum += 1
            return -2,self.filter[flow_id]['flag']
        flag,flowID,regID = self.featureManager.update(pkt)
        #print(flowID,regID)
        ypred = -1
        if flag == False:
            self.collsionNum += 1
            self.totalNum += 1
            return -1,-1
        else :
            if self.featureManager.getCount(regID) == self.featureManager.maxPktCount:
                featureDict = self.featureManager.getFeature(regID)
                features = []
                for featureName in self.featureList:
                    features.append(featureDict[featureName])
                ypred = self.trees.predict(features)
                self.filter[flow_id] = {}
                self.filter[flow_id]['count'] = 0
                self.filter[flow_id]['flag'] = ypred
        self.totalNum += 1     
        return 0,ypred

    def getCollsionInfo(self):
        return self.collsionNum,self.totalNum

if __name__ == "__main__":
    allMethods = feature.featureMethods()
    featureList = ['totalLength','flowDuration','maxPktLength','dstPort','minPktLength','minPktInterval','maxPktInterval']
    methodDict = allMethods.getMethods(featureList)
    featureManager = feature.featureManagemnet(methodDict,featureList,16)
    pkt = feature.packetInfo(2381312,2381313,80,80,6,0,100)
    flag,regID,flowID = featureManager.update(pkt)
    print(flag,regID,flowID)
    print(featureManager.getFeature(flowID))
    pkt2 = feature.packetInfo(2381312,2381313,80,80,6,123,100)
    flag,regID,flowID = featureManager.update(pkt2)
    print(flag,regID,flowID)
    print(featureManager.getFeature(flowID))
    # features=[]
    # for featureName in featureList:
    #     features.append(featureManager.getFeature(flowID)[featureName])
    # ListName = ['feature0', 'feature1', 'feature2', 'feature3', 'feature4', 'feature5', 'feature6']
    # feature_df = pd.DataFrame([features], columns=ListName)
    # model = xgb.Booster()
    # model.load_model("/home/monitor/p4app/BoostFlow/encode/model/model1.json")
    # dtest = xgb.DMatrix(feature_df)
    # y = model.predict(dtest)
    # print(y)