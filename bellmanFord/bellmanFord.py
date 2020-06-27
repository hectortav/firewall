from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.recoco import Timer
from collections import defaultdict
from pox.openflow.discovery import Discovery
from pox.lib.util import dpid_to_str
import pox.lib.packet as pkt
from pox.lib.addresses import EthAddr
import time

_src = "00-00-00-00-00-01"
_dst = "00-00-00-00-00-07"

log = core.getLogger()
adjacency = defaultdict(lambda: defaultdict(lambda: None))
switches = {}
mac_map = {}
waiting_paths = {}

def _get_raw_path(src, dst):
    distance = {}
    previous = {}
    for i in switches.values():
        distance[i] = 9999
        previous[i] = None
    distance[src] = 0
    for m in range(len(switches.values()) - 1):
        for p in switches.values():
            for q in switches.values():
                if adjacency[p][q] != None:
                    if distance[p] + 1 < distance[q]:
                        distance[q] = distance[p] + 1
                        previous[q] = p
    r = []
    p = dst
    r.append(p)
    q = previous[p]
    while q is not None:
        if q == src:
            r.append(q)
            break
        p = q
        r.append(p)
        q = previous[p]
    r.reverse()
    return r


def _get_path(src, dst, first_port, final_port):
    if src == dst:
        path = [src]
    else:
        path = _get_raw_path(src, dst)
        if path is None:
            return None
        if str(src) == _src and str(dst) == _dst:
            print("~~~~~~~~~~~~~~~~~~~~~")
            print("[" + _src[-2:] + " - " + _dst[-2:] + "]")
            print("Path:")
            print(path)
            print("~~~~~~~~~~~~~~~~~~~~~")

    r = []
    in_port = first_port
    for s1, s2 in zip(path[:-1], path[1:]):
        out_port = adjacency[s1][s2]
        r.append((s1, in_port, out_port))
        in_port = adjacency[s2][s1]
    r.append((dst, in_port, final_port))
    return r

class PathInstalled(Event):
    def __init__(self, path):
        Event.__init__(self)
        self.path = path


class Switch(EventMixin):
    def __init__(self):
        self.connection = None
        self.ports = None
        self.dpid = None
        self._listeners = None
        self._connected_at = None

    def __repr__(self):
        return dpid_to_str(self.dpid)

    def _install(self, switch, in_port, out_port, match, buf=None):
        msg = of.ofp_flow_mod()
        msg.match = match
        msg.match.in_port = in_port
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port=out_port))
        msg.buffer_id = buf
        switch.connection.send(msg)

    def _install_path(self, p, match, packet_in=None):
        for sw, in_port, out_port in p:
            self._install(sw, in_port, out_port, match)
            msg = of.ofp_barrier_request()
            sw.connection.send(msg)

    def install_path(self, dst_sw, last_port, match, event):
        p = _get_path(self, dst_sw, event.port, last_port)
        if p is None:
            if (match.dl_type == pkt.ethernet.IP_TYPE and event.parsed.find('ipv4')):
                e = pkt.ethernet()
                e.src = EthAddr(dpid_to_str(self.dpid))
                e.dst = match.dl_src
                e.type = e.IP_TYPE
                ipp = pkt.ipv4()
                ipp.protocol = ipp.ICMP_PROTOCOL
                ipp.srcip = match.nw_dst
                ipp.dstip = match.nw_src
                icmp = pkt.icmp()
                icmp.type = pkt.ICMP.TYPE_DEST_UNREACH
                icmp.code = pkt.ICMP.CODE_UNREACH_HOST
                orig_ip = event.parsed.find('ipv4')
                d = orig_ip.pack()
                d = d[:orig_ip.hl * 4 + 8]
                import struct
                d = struct.pack("!HH", 0, 0) + d
                icmp.payload = d
                ipp.payload = icmp
                e.payload = ipp
                msg = of.ofp_packet_out()
                msg.actions.append(of.ofp_action_output(port=event.port))
                msg.data = e.pack()
                self.connection.send(msg)
            return
        self._install_path(p, match, event.ofp)
        p = [(sw, out_port, in_port) for sw, in_port, out_port in p]
        self._install_path(p, match.flip())

    def _handle_PacketIn(self, event):
        packet = event.parsed
        loc = (self, event.port)
        oldloc = mac_map.get(packet.src)
        if packet.effective_ethertype == packet.LLDP_TYPE:
            return
        if oldloc is None:
            if packet.src.is_multicast == False:
                mac_map[packet.src] = loc
        elif oldloc != loc:
            if core.openflow_discovery.is_edge_port(loc[0].dpid, loc[1]):
                if packet.src.is_multicast == False:
                    mac_map[packet.src] = loc
        if not packet.dst.is_multicast and packet.dst in mac_map:
            dest = mac_map[packet.dst]
            match = of.ofp_match.from_packet(packet)
            self.install_path(dest[0], dest[1], match, event)

    def disconnect(self):
        if self.connection is not None:
            self.connection.removeListeners(self._listeners)
            self.connection = None
            self._listeners = None

    def connect(self, connection):
        if self.dpid is None:
            self.dpid = connection.dpid
        assert self.dpid == connection.dpid
        if self.ports is None:
            self.ports = connection.features.ports
        self.disconnect()
        self.connection = connection
        self._listeners = self.listenTo(connection)
        self._connected_at = time.time()

    def _handle_ConnectionDown(self, event):
        self.disconnect()


class l2_multi(EventMixin):

    def __init__(self):
        def startup():
            core.openflow.addListeners(self, priority=0)
            core.openflow_discovery.addListeners(self)

        core.call_when_ready(startup, ('openflow', 'openflow_discovery'))
    
    def _handle_LinkEvent(self, event):
        def flip(link):
            return Discovery.Link(link[2], link[3], link[0], link[1])

        l = event.link
        sw1 = switches[l.dpid1]
        sw2 = switches[l.dpid2]
        clear = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        for sw in switches.itervalues():
            if sw.connection is None: continue
            sw.connection.send(clear)
        if event.removed:
            if sw2 in adjacency[sw1]: del adjacency[sw1][sw2]
            if sw1 in adjacency[sw2]: del adjacency[sw2][sw1]
            for ll in core.openflow_discovery.adjacency:
                if ll.dpid1 == l.dpid1 and ll.dpid2 == l.dpid2:
                    if flip(ll) in core.openflow_discovery.adjacency:
                        adjacency[sw1][sw2] = ll.port1
                        adjacency[sw2][sw1] = ll.port2
                        break
        else:
            if adjacency[sw1][sw2] is None:
                if flip(l) in core.openflow_discovery.adjacency:
                    adjacency[sw1][sw2] = l.port1
                    adjacency[sw2][sw1] = l.port2
            bad_macs = set()
            for mac, (sw, port) in mac_map.iteritems():
                if (sw is sw1 and port == l.port1) or (sw is sw2
                                                       and port == l.port2):
                    bad_macs.add(mac)

    def _handle_ConnectionUp(self, event):
        sw = switches.get(event.dpid)
        if sw is None:
            sw = Switch()
            switches[event.dpid] = sw
        sw.connect(event.connection)

def launch():
    core.registerNew(l2_multi)
