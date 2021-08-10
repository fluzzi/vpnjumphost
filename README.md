#
vpnjumphost
```
clone this git, create the config.yaml file from config.yaml.example with your vpns information
enable the services required for each vpn in config.yaml: SSH proxy, DNS server, NAT and/or Squid Proxy
install docker and docker-compose
create an sshkey for connecting to the docker jumphost
run ./setup.py 
**passwords are stored as plain text, use it at your own risk**
finally use vpn and vpn down commands to build and remove the containers

to use the container as SSH jumphost just do:
ssh -J root@127.0.0.1:*port asigned to this vpn* x.x.x.x

```
