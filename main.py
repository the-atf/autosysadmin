#auto sysadmin script for basic management

import os
import sys
import subprocess

#check if user is root
if os.geteuid() != 0:
    print("You need to have root privileges to run this script.\n")
    sys.exit(1)

#check what OS is running, if not debian/ubuntu, print error and exit
if os.path.exists("/etc/debian_version"):
    print("Debian/Ubuntu detected\n")
else:
    print("This script is only for Debian/Ubuntu\n")
    sys.exit(1)

subprocess.call("apt install net-tools -y", shell=True)

#check users.txt, cross reference with /etc/passwd, if any extra users.txt are found, print username.
try:
    with open("users.txt") as f:
        users = f.read().splitlines()
    with open("admins.txt") as f:
        admins = f.read().splitlines()
except:
    print("users.txt not found")
    sys.exit(1)


#check if user is in /etc/passwd
for user in users:
    if user not in open("/etc/passwd").read():
        print("User " + user + " not found")
#check for unathorized admin users

for admin in admins:
    if admin not in subprocess.call("getent group sudo | cut -d: -f4", shell=True):
        print("Unauthorized admin user found: " + admin)

#check for disallowed packages, I.E, hacking tools, etc.
subprocess.call("apt list --installed > installed.txt", shell=True)
try:
    with open("installed.txt") as f:
        installed = f.read().splitlines()
        disallowed = open("disallowed.txt").read().splitlines()
        for package in disallowed:
            if package in installed:
                print("Package " + package + " is installed")
                subprocess.call("apt remove " + package + " -y", shell=True)
                sys.exit(1)
except:
    print("installed.txt not found (script error?)")
    sys.exit(1)

#check packages.txt and install any missing packages
packages = input("Enter packages to install: ")

subprocess.call("apt install " + packages + " -y", shell=True)

#disable root login via ssh
print("Disabling root login via ssh")
subprocess.call("sed -i 's/PermitRootLogin yes/PermitRootLogin no/g' /etc/ssh/sshd_config", shell=True)
subprocess.call("systemctl restart sshd", shell=True)

#check for open ports, if any are found, print port number
subprocess.call("netstat -tulpn > ports.txt", shell=True)
try:
    with open("ports.txt") as f:
        ports = f.read().splitlines()
        for port in ports:
            if "LISTEN" in port:
                print("Port " + port + " is open\n")
                sys.exit(1)
except:
    print("ports.txt not found")
    sys.exit(1)

#run apt update
print("Running apt update", shell=True)
subprocess.call("apt update", shell=True)

#run apt upgrade
print("Running apt upgrade")
subprocess.call("apt upgrade -y", shell=True)

#install ufw
print("Installing ufw")
subprocess.call("apt install ufw -y", shell=True)
subprocess.call("ufw enable", shell=True)
subprocess.call("ufw allow ssh", shell=True)
subprocess.call("systemctl enable ufw", shell=True)

#find media files, if any are found, print file name and path
print("Searching for media files\n")

subprocess.call("locate *.mp3 > media.txt", shell=True)
subprocess.call("locate *.mp4 > media.txt", shell=True)
subprocess.call("locate *.webm > media.txt", shell=True)
subprocess.call("locate *.jpg > media.txt", shell=True)
subprocess.call("locate *.png > media.txt", shell=True)
subprocess.call("locate *.gif > media.txt", shell=True)
try:
    with open("media.txt") as f:
        media = f.read().splitlines()
        for file in media:
            print("Media file found: " + file)
except:
    print("media.txt not found")
    sys.exit(1)

#when done, install clamav and run clamscan
print("Installing clamav")
subprocess.call("apt install clamav -y", shell=True)
print("Running clamscan")
subprocess.call("freshclam", shell=True)
subprocess.call("clamscan -r /", shell=True)


