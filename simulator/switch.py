import feature
import treemodel





if __name__ == "__main__":
    allMethods = feature.featureMethods()
    featureList = ['totalLength','flowDuration','maxPktLength','minPktLength','minPktInterval','maxPktInterval','dstPort']
    methodDict = allMethods.getMethods(featureList)
    featureManager = feature.featureManagemnet(methodDict,featureList)
    pkt = feature.packetInfo(2381312,2381313,80,80,6,0,100)
    flag,regID,flowID = featureManager.update(pkt)
    print(flag,regID,flowID)
    print(featureManager.getFeature(flowID))
    pkt2 = feature.packetInfo(2381312,2381313,80,80,6,123,100)
    flag,regID,flowID = featureManager.update(pkt2)
    print(flag,regID,flowID)
    print(featureManager.getFeature(flowID))