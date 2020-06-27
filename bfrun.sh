#!/bin/bash
MININET_DIR=${PWD}
POX_DIR=${PWD}/../../../pox

rm -rf $POX_DIR/ext/bellmanFord.py
cp -r ./bellmanFord/bellmanFord.py $POX_DIR/ext
cd $POX_DIR
./pox.py openflow.of_01 forwarding.l2_learning bellmanFord openflow.discovery