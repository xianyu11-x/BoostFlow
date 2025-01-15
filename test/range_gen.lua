package.path = package.path ..";?.lua;test/?.lua;app/?.lua;"

require "Pktgen"

local function set_range_data(src_ip_prefix)
    pktgen.src_ip("all", "start", src_ip_prefix+".0.1");
    pktgen.src_ip("all", "inc", "0.0.0.3");
    pktgen.src_ip("all", "min", src_ip_prefix+".0.1");
    pktgen.src_ip("all", "max", src_ip_prefix+".0.64");
end

pktgen.page("range");
pktgen.dst_mac("all", "start", "0011:2233:4455");
pktgen.src_mac("all", "start", "0033:2233:4455");

-- pktgen.delay(1000);
pktgen.dst_ip("all", "start", "10.12.0.1");
pktgen.dst_ip("all", "inc", "0.0.0.0");
pktgen.dst_ip("all", "min", "10.12.0.1");
pktgen.dst_ip("all", "max", "10.12.0.64");

-- pktgen.delay(1000);
pktgen.src_ip("all", "start", "10.17.0.1");
pktgen.src_ip("all", "inc", "0.0.0.1");
pktgen.src_ip("all", "min", "10.17.0.1");
pktgen.src_ip("all", "max", "10.17.0.255");

-- pktgen.delay(1000);
pktgen.dst_port("all", "start", 1234);
pktgen.dst_port("all", "inc", 0);
pktgen.dst_port("all", "min", 1234);
pktgen.dst_port("all", "max", 2345);

-- pktgen.delay(1000);
pktgen.src_port("all", "start", 5678);
pktgen.src_port("all", "inc", 0);
pktgen.src_port("all", "min", 1234);
pktgen.src_port("all", "max", 9999);

-- pktgen.delay(1000);
pktgen.pkt_size("all", "start", 1280);
pktgen.pkt_size("all", "inc", 0);
pktgen.pkt_size("all", "min", 64);
pktgen.pkt_size("all", "max", 1518);

pktgen.set_range("all", "on");

pktgen.start("all")

-- pktgen.delay(5000);
-- pktgen.stop("all")


-- pktgen.src_ip("all", "start", "10.16.0.1");
-- pktgen.src_ip("all", "inc", "0.0.0.1");
-- pktgen.src_ip("all", "min", "10.16.0.1");
-- pktgen.src_ip("all", "max", "10.16.0.64");

-- pktgen.set_range("all", "on");
-- pktgen.start("all")

-- pktgen.delay(5000);
-- pktgen.stop("all")