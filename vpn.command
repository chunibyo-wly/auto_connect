#!/bin/bash
/Users/chunibyo/01_project/06_open_source/mygmail/venv/bin/python /Users/chunibyo/01_project/06_open_source/mygmail/main.py &
/opt/cisco/secureclient/bin/vpn disconnect
/opt/cisco/secureclient/bin/vpn connect vpn2fa.hku.hk

function ctrl_c() {
    echo "Disconnecting..."
    /opt/cisco/secureclient/bin/vpn disconnect
    exit 0
}

echo "Press [CTRL+C] to disconnect.."
while true; do
    sleep 1
    trap ctrl_c INT
done
