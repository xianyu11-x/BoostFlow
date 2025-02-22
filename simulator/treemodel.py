import xgboost as xgb
import pandas as pd

class TreeModel:
    def __init__(self, model_type, model_path,class_num=2):
        self.model_type = model_type
        self.model_path = model_path
        self.class_num = class_num
        self.load_model(model_path)
        
    
    def load_model(self, model_path):
        if self.model_type == 'xgboost':
            self.model = xgb.Booster()
            self.model.load_model(model_path)
        else:
            self.model = None
            
    def predict(self, data):
        if self.model_type == 'xgboost':
            ListName = []
            for i in range(len(data)):
                ListName.append('feature'+str(i))
            data_df = pd.DataFrame([data], columns=ListName)
            dtest = xgb.DMatrix(data_df)
            ypred = self.model.predict(dtest)
            if self.class_num == 2:
                ypred = (ypred >= 0.5)*1+1
            return ypred
        else:
            return None