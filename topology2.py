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

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')

        self.addLink(h1, s1)
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s3, s4)
        self.addLink(s2, s5)
        self.addLink(s4, s5)
        self.addLink(s4, h2)

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