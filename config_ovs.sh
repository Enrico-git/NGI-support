#!/bin/bash

#It's supposed that the address for the hosts and switches goes from .0.1 to .6.255
#So I'm skipping from .7.0 to .7.255 which are the link to controller.
INTFS=$(ip address | grep 192.168.[0-6])

SW=$(ls -A /sys/class/net | grep s[0-9] )
NUM_INTFS=$(ls -A /sys/class/net | wc -l)

for ((i=0; i < $NUM_INTFS; i++)); do
    INTF='eth'$i
    if [[ $INTFS =~ $INTF ]]
    then
        sudo ifconfig $INTF 0
        sudo ovs-vsctl add-port $SW $INTF
    fi
done
