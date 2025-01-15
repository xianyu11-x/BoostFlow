from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
class dbClient:
    
    # def __init__(self, host, port,user="admin",passwd = "Admin@123",dbname = ''):
    #     self.host = host
    #     self.port = port
    #     self.user = user
    #     self.passwd = passwd
    #     self.dbname = dbname
    #     self.client = InfluxDBClient(host, port, user, passwd, database=dbname)
    def __init__(self,url,token,org,bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def setClassifyResult(self, classifyResultDict,src_addr, dst_addr):
        if classifyResultDict['protocol']  == 0 or classifyResultDict['src_port'] == 0 or classifyResultDict['dst_port'] == 0:
            return
        if classifyResultDict['protocol']  == 6:
            protocol = "TCP"
        elif classifyResultDict['protocol'] == 17:
            protocol = "UDP"
        else:
            protocol = "Other"
            
        if classifyResultDict['final_res'] == 1:
            class_res = "normal"
        elif classifyResultDict['final_res'] == 2:
            class_res = "abnormal"
        else:
            class_res = "unknown"
            
        # info_data = [ 
        # {
        #     'measurement': "class_info", # table name 
        #     'fields': {
        #         'protocol': protocol,
        #         'srcIP' : src_addr,
        #         'srcPort' : classifyResultDict['src_port'],
        #         'dstIP' : dst_addr,
        #         'dstPort' : classifyResultDict['dst_port'],
        #         'class': class_res
        #     }
        # }
        # ]
        # self.client.write_points(info_data,time_precision="u")
        point = Point("class_info").field("protocol", protocol).field("srcIP", src_addr).field("srcPort", str(classifyResultDict['src_port'])).field("dstIP", dst_addr).field("dstPort", str(classifyResultDict['dst_port'])).field("class", class_res)
        line_protocol = point.to_line_protocol()
        self.write_api.write(bucket=self.bucket, org=self.org, record=line_protocol)
        
    def setFeature(self, FeatureDict):            
        if FeatureDict['final_res'] == 1:
            class_res = "normal"
        elif FeatureDict['final_res'] == 2:
            class_res = "abnormal"
        else:
            class_res = "unknown"
            
        # info_data = [
        # {
        #     'measurement': "class_info", # table name 
        #     'fields': {
        #         'protocol': protocol,
        #         'srcIP' : src_addr,
        #         'srcPort' : classifyResultDict['src_port'],
        #         'dstIP' : dst_addr,
        #         'dstPort' : classifyResultDict['dst_port'],
        #         'class': class_res
        #     }
        # }
        # ]
        # self.client.write_points(info_data,time_precision="u")
        point = Point("feature_info").field("flow_iat_max", str(FeatureDict['flow_iat_max'])).field("flow_iat_min", str(FeatureDict['flow_iat_min'])).field("flow_duration", str(FeatureDict['flow_duration'])).field("pkt_len_max", str(FeatureDict['pkt_len_max'])).field("pkt_len_min", str(FeatureDict['pkt_len_min'])).field("pkt_len_total", str(FeatureDict['pkt_len_total'])).field("dstPort", str(FeatureDict['dst_port'])).field("class", class_res)
        line_protocol = point.to_line_protocol()
        self.write_api.write(bucket=self.bucket, org=self.org, record=line_protocol)
        featureList = [str(FeatureDict['pkt_len_total']),str(FeatureDict['flow_duration']),str(FeatureDict['pkt_len_max']), str(FeatureDict['dst_port']),str(FeatureDict['pkt_len_min']),str(FeatureDict['flow_iat_min']),str(FeatureDict['flow_iat_max'])]
        featureListStr = ",".join(featureList)
        return featureListStr