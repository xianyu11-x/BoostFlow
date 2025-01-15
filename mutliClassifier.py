import xgboost as xgb
import fifo
import simulator.treemodel as treemodel


def predict(msg):
    data = msg.split(',')
    data = [int(i) for i in data]
    ypred = model.predict(data)
    print(ypred)

if __name__ == "__main__":
    modelPath = 'encode/model/model1.json'
    modelType = 'xgboost'
    model = treemodel.TreeModel(modelType,modelPath)
    print('model loaded')
    fifo.reader(predict)




