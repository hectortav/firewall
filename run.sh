#!/bin/bash
MININET_DIR=${PWD}
POX_DIR=${PWD}/../../../pox/

rm -rf $POX_DIR/pox/misc/firewall.py
cp -r ./firewall/firewall.py $POX_DIR/pox/misc
cd $POX_DIR
#python2 pox.py pox.misc.firewall
# ./pox.py forwarding.l2_learning openflow.discovery openflow.spanning_tree --no-flood --hold-down pox.misc.firewall
./pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning pox.misc.firewall