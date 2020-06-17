#!/bin/bash
MININET_DIR=${PWD}
POX_DIR=${PWD}/../../pox/

cp -r ./firewall/firewall.py $POX_DIR/pox/misc
cd $POX_DIR
python2 pox.py pox.misc.firewall
# rm -rf pox/misc/firewall.py