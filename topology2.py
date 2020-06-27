#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.cli  import CLI

'''
net = Mininet(link=TCLink);

# Add hosts and switches


# Add links


# Start
net.addController('c0', controller=RemoteController)
net.build()
net.start()

# CLI
CLI( net )

# Clean up
net.stop()
'''

class DuoSwitchTopo(Topo):

    def __init__(self, **opts):

        Topo.__init__(self, **opts)

        h1  = self.addHost('h1', ip='10.0.0.1')
        h2  = self.addHost('h2', ip='10.0.0.2')
        # h3  = self.addHost('h3', ip='10.0.0.3')
        # h4  = self.addHost('h4', ip='10.0.0.4')

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s7 = self.addSwitch('s7')

        self.addLink(h1, s1)
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s2, s5)
        self.addLink(s3, s6)
        self.addLink(s3, s7)
        self.addLink(s7, s5)
        self.addLink(s7, h2)

def simpleTest():
    topo = DuoSwitchTopo()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    # net.pingAll()
    net.ping([net.hosts[0], net.hosts[1]])
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simpleTest()

topos = { 'topo': DuoSwitchTopo }