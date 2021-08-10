#!/bin/ash
#nat traffic through container
iptables -t nat -A POSTROUTING -o tun1 -j MASQUERADE
