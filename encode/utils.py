import numpy as np

def findNextSplit(minv,maxv):
    count=0
    while (minv>>count)&1==0 and (minv+(1<<count))<maxv:
        count+=1
    if (minv+(1<<count))>maxv:
        return 1<<(count-1)
    return 1<<count

def rangeToTernary(minv,maxv):
    if maxv<minv:
        return [],[]
    if maxv == minv:
        return [minv],[0]
    startNum = []
    addNum = []
    while True:
        count = findNextSplit(minv,maxv)
        startNum.append(minv)
        addNum.append(count)
        if minv+count==maxv:
            break
        minv+=count
    return startNum,addNum

def get_mask(maxBits, maskNum):
    if maskNum>0:
        maskbits = int(np.log2(maskNum))
    else:
        maskbits=0
    result = '0b'
    for i in range(maxBits-maskbits):
        result+='1'
    for i in range(maskbits):
        result+='0'
    return result

if __name__ == '__main__':
    # originDataPath = "./origindata/"
    # trainDataPath = "./traindata/"
    # testDataPath = "./testdata/"
    # csvList = readCsv(originDataPath)
    # splitData(csvList,trainDataPath,testDataPath)
    # print("done")
    startNum,addNum=rangeToTernary(0,9)
    print(startNum)
    print(addNum)
    res= get_mask(4,2)
    print(res)
    # print(startNum)
    # print(addNum)
    # l=[1,2,2,3]
    # np_array=np.array(l)
    # index=np.where(np_array==2)[0]
    # print(index[0])
    # print(index[-1])
    