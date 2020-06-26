#!/bin/bash

MININET_DIR=${PWD}
cd $MININET_DIR
sudo mn --topo topo2 --controller=remote --custom topology.py
