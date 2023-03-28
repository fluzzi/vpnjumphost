#!/bin/sh
while inotifywait /etc/resolv.conf -e modify; do { sleep 10s && supervisorctl restart dnsmasq;   }; done
