#!/usr/bin/python3
import subprocess
import yaml
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
ymlconf = open('config.yaml')
config = yaml.load(ymlconf.read(), Loader=yaml.FullLoader)
subnet = config["config"]["subnet"]
servers = config["servers"]
keys = list(servers.keys())
allfiles = ["conf/supervisord.conf","rootfs/vpn.sh","rootfs/entrypoint.sh"]
home = os.path.expanduser("~")
homekey = home + "/.ssh/id_rsa.pub"
paths = os.environ['PATH'].split(os.pathsep)
pathpattern1 = re.compile("^" + home  +"/bin$")
pathpattern2 = re.compile("^" + home  +"/.local/bin$")
bindir = None
for i in paths:
    if pathpattern1.match(i) or pathpattern2.match(i):
        bindir = i
        if not os.path.exists(bindir):
            os.makedirs(bindir)
if bindir == None:
    if os.geteuid()==0:
        bindir = "/usr/bin"
    else:
        bindir = home + "/bin"
        if not os.path.exists(bindir):
            os.makedirs(bindir)
        print(f"{bcolors.WARNING}Warning: add {bindir} to PATH env{bcolors.ENDC}")
scriptfile = bindir + "/vpn"

if not os.path.exists(homekey):
    print(f"{bcolors.FAIL}Please run ss-keygen to generate a ssh key{bcolors.ENDC}")
    exit()
else:
    copyfile(homekey,"authorized_keys")

if not os.path.exists(home + '/.config/vpnjumphost'):
    os.makedirs(home + '/.config/vpnjumphost')
if not os.path.exists('config'):
    os.makedirs('config')
if not os.path.exists('log'):
    os.makedirs('log')

def make_files(vpnid):
    vpnname = home + "/.config/vpn." + vpnid + ".yml"
    copyfile("vpn",scriptfile)
    st = os.stat(scriptfile)
    os.chmod(scriptfile, st.st_mode | stat.S_IEXEC)
    with fileinput.FileInput(scriptfile, inplace = True) as script:
        for line in script:
            newline = line.replace("workdir = None", "workdir = '" + workdir + "'")
            print(newline.replace("confdir = None", "confdir = '" + home + "/.config'"), end='')
    copyfile("vpn.yml", vpnname)
    workfiles = allfiles.copy()
    workfiles.append(vpnname)
    for f in workfiles:
        with fileinput.FileInput(f, inplace=True) as file:
            for line in file:
                newline = line.replace("vpnid",vpnid)
                newline = newline.replace("dockerdir",workdir)
                newline = newline.replace("proxyport",str(servers[vpnid]["proxyport"]))
                newline = newline.replace("dnsport",str(servers[vpnid]["dnsport"]))
                print(newline.replace("sshport",str(servers[vpnid]["sshport"])), end='')
    try:
        onbootkeys = servers[vpnid]["guestonboot"].keys()
        ob = open("rootfs/onboot.sh",'w')
        onbootlines = "#!/bin/sh"
        for obscript in onbootkeys:
            onbootlines = onbootlines + "\n" + servers[vpnid]["guestonboot"][obscript]
        ob.writelines(onbootlines)
        ob.close()
    except:
        print("No onboot commands")
    try:
        ondownkeys = servers[vpnid]["guestondown"].keys()
        od = open("rootfs/ondown.sh",'w')
        ondownlines = "#!/bin/sh"
        for odscript in ondownkeys:
            ondownlines = ondownlines + "\n" + servers[vpnid]["guestondown"][odscript]
        od.writelines(ondownlines)
        od.close()
    except:
        print("No ondown commands")


def return_files(vpnid):
    for f in allfiles:
        with fileinput.FileInput(f, inplace=True) as file:
            for line in file:
                newline = line
                print(newline.replace(vpnid,"vpnid"), end='')
    firstline = "#!/bin/sh"
    ob = open("rootfs/onboot.sh",'w')
    ob.writelines(firstline)
    ob.close()
    od = open("rootfs/ondown.sh",'w')
    od.writelines(firstline)
    od.close()

for i in keys:
   print("making files for " + i) 
   make_files(i) 
   build = "sudo docker build -t gederico/vpn.{}:v1.0.0 .".format(i)
   start = subprocess.call(build,shell=True)
   print("restoring files") 
   return_files(i)
os.remove("authorized_keys")

print ("Creating network")
network = "docker network inspect vpnjumphost >/dev/null 2>&1 || docker network create --subnet={} --driver bridge vpnjumphost".format(subnet)
start = subprocess.call(network,shell=True)
