import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report, precision_recall_fscore_support
import xgboost as xgb
import matplotlib.pyplot as plt
import numpy as np
import pickle
# 导入数据集
df = pd.read_csv("./origindata/univ_train.csv")
data=df.iloc[:,1:8]
target=df.iloc[:,-1]
 
# 切分训练集和测试集
train_x, test_x, train_y, test_y = train_test_split(data,target,test_size=0.2,random_state=7)
#将test_x和test_y合并并输出到csv文件中、
test_xy = pd.concat([test_x,test_y],axis=1)
base_classifier = DecisionTreeClassifier(max_depth=6)
ada_classfier = AdaBoostClassifier(n_estimators=4, base_estimator=base_classifier,learning_rate=0.1,random_state=42)
ada_classfier.fit(train_x, train_y)
y_pred = ada_classfier.predict(test_x)
F1score = 100*f1_score(test_y, y_pred, average='macro')
c_report = classification_report(test_y, y_pred, output_dict = True)
macro_f1 = 100*c_report['macro avg']['f1-score']

print("####")
print("Macro F1-score:", F1score)
print('Macro F1-score (from c. rep.): ', macro_f1)
save_path = './ada_model.pkl'
pickle.dump(ada_classfier, open(save_path, 'wb'))

#xgboost模型初始化设置
dtrain=xgb.DMatrix(train_x,label=train_y)
dtest=xgb.DMatrix(test_x)
watchlist = [(dtrain,'train')]

# booster:
params={'booster':'gbtree',
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'max_depth':6,
        'lambda':10,
        'subsample':0.75,
        'colsample_bytree':0.75,
        'min_child_weight':2,
        'eta': 0.025,
        'seed':0,
        'nthread':8,
        'gamma':0.15,
        'learning_rate' : 0.01,}

# 建模与预测：50棵树
bst=xgb.train(params,dtrain,num_boost_round=4,evals=watchlist)
ypred=bst.predict(dtest)
# ypred_list=bst.predict(dtest, pred_contribs=True)
# score_list=[]
# ypred_s_list=[]
# for ypred_contrib in ypred_list:
#         score_list.append(sum(ypred_contrib))
#         ypred_s_list.append(1/float(1+np.exp(-sum(ypred_contrib))))
 # 设置阈值、评价指标
y_pred = (ypred >= 0.5)*1
#把y_pred输出到csv文件中
y_pred_df = pd.DataFrame(y_pred)
y_pred_df.to_csv("./y_pred.csv",index=False)
print ('Precesion: %.4f' %metrics.precision_score(test_y,y_pred))
print ('Recall: %.4f' % metrics.recall_score(test_y,y_pred))
print ('F1-score: %.4f' %metrics.f1_score(test_y,y_pred))
print ('Accuracy: %.4f' % metrics.accuracy_score(test_y,y_pred))
print ('AUC: %.4f' % metrics.roc_auc_score(test_y,ypred))

# ypred = bst.predict(dtest)
# print("测试集每个样本的得分\n",ypred)
ypred_leaf = bst.predict(dtest, pred_leaf=True)
print("测试集每棵树所属的节点数\n",ypred_leaf)
# ypred_contribs = bst.predict(dtest, pred_contribs=True)
# print("特征的重要性\n",ypred_contribs )                                              

xgb.plot_importance(bst,height=0.8,title='important feature', ylabel='features')
plt.rc('font', family='Arial Unicode MS', size=14)
plt.show()
plt.savefig('./fig.png')

# #bst.save_model('model1.json')
bst.dump_model('./encode/dump2.txt')
# #pickle.dump(bst, open("xgb_model_1", 'wb'))
