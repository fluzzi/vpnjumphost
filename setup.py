#!/usr/bin/python3
import subprocess
import json
import fileinput
import shutil
from shutil import copyfile
import os
import re
import stat

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

workdir = os.path.dirname(os.path.realpath(__file__))
js = open('servers.json')
servers = json.loads(js.read())
keys = list(servers.keys())
allfiles = ["supervisord.conf","rootfs/vpn.sh"]
home = os.path.expanduser("~")
homekey = home + "/.ssh/id_rsa.pub"
paths = os.environ['PATH'].split(os.pathsep)
pathpattern1 = re.compile("^" + home  +"/bin$")
pathpattern2 = re.compile("^" + home  +"/.local/bin$")
bindir = None
for i in paths:
    if pathpattern1.match(i) or pathpattern2.match(i):
        bindir = i
if bindir == None:
    if os.geteuid()==0:
        bindir = "/usr/local/bin"
    else:
        bindir = home + "/bin"
    print(f"{bcolors.WARNING}Warning: add {bindir} to PATH env{bcolors.ENDC}")
scriptfile = bindir + "/vpn"

if not os.path.exists(homekey):
    print(f"{bcolors.FAIL}Please run ss-keygen to generate a ssh key{bcolors.ENDC}")
    exit()
else:
    copyfile(homekey,"authorized_keys")

if not os.path.exists(bindir + '/compose'):
    os.makedirs(bindir + '/compose')
if not os.path.exists('config'):
    os.makedirs('config')
if not os.path.exists('log'):
    os.makedirs('log')

def make_files(vpnid):
    vpnname = bindir + "/compose/vpn." + vpnid + ".yml"
    copyfile("vpn",scriptfile)
    st = os.stat(scriptfile)
    os.chmod(scriptfile, st.st_mode | stat.S_IEXEC)
    with fileinput.FileInput(scriptfile, inplace = True) as script:
        for line in script:
            newline = line.replace("workdir = None", "workdir = '" + workdir + "'")
            print(newline.replace("bindir = None", "bindir = '" + bindir + "'"), end='')
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
