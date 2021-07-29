#!/bin/sh

set -e

CHOWN=$(/usr/bin/which chown)
SQUID=$(/usr/bin/which squid)

prepare_folders() {
	echo "Preparing folders..."
	mkdir -p /var/cache/squid/
	mkdir -p /var/log/squid/
	"$CHOWN" -R squid:squid /var/cache/squid/
	"$CHOWN" -R squid:squid /var/log/squid/
}

initialize_cache() {
	echo "Creating cache folder..."
	"$SQUID" -z

	sleep 5
}

run() {
	echo "Starting squid..."
	prepare_folders
	initialize_cache
	exec "$SQUID" -NYCd 1 -f /etc/squid/squid.conf
}

run
