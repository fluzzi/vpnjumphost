#!/usr/bin/python3
import subprocess
import json
import fileinput
import shutil
from shutil import copyfile
import os

workdir = os.path.dirname(os.path.realpath(__file__))
js = open('servers.json')
servers = json.loads(js.read())
keys = list(servers.keys())
allfiles = ["supervisord.conf","rootfs/vpn.sh"]
homekey = os.path.expanduser("~") + "/.ssh/id_rsa.pub"

if not os.path.exists('compose'):
    os.makedirs('compose')
if not os.path.exists('config'):
    os.makedirs('config')
if not os.path.exists('log'):
    os.makedirs('log')

if not os.path.exists(homekey):
    print("Please run ssh-keygen to generate a ssh key")
    exit()
else:
    copyfile(homekey,"authorized_keys")

def make_files(vpnid):
    vpnname = "compose/vpn." + vpnid + ".yml"
    copyfile("vpn.yml", vpnname)
    workfiles = allfiles.copy()
    workfiles.append(vpnname)
    for f in workfiles:
        with fileinput.FileInput(f, inplace=True) as file:
            for line in file:
                newline = line.replace("vpnid",vpnid)
                newline = newline.replace("dockerdir",workdir)
                print(newline.replace("vpnport",str(servers[vpnid]["port"])), end='')


def return_files(vpnid):
    for f in allfiles:
        with fileinput.FileInput(f, inplace=True) as file:
            for line in file:
                newline = line.replace(vpnid,"vpnid")
                print(newline.replace(str(servers[vpnid]["port"]),"vpnport"), end='')

for i in keys:
   print("making files for " + i) 
   make_files(i) 
   build = "sudo docker build -t gederico/vpn.{}:v1.0.0 .".format(i)
   start = subprocess.call(build,shell=True)
   print("restoring files") 
   return_files(i)
os.remove("authorized_keys")
