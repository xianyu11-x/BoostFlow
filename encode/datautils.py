import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split

def prepareData(df):
    data=df.iloc[:,:-1]
    target=df.iloc[:,-1]
    # classes=['BENIGN','DDoS','DoS Hulk','DoS Slowhttptest','DoS GoldenEye','DoS slowloris','PortScan','Bot','Infiltration','Web_Attack_Brute_Force','Web_Attack_XSS','Web_Attack_Sql_Injection','Heartbleed','FTP-Patator','SSH-Patator']
    # valueList=[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    # data=data.drop(["Flow Bytes/s"," Flow Packets/s"],axis=1)
    featureList=['Total Length of Fwd Packets', ' Flow Duration', ' Max Packet Length', ' Destination Port', ' Min Packet Length', ' Flow IAT Min', ' Flow IAT Max']
    data=selectCol(data,featureList)
    data=changeDataIndex(data)
    # target=changeLabel(target,classes,valueList)
    return data,target

#修改输入数据的索引为feature0，feature1，feature2，...
def changeDataIndex(df):
    df.columns = ["feature" + str(i) for i in range(0, len(df.columns))]
    return df


def splitData(csvList,trainDataPath,testDataPath,test_size=0.2,random_state=7):
    j=1
    for i in csvList:
        df = pd.read_csv(i)
        data,target=prepareData(df)
        trainX, testX, trainY, testY = train_test_split(data,target, test_size=test_size, random_state=random_state)
        trainXY = pd.concat([trainX,trainY],axis=1)
        trainXY.to_csv(trainDataPath + j.__str__()+".csv")
        testXY= pd.concat([testX,testY],axis=1)
        testXY.to_csv(testDataPath + j.__str__()+".csv")
        j=j+1

#读取文件夹下所有csv文件
def readCsv(path):
    fileList = os.listdir(path)
    csvList = []
    for i in fileList:
        if i.endswith(".csv"):
            csvList.append(path+i)
    return csvList

#根据indexList提供的索引名称选取df中的指定列
def selectCol(df,indexList):
    df = df[indexList]
    return df

def changeLabel(df,labelList,valueList):
    df = df.replace(labelList,valueList)
    return df