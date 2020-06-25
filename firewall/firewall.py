#!/usr/bin/python2
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
import pox.lib.packet as pkt
from pox.lib.addresses import EthAddr, IPAddr

log = core.getLogger()
rules = [['10.0.0.1','10.0.0.2'],['10.0.0.2', '10.0.0.4']]

class Firewall (EventMixin):
    def __init__ (self):
        log.info("Start Firewall")
        self.listenTo(core.openflow)
        
    def _handle_ConnectionUp (self, event):
        for rule in rules:
            log.info("rule")
            msg = of.ofp_flow_mod()
            match = of.ofp_match(dl_type = 0x800, nw_proto = pkt.ipv4.ICMP_PROTOCOL)
            match.nw_src = IPAddr(rule[0])
            match.nw_dst = IPAddr(rule[1])
            msg.match = match
            msg.idle_timeout = 10000
            msg.hard_timeout = 10000
            msg.priority = 10
            event.connection.send(msg)   
        
def launch ():
    core.registerNew(Firewall)
