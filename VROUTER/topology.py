#!/usr/bin/python
#sudo mn --custom tutorialTOPO.py --topo sdnip --mac --controller=remote,127.0.0.1,6653

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info, debug
from mininet.node import Host, RemoteController, OVSBridge
from mininet.nodelib import NAT
from ipaddress import ip_network

QUAGGA_DIR = '/quagga'
# Must exist and be owned by quagga user (quagga:quagga by default on Ubuntu)
QUAGGA_RUN_DIR = '/var/run/quagga'
CONFIG_DIR = 'configs'

class VRHost(Host):
    def __init__(self, name, ip, route, *args, **kwargs):
        Host.__init__(self, name, ip=ip, *args, **kwargs)

        self.route = route

    def config(self, **kwargs):
        Host.config(self, **kwargs)

        debug("configuring route %s" % self.route)

        self.cmd('ip route add default via %s' % self.route)

class Router(Host):
    def __init__(self, name, quaggaConfFile, zebraConfFile, intfDict, *args, **kwargs):
        Host.__init__(self, name, *args, **kwargs)

        self.quaggaConfFile = quaggaConfFile
        self.zebraConfFile = zebraConfFile
        self.intfDict = intfDict

    def config(self, **kwargs):
        Host.config(self, **kwargs)
        self.cmd('sysctl net.ipv4.ip_forward=1')

        for intf, attrs in self.intfDict.items():
            self.cmd('ip addr flush dev %s' % intf)
            if 'mac' in attrs:
                self.cmd('ip link set %s down' % intf)
                self.cmd('ip link set %s address %s' % (intf, attrs['mac']))
                self.cmd('ip link set %s up ' % intf)
            for addr in attrs['ipAddrs']:
                self.cmd('ip addr add %s dev %s' % (addr, intf))

        self.cmd('/quagga/zebra/zebra -d -f %s -z %s/zebra%s.api -i %s/zebra%s.pid' % (self.zebraConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        print('\n%s /quagga/zebra/zebra -d -f %s -z %s/zebra%s.api -i %s/zebra%s.pid' % (self.name,self.zebraConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        
        if self.name == "r1" or self.name == "r2" or self.name == "ospfbgp" :
            self.cmd('/quagga/ospfd/ospfd -d -f %s -z %s/zebra%s.api -i %s/ospfd%s.pid' % (self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
            print('%s /quagga/ospfd/ospfd -d -f %s -z %s/zebra%s.api -i %s/ospfd%s.pid' % (self.name,self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
        else:
            self.cmd('/quagga/bgpd/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
            print('%s /quagga/bgpd/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (self.name,self.quaggaConfFile, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))


        if self.name == "ospfbgp":
            quaggaBgp = "%s/quagga-sdn-bgp.conf" % CONFIG_DIR
            self.cmd('/quagga/bgpd/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (quaggaBgp, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))
            print('%s /quagga/bgpd/bgpd -d -f %s -z %s/zebra%s.api -i %s/bgpd%s.pid' % (self.name,quaggaBgp, QUAGGA_RUN_DIR, self.name, QUAGGA_RUN_DIR, self.name))


    def terminate(self):
        self.cmd("ps ax | egrep 'ospfd%s.pid|bgpd%s.pid'|zebra%s.pid'|zebra2%s.pid' | awk '{print $1}' | xargs kill" % (self.name, self.name))

        Host.terminate(self)


class VRTopo( Topo ):
    "SDN-IP tutorial topology"
    
    def build( self ):
        s1 = self.addSwitch('s1', dpid='00000000000000a1')

        zebraConf = '%s/zebra.conf' % CONFIG_DIR
        fpmzebraConf = '%s/zebra-fpm.conf' % CONFIG_DIR

        # Switches we want to attach our routers to, in the correct order
        attachmentSwitches = [s1 ]

        for i in range(1, 4+1):
            name = 'r%s' % i

            eth0 = { 'mac' : '00:00:00:00:0%s:01' % i,
                     'ipAddrs' : ['10.0.%s.1/24' % i] }
            eth1 = { 'ipAddrs' : ['192.168.%s.254/24' % i] }
            intfs = { '%s-eth0' % name : eth0,
                      '%s-eth1' % name : eth1 }

            quaggaConf = '%s/quagga%s.conf' % (CONFIG_DIR, i)

            router = self.addHost(name, cls=Router, quaggaConfFile=quaggaConf,
                                  zebraConfFile=zebraConf, intfDict=intfs)
            
            host = self.addHost('h%s' % i, cls=VRHost, 
                                ip='192.168.%s.1/24' % i,
                                route='192.168.%s.254' % i)
            
            self.addLink(router, attachmentSwitches[0])
            self.addLink(router, host)

        # Set up the internal OSPF speaker
        ospfbgpEth0 = { 'mac':'00:00:00:00:00:01', 
                     'ipAddrs' : ['10.0.1.101/24','10.0.2.101/24','10.0.3.101/24','10.0.4.101/24',] }
        ospfbgpEth1 = { 'ipAddrs' : ['172.16.0.2/24'] }
        ospfbgpIntfs = { 'ospfbgp-eth0' : ospfbgpEth0,
                     'ospfbgp-eth1' : ospfbgpEth1 }
        
        ospfbgp = self.addHost( "ospfbgp", cls=Router, 
                             quaggaConfFile = '%s/quagga-sdn-ospf.conf' % CONFIG_DIR, 
                             zebraConfFile = fpmzebraConf, 
                             intfDict=ospfbgpIntfs )
        
        self.addLink( ospfbgp, s1 )
        
        # Control plane switch (for quagga fpm)
        cs0 = self.addSwitch('cs0', cls=OVSBridge)

        # Control plane NAT (for quagga fpm)
        nat = self.addHost('nat', cls=NAT,
                           ip='172.16.0.1/24',
                           subnet=str(ip_network(u'172.16.0.0/24')), inNamespace=False)
        self.addLink(cs0, nat)
        self.addLink(cs0, ospfbgp)

topos = { 'vr_topo' : VRTopo }

if __name__ == '__main__':
    setLogLevel('debug')
    topo = VRTopo()
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()
    CLI(net)
    net.stop()
    info("done\n")
