#include <core.p4>
#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

typedef bit<48> mac_addr_t;
typedef bit<32> ipv4_addr_t;
typedef bit<128> ipv6_addr_t;
typedef bit<12> vlan_id_t;
typedef bit<16> ether_type_t;

const bit<16>       TYPE_RECIRC = 0x88B5; //ether type for recirculated packets
const bit<16>       TYPE_IPV4 = 0x800;
const bit<8>        TYPE_TCP = 6;
const bit<8>        TYPE_UDP = 17;
const bit<32>       MAX_REGISTER_ENTRIES = 65536;
#define timeOutThreshold 10
#define INDEX_WIDTH 16
#define MAX_TABLE_SIZE (1 << INDEX_WIDTH)
const ether_type_t ETHERTYPE_IPV4 = 16w0x0800;
const ether_type_t ETHERTYPE_ARP = 16w0x0806;
const ether_type_t ETHERTYPE_IPV6 = 16w0x86dd;
const ether_type_t ETHERTYPE_VLAN = 16w0x8100;
const ether_type_t ETHERTYPE_DT = 16w0x8800;

header ethernet_h {
    mac_addr_t dst_addr;
    mac_addr_t src_addr;
    bit<16> etherType;
}

header recirc_h {
    bit<8>       class_result;
    bit<16>      etherType;
}

header vlan_tag_h {
    bit<3> pcp;
    bit<1> cfi;
    vlan_id_t vid;
    bit<16> ether_type;
}

/* IPV4 header */
header ipv4_h {
    bit<4>       version;
    bit<4>       ihl;
    bit<8>       diffserv;
    bit<16>      total_len;
    bit<16>      identification;
    bit<3>       flags;
    bit<13>      frag_offset;
    bit<8>       ttl;
    bit<8>       protocol;
    bit<16>      hdr_checksum;
    ipv4_addr_t  src_addr;
    ipv4_addr_t  dst_addr;
}

/* TCP header */
header tcp_h {
    bit<16> src_port;
    bit<16> dst_port;
    bit<32> seq_no;
    bit<32> ack_no;
    bit<4>  data_offset;
    bit<4>  res;
    bit<1>  cwr;
    bit<1>  ece;
    bit<1>  urg;
    bit<1>  ack;
    bit<1>  psh;
    bit<1>  rst;
    bit<1>  syn;
    bit<1>  fin;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgent_ptr;
}

/* UDP header */
header udp_h {
    bit<16> src_port;
    bit<16> dst_port;
    bit<16> udp_total_len;
    bit<16> checksum;
}

header payload_h {
    bit<32> payload;
}


struct digest_a_t{
    bit<32> src_addr;
    bit<32> dst_addr;
    bit<16> src_port;
    bit<16> dst_port;
    bit<8> protocol;
    bit<8> final_res;
    bit<32> flow_iat_max;
    bit<32> flow_iat_min;
    bit<32> flow_duration;
    bit<16> pkt_len_max;
    bit<16> pkt_len_min;
    bit<16> pkt_len_total;
} 


struct header_t {
    ethernet_h   ethernet;
    recirc_h     recirc;
    vlan_tag_h   vlan_tag;
    ipv4_h       ipv4;
    tcp_h        tcp;
    udp_h        udp;
}

//#define feature_encode(name,tree) 


