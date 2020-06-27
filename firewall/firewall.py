#!/usr/bin/python2
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
import pox.lib.packet as pkt
from pox.lib.addresses import EthAddr, IPAddr
import csv

log = core.getLogger()
rulesFile = "pox/misc/firewall_rules.csv"


class Firewall (EventMixin):
    def __init__ (self):
        log.info("Start Firewall")
        self.listenTo(core.openflow)
        self.firewall = {}

    def sendRule (self, src, dst, duration = 0):
        if not isinstance(duration, tuple):
            duration = (duration,duration)
        
        msg = of.ofp_flow_mod()

        match = of.ofp_match(dl_type = 0x800, nw_proto = pkt.ipv4.ICMP_PROTOCOL)
        match.nw_src = IPAddr(src)
        match.nw_dst = IPAddr(dst)
        
        msg.match = match

        self.connection.send(msg)

    def addRule (self, src=0, dst=0, value=True):
        log.info("Adding rule: source %s - destination %s", src, dst)
        self.firewall[(src, dst)]=value
        self.sendRule(src, dst, 10000)
        
    def _handle_ConnectionUp (self, event):

        self.connection = event.connection
        
        try:
            ifile  = open(rulesFile, "rb")
        except Exception as e:
            log.info(e)
            return
        
        reader = csv.reader(ifile)
        rowIndex = 0
        for row in reader:
            #All rows but header row
            if rowIndex != 0:
                self.addRule(row[1], row[2])
            rowIndex += 1

        ifile.close()
        
def launch ():
    core.registerNew(Firewall)
