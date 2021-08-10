#!/bin/bash
source /vpn/config/config.vpnid

start(){
    #start programs in order
    supervisorctl start vpn
    $nat && supervisorctl start nat
    (( $ssh )) && supervisorctl start sshd
    (( $proxy )) && supervisorctl start squid
    (( $dns  )) && supervisorctl start unbound
    /onboot.sh
}

end() {
    /ondown.sh
    trap - HUP INT QUIT TERM
    kill -- -$$ # Sends SIGTERM to child/sub processes
}

trap end HUP INT QUIT TERM

echo "starting entrypoint"
start

echo "waiting for kill signal"
read