struct ig_metadata_t {
    // flags for flow management
    bit<4> is_first;
    bit<8> classified_flag;
    //bit<1> is_hash_collision;
    bit<2> state;
    bit<4> classifiedFlowFlag;
    // ID and idex for flow management
    bit<32> flow_ID;
    //bit<32> flowInfo;
    //bit<1> is_timeout;
    bit<(INDEX_WIDTH)> register_index;
    bit<16> tmp_etherType;
    // features and necessary variables
    bit<32> flow_iat_max;
    bit<32> flow_iat_min;
    bit<32> flow_duration;
    bit<32> time_last_pkt;
    bit<8> pkt_count;
    bit<16> hdr_srcport;
    bit<16> hdr_dstport;
    bit<16> pkt_len_max;
    bit<16> pkt_len_min;
    bit<16> pkt_len_total;
    bit<32> iat;
    bit<32> payload1;
    bit<32> payload2;
    bit<32> payload3;
    // features for tree
    bit<4> feature0encode1;
    bit<4> feature0encode2;
    bit<4> feature0encode3;
    bit<4> feature0encode4;
    bit<4> feature1encode1;
    bit<4> feature1encode2;
    bit<4> feature1encode3;
    bit<4> feature1encode4;
    bit<4> feature2encode1;
    bit<4> feature2encode2;
    bit<4> feature2encode3;
    bit<4> feature2encode4;
    bit<4> feature3encode1;
    bit<4> feature3encode2;
    bit<4> feature3encode3;
    bit<4> feature3encode4;
    bit<4> feature4encode1;
    bit<4> feature4encode2;
    bit<4> feature4encode3;
    bit<4> feature4encode4;
    bit<4> feature5encode1;
    bit<4> feature5encode2;
    bit<4> feature5encode3;
    bit<4> feature5encode4;
    bit<4> feature6encode1;
    bit<4> feature6encode2;
    bit<4> feature6encode3;
    bit<4> feature6encode4;
    bit<8> resTree1;
    bit<8> resTree2;
    bit<8> resTree3;
    bit<8> resTree4;
    bit<8> resTree5;
    bit<8> resTree6;
    bit<8> finres;
    bit<8> final_class;
}
struct eg_metadata_t {
}

parser TofinoIngressParser(
        packet_in pkt,
        inout ig_metadata_t ig_md,
        out ingress_intrinsic_metadata_t ig_intr_md) {
    state start {
        pkt.extract(ig_intr_md);
        transition select(ig_intr_md.resubmit_flag) {
            1 : parse_resubmit;
            0 : parse_port_metadata;
        }
    }

    state parse_resubmit {
        // Parse resubmitted packet here.
        pkt.advance(64); 
        transition accept;
    }

    state parse_port_metadata {
        pkt.advance(64);  //tofino 1 port metadata size
        transition accept;
    }
}

parser SwitchIngressParser(
        packet_in pkt,
        out header_t hdr,
        out ig_metadata_t ig_md,
        out ingress_intrinsic_metadata_t ig_intr_md) {

    TofinoIngressParser() tofino_parser;

    state start {
        tofino_parser.apply(pkt, ig_md, ig_intr_md);
        transition parse_ethernet;
    }


    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_RECIRC : parse_recirc;
            TYPE_IPV4:  parse_ipv4;
            ETHERTYPE_VLAN: parse_vlan;
            default: accept;
        }
    }

    state parse_vlan{
        pkt.extract(hdr.vlan_tag);
        transition select(hdr.vlan_tag.ether_type) {
            ETHERTYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_recirc {
       pkt.extract(hdr.recirc);
       transition select(hdr.recirc.etherType) {
            ETHERTYPE_IPV4: parse_ipv4;
            ETHERTYPE_VLAN: parse_vlan;
            default: accept;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_TCP:  parse_tcp;
            TYPE_UDP:  parse_udp;
            default: accept;
        }
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);
        ig_md.hdr_dstport = hdr.tcp.dst_port;
        ig_md.hdr_srcport = hdr.tcp.src_port;
        transition accept;
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        ig_md.hdr_dstport = hdr.udp.dst_port;
        ig_md.hdr_srcport = hdr.udp.src_port;
        transition accept;
    }
}

