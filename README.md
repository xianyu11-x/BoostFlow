# BoostFlow:基于网内智能的异常检测框架

## 文件结构

encode/ 树模型嵌入编码

simulator/ 框架行为模拟器

test/ 测试脚本

controller.py 控制器

BoostFlow.p4 数据平面代码

## 使用方式

1. p4代码编译
   1. 虚拟机里面的P4环境
      1. `cmake $SDE/p4studio/ -DCMAKE_INSTALL_PREFIX=$SDE/install/ -DCMAKE_MODULE_PATH=$SDE/cmake/ -DP4_NAME=<名字> -DP4_PATH=<程序路径>`
      2. `make install`
   2. 交换机
      1. `p4_build-9.x.y.sh <路径>`
2. 运行数据面代码
   1. 模拟器
      1. `run_tofino_model -p <名字/文件名> //启动模拟asic`
      2. `run_switchd -p <名字/文件名> //启动交换机`
   2. 交换机
      1. `run_switchd -p <名字/文件名> //启动交换机`
      2. `run_bfshell.sh -f port_up.txt //配置端口`
3. 控制面代码
   1. `python controller.py <参数>`
      1. add 加载流表(会直接从模型表示文件生成流表)
      2. del 清空流表
      3. reset 清空数据
4. 重放流量
   1. `tcpreplay -i <端口> <pcap文件>`
5. 收集流量
   1. `tcpdump -i <端口> -w <输出文件>`

## 模型编码

1. 使用train_ids_tree.py训练模型
2. format_txt.py 格式化模型表示文件
3. parser_tree 将模型编码为对应的流表项
