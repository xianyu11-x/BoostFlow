from scapy.all import *
import pandas as pd
Ether = scapy.layers.l2.Ether
df=pd.read_csv("./test_xy.csv")
ypred=pd.read_csv("./y_pred.csv")
y_pred=ypred.iloc[:,0]
data=df.iloc[:,:8]
target=df.iloc[:,-1]
test_count=len(target)
ture_count=0
pc_count=0
same_count=0
#读取ans.pcap文件获取Raw数据并转换为16进制str
ans=rdpcap("./ans32_5.pcap")
for i in range(len(target)):
    target_value=target.iloc[i]
    all_data=ans[i][Raw].load.hex()
    if target_value==int(all_data[2:4]):
        ture_count+=1
    if target_value==y_pred.iloc[i]:
        pc_count+=1
    if y_pred.iloc[i]==int(all_data[2:4]):
        same_count+=1
    else:
        print(i)
print(ture_count/test_count)
print(pc_count/test_count)
print(same_count/test_count)
