class featureManagemnet:
    def __init__(self,bitsLen=16,featureNum=7) -> None:
        self.bitsLen = bitsLen
        self.IndexReg = [0]*(1<<bitsLen)
        self.countReg = [0]*(1<<bitsLen)
        self.featureDict = {}
        for i in range(featureNum):
            self.featureDict[i] = [0]*(1<<bitsLen)
    
    def update(self,pktInfo):
        pass
    
    