#!/bin/sh

set -e

UNBOUND=$(/usr/bin/which unbound)

run() {
	echo "Starting unbound..."
	exec "$UNBOUND"
}

run
