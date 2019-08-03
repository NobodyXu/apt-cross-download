#!/usr/bin/env python3

# This script is adapted from:
#     https://github.com/NobodyXu/snippet/src/tips/how_to_download_deb_packages_on_rasp_pi_for_amd64.md

import os
import sys
import subprocess

def run_command(command, wait = True, stdin = subprocess.DEVNULL, stdout = None):
    print("Running", command)
    p = subprocess.Popen(command, stdin = stdin, stdout = stdout, close_fds = True, restore_signals = True)
    if wait:
        p.wait()
    else:
        return p

if "APT_PROXY_PORT" in os.environ:
    run_command(["/root/detect-apt-proxy.sh", os.environ.["APT_PROXY_PORT"]])

if "ARCH" in os.environ:
    run_command(["/usr/bin/dpkg", "--add-architecture", os.environ["ARCH"]])

run_command(["/usr/bin/apt-get", "upate"])

Set = set() # All packages processed
if len(sys.argv) != 1:
    List = set(sys.argv[1 : ]).remove(" ") # To Remove duplicate and empty entries
else:
    # Read from stdin
    List = set( each.strip() for each in sys.stdin.read().strip().replace("\n", " ").split(" ") ).remove(" ")
    if len(List) == 0:
        print("Usage", sys.argv[0], "package ....")
        print("E.x.,", sys.argv[0], "perl:amd64")
        print("Environment variables: APT_PROXY_PORT, ARCH")
        sys.exit()

while len(List) != 0:
    dependencies = set()

    for each in List:
        download = run_command(["/usr/bin/apt-get", "download", each], wait = False)

        # Get dependencies of this packqage
        cache = run_command(["/usr/bin/apt-cache", "depends", each], wait = False, stdout = subprocess.PIPE)
        for line in cache.stdout:
            striped_line = line.decode().strip()
            if "Depends" in striped_line:
                # Remove prefix "PreDepends:" or "Depends:" or "|Depends:"
                dependency = striped_line[(striped_line.find(":") + 1) : ].strip() 
                # Turn <libc-dev> into libc-dev
                dependency = dependency.replace("<", "").replace(">", "")
                dependencies.add(dependency)

        cache.wait()    # Clean up zombie process
	download.wait() # Wait for the download to finish

    Set |= List              # All items in the List have already been processed.
    dependencies -= Set      # Remove package already processed.
    dependencies.remove(" ") # Remove empty entry