control SwitchIngress(
        inout header_t hdr,
        inout ig_metadata_t ig_md,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {  
    
    /************ ACTIONS ************/


    /* Registers for flow management */
    Register<bit<8>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_classified_flag;
    /* Check flag for classified flows */
    RegisterAction<bit<8>,bit<(INDEX_WIDTH)>,bit<8>>(reg_classified_flag)
    update_classified_flag = {
        void apply(inout bit<8> classified_flag, out bit<8> output) {
            if (hdr.recirc.isValid()){
                classified_flag =hdr.recirc.class_result;
            }
            output = classified_flag;
        }
    };


     Register<bit<32>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_flow_ID;
    /* Read and update flow ID */
    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<2>>(reg_flow_ID)
    update_flow_ID = {
        void apply(inout bit<32> flow_ID, out bit<2> output) {
            if(flow_ID == 0){
                flow_ID = ig_md.flow_ID;
                output  = 0;
            }else if(flow_ID != ig_md.flow_ID){
                output  = 1;
            }else{
                output  = 2;
            }
        }
    };

    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<2>>(reg_flow_ID)
    update_oldflow_ID = {
        void apply(inout bit<32> flow_ID, out bit<2> output) {
            if(flow_ID != ig_md.flow_ID){
                flow_ID =ig_md.flow_ID;
                output  = 0;
            }else{
                output = 3;
            }
        }
    };



    /* Only read flow ID */
    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<32>>(reg_flow_ID)
    read_only_flow_ID0 = {
        void apply(inout bit<32> flow_ID, out bit<32> output) {
            output = flow_ID;
        }
    };


    Register<bit<32>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_time_last_pkt;
    /* Read and update timestamp of last packet of a flow */
    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<32>>(reg_time_last_pkt)
    read_time_last_pkt = {
        void apply(inout bit<32> time_last_pkt, out bit<32> output) {
            output = time_last_pkt;
            time_last_pkt = ig_intr_prsr_md.global_tstamp[47:16];
        }
    };

    /*  Registers for ML inference - features */
    Register<bit<8>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_pkt_count;
    /* Read and update packet count */
    RegisterAction<bit<8>,bit<(INDEX_WIDTH)>,bit<8>>(reg_pkt_count)
    read_pkt_count = {
        void apply(inout bit<8> pkt_count, out bit<8> output) {
            pkt_count = pkt_count + 1;
            output = pkt_count;
        }
    };

    Register<bit<32>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_flow_duration;
    /* Read and update flow duration */
    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<32>>(reg_flow_duration)
    read_flow_duration = {
        void apply(inout bit<32> flow_duration, out bit<32> output) {
            if (ig_md.is_first != 1){
                flow_duration = flow_duration + ig_md.iat;
            }
            output = flow_duration;
        }
    };

    Register<bit<32>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_flow_iat_max;
    /* Read and update maximum packet interarrival time */
    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<32>>(reg_flow_iat_max)
    read_flow_iat_max = {
        void apply(inout bit<32> flow_iat_max, out bit<32> output) {
            if (ig_md.is_first != 1){
                if(ig_md.iat > flow_iat_max){
                    flow_iat_max = ig_md.iat;
                }
            }
            output = flow_iat_max;
        }
    };

    Register<bit<32>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_flow_iat_min;
    /* Read and update maximum packet interarrival time */
    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<32>>(reg_flow_iat_min)
    read_flow_iat_min = {
        void apply(inout bit<32> flow_iat_min, out bit<32> output) {
            if (ig_md.is_first != 1){
                if(ig_md.iat < flow_iat_min){
                    flow_iat_min = ig_md.iat;
                }
            }
            output = flow_iat_min;
        }
    };

    RegisterAction<bit<32>,bit<(INDEX_WIDTH)>,bit<32>>(reg_flow_iat_min)
    init_flow_iat_min = {
        void apply(inout bit<32> flow_iat_min) {
            if (ig_md.is_first == 1){
                    flow_iat_min = 0xFFFFFFFF;
                }
        }
    };


    Register<bit<16>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_pkt_len_max;
    /* Read and update maximum packet length */
    RegisterAction<bit<16>,bit<(INDEX_WIDTH)>,bit<16>>(reg_pkt_len_max)
    read_pkt_len_max = {
        void apply(inout bit<16> pkt_len_max, out bit<16> output) {
            if (ig_md.is_first == 1){
                pkt_len_max = hdr.ipv4.total_len;
            }
            else if (hdr.ipv4.total_len > pkt_len_max){
                pkt_len_max  = hdr.ipv4.total_len;
            }
            output = pkt_len_max;
        }
    };


    Register<bit<16>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_pkt_len_min;
    /* Read and update minimum packet length */
    RegisterAction<bit<16>,bit<(INDEX_WIDTH)>,bit<16>>(reg_pkt_len_min)
    read_pkt_len_min = {
        void apply(inout bit<16> pkt_len_min, out bit<16> output) {
            if (ig_md.is_first == 1){
                pkt_len_min = hdr.ipv4.total_len;
            }
            else if (hdr.ipv4.total_len < pkt_len_min){
                pkt_len_min  = hdr.ipv4.total_len;
            }
            output = pkt_len_min;
        }
    };


    Register<bit<16>,bit<(INDEX_WIDTH)>>(MAX_REGISTER_ENTRIES) reg_pkt_len_total;
    /* Read and update total packet length */
    RegisterAction<bit<16>,bit<(INDEX_WIDTH)>,bit<16>>(reg_pkt_len_total)
    read_pkt_len_total = {
        void apply(inout bit<16> pkt_len_total, out bit<16> output) {
            if (ig_md.is_first == 1){
                pkt_len_total = hdr.ipv4.total_len;
            }
            else{
                pkt_len_total = pkt_len_total + hdr.ipv4.total_len;
            }
            output = pkt_len_total;
        }
    };

    /* Declaration of the hashes*/
    //@symmetric("hdr.ipv4.src_addr","hdr.ipv4.dst_addr")
    //@symmetric("ig_md.hdr_srcport","ig_md.hdr_dstport")
    Hash<bit<32>>(HashAlgorithm_t.CRC32)              flow_id_calc;
    //@symmetric("hdr.ipv4.src_addr","hdr.ipv4.dst_addr")
    //@symmetric("ig_md.hdr_srcport","ig_md.hdr_dstport")
    Hash<bit<(INDEX_WIDTH)>>(HashAlgorithm_t.CRC16)   idx_calc;

    /* Calculate hash of the 5-tuple to represent the flow ID */
    action get_flow_ID(bit<16> srcPort, bit<16> dstPort) {
        ig_md.flow_ID = flow_id_calc.get({hdr.ipv4.src_addr,
            hdr.ipv4.dst_addr,srcPort, dstPort, hdr.ipv4.protocol});
    }
    /* Calculate hash of the 5-tuple to use as register index */
    action get_register_index(bit<16> srcPort, bit<16> dstPort) {
        ig_md.register_index = idx_calc.get({hdr.ipv4.src_addr,
            hdr.ipv4.dst_addr,srcPort, dstPort, hdr.ipv4.protocol});
    }

    /* Recirculate packet via loopback port 68 */
    action recirculate(bit<7> recirc_port) {
        ig_intr_tm_md.ucast_egress_port[8:7] = ig_intr_md.ingress_port[8:7];
        ig_intr_tm_md.ucast_egress_port[6:0] = recirc_port;
        hdr.recirc.setValid();
        hdr.recirc.class_result = ig_md.finres;
        hdr.recirc.etherType = ig_md.tmp_etherType;
        hdr.ethernet.etherType = TYPE_RECIRC;
        ig_intr_dprsr_md.digest_type = 1;
    }

    /* Compute packet interarrival time (IAT) */
    action get_iat_value(){
        ig_md.iat = ig_intr_prsr_md.global_tstamp[47:16] - ig_md.time_last_pkt;
    }

    /* Forward to a specific port number */
    action ipv4_forward(PortId_t port) {
        ig_intr_tm_md.ucast_egress_port = port;
    }

    /* Do Nothing Action */
    action nop(){}

    /* Asign final class after voting and recirculate packet */
    // action set_final_class(bit<8> class_result) {
    //     ig_md.final_class = class_result;
    //     recirculate(68);
    // }
 DirectCounter<bit<32>>(CounterType_t.PACKETS) direct_counter;
        /* Feature table actions - build codewords */
    action setClassifiedFlag(bit<4> flag){
        direct_counter.count();
        ig_md.classifiedFlowFlag=flag;
    }
    //@idletime_precision(3)
    table checkNewFlow_tb{
        key={
            hdr.ipv4.src_addr: exact;
            hdr.ipv4.dst_addr: exact;
            ig_md.hdr_srcport: exact;
            ig_md.hdr_dstport: exact;
            hdr.ipv4.protocol: exact;
            //ig_md.flow_ID: exact;
        }
        actions = {
            setClassifiedFlag;
        }
        //idle_timeout = true;
        counters = direct_counter;
        size=65536;
    }
    //#define tb_apply(name) name##_tb.apply();


    action SetCode0(bit<16> allEncode) {
        ig_md.feature0encode1=allEncode[3:0];
        ig_md.feature0encode2=allEncode[7:4];
        ig_md.feature0encode3=allEncode[11:8];
        ig_md.feature0encode4=allEncode[15:12];
    }
    action SetCode1(bit<16> allEncode) {
        ig_md.feature1encode1=allEncode[3:0];
        ig_md.feature1encode2=allEncode[7:4];
        ig_md.feature1encode3=allEncode[11:8];
        ig_md.feature1encode4=allEncode[15:12];
    }
    action SetCode2(bit<16> allEncode) {
        ig_md.feature2encode1=allEncode[3:0];
        ig_md.feature2encode2=allEncode[7:4];
        ig_md.feature2encode3=allEncode[11:8];
        ig_md.feature2encode4=allEncode[15:12];
    }
    action SetCode3(bit<16> allEncode) {
        ig_md.feature3encode1=allEncode[3:0];
        ig_md.feature3encode2=allEncode[7:4];
        ig_md.feature3encode3=allEncode[11:8];
        ig_md.feature3encode4=allEncode[15:12];
    }
    action SetCode4(bit<16> allEncode) {
        ig_md.feature4encode1=allEncode[3:0];
        ig_md.feature4encode2=allEncode[7:4];
        ig_md.feature4encode3=allEncode[11:8];
        ig_md.feature4encode4=allEncode[15:12];
    }
    action SetCode5(bit<16> allEncode) {
        ig_md.feature5encode1=allEncode[3:0];
        ig_md.feature5encode2=allEncode[7:4];
        ig_md.feature5encode3=allEncode[11:8];
        ig_md.feature5encode4=allEncode[15:12];
    }
    action SetCode6(bit<16> allEncode) {
        ig_md.feature6encode1=allEncode[3:0];
        ig_md.feature6encode2=allEncode[7:4];
        ig_md.feature6encode3=allEncode[11:8];
        ig_md.feature6encode4=allEncode[15:12];
    }

    action setTreeRes1(bit<8> res)
    {
        ig_md.resTree1=res;
    }
    action setTreeRes2(bit<8> res)
    {
        ig_md.resTree2=res;
    }
    action setTreeRes3(bit<8> res)
    {
        ig_md.resTree3=res;
    }
    action setTreeRes4(bit<8> res)
    {
        ig_md.resTree4=res;
    }
    action setTreeRes5(bit<8> res)
    {
        ig_md.resTree5=res;
    }
    action setTreeRes6(bit<8> res)
    {
        ig_md.resTree6=res;
    }
    action set_final_res()
    {
        // ig_md.final_class = class_result;
        recirculate(68);
    }


    action set_merge_res(bit<8> res){
        ig_md.finres=res;
        recirculate(68);
    }

    table table_feature0{
	    key = {ig_md.pkt_len_total: ternary @name("feature0");}
	    actions = {@defaultonly nop; SetCode0;}
	    size = 200;
        const default_action = nop();
	}
	table table_feature1{
        key = {ig_md.flow_duration[19:0]: ternary @name("feature1");}
	    actions = {@defaultonly nop; SetCode1;}
	    size = 200;
        const default_action = nop();
	}
	table table_feature2{
	    key = {ig_md.pkt_len_max: ternary @name("feature2");}
	    actions = {@defaultonly nop; SetCode2;}
	    size = 200;
        const default_action = nop();
	}
	table table_feature3{
	    key = {ig_md.hdr_dstport: ternary @name("feature3");}
	    actions = {@defaultonly nop; SetCode3;}
	    size = 200;
        const default_action = nop();
	}
	table table_feature4{
        key = {ig_md.pkt_len_min: ternary @name("feature4");}
	    actions = {@defaultonly nop; SetCode4;}
	    size = 200;
        const default_action = nop();
	}
	table table_feature5{
	    key = {ig_md.flow_iat_min[19:0]: ternary @name("feature5");}
	    actions = {@defaultonly nop; SetCode5;}
	    size = 256;
        const default_action = nop();
	}
	table table_feature6{
	    key = {ig_md.flow_iat_max[19:0]: ternary @name("feature6");}
	    actions = {@defaultonly nop; SetCode6;}
	    size = 200;
        const default_action = nop();
	}

    table merge_tb{
        key={
            ig_md.resTree1:exact;
            ig_md.resTree2:exact;
            ig_md.resTree3:exact;
            ig_md.resTree4:exact;
        }

        actions ={
            set_merge_res;
        }
        size = 125535;
    }


    table dt_1_tb{
        key={
            ig_md.feature0encode1: ternary;
            ig_md.feature1encode1 : ternary;
            ig_md.feature2encode1 : ternary;
            ig_md.feature3encode1 : ternary;
            ig_md.feature4encode1 : ternary;
            ig_md.feature5encode1 : ternary;
            ig_md.feature6encode1 : ternary;
        }
        actions = {
            setTreeRes1;
        }
        size=1024;
    }

    table dt_2_tb{
        key={
            ig_md.feature0encode2: ternary;
            ig_md.feature1encode2 : ternary;
            ig_md.feature2encode2 : ternary;
            ig_md.feature3encode2 : ternary;
            ig_md.feature4encode2 : ternary;
            ig_md.feature5encode2 : ternary;
            ig_md.feature6encode2 : ternary;
        }
        actions = {
            setTreeRes2;
        }
        size=2048;
    }

    table dt_3_tb{
        key={
            ig_md.feature0encode3: ternary;
            ig_md.feature1encode3 : ternary;
            ig_md.feature2encode3 : ternary;
            ig_md.feature3encode3 : ternary;
            ig_md.feature4encode3 : ternary;
            ig_md.feature5encode3 : ternary;
            ig_md.feature6encode3 : ternary;
        }
        actions = {
            setTreeRes3;
        }
        size=2048;
    }

    table dt_4_tb{
        key={
            ig_md.feature0encode4: ternary;
            ig_md.feature1encode4 : ternary;
            ig_md.feature2encode4 : ternary;
            ig_md.feature3encode4 : ternary;
            ig_md.feature4encode4 : ternary;
            ig_md.feature5encode4 : ternary;
            ig_md.feature6encode4 : ternary;
        }
        actions = {
            setTreeRes4;
        }
        size=4096;
    }

    action drop() {
        ig_intr_dprsr_md.drop_ctl = 1;
    }

    action forward(PortId_t port) {
        ig_intr_tm_md.ucast_egress_port = port;
    }

    table simple_forward {
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            drop;
            forward;
        }
        default_action = drop();
        const entries = {
            152 : forward(154);
            154 : forward(152);
        }
    }



        apply {
            //compute flow_ID and hash index
            get_flow_ID(ig_md.hdr_srcport, ig_md.hdr_dstport);
            get_register_index(ig_md.hdr_srcport, ig_md.hdr_dstport);

            // modify timestamp register
            
            ig_md.finres=0;
            ig_md.classified_flag = 0;
            ig_md.classifiedFlowFlag = 0;
            ig_md.tmp_etherType=hdr.ethernet.etherType;
            // calculate iat
            //if (hdr.tcp.isValid() || hdr.udp.isValid()){ 
                checkNewFlow_tb.apply();
                if(ig_md.classifiedFlowFlag == 0){
                    if(!hdr.recirc.isValid()){
                        ig_md.classified_flag = update_classified_flag.execute(ig_md.register_index);
                        if(ig_md.classified_flag == 0){
                            ig_md.state = update_flow_ID.execute(ig_md.register_index); // 0: new flow, 1:hash collision, 2: old flow 3: classified flow
                        }else{
                            ig_md.state = update_oldflow_ID.execute(ig_md.register_index);
                        }
                        if(ig_md.state == 0){
                            ig_md.is_first = 1;
                            ig_md.time_last_pkt = read_time_last_pkt.execute(ig_md.register_index);
                            //get_iat_value();
                            ig_md.pkt_count = read_pkt_count.execute(ig_md.register_index);
                            ig_md.pkt_len_max = read_pkt_len_max.execute(ig_md.register_index);
                            ig_md.pkt_len_min = read_pkt_len_min.execute(ig_md.register_index);
                            ig_md.pkt_len_total = read_pkt_len_total.execute(ig_md.register_index);
                            init_flow_iat_min.execute(ig_md.register_index);
                        }
                        else if(ig_md.state == 2){
                            ig_md.time_last_pkt = read_time_last_pkt.execute(ig_md.register_index);
                            get_iat_value();
                            ig_md.pkt_count = read_pkt_count.execute(ig_md.register_index);
                            //read and update feature registers - time-based features
                            ig_md.flow_iat_max = read_flow_iat_max.execute(ig_md.register_index);
                            ig_md.flow_iat_min = read_flow_iat_min.execute(ig_md.register_index);
                            ig_md.flow_duration = read_flow_duration.execute(ig_md.register_index);
                            //read and update feature registers - packet length-based features
                            ig_md.pkt_len_max = read_pkt_len_max.execute(ig_md.register_index);
                            ig_md.pkt_len_min = read_pkt_len_min.execute(ig_md.register_index);
                            ig_md.pkt_len_total = read_pkt_len_total.execute(ig_md.register_index);
                            
                            if(ig_md.pkt_count == 4){
                                table_feature0.apply();
                                table_feature1.apply();
                                table_feature2.apply();
                                table_feature3.apply();
                                table_feature4.apply();
                                table_feature5.apply();
                                table_feature6.apply();
                                // apply code tables to assign labels
                                dt_1_tb.apply();
                                dt_2_tb.apply();
                                dt_3_tb.apply();
                                dt_4_tb.apply();
                                // decide final class and recirculate
                                merge_tb.apply();
                                //set_final_res();
                            }
                        }                 
                    }else{
                        ig_md.classified_flag = update_classified_flag.execute(ig_md.register_index);
                        hdr.ethernet.etherType = hdr.recirc.etherType;
                        hdr.recirc.setInvalid();
                    }
                }
                if(ig_intr_dprsr_md.digest_type != 1){
                    simple_forward.apply();
                }

            //}
        }
}

control SwitchIngressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in ig_metadata_t ig_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {
         
    // Checksum is not computed yet.
    Digest<digest_a_t>() digest_a;
    apply {      
        if(ig_intr_dprsr_md.digest_type == 1){
            //digest_a.pack({ig_md.flow_ID,ig_md.finres});
             digest_a.pack({hdr.ipv4.src_addr, hdr.ipv4.dst_addr, ig_md.hdr_srcport, ig_md.hdr_dstport, hdr.ipv4.protocol,ig_md.finres,ig_md.flow_iat_max,ig_md.flow_iat_min,ig_md.flow_duration,ig_md.pkt_len_max,ig_md.pkt_len_min,ig_md.pkt_len_total});
        }
        pkt.emit(hdr.ethernet);
        pkt.emit(hdr.recirc);
        pkt.emit(hdr.vlan_tag);
        pkt.emit(hdr.ipv4);
        pkt.emit(hdr.tcp);
        pkt.emit(hdr.udp);
    }
}

parser SwitchEgressParser(
        packet_in pkt,
        out header_t hdr,
        out eg_metadata_t eg_md,
        out egress_intrinsic_metadata_t eg_intr_md) {
    state start {
        pkt.extract(eg_intr_md);
        transition parse_ethernet;
    }

     state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4:  parse_ipv4;
            ETHERTYPE_VLAN: parse_vlan;
            default: parse_timestamp;
        }
    }

    state parse_vlan{
        pkt.extract(hdr.vlan_tag);
        transition select(hdr.vlan_tag.ether_type) {
            ETHERTYPE_IPV4: parse_ipv4;
            default: parse_timestamp;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_TCP:  parse_tcp;
            TYPE_UDP:  parse_udp;
            default: parse_timestamp;
        }
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);
        transition parse_timestamp;
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition parse_timestamp;
    }

    state parse_timestamp{
        transition accept;
    }
}


control SwitchEgress(
        inout header_t hdr,
        inout eg_metadata_t eg_md,
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_intr_md_from_prsr,
        inout egress_intrinsic_metadata_for_deparser_t eg_intr_dprs_md,
        inout egress_intrinsic_metadata_for_output_port_t eg_intr_oport_md) {
    apply {
    }
}

control SwitchEgressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in eg_metadata_t eg_md,
        in egress_intrinsic_metadata_for_deparser_t eg_intr_md_for_dprsr) {
    apply {
        pkt.emit(hdr.ethernet);
        pkt.emit(hdr.vlan_tag);
        pkt.emit(hdr.ipv4);
        pkt.emit(hdr.tcp);
        pkt.emit(hdr.udp);
    }
}

Pipeline(SwitchIngressParser(),
         SwitchIngress(),
         SwitchIngressDeparser(),
         SwitchEgressParser(),
         SwitchEgress(),
         SwitchEgressDeparser()
         ) pipe;

Switch(pipe) main;