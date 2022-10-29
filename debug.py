import subprocess
import sys

print("lis")
subprocess.call("getent group sudo | cut -d: -f4", shell=True)
