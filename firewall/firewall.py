#!/usr/bin/python2
from pox.core import core
from pox.openflow.libopenflow_01 import ofp_flow_mod, ofp_match
from pox.lib.revent import *
import pox.lib.packet as pkt
from pox.lib.addresses import IPAddr
import csv

log = core.getLogger()

class Firewall (EventMixin):
    def __init__ (self):
        print("Start Firewall")
        self.listenTo(core.openflow)
        self.firewall = {}

    def _handle_ConnectionUp (self, event):
        self.connection = event.connection
        try:
            ifile  = open("pox/misc/firewall_rules.csv", "rb")
        except Exception as e:
            log.info(e)
            return
        
        reader = csv.reader(ifile)
        for row in reader:
            print("source: " + str(row[1]))
            print("destination: " + str(row[2]))
            print("~~~~~~~~~~~~~~~~")
            self.firewall[(row[1], row[2])]=True
            msg = ofp_flow_mod()
            match = ofp_match(dl_type = 0x800, nw_proto = pkt.ipv4.ICMP_PROTOCOL)
            match.nw_src = IPAddr(row[1])
            match.nw_dst = IPAddr(row[2])
            msg.match = match
            msg.priority= 10
            event.connection.send(msg)

        ifile.close()
        
def launch ():
    core.registerNew(Firewall)
