#!/bin/bash

MININET_DIR=${PWD}
cd $MININET_DIR
sudo mn --topo topo --controller=remote --custom topology.py
