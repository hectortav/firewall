#!/usr/bin/python                                                                                                                                              
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


class MultiSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def __init__(self, n=8, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        #switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        #for h in range(n):
         #   host = self.addHost('h%s' % (h + 1), ip='10.0.0.%s' % (h+1))
            #self.addLink(host, switch)
        h1 = self.addHost( 'h1', ip='10.0.0.1' )
        h2 = self.addHost( 'h2', ip='10.0.0.2' )
        h3 = self.addHost( 'h3', ip='10.0.0.3' )
        h4 = self.addHost( 'h4', ip='10.0.0.4' )
        h5 = self.addHost( 'h5', ip='10.0.0.5' )
        h6 = self.addHost( 'h6', ip='10.0.0.6' )
        h7 = self.addHost( 'h7', ip='10.0.0.7' )
        h8 = self.addHost( 'h8', ip='10.0.0.8' )

        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        s5 = self.addSwitch( 's5' )
        s6 = self.addSwitch( 's6' )
        s7 = self.addSwitch( 's7' )

        self.addLink( h1, s3 )
        self.addLink( h2, s3 )
        self.addLink( h3, s4 )
        self.addLink( h4, s4 )
        self.addLink( h5, s6 )
        self.addLink( h6, s6 )
        self.addLink( h7, s7 )
        self.addLink( h8, s7 )
        
        
        root = s1
        layer1 = [s2,s5]
        layer2 = [s3,s4,s6,s7]

        for idx,l1 in enumerate(layer1):
            self.addLink( root,l1 )
            self.addLink( l1, layer2[2*idx] )
            self.addLink( l1, layer2[2*idx + 1] )

def simpleTest():
    "Create and test a simple network"
    topo = SingleSwitchTopo(5)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()


topos = { 'topo': MultiSwitchTopo }

