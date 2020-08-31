#!/bin/bash

set -e
quagga_dir=/var/run/quagga/
mn_script=./topology.py
fpm_config=./configs/zebra-fpm.conf

# ip_addr is the ONOS instant's IP
if [ -z "$1" ]; then
    echo "Usage: $0 ip_addr(ONOS)"
    exit -1
fi

# clear quagga files everytime
if [ -d "$quagga_dir" ]; then
    set +e
    rm /var/run/quagga/*
    set -e

    # modify zebra-fpm.conf
    if [ -f "$fpm_config" ]; then
        sed -i -E "s/ip [0-9]+.[0-9]+.[0-9]+.[0-9]+/ip $1/g" $fpm_config
    fi

    # start mininet
    if [ -x "$mn_script" ]; then
        mn --custom=topology.py --topo=vr_topo --mac --controller=remote,ip=$1,port=6653
    else
        echo "'$mn_script' doesn't exist."
        exit -1
    fi
else
    echo "'$quagga_dir' doesn't exist."
    exit -1
fi
