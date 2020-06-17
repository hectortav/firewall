#!/bin/bash

MININET_DIR=${PWD}
cd $MININET_DIR
sudo mn --topo mytopo --mac --controller=remote,ip=localhost --switch ovs,protocols=OpenFlow13,stp=1 --custom topology.py