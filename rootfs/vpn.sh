#!/bin/ash
# generate tunnel interface
openvpn --mktun --dev tun1
ifconfig tun1 up
# start vpn
source /vpn/config/config.vpnid
openconnect -s /etc/vpnc/vpnc-script $server $options --user=$user --interface=tun1 --passwd-on-stdin < /vpn/config/pass.vpnid.txt
kill 1
