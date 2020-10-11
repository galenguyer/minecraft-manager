"""
module to handle creation of start and systemd scripts
"""
import os
import pwd
from pathlib import Path


def create_start_script(server_name, path, jar_name):
    """
    create the startup script given a few arguments
    """
    start_script = f'''#!/usr/bin/env bash
## {server_name}.sh

# exit if a command fails
set -o errexit

# exit if required variables aren't set
set -o nounset

# return the exit status of the final command before a failure
set -o pipefail

# create a new named screen session for the server, killing any existing ones
if screen -list | grep -q "^{server_name}$"; then
    screen -S "{server_name}" -X quit 2>&1 >/dev/null
fi
screen -dmS "{server_name}" java -jar {jar_name} nogui
'''
    with open(Path(path, 'start.sh'), 'wt') as script_fd:
        script_fd.write(start_script)
    Path(path, 'start.sh').chmod(0o744)


def create_systemd_file(server_name, path):
    """
    create a systemd service file if possible
    """
    unit_file = f'/etc/systemd/system/{server_name}-mc.service'
    if os.path.exists(unit_file):
        print('systemd unit file already exists')
        return
    if not os.access('/etc/systemd/system/', os.W_OK):
        print('could not write to systemd unit file')
        return
    file_text = f'''[Unit]
Description=Minecraft Server
After=network.target

[Service]
Type=forking
User={pwd.getpwuid(os.getuid())[0]}
WorkingDirectory={path}
ExecStart={path}/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
'''
    with open(unit_file, 'wt') as script_fd:
        script_fd.write(file_text)
