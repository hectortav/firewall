#!/bin/bash

MININET_DIR=${PWD}
cd $MININET_DIR
sudo mn --topo topo --controller=remote --switch ovs,protocols=OpenFlow13,stp=1 --custom topology.py
