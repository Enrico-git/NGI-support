#!/bin/bash

# It's supposed that the address for the hosts 
# and switches goes from .0.1 to .6.255
INTFS=$(ip address | grep 192.168.[0-6])

IP_CTRL=${1}
#SW=$(ls -A /sys/class/net | grep s[0-9] )
SW=${2}
NUM_INTFS=$(ls -A /sys/class/net | wc -l)

#Creating OVS switch
sudo ovs-vsctl add-br $SW

# Disabling interfaces from node and Mapping the 
# interfaces from node to OVS
for ((i=0; i < $NUM_INTFS; i++)); do
    INTF='eth'$i
    if [[ $INTFS =~ $INTF ]]
    then
        sudo ifconfig $INTF 0
        sudo ovs-vsctl add-port $SW $INTF
    fi
done

#setting the IP of the controller
sudo ovs-vsctl set-controller $SW tcp:$IP_CTRL:6633
sudo ovs-vsctl set-fail-mode $SW secure
