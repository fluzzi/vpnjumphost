#!/bin/sh

set -e

DNSMASQ=$(/usr/bin/which dnsmasq)

run() {
	echo "Starting dnsmasq..."
	exec "$DNSMASQ" -k
}

run
