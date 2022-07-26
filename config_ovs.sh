#!/bin/bash
INTFS=$(ip address | grep 192.168.1)
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
